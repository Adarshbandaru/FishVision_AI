import streamlit as st


def render_about():
    st.html(
        """
        <div style="margin-bottom: 24px;">
            <div style="display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap;">
                <span class="fv-badge fv-badge-cyan">Academic Documentation</span>
                <span class="fv-badge fv-badge-teal">Ichthyology &amp; Computer Vision</span>
            </div>
            <h1 style="color: #e0fdff; font-size: 2.2rem; font-weight: 700; margin: 0 0 8px 0;">
                About Project &amp; Scientific Methodology
            </h1>
            <p style="color: #849495; font-size: 0.95rem; margin: 0;">
                Architectural principles, dataset curation guidelines, and research limits of the FishVision AI platform.
            </p>
        </div>
        <div class="fv-card">
            <h3 style="color: #00f2fe; margin-top: 0;">1. Project Overview &amp; Scientific Motivation</h3>
            <p style="color: #dbe2f8; line-height: 1.6; font-size: 0.95rem;">
                Fine-grained marine organism recognition poses severe challenges for automated ecological monitoring due to underwater turbidity,
                light attenuation, color shifting, posture variance, and strong intra-genus morphological similarities.
                FishVision AI addresses these challenges by orchestrating a 5-model deep learning benchmark matrix comparing
                large foundation vision transformers with lightweight edge-deployable convolutional networks across 152 marine fish classes.
            </p>
        </div>
        <div class="fv-card">
            <h3 style="color: #00f2fe; margin-top: 0;">2. Dataset Specifications &amp; Split Integrity</h3>
            <p style="color: #dbe2f8; line-height: 1.6; font-size: 0.95rem;">
                The research corpus aggregates <strong>22,741 curated images</strong> partitioned into strictly quarantined splits to prevent data leakage:
            </p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 16px 0;">
                <div style="background: #0b1322; border-left: 3px solid #00f2fe; padding: 12px; border-radius: 0 6px 6px 0;">
                    <div style="color: #849495; font-size: 0.75rem;">TRAINING SET</div>
                    <div style="color: #e0fdff; font-size: 1.2rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">15,305 (67.3%)</div>
                    <div style="color: #849495; font-size: 0.8rem;">Supervised model tuning</div>
                </div>
                <div style="background: #0b1322; border-left: 3px solid #47efd6; padding: 12px; border-radius: 0 6px 6px 0;">
                    <div style="color: #849495; font-size: 0.75rem;">VALIDATION SET</div>
                    <div style="color: #e0fdff; font-size: 1.2rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">4,127 (18.1%)</div>
                    <div style="color: #849495; font-size: 0.8rem;">Checkpoint selection</div>
                </div>
                <div style="background: #0b1322; border-left: 3px solid #fbbf24; padding: 12px; border-radius: 0 6px 6px 0;">
                    <div style="color: #849495; font-size: 0.75rem;">HELD-OUT TEST SET</div>
                    <div style="color: #e0fdff; font-size: 1.2rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">3,309 (14.6%)</div>
                    <div style="color: #849495; font-size: 0.8rem;">Frozen verified evaluation</div>
                </div>
            </div>
        </div>
        <div class="fv-card">
            <h3 style="color: #00f2fe; margin-top: 0;">3. Evaluated Model Architectures</h3>
            <ul style="color: #dbe2f8; line-height: 1.7; font-size: 0.95rem; margin-bottom: 0;">
                <li><strong>DINOv2 (ViT-Base / 14 Reg4):</strong> Self-supervised foundation vision transformer operating at high spatial resolution (518x518). Employs 4 register tokens to eliminate feature artifacts and maintain global semantic focus. Top performer at 93.90% accuracy.</li>
                <li><strong>ViT-B/16:</strong> Canonical Vision Transformer with 16x16 patch projection at 224x224. Delivers 88.33% accuracy with excellent macro-F1.</li>
                <li><strong>ConvNeXt Tiny:</strong> Modernized pure convolutional architecture adopting Vision Transformer design principles (7x7 depthwise convolutions, inverted bottlenecks). Robust 87.40% accuracy.</li>
                <li><strong>Swin Tiny:</strong> Hierarchical Vision Transformer using shifted window self-attention for linear computational scaling with image size. Achieves 85.13% accuracy.</li>
                <li><strong>MobileNetV3 Large:</strong> Ultra-lightweight edge neural network optimized with hardware-aware NAS and NetAdapt. Serves as our mobile/low-power reference baseline (70.32% accuracy).</li>
            </ul>
        </div>
        <div class="fv-card">
            <h3 style="color: #00f2fe; margin-top: 0;">4. Research Limitations &amp; Confidence Calibration Note</h3>
            <p style="color: #dbe2f8; line-height: 1.6; font-size: 0.95rem; margin-bottom: 0;">
                <strong>Important Scientific Caveat:</strong> Softmax output scores represent normalized exponential logits and should <em>not</em> be
                treated as calibrated Bayesian probabilities. High softmax confidence does not eliminate the risk of out-of-distribution error.
                Furthermore, the research corpus reflects a composite mixture of wild underwater photography, research vessel trawls, and laboratory
                specimens, and performance on novel marine geographies may differ from reported benchmark figures.
            </p>
        </div>
        """
    )
