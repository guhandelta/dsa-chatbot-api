---
track: algorithm
difficulty: Easy
algorithms: stack
category: Data Structure
source: authored
io_mode: function
---
# Stack — Easy — Data Structure

A stack is last-in, first-out: `push`, `pop` and `peek` are all O(1). It is backed by a dynamic array (push and pop at the end). Common patterns: bracket matching (valid parentheses), monotonic stacks for next-greater-element problems, backtracking state, depth-first search without recursion, expression evaluation (postfix, shunting-yard) and undo history.

#### Balanced brackets — Python

```python
def is_balanced(s):
    pairs, st = {")": "(", "]": "[", "}": "{"}, []
    for ch in s:
        if ch in "([{":
            st.append(ch)
        elif ch in pairs:
            if not st or st.pop() != pairs[ch]:
                return False
    return not st
```
