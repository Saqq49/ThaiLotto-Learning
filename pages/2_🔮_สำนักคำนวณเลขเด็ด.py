import streamlit as st
import plotly.graph_objects as go
from lotto.theme import inject_css, apply_layout, GOLD, CRIMSON, PANEL_WHITE, TEXT_DARK, init_persona, render_explanation
from lotto.data_loader import load_data
from lotto.predictors import frequency_predictor, overdue_predictor, recency_weighted_predictor, random_predictor

st.set_page_config(page_title="สำนักคำนวณเลขเด็ด", page_icon="🔮", layout="wide")
inject_css()
init_persona()

df = st.session_state["df"] if "df" in st.session_state else load_data()
if df.empty:
    st.error("ไม่พบข้อมูล")
    st.stop()

st.title("🔮 สำนักคำนวณเลขเด็ด")
st.markdown("ลองปรุงเลขด้วยสูตรคณิตศาสตร์ — จะคำนวณแบบไหนก็เลือกได้ตามใจชอบ")

with st.sidebar:
    st.header("ตั้งค่า")
    method = st.selectbox("วิธีคำนวณ", ["Frequency", "Overdue", "Recency-Weighted", "Random"])
    top_n = st.slider("จำนวนเลขที่แสดง (Top-N)", 1, 10, 5)
    window = st.slider("ใช้ข้อมูลกี่งวดล่าสุด", 12, len(df), min(120, len(df)))

train_df = df.tail(window)

if method == "Frequency":
    predictions = frequency_predictor(train_df, top_n=top_n)
    layman = "สูตร 'เลขขยัน' - เน้นตามเลขที่มาบ่อยๆ เพราะเชื่อว่าช่วงนี้กำลังเดินดี เลขไหนออกซ้ำบ่อยก็มีสิทธิจะมาอีก"
    math = "การประมาณค่าความน่าจะเป็นแบบ Empirical Distribution ด้วยเทคนิค Laplace Smoothing (Additive Smoothing) เพื่อลดอคติจากกลุ่มตัวอย่างที่มีขนาดจำกัดและป้องกันความน่าจะเป็นเป็นศูนย์ (Zero-frequency problem)"
    formula = r"P(x) = \frac{count(x) + 1}{\sum_{i=0}^{99} (count(i) + 1)}"
elif method == "Overdue":
    predictions = overdue_predictor(train_df, top_n=top_n)
    layman = "สูตร 'เลขตาม' - หาเลขที่อั้นมานาน ไม่ยอมออกซักที ยิ่งหายไปนานเท่าไหร่ ยิ่งมีโอกาสจะโผล่มาให้เห็น (ตามความเชื่อเรื่องเลขวนลูป)"
    math = "การวิเคราะห์ระยะเวลาห่าง (Waiting Time) ในกระบวนการแบบสุ่ม โดยคำนวณจากจำนวนหน่วยเวลา (งวด) ที่ไม่เกิดเหตุการณ์ (Draw event) และทำการปรับบรรทัดฐาน (Normalization) ค่าสถิติคงค้างเพื่อให้สามารถเปรียบเทียบเชิงสัมพัทธ์ได้"
    formula = r"Score(x) = \frac{T - last\_seen(x)}{\max_{i} (T - last\_seen(i))}"
elif method == "Recency-Weighted":
    predictions = recency_weighted_predictor(train_df, top_n=top_n)
    layman = "สูตร 'เลขกระแส' - ให้น้ำหนักกับงวดใกล้ๆ มากกว่างวดไกลๆ เลขที่เพิ่งออกไปหมาดๆ จะถือว่ากำลัง 'ร้อน' และเด่นกว่าเลขเก่า"
    math = "การคำนวณฟังก์ชันน้ำหนักถ่วงเวลา (Time-weighted scoring) โดยใช้เทคนิค Exponential Decay เพื่อให้ความสำคัญกับข้อมูลล่าสุด (Recency bias) ในเชิงเรขาคณิต"
    formula = r"Score(x) = \sum_{t=1}^{T} \mathbb{1}(draw_t = x) \cdot \alpha^{T-t}"
else:
    predictions = random_predictor(top_n=top_n)
    layman = "สูตร 'วัดดวง' - สุ่มเลขแบบแฟร์ๆ เท่ากันทุกตัว ไม่สนสถิติ เพราะเชื่อว่าหวยทุกลูกมีสิทธิถูกดึงขึ้นมาเท่ากัน"
    math = "สมมติฐานกระบวนการสุ่มแบบ Discrete Uniform Distribution โดยกำหนดให้ตัวแปรสุ่มทุกตัวในปริภูมิตัวอย่างมีฟังก์ชันมวลความน่าจะเป็น (Probability Mass Function) ที่เท่ากัน"
    formula = r"P(X=x) = \frac{1}{100}, \forall x \in \{00, 01, ..., 99\}"

st.subheader(f"เลขที่วิธีนี้จัดอันดับสูง ({method})")
render_explanation(layman, math, formula)
st.markdown("---")

cols = st.columns(top_n)
for i, (num, score) in enumerate(predictions):
    with cols[i]:
        st.markdown(f"""
        <div style="background:{PANEL_WHITE}; border:2px solid {GOLD}; border-radius:8px;
                    padding:20px; text-align:center; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <div style="font-size:2.5rem; font-weight:bold; color:{CRIMSON};">{num}</div>
            <div style="color:{TEXT_DARK}; font-size:0.8rem; opacity:0.6;">score: {score:.4f}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Bar chart of all scores
st.subheader("การกระจาย Score ทุกเลข (00–99)")
if method != "Random":
    from lotto.predictors import PREDICTORS
    all_preds = PREDICTORS.get(method, frequency_predictor)(train_df, top_n=100)
else:
    import numpy as np
    all_preds = [(f"{i:02d}", 1/100) for i in range(100)]

nums = [p[0] for p in all_preds]
scores = [p[1] for p in all_preds]
colors = [CRIMSON if n in [p[0] for p in predictions] else GOLD for n in nums]

fig = go.Figure(go.Bar(x=nums, y=scores, marker_color=colors,
                       hovertemplate="เลข: %{x}<br>Score: %{y:.4f}<extra></extra>"))
fig = apply_layout(fig, title="Score ของแต่ละเลข (สีแดง = Top-N ที่วิธีนี้เลือก)",
                   xaxis_title="เลข", yaxis_title="Score", height=350)
st.plotly_chart(fig, width="stretch")

st.markdown('<div class="disclaimer">🎲 ค่าอ้างอิงจากการสุ่มสำหรับ Top-N: {:.1f}% — หากวิธีคำนวณไม่ดีกว่านี้อย่างสม่ำเสมอ แปลว่ายังไม่มี edge ทางสถิติ</div>'.format(top_n), unsafe_allow_html=True)
