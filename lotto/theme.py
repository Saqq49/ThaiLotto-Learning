import base64
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

def _sidebar_credit_html() -> str:
    img_path = Path(__file__).parent.parent / "Blackcat.jpg"
    if not img_path.exists():
        return ""
    b64 = base64.b64encode(img_path.read_bytes()).decode()
    return f"""
    <style>
    .sidebar-credit {{
        position: fixed;
        bottom: 14px;
        left: 0;
        width: 260px;
        padding: 0 16px;
        display: flex;
        align-items: center;
        gap: 10px;
        z-index: 999;
    }}
    .sidebar-credit img {{
        width: 38px;
        height: 38px;
        border-radius: 50%;
        object-fit: cover;
        border: 1.5px solid rgba(201,168,76,0.5);
        flex-shrink: 0;
    }}
    .sidebar-credit-text {{
        font-family: 'Prompt', sans-serif;
        font-size: 0.72rem;
        color: #A08C78;
        line-height: 1.4;
    }}
    .sidebar-credit-text b {{
        color: #C9A84C;
        font-size: 0.78rem;
    }}
    </style>
    <div class="sidebar-credit">
        <img src="data:image/jpeg;base64,{b64}" alt="Blackcat" />
        <div class="sidebar-credit-text">
            Design &amp; Dev<br/><b>By Blackcat</b>
        </div>
    </div>
    """

# --- Refined Imperial Palette ---
GOLD_GRADIENT = "linear-gradient(135deg, #BF953F 0%, #F0DC82 45%, #B38728 75%, #F0DC82 100%)"
GOLD_SOLID    = "#C9A84C"          # warm amber-gold, easier on the eyes than pure D4AF37
GOLD_LIGHT    = "#EDE0C4"          # champagne — primary readable text
CRIMSON_RICH  = "#7A1818"          # deep muted crimson for accents
CRIMSON_GLOW  = "#9B2020"          # slightly brighter for hover/active
INK           = "#0D0B0B"          # near-black base
SURFACE       = "rgba(22,10,10,0.85)"   # card/panel surface
SURFACE_LIGHT = "rgba(40,18,18,0.7)"    # slightly lighter surface
TEXT_PRIMARY  = "#EDE0C4"          # warm off-white — easy to read
TEXT_SECONDARY= "#A08C78"          # muted warm taupe
BORDER_GOLD   = "rgba(201,168,76,0.28)" # subtle gold border

GOLD_METALLIC = GOLD_GRADIENT      # alias kept for backward compat
GOLD_BRUSHED  = GOLD_GRADIENT
ROYAL_CRIMSON = CRIMSON_RICH
DEEP_RED      = CRIMSON_RICH
RICH_BLACK    = INK
TEXT_GOLD     = TEXT_PRIMARY
TEXT_MUTED    = TEXT_SECONDARY

# For backwards compatibility
CRIMSON   = CRIMSON_RICH
GOLD      = GOLD_SOLID
GOLD_DARK = "#9A7B2E"
PANEL     = SURFACE
PANEL_DARK= INK
TEXT      = TEXT_PRIMARY
TEXT_DARK = TEXT_PRIMARY
TEXT_DIM  = TEXT_SECONDARY
PANEL_WHITE = SURFACE_LIGHT
BG_DARK   = INK

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,11,11,0.6)",
    font=dict(color=TEXT_PRIMARY, family="'Sarabun', 'Playfair Display', serif", size=13),
    colorway=[GOLD_SOLID, "#C0392B", "#E8A838", "#5D8AA8", "#6A4C93"],
    margin=dict(l=40, r=40, t=50, b=40),
    hoverlabel=dict(bgcolor="#1A0800", font_color=TEXT_PRIMARY, bordercolor=GOLD_SOLID),
    xaxis=dict(gridcolor="rgba(201,168,76,0.08)", zerolinecolor="rgba(201,168,76,0.15)"),
    yaxis=dict(gridcolor="rgba(201,168,76,0.08)", zerolinecolor="rgba(201,168,76,0.15)"),
    dragmode=False,
)

PLOTLY_CONFIG = {
    "scrollZoom": False,
    "displayModeBar": False,
    "doubleClick": False,
}

CUSTOM_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Sarabun:wght@300;400;600&family=Prompt:wght@300;400;600&display=swap');

    /* ═══════════════════════════════════════
       BASE
    ═══════════════════════════════════════ */
    html, body, .stApp {{
        background:
            radial-gradient(ellipse at 20% 0%,   rgba(100,20,20,0.45) 0%, transparent 55%),
            radial-gradient(ellipse at 80% 100%,  rgba(80,10,10,0.3)  0%, transparent 50%),
            {INK} !important;
        color: {TEXT_PRIMARY} !important;
        font-family: 'Sarabun', 'Prompt', sans-serif !important;
        font-size: 1rem !important;
        line-height: 1.7 !important;
    }}

    /* ═══════════════════════════════════════
       TYPOGRAPHY
    ═══════════════════════════════════════ */
    h1, h2, h3, h4 {{
        font-family: 'Playfair Display', serif !important;
        letter-spacing: 0.01em;
    }}
    h1 {{
        background: {GOLD_GRADIENT};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: clamp(1.9rem, 5vw, 3rem) !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
        padding-bottom: 0.4rem;
    }}
    h2 {{
        color: {GOLD_SOLID} !important;
        font-size: clamp(1.2rem, 3vw, 1.6rem) !important;
        border-bottom: 1px solid rgba(201,168,76,0.25);
        padding-bottom: 0.4rem;
        margin-top: 1.6rem !important;
    }}
    h3 {{
        color: {TEXT_PRIMARY} !important;
        font-size: clamp(1rem, 2.5vw, 1.2rem) !important;
        font-weight: 600 !important;
        opacity: 0.9;
    }}
    p, li, .stMarkdown {{
        line-height: 1.75 !important;
        color: {TEXT_PRIMARY} !important;
    }}

    /* ── Equal-height, equal-width columns for metric cards ── */
    [data-testid="stColumns"] {{
        align-items: stretch !important;
    }}
    [data-testid="stColumns"] > [data-testid="stColumn"] {{
        display: flex !important;
        flex-direction: column !important;
        min-width: 0 !important;
        overflow: hidden !important;
    }}
    [data-testid="stColumns"] > [data-testid="stColumn"] > div {{
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
        min-width: 0 !important;
    }}
    [data-testid="stColumns"] > [data-testid="stColumn"] > div > div {{
        flex: 1 !important;
        min-width: 0 !important;
    }}

    /* ═══════════════════════════════════════
       SIDEBAR
    ═══════════════════════════════════════ */
    [data-testid="stSidebar"] {{
        background:
            linear-gradient(180deg,
                rgba(80,15,15,0.9)  0%,
                rgba(20,6,6,0.98)  35%,
                {INK}              100%
            ) !important;
        border-right: 1px solid rgba(201,168,76,0.2) !important;
        box-shadow: 4px 0 24px rgba(0,0,0,0.6) !important;
    }}
    [data-testid="stSidebarNav"] a {{
        font-family: 'Sarabun', sans-serif !important;
        font-size: 0.97rem !important;
        color: {TEXT_SECONDARY} !important;
        padding: 10px 20px !important;
        border-radius: 6px !important;
        margin: 1px 8px !important;
        transition: background 0.25s ease, color 0.25s ease, padding-left 0.25s ease !important;
    }}
    [data-testid="stSidebarNav"] a:hover {{
        background: rgba(201,168,76,0.1) !important;
        color: {GOLD_SOLID} !important;
        padding-left: 26px !important;
    }}
    [data-testid="stSidebarNav"] a[aria-current="page"] {{
        background: rgba(122,24,24,0.35) !important;
        color: {GOLD_LIGHT} !important;
        border-left: 2px solid {GOLD_SOLID} !important;
    }}

    /* ── Thai Lotto brand (first nav item) ── */
    [data-testid="stSidebarNav"] li:first-child a {{
        font-family: 'Playfair Display', serif !important;
        font-size: 1.45rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em !important;
        background: {GOLD_GRADIENT} !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        padding: 18px 20px 14px !important;
        margin: 0 !important;
        border-radius: 0 !important;
        border-bottom: 1px solid rgba(201,168,76,0.2) !important;
        display: block !important;
    }}
    [data-testid="stSidebarNav"] li:first-child a:hover {{
        background: {GOLD_GRADIENT} !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        padding-left: 20px !important;
        filter: brightness(1.12) !important;
    }}

    /* ═══════════════════════════════════════
       SIDEBAR MODE SELECTOR
    ═══════════════════════════════════════ */
    .sidebar-mode-wrap {{
        margin: 12px 10px 14px;
        padding: 12px 14px;
        background: rgba(201,168,76,0.05);
        border: 1px solid rgba(201,168,76,0.2);
        border-radius: 10px;
    }}
    .sidebar-mode-title {{
        font-family: 'Prompt', sans-serif;
        font-size: 0.58rem;
        font-weight: 600;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: {GOLD_SOLID};
        margin-bottom: 3px;
        opacity: 0.75;
    }}
    .sidebar-mode-desc {{
        font-family: 'Sarabun', sans-serif;
        font-size: 0.72rem;
        color: {TEXT_SECONDARY};
        margin-bottom: 10px;
        line-height: 1.45;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] > label {{
        display: none !important;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {{
        background: rgba(0,0,0,0.4) !important;
        border: 1px solid rgba(201,168,76,0.3) !important;
        border-radius: 50px !important;
        padding: 3px !important;
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 2px !important;
        width: 100% !important;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {{
        border-radius: 50px !important;
        padding: 0.28rem 0.5rem !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        text-align: center !important;
        justify-content: center !important;
        color: {TEXT_SECONDARY} !important;
        transition: all 0.25s ease !important;
        margin: 0 !important;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {{
        background: {GOLD_GRADIENT} !important;
        color: {INK} !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(201,168,76,0.35) !important;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover {{
        color: {GOLD_SOLID} !important;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] svg {{
        display: none !important;
    }}

    /* ═══════════════════════════════════════
       METRIC CARDS
    ═══════════════════════════════════════ */
    .metric-container {{
        background: {SURFACE} !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid {BORDER_GOLD};
        border-top: 2px solid rgba(201,168,76,0.5);
        border-radius: 10px;
        padding: 24px 16px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.45);
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 130px;
        width: 100%;
        height: 100%;
        box-sizing: border-box;
        overflow: hidden;
    }}
    .metric-container:hover {{
        border-color: rgba(201,168,76,0.55);
        box-shadow: 0 12px 40px rgba(0,0,0,0.55), 0 0 20px rgba(201,168,76,0.08);
    }}
    .metric-label {{
        font-family: 'Prompt', sans-serif;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: {GOLD_SOLID};
        opacity: 0.75;
        margin-bottom: 10px;
    }}
    .metric-value {{
        font-family: 'Playfair Display', serif;
        font-size: clamp(1.8rem, 4vw, 2.6rem);
        font-weight: 700;
        background: {GOLD_GRADIENT};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
        max-width: 100%;
        word-break: break-word;
        overflow-wrap: break-word;
    }}

    /* ═══════════════════════════════════════
       BUTTONS
    ═══════════════════════════════════════ */
    .stButton > button {{
        background: rgba(122,24,24,0.7) !important;
        color: {GOLD_LIGHT} !important;
        border: 1px solid rgba(201,168,76,0.5) !important;
        border-radius: 8px !important;
        font-family: 'Prompt', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.05em !important;
        padding: 0.5rem 1.4rem !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35) !important;
        transition: background 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease !important;
    }}
    .stButton > button:hover {{
        background: rgba(155,32,32,0.85) !important;
        border-color: {GOLD_SOLID} !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.45), 0 0 12px rgba(201,168,76,0.15) !important;
    }}
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #7A1818, #9B2020) !important;
        border-color: rgba(201,168,76,0.6) !important;
    }}

    /* ═══════════════════════════════════════
       INPUTS, SELECTS, SLIDERS
    ═══════════════════════════════════════ */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] > div > div {{
        background: rgba(20,8,8,0.7) !important;
        border: 1px solid rgba(201,168,76,0.25) !important;
        border-radius: 6px !important;
        color: {TEXT_PRIMARY} !important;
    }}
    [data-testid="stSlider"] [data-testid="stSliderTrack"] {{
        background: rgba(201,168,76,0.2) !important;
    }}
    [data-baseweb="slider"] [data-testid="stSliderThumb"] {{
        background: {GOLD_SOLID} !important;
    }}

    /* ═══════════════════════════════════════
       EXPANDER
    ═══════════════════════════════════════ */
    .stExpander {{
        background: {SURFACE_LIGHT} !important;
        border: 1px solid {BORDER_GOLD} !important;
        border-radius: 8px !important;
    }}
    .stExpander summary {{
        color: {GOLD_SOLID} !important;
        font-weight: 500 !important;
    }}

    /* ═══════════════════════════════════════
       TABS
    ═══════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {{
        background: transparent !important;
        border-bottom: 1px solid rgba(201,168,76,0.15) !important;
        gap: 4px !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: 'Sarabun', sans-serif !important;
        color: {TEXT_SECONDARY} !important;
        border-radius: 6px 6px 0 0 !important;
        padding: 8px 18px !important;
        transition: color 0.2s ease, background 0.2s ease !important;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: {GOLD_SOLID} !important;
        background: rgba(201,168,76,0.06) !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: {GOLD_SOLID} !important;
        background: rgba(201,168,76,0.08) !important;
        border-bottom: 2px solid {GOLD_SOLID} !important;
    }}

    /* ═══════════════════════════════════════
       DATAFRAME / TABLE
    ═══════════════════════════════════════ */
    [data-testid="stDataFrame"] {{
        background: {SURFACE} !important;
        border: 1px solid {BORDER_GOLD} !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }}

    /* ═══════════════════════════════════════
       ALERTS / CALLOUTS
    ═══════════════════════════════════════ */
    .stAlert {{
        border-radius: 8px !important;
        border-left-width: 3px !important;
    }}
    .disclaimer {{
        font-size: 0.82rem;
        color: {TEXT_SECONDARY};
        background: rgba(201,168,76,0.05);
        border: 1px solid rgba(201,168,76,0.15);
        border-radius: 8px;
        padding: 10px 16px;
        margin: 12px 0;
    }}

    /* ═══════════════════════════════════════
       EXPLANATION PANELS
    ═══════════════════════════════════════ */
    .layman-panel {{
        font-family: 'Sarabun', sans-serif;
        font-size: 1rem;
        color: {TEXT_PRIMARY};
        background: rgba(201,168,76,0.05);
        border-left: 3px solid rgba(201,168,76,0.4);
        border-radius: 0 8px 8px 0;
        padding: 14px 20px;
        margin: 16px 0;
        line-height: 1.75;
    }}
    .tech-block {{
        background: rgba(122,24,24,0.12);
        border-left: 3px solid {GOLD_SOLID};
        border-radius: 0 8px 8px 0;
        padding: 16px 22px;
        margin: 16px 0;
    }}

    /* ═══════════════════════════════════════
       RESPONSIVE — LARGE TABLET (≤ 1024px)
    ═══════════════════════════════════════ */
    @media (max-width: 1024px) {{
        h1 {{ font-size: clamp(1.6rem, 4vw, 2.4rem) !important; }}
        .metric-value {{ font-size: clamp(1.6rem, 3.5vw, 2.2rem); }}
        .metric-container {{ padding: 20px 14px; min-height: 115px; }}
    }}

    /* ═══════════════════════════════════════
       RESPONSIVE — TABLET (≤ 768px)
    ═══════════════════════════════════════ */
    @media (max-width: 768px) {{
        /* Typography */
        h1 {{ font-size: 1.55rem !important; }}
        h2 {{ font-size: 1.08rem !important; }}
        h3 {{ font-size: 0.95rem !important; }}
        p, li {{ font-size: 0.92rem !important; }}

        /* Metric cards — 2 per row */
        .metrics-row {{
            flex-wrap: wrap !important;
            gap: 10px !important;
        }}
        .metrics-row .metric-container {{
            flex: 1 1 calc(50% - 10px) !important;
            min-width: calc(50% - 10px) !important;
            min-height: 105px !important;
            padding: 16px 10px !important;
        }}
        .metric-value {{ font-size: 1.65rem !important; }}
        .metric-label {{ font-size: 0.6rem; letter-spacing: 0.1em; }}

        /* Sidebar */
        [data-testid="stSidebarNav"] li:first-child a {{ font-size: 1.2rem !important; }}
        .sidebar-credit {{ width: 230px !important; }}

        /* Buttons */
        .stButton > button {{
            font-size: 0.88rem !important;
            padding: 0.45rem 1rem !important;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab"] {{
            padding: 6px 12px !important;
            font-size: 0.84rem !important;
        }}

        /* Explanation panels */
        .layman-panel, .tech-block {{
            padding: 12px 14px !important;
            font-size: 0.9rem !important;
        }}

        /* Disclaimer */
        .disclaimer {{ font-size: 0.78rem !important; }}

        /* Sidebar mode selector */
        .sidebar-mode-desc {{ font-size: 0.68rem !important; }}
    }}

    /* ═══════════════════════════════════════
       RESPONSIVE — PHONE (≤ 480px)
    ═══════════════════════════════════════ */
    @media (max-width: 480px) {{
        /* Typography */
        h1 {{ font-size: 1.3rem !important; }}
        h2 {{ font-size: 1rem !important; }}
        h3 {{ font-size: 0.9rem !important; }}

        /* Main content padding */
        [data-testid="stMainBlockContainer"] {{
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }}

        /* Metric cards — stack to 1 column */
        .metrics-row .metric-container {{
            flex: 1 1 100% !important;
            min-width: 100% !important;
            min-height: 90px !important;
            padding: 14px 10px !important;
        }}
        .metric-value {{ font-size: 1.5rem !important; }}
        .metric-label {{ font-size: 0.58rem !important; letter-spacing: 0.08em !important; }}

        /* Touch-friendly controls */
        .stButton > button {{
            font-size: 0.85rem !important;
            padding: 0.55rem 1rem !important;
            min-height: 44px !important;
        }}
        [data-testid="stSlider"] {{ padding: 6px 0 !important; }}
        [data-testid="stSelectbox"] > div > div {{ min-height: 42px !important; }}

        /* Tabs scroll friendly */
        .stTabs [data-baseweb="tab-list"] {{
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            padding: 5px 10px !important;
            font-size: 0.8rem !important;
            white-space: nowrap !important;
        }}

        /* Explanation panels */
        .layman-panel, .tech-block {{
            padding: 10px 12px !important;
            font-size: 0.88rem !important;
        }}

        /* Sidebar credit — smaller */
        .sidebar-credit {{ width: 200px !important; }}
        .sidebar-credit img {{ width: 30px !important; height: 30px !important; }}
        .sidebar-credit-text {{ font-size: 0.65rem !important; }}
        .sidebar-credit-text b {{ font-size: 0.7rem !important; }}

        /* Charts — reduce top margin */
        [data-testid="stPlotlyChart"] {{ margin-top: 0 !important; }}
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


def render_metrics_row(items: list[tuple[str, str]]) -> None:
    """Render a list of (label, value) pairs as equal-width metric cards in one HTML row."""
    cards = "".join(
        f'<div class="metric-container" style="flex:1 1 0; min-width:0;">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'</div>'
        for label, value in items
    )
    st.markdown(
        f'<div class="metrics-row" style="display:flex; gap:16px; align-items:stretch; width:100%; box-sizing:border-box;">{cards}</div>',
        unsafe_allow_html=True,
    )

def apply_layout(fig: go.Figure, **overrides) -> go.Figure:
    layout = {**PLOTLY_LAYOUT, **overrides}
    fig.update_layout(**layout)
    return fig

PERSONA_OPTIONS = ["ทั่วไป", "Math"]
PERSONA_QUERY_VALUES = {
    "ทั่วไป": "general",
    "Math": "math",
}
PERSONA_QUERY_LOOKUP = {value: key for key, value in PERSONA_QUERY_VALUES.items()}


def _query_persona() -> str | None:
    value = st.query_params.get("persona")
    if isinstance(value, list):
        value = value[0] if value else None
    return PERSONA_QUERY_LOOKUP.get(value)


def _lock_persona() -> None:
    selected = st.session_state.get("_persona_selector", "ทั่วไป")
    if selected not in PERSONA_OPTIONS:
        selected = "ทั่วไป"
    st.session_state.persona = selected
    st.query_params["persona"] = PERSONA_QUERY_VALUES[selected]


def _persist_persona_in_browser() -> None:
    current = PERSONA_QUERY_VALUES[st.session_state.persona]
    components.html(
        f"""
        <script>
        (function() {{
            const key = "thai_lotto_persona";
            const current = "{current}";
            const url = new URL(window.parent.location.href);
            const urlPersona = url.searchParams.get("persona");
            const stored = window.parent.localStorage.getItem(key);

            if (!urlPersona && stored && stored !== current) {{
                url.searchParams.set("persona", stored);
                window.parent.location.replace(url.toString());
                return;
            }}

            window.parent.localStorage.setItem(key, current);
            if (urlPersona !== current) {{
                url.searchParams.set("persona", current);
                window.parent.history.replaceState(null, "", url.toString());
            }}

            const navLabels = {{
                home: {{
                    general: "Thai Lotto",
                    math: "Thai Lotto",
                    icon: "",
                    aliases: ["app", "Thai Lotto"]
                }},
                dataOverview: {{
                    general: "ส่องโพยสถิติ",
                    math: "Data Overview",
                    icon: "📋",
                    aliases: ["ส่องโพยสถิติ", "Data Overview"]
                }},
                selector: {{
                    general: "คิดไม่ออก เดี๋ยวเลือกให้",
                    math: "Selection Engine",
                    icon: "🎲",
                    aliases: ["คิดไม่ออก เดี๋ยวเลือกให้", "Selection Engine"]
                }},
                frequency: {{
                    general: "เลขไหนฮิต เลขไหนดับ",
                    math: "Frequency Distribution",
                    icon: "📊",
                    aliases: ["เลขไหนฮิต เลขไหนดับ", "Frequency Distribution"]
                }},
                predictor: {{
                    general: "สำนักคำนวณเลขเด็ด",
                    math: "Predictor Lab",
                    icon: "🔮",
                    aliases: ["สำนักคำนวณเลขเด็ด", "Predictor Lab"]
                }},
                validation: {{
                    general: "AI จะแม่นจริงไหม",
                    math: "Walk-Forward Validation",
                    icon: "🎯",
                    aliases: ["AI จะแม่นจริงไหม", "Walk-Forward Validation"]
                }},
                backtest: {{
                    general: "ลองแทงทิพย์ รวยหรือเจ๊ง",
                    math: "Strategy Backtest",
                    icon: "💰",
                    aliases: ["ลองแทงทิพย์ รวยหรือเจ๊ง", "Strategy Backtest"]
                }},
                calendar: {{
                    general: "อาถรรพ์เลขตามปฏิทิน",
                    math: "Calendar Effect Test",
                    icon: "📅",
                    aliases: ["อาถรรพ์เลขตามปฏิทิน", "Calendar Effect Test"]
                }}
            }};
            const aliasToKey = {{}};
            Object.keys(navLabels).forEach(function(keyName) {{
                navLabels[keyName].aliases.forEach(function(alias) {{
                    aliasToKey[alias] = keyName;
                }});
            }});

            function normalizeLabel(text) {{
                return (text || "")
                    .replace(/[📋🎲📊🔮🎯💰📅]/g, "")
                    .replace(/[:?]/g, "")
                    .replace(/^[0-9]+[_\\s-]*/, "")
                    .replace(/\\s+/g, " ")
                    .trim();
            }}

            function rewriteSidebarLabels() {{
                const persona = window.parent.localStorage.getItem(key) || current;
                const nav = window.parent.document.querySelector('[data-testid="stSidebarNav"]');
                if (!nav) return;
                nav.querySelectorAll("a").forEach(function(el) {{
                    if (!el) return;
                    const raw = el.textContent || "";
                    const normalized = normalizeLabel(raw);
                    const labelKey = aliasToKey[normalized];
                    if (!labelKey) return;
                    const nextLabel = persona === "math" ? navLabels[labelKey].math : navLabels[labelKey].general;
                    const icon = navLabels[labelKey].icon;
                    const next = persona === "math" ? nextLabel : ((icon ? icon + " " : "") + nextLabel);
                    if (el.textContent !== next) el.textContent = next;
                    if (el.title) el.title = next;
                    el.setAttribute("aria-label", next);
                }});
            }}

            rewriteSidebarLabels();
            setTimeout(rewriteSidebarLabels, 150);
            setTimeout(rewriteSidebarLabels, 600);
            if (!window.parent.__thaiLottoNavObserver) {{
                window.parent.__thaiLottoNavObserver = new MutationObserver(rewriteSidebarLabels);
                window.parent.__thaiLottoNavObserver.observe(window.parent.document.body, {{
                    childList: true,
                    subtree: true
                }});
            }}
        }})();
        </script>
        """,
        height=0,
        width=1,
    )


def init_persona() -> str:
    query_persona = _query_persona()
    if query_persona:
        st.session_state.persona = query_persona
    elif "persona" not in st.session_state:
        st.session_state.persona = "ทั่วไป"
    if st.session_state.persona not in PERSONA_OPTIONS:
        st.session_state.persona = "ทั่วไป"

    with st.sidebar:
        st.markdown("""
        <div class="sidebar-mode-wrap">
            <div class="sidebar-mode-title">โหมดการแสดงผล</div>
            <div class="sidebar-mode-desc">ทั่วไป = ภาษาไทยเข้าใจง่าย<br>Math = สูตรและรายละเอียดวิชาการ</div>
        </div>
        """, unsafe_allow_html=True)
        st.radio(
            "โหมดการแสดงผล",
            PERSONA_OPTIONS,
            key="_persona_selector",
            index=PERSONA_OPTIONS.index(st.session_state.persona),
            horizontal=True,
            label_visibility="collapsed",
            on_change=_lock_persona,
        )
        credit_html = _sidebar_credit_html()
        if credit_html:
            st.markdown(credit_html, unsafe_allow_html=True)
    _persist_persona_in_browser()
    return st.session_state.persona


def is_math_mode() -> bool:
    return st.session_state.get("persona", "ทั่วไป") == "Math"


def mode_text(general: str, math: str) -> str:
    return math if is_math_mode() else general

def render_explanation(layman: str, math: str, formula: str = None) -> None:
    if is_math_mode():
        st.markdown(f"""
        <div class="tech-block explanation-panel">
            <b style="color:{GOLD_SOLID}; font-family:'Playfair Display', serif; letter-spacing:0.1em; font-size:1.1rem;">EXPERIMENTAL LOG & SPECS</b><br>
            <p style="color:{TEXT_GOLD}; font-size: 0.95rem; line-height:1.7; margin-top:10px;">{math}</p>
        </div>
        """, unsafe_allow_html=True)
        if formula:
            st.latex(formula)
    else:
        st.markdown(f'<div class="layman-panel explanation-panel">“ {layman} ”</div>', unsafe_allow_html=True)

def gold_line_style() -> dict:
    return dict(color=GOLD_SOLID, width=2)

def crimson_bar_style() -> dict:
    return dict(color=ROYAL_CRIMSON)
