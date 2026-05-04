import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from lotto.data_loader import load_data
from lotto.theme import CRIMSON, GOLD, GOLD_DARK, apply_layout, inject_css, render_metric


st.set_page_config(page_title="ส่องโพยสถิติ", page_icon="📋", layout="wide")
inject_css()

# Load data
df = st.session_state["df"] if "df" in st.session_state else load_data()
if df.empty:
    st.error("ไม่พบข้อมูล")
    st.stop()

st.title("📋 ส่องโพยสถิติ")
st.markdown("คลังข้อมูลสถิติสลากกินแบ่งรัฐบาล — เช็กให้ชัวร์ก่อนเริ่มวิเคราะห์")

# Prepare data
df = df.copy().sort_values("Draw_Date").reset_index(drop=True)
df["Draw_Date"] = pd.to_datetime(df["Draw_Date"])

# Metrics calculation
total_draws = len(df)
date_min = df["Draw_Date"].min()
date_max = df["Draw_Date"].max()

# Integrity Score calculation (Essential fields: Draw_Date, Prize_1, Last_2)
essential_cols = ["Draw_Date", "Prize_1", "Last_2"]
total_cells = total_draws * len(essential_cols)
missing_cells = df[essential_cols].isna().sum().sum()
integrity_score = ((total_cells - missing_cells) / total_cells) * 100

# Latest result
latest = df.iloc[-1]

# Render Top Metrics
m_cols = st.columns(4)
with m_cols[0]:
    render_metric("งวดทั้งหมด", f"{total_draws:,}")
with m_cols[1]:
    render_metric("ช่วงเวลา", f"{date_min.year} - {date_max.year}")
with m_cols[2]:
    render_metric("Integrity Score", f"{integrity_score:.1f}%")
with m_cols[3]:
    render_metric("งวดล่าสุด", latest["Draw_Date"].strftime("%d/%b/%y"))

st.markdown("---")

# Quality Checks
duplicate_dates = int(df["Draw_Date"].duplicated().sum())
invalid_last2 = int((~df["Last_2"].astype(str).str.match(r"^\d{2}$", na=False)).sum())
invalid_prize1 = int((~df["Prize_1"].astype(str).str.match(r"^\d{6}$", na=False)).sum())
missing_3digit = int(df["Last_3"].isna().sum())

left, right = st.columns([1, 1])

with left:
    st.subheader("🛡️ Data Integrity Status")
    quality_rows = [
        {"Check": "Duplicate Dates", "Result": "✅ PASS" if duplicate_dates == 0 else "⚠️ WARN", "Detail": f"{duplicate_dates} duplicate rows"},
        {"Check": "Last 2 Format", "Result": "✅ PASS" if invalid_last2 == 0 else "❌ FAIL", "Detail": f"{invalid_last2} invalid rows"},
        {"Check": "Prize 1 Format", "Result": "✅ PASS" if invalid_prize1 == 0 else "❌ FAIL", "Detail": f"{invalid_prize1} invalid rows"},
        {"Check": "Missing 3-Digits", "Result": "ℹ️ INFO", "Detail": f"{missing_3digit} records (Expected for older data)"},
    ]
    st.table(pd.DataFrame(quality_rows))

with right:
    st.subheader("🚩 Historical Milestones")
    st.info("""
    **Sep 2015: First 3-Digits Introduction**
    เริ่มมีการประกาศรางวัล 'เลขหน้า 3 ตัว' 2 รางวัล แทนที่ 'เลขท้าย 3 ตัว' จากเดิม 4 รางวัล เหลือ 2 รางวัล
    
    **Dec 2006: Data Boundary**
    ข้อมูลเริ่มต้นเก็บสถิติเชิงลึกตั้งแต่เดือนธันวาคม 2006 เพื่อความแม่นยำของ Model
    
    **May 2026: Prediction Window**
    Data ล่าสุดครอบคลุมถึงงวดปัจจุบัน พร้อมสำหรับการทำ AI Reality Check
    """)

st.markdown("---")

# Visualization: Draws per Year
st.subheader("📈 Historical Data Coverage")
df["Year"] = df["Draw_Date"].dt.year
annual_draws = df.groupby("Year").size().reset_index(name="Draws")

fig_annual = go.Figure(go.Bar(
    x=annual_draws["Year"],
    y=annual_draws["Draws"],
    marker_color=CRIMSON,
    hovertemplate="ปี: %{x}<br>จำนวนงวด: %{y}<extra></extra>",
))
fig_annual = apply_layout(
    fig_annual,
    title="จำนวนการออกรางวัลรายปี",
    xaxis_title="ปี (พ.ศ. / ค.ศ.)",
    yaxis_title="จำนวนงวด",
    height=360,
)
st.plotly_chart(fig_annual, width="stretch")

# Tabs for Details
tab_sample, tab_schema, tab_gaps = st.tabs(["📄 Latest Records", "📂 Data Schema", "⚠️ Anomalies"])

with tab_sample:
    st.dataframe(df.tail(15).sort_values("Draw_Date", ascending=False), width="stretch", hide_index=True)

with tab_schema:
    schema = pd.DataFrame({
        "Field": df.columns,
        "Type": [str(t) for t in df.dtypes],
        "Non-Null": [int(df[c].count()) for c in df.columns],
        "Example": [str(df[c].dropna().iloc[-1]) if not df[c].dropna().empty else "N/A" for c in df.columns],
    })
    st.dataframe(schema, width="stretch", hide_index=True)

with tab_gaps:
    gaps = df[["Draw_Date"]].copy()
    gaps["Gap"] = gaps["Draw_Date"].diff().dt.days
    anomalies = gaps[gaps["Gap"] > 25]
    if not anomalies.empty:
        st.warning(f"พบช่วงห่างระหว่างงวดผิดปกติ (> 25 วัน) จำนวน {len(anomalies)} รายการ")
        st.dataframe(anomalies, width="stretch")
    else:
        st.success("ไม่พบช่องว่างข้อมูล (Gaps) ที่ผิดปกติ")
