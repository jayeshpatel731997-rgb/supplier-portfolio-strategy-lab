# Supplier Portfolio Strategy Lab

Supplier Portfolio Strategy Lab is a **strategic sourcing strategy lab, not just a supplier dashboard**. It uses Kraljic segmentation to route each procurement category to the sourcing game that best fits its value impact and supply risk, then supports that choice with supplier scorecards, AVL governance, risk-adjusted TCO, award allocation, and deterministic negotiation tools.

The fictional business is **Bayou Specialty Chemicals**, a Houston petrochemical company purchasing specialty valves, MRO pumps, safety PPE, specialty chemicals, packaging materials, and maintenance services. All supplier names and figures are synthetic and portfolio-safe.

## Why this is more than a dashboard

A supplier dashboard describes what happened. This lab supports a **category management decision**: it uses Kraljic segmentation to route each category to the appropriate **strategic sourcing** posture, then connects **supplier scorecards**, **AVL/vendor governance**, modeled TCO penalties, and game-theory-inspired logic to a capacity-feasible **award allocation** recommendation.

```text
Synthetic supplier portfolio
          |
          v
Spend, value, and supply-risk scoring
          |
          v
Kraljic quadrant = strategy router
          |
          +-- Non-critical -> process automation / catalog buying
          +-- Leverage     -> competitive RFQ / reverse auction posture
          +-- Bottleneck   -> secure supply / dual-sourcing-as-insurance
          +-- Strategic    -> repeated partnership / Nash bargaining
          |
          v
Supplier scorecards + AVL eligibility + risk-adjusted TCO
          |
          v
Award allocation + category-manager actions + executive memo
```

The output is a defensible recommendation about **which sourcing game to play, which suppliers to govern, and how to allocate the award**—not merely a ranked supplier table.

## Recruiter quick scan — the 30-second story

> A Houston-focused procurement portfolio project that turns supplier data into a strategic sourcing recommendation: select the category strategy, evaluate supplier performance and governance, compare risk-adjusted award scenarios, and communicate the decision.

| What a hiring manager wants to see | Evidence in this project |
|---|---|
| Category strategy | Kraljic segmentation routes each category to a category management posture |
| Commercial decision-making | Competitive RFQ logic for Leverage categories and Nash bargaining for Strategic categories |
| Supplier performance and controls | Weighted supplier scorecards plus supplier governance and AVL/vendor governance checks |
| Total-cost thinking | Risk-adjusted TCO combines purchase cost, disruption loss, quality penalties, and lead-time exposure |
| Resilient sourcing | Capacity-feasible dual-sourcing scenarios compare 100/0 through 50/50 award allocation |
| Executive communication | Downloadable sourcing memo connects the analysis to three category-manager actions |
| Technical delivery | Python, Pandas, Streamlit, Altair, pytest, and local synthetic CSV data |

Target roles include Houston supply chain analyst, procurement analyst, strategic sourcing analyst, category analyst, and supplier governance positions in energy, petrochemical, LNG, oilfield services, industrial distribution, and manufacturing.

## Product screenshots

> **Screenshot placeholders:** The files below are intentionally referenced for the GitHub portfolio layout but are not generated automatically. Capture them manually using the instructions in [docs/screenshots/README.md](docs/screenshots/README.md), then save each image under the exact filename shown.

### Executive overview

![Supplier Portfolio Strategy Lab executive overview](docs/screenshots/01_executive_overview.png)

### Kraljic strategy router

![Kraljic category matrix and strategy router](docs/screenshots/02_kraljic_strategy_router.png)

### Game Theory Lens

![Game Theory Lens sourcing recommendation](docs/screenshots/03_game_theory_lens.png)

### Supplier scorecards

![Weighted supplier scorecards and AVL governance](docs/screenshots/04_supplier_scorecards.png)

### Risk-adjusted award allocation

![Risk-adjusted TCO and dual-sourcing award allocation](docs/screenshots/05_award_allocation.png)

### Nash bargaining

![Strategic-category Nash bargaining calculator](docs/screenshots/06_nash_bargaining.png)

### Reverse auction simulator

![Leverage-category competitive RFQ and reverse auction simulator](docs/screenshots/07_reverse_auction_simulator.png)

### Executive memo

![Deterministic executive category sourcing memo](docs/screenshots/08_executive_memo.png)

## Business case

Bayou Specialty Chemicals needs to make sourcing decisions across industrial categories with very different economics and supply markets. A low-risk PPE buy should not consume the same sourcing effort as a strategic specialty-chemical relationship. A bottleneck maintenance service should not be treated like a competitive commodity. A low unit-cost valve supplier may not minimize TCO once disruption, quality, lead time, capacity, and AVL status are considered.

The lab gives a category manager one transparent workflow for answering:

1. How important and risky is this category?
2. Which sourcing game fits that position?
3. Which suppliers are qualified and competitive?
4. What award split minimizes risk-adjusted TCO?
5. What should the buyer do next?

## Methods used

- Portfolio-relative Kraljic segmentation
- Quadrant-based sourcing strategy router
- Weighted supplier scorecards
- AVL/vendor governance screening
- Risk-adjusted TCO modeling
- Capacity-feasible dual-source award allocation
- Weighted Nash bargaining
- Competitive-tension and RFQ simulation
- Deterministic executive memo generation

Detailed assumptions and formulas are in [docs/methodology.md](docs/methodology.md).

## Game theory lens

### Non-critical: process automation / catalog buying

Reduce administrative cost with standardized specifications, catalogs, standard terms, vendor rationalization, P-cards, or blanket POs. Avoid spending more buyer time on the sourcing event than the category can return.

### Leverage: competitive RFQ / reverse auction posture

Use qualified bidder tension to reduce TCO. The simulator estimates bid reduction, expected savings, expected bid value, and TCO-adjusted award value. It also warns against converting a low bid directly into a price-only award.

### Bottleneck: secure supply / dual-sourcing-as-insurance

Treat a second source, reserved capacity, targeted inventory, and supplier development as continuity options. Avoid creating single-source exposure for a small price concession.

### Strategic: repeated partnership / Nash bargaining

Use both parties' BATNAs, the joint value pool, and buyer bargaining power to model a fair surplus split. The calculator returns buyer and supplier values plus a plain-English negotiation posture. It is a deterministic planning lens, not an autonomous negotiator.

## Supplier scorecards and AVL governance

| Dimension | Weight |
|---|---:|
| Cost | 25% |
| Quality | 20% |
| OTIF | 15% |
| Lead time | 10% |
| Supplier risk | 15% |
| Capacity | 10% |
| AVL status | 5% |

Unapproved suppliers remain visible for governance and qualification decisions, but the allocation model requires at least two AVL-approved suppliers before modeling a dual-source award.

## Risk-adjusted TCO and award allocation

The app compares 100/0, 80/20, 70/30, 60/40, and 50/50 awards between the lowest-cost approved supplier and the strongest approved alternative.

```text
Risk-adjusted TCO
= expected purchase cost
+ expected disruption loss
+ quality penalty
+ lead-time risk penalty
```

The recommendation is the lowest modeled TCO among capacity-feasible scenarios. This makes the tradeoff between purchase price and supplier risk visible.

## Demo walkthrough

1. Open **Specialty Valves** and explain its spend, AVL coverage, OTIF, and risk.
2. Show its Kraljic position and the Strategic sourcing route.
3. Use the Game Theory Lens to explain why a repeated partnership fits better than a one-shot auction.
4. Adjust the Nash bargaining inputs and discuss BATNAs, surplus, and bargaining power.
5. Compare supplier scorecards and risk-adjusted award scenarios.
6. Download the executive memo and show its next three category-manager actions.
7. Switch to **MRO Pumps** to show the Leverage route and competitive RFQ simulator.

See [docs/demo_script.md](docs/demo_script.md) for a timed three-minute interview narrative.

## How to run on Windows PowerShell

The tested setup uses `uv` and a local virtual environment:

```powershell
cd C:\Users\jayes\Desktop\supplier-portfolio-strategy-lab
uv venv .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
.venv\Scripts\streamlit.exe run app\streamlit_app.py
```

Open the local URL shown in the terminal, normally `http://localhost:8501`.

If the virtual environment is already prepared, only the final command is needed.

## Test commands

```powershell
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m compileall -q src app tests
```

The suite covers segmentation, quadrant posture mapping, the strategy router, supplier scorecards, allocation math, capacity feasibility, Nash bargaining, competitive tension, memo content, determinism, and Streamlit rendering.

## Project structure

```text
supplier-portfolio-strategy-lab/
|-- app/
|   `-- streamlit_app.py
|-- data/
|   `-- supplier_portfolio.csv
|-- docs/
|   |-- demo_script.md
|   |-- methodology.md
|   `-- screenshots/
|       `-- README.md
|-- src/
|   |-- allocation.py
|   |-- kraljic.py
|   |-- memo.py
|   |-- scorecards.py
|   `-- strategy.py
|-- tests/
|   |-- test_allocation.py
|   |-- test_app.py
|   |-- test_kraljic.py
|   |-- test_memo.py
|   |-- test_scorecards.py
|   `-- test_strategy.py
|-- .gitignore
|-- LICENSE
|-- README.md
`-- requirements.txt
```

## Roadmap

Future portfolio phases may add:

- CSV upload with schema validation
- Sensitivity sliders for scoring weights and TCO assumptions
- Full reverse auction optimizer
- Full Nash bargaining scenario builder
- Supplier network resilience stress tester
- Power BI export
- Optional Claude/OpenAI memo generation later

These are roadmap items only. The current project has no deployment, database, authentication, SaaS features, live procurement integration, real company data, or live AI API usage.

## Disclaimer

Bayou Specialty Chemicals, its suppliers, and all figures are fictional. The models are transparent sourcing-planning aids, not accounting forecasts, legal advice, or production award approvals.
