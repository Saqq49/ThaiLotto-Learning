import pandas as pd
import numpy as np
from scipy import stats


MONTH_NAMES = {1: "ม.ค.", 2: "ก.พ.", 3: "มี.ค.", 4: "เม.ย.", 5: "พ.ค.", 6: "มิ.ย.",
               7: "ก.ค.", 8: "ส.ค.", 9: "ก.ย.", 10: "ต.ค.", 11: "พ.ย.", 12: "ธ.ค."}

DOW_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def compute_monthly_frequency(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for month in range(1, 13):
        sub = df[df["Month"] == month]
        counts = sub["Last_2"].value_counts()
        row = {f"{i:02d}": counts.get(f"{i:02d}", 0) for i in range(100)}
        row["Month"] = month
        rows.append(row)
    result = pd.DataFrame(rows).set_index("Month")
    return result


def compute_dow_distribution(df: pd.DataFrame) -> pd.Series:
    dow_counts = df["Day_of_Week"].value_counts()
    ordered = pd.Series({d: dow_counts.get(d, 0) for d in DOW_ORDER})
    return ordered


def chi_squared_monthly(df: pd.DataFrame) -> tuple[float, float]:
    table = compute_monthly_frequency(df)
    if table.empty or table.values.sum() == 0:
        return 0.0, 1.0
    # Add Laplace smoothing (+1) to avoid zero cells
    smoothed = table.values + 1
    try:
        chi2, p, _, _ = stats.chi2_contingency(smoothed)
    except ValueError:
        return 0.0, 1.0
    return float(chi2), float(p)


def chi_squared_dow(df: pd.DataFrame) -> tuple[float, float]:
    dow_counts = compute_dow_distribution(df)
    observed = dow_counts.values
    if observed.sum() == 0:
        return 0.0, 1.0
    expected = np.full(len(observed), observed.mean())
    chi2, p = stats.chisquare(observed, f_exp=expected)
    return float(chi2), float(p)


def monthly_number_summary(df: pd.DataFrame, number: str) -> pd.DataFrame:
    rows = []
    for month in range(1, 13):
        sub = df[df["Month"] == month]
        count = (sub["Last_2"] == number).sum()
        total = len(sub)
        rows.append({
            "Month": MONTH_NAMES[month],
            "Draws": total,
            "Hits": int(count),
            "Rate_%": round(count / total * 100, 1) if total > 0 else 0,
        })
    return pd.DataFrame(rows)
