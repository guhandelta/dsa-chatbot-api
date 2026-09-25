---
track: dsa
difficulty: Medium
source: leetcode
io_mode: function
algorithms: dynamic-programming
fn_python: coin_change
fn_javascript: coinChange
test_cases: [{"args": [[1, 2, 5], 11], "expected": 3}, {"args": [[2], 3], "expected": -1}, {"args": [[1], 0], "expected": 0}, {"args": [[1], 2], "expected": 2}, {"args": [[2, 5, 10, 1], 27], "expected": 4}, {"args": [[186, 419, 83, 408], 6249], "expected": 20}]
---
# Coin Change (LC 322) — Medium — DP

## Problem
Given coin denominations and a target amount, return the fewest coins needed to make the amount, or -1 if impossible. Unlimited supply of each coin.

## Example
coins = [1,2,5], amount = 11 → 3 (5+5+1)

## Approach
Bottom-up DP over amounts 1..amount: dp[a] = 1 + min(dp[a - coin]) over usable coins. Initialize with a sentinel "infinity". Time O(amount × coins), space O(amount).

## Hints
- Subproblem: fewest coins for each smaller amount.
- Greedy (largest coin first) fails — try coins=[1,3,4], amount=6.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def coin_change(coins, amount):
    INF = amount + 1
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] != INF else -1
```

### JavaScript
```javascript
function coinChange(coins, amount) {
  const INF = amount + 1;
  const dp = new Array(amount + 1).fill(INF);
  dp[0] = 0;
  for (let a = 1; a <= amount; a++)
    for (const c of coins)
      if (c <= a) dp[a] = Math.min(dp[a], dp[a - c] + 1);
  return dp[amount] === INF ? -1 : dp[amount];
}
```

### Java
```java
public int coinChange(int[] coins, int amount) {
    int INF = amount + 1;
    int[] dp = new int[amount + 1];
    Arrays.fill(dp, INF);
    dp[0] = 0;
    for (int a = 1; a <= amount; a++)
        for (int c : coins)
            if (c <= a) dp[a] = Math.min(dp[a], dp[a - c] + 1);
    return dp[amount] == INF ? -1 : dp[amount];
}
```

### C++
```cpp
int coinChange(vector<int>& coins, int amount) {
    int INF = amount + 1;
    vector<int> dp(amount + 1, INF);
    dp[0] = 0;
    for (int a = 1; a <= amount; a++)
        for (int c : coins)
            if (c <= a) dp[a] = min(dp[a], dp[a - c] + 1);
    return dp[amount] == INF ? -1 : dp[amount];
}
```

### C
```c
int coinChange(int* coins, int coinsSize, int amount) {
    int INF = amount + 1;
    int* dp = malloc((amount + 1) * sizeof(int));
    dp[0] = 0;
    for (int a = 1; a <= amount; a++) dp[a] = INF;
    for (int a = 1; a <= amount; a++)
        for (int i = 0; i < coinsSize; i++)
            if (coins[i] <= a && dp[a - coins[i]] + 1 < dp[a])
                dp[a] = dp[a - coins[i]] + 1;
    int res = dp[amount] == INF ? -1 : dp[amount];
    free(dp);
    return res;
}
```

### Rust
```rust
pub fn coin_change(coins: Vec<i32>, amount: i32) -> i32 {
    let amount = amount as usize;
    let inf = (amount + 1) as i32;
    let mut dp = vec![inf; amount + 1];
    dp[0] = 0;
    for a in 1..=amount {
        for &c in &coins {
            let c = c as usize;
            if c <= a {
                dp[a] = dp[a].min(dp[a - c] + 1);
            }
        }
    }
    if dp[amount] == inf { -1 } else { dp[amount] }
}
```
