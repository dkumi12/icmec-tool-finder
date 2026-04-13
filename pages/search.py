"""
Search Page — ICMEC Tool Finder
Main form + ranked results display.
"""

import json
import pathlib

import streamlit as st

from scoring.recommend import recommend_tools, UserQuery
from scoring.tag_maps import INVESTIGATION_TAG_MAP, INPUT_TAG_MAP

# ── Data Loading ─────────────────────────────────────────────────────────────

@st.cache_data
def load_tools() -> list[dict]:
    data_path = pathlib.Path(__file__).parent.parent / "data" / "tools.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


tools = load_tools()

# ── Header ───────────────────────────────────────────────────────────────────

st.title("Investiqo")
st.markdown("*Build the right stack without the guesswork.*")
st.divider()

# ── Input Form (centred, max 720px feel) ─────────────────────────────────────

_, form_col, _ = st.columns([1, 2, 1])

with form_col:
    with st.container(border=True):
        st.markdown("#### Describe Your Case")

        investigation_types = st.multiselect(
            "Investigation Type(s)",
            options=sorted(INVESTIGATION_TAG_MAP.keys()),
            help="Select one or more investigation types relevant to your case",
            placeholder="Choose investigation types...",
        )

        input_types = st.multiselect(
            "Available Evidence / Input Types",
            options=sorted(INPUT_TAG_MAP.keys()),
            help="What evidence do you have to work with?",
            placeholder="Choose evidence types...",
        )

        row1_left, row1_right = st.columns(2)
        with row1_left:
            budget = st.selectbox(
                "Budget",
                options=["free", "freemium", "paid"],
                format_func=lambda x: {
                    "free": "Free only",
                    "freemium": "Free + Freemium",
                    "paid": "Any (including paid)",
                }[x],
            )

            urgency = st.selectbox(
                "Urgency",
                options=["immediate", "days", "weeks"],
                format_func=lambda x: {
                    "immediate": "Immediate (need tools now)",
                    "days": "Days",
                    "weeks": "Weeks (can wait)",
                }[x],
            )

        with row1_right:
            skill_level = st.selectbox(
                "Your Skill Level",
                options=["beginner", "intermediate", "advanced"],
                index=1,
                format_func=str.capitalize,
            )

            is_le = st.checkbox("I am Law Enforcement / Government", value=False)

# ── Session State Init ───────────────────────────────────────────────────────

if "results" not in st.session_state:
    st.session_state.results = None
if "search_summary" not in st.session_state:
    st.session_state.search_summary = ""

# ── Submit (inside centred column) ───────────────────────────────────────────

_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    submitted = st.button("Find Recommended Tools", type="primary", use_container_width=True)

if submitted:
    if not investigation_types:
        st.warning("Please select at least one investigation type.")
    else:
        query = UserQuery(
            investigation_types=investigation_types,
            budget=budget,
            skill_level=skill_level,
            input_types=input_types,
            urgency=urgency,
            is_law_enforcement=is_le,
        )
        st.session_state.results = recommend_tools(tools, query, top_n=5)
        st.session_state.search_summary = (
            f"{', '.join(investigation_types)} · "
            f"Budget: {budget} · Skill: {skill_level}"
        )

# ── Results ──────────────────────────────────────────────────────────────────

if st.session_state.results:
    results = st.session_state.results

    st.divider()
    st.markdown(f"### Top {len(results)} Recommended Tools")
    st.caption(st.session_state.search_summary)

    for rank, result in enumerate(results, 1):
        t = result.tool
        name = (t.get("tool_name") or "Unknown").strip()
        vendor = t.get("vendor", "").strip()
        url = t.get("url", "")
        score = result.score
        cost = t.get("cost_and_licensing", "N/A")
        skill = t.get("skill_level", "N/A").split("(")[0].strip()
        platform = t.get("platform_and_integration", "N/A")
        access = t.get("access_restrictions", "N/A")

        with st.container(border=True):
            # ── Header: rank, name, vendor, score ────────
            top_left, top_right = st.columns([4, 1])
            with top_left:
                st.markdown(f"#### {rank}. {name}")
                if vendor:
                    st.caption(vendor)
            with top_right:
                if score >= 12:
                    st.success(f"**{score} pts**")
                elif score >= 6:
                    st.warning(f"**{score} pts**")
                else:
                    st.error(f"**{score} pts**")

            # ── Quick info row ───────────────────────────
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"**Cost:** {cost}")
            c2.markdown(f"**Skill:** {skill}")
            c3.markdown(f"**Platform:** {platform}")
            c4.markdown(f"**Access:** {access}")

            # ── Why this tool (match reasons) ────────────
            if result.match_reasons:
                reasons_text = " · ".join(result.match_reasons)
                st.info(reasons_text, icon="💡")

            # ── Actions ──────────────────────────────────
            btn_left, btn_right, _ = st.columns([1, 1, 3])
            with btn_left:
                if st.button("View Details", key=f"detail_{rank}"):
                    st.session_state.selected_tool = t
                    st.session_state.selected_reasons = result.match_reasons
                    st.session_state.selected_score = score
                    st.switch_page("pages/detail.py")
            with btn_right:
                if url:
                    st.link_button("Visit Website", url)
