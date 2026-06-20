"""Kraljic category segmentation for procurement portfolio decisions."""

from __future__ import annotations

import pandas as pd


SOURCING_POSTURES = {
    "Non-critical": (
        "Simplify the buy: standardize specifications, reduce transaction cost, "
        "and use catalog or blanket-order controls."
    ),
    "Leverage": (
        "Use competitive tension and volume aggregation to negotiate TCO, service "
        "levels, and measurable savings."
    ),
    "Bottleneck": (
        "Protect continuity through supplier risk mitigation, safety stock, "
        "qualification of alternatives, and active AVL governance."
    ),
    "Strategic": (
        "Build a performance-based supplier partnership, use resilient award "
        "allocation, and govern capacity, quality, continuity, and cost jointly."
    ),
}

REQUIRED_SEGMENTATION_COLUMNS = {
    "category_name",
    "annual_spend",
    "unit_cost",
    "lead_time_days",
    "disruption_probability",
    "supplier_risk_score",
    "avl_approved_flag",
}


def assign_kraljic_quadrant(
    value_impact: float, supply_risk: float, threshold: float = 50.0
) -> str:
    """Map value impact and supply risk scores to a Kraljic quadrant."""
    high_value = float(value_impact) >= threshold
    high_risk = float(supply_risk) >= threshold
    if high_value and high_risk:
        return "Strategic"
    if high_value:
        return "Leverage"
    if high_risk:
        return "Bottleneck"
    return "Non-critical"


def get_sourcing_posture(quadrant: str) -> str:
    """Return the recommended category-management posture for a quadrant."""
    try:
        return SOURCING_POSTURES[quadrant]
    except KeyError as exc:
        raise ValueError(f"Unknown Kraljic quadrant: {quadrant}") from exc


def _portfolio_score(series: pd.Series) -> pd.Series:
    """Scale portfolio values to 20-100 while preserving a neutral single item."""
    numeric = pd.to_numeric(series, errors="raise").astype(float)
    spread = numeric.max() - numeric.min()
    if spread == 0:
        return pd.Series(50.0, index=series.index)
    return 20.0 + 80.0 * (numeric - numeric.min()) / spread


def segment_categories(procurement_data: pd.DataFrame) -> pd.DataFrame:
    """Calculate category value/risk scores and the recommended sourcing posture."""
    missing = REQUIRED_SEGMENTATION_COLUMNS.difference(procurement_data.columns)
    if missing:
        raise ValueError(f"Missing required segmentation columns: {sorted(missing)}")
    if procurement_data.empty:
        raise ValueError("Procurement data cannot be empty")

    data = procurement_data.copy()
    data["avl_approved_flag"] = data["avl_approved_flag"].astype(bool)
    grouped = (
        data.groupby("category_name", as_index=False)
        .agg(
            annual_spend=("annual_spend", "sum"),
            average_unit_cost=("unit_cost", "mean"),
            average_lead_time_days=("lead_time_days", "mean"),
            average_disruption_probability=("disruption_probability", "mean"),
            average_supplier_risk=("supplier_risk_score", "mean"),
            supplier_count=("category_name", "size"),
            avl_approved_suppliers=("avl_approved_flag", "sum"),
        )
        .sort_values("category_name")
        .reset_index(drop=True)
    )

    spend_score = _portfolio_score(grouped["annual_spend"])
    unit_cost_score = _portfolio_score(grouped["average_unit_cost"])
    lead_time_score = _portfolio_score(grouped["average_lead_time_days"])
    avl_coverage = grouped["avl_approved_suppliers"] / grouped["supplier_count"]

    grouped["profit_value_impact_score"] = (
        0.75 * spend_score + 0.25 * unit_cost_score
    ).round(1)
    grouped["supply_risk_score"] = (
        0.30 * grouped["average_supplier_risk"]
        + 0.30 * grouped["average_disruption_probability"] * 100.0
        + 0.20 * lead_time_score
        + 0.20 * (1.0 - avl_coverage) * 100.0
    ).clip(0, 100).round(1)
    grouped["kraljic_quadrant"] = grouped.apply(
        lambda row: assign_kraljic_quadrant(
            row["profit_value_impact_score"], row["supply_risk_score"]
        ),
        axis=1,
    )
    grouped["sourcing_posture"] = grouped["kraljic_quadrant"].map(SOURCING_POSTURES)
    return grouped
