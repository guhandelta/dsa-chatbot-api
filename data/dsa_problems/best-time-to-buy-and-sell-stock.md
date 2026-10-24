---
track: dsa
difficulty: Easy
source: authored
io_mode: function
algorithms: arrays, greedy
fn_python: max_profit
fn_javascript: maxProfit
fn_typescript: maxProfit
fn_java: maxProfit
fn_cpp: max_profit
fn_c: max_profit
fn_rust: max_profit
fn_go: maxProfit
fn_csharp: MaxProfit
fn_ruby: max_profit
test_cases: [{"args": [[]], "expected": 0}, {"args": [[4]], "expected": 0}, {"args": [[10, 9, 8, 1]], "expected": 0}, {"args": [[4, 4, 4, 4]], "expected": 0}, {"args": [[1, 10]], "expected": 9}, {"args": [[5, 1, 4, 2, 6, 0, 3]], "expected": 5}, {"args": [[2000000000, 1, 2147483647]], "expected": 2147483646}, {"args": [[6, 2, 6, 1, 6]], "expected": 5}]
---
# Largest Gain from One Trade — Easy — Array, Greedy

## Problem
`quotes[i]` is the price of an item on day i. You may choose one day to buy and a later day to sell; the sale must come after the purchase. Return the largest gain that one such buy-then-sell trade can produce. If no trade produces a positive gain, return 0. An empty list means there are no days to trade, so the answer is 0. Every price fits in a signed 32-bit integer.

## Example
quotes = [3,8,2,9,4] → 7 (buy on day 2 at 2, sell on day 3 at 9)

## Approach
Walk the days in order and remember the lowest price seen so far. For each day, the best gain from selling that day is today's price minus that lowest price. Keep the largest such gain, starting from 0. Time O(n), space O(1).

## Hints
- For any sale day, the best purchase is the cheapest day before it.
- Start the running best at zero so that a list with no profitable trade returns 0.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution`.*

### Python
```python
def max_profit(quotes):
    best, cheapest = 0, float('inf')
    for q in quotes:
        cheapest = min(cheapest, q)
        best = max(best, q - cheapest)
    return best
```

### JavaScript
```javascript
function maxProfit(quotes) {
  let best = 0, cheapest = Infinity;
  for (const q of quotes) {
    cheapest = Math.min(cheapest, q);
    best = Math.max(best, q - cheapest);
  }
  return best;
}
```

### TypeScript
```typescript
function maxProfit(quotes: number[]): number {
  let best = 0, cheapest = Infinity;
  for (const q of quotes) {
    cheapest = Math.min(cheapest, q);
    best = Math.max(best, q - cheapest);
  }
  return best;
}
```

### Java
```java
public int maxProfit(int[] quotes) {
    int best = 0, cheapest = Integer.MAX_VALUE;
    for (int q : quotes) {
        cheapest = Math.min(cheapest, q);
        best = Math.max(best, q - cheapest);
    }
    return best;
}
```

### C++
```cpp
#include <algorithm>
#include <climits>
#include <vector>
int max_profit(std::vector<int>& quotes) {
    int best = 0, cheapest = INT_MAX;
    for (int q : quotes) {
        cheapest = std::min(cheapest, q);
        best = std::max(best, q - cheapest);
    }
    return best;
}
```

### C
```c
#include <limits.h>
long long max_profit(long long* quotes, int quotesSize) {
    long long best = 0, cheapest = LLONG_MAX;
    for (int i = 0; i < quotesSize; i++) {
        if (quotes[i] < cheapest) cheapest = quotes[i];
        if (quotes[i] - cheapest > best) best = quotes[i] - cheapest;
    }
    return best;
}
```

### Rust
```rust
pub fn max_profit(quotes: Vec<i32>) -> i32 {
    let (mut best, mut cheapest) = (0, i32::MAX);
    for q in quotes {
        cheapest = cheapest.min(q);
        best = best.max(q - cheapest);
    }
    best
}
```

### Go
```go
func maxProfit(quotes []int) int {
	if len(quotes) == 0 {
		return 0
	}
	best, cheapest := 0, quotes[0]
	for _, q := range quotes {
		if q < cheapest {
			cheapest = q
		}
		if q-cheapest > best {
			best = q - cheapest
		}
	}
	return best
}
```

### C#
```csharp
public static int MaxProfit(int[] quotes)
{
    int best = 0, cheapest = int.MaxValue;
    foreach (int q in quotes)
    {
        cheapest = System.Math.Min(cheapest, q);
        best = System.Math.Max(best, q - cheapest);
    }
    return best;
}
```

### Ruby
```ruby
def max_profit(quotes)
  best = 0
  cheapest = Float::INFINITY
  quotes.each do |q|
    cheapest = [cheapest, q].min
    best = [best, q - cheapest].max
  end
  best
end
```
