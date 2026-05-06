import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from lotto.theme import inject_css, apply_layout, PLOTLY_CONFIG, CRIMSON, GOLD, GOLD_SOLID, TEXT_PRIMARY as TEXT, init_persona, render_explanation, mode_text
from lotto.data_loader import load_data, compute_last2_frequency
from lotto.stats import compute_last2_heatmap_matrix, compute_max_drawdown_per_number, get_hot_cold_numbers

st.set_page_config(page_title="เลขไหนฮิต เลขไหนดับ", page_icon="📊", layout="wide")
inject_css()
init_persona()

df = st.session_state["df"] if "df" in st.session_state else load_data()
if df.empty:
    st.error("ไม่พบข้อมูล")
    st.stop()

st.title(mode_text("📊 เลขไหนฮิต เลขไหนดับ", "📊 Frequency Distribution"))
st.markdown(mode_text(
    "ดูภาพรวมว่าเลขท้าย 2 ตัวแต่ละเลขเคยออกบ่อยแค่ไหน เลขเหล่านี้เป็นสถิติย้อนหลัง ไม่ใช่สัญญาณทำนายงวดหน้า",
    "Inspect empirical frequencies for Last_2 outcomes. The calculation is descriptive and does not alter future probability assumptions.",
))

filtered = df

if filtered.empty:
    st.warning(mode_text("ไม่มีข้อมูลในช่วงนี้", "No data available for this selection."))
    st.stop()

freq = compute_last2_frequency(filtered)
st.caption(mode_text(f"แสดงข้อมูล {len(filtered)} งวด", f"Sample size: {len(filtered)} draws"))

# --- Heatmap ---
st.subheader(mode_text("🗺️ แผนภูมิความถี่ (เลข 00–99)", "🗺️ 10x10 Frequency Matrix"))
matrix = compute_last2_heatmap_matrix(freq)
labels = [[f"{r*10+c:02d}" for c in range(10)] for r in range(10)]

fig_heat = go.Figure(go.Heatmap(
    z=matrix,
    x=[str(i) for i in range(10)],
    y=[str(i) for i in range(10)],
    colorscale=[
        [0.00, "#0D0808"],
        [0.22, "#3A0A0A"],
        [0.46, "#7A1818"],
        [0.68, "#B84A12"],
        [0.84, "#C9A84C"],
        [1.00, "#FFED80"],
    ],
    text=labels,
    texttemplate="%{text}",
    hovertemplate=mode_text("เลข: %{text}<br>ออก: %{z} ครั้ง<extra></extra>", "Node: %{text}<br>Count: %{z}<extra></extra>"),
    showscale=True,
    colorbar=dict(
        title=dict(text=mode_text("ครั้ง", "Draws"), font=dict(color="#C9A84C", size=12)),
        tickfont=dict(color="#EDE0C4"),
        outlinecolor="rgba(201,168,76,0.4)",
        outlinewidth=1,
        thickness=14,
        bgcolor="rgba(13,8,8,0.6)",
    ),
))
fig_heat = apply_layout(
    fig_heat,
    title=mode_text("ความถี่การออกของเลขท้าย 2 ตัว", "Empirical Last_2 Frequency"),
    xaxis_title=mode_text("หลักหน่วย", "Ones Digit"),
    yaxis_title=mode_text("หลักสิบ", "Tens Digit"),
    height=520,
    paper_bgcolor="rgba(80,12,12,0.18)",
)
fig_heat.update_traces(
    textfont=dict(size=12, color="#F8F1DF"),
    xgap=3,
    ygap=3,
)
fig_heat.update_layout(
    shapes=[dict(
        type="rect",
        xref="paper", yref="paper",
        x0=0, y0=0, x1=1, y1=1,
        line=dict(color="rgba(201,168,76,0.7)", width=2),
        fillcolor="rgba(0,0,0,0)",
        layer="above",
    )]
)
st.plotly_chart(fig_heat, width="stretch", config=PLOTLY_CONFIG)

# --- Hot / Cold ---
hot, cold = get_hot_cold_numbers(freq, top_n=10)
col_hot, col_cold = st.columns(2)

with col_hot:
    st.subheader(mode_text("🔥 เลขที่ออกบ่อย", "🔥 High-Frequency Nodes"))
    for num, count in hot.items():
        st.markdown(f'<div class="hot-tag">{mode_text("เลข", "Node")} {num} — {count} {mode_text("ครั้ง", "draws")}</div>', unsafe_allow_html=True)

with col_cold:
    st.subheader(mode_text("🧊 เลขที่ออกน้อย", "🧊 Low-Frequency Nodes"))
    for num, count in cold.items():
        st.markdown(f'<div class="cold-tag">{mode_text("เลข", "Node")} {num} — {count} {mode_text("ครั้ง", "draws")}</div>', unsafe_allow_html=True)

# --- Max Drawdown ---
st.markdown("---")
st.subheader(mode_text("📉 เลขที่เคยหายหน้าไปนานที่สุด", "📉 Maximum Inter-Arrival Time"))
layman_dd = "ช่วงเลข 'จำศีล' - ดูว่าเลขไหนเคยหายหน้าไปนานที่สุดกี่งวด ใครที่กำลังรอเลขตัวไหนอยู่ มาเช็กดูได้ว่ามันเคยทำสถิติหนีหายไปนานแค่ไหนก่อนจะโผล่มาอีกรอบ"
math_dd = "Maximum inter-arrival time measures the longest observed gap between occurrences of the same node in a time-series process."
formula_dd = r"\text{MaxGap}(x) = \max_{i \in \{1 \dots k-1\}} (t_{x, i+1} - t_{x, i} - 1)"
render_explanation(layman_dd, math_dd, formula_dd)

dd_df = compute_max_drawdown_per_number(filtered)

tab1, tab2 = st.tabs([
    mode_text("📊 กราฟ", "📊 Visualization"),
    mode_text("📋 ตาราง", "📋 Data Table"),
])
with tab1:
    top_dd = dd_df.head(20)
    fig_dd = go.Figure(go.Bar(
        x=top_dd["Number"],
        y=top_dd["Max_Gap"],
        marker=dict(
            color=top_dd["Max_Gap"],
            colorscale=[
                [0.0, "rgba(120,90,20,0.50)"],
                [0.5, "rgba(201,168,76,0.80)"],
                [1.0, "rgba(240,220,130,1.00)"],
            ],
            showscale=False,
            line=dict(color="rgba(201,168,76,0.25)", width=1),
        ),
        text=top_dd["Max_Gap"],
        textposition="outside",
        textfont=dict(color="#EDE0C4", size=11),
        hovertemplate=mode_text("เลข: %{x}<br>หายไปนาน: %{y} งวด<extra></extra>", "Node: %{x}<br>Max gap: %{y} draws<extra></extra>"),
    ))
    fig_dd = apply_layout(
        fig_dd,
        title=mode_text("20 เลขที่เคยหายหน้าไปนานที่สุด", "Top 20 Maximum Gap Nodes"),
        xaxis_title=mode_text("เลข", "Node"),
        yaxis_title=mode_text("จำนวนงวด", "Draw Count"),
        height=420,
    )
    st.plotly_chart(fig_dd, width="stretch", config=PLOTLY_CONFIG)

with tab2:
    display_df = dd_df.copy().rename(columns={
        "Number": mode_text("เลข", "Node"),
        "Max_Gap": mode_text("เว้นช่วงนานสุด (งวด)", "Max Gap (draws)"),
        "Current_Gap": mode_text("เว้นช่วงล่าสุด (งวด)", "Current Gap (draws)"),
        "Last_Seen": mode_text("มาครั้งล่าสุดเมื่อ", "Last Seen")
    })
    last_seen_col = mode_text("มาครั้งล่าสุดเมื่อ", "Last Seen")
    display_df[last_seen_col] = display_df[last_seen_col].apply(
        lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) else mode_text("ไม่เคยออก", "Never Seen")
    )
    st.dataframe(display_df, width="stretch", hide_index=True)
