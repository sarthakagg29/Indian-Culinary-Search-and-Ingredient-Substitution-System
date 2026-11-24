# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""New Features Coming page: edit the ROADMAP list to add or change cards."""
import streamlit as st

from ui_common import GREEN, P_SEARCH, SAFFRON, go_page


ROADMAP = [
    ("Next up", "🧬", "FlavorDB compounds",
     "The plan was FlavorDB. We used Ahn et al. data for now; a FlavorDB loader would give more ingredients real compound scores."),
    ("Next up", "🔤", "Smarter spelling",
     "Sound-based matching so jira, zira and lasan find jeera and lahsun."),
    ("Next up", "🚩", "Report a wrong match",
     "One click to tell us when a search or a swap looks wrong."),
    ("Planned", "🍽️", "Several missing ingredients at once",
     "Pick replacements that suit each other and respect what is in your kitchen."),
    ("Planned", "🌿", "More Ayurvedic qualities",
     "Heavy or light, hot or cold: more labels to break the many ties between label-based swaps."),
    ("Planned", "🥛", "Diet filters",
     "Vegan, dairy-free, nut-free and gluten-free swaps only."),
    ("Idea", "⚖️", "Quantity guide",
     "“1 cup ghee = how much oil?” with ready conversions."),
    ("Idea", "🗣️", "Regional names",
     "Marathi, Gujarati, Tamil, Bengali and more."),
    ("Idea", "📋", "Paste a whole recipe",
     "Paste the ingredient list and get swaps for everything you are missing."),
]


def render():
    st.title("🚀 New features coming")
    st.caption("What we are working on next. Order can change.")
    status = st.pills("Show", ["All", "Next up", "Planned", "Idea"], default="All", selection_mode="single") or "All"
    items = [r for r in ROADMAP if status in ("All", r[0])]
    colour = {"Next up": GREEN, "Planned": SAFFRON, "Idea": "#7A7A7A"}
    for row_start in range(0, len(items), 3):
        cols = st.columns(3)
        for col, (state, icon, title, text) in zip(cols, items[row_start:row_start + 3]):
            with col.container(border=True):
                st.markdown(f"<span class='badge' style='background:{colour[state]}22;color:{colour[state]}'>{state}</span>",
                            unsafe_allow_html=True)
                st.markdown(f"### {icon} {title}")
                st.write(text)
    st.divider()
    st.button("← Back to search", on_click=go_page, args=(P_SEARCH,))
