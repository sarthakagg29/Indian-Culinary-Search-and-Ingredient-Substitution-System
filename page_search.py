# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Main page: the search bar.  Uses the Deliverable 2 search; shows replacements via page_substitutes."""
import streamlit as st

from page_substitutes import render_substitutes
from ui_common import get_engine, label, set_query

EXAMPLES = ["ghee", "jeera", "जीरा", "zeera", "curd", "sugar", "haldi"]
MAX_TERMS = 5


def _banner(match):
    kind = match["match_type"]
    text = {"exact": "Exact match", "prefix": "Starts-with match",
            "fuzzy": "Closest guess (spelling is different)"}[kind]
    st.markdown(f"<span class='badge {kind}'>{text}</span> &nbsp; matched on "
                f"<b>{match['matched_name']}</b> · confidence {match['score']:.0%}", unsafe_allow_html=True)
    if kind == "fuzzy":
        st.caption("We are guessing from similar spelling. If this is not the ingredient you meant, "
                   "pick another one from the list above.")


def _log_search(term, matches):
    """Remember each distinct search once, for the Analysis page."""
    key = term.lower()
    if st.session_state["last_logged"] == key and st.session_state["search_log"]:
        return
    st.session_state["last_logged"] = key
    top = matches[0] if matches else None
    st.session_state["search_log"].append({
        "searched": term,
        "found": top["english_name"] if top else "(no match)",
        "match type": top["match_type"] if top else "none",
        "confidence": round(top["score"], 2) if top else 0.0})


def render():
    engine = get_engine()
    st.markdown("<div class='hero'><h1>Out of an ingredient? Find a replacement.</h1>"
                "<p>Type it in English, Hindi or Roman spelling. Typos are fine.</p></div>",
                unsafe_allow_html=True)

    st.markdown("<div class='search-label'>Name the ingredients you want to replace</div>", unsafe_allow_html=True)
    query = st.text_input("Name the ingredients you want to replace", key="query", label_visibility="collapsed",
                          placeholder="e.g.  ghee   ·   jeera   ·   जीरा   ·   ghee, sugar",
                          help="Press Enter to search. Separate several ingredients with commas.")

    cols = st.columns(len(EXAMPLES) + 1, vertical_alignment="center")
    cols[0].caption("Try:")
    for col, example in zip(cols[1:], EXAMPLES):
        col.button(example, key=f"ex_{example}", on_click=set_query, args=(example,), width="stretch")

    terms = []
    for raw in query.replace(";", ",").replace("\n", ",").split(","):
        raw = raw.strip()
        if raw and raw.lower() not in [t.lower() for t in terms]:
            terms.append(raw)
    if not terms:
        st.markdown("###### How it works")
        a, b, c = st.columns(3)
        a.markdown("**1. Type**  \nAny name or spelling: *ghee*, *zeera*, *जीरा*.")
        b.markdown("**2. We find it**  \nSpelling mistakes and Hindi script are handled.")
        c.markdown("**3. Pick a swap**  \nSee replacements ranked by how well the flavour matches.")
        return
    if len(terms) > MAX_TERMS:
        st.warning(f"Showing the first {MAX_TERMS} ingredients only.")
        terms = terms[:MAX_TERMS]

    for n, term in enumerate(terms):
        st.divider()
        matches = engine.search(term, top_k=5)
        _log_search(term, matches)
        if not matches:
            st.error(f"No match for **{term}**.")
            hints = engine.suggest(term[:2]) if len(term) >= 2 else []
            st.caption("Try the English name, a different spelling, or Hindi script."
                       + (f" Names starting with “{term[:2]}”: {', '.join(hints)}." if hints else ""))
            continue

        chosen = matches[0]
        if len(matches) > 1:
            by_index = {m["index"]: m for m in matches}
            pick = st.selectbox(
                f"Matches for “{term}”", list(by_index), key=f"pick_{n}_{term}",
                format_func=lambda i: f"{label(i)}   ·   {by_index[i]['match_type']} {by_index[i]['score']:.0%}",
                help="Best match is first. Choose another if the top one is not what you meant.")
            chosen = by_index[pick]
        _banner(chosen)
        render_substitutes(n, chosen["index"], st.session_state.get("top_n", 5))
