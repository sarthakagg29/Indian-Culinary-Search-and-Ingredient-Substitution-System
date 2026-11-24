# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Tests Jaccard against IDF, compounds against tags, and the real scores against chance (Deliverable 3).

Tests:
1. gold pairs: known Indian swaps from D3_6_gold_pairs.csv (we write these by hand, with a source).
2. category check: does a ranked substitute share the Ahn food category (fruit, spice, dairy...)?
   This needs no hand-made list, so it runs now. It is a rough check, not proof.
3. wins: how often the tag score beats the compound score, and a sheet of 40 winners for a person to
   mark as a good win or a bad win (D3_7_win_review.csv).
"""
import csv
import os
import random
from math import comb

from D3_5_substitute import METHODS, Substituter

HERE = os.path.dirname(os.path.abspath(__file__))
GOLD_CSV = os.path.join(HERE, "D3_6_gold_pairs.csv")
RESULTS_CSV = os.path.join(HERE, "D3_7_evaluation_results.csv")
SUMMARY_CSV = os.path.join(HERE, "D3_7_evaluation_summary.csv")
REVIEW_CSV = os.path.join(HERE, "D3_7_win_review.csv")
REVIEW_SIZE = 40
GOLD_BASES = ("auto", "molecular", "tags", "best")
SEED = 42
KS = (1, 3, 5)


# ---- small helpers -----------------------------------------------------
def hit_at(rank, k):
    return 1.0 if rank is not None and rank <= k else 0.0


def reciprocal(rank):
    return 1.0 / rank if rank else 0.0


def random_hit(n_pool, n_good, k):
    """Chance that k random picks from the pool contain at least one good one."""
    k = min(k, n_pool)
    return 1 - comb(n_pool - n_good, k) / comb(n_pool, k)


def random_mrr(n_pool, n_good):
    """Expected reciprocal rank of the first good item in a random order."""
    total, none_yet = 0.0, 1.0
    for r in range(1, n_pool - n_good + 2):
        p_here = none_yet * n_good / (n_pool - r + 1)
        total += p_here / r
        none_yet *= (n_pool - n_good - r + 1) / (n_pool - r + 1)
    return total


def split_half(items, seed=SEED):
    """Tuning half and test half, the same every run."""
    items = sorted(items)
    random.Random(seed).shuffle(items)
    cut = len(items) // 2
    return sorted(items[:cut]), sorted(items[cut:])


def summarise(ranks):
    """ranks: list of rank-or-None. Returns Hit@1/3/5 and MRR."""
    n = len(ranks)
    if n == 0:
        return {"n": 0, "hit1": "", "hit3": "", "hit5": "", "mrr": ""}
    out = {"n": n}
    for k in KS:
        out["hit%d" % k] = round(sum(hit_at(r, k) for r in ranks) / n, 3)
    out["mrr"] = round(sum(reciprocal(r) for r in ranks) / n, 3)
    return out


# ---- test 2: category check -----------------------------------------------
def category_ranks(sub, method, queries, basis="molecular"):
    """{query: (rank of the first same-category substitute or None, n_pool, n_good)}
    Only ingredients with compounds have an Ahn category, so every basis is ranked on that same pool."""
    mol = sub.molecules
    out = {}
    for q in queries:
        pool = [i for i in mol.compounds if i != q and not sub._same_source(q, i)]
        in_pool = set(pool)
        good = {i for i in pool if mol.category[i] == mol.category[q]}
        ranked = [r for r in sub.substitutes(q, top_k=10 ** 6, method=method, basis=basis, details=False)
                  if r["index"] in in_pool]
        rank = next((pos for pos, r in enumerate(ranked, 1) if r["index"] in good), None)
        out[q] = (rank, len(pool), len(good))
    return out


def run_category_check(sub):
    mol = sub.molecules
    queries = [q for q in mol.compounds
               if any(i != q and mol.category[i] == mol.category[q] and not sub._same_source(q, i)
                      for i in mol.compounds)]
    by_method = {m: category_ranks(sub, m, queries) for m in METHODS}
    tune, test = split_half(queries)
    summary, results = [], []
    for part, members in (("all", queries), ("tuning", tune), ("test", test)):
        for m in METHODS:
            row = summarise([by_method[m][q][0] for q in members])
            summary.append(dict(evaluation="category_check", split=part, method=m, **row))
        n = len(members)
        base = {"n": n}
        for k in KS:
            base["hit%d" % k] = round(sum(random_hit(by_method["jaccard"][q][1], by_method["jaccard"][q][2], k)
                                          for q in members) / n, 3)
        base["mrr"] = round(sum(random_mrr(by_method["jaccard"][q][1], by_method["jaccard"][q][2])
                                for q in members) / n, 3)
        summary.append(dict(evaluation="category_check", split=part, method="random", **base))
    for m in METHODS:
        for q in queries:
            results.append({"evaluation": "category_check", "query": sub.rows[q]["english_name"],
                            "method": m, "rank": by_method[m][q][0] or "", "note": ""})
    chosen = max(METHODS, key=lambda m: (next(s["mrr"] for s in summary if s["split"] == "tuning" and s["method"] == m), -METHODS.index(m)))
    # the same check for compounds only, tags only (smell + rasa) and the higher of the two
    for basis in ("molecular", "tags", "best"):
        for m in METHODS:
            ranks = category_ranks(sub, m, queries, basis)
            for part, members in (("all", queries), ("tuning", tune), ("test", test)):
                summary.append(dict(evaluation="category_check_bases", split=part, method="%s %s" % (basis, m),
                                    **summarise([ranks[q][0] for q in members])))
    return summary, results, chosen, len(queries)


def pair_score_gap(sub):
    """Same-category pairs against other pairs: do the scores separate them?"""
    mol = sub.molecules
    ids = sorted(mol.compounds)
    rows = {"same category": {"jaccard": [], "idf": []}, "different category": {"jaccard": [], "idf": []}}
    for pos, i in enumerate(ids):
        for j in ids[pos + 1:]:
            if sub._same_source(i, j):
                continue
            key = "same category" if mol.category[i] == mol.category[j] else "different category"
            rows[key]["jaccard"].append(mol.jaccard(i, j))
            rows[key]["idf"].append(mol.idf(i, j))
    return {k: {m: round(sum(v) / len(v), 4) for m, v in d.items()} | {"pairs": len(d["jaccard"])} for k, d in rows.items()}


# ---- test 1: gold pairs ---------------------------------------------------------
def read_gold(sub, path=None):
    """Reads the hand-made pairs. Names are matched to D1 english names, else to the D2 search."""
    path = path or GOLD_CSV
    if not os.path.exists(path):
        return [], []
    by_name = {r["english_name"].strip().lower(): i for i, r in sub.rows.items()}
    pairs, problems = [], []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for line, row in enumerate(csv.DictReader(f), 2):
            if not (row.get("ingredient") or "").strip():
                continue
            ids = []
            for field in ("ingredient", "substitute"):
                name = row[field].strip().lower()
                idx = by_name.get(name)
                if idx is None:
                    found = sub.find(name, top_k=1)
                    idx = found[0]["index"] if found else None
                    if idx is not None:
                        problems.append("line %d: '%s' not an exact D1 name, used '%s'" % (line, row[field], found[0]["english_name"]))
                ids.append(idx)
            if None in ids:
                problems.append("line %d: could not find '%s' or '%s'" % (line, row["ingredient"], row["substitute"]))
            else:
                pairs.append((ids[0], ids[1], row.get("source", "")))
    return pairs, problems


def gold_ranks(sub, method, pairs, basis="best"):
    """For each pair: rank of the substitute in the list for the ingredient, and why if missing."""
    out = []
    for a, b, _ in pairs:
        ranked = sub.substitutes(a, top_k=10 ** 6, method=method, basis=basis, details=False)
        rank = next((pos for pos, r in enumerate(ranked, 1) if r["index"] == b), None)
        why = ""
        if rank is None:
            if sub._same_source(a, b):
                why = "same_source"
            elif not (sub.molecules.has(a) or sub.tags.has(a)):
                why = "no_data_for_ingredient"
            else:
                why = "not_scored"
        out.append((rank, why))
    return out


def run_gold_check(sub, pairs):
    summary, results = [], []
    combos = ["%s %s" % (b, m) for b in GOLD_BASES for m in METHODS]          # e.g. "best jaccard"
    by_method = {c: gold_ranks(sub, c.split()[1], pairs, c.split()[0]) for c in combos}
    idx = list(range(len(pairs)))
    tune, test = split_half(idx) if len(pairs) >= 10 else (idx, idx)
    for part, members in (("all", idx), ("tuning", tune), ("test", test)):
        for c in combos:
            row = summarise([by_method[c][i][0] for i in members])
            summary.append(dict(evaluation="gold_pairs", split=part, method=c, **row,
                                note="" if len(pairs) >= 10 or part == "all" else "fewer than 10 pairs: no real split"))
    for c in combos:
        for i, (a, b, source) in enumerate(pairs):
            rank, why = by_method[c][i]
            results.append({"evaluation": "gold_pairs", "query": "%s -> %s" % (sub.rows[a]["english_name"], sub.rows[b]["english_name"]),
                            "method": c, "rank": rank or "", "note": why or source})
    chosen = max(combos, key=lambda c: (next(s["mrr"] for s in summary if s["split"] == "tuning" and s["method"] == c) or 0, -combos.index(c)))
    return summary, results, chosen


# ---- test 3: which score wins, and a sheet for a person to judge the wins ----------
def win_stats(sub):
    """How often the tag score beats the compound score (pairs where both exist), and who wins the top spot."""
    ids = sorted(sub.molecules.compounds)
    out = []
    for m in METHODS:
        count = {"tags": 0, "molecular": 0, "tie": 0}
        for pos, i in enumerate(ids):
            for j in ids[pos + 1:]:
                if sub._same_source(i, j):
                    continue
                s = sub._score_pair(i, j, m)
                if s["molecular"] is None or s["tags"] is None:
                    continue
                count["tags" if s["tags"] > s["molecular"] else "molecular" if s["tags"] < s["molecular"] else "tie"] += 1
        top1 = {"molecular": 0, "tags": 0}
        for q in ids:
            best = sub.substitutes(q, top_k=1, method=m, basis="best", details=False)
            if best:
                top1[best[0]["basis"]] += 1
        out.append({"method": m, "pairs": sum(count.values()), "tags_win": count["tags"],
                    "compounds_win": count["molecular"], "tie": count["tie"],
                    "top1_by_tags": top1["tags"], "top1_by_compounds": top1["molecular"]})
    return out


def write_win_review(sub, path=None):
    """40 ingredients with compounds, each with its winning substitute. A person fills the column
    good_win (yes or no). Not rewritten if the file exists, so filled-in answers are never lost."""
    path = path or REVIEW_CSV
    if os.path.exists(path):
        return False
    ids = sorted(sub.molecules.compounds)
    rows = []
    for q in sorted(random.Random(SEED).sample(ids, min(REVIEW_SIZE, len(ids)))):
        best = sub.substitutes(q, top_k=1, method="jaccard", basis="best")
        if not best:
            continue
        mol = sub.substitutes(q, top_k=1, method="jaccard", basis="molecular", details=False)
        tag = sub.substitutes(q, top_k=1, method="jaccard", basis="tags", details=False)
        b = best[0]
        rows.append({"ingredient": sub.rows[q]["english_name"], "winner": b["english_name"], "won_by": b["basis"],
                     "score": b["score"], "score_compounds": b["score_molecular"], "score_tags": b["score_tags"],
                     "shared_compounds": "; ".join(b["shared_compounds"]), "shared_tags": "; ".join(b["shared_tags"]),
                     "compound_top1": sub.rows[mol[0]["index"]]["english_name"] if mol else "",
                     "tag_top1": sub.rows[tag[0]["index"]]["english_name"] if tag else "",
                     "good_win": "", "note": ""})
    write_csv(path, rows, ["ingredient", "winner", "won_by", "score", "score_compounds", "score_tags",
                           "shared_compounds", "shared_tags", "compound_top1", "tag_top1", "good_win", "note"])
    return True


def read_win_review(path=None):
    """{won_by: {"yes": n, "no": n}} from the rows a person has marked."""
    path = path or REVIEW_CSV
    counts = {}
    if not os.path.exists(path):
        return counts
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            verdict = (row.get("good_win") or "").strip().lower()
            if verdict in ("yes", "no"):
                counts.setdefault(row["won_by"], {"yes": 0, "no": 0})[verdict] += 1
    return counts


def write_csv(path, rows, columns):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        out = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        out.writeheader()
        out.writerows(rows)


def main():
    sub = Substituter()
    summary, results = [], []
    s, r, chosen, n = run_category_check(sub)
    summary += s
    results += r
    print("Category check (%d ingredients with compounds and a same-category partner)" % n)
    for row in s:
        if row["evaluation"] == "category_check" and row["split"] in ("all", "test"):
            print("  %-5s %-8s n=%-3s hit@1 %-6s hit@3 %-6s hit@5 %-6s mrr %s" % (row["split"], row["method"], row["n"], row["hit1"], row["hit3"], row["hit5"], row["mrr"]))
    print("  better method on the tuning half (by MRR):", chosen)
    for row in s:
        if row["evaluation"] == "category_check_bases" and row["split"] == "all":
            print("  bases %-18s n=%-3s hit@1 %-6s hit@3 %-6s hit@5 %-6s mrr %s" % (row["method"], row["n"], row["hit1"], row["hit3"], row["hit5"], row["mrr"]))
    gap = pair_score_gap(sub)
    for k, v in gap.items():
        print("  mean score of %s pairs (%d): jaccard %s, idf %s" % (k, v["pairs"], v["jaccard"], v["idf"]))
    wins = win_stats(sub)
    print("Which score wins (pairs where both exist, and the top substitute of each ingredient with compounds)")
    for w in wins:
        print("  %-8s pairs %d: tags win %d, compounds win %d, tie %d | top substitute won by tags %d, by compounds %d"
              % (w["method"], w["pairs"], w["tags_win"], w["compounds_win"], w["tie"], w["top1_by_tags"], w["top1_by_compounds"]))
        summary.append(dict(evaluation="win_share", split="all", method=w["method"], n=w["pairs"],
                            note="tags win %d, compounds win %d, tie %d; top1 by tags %d, by compounds %d"
                                 % (w["tags_win"], w["compounds_win"], w["tie"], w["top1_by_tags"], w["top1_by_compounds"])))
    made = write_win_review(sub)
    print("  %s %s" % (os.path.basename(REVIEW_CSV), "written: fill the good_win column (yes or no) and run again" if made else "already exists, kept as it is"))
    for basis, c in read_win_review().items():
        n = c["yes"] + c["no"]
        print("  marked wins by %-9s: %d good of %d" % (basis, c["yes"], n))
        summary.append(dict(evaluation="win_review", split="all", method=basis, n=n, note="good wins %d of %d" % (c["yes"], n)))
    pairs, problems = read_gold(sub)
    for p in problems:
        print("  gold file:", p)
    if pairs:
        s, r, chosen = run_gold_check(sub, pairs)
        summary += s
        results += r
        print("Gold pairs (%d)" % len(pairs))
        for row in s:
            if row["split"] in ("all", "test"):
                print("  %-5s %-8s n=%-3s hit@1 %-6s hit@3 %-6s hit@5 %-6s mrr %s" % (row["split"], row["method"], row["n"], row["hit1"], row["hit3"], row["hit5"], row["mrr"]))
        print("  better method on the tuning half (by MRR):", chosen)
    else:
        print("Gold pairs: D3_6_gold_pairs.csv has no rows yet. Add known swaps (columns: ingredient, substitute, source) and run again.")
    write_csv(SUMMARY_CSV, summary, ["evaluation", "split", "method", "n", "hit1", "hit3", "hit5", "mrr", "note"])
    write_csv(RESULTS_CSV, results, ["evaluation", "query", "method", "rank", "note"])
    print("saved", os.path.basename(SUMMARY_CSV), "and", os.path.basename(RESULTS_CSV))


if __name__ == "__main__":
    # `python D3_7_evaluate.py` runs the tests. The checks below run with:  python D3_7_evaluate.py check
    import sys
    if sys.argv[1:] == ["check"]:
        print("ok  " if abs(random_hit(10, 2, 1) - 0.2) < 1e-12 else "FAIL", "random hit@1 with 2 good of 10 is 0.2")
        print("ok  " if abs(random_hit(10, 2, 3) - (1 - comb(8, 3) / comb(10, 3))) < 1e-12 else "FAIL", "random hit@3")
        print("ok  " if abs(random_mrr(2, 1) - 0.75) < 1e-12 else "FAIL", "random mrr, 1 good of 2 = (1 + 1/2) / 2")
        print("ok  " if summarise([1, 3, None, 2])["hit1"] == 0.25 and summarise([1, 3, None, 2])["mrr"] == round((1 + 1 / 3 + 0 + 1 / 2) / 4, 3) else "FAIL", "hit@1 and mrr from ranks")
        print("ok  " if split_half(range(10)) == split_half(range(10)) and len(split_half(range(10))[0]) == 5 else "FAIL", "split is repeatable and half and half")
    else:
        main()
