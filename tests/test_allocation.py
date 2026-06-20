import pandas as pd
import pytest

from src.allocation import evaluate_allocation_scenarios, recommend_best_scenario


def _award_suppliers():
    return pd.DataFrame(
        [
            {
                "supplier_name": "Economy Valve Co.",
                "unit_cost": 10.0,
                "quality_score": 92.0,
                "otif_rate": 0.86,
                "lead_time_days": 45,
                "disruption_probability": 0.35,
                "supplier_risk_score": 70.0,
                "capacity": 2_000,
                "avl_approved_flag": True,
            },
            {
                "supplier_name": "Gulf Reliability Partners",
                "unit_cost": 14.0,
                "quality_score": 99.0,
                "otif_rate": 0.98,
                "lead_time_days": 20,
                "disruption_probability": 0.03,
                "supplier_risk_score": 10.0,
                "capacity": 2_000,
                "avl_approved_flag": True,
            },
        ]
    )


def test_allocation_purchase_cost_math_for_80_20_split():
    scenarios = evaluate_allocation_scenarios(_award_suppliers(), annual_demand_units=1_000)
    split = scenarios.set_index("scenario").loc["80/20"]

    assert split["expected_purchase_cost"] == pytest.approx(10_800.0)
    assert split["primary_supplier"] == "Economy Valve Co."
    assert split["secondary_supplier"] == "Gulf Reliability Partners"
    assert split["primary_share"] == pytest.approx(0.80)
    assert split["secondary_share"] == pytest.approx(0.20)
    assert split["total_risk_adjusted_cost"] == pytest.approx(
        split["expected_purchase_cost"]
        + split["expected_disruption_loss"]
        + split["quality_penalty"]
        + split["lead_time_risk_penalty"]
    )


def test_all_required_award_scenarios_are_compared():
    scenarios = evaluate_allocation_scenarios(_award_suppliers(), annual_demand_units=1_000)
    assert scenarios["scenario"].tolist() == ["100/0", "80/20", "70/30", "60/40", "50/50"]


def test_risk_adjusted_recommendation_can_beat_single_source_low_cost():
    scenarios = evaluate_allocation_scenarios(_award_suppliers(), annual_demand_units=1_000)
    best = recommend_best_scenario(scenarios)
    baseline = scenarios.loc[scenarios["scenario"] == "100/0"].iloc[0]

    assert best["scenario"] != "100/0"
    assert best["total_risk_adjusted_cost"] < baseline["total_risk_adjusted_cost"]
    assert best["recommended_award_split"].startswith(best["primary_supplier"])


def test_dual_source_analysis_requires_two_avl_approved_suppliers():
    suppliers = _award_suppliers()
    suppliers.loc[1, "avl_approved_flag"] = False
    with pytest.raises(ValueError, match="two AVL-approved suppliers"):
        evaluate_allocation_scenarios(suppliers, annual_demand_units=1_000)
