# CGAS Web App (Deliverable 4)

Streamlit app for the Indian Culinary Search and Ingredient Substitution System.
Built by Sarthak Aggarwal (MT26139) and Divyanshu Joshi (MT26120), Group 26, Computational Gastronomy, IIIT Delhi.
Type an ingredient (English, Hindi or Roman spelling, typos allowed) and see what can replace it.

```
pip install -r requirements.txt
streamlit run app.py
```

## What the app uses from each deliverable (all real, nothing is dummy any more)
| Deliverable | Used for |
|---|---|
| 1 | The 250-ingredient dataset, food categories (`D1_0_ingredient_categories.csv`), swap notes (`D1_7_...csv`) |
| 2 | The search bar: names, Hindi, typos (`D2_1` to `D2_5`) |
| 3 | The scores and substitute ranking (`D3_1` to `D3_5`, Ahn compound data, synonyms, known-swap list, evaluation results) |

## Files
| File | What it is |
|---|---|
| `app.py` | Entry point: page setup, sidebar menu (page, how many swaps, score type), router |
| `page_search.py` | Main page: search bar, example buttons, match badge and dropdown |
| `page_substitutes.py` | Replacement cards: **Known swaps**, then **More ideas** (calls `get_substitutes`) |
| `page_compare.py` | Compare two ingredients (calls `match_details`) |
| `page_analysis.py` | Charts: dataset, search quality, swap quality, your searches |
| `page_soon.py` | New Features Coming; edit the `ROADMAP` list |
| `page_about.py` | About text and sources |
| `ui_common.py` | Shared helpers: page names, colours, CSS, badges, button callbacks |
| `backend.py` | The three functions the pages call; wraps Deliverable 3's `Substituter` |
| `D1_*.csv`, `D2_*.py`, `D3_*.py`, `D3_*.csv`, `Ahn_input_*.tsv` | Your earlier deliverables, copied unchanged |
| `requirements.txt`, `.streamlit/config.toml` | Libraries and colours |
| `test_app.py` | Runs searches through the app without a browser |
| `optional_name_fixes.py` | Adds common spellings (lahsun, shakkar, jira, kanda...) to this app's copy of the ingredient CSV. Already applied; safe to run again |
| `DEPLOYMENT.md`, `TESTING.md` | GitHub + Streamlit Cloud steps, test notes |

Keep every `.py` and data file in the same folder; the deliverable files find each other by name.

## How the pages fit together
- `app.py` draws the sidebar menu (the chosen page is `st.session_state["page"]`) and calls `render()` on the matching page file.
- `page_search.py` shows **"Name the ingredient you want to replace"** above a live search box. While you type, a dropdown lists
  matches from the Deliverable 2 search (trie for prefixes, Levenshtein for typos), each tagged exact / starts with / closest guess.
  Picking one shows an **Exact / Starts-with / Closest guess** badge and hands the choice to `page_substitutes.py`.
  The live box needs `streamlit-searchbox` (in `requirements.txt`); without it the page falls back to a plain text box
  (press Enter, commas allowed, max 5).
- Each ingredient gets two groups of replacements:
  1. **Known swaps**: the team's hand-written list (`D3_6_gold_pairs.csv`, 192 pairs), each shown with its real Deliverable 3 score.
  2. **More ideas**: Deliverable 3's ranking, minus the known swaps.
- Every card has a badge: **Flavour compounds** (measured data) or **Smell/taste labels · weaker**, and **Compare** opens
  `page_compare.py` with both ingredients chosen. The sidebar lets the user switch between Jaccard and IDF-weighted scores.

## The backend contract (`backend.py`)
| Function | Returns |
|---|---|
| `get_profiles()` | `{index: {english_name, hindi, scientific_name, aroma, taste, category}}` |
| `get_substitutes(index, top_n, method)` | list of dicts: `index, english_name, hindi, category, score (0-100 or None), basis, weaker, known, shared, tip`; known swaps first |
| `match_details(a, b, method)` | dict: `score, basis, weaker, known, same_source, score_molecular, score_tags, shared_compounds, shared_labels`, plus shared / only-A / only-B aroma and taste |

`method` is `"jaccard"` or `"idf"`. To change scoring, edit `backend.py` only; the pages read these keys.

## Things to know (also in About and in the badges)
- **Flavour data is Ahn et al. (2011), not FlavorDB** (the project plan said FlavorDB; Deliverable 3 documents why it was not used).
- **Only 151 of 250 ingredients have compounds.** The rest (ghee, many spices, millets) are scored on labels, marked *weaker*.
  Deliverable 3's own check found label-based winners judged good 8 times out of 33, compound-based 6 out of 7.
- **Known swaps come from the same hand-written list Deliverable 3 was tested against**, so they look better than the
  raw ranking would (raw top-5 hits that list about 26% of the time). The Analysis page shows this.
- **Licence:** the three `Ahn_input_*.tsv` files are a copy from `lingcheng99/Flavor-Network` (GPL-3.0, per Deliverable 3's README).
  If you make the GitHub repo public, keep the credit in About and check that licence first, or keep the repo private.
- Spelling guesses come from Deliverable 2 and can still be wrong for spellings that are not in the dataset. The common ones (`kanda`, `lahsun`, `jira`, `shakkar`, `mirchi`) were added to this app's copy of the CSV with `optional_name_fixes.py`.
- Search history lives only in the browser tab. Nothing is saved on a server.

## Limits
**App**
- Scores are flavour similarity only. The app does not know about the dish, texture, quantity or cooking method.
- The live search box takes one ingredient at a time; searches are remembered only in the browser tab.

**Scoring (Deliverable 3)**
- **Not every ingredient has compounds.** Spices, millets, gourds, fish, ghee and salt are mostly missing from the Ahn data. They can only get tag scores, which often tie: `soya chunks` has 21 substitutes at the same top score and `tofu` 10. Ties are ordered by shared taste, then by name.
- **Some Ahn entries are near copies.** Beans, peas and peppers have almost the same compound lists (`green peas` and `black eyed beans` share 100%, `chilli` and `long pepper` 92%). Their high scores say the data is similar, not that the swap is good.
- **A link can be too loose.** `jaggery` is linked to `cane molasses` and `ghee` to `butter oil`, the closest Ahn entries, and `peppermint extract` to peppermint leaves. The `note` column in `D3_2_synonyms.csv` says which links are close and not exact.
- **Forms share one entry.** Fresh and powdered forms of one ingredient have the same compounds, so the score cannot tell them apart.
- **Presence only.** The Ahn data says whether a compound is present, not how much. Both scores treat a trace and a main compound the same.
- **Size matters.** Jaccard falls when one ingredient has many more compounds than the other (a tomato has 150, saffron 6).
- **Not a recipe check.** A high score means the two share flavor compounds. It does not check taste, texture or how the ingredient behaves in cooking.

## Future work
Ideas we did not build, to keep each part to its plan.

**App (Deliverable 4)**
- **Real intensity for aroma and taste.** The Compare page radar charts only show present or absent, because the dataset has no strength values.
- **Several ingredients at once in the live search box.** The plain-text fallback accepts a comma-separated list (max 5); the live dropdown takes one ingredient.
- **Report a wrong match, diet filters, quantity guide, pasting a whole recipe.** Listed on the app's "New features coming" page.

**Search (Deliverable 2)**
- **More Hindi spelling rules.** `normalize()` handles the nukta, the chandrabindu and zero-width characters. Apache Lucene's Hindi normalizer (based on Pingali and Varma, "Word normalization in Indian languages", with additions from Larkey, Connell and AbdulJaleel, "Hindi CLIR in Thirty Days") also removes the halant, turns na + halant into an anusvara, and shortens long vowels. We tried these rules on a copy of the code and the results on our 389 test queries did not change, and no new Hindi names collided, so we left them out. A larger test set with more vowel-length and anusvara variants might show a difference.
- **Short Roman spellings and sound rules.** Spellings like `jira`, `zira` or `lasan` can fall below the 0.7 similarity cut-off and return nothing. `jira` and the stored `jeera` differ by 2 letters out of 5, so similarity is 0.6, and the cut-off compares letters, not sounds. Lowering the cut-off does not fix this: at 0.6 `jira` is found, but cucumber (`khira`, also 0.6) comes in with it and rejection of nonsense queries drops from 0.96 to 0.76. A better fix is a small function, for example `sound_fold(text)` in `D2_1_normalize.py` with a `SOUND_RULES` list (`ee`→`i`, `oo`→`u`, `aa`→`a`, `z`→`j`, `w`→`v`, doubled letters→one), applied only to Roman text and to both stored names and queries. On a copy of the code this made `jira`, `zira`, `zeera`, `haldee`, `maatar` and `pyaz` exact matches and raised overall Hit@1 from 0.819 to 0.865. It is not in the final code yet, for these reasons:
  - The rules were written while looking at our own `alt_spelling` queries, so the gain may be partly fitted to that list. It must be checked on the reviewed labels and on spellings nobody designed the rules for.
  - It can merge two different words (for example a name written with `oo` and another with `u`), and rejection of nonsense queries fell from 0.96 to 0.92 on the copy.
  - `lasan` and `jera` are still not found, because the rules do not add or remove vowels.
  - It would change `normalize()`, which Deliverables 3 and 4 reuse, so everything would need a re-run.
  The alternative that needs no code is adding variants such as `zira|jira|zeera` to the cumin seeds row in Deliverable 1. This app's copy already has `jira` added that way.
- **Short Hindi words with one wrong letter.** A Hindi word of 3 letters has no room for a mistake at the 0.7 cut-off: `मतर` (two letters of `मटर` swapped) is 1 wrong letter out of 3, similarity 0.667, and returns nothing. `मटरा` and `मटार` do work, but only as fuzzy guesses (score 0.45, tied with white peas). A cut-off that depends on word length, for example in `_fuzzy` of `D2_5_search.py`, could help, but needs a test run first.
- **Tie order.** When fuzzy results tie, they are sorted alphabetically, so `zeera` showed `black cumin` above `cumin seeds`, and the right one sat at rank 3. A tie-break that prefers the shorter or more common name would be a small change to the sort in `search()`.
- **Names missing in Deliverable 1.** The search can only find names that are stored. `shakar` and `शकर` (sugar) land on sweet potato by prefix (`shakarkand`), and `शक्कर` finds nothing, because the sugar row has only `cheeni`, `chini`, `danedar cheeni` and `चीनी`. Adding `shakkar|shakar` and `शक्कर` there is the fix. Deliverable 1 is unchanged; this app's copy of the dataset adds common spellings such as `shakkar` (see `optional_name_fixes.py`).
- **Plurals, extra words and multi-word queries.** Phrases such as `potatoes`, `tomatoes` or `lemon juice` are compared as a whole string, so the extra letters or words lower the score. Splitting the query into words and looking up each word, and removing plural endings and common filler words (fresh, ground, ripe, juice) before matching, would help.
- **Hinglish words.** A query like `meetha potato` fails because `meetha` (sweet) is a different word, not a spelling variation, and we have no word list for it. A small hand-made dictionary of common Hindi food words (meetha, kaccha, hara, lal) mapped to English would help.
- **Mixed scripts.** A query with Hindi and English letters together, such as `जीra`, finds nothing, because the fuzzy step compares letters and does not know that `ra` and `रा` sound the same. Converting between Hindi and Roman letters (transliteration) before comparing would be needed.
- **Library baseline.** Run an existing fuzzy-matching library on the same test queries and compare accuracy and speed with our own code.
- **Speed.** Fuzzy search compares the query with every name, so it slows down as the ingredient list grows. An index built for edit-distance search would speed it up.
- **Regional names and wrong fuzzy matches.** Adding common regional names (Marathi, Gujarati and others) to Deliverable 1 would turn matches like `bhendi` from luck into exact matches. A rule that rejects fuzzy matches when the top two results score almost the same, or a stricter cut-off for short words, could reduce wrong guesses such as `kanda` to eggs (`kanda` is fixed in this app's copy, the problem remains for other names). Either would need a new test run to check that it does not lose the correct matches.

**Scoring (Deliverable 3)**
- **More synonym names.** About 50 name links are written by hand in `D3_2_synonyms.csv`. Finding more good synonyms would link more of our 250 ingredients to Ahn ingredients, so more of them get a compound score.
- **FlavorDB.** The task is written around FlavorDB. We did not have access, so we used the Ahn data. A second loader that returns the same two dictionaries as `load_ahn()` would let the rest of the code run unchanged.
- **FlavorGraph.** A second compound source with more ingredients. Its compound ids are PubChem numbers and Ahn's are not, so the two cannot be mixed in one Jaccard score without a mapping through CAS numbers.
- **More Ayurvedic dimensions.** We used only rasa (taste) from Ayurveda. Adding guna (qualities such as heavy or light), virya (hot or cold potency) and vipaka (post-digestive effect) would give each ingredient more labels. This could separate the many substitutes that now tie on tag score and improve matching where compound data is missing.
- **Several missing ingredients at once.** A function `substitute_many(missing, pantry, exclude)` in `D3_5_substitute.py` that picks replacements that suit each other and respect what is in the kitchen.
- **Hub and bridge ingredients.** Which ingredients are good substitutes for many others, and which have none.
- **Food pairing against substitution.** Compare flavor overlap with how often two ingredients appear together in the 10,000 recipes. This tests food pairing, which is a different question from substitution, so it should be a separate analysis.
- **Better ties for tag scores.** Use more than three tags per ingredient, or add a second smell source, so that fewer substitutes tie.
- **Nutrition, price and cuisine.** Filtering substitutes by nutrition or by whether they suit the dish needs data we do not have yet.
