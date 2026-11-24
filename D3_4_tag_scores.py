# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Smell-tag and rasa overlap for all 250 ingredients (Deliverable 3).
Each ingredient gets one set of labels: its smell tags and its taste (rasa) labels from Deliverable 1.
Two ingredients are scored on the labels they share. These are short labels, not measured molecules,
so this score is marked weaker next to the compound score."""
import math

from D3_2_match_names import read_d1
from D3_3_scores import jaccard, weighted_overlap

NOT_AVAILABLE = "not available"


def read_tags(rows):
    """{d1_index: set of labels}. A label looks like 'smell: nutty' or 'rasa: sweet', so the two
    lists never mix. Ingredients with no label at all are left out."""
    tags = {}
    for row in rows:
        found = set()
        for column, kind in (("olfactory", "smell"), ("gustatory", "rasa")):
            for t in row[column].split("|"):
                t = t.strip()
                if t and t != NOT_AVAILABLE:
                    found.add("%s: %s" % (kind, t))
        if found:
            tags[row["index"]] = found
    return tags


def tag_idf(tags):
    """IDF per label over our own ingredients: a label on most of them weighs little."""
    count = {}
    for found in tags.values():
        for t in found:
            count[t] = count.get(t, 0) + 1
    n = len(tags)
    return {t: math.log(n / df) for t, df in count.items()}


class TagScorer:
    """Same two scores as MoleculeScorer, but on smell tags and rasa together."""

    def __init__(self, rows=None):
        rows = rows if rows is not None else read_d1()
        self.tags = read_tags(rows)
        self.weight = tag_idf(self.tags)

    def has(self, index):
        return index in self.tags

    def jaccard(self, i, j):
        return jaccard(self.tags.get(i, set()), self.tags.get(j, set()))

    def idf(self, i, j):
        return weighted_overlap(self.tags.get(i, set()), self.tags.get(j, set()), self.weight)

    def shared(self, i, j, top=5):
        common = self.tags.get(i, set()) & self.tags.get(j, set())
        return sorted(common, key=lambda t: (-self.weight.get(t, 0.0), t))[:top]


if __name__ == "__main__":
    # small self-check:  python D3_4_tag_scores.py
    rows = [{"index": 1, "olfactory": "green|earthy", "gustatory": "sweet"},
            {"index": 2, "olfactory": "green|nutty", "gustatory": "sweet|bitter"},
            {"index": 3, "olfactory": "not available", "gustatory": "not available"},
            {"index": 4, "olfactory": "green|earthy|nutty", "gustatory": "bitter"}]
    scorer = TagScorer(rows)
    checks = [("ingredient with only 'not available' has no tags", scorer.has(3), False),
              ("jaccard of 1 and 2: green and sweet shared, 5 labels in all = 2/5", round(scorer.jaccard(1, 2), 4), 0.4),
              ("idf of 'smell: green' (on all 3 ingredients) is 0", scorer.weight["smell: green"], 0.0),
              ("smell and rasa labels do not mix", "rasa: bitter" in scorer.tags[4] and "smell: bitter" not in scorer.tags[4], True),
              ("shared labels of 1 and 4, rarest first", scorer.shared(1, 4), ["smell: earthy", "smell: green"])]
    for label, got, want in checks:
        print("ok  " if got == want else "FAIL", label, got)
    real = TagScorer()
    print("ok  " if len(real.tags) > 240 else "FAIL", "ingredients with labels:", len(real.tags))
