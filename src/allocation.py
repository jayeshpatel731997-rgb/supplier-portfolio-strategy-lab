"""Risk-adjusted supplier award allocation and TCO scenario analysis."""

from __future__ import annotations

import pandas as pd

from src.scorecards import calculate_supplier_scorecards


AWARD_SCENARIOS = (
    ("100/0", 1.00, 0.00),
    ("80/20", 0.80, 0.20),
    ("70/30", 0.70, 0.30),
    ("60/40", 0.60, 0.40),
    ("50/50", 0.50, 0.50),
)
DISRUPTION_RECOVERY_RATE = 0.80
QUALITY_FAILURE_COST_RATE = 0.35
LEAD_TIME_TARGET_DAYS = 30.0
LEAD_TIME_COST_RATE = 0.05

REQUIRED_ALLOCATION_COLUMNS = {
    "supplier_name",
    "unit_cost",
    "quality_score",
    "otif_rate",
    "lead_time_days",
    "disruption_probability",
    "supplier_risk_score",
    "capacity",
    "avl_approved_flag",
}


def _select_award_suppliers(suppliers: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    approved = suppliers.loc[suppliers["avl_approved_flag"].astype(bool)].copy()
    if len(approved) < 2:
        raise ValueError("Dual-source analysis requires at least two AVL-approved suppliers")

    primary_index = approved["unit_cost"].astype(float).idxmin()
    primary = approved.loc[primary_index]
    scorecards = calculate_supplier_scorecards(approved)
    secondary_name = scorecards.loc[
        scorecards["supplier_name"] != primary["supplier_name"], "supplier_name"
    ].iloc[0]
    secondary = approved.loc[approved["supplier_name"] == secondary_name].iloc[0]
    return primary, secondary


def _supplier_cost_components(
    supplier: pd.Series, share: float, annual_demand_units: float
) -> tuple[float, float, float, float]:
    purchase_cost = annual_demand_units * share * float(supplier["unit_cost"])
    disruption_exposure = purchase_cost * float(supplier["disruption_probability"])
    quality_penalty = (
        purchase_cost
        * max(0.0, 1.0 - float(supplier["quality_score"]) / 100.0)
        * QUALITY_FAILURE_COST_RATE
    )
    lead_time_overrun = max(
        0.0, float(supplier["lead_time_days"]) - LEAD_TIME_TARGET_DAYS
    ) / LEAD_TIME_TARGET_DAYS
    lead_time_penalty = purchase_cost * lead_time_overrun * LEAD_TIME_COST_RATE
    return purchase_cost, disruption_exposure, quality_penalty, lead_time_penalty


def evaluate_allocation_scenarios(
    suppliers: pd.DataFrame, annual_demand_units: float
) -> pd.DataFrame:
    """Compare single- and dual-source awards using risk-adjusted TCO."""
    missing = REQUIRED_ALLOCATION_COLUMNS.difference(suppliers.columns)
    if missing:
        raise ValueError(f"Missing required allocation columns: {sorted(missing)}")
    if annual_demand_units <= 0:
        raise ValueError("Annual demand units must be greater than zero")

    primary, secondary = _select_award_suppliers(suppliers)
    records = []
    for scenario, primary_share, secondary_share in AWARD_SCENARIOS:
        primary_costs = _supplier_cost_components(
            primary, primary_share, annual_demand_units
        )
        secondary_costs = _supplier_cost_components(
            secondary, secondary_share, annual_demand_units
        )
        expected_purchase_cost = primary_costs[0] + secondary_costs[0]
        concentration_factor = primary_share**2 + secondary_share**2
        expected_disruption_loss = (
            primary_costs[1] + secondary_costs[1]
        ) * DISRUPTION_RECOVERY_RATE * concentration_factor
        quality_penalty = primary_costs[2] + secondary_costs[2]
        lead_time_risk_penalty = primary_costs[3] + secondary_costs[3]
        total_risk_adjusted_cost = (
            expected_purchase_cost
            + expected_disruption_loss
            + quality_penalty
            + lead_time_risk_penalty
        )
        capacity_shortfall_units = max(
            0.0, annual_demand_units * primary_share - float(primary["capacity"])
        ) + max(
            0.0, annual_demand_units * secondary_share - float(secondary["capacity"])
        )

        records.append(
            {
                "scenario": scenario,
                "primary_supplier": primary["supplier_name"],
                "secondary_supplier": secondary["supplier_name"],
                "primary_share": primary_share,
                "secondary_share": secondary_share,
                "expected_purchase_cost": expected_purchase_cost,
                "expected_disruption_loss": expected_disruption_loss,
                "quality_penalty": quality_penalty,
                "lead_time_risk_penalty": lead_time_risk_penalty,
                "total_risk_adjusted_cost": total_risk_adjusted_cost,
                "capacity_feasible": capacity_shortfall_units == 0,
                "capacity_shortfall_units": capacity_shortfall_units,
                "recommended_award_split": (
                    f"{primary['supplier_name']} {primary_share:.0%} / "
                    f"{secondary['supplier_name']} {secondary_share:.0%}"
                ),
            }
        )
    return pd.DataFrame(records)


def recommend_best_scenario(scenarios: pd.DataFrame) -> pd.Series:
    """Return the lowest risk-adjusted, capacity-feasible award scenario."""
    required = {"total_risk_adjusted_cost", "capacity_feasible", "scenario"}
    missing = required.difference(scenarios.columns)
    if missing:
        raise ValueError(f"Missing scenario columns: {sorted(missing)}")
    feasible = scenarios.loc[scenarios["capacity_feasible"].astype(bool)]
    if feasible.empty:
        raise ValueError("No capacity-feasible award scenario is available")
    return feasible.loc[feasible["total_risk_adjusted_cost"].idxmin()]
