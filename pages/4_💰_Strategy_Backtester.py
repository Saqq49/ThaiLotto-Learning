import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from lotto.theme import inject_css, apply_layout, CRIMSON, GOLD, PANEL_WHITE, TEXT_DARK
from lotto.data_loader import load_data
from lotto.backtest import run_backtest, PRIZE_PAYOUTS, TICKET_PRICE

st.set_page_config(page_title="Strategy Backtester", page_icon="💰", layout="wide")
inject_css()

df = st.session_state["df"] if "df" in st.session_state else load_data()
if df.empty:
    st.error("ไม่พบข้อมูล")
    st.stop()

st.title("💰 Lottery Strategy Backtester")
st.markdown('<div class="disclaimer">⚠️ เครื่องมือนี้จำลองความเสี่ยงทางการเงิน ไม่ใช่คำแนะนำการลงทุน — ผลลัพธ์ส่วนใหญ่คือการขาดทุน</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("ตั้งค่ากลยุทธ์")
    initial_capital = st.number_input("ทุนเริ่มต้น (฿)", 1000, 1_000_000, 10_000, step=1000)
    prize_type = st.selectbox("ประเภทรางวัล", ["Last_2", "First_3", "Last_3", "Prize_1"])
    strategy_options = {
        "fixed": "Fixed (ซื้อเดิมทุกงวด)",
        "martingale": "Martingale (ทบสองเมื่อแพ้)",
        "anti_martingale": "Anti-Martingale (ทบสองเมื่อชนะ)",
        "random": "Random (สุ่มเลขทุกงวด)",
    }
    strategy_key = st.selectbox("กลยุทธ์", options=list(strategy_options.keys()), format_func=lambda x: strategy_options[x])
    base_bet = st.number_input("เงินเดิมพันต่อเลข (฿)", 80, 10_000, 80, step=80)
    tickets = st.number_input("จำนวนใบต่อเลข", 1, 50, 1)
    max_stake = st.number_input("วงเงินสูงสุดต่องวด (฿)", base_bet, 100_000, 5_000, step=500)
    target_input = st.text_input("เลขเป้าหมาย (คั่นด้วย ,)", "07")
    run_btn = st.button("▶️ รัน Simulation", type="primary")

    payout = PRIZE_PAYOUTS[prize_type]
    st.caption(f"รางวัลต่อใบที่ถูกรางวัล: ฿{payout:,.0f} | ราคาใบ: ฿{TICKET_PRICE}")

    target_numbers = [n.strip().zfill(2) for n in target_input.split(",") if n.strip()]

    if run_btn:
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
    st.info("ตั้งค่ากลยุทธ์แล้วกด 'รัน Simulation'")
    st.stop()

initial_capital = st.session_state.get("bt_capital", 10_000)

# KPI metrics
st.subheader("📊 ผลลัพธ์การจำลอง")
c1, c2, c3, c4, c5 = st.columns(5)
pnl_color = CRIMSON if result.net_pnl < 0 else "#4CAF50"
with c1:
    st.metric("ทุนสุดท้าย", f"฿{result.final_equity:,.0f}", f"{result.net_pnl:+,.0f}")
with c2:
    st.metric("Win Rate", f"{result.win_rate*100:.2f}%")
with c3:
    st.metric("Max Drawdown", f"{result.max_drawdown*100:.1f}%")
with c4:
    st.metric("Losing Streak ยาวสุด", f"{result.longest_losing_streak} งวด")
with c5:
    st.metric("สถานะ", "💀 ล้มละลาย" if result.bankrupt else "✅ รอด")

# Equity curve
st.markdown("---")
st.subheader("📈 Equity Curve")
records = result.records
dates = [r.draw_date for r in records]
equities = [r.equity for r in records]

fig_eq = go.Figure()
fig_eq.add_scatter(x=dates, y=equities, mode="lines", name="Equity",
                   line=dict(color=CRIMSON, width=2), fill="tozeroy",
                   fillcolor=f"{CRIMSON}11")
fig_eq.add_hline(y=initial_capital, line_dash="dash", line_color=TEXT_DARK,
                 opacity=0.3, annotation_text="ทุนเริ่มต้น")
fig_eq.add_hline(y=0, line_color=TEXT_DARK, line_width=1, opacity=0.5)
fig_eq = apply_layout(fig_eq, title="เส้นทุน (Equity Curve)",
                      xaxis_title="งวด", yaxis_title="ทุน (฿)", height=400)
st.plotly_chart(fig_eq, width="stretch")

# Detail table
st.subheader("📋 รายละเอียดทุกงวด")
records_df = pd.DataFrame([{
    "งวด": r.draw_date, "เลขที่ซื้อ": ", ".join(r.numbers_bet), "ผลจริง": r.actual,
    "ชนะ": "✅" if r.won else "❌", "เงินเดิมพัน (฿)": f"{r.bet_per_number*r.tickets_per_number*len(r.numbers_bet):.0f}",
    "รายได้ (฿)": f"{r.gross_payout:.0f}", "กำไร/ขาดทุน (฿)": f"{r.pnl:+.0f}",
    "ทุนสะสม (฿)": f"{r.equity:,.0f}",
} for r in records])

st.dataframe(records_df, width="stretch", hide_index=True,
             column_config={"ชนะ": st.column_config.TextColumn(width="small")})

# Financial summary
st.markdown("---")
col_a, col_b = st.columns(2)
with col_a:
    st.metric("เงินที่ใช้ทั้งหมด (฿)", f"{result.total_spent:,.0f}")
with col_b:
    st.metric("เงินที่ได้รับคืนทั้งหมด (฿)", f"{result.total_payout:,.0f}")
roi = (result.total_payout / result.total_spent - 1) * 100 if result.total_spent > 0 else 0
st.metric("ROI", f"{roi:.1f}%", delta=f"{roi:.1f}%")
