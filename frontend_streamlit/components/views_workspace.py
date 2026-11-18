from datetime import datetime
from html import escape
from io import BytesIO
import json
from pathlib import Path

import pandas as pd
from PIL import Image, UnidentifiedImageError
import requests
import streamlit as st

MAX_UPLOAD_MB = 15
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024


def _load_species_catalog(root_dir: Path) -> dict:
    meta_path = root_dir / "data" / "species_metadata.json"
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _render_result_header(
    common_name: str,
    sci_name: str,
    pred_conf: float,
    agree_count: int,
    total_models: int,
    consensus_pct: float,
):
    if agree_count >= 4:
        banner_bg = "rgba(71, 239, 214, 0.1)"
        banner_border = "rgba(71, 239, 214, 0.3)"
        banner_color = "#47efd6"
        agreement_label = "High Cross-Model Agreement"
    elif agree_count >= 2:
        banner_bg = "rgba(251, 191, 36, 0.1)"
        banner_border = "rgba(251, 191, 36, 0.3)"
        banner_color = "#fbbf24"
        agreement_label = "Moderate Model Agreement"
    else:
        banner_bg = "rgba(239, 68, 68, 0.1)"
        banner_border = "rgba(239, 68, 68, 0.3)"
        banner_color = "#f87171"
        agreement_label = "Significant Model Disagreement"

    st.html(
        f"""
        <div class="fv-card fv-card-glow" style="padding: 22px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                <div>
                    <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 8px; flex-wrap: wrap;">
                        <span class="fv-badge fv-badge-cyan">Primary SOTA Inference</span>
                        <span class="fv-badge fv-badge-teal">DINOv2 Backbone</span>
                    </div>
                    <h2 style="color: #00f2fe; font-size: 2rem; font-weight: 800; margin: 0 0 4px 0;">{escape(common_name)}</h2>
                    <div style="color: #47efd6; font-style: italic; font-size: 1.05rem; font-family: Georgia, serif;">{escape(sci_name)}</div>
                </div>
                <div style="text-align: right;">
                    <div style="color: #849495; font-size: 0.75rem; text-transform: uppercase;">Softmax Score (Uncalibrated)</div>
                    <div style="color: #00f2fe; font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 700;">{pred_conf:.2f}%</div>
                </div>
            </div>
            <div style="margin-top: 16px; padding: 10px 14px; border-radius: 6px;
                        background: {banner_bg}; border: 1px solid {banner_border};
                        display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div style="color: {banner_color}; font-size: 0.9rem; font-weight: 600;">
                    {escape(agreement_label)}
                </div>
                <div style="color: #dbe2f8; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">
                    <strong>{agree_count} of {total_models}</strong> models consensus ({consensus_pct:.0f}%)
                </div>
            </div>
        </div>
        """
    )


def _render_model_cards(results: list, primary_species: str):
    cards_html = []
    for r in results:
        model_name = escape(str(r.get("model", "Model")))
        species_name = escape(str(r.get("prediction", "Unknown")))
        conf = float(r.get("confidence", 0.0))
        is_match = r.get("prediction") == primary_species
        accent = "#47efd6" if is_match else "#fbbf24"
        status_text = "Agrees with DINOv2" if is_match else "Differs from DINOv2"
        badge_cls = "fv-badge-teal" if is_match else "fv-badge-amber"
        cards_html.append(
            f"""
            <div style="background: #0b1322; border: 1px solid #1f2a3e; border-left: 3px solid {accent}; border-radius: 8px; padding: 12px 14px;">
                <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="color: #849495; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;">{model_name}</span>
                    <span class="fv-badge {badge_cls}" style="font-size: 10px; padding: 2px 7px;">{escape(status_text)}</span>
                </div>
                <div style="color: #e0fdff; font-size: 1rem; font-weight: 700; margin-bottom: 4px;">{species_name}</div>
                <div style="color: #00f2fe; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; font-weight: 600;">{conf:.2f}% softmax</div>
            </div>
            """
        )

    st.html(
        f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; margin: 12px 0 16px 0;">
            {''.join(cards_html)}
        </div>
        """
    )


def _render_species_cards(meta: dict):
    habitat = escape(str(meta.get("habitat", "Information not available")))
    water_type = escape(str(meta.get("water_type", "Information not available")))
    distribution = escape(str(meta.get("geographic_distribution", "Information not available")))
    typical_size = escape(str(meta.get("typical_size", "Information not available")))
    diet = escape(str(meta.get("diet", "Information not available")))
    conservation = escape(str(meta.get("conservation_status", "Information not available")))
    interesting_facts = escape(str(meta.get("interesting_facts", "Information not available")))

    st.html(
        f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin: 12px 0 14px 0;">
            <div style="background: #0b1322; padding: 12px; border-radius: 8px; border: 1px solid #1f2a3e;">
                <div style="color: #849495; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 4px;">Habitat</div>
                <div style="color: #dbe2f8; font-size: 0.88rem; font-weight: 500;">{habitat}</div>
            </div>
            <div style="background: #0b1322; padding: 12px; border-radius: 8px; border: 1px solid #1f2a3e;">
                <div style="color: #849495; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 4px;">Water Type</div>
                <div style="color: #dbe2f8; font-size: 0.88rem; font-weight: 500;">{water_type}</div>
            </div>
            <div style="background: #0b1322; padding: 12px; border-radius: 8px; border: 1px solid #1f2a3e;">
                <div style="color: #849495; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 4px;">Geographic Distribution</div>
                <div style="color: #dbe2f8; font-size: 0.88rem; font-weight: 500;">{distribution}</div>
            </div>
            <div style="background: #0b1322; padding: 12px; border-radius: 8px; border: 1px solid #1f2a3e;">
                <div style="color: #849495; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 4px;">Typical Size</div>
                <div style="color: #dbe2f8; font-size: 0.88rem; font-weight: 500;">{typical_size}</div>
            </div>
            <div style="background: #0b1322; padding: 12px; border-radius: 8px; border: 1px solid #1f2a3e;">
                <div style="color: #849495; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 4px;">Diet</div>
                <div style="color: #dbe2f8; font-size: 0.88rem; font-weight: 500;">{diet}</div>
            </div>
            <div style="background: #0b1322; padding: 12px; border-radius: 8px; border: 1px solid #1f2a3e;">
                <div style="color: #849495; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 4px;">Conservation Status</div>
                <div style="color: #fbbf24; font-size: 0.88rem; font-weight: 600;">{conservation}</div>
            </div>
        </div>
        <div style="background: #0b1322; padding: 12px 14px; border-radius: 6px; border-left: 3px solid #00f2fe;">
            <div style="color: #00f2fe; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Ecological Notes & Facts</div>
            <div style="color: #dbe2f8; font-size: 0.88rem; line-height: 1.5; margin-top: 4px;">{interesting_facts}</div>
        </div>
        """
    )


def render_workspace(api_url: str, root_dir: Path):
    species_catalog = _load_species_catalog(root_dir)

    st.html(
        """
        <div style="margin-bottom: 20px;">
            <div style="display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap;">
                <span class="fv-badge fv-badge-cyan">Inference Console</span>
                <span class="fv-badge fv-badge-teal">Live Multi-Model Pipeline</span>
            </div>
            <h1 style="color: #e0fdff; font-size: 2.2rem; font-weight: 700; margin: 0 0 8px 0;">
                Fish Recognition Workspace
            </h1>
            <p style="color: #849495; font-size: 0.95rem; margin: 0;">
                Upload specimen imagery to execute concurrent 5-model vision inference, evaluate top-5 probability spreads, and audit model consensus.
            </p>
        </div>
        """
    )

    col_left, col_right = st.columns([1, 1.35], gap="large")

    # Left Column: Upload & Specimen Viewport
    with col_left:
        with st.container(border=True, key="upload_card"):
            st.subheader("Input Marine Specimen")

            uploaded_file = st.file_uploader(
                f"Select Fish Image (JPG, PNG, WEBP, BMP · Max {MAX_UPLOAD_MB} MB)",
                type=["jpg", "jpeg", "png", "webp", "bmp"],
                key="workspace_uploader",
            )

            sample_img_path = root_dir / "data" / "sample_images" / "sample_fish.jpg"
            if sample_img_path.exists():
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    if st.button("Use Sample Specimen", type="secondary", width="stretch"):
                        st.session_state["active_sample"] = str(sample_img_path)
                        st.rerun()
                with col_s2:
                    if st.session_state.get("active_sample"):
                        if st.button("Clear Sample", width="stretch"):
                            del st.session_state["active_sample"]
                            st.rerun()

            staged_image = None
            img_bytes = None
            img_filename = "specimen.jpg"
            img_mime = "image/jpeg"
            upload_error = None

            if uploaded_file is not None:
                raw_bytes = uploaded_file.getvalue()
                if len(raw_bytes) > MAX_UPLOAD_BYTES:
                    upload_error = (
                        f"File '{uploaded_file.name}' is {len(raw_bytes) / (1024 * 1024):.2f} MB. "
                        f"Maximum allowed size is {MAX_UPLOAD_MB} MB."
                    )
                else:
                    try:
                        img = Image.open(BytesIO(raw_bytes))
                        img.verify()
                        staged_image = Image.open(BytesIO(raw_bytes)).convert("RGB")
                        img_bytes = raw_bytes
                        img_filename = uploaded_file.name
                        img_mime = uploaded_file.type or "image/jpeg"
                    except (UnidentifiedImageError, OSError, Exception) as exc:
                        upload_error = f"Invalid or corrupted image file: {exc}"
            elif st.session_state.get("active_sample"):
                sample_p = Path(st.session_state["active_sample"])
                if sample_p.exists():
                    try:
                        raw_bytes = sample_p.read_bytes()
                        staged_image = Image.open(BytesIO(raw_bytes)).convert("RGB")
                        img_bytes = raw_bytes
                        img_filename = sample_p.name
                        img_mime = "image/jpeg"
                    except Exception as exc:
                        upload_error = f"Unable to load sample image: {exc}"

            if upload_error:
                st.error(upload_error)

            if staged_image is not None and img_bytes is not None:
                st.image(
                    staged_image,
                    caption=f"Specimen Preview: {img_filename}",
                    width="stretch",
                )

                if st.button("Analyze Fish Specimen", type="primary", width="stretch"):
                    with st.spinner(
                        "Executing multi-model inference pipeline (DINOv2, ViT-B/16, ConvNeXt, Swin, MobileNetV3)..."
                    ):
                        try:
                            resp = requests.post(
                                f"{api_url}/predict",
                                files={"file": (img_filename, img_bytes, img_mime)},
                                timeout=900,
                            )
                            if resp.status_code >= 400:
                                detail = resp.json().get("detail", resp.text) if "application/json" in resp.headers.get("content-type", "") else resp.text
                                st.error(f"Backend rejected request ({resp.status_code}): {detail}")
                            else:
                                result_data = resp.json()
                                st.session_state["active_prediction"] = result_data

                                if "prediction_history" not in st.session_state:
                                    st.session_state["prediction_history"] = []

                                results = result_data["results"]
                                dinov2_res = next(
                                    (r for r in results if r["model"] == "DINOv2"),
                                    results[0],
                                )
                                pred_species = dinov2_res["prediction"]
                                pred_conf = dinov2_res["confidence"]

                                agree_count = sum(
                                    1 for r in results if r["prediction"] == pred_species
                                )
                                consensus_pct = (agree_count / len(results)) * 100
                                status_str = (
                                    "Full Consensus"
                                    if agree_count == 5
                                    else ("High Agreement" if agree_count >= 3 else "Model Disagreement")
                                )

                                meta = species_catalog.get(pred_species, {})
                                sci_name = meta.get("scientific_name", "Information not available")

                                history_entry = {
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "filename": img_filename,
                                    "predicted_species": pred_species,
                                    "scientific_name": sci_name,
                                    "confidence": pred_conf,
                                    "consensus_pct": consensus_pct,
                                    "agreement_status": status_str,
                                    "agree_count": agree_count,
                                    "total_models": len(results),
                                    "all_models": results,
                                }
                                st.session_state["prediction_history"].append(history_entry)
                                st.success("Analysis complete across all 5 models!")
                        except requests.exceptions.ConnectionError:
                            st.error("Could not connect to FastAPI backend on port 8000. Verify run.bat or backend server status.")
                        except Exception as exc:
                            st.error(f"Inference pipeline failed: {exc}")
            elif not upload_error:
                st.html(
                    """
                    <div style="background: #0b1322; border: 1px dashed #2d3545; border-radius: 8px; padding: 36px 16px; text-align: center; margin-top: 8px;">
                        <span class="material-symbols-outlined" style="font-size: 40px; color: #849495; display: block; margin-bottom: 8px;">cloud_upload</span>
                        <span style="color: #dbe2f8; font-weight: 500; font-size: 0.9rem;">Drag and drop or select an image to stage specimen</span>
                    </div>
                    """
                )

    # Right Column: Prediction Results & Model Comparison Matrix
    with col_right:
        active_prediction = st.session_state.get("active_prediction")
        if active_prediction and active_prediction.get("results"):
            results = active_prediction["results"]
            dino = next((r for r in results if r["model"] == "DINOv2"), results[0])
            pred_species = dino["prediction"]
            pred_conf = float(dino["confidence"])

            agree_count = sum(1 for r in results if r["prediction"] == pred_species)
            consensus_pct = (agree_count / len(results)) * 100

            meta = species_catalog.get(pred_species, {})
            common_name = meta.get("common_name", pred_species)
            sci_name = meta.get("scientific_name", "Information not available")

            _render_result_header(
                common_name=common_name,
                sci_name=sci_name,
                pred_conf=pred_conf,
                agree_count=agree_count,
                total_models=len(results),
                consensus_pct=consensus_pct,
            )

            if agree_count <= 2:
                st.warning(
                    "Significant model disagreement detected. Different architectures predicted different species; manual taxonomic verification is recommended.",
                    title="Model Disagreement Warning",
                )

            res_tab1, res_tab2, res_tab3 = st.tabs(
                [
                    "Five-Model Comparison",
                    "Top-5 Predictions (DINOv2)",
                    "Species Taxonomy & Biology",
                ]
            )

            with res_tab1:
                st.markdown("#### Live Architecture Output Comparison")
                _render_model_cards(results, pred_species)

                comp_rows = []
                for r in results:
                    is_match = r["prediction"] == pred_species
                    comp_rows.append(
                        {
                            "Model Architecture": r["model"],
                            "Predicted Taxon": r["prediction"],
                            "Softmax Confidence (%)": round(float(r["confidence"]), 2),
                            "Consensus": "Agrees" if is_match else "Disagrees",
                        }
                    )
                st.dataframe(pd.DataFrame(comp_rows), hide_index=True, width="stretch")
                st.caption(
                    "Note: Softmax confidence reflects raw model activations for this image, not calibrated probabilities or cross-model probability equivalence."
                )

            with res_tab2:
                st.markdown("#### DINOv2 Top-5 Predicted Distribution")
                for i, item in enumerate(dino.get("top5", []), 1):
                    c_name = str(item["species"])
                    c_conf = float(item["confidence"])
                    col_lbl, col_val = st.columns([3, 1])
                    with col_lbl:
                        st.markdown(f"**{i}. {c_name}**" if i == 1 else f"{i}. {c_name}")
                    with col_val:
                        st.markdown(f"`{c_conf:.2f}%`")
                    st.progress(min(max(c_conf / 100.0, 0.0), 1.0))

            with res_tab3:
                st.markdown("#### Biological Taxonomy & Ecology")
                _render_species_cards(meta)
        else:
            st.html(
                """
                <div class="fv-card" style="text-align: center; padding: 54px 24px; min-height: 400px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                    <span class="material-symbols-outlined" style="font-size: 52px; color: #2d3545; display: block; margin-bottom: 16px;">search_insights</span>
                    <h3 style="color: #dbe2f8; margin: 0 0 8px 0; font-size: 1.3rem;">Awaiting Specimen Input</h3>
                    <p style="color: #849495; max-width: 440px; margin: 0; font-size: 0.9rem; line-height: 1.5;">
                        Upload an image or click "Use Sample Specimen" on the left, then trigger "Analyze Fish Specimen" to initiate the 5-model deep learning inference matrix.
                    </p>
                </div>
                """
            )
