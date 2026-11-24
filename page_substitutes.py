# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""The list of replacements for one ingredient.  Calls backend function: get_substitutes()."""
import streamlit as st

import backend
from ui_common import basis_badge, go_compare, method, profiles, score_colour


def _card(term_no, index, sub):
    with st.container(border=True):
        left, mid, right = st.columns([3.4, 2.1, 1.1], vertical_alignment="center")
        with left:
            hindi = f" · {sub['hindi']}" if sub["hindi"] else ""
            st.markdown(f"**{sub['english_name']}**{hindi}", help=sub["category"])
            st.markdown(basis_badge(sub["basis"], sub["weaker"], sub["known"]), unsafe_allow_html=True)
            st.caption(sub["tip"])
        with mid:
            if sub["score"] is None:
                st.markdown("<span style='opacity:.65'>no score for this pair</span>", unsafe_allow_html=True)
            else:
                # a label-only score is a weak signal (few labels, many ties), so it is shown in grey
                colour = score_colour(sub["score"]) if sub["basis"] == "molecular" else "#7A7A7A"
                what = "overlap" if sub["basis"] == "molecular" else "label overlap"
                st.markdown(f"<span style='font-size:1.5rem;font-weight:700;color:{colour}'>"
                            f"{sub['score']}%</span> <span style='opacity:.65'>{what}</span>", unsafe_allow_html=True)
                st.progress(sub["score"] / 100)
        with right:
            st.button("Compare", key=f"cmp_{term_no}_{index}_{sub['index']}",
                      on_click=go_compare, args=(index, sub["index"]), width="stretch")


def render_substitutes(term_no, index, top_n):
    me = profiles()[index]
    st.markdown(f"#### What can replace **{me['english_name']}**"
                f"{' · ' + me['hindi'] if me['hindi'] else ''}?")
    st.caption(f"Group: {me['category']}  ·  Aroma: {', '.join(me['aroma']) or 'n/a'}  ·  "
               f"Taste: {', '.join(me['taste']) or 'n/a'}")
    subs = backend.get_substitutes(index, top_n, method())
    known = [s for s in subs if s["known"]]
    ideas = [s for s in subs if not s["known"]]
    if not subs:
        st.info("No substitutes found for this ingredient.")
        return
    if known:
        st.markdown("**Known swaps**  \n<span style='opacity:.7;font-size:.9rem'>Hand-picked by the team. "
                    "The percentage is the shared-flavour score.</span>", unsafe_allow_html=True)
        for s in known:
            _card(term_no, index, s)
    if ideas:
        st.markdown("**More ideas, ranked by shared flavour**")
        if not backend.has_compounds(index):
            st.caption("No flavour-compound data for this ingredient, so these use smell and taste labels only. "
                       "That is the weaker kind of match: treat them as ideas, not answers.")
        else:
            st.caption("Ranked by shared flavour compounds where available, otherwise by labels (marked weaker).")
        for s in ideas:
            _card(term_no, index, s)
