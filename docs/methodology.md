# Methodology

Supplier Portfolio Strategy Lab converts synthetic procurement data into a category strategy for Bayou Specialty Chemicals. The method is intentionally deterministic: every calculation is visible, repeatable, and testable without live APIs.

## 1. Decision architecture

The lab follows a category-manager workflow:

1. Aggregate supplier data into category spend and risk measures.
2. Assign a Kraljic quadrant.
3. Route the quadrant to a sourcing game.
4. Compare suppliers using one weighted scorecard.
5. Screen award options for AVL eligibility, capacity, and risk-adjusted TCO.
6. Apply the relevant negotiation or competitive-tension lens.
7. Generate a deterministic executive memo and next actions.

Kraljic is the strategy router. The scorecard and TCO model support the routed strategy; they do not replace it.

## 2. Data foundation

Each CSV row represents one supplier-category relationship and includes annual spend, unit cost, capacity, lead time, OTIF, quality, disruption probability, supplier risk, notes, incumbent status, and AVL status.

The model estimates comparable annual demand as:

```text
Spend-weighted unit cost = sum(supplier spend x unit cost) / category spend
Annual demand units      = category spend / spend-weighted unit cost
```

This is a planning denominator for comparing award splits. It is not a production demand forecast.

## 3. Kraljic segmentation

### Profit/value impact

```text
Profit/value impact = 75% x portfolio-relative category spend score
                    + 25% x portfolio-relative average unit-cost score
```

### Supply risk

```text
Supply risk = 30% x average supplier risk
            + 30% x average disruption probability
            + 20% x portfolio-relative lead-time score
            + 20% x AVL coverage gap
```

Portfolio-relative values are scaled from 20 to 100. Scores at or above 50 are high.

| Value | Risk | Quadrant |
|---|---|---|
| Low | Low | Non-critical |
| High | Low | Leverage |
| Low | High | Bottleneck |
| High | High | Strategic |

## 4. Strategy router

Each quadrant maps to a recommended sourcing game, buyer objective, supplier behavior assumption, tactics, wrong-strategy risk, and next action.

### Non-critical

- **Game:** Process automation / catalog buying
- **Objective:** Reduce administrative cost and simplify purchasing
- **Assumption:** Many suppliers can meet the need; relationship depth is less critical
- **Tactics:** Catalog buying, standard terms, vendor rationalization, P-card or blanket PO
- **Avoid:** Over-engineering sourcing events

### Leverage

- **Game:** Competitive RFQ / reverse auction posture
- **Objective:** Use competition to reduce TCO
- **Assumption:** Qualified suppliers compete for share when award rules are credible
- **Tactics:** Multi-round RFQ, TCO scoring, competitive tension, split award when useful
- **Avoid:** A price-only award that ignores quality, lead time, OTIF, capacity, and risk

### Bottleneck

- **Game:** Secure supply / dual-sourcing-as-insurance
- **Objective:** Protect continuity of supply
- **Assumption:** A limited supply base creates dependency
- **Tactics:** Dual source, capacity reservation, buffer inventory, supplier development
- **Avoid:** Chasing lowest price and increasing single-source exposure

### Strategic

- **Game:** Repeated partnership / Nash bargaining
- **Objective:** Protect long-term value and split gains fairly
- **Assumption:** Cooperation matters because the relationship repeats
- **Tactics:** Long-term agreement, joint cost reduction, performance incentives, executive governance
- **Avoid:** Treating a strategic supplier like a one-shot auction

The game-theory language is deliberately business-friendly. It frames expected supplier behavior and the buyer's decision rules rather than claiming that every sourcing event is a formal mathematical game.

## 5. Supplier scorecards

Supplier measures use different units, so the model converts them to a common 0-100 scale.

| Dimension | Weight | Better performance |
|---|---:|---|
| Cost | 25% | Lower unit cost |
| Quality | 20% | Higher quality score |
| OTIF | 15% | Higher on-time-in-full rate |
| Lead time | 10% | Fewer days |
| Risk | 15% | Lower supplier risk score |
| Capacity | 10% | More available units |
| AVL | 5% | Approved status |

Cost, lead time, and capacity are normalized within the selected category. Quality and OTIF keep their business percentages. Risk is inverted so lower risk produces a higher score.

AVL status remains a governance gate. Unapproved suppliers are visible, but the allocation model requires two approved suppliers for dual-source analysis.

## 6. Risk-adjusted award allocation

The model compares 100/0, 80/20, 70/30, 60/40, and 50/50 awards. The primary supplier is the lowest-cost approved source. The secondary supplier is the strongest approved alternative by weighted scorecard.

### Purchase cost

```text
Purchase cost = annual demand x supplier share x unit cost
```

### Disruption loss

```text
Supplier disruption exposure = allocated purchase cost x disruption probability
Concentration factor          = primary share^2 + secondary share^2
Expected disruption loss      = combined exposure x 80% recovery premium
                              x concentration factor
```

The concentration factor makes the continuity value of diversification visible.

### Quality penalty

```text
Quality penalty = allocated purchase cost x (1 - quality score) x 35%
```

### Lead-time penalty

```text
Lead-time penalty = allocated purchase cost
                  x days above the 30-day target / 30
                  x 5%
```

### Recommendation

```text
Risk-adjusted TCO = purchase cost + disruption loss + quality penalty + lead-time penalty
```

The recommended award is the capacity-feasible scenario with the lowest risk-adjusted TCO.

## 7. Weighted Nash bargaining calculator

The Strategic-category calculator uses four inputs:

- buyer BATNA value;
- supplier BATNA value;
- joint value created;
- buyer bargaining power from 0.0 to 1.0.

BATNA means the value each party can protect without the proposed agreement.

```text
Total surplus          = joint value - buyer BATNA - supplier BATNA
Buyer surplus share    = total surplus x buyer bargaining power
Supplier surplus share = total surplus - buyer surplus share
Buyer value            = buyer BATNA + buyer surplus share
Supplier value         = supplier BATNA + supplier surplus share
```

Joint value must cover both BATNAs. The calculator classifies the posture as supplier-advantaged, balanced, or buyer-advantaged and explains the result in plain English.

This is a weighted Nash-inspired planning model. It does not estimate legal entitlement, supplier profit, or a binding contract price.

## 8. Competitive RFQ / reverse auction simulator

The Leverage-category simulator uses qualified bidders, starting average bid, competition intensity, and a TCO adjustment factor.

```text
Bidder effect       = min((qualified bidders - 1) x 1.5%, 12%)
Intensity effect    = competition intensity x 10%
Bid reduction rate = min(bidder effect + intensity effect, 25%)
Expected savings    = starting bid x bid reduction rate
Expected bid        = starting bid - expected savings
TCO-adjusted award  = expected bid x TCO adjustment factor
```

Five or more bidders plus high competition intensity produces a posture that may include an optional reverse-auction round. Moderate competition routes to a multi-round RFQ and best-and-final offer. Limited competition routes to a sealed RFQ and supply-base development.

The warning is intentional: estimated bid reduction is not the same as realized TCO savings.

## 9. Executive memo

The memo includes:

- category and Kraljic quadrant;
- recommended sourcing game and buyer objective;
- leading supplier scorecard insight;
- recommended capacity-feasible award split;
- risk-adjusted TCO bridge;
- Nash negotiation or competitive RFQ posture when applicable;
- AVL/vendor governance comment;
- the next three category-manager actions.

The same inputs always produce the same memo. No live AI API is used.

## 10. Interpretation limits

Before a real sourcing decision, a category manager would validate demand, quote scope, freight and duties, payment terms, supplier capacity by period, switching cost, qualification time, correlated disruption, contract terms, and finance-approved penalty rates. The lab is a portfolio demonstration and decision-framing tool, not an award authorization system.
