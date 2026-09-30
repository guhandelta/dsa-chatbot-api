---
track: algorithm
difficulty: Hard
algorithms: knapsack-coin-change
category: Paradigm
source: authored
io_mode: function
---
# Knapsack and coin change — Hard — Paradigm

In 0/1 knapsack each item is used at most once, so the 1D table is filled with capacity decreasing (each item reads values from before it was considered). In unbounded knapsack and coin change, items repeat, so capacity increases. For counting combinations in coin change, loop coins outside and amounts inside; swapping the loops counts ordered permutations instead.

#### Knapsack and coin change — Python

```python
def knapsack_01(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for c in range(capacity, w - 1, -1):      # decreasing: each item once
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[capacity]

def coin_change_min(coins, amount):             # fewest coins, -1 if impossible
    INF = amount + 1
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] <= amount else -1

def coin_change_ways(coins, amount):            # number of combinations
    dp = [1] + [0] * amount
    for c in coins:
        for a in range(c, amount + 1):
            dp[a] += dp[a - c]
    return dp[amount]
```
