"""
Investiqo — Build the right stack without the guesswork.
ICMEC Ishango Hackathon 2026
"""

import streamlit as st

st.set_page_config(page_title="Investiqo", page_icon="🔍", layout="wide")

search_page = st.Page("pages/search.py", title="Find Tools", icon="🔍", default=True)
detail_page = st.Page("pages/detail.py", title="Tool Details", icon="🔍")

nav = st.navigation([search_page, detail_page], position="hidden")
nav.run()
