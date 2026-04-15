"""
Tool Detail Page — ICMEC Tool Finder
Displays full information for a selected tool with score breakdown.
"""

import pathlib

import streamlit as st
from streamlit_feedback import streamlit_feedback
from scoring.normalise import parse_coding_requirement, parse_languages
from scoring.ratings import (
    get_investigator_tool_rating,
    get_tool_rating_summary,
    submit_rating,
)

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

# ── Deprecation / Change Warning ─────────────────────────────────────────────

_tool_status = (tool.get("status") or "active").lower()
if _tool_status == "deprecated":
    st.error("⚠️ This tool has been deprecated or is no longer maintained. Verify availability before use.")
elif _tool_status == "unverified":
    st.warning("⚠️ This tool's information may be outdated. Last verified: " + tool.get("last_verified", "unknown"))

st.divider()

# ── Score & Why Recommended ──────────────────────────────────────────────────

if score or reasons:
    score_col, reason_col = st.columns([1, 3])

    with score_col:
        st.markdown("##### Relevance Score")
        if score >= 70:
            st.success(f"### {score}%")
        elif score >= 40:
            st.warning(f"### {score}%")
        else:
            st.error(f"### {score}%")

    with reason_col:
        st.markdown("##### Why This Tool Was Recommended")
        for reason in reasons:
            if reason.startswith("⚠"):
                st.warning(reason)
            else:
                st.markdown(f"✓ {reason}")

    st.divider()

# ── Community Ratings ────────────────────────────────────────────────────────

st.markdown("### Community Rating")
if "investigator_name" not in st.session_state:
    st.session_state.investigator_name = ""

rating_col, submit_col = st.columns([2, 3])
with rating_col:
    avg_rating, rating_count = get_tool_rating_summary(name)
    if avg_rating is None:
        st.caption("No ratings yet — be the first.")
    else:
        stars = "⭐" * round(avg_rating)
        st.markdown(f"{stars} **{avg_rating} / 5**")
        st.caption(f"Rated by {rating_count} investigator submission(s)")

with submit_col:
    st.info("Used only to track your tool ratings. You can use an anonymous alias (for example: Anonymous-01).")
    investigator = st.text_input(
        "Name or alias for ratings only",
        key=f"investigator_for_{name}",
        value=st.session_state.investigator_name,
        placeholder="e.g. Anonymous-01",
    )
    st.session_state.investigator_name = investigator

    if investigator.strip():
        existing_rating = get_investigator_tool_rating(name, investigator)
        if existing_rating is not None:
            st.caption(f"Your latest rating: {existing_rating} / 5")
        user_star = st.feedback("stars", key=f"rating_{name}_{investigator.strip().lower()}")
        if user_star is not None:
            saved = submit_rating(
                tool_name=name,
                investigator=investigator,
                stars=user_star + 1,
                source="detail_page",
            )
            if saved:
                st.toast("Rating submitted — thank you!", icon="⭐")
                st.rerun()
    else:
        st.caption("Enter your name/alias to submit a rating.")

st.divider()

# ── Quick Overview (2-column grid) ───────────────────────────────────────────

# ── Coding / Language indicators (shared with scoring filters) ──────────────

_coding_requirement = parse_coding_requirement(tool)
_languages = parse_languages(tool)

st.markdown("### Overview")

left, right = st.columns(2)

with left:
    st.markdown("**Cost & Licensing**")
    st.write(tool.get("cost_and_licensing", "N/A"))

    st.markdown("**Technical Skill Level Required**")
    st.write(tool.get("skill_level", "N/A"))

    st.markdown("**Platform & Integration**")
    st.write(tool.get("platform_and_integration", "N/A"))

with right:
    st.markdown("**Access Restrictions**")
    st.write(tool.get("access_restrictions", "N/A"))

    st.markdown("**Last Verified**")
    st.write(tool.get("last_verified", "N/A"))

    st.markdown("**Languages**")
    st.write(", ".join(sorted(_languages)))

    st.markdown("**Requires Coding Skills**")
    if _coding_requirement == "requires_coding":
        st.write("Yes — likely requires API/CLI/developer workflow")
    elif _coding_requirement == "optional_coding":
        st.write("Optional — GUI/web available, with coding integrations")
    else:
        st.write("No — generally GUI/web-based")

    if url:
        st.markdown("**Official Website**")
        st.link_button("Visit Website", url)

st.divider()

# ── Contact & Licensing ──────────────────────────────────────────────────────

st.markdown("### Contact & Licensing")

cl_left, cl_right = st.columns(2)

with cl_left:
    st.markdown("**Licensing Model**")
    st.write(tool.get("cost_and_licensing", "N/A"))

    if url:
        st.markdown("**Vendor Website**")
        st.link_button(f"Visit {vendor or 'Website'}", url)

with cl_right:
    st.markdown("**Access Requirements**")
    access = tool.get("access_restrictions", "N/A")
    st.write(access)

    docs_support = tool.get("documentation_and_support", "")
    if docs_support:
        st.markdown("**How to Get Started**")
        st.write(docs_support)

st.divider()

# ── Capabilities ─────────────────────────────────────────────────────────────

tags = tool.get("capability_tags", [])
if tags:
    st.markdown("### Capabilities")
    # Display as columns of chips for readability
    cols = st.columns(3)
    for i, tag in enumerate(tags):
        cols[i % 3].code(tag.replace("_", " "))

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

# ── Recommendation Feedback (Thierry Donambi) ────────────────────────────────

def handle_feedback(response):
    """Store thumbs feedback in session state."""
    if "feedback_logs" not in st.session_state:
        st.session_state.feedback_logs = []
    st.session_state.feedback_logs.append({
        "tool": name,
        "score": response["score"],
        "comment": response.get("text", "No comment"),
        "relevance_at_time": score,
    })
    st.toast(f"Feedback for {name} recorded!", icon="✅")

st.divider()
st.markdown("### Was this recommendation helpful?")
st.caption("Your feedback helps the Investiqo team improve the scoring engine.")

streamlit_feedback(
    feedback_type="thumbs",
    optional_text_label="How can we improve this recommendation?",
    on_submit=handle_feedback,
    key=f"fb_{name.replace(' ', '_')}",
)

# ── Display existing feedback for this tool ───────────────────────────────────

if "feedback_logs" in st.session_state and st.session_state.feedback_logs:
    tool_feedback = [f for f in st.session_state.feedback_logs if f["tool"] == name]
    if tool_feedback:
        st.markdown(f"### User Feedback on {name}")
        for entry in tool_feedback:
            with st.container(border=True):
                col_icon, col_text = st.columns([1, 10])
                with col_icon:
                    icon = "👍" if entry["score"] == "👍" else "👎"
                    st.markdown(f"## {icon}")
                with col_text:
                    st.markdown(f"**Comment:** {entry['comment']}")
                    st.caption(f"Relevance score at time of review: {entry['relevance_at_time']}%")

