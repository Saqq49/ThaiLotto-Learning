import pandas as pd
import numpy as np


def frequency_predictor(df: pd.DataFrame, top_n: int = 5) -> list[tuple[str, float]]:
    counts = df["Last_2"].value_counts()
    all_nums = [f"{i:02d}" for i in range(100)]
    freq = pd.Series({num: counts.get(num, 0) for num in all_nums}, dtype=float)
    total = freq.sum()
    if total == 0:
        probs = pd.Series({num: 1 / 100 for num in all_nums}, dtype=float)
    else:
        probs = (freq + 1) / (total + 100)  # Laplace smoothing
    top = probs.sort_values(ascending=False, kind="stable").head(top_n)
    return list(zip(top.index.tolist(), top.values.tolist()))


def overdue_predictor(df: pd.DataFrame, top_n: int = 5) -> list[tuple[str, float]]:
    draws = df["Last_2"].tolist()
    total = len(draws)
    last_seen = {}
    for i, num in enumerate(draws):
        last_seen[num] = i
    gaps = {}
    for num_int in range(100):
        num = f"{num_int:02d}"
        gaps[num] = total - last_seen.get(num, -1) - 1
    gap_series = pd.Series(gaps)
    max_gap = gap_series.max()
    scores = gap_series / max_gap if max_gap > 0 else gap_series
    top = scores.sort_values(ascending=False).head(top_n)
    return list(zip(top.index.tolist(), top.values.tolist()))


def recency_weighted_predictor(df: pd.DataFrame, top_n: int = 5, decay: float = 0.95) -> list[tuple[str, float]]:
    draws = df["Last_2"].tolist()
    n = len(draws)
    weights = np.array([decay ** (n - 1 - i) for i in range(n)])
    scores = {f"{i:02d}": 0.0 for i in range(100)}
    for i, num in enumerate(draws):
        if num in scores:
            scores[num] += weights[i]
    score_series = pd.Series(scores)
    total = score_series.sum()
    if total > 0:
        score_series = score_series / total
    top = score_series.sort_values(ascending=False).head(top_n)
    return list(zip(top.index.tolist(), top.values.tolist()))


def random_predictor(top_n: int = 5, seed: int | None = None) -> list[tuple[str, float]]:
    rng = np.random.default_rng(seed)
    nums = rng.choice([f"{i:02d}" for i in range(100)], size=top_n, replace=False)
    return [(n, 1 / 100) for n in nums]


PREDICTORS = {
    "Frequency": frequency_predictor,
    "Overdue": overdue_predictor,
    "Recency-Weighted": recency_weighted_predictor,
}
