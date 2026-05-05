# Lotto Dashboard - Project Plan

## Project Overview

**Project**: Thai Lottery Interactive Dashboard  
**Goal**: Build an interactive dashboard for exploring Thai Government Lottery results over the last 5-10 years, testing common beliefs with statistics, and demonstrating the practical limits of prediction and betting strategies.  
**Created**: 2026-05-04  
**Status**: Planning Phase

## Product Positioning

This project is an educational and analytical dashboard, not a lottery prediction product.

The main product message should be:

- Historical data can reveal frequencies, gaps, and visual patterns.
- These patterns do not prove that future lottery results are predictable.
- Any predictive model must be tested against simple random and rule-based baselines.
- Backtesting should show financial risk realistically, including losing streaks, maximum drawdown, and bankroll depletion.

## Core Objectives

1. Collect and clean Thai lottery historical results for approximately 5-10 years.
2. Focus the MVP on `Last_2` analysis because it has a clear outcome space of 100 values.
3. Visualize historical number behavior such as frequency, hot/cold numbers, and overdue numbers.
4. Create simple mathematical or statistical prediction methods as a controlled experiment.
5. Measure prediction accuracy with rolling backtests and compare against random baselines.
6. Simulate lottery buying strategies and show realistic financial outcomes.
7. Test seasonality beliefs by day of week and month using statistical tests.

## MVP Scope

The first release should focus on `Last_2` only.

Included in MVP:

- `Last_2` historical frequency analysis.
- `Last_2` heatmap from `00` to `99`.
- Hot, cold, overdue, and maximum gap metrics for `Last_2`.
- Transparent predictor baselines for `Last_2`.
- Reality-check backtesting using top-1, top-5, and top-10 accuracy.
- Strategy backtesting based on `Last_2` ticket assumptions.
- Month and weekday filters for `Last_2`.

Deferred until after MVP:

- `First_3` analysis.
- `Last_3` analysis.
- `Prize_1` analysis beyond basic descriptive display.
- Any ML model that is harder to explain than simple baseline methods.

## Recommended Dashboard Structure

### 1. Data Overview

Purpose: confirm that the dataset is complete and trustworthy before analysis.

Features:

- Date range summary.
- Total number of draws.
- Missing or duplicated draw checks.
- Latest draw in the dataset.
- Sample table of cleaned records.
- Basic distribution of draw days and months.

### 2. Historical Visualizer

Purpose: show what has happened historically without implying causation.

Features:

- Frequency heatmap for `Last_2` values from `00` to `99`.
- Hot numbers: numbers with the highest historical frequency.
- Cold numbers: numbers with the lowest historical frequency.
- Overdue numbers: numbers with the longest current gap since last appearance.
- Maximum gap / max drawdown by number: longest historical absence before reappearing.
- Rolling frequency chart for selected numbers.

Important caveat:

- Hot, cold, and overdue labels are descriptive only. They should not be presented as evidence that a number is more likely to appear next.

### 3. Prediction Lab

Purpose: generate candidate numbers using transparent mathematical rules, then treat them as hypotheses to test.

Recommended methods:

- Random baseline: select numbers uniformly from `00` to `99`.
- Frequency baseline: select the most frequent numbers from a rolling historical window.
- Overdue baseline: select numbers with the longest gap from recent draws.
- Recency-weighted probability: give more weight to recent draws.
- Simple ML demo: train a basic model only if it can be evaluated honestly with rolling validation.

Output:

- Suggested numbers for the next draw.
- Method used.
- Input window used.
- Top-k list, for example top 1, top 5, or top 10.
- Warning that suggestions are experimental and not reliable predictions.

Implementation rule:

- Every prediction shown to users must be produced using only data available before the target draw. This prevents look-ahead bias.

### 4. AI Prediction Reality Check

Purpose: show whether the prediction methods perform better than chance.

Metrics:

- Top-1 accuracy.
- Top-5 accuracy.
- Top-10 accuracy.
- Hit count by method.
- Expected random accuracy:
  - Top-1: approximately 1% for `Last_2`.
  - Top-5: approximately 5%.
  - Top-10: approximately 10%.
- Lift over random baseline.
- Rolling accuracy over time.

Evaluation approach:

- Use rolling backtesting.
- For each historical draw, train or calculate the method using only previous draws.
- Predict the target draw.
- Compare prediction against the actual result.
- Aggregate accuracy across all eligible draws.

Reality-check message:

- If a method does not beat the random baseline consistently, the dashboard should state this clearly.
- Even if a method beats random in a small sample, show confidence limits or sample-size warnings.

### 5. Lottery Strategy Backtester

Purpose: simulate financial outcomes and make risk visible.

Supported strategies:

- Buy the same fixed number every draw.
- Buy top-k numbers from a selected prediction method.
- Buy random numbers every draw.
- Buy overdue numbers.
- Martingale-style staking with strict bankroll and bet limits.
- Fixed budget per draw, for example 10 tickets per draw.

Required inputs:

- Initial bankroll.
- Ticket price.
- Prize payout for `Last_2`.
- Number of tickets per draw.
- Selected strategy.
- Backtest start and end dates.
- Maximum stake per draw.
- Stop condition when bankroll is insufficient.

Required outputs:

- Equity curve.
- Net PnL.
- Total amount spent.
- Total payout.
- Win rate.
- Maximum drawdown.
- Longest losing streak.
- Bankruptcy / ruin flag.
- Final bankroll.

Implementation rule:

- Strategy decisions must use only information available before each draw.
- Martingale must include bankroll constraints; unlimited doubling is not realistic.

### 6. Seasonality & Event Correlation

Purpose: test beliefs about dates, weekdays, months, and festival periods.

Features:

- Filter results by day of week.
- Filter results by month.
- Compare selected periods such as December or festival months.
- Show frequency differences across periods.
- Run chi-square test or permutation test where sample size allows.

Output:

- Observed frequency table.
- Expected frequency under randomness.
- p-value or simulation-based significance estimate.
- Plain-language conclusion:
  - "No statistically meaningful difference found."
  - "Possible difference observed, but sample size is small."
  - "Difference found in historical data, but this does not imply predictive power."

## Data Structure

Primary DataFrame columns:

| Column | Type | Description |
| --- | --- | --- |
| `Draw_Date` | date | Official lottery draw date |
| `Day_of_Week` | string | Day name derived from `Draw_Date` |
| `Month` | integer/string | Month derived from `Draw_Date` |
| `Prize_1` | string | First prize, stored as zero-padded 6 digits |
| `Last_2` | string | Last 2 digits, stored as zero-padded 2 digits |
| `First_3` | list/string | Front 3-digit prizes |
| `Last_3` | list/string | Last 3-digit prizes |
| `Source_URL` | string | Source page for traceability |
| `Scraped_At` | datetime | Data collection timestamp |

Data quality requirements:

- Preserve leading zeros for all prize numbers.
- Validate `Last_2` as exactly 2 digits.
- Validate `Prize_1` as exactly 6 digits.
- Normalize draw dates to a single timezone/date format.
- Detect duplicate draw dates.
- Detect missing expected draw periods.
- Keep raw scraped data separate from cleaned data.

## Data Source Plan

Planned approach:

1. **Primary candidate**: Use the [Rayriffy Thai Lotto API](https://lotto.api.rayriffy.com) for programmatic access to results in JSON format.
2. **Fallback/backfill candidate**: Use the `heart/Data-Set-Thai-Lotto` GitHub repository for bulk historical data from 2000-2024.
3. **Cross-checking**: Validate sampled draws against another public source or official result page before treating the dataset as trusted.
4. **Known cleanup requirement**: The `heart/Data-Set-Thai-Lotto` dataset may contain an incomplete/current row with `xxx`; importer must remove or quarantine invalid rows.
5. **Prize-tier validation**: Check for the "First 3 Digits" prize introduction in Sep 2015; data prior to this must handle the absence of this prize tier gracefully.
6. **Storage**: Store results in `data/processed/lottery_results.parquet` for efficient loading in Streamlit.
7. **Traceability**: Keep raw source snapshots and source metadata so result mismatches can be audited later.

## Technical Stack

### Application

- **Frontend/Backend**: **Streamlit** (Python). Selected for rapid development and native compatibility with Python data science libraries.
- **Visualization**: 
  - `Plotly`: For interactive heatmaps, line charts, equity curves, and frequency comparisons.
  - Add `streamlit-echarts` later only if calendar-style heatmaps or ECharts-specific interactions become necessary.
- **Data Processing**: `pandas` and `numpy`.
- **Statistics**: `scipy.stats` for randomness tests (Chi-Square, Uniform distribution comparisons).
- **Machine Learning**: `scikit-learn` for baseline comparison models.

### Storage

- Raw data: `data/raw/` (JSON snapshots from Rayriffy API).
- Cleaned data: `data/processed/lottery_results.parquet`.
- Backtest outputs: Cached using `@st.cache_data`.

### Suggested Project Structure

```text
.
├── app.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── cache/
├── lotto/
│   ├── data_loader.py
│   ├── scraper.py
│   ├── validation.py
│   ├── stats.py
│   ├── predictors.py
│   ├── backtest.py
│   └── plotting.py
├── tests/
│   ├── test_stats.py
│   ├── test_predictors.py
│   └── test_backtest.py
├── requirements.txt
└── README.md
```

## Statistical Guardrails

The dashboard must avoid implying that lottery numbers can be reliably predicted.

Required guardrails:

- Add visible disclaimers on prediction and backtesting pages.
- Always show random baseline performance next to model performance.
- Use rolling validation rather than evaluating on already-seen data.
- Show sample size warnings when results are based on few draws.
- Separate descriptive statistics from predictive claims.
- Use exact wording such as "suggested by this method" instead of "likely to win".

## Implementation Phases

### Phase 1: Data Foundation

- [ ] Verify Rayriffy API coverage and response stability.
- [ ] Verify fallback dataset coverage and invalid-row behavior.
- [ ] Document selected data source and fallback source.
- [ ] Build scraper or importer.
- [ ] Create raw and cleaned datasets.
- [ ] Add data validation checks.
- [ ] Build Data Overview page.

### Phase 2: Historical Statistics

- [ ] Implement frequency calculations.
- [ ] Implement current gap and maximum gap calculations.
- [ ] Build `Last_2` heatmap.
- [ ] Build hot/cold/overdue number tables.
- [ ] Add filters by date range, month, and day of week.

### Phase 3: Prediction Lab & Reality Check

- [ ] Implement random baseline.
- [ ] Implement frequency baseline.
- [ ] Implement overdue baseline.
- [ ] Implement recency-weighted method.
- [ ] Implement rolling backtest evaluator.
- [ ] Show top-k accuracy and random expected accuracy.
- [ ] Add plain-language conclusion for each method.

### Phase 4: Strategy Backtester

- [ ] Define ticket cost and payout assumptions.
- [ ] Implement fixed-number strategy.
- [ ] Implement top-k strategy from predictor outputs.
- [ ] Implement random strategy.
- [ ] Implement constrained Martingale strategy.
- [ ] Plot equity curve.
- [ ] Report PnL, win rate, maximum drawdown, losing streak, and bankruptcy flag.

### Phase 5: Seasonality Testing

- [ ] Add weekday and month filters.
- [ ] Add observed vs expected frequency views.
- [ ] Implement chi-square or permutation tests.
- [ ] Add statistical significance summary.

### Phase 6: Polish, Testing, and Deployment

- [ ] Add unit tests for statistics, predictors, and backtesting.
- [ ] Add Streamlit caching for data loading and expensive calculations.
- [ ] Improve responsive layout and visual hierarchy.
- [ ] Apply red-gold visual theme without reducing readability.
- [ ] Document assumptions, limitations, and setup steps.
- [ ] Prepare deployment configuration.

## UI Direction

Visual style:

- Red-gold theme inspired by Thai lottery and wealth symbolism.
- Use restrained contrast so charts remain readable.
- Avoid visual language that suggests guaranteed winning or secret knowledge.

Dashboard behavior:

- Sidebar filters for date range, method, top-k size, and strategy settings.
- Main content organized with tabs or pages.
- Interactive Plotly charts for heatmaps, equity curves, rolling accuracy, and frequency comparisons.
- Summary metric cards for key values such as total draws, hit rate, net PnL, and maximum drawdown.

## Success Criteria

- [ ] Dashboard loads historical lottery data correctly.
- [ ] Data validation catches malformed numbers, duplicates, and missing dates.
- [ ] Heatmap and frequency statistics are reproducible from the cleaned dataset.
- [ ] Prediction methods are evaluated with rolling backtests only.
- [ ] Accuracy is always compared with random baseline expectations.
- [ ] Strategy backtester prevents look-ahead bias.
- [ ] Financial simulations include bankroll limits and maximum drawdown.
- [ ] Seasonality claims are backed by statistical tests or clearly marked as inconclusive.
- [ ] UI communicates randomness and risk clearly.
- [ ] Core calculation modules have unit tests.

## Key Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Unreliable or inconsistent data source | Incorrect analysis | Store source URLs, validate schema, keep raw snapshots |
| Look-ahead bias | Misleading prediction/backtest results | Use rolling calculations based only on past draws |
| Small sample size | False patterns | Show sample warnings and baseline comparisons |
| User misinterprets predictions | Harmful financial assumptions | Use clear wording, disclaimers, and reality-check metrics |
| Martingale appears profitable in limited tests | Misleading financial risk | Enforce bankroll, bet limits, and ruin conditions |
| Overcomplicated ML | Low value and hard to explain | Start with transparent baselines before ML |

## Open Decisions

- Whether Rayriffy API is reliable enough as the primary source after verification.
- Which public or official source will be used for sampled cross-checking.
- Prize payout assumptions for strategy backtesting.
- Deployment target: local Streamlit, Streamlit Community Cloud, or another hosting platform.

## Notes

- Start with `Last_2` analysis because it has a manageable outcome space of 100 values.
- Treat `Prize_1` as mostly descriptive unless a much larger dataset is available.
- The strongest product insight is likely not "which number to buy", but "how quickly apparent patterns disappear under honest backtesting".
