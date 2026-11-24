# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Analysis page: charts about the dataset, the search quality and this visit's searches.
Uses backend function: get_profiles() (through ui_common.profiles)."""
import os
import re
from collections import Counter

import pandas as pd
import plotly.express as px
import streamlit as st

import backend
from ui_common import GREEN, SAFFRON, profiles


@st.cache_data
def dataset_frame():
    return pd.DataFrame([{"ingredient": p["english_name"], "category": p["category"],
                          "aroma": p["aroma"], "taste": p["taste"]} for p in profiles().values()])


@st.cache_data
def swap_eval():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D3_7_evaluation_summary.csv")
    return pd.read_csv(path, encoding="utf-8-sig") if os.path.exists(path) else None


def _row(df, **where):
    """First row of df that matches all the column=value pairs, or None."""
    for col, value in where.items():
        df = df[df[col] == value]
    return None if df.empty else df.iloc[0]


def _good_wins(ev, basis):
    """(good, total) hand-marked wins for 'tags' or 'molecular', from the win_review rows, or None."""
    row = _row(ev, evaluation="win_review", method=basis)
    if row is None:
        return None
    found = re.search(r"good wins (\d+) of (\d+)", str(row["note"]))
    return (int(found.group(1)), int(found.group(2))) if found else None


def _swap_quality():
    ev = swap_eval()
    has = sum(backend.has_compounds(i) for i in profiles())
    c1, c2 = st.columns([1, 2])
    cov = pd.DataFrame({"data": ["Has flavour compounds", "Labels only (weaker)"], "ingredients": [has, len(profiles()) - has]})
    c1.plotly_chart(px.pie(cov, names="data", values="ingredients", title="What the scores can use",
                           color_discrete_sequence=[GREEN, SAFFRON]).update_layout(height=340), width="stretch")
    c2.markdown(f"**{has} of {len(profiles())} ingredients** have measured flavour compounds (Ahn et al. data). "
                "The rest, including ghee, many spices and millets, can only be scored on smell and taste labels from "
                "Deliverable 1. Label scores are marked **weaker** everywhere in the app, because a few shared labels "
                "can already give 100%.")
    if ev is None:
        st.info("Evaluation file (D3_7_evaluation_summary.csv) not found.")
        return
    gold = ev[(ev["evaluation"] == "gold_pairs") & (ev["split"] == "all") & ev["method"].str.endswith("jaccard")].copy()
    gold["basis"] = gold["method"].str.replace(" jaccard", "", regex=False).map(
        {"molecular": "Compounds only", "tags": "Labels only", "best": "Higher of the two", "auto": "Compounds if any, else labels"})
    n_gold = int(gold["n"].iloc[0])
    best5 = _row(gold, method="best jaccard")["hit5"]
    long = gold.melt(id_vars="basis", value_vars=["hit1", "hit5"], var_name="measure", value_name="share")
    long["measure"] = long["measure"].map({"hit1": "Hit@1", "hit5": "Hit@5"})
    st.plotly_chart(px.bar(long, x="basis", y="share", color="measure", barmode="group",
                           title=f"Does the system's top list contain the team's known swaps? ({n_gold} pairs)",
                           color_discrete_map={"Hit@1": SAFFRON, "Hit@5": GREEN}).update_layout(height=400),
                    width="stretch")
    st.markdown(f"**In plain words:** the known swap shows up in the top five about {round(100 * best5)}% of the time "
                "(a random list would manage about 2%). Compound-only scores look low because many known swaps involve "
                "ingredients with no compound data. This is why the app lists the hand-picked **known swaps** first and "
                "treats the computed list as ideas to explore.")
    cat = ev[(ev["evaluation"] == "category_check") & (ev["split"] == "all")].copy()
    n_cat = int(cat["n"].iloc[0])
    cat["method"] = cat["method"].map({"jaccard": "Jaccard", "idf": "IDF-weighted", "random": "Random order"})
    st.plotly_chart(px.bar(cat.melt(id_vars="method", value_vars=["hit1", "hit5"], var_name="measure", value_name="share")
                           .assign(measure=lambda d: d["measure"].map({"hit1": "Hit@1", "hit5": "Hit@5"})),
                           x="method", y="share", color="measure", barmode="group",
                           title=f"Does the top swap share the food category? ({n_cat} ingredients)",
                           color_discrete_map={"Hit@1": SAFFRON, "Hit@5": GREEN}).update_layout(height=380),
                    width="stretch")
    ws = []
    for r in ev[(ev["evaluation"] == "win_share") & (ev["split"] == "all")].itertuples():
        found = re.search(r"tags win (\d+), compounds win (\d+), tie (\d+)", str(r.note))
        if found:
            name = "Jaccard" if r.method == "jaccard" else "IDF-weighted"
            for who, count in zip(["Label score higher", "Compound score higher", "Tie"], found.groups()):
                ws.append({"method": name, "who": who, "pairs": int(count)})
    if ws:
        st.plotly_chart(px.bar(pd.DataFrame(ws), x="pairs", y="method", color="who", orientation="h", barmode="stack",
                               title="Which data source scores higher? (11,214 pairs that have both)",
                               color_discrete_map={"Label score higher": SAFFRON, "Compound score higher": GREEN,
                                                   "Tie": "#B8B8B8"}).update_layout(height=300), width="stretch")
        st.caption("Labels have few values and many ties, so they reach high percentages more easily. That is why a "
                   "label win is not automatically a good swap, and why label scores are marked weaker.")
    tags_good, mol_good = _good_wins(ev, "tags"), _good_wins(ev, "molecular")
    if tags_good and mol_good:
        m = st.columns(2)
        m[0].metric("Label-based top swaps judged good by hand", f"{tags_good[0]} of {tags_good[1]}")
        m[1].metric("Compound-based top swaps judged good by hand", f"{mol_good[0]} of {mol_good[1]}", help="Small sample")


@st.cache_data
def search_quality():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D2_8_evaluation_summary.csv")
    return pd.read_csv(path, encoding="utf-8-sig") if os.path.exists(path) else None


def render():
    st.title("Analysis")
    df = dataset_frame()
    aroma_counts = Counter(t for tags in df["aroma"] for t in tags)
    taste_counts = Counter(t for tags in df["taste"] for t in tags)

    m = st.columns(4)
    m[0].metric("Ingredients", len(df))
    m[1].metric("Aroma tags", len(aroma_counts))
    m[2].metric("Taste tags", len(taste_counts))
    m[3].metric("Searches this visit", len(st.session_state["search_log"]))

    tab_data, tab_search, tab_sub, tab_you = st.tabs(
        ["Deliverable 1: Data", "Deliverable 2: Search", "Deliverable 3: Swaps", "Your searches"])

    with tab_data:
        st.caption("Food groups come from Deliverable 1's category file.")
        cat = df["category"].value_counts().rename_axis("category").reset_index(name="ingredients")
        st.plotly_chart(px.bar(cat, x="ingredients", y="category", orientation="h", title="Ingredients per food group",
                               color_discrete_sequence=[SAFFRON]).update_layout(yaxis=dict(autorange="reversed"), height=420),
                        width="stretch")
        left, right = st.columns(2)
        pick = left.selectbox("Aroma tags for", ["All groups"] + sorted(df["category"].unique()))
        sub = df if pick == "All groups" else df[df["category"] == pick]
        ac = Counter(t for tags in sub["aroma"] for t in tags).most_common(12)
        if ac:
            left.plotly_chart(px.bar(pd.DataFrame(ac, columns=["aroma", "ingredients"]), x="ingredients", y="aroma",
                                     orientation="h", title="Most common aromas", color_discrete_sequence=[GREEN])
                              .update_layout(yaxis=dict(autorange="reversed"), height=400), width="stretch")
        else:
            left.info("No aroma data for this group.")
        tc = pd.DataFrame(taste_counts.most_common(), columns=["taste", "ingredients"])
        right.plotly_chart(px.bar(tc, x="taste", y="ingredients", title="Taste tags across all ingredients",
                                  color_discrete_sequence=[SAFFRON]).update_layout(height=400), width="stretch")

        rows = [{"category": r.category, "taste": t} for r in df.itertuples() for t in r.taste]
        heat = pd.crosstab(pd.DataFrame(rows)["category"], pd.DataFrame(rows)["taste"], normalize="index") * 100
        st.plotly_chart(px.imshow(heat.round(0), text_auto=True, aspect="auto", color_continuous_scale="YlOrBr",
                                  title="Share of each food group that has each taste (%)").update_layout(height=460),
                        width="stretch")

        st.subheader("Do our spellings match real recipes?")
        st.caption("From Deliverable 1's variant mining on 10,000 recipes.")
        v = st.columns(4)
        v[0].metric("Our spellings", "885")
        v[1].metric("Recipe phrases checked", "5,309")
        v[2].metric("Ingredients seen in recipes", "192 of 250", help="77% of the dataset appears in the recipes.")
        v[3].metric("Frequent phrases we miss", "218")
        st.markdown("Our main names account for 43,108 hits in the recipes and the extra spellings for 2,712 more. "
                    "The missed phrases are mostly forms like cut or cooked versions, which is where the search's "
                    "“closest guess” helps.")

    with tab_search:
        q = search_quality()
        if q is None:
            st.info("Search test results file (D2_8_evaluation_summary.csv) was not found.")
        else:
            total = int(q[q["query_type"] != "ALL (without no_match)"]["n"].sum())
            typo = q[q["query_type"].isin(["typo_1", "typo_2", "hindi_typo"])]
            typo_hit = (typo["hit1"] * typo["n"]).sum() / typo["n"].sum() if len(typo) else 0
            st.caption(f"From the {total} test queries in Deliverable 2. Hit@1 = right ingredient is the first result; "
                       "Hit@5 = it is in the top five.")
            raw = q
            allrow = _row(raw, query_type="ALL (without no_match)")
            miss = _row(raw, query_type="no_match")
            k = st.columns(4)
            k[0].metric("Right ingredient first (Hit@1)", f"{allrow['hit1']:.0%}")
            k[1].metric("In the top five (Hit@5)", f"{allrow['hit5']:.0%}")
            k[2].metric("Average rank score (MRR)", f"{allrow['mrr']:.2f}", help="1.0 means always first; 0.5 means second on average.")
            k[3].metric("Unknown names rejected", f"{miss['rejection_rate']:.0%}", help="Queries for things not in the list, like paprika.")
            q = q[~q["query_type"].isin(["no_match", "ALL (without no_match)"])]
            long = q.melt(id_vars="query_type", value_vars=["hit1", "hit5"], var_name="measure", value_name="share")
            long["measure"] = long["measure"].map({"hit1": "Hit@1", "hit5": "Hit@5"})
            st.plotly_chart(px.bar(long, x="query_type", y="share", color="measure", barmode="group",
                                   title="Search accuracy by kind of query",
                                   color_discrete_map={"Hit@1": SAFFRON, "Hit@5": GREEN}).update_layout(height=420),
                            width="stretch")
            st.markdown(f"**In plain words:** exact names in English, Roman or Hindi are always found. Typos are found "
                        f"first about {round(100 * typo_hit)} times in 100. Different spellings (like *jira*) and whole recipe phrases are the weak spot, "
                        "which is why the app shows you a “closest guess” label and lets you pick another match.")
            speed = raw[~raw["query_type"].isin(["ALL (without no_match)"])]
            st.plotly_chart(px.bar(speed, x="query_type", y="mean_ms", log_y=True,
                                   title="Time per search by kind of query (milliseconds, log scale)",
                                   color_discrete_sequence=[SAFFRON]).update_layout(height=380), width="stretch")
            st.markdown("Exact lookups take about 0.02 ms. Anything that needs spelling comparison (fuzzy) takes 35 to 64 ms. "
                        "Fuzzy cost grows with the list: 57 ms on 1,135 names, 435 ms on 5,309. The trie finds a prefix in "
                        "0.11 ms against 0.40 ms for checking every name.")


    with tab_sub:
        _swap_quality()

    with tab_you:
        log = st.session_state["search_log"]
        if not log:
            st.info("Run a search on the first page and it will appear here.")
        else:
            log_df = pd.DataFrame(log)
            st.dataframe(log_df, width="stretch", hide_index=True)
            kinds = log_df["match type"].value_counts().rename_axis("match type").reset_index(name="searches")
            st.plotly_chart(px.pie(kinds, names="match type", values="searches", title="How your searches were matched",
                                   color_discrete_sequence=[GREEN, SAFFRON, "#4A7FB5", "#B5473A"]).update_layout(height=340),
                            width="stretch")
            if st.button("Clear my search history"):
                st.session_state["search_log"], st.session_state["last_logged"] = [], ""
                st.rerun()
