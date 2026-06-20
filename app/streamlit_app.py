"""Streamlit decision-support app for Supplier Portfolio Strategy Lab."""

from __future__ import annotations

import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.allocation import evaluate_allocation_scenarios, recommend_best_scenario
from src.kraljic import segment_categories
from src.memo import generate_executive_memo
from src.scorecards import SCORECARD_WEIGHTS, calculate_supplier_scorecards
from src.strategy import (
    calculate_nash_bargaining,
    get_strategy_route,
    simulate_competitive_tension,
)


DATA_PATH = PROJECT_ROOT / "data" / "supplier_portfolio.csv"

st.set_page_config(
    page_title="Supplier Portfolio Strategy Lab",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --bayou-navy: #102A43;
        --bayou-teal: #087E8B;
        --bayou-orange: #E07A3F;
        --bayou-paper: #F6F8FA;
    }
    .stApp { background: linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 42%); }
    .block-container { max-width: 1280px; padding-top: 2rem; padding-bottom: 3rem; }
    h1, h2, h3 { color: var(--bayou-navy); letter-spacing: -0.02em; }
    [data-testid="stSidebar"] { background-color: #102A43; }
    [data-testid="stSidebar"] * { color: #F8FAFC; }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * { color: #102A43; }
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #D9E2EC;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        box-shadow: 0 5px 18px rgba(16, 42, 67, 0.06);
    }
    .eyebrow {
        color: #087E8B;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }
    .hero-copy { color: #486581; font-size: 1.05rem; max-width: 850px; }
    .decision-card {
        background: #102A43;
        color: white;
        padding: 1.35rem 1.5rem;
        border-radius: 16px;
        border-left: 6px solid #E07A3F;
        margin: 0.5rem 0 1.2rem 0;
    }
    .decision-card h3 { color: white; margin: 0 0 0.35rem 0; }
    .decision-card p { margin: 0.2rem 0; color: #D9E2EC; }
    .posture-card {
        background: #EAF7F7;
        border: 1px solid #A9D9DC;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        color: #102A43;
    }
    .strategy-label {
        color: #087E8B;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    .strategy-copy { color: #334E68; margin-bottom: 1rem; }
    .tactic-chip {
        display: inline-block;
        background: #EAF7F7;
        border: 1px solid #A9D9DC;
        border-radius: 999px;
        color: #102A43;
        font-size: 0.82rem;
        font-weight: 600;
        margin: 0.15rem 0.25rem 0.15rem 0;
        padding: 0.32rem 0.65rem;
    }
    .small-note { color: #627D98; font-size: 0.86rem; }
    div[data-testid="stDownloadButton"] button {
        background: #087E8B; color: white; border: 0; font-weight: 700;
    }
    div[data-testid="stDownloadButton"] button:focus-visible,
    button:focus-visible { outline: 3px solid #F6C177 !important; outline-offset: 2px; }
    @media (max-width: 700px) {
        .block-container { padding-top: 1rem; }
        .decision-card { padding: 1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_procurement_data(path: Path) -> pd.DataFrame:
    """Load the fictional Bayou Specialty Chemicals supplier portfolio."""
    data = pd.read_csv(path)
    for column in ("incumbent_flag", "avl_approved_flag"):
        data[column] = data[column].astype(bool)
    return data


def currency(value: float) -> str:
    return f"${value:,.0f}"


def estimate_annual_demand(category_data: pd.DataFrame) -> float:
    """Convert current category spend to comparable annual demand units."""
    spend = category_data["annual_spend"].sum()
    weighted_unit_cost = (
        category_data["annual_spend"] * category_data["unit_cost"]
    ).sum() / spend
    return spend / weighted_unit_cost


data = load_procurement_data(DATA_PATH)
portfolio = segment_categories(data)

with st.sidebar:
    st.markdown("### ⚙️ Strategy Lab")
    st.caption("Bayou Specialty Chemicals")
    st.markdown("---")
    selected_category = st.selectbox(
        "Select an industrial category",
        options=sorted(data["category_name"].unique()),
        index=sorted(data["category_name"].unique()).index("Specialty Valves"),
        help="Change the category to refresh spend analytics, supplier scorecards, and award allocation.",
    )
    st.markdown("---")
    st.markdown("**Decision lens**")
    st.caption("Spend analytics → Kraljic → sourcing game → supplier scorecards → risk-adjusted TCO → memo")
    st.markdown("**Data status**")
    st.caption("Synthetic portfolio • deterministic logic • no live APIs")

st.markdown('<div class="eyebrow">Houston strategic sourcing portfolio</div>', unsafe_allow_html=True)
st.title("Supplier Portfolio Strategy Lab")
st.markdown(
    '<p class="hero-copy">Turn supplier spend, cost, quality, delivery, capacity, AVL status, and disruption risk into a defensible category strategy for Bayou Specialty Chemicals.</p>',
    unsafe_allow_html=True,
)

category_data = data.loc[data["category_name"] == selected_category].copy()
category_segment = portfolio.loc[
    portfolio["category_name"] == selected_category
].iloc[0]
strategy_route = get_strategy_route(category_segment["kraljic_quadrant"])
scorecards = calculate_supplier_scorecards(category_data)
annual_demand_units = estimate_annual_demand(category_data)
scenarios = evaluate_allocation_scenarios(category_data, annual_demand_units)
best = recommend_best_scenario(scenarios)
baseline = scenarios.loc[scenarios["scenario"] == "100/0"].iloc[0]
tco_impact = baseline["total_risk_adjusted_cost"] - best["total_risk_adjusted_cost"]
risk_columns = [
    "expected_disruption_loss",
    "quality_penalty",
    "lead_time_risk_penalty",
]
risk_avoided = baseline[risk_columns].sum() - best[risk_columns].sum()
approved_count = int(category_data["avl_approved_flag"].sum())
incumbent_count = int(category_data["incumbent_flag"].sum())

st.markdown("### Category snapshot")
kpi_columns = st.columns(5)
kpi_columns[0].metric("Addressable spend", currency(category_data["annual_spend"].sum()))
kpi_columns[1].metric("Suppliers", len(category_data))
kpi_columns[2].metric("AVL approved", f"{approved_count} / {len(category_data)}")
kpi_columns[3].metric("Average OTIF", f"{category_data['otif_rate'].mean():.1%}")
kpi_columns[4].metric("Average risk", f"{category_data['supplier_risk_score'].mean():.0f} / 100")
st.caption(
    f"{incumbent_count} incumbent supplier(s) • modeled annual demand: {annual_demand_units:,.0f} comparable units"
)

st.markdown("### Kraljic category position")
position_col, chart_col = st.columns([1, 1.25], gap="large")
with position_col:
    st.markdown(
        f"""
        <div class="decision-card">
            <h3>{category_segment['kraljic_quadrant']}</h3>
            <p>Value impact: <strong>{category_segment['profit_value_impact_score']:.1f}</strong> / 100</p>
            <p>Supply risk: <strong>{category_segment['supply_risk_score']:.1f}</strong> / 100</p>
        </div>
        <div class="posture-card"><strong>Recommended sourcing posture</strong><br>{category_segment['sourcing_posture']}</div>
        """,
        unsafe_allow_html=True,
    )
with chart_col:
    matrix = (
        alt.Chart(portfolio)
        .mark_circle(size=180, opacity=0.82, stroke="white", strokeWidth=1.5)
        .encode(
            x=alt.X(
                "profit_value_impact_score:Q",
                title="Profit / value impact",
                scale=alt.Scale(domain=[0, 100]),
            ),
            y=alt.Y(
                "supply_risk_score:Q",
                title="Supply risk",
                scale=alt.Scale(domain=[0, 100]),
            ),
            color=alt.Color(
                "kraljic_quadrant:N",
                title="Quadrant",
                scale=alt.Scale(
                    domain=["Non-critical", "Leverage", "Bottleneck", "Strategic"],
                    range=["#9FB3C8", "#087E8B", "#E9A23B", "#D64545"],
                ),
            ),
            tooltip=[
                alt.Tooltip("category_name:N", title="Category"),
                alt.Tooltip("profit_value_impact_score:Q", title="Value", format=".1f"),
                alt.Tooltip("supply_risk_score:Q", title="Risk", format=".1f"),
                alt.Tooltip("kraljic_quadrant:N", title="Quadrant"),
            ],
        )
        .properties(height=315)
    )
    rules = (
        alt.Chart(pd.DataFrame({"threshold": [50]}))
        .mark_rule(color="#829AB1", strokeDash=[5, 5])
    )
    st.altair_chart(
        matrix + rules.encode(x="threshold:Q") + rules.encode(y="threshold:Q"),
        width="stretch",
    )

st.markdown("### Game Theory Lens: Which Sourcing Game Should We Play?")
st.caption(
    "Kraljic is the strategy router: the category position determines how the buyer should create and protect value."
)
game_col, logic_col = st.columns([1, 1.25], gap="large")
with game_col:
    st.markdown(
        f"""
        <div class="decision-card">
            <div class="strategy-label" style="color:#F6C177;">Recommended sourcing game</div>
            <h3>{strategy_route['recommended_sourcing_game']}</h3>
            <p><strong>{category_segment['kraljic_quadrant']} quadrant</strong> strategy route</p>
            <p>{strategy_route['why_this_game_fits']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("**Buyer objective**")
    st.write(strategy_route["buyer_objective"])
    st.markdown("**Supplier behavior assumption**")
    st.write(strategy_route["supplier_behavior_assumption"])
with logic_col:
    st.markdown('<div class="strategy-label">Recommended tactics</div>', unsafe_allow_html=True)
    tactic_chips = "".join(
        f'<span class="tactic-chip">{tactic}</span>'
        for tactic in strategy_route["recommended_tactics"]
    )
    st.markdown(tactic_chips, unsafe_allow_html=True)
    st.markdown("#### What to avoid")
    st.warning(strategy_route["risk_of_wrong_strategy"])
    st.markdown("#### Next sourcing action")
    st.info(strategy_route["next_sourcing_action"])

commercial_posture = strategy_route["next_sourcing_action"]
category_spend = float(category_data["annual_spend"].sum())

if category_segment["kraljic_quadrant"] == "Strategic":
    st.markdown("#### Nash Bargaining Calculator")
    st.caption(
        "Use a weighted Nash split to divide only the value above each party's BATNA. This is a planning lens, not a contract valuation."
    )
    with st.expander("Model the strategic value split", expanded=True):
        input_columns = st.columns(4)
        step = max(round(category_spend * 0.05, -3), 1_000.0)
        buyer_batna = input_columns[0].number_input(
            "Buyer BATNA value",
            min_value=0.0,
            value=float(round(category_spend * 0.45, -3)),
            step=float(step),
            help="Value the buyer can protect without this negotiated agreement.",
        )
        supplier_batna = input_columns[1].number_input(
            "Supplier BATNA value",
            min_value=0.0,
            value=float(round(category_spend * 0.35, -3)),
            step=float(step),
            help="Value the supplier can protect through its best alternative.",
        )
        joint_value = input_columns[2].number_input(
            "Joint value created",
            min_value=0.0,
            value=category_spend,
            step=float(step),
            help="Total value pool available if the parties cooperate.",
        )
        buyer_power = input_columns[3].slider(
            "Buyer bargaining power",
            min_value=0.0,
            max_value=1.0,
            value=0.55,
            step=0.05,
        )
        try:
            nash_result = calculate_nash_bargaining(
                buyer_batna_value=buyer_batna,
                supplier_batna_value=supplier_batna,
                joint_value_created=joint_value,
                buyer_bargaining_power=buyer_power,
            )
        except ValueError as exc:
            st.error(str(exc))
        else:
            result_columns = st.columns(5)
            result_columns[0].metric("Total surplus", currency(nash_result["total_surplus"]))
            result_columns[1].metric("Buyer surplus share", currency(nash_result["buyer_share_of_surplus"]))
            result_columns[2].metric("Supplier surplus share", currency(nash_result["supplier_share_of_surplus"]))
            result_columns[3].metric("Recommended buyer value", currency(nash_result["recommended_buyer_value"]))
            result_columns[4].metric("Recommended supplier value", currency(nash_result["recommended_supplier_value"]))
            st.info(nash_result["negotiation_posture"])
            st.write(nash_result["plain_english_interpretation"])
            commercial_posture = nash_result["negotiation_posture"]

elif category_segment["kraljic_quadrant"] == "Leverage":
    st.markdown("#### Competitive RFQ / Reverse Auction Simulator")
    st.caption(
        "Estimate competitive tension before choosing an RFQ posture. The model keeps TCO guardrails visible."
    )
    with st.expander("Model competitive tension", expanded=True):
        input_columns = st.columns(4)
        qualified_bidders = input_columns[0].number_input(
            "Qualified bidders",
            min_value=2,
            max_value=12,
            value=max(2, approved_count),
            step=1,
        )
        starting_bid = input_columns[1].number_input(
            "Starting average bid",
            min_value=1.0,
            value=category_spend,
            step=max(float(round(category_spend * 0.05, -3)), 1_000.0),
        )
        competition_intensity = input_columns[2].slider(
            "Competition intensity",
            min_value=0.0,
            max_value=1.0,
            value=0.65,
            step=0.05,
        )
        tco_factor = input_columns[3].slider(
            "TCO adjustment factor",
            min_value=0.90,
            max_value=1.25,
            value=1.04,
            step=0.01,
            help="Above 1.00 adds modeled quality, delivery, capacity, and risk cost.",
        )
        auction_result = simulate_competitive_tension(
            qualified_bidders=int(qualified_bidders),
            starting_average_bid=starting_bid,
            competition_intensity=competition_intensity,
            tco_adjustment_factor=tco_factor,
        )
        result_columns = st.columns(4)
        result_columns[0].metric(
            "Estimated bid reduction",
            f"{auction_result['estimated_bid_reduction']:.1%}",
        )
        result_columns[1].metric("Expected savings", currency(auction_result["expected_savings"]))
        result_columns[2].metric("Expected bid", currency(auction_result["expected_bid"]))
        result_columns[3].metric(
            "TCO-adjusted award value",
            currency(auction_result["tco_adjusted_expected_award_value"]),
        )
        st.info(auction_result["recommended_rfq_posture"])
        st.warning(auction_result["price_only_award_warning"])
        commercial_posture = auction_result["recommended_rfq_posture"]

st.markdown("### Supplier scorecards")
st.caption(
    "Weighted view of cost, quality, OTIF, lead time, supplier risk, capacity, and AVL/vendor governance."
)
scorecard_display = scorecards[
    [
        "supplier_rank",
        "supplier_name",
        "weighted_supplier_score",
        "cost_score",
        "quality_score_component",
        "otif_score",
        "lead_time_score",
        "risk_score",
        "capacity_score",
        "avl_approved_flag",
    ]
].rename(
    columns={
        "supplier_rank": "Rank",
        "supplier_name": "Supplier",
        "weighted_supplier_score": "Overall score",
        "cost_score": "Cost",
        "quality_score_component": "Quality",
        "otif_score": "OTIF",
        "lead_time_score": "Lead time",
        "risk_score": "Risk",
        "capacity_score": "Capacity",
        "avl_approved_flag": "AVL approved",
    }
)
st.dataframe(
    scorecard_display.style.format(
        {column: "{:.1f}" for column in scorecard_display.columns if column not in {"Rank", "Supplier", "AVL approved"}}
    ),
    width="stretch",
    hide_index=True,
    column_config={"AVL approved": st.column_config.CheckboxColumn("AVL approved")},
)
with st.expander("View scorecard weighting and supplier notes"):
    weights = " • ".join(f"{name.replace('_', ' ').title()} {weight:.0%}" for name, weight in SCORECARD_WEIGHTS.items())
    st.write(weights)
    st.dataframe(
        category_data[["supplier_name", "supplier_notes"]].rename(
            columns={"supplier_name": "Supplier", "supplier_notes": "Procurement note"}
        ),
        width="stretch",
        hide_index=True,
    )

st.markdown("### Risk-adjusted award allocation")
recommendation_col, economics_col = st.columns([1.25, 1], gap="large")
with recommendation_col:
    st.markdown(
        f"""
        <div class="decision-card">
            <h3>Recommended: {best['scenario']} split</h3>
            <p>{best['recommended_award_split']}</p>
            <p>Risk-adjusted TCO: <strong>{currency(best['total_risk_adjusted_cost'])}</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with economics_col:
    label = "Risk-adjusted value vs. 100% low cost" if tco_impact >= 0 else "Continuity premium vs. 100% low cost"
    value_col, risk_col = st.columns(2)
    value_col.metric(label, currency(abs(tco_impact)))
    risk_col.metric("Modeled risk avoided", currency(risk_avoided))
    st.caption("Recommendation minimizes modeled TCO among capacity-feasible scenarios.")

scenario_display = scenarios[
    [
        "scenario",
        "expected_purchase_cost",
        "expected_disruption_loss",
        "quality_penalty",
        "lead_time_risk_penalty",
        "total_risk_adjusted_cost",
        "capacity_feasible",
    ]
].rename(
    columns={
        "scenario": "Award split",
        "expected_purchase_cost": "Purchase cost",
        "expected_disruption_loss": "Disruption loss",
        "quality_penalty": "Quality penalty",
        "lead_time_risk_penalty": "Lead-time penalty",
        "total_risk_adjusted_cost": "Risk-adjusted TCO",
        "capacity_feasible": "Capacity feasible",
    }
)
currency_columns = [
    "Purchase cost",
    "Disruption loss",
    "Quality penalty",
    "Lead-time penalty",
    "Risk-adjusted TCO",
]
st.dataframe(
    scenario_display.style.format({column: "${:,.0f}" for column in currency_columns}),
    width="stretch",
    hide_index=True,
    column_config={
        "Capacity feasible": st.column_config.CheckboxColumn("Capacity feasible")
    },
)
with st.expander("How the risk-adjusted TCO model works"):
    st.write(
        "Expected purchase cost is adjusted for disruption exposure, quality failure cost, and lead-time risk. "
        "A concentration factor recognizes that dual sourcing reduces the amount of category demand exposed to one event. "
        "The model uses transparent planning assumptions—not a live quote or a financial forecast."
    )
    st.caption(
        "Planning assumptions: 80% disruption recovery premium, 35% quality failure-cost rate, "
        "30-day lead-time target, and 5% lead-time carrying/expedite rate."
    )

memo = generate_executive_memo(
    category_name=selected_category,
    quadrant=category_segment["kraljic_quadrant"],
    sourcing_posture=category_segment["sourcing_posture"],
    scenarios=scenarios,
    scorecards=scorecards,
    avl_cleanup_count=int((~category_data["avl_approved_flag"]).sum()),
    strategy_route=strategy_route,
    commercial_posture=commercial_posture,
)

st.markdown("### Executive category memo")
st.text_area(
    "Deterministic sourcing memo",
    value=memo,
    height=430,
    label_visibility="collapsed",
)
st.download_button(
    "Download sourcing memo",
    data=memo,
    file_name=f"{selected_category.lower().replace(' ', '_')}_sourcing_memo.txt",
    mime="text/plain",
    use_container_width=False,
)
st.markdown(
    '<p class="small-note">Portfolio MVP • synthetic data • Bayou Specialty Chemicals • Houston, Texas</p>',
    unsafe_allow_html=True,
)
