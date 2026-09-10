from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RuleContribution:
    rule: str
    points: int
    reason: str


@dataclass(frozen=True, slots=True)
class RiskContext:
    path: str
    status: int
    is_proxy: bool
    recent_request_count: int
    recent_failed_count: int
    country_is_unusual: bool
    asn_burst_count: int
    impossible_travel: bool = False


@dataclass(frozen=True, slots=True)
class RiskAssessment:
    score: int
    severity: str
    contributions: list[RuleContribution]


SENSITIVE_PATH_MARKERS = (
    "/admin",
    "/login",
    "/wp-admin",
    "/wp-login",
    "/.env",
    "/.git",
    "/phpmyadmin",
    "/config",
)


def _severity(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 30:
        return "medium"
    return "low"


def evaluate_risk(context: RiskContext) -> RiskAssessment:
    contributions: list[RuleContribution] = []

    if context.is_proxy:
        contributions.append(RuleContribution("proxy", 30, "Source is identified as a proxy/VPN/TOR endpoint."))

    if context.status in {401, 403, 404} and context.recent_failed_count >= 3:
        contributions.append(
            RuleContribution("failed_responses", 20, "Repeated authentication/authorization/not-found failures were observed.")
        )

    normalized_path = context.path.lower()
    if any(marker in normalized_path for marker in SENSITIVE_PATH_MARKERS):
        contributions.append(RuleContribution("sensitive_path", 20, "Request targets a commonly sensitive or scanned path."))

    if context.recent_request_count >= 20:
        contributions.append(RuleContribution("request_burst", 20, "High request rate from this IP in the recent window."))

    if context.country_is_unusual:
        contributions.append(RuleContribution("unusual_country", 10, "Country is unusual compared with recent traffic."))

    if context.asn_burst_count >= 5:
        contributions.append(RuleContribution("asn_burst", 15, "Many distinct recent source IPs are concentrated in the same ASN."))

    if context.impossible_travel:
        contributions.append(RuleContribution("impossible_travel", 35, "The same user identifier appeared too far away to travel there in the observed time."))

    score = min(100, sum(item.points for item in contributions))
    return RiskAssessment(score=score, severity=_severity(score), contributions=contributions)
