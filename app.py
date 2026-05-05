import streamlit as st
from lotto.theme import inject_css, render_metrics_row, init_persona, mode_text
from lotto.data_loader import load_data

st.set_page_config(
    page_title="Thai Lotto",
    page_icon="🎱",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
init_persona()

if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

st.markdown(f"<h1 style='text-align: center;'>{mode_text('Thai Lotto', 'Thai Lotto')}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#8A817C; font-size:0.9rem; letter-spacing:0.1em;'>{mode_text('ข้อมูลสถิติสลากกินแบ่งรัฐบาล เพื่อการวิเคราะห์อย่างตรงไปตรงมา', 'Statistical exploration of Thai Government Lottery results with transparent assumptions')}</p>", unsafe_allow_html=True)

st.markdown(f'<div class="disclaimer" style="text-align:center; border:none; background:rgba(255,255,255,0.02); color:#7A7060;">{mode_text("⚠️ เว็บนี้จัดทำเพื่อการศึกษาและวิเคราะห์สถิติเท่านั้น ผลการออกรางวัลเป็นเรื่องของดวงล้วนๆ", "⚠️ Educational/statistical tool only. Historical observations do not imply predictive power.")}</div>', unsafe_allow_html=True)

st.markdown("---")

if df.empty:
    st.warning(mode_text("ยังไม่มีข้อมูล กรุณารัน: `.venv/bin/python -m lotto.scraper` ก่อน", "No dataset found. Run `.venv/bin/python -m lotto.scraper` first."))
    st.stop()

render_metrics_row([
    (mode_text("งวดทั้งหมด", "Total Draws"), f"{len(df):,}"),
    (mode_text("ช่วงข้อมูลเริ่มต้น", "Start Date"), df['Draw_Date'].min().strftime('%d/%m/%Y')),
    (mode_text("ช่วงข้อมูลล่าสุด", "End Date"), df['Draw_Date'].max().strftime('%d/%m/%Y')),
    (mode_text("เลขท้าย 2 ตัวล่าสุด", "Latest Last_2"), df.sort_values("Draw_Date").iloc[-1]["Last_2"]),
])

st.markdown("---")
st.markdown(mode_text("""
### เมนูหลัก (เลือกจากเมนูด้านซ้าย)

| หน้า | จุดประสงค์ |
|---|---|
| 📋 ส่องโพยสถิติ | ตรวจสอบข้อมูลย้อนหลัง และความโปร่งใสของแหล่งข้อมูล |
| 🎲 คิดไม่ออก เดี๋ยวเลือกให้ | ให้ระบบช่วยจัดเลขที่น่าสนใจแบบเล่นสนุก |
| 📊 เลขไหนฮิต เลขไหนดับ | ดูความถี่และแผนภูมิสี รวมถึงเลขที่หายหน้าไปนาน |
| 🔮 สำนักคำนวณเลขเด็ด | ลองจัดอันดับเลขด้วยสูตรพื้นฐาน |
| 🎯 ระบบจะแม่นจริงไหม? | ทดสอบย้อนหลังว่าสูตรต่าง ๆ ดีกว่าสุ่มไหม |
| 💰 ลองแทงทิพย์: รวยหรือเจ๊ง? | จำลองการซื้อสลากด้วยกลยุทธ์ต่าง ๆ |
| 📅 อาถรรพ์เลขตามปฏิทิน | ทดสอบความเชื่อเรื่องเลขตามวันและเดือน |
""", """
### Main Features

| Page | Purpose |
|---|---|
| 📋 Data Overview | Dataset coverage, integrity checks, and source transparency |
| 🎲 Selection Engine | Candidate generation with visible rank rationale |
| 📊 Frequency Distribution | Empirical frequency matrix and inter-arrival analysis |
| 🔮 Predictor Lab | Transparent baseline ranking algorithms |
| 🎯 Walk-Forward Validation | Historical validation against random baselines |
| 💰 Strategy Backtest | Financial risk simulation under explicit assumptions |
| 📅 Calendar Effect Test | Month/weekday independence checks |
"""))
