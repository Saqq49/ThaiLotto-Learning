import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from lotto.theme import inject_css, apply_layout, CRIMSON, GOLD, PANEL, TEXT, TEXT_DARK, PANEL_WHITE
from lotto.data_loader import load_data, compute_last2_frequency, filter_by_date
from lotto.stats import compute_last2_heatmap_matrix, compute_max_drawdown_per_number, get_hot_cold_numbers

st.set_page_config(page_title="เลขไหนฮิต เลขไหนดับ", page_icon="📊", layout="wide")
inject_css()

df = st.session_state["df"] if "df" in st.session_state else load_data()
if df.empty:
    st.error("ไม่พบข้อมูล")
    st.stop()

st.title("📊 เลขไหนฮิต เลขไหนดับ")
st.markdown("สถิติความถี่ของเลขท้าย 2 ตัว — มาดูว่าเลขไหนมาแรง เลขไหนหายเงียบ")

# Sidebar filters
with st.sidebar:
    st.header("ตัวกรอง")
    min_date = df["Draw_Date"].min().date()
    max_date = df["Draw_Date"].max().date()
    date_range = st.date_input("ช่วงวันที่", value=(min_date, max_date), min_value=min_date, max_value=max_date)

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    filtered = filter_by_date(df, pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]))
else:
    filtered = df

if filtered.empty:
    st.warning("ไม่มีข้อมูลในช่วงนี้")
    st.stop()

freq = compute_last2_frequency(filtered)
st.caption(f"แสดงข้อมูล {len(filtered)} งวด")

# --- Heatmap ---
st.subheader("🗺️ Frequency Heatmap (เลข 00–99)")
matrix = compute_last2_heatmap_matrix(freq)
labels = [[f"{r*10+c:02d}" for c in range(10)] for r in range(10)]

fig_heat = go.Figure(go.Heatmap(
    z=matrix,
    x=[str(i) for i in range(10)],
    y=[str(i) for i in range(10)],
    colorscale=[
        [0.0, PANEL],
        [0.4, GOLD],
        [1.0, CRIMSON],
    ],
    text=labels,
    texttemplate="%{text}",
    hovertemplate="เลข: %{text}<br>ออก: %{z} ครั้ง<extra></extra>",
    showscale=True,
    colorbar=dict(title="ครั้ง", tickfont=dict(color=TEXT)),
))
fig_heat = apply_layout(
    fig_heat,
    title="ความถี่การออกของเลขท้าย 2 ตัว",
    xaxis_title="หลักหน่วย",
    yaxis_title="หลักสิบ",
    height=500,
)
fig_heat.update_traces(textfont=dict(size=11, color=TEXT))
st.plotly_chart(fig_heat, width="stretch")

# --- Hot / Cold ---
hot, cold = get_hot_cold_numbers(freq, top_n=10)
col_hot, col_cold = st.columns(2)

with col_hot:
    st.subheader("🔥 Hot Numbers (ออกบ่อย)")
    for num, count in hot.items():
        st.markdown(f'<div class="hot-tag">เลข {num} — {count} ครั้ง</div>', unsafe_allow_html=True)

with col_cold:
    st.subheader("🧊 Cold Numbers (ออกน้อย)")
    for num, count in cold.items():
        st.markdown(f'<div class="cold-tag">เลข {num} — {count} ครั้ง</div>', unsafe_allow_html=True)

# --- Max Drawdown ---
st.markdown("---")
st.subheader("📉 Max Drawdown per Number")
st.caption("ทิ้งช่วงนานที่สุด (จำนวนงวด) ก่อนที่เลขนั้นจะกลับมาออกอีกครั้ง")

dd_df = compute_max_drawdown_per_number(filtered)

tab1, tab2 = st.tabs(["📊 กราฟ", "📋 ตาราง"])
with tab1:
    top_dd = dd_df.head(20)
    fig_dd = go.Figure(go.Bar(
        x=top_dd["Number"], y=top_dd["Max_Gap"],
        marker_color=CRIMSON, text=top_dd["Max_Gap"], textposition="outside",
        hovertemplate="เลข: %{x}<br>Max Gap: %{y} งวด<extra></extra>",
    ))
    fig_dd = apply_layout(fig_dd, title="Top 20 เลขที่มี Max Gap สูงสุด",
                          xaxis_title="เลข", yaxis_title="จำนวนงวด", height=400)
    st.plotly_chart(fig_dd, width="stretch")

with tab2:
    display_df = dd_df.copy()
    display_df["Last_Seen"] = display_df["Last_Seen"].apply(
        lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) else "ไม่เคยออก"
    )
    st.dataframe(display_df, width="stretch", hide_index=True)
