import importlib

import pytest


def _strategy_module():
    return importlib.import_module("src.strategy")


@pytest.mark.parametrize(
    ("quadrant", "expected_game"),
    [
        ("Non-critical", "Process automation / catalog buying"),
        ("Leverage", "Competitive RFQ / reverse auction posture"),
        ("Bottleneck", "Secure supply / dual-sourcing-as-insurance"),
        ("Strategic", "Repeated partnership / Nash bargaining"),
    ],
)
def test_strategy_router_maps_each_quadrant_to_a_sourcing_game(
    quadrant, expected_game
):
    route = _strategy_module().get_strategy_route(quadrant)

    assert route["recommended_sourcing_game"] == expected_game
    assert route["buyer_objective"]
    assert route["supplier_behavior_assumption"]
    assert route["why_this_game_fits"]
    assert len(route["recommended_tactics"]) >= 4
    assert route["risk_of_wrong_strategy"]
    assert route["next_sourcing_action"]


def test_strategy_router_returns_a_copy_and_rejects_unknown_quadrants():
    strategy = _strategy_module()
    route = strategy.get_strategy_route("Leverage")
    route["buyer_objective"] = "changed by caller"

    assert strategy.get_strategy_route("Leverage")["buyer_objective"] != route[
        "buyer_objective"
    ]
    with pytest.raises(ValueError, match="Unknown Kraljic quadrant"):
        strategy.get_strategy_route("Unknown")


def test_nash_bargaining_splits_only_the_surplus_above_batnas():
    result = _strategy_module().calculate_nash_bargaining(
        buyer_batna_value=100,
        supplier_batna_value=80,
        joint_value_created=250,
        buyer_bargaining_power=0.60,
    )

    assert result["total_surplus"] == pytest.approx(70)
    assert result["buyer_share_of_surplus"] == pytest.approx(42)
    assert result["supplier_share_of_surplus"] == pytest.approx(28)
    assert result["recommended_buyer_value"] == pytest.approx(142)
    assert result["recommended_supplier_value"] == pytest.approx(108)
    assert (
        result["recommended_buyer_value"] + result["recommended_supplier_value"]
        == pytest.approx(250)
    )
    assert "balanced" in result["negotiation_posture"].lower()
    assert "BATNA" in result["plain_english_interpretation"]


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "buyer_batna_value": 100,
            "supplier_batna_value": 100,
            "joint_value_created": 150,
            "buyer_bargaining_power": 0.5,
        },
        {
            "buyer_batna_value": 100,
            "supplier_batna_value": 80,
            "joint_value_created": 250,
            "buyer_bargaining_power": 1.1,
        },
    ],
)
def test_nash_bargaining_rejects_invalid_value_pools(kwargs):
    with pytest.raises(ValueError):
        _strategy_module().calculate_nash_bargaining(**kwargs)


def test_competitive_tension_simulator_estimates_savings_and_tco():
    result = _strategy_module().simulate_competitive_tension(
        qualified_bidders=5,
        starting_average_bid=1_000_000,
        competition_intensity=0.80,
        tco_adjustment_factor=1.04,
    )

    assert result["estimated_bid_reduction"] == pytest.approx(0.14)
    assert result["expected_savings"] == pytest.approx(140_000)
    assert result["expected_bid"] == pytest.approx(860_000)
    assert result["tco_adjusted_expected_award_value"] == pytest.approx(894_400)
    assert "reverse-auction" in result["recommended_rfq_posture"].lower()
    assert "price-only" in result["price_only_award_warning"].lower()


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "qualified_bidders": 1,
            "starting_average_bid": 1_000,
            "competition_intensity": 0.5,
            "tco_adjustment_factor": 1.0,
        },
        {
            "qualified_bidders": 3,
            "starting_average_bid": 0,
            "competition_intensity": 0.5,
            "tco_adjustment_factor": 1.0,
        },
        {
            "qualified_bidders": 3,
            "starting_average_bid": 1_000,
            "competition_intensity": -0.1,
            "tco_adjustment_factor": 1.0,
        },
    ],
)
def test_competitive_tension_simulator_validates_inputs(kwargs):
    with pytest.raises(ValueError):
        _strategy_module().simulate_competitive_tension(**kwargs)
