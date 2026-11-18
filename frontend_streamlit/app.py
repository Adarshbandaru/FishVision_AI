from html import escape
from pathlib import Path

import requests
import streamlit as st

from components.theme import inject_custom_css
from components.views_about import render_about
from components.views_benchmarks import render_benchmarks
from components.views_catalog import render_catalog
from components.views_dashboard import render_dashboard
from components.views_history import render_history
from components.views_workspace import render_workspace

st.set_page_config(
    page_title="FishVision AI — Research Platform",
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom design tokens & responsive CSS
inject_custom_css()

API = "http://127.0.0.1:8000"
ROOT_DIR = Path(__file__).resolve().parents[1]

# Sidebar Brand & Health Check
with st.sidebar:
    st.html(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px; padding-bottom: 14px; border-bottom: 1px solid #1f2a3e;">
            <span style="font-size: 26px;">🐟</span>
            <div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #00f2fe; line-height: 1.1;">
                    FishVision <span style="color: #47efd6; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">AI</span>
                </div>
                <div style="font-size: 0.72rem; color: #849495; letter-spacing: 0.05em; text-transform: uppercase;">v2.4 Academic Edition</div>
            </div>
        </div>
        """
    )

    # Backend Health Check
    backend_online = False
    try:
        health_resp = requests.get(f"{API}/health", timeout=3)
        if health_resp.status_code == 200:
            health = health_resp.json()
            backend_online = True
            device = escape(str(health.get("device", "cpu")).upper())
            models_count = int(health.get("models", 5))
            st.html(
                f"""
                <div style="background: rgba(71, 239, 214, 0.08); border: 1px solid rgba(71, 239, 214, 0.3); border-radius: 6px; padding: 8px 12px; margin-bottom: 14px;">
                    <div style="color: #47efd6; font-size: 0.8rem; font-weight: 600; display: flex; align-items: center; gap: 6px;">
                        <span style="width: 8px; height: 8px; border-radius: 50%; background: #47efd6; display: inline-block;"></span>
                        Backend Operational
                    </div>
                    <div style="color: #849495; font-size: 0.72rem; margin-top: 3px; font-family: 'JetBrains Mono', monospace;">
                        {device} · {models_count} Models Configured
                    </div>
                </div>
                """
            )
    except Exception:
        st.html(
            """
            <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; padding: 8px 12px; margin-bottom: 14px;">
                <div style="color: #f87171; font-size: 0.8rem; font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: #f87171; display: inline-block;"></span>
                    Backend Offline
                </div>
                <div style="color: #849495; font-size: 0.72rem; margin-top: 3px;">
                    Start FastAPI on port 8000 via run.bat.
                </div>
            </div>
            """
        )

    nav_options = [
        "Dashboard",
        "Fish Recognition Workspace",
        "Model Comparison & Benchmarks",
        "Prediction History",
        "Species Information Catalog",
        "About Project & Methodology",
    ]

    if "nav_radio" not in st.session_state:
        st.session_state["nav_radio"] = "Dashboard"
    if "pending_nav" in st.session_state:
        st.session_state["nav_radio"] = st.session_state.pop("pending_nav")

    selected_page = st.radio(
        "Navigation",
        options=nav_options,
        label_visibility="collapsed",
        key="nav_radio",
    )

    st.html("<div style='margin-top: 24px; padding-top: 14px; border-top: 1px solid #1f2a3e;'></div>")
    st.caption("152-class deep learning fish identification across Vision Transformers & ConvNets.")

# Page Routing
if selected_page == "Dashboard":
    render_dashboard()
elif selected_page == "Fish Recognition Workspace":
    if not backend_online:
        st.error("Backend service is offline. Please launch FastAPI backend (e.g. via run.bat) to execute model inference.")
    render_workspace(API, ROOT_DIR)
elif selected_page == "Model Comparison & Benchmarks":
    render_benchmarks(ROOT_DIR)
elif selected_page == "Prediction History":
    render_history()
elif selected_page == "Species Information Catalog":
    render_catalog(ROOT_DIR)
elif selected_page == "About Project & Methodology":
    render_about()
