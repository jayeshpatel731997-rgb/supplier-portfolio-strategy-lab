# Screenshot Capture Guide

This folder holds the portfolio screenshots referenced by the repository [README](../../README.md). The images are captured manually so the published screenshots reflect the actual Streamlit experience and do not imply an automated deployment.

The folder is already tracked by this guide, so a `.gitkeep` file is not needed.

## Before capturing

1. Start the app from the repository root:

   ```powershell
   .venv\Scripts\streamlit.exe run app\streamlit_app.py
   ```

2. Open the local URL shown by Streamlit, normally `http://localhost:8501`.
3. Use a desktop viewport around 1440 x 1000 or larger at 100% browser zoom.
4. Keep the Streamlit sidebar open so the selected category and decision flow are visible.
5. Use only the included synthetic Bayou Specialty Chemicals data.
6. Crop out browser bookmarks, personal profiles, notifications, unrelated tabs, and local filesystem details.

## Required screenshots

Save each image as PNG under the exact filename below.

| Filename | Category | Capture focus |
|---|---|---|
| `01_executive_overview.png` | Specialty Valves | Page title, category selector, and category-level KPIs |
| `02_kraljic_strategy_router.png` | Specialty Valves | Strategic quadrant card and full Kraljic portfolio matrix |
| `03_game_theory_lens.png` | Specialty Valves | Recommended sourcing game, buyer objective, tactics, warning, and next action |
| `04_supplier_scorecards.png` | Specialty Valves | Full supplier scorecard table with rank, scores, and AVL status |
| `05_award_allocation.png` | Specialty Valves | Recommended split, risk-adjusted value, risk avoided, and scenario table |
| `06_nash_bargaining.png` | Specialty Valves | Nash inputs, surplus split, recommended values, and negotiation posture |
| `07_reverse_auction_simulator.png` | MRO Pumps | Competitive RFQ inputs, expected savings, TCO-adjusted award value, and warning |
| `08_executive_memo.png` | Specialty Valves | Memo heading, sourcing game, TCO explanation, and next three actions |

## Suggested capture order

1. Select **Specialty Valves** and capture files 01 through 06.
2. Scroll to the executive memo and capture file 08.
3. Select **MRO Pumps**, open the competitive-tension module, and capture file 07.
4. Return to the GitHub README preview and confirm all eight images render at a readable size.

## Image quality checklist

- Use consistent browser width, zoom, and crop margins.
- Keep headings and units visible; avoid cutting tables mid-row.
- Preserve enough surrounding interface to show that each result comes from the app.
- Check that supplier names and category labels remain legible on a normal laptop screen.
- Do not add claims, logos, real supplier data, API keys, or company-confidential information.
- Use descriptive alt text in the root README if an image or filename changes.

## Add the completed images

After capture, verify the filenames and stage only the intended PNG files:

```powershell
Get-ChildItem docs\screenshots\*.png | Select-Object Name,Length
git add docs\screenshots\*.png
```

The root README already contains the Markdown image references, so no additional README edit is required when the files are added with these names.
