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
    render_metric("เก็บสถิติตั้งแต่ปี", f"{date_min.year} - {date_max.year}")
with m_cols[2]:
    render_metric("ความเป๊ะของข้อมูล", f"{integrity_score:.1f}%")
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
    st.subheader("🛡️ เช็กความเรียบร้อยของข้อมูล")
    quality_rows = [
        {"หัวข้อตรวจสอบ": "งวดที่ซ้ำกัน", "ผลลัพธ์": "✅ ไม่มี" if duplicate_dates == 0 else "⚠️ มีซ้ำ", "รายละเอียด": f"{duplicate_dates} งวด"},
        {"หัวข้อตรวจสอบ": "เลขท้าย 2 ตัว (ต้องมี 2 หลัก)", "ผลลัพธ์": "✅ ถูกต้อง" if invalid_last2 == 0 else "❌ ผิดปกติ", "รายละเอียด": f"เจอที่ผิด {invalid_last2} จุด"},
        {"หัวข้อตรวจสอบ": "รางวัลที่ 1 (ต้องมี 6 หลัก)", "ผลลัพธ์": "✅ ถูกต้อง" if invalid_prize1 == 0 else "❌ ผิดปกติ", "รายละเอียด": f"เจอที่ผิด {invalid_prize1} จุด"},
        {"หัวข้อตรวจสอบ": "เลขหน้า 3 ตัว (ย้อนหลัง)", "ผลลัพธ์": "ℹ️ ข้อมูล", "รายละเอียด": f"ไม่มีข้อมูล {missing_3digit} งวด (ปกติสำหรับหวยสมัยก่อน)"},
    ]
    st.table(pd.DataFrame(quality_rows))

with right:
    st.subheader("🚩 เรื่องน่ารู้ในอดีต")
    st.info("""
    **ก.ย. 2015: กำเนิดเลขหน้า 3 ตัว**
    เริ่มมีการออก 'เลขหน้า 3 ตัว' ครั้งแรก โดยยุบรางวัล 'เลขท้าย 3 ตัว' จาก 4 รางวัล เหลือ 2 รางวัล
    
    **ธ.ค. 2006: จุดเริ่มต้นสถิติ**
    เราเริ่มเก็บข้อมูลแบบละเอียดตั้งแต่งวดนี้ เพื่อความแม่นยำในการวิเคราะห์
    
    **พ.ค. 2026: ปัจจุบัน**
    ข้อมูลอัปเดตถึงงวดล่าสุด พร้อมให้คุณลองเอาไปคำนวณแล้ว!
    """)

st.markdown("---")

# Visualization: Draws per Year
st.subheader("📈 ปริมาณข้อมูลในแต่ละปี")
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
    title="จำนวนครั้งที่มีการออกรางวัลในแต่ละปี",
    xaxis_title="ปี ค.ศ.",
    yaxis_title="จำนวนงวด",
    height=360,
)
st.plotly_chart(fig_annual, width="stretch")

# Tabs for Details
tab_sample, tab_schema, tab_gaps = st.tabs(["📄 ดูโพยงวดล่าสุด", "📂 โครงสร้างข้อมูล", "⚠️ จุดที่น่าสงสัย"])

with tab_sample:
    st.dataframe(df.tail(15).sort_values("Draw_Date", ascending=False), width="stretch", hide_index=True)

with tab_schema:
    schema = pd.DataFrame({
        "ชื่อคอลัมน์": df.columns,
        "ประเภทข้อมูล": [str(t) for t in df.dtypes],
        "ข้อมูลที่มีอยู่": [int(df[c].count()) for c in df.columns],
        "ตัวอย่างข้อมูล": [str(df[c].dropna().iloc[-1]) if not df[c].dropna().empty else "N/A" for c in df.columns],
    })
    st.dataframe(schema, width="stretch", hide_index=True)

with tab_gaps:
    gaps = df[["Draw_Date"]].copy()
    gaps["Gap"] = gaps["Draw_Date"].diff().dt.days
    anomalies = gaps[gaps["Gap"] > 25]
    if not anomalies.empty:
        st.warning(f"พบช่วงห่างระหว่างงวดนานผิดปกติ (> 25 วัน) ทั้งหมด {len(anomalies)} รายการ")
        st.dataframe(anomalies, width="stretch")
    else:
        st.success("ไม่พบช่องว่างข้อมูลที่น่าสงสัย (ข้อมูลครบถ้วนต่อเนื่องดี)")
