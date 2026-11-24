# Testing notes

## Honest status
The live link does not exist yet, so **the live-link test below is still to be done by you after deploying** (checklist in section 2).
What has been done: the same searches were run through the real app on a computer, without a browser
(`python test_app.py`, which uses Streamlit's built-in test runner), and the real server was started and answered.
Nothing crashed. Some searches give a weak or wrong answer, listed in section 1.

## 1. Pre-deployment run (19 searches, with the real Deliverable 3 scores)
"Breaks" = crash, or a clearly wrong answer. No search crashed the app. "Ideas" marked * are label-based (weaker).

| # | Typed | Matched | Known swaps shown | First "ideas" | Verdict |
|---|---|---|---|---|---|
| 1 | `ghee` | ghee, exact | butter 50%, coconut oil 50%, groundnut oil 50%, sunflower oil 40%, olive oil 0% | cashew nuts 100%*, chironji 100%* | OK. Oils appear. See note A |
| 2 | `jeera` | cumin seeds, exact | cumin powder 100% | turmeric powder 100%*, cloves 80%* | OK. See note B |
| 3 | `जीरा` | cumin powder, exact | cumin seeds 100% | same as above | OK. Cumin seeds is in the dropdown |
| 4 | `zeera` | black cumin, closest guess | none listed | carom seeds 100%* | **Weak.** Wrong guess; cumin seeds is in the dropdown |
| 5 | `cumin` | cumin seeds, starts-with | cumin powder 100% | as above | OK |
| 6 | `jira` | no match message | | | **Breaks (no result)** |
| 7 | `haldi` | turmeric powder, starts-with | fresh turmeric 100% | cumin powder 100%* | OK |
| 8 | `turmaric` (typo) | fresh turmeric, closest guess | turmeric powder 100% | cumin 67%* | OK |
| 9 | `lahsun` | garlic chutney, starts-with | none | black salt 60%* | **Wrong.** Should be garlic |
| 10 | `पनीर` | cottage cheese, exact | chenna 75%, tofu 17% | coconut milk 100%*, cream 100%* | OK |
| 11 | `kali mirch` | black pepper corns, exact | black pepper powder 100% | long pepper 100%*, green bell pepper 92% | OK |
| 12 | `xyzabc` | friendly "No match" | | | OK (correct) |
| 13 | `ghee, sugar` | two sections | sugar: rock sugar 100%, jaggery 25%, honey 20% | | OK |
| 14 | `g` | no match message | | | OK (too short) |
| 15 | `shakkar` | hung yogurt, closest guess | curd 100% | | **Wrong.** Should be sugar |
| 16 | `kanda` | eggs, closest guess | none | crab 50%*, prawns 50%* | **Wrong before the name fix.** Now an exact match on onion |
| 17 | `mirchi` | black pepper corns, closest guess | black pepper powder 100% | | **Weak.** Should be a chilli |
| 18 | `  GHEE  ` | ghee, exact | as row 1 | | OK |
| 19 | `curd` | curd, exact | hung yogurt 100%, buttermilk 80% | gooseberry 50%*, lemon 40%* | OK |

Also checked: **Compare** opens the Compare page with both ingredients chosen; all five pages and both score types
(Jaccard and IDF) open without errors; the Analysis page's four tabs draw; the real server starts and answers.

**Note A:** the percentage for a known swap is the computed overlap, so it can be low (ghee and butter share two labels, 50%)
or 0% (virgin olive oil shares nothing with ghee on the labels). The swap is still real; the score says the data
cannot show why. This is a limit of the data, not a bug.

**Note B:** the "ideas" lists often look odd where they are label-based (turmeric for cumin at 100%). Deliverable 3's own hand
review found label-based winners good only 8 times in 33. The app marks them **weaker** and says so on the page. If this
looks too misleading for your demo, ask your teammate about hiding label-only ideas when an ingredient has known swaps.

### Why the search misses happen and the quick fix
They are limits of the Deliverable 2 search (it compares letters, not sounds) and of missing spellings in the dataset, already
listed in Deliverable 2's README. They are not app bugs. The app softens them: guesses are labelled "Closest guess" and a
dropdown lets the user pick another match.

**Fixed in this app's copy of the CSV:** `optional_name_fixes.py` (already applied) added `lahsun` to garlic, `shakkar|shakar` to sugar,
`jira|zira|zeera` to cumin seeds, `kanda` to onion and `mirchi` to green chilies. Tested earlier on a copy: all seven
searches then return the right ingredient as an exact match. It only edits the CSV copy inside this app folder, not the Deliverable 1 original.
Undo with `git checkout -- D1_input_lookup_ingredient_250_final_dataset.csv`.

## 2. Live-link test (fill this in after deploying)
Open your `https://....streamlit.app` link in a normal browser and, if you can, once on a phone. Wait for the first load (a sleeping app takes ~30 seconds). For each row type the search, press Enter, and tick or write what happened.

Link tested: ______________________    Date: __________    Browser/device: ______________

| # | Search | What to expect | Works? | Notes |
|---|---|---|---|---|
| 1 | `ghee` | Exact match; known swaps list butter and oils | | |
| 2 | `jeera` | cumin seeds | | |
| 3 | `जीरा` | Hindi typed or pasted; cumin, dropdown shows both rows | | |
| 4 | `zeera` | "Closest guess" label | | |
| 5 | `cumin` | cumin seeds | | |
| 6 | `haldi` | turmeric | | |
| 7 | `turmaric` | turmeric (typo) | | |
| 8 | `पनीर` | cottage cheese | | |
| 9 | `kali mirch` | black pepper | | |
| 10 | `ghee, sugar` | two result sections | | |
| 11 | `xyzabc` | friendly "No match" | | |
| 12 | `GHEE` with spaces | still ghee | | |
| 13 | (empty box) | "How it works" panel, no error | | |
| 14 | `jira`, `lahsun`, `kanda` | should now find cumin seeds, garlic and onion (name fix applied) | | |
| 15 | Click **Compare** on a result | Compare page opens with both ingredients chosen | | |

Then click through the menu once: Analysis (all three tabs), New Features Coming (try the filter buttons), About.
For any failure, write down the exact text typed, what appeared, and copy any red error text; with **Manage app** (bottom right) you can read the server log.
