# CGAS Group 26: Indian ingredient dataset (Deliverable 1)

Team: Sarthak Aggarwal (MT26139) and Divyanshu Joshi (MT26120).

This part of the project is the dataset that the search (Deliverable 2) and the substitution calculator (Deliverable 3) read. It holds 250 Indian cooking ingredients. Each one has an English name, Roman spellings, a Hindi name, taste (rasa) labels, smell labels and a scientific name. It also holds a category for each ingredient, and the analyses we ran on the dataset.

## How the 250 ingredients were chosen
1. **First list.** The notebook `D1_1_list_building.ipynb` reads a dataset of 725 dishes (`D1_input_dishes_725.zip`), keeps the 523 dishes with an Indian label, cleans the ingredient names with written rules (R1 to R14), counts the dishes each ingredient appears in and takes the top ones.
2. **More ingredients.** The rest were chosen by us from the 10,000 recipes (`D1_input_recipes_10000.csv`). For each candidate we searched the internet to check that it is really used in Indian cooking.
3. **By hand.** English names, Roman spellings and Hindi names were collected and checked by hand. Doubles and typos were removed.
4. **Final file.** `D1_0_ingredient_250_final_dataset.csv`, sorted by English name, 250 rows.

## The dataset columns
| Column | What it holds |
|---|---|
| `english_name` | Lowercase name, unique. Forms of one ingredient are separate rows (`garlic paste`, `green garlic`) |
| `index` | Row number 1 to 250 after sorting |
| `roman_variants` | Other spellings in English letters, joined with `\|` (for example `jeera`) |
| `hindi_devanagari` | Hindi name in Devanagari |
| `olfactory` | 1 to 3 smell labels (the 35 below), or `not available` |
| `gustatory` | 1 to 2 taste labels (the 7 below), or `not available` |
| `scientific_name` | Genus and species, or `not applicable` for salt, water, baking soda, black salt and vinegar |

The full rules are in `data_dictionary.md`.

## The 7 taste (gustatory) labels
Ayurveda describes six tastes (rasa). We took them from the *Ashtanga Hridayam* of Vagbhata, together with Ayurvedic general knowledge of which foods have which taste. We added a seventh label, umami, because everyday cooking has a savory taste that the six do not cover.

| Label | Ayurvedic name | Ingredients using it |
|---|---|---|
| sweet | madhura | 152 |
| sour | amla | 25 |
| salty | lavana | 6 |
| pungent | katu | 72 |
| bitter | tikta | 45 |
| astringent | kashaya | 54 |
| umami | added by us | 21 |

An ingredient has 1 or 2 of these. 2 ingredients have no taste label (`not available`). There are other dimensions that for this mini project we have not explored like *Guna*, *vikalpa*, etc.

## The 35 smell (olfactory) labels
These come from Ayurvedic general knowledge. The word list started from the FooDB smell vocabulary (35 labels).
anise (5), bready (21), camphor (7), caramel (17), citrus (17), cooked (28), creamy (20), cucumber (6), earthy (65), fatty (20), fermented (11), fishy (9), floral (9), fresh (33), fruity (30), garlic (5), grassy (12), green (86), herbal (19), honey (6), meaty (6), mild (24), milky (12), minty (4), mustard (7), musty (10), nutty (51), onion (7), pepper (18), roasted (13), spicy (29), sulfurous (17), tropical (8), vegetable (25), woody (26)

An ingredient has 1 to 3 of these. 5 ingredients have no smell of their own (salt, sugar, water, baking soda, rock sugar) and are marked `not available`. The allowed labels are in `D1_0_tag_vocabulary.csv`, and `D1_4_validate.py` reads that file to check every row.

## The 13 categories
Every ingredient has one of 13 categories in `D1_0_ingredient_categories.csv`, and each category belongs to a parent group. The categories are our own coarse groups. 

| Category | Ingredients | Parent group |
|---|---|---|
| vegetable | 69 | plant_based |
| spice | 39 | plant_based |
| cereal_grain | 27 | plant_based |
| fruit | 22 | plant_based |
| legume | 18 | plant_based |
| nut_seed | 13 | plant_based |
| herb | 13 | plant_based |
| oil_fat | 6 | plant_based |
| dairy | 13 | animal_based |
| seafood | 9 | animal_based |
| meat_poultry | 6 | animal_based |
| condiment_other | 11 | processed_or_other |
| sweetener | 4 | processed_or_other |

Parent groups: plant_based 207, animal_based 28, processed_or_other 15.

## Files
Numbers show the order of the work. `D1_input_` files are raw inputs. Deliverables 2 and 3 use a copy of `D1_0_ingredient_250_final_dataset.csv`.

| Step | File | What it does |
|---|---|---|
| input | `D1_input_dishes_725.zip` | The 725-dish dataset used for the first list |
| input | `D1_input_recipes_10000.csv` | The 10,000 recipes (columns `Recipe_ID`, `Ingredients_List`) |
| 0 | `D1_0_ingredient_250_final_dataset.csv` | The dataset |
| 0 | `D1_0_tag_vocabulary.csv` | The allowed taste and smell labels, with how many ingredients use each |
| 0 | `D1_0_ingredient_categories.csv` | Category and parent group of each ingredient |
| 1 | `D1_1_list_building.ipynb` | Builds the first list from the 725 dishes, with the cleaning rules. Also a repetition check on the final dataset |
| 2 | `D1_2_scientific_draft.csv` | The drafted scientific names |
| 2 | `D1_2_gbif_check.py`, `D1_2_gbif_check.csv` | Checks scientific names against GBIF. Needs internet |
| 3 | `D1_3_dedupe_synonyms.py` | Finds ingredients that are the same under different names (hash map and Union-Find) |
| 4 | `D1_4_validate.py` | Checks every row of the dataset |
| 5 | `D1_5_taste_clustering.ipynb` | Clusters ingredients by their tags and compares with the categories |
| 6 | `D1_6_variant_mining.ipynb` | Compares our spellings with the 10,000 recipes |
| 6 | `D1_6_coverage_check.csv` | The 250 most frequent recipe phrases, each marked covered or missing in our dataset. `strict_match` means the phrase is an exact match to one of our ingredient names or spellings. `loose_match` also accepts a partial match, where the words overlap or one word is left out |
| 7 | `D1_7_substitutes_ground_truth.csv` | 38 substitution pairs for testing the similarity score.  |
| doc | `data_dictionary.md`  | Column rules, and the quality numbers |

## How to run
Run everything from this folder, in the order below. Python 3 is needed (use `python3` if `python` does not work on your computer). The notebooks also need pandas, numpy and matplotlib. Open a notebook with `jupyter notebook` and choose Run All.

1. `D1_1_list_building.ipynb` (notebook): reads the 725-dish zip and writes `D1_1_first_list.csv`.
2. Check the scientific names against GBIF. This needs internet, and `--limit 5` checks only the first 5 rows.
3. Find ingredients that are the same under different names. `--demo` shows the merge on two extra test rows.
4. Validate every row of the dataset.
```
python D1_2_gbif_check.py --limit 5
python D1_3_dedupe_synonyms.py
python D1_3_dedupe_synonyms.py --demo
python D1_4_validate.py
```
5. `D1_5_taste_clustering.ipynb` (notebook): clusters the ingredients by their tags.
6. `D1_6_variant_mining.ipynb` (notebook): compares our spellings with the 10,000 recipes.

## Analyses on Deliverable 1
**Validation (`D1_4_validate.py`).** 15 checks on every row: names, spellings, Hindi, taste and smell labels, scientific name, index and order. 249 of 250 rows pass. One row fails: `green moong dal` is a spelling on both `mung bean` and `green gram sprouts`. `D1_3_dedupe_synonyms.py` reports the same pair.

**Do the tags carry information? (`D1_5_taste_clustering.ipynb`).** Each ingredient becomes a 0/1 vector over the 7 taste and 35 smell labels. We cluster the vectors with k-means (written with numpy) and compare the clusters with the 13 categories using purity: for each cluster take its most common category, add the counts and divide by all ingredients. As a check, the categories are shuffled at random 200 times. Water has no labels and is left out, so 249 ingredients are clustered.

| Clusters (k) | Purity | Purity with shuffled categories |
|---|---|---|
| 5 | 0.50 | 0.28 |
| 8 | 0.56 | 0.29 |
| 10 | 0.61 | 0.29 |
| 13 | 0.62 | 0.30 |

The clusters are far better than chance, so the labels carry real signal. Meat, seafood, nuts, pulses, fruit and dairy each end up mostly in one or two clusters. Spices spread over several clusters, because different spices smell very different. Vegetables and grains blur together, since they share labels such as green, earthy, mild and cooked.

**How the 10,000 recipes were used (`D1_6_variant_mining.ipynb`).** The recipes were used in three ways: to add ingredients to the list (above), to test whether the Roman spellings in our dataset are used in real recipes, and to find spellings we missed.
- Every ingredient phrase in the 10,000 recipes is read. There are 5,309 different phrases. Every English name and Roman variant of our dataset (885 spellings) points to its ingredient in one dictionary, so each phrase needs one lookup.
- 192 of our 250 ingredients (77%) appear in at least one recipe. 58 never appear, among them `kohlrabi`, `hilsa`, `pomfret`, `kapok buds` and `dried mango powder`.
- Matching by English name gives 43,108 hits in recipes and matching by a Roman variant gives 2,712 (a recipe counts once per phrase). So the variant column matches how recipes are really written, for example `eggplant`, `paneer`, `zucchini`.
- 218 frequent phrases (in at least 40 recipes) match nothing in our list. For each one the notebook suggests the closest ingredient by shared words (Jaccard score) and saves the table as `D1_6_variant_mining_missed.csv`. Plain `turmeric`, `ginger` and `green chilli` are the first candidates for new variants. A person decides whether to add each one.
- The recipe file is mostly English, so it confirms English synonyms better than Hindi spellings.

## Sources and credits
- Dishes for the first list: a 725-dish Indian food dataset (`D1_input_dishes_725.zip`).
- Recipes: the 10,000-recipe file from the CGAS course (`D1_input_recipes_10000.csv`).
- Taste labels: the six rasas of the *Ashtanga Hridayam* of Vagbhata, Charaka and Sushrita plus umami added by us.
- Smell labels: Ayurvedic general knowledge.FooDB data aroma tag.
- The taste and smell labels of each ingredient and the scientific names were drafted using internet search and checked by hand only in part.
