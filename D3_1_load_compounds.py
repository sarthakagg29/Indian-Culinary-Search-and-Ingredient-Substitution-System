# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Reads the Ahn et al. flavor data: which compounds each ingredient has (Deliverable 3)."""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PREFIX = "Ahn_input_D3_1_load_compounds_"


def read_tsv(path):
    """Rows of a tab-separated file, skipping the '#' header line."""
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            rows.append(line.rstrip("\n").split("\t"))
    return rows


def load_ahn(folder=None):
    """Returns {ahn_name: {"category": str, "compounds": set of compound ids}}
    and {compound_id: compound name}."""
    folder = folder or HERE
    info = {int(i): (name, cat) for i, name, cat in read_tsv(os.path.join(folder, PREFIX + "ingr_info.tsv"))}
    compound_names = {int(row[0]): html.unescape(row[1]).replace("_", " ")
                      for row in read_tsv(os.path.join(folder, PREFIX + "comp_info.tsv"))}
    ingredients = {name: {"category": cat, "compounds": set()} for name, cat in info.values()}
    for ingr_id, comp_id in read_tsv(os.path.join(folder, PREFIX + "ingr_comp.tsv")):
        ingredients[info[int(ingr_id)][0]]["compounds"].add(int(comp_id))
    return ingredients, compound_names


if __name__ == "__main__":
    # small self-check:  python D3_1_load_compounds.py
    ingredients, compound_names = load_ahn()
    with_compounds = sum(1 for v in ingredients.values() if v["compounds"])
    checks = [("ingredients read", len(ingredients), 1530),
              ("compounds read", len(compound_names), 1107),
              ("ingredients with compounds", with_compounds, 1525)]
    for label, got, want in checks:
        print("ok  " if got == want else "FAIL", label, got)
    print("ok  " if "turmeric" in ingredients else "FAIL", "turmeric present;",
          len(ingredients["turmeric"]["compounds"]), "compounds")
