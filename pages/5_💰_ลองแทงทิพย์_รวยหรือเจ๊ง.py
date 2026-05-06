import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from lotto.theme import inject_css, apply_layout, PLOTLY_CONFIG, CRIMSON, GOLD, init_persona, render_explanation, mode_text, is_math_mode
from lotto.data_loader import load_data
from lotto.backtest import run_backtest, PRIZE_PAYOUTS, TICKET_PRICE

st.set_page_config(page_title="ลองแทงทิพย์: รวยหรือเจ๊ง?", page_icon="💰", layout="wide")
inject_css()
init_persona()

df = st.session_state["df"] if "df" in st.session_state else load_data()
if df.empty:
    st.error("ไม่พบข้อมูล")
    st.stop()

st.title(mode_text("💰 ลองแทงทิพย์: รวยหรือเจ๊ง?", "💰 Strategy Backtest"))
st.markdown(
    f'<div class="disclaimer">{mode_text("⚠️ จำลองความเสี่ยงแบบไม่ต้องเสียเงินจริง ผลลัพธ์นี้ใช้เพื่อเรียนรู้ ไม่ใช่คำแนะนำให้ซื้อ", "⚠️ Risk simulation only. Results are descriptive; the computation is unchanged across display modes.")}</div>',
    unsafe_allow_html=True,
)

STRATEGY_DISPLAY = {
    "fixed":          mode_text("ซื้อเลขเดิมทุกงวด", "Fixed — same number every draw"),
    "martingale":     mode_text("ทบสองเมื่อแพ้ (Martingale)", "Martingale — double stake after loss"),
    "anti_martingale":mode_text("ทบสองเมื่อชนะ (Anti-Martingale)", "Anti-Martingale — double stake after win"),
    "random":         mode_text("สุ่มเลขใหม่ทุกงวด", "Random — new number each draw"),
}

PRIZE_DISPLAY = {
    "Last_2":  mode_text("เลขท้าย 2 ตัว", "Last 2 Digits"),
    "First_3": mode_text("เลขหน้า 3 ตัว", "Front 3 Digits"),
    "Last_3":  mode_text("เลขท้าย 3 ตัว", "Last 3 Digits"),
    "Prize_1": mode_text("รางวัลที่ 1", "First Prize"),
}

with st.expander(mode_text("⚙️ ตั้งค่ากลยุทธ์และการลงทุน", "⚙️ Simulation Parameters"), expanded=not st.session_state.get("bt_result") is not None):
    col1, col2, col3 = st.columns(3)
    with col1:
        initial_capital = st.number_input(
            mode_text("ทุนเริ่มต้น (฿)", "Initial Capital (฿)"),
            1000, 1_000_000, 10_000, step=1000,
        )
        strategy_key = st.selectbox(
            mode_text("กลยุทธ์การเดินเงิน", "Execution Strategy"),
            options=list(STRATEGY_DISPLAY.keys()),
            format_func=lambda x: STRATEGY_DISPLAY[x],
        )

    with col2:
        prize_type = st.selectbox(
            mode_text("ประเภทรางวัล", "Prize Type"),
            options=list(PRIZE_DISPLAY.keys()),
            format_func=lambda x: PRIZE_DISPLAY[x],
        )
        target_input = st.text_input(
            mode_text("เลขเป้าหมาย (คั่นด้วย ,)", "Target Numbers (comma-separated)"),
            "07",
        )

    with col3:
        base_bet = st.number_input(
            mode_text("เงินเดิมพันต่อเลข (฿)", "Base Bet per Number (฿)"),
            80, 10_000, 80, step=80,
        )
        tickets = st.number_input(
            mode_text("จำนวนใบต่อเลข", "Tickets per Number"),
            1, 50, 1,
        )
        max_stake = st.number_input(
            mode_text("วงเงินสูงสุดต่องวด (฿)", "Max Stake per Draw (฿)"),
            base_bet, 100_000, 5_000, step=500,
        )

    payout = PRIZE_PAYOUTS[prize_type]
    st.caption(mode_text(
        f"รางวัลต่อใบที่ถูก: ฿{payout:,.0f} | ราคาใบ: ฿{TICKET_PRICE}",
        f"Payout per winning ticket: ฿{payout:,.0f} | Ticket price: ฿{TICKET_PRICE}",
    ))
    run_btn = st.button(mode_text("▶️ เริ่มจำลองกลยุทธ์", "▶ Run Backtest"), type="primary", use_container_width=True)

target_numbers = [n.strip().zfill(2) for n in target_input.split(",") if n.strip()]

if run_btn:
    with st.spinner(mode_text("กำลังจำลอง...", "Running simulation...")):
        result = run_backtest(
            df, prize_type=prize_type, strategy=strategy_key,
            initial_capital=initial_capital, base_bet=base_bet,
            tickets_per_number=tickets, target_numbers=target_numbers,
            max_stake_per_draw=max_stake,
        )
    st.session_state["bt_result"] = result
    st.session_state["bt_capital"] = initial_capital

result = st.session_state.get("bt_result")
if result is None:
    st.info(mode_text("ตั้งค่ากลยุทธ์แล้วกดปุ่มเริ่มจำลอง", "Configure parameters and click Run Backtest."))
    st.stop()

initial_capital = st.session_state.get("bt_capital", 10_000)

# KPI metrics
st.subheader(mode_text("📊 ผลลัพธ์การจำลอง", "📊 Simulation Results"))
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric(mode_text("ทุนสุดท้าย", "Final Equity"), f"฿{result.final_equity:,.0f}", f"{result.net_pnl:+,.0f}")
with c2:
    st.metric(mode_text("อัตราการชนะ", "Win Rate"), f"{result.win_rate*100:.2f}%")
with c3:
    st.metric(mode_text("ขาดทุนสะสมสูงสุด", "Max Drawdown"), f"{result.max_drawdown*100:.1f}%")
with c4:
    st.metric(
        mode_text("แพ้ติดกันยาวสุด", "Longest Losing Streak"),
        mode_text(f"{result.longest_losing_streak} งวด", f"{result.longest_losing_streak} draws"),
    )
with c5:
    st.metric(
        mode_text("สถานะ", "Status"),
        mode_text("💀 ล้มละลาย", "💀 Bankrupt") if result.bankrupt else mode_text("✅ รอด", "✅ Solvent"),
    )

# Equity curve
st.markdown("---")
st.subheader(mode_text("📈 เส้นทางเงินทุน", "📈 Equity Curve"))
records = result.records
dates = [r.draw_date for r in records]
equities = [r.equity for r in records]

fig_eq = go.Figure()
fig_eq.add_scatter(
    x=dates, y=equities,
    mode="lines",
    name=mode_text("ทุนสะสม", "Equity"),
    line=dict(color=CRIMSON, width=2),
    fill="tozeroy",
    fillcolor="rgba(122,24,24,0.12)",
)
fig_eq.add_hline(
    y=initial_capital,
    line_dash="dash",
    line_color=GOLD,
    opacity=0.6,
    annotation_text=mode_text("ทุนเริ่มต้น", "Initial Capital"),
    annotation_font_color=GOLD,
)
fig_eq.add_hline(y=0, line_color="rgba(237,224,196,0.2)", line_width=1)
fig_eq = apply_layout(
    fig_eq,
    title=mode_text("ความเคลื่อนไหวของเงินทุนตลอดการจำลอง", "Capital Trajectory over Simulation"),
    xaxis_title=mode_text("งวดวันที่", "Draw Date"),
    yaxis_title=mode_text("เงินทุน (฿)", "Equity (฿)"),
    height=420,
)
st.plotly_chart(fig_eq, width="stretch", config=PLOTLY_CONFIG)

# Detail table
st.subheader(mode_text("📋 รายละเอียดทุกงวด", "📋 Transaction Log"))
records_df = pd.DataFrame([{
    mode_text("งวด", "Draw Date"):             r.draw_date,
    mode_text("เลขที่ซื้อ", "Numbers Bet"):    ", ".join(r.numbers_bet),
    mode_text("ผลจริง", "Actual Result"):       r.actual,
    mode_text("ชนะ", "Hit"):                   "✅" if r.won else "❌",
    mode_text("เงินเดิมพัน (฿)", "Stake (฿)"): f"{r.bet_per_number * r.tickets_per_number * len(r.numbers_bet):.0f}",
    mode_text("รายได้ (฿)", "Gross Payout (฿)"): f"{r.gross_payout:.0f}",
    mode_text("กำไร/ขาดทุน (฿)", "PnL (฿)"):  f"{r.pnl:+.0f}",
    mode_text("ทุนสะสม (฿)", "Equity (฿)"):    f"{r.equity:,.0f}",
} for r in records])
st.dataframe(
    records_df, width="stretch", hide_index=True,
    column_config={mode_text("ชนะ", "Hit"): st.column_config.TextColumn(width="small")},
)

# Financial summary
st.markdown("---")
layman_roi = "ความคุ้มค่าของการลงทุน — ทุกๆ 100 บาทที่ควักกระเป๋าไป เราได้กลับมาเฉลี่ยกี่บาท ถ้าได้น้อยกว่า 100 แปลว่าขาดทุน ซึ่งในกรณีของหวยมักเป็นแบบนั้นเสมอ"
math_roi = "Expected return and ROI summarize the economic outcome of a strategy under uncertainty by comparing total payouts against total capital outflow."
formula_roi = r"ROI = \frac{\sum \text{Payout} - \sum \text{Cost}}{\sum \text{Cost}} \times 100\%"
render_explanation(layman_roi, math_roi, formula_roi)

col_a, col_b = st.columns(2)
with col_a:
    st.metric(mode_text("เงินที่ใช้ทั้งหมด (฿)", "Total Capital Outflow (฿)"), f"฿{result.total_spent:,.0f}")
with col_b:
    st.metric(mode_text("เงินที่ได้รับคืนทั้งหมด (฿)", "Total Capital Inflow (฿)"), f"฿{result.total_payout:,.0f}")

roi = (result.total_payout / result.total_spent - 1) * 100 if result.total_spent > 0 else 0
roi_label = mode_text("อัตราส่วนผลตอบแทน (ROI)", "Net ROI")
st.metric(roi_label, f"{roi:.1f}%", delta=f"{roi:.1f}%")
