import streamlit as st
from lotto.theme import inject_css, render_metric, init_persona
from lotto.data_loader import load_data

st.set_page_config(
    page_title="Thai Lottery Dashboard",
    page_icon="🎱",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
init_persona()

if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

st.title("🎱 Thai Lottery Statistical Dashboard")
st.markdown('<div class="disclaimer">⚠️ แดชบอร์ดนี้จัดทำเพื่อการศึกษาและความบันเทิงเท่านั้น ผลสลากกินแบ่งเป็นการสุ่มสมบูรณ์แบบ ประวัติการออกรางวัลไม่สามารถทำนายผลในอนาคตได้</div>', unsafe_allow_html=True)

st.markdown("---")

if df.empty:
    st.warning("ยังไม่มีข้อมูล กรุณารัน: `.venv/bin/python -m lotto.scraper` ก่อน")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric("งวดทั้งหมด", f"{len(df):,}")
with col2:
    render_metric("ช่วงข้อมูลเริ่มต้น", f"{df['Draw_Date'].min().strftime('%d/%m/%Y')}")
with col3:
    render_metric("ช่วงข้อมูลล่าสุด", f"{df['Draw_Date'].max().strftime('%d/%m/%Y')}")
with col4:
    render_metric("ล่าสุด Last_2", df.sort_values("Draw_Date").iloc[-1]["Last_2"])

st.markdown("---")
st.markdown("""
### เมนูหลัก (เลือกจาก Sidebar)

| หน้า | จุดประสงค์ |
|---|---|
| 📋 ส่องโพยสถิติ | ตรวจสอบข้อมูลย้อนหลัง และความโปร่งใสของแหล่งข้อมูล |
| 📊 เลขไหนฮิต เลขไหนดับ | ดูความถี่ Heatmap และเลขที่หายหน้าไปนานๆ |
| 🔮 สำนักคำนวณเลขเด็ด | ลองคำนวณเลขเด็ดด้วยสารพัดสูตรคณิตศาสตร์ |
| 🎯 AI จะแม่นจริงไหม? | พิสูจน์ให้เห็นกันไปเลยว่า AI ทายถูกกี่งวด |
| 💰 ลองแทงทิพย์: รวยหรือเจ๊ง? | จำลองการซื้อสลากด้วยกลยุทธ์ต่างๆ (เตือน: ส่วนใหญ่จะเจ๊ง!) |
| 📅 อาถรรพ์เลขตามปฏิทิน | ทดสอบความเชื่อเรื่องเลขตามวันและเดือน |
""")
