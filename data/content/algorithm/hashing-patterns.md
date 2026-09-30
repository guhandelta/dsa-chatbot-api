---
track: algorithm
difficulty: Easy
algorithms: hashing-patterns
category: Data Structure
source: authored
io_mode: function
---
# Hash table problem patterns — Easy — Data Structure

| Pattern | Key → value | Example problems |
| --- | --- | --- |
| Complement lookup | value → index | Two sum, pairs with difference k |
| Frequency count | item → count | Top k frequent, valid anagram, majority element |
| Canonical grouping | sorted string or count tuple → list | Group anagrams, group shifted strings |
| Prefix sum index | prefix sum → count or first index | Subarray sum equals k, longest balanced subarray |
| Seen set | item → presence | Contains duplicate, longest consecutive sequence, cycle detection |
| Last position | item → last index | Longest substring without repeating characters |

#### Two sum and subarray sum equals k — Python

```python
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return seen[target - x], i
        seen[x] = i
    return None

def subarray_sum_count(nums, k):
    count, prefix, freq = 0, 0, {0: 1}
    for x in nums:
        prefix += x
        count += freq.get(prefix - k, 0)
        freq[prefix] = freq.get(prefix, 0) + 1
    return count
```
