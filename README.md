# Thai Lottery Statistical Dashboard

Interactive Streamlit dashboard for exploring Thai Government Lottery history, testing common lottery beliefs, and showing the limits of prediction/backtesting under random outcomes.

This is an educational statistics project, not a lottery prediction product.

## Current Status

- Dataset: 461 draws, `2006-12-30` to `2026-05-02`
- App: Streamlit + Plotly
- Core scope: `Last_2` analysis first
- Tests: `21 passed` in the current Codex environment

## Features

- Data Overview: date range, source summary, schema, quality checks, draw coverage
- Historical Visualizer: `00-99` heatmap, hot/cold numbers, max gap
- Prediction Lab: transparent baseline methods only
- AI Reality Check: walk-forward accuracy vs random baseline
- Strategy Backtester: official payout assumptions, equity curve, PnL, drawdown
- Seasonality: month/day-of-week checks and chi-square summaries

## Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Architecture note for Apple Silicon:

- Build and use `.venv` from the same terminal architecture.
- If NumPy/Pandas fails with an architecture mismatch, delete `.venv` and recreate it from the terminal you will use to run the app.

## Run

```bash
.venv/bin/python -m streamlit run app.py
```

If port `8501` is busy:

```bash
.venv/bin/python -m streamlit run app.py --server.port 8502
```

## Test

```bash
.venv/bin/python -m pytest -q
```

## Data

Processed data lives at:

```text
data/processed/lottery_results.parquet
```

Manual 2025-2026 updates are stored at:

```text
data/raw/update_2025_2026.csv
```

To merge manual updates into the processed dataset:

```bash
.venv/bin/python scripts/merge_updates.py
```

To run a repeatable data quality check:

```bash
.venv/bin/python scripts/check_data_quality.py
```

## Deployment

For Streamlit Community Cloud:

- Entry point: `app.py`
- Python dependencies: `requirements.txt`
- Streamlit config: `.streamlit/config.toml`
- Ensure `data/processed/lottery_results.parquet` is included in the deployed repo.

## Important Caveats

- Historical frequency does not imply future probability.
- Predictor output is a method suggestion, not a winning forecast.
- Backtesting must use only past data for each simulated draw.
- Official payout assumptions should stay documented and separate from underground lottery odds.

## Collaboration Files

- `require.md`: original requirements
- `plan.md`: project plan
- `session.md`: latest progress and handoff status
- `lesson.md`: lessons learned across Claude, Codex, and Gemini
