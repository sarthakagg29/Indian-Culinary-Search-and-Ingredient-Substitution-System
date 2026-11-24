# Sarthak Aggarwal
# MT26139
"""Ingredient search: exact match, then prefix (trie), then fuzzy (Levenshtein).

    engine = IngredientSearch()
    engine.search("zeera")      -> list of matches, best first
    engine.suggest("jee")       -> names for an autocomplete box
"""
from D2_1_normalize import normalize
from D2_2_levenshtein import edit_distance      # edit_distance(a, b) -> int
from D2_3_lookup import build_exact_index, exact_lookup, load_ingredients
from D2_4_trie import Trie

MIN_PREFIX_LEN = 2          # shorter queries are too vague for 'starts with'
MIN_FUZZY_LEN = 3           # shorter queries are too vague for typo matching
MIN_SIMILARITY = 0.7        # fuzzy matches below this are dropped (1.0 = identical)


class IngredientSearch:
    def __init__(self, csv_path=None):
        self.ingredients = load_ingredients(csv_path)
        self.exact_index = build_exact_index(self.ingredients)
        self.trie = Trie()
        for index, record in self.ingredients.items():
            for name in record["names"]:
                self.trie.insert(name, index)

    def search(self, query, top_k=5):
        """Return up to top_k matches, best first. Each match is a dict with
        index, english_name, hindi_name, score (0 to 1), match_type and matched_name."""
        q = normalize(query)
        if not q:
            return []
        found = {}                                   # ingredient index -> its best match so far

        def keep(index, score, match_type, name):
            if index not in found or score > found[index]["score"]:
                record = self.ingredients[index]
                found[index] = {"index": index, "english_name": record["english_name"],
                                "hindi_name": record["hindi"], "score": round(score, 3),
                                "match_type": match_type, "matched_name": name}

        for index in exact_lookup(self.exact_index, q):              # 1. exact
            keep(index, 1.0, "exact", q)
        if len(q) >= MIN_PREFIX_LEN:                                 # 2. prefix
            for name, index in self.trie.with_prefix(q):
                keep(index, 0.6 + 0.3 * len(q) / len(name), "prefix", name)
        if not exact_lookup(self.exact_index, q) and len(q) >= MIN_FUZZY_LEN:   # 3. fuzzy, only if no exact match
            self._fuzzy(q, keep)

        ranked = sorted(found.values(), key=lambda m: (-m["score"], m["english_name"]))
        return ranked[:top_k]

    def _fuzzy(self, q, keep):
        for index, record in self.ingredients.items():
            for name in record["names"]:
                sim = self._similarity(q, name)
                if sim >= MIN_SIMILARITY:
                    keep(index, 0.6 * sim, "fuzzy", name)
                if " " not in q:                     # one typed word: also compare with each word of the name
                    for word in name.split():
                        if len(word) >= MIN_FUZZY_LEN:
                            sim = self._similarity(q, word)
                            if sim >= MIN_SIMILARITY:
                                keep(index, 0.6 * sim, "fuzzy", word)

    @staticmethod
    def _similarity(a, b):
        return 1 - edit_distance(a, b) / max(len(a), len(b))

    def suggest(self, prefix, limit=8):
        """English names of ingredients with a name starting with prefix (uses the trie only)."""
        q = normalize(prefix)
        if not q:
            return []
        names = {self.ingredients[i]["english_name"] for _, i in self.trie.with_prefix(q)}
        return sorted(names)[:limit]
