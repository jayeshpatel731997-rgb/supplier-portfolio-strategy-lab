# Three-Minute Interview Demo Script

## 0:00-0:25 - Frame the business problem

"Supplier Portfolio Strategy Lab is a strategic sourcing lab I built in Python and Streamlit for a fictional Houston petrochemical company, Bayou Specialty Chemicals. It does more than display supplier KPIs. It helps a category manager decide which sourcing game to play."

Select **Specialty Valves**.

## 0:25-0:50 - Establish the category facts

"I start with addressable spend, supplier count, AVL coverage, OTIF, and supplier risk. This keeps the strategy grounded in both commercial impact and operational performance."

Call out the unapproved supplier as an AVL/vendor governance gap.

## 0:50-1:15 - Use Kraljic as the strategy router

"The Kraljic model scores value impact using spend and unit cost, then scores supply risk using supplier risk, disruption probability, lead time, and AVL coverage. Specialty Valves is Strategic: high value and high risk."

Point to the portfolio matrix.

"That quadrant is not just a label. It routes the category to a repeated partnership and Nash bargaining posture."

## 1:15-1:50 - Explain the Game Theory Lens

"The buyer's objective is to protect long-term value and split gains fairly. The supplier behavior assumption is that cooperation matters because this relationship repeats. So the tactics are a long-term agreement, joint cost reduction, performance incentives, and executive governance. The model explicitly warns against treating this supplier like a one-shot auction."

Open the Nash calculator.

"The calculator protects each party's BATNA, splits only the value above those alternatives, and translates bargaining power into recommended buyer and supplier values. It is deterministic and business-friendly, not an autonomous negotiator."

## 1:50-2:25 - Connect suppliers to TCO and allocation

"I then compare suppliers using cost, quality, OTIF, lead time, risk, capacity, and AVL status. The allocation model tests five award splits. It adds expected disruption loss, quality penalty, and lead-time risk to purchase cost, then recommends the lowest risk-adjusted TCO among capacity-feasible scenarios."

Point to the recommended split and modeled risk avoided.

"This shows why lowest unit price is not always the lowest-cost sourcing decision."

## 2:25-2:50 - Show the executive output

"The final memo brings the analysis together: Kraljic quadrant, sourcing game, scorecard insight, award split, TCO logic, negotiation posture, AVL governance, and the next three actions for the category manager. It is downloadable and uses no live AI API."

## 2:50-3:00 - Close with breadth

Briefly select **MRO Pumps**.

"A Leverage category routes differently. Here the app uses a competitive RFQ and optional reverse-auction posture, with a simulator for bidder tension and a warning against price-only awards. That routing is what makes this a strategy lab rather than a dashboard."

## Optional follow-up: what comes next?

"The next practical phase is CSV upload and sensitivity controls. Longer-term roadmap items include a full reverse auction optimizer, a deeper Nash scenario builder, network resilience stress testing, Power BI export, and optional AI-assisted memo drafting. The current version stays local, deterministic, and portfolio-safe."
