# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Shared bits used by every page: page names, colours, small helpers, button callbacks.
No page code lives here and nothing is drawn on import."""
import streamlit as st

import backend
from D2_5_search import IngredientSearch

PAGES = ["🔍 Find a Substitute", "⚖️ Compare Two", "📊 Analysis", "🚀 New Features Coming", "ℹ️ About"]
P_SEARCH, P_COMPARE, P_ANALYSIS, P_SOON, P_ABOUT = PAGES

SAFFRON, GREEN = "#E07A1F", "#2F7D5B"

CSS = f"""
<style>
.hero {{ background: linear-gradient(120deg, {SAFFRON} 0%, #F2A33A 60%, #F6C667 100%);
        border-radius: 18px; padding: 1.6rem 1.8rem; margin-bottom: 1.2rem; color: #fff; }}
.hero h1 {{ margin: 0; font-size: 2rem; color: #fff; }}
.hero p  {{ margin: .3rem 0 0 0; font-size: 1.02rem; opacity: .95; }}
.search-label {{ font-size: 1.35rem; font-weight: 700; margin: .4rem 0 .2rem 0; }}
.chip {{ display: inline-block; padding: .12rem .6rem; margin: .1rem .2rem .1rem 0; border-radius: 999px;
        font-size: .82rem; background: rgba(224,122,31,.14); border: 1px solid rgba(224,122,31,.35); }}
.chip.shared {{ background: rgba(47,125,91,.15); border-color: rgba(47,125,91,.45); }}
.badge {{ display: inline-block; padding: .1rem .55rem; border-radius: 6px; font-size: .78rem; font-weight: 600; }}
.badge.exact {{ background: #DCF2E6; color: #17613F; }}
.badge.prefix {{ background: #E1EEFB; color: #1B4F87; }}
.badge.fuzzy {{ background: #FFF0CC; color: #8A5A00; }}
.badge.known {{ background: #E8E1F7; color: #4B3A8C; }}
.badge.mol {{ background: #DCF2E6; color: #17613F; }}
.badge.tags {{ background: #FFF0CC; color: #8A5A00; }}
.big-score {{ font-size: 3rem; font-weight: 800; line-height: 1; }}
div[data-testid="stMetricValue"] {{ font-size: 1.7rem; }}
</style>
"""


@st.cache_resource(show_spinner="Loading the ingredient search...")
def get_engine():
    """Deliverable 2 search, built once and kept."""
    return IngredientSearch()


def profiles():
    return backend.get_profiles()           # backend function 1 of 3


def all_indexes():
    p = profiles()
    return sorted(p, key=lambda i: p[i]["english_name"])


def label(index):
    p = profiles()[index]
    return f"{p['english_name']}  ({p['hindi']})" if p["hindi"] else p["english_name"]


def chips(tags, css=""):
    if not tags:
        return "<span style='opacity:.6'>none listed</span>"
    return "".join(f"<span class='chip {css}'>{t}</span>" for t in tags)


def score_colour(score):
    return GREEN if score >= 70 else SAFFRON if score >= 50 else "#B5473A"


# Button callbacks: they run before the page redraws, so they can change widgets safely
def set_query(text):
    st.session_state["query"] = text


def go_compare(a, b):
    st.session_state["cmp_a"], st.session_state["cmp_b"] = a, b
    st.session_state["page"] = P_COMPARE


def go_page(page):
    st.session_state["page"] = page


def method():
    """Chosen scoring method ('jaccard' or 'idf'), set in the sidebar."""
    return st.session_state.get("method", "jaccard")


def basis_badge(basis, weaker, known=False):
    """Small coloured tags that say where a score comes from."""
    out = ""
    if known:
        out += "<span class='badge known'>✓ Known swap</span> "
    if basis == "molecular":
        out += "<span class='badge mol'>Flavour compounds</span>"
    elif basis == "tags":
        out += "<span class='badge tags'>Smell/taste labels · weaker</span>"
    else:
        out += "<span class='badge tags'>No score</span>"
    return out
