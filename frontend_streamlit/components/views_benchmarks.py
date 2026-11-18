import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render_benchmarks(root_dir: Path):
    metrics_file = root_dir / "data" / "verified_metrics.json"
    if metrics_file.exists():
        raw_data = json.loads(metrics_file.read_text(encoding="utf-8"))
        metrics_list = raw_data.get("metrics", [])
        dataset_info = raw_data.get("dataset", {})
    else:
        dataset_info = {"classes": 152, "train": 15305, "validation": 4127, "test": 3309, "total": 22741}
        metrics_list = [
            {"model": "DINOv2", "accuracy": 93.8954, "macro_precision": 88.2366, "macro_recall": 87.3145, "macro_f1": 86.9592, "weighted_f1": None},
            {"model": "ViT-B/16", "accuracy": 88.3348, "macro_precision": 80.0143, "macro_recall": 81.3011, "macro_f1": 78.8563, "weighted_f1": 88.4780},
            {"model": "ConvNeXt Tiny", "accuracy": 87.3980, "macro_precision": 79.8363, "macro_recall": 79.0629, "macro_f1": 77.5887, "weighted_f1": 87.5096},
            {"model": "Swin Tiny", "accuracy": 85.1315, "macro_precision": 78.0993, "macro_recall": 76.3637, "macro_f1": 75.6324, "weighted_f1": 85.1313},
            {"model": "MobileNetV3", "accuracy": 70.3234, "macro_precision": 59.4439, "macro_recall": 58.9083, "macro_f1": 57.3600, "weighted_f1": 69.8887},
        ]

    st.html(
        """
        <div style="margin-bottom: 24px;">
            <div style="display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap;">
                <span class="fv-badge fv-badge-cyan">Model Matrix</span>
                <span class="fv-badge fv-badge-teal">Held-Out Test Set Verification</span>
            </div>
            <h1 style="color: #e0fdff; font-size: 2.2rem; font-weight: 700; margin: 0 0 8px 0;">
                Deep Learning Model Benchmark Suite
            </h1>
            <p style="color: #849495; font-size: 0.95rem; margin: 0;">
                Rigorous evaluation of five distinct vision backbones across 3,309 unseen test specimens across 152 marine species classes.
            </p>
        </div>
        """
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.html(
            f"""
            <div class="fv-card" style="padding: 16px; margin-bottom: 0;">
                <div style="color: #849495; font-size: 0.75rem; text-transform: uppercase;">Total Dataset Size</div>
                <div style="color: #00f2fe; font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; font-weight: 700;">{dataset_info.get('total', 22741):,}</div>
                <div style="color: #849495; font-size: 0.75rem;">152 ichthyological classes</div>
            </div>
            """
        )
    with c2:
        st.html(
            f"""
            <div class="fv-card" style="padding: 16px; margin-bottom: 0;">
                <div style="color: #849495; font-size: 0.75rem; text-transform: uppercase;">Training Split (67%)</div>
                <div style="color: #47efd6; font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; font-weight: 700;">{dataset_info.get('train', 15305):,}</div>
                <div style="color: #849495; font-size: 0.75rem;">Supervised &amp; Self-supervised</div>
            </div>
            """
        )
    with c3:
        st.html(
            f"""
            <div class="fv-card" style="padding: 16px; margin-bottom: 0;">
                <div style="color: #849495; font-size: 0.75rem; text-transform: uppercase;">Validation Split (18%)</div>
                <div style="color: #38bdf8; font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; font-weight: 700;">{dataset_info.get('validation', 4127):,}</div>
                <div style="color: #849495; font-size: 0.75rem;">Hyperparameter calibration</div>
            </div>
            """
        )
    with c4:
        st.html(
            f"""
            <div class="fv-card" style="padding: 16px; margin-bottom: 0;">
                <div style="color: #849495; font-size: 0.75rem; text-transform: uppercase;">Final Test Split (15%)</div>
                <div style="color: #fbbf24; font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; font-weight: 700;">{dataset_info.get('test', 3309):,}</div>
                <div style="color: #849495; font-size: 0.75rem;">Frozen zero-leakage evaluation</div>
            </div>
            """
        )

    st.write("")
    df_metrics = pd.DataFrame(metrics_list)

    col_chart, col_radar = st.columns([1.3, 1])
    with col_chart:
        st.subheader("Top-1 Accuracy Comparison")
        fig_bar = px.bar(
            df_metrics.sort_values("accuracy", ascending=True),
            x="accuracy",
            y="model",
            orientation="h",
            text="accuracy",
            color="accuracy",
            color_continuous_scale=["#141c2b", "#00dce6", "#00f2fe"],
        )
        fig_bar.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
            marker_line_color="#00f2fe",
            marker_line_width=1,
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Top-1 Accuracy (%)", range=[50, 100], gridcolor="#1e283d", tickfont=dict(color="#849495")),
            yaxis=dict(title="", tickfont=dict(color="#dbe2f8", size=13)),
            showlegend=False,
            height=320,
            margin=dict(l=10, r=40, t=10, b=30),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_bar, width="stretch")

    with col_radar:
        st.subheader("Multi-Metric Radar Comparison")
        categories = ["Accuracy", "Macro Precision", "Macro Recall", "Macro F1"]
        fig_radar = go.Figure()

        colors = ["#00f2fe", "#47efd6", "#38bdf8", "#a78bfa", "#fbbf24"]
        for idx, row in df_metrics.iterrows():
            vals = [row["accuracy"], row["macro_precision"], row["macro_recall"], row["macro_f1"]]
            vals.append(vals[0])
            cats = categories + [categories[0]]
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=vals,
                    theta=cats,
                    fill="toself" if idx == 0 else "none",
                    name=row["model"],
                    line=dict(color=colors[idx % len(colors)], width=2),
                    opacity=0.7,
                )
            )

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[50, 100], gridcolor="#1e283d", tickfont=dict(color="#849495", size=9)),
                angularaxis=dict(gridcolor="#1e283d", tickfont=dict(color="#dbe2f8", size=10)),
                bgcolor="rgba(0,0,0,0)",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            legend=dict(font=dict(color="#dbe2f8", size=10), orientation="h", y=-0.15),
            height=320,
            margin=dict(l=20, r=20, t=10, b=40),
        )
        st.plotly_chart(fig_radar, width="stretch")

    st.subheader("Comprehensive Performance Matrix")

    display_df = df_metrics.copy()
    display_df.columns = ["Architecture", "Accuracy (%)", "Macro Precision (%)", "Macro Recall (%)", "Macro F1 (%)", "Weighted F1 (%)"]

    formatted_df = display_df.copy()
    for col in ["Accuracy (%)", "Macro Precision (%)", "Macro Recall (%)", "Macro F1 (%)", "Weighted F1 (%)"]:
        formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "— (Not Reported)")

    st.dataframe(formatted_df, hide_index=True, width="stretch")

    st.html(
        """
        <div style="background: #141c2b; border: 1px solid #222a3a; border-radius: 8px; padding: 14px 18px; margin-top: 14px; font-size: 0.85rem; color: #849495;">
            <strong style="color: #00f2fe;">Verification Note:</strong>
            The metrics above reflect previously evaluated test-set outcomes from the final research report across 3,309 held-out images.
            DINOv2 weighted F1 was not computed in the original benchmark log and is preserved as missing without fabrication.
            Live uploaded image confidences reflect individual model softmax activations and are kept strictly distinct from these test-set metrics.
        </div>
        """
    )
