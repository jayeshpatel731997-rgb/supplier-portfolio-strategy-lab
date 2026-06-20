"""Deterministic category sourcing memo generation."""

from __future__ import annotations

import pandas as pd


def _currency(value: float) -> str:
    return f"${value:,.0f}"


def generate_executive_memo(
    *,
    category_name: str,
    quadrant: str,
    sourcing_posture: str,
    scenarios: pd.DataFrame,
    scorecards: pd.DataFrame,
    avl_cleanup_count: int,
    strategy_route: dict,
    commercial_posture: str,
) -> str:
    """Build a repeatable, plain-English sourcing recommendation memo."""
    if scenarios.empty:
        raise ValueError("Allocation scenarios cannot be empty")
    if scorecards.empty:
        raise ValueError("Supplier scorecards cannot be empty")
    required_route_fields = {
        "recommended_sourcing_game",
        "buyer_objective",
        "next_sourcing_action",
    }
    missing_route_fields = required_route_fields.difference(strategy_route)
    if missing_route_fields:
        raise ValueError(
            f"Missing strategy route fields: {sorted(missing_route_fields)}"
        )

    eligible_scenarios = scenarios
    if "capacity_feasible" in scenarios.columns:
        eligible_scenarios = scenarios.loc[scenarios["capacity_feasible"].astype(bool)]
        if eligible_scenarios.empty:
            raise ValueError("No capacity-feasible scenario is available for the memo")
    best = eligible_scenarios.loc[
        eligible_scenarios["total_risk_adjusted_cost"].idxmin()
    ]
    baseline_rows = scenarios.loc[scenarios["scenario"] == "100/0"]
    baseline = baseline_rows.iloc[0] if not baseline_rows.empty else scenarios.iloc[0]
    top_supplier_index = scorecards["weighted_supplier_score"].idxmax()
    top_supplier = scorecards.loc[top_supplier_index, "supplier_name"]
    top_supplier_score = float(
        scorecards.loc[top_supplier_index, "weighted_supplier_score"]
    )
    tco_improvement = float(baseline["total_risk_adjusted_cost"]) - float(
        best["total_risk_adjusted_cost"]
    )
    risk_columns = (
        "expected_disruption_loss",
        "quality_penalty",
        "lead_time_risk_penalty",
    )
    baseline_risk = sum(float(baseline[column]) for column in risk_columns)
    recommended_risk = sum(float(best[column]) for column in risk_columns)
    risk_avoided = baseline_risk - recommended_risk
    purchase_delta = float(best["expected_purchase_cost"]) - float(
        baseline["expected_purchase_cost"]
    )

    if tco_improvement >= 0:
        economics = (
            f"The recommendation improves modeled risk-adjusted cost by "
            f"{_currency(tco_improvement)} versus the 100% lowest-cost baseline."
        )
    else:
        economics = (
            f"The recommendation adds {_currency(abs(tco_improvement))} of modeled "
            "risk-adjusted cost and should be treated as a continuity investment."
        )

    avl_action = (
        f"Close {avl_cleanup_count} AVL/vendor governance gap"
        + ("s" if avl_cleanup_count != 1 else "")
        + " before award."
        if avl_cleanup_count
        else "Maintain current AVL approvals and evidence files before award."
    )

    return f"""BAYOU SPECIALTY CHEMICALS - CATEGORY SOURCING MEMO

Category decision
{category_name} is classified in the {quadrant} Kraljic quadrant. The recommended sourcing posture is: {sourcing_posture}

Recommended sourcing game
{strategy_route['recommended_sourcing_game']}. Buyer objective: {strategy_route['buyer_objective']}

Supplier scorecard insight
{top_supplier} leads the supplier scorecard at {top_supplier_score:.1f}/100 across cost, quality, OTIF, lead time, risk, capacity, and AVL status.

Sourcing recommendation
Award {best['recommended_award_split']} ({best['scenario']} scenario).

TCO and risk-adjusted cost logic
The lowest-unit-cost baseline has a modeled TCO of {_currency(float(baseline['total_risk_adjusted_cost']))}. The recommended split has {_currency(float(best['expected_purchase_cost']))} in expected purchase cost, {_currency(float(best['expected_disruption_loss']))} in expected disruption loss, {_currency(float(best['quality_penalty']))} in quality penalty, and {_currency(float(best['lead_time_risk_penalty']))} in lead-time risk penalty, producing {_currency(float(best['total_risk_adjusted_cost']))} in total risk-adjusted cost. {economics} It changes purchase cost by {_currency(purchase_delta)} while avoiding {_currency(risk_avoided)} of modeled disruption, quality, and lead-time exposure.

Commercial posture
{commercial_posture}

Next 3 actions
1. {strategy_route['next_sourcing_action']}
2. Confirm the proposed award allocation, risk-adjusted TCO assumptions, capacity, and performance commitments with shortlisted suppliers.
3. {avl_action} Establish monthly supplier governance for OTIF, quality, risk triggers, and corrective actions.
"""
