<!-- Sarthak Aggarwal MT26139 -->
<!-- Divyanshu Joshi MT26120 -->
# Data dictionary

Main file: `D1_0_ingredient_250_final_dataset.csv`. UTF-8 with a header row, 250 rows, 7 columns. Rows are sorted alphabetically by `english_name`. Several values in one cell are separated by a pipe `|`.

| Column | What it holds | Example | Rule |
|---|---|---|---|
| `english_name` | The ingredient name in English | `cumin seeds` | Lowercase, no extra spaces, unique. Forms of one ingredient are separate rows (`garlic paste`, `green garlic`). |
| `index` | Row number after sorting | `65` | Runs 1 to 250 with no gaps. It is only a row number, not a rank. |
| `roman_variants` | Other names written in English letters: Hindi transliterations, regional names, English synonyms | `dhania patta\|dharnia ka patta` | At least 1 variant (`MIN_VARIANTS` in `D1_4_validate.py`). Lowercase, pipes only, no empty piece, no repeat, and no spelling on two ingredients. |
| `hindi_devanagari` | Hindi name in Devanagari | `धनिया` | Must contain Devanagari letters, or the value `not available`. |
| `olfactory` | What the ingredient smells like | `herbal\|citrus\|green` | 1 to 3 labels from the smell list in `D1_0_tag_vocabulary.csv`, or `not available`. |
| `gustatory` | What the ingredient tastes like | `astringent\|bitter` | 1 to 2 labels from sweet, sour, salty, pungent, bitter, astringent, umami, or `not available`. |
| `scientific_name` | Species name of the source plant or animal | `Coriandrum sativum` | Genus plus species, for example `Allium sativum`. `not applicable` for salt, water, baking soda, black salt and vinegar. Two species are joined with a pipe. Prepared forms (paste, powder, oil) carry the species of the base ingredient. |

## The allowed labels

**Taste (7):** sweet, sour, salty, pungent, bitter, astringent, umami. The first six are the Ayurvedic tastes (rasa) from the Ashtanga Hridayam of Vagbhata. Umami is added by us.

**Smell (35 labels):** the list is kept in `D1_0_tag_vocabulary.csv` (column `type` = olfactory). The list was cut down from 61 labels by merging rarely used ones into broader ones (for example apple, banana and mango became `fruity`), so ingredients can be compared in Deliverable 3. Each label is used by at least 4 ingredients. `not available` means the ingredient has no smell of its own (salt, sugar, water and similar).

The label list must be edited by hand when it changes. `D1_4_validate.py` reads it to check the data, so it should not be regenerated from the data.
