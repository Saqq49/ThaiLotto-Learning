import plotly.graph_objects as go
import streamlit as st

# Dark Luxury Palette
CRIMSON   = "#C8102E"   # royal red
GOLD      = "#D4AF37"   # metallic gold
GOLD_DARK = "#A8892A"   # deep gold
CHAMPAGNE = "#F0E8D5"   # warm off-white text
BG_DARK   = "#07090D"   # near-black
PANEL     = "#0F1420"   # card background
PANEL_ALT = "#141C2E"   # slightly lighter panel
BORDER    = "#D4AF3728" # gold border (subtle)
TEXT      = "#F0E8D5"   # warm off-white
TEXT_DIM  = "#7A7060"   # muted label text

# Aliases for backwards compatibility with existing pages
TEXT_DARK   = TEXT
PANEL_WHITE = PANEL
GOLD_DIM    = GOLD_DARK

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(7,9,13,0.6)",
    font=dict(color=TEXT, family="'Cinzel', 'Sarabun', sans-serif", size=13),
    colorway=[CRIMSON, GOLD, "#E8A838", "#FF6B6B", "#4488CC"],
    margin=dict(l=40, r=40, t=50, b=40),
    hoverlabel=dict(bgcolor=PANEL_ALT, font_color=CHAMPAGNE, bordercolor=GOLD),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.03)",
        linecolor="rgba(255,255,255,0.07)",
        zerolinecolor="rgba(255,255,255,0.07)",
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.03)",
        linecolor="rgba(255,255,255,0.07)",
        zerolinecolor="rgba(255,255,255,0.07)",
    ),
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Sarabun:wght@300;400;600&display=swap');

    /* ── Base ── */
    html, body, .stApp {
        background-color: #07090D !important;
        color: #F0E8D5 !important;
        font-family: 'Sarabun', sans-serif !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; background: #0F1420; }
    ::-webkit-scrollbar-thumb { background: #D4AF3744; border-radius: 3px; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A0D15 0%, #07090D 100%) !important;
        border-right: 1px solid #D4AF3720;
    }
    [data-testid="stSidebar"] * { color: #F0E8D5 !important; }
    [data-testid="stSidebarNav"] a:hover { background: #D4AF3712 !important; }

    /* ── Headings ── */
    h1, h2, h3 {
        font-family: 'Cinzel', serif !important;
        letter-spacing: 0.04em;
    }
    h1 {
        background: linear-gradient(135deg, #D4AF37 0%, #F0E8D5 55%, #A8892A 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    h2 { color: #D4AF37 !important; }
    h3 { color: #C5A04A !important; font-size: 1.1rem !important; }

    /* ── Gold divider ── */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #D4AF3766 50%, transparent 100%);
        margin: 1.5rem 0;
    }

    /* ── Custom metric cards ── */
    .metric-container {
        background: linear-gradient(145deg, #0F1420 0%, #141C2E 100%);
        border: 1px solid #D4AF3728;
        border-top: 2px solid #D4AF37;
        border-radius: 12px;
        padding: 22px 16px;
        text-align: center;
        box-shadow: 0 4px 32px rgba(0,0,0,0.5), inset 0 1px 0 #D4AF3718;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        margin-bottom: 16px;
    }
    .metric-container:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 40px rgba(212,175,55,0.18), inset 0 1px 0 #D4AF3728;
    }
    .metric-label {
        color: #7A7060;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .metric-value {
        background: linear-gradient(135deg, #D4AF37 0%, #F0E8D5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-family: 'Cinzel', serif;
        font-size: 2rem;
        font-weight: 700;
        line-height: 1.2;
    }

    /* ── Native st.metric ── */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #0F1420 0%, #141C2E 100%);
        border: 1px solid #D4AF3728;
        border-top: 2px solid #D4AF37;
        border-radius: 12px;
        padding: 16px 14px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    }
    [data-testid="stMetricLabel"] p {
        color: #7A7060 !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    [data-testid="stMetricValue"] {
        color: #D4AF37 !important;
        font-family: 'Cinzel', serif !important;
    }
    [data-testid="stMetricDelta"] { opacity: 0.8; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: transparent;
        border-bottom: 1px solid #D4AF3728;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #7A7060 !important;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-family: 'Sarabun', sans-serif;
    }
    .stTabs [aria-selected="true"] {
        background: #D4AF3710 !important;
        color: #D4AF37 !important;
        border-bottom: 2px solid #D4AF37 !important;
    }

    /* ── Tags ── */
    .hot-tag {
        display: inline-block;
        background: #C8102E15;
        border-left: 3px solid #C8102E;
        color: #FF6B7A;
        padding: 6px 14px;
        margin: 4px 0;
        border-radius: 0 6px 6px 0;
        font-weight: 600;
        width: 100%;
        font-size: 0.95rem;
    }
    .cold-tag {
        display: inline-block;
        background: #0D1E30;
        border-left: 3px solid #4488CC;
        color: #88BBDD;
        padding: 6px 14px;
        margin: 4px 0;
        border-radius: 0 6px 6px 0;
        font-weight: 600;
        width: 100%;
        font-size: 0.95rem;
    }

    /* ── Disclaimer ── */
    .disclaimer {
        background: linear-gradient(135deg, #C8102E10 0%, transparent 100%);
        border: 1px solid #C8102E33;
        border-left: 3px solid #C8102E;
        padding: 14px 18px;
        border-radius: 8px;
        color: #7A7060;
        font-size: 0.85rem;
        margin: 16px 0;
        line-height: 1.6;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #C8102E 0%, #8B0015 100%) !important;
        color: #F0E8D5 !important;
        border: 1px solid #C8102E60 !important;
        border-radius: 8px !important;
        font-family: 'Sarabun', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em !important;
        transition: all 0.2s ease !important;
        padding: 0.5rem 1.5rem !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #E01030 0%, #C8102E 100%) !important;
        box-shadow: 0 4px 24px #C8102E44 !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #D4AF37 0%, #A8892A 100%) !important;
        color: #07090D !important;
        border: none !important;
        font-weight: 700 !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 4px 24px #D4AF3744 !important;
    }

    /* ── Inputs ── */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input {
        background: #0F1420 !important;
        color: #F0E8D5 !important;
        border: 1px solid #D4AF3730 !important;
        border-radius: 8px !important;
    }
    [data-testid="stSelectbox"] > div > div {
        background: #0F1420 !important;
        color: #F0E8D5 !important;
        border: 1px solid #D4AF3730 !important;
        border-radius: 8px !important;
    }

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] {
        border: 1px solid #D4AF3722;
        border-radius: 10px;
        overflow: visible;
    }

    /* ── Info / Warning / Error boxes ── */
    [data-testid="stAlert"] {
        background: #0F1420;
        border-radius: 8px;
    }

    /* ── Mobile ── */
    @media (max-width: 768px) {
        h1 { font-size: 1.5rem !important; }
        .metric-value { font-size: 1.5rem !important; }
        [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; overflow: visible !important; }
        [data-testid="stHorizontalBlock"] > div {
            min-width: min(100%, 18rem) !important;
            flex: 1 1 min(100%, 18rem) !important;
        }
    }
</style>
"""


def inject_css() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_metric(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_layout(fig: go.Figure, **overrides) -> go.Figure:
    layout = {**PLOTLY_LAYOUT, **overrides}
    fig.update_layout(**layout)
    return fig


def gold_line_style() -> dict:
    return dict(color=GOLD, width=2)


def crimson_bar_style() -> dict:
    return dict(color=CRIMSON)


def init_persona() -> str:
    if "persona" not in st.session_state:
        st.session_state.persona = "ภาษาชาวบ้าน"
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🎭 เลือกโหมดการอธิบาย")
        st.session_state.persona = st.radio(
            "ระดับเนื้อหา:",
            ["ภาษาชาวบ้าน", "วิชาการ / คณิตศาสตร์"],
            index=0 if st.session_state.persona == "ภาษาชาวบ้าน" else 1,
            help="ภาษาชาวบ้าน: เน้นเข้าใจง่าย คุยแบบคอหวย | วิชาการ: เน้นนิยาม ทฤษฎี และสมการ"
        )
        st.markdown("---")
    return st.session_state.persona


def render_explanation(layman: str, math: str, formula: str = None) -> None:
    persona = st.session_state.get("persona", "ภาษาชาวบ้าน")
    if persona == "วิชาการ / คณิตศาสตร์":
        with st.container():
            st.markdown(f"""
            <div style="border-left: 3px solid {GOLD}; padding-left: 15px; margin: 10px 0;">
                <b style="color:{GOLD};">🔬 คำอธิบายเชิงวิชาการ (Technical Definition):</b><br>
                <i style="color:{TEXT_DIM}; font-size: 0.9rem;">{math}</i>
            </div>
            """, unsafe_allow_html=True)
            if formula:
                st.latex(formula)
    else:
        st.markdown(f"**💡 อธิบายแบบเข้าใจง่าย:** {layman}")
