"""Kraljic strategy routing and deterministic sourcing-game calculators."""

from __future__ import annotations

from copy import deepcopy
from math import isfinite


STRATEGY_ROUTES = {
    "Non-critical": {
        "recommended_sourcing_game": "Process automation / catalog buying",
        "why_this_game_fits": (
            "Value impact and supply risk are both low, so process efficiency is "
            "more valuable than a complex sourcing event."
        ),
        "buyer_objective": "Reduce administrative cost and simplify purchasing.",
        "supplier_behavior_assumption": (
            "Many suppliers can meet the need, and deep relationship investment is "
            "less critical."
        ),
        "recommended_tactics": (
            "Catalog buying",
            "Standard terms",
            "Vendor rationalization",
            "P-card or blanket PO",
        ),
        "risk_of_wrong_strategy": (
            "Over-engineering sourcing events can cost more in buyer time than the "
            "commercial value they create."
        ),
        "next_sourcing_action": (
            "Standardize the specification and move repeat demand to an approved "
            "catalog, P-card, or blanket-PO channel."
        ),
    },
    "Leverage": {
        "recommended_sourcing_game": "Competitive RFQ / reverse auction posture",
        "why_this_game_fits": (
            "High value impact and a competitive supply market create room to use "
            "qualified bidding tension without accepting avoidable supply risk."
        ),
        "buyer_objective": "Use competition to reduce total cost of ownership.",
        "supplier_behavior_assumption": (
            "Qualified suppliers will compete for share when requirements, scoring, "
            "and award rules are credible."
        ),
        "recommended_tactics": (
            "Multi-round RFQ",
            "TCO scoring",
            "Competitive tension",
            "Split award when it improves value",
        ),
        "risk_of_wrong_strategy": (
            "A price-only award can erase savings through quality failures, long lead "
            "times, poor OTIF, or supplier risk."
        ),
        "next_sourcing_action": (
            "Confirm the qualified bidder list and issue a multi-round RFQ with "
            "published TCO and service-level criteria."
        ),
    },
    "Bottleneck": {
        "recommended_sourcing_game": "Secure supply / dual-sourcing-as-insurance",
        "why_this_game_fits": (
            "Supply risk is high even though spend impact is lower, so continuity and "
            "option value matter more than a small unit-price reduction."
        ),
        "buyer_objective": "Protect continuity of supply.",
        "supplier_behavior_assumption": (
            "A limited supply base creates dependency and gives constrained suppliers "
            "more negotiating leverage."
        ),
        "recommended_tactics": (
            "Dual source",
            "Capacity reservation",
            "Buffer inventory",
            "Supplier development",
        ),
        "risk_of_wrong_strategy": (
            "Chasing the lowest price can create single-source exposure and a much "
            "larger operational interruption."
        ),
        "next_sourcing_action": (
            "Secure near-term capacity and qualify a second source before negotiating "
            "incremental price concessions."
        ),
    },
    "Strategic": {
        "recommended_sourcing_game": "Repeated partnership / Nash bargaining",
        "why_this_game_fits": (
            "High value and high supply risk make this a repeated relationship where "
            "joint improvement and continuity can create more value than a one-shot bid."
        ),
        "buyer_objective": "Protect long-term value and split gains fairly.",
        "supplier_behavior_assumption": (
            "Cooperation matters because the relationship repeats and both parties "
            "invest in performance, capacity, and continuity."
        ),
        "recommended_tactics": (
            "Long-term agreement",
            "Joint cost reduction",
            "Performance incentives",
            "Executive governance",
        ),
        "risk_of_wrong_strategy": (
            "Treating a strategic supplier like a one-shot auction can damage trust, "
            "investment, continuity, and long-term value."
        ),
        "next_sourcing_action": (
            "Build a fact-based negotiation plan around BATNAs, joint value creation, "
            "performance commitments, and executive governance."
        ),
    },
}


def get_strategy_route(quadrant: str) -> dict:
    """Return an independent strategy route for a Kraljic quadrant."""
    try:
        return deepcopy(STRATEGY_ROUTES[quadrant])
    except KeyError as exc:
        raise ValueError(f"Unknown Kraljic quadrant: {quadrant}") from exc


def _validated_value(name: str, value: float) -> float:
    numeric = float(value)
    if not isfinite(numeric) or numeric < 0:
        raise ValueError(f"{name} must be a finite non-negative value")
    return numeric


def calculate_nash_bargaining(
    *,
    buyer_batna_value: float,
    supplier_batna_value: float,
    joint_value_created: float,
    buyer_bargaining_power: float,
) -> dict:
    """Split cooperative value above both BATNAs using a weighted Nash rule."""
    buyer_batna = _validated_value("Buyer BATNA value", buyer_batna_value)
    supplier_batna = _validated_value("Supplier BATNA value", supplier_batna_value)
    joint_value = _validated_value("Joint value created", joint_value_created)
    power = float(buyer_bargaining_power)
    if not isfinite(power) or not 0.0 <= power <= 1.0:
        raise ValueError("Buyer bargaining power must be between 0.0 and 1.0")

    total_surplus = joint_value - buyer_batna - supplier_batna
    if total_surplus < 0:
        raise ValueError("Joint value must cover both buyer and supplier BATNA values")

    buyer_surplus = total_surplus * power
    supplier_surplus = total_surplus - buyer_surplus
    buyer_value = buyer_batna + buyer_surplus
    supplier_value = supplier_batna + supplier_surplus

    if power > 0.60:
        posture = (
            "Buyer-advantaged negotiation: protect supplier participation while using "
            "the stronger buyer BATNA to trade for measurable TCO and service gains."
        )
    elif power < 0.40:
        posture = (
            "Supplier-advantaged negotiation: strengthen the buyer BATNA, trade across "
            "multiple variables, and avoid forcing a deal below supplier participation value."
        )
    else:
        posture = (
            "Balanced negotiation: protect both BATNAs and trade cost, capacity, risk, "
            "and performance commitments to grow the joint value pool."
        )

    interpretation = (
        f"The two BATNAs protect ${buyer_batna:,.0f} for the buyer and "
        f"${supplier_batna:,.0f} for the supplier. The remaining "
        f"${total_surplus:,.0f} surplus is split {power:.0%} to the buyer and "
        f"{1.0 - power:.0%} to the supplier, producing recommended values of "
        f"${buyer_value:,.0f} and ${supplier_value:,.0f}."
    )
    return {
        "total_surplus": total_surplus,
        "buyer_share_of_surplus": buyer_surplus,
        "supplier_share_of_surplus": supplier_surplus,
        "recommended_buyer_value": buyer_value,
        "recommended_supplier_value": supplier_value,
        "negotiation_posture": posture,
        "plain_english_interpretation": interpretation,
    }


def simulate_competitive_tension(
    *,
    qualified_bidders: int,
    starting_average_bid: float,
    competition_intensity: float,
    tco_adjustment_factor: float,
) -> dict:
    """Estimate a simple, deterministic competitive RFQ outcome."""
    if isinstance(qualified_bidders, bool) or not isinstance(qualified_bidders, int):
        raise ValueError("Qualified bidders must be a whole number")
    if qualified_bidders < 2:
        raise ValueError("At least two qualified bidders are required")
    starting_bid = _validated_value("Starting average bid", starting_average_bid)
    if starting_bid == 0:
        raise ValueError("Starting average bid must be greater than zero")
    intensity = float(competition_intensity)
    if not isfinite(intensity) or not 0.0 <= intensity <= 1.0:
        raise ValueError("Competition intensity must be between 0.0 and 1.0")
    tco_factor = float(tco_adjustment_factor)
    if not isfinite(tco_factor) or tco_factor <= 0:
        raise ValueError("TCO adjustment factor must be greater than zero")

    bidder_effect = min((qualified_bidders - 1) * 0.015, 0.12)
    intensity_effect = intensity * 0.10
    reduction_rate = min(bidder_effect + intensity_effect, 0.25)
    expected_savings = starting_bid * reduction_rate
    expected_bid = starting_bid - expected_savings
    tco_adjusted_value = expected_bid * tco_factor

    if qualified_bidders >= 5 and intensity >= 0.70:
        posture = (
            "High competitive tension: use a structured multi-round RFQ with an "
            "optional reverse-auction round, subject to qualification and TCO guardrails."
        )
    elif qualified_bidders >= 3:
        posture = (
            "Moderate competitive tension: use a multi-round RFQ, transparent TCO "
            "scoring, and a best-and-final offer round."
        )
    else:
        posture = (
            "Limited competition: use a sealed multi-round RFQ and strengthen the "
            "qualified supply base before considering an auction."
        )

    return {
        "estimated_bid_reduction": reduction_rate,
        "expected_savings": expected_savings,
        "expected_bid": expected_bid,
        "tco_adjusted_expected_award_value": tco_adjusted_value,
        "recommended_rfq_posture": posture,
        "price_only_award_warning": (
            "Do not convert bid reduction directly into an award: a price-only decision "
            "can lose value through quality, lead time, OTIF, capacity, or supplier risk."
        ),
    }
