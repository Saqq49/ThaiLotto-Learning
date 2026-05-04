import numpy as np
import pandas as pd


def compute_last2_heatmap_matrix(freq: pd.Series) -> np.ndarray:
    matrix = np.zeros((10, 10), dtype=int)
    for num_str, count in freq.items():
        if len(str(num_str)) == 2:
            r, c = int(str(num_str)[0]), int(str(num_str)[1])
            matrix[r][c] = count
    return matrix


def compute_max_drawdown_per_number(df: pd.DataFrame) -> pd.DataFrame:
    results = []
    draws = df["Last_2"].tolist()
    dates = df["Draw_Date"].tolist()
    total = len(draws)

    for num in [f"{i:02d}" for i in range(100)]:
        appearances = [i for i, d in enumerate(draws) if d == num]
        if not appearances:
            max_gap = total
            last_seen = None
        else:
            gaps = []
            if appearances[0] > 0:
                gaps.append(appearances[0])
            for j in range(1, len(appearances)):
                gaps.append(appearances[j] - appearances[j - 1] - 1)
            current_gap = total - appearances[-1] - 1
            max_gap = max(gaps) if gaps else 0
            last_seen = dates[appearances[-1]]
        results.append({
            "Number": num,
            "Max_Gap": max_gap,
            "Current_Gap": total - (appearances[-1] + 1) if appearances else total,
            "Total_Appearances": len(appearances),
            "Last_Seen": last_seen,
        })

    return pd.DataFrame(results).sort_values("Max_Gap", ascending=False).reset_index(drop=True)


def get_hot_cold_numbers(freq: pd.Series, top_n: int = 10) -> tuple[pd.Series, pd.Series]:
    hot = freq.sort_values(ascending=False).head(top_n)
    cold = freq.sort_values(ascending=True).head(top_n)
    return hot, cold


def compute_rolling_frequency(df: pd.DataFrame, number: str, window: int = 24) -> pd.DataFrame:
    df = df.copy().sort_values("Draw_Date")
    df["hit"] = (df["Last_2"] == number).astype(int)
    df["rolling_rate"] = df["hit"].rolling(window, min_periods=1).mean() * 100
    return df[["Draw_Date", "hit", "rolling_rate"]]
