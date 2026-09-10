from app.risk.engine import RiskContext, evaluate_risk

def test_proxy_failed_login_to_sensitive_path_becomes_high_risk():
    assessment=evaluate_risk(RiskContext(path="/admin/login",status=401,is_proxy=True,recent_request_count=25,recent_failed_count=8,country_is_unusual=False,asn_burst_count=0))
    assert assessment.score >= 70
    assert assessment.severity == "high"
    assert {c.rule for c in assessment.contributions} >= {"proxy","failed_responses","sensitive_path","request_burst"}

def test_normal_request_has_low_risk():
    assessment=evaluate_risk(RiskContext(path="/products",status=200,is_proxy=False,recent_request_count=1,recent_failed_count=0,country_is_unusual=False,asn_burst_count=0))
    assert assessment.score < 30
    assert assessment.severity == "low"
    assert assessment.contributions == []

def test_score_is_clamped_to_100():
    assessment=evaluate_risk(RiskContext(path="/.env",status=403,is_proxy=True,recent_request_count=100,recent_failed_count=100,country_is_unusual=True,asn_burst_count=100))
    assert assessment.score == 100

def test_impossible_travel_is_explainable_medium_risk():
    assessment=evaluate_risk(RiskContext(path="/account",status=200,is_proxy=False,recent_request_count=1,recent_failed_count=0,country_is_unusual=False,asn_burst_count=0,impossible_travel=True))
    assert assessment.score >= 30
    assert assessment.severity == "medium"
    assert {c.rule for c in assessment.contributions} == {"impossible_travel"}
