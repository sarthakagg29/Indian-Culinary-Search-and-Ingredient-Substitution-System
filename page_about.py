# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""About page: static text."""
import streamlit as st


def render():
    st.title("ℹ️ About")
    st.markdown("""
**CGAS** helps you find ingredients across languages and spellings, and suggests what can replace them.

| Part | What it does | Status in this app |
|---|---|---|
| Deliverable 1 | Dataset of 250 Indian ingredients (Hindi, English, Roman spellings, taste, aroma, scientific name) | Live |
| Deliverable 2 | Multi-language search with typo handling | Live |
| Deliverable 3 | Shared-flavour overlap score and substitute ranking | Live (uses Ahn et al. compound data, not FlavorDB) |
| Deliverable 4 | This web app | Live |

**How the search treats your words:** it tries an exact name first, then names that start with what you typed,
then the closest spelling. The label next to each result tells you which one happened.

**How a score is made:** for two ingredients we count the flavour compounds they share (Jaccard overlap, or IDF-weighted
so rare compounds count more). Ingredients without compound data are scored on shared smell and taste labels instead,
which is marked **weaker**. The higher of the two scores is used. A high score means similar flavour chemistry or labels,
not a guarantee the dish will taste right.

**Known swaps** are hand-picked by the team and shown first; the percentage next to them is still the computed score.

**Data sources:** flavour compounds from Ahn, Ahnert, Bagrow and Barabási, *Flavor network and the principles of food pairing*,
Scientific Reports 1:196 (2011). Smell and taste labels from Deliverable 1.

**Team:** Sarthak Aggarwal (MT26139) · Divyanshu Joshi (MT26120) · Group 26, Computational Gastronomy.
""")
