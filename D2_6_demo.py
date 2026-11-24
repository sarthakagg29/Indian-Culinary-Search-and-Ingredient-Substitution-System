# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Shows the search working. Run once:  python D2_6_demo.py
Or give your own queries:              python D2_6_demo.py haldi जीरा turmaric"""
import sys

from D2_5_search import IngredientSearch

SAMPLE_QUERIES = ["jeera", "jira", "zeera", "जीरा", "cumin","turmaric",'टिंडा', "lahsun","makka", "kali mirch", "pyaaz","xyzabc",]


def show(engine, query):
    print(f"\nsearch: {query}")
    matches = engine.search(query)
    if not matches:
        print("  no match")
    for m in matches:
        print(f"  {m['score']:.2f}  {m['english_name']:<22} {m['hindi_name']:<12} ({m['match_type']}: {m['matched_name']})")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    engine = IngredientSearch()
    for query in sys.argv[1:] or SAMPLE_QUERIES:
        show(engine, query)
    print("\nautocomplete for 'jee':", engine.suggest("jee"))


if __name__ == "__main__":
    main()
