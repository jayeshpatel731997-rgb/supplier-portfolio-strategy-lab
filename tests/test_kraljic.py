import pytest
import pandas as pd

from src import kraljic
from src.kraljic import SOURCING_POSTURES, assign_kraljic_quadrant, get_sourcing_posture


@pytest.mark.parametrize(
    ("value_impact", "supply_risk", "expected"),
    [
        (30, 20, "Non-critical"),
        (75, 25, "Leverage"),
        (25, 80, "Bottleneck"),
        (85, 70, "Strategic"),
    ],
)
def test_assigns_all_four_kraljic_quadrants(value_impact, supply_risk, expected):
    assert assign_kraljic_quadrant(value_impact, supply_risk) == expected


def test_threshold_scores_are_classified_as_high():
    assert assign_kraljic_quadrant(50, 50) == "Strategic"


def test_each_quadrant_has_a_sourcing_posture():
    for quadrant in ("Non-critical", "Leverage", "Bottleneck", "Strategic"):
        posture = get_sourcing_posture(quadrant)
        assert posture == SOURCING_POSTURES[quadrant]
        assert len(posture) > 30


def test_unknown_quadrant_is_rejected():
    with pytest.raises(ValueError, match="Unknown Kraljic quadrant"):
        get_sourcing_posture("Unknown")


def test_category_segmentation_scores_portfolio_data():
    data = pd.DataFrame(
        [
            {
                "category_name": "High Exposure",
                "annual_spend": 4_000_000,
                "unit_cost": 100,
                "lead_time_days": 100,
                "disruption_probability": 0.30,
                "supplier_risk_score": 80,
                "avl_approved_flag": False,
            },
            {
                "category_name": "Low Exposure",
                "annual_spend": 500_000,
                "unit_cost": 10,
                "lead_time_days": 10,
                "disruption_probability": 0.02,
                "supplier_risk_score": 10,
                "avl_approved_flag": True,
            },
        ]
    )

    result = kraljic.segment_categories(data).set_index("category_name")

    assert result.loc["High Exposure", "profit_value_impact_score"] > result.loc[
        "Low Exposure", "profit_value_impact_score"
    ]
    assert result.loc["High Exposure", "supply_risk_score"] > result.loc[
        "Low Exposure", "supply_risk_score"
    ]
    assert result.loc["High Exposure", "kraljic_quadrant"] == "Strategic"
    assert "sourcing_posture" in result.columns
