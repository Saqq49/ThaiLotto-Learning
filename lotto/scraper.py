import requests
import pandas as pd
from datetime import date, timedelta
from pathlib import Path
import json
import time
import ast

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_PATH = Path(__file__).parent.parent / "data" / "processed" / "lottery_results.parquet"

RAYRIFFY_API = "https://lotto.api.rayriffy.com/date/{date}"
GITHUB_CSV_URL = "https://raw.githubusercontent.com/heart/Data-Set-Thai-Lotto/master/lotto.csv"
HEADERS = {"User-Agent": "Mozilla/5.0 (LottoDashboard/1.0)", "Accept-Language": "th-TH,th;q=0.9"}


def build_draw_dates(start: str = "2015-01-01") -> list[str]:
    dates = []
    current = date.fromisoformat(start)
    today = date.today()
    while current <= today:
        if current.day in (1, 16):
            dates.append(current.isoformat())
        current += timedelta(days=1)
    return dates


def _fetch_rayriffy(draw_date: str, session: requests.Session) -> dict | None:
    url = RAYRIFFY_API.format(date=draw_date)
    try:
        resp = session.get(url, timeout=10, headers=HEADERS)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "ok":
            return None
        return data.get("response", {})
    except Exception:
        return None


def _parse_response(draw_date: str, raw: dict) -> dict | None:
    try:
        prize1 = str(raw.get("prizeFirst", {}).get("number", [""])[0]).zfill(6)
        last2 = str(raw.get("prizeLastTwo", {}).get("number", [""])[0]).zfill(2)

        first3_list = raw.get("prizeFrontThree", {}).get("number", [])
        last3_list = raw.get("prizeLastThree", {}).get("number", [])

        first3 = ",".join(str(n).zfill(3) for n in first3_list) if first3_list else ""
        last3 = ",".join(str(n).zfill(3) for n in last3_list) if last3_list else ""

        dt = pd.to_datetime(draw_date)
        return {
            "Draw_Date": draw_date,
            "Day_of_Week": dt.strftime("%A"),
            "Month": dt.month,
            "Prize_1": prize1,
            "Last_2": last2,
            "First_3": first3,
            "Last_3": last3,
            "Source_URL": RAYRIFFY_API.format(date=draw_date),
        }
    except Exception:
        return None


def run_scraper(start: str = "2015-01-01", delay: float = 0.3) -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)

    existing = _load_existing()
    existing_dates = set(existing["Draw_Date"].tolist()) if not existing.empty else set()

    all_dates = build_draw_dates(start)
    missing = [d for d in all_dates if d not in existing_dates]

    if not missing:
        print(f"Already up to date ({len(existing)} draws).")
        return existing

    print(f"Fetching {len(missing)} missing draws...")
    records = []
    session = requests.Session()

    for i, draw_date in enumerate(missing):
        raw = _fetch_rayriffy(draw_date, session)
        if raw:
            record = _parse_response(draw_date, raw)
            if record:
                records.append(record)
                raw_file = RAW_DIR / f"{draw_date}.json"
                raw_file.write_text(json.dumps(raw, ensure_ascii=False))
        if (i + 1) % 20 == 0:
            print(f"  {i + 1}/{len(missing)} done")
        time.sleep(delay)

    if records:
        new_df = pd.DataFrame(records)
        combined = pd.concat([existing, new_df], ignore_index=True)
        combined = combined.drop_duplicates("Draw_Date").sort_values("Draw_Date").reset_index(drop=True)
        combined.to_parquet(PROCESSED_PATH, index=False)
        print(f"Saved {len(combined)} total draws to {PROCESSED_PATH}")
        return combined

    print(f"No new records fetched. Returning {len(existing)} existing draws.")
    return existing


def _load_existing() -> pd.DataFrame:
    if PROCESSED_PATH.exists():
        return pd.read_parquet(PROCESSED_PATH)
    return pd.DataFrame()


def load_from_raw_json(start: str = "2015-01-01") -> pd.DataFrame:
    """Build DataFrame from already-downloaded raw JSON files (offline mode)."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    for f in sorted(RAW_DIR.glob("*.json")):
        draw_date = f.stem
        try:
            raw = json.loads(f.read_text())
            record = _parse_response(draw_date, raw)
            if record:
                records.append(record)
        except Exception:
            continue
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records).sort_values("Draw_Date").reset_index(drop=True)
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PROCESSED_PATH, index=False)
    return df


def load_from_github() -> pd.DataFrame:
    """Download and parse the heart/Data-Set-Thai-Lotto dataset from GitHub."""
    print("Downloading from GitHub fallback dataset...")
    resp = requests.get(GITHUB_CSV_URL, timeout=30, headers=HEADERS)
    resp.raise_for_status()

    from io import StringIO
    raw_csv = pd.read_csv(StringIO(resp.text))

    records = []
    def parse_list(val) -> str:
        try:
            lst = ast.literal_eval(str(val).strip())
            return ",".join(str(x).zfill(3) for x in lst)
        except Exception:
            return ""

    for _, row in raw_csv.iterrows():
        try:
            draw_date = str(row.get("date", "")).strip()
            if not draw_date or len(draw_date) != 10:
                continue

            # prize_1st is a float like 97863.0 → "097863"
            prize1_raw = row.get("prize_1st", None)
            if pd.isna(prize1_raw):
                continue
            prize1 = str(int(float(prize1_raw))).zfill(6)
            if not prize1.isdigit() or len(prize1) != 6:
                continue

            # prize_2digits is a float like 21.0 → "21"
            last2_raw = row.get("prize_2digits", None)
            if pd.isna(last2_raw):
                continue
            last2 = str(int(float(last2_raw))).zfill(2)
            if len(last2) != 2:
                continue

            first3 = parse_list(row.get("prize_pre_3digit", "[]"))
            last3 = parse_list(row.get("prize_sub_3digits", "[]"))

            dt = pd.to_datetime(draw_date)
            records.append({
                "Draw_Date": draw_date,
                "Day_of_Week": dt.strftime("%A"),
                "Month": dt.month,
                "Prize_1": prize1,
                "Last_2": last2,
                "First_3": first3,
                "Last_3": last3,
                "Source_URL": GITHUB_CSV_URL,
            })
        except Exception:
            continue

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df = df.sort_values("Draw_Date").reset_index(drop=True)
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PROCESSED_PATH, index=False)
    print(f"Saved {len(df)} draws from GitHub dataset to {PROCESSED_PATH}")
    return df


if __name__ == "__main__":
    df = load_from_github()
    print(df.tail())
    print(f"\nTotal: {len(df)} draws, columns: {list(df.columns)}")
