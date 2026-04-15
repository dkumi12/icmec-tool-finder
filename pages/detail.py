"""
Tool Detail Page — ICMEC Tool Finder
Displays full information for a selected tool with score breakdown.
"""

import json
import pathlib

import streamlit as st
from scoring.normalise import parse_coding_requirement, parse_languages

# ── Ratings helpers ───────────────────────────────────────────────────────────

_RATINGS_PATH = pathlib.Path(__file__).parent.parent / "data" / "ratings.json"

def _load_ratings() -> dict:
    if _RATINGS_PATH.exists():
        return json.loads(_RATINGS_PATH.read_text(encoding="utf-8"))
    return {}

def _save_rating(tool_name: str, stars: int) -> None:
    data = _load_ratings()
    data.setdefault(tool_name, []).append(stars)
    _RATINGS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

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

# ── Community Ratings ────────────────────────────────────────────────────────

st.markdown("### Community Rating")
_all_ratings = _load_ratings()
_tool_ratings = _all_ratings.get(name, [])
_rated_key = f"has_rated_{name}"

if _tool_ratings:
    _avg = round(sum(_tool_ratings) / len(_tool_ratings), 1)
    _stars = "⭐" * round(_avg)
    rating_col, submit_col = st.columns([2, 3])
    with rating_col:
        st.markdown(f"{_stars} **{_avg} / 5**")
        st.caption(f"Rated by {len(_tool_ratings)} user(s)")
    with submit_col:
        if not st.session_state.get(_rated_key):
            _user_star = st.feedback("stars", key=f"rating_{name}")
            if _user_star is not None:
                _save_rating(name, _user_star + 1)
                st.session_state[_rated_key] = True
                st.toast("Rating submitted — thank you!", icon="⭐")
                st.rerun()
else:
    st.caption("No ratings yet — be the first.")
    if not st.session_state.get(_rated_key):
        _user_star = st.feedback("stars", key=f"rating_{name}")
        if _user_star is not None:
            _save_rating(name, _user_star + 1)
            st.session_state[_rated_key] = True
            st.toast("Rating submitted — thank you!", icon="⭐")
            st.rerun()

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

