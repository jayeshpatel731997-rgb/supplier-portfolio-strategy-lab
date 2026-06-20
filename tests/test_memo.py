import pandas as pd

from src.memo import generate_executive_memo


STRATEGY_ROUTE = {
    "recommended_sourcing_game": "Repeated partnership / Nash bargaining",
    "buyer_objective": "Protect long-term value and split gains fairly.",
    "supplier_behavior_assumption": "Cooperation matters because the relationship repeats.",
    "why_this_game_fits": "High value and high risk make continuity and cooperation material.",
    "recommended_tactics": (
        "Long-term agreement",
        "Joint cost reduction",
        "Performance incentives",
        "Executive governance",
    ),
    "risk_of_wrong_strategy": "A one-shot auction can damage long-term value.",
    "next_sourcing_action": "Prepare a joint value-creation and negotiation plan.",
}


def test_memo_contains_core_sourcing_recommendation():
    scorecards = pd.DataFrame(
        [
            {"supplier_name": "Economy Valve Co.", "weighted_supplier_score": 64.2},
            {"supplier_name": "Gulf Reliability Partners", "weighted_supplier_score": 91.4},
        ]
    )
    scenarios = pd.DataFrame(
        [
            {
                "scenario": "100/0",
                "recommended_award_split": "Economy Valve Co. 100% / Gulf Reliability Partners 0%",
                "expected_purchase_cost": 10_000.0,
                "expected_disruption_loss": 2_800.0,
                "quality_penalty": 280.0,
                "lead_time_risk_penalty": 250.0,
                "total_risk_adjusted_cost": 13_330.0,
            },
            {
                "scenario": "70/30",
                "recommended_award_split": "Economy Valve Co. 70% / Gulf Reliability Partners 30%",
                "expected_purchase_cost": 11_200.0,
                "expected_disruption_loss": 1_195.0,
                "quality_penalty": 210.0,
                "lead_time_risk_penalty": 175.0,
                "total_risk_adjusted_cost": 12_780.0,
            },
        ]
    )

    memo = generate_executive_memo(
        category_name="Specialty Valves",
        quadrant="Strategic",
        sourcing_posture="Partner selectively and protect continuity.",
        scenarios=scenarios,
        scorecards=scorecards,
        avl_cleanup_count=1,
        strategy_route=STRATEGY_ROUTE,
        commercial_posture="Balanced negotiation: protect both BATNAs and trade value.",
    )

    for expected in (
        "Specialty Valves",
        "Strategic",
        "70/30",
        "risk-adjusted cost",
        "$550",
        "AVL",
        "Repeated partnership / Nash bargaining",
        "Balanced negotiation",
        "Next 3 actions",
    ):
        assert expected.lower() in memo.lower()


def test_memo_is_deterministic():
    scenarios = pd.DataFrame(
        [
            {
                "scenario": "100/0",
                "recommended_award_split": "A 100% / B 0%",
                "expected_purchase_cost": 100.0,
                "expected_disruption_loss": 20.0,
                "quality_penalty": 5.0,
                "lead_time_risk_penalty": 2.0,
                "total_risk_adjusted_cost": 127.0,
            },
            {
                "scenario": "80/20",
                "recommended_award_split": "A 80% / B 20%",
                "expected_purchase_cost": 104.0,
                "expected_disruption_loss": 8.0,
                "quality_penalty": 4.0,
                "lead_time_risk_penalty": 1.0,
                "total_risk_adjusted_cost": 117.0,
            },
        ]
    )
    scorecards = pd.DataFrame([{"supplier_name": "A", "weighted_supplier_score": 80.0}])
    kwargs = dict(
        category_name="MRO Pumps",
        quadrant="Leverage",
        sourcing_posture="Use competition and negotiate TCO.",
        scenarios=scenarios,
        scorecards=scorecards,
        avl_cleanup_count=0,
        strategy_route=STRATEGY_ROUTE,
        commercial_posture="Balanced negotiation posture.",
    )
    assert generate_executive_memo(**kwargs) == generate_executive_memo(**kwargs)


def test_memo_does_not_recommend_capacity_infeasible_lowest_tco():
    scenarios = pd.DataFrame(
        [
            {
                "scenario": "100/0",
                "recommended_award_split": "A 100% / B 0%",
                "expected_purchase_cost": 90.0,
                "expected_disruption_loss": 5.0,
                "quality_penalty": 1.0,
                "lead_time_risk_penalty": 1.0,
                "total_risk_adjusted_cost": 97.0,
                "capacity_feasible": False,
            },
            {
                "scenario": "80/20",
                "recommended_award_split": "A 80% / B 20%",
                "expected_purchase_cost": 100.0,
                "expected_disruption_loss": 4.0,
                "quality_penalty": 1.0,
                "lead_time_risk_penalty": 1.0,
                "total_risk_adjusted_cost": 106.0,
                "capacity_feasible": True,
            },
        ]
    )
    memo = generate_executive_memo(
        category_name="Packaging Materials",
        quadrant="Non-critical",
        sourcing_posture="Simplify the buy.",
        scenarios=scenarios,
        scorecards=pd.DataFrame(
            [{"supplier_name": "A", "weighted_supplier_score": 80.0}]
        ),
        avl_cleanup_count=0,
        strategy_route=STRATEGY_ROUTE,
        commercial_posture="Balanced negotiation posture.",
    )

    assert "80/20 scenario" in memo
