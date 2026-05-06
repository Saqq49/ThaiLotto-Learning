import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from lotto.theme import inject_css, apply_layout, PLOTLY_CONFIG, CRIMSON, GOLD, init_persona, render_explanation, mode_text
from lotto.data_loader import load_data
from lotto.walk_forward import walk_forward_validate

st.set_page_config(page_title="AI จะแม่นจริงไหม?", page_icon="🎯", layout="wide")
inject_css()
init_persona()

df = st.session_state["df"] if "df" in st.session_state else load_data()
if df.empty:
    st.error("ไม่พบข้อมูล")
    st.stop()

st.title(mode_text("🎯 AI จะแม่นจริงไหม?", "🎯 Walk-Forward Validation"))
st.error(mode_text(
    "⚠️ หน้านี้เราจะมาจับโกหก AI — ลองให้สูตรต่างๆ ทายเลขย้อนหลัง แล้วดูว่ามันเก่งกว่าการสุ่มตาบอดจริงไหม",
    "⚠️ This page evaluates whether candidate ranking methods outperform a random Top-N baseline under walk-forward validation.",
))

layman_wf = (
    "วิธีทดสอบง่ายๆ คือ เราสมมติว่าย้อนเวลากลับไปในอดีต "
    "แล้วให้แต่ละสูตรทายเลขไปทีละงวด โดยรู้แค่ข้อมูลที่มีก่อนหน้านั้น "
    "พอออกรางวัลจริงก็ตรวจว่าเดาถูกไหม แล้วทำแบบนี้ซ้ำหลายร้อยงวด "
    "ถ้าสูตรไหนถูกบ่อยกว่าการสุ่มสุ่ม ก็ถือว่า 'อาจมีของ' "
    "แต่ถ้าพอๆ กัน ก็แปลว่าสูตรนั้นไม่ต่างจากดวง"
)
math_wf = "Walk-forward validation for time-series backtesting. Each target draw is evaluated using only prior observations inside a sliding training window, then repeated chronologically."
formula_wf = r"HitRate = \frac{1}{T} \sum_{t=W}^{T-1} \mathbb{1}(y_{t+1} \in \hat{\mathbf{y}}_{t+1} | \mathbf{X}_{t-W+1:t})"
render_explanation(layman_wf, math_wf, formula_wf)

with st.expander(mode_text("⚙️ ปรับการทดสอบ", "⚙️ Validation Parameters"), expanded=not st.session_state.get("wf_results") is not None):
    col1, col2 = st.columns(2)
    with col1:
        train_window = st.slider(
            mode_text("ใช้ข้อมูลกี่งวดก่อนทาย", "Training Window"),
            30, min(150, len(df) - 10), 60,
            help=mode_text("สูตรจะดูย้อนหลังจำนวนงวดนี้ก่อนจะทายงวดถัดไป", "Number of prior draws used to fit each prediction.")
        )
    with col2:
        top_n = st.slider(
            mode_text("ทายกี่เลขต่องวด", "Top-N Selection"),
            1, 10, 5,
            help=mode_text("ยิ่งทายเยอะ โอกาสถูกยิ่งสูงตามธรรมชาติ — ใช้เปรียบกันเป็น apple-to-apple", "Wider selection increases baseline hit rate proportionally.")
        )
    run_btn = st.button(mode_text("▶️ เริ่มจับโกหก!", "Run Validation"), type="primary", use_container_width=True)


if run_btn:
    with st.spinner(mode_text("กำลังย้อนเวลาทดสอบ...", "Running walk-forward validation...")):
        results = walk_forward_validate(df, train_window=train_window, top_n=top_n)
    st.session_state["wf_results"] = results
    st.session_state["wf_top_n"] = top_n

results = st.session_state.get("wf_results")
if results is None or results.empty:
    st.info(mode_text("กดปุ่มด้านบนเพื่อเริ่มทดสอบ", "Configure parameters and run validation."))
    st.stop()

top_n = st.session_state.get("wf_top_n", 5)
random_baseline = top_n / 100

# Summary metrics
summary = results.groupby("method")["hit"].mean().reset_index()
summary.columns = ["Method", "ความแม่นยำ"]
summary["vs_Random"] = summary["ความแม่นยำ"] - random_baseline

st.subheader(mode_text("📊 ผลรวมทุกสูตร", "📊 Backtest Summary"))
random_pct = random_baseline * 100

cols = st.columns(len(summary) + 1)
with cols[0]:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">{mode_text(f"ถ้าสุ่มตาบอด {top_n} เลข", f"Random Baseline (Top-{top_n})")}</div>
        <div class="metric-value" style="color:{GOLD};">{random_pct:.1f}%</div>
        <div class="metric-label" style="font-size:0.75rem;">{mode_text("นี่คือเส้นขั้นต่ำที่ต้องชนะ", f"Top-{top_n} / 100 nodes")}</div>
    </div>""", unsafe_allow_html=True)

for i, row in summary.iterrows():
    acc_pct = row["ความแม่นยำ"] * 100
    delta = row["vs_Random"] * 100
    color = CRIMSON if abs(delta) < 2 else ("#4CAF50" if delta > 0 else CRIMSON)
    with cols[i + 1]:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{row['Method']}</div>
            <div class="metric-value" style="color:{color};">{acc_pct:.1f}%</div>
            <div class="metric-label" style="font-size:0.75rem;">{mode_text("ต่างจากสุ่มตาบอด", "vs Random")}: {delta:+.1f}%</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# Per-method bar chart
st.subheader(mode_text("📈 เปรียบแต่ละสูตร", "📈 Method Accuracy"))
fig_bar = go.Figure()
for method in summary["Method"]:
    sub = results[results["method"] == method]
    fig_bar.add_bar(
        name=method,
        x=[method],
        y=[sub["hit"].mean() * 100],
        text=[f"{sub['hit'].mean()*100:.1f}%"],
        textposition="outside",
    )

fig_bar.add_hline(
    y=random_pct,
    line_dash="dash",
    line_color=GOLD,
    annotation_text=mode_text(f"ถ้าสุ่มตาบอด ({random_pct:.1f}%)", f"Random Baseline {random_pct:.1f}%"),
    annotation_position="top right",
)
fig_bar = apply_layout(
    fig_bar,
    title=mode_text("อัตราถูกของแต่ละสูตร เทียบกับการสุ่มตาบอด", "Accuracy vs Random Baseline"),
    yaxis_title=mode_text("อัตราถูก (%)", "Accuracy (%)"),
    height=400,
)
st.plotly_chart(fig_bar, width="stretch", config=PLOTLY_CONFIG)

# Rolling accuracy over time
st.subheader(mode_text("📉 ความแม่นในแต่ละช่วงเวลา", "📉 Rolling Accuracy"))
method_sel = st.selectbox(mode_text("เลือกสูตรที่อยากดู", "Method"), results["method"].unique())
sub = results[results["method"] == method_sel].copy()
sub["draw_date"] = pd.to_datetime(sub["draw_date"])
sub = sub.sort_values("draw_date")
sub["rolling_acc"] = sub["hit"].rolling(24, min_periods=6).mean() * 100

fig_roll = go.Figure()
fig_roll.add_scatter(
    x=sub["draw_date"],
    y=sub["rolling_acc"],
    mode="lines",
    name=method_sel,
    line=dict(color=CRIMSON, width=2),
)
fig_roll.add_hline(
    y=random_pct,
    line_dash="dash",
    line_color=GOLD,
    annotation_text=mode_text("เส้นถ้าสุ่มตาบอด", "Random Baseline"),
)
fig_roll = apply_layout(
    fig_roll,
    title=mode_text(f"อัตราถูกเฉลี่ย 24 งวด — {method_sel}", f"Rolling Accuracy (24 draws) — {method_sel}"),
    xaxis_title=mode_text("วันที่ออกรางวัล", "Draw Date"),
    yaxis_title=mode_text("อัตราถูก (%)", "Accuracy (%)"),
    height=350,
)
st.plotly_chart(fig_roll, width="stretch", config=PLOTLY_CONFIG)

# Conclusion
best_acc = summary["ความแม่นยำ"].max() * 100
st.markdown("---")
if best_acc - random_pct < 2:
    st.success(mode_text(
        f"🎯 สรุป: ทุกสูตรทำได้พอๆ กับการสุ่มตาบอด (ดีที่สุด {best_acc:.1f}% ส่วนสุ่มตาบอดได้ {random_pct:.1f}%)\n\n"
        f"**แปลว่า ยังไม่มีสูตรไหนที่ 'แม่น' จริงๆ — ผลลัพธ์ยืนยันว่าเลขหวยยังคาดเดาไม่ได้จากสถิติย้อนหลัง**",
        f"Conclusion: no method shows meaningful lift over random baseline. Best observed accuracy is {best_acc:.1f}% vs random {random_pct:.1f}%.\n\n"
        f"**This supports the assumption that short historical windows should not be treated as predictive evidence.**",
    ))
else:
    st.warning(mode_text(
        f"⚠️ สูตรที่ดีที่สุดทำได้ {best_acc:.1f}% ซึ่งสูงกว่าสุ่มตาบอดที่ {random_pct:.1f}% — "
        f"แต่ยังไม่ควรด่วนสรุป เพราะอาจเป็นแค่ความบังเอิญจากข้อมูลชุดนี้ ต้องทดสอบในข้อมูลชุดอื่นด้วย",
        f"Observed accuracy {best_acc:.1f}% exceeds random baseline {random_pct:.1f}% in this sample, but this can still be sample noise or overfitting. "
        f"Additional validation is required before interpreting it as signal.",
    ))
