import streamlit as st
import plotly.graph_objects as go
from lotto.theme import inject_css, apply_layout, PLOTLY_CONFIG, GOLD, CRIMSON, init_persona, render_explanation, mode_text, is_math_mode, GOLD_BRUSHED, TEXT_MUTED
from lotto.data_loader import load_data
from lotto.predictors import frequency_predictor, overdue_predictor, recency_weighted_predictor, random_predictor

st.set_page_config(page_title="สำนักคำนวณเลขเด็ด", page_icon="🔮", layout="wide")
inject_css()
init_persona()

df = st.session_state["df"] if "df" in st.session_state else load_data()
if df.empty:
    st.error("ไม่พบข้อมูล")
    st.stop()

st.title(mode_text("🔮 สำนักคำนวณเลขเด็ด", "🔮 Predictor Lab"))
st.markdown(mode_text(
    "ลองจัดอันดับเลขด้วยสูตรง่าย ๆ หลายแบบ ผลลัพธ์เป็นการเรียงสถิติย้อนหลัง ไม่ใช่คำทำนาย",
    "Rank Last_2 candidates with transparent baseline algorithms. Computation is identical across display modes.",
))

# Settings logic
METHOD_NAMES = {
    "Frequency": "ออกบ่อย (ความถี่)",
    "Overdue": "อั้นมานาน (ทิ้งช่วง)",
    "Recency-Weighted": "มาล่าสุด (น้ำหนักใหม่)",
    "Random": "สุ่มวัดดวง",
}

with st.container():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        method = st.selectbox(
            mode_text("วิธีคำนวณ", "Algorithm"),
            list(METHOD_NAMES.keys()),
            format_func=lambda x: x if is_math_mode() else METHOD_NAMES[x],
        )
    with col2:
        top_n = st.slider(mode_text("จำนวนเลขที่แสดง", "Top-N Candidates"), 1, 10, 5)
    with col3:
        window = st.slider(mode_text("ใช้ข้อมูลกี่งวดล่าสุด", "Lookback Window"), 12, len(df), min(120, len(df)))

train_df = df.tail(window)

if method == "Frequency":
    predictions = frequency_predictor(train_df, top_n=top_n)
    layman = "สูตร 'เลขขยัน' - จัดเลขที่เคยออกบ่อยไว้ด้านหน้า เพื่อให้เห็นว่าในข้อมูลย้อนหลังเลขไหนโผล่มาบ่อยกว่าตัวอื่น ไม่ได้แปลว่างวดหน้าจะออกง่ายขึ้น"
    math = "Empirical distribution estimation with Laplace smoothing. The additive prior prevents zero-frequency nodes and stabilizes scores under limited historical sample size."
    formula = r"P(x) = \frac{count(x) + 1}{\sum_{i=0}^{99} (count(i) + 1)}"
elif method == "Overdue":
    predictions = overdue_predictor(train_df, top_n=top_n)
    layman = "สูตร 'เลขตาม' - จัดเลขที่หายไปนานไว้ด้านหน้า เพื่อให้เห็นเลขที่คนชอบเรียกว่าอั้นมานาน แต่การหายไปนานไม่ทำให้โอกาสงวดหน้าสูงขึ้นเอง"
    math = "Waiting-time scoring over a random process. Each node receives a normalized gap score based on the number of draws since its latest observed occurrence."
    formula = r"Score(x) = \frac{T - last\_seen(x)}{\max_{i} (T - last\_seen(i))}"
elif method == "Recency-Weighted":
    predictions = recency_weighted_predictor(train_df, top_n=top_n)
    layman = "สูตร 'เลขกระแส' - ให้น้ำหนักกับงวดใกล้ๆ มากกว่างวดไกลๆ เลขที่เพิ่งออกไปหมาดๆ จะถือว่ากำลัง 'ร้อน' และเด่นกว่าเลขเก่า"
    math = "Time-weighted scoring with exponential decay. More recent observations receive larger weights, producing a recency-biased descriptive score."
    formula = r"Score(x) = \sum_{t=1}^{T} \mathbb{1}(draw_t = x) \cdot \alpha^{T-t}"
else:
    predictions = random_predictor(top_n=top_n)
    layman = "สูตร 'วัดดวง' - สุ่มเลขแบบแฟร์ๆ เท่ากันทุกตัว ไม่สนสถิติ เพราะเชื่อว่าหวยทุกลูกมีสิทธิถูกดึงขึ้นมาเท่ากัน"
    math = "Discrete uniform baseline. Each node in the 00-99 sample space has the same probability mass and no historical features are used."
    formula = r"P(X=x) = \frac{1}{100}, \forall x \in \{00, 01, ..., 99\}"

st.subheader(mode_text(f"เลขที่วิธีนี้จัดอันดับสูง ({METHOD_NAMES[method]})", f"Selected Nodes: {method}"))
render_explanation(layman, math, formula)
st.markdown("---")

cols = st.columns(top_n)
for i, (num, score) in enumerate(predictions):
    with cols[i]:
        st.markdown(f"""
        <div class="metric-container" style="padding: 30px 10px;">
            <div style="font-family: 'Playfair Display', serif; font-size: 3.5rem; font-weight: 700; color: {GOLD};
                        background: {GOLD_BRUSHED if 'GOLD_BRUSHED' in globals() else GOLD}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                {num}
            </div>
            <div style="color: {TEXT_MUTED if 'TEXT_MUTED' in globals() else '#888'}; font-size: 0.75rem; letter-spacing: 0.1em; margin-top: 10px;">
                {mode_text("คะแนน", "Score")}: {score:.4f}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Bar chart of all scores
st.subheader(mode_text("คะแนนของเลขทุกตัว (00–99)", "Distribution of Predictor Scores"))
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
                       hovertemplate=mode_text("เลข: %{x}<br>คะแนน: %{y:.4f}<extra></extra>", "Node: %{x}<br>Score: %{y:.4f}<extra></extra>")))
fig = apply_layout(fig, title=mode_text("คะแนนของแต่ละเลข (สีแดง = เลขที่วิธีนี้เลือก)", f"Score Map ({method})"),
                   xaxis_title=mode_text("เลข", "Node"), yaxis_title=mode_text("คะแนน", "Score"), height=350)
st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)

st.markdown(f'<div class="disclaimer">{mode_text(f"🎲 ถ้าสุ่มแบบปกติ ควรได้ {top_n:.1f}% — ถ้าวิธีคำนวณไม่ได้ดีกว่านี้อย่างสม่ำเสมอ แปลว่ายังไม่ได้เปรียบอะไรจากสถิติเลย", f"🎲 Random Top-{top_n} baseline is {top_n:.1f}%. A method needs consistent out-of-sample lift before it should be interpreted as useful.")}</div>', unsafe_allow_html=True)
