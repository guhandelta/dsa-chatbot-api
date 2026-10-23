---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: arrays-and-hashing
fn_python: top_frequent
fn_javascript: topFrequent
fn_typescript: topFrequent
fn_java: topFrequent
fn_cpp: top_frequent
fn_c: top_frequent
fn_rust: top_frequent
fn_go: topFrequent
fn_csharp: TopFrequent
fn_ruby: top_frequent
test_cases: [{"args": [[5], 1], "expected": [5]}, {"args": [[2, 2, 1, 1, 3], 1], "expected": [1]}, {"args": [[2, 2, 1, 1, 3], 2], "expected": [1, 2]}, {"args": [[2, 2, 1, 1, 3], 3], "expected": [1, 2, 3]}, {"args": [[7, 7, 7, -3, -3, 0], 2], "expected": [7, -3]}, {"args": [[10, 20, 30, 40], 4], "expected": [10, 20, 30, 40]}, {"args": [[6, 6, 6, 6, 5, 5, 5, 8, 8, 1, 1, 1, 1, 1], 3], "expected": [1, 6, 5]}, {"args": [[100, -100, 100, -100, 0, 0, 0, 0, 1], 2], "expected": [0, -100]}]
---

# Most Frequent Values — Medium — Arrays and Hashing

## Problem
Given a list of integers `values` and an integer `k`, return the `k` values that occur most often in `values`, as a list ordered from most frequent to least frequent. When two values occur equally often, the smaller value comes first. Each distinct value appears at most once in the answer. You may assume 1 ≤ `k` ≤ the number of distinct values in `values`, so `values` is never empty. Negative values are allowed.

## Example
values = [4,4,9,-1,9,9,3,-1,4,8], k = 3 → [4,9,-1] (4 and 9 each occur three times, with 4 first; -1 occurs twice)

## Approach
Count each value with a hash map, then place every distinct value into a bucket indexed by its count. Filling the buckets from the distinct values in ascending order keeps each bucket sorted, so the tie rule comes for free. Reading the buckets from the highest count downward and stopping after `k` values gives the answer. Time O(n + d log d) for d distinct values, space O(n).

## Hints
- A count can be at most n, so the buckets need n + 1 slots.
- Fill the buckets from the sorted distinct values so ties come out smallest first.
- Stop as soon as k values are collected.

## Solutions
*Conventions: C++ code uses `std::`-qualified names. Java code sits in `class Solution` with `import java.util.*;`. Go and Rust snippets show any needed package import at the top. C returns a heap array and writes its length to `returnSize`.*

### Python
```python
def top_frequent(values, k):
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    n = len(values)
    buckets = [[] for _ in range(n + 1)]
    for v in sorted(counts):
        buckets[counts[v]].append(v)
    out = []
    for c in range(n, 0, -1):
        for v in buckets[c]:
            if len(out) == k:
                return out
            out.append(v)
    return out
```

### JavaScript
```javascript
function topFrequent(values, k) {
  const counts = new Map();
  for (const v of values) counts.set(v, (counts.get(v) || 0) + 1);
  const n = values.length;
  const buckets = Array.from({ length: n + 1 }, () => []);
  for (const v of [...counts.keys()].sort((a, b) => a - b)) buckets[counts.get(v)].push(v);
  const out = [];
  for (let c = n; c >= 1 && out.length < k; c--) {
    for (const v of buckets[c]) {
      if (out.length === k) break;
      out.push(v);
    }
  }
  return out;
}
```

### TypeScript
```typescript
function topFrequent(values: number[], k: number): number[] {
  const counts = new Map<number, number>();
  for (const v of values) counts.set(v, (counts.get(v) || 0) + 1);
  const n = values.length;
  const buckets: number[][] = Array.from({ length: n + 1 }, () => [] as number[]);
  for (const v of [...counts.keys()].sort((a, b) => a - b)) buckets[counts.get(v)!].push(v);
  const out: number[] = [];
  for (let c = n; c >= 1 && out.length < k; c--) {
    for (const v of buckets[c]) {
      if (out.length === k) break;
      out.push(v);
    }
  }
  return out;
}
```

### Java
```java
public long[] topFrequent(long[] values, long k) {
    Map<Long, Integer> counts = new HashMap<>();
    for (long v : values) counts.merge(v, 1, Integer::sum);
    int n = values.length;
    List<List<Long>> buckets = new ArrayList<>();
    for (int c = 0; c <= n; c++) buckets.add(new ArrayList<>());
    List<Long> keys = new ArrayList<>(counts.keySet());
    Collections.sort(keys);
    for (long v : keys) buckets.get(counts.get(v)).add(v);
    long[] out = new long[(int) k];
    int filled = 0;
    for (int c = n; c >= 1 && filled < k; c--) {
        for (long v : buckets.get(c)) {
            if (filled == k) break;
            out[filled++] = v;
        }
    }
    return out;
}
```

### C++
```cpp
#include <map>
#include <vector>
std::vector<long long> top_frequent(std::vector<long long>& values, long long k) {
    std::map<long long, long long> counts;
    for (long long v : values) counts[v]++;
    long long n = (long long)values.size();
    std::vector<std::vector<long long>> buckets(n + 1);
    for (auto& p : counts) buckets[p.second].push_back(p.first);
    std::vector<long long> out;
    for (long long c = n; c >= 1 && (long long)out.size() < k; c--) {
        for (long long v : buckets[c]) {
            if ((long long)out.size() == k) break;
            out.push_back(v);
        }
    }
    return out;
}
```

### C
```c
static int cmp_ll(const void* a, const void* b) {
    long long x = *(const long long*)a, y = *(const long long*)b;
    return (x > y) - (x < y);
}
long long* top_frequent(long long* values, int valuesSize, long long k, int* returnSize) {
    long long* sorted = malloc((valuesSize + 1) * sizeof(long long));
    memcpy(sorted, values, valuesSize * sizeof(long long));
    qsort(sorted, valuesSize, sizeof(long long), cmp_ll);
    long long* vals = malloc((valuesSize + 1) * sizeof(long long));
    int* cnts = malloc((valuesSize + 1) * sizeof(int));
    bool* used = calloc(valuesSize + 1, sizeof(bool));
    int d = 0;
    for (int i = 0; i < valuesSize;) {
        int j = i;
        while (j < valuesSize && sorted[j] == sorted[i]) j++;
        vals[d] = sorted[i];
        cnts[d] = j - i;
        d++;
        i = j;
    }
    int want = (int)k;
    long long* out = malloc((want + 1) * sizeof(long long));
    for (int t = 0; t < want; t++) {
        int best = -1;
        for (int x = 0; x < d; x++) {
            if (!used[x] && (best < 0 || cnts[x] > cnts[best])) best = x;
        }
        used[best] = true;
        out[t] = vals[best];
    }
    *returnSize = want;
    free(sorted);
    free(vals);
    free(cnts);
    free(used);
    return out;
}
```

### Rust
```rust
use std::collections::BTreeMap;
pub fn top_frequent(values: Vec<i64>, k: i64) -> Vec<i64> {
    let n = values.len();
    let mut counts: BTreeMap<i64, usize> = BTreeMap::new();
    for v in values {
        *counts.entry(v).or_insert(0) += 1;
    }
    let mut buckets: Vec<Vec<i64>> = vec![Vec::new(); n + 1];
    for (&v, &c) in &counts {
        buckets[c].push(v);
    }
    let mut out: Vec<i64> = Vec::new();
    for c in (1..=n).rev() {
        for &v in &buckets[c] {
            if out.len() as i64 == k {
                return out;
            }
            out.push(v);
        }
    }
    out
}
```

### Go
```go
import "sort"

func topFrequent(values []int, k int) []int {
	counts := make(map[int]int)
	for _, v := range values {
		counts[v]++
	}
	keys := make([]int, 0, len(counts))
	for v := range counts {
		keys = append(keys, v)
	}
	sort.Ints(keys)
	n := len(values)
	buckets := make([][]int, n+1)
	for _, v := range keys {
		buckets[counts[v]] = append(buckets[counts[v]], v)
	}
	out := []int{}
	for c := n; c >= 1 && len(out) < k; c-- {
		for _, v := range buckets[c] {
			if len(out) == k {
				break
			}
			out = append(out, v)
		}
	}
	return out
}
```

### C#
```csharp
public static long[] TopFrequent(long[] values, long k)
{
    var counts = new System.Collections.Generic.Dictionary<long, int>();
    foreach (long v in values)
    {
        counts[v] = counts.ContainsKey(v) ? counts[v] + 1 : 1;
    }
    int n = values.Length;
    var keys = new System.Collections.Generic.List<long>(counts.Keys);
    keys.Sort();
    var buckets = new System.Collections.Generic.List<long>[n + 1];
    for (int c = 0; c <= n; c++) buckets[c] = new System.Collections.Generic.List<long>();
    foreach (long v in keys) buckets[counts[v]].Add(v);
    var outList = new System.Collections.Generic.List<long>();
    for (int c = n; c >= 1 && outList.Count < k; c--)
    {
        foreach (long v in buckets[c])
        {
            if (outList.Count == k) break;
            outList.Add(v);
        }
    }
    return outList.ToArray();
}
```

### Ruby
```ruby
def top_frequent(values, k)
  counts = Hash.new(0)
  values.each { |v| counts[v] += 1 }
  n = values.length
  buckets = Array.new(n + 1) { [] }
  counts.keys.sort.each { |v| buckets[counts[v]] << v }
  out = []
  n.downto(1) do |c|
    buckets[c].each do |v|
      return out if out.length == k
      out << v
    end
  end
  out
end
```
