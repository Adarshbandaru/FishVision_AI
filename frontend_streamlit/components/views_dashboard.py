import streamlit as st


def render_dashboard(switch_tab_callback=None):
    st.html(
        """
        <div style="background: linear-gradient(135deg, rgba(11, 28, 54, 0.9) 0%, rgba(14, 23, 38, 0.95) 100%);
                    border: 1px solid #222a3a; border-radius: 16px; padding: 36px 40px; margin-bottom: 24px;
                    box-shadow: 0 0 35px rgba(0, 242, 254, 0.08); position: relative; overflow: hidden;">
            <div style="position: absolute; right: -20px; top: -20px; width: 220px; height: 220px;
                        background: radial-gradient(circle, rgba(0, 242, 254, 0.15) 0%, rgba(0,0,0,0) 70%);"></div>
            <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 12px; flex-wrap: wrap;">
                <span class="fv-badge fv-badge-cyan">FishVision AI Research Platform</span>
                <span class="fv-badge fv-badge-teal">Production Model Matrix v2.4</span>
            </div>
            <h1 style="font-size: 2.8rem; font-weight: 800; color: #e0fdff; line-height: 1.15; margin: 0 0 16px 0; letter-spacing: -0.02em;">
                Discover the Species <br/><span style="color: #00f2fe;">Beneath the Surface.</span>
            </h1>
            <p style="font-size: 1.05rem; color: #b9cacb; max-width: 680px; line-height: 1.6; margin: 0 0 24px 0;">
                Academic multi-architecture marine taxon classification engine. Leverages 5 vision transformers
                and deep convolutional neural networks calibrated against 152 verified ichthyological species.
            </p>
            <div style="display: flex; gap: 16px; flex-wrap: wrap;">
                <div style="background: #141c2b; border: 1px solid #2d3545; border-radius: 8px; padding: 8px 18px; display: flex; align-items: center; gap: 10px;">
                    <span style="color: #00f2fe; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 1.2rem;">93.90%</span>
                    <span style="color: #849495; font-size: 0.85rem;">Top DINOv2 Accuracy</span>
                </div>
                <div style="background: #141c2b; border: 1px solid #2d3545; border-radius: 8px; padding: 8px 18px; display: flex; align-items: center; gap: 10px;">
                    <span style="color: #47efd6; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 1.2rem;">152</span>
                    <span style="color: #849495; font-size: 0.85rem;">Marine Taxa Cataloged</span>
                </div>
                <div style="background: #141c2b; border: 1px solid #2d3545; border-radius: 8px; padding: 8px 18px; display: flex; align-items: center; gap: 10px;">
                    <span style="color: #dbe2f8; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 1.2rem;">22,741</span>
                    <span style="color: #849495; font-size: 0.85rem;">Curated Research Images</span>
                </div>
            </div>
        </div>
        """
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.html(
            """
            <div class="fv-card" style="padding: 18px; margin-bottom: 0;">
                <div style="color: #849495; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">Benchmark SOTA</div>
                <div style="color: #00f2fe; font-size: 1.8rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; margin: 4px 0;">93.90%</div>
                <div style="color: #47efd6; font-size: 0.8rem;">DINOv2 ViT-Base (518px)</div>
            </div>
            """
        )
    with c2:
        st.html(
            """
            <div class="fv-card" style="padding: 18px; margin-bottom: 0;">
                <div style="color: #849495; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">Active Ensemble</div>
                <div style="color: #47efd6; font-size: 1.8rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; margin: 4px 0;">5 Models</div>
                <div style="color: #849495; font-size: 0.8rem;">ViT, ConvNeXt, Swin, MobileNet</div>
            </div>
            """
        )
    with c3:
        st.html(
            """
            <div class="fv-card" style="padding: 18px; margin-bottom: 0;">
                <div style="color: #849495; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">Held-out Test Cohort</div>
                <div style="color: #dbe2f8; font-size: 1.8rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; margin: 4px 0;">3,309</div>
                <div style="color: #849495; font-size: 0.8rem;">Zero-data-leakage verification</div>
            </div>
            """
        )
    with c4:
        st.html(
            """
            <div class="fv-card" style="padding: 18px; margin-bottom: 0;">
                <div style="color: #849495; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">Inference Platform</div>
                <div style="color: #fbbf24; font-size: 1.8rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; margin: 4px 0;">CPU/Edge</div>
                <div style="color: #849495; font-size: 0.8rem;">FastAPI + PyTorch/timm</div>
            </div>
            """
        )

    st.write("")
    col_left, col_right = st.columns([1.2, 1])
    with col_left:
        st.html(
            """
            <div class="fv-card fv-card-glow" style="margin-bottom: 12px;">
                <h3 style="color: #e0fdff; margin-top: 0; font-size: 1.3rem;">Scientific Marine Specimen Workspace</h3>
                <p style="color: #b9cacb; font-size: 0.95rem; line-height: 1.5;">
                    Upload a raw underwater photograph, aquarium catch, or lab specimen image to run real-time inference
                    across all 5 deep neural networks with full top-5 probability distribution and taxonomy catalog retrieval.
                </p>
                <div style="margin: 20px 0 4px 0; background: #0b1322; border: 1px dashed #2d3545; border-radius: 8px; padding: 18px; text-align: center;">
                    <span class="material-symbols-outlined" style="font-size: 36px; color: #00f2fe; display: block; margin-bottom: 8px;">biotech</span>
                    <span style="color: #dbe2f8; font-weight: 600; font-size: 0.95rem;">Ready for Image Inference</span>
                    <div style="color: #849495; font-size: 0.8rem; margin-top: 4px;">Supports JPG, PNG, WEBP, BMP up to 15 MB</div>
                </div>
            </div>
            """
        )
        if st.button("Open Recognition Workspace", type="primary", width="stretch"):
            st.session_state["pending_nav"] = "Fish Recognition Workspace"
            st.rerun()

    with col_right:
        st.html(
            """
            <div class="fv-card">
                <h3 style="color: #e0fdff; margin-top: 0; font-size: 1.3rem;">Evaluated Deep Architectures</h3>
                <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #0b1322; border-radius: 6px; border-left: 3px solid #00f2fe;">
                        <div><strong style="color: #e0fdff;">DINOv2 ViT-Base</strong> <span style="color: #849495; font-size: 0.8rem;">(518x518)</span></div>
                        <span style="font-family: 'JetBrains Mono', monospace; color: #00f2fe; font-weight: 700;">93.90%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #0b1322; border-radius: 6px; border-left: 3px solid #47efd6;">
                        <div><strong style="color: #e0fdff;">ViT-B/16</strong> <span style="color: #849495; font-size: 0.8rem;">(224x224)</span></div>
                        <span style="font-family: 'JetBrains Mono', monospace; color: #47efd6; font-weight: 700;">88.33%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #0b1322; border-radius: 6px; border-left: 3px solid #38bdf8;">
                        <div><strong style="color: #e0fdff;">ConvNeXt Tiny</strong> <span style="color: #849495; font-size: 0.8rem;">(224x224)</span></div>
                        <span style="font-family: 'JetBrains Mono', monospace; color: #38bdf8; font-weight: 700;">87.40%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #0b1322; border-radius: 6px; border-left: 3px solid #a78bfa;">
                        <div><strong style="color: #e0fdff;">Swin Tiny</strong> <span style="color: #849495; font-size: 0.8rem;">(224x224)</span></div>
                        <span style="font-family: 'JetBrains Mono', monospace; color: #a78bfa; font-weight: 700;">85.13%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #0b1322; border-radius: 6px; border-left: 3px solid #fbbf24;">
                        <div><strong style="color: #e0fdff;">MobileNetV3</strong> <span style="color: #849495; font-size: 0.8rem;">(224x224)</span></div>
                        <span style="font-family: 'JetBrains Mono', monospace; color: #fbbf24; font-weight: 700;">70.32%</span>
                    </div>
                </div>
            </div>
            """
        )

    st.html(
        """
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-top: 10px;">
            <div class="fv-card" style="margin-bottom: 0;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span class="material-symbols-outlined" style="color: #00f2fe;">analytics</span>
                    <strong style="color: #e0fdff;">Benchmark &amp; Metrics Matrix</strong>
                </div>
                <p style="color: #849495; font-size: 0.85rem; margin: 0;">
                    Inspect verified Macro Precision, Recall, Macro F1, and Weighted F1 curves across all 3,309 test images.
                </p>
            </div>
            <div class="fv-card" style="margin-bottom: 0;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span class="material-symbols-outlined" style="color: #47efd6;">menu_book</span>
                    <strong style="color: #e0fdff;">Species Information Catalog</strong>
                </div>
                <p style="color: #849495; font-size: 0.85rem; margin: 0;">
                    Explore rich biological taxonomy, habitats, diet, water type, and biometrics for all 152 marine species.
                </p>
            </div>
            <div class="fv-card" style="margin-bottom: 0;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span class="material-symbols-outlined" style="color: #fbbf24;">history</span>
                    <strong style="color: #e0fdff;">Prediction Audit Log</strong>
                </div>
                <p style="color: #849495; font-size: 0.85rem; margin: 0;">
                    Review session inference history, model consensus ratios, latency logs, and export findings as JSON.
                </p>
            </div>
        </div>
        """
    )
