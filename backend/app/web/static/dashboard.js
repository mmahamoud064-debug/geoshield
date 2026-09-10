const qs = (selector) => document.querySelector(selector);

const els = {
  totalEvents: qs('#totalEvents'),
  uniqueIps: qs('#uniqueIps'),
  riskyEvents: qs('#riskyEvents'),
  activeAlerts: qs('#activeAlerts'),
  alertsList: qs('#alertsList'),
  alertMeta: qs('#alertMeta'),
  eventsTable: qs('#eventsTable'),
  eventMeta: qs('#eventMeta'),
  activityPoints: qs('#activityPoints'),
  mapMeta: qs('#mapMeta'),
  mapEmpty: qs('#mapEmpty'),
  demoButton: qs('#demoButton'),
  refreshButton: qs('#refreshButton'),
  logFile: qs('#logFile'),
  toast: qs('#toast'),
  incidentBackdrop: qs('#incidentBackdrop'),
  incidentDrawer: qs('#incidentDrawer'),
  incidentClose: qs('#incidentClose'),
  incidentIp: qs('#incidentIp'),
  incidentSeverity: qs('#incidentSeverity'),
  incidentScore: qs('#incidentScore'),
  incidentExplanation: qs('#incidentExplanation'),
  incidentRequest: qs('#incidentRequest'),
  incidentStatus: qs('#incidentStatus'),
  incidentObserved: qs('#incidentObserved'),
  incidentDataType: qs('#incidentDataType'),
  incidentEnrichment: qs('#incidentEnrichment'),
  incidentLocation: qs('#incidentLocation'),
  incidentAsn: qs('#incidentAsn'),
  incidentIsp: qs('#incidentIsp'),
  incidentProxy: qs('#incidentProxy'),
  incidentReasons: qs('#incidentReasons'),
  incidentTimeline: qs('#incidentTimeline'),
};

const api = {
  overview: '/api/overview',
  alerts: '/api/alerts',
  events: '/api/events',
  geo: '/api/geo/activity',
  demo: '/api/demo/start',
  upload: '/api/logs/upload',
  alertDetail: (id) => `/api/alerts/${id}`,
};

async function request(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const payload = await response.json();
      detail = payload.detail || detail;
    } catch (_) {}
    throw new Error(detail);
  }
  return response.json();
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function showToast(message, isError = false) {
  els.toast.textContent = message;
  els.toast.classList.toggle('error', isError);
  els.toast.classList.add('show');
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => els.toast.classList.remove('show'), 2800);
}

function renderOverview(data) {
  els.totalEvents.textContent = Number(data.total_events || 0).toLocaleString();
  els.uniqueIps.textContent = Number(data.unique_ips || 0).toLocaleString();
  els.riskyEvents.textContent = Number(data.risky_events || 0).toLocaleString();
  els.activeAlerts.textContent = Number(data.active_alerts || 0).toLocaleString();
}

function severityClass(severity) {
  const s = String(severity || 'low').toLowerCase();
  return ['low', 'medium', 'high', 'critical'].includes(s) ? s : 'low';
}

function renderAlerts(alerts) {
  els.alertMeta.textContent = `${alerts.length} alert${alerts.length === 1 ? '' : 's'}`;
  if (!alerts.length) {
    els.alertsList.innerHTML = '<div class="empty-state">No alerts yet. Run the demo or ingest traffic.</div>';
    return;
  }

  els.alertsList.innerHTML = alerts.slice(0, 20).map((alert) => {
    const reasons = (alert.reasons || []).map((reason) =>
      `<span class="reason-chip" title="${escapeHtml(reason.reason)}"><b>+${Number(reason.points || 0)}</b>${escapeHtml(reason.rule)}</span>`
    ).join('');
    return `
      <article class="alert-item" data-alert-id="${Number(alert.id)}" role="button" tabindex="0" aria-label="Open incident details for ${escapeHtml(alert.ip)}">
        <div class="alert-top">
          <div><span class="alert-ip">${escapeHtml(alert.ip)}</span><span class="alert-country">${escapeHtml(alert.country_code || 'Unknown')}</span></div>
          <span class="severity ${severityClass(alert.severity)}">${escapeHtml(alert.severity)}</span>
        </div>
        <div class="score-row"><strong>${Number(alert.score || 0)}</strong><span>/ 100 risk</span></div>
        <p class="alert-explanation">${escapeHtml(alert.explanation || 'Suspicious activity detected.')}</p>
        <div class="reason-list">${reasons}</div>
      </article>`;
  }).join('');
}

function openIncidentDrawer() {
  els.incidentBackdrop.hidden = false;
  els.incidentDrawer.classList.add('open');
  els.incidentDrawer.setAttribute('aria-hidden', 'false');
}

function closeIncidentDrawer() {
  els.incidentDrawer.classList.remove('open');
  els.incidentDrawer.setAttribute('aria-hidden', 'true');
  els.incidentBackdrop.hidden = true;
}

function renderIncident(detail) {
  const event = detail.event || {};
  const network = detail.network || {};
  const reasons = detail.reasons || [];
  const timeline = detail.timeline || [];
  const severity = severityClass(detail.severity);

  els.incidentIp.textContent = detail.ip || 'Unknown';
  els.incidentSeverity.className = `severity ${severity}`;
  els.incidentSeverity.textContent = detail.severity || 'unknown';
  els.incidentScore.textContent = Number(detail.score || 0);
  els.incidentExplanation.textContent = detail.explanation || 'Suspicious activity detected.';
  els.incidentRequest.textContent = `${event.method || '—'} ${event.path || '—'}`;
  els.incidentStatus.textContent = event.status ?? '—';
  els.incidentObserved.textContent = event.timestamp ? formatTime(event.timestamp) : '—';
  els.incidentDataType.textContent = event.synthetic ? 'Synthetic demo' : 'Real traffic';
  els.incidentEnrichment.textContent = event.enrichment_status || '—';

  const locationParts = [network.city, network.region, network.country_code].filter(Boolean);
  els.incidentLocation.textContent = locationParts.join(', ') || 'Unknown';
  els.incidentAsn.textContent = network.asn ? `AS${network.asn}` : 'Unknown';
  els.incidentIsp.textContent = network.isp || 'Unknown';
  els.incidentProxy.textContent = network.is_proxy
    ? (network.proxy_type ? `Yes · ${network.proxy_type}` : 'Yes')
    : 'No';

  els.incidentReasons.innerHTML = reasons.length
    ? reasons.map((reason) => `
      <div class="incident-reason">
        <div class="incident-reason-points">+${Number(reason.points || 0)}</div>
        <div><strong>${escapeHtml(reason.rule)}</strong><p>${escapeHtml(reason.reason)}</p></div>
      </div>`).join('')
    : '<div class="drawer-empty">No rule contributions recorded.</div>';

  els.incidentTimeline.innerHTML = timeline.length
    ? timeline.map((item) => `
      <div class="timeline-item ${Number(item.risk_score || 0) >= 30 ? 'risky' : ''}">
        <div class="timeline-dot"></div>
        <div class="timeline-copy">
          <div><strong>${escapeHtml(item.method)}</strong> <span>${escapeHtml(item.path)}</span></div>
          <small>${escapeHtml(formatTime(item.timestamp))} · HTTP ${Number(item.status || 0)} · risk ${Number(item.risk_score || 0)}${item.synthetic ? ' · synthetic' : ''}</small>
        </div>
      </div>`).join('')
    : '<div class="drawer-empty">No related activity found.</div>';
}

async function loadIncident(alertId) {
  if (!alertId) return;
  openIncidentDrawer();
  els.incidentExplanation.textContent = 'Loading incident context…';
  try {
    const detail = await request(api.alertDetail(alertId));
    renderIncident(detail);
  } catch (error) {
    closeIncidentDrawer();
    showToast(`Could not load incident: ${error.message}`, true);
  }
}

function riskClass(score) {
  if (score >= 50) return 'danger';
  if (score >= 30) return 'warn';
  return 'safe';
}

function formatTime(value) {
  try {
    return new Intl.DateTimeFormat(undefined, { hour: '2-digit', minute: '2-digit', second: '2-digit' }).format(new Date(value));
  } catch (_) {
    return '—';
  }
}

function renderEvents(events) {
  els.eventMeta.textContent = `${events.length} recent`;
  if (!events.length) {
    els.eventsTable.innerHTML = '<tr><td colspan="7" class="table-empty">No events yet.</td></tr>';
    return;
  }

  els.eventsTable.innerHTML = events.slice(0, 30).map((event) => `
    <tr>
      <td>${escapeHtml(formatTime(event.timestamp))}</td>
      <td><span class="event-ip">${escapeHtml(event.ip)}</span>${event.synthetic ? '<span class="synthetic-badge">SYNTHETIC</span>' : ''}</td>
      <td class="path-cell" title="${escapeHtml(event.path)}"><b>${escapeHtml(event.method)}</b> ${escapeHtml(event.path)}</td>
      <td><span class="status-code ${Number(event.status) >= 400 ? 'bad' : 'ok'}">${Number(event.status || 0)}</span></td>
      <td>${escapeHtml(event.country_code || '—')}</td>
      <td>${escapeHtml(event.asn || '—')}</td>
      <td><span class="risk-score ${riskClass(Number(event.risk_score || 0))}">${Number(event.risk_score || 0)}</span></td>
    </tr>`).join('');
}

function project(longitude, latitude) {
  const x = ((Number(longitude) + 180) / 360) * 960;
  const y = ((90 - Number(latitude)) / 180) * 480;
  return { x: Math.max(0, Math.min(960, x)), y: Math.max(0, Math.min(480, y)) };
}

function svgNode(name, attrs = {}) {
  const node = document.createElementNS('http://www.w3.org/2000/svg', name);
  Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, String(value)));
  return node;
}

function renderMap(points) {
  els.activityPoints.replaceChildren();
  els.mapEmpty.style.display = points.length ? 'none' : 'grid';
  const total = points.reduce((sum, item) => sum + Number(item.event_count || 0), 0);
  els.mapMeta.textContent = points.length ? `${points.length} locations · ${total} events` : 'Waiting for data';

  points.forEach((item) => {
    if (item.latitude == null || item.longitude == null) return;
    const { x, y } = project(item.longitude, item.latitude);
    const events = Number(item.event_count || 0);
    const risky = Number(item.risky_count || 0);
    const radius = Math.min(16, 4.5 + Math.sqrt(Math.max(1, events)) * 2.5);
    const group = svgNode('g', { class: `activity-point ${risky > 0 ? 'risky' : 'normal'}` });
    const title = svgNode('title');
    title.textContent = `${item.country_name || item.country_code || 'Unknown'}: ${events} event(s), ${risky} risky`;
    group.appendChild(title);
    group.appendChild(svgNode('circle', { class: 'pulse', cx: x, cy: y, r: radius * 2.4 }));
    group.appendChild(svgNode('circle', { class: 'core', cx: x, cy: y, r: radius, fill: 'currentColor' }));
    if (item.country_code) {
      const label = svgNode('text', { class: 'map-label', x: x + radius + 5, y: y + 4 });
      label.textContent = `${item.country_code} ${events}`;
      group.appendChild(label);
    }
    els.activityPoints.appendChild(group);
  });
}

async function refreshDashboard(silent = false) {
  try {
    const [overview, alerts, events, geo] = await Promise.all([
      request(api.overview), request(api.alerts), request(api.events), request(api.geo)
    ]);
    renderOverview(overview);
    renderAlerts(alerts);
    renderEvents(events);
    renderMap(geo);
    if (!silent) showToast('Dashboard refreshed');
  } catch (error) {
    showToast(`Could not refresh: ${error.message}`, true);
  }
}

async function runDemo() {
  els.demoButton.disabled = true;
  const original = els.demoButton.textContent;
  els.demoButton.textContent = 'Running…';
  try {
    const result = await request(api.demo, { method: 'POST' });
    await refreshDashboard(true);
    showToast(`Demo loaded: ${result.synthetic_events} events, ${result.alerts_created} alerts`);
  } catch (error) {
    showToast(`Demo failed: ${error.message}`, true);
  } finally {
    els.demoButton.disabled = false;
    els.demoButton.textContent = original;
  }
}

async function uploadLog(file) {
  if (!file) return;
  const data = new FormData();
  data.append('file', file);
  try {
    showToast(`Uploading ${file.name}…`);
    const result = await request(api.upload, { method: 'POST', body: data });
    await refreshDashboard(true);
    showToast(`Processed ${result.processed}; skipped ${result.skipped}`);
  } catch (error) {
    showToast(`Upload failed: ${error.message}`, true);
  } finally {
    els.logFile.value = '';
  }
}

els.demoButton.addEventListener('click', runDemo);
els.refreshButton.addEventListener('click', () => refreshDashboard());
els.logFile.addEventListener('change', (event) => uploadLog(event.target.files?.[0]));
els.alertsList.addEventListener('click', (event) => {
  const item = event.target.closest('[data-alert-id]');
  if (item) loadIncident(item.dataset.alertId);
});
els.alertsList.addEventListener('keydown', (event) => {
  if (event.key !== 'Enter' && event.key !== ' ') return;
  const item = event.target.closest('[data-alert-id]');
  if (!item) return;
  event.preventDefault();
  loadIncident(item.dataset.alertId);
});
els.incidentClose.addEventListener('click', closeIncidentDrawer);
els.incidentBackdrop.addEventListener('click', closeIncidentDrawer);
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && els.incidentDrawer.classList.contains('open')) closeIncidentDrawer();
});
refreshDashboard(true);
