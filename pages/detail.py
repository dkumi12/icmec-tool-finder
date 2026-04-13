"""
Tool Detail Page — ICMEC Tool Finder
Displays full information for a selected tool with score breakdown.
"""

import streamlit as st

# ── Check if a tool was selected ─────────────────────────────────────────────

if "selected_tool" not in st.session_state or st.session_state.selected_tool is None:
    st.warning("No tool selected. Please go back and choose a tool from the results.")
    if st.button("← Back to Search"):
        st.switch_page("pages/search.py")
    st.stop()

tool = st.session_state.selected_tool
reasons = st.session_state.get("selected_reasons", [])
score = st.session_state.get("selected_score", 0)

name = (tool.get("tool_name") or "Unknown").strip()
vendor = tool.get("vendor", "").strip()
url = tool.get("url", "")

# ── Header ───────────────────────────────────────────────────────────────────

col_back, _ = st.columns([1, 4])
with col_back:
    if st.button("← Back to Results"):
        st.switch_page("pages/search.py")

st.markdown(f"# {name}")
if vendor:
    st.markdown(f"*{vendor}*")

st.divider()

# ── Score & Why Recommended ──────────────────────────────────────────────────

if score or reasons:
    score_col, reason_col = st.columns([1, 3])

    with score_col:
        st.markdown("##### Relevance Score")
        if score >= 12:
            st.success(f"### {score} / 17 pts")
        elif score >= 6:
            st.warning(f"### {score} / 17 pts")
        else:
            st.error(f"### {score} / 17 pts")

    with reason_col:
        st.markdown("##### Why This Tool Was Recommended")
        for reason in reasons:
            if reason.startswith("⚠"):
                st.warning(reason)
            else:
                st.markdown(f"✓ {reason}")

    st.divider()

# ── Quick Overview (2-column grid) ───────────────────────────────────────────

st.markdown("### Overview")

left, right = st.columns(2)

with left:
    st.markdown("**Cost & Licensing**")
    st.write(tool.get("cost_and_licensing", "N/A"))

    st.markdown("**Skill Level Required**")
    st.write(tool.get("skill_level", "N/A"))

    st.markdown("**Platform & Integration**")
    st.write(tool.get("platform_and_integration", "N/A"))

with right:
    st.markdown("**Access Restrictions**")
    st.write(tool.get("access_restrictions", "N/A"))

    st.markdown("**Last Verified**")
    st.write(tool.get("last_verified", "N/A"))

    if url:
        st.markdown("**Official Website**")
        st.link_button("Visit Website", url)

st.divider()

# ── Capabilities ─────────────────────────────────────────────────────────────

tags = tool.get("capability_tags", [])
if tags:
    st.markdown("### Capabilities")
    # Display as columns of chips for readability
    cols = st.columns(4)
    for i, tag in enumerate(tags):
        cols[i % 4].code(tag.replace("_", " "))

    st.divider()

# ── Legal & Admissibility ────────────────────────────────────────────────────

legality = tool.get("jurisdictional_legality", "")
admissibility = tool.get("evidentiary_admissibility", "")

if legality or admissibility:
    st.markdown("### Legal & Evidentiary Context")

    if legality:
        st.markdown("**Jurisdictional Legality**")
        st.write(legality)

    if admissibility:
        st.markdown("**Evidentiary Admissibility**")
        st.write(admissibility)

    st.divider()

# ── Documentation & Support ──────────────────────────────────────────────────

docs = tool.get("documentation_and_support", "")
if docs:
    st.markdown("### Documentation & Support")
    st.write(docs)
    st.divider()

# ── Additional Metadata ──────────────────────────────────────────────────────

meta = tool.get("additional_metadata")
if meta and isinstance(meta, dict) and meta:
    st.markdown("### Additional Information")
    for key, value in meta.items():
        # Clean up the key for display
        display_key = key.replace("_", " ").title()
        st.markdown(f"**{display_key}**")
        st.write(value)
