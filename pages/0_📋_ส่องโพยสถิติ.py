import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from lotto.data_loader import load_data
from lotto.theme import CRIMSON, GOLD, GOLD_DARK, GOLD_SOLID, GOLD_GRADIENT, apply_layout, inject_css, render_metrics_row, init_persona, render_explanation, mode_text, is_math_mode


st.set_page_config(page_title="ส่องโพยสถิติ", page_icon="📋", layout="wide")
inject_css()
init_persona()

# Load data
df = st.session_state["df"] if "df" in st.session_state else load_data()
if df.empty:
    st.error("ไม่พบข้อมูล")
    st.stop()

st.title(mode_text("📋 ส่องโพยสถิติ", "📋 Data Overview"))
st.markdown(mode_text(
    "คลังข้อมูลสถิติสลากกินแบ่งรัฐบาล เช็กให้ชัวร์ก่อนเริ่มวิเคราะห์",
    "Dataset coverage, schema integrity, and source completeness for downstream analysis.",
))

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
render_metrics_row([
    (mode_text("งวดทั้งหมด", "Total Draws"), f"{total_draws:,}"),
    (mode_text("เก็บสถิติตั้งแต่ปี", "Coverage Years"), f"{date_min.year}–{date_max.year}"),
    (mode_text("ความเป๊ะของข้อมูล", "Integrity Score"), f"{integrity_score:.1f}%"),
    (mode_text("งวดล่าสุด", "Latest Draw"), latest["Draw_Date"].strftime("%d/%b/%y")),
])

st.markdown("---")

layman_integrity = "เช็กความเนียนของโพย - ดูว่าข้อมูลที่เราเก็บมามันแหว่งตรงไหนไหม มีเลขที่พิมพ์ตกหรือหายไปหรือเปล่า ถ้าได้ 100% คือข้อมูลเต็มครบทุกงวด"
math_integrity = "Data completeness analysis over primary fields. The integrity score is the ratio of non-null required values to all required field slots in the dataset."
formula_integrity = r"Integrity Score = \frac{\sum_{j \in \mathcal{F}} \sum_{i=1}^{N} \mathbb{1}(x_{i,j} \neq \text{null})}{|\mathcal{F}| \times N} \times 100\%"
render_explanation(layman_integrity, math_integrity, formula_integrity)

st.markdown("---")

# Quality Checks
duplicate_dates = int(df["Draw_Date"].duplicated().sum())
invalid_last2 = int((~df["Last_2"].astype(str).str.match(r"^\d{2}$", na=False)).sum())
invalid_prize1 = int((~df["Prize_1"].astype(str).str.match(r"^\d{6}$", na=False)).sum())
missing_3digit = int(df["Last_3"].isna().sum())

left, right = st.columns([1, 1])

with left:
    st.subheader(mode_text("🛡️ เช็กความเรียบร้อยของข้อมูล", "🛡️ Data Quality Checks"))
    if is_math_mode():
        quality_rows = [
            {"Check": "Duplicate draw dates", "Status": "✅ None" if duplicate_dates == 0 else "⚠️ Found", "Detail": f"{duplicate_dates} rows"},
            {"Check": "Last_2 format", "Status": "✅ Valid" if invalid_last2 == 0 else "❌ Invalid", "Detail": f"{invalid_last2} invalid rows"},
            {"Check": "Prize_1 format", "Status": "✅ Valid" if invalid_prize1 == 0 else "❌ Invalid", "Detail": f"{invalid_prize1} invalid rows"},
            {"Check": "Historical First_3 coverage", "Status": "ℹ️ Expected", "Detail": f"{missing_3digit} missing rows before prize-tier introduction"},
        ]
    else:
        quality_rows = [
            {"หัวข้อตรวจสอบ": "งวดที่ซ้ำกัน", "ผลลัพธ์": "✅ ไม่มี" if duplicate_dates == 0 else "⚠️ มีซ้ำ", "รายละเอียด": f"{duplicate_dates} งวด"},
            {"หัวข้อตรวจสอบ": "เลขท้าย 2 ตัว (ต้องมี 2 หลัก)", "ผลลัพธ์": "✅ ถูกต้อง" if invalid_last2 == 0 else "❌ ผิดปกติ", "รายละเอียด": f"เจอที่ผิด {invalid_last2} จุด"},
            {"หัวข้อตรวจสอบ": "รางวัลที่ 1 (ต้องมี 6 หลัก)", "ผลลัพธ์": "✅ ถูกต้อง" if invalid_prize1 == 0 else "❌ ผิดปกติ", "รายละเอียด": f"เจอที่ผิด {invalid_prize1} จุด"},
            {"หัวข้อตรวจสอบ": "เลขหน้า 3 ตัว (ย้อนหลัง)", "ผลลัพธ์": "ℹ️ ข้อมูล", "รายละเอียด": f"ไม่มีข้อมูล {missing_3digit} งวด (ปกติสำหรับหวยสมัยก่อน)"},
        ]
    st.table(pd.DataFrame(quality_rows))

with right:
    st.subheader(mode_text("🚩 เรื่องน่ารู้ในอดีต", "🚩 Historical Notes"))
    st.info(mode_text("""
    **ก.ย. 2015: กำเนิดเลขหน้า 3 ตัว**
    เริ่มมีการออก 'เลขหน้า 3 ตัว' ครั้งแรก โดยยุบรางวัล 'เลขท้าย 3 ตัว' จาก 4 รางวัล เหลือ 2 รางวัล
    
    **ธ.ค. 2006: จุดเริ่มต้นสถิติ**
    เราเริ่มเก็บข้อมูลแบบละเอียดตั้งแต่งวดนี้ เพื่อความแม่นยำในการวิเคราะห์
    
    **พ.ค. 2026: ปัจจุบัน**
    ข้อมูลอัปเดตถึงงวดล่าสุด พร้อมให้คุณลองเอาไปคำนวณแล้ว!
    """, """
    **Sep 2015: First_3 prize tier introduced**
    The front 3-digit prize tier started here, so older rows can legitimately have missing First_3 values.

    **Dec 2006: Analysis boundary**
    The processed dataset starts from this point for the current dashboard.

    **May 2026: Current update window**
    The local dataset includes the latest manually merged records through the current analysis window.
    """))

st.markdown("---")

# Visualization: Draws per Year
st.subheader(mode_text("📈 ปริมาณข้อมูลในแต่ละปี", "📈 Annual Data Coverage"))
df["Year"] = df["Draw_Date"].dt.year
annual_draws = df.groupby("Year").size().reset_index(name="Draws")

fig_annual = go.Figure(go.Bar(
    x=annual_draws["Year"],
    y=annual_draws["Draws"],
    marker=dict(
        color=annual_draws["Draws"],
        colorscale=[
            [0.0, "rgba(120,90,20,0.45)"],
            [0.5, "rgba(180,140,40,0.75)"],
            [1.0, "rgba(240,220,130,1.0)"],
        ],
        showscale=False,
        line=dict(color="rgba(201,168,76,0.2)", width=1),
    ),
    hovertemplate=mode_text("ปี: %{x}<br>จำนวนงวด: %{y}<extra></extra>", "Year: %{x}<br>Draws: %{y}<extra></extra>"),
))
fig_annual = apply_layout(
    fig_annual,
    title=mode_text("จำนวนครั้งที่มีการออกรางวัลในแต่ละปี", "Draw Count by Year"),
    xaxis_title=mode_text("ปี ค.ศ.", "Year"),
    yaxis_title=mode_text("จำนวนงวด", "Draw Count"),
    height=360,
)
st.plotly_chart(fig_annual, width="stretch")

# Tabs for Details
tab_sample, tab_schema, tab_gaps = st.tabs([
    mode_text("📄 ดูโพยงวดล่าสุด", "📄 Recent Records"),
    mode_text("📂 โครงสร้างข้อมูล", "📂 Schema"),
    mode_text("⚠️ จุดที่น่าสงสัย", "⚠️ Gap Review"),
])

COLUMN_MAPPING = {
    "Draw_Date": "งวดวันที่",
    "Prize_1": "รางวัลที่ 1",
    "Last_2": "เลขท้าย 2 ตัว",
    "First_3": "เลขหน้า 3 ตัว",
    "Last_3": "เลขท้าย 3 ตัว",
    "Day_of_Week": "วันในสัปดาห์",
    "Month": "เดือน",
    "Source_URL": "แหล่งข้อมูล"
}
MATH_COLUMN_MAPPING = {
    "Draw_Date": "Draw Date",
    "Prize_1": "First Prize",
    "Last_2": "Last 2 Digits",
    "First_3": "Front 3 Digits",
    "Last_3": "Last 3 Digits",
    "Day_of_Week": "Day of Week",
    "Month": "Month",
    "Source_URL": "Source URL"
}

with tab_sample:
    display_df = df.tail(15).sort_values("Draw_Date", ascending=False).rename(columns=MATH_COLUMN_MAPPING if is_math_mode() else COLUMN_MAPPING)
    st.dataframe(display_df, width="stretch", hide_index=True)

with tab_schema:
    schema = pd.DataFrame({
        mode_text("ชื่อคอลัมน์", "Column"): [(MATH_COLUMN_MAPPING if is_math_mode() else COLUMN_MAPPING).get(c, c) for c in df.columns],
        mode_text("ประเภทข้อมูล", "Dtype"): [str(t) for t in df.dtypes],
        mode_text("ข้อมูลที่มีอยู่", "Non-null Count"): [int(df[c].count()) for c in df.columns],
        mode_text("ตัวอย่างข้อมูล", "Example"): [str(df[c].dropna().iloc[-1]) if not df[c].dropna().empty else "N/A" for c in df.columns],
    })
    st.dataframe(schema, width="stretch", hide_index=True)

with tab_gaps:
    gaps = df[["Draw_Date"]].copy()
    gaps["Gap"] = gaps["Draw_Date"].diff().dt.days
    anomalies = gaps[gaps["Gap"] > 25]
    if not anomalies.empty:
        st.warning(mode_text(f"พบช่วงห่างระหว่างงวดนานผิดปกติ (> 25 วัน) ทั้งหมด {len(anomalies)} รายการ", f"Found {len(anomalies)} unusually long draw gaps (>25 days)."))
        st.dataframe(anomalies, width="stretch")
    else:
        st.success(mode_text("ไม่พบช่องว่างข้อมูลที่น่าสงสัย (ข้อมูลครบถ้วนต่อเนื่องดี)", "No suspicious draw gaps detected."))
