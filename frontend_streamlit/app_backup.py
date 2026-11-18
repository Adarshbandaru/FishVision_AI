import streamlit as st
import requests, pandas as pd
import plotly.express as px
from PIL import Image
from pathlib import Path

st.set_page_config(page_title="FishVision V2", page_icon="🐟", layout="wide")
API = "http://127.0.0.1:8000"
st.markdown("""
<style>
.main {background:#f7f9fc}
.hero {padding:1.2rem 1.5rem;border-radius:16px;background:linear-gradient(110deg,#102a43,#176b87);color:white}
.metric {border:1px solid #dce5ee;border-radius:12px;padding:14px;background:white}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🐟 FishVision V2</h1><p>Vision Transformers for Fish Species Recognition · 152 species · 5 deep-learning architectures</p></div>', unsafe_allow_html=True)
st.write("")
try:
    health = requests.get(f"{API}/health", timeout=5).json()
    st.sidebar.success("Backend connected")
    st.sidebar.caption(f"Device: {health['device'].upper()} · CPU inference")
except Exception:
    st.error("Backend is not running. Close this page, launch run.bat, then refresh.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["🔍 Live Prediction", "📊 Model Comparison", "ℹ️ About"])
with tab1:
    st.subheader("Upload a fish image")
    up = st.file_uploader("Choose a JPG, PNG or WEBP image", type=["jpg","jpeg","png","webp","bmp"])
    if up:
        image = Image.open(up).convert("RGB")
        left, right = st.columns([1,1.5])
        with left:
            st.image(image, caption="Uploaded image", use_container_width=True)
            run = st.button("Run all five models", type="primary", use_container_width=True)
        if run:
            with st.spinner("Running CPU inference. DINOv2 may take longer on a laptop without an NVIDIA GPU..."):
                try:
                    resp = requests.post(f"{API}/predict",
                        files={"file":(up.name, up.getvalue(), up.type or "image/jpeg")},
                        timeout=900)
                    resp.raise_for_status()
                    st.session_state["prediction"] = resp.json()
                except Exception as e:
                    st.error(f"Prediction error: {e}")
        if "prediction" in st.session_state:
            results = st.session_state["prediction"]["results"]
            with right:
                st.markdown("### Five-model live predictions")
                df = pd.DataFrame([{"Model":r["model"],"Predicted species":r["prediction"],
                                    "Confidence (%)":r["confidence"]} for r in results])
                st.dataframe(df, hide_index=True, use_container_width=True)
                st.markdown("### DINOv2 — Top 5")
                dino = next(r for r in results if r["model"]=="DINOv2")
                for i, item in enumerate(dino["top5"],1):
                    st.write(f"**{i}. {item['species']}** — {item['confidence']:.2f}%")
                    st.progress(min(item["confidence"]/100,1.0))
                st.caption("Confidence is the model's softmax score, not a guarantee of correctness.")
with tab2:
    st.subheader("Frozen test-set performance")
    st.caption("These are the previously evaluated test-set metrics (3,309 images), not predictions on your uploaded image.")
    metrics = pd.DataFrame([
        ["DINOv2",93.8954,88.2366,87.3145,86.9592,None],
        ["ViT-B/16",88.3348,80.0143,81.3011,78.8563,88.4780],
        ["ConvNeXt Tiny",87.3980,79.8363,79.0629,77.5887,87.5096],
        ["Swin Tiny",85.1315,78.0993,76.3637,75.6324,85.1313],
        ["MobileNetV3",70.3234,59.4439,58.9083,57.3600,69.8887],
    ],columns=["Model","Accuracy","Macro precision","Macro recall","Macro F1","Weighted F1"])
    c1,c2,c3=st.columns(3)
    c1.metric("Best accuracy","93.90%","DINOv2")
    c2.metric("Best Macro F1","86.96%","DINOv2")
    c3.metric("Test images","3,309","152 classes")
    fig=px.bar(metrics.sort_values("Accuracy",ascending=True),x="Accuracy",y="Model",
               orientation="h",text_auto=".2f",title="Test accuracy by model")
    fig.update_layout(xaxis_title="Accuracy (%)",yaxis_title="",xaxis_range=[0,100])
    st.plotly_chart(fig,use_container_width=True)
    st.dataframe(metrics.style.format({c:"{:.2f}%" for c in ["Accuracy","Macro precision","Macro recall","Macro F1","Weighted F1"]}),
                 hide_index=True,use_container_width=True)
    st.info("DINOv2 weighted F1 was not available in the verified report and is intentionally shown as missing.")
with tab3:
    st.subheader("Project details")
    st.markdown("""
    - **Task:** Fine-grained fish species image classification.
    - **Dataset:** 22,741 images across 152 classes (15,305 train / 4,127 validation / 3,309 test).
    - **Architectures:** DINOv2, ViT-B/16, ConvNeXt Tiny, Swin Tiny and MobileNetV3.
    - **Deployment:** Streamlit frontend + FastAPI backend + PyTorch/timm.
    - **Hardware:** CPU inference on this laptop; no retraining is performed.

    **Research limitations:** The dataset is imbalanced and mixes natural underwater and specimen imagery. The reported results do not establish generalization to independent external datasets or all underwater environments.
    """)
    st.caption("FishVision V2 — local demonstration build")
