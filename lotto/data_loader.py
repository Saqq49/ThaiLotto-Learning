import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

PROCESSED_PATH = Path(__file__).parent.parent / "data" / "processed" / "lottery_results.parquet"


@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    if not PROCESSED_PATH.exists():
        st.error("ไม่พบข้อมูล กรุณารัน `.venv/bin/python -m lotto.scraper` ก่อน")
        return pd.DataFrame()

    df = pd.read_parquet(PROCESSED_PATH)
    df["Draw_Date"] = pd.to_datetime(df["Draw_Date"])
    df["Day_of_Week"] = df["Draw_Date"].dt.strftime("%A")
    df["Month"] = df["Draw_Date"].dt.month

    for col, width in [("Prize_1", 6), ("Last_2", 2), ("First_3", 3), ("Last_3", 3)]:
        if col in df.columns:
            if col in ("First_3", "Last_3"):
                df[col] = df[col].fillna("").astype(str)
            else:
                df[col] = df[col].fillna("").astype(str).str.zfill(width)

    df = _validate(df)
    return df.sort_values("Draw_Date").reset_index(drop=True)


def _validate(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df[df["Last_2"].str.match(r"^\d{2}$", na=False)]
    df = df[df["Prize_1"].str.match(r"^\d{6}$", na=False)]
    df = df.drop_duplicates("Draw_Date")
    after = len(df)
    if before != after:
        st.warning(f"กรองข้อมูลผิดปกติออก {before - after} แถว")
    return df


@st.cache_data
def compute_last2_frequency(df: pd.DataFrame) -> pd.Series:
    all_nums = pd.Series([f"{i:02d}" for i in range(100)])
    counts = df["Last_2"].value_counts()
    freq = all_nums.map(counts).fillna(0).astype(int)
    freq.index = all_nums
    return freq


def filter_by_date(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    return df[(df["Draw_Date"] >= start) & (df["Draw_Date"] <= end)]
