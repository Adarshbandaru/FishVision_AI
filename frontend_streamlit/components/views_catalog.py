from html import escape
import json
from pathlib import Path

import streamlit as st


def render_catalog(root_dir: Path):
    meta_path = root_dir / "data" / "species_metadata.json"
    if not meta_path.exists():
        st.warning("Species metadata not found. Please ensure data/species_metadata.json is generated.")
        return

    species_data = json.loads(meta_path.read_text(encoding="utf-8"))
    species_keys = sorted(list(species_data.keys()))

    st.html(
        """
        <div style="margin-bottom: 24px;">
            <div style="display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap;">
                <span class="fv-badge fv-badge-cyan">Taxonomy Catalog</span>
                <span class="fv-badge fv-badge-teal">152 Supported Species</span>
            </div>
            <h1 style="color: #e0fdff; font-size: 2.2rem; font-weight: 700; margin: 0 0 8px 0;">
                Species Information Catalog
            </h1>
            <p style="color: #849495; font-size: 0.95rem; margin: 0;">
                Comprehensive biological, morphological, and ecological metadata verified for the 152 fish taxa classes.
            </p>
        </div>
        """
    )

    c_search, c_filter = st.columns([2, 1])
    with c_search:
        search_query = st.text_input(
            "Search species by common name, scientific name, or key",
            placeholder="e.g. Bangus, Carp, Salmo, Puffer...",
        ).strip().lower()
    with c_filter:
        selected_key = st.selectbox(
            "Or choose directly from catalog list:",
            options=["(Select Species)"] + species_keys,
        )

    active_key = None
    if selected_key != "(Select Species)":
        active_key = selected_key
    elif search_query:
        matches = [
            k
            for k, v in species_data.items()
            if search_query in k.lower()
            or search_query in v.get("common_name", "").lower()
            or search_query in v.get("scientific_name", "").lower()
        ]
        if matches:
            active_key = matches[0]
            if len(matches) > 1:
                st.caption(f"Found {len(matches)} matches. Showing first match: **{matches[0]}**")
        else:
            st.info(f"No species found matching '{search_query}'. Try another term.")
    else:
        active_key = "Bangus" if "Bangus" in species_data else (species_keys[0] if species_keys else None)

    if active_key and active_key in species_data:
        spec = species_data[active_key]

        key_esc = escape(str(active_key))
        water_type = escape(str(spec.get("water_type", "Information not available")))
        common_name = escape(str(spec.get("common_name", active_key)))
        scientific_name = escape(str(spec.get("scientific_name", "Information not available")))
        conservation_status = escape(str(spec.get("conservation_status", "Information not available")))
        habitat = escape(str(spec.get("habitat", "Information not available")))
        geographic_distribution = escape(str(spec.get("geographic_distribution", "Information not available")))
        diet = escape(str(spec.get("diet", "Information not available")))
        typical_size = escape(str(spec.get("typical_size", "Information not available")))
        interesting_facts = escape(str(spec.get("interesting_facts", "Information not available")))

        st.html(
            f"""
            <div class="fv-card fv-card-glow" style="margin-top: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; margin-bottom: 20px;">
                    <div>
                        <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px; flex-wrap: wrap;">
                            <span class="fv-badge fv-badge-cyan">{key_esc}</span>
                            <span class="fv-badge fv-badge-teal">{water_type}</span>
                        </div>
                        <h2 style="color: #00f2fe; font-size: 2.2rem; font-weight: 800; margin: 0 0 4px 0;">{common_name}</h2>
                        <div style="color: #47efd6; font-style: italic; font-size: 1.15rem; font-family: Georgia, serif;">{scientific_name}</div>
                    </div>
                    <div style="background: #0b1322; border: 1px solid #222a3a; border-radius: 8px; padding: 10px 16px; text-align: right;">
                        <div style="color: #849495; font-size: 0.75rem; text-transform: uppercase;">Conservation Status</div>
                        <div style="color: #fbbf24; font-weight: 700; font-size: 0.95rem; margin-top: 2px;">{conservation_status}</div>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-bottom: 24px;">
                    <div style="background: #0b1322; border: 1px solid #1f2a3e; border-radius: 8px; padding: 14px;">
                        <div style="color: #849495; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 4px;">Habitat &amp; Bio-Zone</div>
                        <div style="color: #dbe2f8; font-size: 0.95rem; font-weight: 500;">{habitat}</div>
                    </div>
                    <div style="background: #0b1322; border: 1px solid #1f2a3e; border-radius: 8px; padding: 14px;">
                        <div style="color: #849495; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 4px;">Geographic Distribution</div>
                        <div style="color: #dbe2f8; font-size: 0.95rem; font-weight: 500;">{geographic_distribution}</div>
                    </div>
                    <div style="background: #0b1322; border: 1px solid #1f2a3e; border-radius: 8px; padding: 14px;">
                        <div style="color: #849495; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 4px;">Trophic Ecology &amp; Diet</div>
                        <div style="color: #dbe2f8; font-size: 0.95rem; font-weight: 500;">{diet}</div>
                    </div>
                    <div style="background: #0b1322; border: 1px solid #1f2a3e; border-radius: 8px; padding: 14px;">
                        <div style="color: #849495; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 4px;">Typical Adult Size</div>
                        <div style="color: #dbe2f8; font-size: 0.95rem; font-weight: 500;">{typical_size}</div>
                    </div>
                </div>
                <div style="background: linear-gradient(90deg, rgba(0, 242, 254, 0.08) 0%, rgba(71, 239, 214, 0.04) 100%);
                            border-left: 4px solid #00f2fe; border-radius: 0 8px 8px 0; padding: 16px 20px;">
                    <div style="color: #00f2fe; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">
                        Ethology &amp; Biological Adaptations
                    </div>
                    <div style="color: #dbe2f8; font-size: 0.95rem; line-height: 1.5;">
                        {interesting_facts}
                    </div>
                </div>
            </div>
            """
        )
