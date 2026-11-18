from html import escape
import json

import streamlit as st


def render_history():
    st.html(
        """
        <div style="margin-bottom: 24px;">
            <div style="display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap;">
                <span class="fv-badge fv-badge-cyan">Inference Log</span>
                <span class="fv-badge fv-badge-teal">Session Audit Trail</span>
            </div>
            <h1 style="color: #e0fdff; font-size: 2.2rem; font-weight: 700; margin: 0 0 8px 0;">
                Prediction History &amp; Inference Audit Log
            </h1>
            <p style="color: #849495; font-size: 0.95rem; margin: 0;">
                Review previously analyzed specimens during this session, examine cross-model consensus rates, and export structured JSON audit batches.
            </p>
        </div>
        """
    )

    history = st.session_state.get("prediction_history", [])
    if not history:
        st.html(
            """
            <div class="fv-card" style="text-align: center; padding: 48px 24px;">
                <span class="material-symbols-outlined" style="font-size: 48px; color: #849495; display: block; margin-bottom: 12px;">history_toggle_off</span>
                <h3 style="color: #dbe2f8; margin: 0 0 8px 0;">No Inferences Recorded Yet</h3>
                <p style="color: #849495; max-width: 480px; margin: 0 auto; font-size: 0.9rem;">
                    When you upload and analyze marine specimens in the Fish Recognition Workspace, their predictions,
                    model consensus scores, and metadata will be logged here for audit.
                </p>
            </div>
            """
        )
        if st.button("Go to Fish Recognition Workspace", type="primary"):
            st.session_state["pending_nav"] = "Fish Recognition Workspace"
            st.rerun()
        return

    st.caption(f"Showing **{len(history)}** recorded specimen inferences in this active session.")

    col_actions1, col_actions2 = st.columns([1, 4])
    with col_actions1:
        if st.button("Clear Session Log", type="secondary", width="stretch"):
            st.session_state["prediction_history"] = []
            st.rerun()
    with col_actions2:
        export_json = json.dumps(history, indent=2)
        st.download_button(
            label="Export Session Audit Log (JSON)",
            data=export_json,
            file_name="fishvision_prediction_audit.json",
            mime="application/json",
        )

    st.write("")
    for idx, item in enumerate(reversed(history)):
        specimen_num = len(history) - idx
        consensus = float(item.get("consensus_pct", 100.0))
        consensus_color = (
            "#47efd6" if consensus >= 80 else ("#fbbf24" if consensus >= 50 else "#f87171")
        )
        timestamp = escape(str(item.get("timestamp", "Recent")))
        filename = escape(str(item.get("filename", "specimen")))
        agreement_status = escape(str(item.get("agreement_status", "Agreement")))
        predicted_species = escape(str(item.get("predicted_species", "Unknown")))
        scientific_name = escape(str(item.get("scientific_name", "")))
        confidence = float(item.get("confidence", 0.0))

        model_pills = []
        for m in item.get("all_models", []):
            m_name = escape(str(m.get("model", "")))
            m_pred = escape(str(m.get("prediction", "")))
            m_conf = float(m.get("confidence", 0.0))
            model_pills.append(
                f"""
                <div style="background: #0b1322; border: 1px solid #1f2a3e; border-radius: 6px; padding: 6px 10px; font-size: 0.8rem;">
                    <span style="color: #849495;">{m_name}:</span>
                    <strong style="color: #dbe2f8;">{m_pred}</strong>
                    <span style="color: #00f2fe; font-family: 'JetBrains Mono', monospace;">({m_conf:.1f}%)</span>
                </div>
                """
            )

        st.html(
            f"""
            <div class="fv-card" style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px; flex-wrap: wrap;">
                            <span class="fv-badge fv-badge-cyan">SPECIMEN #{specimen_num}</span>
                            <span style="color: #849495; font-size: 0.8rem; font-family: 'JetBrains Mono', monospace;">{timestamp}</span>
                            <span style="color: #849495; font-size: 0.8rem;">· {filename}</span>
                            <span style="color: {consensus_color}; font-size: 0.8rem; font-weight: 600;">{agreement_status} ({consensus:.0f}% Consensus)</span>
                        </div>
                        <h3 style="color: #00f2fe; margin: 0 0 2px 0; font-size: 1.4rem;">{predicted_species}</h3>
                        <div style="color: #dbe2f8; font-style: italic; font-size: 0.95rem;">{scientific_name}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #849495; font-size: 0.75rem; text-transform: uppercase;">Primary DINOv2 Softmax</div>
                        <div style="color: #00f2fe; font-family: 'JetBrains Mono', monospace; font-size: 1.5rem; font-weight: 700;">{confidence:.2f}%</div>
                    </div>
                </div>
                <div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid #1f2a3e;">
                    <div style="color: #849495; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 8px;">Individual Model Predictions:</div>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        {''.join(model_pills)}
                    </div>
                </div>
            </div>
            """
        )
