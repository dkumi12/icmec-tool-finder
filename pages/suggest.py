"""
Suggest a Tool Page — ICMEC Tool Finder
Allows users to suggest tools not yet in the database.
"""

import streamlit as st

st.markdown("# Suggest a Tool")
st.markdown("*Know a tool that should be in our database? Let us know.*")
st.divider()

_, form_col, _ = st.columns([1, 2, 1])

with form_col:
    with st.form("suggest_tool_form", clear_on_submit=True):
        tool_name = st.text_input("Tool Name *", placeholder="e.g. Maltego")
        vendor = st.text_input("Vendor / Developer", placeholder="e.g. Paterva")
        tool_url = st.text_input("Website URL", placeholder="https://...")
        description = st.text_area(
            "Brief Description *",
            placeholder="What does this tool do? What type of investigation is it used for?",
            height=120,
        )
        category = st.selectbox(
            "Primary Category",
            options=[
                "Digital Forensics",
                "OSINT",
                "CSAM Detection",
                "Crypto Tracing",
                "Mobile Forensics",
                "Network Forensics",
                "Social Media Intelligence",
                "Other",
            ],
        )
        submitted = st.form_submit_button("Submit Suggestion", type="primary", use_container_width=True)

    if submitted:
        if not tool_name or not description:
            st.warning("Please fill in at least the tool name and description.")
        else:
            st.success(
                f"Thank you! **{tool_name}** has been submitted for review. "
                "Our team will evaluate it for inclusion in the database."
            )
            # In a production system this would write to a database or send an email.
            # For the prototype, we acknowledge the submission.

st.divider()

col_back, _ = st.columns([1, 4])
with col_back:
    if st.button("← Back to Search"):
        st.switch_page("pages/search.py")
