"""
Search Page — ICMEC Tool Finder
Main form + ranked results display.
"""

import json
import pathlib

import streamlit as st

from scoring.recommend import recommend_tools, UserQuery
from scoring.tag_maps import INVESTIGATION_TAG_MAP, INPUT_TAG_MAP
from scoring.normalise import parse_languages

# ── Data Loading ─────────────────────────────────────────────────────────────

@st.cache_data
def load_tools() -> list[dict]:
    data_path = pathlib.Path(__file__).parent.parent / "data" / "tools.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


tools = load_tools()


@st.cache_data
def get_language_options(tool_data: list[dict]) -> list[str]:
    all_langs: set[str] = set()
    for tool in tool_data:
        langs = parse_languages(tool)
        all_langs.update(lang for lang in langs if lang != "Not specified")
    return sorted(all_langs)

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
                "Your Technical Skill Level",
                options=["beginner", "intermediate", "advanced"],
                index=1,
                format_func=str.capitalize,
            )

            is_le = st.checkbox("I am Law Enforcement / Government", value=False)

        st.markdown("##### Optional Filters")
        filter_left, filter_right = st.columns(2)
        with filter_left:
            coding_requirement = st.selectbox(
                "Coding Skills Requirement",
                options=["any", "no_coding", "optional_or_no", "requires_coding"],
                format_func=lambda x: {
                    "any": "Any",
                    "no_coding": "No coding required",
                    "optional_or_no": "No coding or optional coding",
                    "requires_coding": "Requires coding / API skills",
                }[x],
                help="Use this to include only tools that match your team's coding capacity.",
            )
        with filter_right:
            language_options = get_language_options(tools)
            languages = st.multiselect(
                "Preferred Interface Language(s)",
                options=language_options + ["Any / Not specified"],
                help="Filters tools by known language support when available in the dataset.",
                placeholder="Choose languages (optional)...",
            )

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
            coding_requirement=coding_requirement,
            languages=languages,
        )
        st.session_state.results = recommend_tools(tools, query, top_n=20)
        st.session_state.show_all = False
        st.session_state.search_summary = (
            f"{', '.join(investigation_types)} · "
            f"Budget: {budget} · Skill: {skill_level} · "
            f"Coding: {coding_requirement.replace('_', ' ')}"
        )

# ── Results ──────────────────────────────────────────────────────────────────

if "show_all" not in st.session_state:
    st.session_state.show_all = False

if st.session_state.results:
    results = st.session_state.results
    display_count = len(results) if st.session_state.show_all else min(5, len(results))
    visible_results = results[:display_count]

    st.divider()
    st.markdown(f"### Top {display_count} Recommended Tools")
    st.caption(st.session_state.search_summary)

    with st.expander("How are tools scored?"):
        st.markdown("""
Each tool is scored against your case inputs using these criteria:

- **Investigation type match** — tools whose capabilities align with your selected case type score highest (up to 9 pts)
- **Budget fit** — tools within your stated budget score higher; tools outside it are penalised (+2 / −2 pts)
- **Technical skill match** — tools appropriate for your skill level score higher (+2 pts)
- **Evidence type match** — tools that handle the evidence you have available score higher (up to 3 pts)
- **Urgency** — free, publicly available tools get a bonus when you need something immediately (+1 pt)
- **Access restrictions** — tools restricted to law enforcement are penalised for non-LE users (−5 pts)
- **Optional hard filters** — coding requirement and interface language can remove non-matching tools before ranking

**Score range:** −7 to 17 points. Higher scores mean a stronger match for your case.
""")

    for rank, result in enumerate(visible_results, 1):
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
            c2.markdown(f"**Technical Skill:** {skill}")
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

    # ── Show More / Show Less ───────────────────────────────────────
    if len(results) > 5:
        _, show_col, _ = st.columns([1, 2, 1])
        with show_col:
            if not st.session_state.show_all:
                if st.button(f"Show More ({len(results) - 5} more tools)", use_container_width=True):
                    st.session_state.show_all = True
                    st.rerun()
            else:
                if st.button("Show Less", use_container_width=True):
                    st.session_state.show_all = False
                    st.rerun()

    # ── Suggest a Tool link ─────────────────────────────────────────
    st.divider()
    _, suggest_col, _ = st.columns([1, 2, 1])
    with suggest_col:
        st.markdown("Can't find what you're looking for?")
        if st.button("Suggest a Tool", use_container_width=True):
            st.switch_page("pages/suggest.py")
