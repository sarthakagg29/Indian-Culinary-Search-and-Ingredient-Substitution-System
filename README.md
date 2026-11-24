# CGAS Web App (Deliverable 4)

Streamlit app for the Indian Culinary Search and Ingredient Substitution System.
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
| `optional_name_fixes.py` | Optional spelling fix for Deliverable 1, see TESTING.md |
| `DEPLOYMENT.md`, `TESTING.md` | GitHub + Streamlit Cloud steps, test notes |

Keep every `.py` and data file in the same folder; the deliverable files find each other by name.

## How the pages fit together
- `app.py` draws the sidebar menu (the chosen page is `st.session_state["page"]`) and calls `render()` on the matching page file.
- `page_search.py` shows **"Name the ingredients you want to replace"** above the box. Several ingredients can be typed with
  commas (max 5). It searches (Deliverable 2), shows an **Exact / Starts-with / Closest guess** badge, offers a dropdown if
  there is more than one match, then hands the choice to `page_substitutes.py`.
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
- Spelling guesses come from Deliverable 2 and can be wrong (`kanda` finds eggs); `optional_name_fixes.py` fixes the worst ones.
- Search history lives only in the browser tab. Nothing is saved on a server.
