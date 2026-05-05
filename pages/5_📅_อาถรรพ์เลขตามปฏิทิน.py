import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from lotto.theme import inject_css, apply_layout, CRIMSON, GOLD, PANEL, TEXT, TEXT_DARK, PANEL_WHITE, init_persona, render_explanation
from lotto.data_loader import load_data
from lotto.seasonality import (compute_monthly_frequency, compute_dow_distribution,
                                chi_squared_monthly, chi_squared_dow,
                                monthly_number_summary, MONTH_NAMES, DOW_ORDER)

st.set_page_config(page_title="อาถรรพ์เลขตามปฏิทิน", page_icon="📅", layout="wide")
inject_css()
init_persona()

df = st.session_state["df"] if "df" in st.session_state else load_data()
if df.empty:
    st.error("ไม่พบข้อมูล")
    st.stop()


@st.cache_data(show_spinner=False)
def get_seasonality_summary(source_df: pd.DataFrame):
    monthly = compute_monthly_frequency(source_df)
    dow = compute_dow_distribution(source_df)
    monthly_chi = chi_squared_monthly(source_df)
    dow_chi = chi_squared_dow(source_df)
    monthly_counts_df = source_df.groupby("Month").size().reset_index(name="draws")
    monthly_counts_df["Month_Name"] = monthly_counts_df["Month"].map(MONTH_NAMES)
    top_numbers = source_df["Last_2"].value_counts().head(20).index.tolist()
    return monthly, dow, monthly_chi, dow_chi, monthly_counts_df, top_numbers


@st.cache_data(show_spinner=False)
def get_monthly_number_summary(source_df: pd.DataFrame, number: str) -> pd.DataFrame:
    return monthly_number_summary(source_df, number)


st.title("📅 อาถรรพ์เลขตามปฏิทิน")
st.markdown("เลขไหนชอบมาวันไหน? เดือนไหนมีเลขอะไรพิเศษ? — มาพิสูจน์ความเชื่อด้วยสถิติกัน")

monthly_freq, dow_counts, (chi2_m, p_m), (chi2_d, p_d), monthly_counts, top20 = get_seasonality_summary(df)

render_explanation(
    "การเช็กความแปลกแยก - ดูว่าข้อมูลที่เห็นมันต่างจากการสุ่มมั่วๆ จนผิดปกติไหม (ถ้า p-value น้อยกว่า 0.05 คือเริ่มมีเงื่อนงำ)",
    "Chi-Squared Independence Test ใช้ทดสอบความสัมพันธ์ระหว่างตัวแปรเชิงคุณภาพสองตัว เพื่อดูว่ามีความแตกต่างจากผลลัพธ์ที่คาดหวังภายใต้สมมติฐานหลัก (Null Hypothesis) หรือไม่",
    r"\chi^2 = \sum \frac{(O - E)^2}{E}"
)

tab1, tab2, tab3 = st.tabs(["📆 รายเดือน", "📅 Day of Week", "🔍 เจาะเลขเฉพาะ"])

# --- Tab 1: Monthly ---
with tab1:
    st.subheader("การกระจายเลขตามเดือน")

    if len(df["Last_2"].unique()) < 10:
        st.warning("ข้อมูลน้อยเกินไปสำหรับ Chi-Squared Test ที่น่าเชื่อถือ")

    color_p = "#4CAF50" if p_m > 0.05 else CRIMSON
    st.markdown(f"""
    <div style="border:1px solid {color_p}33; background:{color_p}05; padding:16px; border-radius:8px; margin-bottom:16px;">
        <h4 style="color:{color_p}; margin:0;">Chi-Squared Test: เดือน × ความถี่เลข</h4>
        <p style="margin:4px 0; color:{TEXT_DARK};">χ² = {chi2_m:.2f} &nbsp;|&nbsp; p-value = <b>{p_m:.4f}</b></p>
        <p style="margin:0; color:{TEXT_DARK}; opacity:0.6;">{"ไม่พบหลักฐานว่าเดือนทำให้เลขออกต่างจากความสุ่มอย่างมีนัยสำคัญ" if p_m > 0.05 else "พบความต่างในข้อมูลย้อนหลัง แต่ยังไม่ใช่หลักฐานว่าใช้ทำนายอนาคตได้"}</p>
    </div>
    """, unsafe_allow_html=True)

    # Monthly draw count bar chart
    fig_mc = go.Figure(go.Bar(
        x=monthly_counts["Month_Name"], y=monthly_counts["draws"],
        marker_color=CRIMSON, text=monthly_counts["draws"], textposition="outside",
    ))
    fig_mc = apply_layout(fig_mc, title="จำนวนงวดที่ออกในแต่ละเดือน",
                          xaxis_title="เดือน", yaxis_title="จำนวนงวด", height=350)
    st.plotly_chart(fig_mc, width="stretch")

    # Monthly heatmap (month vs top numbers)
    st.subheader("Heatmap: เดือน × เลข Last_2 (Top 20 เลขที่ออกบ่อย)")
    heat_data = monthly_freq[top20]
    month_labels = [MONTH_NAMES[m] for m in heat_data.index]
    fig_mh = go.Figure(go.Heatmap(
        z=heat_data.values, x=top20, y=month_labels,
        colorscale=[[0, "#FFFFFF"], [0.5, GOLD], [1.0, CRIMSON]],
        hovertemplate="เดือน: %{y}<br>เลข: %{x}<br>ครั้ง: %{z}<extra></extra>",
    ))
    fig_mh = apply_layout(fig_mh, title="ความถี่รายเดือนของ Top-20 เลข",
                          xaxis_title="เลข", yaxis_title="เดือน", height=400)
    st.plotly_chart(fig_mh, width="stretch")

# --- Tab 2: Day of Week ---
with tab2:
    st.subheader("วันที่ 1 และ 16 ตกวันไหนบ้าง")

    color_pd = "#4CAF50" if p_d > 0.05 else CRIMSON
    st.markdown(f"""
    <div style="border:1px solid {color_pd}33; background:{color_pd}05; padding:16px; border-radius:8px; margin-bottom:16px;">
        <h4 style="color:{color_pd}; margin:0;">Chi-Squared Test: วันในสัปดาห์</h4>
        <p style="margin:4px 0; color:{TEXT_DARK};">χ² = {chi2_d:.2f} &nbsp;|&nbsp; p-value = <b>{p_d:.4f}</b></p>
        <p style="margin:0; color:{TEXT_DARK}; opacity:0.6;">{"ไม่พบหลักฐานว่าวันในสัปดาห์เป็นปัจจัยพิเศษ" if p_d > 0.05 else "การกระจายวันไม่สม่ำเสมอจากปฏิทิน แต่ไม่ได้แปลว่าวันทำนายผลเลขได้"}</p>
    </div>
    """, unsafe_allow_html=True)

    fig_dow = go.Figure(go.Bar(
        x=dow_counts.index, y=dow_counts.values,
        marker_color=[GOLD if d in ["Saturday", "Sunday"] else CRIMSON for d in dow_counts.index],
        text=dow_counts.values, textposition="outside",
    ))
    fig_dow = apply_layout(fig_dow, title="จำนวนงวดที่ออกในแต่ละวัน (วันที่ 1/16)",
                           xaxis_title="วัน", yaxis_title="จำนวนงวด", height=380)
    st.plotly_chart(fig_dow, width="stretch")

# --- Tab 3: Specific number ---
with tab3:
    st.subheader("ติดตามเลขเฉพาะรายเดือน")
    num_input = st.text_input("ใส่เลข 2 หลัก", "07", max_chars=2)
    if num_input.isdigit() and len(num_input) == 2:
        summary = get_monthly_number_summary(df, num_input.zfill(2))
        expected = len(df) / 100 / 12
        st.caption(f"Expected ออก/เดือน (สุ่มสมบูรณ์): {expected:.1f} ครั้ง")
        st.dataframe(summary, width="stretch", hide_index=True)

        fig_ns = go.Figure(go.Bar(
            x=summary["Month"], y=summary["Rate_%"],
            marker_color=CRIMSON, text=summary["Hits"], textposition="outside",
        ))
        expected_rate = 100 / 100
        fig_ns.add_hline(y=expected_rate, line_dash="dash", line_color=GOLD,
                         annotation_text=f"Expected {expected_rate:.1f}%")
        fig_ns = apply_layout(fig_ns, title=f"อัตราการออกของเลข {num_input} รายเดือน",
                              xaxis_title="เดือน", yaxis_title="Rate (%)", height=380)
        st.plotly_chart(fig_ns, width="stretch")
    else:
        st.warning("กรุณาใส่เลข 2 หลัก เช่น 07")
