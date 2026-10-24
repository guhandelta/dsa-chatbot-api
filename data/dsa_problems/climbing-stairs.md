---
track: dsa
difficulty: Easy
source: authored
io_mode: function
algorithms: dynamic-programming
fn_python: climb_stairs
fn_javascript: climbStairs
fn_typescript: climbStairs
fn_java: climbStairs
fn_cpp: climb_stairs
fn_c: climb_stairs
fn_rust: climb_stairs
fn_go: climbStairs
fn_csharp: ClimbStairs
fn_ruby: climb_stairs
test_cases: [{"args": [0], "expected": 1}, {"args": [1], "expected": 1}, {"args": [6], "expected": 13}, {"args": [7], "expected": 21}, {"args": [12], "expected": 233}, {"args": [20], "expected": 10946}, {"args": [30], "expected": 1346269}, {"args": [44], "expected": 1134903170}]
---
# Count Ways to Cover a Distance with Moves of One or Two — Easy — DP

## Problem
A walker must cover exactly n units of distance, where each move covers either 1 unit or 2 units. Count the distinct ordered sequences of moves whose lengths add up to exactly n. For n = 0 the answer is 1, the empty sequence. Return the count as an integer.

## Example
n = 4 → 5 (1+1+1+1, 1+1+2, 1+2+1, 2+1+1, 2+2)

## Approach
Let ways(k) be the number of sequences that cover exactly k units. Consider the last move: it covers 1 unit or 2 units, so ways(k) = ways(k-1) + ways(k-2), with ways(0) = 1 and ways(1) = 1. Keep only the last two values while counting upward. Time O(n), space O(1).

## Hints
- Think about how the final move could have been made.
- Two running variables are enough; a full table is not needed.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution`.*

### Python
```python
def climb_stairs(n):
    prev, cur = 1, 1       # ways(0), ways(1)
    for _ in range(n - 1):
        prev, cur = cur, prev + cur
    return cur
```

### JavaScript
```javascript
function climbStairs(n) {
  let prev = 1, cur = 1;
  for (let i = 0; i < n - 1; i++) [prev, cur] = [cur, prev + cur];
  return cur;
}
```

### TypeScript
```typescript
function climbStairs(n: number): number {
  let prev = 1, cur = 1;
  for (let i = 0; i < n - 1; i++) [prev, cur] = [cur, prev + cur];
  return cur;
}
```

### Java
```java
public int climbStairs(int n) {
    int prev = 1, cur = 1;
    for (int i = 0; i < n - 1; i++) {
        int next = prev + cur;
        prev = cur;
        cur = next;
    }
    return cur;
}
```

### C++
```cpp
int climb_stairs(int n) {
    int prev = 1, cur = 1;
    for (int i = 0; i < n - 1; i++) {
        int next = prev + cur;
        prev = cur;
        cur = next;
    }
    return cur;
}
```

### C
```c
long long climb_stairs(long long n) {
    long long prev = 1, cur = 1;
    for (long long i = 0; i < n - 1; i++) {
        long long next = prev + cur;
        prev = cur;
        cur = next;
    }
    return cur;
}
```

### Rust
```rust
pub fn climb_stairs(n: i32) -> i32 {
    let (mut prev, mut cur) = (1, 1);
    for _ in 0..n - 1 {
        let next = prev + cur;
        prev = cur;
        cur = next;
    }
    cur
}
```

### Go
```go
func climbStairs(n int) int {
	prev, cur := 1, 1
	for i := 0; i < n-1; i++ {
		prev, cur = cur, prev+cur
	}
	return cur
}
```

### C#
```csharp
public static int ClimbStairs(int n)
{
    int prev = 1, cur = 1;
    for (int i = 0; i < n - 1; i++)
    {
        int next = prev + cur;
        prev = cur;
        cur = next;
    }
    return cur;
}
```

### Ruby
```ruby
def climb_stairs(n)
  prev = 1
  cur = 1
  (n - 1).times do
    prev, cur = cur, prev + cur
  end
  cur
end
```
