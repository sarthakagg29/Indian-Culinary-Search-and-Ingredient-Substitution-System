# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Reads the ingredient CSV and builds the exact-match table."""
import csv
import os

from D2_1_normalize import normalize

CSV_DEFAULT = "D1_input_lookup_ingredient_250_final_dataset.csv"
NOT_AVAILABLE = "not available"


def load_ingredients(csv_path=None):
    """Return {index: record}. A record holds the index, english_name, hindi and names,
    where names is every cleaned name of the ingredient (English, Roman variants, Hindi)."""
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CSV_DEFAULT)
    dict_ingre = {}
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            raw = [row["english_name"]] + row["roman_variants"].split("|")
            if row["hindi_devanagari"] != NOT_AVAILABLE:
                raw.append(row["hindi_devanagari"])
            names = []
            for name in map(normalize, raw):
                if name and name not in names:
                    names.append(name)
            index = int(row["index"])
            dict_ingre[index] = {"index": index, "english_name": row["english_name"],
                                  "hindi": row["hindi_devanagari"], "names": names}
    return dict_ingre


def build_exact_index(dict_ingre):
    """Hash map: cleaned name -> list of ingredient indexes.
    A list, because one Hindi name can belong to two rows (जीरा is cumin seeds and cumin powder)."""
    table = {}
    for index, record in dict_ingre.items():
        for name in record["names"]:
            table.setdefault(name, []).append(index)
    return table


def exact_lookup(exact_index, cleaned_query):
    """Indexes whose name is exactly the query. The query must already be cleaned with normalize()."""
    return exact_index.get(cleaned_query, [])

if __name__ == "__main__":
    # small self-check:  python D2_3_lookup.py
    tiny = {1: {"names": ["okra", "bhindi"]},
            2: {"names": ["cumin seeds", "जीरा"]},
            3: {"names": ["cumin powder", "जीरा"]}}
    table = build_exact_index(tiny)
    checks = [("okra", [1]), ("bhindi", [1]), ("जीरा", [2, 3]), ("xyzabc", [])]
    for query, want in checks:
        got = exact_lookup(table, query)
        print("ok  " if got == want else "FAIL", repr(query), got)
    rows = len(load_ingredients())
    print("ok  " if rows == 250 else "FAIL", "rows loaded:", rows)
