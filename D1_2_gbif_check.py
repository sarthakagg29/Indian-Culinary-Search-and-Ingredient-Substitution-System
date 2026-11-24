# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Check the drafted scientific names against GBIF. Standard library only, needs internet.
Reads D1_2_scientific_draft.csv, writes D1_2_gbif_check.csv. Run:
  python D1_2_gbif_check.py --limit 5     (test)
  python D1_2_gbif_check.py               (all rows)
"""
import argparse, csv, json, os, time, urllib.parse, urllib.request

API = "https://api.gbif.org/v1/species/match"


def match(name, cache):
    if name in cache:
        return cache[name]
    with urllib.request.urlopen(f"{API}?{urllib.parse.urlencode({'name': name})}", timeout=30) as r:
        d = json.load(r)
    out = {"match_type": d.get("matchType", ""), "status": d.get("status", ""),
           "gbif_name": d.get("canonicalName") or d.get("scientificName", ""),
           "kingdom": d.get("kingdom", ""), "confidence": d.get("confidence", "")}
    cache[name] = out
    time.sleep(0.3)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default="D1_2_scientific_draft.csv")
    p.add_argument("--out", default="D1_2_gbif_check.csv")
    p.add_argument("--cache", default="D1_2_gbif_match_cache.json")
    p.add_argument("--limit", type=int, default=None)
    a = p.parse_args()
    cache = json.load(open(a.cache, encoding="utf-8")) if os.path.exists(a.cache) else {}
    rows = list(csv.DictReader(open(a.csv, encoding="utf-8-sig")))
    out, exact = [], 0
    for row in rows[:a.limit]:
        draft = row["scientific_name_draft"].strip()
        if draft == "not applicable":
            out.append({**row, "result": "skipped", "gbif_name": "", "check": ""})
            continue
        name = draft.split(";")[0].strip()
        try:
            m = match(name, cache)
        except Exception as err:
            print("stopped:", err)
            break
        ok = m["match_type"] == "EXACT" and m["status"] == "ACCEPTED"
        exact += ok
        verdict = "ok" if ok else "check by hand"
        print(f"{row['rank']:>3} {row['english_name']}: {name} -> {m['gbif_name']} "
              f"[{m['match_type']}, {m['status']}, {m['kingdom']}] {verdict}")
        out.append({**row, "result": f"{m['match_type']}/{m['status']}", "gbif_name": m["gbif_name"], "check": verdict})
    json.dump(cache, open(a.cache, "w", encoding="utf-8"))
    with open(a.out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)
    print(f"exact and accepted: {exact} of {len(out)} rows. saved to {a.out}")


if __name__ == "__main__":
    main()
