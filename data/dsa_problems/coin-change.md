---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: dynamic-programming
fn_python: coin_change
fn_javascript: coinChange
fn_typescript: coinChange
fn_java: coinChange
fn_cpp: coinChange
fn_c: coinChange
fn_rust: coin_change
fn_go: coinChange
fn_csharp: CoinChange
fn_ruby: coin_change
test_cases: [{"args": [[3, 7], 26], "expected": 6}, {"args": [[4, 6], 7], "expected": -1}, {"args": [[], 0], "expected": 0}, {"args": [[], 5], "expected": -1}, {"args": [[5, 5, 5], 15], "expected": 3}, {"args": [[1, 3, 4], 6], "expected": 2}, {"args": [[7], 0], "expected": 0}, {"args": [[2, 9, 10, 1], 100], "expected": 10}, {"args": [[6, 10, 15], 61], "expected": 5}, {"args": [[250, 1], 2500], "expected": 10}, {"args": [[1, 2], 0], "expected": 0}]
---
# Fewest Tokens for a Target Sum — Medium — DP

## Problem
You are given a list `coins` of positive integer token values and a non-negative integer `amount`. You have an unlimited supply of every token value. Find the smallest number of tokens whose values add up to exactly `amount`, and return that count. If no combination of tokens reaches `amount`, return -1.

The list may be empty. In that case the answer is 0 when `amount` is 0, and -1 otherwise.

## Example
coins = [4, 9, 10], amount = 18 → 2 (9 + 9)

## Approach
Build a table `best` where `best[t]` is the fewest tokens that reach the total `t`, for every `t` from 0 to `amount`. Set `best[0] = 0`. For each larger total, try every token that fits and take one more than the count for the remainder; totals that cannot be reached keep a large sentinel value. Time O(amount × number of tokens), space O(amount).

## Hints
- Each entry depends only on smaller totals, so fill the table in increasing order.
- Always taking the largest token that fits is not safe. With tokens 1, 3 and 4 and a total of 6, the greedy choice gives 4 + 1 + 1 (three tokens), while 3 + 3 uses only two.

## Solutions
*Conventions: C++ code uses `std::` names and includes the headers it needs. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution`.*

### Python
```python
def coin_change(coins, amount):
    unreachable = float('inf')
    table = [0] + [unreachable] * amount
    for total in range(1, amount + 1):
        for token in coins:
            if token <= total and table[total - token] + 1 < table[total]:
                table[total] = table[total - token] + 1
    return -1 if table[amount] == unreachable else table[amount]
```

### JavaScript
```javascript
function coinChange(coins, amount) {
  const reach = new Array(amount + 1).fill(Infinity);
  reach[0] = 0;
  for (let total = 1; total <= amount; total++)
    for (const token of coins)
      if (token <= total && reach[total - token] + 1 < reach[total])
        reach[total] = reach[total - token] + 1;
  return reach[amount] === Infinity ? -1 : reach[amount];
}
```

### TypeScript
```typescript
function coinChange(coins: number[], amount: number): number {
  const reach: number[] = new Array(amount + 1).fill(Infinity);
  reach[0] = 0;
  for (let total = 1; total <= amount; total++)
    for (const token of coins)
      if (token <= total && reach[total - token] + 1 < reach[total])
        reach[total] = reach[total - token] + 1;
  return reach[amount] === Infinity ? -1 : reach[amount];
}
```

### Java
```java
public int coinChange(int[] coins, int amount) {
    final int UNREACHABLE = Integer.MAX_VALUE / 2;
    int[] best = new int[amount + 1];
    Arrays.fill(best, UNREACHABLE);
    best[0] = 0;
    for (int total = 1; total <= amount; total++)
        for (int token : coins)
            if (token <= total) best[total] = Math.min(best[total], best[total - token] + 1);
    return best[amount] >= UNREACHABLE ? -1 : best[amount];
}
```

### C++
```cpp
int coinChange(std::vector<int>& coins, int amount) {
    const int unreachable = amount + 1;   // a real answer is never above amount
    std::vector<int> best(amount + 1, unreachable);
    best[0] = 0;
    for (int total = 1; total <= amount; total++)
        for (int token : coins)
            if (token <= total) best[total] = std::min(best[total], best[total - token] + 1);
    return best[amount] == unreachable ? -1 : best[amount];
}
```

### C
```c
long long coinChange(long long* coins, int coinsSize, long long amount) {
    long long unreachable = amount + 1;
    long long* best = malloc((amount + 1) * sizeof(long long));
    best[0] = 0;
    for (long long total = 1; total <= amount; total++) {
        best[total] = unreachable;
        for (int i = 0; i < coinsSize; i++) {
            long long token = coins[i];
            if (token <= total && best[total - token] + 1 < best[total])
                best[total] = best[total - token] + 1;
        }
    }
    long long result = best[amount] == unreachable ? -1 : best[amount];
    free(best);
    return result;
}
```

### Rust
```rust
pub fn coin_change(coins: Vec<i32>, amount: i32) -> i32 {
    let target = amount as usize;
    let unreachable = amount + 1;
    let mut best = vec![unreachable; target + 1];
    best[0] = 0;
    for total in 1..=target {
        for &token in coins.iter() {
            let token = token as usize;
            if token <= total && best[total - token] + 1 < best[total] {
                best[total] = best[total - token] + 1;
            }
        }
    }
    if best[target] == unreachable { -1 } else { best[target] }
}
```

### Go
```go
func coinChange(coins []int, amount int) int {
	unreachable := amount + 1
	best := make([]int, amount+1)
	for total := 1; total <= amount; total++ {
		best[total] = unreachable
		for _, token := range coins {
			if token <= total && best[total-token]+1 < best[total] {
				best[total] = best[total-token] + 1
			}
		}
	}
	if best[amount] == unreachable {
		return -1
	}
	return best[amount]
}
```

### C#
```csharp
public static int CoinChange(int[] coins, int amount) {
    int unreachable = amount + 1;
    int[] best = new int[amount + 1];
    for (int total = 1; total <= amount; total++) {
        best[total] = unreachable;
        foreach (int token in coins) {
            if (token <= total && best[total - token] + 1 < best[total])
                best[total] = best[total - token] + 1;
        }
    }
    return best[amount] == unreachable ? -1 : best[amount];
}
```

### Ruby
```ruby
def coin_change(coins, amount)
  best = Array.new(amount + 1, nil)
  best[0] = 0
  (1..amount).each do |total|
    options = coins.select { |token| token <= total && best[total - token] }
    best[total] = options.map { |token| best[total - token] + 1 }.min
  end
  best[amount] || -1
end
```
