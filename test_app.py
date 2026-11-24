# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Runs searches through the real app (headless) and prints what the page shows.
Usage:  python test_app.py          (needs: pip install -r requirements.txt)"""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from streamlit.testing.v1 import AppTest

QUERIES = ["ghee", "jeera", "जीरा", "zeera", "cumin", "jira", "haldi", "turmaric", "lahsun", "पनीर",
           "kali mirch", "xyzabc", "ghee, sugar", "g", "shakkar", "kanda", "mirchi", "  GHEE  ", "curd"]

def strip(s): return re.sub(r"<[^>]+>|&nbsp;", "", s).strip()

at = AppTest.from_file("app.py", default_timeout=60).run()
for q in QUERIES:
    at.text_input(key="query").set_value(q).run()
    exc = [e.value for e in at.exception]
    banner = [strip(m.value) for m in at.markdown if "class='badge" in m.value and "match" in m.value.lower()]
    heads = [strip(m.value) for m in at.markdown if m.value.startswith("#### What can replace")]
    errs = [e.value for e in at.error]
    n_sub = len([b for b in at.button if b.label == "Compare"])
    print(f"{q!r:16} exc={'YES '+str(exc) if exc else 'no'} | no-match msg={'yes' if errs else 'no'} | substitute cards={n_sub}")
    for b in banner: print("      ", b)
    for h in heads: print("      ", h)

# Compare button -> Compare page
at.text_input(key="query").set_value("ghee").run()
next(b for b in at.button if b.label == "Compare").click().run()
print("\nAfter clicking Compare: page =", at.session_state["page"], "| exceptions:", [e.value for e in at.exception])
print("   A/B selected:", at.selectbox(key="cmp_a").value, at.selectbox(key="cmp_b").value)
