# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Main page: the search bar.  Uses the Deliverable 2 search (trie + fuzzy); shows replacements via page_substitutes.

With the streamlit-searchbox library installed, the box shows a live dropdown while you type.
Without it, the page falls back to a plain text box (press Enter to search)."""
import streamlit as st

from D2_1_normalize import normalize
from page_substitutes import render_substitutes
from ui_common import get_engine, label, set_query

try:
    from streamlit_searchbox import st_searchbox
    HAVE_SEARCHBOX = True
except ImportError:
    HAVE_SEARCHBOX = False

EXAMPLES = ["ghee", "jeera", "जीरा", "zeera", "curd", "sugar", "haldi"]
MAX_TERMS = 5
KIND = {"exact": "exact", "prefix": "starts with", "fuzzy": "closest guess"}


def _banner(match):
    kind = match["match_type"]
    text = {"exact": "Exact match", "prefix": "Starts-with match",
            "fuzzy": "Closest guess (spelling is different)"}[kind]
    st.markdown(f"<span class='badge {kind}'>{text}</span> &nbsp; matched on "
                f"<b>{match['matched_name']}</b> · confidence {match['score']:.0%}", unsafe_allow_html=True)
    if kind == "fuzzy":
        st.caption("We are guessing from similar spelling. If this is not the ingredient you meant, "
                   "search again and pick another one from the list.")


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


def _how_it_works():
    st.markdown("###### How it works")
    a, b, c = st.columns(3)
    a.markdown("**1. Type**  \nAny name or spelling: *ghee*, *zeera*, *जीरा*.")
    b.markdown("**2. We find it**  \nSpelling mistakes and Hindi script are handled.")
    c.markdown("**3. Pick a swap**  \nSee replacements ranked by how well the flavour matches.")


def _examples(on_click):
    cols = st.columns([1] + [2] * len(EXAMPLES) + [3], vertical_alignment="center", gap="xsmall")
    cols[0].caption("Try:")
    for col, example in zip(cols[1:], EXAMPLES):
        col.button(example, key=f"ex_{example}", on_click=on_click, args=(example,), width="stretch")


# ---------- live dropdown version (streamlit-searchbox) ----------
def _suggestions(typed):
    """Called on every key press. Returns (label, ingredient index) pairs for the dropdown."""
    st.session_state["last_typed"] = typed
    q = normalize(typed)
    if not q:
        return []
    engine = get_engine()
    if len(q) < 2:                                   # too short for search(): use the trie directly
        seen, out = set(), []
        for _name, index in engine.trie.with_prefix(q):
            if index not in seen:
                seen.add(index)
                out.append((f"{label(index)}   ·   starts with", index))
        return sorted(out)[:8]
    found = engine.search(typed, top_k=8)
    if any(m["match_type"] != "fuzzy" for m in found):       # real prefix/exact hits: leave out spelling guesses
        found = [m for m in found if m["match_type"] != "fuzzy"]
    return [(f"{label(m['index'])}   ·   {KIND[m['match_type']]} {m['score']:.0%}", m["index"])
            for m in found]


def _pick_example(example):
    """Example button: search that word and select the best match."""
    matches = get_engine().search(example, top_k=1)
    if matches:
        st.session_state.update(chosen=matches[0]["index"], chosen_match=matches[0], sb_last=None,
                                last_typed=example)


def _render_live():
    st.markdown("<div class='search-label'>Name the ingredient you want to replace</div>", unsafe_allow_html=True)
    picked = st_searchbox(_suggestions, key="sb", placeholder="Start typing: ghee, jeera, जीरा, zeera ...",
                          clear_on_submit=False, debounce=150)

    if picked is not None and picked != st.session_state.get("sb_last"):   # a new choice from the dropdown
        typed = st.session_state.get("last_typed", "")
        match = next((m for m in get_engine().search(typed, top_k=8) if m["index"] == picked), None)
        st.session_state.update(chosen=picked, chosen_match=match, sb_last=picked)

    chosen = st.session_state.get("chosen")
    if chosen is None:                      # start screen only: example chips, then how it works
        _examples(_pick_example)
        _how_it_works()
        return
    st.divider()
    match = st.session_state.get("chosen_match")
    if match:
        _log_search(st.session_state.get("last_typed", match["english_name"]), [match])
        _banner(match)
    render_substitutes(0, chosen, st.session_state.get("top_n", 5))


# ---------- fallback version (plain text box, press Enter) ----------
def _render_text():
    st.markdown("<div class='search-label'>Name the ingredients you want to replace</div>", unsafe_allow_html=True)
    query = st.text_input("Name the ingredients you want to replace", key="query", label_visibility="collapsed",
                          placeholder="e.g.  ghee   ·   jeera   ·   जीरा   ·   ghee, sugar",
                          help="Press Enter to search. Separate several ingredients with commas.")

    engine = get_engine()
    terms = []
    for raw in query.replace(";", ",").replace("\n", ",").split(","):
        raw = raw.strip()
        if raw and raw.lower() not in [t.lower() for t in terms]:
            terms.append(raw)
    if not terms:                           # start screen only
        _examples(set_query)
        _how_it_works()
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


def render():
    st.markdown("<div class='hero'><h1>Out of an ingredient? Find a replacement.</h1>"
                "<p>Type it in English, Hindi or Roman spelling. Typos are fine.</p></div>",
                unsafe_allow_html=True)
    (_render_live if HAVE_SEARCHBOX else _render_text)()
