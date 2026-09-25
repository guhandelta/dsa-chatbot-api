---
track: language
difficulty: Easy
language: python
source: authored
io_mode: function
algorithms: hash-map
---
# Python Dictionaries & Sets — Easy — Built-in Data Structures

## Concept
A `dict` maps hashable keys to values with average O(1) lookup, insert, and delete. A `set` is the same machinery without values — membership testing in O(1). Both are backed by a hash table, so ordering is insertion order (guaranteed since Python 3.7) and keys must be hashable (immutable types: str, int, tuple; not list or dict).

## Why it matters
Most "reduce O(n²) to O(n)" moves in interviews are a dict or set in disguise. Recognising that you need to answer "have I seen this before, and where?" is the trigger to reach for one.

## Key operations
- `d[k]` raises `KeyError` if absent; `d.get(k, default)` does not.
- `d.setdefault(k, [])` and `collections.defaultdict(list)` avoid the "initialise if missing" dance.
- `collections.Counter(iterable)` counts occurrences in one line.
- `k in d` tests keys, not values, and is O(1).
- Sets support `|` union, `&` intersection, `-` difference.

## Thinking Style (transferable pattern)
- "Have I seen this value?" → set. "Where did I see it?" → dict.
- Counting anything → `Counter`. Grouping anything → `defaultdict(list)`.
- Trading memory for speed is almost always the intended optimisation when the brute force is a nested loop over one array.

## Common Mistakes
- Using a list for membership tests — `x in my_list` is O(n) and silently turns your solution quadratic.
- Mutating a dict while iterating over it (raises `RuntimeError`).
- Trying to use a list as a key (unhashable) instead of a tuple.

## Exercise
Write `first_repeated(nums)` returning the first value that appears more than once, scanning left to right, or `None` if all values are distinct.

### Python
```python
def first_repeated(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return x
        seen.add(x)
    return None
```

The set answers "have I seen this?" in O(1), so one pass suffices: O(n) time, O(n) space. Returning inside the loop guarantees it is the *first* repeat by scan order, not the smallest or most frequent.
