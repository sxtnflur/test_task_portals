from domain.risk import RiskFactorEnum, RiskLevel


def test_risk_factor_values_match_member_names():
    assert RiskFactorEnum.high_instability == "high_instability"
    assert RiskFactorEnum.high_energy == "high_energy"
    assert RiskFactorEnum.closing_soon == "closing_soon"


def test_risk_level_values_match_member_names():
    assert RiskLevel.low == "low"
    assert RiskLevel.middle == "middle"
    assert RiskLevel.high == "high"
