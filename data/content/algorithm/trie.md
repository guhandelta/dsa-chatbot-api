---
track: algorithm
difficulty: Medium
algorithms: trie
category: Data Structure
source: authored
io_mode: function
---
# Trie — Medium — Data Structure

A trie (prefix tree) stores strings character by character along root-to-node paths, so insert and lookup cost O(k) for a key of length k no matter how many keys are stored. Common patterns: autocomplete (walk to the prefix node, then collect every word beneath it), spell checking (exact lookup, or a walk that allows one insert, delete or replace to suggest words within edit distance 1), prefix matching and counting, word search on a grid with pruning, and longest common prefix. For lowercase ASCII, a fixed 26-slot child array per node is faster and smaller than a hash map per node.

#### Trie — Python

```python
class Trie:
    END = "$"                              # end-of-word marker key

    def __init__(self):
        self.root = {}

    def insert(self, word):
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node[self.END] = True

    def _walk(self, prefix):
        node = self.root
        for ch in prefix:
            if ch not in node:
                return None
            node = node[ch]
        return node

    def search(self, word):
        node = self._walk(word)
        return node is not None and self.END in node

    def starts_with(self, prefix):
        return self._walk(prefix) is not None

    def autocomplete(self, prefix, limit=10):   # words with this prefix, alphabetical
        start, out = self._walk(prefix), []
        if start is None:
            return out
        stack = [(start, prefix)]
        while stack and len(out) < limit:
            node, word = stack.pop()
            if self.END in node:
                out.append(word)
            for ch in sorted((c for c in node if c != self.END), reverse=True):
                stack.append((node[ch], word + ch))
        return out
```
