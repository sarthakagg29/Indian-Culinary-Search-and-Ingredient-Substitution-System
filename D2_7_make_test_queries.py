# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""
Queries from the dataset and the typos are made by this script with a fixed seed, so the file can be rebuilt.
Spellings, recipe phrases and no-match words are written by hand. For these, needs_review is not typed in:
the search (D2_5) is run on each query. If its top result is a correct answer (or, for a no-match word,
it returns nothing), needs_review = no. Otherwise needs_review = yes, so a person can look at that row."""

import collections
import csv
import random
import string

from D2_1_normalize import normalize
from D2_2_levenshtein import edit_distance
from D2_3_lookup import NOT_AVAILABLE, build_exact_index, load_ingredients
from D2_5_search import IngredientSearch

SEED = 26
OUT = "D2_7_test_queries.csv"
RECIPES = "D1_input_make_test_queries_26_Assignment_3_raw_input.csv"
LETTERS = string.ascii_lowercase

# Roman spellings that are NOT in the dataset (written by hand): query, ingredients it should find
ALT_SPELLINGS = [
    ("jira", ["cumin seeds"]), ("zeera", ["cumin seeds"]), ("zira", ["cumin seeds"]),
    ("lasan", ["garlic"]), ("lahsun", ["garlic"]), ("lehsan", ["garlic"]), ("lasun", ["garlic"]),
    ("pyaz", ["onion"]), ("piyaz", ["onion"]), ("pyaj", ["onion"]),
    ("haldi", ["turmeric powder", "fresh turmeric"]),
    ("dhaniya", ["coriander leaves", "coriander seeds", "coriander powder"]),
    ("dhania", ["coriander leaves", "coriander seeds", "coriander powder"]),
    ("hari mirchi", ["green chilies"]), ("aaloo", ["potato"]), ("gobi", ["cauliflower"]),
    ("phool gobhi", ["cauliflower"]), ("desi ghee", ["ghee"]), ("elachi", ["cardamom pods"]),
    ("dal chini", ["cinnamon stick"]), ("lavang", ["cloves"]), ("kaali mirchi", ["black pepper corns"]),
    ("tamater", ["tomato"]), ("bhendi", ["okra"]), ("nimboo", ["lemon"]), ("dahee", ["curd"]),
    ("dood", ["milk"]), ("chaawal", ["white rice"]), ("atta", ["wheat flour"]), ("beson", ["gram flour"]),
    ("heeng", ["asafoetida"]), ("ajwayan", ["carom seeds"]), ("ajvain", ["carom seeds"]),
    ("sonf", ["fennel seeds", "mouth-freshener fennel seeds"]), ("kajoo", ["cashew nuts"]),
    ("baadam", ["almonds"]), ("gur", ["jaggery"]), ("shakkar", ["sugar"]), ("mutter", ["green peas"]),
    ("rajmah", ["kidney beans"]), ("chhole", ["white chickpeas"]), ("zafran", ["saffron strands"]),
    ("pudeena", ["fresh peppermint leaves"]), ("kerela", ["bitter gourd"]), ("louki", ["bottle gourd"]),
    ("gaajar", ["carrot"]), ("sabu dana", ["tapioca pearls"]),
    ("adrak", ["ginger paste", "ginger juice", "dry ginger powder"]),
]

# Real phrases from the 10,000 recipes that are not in the dataset (matched to a row by hand)
RECIPE_PHRASES = [
    ("turmeric", ["turmeric powder", "fresh turmeric"]), ("green chilli", ["green chilies"]),
    ("ground black pepper", ["black pepper powder"]), ("black pepper", ["black pepper corns", "black pepper powder"]),
    ("mustard seeds", ["black mustard seeds", "yellow mustard seeds"]), ("lemon juice", ["lemon"]),
    ("dry red chilli", ["dried red chilies"]), ("cardamom", ["cardamom pods", "cardamom powder", "black cardamom"]),
    ("cinnamon", ["cinnamon stick", "cinnamon powder"]), ("fresh coconut", ["coconut"]),
    ("potatoes", ["potato"]), ("egg", ["eggs"]), ("mint leaves", ["fresh peppermint leaves"]),
    ("cashew nut", ["cashew nuts"]), ("almond", ["almonds"]), ("spinach", ["spinach leaves", "spinach powder"]),
    ("mustard oil", ["yellow mustard oil"]), ("dry mango powder", ["dried mango powder"]),
    ("green onions", ["spring onion"]), ("carrots", ["carrot"]), ("tomatoes", ["tomato"]),
    ("onions", ["onion"]), ("pistachio", ["pistachios"]), ("black peppercorns", ["black pepper corns"]),
    ("ripe bananas", ["banana"]), ("bananas", ["banana"]), ("strained yogurt", ["hung yogurt"]),
    ("shrimp", ["prawns"]), ("fenugreek leaves", ["fresh fenugreek leaves", "dried fenugreek leaves"]),
    ("fresh cilantro", ["coriander leaves"]), ("split pigeon peas", ["split pigeon pea"]),
    ("split and skinned black gram", ["split skinned black gram"]),
    ("kashmiri red chilli powder", ["red chilli powder"]), ("whole wheat flour", ["wheat flour"]),
    ("refined wheat flour", ["refined flour"]), ("unsalted butter", ["butter"]),
    ("cherry tomatoes", ["cherry tomato"]), ("pearl onions", ["pearl onion"]),
    ("extra virgin olive oil", ["virgin olive oil"]), ("nutmeg powder", ["nutmeg"]),
    ("roasted peanuts", ["peanuts"]), ("raw peanuts", ["peanuts"]),
    ("ginger garlic paste", ["ginger paste", "garlic paste"]), ("yellow onion", ["onion"]),
    ("red onion", ["onion"]), ("spring onion greens", ["spring onion"]),
]

# Things that are NOT in the dataset: the search should return nothing
NO_MATCH = ["xyzabc", "qwerty", "asdfgh", "zzzzzz", "q", "12345", "hello world", "laptop", "football",
            "ज्ञ्झ", "कंप्यूटर", "मोबाइल",
            "pizza", "chocolate", "sushi", "noodles", "vanilla extract", "baking powder",
            "worcestershire sauce", "ground beef", "bacon", "mayonnaise", "ketchup", "paprika",
            "dried oregano"]


def single_edit(s, rng):
    """One drop, insert or change of a letter, never the first or last letter."""
    i = rng.choice([k for k in range(1, len(s) - 1) if s[k] != " "])
    kind = rng.choice(["delete", "insert", "change"])
    if kind == "delete":
        return s[:i] + s[i + 1:]
    if kind == "insert":
        return s[:i] + rng.choice(LETTERS) + s[i:]
    return s[:i] + rng.choice(LETTERS.replace(s[i], "")) + s[i + 1:]


def swap_letters(s, rng):
    spots = [k for k in range(1, len(s) - 2) if s[k] != " " and s[k + 1] != " " and s[k] != s[k + 1]]
    if not spots:
        return s
    i = rng.choice(spots)
    return s[:i] + s[i + 1] + s[i] + s[i + 2:]


def make_typo(name, distance, rng, exact_index):
    """A misspelling of name that is exactly `distance` edits away and is not itself a real name."""
    for _ in range(100):
        typo = name
        if distance == 2 and rng.random() < 0.4:
            typo = swap_letters(name, rng)                  # two letters swapped counts as 2 edits
        else:
            for _ in range(distance):
                typo = single_edit(typo, rng)
        if typo != name and typo not in exact_index and edit_distance(typo, name) == distance:
            return typo
    return None


def main():
    rng = random.Random(SEED)
    ingredients = load_ingredients()
    exact = build_exact_index(ingredients)
    by_english = {rec["english_name"]: i for i, rec in ingredients.items()}
    engine = IngredientSearch()
    rows = []

    def check(query, ids):
        """'no' if the search already gives the expected answer, else 'yes' (a person should look)."""
        top = engine.search(query, top_k=1)
        if not ids:                                         # a no-match word: the search should return nothing
            return "yes" if top else "no"
        return "no" if top and top[0]["index"] in ids else "yes"

    def add(query, qtype, ids, source, review="no"):
        rows.append({"query_id": f"Q{len(rows) + 1:03d}", "query": query, "query_type": qtype,
                     "correct_indexes": "|".join(str(i) for i in sorted(ids)),
                     "correct_names": "|".join(ingredients[i]["english_name"] for i in sorted(ids)),
                     "source": source, "needs_review": review})

    # names of each kind, per ingredient
    english, roman, hindi = {}, {}, {}
    for i, rec in ingredients.items():
        hindi_name = normalize(rec["hindi"]) if rec["hindi"] != NOT_AVAILABLE else None
        english[i] = rec["names"][0]
        roman[i] = [n for n in rec["names"][1:] if n != hindi_name]
        if hindi_name:
            hindi[i] = hindi_name
    ids = sorted(ingredients)

    # 1. English names
    for i in rng.sample(ids, 30):
        add(english[i], "english_exact", exact[english[i]], "english_name in the dataset")
    # 2. Roman variants (one per ingredient)
    for i in rng.sample([k for k in ids if roman[k]], 40):
        name = rng.choice(roman[i])
        add(name, "roman_exact", exact[name], "roman_variants in the dataset")
    # 3. Hindi names (a name shared by two rows is correct for both)
    for i in rng.sample(sorted(hindi), 40):
        add(hindi[i], "hindi_exact", exact[hindi[i]], "hindi_devanagari in the dataset")
    # 4. Hindi names that are written with a nukta: query without it
    for i in sorted(hindi):
        if "़" in ingredients[i]["hindi"]:
            add(ingredients[i]["hindi"].replace("़", ""), "hindi_nukta", exact[hindi[i]],
                "hindi name with the nukta taken out")
    # 5. Capital letters, extra spaces, hyphens, punctuation
    for n, i in enumerate(rng.sample(ids, 12)):
        name = english[i]
        kind = n % 4
        query = [name.upper(), "  " + name + "  ", name.replace(" ", "-") if " " in name else name + "!",
                 name.title() + "."][kind]
        add(query, "format_noise", exact[name], "dataset name with changed case, spaces or punctuation")
    # 6. Prefixes (about 60% of a name)
    for i in rng.sample([k for k in ids if len(english[k]) >= 6], 30):
        name = english[i]
        add(name[:max(4, round(len(name) * 0.6))].rstrip(), "prefix", [i], "first letters of the english_name")
    # 7. Typos: one edit (names with 5+ letters), two edits (names with 7+ letters)
    pool = [(i, n) for i in ids for n in [english[i]] + roman[i] if len(n) >= 5]
    for distance, count in ((1, 40), (2, 30)):
        # two edits on a 5-letter word leave nonsense, so that group uses names of 7 or more letters
        candidates = [(i, n) for i, n in pool if len(n) >= (7 if distance == 2 else 5)]
        for i, name in rng.sample(candidates, count):
            typo = make_typo(name, distance, rng, exact)
            if typo:
                add(typo, f"typo_{distance}", exact[name], f"'{name}' with {distance} edit(s), seed {SEED}")
    # 8. Typos in Hindi: one letter or vowel sign dropped
    hindi_pool = [(i, h) for i, h in hindi.items() if len(h) >= 4]
    made = 0
    for i, name in rng.sample(hindi_pool, len(hindi_pool)):
        pos = [k for k in range(1, len(name) - 1) if name[k] != " "]
        typo = name[:(k := rng.choice(pos))] + name[k + 1:]
        if typo not in exact and made < 25:
            add(typo, "hindi_typo", exact[name], f"'{name}' with one character dropped")
            made += 1
    # 9. Roman spellings not in the dataset, written by hand
    for query, names in ALT_SPELLINGS:
        if normalize(query) in exact:
            print("dropped (already in the dataset):", query)
            continue
        ids_ = [by_english[n] for n in names]
        add(query, "alt_spelling", ids_, "written by hand", check(query, ids_))
    # 10. Real phrases from the recipe file
    counts = collections.Counter()
    with open(RECIPES, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            text = row["Ingredients_List"].strip().strip("[]")
            counts.update({p.strip().lower() for p in text.split(",") if p.strip()})
    for query, names in RECIPE_PHRASES:
        if normalize(query) in exact:
            print("dropped (already in the dataset):", query)
            continue
        ids_ = [by_english[n] for n in names]
        add(query, "recipe_phrase", ids_,
            f"recipe file, in {counts[query]} recipes; matched by hand", check(query, ids_))
    # 11. Nothing should match
    for query in NO_MATCH:
        add(query, "no_match", [], "not an ingredient in the dataset", check(query, []))

    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} queries to {OUT}")
    for qtype, n in collections.Counter(r["query_type"] for r in rows).items():
        print(f"  {qtype:<14}{n}")
    print("  needs_review = yes:", sum(r["needs_review"] == "yes" for r in rows))


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()