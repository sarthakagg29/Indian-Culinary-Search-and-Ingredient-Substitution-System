# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Compare two ingredients.  Calls backend function: match_details()."""
import plotly.graph_objects as go
import streamlit as st

import backend
from ui_common import GREEN, SAFFRON, all_indexes, basis_badge, chips, label, method, profiles, score_colour


def _radar(a, b, axes, field, title):
    fig = go.Figure()
    for p, colour in ((a, SAFFRON), (b, GREEN)):
        values = [1 if ax in p[field] else 0 for ax in axes]
        fig.add_trace(go.Scatterpolar(r=values + values[:1], theta=axes + axes[:1], fill="toself",
                                      name=p["english_name"], line_color=colour, opacity=0.65))
    fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1])), title=title,
                      margin=dict(t=50, b=20, l=30, r=30), height=380, legend=dict(orientation="h", y=-0.1))
    return fig


def render():
    prof = profiles()
    st.title("⚖️ Compare two ingredients")
    st.caption("Pick the ingredient you have to replace and the one you want to use instead.")
    c1, c2 = st.columns(2)
    by_name = {p["english_name"]: i for i, p in prof.items()}
    st.session_state.setdefault("cmp_a", by_name["ghee"])      # first-visit defaults
    st.session_state.setdefault("cmp_b", by_name["butter"])
    ia = c1.selectbox("Replace this", all_indexes(), key="cmp_a", format_func=label)
    ib = c2.selectbox("With this", all_indexes(), key="cmp_b", format_func=label)
    if ia == ib:
        st.info("Choose two different ingredients to compare.")
        return
    a, b = prof[ia], prof[ib]
    d = backend.match_details(ia, ib, method())          # backend function 3 of 3

    top = st.columns([1.3, 2.7], vertical_alignment="center")
    with top[0]:
        if d["score"] is None:
            st.markdown("<div class='big-score' style='opacity:.4'>n/a</div>"
                        "<div style='opacity:.7'>not enough data to score</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='big-score' style='color:{score_colour(d['score'])}'>{d['score']}%</div>"
                        f"<div style='opacity:.7'>shared flavour overlap</div>", unsafe_allow_html=True)
    with top[1]:
        st.markdown(basis_badge(d["basis"], d["weaker"], d["known"]), unsafe_allow_html=True)
        if d["same_source"]:
            st.caption("These two share one flavour-data entry (like fresh and powdered forms), so the score cannot tell them apart.")
        if d["basis"] == "tags":
            st.caption("This score comes from smell and taste labels, not measured compounds. Labels are short, so "
                       "even a few shared ones can give a high percentage.")
        elif d["basis"] == "molecular":
            st.caption("This score comes from flavour compounds both ingredients contain (Ahn et al. data).")
        if d["note"]:
            st.caption(f"Note on this swap: {d['note']}")
        parts = []
        if d["score_molecular"] is not None:
            parts.append(f"compounds {d['score_molecular']}%")
        if d["score_tags"] is not None:
            parts.append(f"labels {d['score_tags']}%")
        if parts:
            st.caption("Both scores for this pair: " + ", ".join(parts) + ". The higher one is used.")
    if d["shared_compounds"]:
        with st.expander(f"{len(d['shared_compounds'])} shared flavour compounds"):
            st.write(", ".join(d["shared_compounds"]))

    st.divider()
    pa, pb = st.columns(2)
    for col, p, colour in ((pa, a, SAFFRON), (pb, b, GREEN)):
        with col:
            with st.container(border=True):
                st.markdown(f"<h4 style='color:{colour};margin:0'>{p['english_name'].title()}</h4>", unsafe_allow_html=True)
                st.markdown(f"{p['hindi'] or ''}  \n*{p['scientific_name'] or 'scientific name not listed'}*  \n"
                            f"Group: {p['category']}")
                st.markdown("**Aroma**", help="Smell notes from the dataset")
                st.markdown(chips(p["aroma"]), unsafe_allow_html=True)
                st.markdown("**Taste**")
                st.markdown(chips(p["taste"]), unsafe_allow_html=True)

    st.markdown("### Shared and different flavour")
    t_aroma, t_taste = st.tabs(["Aroma", "Taste"])
    for tab, kind in ((t_aroma, "aroma"), (t_taste, "taste")):
        with tab:
            x, y, z = st.columns(3)
            x.markdown(f"**Only {a['english_name']}**"); x.markdown(chips(d[f"only_a_{kind}"]), unsafe_allow_html=True)
            y.markdown("**Shared**");                     y.markdown(chips(d[f"shared_{kind}"], "shared"), unsafe_allow_html=True)
            z.markdown(f"**Only {b['english_name']}**"); z.markdown(chips(d[f"only_b_{kind}"]), unsafe_allow_html=True)

    st.markdown("### Charts")
    r1, r2 = st.columns(2)
    r1.plotly_chart(_radar(a, b, backend.TASTE_AXES, "taste", "Taste profile"), width="stretch")
    aroma_axes = sorted(set(a["aroma"]) | set(b["aroma"]))
    if len(aroma_axes) >= 3:
        r2.plotly_chart(_radar(a, b, aroma_axes, "aroma", "Aroma profile"), width="stretch")
    else:
        r2.info("Too few aroma tags to draw an aroma chart for this pair.")
