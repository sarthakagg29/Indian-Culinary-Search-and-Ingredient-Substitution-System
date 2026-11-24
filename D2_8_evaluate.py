# Sarthak Aggarwal
# MT26139
"""Runs every query in D2_7_test_queries.csv through the search and saves the results (Deliverable 2).
Run once:  python D2_8_evaluate.py
Writes D2_8_evaluation_results.csv (one row per query) and D2_8_evaluation_summary.csv (one row per query type)."""
import csv
import sys
import time

from D2_2_levenshtein import edit_distance
from D2_5_search import IngredientSearch

QUERIES = "D2_7_test_queries.csv"
RESULTS = "D2_8_evaluation_results.csv"
SUMMARY = "D2_8_evaluation_summary.csv"
TOP_K = 5
REPEATS = 3          # each query is timed this many times and the average is kept


def closest_name_distance(query, correct, engine):
    """Edit distance from the cleaned query to the nearest name of a correct ingredient."""
    from D2_1_normalize import normalize
    q = normalize(query)
    return min(edit_distance(q, name) for i in correct for name in engine.ingredients[i]["names"])


def run_query(engine, row):
    correct = [int(i) for i in row["correct_indexes"].split("|") if i]
    start = time.perf_counter()
    for _ in range(REPEATS):
        matches = engine.search(row["query"], top_k=TOP_K)
    ms = (time.perf_counter() - start) / REPEATS * 1000

    out = {"query_id": row["query_id"], "query": row["query"], "query_type": row["query_type"],
           "correct": row["correct_names"], "needs_review": row["needs_review"],
           "edit_distance": "", "rank_of_correct": "", "hit1": "", "hit3": "", "hit5": "", "rejected": "",
           "top1": matches[0]["english_name"] if matches else "",
           "top1_score": matches[0]["score"] if matches else "",
           "top1_match_type": matches[0]["match_type"] if matches else "",
           "top3": "; ".join(f"{m['english_name']} ({m['score']:.2f}, {m['match_type']})" for m in matches[:3]),
           "ms": round(ms, 3)}
    if not correct:                                   # nothing should match: success is an empty list
        out["rejected"] = int(not matches)
        return out
    rank = next((r for r, m in enumerate(matches, 1) if m["index"] in correct), 0)
    out.update({"edit_distance": closest_name_distance(row["query"], correct, engine),
                "rank_of_correct": rank, "hit1": int(rank == 1), "hit3": int(0 < rank <= 3), "hit5": int(rank > 0)})
    return out


def summarize(results):
    rows = []
    types = list(dict.fromkeys(r["query_type"] for r in results))
    groups = [(t, [r for r in results if r["query_type"] == t]) for t in types]
    groups.append(("ALL (without no_match)", [r for r in results if r["query_type"] != "no_match"]))
    for name, rs in groups:
        n = len(rs)
        if name == "no_match":
            rows.append({"query_type": name, "n": n, "hit1": "", "hit3": "", "hit5": "", "mrr": "",
                         "rejection_rate": round(sum(r["rejected"] for r in rs) / n, 3),
                         "mean_ms": round(sum(r["ms"] for r in rs) / n, 3)})
            continue
        rr = [1 / r["rank_of_correct"] if r["rank_of_correct"] else 0 for r in rs]
        rows.append({"query_type": name, "n": n,
                     "hit1": round(sum(r["hit1"] for r in rs) / n, 3),
                     "hit3": round(sum(r["hit3"] for r in rs) / n, 3),
                     "hit5": round(sum(r["hit5"] for r in rs) / n, 3),
                     "mrr": round(sum(rr) / n, 3), "rejection_rate": "",
                     "mean_ms": round(sum(r["ms"] for r in rs) / n, 3)})
    return rows


def save(path, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    engine = IngredientSearch()
    with open(QUERIES, encoding="utf-8-sig", newline="") as f:
        queries = list(csv.DictReader(f))
    results = [run_query(engine, row) for row in queries]
    summary = summarize(results)
    save(RESULTS, results)
    save(SUMMARY, summary)

    print(f"{len(results)} queries, top {TOP_K} results each\n")
    print(f"{'query type':<24}{'n':>4}{'hit@1':>8}{'hit@3':>8}{'hit@5':>8}{'MRR':>8}{'ms':>9}")
    for s in summary:
        if s["query_type"] == "no_match":
            print(f"{s['query_type']:<24}{s['n']:>4}  returned nothing for {s['rejection_rate']:.0%} of them{s['mean_ms']:>16}")
        else:
            print(f"{s['query_type']:<24}{s['n']:>4}{s['hit1']:>8.2f}{s['hit3']:>8.2f}{s['hit5']:>8.2f}{s['mrr']:>8.2f}{s['mean_ms']:>9.2f}")
    print(f"\nsaved {RESULTS} and {SUMMARY}")


if __name__ == "__main__":
    main()
