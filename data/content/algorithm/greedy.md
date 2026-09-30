---
track: algorithm
difficulty: Hard
algorithms: greedy
category: Paradigm
source: authored
io_mode: function
---
# Greedy algorithms — Hard — Paradigm

A greedy algorithm commits to the locally best choice at each step and never revisits it. It is correct only when an exchange argument shows that replacing any optimal solution's choice with the greedy choice never makes it worse; otherwise use dynamic programming.

| Problem | Greedy rule |
| --- | --- |
| Activity selection, non-overlapping intervals | Sort by end time; take each interval starting at or after the last taken end |
| Merge intervals | Sort by start; extend the current interval while the next one overlaps |
| Minimum arrows / meeting rooms | Sort by end (arrows) or sweep start and end times with a min-heap (rooms) |
| Jump game | Track the farthest reachable index |
| Gas station | If total gas ≥ total cost, start after the last index where the running balance went negative |
| Task scheduler | Place the most frequent task first; fill gaps with other tasks or idle slots |
| Huffman coding | Repeatedly merge the two lowest-frequency nodes from a min-heap |
| Fractional knapsack | Take items in decreasing value-to-weight ratio |
| Coin change | Greedy works only for canonical coin systems such as 1, 5, 10, 25; use DP otherwise |

#### Merge intervals — Python

```python
def merge_intervals(intervals):
    intervals.sort(key=lambda x: x[0])
    merged = []
    for start, end in intervals:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
```
