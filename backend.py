# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""
BACKEND for the CGAS web app: Deliverable 3 (real scores) + Deliverable 1 data.

app pages call only these functions:

    get_profiles()                          {index: profile}   (names, tags, real food group)
    get_substitutes(index, top_n, method)   replacements for one ingredient, best first
    match_details(index_a, index_b, method) score + shared / different flavour for one pair

Where the numbers come from
  * Scores are Deliverable 3's `Substituter` (Jaccard or IDF-weighted overlap).
      basis "molecular" = shared flavour compounds (Ahn et al. data), only for ingredients that have them
      basis "tags"      = shared smell tags + taste (rasa) labels from Deliverable 1. Weaker: short labels, many ties.
    For each pair the higher of the two wins and the result says which one it was.
  * "Known swaps" = the team's hand-written list (D3_6_gold_pairs.csv). They are shown first and get their
    real Deliverable 3 score. Their notes come from D1_7_substitutes_ground_truth.csv where one exists.
  * "Flavour matches" = Deliverable 3's own ranking, minus anything already shown as a known swap.
"""
import csv
import os
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
DATASET = os.path.join(HERE, "D1_input_lookup_ingredient_250_final_dataset.csv")
NA = "not available"
TASTE_AXES = ["sweet", "sour", "salty", "bitter", "pungent", "astringent", "umami"]
METHODS = {"jaccard": "Jaccard (simple overlap)", "idf": "IDF-weighted (rare compounds count more)"}

CATEGORY_NAMES = {
    "vegetable": "Vegetables", "spice": "Spices", "cereal_grain": "Grains & Cereals", "fruit": "Fruits",
    "legume": "Legumes & Pulses", "nut_seed": "Nuts & Seeds", "herb": "Herbs", "dairy": "Dairy",
    "condiment_other": "Condiments & Other", "seafood": "Seafood", "meat_poultry": "Meat & Poultry",
    "oil_fat": "Oils & Fats", "sweetener": "Sweeteners",
}


def _read(name):
    with open(os.path.join(HERE, name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _tags(text):
    return [] if text.strip().lower() == NA else [t.strip() for t in text.split("|") if t.strip()]


@lru_cache(maxsize=1)
def _substituter():
    from D3_5_substitute import Substituter          # builds the compound and tag scorers (about 1 second)
    return Substituter()


@lru_cache(maxsize=1)
def get_profiles():
    """{index: {index, english_name, hindi, scientific_name, aroma, taste, category}}"""
    cats = {r["english_name"]: CATEGORY_NAMES.get(r["category"], r["category"]) for r in _read("D1_0_ingredient_categories.csv")}
    profiles = {}
    for row in _read("D1_input_lookup_ingredient_250_final_dataset.csv"):
        sci = row["scientific_name"].strip()
        profiles[int(row["index"])] = {
            "index": int(row["index"]), "english_name": row["english_name"],
            "hindi": "" if row["hindi_devanagari"] == NA else row["hindi_devanagari"],
            "scientific_name": "" if sci.lower() == NA else sci,
            "aroma": _tags(row["olfactory"]), "taste": _tags(row["gustatory"]),
            "category": cats.get(row["english_name"], "Other")}
    return profiles


@lru_cache(maxsize=1)
def _by_name():
    return {p["english_name"]: i for i, p in get_profiles().items()}


@lru_cache(maxsize=1)
def _known_swaps():
    """{ingredient index: [substitute index, ...]} from the team's hand-written list, in file order."""
    by = _by_name()
    out = {}
    for r in _read("D3_6_gold_pairs.csv"):
        a, b = by.get(r["ingredient"]), by.get(r["substitute"])
        if a and b and b not in out.setdefault(a, []):
            out[a].append(b)
    return out


@lru_cache(maxsize=1)
def _notes():
    """{(ingredient index, substitute index): note} from Deliverable 1's swap notes."""
    by = _by_name()
    return {(by[r["ingredient"]], by[r["substitute"]]): r["note"].strip()
            for r in _read("D1_7_substitutes_ground_truth.csv")
            if r["ingredient"] in by and r["substitute"] in by and r["note"].strip()}


def has_compounds(index):
    return _substituter().molecules.has(index)


def _percent(result, method):
    value = result["jaccard_percent"] if method == "jaccard" else result["idf_percent"]
    return None if value is None else round(value)


def _short_list(items, n=4):
    return ", ".join(items[:n]) + (f" and {len(items) - n} more" if len(items) > n else "")


def _item(profile, score, basis, weaker, known, shared, tip):
    return {"index": profile["index"], "english_name": profile["english_name"], "hindi": profile["hindi"],
            "category": profile["category"], "score": score, "basis": basis, "weaker": weaker,
            "known": known, "shared": shared, "tip": tip}


def get_substitutes(index, top_n=5, method="jaccard"):
    """Replacements for one ingredient. Known swaps come first (best score first), then Deliverable 3's
    flavour matches. Each item: index, english_name, hindi, category, score (0-100 or None), basis
    ('molecular'|'tags'|'none'), weaker (bool), known (bool), shared (list), tip (text)."""
    sub, profiles = _substituter(), get_profiles()
    out, seen = [], {index}
    for j in _known_swaps().get(index, []):
        c = sub.compare(index, j, method=method)
        out.append(_item(profiles[j], _percent(c, method), c["basis"], c["weaker"], True, c["shared"],
                         _notes().get((index, j), "Hand-picked known swap.")))
        seen.add(j)
    out.sort(key=lambda x: (x["score"] is None, -(x["score"] or 0)))   # best first, unscored last
    out = out[:top_n]
    seen |= {x["index"] for x in out}
    pool = sub.substitutes(index, top_k=top_n + len(seen) + 5, method=method)
    shown = 0
    for r in pool:
        if r["index"] in seen or shown >= top_n:
            continue
        shown += 1
        what = _short_list(r["shared"]) if r["shared"] else "nothing listed"
        out.append(_item(profiles[r["index"]], round(r["percent"]), r["basis"], r["weaker"], False, r["shared"],
                         f"Shares: {what}"))
    return out


def match_details(index_a, index_b, method="jaccard"):
    """One pair. Keys: score (0-100 or None), basis, weaker, known, same_source, same_category,
    score_molecular, score_tags (each 0-100 or None), shared_compounds, shared_labels,
    and shared / only_a / only_b lists of aroma and taste tags."""
    sub, profiles = _substituter(), get_profiles()
    a, b = profiles[index_a], profiles[index_b]
    c = sub.compare(index_a, index_b, method=method)
    pick = lambda kind: None if c[kind] is None else round(100 * c[kind][method])
    sets = lambda f: (set(a[f]), set(b[f]))
    d = {"score": _percent(c, method), "basis": c["basis"], "weaker": c["weaker"], "same_source": c["same_source"],
         "known": index_b in _known_swaps().get(index_a, []) or index_a in _known_swaps().get(index_b, []),
         "same_category": a["category"] == b["category"],
         "score_molecular": pick("molecular"), "score_tags": pick("tags"),
         "shared_compounds": c["molecular"]["shared"] if c["molecular"] else [],
         "shared_labels": c["tags"]["shared"] if c["tags"] else [],
         "note": _notes().get((index_a, index_b))}
    for kind, field in (("aroma", "aroma"), ("taste", "taste")):
        x, y = sets(field)
        d[f"shared_{kind}"], d[f"only_a_{kind}"], d[f"only_b_{kind}"] = sorted(x & y), sorted(x - y), sorted(y - x)
    return d


if __name__ == "__main__":      # self-check:  python backend.py
    by = _by_name()
    print("ghee ->", [(s["english_name"], s["score"], "known" if s["known"] else s["basis"]) for s in get_substitutes(by["ghee"], 5)])
    d = match_details(by["ghee"], by["butter"])
    print("ghee vs butter:", d["score"], d["basis"], "known" if d["known"] else "")
    print("ingredients with compounds:", sum(has_compounds(i) for i in get_profiles()), "of", len(get_profiles()))
