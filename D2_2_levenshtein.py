# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Edit distance: how many single-letter changes turn one word into another."""


def edit_distance(a, b):
    """Fewest inserts, deletes or letter changes needed to turn a into b.
    edit_distance("jira", "jeera") is 2: change i to e, then add an e."""
    if len(a) < len(b):
        a, b = b, a                                 # keep b the shorter word, so the rows stay short
    previous = list(range(len(b) + 1))              # distance from "" to each start of b
    for i, ch_a in enumerate(a, 1):
        current = [i]                               # turning a[:i] into "" takes i deletes
        for j, ch_b in enumerate(b, 1):
            current.append(min(previous[j] + 1,                     # delete a letter of a
                               current[j - 1] + 1,                  # insert a letter of b
                               previous[j - 1] + (ch_a != ch_b)))   # change a letter (free if same)
        previous = current
    return previous[-1]


if __name__ == "__main__":
    # small self-check:  python D2_2_levenshtein.py
    
        cases = [("kitten", "sitting", 3), ("jira", "jeera", 2), 
                 ("haldi", "haldi", 0), ("", "abc", 3), ("abc", "", 3),
                 ("जीरा", "जिरा", 1), ("हींग", "हिंग", 1), ("जीरा", "ज़ीरा", 1)]
    
        for a, b, want in cases:
            got = edit_distance(a, b)
            print("ok  " if got == want else "FAIL", repr(a), repr(b), got)
