import pandas as pd
import pytest

from src.scorecards import SCORECARD_WEIGHTS, calculate_supplier_scorecards


def _suppliers():
    return pd.DataFrame(
        [
            {
                "supplier_name": "Low Cost Industrial",
                "unit_cost": 10.0,
                "quality_score": 90.0,
                "otif_rate": 0.90,
                "lead_time_days": 40,
                "supplier_risk_score": 60.0,
                "capacity": 1_000,
                "avl_approved_flag": True,
            },
            {
                "supplier_name": "Reliable Gulf Supply",
                "unit_cost": 12.0,
                "quality_score": 98.0,
                "otif_rate": 0.98,
                "lead_time_days": 20,
                "supplier_risk_score": 10.0,
                "capacity": 1_400,
                "avl_approved_flag": False,
            },
        ]
    )


def test_scorecard_component_normalization_and_avl_status():
    result = calculate_supplier_scorecards(_suppliers()).set_index("supplier_name")

    assert result.loc["Low Cost Industrial", "cost_score"] == pytest.approx(100.0)
    assert result.loc["Reliable Gulf Supply", "lead_time_score"] == pytest.approx(100.0)
    assert result.loc["Reliable Gulf Supply", "risk_score"] == pytest.approx(90.0)
    assert result.loc["Low Cost Industrial", "avl_score"] == pytest.approx(100.0)
    assert result.loc["Reliable Gulf Supply", "avl_score"] == pytest.approx(0.0)


def test_weighted_supplier_score_uses_documented_weights():
    result = calculate_supplier_scorecards(_suppliers()).set_index("supplier_name")
    supplier = result.loc["Low Cost Industrial"]
    component_columns = {
        "cost": "cost_score",
        "quality": "quality_score_component",
        "otif": "otif_score",
        "lead_time": "lead_time_score",
        "risk": "risk_score",
        "capacity": "capacity_score",
        "avl": "avl_score",
    }
    expected = sum(
        supplier[column] * SCORECARD_WEIGHTS[component]
        for component, column in component_columns.items()
    )

    assert supplier["weighted_supplier_score"] == pytest.approx(expected)
    assert sorted(result["supplier_rank"].tolist()) == [1, 2]


def test_scorecard_requires_all_input_columns():
    with pytest.raises(ValueError, match="Missing required scorecard columns"):
        calculate_supplier_scorecards(_suppliers().drop(columns=["capacity"]))


def test_equal_cost_and_lead_time_receive_full_component_scores():
    suppliers = _suppliers()
    suppliers["unit_cost"] = 10.0
    suppliers["lead_time_days"] = 20

    result = calculate_supplier_scorecards(suppliers)

    assert result["cost_score"].tolist() == pytest.approx([100.0, 100.0])
    assert result["lead_time_score"].tolist() == pytest.approx([100.0, 100.0])
