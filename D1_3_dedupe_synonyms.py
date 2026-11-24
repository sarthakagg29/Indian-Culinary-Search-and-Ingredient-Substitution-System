# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Finds ingredients that are the same thing under different names, using Union-Find.
Two rows are joined when they share an English name or any Roman variant.
Run:  python D1_3_dedupe_synonyms.py                 (just report)
      python D1_3_dedupe_synonyms.py --demo          (adds two test rows first, to show a merge)
      python D1_3_dedupe_synonyms.py --merge out.csv (also write a file with one row per group)"""
import argparse, csv

CSV_DEFAULT = "D1_0_ingredient_250_final_dataset.csv"
DEMO_ROWS = [  # not real data, only for the demo
    {"english_name": "demo cilantro", "roman_variants": "dhania patta|hara dhania"},
    {"english_name": "demo coriander greens", "roman_variants": "hara dhania|kothmir"},
]


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]      # path halving
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def keys_of(row):
    keys = {row["english_name"].strip().lower()}
    keys |= {v.strip().lower() for v in row["roman_variants"].split("|") if v.strip()}
    return keys


def group_rows(rows):
    uf, first = UnionFind(len(rows)), {}        # first: name or variant -> first row that used it
    for i, row in enumerate(rows):
        for k in keys_of(row):
            if k in first:
                uf.union(first[k], i)
            else:
                first[k] = i
    groups = {}
    for i in range(len(rows)):
        groups.setdefault(uf.find(i), []).append(i)
    return list(groups.values())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default=CSV_DEFAULT)
    p.add_argument("--demo", action="store_true", help="add two test rows that share a variant")
    p.add_argument("--merge", help="write a csv with one row per group")
    a = p.parse_args()
    with open(a.csv, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        cols, rows = reader.fieldnames, list(reader)
    if a.demo:
        for d in DEMO_ROWS:
            rows.append({c: d.get(c, "") for c in cols})
        print("demo: added 2 test rows:", [d["english_name"] for d in DEMO_ROWS], "\n")
    groups = group_rows(rows)
    same = [g for g in groups if len(g) > 1]
    print(f"rows: {len(rows)} | groups: {len(groups)} | groups with more than one row: {len(same)}")
    for g in same:
        print("  same ingredient:", " + ".join(rows[i]["english_name"] for i in g))
        shared = set.intersection(*(keys_of(rows[i]) for i in g)) if len(g) == 2 else set()
        if shared:
            print("    shared spelling:", ", ".join(sorted(shared)))
    if a.merge:
        out = []
        for g in groups:
            keep = min(g)                          # keep the first row of the group
            row = dict(rows[keep])
            if len(g) > 1:                         # merged row gets every spelling
                allv = []
                for i in g:
                    for v in rows[i]["roman_variants"].split("|"):
                        if v and v not in allv:
                            allv.append(v)
                row["roman_variants"] = "|".join(allv)
            out.append(row)
        with open(a.merge, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader(); w.writerows(out)
        print("saved", len(out), "rows to", a.merge)


if __name__ == "__main__":
    main()
