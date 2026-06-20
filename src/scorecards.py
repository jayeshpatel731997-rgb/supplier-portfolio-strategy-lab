"""Supplier scorecard calculations for sourcing decisions."""

from __future__ import annotations

import pandas as pd


SCORECARD_WEIGHTS = {
    "cost": 0.25,
    "quality": 0.20,
    "otif": 0.15,
    "lead_time": 0.10,
    "risk": 0.15,
    "capacity": 0.10,
    "avl": 0.05,
}

REQUIRED_SCORECARD_COLUMNS = {
    "supplier_name",
    "unit_cost",
    "quality_score",
    "otif_rate",
    "lead_time_days",
    "supplier_risk_score",
    "capacity",
    "avl_approved_flag",
}


def _benefit_score(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="raise").astype(float)
    spread = numeric.max() - numeric.min()
    if spread == 0:
        return pd.Series(100.0, index=series.index)
    return 100.0 * (numeric - numeric.min()) / spread


def _cost_score(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="raise").astype(float)
    spread = numeric.max() - numeric.min()
    if spread == 0:
        return pd.Series(100.0, index=series.index)
    return 100.0 * (numeric.max() - numeric) / spread


def calculate_supplier_scorecards(suppliers: pd.DataFrame) -> pd.DataFrame:
    """Normalize supplier measures and calculate a weighted sourcing score."""
    missing = REQUIRED_SCORECARD_COLUMNS.difference(suppliers.columns)
    if missing:
        raise ValueError(f"Missing required scorecard columns: {sorted(missing)}")
    if suppliers.empty:
        raise ValueError("Supplier scorecard input cannot be empty")

    result = suppliers.copy()
    otif = pd.to_numeric(result["otif_rate"], errors="raise").astype(float)
    if otif.max() <= 1.0:
        otif = otif * 100.0

    result["cost_score"] = _cost_score(result["unit_cost"])
    result["quality_score_component"] = pd.to_numeric(
        result["quality_score"], errors="raise"
    ).clip(0, 100)
    result["otif_score"] = otif.clip(0, 100)
    result["lead_time_score"] = _cost_score(result["lead_time_days"])
    result["risk_score"] = (
        100.0 - pd.to_numeric(result["supplier_risk_score"], errors="raise")
    ).clip(0, 100)
    result["capacity_score"] = _benefit_score(result["capacity"])
    result["avl_score"] = result["avl_approved_flag"].astype(bool).astype(float) * 100.0

    weighted_components = {
        "cost": "cost_score",
        "quality": "quality_score_component",
        "otif": "otif_score",
        "lead_time": "lead_time_score",
        "risk": "risk_score",
        "capacity": "capacity_score",
        "avl": "avl_score",
    }
    result["weighted_supplier_score"] = sum(
        result[column] * SCORECARD_WEIGHTS[component]
        for component, column in weighted_components.items()
    ).round(1)
    result["supplier_rank"] = (
        result["weighted_supplier_score"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )
    return result.sort_values(
        ["weighted_supplier_score", "supplier_name"], ascending=[False, True]
    ).reset_index(drop=True)
