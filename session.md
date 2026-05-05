# Session Handoff - Thai Lotto

## Purpose

This file is the current handoff for Claude, Codex, and Gemini. It should reflect the real local state, not older session claims. Update it before switching AI or before deployment.

## Current State

**Date:** 2026-05-05  
**Local review URL:** `http://localhost:8560`  
**Deployed URL:** `https://thailotto-learning-w3xpaw8apwaungtaktzkxd.streamlit.app/`  
**Deploy status:** Pushed to main — Streamlit Cloud redeploying.

The product is branded as **Thai Lotto**. It is an educational/statistical Streamlit dashboard, not a lottery prediction product.

## Current Product Rules

- `ทั่วไป` / `Math` is a presentation mode only.
  - `ทั่วไป`: plain Thai copy for everyday users.
  - `Math`: English/technical copy for users who want methodology, scores, formulas.
  - The mode must not change calculations, selected numbers, strategy results, model parameters, charts, or data.
- Sidebar feature labels change with mode (via JS MutationObserver).
- Sidebar controls must not be reintroduced. Feature controls belong in the main page body.
- Copy must not imply that frequent, overdue, or trending numbers are more likely to appear next draw.

## Page Order

1. `app.py` — Thai Lotto home
2. `pages/0_📋_ส่องโพยสถิติ.py` — Data Overview
3. `pages/1_🎲_คิดไม่ออก_เดี๋ยวเลือกให้.py` — Selection Engine
4. `pages/2_📊_เลขไหนฮิต_เลขไหนดับ.py` — Frequency Distribution
5. `pages/3_🔮_สำนักคำนวณเลขเด็ด.py` — Predictor Lab
6. `pages/4_🎯_AI_จะแม่นจริงไหม.py` — Walk-Forward Validation
7. `pages/5_💰_ลองแทงทิพย์_รวยหรือเจ๊ง.py` — Strategy Backtest

Calendar Effect Test (`hidden_pages/6_📅_อาถรรพ์เลขตามปฏิทิน.py`) is intentionally hidden — move back into `pages/` to restore.

## Work Completed This Session

### Metric Cards — Equal Width Fix
- Replaced `st.columns()` + `render_metric()` with `render_metrics_row()` in `app.py` and `pages/0`.
- `render_metrics_row()` renders a single HTML flex row with `flex:1 1 0; min-width:0` per card — guarantees equal width regardless of content.
- Outer div has class `metrics-row` so responsive CSS can target it.

### Data Overview (pages/0)
- Bar chart colorscale changed from CRIMSON to gold gradient based on y-value (short bars = dim gold, tall bars = bright gold).
- "2006 - 2026" changed to "2006–2026" (en-dash) to reduce character width.

### Selection Engine (pages/1)
- Math mode: all labels converted to English (radio options, button, spinner, card subtitle, table columns, rationale text, footer).
- Replaced "Statistical Rank Band" selector with **Algorithm** selector: Frequency / Overdue / Recency-Weighted / Ensemble — matches Predictor Lab.
- Candidate Count max reduced from 10 → **5**.
- Statistical mode now **randomly samples `num_count` from Top 20** of chosen algorithm (no duplicates). Rationale shows pool rank + sub-ranks across all 3 algorithms.

### Frequency Distribution (pages/2)
- Heatmap colorscale: ink → dark crimson → crimson → orange-amber → gold → bright gold.
- Gold border around heatmap (Plotly shape layer).
- Max Gap bar chart: gold colorscale by y-value.

### Walk-Forward Validation (pages/4)
- ทั่วไป mode rewritten in plain Thai: "จับโกหก AI", "สุ่มตาบอด", "ถ้าสุ่มตาบอด X%", "อัตราถูก (%)", "เลือกสูตรที่อยากดู", "เริ่มจับโกหก!".
- Test result boxes and conclusion use plain conversational Thai.

### Strategy Backtest (pages/5)
- **Bug fix**: `fillcolor=f"{CRIMSON}11"` produced 8-digit hex (`#7A181811`) — Plotly does not support this. Changed to `rgba(122,24,24,0.12)`. Charts now display correctly.
- Math mode: all labels English — strategy options, prize types, KPI labels, chart names, table columns, spinner, footer.
- `longest_losing_streak` value uses `mode_text` for "งวด"/"draws".

### Calendar Effect Test (pages/6)
- Explanations rewritten: plain Thai explanation of chi-squared test, p-value meaning, per-tab context.
- Heatmap colorscale unified with Frequency Matrix theme (ink → crimson → gold).
- Node drilldown bar chart also uses gold colorscale.
- **Page hidden**: moved to `hidden_pages/` — not shown in sidebar. Restore by moving back to `pages/`.

### Sidebar Credit
- `Blackcat.jpg` (project root) embedded as base64 in sidebar bottom-left.
- Shows circular avatar (38px, gold border) + "Design & Dev / **By Blackcat**".
- Implemented in `_sidebar_credit_html()` in `lotto/theme.py`, called from `init_persona()`.

### Responsive Design
Three breakpoints added to `CUSTOM_CSS`:

| Breakpoint | Metric cards | Notes |
|---|---|---|
| ≤ 1024px | slightly smaller | fluid font via clamp() |
| ≤ 768px | **2 per row** | tabs smaller, panels less padding |
| ≤ 480px | **1 per row** | main padding reduced, touch-friendly buttons (min-height 44px), tabs scroll horizontally |

## Verification

- `.venv/bin/python -m compileall app.py lotto pages` — passed, no errors.
- pytest blocked by numpy arch mismatch in local venv (x86_64 vs arm64) — pre-existing environment issue, not code-related. Streamlit Cloud runs fine.

## Known Non-Blocking Issues

- `pyarrow` sandbox `sysctlbyname` warnings in some shells.
- `st.components.v1.html` deprecation warning (needed for persona persistence until 2026-06-01).
- numpy local venv arch mismatch — tests cannot run locally but deploy works.

## Guardrails For Next AI

- Do not make `ทั่วไป` / `Math` change computation.
- Do not change persona radio back to `key="persona"`.
- Do not assign `st.session_state.persona = st.session_state._persona_selector` after `st.radio()`.
- Do not remove the parent-window persistence bridge unless page-to-page Math persistence is verified in browser.
- Do not replace the sidebar label rewrite with server-side page titles.
- Do not reintroduce sidebar controls.
- Keep Plotly colors valid (`#RRGGBB` or `rgba(...)`); **never use 8-digit hex** (`#RRGGBBAA`).
- `render_metrics_row()` must keep `class="metrics-row"` on the outer div for responsive CSS.
- Calendar page is intentionally hidden in `hidden_pages/` — do not delete it.

## Git Notes

Use `git add -A` when committing — page renames/deletes/adds will be missed otherwise.

Untracked project docs in repo root (committed alongside code):
- `claude.md`, `codex.md`, `gemini.md`, `lesson.md`, `plan.md`, `require.md`
