# Sarthak Aggarwal MT26139
# Divyanshu Joshi MT26120
"""Prefix tree for autocomplete and 'starts with' search."""


class TrieNode:
    def __init__(self):
        self.children = {}      # letter -> next node
        self.ids = []           # ingredient indexes of names that end at this node


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, ingredient_id):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        if ingredient_id not in node.ids:
            node.ids.append(ingredient_id)

    def with_prefix(self, prefix):
        """Every (name, ingredient_id) whose name starts with prefix, sorted by name."""
        node = self.root
        for ch in prefix:                       # walk down the prefix first
            if ch not in node.children:
                return []
            node = node.children[ch]
        found, stack = [], [(node, prefix)]     # then collect everything below it
        while stack:
            node, word = stack.pop()
            found.extend((word, i) for i in node.ids)
            for ch, child in node.children.items():
                stack.append((child, word + ch))
        return sorted(found)


        

if __name__ == "__main__":
    # small self-check:  python D2_4_trie.py
    trie = Trie()
    for word, i in [("okra", 1), ("oats", 2), ("jeera", 3), ("जीरा", 3), ("जीरा", 4)]:
        trie.insert(word, i)
    checks = [("o", [("oats", 2), ("okra", 1)]),
              ("ok", [("okra", 1)]),
              ("okra", [("okra", 1)]),
              ("जी", [("जीरा", 3), ("जीरा", 4)]),
              ("okrax", []),
              ("x", [])]
    for prefix, want in checks:
        got = trie.with_prefix(prefix)
        print("ok  " if got == want else "FAIL", repr(prefix), got)
