# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Two overlap scores for flavor compounds: plain Jaccard and IDF-weighted (Deliverable 3)."""
import math

from D3_1_load_compounds import load_ahn
from D3_2_match_names import build_matches, read_d1

MIN_COMPOUNDS = 5   # fewer than this and an overlap score says very little


def jaccard(a, b):
    """Shared items divided by all items in either set (0 to 1)."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def compound_idf(ahn_ingredients):
    """IDF weight per compound: log(N / df). N = all ingredients that have compounds,
    df = how many of them contain this compound. A compound found everywhere weighs little."""
    with_compounds = [v["compounds"] for v in ahn_ingredients.values() if v["compounds"]]
    count = {}
    for compounds in with_compounds:
        for c in compounds:
            count[c] = count.get(c, 0) + 1
    n = len(with_compounds)
    return {c: math.log(n / df) for c, df in count.items()}


def weighted_overlap(a, b, weight):
    """Like Jaccard, but each compound counts as its IDF weight instead of 1."""
    union = sum(weight.get(c, 0.0) for c in a | b)
    if union == 0:
        return 0.0
    return sum(weight.get(c, 0.0) for c in a & b) / union


class MoleculeScorer:
    """Scores two of our ingredients by the flavor compounds they share.
    The IDF weights are computed from the whole Ahn data, not just our 250."""

    def __init__(self, rows=None, ahn_ingredients=None, compound_names=None, matches=None):
        if ahn_ingredients is None:
            ahn_ingredients, compound_names = load_ahn()
        rows = rows if rows is not None else read_d1()
        matches = matches if matches is not None else build_matches(rows, ahn_ingredients)
        self.compound_names = compound_names or {}
        self.weight = compound_idf(ahn_ingredients)
        self.ahn_name = {}      # d1 index -> Ahn ingredient it was linked to
        self.compounds = {}     # d1 index -> set of compound ids
        self.category = {}      # d1 index -> Ahn category (used by the evaluation)
        for index, m in matches.items():
            compounds = ahn_ingredients[m["ahn_name"]]["compounds"] if m["ahn_name"] else set()
            if len(compounds) >= MIN_COMPOUNDS:
                self.ahn_name[index] = m["ahn_name"]
                self.compounds[index] = compounds
                self.category[index] = m["category"]

    def has(self, index):
        return index in self.compounds

    def jaccard(self, i, j):
        return jaccard(self.compounds.get(i, set()), self.compounds.get(j, set()))

    def idf(self, i, j):
        return weighted_overlap(self.compounds.get(i, set()), self.compounds.get(j, set()), self.weight)

    def shared(self, i, j, top=5):
        """Names of the shared compounds, rarest (highest weight) first."""
        common = self.compounds.get(i, set()) & self.compounds.get(j, set())
        ranked = sorted(common, key=lambda c: (-self.weight.get(c, 0.0), c))
        return [self.compound_names.get(c, str(c)) for c in ranked[:top]]


if __name__ == "__main__":
    # small self-check:  python D3_3_scores.py
    a, b = {1, 2, 3}, {2, 3, 4, 5}
    checks = [("jaccard {1,2,3} vs {2,3,4,5} = 2/5", jaccard(a, b), 0.4),
              ("jaccard with an empty set", jaccard(a, set()), 0.0),
              ("jaccard of a set with itself", jaccard(a, a), 1.0)]
    weight = {1: 1.0, 2: 3.0, 3: 1.0, 4: 1.0, 5: 1.0}      # compound 2 is rare, so it counts 3
    checks.append(("weighted: (3+1) / (1+3+1+1+1) = 4/7", weighted_overlap(a, b, weight), 4 / 7))
    for label, got, want in checks:
        print("ok  " if abs(got - want) < 1e-9 else "FAIL", label, round(got, 4))
    tiny = {"x": {"compounds": {1, 2}}, "y": {"compounds": {1}}, "z": {"compounds": {1, 3}}, "w": {"compounds": set()}}
    idf = compound_idf(tiny)         # N = 3, compound 1 is in all three, 2 and 3 in one
    print("ok  " if idf[1] == 0 and abs(idf[2] - math.log(3)) < 1e-9 else "FAIL", "idf: common compound weighs 0")
    scorer = MoleculeScorer()
    print("ok  " if len(scorer.compounds) > 100 else "FAIL", "ingredients with 5+ compounds:", len(scorer.compounds))
