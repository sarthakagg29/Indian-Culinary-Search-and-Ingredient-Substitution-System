# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Links each of our 250 ingredients to an ingredient in the Ahn flavor data (Deliverable 3)."""
import csv
import os
import re

from D2_1_normalize import normalize
from D2_2_levenshtein import edit_distance
from D3_1_load_compounds import load_ahn

HERE = os.path.dirname(os.path.abspath(__file__))
D1_CSV = os.path.join(HERE, "D1_input_lookup_ingredient_250_final_dataset.csv")
SYNONYMS_CSV = os.path.join(HERE, "D3_2_synonyms.csv")
MATCHES_CSV = os.path.join(HERE, "D3_2_matches.csv")

# words that only say which form it is: "turmeric powder" is still turmeric
FORM_WORDS = {"powder", "paste", "fresh", "dried", "dry", "whole", "seeds", "seed", "leaves",
              "leaf", "pods", "pod", "raw", "ground", "juice", "chutney", "flour", "oil",
              "cubes", "boneless", "pieces", "split", "baby"}
FUZZY_MIN_SIMILARITY = 0.85   # whole-name similarity, stricter than the search in D2
FUZZY_MIN_LEN = 5


def read_d1(path=None):
    """The 250 rows of the D1 dataset (a list of dicts, index turned into an int)."""
    with open(path or D1_CSV, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["index"] = int(row["index"])
    return rows


def read_synonyms(path=None):
    """{english_name: ahn_name} from the hand-made file. A blank ahn_name means 'no match'."""
    path = path or SYNONYMS_CSV
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        return {r["english_name"].strip().lower(): r["ahn_name"].strip() for r in csv.DictReader(f)}


def _singular(word):
    if word.endswith("ies"):
        return word[:-3] + "y"
    return word[:-1] if word.endswith("s") and not word.endswith("ss") else word


def spellings(name):
    """Ways an ingredient name might be written in the Ahn data (underscores, no form words)."""
    words = [_singular(w) for w in re.split(r"[\s\-]+", normalize(name)) if w]
    core = [w for w in words if w not in FORM_WORDS]
    found = ["_".join(words), "_".join(core)]
    if len(core) > 1:
        found.append("_".join(core[::-1]))      # "gourd bitter" style order
    return [s for s in dict.fromkeys(found) if s]


def _first_hit(names, usable):
    for spelling in names:
        for candidate in (spelling, spelling + "s"):
            if candidate in usable:
                return candidate
    return None


def match_one(row, usable, synonyms):
    """Returns (ahn_name, how). how is synonym, name, stripped, variant, scientific or fuzzy."""
    key = row["english_name"].strip().lower()
    if key in synonyms:
        target = synonyms[key]
        return (target, "synonym") if target in usable else (None, "")
    plain = "_".join(_singular(w) for w in re.split(r"[\s\-]+", normalize(row["english_name"])) if w)
    hit = _first_hit(spellings(row["english_name"]), usable)
    if hit:
        return hit, ("name" if hit.rstrip("s") == plain.rstrip("s") else "stripped")
    for variant in row["roman_variants"].split("|"):
        hit = _first_hit(spellings(variant), usable)
        if hit:
            return hit, "variant"
    latin = row["scientific_name"].split("|")[0].strip().lower().replace(" ", "_")
    if latin in usable:
        return latin, "scientific"
    return _fuzzy_hit(row["english_name"], usable)


def _fuzzy_hit(english_name, usable):
    """Last resort: a whole-name spelling difference (asafoetida / asafetida)."""
    query = normalize(english_name)
    if len(query) < FUZZY_MIN_LEN:
        return None, ""
    best, best_sim = None, FUZZY_MIN_SIMILARITY
    for name in usable:
        text = name.replace("_", " ")
        if abs(len(text) - len(query)) > 2:
            continue
        sim = 1 - edit_distance(query, text) / max(len(query), len(text))
        if sim >= best_sim:
            best, best_sim = name, sim
    return (best, "fuzzy") if best else (None, "")


def build_matches(rows=None, ahn_ingredients=None, synonyms=None):
    """{d1_index: {"ahn_name", "how", "category", "n_compounds"}} for every D1 row."""
    rows = rows if rows is not None else read_d1()
    ahn_ingredients = ahn_ingredients if ahn_ingredients is not None else load_ahn()[0]
    synonyms = synonyms if synonyms is not None else read_synonyms()
    usable = {name for name, v in ahn_ingredients.items() if v["compounds"]}
    matches = {}
    for row in rows:
        name, how = match_one(row, usable, synonyms)
        info = ahn_ingredients.get(name) if name else None
        matches[row["index"]] = {"ahn_name": name or "", "how": how,
                                 "category": info["category"] if info else "",
                                 "n_compounds": len(info["compounds"]) if info else 0}
    return matches


def write_matches_csv(rows, matches, path=None):
    """A table to read through by hand. Fix mistakes in D3_2_synonyms.csv, not here."""
    with open(path or MATCHES_CSV, "w", encoding="utf-8-sig", newline="") as f:
        out = csv.writer(f)
        out.writerow(["index", "english_name", "ahn_name", "how", "n_compounds", "check"])
        for row in rows:
            m = matches[row["index"]]
            check = "yes" if m["how"] in ("variant", "scientific", "fuzzy") else ""
            out.writerow([row["index"], row["english_name"], m["ahn_name"], m["how"], m["n_compounds"], check])


if __name__ == "__main__":
    # builds D3_2_matches.csv and runs a small self-check:  python D3_2_match_names.py
    rows = read_d1()
    ahn, _ = load_ahn()
    matches = build_matches(rows, ahn)
    write_matches_csv(rows, matches)
    found = sum(1 for m in matches.values() if m["ahn_name"])
    print("matched", found, "of", len(rows), "- written to", os.path.basename(MATCHES_CSV))
    usable = {n for n, v in ahn.items() if v["compounds"]}
    tiny = {"turmeric powder": ("turmeric", "stripped"), "cloves": ("clove", "name")}
    for text, want in tiny.items():
        row = {"english_name": text, "roman_variants": "", "scientific_name": ""}
        got = match_one(row, usable, {})
        print("ok  " if got == want else "FAIL", repr(text), got)
    row = {"english_name": "beetroot", "roman_variants": "", "scientific_name": ""}
    got = match_one(row, usable, {"beetroot": "beet"})
    print("ok  " if got == ("beet", "synonym") else "FAIL", "synonym wins:", got)
    got = match_one({"english_name": "xyzabc", "roman_variants": "", "scientific_name": ""}, usable, {})
    print("ok  " if got == (None, "") else "FAIL", "unknown name gives no match:", got)
