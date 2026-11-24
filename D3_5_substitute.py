# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Compare two ingredients and rank substitutes by shared flavor (Deliverable 3)."""
from D3_1_load_compounds import load_ahn
from D3_2_match_names import build_matches, read_d1
from D3_3_scores import MoleculeScorer
from D3_4_tag_scores import TagScorer

METHODS = ("jaccard", "idf")
BASES = ("best", "auto", "molecular", "tags")


class Substituter:
    """Main entry point of Deliverable 3. Two scores can exist for a pair of ingredients:
    'molecular' = shared flavor compounds (Ahn et al., needs 5+ compounds on both sides) and
    'tags' = shared smell tags and rasa from Deliverable 1 (every ingredient has these).
    basis='best' (default) takes the higher of the two for each pair and says which one won.
    basis='auto' is the older rule: compounds if the ingredient has them, else tags.
    basis='molecular' or 'tags' uses only that score. A tag score is marked weaker."""

    def __init__(self):
        self.rows = {r["index"]: r for r in read_d1()}
        ahn, compound_names = load_ahn()
        matches = build_matches(list(self.rows.values()), ahn)
        self.molecules = MoleculeScorer(list(self.rows.values()), ahn, compound_names, matches)
        self.tags = TagScorer(list(self.rows.values()))
        # two rows linked to the same Ahn entry (cumin seeds / cumin powder) have identical compounds
        self.source = {i: m["ahn_name"] for i, m in matches.items() if m["ahn_name"]}
        self._search = None

    # ---- helpers -------------------------------------------------------
    def find(self, text, top_k=5):
        """Turns what a user typed into D1 indexes, using the Deliverable 2 search."""
        if self._search is None:
            from D2_5_search import IngredientSearch
            self._search = IngredientSearch()
        return self._search.search(text, top_k=top_k)

    def _scorer(self, basis):
        return self.molecules if basis == "molecular" else self.tags

    def _basis_for(self, index, basis):
        """Only used by basis='auto': compounds when the ingredient has them, else tags."""
        if basis == "auto":
            return "molecular" if self.molecules.has(index) else "tags"
        return basis

    def _score_pair(self, i, j, method):
        """Both scores for one pair. A score is None when one of the two has no data of that kind."""
        out = {"molecular": None, "tags": None}
        if self.molecules.has(i) and self.molecules.has(j):
            out["molecular"] = getattr(self.molecules, method)(i, j)
        if self.tags.has(i) and self.tags.has(j):
            out["tags"] = getattr(self.tags, method)(i, j)
        return out

    @staticmethod
    def _winner(scores):
        """The basis with the higher score. A tie goes to the compounds, which are measured data."""
        m, t = scores["molecular"], scores["tags"]
        if m is None and t is None:
            return None
        if t is None or (m is not None and m >= t):
            return "molecular"
        return "tags"

    def _rasa_overlap(self, i, j):
        """Shared tastes (rasa), used only to order equal scores."""
        a = set(self.rows[i]["gustatory"].split("|"))
        b = set(self.rows[j]["gustatory"].split("|"))
        return len(a & b) / len(a | b)

    def _same_source(self, i, j):
        return i in self.source and self.source.get(i) == self.source.get(j)

    def _info(self, index):
        row = self.rows[index]
        return {"index": index, "english_name": row["english_name"],
                "hindi_name": row["hindi_devanagari"], "rasa": row["gustatory"],
                "olfactory": [t for t in row["olfactory"].split("|") if t != "not available"]}

    # ---- the two public functions ----------------------------------------
    def compare(self, a, b, method="jaccard"):
        """Overlap of two ingredients (D1 indexes). The higher of the compound and tag score wins
        (chosen with `method`). Both scores are returned under 'molecular' and 'tags'."""
        both = {m: self._score_pair(a, b, m) for m in METHODS}
        basis = self._winner(both[method])
        out = {"a": self._info(a), "b": self._info(b), "basis": basis or "none", "weaker": basis != "molecular",
               "jaccard": None, "idf": None, "jaccard_percent": None, "idf_percent": None,
               "shared": [], "same_source": self._same_source(a, b), "molecular": None, "tags": None}
        for kind in ("molecular", "tags"):
            if both["jaccard"][kind] is not None:
                out[kind] = {"jaccard": round(both["jaccard"][kind], 4), "idf": round(both["idf"][kind], 4),
                             "shared": self._scorer(kind).shared(a, b)}
        if basis:
            win = out[basis]
            out.update({"jaccard": win["jaccard"], "idf": win["idf"], "shared": win["shared"],
                        "jaccard_percent": round(100 * win["jaccard"], 1), "idf_percent": round(100 * win["idf"], 1)})
        return out

    def substitutes(self, index, top_k=5, method="jaccard", basis="best", include_same_source=False, details=True):
        """Best replacements for one ingredient, best first. Candidates with a score of 0 are dropped.
        Equal scores are ordered by shared taste (rasa), then by name.
        details=False skips the shared lists and names (faster, used by the evaluation)."""
        if method not in METHODS or basis not in BASES:
            raise ValueError("method must be one of %s and basis one of %s" % (METHODS, BASES))
        found = []
        for other in self.rows:
            if other == index:
                continue
            same = self._same_source(index, other)
            if same and not include_same_source:
                continue
            scores = self._score_pair(index, other, method)
            if basis == "best":
                use = self._winner(scores)
            elif basis == "auto":
                use = self._basis_for(index, "auto")
            else:
                use = basis
            score = scores.get(use) if use else None
            if score:
                found.append((score, self._rasa_overlap(index, other), other, same, use, scores))
        found.sort(key=lambda t: (-t[0], -t[1], self.rows[t[2]]["english_name"]))
        results = []
        for score, _, other, same, use, scores in found[:top_k]:
            item = {"index": other, "score": round(score, 4), "percent": round(100 * score, 1), "method": method,
                    "basis": use, "weaker": use == "tags", "same_source": same,
                    "score_molecular": None if scores["molecular"] is None else round(scores["molecular"], 4),
                    "score_tags": None if scores["tags"] is None else round(scores["tags"], 4)}
            if details:
                item.update(self._info(other))
                item["shared"] = self._scorer(use).shared(index, other)
                item["shared_compounds"] = self.molecules.shared(index, other) if scores["molecular"] is not None else []
                item["shared_tags"] = self.tags.shared(index, other) if scores["tags"] is not None else []
            results.append(item)
        return results


if __name__ == "__main__":
    # small self-check:  python D3_5_substitute.py
    sub = Substituter()
    by_name = {r["english_name"]: i for i, r in sub.rows.items()}
    cumin_seeds, cumin_powder, tomato, tofu = (by_name[n] for n in ("cumin seeds", "cumin powder", "tomato", "tofu"))
    both = sub.compare(cumin_seeds, cumin_powder)
    print("ok  " if both["jaccard"] == 1.0 and both["same_source"] else "FAIL", "cumin seeds vs cumin powder:", both["jaccard_percent"], "%")
    top = sub.substitutes(tomato, top_k=5, method="jaccard")
    scores = [r["score"] for r in top]
    print("ok  " if len(top) == 5 and scores == sorted(scores, reverse=True) else "FAIL", "tomato: 5 results, best first")
    print("ok  " if all(r["index"] != tomato for r in top) else "FAIL", "no self in the list")
    print("ok  " if not any(r["same_source"] for r in top) else "FAIL", "same-source rows hidden by default")
    higher = all(r["score"] == max(s for s in (r["score_molecular"], r["score_tags"]) if s is not None) for r in top)
    print("ok  " if higher else "FAIL", "best basis: each score is the higher of the compound and tag score")
    weak = sub.substitutes(tofu, top_k=3)
    print("ok  " if weak and all(r["basis"] == "tags" and r["weaker"] for r in weak) else "FAIL", "tofu has no compounds: tag basis, marked weaker")
    mol_only = sub.substitutes(tomato, top_k=3, basis="molecular")
    print("ok  " if mol_only and all(r["basis"] == "molecular" for r in mol_only) else "FAIL", "basis='molecular' uses compounds only")
    print("ok  " if sub.substitutes(tomato, method="idf") != top else "FAIL", "idf ranking differs from jaccard")
    print("ok  " if sub.find("jeera")[0]["english_name"] else "FAIL", "typed 'jeera' found through the D2 search")
