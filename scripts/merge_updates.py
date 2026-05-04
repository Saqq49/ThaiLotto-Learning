import pandas as pd
from pathlib import Path

PROCESSED_PATH = Path("data/processed/lottery_results.parquet")
UPDATE_CSV = Path("data/raw/update_2025_2026.csv")

if not PROCESSED_PATH.exists():
    print("Processed data not found.")
    exit(1)

df_existing = pd.read_parquet(PROCESSED_PATH)
df_update = pd.read_csv(UPDATE_CSV)

# Convert types to match
df_update["Draw_Date"] = pd.to_datetime(df_update["Draw_Date"]).dt.date.astype(str)
df_update["Prize_1"] = df_update["Prize_1"].astype(str).str.zfill(6)
df_update["Last_2"] = df_update["Last_2"].astype(str).str.zfill(2)
df_update["Month"] = pd.to_datetime(df_update["Draw_Date"]).dt.month
df_update["Day_of_Week"] = pd.to_datetime(df_update["Draw_Date"]).dt.strftime("%A")
df_update["Source_URL"] = "Manual Search"

# Reorder columns to match existing
cols = df_existing.columns.tolist()
df_update = df_update[cols]

combined = pd.concat([df_existing, df_update], ignore_index=True)
combined = combined.drop_duplicates("Draw_Date").sort_values("Draw_Date").reset_index(drop=True)

combined.to_parquet(PROCESSED_PATH, index=False)
print(f"Merged successfully. Total draws: {len(combined)}")
print(f"Latest draw: {combined['Draw_Date'].max()}")
