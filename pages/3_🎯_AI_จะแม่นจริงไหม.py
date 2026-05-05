import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from lotto.theme import inject_css, apply_layout, CRIMSON, GOLD, TEXT_DARK, PANEL_WHITE, init_persona, render_explanation
from lotto.data_loader import load_data
from lotto.walk_forward import walk_forward_validate

st.set_page_config(page_title="AI จะแม่นจริงไหม?", page_icon="🎯", layout="wide")
inject_css()
init_persona()

df = st.session_state["df"] if "df" in st.session_state else load_data()
if df.empty:
    st.error("ไม่พบข้อมูล")
    st.stop()

st.title("🎯 AI จะแม่นจริงไหม?")
st.error("⚠️ หน้านี้เรามาจับโป๊ะ AI — วัดกันไปเลยว่าถ้าให้ AI เลือกเลขให้ย้อนหลัง มันจะทายถูกบ่อยกว่าการสุ่มไหม")

layman_wf = "ลอง 'ทายย้อนหลัง' - สมมติว่าเราย้อนเวลากลับไป แล้วลองเอาสูตรเด็ดไปทายเลขงวดถัดไปดูทีละงวดๆ เพื่อดูว่าถ้าใช้สูตรนี้มาตั้งแต่อดีต เราจะถูกหวยจริงๆ กี่ครั้ง"
math_wf = "การทดสอบประสิทธิภาพตัวแบบด้วยวิธี Walk-Forward Validation (Time-series Backtesting) โดยการกำหนดหน้าต่างข้อมูลฝึกสอน (Sliding training window) เพื่อพยากรณ์ผลลัพธ์ในงวดถัดไป ($t+1$) และทำการทดสอบซ้ำอย่างต่อเนื่องตามลำดับเวลา"
formula_wf = r"HitRate = \frac{1}{T} \sum_{t=W}^{T-1} \mathbb{1}(y_{t+1} \in \hat{\mathbf{y}}_{t+1} | \mathbf{X}_{t-W+1:t})"
render_explanation(layman_wf, math_wf, formula_wf)

with st.sidebar:
    st.header("ตั้งค่า Walk-Forward")
    train_window = st.slider("Training Window (งวด)", 30, min(150, len(df) - 10), 60)
    top_n = st.slider("Top-N ที่ประเมิน", 1, 10, 5)
    run_btn = st.button("▶️ รัน Validation", type="primary")

if run_btn:
    with st.spinner("กำลังรัน Walk-Forward Validation..."):
        results = walk_forward_validate(df, train_window=train_window, top_n=top_n)
    st.session_state["wf_results"] = results
    st.session_state["wf_top_n"] = top_n

results = st.session_state.get("wf_results")
if results is None or results.empty:
    st.info("กด 'รัน Validation' เพื่อเริ่มต้น")
    st.stop()

top_n = st.session_state.get("wf_top_n", 5)
random_baseline = top_n / 100

# Summary metrics
summary = results.groupby("method")["hit"].mean().reset_index()
summary.columns = ["Method", "Accuracy"]
summary["vs_Random"] = summary["Accuracy"] - random_baseline

st.subheader("📊 ผลการประเมิน Walk-Forward")
random_pct = random_baseline * 100

cols = st.columns(len(summary) + 1)
with cols[0]:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">Random Baseline</div>
        <div class="metric-value" style="color:{GOLD};">{random_pct:.1f}%</div>
        <div class="metric-label" style="font-size:0.75rem;">Top-{top_n} / 100</div>
    </div>""", unsafe_allow_html=True)

for i, row in summary.iterrows():
    acc_pct = row["Accuracy"] * 100
    delta = row["vs_Random"] * 100
    color = CRIMSON if abs(delta) < 2 else ("#4CAF50" if delta > 0 else CRIMSON)
    with cols[i + 1]:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{row['Method']}</div>
            <div class="metric-value" style="color:{color};">{acc_pct:.1f}%</div>
            <div class="metric-label" style="font-size:0.75rem;">vs Random: {delta:+.1f}%</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# Per-method bar chart
st.subheader("📈 Accuracy แต่ละ Method")
fig_bar = go.Figure()
for method in summary["Method"]:
    sub = results[results["method"] == method]
    fig_bar.add_bar(name=method, x=[method], y=[sub["hit"].mean() * 100],
                    text=[f"{sub['hit'].mean()*100:.1f}%"], textposition="outside")

fig_bar.add_hline(y=random_pct, line_dash="dash", line_color=GOLD,
                  annotation_text=f"Random Baseline {random_pct:.1f}%", annotation_position="top right")
fig_bar = apply_layout(fig_bar, title="Accuracy เทียบกับ Random Baseline",
                       yaxis_title="Accuracy (%)", height=400)
st.plotly_chart(fig_bar, width="stretch")

# Rolling accuracy over time
st.subheader("📉 Rolling Accuracy ตามเวลา")
method_sel = st.selectbox("เลือก Method", results["method"].unique())
sub = results[results["method"] == method_sel].copy()
sub["draw_date"] = pd.to_datetime(sub["draw_date"])
sub = sub.sort_values("draw_date")
sub["rolling_acc"] = sub["hit"].rolling(24, min_periods=6).mean() * 100

fig_roll = go.Figure()
fig_roll.add_scatter(x=sub["draw_date"], y=sub["rolling_acc"],
                     mode="lines", name=method_sel, line=dict(color=CRIMSON, width=2))
fig_roll.add_hline(y=random_pct, line_dash="dash", line_color=GOLD,
                   annotation_text="Random Baseline")
fig_roll = apply_layout(fig_roll, title=f"Rolling Accuracy (24 งวด) — {method_sel}",
                        xaxis_title="งวด", yaxis_title="Accuracy (%)", height=350)
st.plotly_chart(fig_roll, width="stretch")

# Conclusion
best_acc = summary["Accuracy"].max() * 100
st.markdown("---")
if best_acc - random_pct < 2:
    st.success(f"สรุป: ยังไม่พบวิธีที่ดีกว่า Random อย่างมีนัยสำคัญ (ดีที่สุด {best_acc:.1f}% vs Random {random_pct:.1f}%)\n\n**ผลนี้สนับสนุนข้อเท็จจริงว่าเลขสลากไม่ควรถูกมองว่าเป็นสิ่งที่ทำนายได้จากข้อมูลย้อนหลังสั้น ๆ**")
else:
    st.warning(f"พบ Accuracy {best_acc:.1f}% > Random {random_pct:.1f}% ในชุดข้อมูลนี้ แต่ยังอาจเกิดจาก overfitting หรือ sample noise ต้องตรวจซ้ำก่อนตีความว่าเป็น edge จริง")
