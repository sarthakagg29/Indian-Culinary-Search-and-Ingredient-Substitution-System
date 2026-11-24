# CGAS Group 26: Molecular Flavor Match and Substitution Calculator (Deliverable 3)

Team: Sarthak Aggarwal (MT26139) and Divyanshu Joshi (MT26120).

This part compares two ingredients by the flavor they share and suggests substitutes. Give it two ingredients and it returns a percentage overlap. Give it one and it returns a ranked list of replacements. It works on the 250 ingredients from Deliverable 1, and it uses the search from Deliverable 2 so that a user can type `jeera`, `जीरा` or `cumin`.

Every pair of ingredients gets two scores. One comes from shared flavor compounds (Ahn data, only for ingredients that have them). The other comes from the smell tags and taste (rasa) labels of Deliverable 1, which all 250 ingredients have. Each score is a Jaccard and an IDF-weighted overlap. The higher of the two wins, and the result says which one won. A tag win is marked as weaker, because tags are short labels and not measured molecules.

## Files
Numbers show the build order. A file only imports files with a lower number.

| Step | File | What it does |
|---|---|---|
| input | `D1_input_lookup_ingredient_250_final_dataset.csv` | The Deliverable 1 dataset, copied unchanged |
| input | `D2_1_normalize.py` to `D2_5_search.py` | The Deliverable 2 search, copied unchanged. Only `IngredientSearch` is used |
| input | `Ahn_input_D3_1_load_compounds_*.tsv` (3 files) | Flavor compound data from Ahn et al. (see Sources) |
| 1 | `D3_1_load_compounds.py` | Reads the Ahn files: which compounds each ingredient has |
| 2 | `D3_2_match_names.py` | Links each of our 250 ingredients to an Ahn ingredient. Writes `D3_2_matches.csv` |
| 2 | `D3_2_synonyms.csv` | Hand-made name links (`beetroot` to `beet`). Fix wrong links here |
| 3 | `D3_3_scores.py` | Jaccard overlap and IDF-weighted overlap on shared compounds |
| 4 | `D3_4_tag_scores.py` | The same two scores on smell tags and rasa together, for all 250 ingredients |
| 5 | `D3_5_substitute.py` | `Substituter`: `compare(a, b)` and `substitutes(index, top_k)`. The higher of the compound and tag score wins |
| 6 | `D3_6_gold_pairs.csv` | Known Indian swaps (192 pairs), written by hand |
| 7 | `D3_7_evaluate.py` | Tests compounds, tags and the higher of the two. Saves `D3_7_evaluation_results.csv`, `D3_7_evaluation_summary.csv` and the review sheet `D3_7_win_review.csv` |
| 8 | `D3_8_demo.py` | Prints example substitutes and one comparison |
| 9 | `D3_9_analysis.ipynb` | Charts and tables from the results |

## How to run
Run from this folder, in the order below. Only Python 3 is needed for the scoring (use `python3` if `python` does not work on your computer). The notebook also needs pandas and matplotlib. `D3_6_gold_pairs.csv` is the answer key, a data file with nothing to run.

1. Self-checks, in build order. Each prints `ok` or `FAIL`. `D3_2_match_names.py` also rebuilds `D3_2_matches.csv`.
```
python D3_1_load_compounds.py
python D3_2_match_names.py
python D3_3_scores.py
python D3_4_tag_scores.py
python D3_5_substitute.py
```
2. Evaluation. It saves `D3_7_evaluation_results.csv` and `D3_7_evaluation_summary.csv`. The review sheet `D3_7_win_review.csv` is created only if it does not exist yet, so answers already filled in are never overwritten. `check` runs only the small self-check.
```
python D3_7_evaluate.py
python D3_7_evaluate.py check
```
3. Demo.
```
python D3_8_demo.py
python D3_8_demo.py jeera tomato aam
python D3_8_demo.py compare jeera dhaniya
```
4. Charts and tables: open `D3_9_analysis.ipynb` with `jupyter notebook` and choose Run All. Do step 2 first so the result files are up to date.

In code:
```python
from D3_5_substitute import Substituter
sub = Substituter()
sub.compare(a, b)                       # a and b are Deliverable 1 indexes
sub.substitutes(a, top_k=5, method="jaccard")   # or method="idf"
sub.substitutes(a, basis="molecular")           # compounds only; basis="tags" for tags only; default is "best"
sub.find("jeera")                       # turns typed text into indexes (Deliverable 2)
```
Each result has `index`, `english_name`, `hindi_name`, `score` (0 to 1), `percent`, `method`, `basis` (`molecular` or `tags`: which score won), `weaker`, `score_molecular`, `score_tags`, `shared` (from the winning side), `shared_compounds`, `shared_tags`, `rasa` and `olfactory`.

## How it works
1. **Compounds.** `D3_1` reads which flavor compounds each ingredient has in the Ahn data (1,530 ingredients, 1,107 compounds).
2. **Linking.** `D3_2` links our 250 ingredients to Ahn ingredients, in this order: the hand-made synonym file, the English name (with form words such as powder, paste or seeds removed), the Roman variants, the scientific name, and last a close spelling match using the Levenshtein code from Deliverable 2. Rows linked by variant, scientific name or spelling are marked `check` in `D3_2_matches.csv` so they can be read by hand.
3. **Scores.** For two ingredients A and B with compound sets:
   - Jaccard = shared compounds / all compounds in either set.
   - IDF-weighted overlap = the same, but each compound counts as log(N / df) instead of 1, where N is the number of Ahn ingredients and df is how many contain that compound. A compound found in almost every ingredient counts for little. The weights come from the whole Ahn data, not only our 250.
   - The percentage shown to the user is the score times 100.
4. **Tags.** `D3_4` gives each ingredient one label set: its smell tags and its rasa labels (`smell: nutty`, `rasa: sweet`), scored together with the same two formulas. IDF weights come from our own 250 ingredients. A compound score needs at least 5 compounds on both sides, because an overlap of one or two compounds says very little.
5. **Higher score wins.** For each pair, `substitutes()` computes the compound score (if both have compounds) and the tag score, keeps the higher one and records which won. A tie goes to the compounds. Results where the tags won are marked `weaker`.
6. **Substitutes.** `substitutes()` scores every other ingredient this way and sorts by the winning score. Equal scores are ordered by shared taste, then by name. Candidates with a score of 0 are dropped. Rows that link to the same Ahn ingredient (cumin seeds and cumin powder, or the chilli rows) have identical compounds, so they are hidden from each other's lists unless `include_same_source=True`.

## Results so far
- 175 of 250 ingredients link to an Ahn ingredient. 151 of those have at least 5 compounds and get a compound score. The other 98 can only be scored on tags, and 1 has no data at all.
- Jaccard and IDF-weighted overlap give nearly the same top substitutes (on average 4.3 of the top 5 are shared).
- Category check (no hand-made list needed): does a top substitute share the Ahn food category? On 141 ingredients, Hit@1 is 0.67 for Jaccard and 0.66 for IDF, against 0.12 for a random order. On the test half, IDF has a slightly higher MRR (0.747 against 0.739). The tuning half picked IDF, and the difference is small. The check is rough, because a shared category is not the same as a good swap.
- Compounds against tags, on the same 141 ingredients (category check, Hit@1 / Hit@5): compounds 0.67 / 0.77 (Jaccard) and 0.66 / 0.79 (IDF); tags 0.60 / 0.82 (Jaccard) and 0.66 / 0.85 (IDF); random 0.12 / 0.45. Tags do as well as compounds on this rough check, but they pick different substitutes.
- Who wins: over 11,214 pairs that have both scores, the tag score is higher in 5,327 pairs, the compound score in 5,179, and 708 tie (Jaccard). For the top substitute of an ingredient, the tags win for 135 of 151 ingredients. Tag scores sit on a coarser scale (few labels, many equal values), so they reach high percentages more easily. Whether a win is a good win is checked by hand in `D3_7_win_review.csv` (40 ingredients, a `good_win` column to fill).
- Known swaps (192 hand-written pairs, how often the real substitute is in the top 5, Hit@5): tags 0.26, higher-score-wins 0.26, compounds only 0.04. The compounds-only number is low because it can only answer for ingredients that have compounds, and many known swaps involve ingredients that do not. Hit@1 is about 0.10 for tags and for higher-score-wins. A random order would put a swap in the top 5 about 2% of the time.
- Human review of winners (40 ingredients, `D3_7_win_review.csv`): when the tag score won, 8 of 33 winning substitutes were judged good. When the compound score won, 6 of 7. Tag scores often reach 100% with a few shared labels, so a tag win is a weak sign of a good swap. Compound wins were few, so this is a small sample.

## Sources
- Ahn, Ahnert, Bagrow and Barabasi, "Flavor network and the principles of food pairing", Scientific Reports 1:196 (2011). Ingredient to compound data.
- The three `.tsv` files are a copy of that data from the GitHub repository `lingcheng99/Flavor-Network` (GPL-3.0). Check the licence of the original release before sharing the data further.
- Smell tags and taste labels: Deliverable 1. The smell tags use the FlavorDB smell vocabulary and the taste labels come from Ayurvedic rasa, both written with AI help. This is the weaker data, and it is why tag scores are marked as weaker.
