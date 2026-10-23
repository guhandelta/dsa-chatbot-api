---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: arrays-and-hashing
fn_python: grid_is_consistent
fn_javascript: gridIsConsistent
fn_typescript: gridIsConsistent
fn_java: gridIsConsistent
fn_cpp: grid_is_consistent
fn_c: grid_is_consistent
fn_rust: grid_is_consistent
fn_go: gridIsConsistent
fn_csharp: GridIsConsistent
fn_ruby: grid_is_consistent
test_cases: [{"args": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "expected": true}, {"args": [[1, 2, 3, 4, 5, 6, 7, 8, 9, 4, 5, 6, 7, 8, 9, 1, 2, 3, 7, 8, 9, 1, 2, 3, 4, 5, 6, 2, 3, 4, 5, 6, 7, 8, 9, 1, 5, 6, 7, 8, 9, 1, 2, 3, 4, 8, 9, 1, 2, 3, 4, 5, 6, 7, 3, 4, 5, 6, 7, 8, 9, 1, 2, 6, 7, 8, 9, 1, 2, 3, 4, 5, 9, 1, 2, 3, 4, 5, 6, 7, 8]], "expected": true}, {"args": [[1, 1, 3, 4, 5, 6, 7, 8, 9, 4, 5, 6, 7, 8, 9, 1, 2, 3, 7, 8, 9, 1, 2, 3, 4, 5, 6, 2, 3, 4, 5, 6, 7, 8, 9, 1, 5, 6, 7, 8, 9, 1, 2, 3, 4, 8, 9, 1, 2, 3, 4, 5, 6, 7, 3, 4, 5, 6, 7, 8, 9, 1, 2, 6, 7, 8, 9, 1, 2, 3, 4, 5, 9, 1, 2, 3, 4, 5, 6, 7, 8]], "expected": false}, {"args": [[7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "expected": false}, {"args": [[7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "expected": true}, {"args": [[3, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "expected": false}, {"args": [[3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0]], "expected": false}, {"args": [[0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "expected": true}, {"args": [[1, 2, 3, 4, 5, 6, 7, 8, 9, 4, 5, 6, 7, 8, 9, 1, 2, 3, 7, 8, 9, 1, 2, 3, 4, 5, 6, 2, 3, 4, 5, 6, 7, 8, 9, 1, 5, 6, 7, 8, 9, 1, 2, 3, 4, 8, 9, 1, 2, 3, 4, 5, 6, 7, 3, 4, 5, 6, 7, 8, 9, 1, 2, 6, 7, 8, 9, 1, 2, 3, 4, 5, 9, 1, 2, 3, 4, 5, 6, 7, 9]], "expected": false}, {"args": [[5, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "expected": false}]
---

# Grid Consistency — Medium — Arrays and Hashing

## Problem
A grid is given as a flat list `cells` of exactly 81 integers in row-major order, the way a 9×9 Sudoku board is read: the cell in row `r` (0 to 8) and column `c` (0 to 8) is `cells[r * 9 + c]`. A value of 0 means an empty cell; any other value is a digit from 1 to 9. The nine 3×3 boxes are the blocks formed by rows 0–2, 3–5, 6–8 and columns 0–2, 3–5, 6–8. Return `true` if no nonzero digit appears more than once within any row, any column, or any 3×3 box, and `false` otherwise. The grid need not be complete or solvable; only repeats matter.

## Example
cells has zeros everywhere except cells[0] = 4 and cells[10] = 4 → false (position 10 is row 1, column 1, which lies in the same top-left box as position 0)

## Approach
Keep a set of digits already seen for each of the 27 units: 9 rows, 9 columns and 9 boxes. Scan the cells in order. For each nonzero digit, compute its row, column and box index; if the digit is already in any of those three sets, return `false`, otherwise add it to all three. The grid has a fixed size, so the work is constant: O(81) time and space.

## Hints
- The box index is (row / 3) * 3 + (column / 3).
- Skip zero cells before doing any lookups.
- A 27-entry array of bitmasks works as well as sets of digits.

## Solutions
*Conventions: C++ code uses `std::`-qualified names. Java code sits in `class Solution` with `import java.util.*;`. Go and Rust snippets show any needed package import at the top. C returns a heap array and writes its length to `returnSize`.*

### Python
```python
def grid_is_consistent(cells):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    for idx, d in enumerate(cells):
        if d == 0:
            continue
        r, c = divmod(idx, 9)
        b = (r // 3) * 3 + c // 3
        if d in rows[r] or d in cols[c] or d in boxes[b]:
            return False
        rows[r].add(d)
        cols[c].add(d)
        boxes[b].add(d)
    return True
```

### JavaScript
```javascript
function gridIsConsistent(cells) {
  const rows = Array.from({ length: 9 }, () => new Set());
  const cols = Array.from({ length: 9 }, () => new Set());
  const boxes = Array.from({ length: 9 }, () => new Set());
  for (let idx = 0; idx < cells.length; idx++) {
    const d = cells[idx];
    if (d === 0) continue;
    const r = Math.floor(idx / 9);
    const c = idx % 9;
    const b = Math.floor(r / 3) * 3 + Math.floor(c / 3);
    if (rows[r].has(d) || cols[c].has(d) || boxes[b].has(d)) return false;
    rows[r].add(d);
    cols[c].add(d);
    boxes[b].add(d);
  }
  return true;
}
```

### TypeScript
```typescript
function gridIsConsistent(cells: number[]): boolean {
  const rows = Array.from({ length: 9 }, () => new Set<number>());
  const cols = Array.from({ length: 9 }, () => new Set<number>());
  const boxes = Array.from({ length: 9 }, () => new Set<number>());
  for (let idx = 0; idx < cells.length; idx++) {
    const d = cells[idx];
    if (d === 0) continue;
    const r = Math.floor(idx / 9);
    const c = idx % 9;
    const b = Math.floor(r / 3) * 3 + Math.floor(c / 3);
    if (rows[r].has(d) || cols[c].has(d) || boxes[b].has(d)) return false;
    rows[r].add(d);
    cols[c].add(d);
    boxes[b].add(d);
  }
  return true;
}
```

### Java
```java
public boolean gridIsConsistent(long[] cells) {
    List<Set<Long>> rows = new ArrayList<>();
    List<Set<Long>> cols = new ArrayList<>();
    List<Set<Long>> boxes = new ArrayList<>();
    for (int i = 0; i < 9; i++) {
        rows.add(new HashSet<>());
        cols.add(new HashSet<>());
        boxes.add(new HashSet<>());
    }
    for (int idx = 0; idx < cells.length; idx++) {
        long d = cells[idx];
        if (d == 0) continue;
        int r = idx / 9, c = idx % 9;
        int b = (r / 3) * 3 + c / 3;
        if (rows.get(r).contains(d) || cols.get(c).contains(d) || boxes.get(b).contains(d)) return false;
        rows.get(r).add(d);
        cols.get(c).add(d);
        boxes.get(b).add(d);
    }
    return true;
}
```

### C++
```cpp
#include <unordered_set>
#include <vector>
bool grid_is_consistent(std::vector<long long>& cells) {
    std::unordered_set<long long> rows[9], cols[9], boxes[9];
    for (size_t idx = 0; idx < cells.size(); idx++) {
        long long d = cells[idx];
        if (d == 0) continue;
        size_t r = idx / 9, c = idx % 9, b = (r / 3) * 3 + c / 3;
        if (rows[r].count(d) || cols[c].count(d) || boxes[b].count(d)) return false;
        rows[r].insert(d);
        cols[c].insert(d);
        boxes[b].insert(d);
    }
    return true;
}
```

### C
```c
bool grid_is_consistent(long long* cells, int cellsSize) {
    bool seen[3][9][10];  /* [0] rows, [1] columns, [2] boxes; digits 1..9 */
    memset(seen, 0, sizeof seen);
    for (int idx = 0; idx < cellsSize; idx++) {
        int d = (int)cells[idx];
        if (d == 0) continue;
        int r = idx / 9, c = idx % 9, b = (r / 3) * 3 + c / 3;
        if (seen[0][r][d] || seen[1][c][d] || seen[2][b][d]) return false;
        seen[0][r][d] = true;
        seen[1][c][d] = true;
        seen[2][b][d] = true;
    }
    return true;
}
```

### Rust
```rust
use std::collections::HashSet;
pub fn grid_is_consistent(cells: Vec<i64>) -> bool {
    let mut rows: Vec<HashSet<i64>> = vec![HashSet::new(); 9];
    let mut cols: Vec<HashSet<i64>> = vec![HashSet::new(); 9];
    let mut boxes: Vec<HashSet<i64>> = vec![HashSet::new(); 9];
    for (idx, &d) in cells.iter().enumerate() {
        if d == 0 {
            continue;
        }
        let (r, c) = (idx / 9, idx % 9);
        let b = (r / 3) * 3 + c / 3;
        if rows[r].contains(&d) || cols[c].contains(&d) || boxes[b].contains(&d) {
            return false;
        }
        rows[r].insert(d);
        cols[c].insert(d);
        boxes[b].insert(d);
    }
    true
}
```

### Go
```go
func gridIsConsistent(cells []int) bool {
	var rows, cols, boxes [9]map[int]bool
	for i := 0; i < 9; i++ {
		rows[i] = map[int]bool{}
		cols[i] = map[int]bool{}
		boxes[i] = map[int]bool{}
	}
	for idx, d := range cells {
		if d == 0 {
			continue
		}
		r, c := idx/9, idx%9
		b := (r/3)*3 + c/3
		if rows[r][d] || cols[c][d] || boxes[b][d] {
			return false
		}
		rows[r][d] = true
		cols[c][d] = true
		boxes[b][d] = true
	}
	return true
}
```

### C#
```csharp
public static bool GridIsConsistent(long[] cells)
{
    bool[,] rows = new bool[9, 10];
    bool[,] cols = new bool[9, 10];
    bool[,] boxes = new bool[9, 10];
    for (int idx = 0; idx < cells.Length; idx++)
    {
        int d = (int)cells[idx];
        if (d == 0) continue;
        int r = idx / 9, c = idx % 9;
        int b = (r / 3) * 3 + c / 3;
        if (rows[r, d] || cols[c, d] || boxes[b, d]) return false;
        rows[r, d] = true;
        cols[c, d] = true;
        boxes[b, d] = true;
    }
    return true;
}
```

### Ruby
```ruby
def grid_is_consistent(cells)
  rows = Array.new(9) { {} }
  cols = Array.new(9) { {} }
  boxes = Array.new(9) { {} }
  cells.each_with_index do |d, idx|
    next if d.zero?
    r, c = idx.divmod(9)
    b = (r / 3) * 3 + c / 3
    return false if rows[r][d] || cols[c][d] || boxes[b][d]
    rows[r][d] = true
    cols[c][d] = true
    boxes[b][d] = true
  end
  true
end
```
