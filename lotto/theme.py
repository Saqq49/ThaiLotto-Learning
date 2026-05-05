import plotly.graph_objects as go
import streamlit as st

# --- Premium Luxury Palette ---
GOLD_BRUSHED = "linear-gradient(135deg, #D4AF37 0%, #F1E5AC 50%, #A8892A 100%)"
GOLD_SOLID   = "#D4AF37"
DEEP_BLACK   = "#050505"
MIDNIGHT     = "#0A0D15"
SURFACE_CARD = "rgba(20, 28, 46, 0.6)"
TEXT_CHAMPAGNE = "#F0E8D5"
TEXT_MUTED    = "#8A817C"
CRIMSON_ACCENT = "#9B111E" # Ruby Red

# For backwards compatibility
CRIMSON = CRIMSON_ACCENT
GOLD = GOLD_SOLID
GOLD_DARK = "#A8892A"
PANEL = SURFACE_CARD
PANEL_DARK = MIDNIGHT      # opaque dark hex for Plotly colorscales
TEXT = TEXT_CHAMPAGNE
TEXT_DARK = TEXT_CHAMPAGNE
TEXT_DIM = TEXT_MUTED
PANEL_WHITE = SURFACE_CARD
PANEL_ALT = "#111926"
GOLD_DIM = "#7A7060"
CHAMPAGNE = TEXT_CHAMPAGNE
BG_DARK = DEEP_BLACK

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(5,5,5,0.4)",
    font=dict(color=TEXT_CHAMPAGNE, family="'Playfair Display', 'Sarabun', serif", size=13),
    colorway=[GOLD_SOLID, CRIMSON_ACCENT, "#E8A838", "#4488CC", "#6A4C93"],
    margin=dict(l=40, r=40, t=50, b=40),
    hoverlabel=dict(bgcolor="#141C2E", font_color="#F0E8D5", bordercolor=GOLD_SOLID),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)"),
)

CUSTOM_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Prompt:wght@200;300;400;600&family=Sarabun:wght@300;400;600&display=swap');

    /* ── Base ── */
    html, body, .stApp {{
        background: radial-gradient(circle at top right, #10141D 0%, {DEEP_BLACK} 100%) !important;
        color: {TEXT_CHAMPAGNE} !important;
        font-family: 'Prompt', sans-serif !important;
    }}

    /* ── Headings ── */
    h1, h2, h3, h4 {{
        font-family: 'Playfair Display', serif !important;
        letter-spacing: -0.01em;
        font-weight: 700;
    }}
    h1 {{
        background: {GOLD_BRUSHED};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem !important;
        padding-bottom: 1rem;
        text-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }}
    h2 {{ color: {GOLD_SOLID} !important; border-bottom: 1px solid rgba(212, 175, 55, 0.2); padding-bottom: 0.5rem; }}
    h3 {{ color: {TEXT_CHAMPAGNE} !important; font-weight: 400; font-style: italic; opacity: 0.9; }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background: {DEEP_BLACK} !important;
        border-right: 1px solid rgba(212, 175, 55, 0.15);
        box-shadow: 10px 0 30px rgba(0,0,0,0.5);
    }}
    [data-testid="stSidebarNav"] a {{
        font-family: 'Prompt', sans-serif;
        font-size: 1.05rem;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }}
    [data-testid="stSidebarNav"] a:hover {{
        background: rgba(212, 175, 55, 0.1) !important;
        border-left: 3px solid {GOLD_SOLID};
    }}

    /* ── Luxury Metric Cards ── */
    .metric-container {{
        background: {SURFACE_CARD};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(212, 175, 55, 0.15);
        border-radius: 4px; /* Sharper, more modern luxury */
        padding: 24px 20px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.4), inset 0 1px 1px rgba(255,255,255,0.05);
        transition: transform 0.4s cubic-bezier(0.165, 0.84, 0.44, 1), box-shadow 0.4s ease;
    }}
    .metric-container:hover {{
        transform: translateY(-8px);
        border-color: rgba(212, 175, 55, 0.5);
        box-shadow: 0 20px 50px rgba(0,0,0,0.6), 0 0 15px rgba(212, 175, 55, 0.1);
    }}
    .metric-label {{
        color: {TEXT_MUTED};
        font-family: 'Prompt', sans-serif;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }}
    .metric-value {{
        font-family: 'Playfair Display', serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: {GOLD_SOLID};
        background: {GOLD_BRUSHED};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    /* ── Glass Components ── */
    .stTabs [data-baseweb="tab-list"] {{
        background: transparent;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: 'Prompt', sans-serif;
        color: {TEXT_MUTED} !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: {GOLD_SOLID} !important;
        border-bottom-color: {GOLD_SOLID} !important;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background: transparent !important;
        color: {GOLD_SOLID} !important;
        border: 1px solid {GOLD_SOLID} !important;
        border-radius: 2px !important;
        font-family: 'Prompt', sans-serif !important;
        font-weight: 400 !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        transition: all 0.3s ease !important;
        padding: 0.6rem 2rem !important;
    }}
    .stButton > button:hover {{
        background: {GOLD_SOLID} !important;
        color: {DEEP_BLACK} !important;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.3) !important;
    }}

    /* ── Dataframe & Inputs ── */
    [data-testid="stDataFrame"] {{
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.05);
    }}
    [data-testid="stTextInput"] input, [data-testid="stSelectbox"] > div > div {{
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 2px !important;
    }}

    /* ── Technical Info Block ── */
    .tech-block {{
        border-left: 2px solid {GOLD_SOLID};
        background: linear-gradient(90deg, rgba(212, 175, 55, 0.05) 0%, transparent 100%);
        padding: 15px 25px;
        margin: 20px 0;
    }}
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

def init_persona() -> str:
    if "persona" not in st.session_state:
        st.session_state.persona = "ภาษาชาวบ้าน"
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("<h3 style='text-align:center; font-style:normal; font-size:1rem; letter-spacing:0.1em; color:#8A817C;'>MODE SELECTOR</h3>", unsafe_allow_html=True)
        st.session_state.persona = st.radio(
            "Content Depth:",
            ["ภาษาชาวบ้าน", "วิชาการ / คณิตศาสตร์"],
            index=0 if st.session_state.persona == "ภาษาชาวบ้าน" else 1,
            label_visibility="collapsed"
        )
        st.markdown("---")
    return st.session_state.persona

def render_explanation(layman: str, math: str, formula: str = None) -> None:
    persona = st.session_state.get("persona", "ภาษาชาวบ้าน")
    if persona == "วิชาการ / คณิตศาสตร์":
        st.markdown(f"""
        <div class="tech-block">
            <b style="color:{GOLD_SOLID}; font-family:'Playfair Display', serif; letter-spacing:0.05em;">TECHNICAL SPECIFICATION</b><br>
            <i style="color:{TEXT_CHAMPAGNE}; font-size: 0.95rem; line-height:1.6;">{math}</i>
        </div>
        """, unsafe_allow_html=True)
        if formula:
            st.latex(formula)
    else:
        st.markdown(f"<div style='padding:10px 0; border-top:1px solid rgba(255,255,255,0.05); border-bottom:1px solid rgba(255,255,255,0.05); font-style:italic; color:{TEXT_CHAMPAGNE}; opacity:0.8;'>“ {layman} ”</div>", unsafe_allow_html=True)

def gold_line_style() -> dict:
    return dict(color=GOLD_SOLID, width=1.5)

def crimson_bar_style() -> dict:
    return dict(color=CRIMSON_ACCENT)
