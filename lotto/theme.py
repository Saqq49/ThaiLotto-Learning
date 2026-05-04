import plotly.graph_objects as go
import streamlit as st

# Thai Prestige Color Palette (Red-Gold)
CRIMSON = "#BD001B"  # Royal Crimson
GOLD = "#D4AF37"     # Metallic Gold
GOLD_DARK = "#D3A42E" # Liquid Gold
CHAMPAGNE = "#F6D365" # Soft Champagne
BG_LIGHT = "#F5F5F5"  # Panel Gray
TEXT_DARK = "#0B0F14" # Rich Charcoal
PANEL_WHITE = "#FFFFFF"

# Backward compatibility or alternate shades
GOLD_DIM = GOLD_DARK

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT_DARK, family="sans-serif"),
    colorway=[CRIMSON, GOLD, GOLD_DARK, "#FF6B6B", "#FFC300"],
    margin=dict(l=40, r=40, t=50, b=40),
    hoverlabel=dict(bgcolor=PANEL_WHITE, font_color=TEXT_DARK),
)

CUSTOM_CSS = f"""
<style>
    /* Main Background */
    .stApp {{
        background-color: {BG_LIGHT};
        color: {TEXT_DARK};
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {PANEL_WHITE};
        border-right: 1px solid {GOLD}33;
    }}

    /* Metric Cards */
    .metric-container {{
        background: {PANEL_WHITE};
        border-top: 3px solid {GOLD};
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
        margin-bottom: 20px;
    }}
    .metric-container:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.1);
    }}
    .metric-label {{
        color: {TEXT_DARK};
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 5px;
        opacity: 0.7;
    }}
    .metric-value {{
        color: {CRIMSON};
        font-size: 2rem;
        font-weight: 800;
        font-family: 'serif';
    }}

    /* Tags */
    .hot-tag {{
        display: inline-block;
        background: {CRIMSON}15;
        border-left: 4px solid {CRIMSON};
        color: {CRIMSON};
        padding: 6px 15px;
        margin: 4px 0;
        border-radius: 0 5px 5px 0;
        font-weight: 600;
        width: 100%;
    }}
    .cold-tag {{
        display: inline-block;
        background: #E8F0F8;
        border-left: 4px solid #4488CC;
        color: #4488CC;
        padding: 6px 15px;
        margin: 4px 0;
        border-radius: 0 5px 5px 0;
        font-weight: 600;
        width: 100%;
    }}

    /* Disclaimer */
    .disclaimer {{
        background: {CRIMSON}05;
        border: 1px solid {CRIMSON}33;
        padding: 15px;
        border-radius: 8px;
        color: {TEXT_DARK};
        font-size: 0.85rem;
        margin: 15px 0;
        line-height: 1.5;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
        color: {TEXT_DARK};
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {GOLD}15 !important;
        border-bottom: 2px solid {GOLD} !important;
        color: {CRIMSON} !important;
    }}

    /* Mobile Responsive Columns Hack */
    @media (max-width: 768px) {{
        [data-testid="stHorizontalBlock"] {{
            flex-direction: row !important;
            flex-wrap: wrap !important;
        }}
        [data-testid="stHorizontalBlock"] > div {{
            width: calc(50% - 0.5rem) !important;
            min-width: calc(50% - 0.5rem) !important;
            flex: 1 1 calc(50% - 0.5rem) !important;
        }}
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


def gold_line_style() -> dict:
    return dict(color=GOLD, width=2)


def crimson_bar_style() -> dict:
    return dict(color=CRIMSON)
