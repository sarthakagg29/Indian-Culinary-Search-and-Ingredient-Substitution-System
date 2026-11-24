# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Checks the ingredient dataset row by row. Standard library only.
Run:  python D1_4_validate.py
      python D1_4_validate.py --csv D1_0_ingredient_250_final_dataset.csv --vocab D1_0_tag_vocabulary.csv
Exit code is 0 when every check passes, 1 when something fails."""
import argparse, csv, re, sys

# ---- settings, change here ----
COLUMNS = ["english_name", "index", "roman_variants", "hindi_devanagari",
           "olfactory", "gustatory", "scientific_name"]
MIN_VARIANTS = 1
MAX_TASTE = 2
MAX_SMELL = 3
TASTES = {"sweet", "sour", "salty", "pungent", "bitter", "astringent", "umami"}
NA = "not available"
NOT_APPLICABLE = "not applicable"
BINOMIAL = re.compile(r"^[A-Z][a-z]+ [a-z-]+( [a-z-]+)*$")


def has_devanagari(text):
    return any("ऀ" <= ch <= "ॿ" for ch in text)


def load_smells(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return {r["label"] for r in csv.DictReader(f) if r["type"] == "olfactory"}


def pieces(cell):
    return [p for p in cell.split("|")]


def run_checks(rows, smells):
    fails = {}          # check name -> list of messages

    def fail(check, row, why):
        fails.setdefault(check, []).append(f"row {row['index']} ({row['english_name']}): {why}")

    seen_names, owner = {}, {}          # hash maps: name -> index, variant -> first ingredient
    for pos, row in enumerate(rows, start=1):
        name = row["english_name"]
        # required fields
        if not name:
            fail("english name present", row, "empty")
        if name != name.strip().lower() or "  " in name:
            fail("english name format", row, "not lowercase or has extra spaces")
        key = " ".join(name.lower().split())
        if key in seen_names:
            fail("no duplicate names", row, f"same as row {seen_names[key]}")
        seen_names[key] = row["index"]
        # roman variants
        parts = pieces(row["roman_variants"])
        real = [p for p in parts if p.strip()]
        if len(real) < MIN_VARIANTS:
            fail("roman variants count", row, f"{len(real)} variants, need {MIN_VARIANTS}")
        if "," in row["roman_variants"]:
            fail("variants use pipes", row, "comma found")
        if len(real) != len(parts):
            fail("variants use pipes", row, "empty piece between pipes")
        if len(set(real)) != len(real):
            fail("no repeated variant in row", row, "same spelling twice")
        if any(p != p.strip().lower() for p in real):
            fail("variants lowercase", row, "uppercase or spaces at the ends")
        for v in set(real):
            if v in owner and owner[v] != name:
                fail("no variant shared by two ingredients", row, f"'{v}' also on {owner[v]}")
            owner.setdefault(v, name)
        # hindi
        hi = row["hindi_devanagari"]
        if hi != NA and not has_devanagari(hi):
            fail("hindi name in devanagari", row, f"'{hi}'")
        # tags
        taste, smell = row["gustatory"], row["olfactory"]
        tl, sl = pieces(taste), pieces(smell)
        if taste != NA and (not all(t in TASTES for t in tl) or len(tl) > MAX_TASTE):
            fail("taste labels allowed", row, f"'{taste}'")
        if smell != NA and (not all(s in smells for s in sl) or len(sl) > MAX_SMELL):
            fail("smell labels allowed", row, f"'{smell}'")
        # scientific name
        sci = row["scientific_name"]
        if sci != NOT_APPLICABLE and not all(BINOMIAL.match(s) for s in pieces(sci)):
            fail("scientific name format", row, f"'{sci}'")
    # index and order
    idx = [r["index"] for r in rows]
    if idx != [str(i) for i in range(1, len(rows) + 1)]:
        fails.setdefault("index runs 1..N", []).append("index has gaps, repeats or is out of order")
    names = [r["english_name"] for r in rows]
    if names != sorted(names):
        fails.setdefault("rows sorted by name", []).append("english_name is not in alphabetical order")
    # a variant equal to another ingredient's name
    for r in rows:
        for v in pieces(r["roman_variants"]):
            if v in seen_names and v != r["english_name"]:
                fails.setdefault("variant is not another name", []).append(
                    f"row {r['index']} ({r['english_name']}): '{v}' is also an ingredient name")
    return fails


ALL_CHECKS = ["english name present", "english name format", "no duplicate names",
              "roman variants count", "variants use pipes", "no repeated variant in row",
              "variants lowercase", "no variant shared by two ingredients",
              "variant is not another name", "hindi name in devanagari",
              "taste labels allowed", "smell labels allowed", "scientific name format",
              "index runs 1..N", "rows sorted by name"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default="D1_0_ingredient_250_final_dataset.csv")
    p.add_argument("--vocab", default="D1_0_tag_vocabulary.csv")
    a = p.parse_args()
    with open(a.csv, encoding="utf-8-sig", newline="") as f:      # utf-8 read also proves the encoding
        reader = csv.reader(f)
        header = next(reader)
        raw = list(reader)
    bad_shape = [i for i, r in enumerate(raw, start=2) if len(r) != len(COLUMNS)]
    if header != COLUMNS or bad_shape:
        print("FAIL columns: header should be", COLUMNS, "| lines with wrong column count:", bad_shape)
        sys.exit(1)
    rows = [dict(zip(COLUMNS, r)) for r in raw]
    fails = run_checks(rows, load_smells(a.vocab))
    print(f"file: {a.csv} | rows: {len(rows)}\n")
    for c in ALL_CHECKS:
        print(f"{'FAIL' if c in fails else 'PASS'}  {c}" + (f"  ({len(fails[c])})" if c in fails else ""))
    for c in ALL_CHECKS:
        for msg in fails.get(c, []):
            print(f"  [{c}] {msg}")
    for c in fails:
        if c not in ALL_CHECKS:
            print("FAIL", c, fails[c])
    # summary for quality_report.md
    bad_rows = {m.split(":")[0] for v in fails.values() for m in v if m.startswith("row ")}
    n = len(rows)
    print("\n--- summary ---")
    print("rows checked:", n, "| rows with no problem:", n - len(bad_rows))
    print("hindi not available:", sum(r["hindi_devanagari"] == NA for r in rows))
    print("taste not available:", sum(r["gustatory"] == NA for r in rows))
    print("smell not available:", sum(r["olfactory"] == NA for r in rows))
    print("scientific name not applicable:", sum(r["scientific_name"] == NOT_APPLICABLE for r in rows))
    counts = {}
    for r in rows:
        k = len(r["roman_variants"].split("|"))
        counts[k] = counts.get(k, 0) + 1
    print("rows by number of roman variants:", dict(sorted(counts.items())))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
