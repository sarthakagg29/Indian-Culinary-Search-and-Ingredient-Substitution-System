# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""OPTIONAL: adds a few missing spellings to the Deliverable 1 dataset (in place).
Fixes searches that currently miss or guess wrong: lahsun, shakkar, jira, zira, zeera, kanda, mirchi.
This changes Deliverable 1's CSV, so check with whoever owns it first.
Run once:  python optional_name_fixes.py     (undo with: git checkout -- D1_input_lookup_ingredient_250_final_dataset.csv)"""
import csv

PATH = "D1_input_lookup_ingredient_250_final_dataset.csv"
ADD = {"garlic": ["lahsun"], "sugar": ["shakkar", "shakar"], "cumin seeds": ["jira", "zira", "zeera"],
       "onion": ["kanda"], "green chilies": ["mirchi"]}

with open(PATH, encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    fields, rows = reader.fieldnames, list(reader)
for row in rows:
    names = row["roman_variants"].split("|")
    for new in ADD.get(row["english_name"], []):
        if new not in names:
            names.append(new)
    row["roman_variants"] = "|".join(names)
with open(PATH, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
print("done: added", sum(len(v) for v in ADD.values()), "spellings")
