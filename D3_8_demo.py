# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Prints example substitutes and one comparison (Deliverable 3).

python D3_8_demo.py                       a few examples
python D3_8_demo.py jeera tomato aam      substitutes for what you type (Hindi, Roman or English)
python D3_8_demo.py compare jeera dhaniya overlap of two ingredients
"""
import sys

from D3_5_substitute import Substituter

DEFAULTS = ["jeera", "tomato", "mango", "paneer", "ghee"]


def first_match(sub, text):
    found = sub.find(text, top_k=1)
    return found[0]["index"] if found else None


def show_substitutes(sub, text, top_k=5):
    index = first_match(sub, text)
    if index is None:
        print("\n%s: no ingredient found" % text)
        return
    info = sub.rows[index]
    note = "" if sub.molecules.has(index) else "  (no usable flavor compounds: tags only, weaker)"
    print("\n%s -> %s (%s)%s" % (text, info["english_name"], info["hindi_devanagari"], note))
    for method in ("jaccard", "idf"):
        results = sub.substitutes(index, top_k=top_k, method=method)
        line = ", ".join("%s %.0f%% (%s)" % (r["english_name"], r["percent"], "tags" if r["basis"] == "tags" else "compounds")
                         for r in results)
        print("  %-8s %s" % (method, line or "nothing shares a compound or tag"))
    best = sub.substitutes(index, top_k=1)
    if best:
        print("  best match shares: %s" % ", ".join(best[0]["shared"]))
        print("  best match scores: compounds %s, tags %s" % (best[0]["score_molecular"], best[0]["score_tags"]))


def show_compare(sub, text_a, text_b):
    a, b = first_match(sub, text_a), first_match(sub, text_b)
    if a is None or b is None:
        print("could not find both ingredients")
        return
    c = sub.compare(a, b)
    print("%s vs %s (%s basis%s)" % (c["a"]["english_name"], c["b"]["english_name"], c["basis"], ", weaker" if c["weaker"] else ""))
    if c["jaccard"] is None:
        print("  not enough data to compare these two")
        return
    for kind, label in (("molecular", "compounds"), ("tags", "smell + rasa tags")):
        if c[kind]:
            print("  %-18s Jaccard %.1f%%, IDF %.1f%%" % (label, 100 * c[kind]["jaccard"], 100 * c[kind]["idf"]))
    print("  winner: Jaccard overlap %.1f%%, IDF-weighted overlap %.1f%%" % (c["jaccard_percent"], c["idf_percent"]))
    print("  shared: %s" % (", ".join(c["shared"]) or "nothing"))
    print("  taste (rasa): %s | %s" % (c["a"]["rasa"], c["b"]["rasa"]))


if __name__ == "__main__":
    args = sys.argv[1:]
    sub = Substituter()
    if args[:1] == ["compare"] and len(args) == 3:
        show_compare(sub, args[1], args[2])
    else:
        for name in args or DEFAULTS:
            show_substitutes(sub, name)
