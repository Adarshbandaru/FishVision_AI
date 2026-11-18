# Custom styling for FishVision AI following Stitch Design Tokens
import streamlit as st


def inject_custom_css():
    st.markdown(
        """<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

:root {
    --bg-surface: #0b1322;
    --bg-surface-low: #141c2b;
    --bg-surface-container: #18202f;
    --bg-surface-high: #222a3a;
    --bg-surface-highest: #2d3545;
    --primary: #00f2fe;
    --primary-bright: #e0fdff;
    --secondary: #47efd6;
    --text-primary: #dbe2f8;
    --text-muted: #849495;
    --border-subtle: #2d3545;
    --border-cyan: rgba(0, 242, 254, 0.25);
    --accent-glow: 0 0 25px rgba(0, 242, 254, 0.15);
}

/* Base Body and Streamlit App Background */
.stApp {
    background-color: #0b1322 !important;
    color: #dbe2f8 !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

header[data-testid="stHeader"] {
    background: rgba(11, 19, 34, 0.85) !important;
    backdrop-filter: blur(12px) !important;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #0e1726 !important;
    border-right: 1px solid #1f2a3e !important;
}

section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #00f2fe !important;
}

/* Radio buttons for navigation */
div[data-testid="stRadio"] > div {
    gap: 6px;
}
div[data-testid="stRadio"] label {
    background: #141c2b;
    border: 1px solid #222a3a;
    border-radius: 8px;
    padding: 10px 14px;
    color: #dbe2f8 !important;
    transition: all 0.2s ease;
    cursor: pointer;
}
div[data-testid="stRadio"] label:hover {
    background: #1e283d;
    border-color: rgba(0, 242, 254, 0.4);
}
div[data-testid="stRadio"] label[data-checked="true"] {
    background: #1a273b !important;
    border-color: #00f2fe !important;
    box-shadow: 0 0 12px rgba(0, 242, 254, 0.25) !important;
}

/* Native bordered containers styled as Stitch cards */
.st-key-upload_card,
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #141c2b;
    border-color: #222a3a !important;
    border-radius: 12px !important;
}

/* Glass & Surface Cards */
.fv-card {
    background: #141c2b;
    border: 1px solid #222a3a;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.fv-card:hover {
    border-color: rgba(0, 242, 254, 0.35);
}
.fv-card-glow {
    border-color: rgba(0, 242, 254, 0.4) !important;
    box-shadow: 0 0 25px rgba(0, 242, 254, 0.08);
}

.fv-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.fv-badge-cyan {
    background: rgba(0, 242, 254, 0.12);
    color: #00f2fe;
    border: 1px solid rgba(0, 242, 254, 0.3);
}
.fv-badge-teal {
    background: rgba(71, 239, 214, 0.12);
    color: #47efd6;
    border: 1px solid rgba(71, 239, 214, 0.3);
}
.fv-badge-amber {
    background: rgba(251, 191, 36, 0.12);
    color: #fbbf24;
    border: 1px solid rgba(251, 191, 36, 0.3);
}
.fv-badge-red {
    background: rgba(239, 68, 68, 0.12);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

/* Buttons */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00f2fe 0%, #03d2ba 100%) !important;
    color: #002022 !important;
    border: none !important;
    box-shadow: 0 0 16px rgba(0, 242, 254, 0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 24px rgba(0, 242, 254, 0.5) !important;
    transform: translateY(-1px);
}
.stButton > button[kind="secondary"] {
    background: #18202f !important;
    color: #dbe2f8 !important;
    border: 1px solid #2d3545 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #222a3a !important;
    border-color: #00f2fe !important;
}

/* File Uploader */
div[data-testid="stFileUploader"] {
    background: #0b1322;
    border: 2px dashed #2d3545;
    border-radius: 12px;
    padding: 14px;
    transition: border-color 0.2s ease;
}
div[data-testid="stFileUploader"]:hover {
    border-color: #00f2fe;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #849495 !important;
    font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #00f2fe !important;
}

/* Metrics and Dataframe styling */
div[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    color: #00f2fe !important;
    font-size: 28px !important;
}
div[data-testid="stMetricLabel"] {
    color: #849495 !important;
    font-size: 13px !important;
}

/* Dataframe dark mode */
div[data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #222a3a;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #0b1322;
}
::-webkit-scrollbar-thumb {
    background: #222a3a;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #00f2fe;
}
</style>""",
        unsafe_allow_html=True,
    )
