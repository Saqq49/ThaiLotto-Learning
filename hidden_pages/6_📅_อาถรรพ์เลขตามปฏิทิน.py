import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from lotto.theme import inject_css, apply_layout, CRIMSON, GOLD, GOLD_SOLID, init_persona, render_explanation, mode_text, is_math_mode, TEXT_PRIMARY
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


st.title(mode_text("📅 อาถรรพ์เลขตามปฏิทิน", "📅 Calendar Effect Test"))
st.markdown(mode_text(
    "ทดสอบว่า เดือนหรือวันที่ออกรางวัล มีผลต่อเลขที่ออกจริงๆ ไหม หรือทั้งหมดเป็นแค่เรื่องบังเอิญ",
    "Evaluate whether month or weekday categories show statistically meaningful deviations from baseline randomness.",
))

monthly_freq, dow_counts, (chi2_m, p_m), (chi2_d, p_d), monthly_counts, top20 = get_seasonality_summary(df)

layman_chi = (
    "**วิธีทดสอบ:** ถ้าหวยสุ่มจริงๆ แต่ละเดือนควรออกเลขทุกตัวในอัตราพอๆ กัน "
    "เราเลยนับว่าเลขแต่ละตัวออกในเดือนไหนบ้าง แล้วเปรียบกับที่ควรจะเป็นถ้าสุ่มสมบูรณ์\n\n"
    "**ค่า p-value คืออะไร?** คือโอกาสที่เราจะเห็นข้อมูลแบบนี้ แม้ว่าจริงๆ มันสุ่มอย่างสมบูรณ์ "
    "ถ้า p < 0.05 แปลว่า 'ข้อมูลดูแปลกมากพอที่จะน่าสงสัย' "
    "แต่ถ้า p ≥ 0.05 แปลว่า 'ดูเหมือนสุ่มปกติ ไม่มีอะไรน่าตกใจ'"
)
math_chi = (
    "Chi-squared goodness-of-fit test for calendar independence. "
    "Observed cell frequencies are compared against expected uniform counts under H₀ (calendar category has no effect on Last_2 outcome). "
    "p < 0.05 rejects H₀ at the 5% significance level."
)
formula_chi = r"\chi^2 = \sum_{i=1}^{k} \frac{(O_i - E_i)^2}{E_i}, \quad E_i = \frac{N}{k}"
render_explanation(layman_chi, math_chi, formula_chi)

tab1, tab2, tab3 = st.tabs([
    mode_text("📆 รายเดือน", "📆 Monthly Distribution"),
    mode_text("📅 รายวัน", "📅 Weekday Distribution"),
    mode_text("🔍 ติดตามเลขเฉพาะ", "🔍 Node Drilldown"),
])

# Shared heatmap colorscale
HEATMAP_COLORSCALE = [
    [0.00, "#0D0808"],
    [0.22, "#3A0A0A"],
    [0.46, "#7A1818"],
    [0.68, "#B84A12"],
    [0.84, "#C9A84C"],
    [1.00, "#FFED80"],
]

def p_result_box(p_val: float, layman_pass: str, layman_fail: str, math_pass: str, math_fail: str, chi2: float, label_th: str, label_en: str):
    passed = p_val > 0.05
    color = "#4CAF50" if passed else CRIMSON
    interpretation_th = layman_pass if passed else layman_fail
    interpretation_en = math_pass if passed else math_fail
    st.markdown(f"""
    <div style="border:1px solid {color}55; background:{color}08; padding:18px 20px; border-radius:10px; margin-bottom:18px;">
        <h4 style="color:{color}; margin:0 0 8px 0;">{mode_text(label_th, label_en)}</h4>
        <p style="margin:2px 0; color:{TEXT_PRIMARY}; font-size:0.9rem;">
            χ² = <b>{chi2:.2f}</b> &nbsp;|&nbsp; p-value = <b>{p_val:.4f}</b>
            &nbsp;|&nbsp; {"✅ " if passed else "⚠️ "}{"p ≥ 0.05" if passed else "p < 0.05"}
        </p>
        <p style="margin:6px 0 0 0; color:{TEXT_PRIMARY}; opacity:0.75; font-size:0.88rem;">
            {mode_text(interpretation_th, interpretation_en)}
        </p>
    </div>
    """, unsafe_allow_html=True)


# --- Tab 1: Monthly ---
with tab1:
    st.subheader(mode_text("เดือนมีผลต่อเลขที่ออกไหม?", "Monthly Independence Test"))
    st.markdown(mode_text(
        "เราดูว่าแต่ละเดือน เลขท้าย 2 ตัวกระจายตัวสม่ำเสมอไหม "
        "หรือมีเดือนไหนที่เลขบางตัวออกบ่อยผิดปกติ",
        "Testing whether Last_2 frequencies are uniformly distributed across calendar months.",
    ))

    p_result_box(
        p_m, chi2=chi2_m,
        layman_pass="สรุป: ยังไม่พบหลักฐานที่ชัดเจนว่าเดือนมีผลต่อเลขที่ออก — ดูเหมือนสุ่มปกติดี",
        layman_fail="สรุป: ข้อมูลดูผิดปกติจากการสุ่มล้วนๆ แต่ยังไม่ได้แปลว่าเดือนทำนายเลขได้จริง เพราะอาจเป็นแค่ความบังเอิญในข้อมูลชุดนี้",
        math_pass="Result: Fail to reject H₀ (p ≥ 0.05). No statistically significant monthly effect detected.",
        math_fail="Result: Reject H₀ (p < 0.05). Monthly distribution deviates from uniform baseline. Note: statistical significance ≠ predictive power.",
        label_th="ผลทดสอบ: เดือนกับเลขสลาก",
        label_en="Test Result: Month × Last_2 Independence",
    )

    fig_mc = go.Figure(go.Bar(
        x=monthly_counts["Month_Name"],
        y=monthly_counts["draws"],
        marker=dict(
            color=monthly_counts["draws"],
            colorscale=[[0, "rgba(120,90,20,0.5)"], [0.5, "rgba(201,168,76,0.8)"], [1, "rgba(240,220,130,1)"]],
            showscale=False,
            line=dict(color="rgba(201,168,76,0.2)", width=1),
        ),
        text=monthly_counts["draws"],
        textposition="outside",
        textfont=dict(color="#EDE0C4", size=11),
        hovertemplate=mode_text("เดือน: %{x}<br>จำนวนงวด: %{y}<extra></extra>", "Month: %{x}<br>Draws: %{y}<extra></extra>"),
    ))
    fig_mc = apply_layout(
        fig_mc,
        title=mode_text("จำนวนงวดในแต่ละเดือน (หวยออกวันที่ 1 และ 16)", "Draw Count by Month"),
        xaxis_title=mode_text("เดือน", "Month"),
        yaxis_title=mode_text("จำนวนงวด", "Draw Count"),
        height=360,
    )
    st.plotly_chart(fig_mc, width="stretch")

    st.subheader(mode_text(
        "แผนภูมิสี: แต่ละเดือนเลขไหนออกบ่อย?",
        "Heatmap: Monthly Frequency × Top 20 Nodes",
    ))
    st.caption(mode_text(
        "สีเข้ม (ทอง) = ออกบ่อยในเดือนนั้น | สีจาง (แดงเข้ม) = ออกน้อย — ดูว่ามีเดือนไหนที่เลขบางตัวเด่นกว่าปกติไหม",
        "Bright gold = high frequency in that month | Dark = low frequency. Look for cells that stand out from their row/column.",
    ))
    heat_data = monthly_freq[top20]
    month_labels = [MONTH_NAMES[m] for m in heat_data.index]
    fig_mh = go.Figure(go.Heatmap(
        z=heat_data.values,
        x=[str(n) for n in top20],
        y=month_labels,
        colorscale=HEATMAP_COLORSCALE,
        hovertemplate=mode_text(
            "เดือน: %{y}<br>เลข: %{x}<br>ออก: %{z} ครั้ง<extra></extra>",
            "Month: %{y}<br>Node: %{x}<br>Count: %{z}<extra></extra>",
        ),
        showscale=True,
        colorbar=dict(
            title=dict(text=mode_text("ครั้ง", "Draws"), font=dict(color=GOLD_SOLID)),
            tickfont=dict(color="#EDE0C4"),
            outlinecolor="rgba(201,168,76,0.4)",
            outlinewidth=1,
            thickness=14,
        ),
    ))
    fig_mh = apply_layout(
        fig_mh,
        title=mode_text("ความถี่รายเดือนของ 20 เลขที่ออกบ่อยที่สุด", "Monthly Frequency — Top 20 Nodes"),
        xaxis_title=mode_text("เลขท้าย 2 ตัว", "Last 2 Digits"),
        yaxis_title=mode_text("เดือน", "Month"),
        height=450,
    )
    fig_mh.update_traces(xgap=2, ygap=2)
    fig_mh.update_layout(
        shapes=[dict(
            type="rect", xref="paper", yref="paper",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color="rgba(201,168,76,0.6)", width=1.5),
            fillcolor="rgba(0,0,0,0)", layer="above",
        )]
    )
    st.plotly_chart(fig_mh, width="stretch")

# --- Tab 2: Day of Week ---
with tab2:
    st.subheader(mode_text("วันในสัปดาห์มีผลต่อเลขไหม?", "Weekday Independence Test"))
    st.markdown(mode_text(
        "หวยไทยออกวันที่ 1 และ 16 ของทุกเดือน ซึ่งตกวันไหนในสัปดาห์ก็แล้วแต่ปฏิทิน "
        "เราเลยตรวจดูว่าวันที่ออก (จันทร์-อาทิตย์) มีผลต่อเลขที่ออกหรือเปล่า",
        "Thai lottery draws fall on the 1st and 16th of each month, which land on different weekdays. "
        "This tab tests whether the weekday of a draw date correlates with Last_2 outcomes.",
    ))

    p_result_box(
        p_d, chi2=chi2_d,
        layman_pass="สรุป: วันในสัปดาห์ไม่ได้มีผลพิเศษต่อเลขที่ออก — ดูปกติดี",
        layman_fail="สรุป: การกระจายตามวันดูไม่สม่ำเสมอ แต่นั่นอาจเป็นเพราะปฏิทินทำให้บางวันมีงวดมากกว่าวันอื่น ไม่ใช่เพราะวันทำนายเลขได้",
        math_pass="Result: Fail to reject H₀ (p ≥ 0.05). No significant weekday effect on Last_2 distribution.",
        math_fail="Result: Reject H₀ (p < 0.05). Weekday distribution is non-uniform, likely due to calendar mechanics rather than any predictive relationship.",
        label_th="ผลทดสอบ: วันออกรางวัลกับเลขสลาก",
        label_en="Test Result: Weekday × Last_2 Independence",
    )

    fig_dow = go.Figure(go.Bar(
        x=list(dow_counts.index),
        y=list(dow_counts.values),
        marker=dict(
            color=[
                "rgba(201,168,76,0.9)" if d in ["Saturday", "Sunday"] else "rgba(122,24,24,0.8)"
                for d in dow_counts.index
            ],
            line=dict(color="rgba(201,168,76,0.3)", width=1),
        ),
        text=list(dow_counts.values),
        textposition="outside",
        textfont=dict(color="#EDE0C4", size=11),
        hovertemplate=mode_text("วัน: %{x}<br>จำนวนงวด: %{y}<extra></extra>", "Weekday: %{x}<br>Draws: %{y}<extra></extra>"),
    ))
    fig_dow = apply_layout(
        fig_dow,
        title=mode_text("จำนวนงวดที่ตกในแต่ละวัน (สีทอง = เสาร์-อาทิตย์)", "Draw Count by Weekday (gold = weekend)"),
        xaxis_title=mode_text("วันในสัปดาห์", "Weekday"),
        yaxis_title=mode_text("จำนวนงวด", "Draw Count"),
        height=380,
    )
    st.plotly_chart(fig_dow, width="stretch")

# --- Tab 3: Specific number ---
with tab3:
    st.subheader(mode_text("ติดตามเลขเดียว รายเดือน", "Individual Node Monthly Analysis"))
    st.markdown(mode_text(
        "เลือกเลข 2 หลักที่สนใจ แล้วดูว่ามันออกบ่อยแค่ไหนในแต่ละเดือน "
        "เส้นประสีทอง = ค่าที่ควรจะเป็นถ้าสุ่มสมบูรณ์ ถ้าแท่งสูงกว่าเส้น = เดือนนั้นออกบ่อยกว่าคาด",
        "Select a two-digit node to inspect its per-month hit rate. "
        "The dashed line shows the expected rate under perfect randomness (1% per draw).",
    ))

    num_input = st.text_input(
        mode_text("ใส่เลข 2 หลักที่ต้องการ", "Target Node (00–99)"),
        "07", max_chars=2,
    )

    if num_input.isdigit() and len(num_input) == 2:
        summary_df = get_monthly_number_summary(df, num_input.zfill(2))
        expected = len(df) / 100 / 12
        st.caption(mode_text(
            f"ถ้าสุ่มสมบูรณ์ เลข {num_input} ควรออกราวๆ {expected:.1f} ครั้งต่อเดือน",
            f"Expected frequency under uniform randomness: {expected:.2f} hits/month",
        ))
        st.dataframe(summary_df.rename(columns={
            "Month":   mode_text("เดือน", "Month"),
            "Hits":    mode_text("จำนวนที่ออก", "Hits"),
            "Rate_%":  mode_text("อัตราส่วน (%)", "Rate (%)"),
        }), width="stretch", hide_index=True)

        expected_rate = 100 / 100
        fig_ns = go.Figure(go.Bar(
            x=summary_df["Month"],
            y=summary_df["Rate_%"],
            marker=dict(
                color=summary_df["Rate_%"],
                colorscale=HEATMAP_COLORSCALE,
                showscale=False,
                line=dict(color="rgba(201,168,76,0.2)", width=1),
            ),
            text=summary_df["Hits"],
            textposition="outside",
            textfont=dict(color="#EDE0C4", size=11),
            hovertemplate=mode_text(
                "เดือน: %{x}<br>อัตรา: %{y:.2f}%<extra></extra>",
                "Month: %{x}<br>Rate: %{y:.2f}%<extra></extra>",
            ),
        ))
        fig_ns.add_hline(
            y=expected_rate,
            line_dash="dash",
            line_color=GOLD,
            annotation_text=mode_text(f"ถ้าสุ่ม = {expected_rate:.1f}%", f"Baseline {expected_rate:.1f}%"),
            annotation_font_color=GOLD,
        )
        fig_ns = apply_layout(
            fig_ns,
            title=mode_text(
                f"อัตราการออกของเลข {num_input} แยกตามเดือน",
                f"Monthly Hit Rate — Node {num_input}",
            ),
            xaxis_title=mode_text("เดือน", "Month"),
            yaxis_title=mode_text("อัตราส่วน (%)", "Rate (%)"),
            height=380,
        )
        st.plotly_chart(fig_ns, width="stretch")
    else:
        st.warning(mode_text("กรุณาใส่เลข 2 หลัก เช่น 07 หรือ 23", "Enter a two-digit node, e.g. 07 or 23."))
