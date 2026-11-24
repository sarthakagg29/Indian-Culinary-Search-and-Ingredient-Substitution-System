# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""
CGAS: Indian Culinary Search & Ingredient Substitution  (Deliverable 4)
=======================================================================
Entry point. Run with:   streamlit run app.py

This file only does three things: page setup, the sidebar menu, and sending you to the chosen page.
Each page is its own small file with a render() function:

    page_search.py       the search bar            (Deliverable 2 search)
    page_substitutes.py  list of replacements      (backend get_substitutes)
    page_compare.py      compare two ingredients   (backend match_details)
    page_analysis.py     charts                    (backend get_profiles)
    page_soon.py         New Features Coming
    page_about.py        About
    ui_common.py         shared helpers and colours
    backend.py           the three backend functions (uses Deliverable 3 + Deliverable 1 data)
"""
import streamlit as st

# set_page_config must be the first Streamlit call, so the other imports come after it
st.set_page_config(page_title="CGAS | Indian Ingredient Substitution", page_icon="🌿",
                   layout="wide", initial_sidebar_state="expanded")

import backend                     # noqa: E402
import page_about, page_analysis, page_compare, page_search, page_soon   # noqa: E402,E401
from ui_common import (CSS, P_ABOUT, P_ANALYSIS, P_COMPARE, P_SEARCH, P_SOON, PAGES, get_engine)  # noqa: E402

st.markdown(CSS, unsafe_allow_html=True)
get_engine()                                        # load the search once, up front
st.session_state.setdefault("search_log", [])       # searches made in this visit
st.session_state.setdefault("last_logged", "")

with st.sidebar:
    st.markdown("## 🌿 CGAS")
    st.caption("Indian Culinary Search & Ingredient Substitution")
    st.radio("Menu", PAGES, key="page", label_visibility="collapsed")
    st.divider()
    st.slider("Substitutes to show", 3, 8, 5, key="top_n",
              help="How many replacement ideas to list in each group.")
    st.selectbox("Score type", list(backend.METHODS), key="method", format_func=backend.METHODS.get,
                 help="Both measure shared flavour. IDF-weighted counts rare compounds more than common ones.")
    st.caption("Scores use flavour-compound data from Ahn et al. (2011) where an ingredient has it, otherwise "
               "smell and taste labels (marked weaker).")
    st.caption("Group 26 · Computational Gastronomy")

{P_SEARCH: page_search, P_COMPARE: page_compare, P_ANALYSIS: page_analysis,
 P_SOON: page_soon, P_ABOUT: page_about}[st.session_state["page"]].render()
