# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""About page: team first, then how the system works.  Photos are read from the team/ folder if present."""
from pathlib import Path

import streamlit as st

TEAM_DIR = Path(__file__).parent / "team"
PEOPLE = [
    {"name": "Sarthak Aggarwal", "roll": "MT26139", "photo": "sarthak"},
    {"name": "Divyanshu Joshi", "roll": "MT26120", "photo": "divyanshu"},
]


def _photo(person):
    """Show team/<name>.jpg (or .jpeg/.png) if it exists, otherwise a round badge with the initials."""
    for ext in (".jpg", ".jpeg", ".png"):
        path = TEAM_DIR / (person["photo"] + ext)
        if path.exists():
            st.image(str(path), width=170)
            return
    initials = "".join(w[0] for w in person["name"].split())
    st.markdown(f"<div style='width:130px;height:130px;border-radius:50%;background:#E07A1F;color:#fff;"
                f"display:flex;align-items:center;justify-content:center;font-size:2.6rem;font-weight:700'>"
                f"{initials}</div>", unsafe_allow_html=True)


def render():
    st.title("About")

    st.subheader("Team")
    for col, person in zip(st.columns(2), PEOPLE):
        with col, st.container(border=True):
            _photo(person)
            st.markdown(f"**{person['name']}**  \n{person['roll']}  \nMTech CSE (2026-2028), IIIT Delhi")
    st.caption("We are Computational Gastronomy students (BIO544, Group 26), working under the guidance of Dr Ganesh Bagler.")

    st.markdown("""
**Indian Culinary Search and Ingredient Substitution System** helps you find ingredients across languages and
spellings, and suggests what can replace them.

**How the search treats your words:** it tries an exact name first, then names that start with what you typed,
then the closest spelling. The label next to each result tells you which one happened.

**How a score is made:** for two ingredients we count the flavour compounds they share (Jaccard overlap, or IDF-weighted
so rare compounds count more). Ingredients without compound data are scored on shared smell and taste labels instead,
which is marked **weaker**. The higher of the two scores is used. A high score means similar flavour chemistry or labels,
not a guarantee the dish will taste right.

**Known swaps** are hand-picked by the team and shown first; the percentage next to them is still the computed score.

**Data sources:** flavour compounds from Ahn, Ahnert, Bagrow and Barabási, *Flavor network and the principles of food pairing*,
Scientific Reports 1:196 (2011). Smell and taste labels from Deliverable 1.
""")
