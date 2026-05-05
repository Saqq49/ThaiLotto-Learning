import streamlit as st
import pandas as pd
import random
import time
from lotto.theme import inject_css, init_persona, render_explanation, mode_text, is_math_mode, GOLD, GOLD_BRUSHED
from lotto.data_loader import load_data
from lotto.predictors import frequency_predictor, overdue_predictor, recency_weighted_predictor

st.set_page_config(page_title="คิดไม่ออก เดี๋ยวเลือกให้", page_icon="🎲", layout="wide")
inject_css()
init_persona()

df = st.session_state["df"] if "df" in st.session_state else load_data()

st.title(mode_text("🎲 คิดไม่ออก เดี๋ยวเลือกให้", "🎲 Selection Engine"))
st.markdown(mode_text(
    "เลือกเลขแบบเล่นสนุก จะเอาสายสถิติหรือสายดวงก็ได้ แต่ผลสลากยังเป็นเรื่องสุ่มเหมือนเดิม",
    "Generate candidates with identical internal computation while exposing the selection rationale and score composition.",
))

MODE_STAT = "สายสถิติ"
MODE_RAND = "สายดวง"
MODE_DISPLAY = {
    MODE_STAT: mode_text("สายสถิติ", "Statistical"),
    MODE_RAND: mode_text("สายดวง", "Random"),
}

ALGORITHMS = ["Frequency", "Overdue", "Recency-Weighted", "Ensemble"]
ALGO_DISPLAY_TH = {
    "Frequency":        "ออกบ่อย (ความถี่)",
    "Overdue":          "อั้นมานาน (ทิ้งช่วง)",
    "Recency-Weighted": "มาล่าสุด (น้ำหนักใหม่)",
    "Ensemble":         "รวมทุกสูตร (Ensemble)",
}

TOP_POOL = 20  # sample candidates from this rank pool

with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        mode = st.radio(
            mode_text("สไตล์การเลือก", "Selection Mode"),
            [MODE_STAT, MODE_RAND],
            format_func=lambda v: MODE_DISPLAY[v],
            horizontal=True,
        )
    with col2:
        num_count = st.slider(mode_text("จำนวนเลขที่ต้องการ", "Candidate Count"), 1, 5, 3)
    with col3:
        algorithm = st.selectbox(
            mode_text("อัลกอริทึม", "Algorithm"),
            ALGORITHMS,
            format_func=lambda x: x if is_math_mode() else ALGO_DISPLAY_TH[x],
            disabled=mode != MODE_STAT,
            help=mode_text(
                f"เลือกสูตรที่ใช้จัดอันดับ แล้วระบบจะสุ่มเลข {num_count} ตัวจาก Top {TOP_POOL}",
                f"Algorithm used to rank all 100 nodes. {num_count} candidates are sampled randomly from the top {TOP_POOL}.",
            ),
        )

if st.button(mode_text("✨ เริ่มเลือกเลข", "▶ Run Selection"), type="primary", use_container_width=True):
    with st.spinner(mode_text("กำลังจัดอันดับเลข...", "Computing candidate ranks...")):
        time.sleep(1.5)

        if mode == MODE_STAT:
            f_list = frequency_predictor(df, top_n=100)
            o_list = overdue_predictor(df, top_n=100)
            r_list = recency_weighted_predictor(df, top_n=100)
            f_scores = dict(f_list)
            o_scores = dict(o_list)
            r_scores = dict(r_list)

            if algorithm == "Frequency":
                ranked = f_list
                algo_label = mode_text("ความถี่", "Frequency")
            elif algorithm == "Overdue":
                ranked = o_list
                algo_label = mode_text("ทิ้งช่วง", "Gap/Overdue")
            elif algorithm == "Recency-Weighted":
                ranked = r_list
                algo_label = mode_text("น้ำหนักล่าสุด", "Recency Weight")
            else:  # Ensemble
                ensemble = {
                    f"{i:02d}": (f_scores.get(f"{i:02d}", 0) + o_scores.get(f"{i:02d}", 0) + r_scores.get(f"{i:02d}", 0)) / 3
                    for i in range(100)
                }
                ranked = sorted(ensemble.items(), key=lambda x: x[1], reverse=True)
                algo_label = mode_text("Ensemble (รวมทุกสูตร)", "Ensemble (avg of all 3)")

            top_pool = ranked[:TOP_POOL]
            selected_pairs = random.sample(top_pool, k=min(num_count, len(top_pool)))
            nums = [p[0] for p in selected_pairs]

            # Build per-number rank info across all algorithms
            f_rank = {num: r + 1 for r, (num, _) in enumerate(f_list)}
            o_rank = {num: r + 1 for r, (num, _) in enumerate(o_list)}
            r_rank = {num: r + 1 for r, (num, _) in enumerate(r_list)}
            pool_rank = {num: r + 1 for r, (num, _) in enumerate(ranked)}

            reason_rows = []
            for i, num in enumerate(nums):
                if is_math_mode():
                    rationale = (
                        f"Pool rank {pool_rank[num]}/{TOP_POOL} by {algo_label} — "
                        f"Freq #{f_rank[num]}, Gap #{o_rank[num]}, Recency #{r_rank[num]}"
                    )
                else:
                    rationale = (
                        f"อันดับ {pool_rank[num]} จาก {TOP_POOL} อันดับแรก (สูตร{algo_label}) — "
                        f"ความถี่#{f_rank[num]} ทิ้งช่วง#{o_rank[num]} ล่าสุด#{r_rank[num]}"
                    )
                reason_rows.append({
                    mode_text("เลข", "Node"): num,
                    mode_text("อันดับใน Pool", "Pool Rank"): pool_rank[num],
                    mode_text("สูตรที่ใช้", "Algorithm"): algo_label,
                    mode_text("เหตุผล", "Rationale"): rationale,
                })

            layman = f"ระบบจัดอันดับเลขทั้ง 100 ตัวด้วยสูตร '{ALGO_DISPLAY_TH[algorithm]}' แล้วสุ่มเลือก {num_count} ตัวจาก {TOP_POOL} อันดับแรก ผลที่ได้จึงมีเหตุผลรองรับแต่ไม่ซ้ำเดิมทุกครั้ง"
            math = f"Algorithm: {algorithm}. All 100 nodes are scored and ranked. {num_count} candidates are sampled uniformly at random (without replacement) from the top-{TOP_POOL} pool. This prevents repeated identical outputs while keeping candidates statistically grounded."

        else:
            nums = random.sample([f"{i:02d}" for i in range(100)], k=num_count)
            reason_rows = [
                {
                    mode_text("เลข", "Node"): num,
                    mode_text("อันดับใน Pool", "Pool Rank"): "—",
                    mode_text("สูตรที่ใช้", "Algorithm"): mode_text("สุ่ม", "Random"),
                    mode_text("เหตุผล", "Rationale"): mode_text(
                        "สุ่มแบบเท่าเทียมจากเลข 00–99",
                        "Uniform random sample from 00–99",
                    ),
                }
                for i, num in enumerate(nums)
            ]
            layman = "ระบบสุ่มเลขแบบไม่เลือกหน้า เพราะในโลกของความน่าจะเป็น ทุกเลขมีโอกาสเกิดเท่ากันในทุกๆ งวด"
            math = "Uniform sampling without replacement from the 00–99 sample space. Every node has equal selection probability within the random draw, and duplicates are prevented within one generated set."

    st.markdown("""
<style>
@keyframes coinFall {
    0%   { transform: translateY(-120px) rotateY(0deg) scale(1);   opacity: 1; }
    80%  { opacity: 1; }
    100% { transform: translateY(110vh)  rotateY(720deg) scale(0.6); opacity: 0; }
}
.coin-rain-container {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none; z-index: 9999; overflow: hidden;
}
.coin {
    position: absolute; top: -80px;
    font-size: 2rem; line-height: 1;
    animation: coinFall linear forwards;
    filter: drop-shadow(0 4px 8px rgba(212,175,55,0.6));
}
</style>
<div class="coin-rain-container" id="coinRain"></div>
<script>
(function() {
    var container = document.getElementById('coinRain');
    var coins = ['🪙','💰','🥇'];
    var count = 55;
    for (var i = 0; i < count; i++) {
        var el = document.createElement('span');
        el.className = 'coin';
        el.textContent = coins[i % coins.length];
        el.style.left = (Math.random() * 100) + '%';
        el.style.animationDuration = (1.6 + Math.random() * 2.2) + 's';
        el.style.animationDelay = (Math.random() * 2.5) + 's';
        el.style.fontSize = (1.4 + Math.random() * 1.4) + 'rem';
        container.appendChild(el);
    }
    setTimeout(function() {
        if (container && container.parentNode) container.parentNode.removeChild(container);
    }, 6000);
})();
</script>
""", unsafe_allow_html=True)

    st.subheader(mode_text("🎯 เลขที่คัดมาให้", "🎯 Selected Candidates"))

    cols = st.columns(num_count)
    for i, num in enumerate(nums):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-container" style="padding: 40px 10px; border-radius: 10px;">
                <div style="font-family: 'Playfair Display', serif; font-size: 4.5rem; font-weight: 700;
                            background: {GOLD_BRUSHED}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    {num}
                </div>
                <div style="color: #8A817C; font-size: 0.8rem; letter-spacing: 0.1em; margin-top: 15px;">
                    {mode_text("เลขที่", "Candidate")} {i+1}
                </div>
                <div style="margin-top: 14px; color: #F0E8D5; opacity: 0.78; font-size: 0.82rem; line-height: 1.55;">
                    {reason_rows[i][mode_text("เหตุผล", "Rationale")]}
                </div>
            </div>
            """, unsafe_allow_html=True)

    if mode == MODE_STAT:
        st.markdown(mode_text("#### เหตุผลประกอบรายเลข", "#### Per-Candidate Rationale"))
        st.dataframe(pd.DataFrame(reason_rows), width="stretch", hide_index=True)

    st.markdown("---")
    render_explanation(layman, math)
else:
    st.info(mode_text("เลือกสไตล์ที่ชอบแล้วกดปุ่มเพื่อเริ่ม", "Choose a selection mode and click Run Selection."))

st.markdown(f"""
<div style="text-align:center; margin-top: 50px; opacity: 0.5; font-size: 0.8rem;">
    {mode_text(
        "*โปรดใช้วิจารณญาณ ข้อมูลนี้เป็นเพียงการนำสถิติมาเรียบเรียงใหม่ ไม่ได้รับรองผลการถูกรางวัล",
        "*For educational use only. Statistical ranking does not imply predictive power or guaranteed outcomes.",
    )}
</div>
""", unsafe_allow_html=True)
