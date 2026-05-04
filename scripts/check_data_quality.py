from pathlib import Path

import pandas as pd


PROCESSED_PATH = Path("data/processed/lottery_results.parquet")
REQUIRED_COLUMNS = ["Draw_Date", "Day_of_Week", "Month", "Prize_1", "Last_2", "First_3", "Last_3", "Source_URL"]


def validate_dataframe(df: pd.DataFrame) -> tuple[int, list[str]]:
    df = df.copy()
    df["Draw_Date"] = pd.to_datetime(df["Draw_Date"])

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    duplicate_dates = int(df["Draw_Date"].duplicated().sum())
    invalid_last2 = int((~df["Last_2"].astype(str).str.match(r"^\d{2}$", na=False)).sum())
    invalid_prize1 = int((~df["Prize_1"].astype(str).str.match(r"^\d{6}$", na=False)).sum())
    missing_source = int(df["Source_URL"].isna().sum() + (df["Source_URL"].astype(str).str.strip() == "").sum())

    lines = [
        "Thai Lottery dataset quality report",
        f"Rows: {len(df):,}",
        f"Date range: {df['Draw_Date'].min().date()} to {df['Draw_Date'].max().date()}",
        f"Required columns missing: {missing_columns or 'none'}",
        f"Duplicate draw dates: {duplicate_dates}",
        f"Invalid Last_2 rows: {invalid_last2}",
        f"Invalid Prize_1 rows: {invalid_prize1}",
        f"Rows missing Source_URL: {missing_source}",
        "",
        "Source counts:",
    ]
    for source, count in df["Source_URL"].fillna("Unknown").replace("", "Unknown").value_counts().items():
        lines.append(f"- {source}: {count}")

    failed = bool(missing_columns or duplicate_dates or invalid_last2 or invalid_prize1)
    return (1 if failed else 0), lines


def main(path: Path = PROCESSED_PATH) -> int:
    if not path.exists():
        print(f"FAIL: missing {path}")
        return 1

    status, lines = validate_dataframe(pd.read_parquet(path))
    print("\n".join(lines))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
