---
track: dsa
difficulty: Easy
source: leetcode
io_mode: function
algorithms: arrays, greedy
fn_python: max_profit
fn_javascript: maxProfit
test_cases: [{"args": [[7, 1, 5, 3, 6, 4]], "expected": 5}, {"args": [[7, 6, 4, 3, 1]], "expected": 0}, {"args": [[1]], "expected": 0}, {"args": [[2, 4, 1]], "expected": 2}, {"args": [[3, 3, 3]], "expected": 0}, {"args": [[1, 2]], "expected": 1}]
---
# Best Time to Buy and Sell Stock (LC 121) — Easy — Array, Greedy

## Problem
Given `prices[i]`, the price of a stock on day i, choose one day to buy and a later day to sell to maximize profit. Return the max profit, or 0 if no profit is possible.

## Example
prices = [7,1,5,3,6,4] → 5 (buy at 1, sell at 6)

## Approach
Track the minimum price seen so far; at each day, candidate profit = price - minSoFar. Keep the best. Time O(n), space O(1).

## Hints
- You only ever need the cheapest price before today.
- One pass; no nested loops needed.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def max_profit(prices):
    best, low = 0, float('inf')
    for p in prices:
        low = min(low, p)
        best = max(best, p - low)
    return best
```

### JavaScript
```javascript
function maxProfit(prices) {
  let best = 0, low = Infinity;
  for (const p of prices) {
    low = Math.min(low, p);
    best = Math.max(best, p - low);
  }
  return best;
}
```

### Java
```java
public int maxProfit(int[] prices) {
    int best = 0, low = Integer.MAX_VALUE;
    for (int p : prices) {
        low = Math.min(low, p);
        best = Math.max(best, p - low);
    }
    return best;
}
```

### C++
```cpp
int maxProfit(vector<int>& prices) {
    int best = 0, low = INT_MAX;
    for (int p : prices) {
        low = min(low, p);
        best = max(best, p - low);
    }
    return best;
}
```

### C
```c
int maxProfit(int* prices, int pricesSize) {
    int best = 0, low = INT_MAX;
    for (int i = 0; i < pricesSize; i++) {
        if (prices[i] < low) low = prices[i];
        if (prices[i] - low > best) best = prices[i] - low;
    }
    return best;
}
```

### Rust
```rust
pub fn max_profit(prices: Vec<i32>) -> i32 {
    let (mut best, mut low) = (0, i32::MAX);
    for p in prices {
        low = low.min(p);
        best = best.max(p - low);
    }
    best
}
```
