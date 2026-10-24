---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: matrix-and-grid
fn_python: rotate_grid
fn_javascript: rotateGrid
fn_typescript: rotateGrid
fn_java: rotateGrid
fn_cpp: rotate_grid
fn_c: rotate_grid
fn_rust: rotate_grid
fn_go: rotateGrid
fn_csharp: RotateGrid
fn_ruby: rotate_grid
test_cases: [{"args": [[], 1], "expected": []}, {"args": [[7], 1], "expected": [7]}, {"args": [[1, 2, 3, 4, 5, 6], 3], "expected": [4, 1, 5, 2, 6, 3]}, {"args": [[1, 2, 3, 4, 5, 6, 7, 8, 9], 3], "expected": [7, 4, 1, 8, 5, 2, 9, 6, 3]}, {"args": [[1, 2, 3, 4], 1], "expected": [4, 3, 2, 1]}, {"args": [[2, 2, 1, 2], 2], "expected": [1, 2, 2, 2]}, {"args": [[1, 2, 3, 4, 5, 6, 7, 8], 4], "expected": [5, 1, 6, 2, 7, 3, 8, 4]}, {"args": [[-5, 1000000000, 0, 3], 2], "expected": [0, -5, 3, 1000000000]}]
---
# Rotate a Grid 90 Degrees — Medium — Matrix

## Problem
A grid of integers is passed as a flat array `values` in row-major order, together with the number of columns `cols`.

- `cols` is at least 1.
- `len(values)` is a multiple of `cols`. The number of rows is `rows = len(values) / cols`. Neither `rows` nor a separate matrix type is passed in.
- The element in row `r` (0-based, 0 ≤ r < rows) and column `c` (0 ≤ c < cols) is `values[r * cols + c]`.

Return the grid rotated 90 degrees clockwise, also as a flat row-major array. The rotated grid has `cols` rows and `rows` columns, so its length is `rows * cols`. Its element in row `i` (0 ≤ i < cols) and column `j` (0 ≤ j < rows) is `values[(rows - 1 - j) * cols + i]`.

If `values` is empty, return an empty array.

## Example
values = [1,2,3,4,5,6], cols = 3 → a 2×3 grid
```
1 2 3
4 5 6
```
rotated clockwise gives a 3×2 grid
```
4 1
5 2
6 3
```
returned flat as [4,1,5,2,6,3].

## Approach
Each column of the input, read from bottom to top, becomes a row of the output. Input column `i` has its elements at indices `i, i + cols, i + 2·cols, …`, so the output row `i` is built by walking the input from the last row to the first. Write each element directly to its output index `i * rows + j`. Time O(n), space O(n) for the output, where n = len(values).

Checking the formula on the example (rows = 2, cols = 3): output index 0 (i = 0, j = 0) is `values[(2 - 1 - 0) * 3 + 0] = values[3] = 4`, and output index 1 (i = 0, j = 1) is `values[(2 - 1 - 1) * 3 + 0] = values[0] = 1`. The output starts [4,1,…], as expected.

## Hints
- Work out `rows` from `len(values) / cols` first, and handle the empty case before dividing.
- Hold the row-major layout fixed: the input index of (row r, column c) is `r * cols + c`.
- Test a non-square case, such as 2×4 or 4×1. Mixing up `rows` and `cols` only shows up there.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution`. C returns a heap array and writes its length to `returnSize`.*

### Python
```python
def rotate_grid(values, cols):
    n = len(values)
    if n == 0:
        return []
    rows = n // cols
    out = [0] * n
    for i in range(cols):
        for j in range(rows):
            out[i * rows + j] = values[(rows - 1 - j) * cols + i]
    return out
```

### JavaScript
```javascript
function rotateGrid(values, cols) {
  const n = values.length;
  if (n === 0) return [];
  const rows = n / cols;
  const out = new Array(n);
  for (let i = 0; i < cols; i++)
    for (let j = 0; j < rows; j++)
      out[i * rows + j] = values[(rows - 1 - j) * cols + i];
  return out;
}
```

### TypeScript
```typescript
function rotateGrid(values: number[], cols: number): number[] {
  const n = values.length;
  if (n === 0) return [];
  const rows = n / cols;
  const out: number[] = new Array(n);
  for (let i = 0; i < cols; i++)
    for (let j = 0; j < rows; j++)
      out[i * rows + j] = values[(rows - 1 - j) * cols + i];
  return out;
}
```

### Java
```java
public int[] rotateGrid(int[] values, int cols) {
    int n = values.length;
    if (n == 0) return new int[0];
    int rows = n / cols;
    int[] out = new int[n];
    for (int i = 0; i < cols; i++)
        for (int j = 0; j < rows; j++)
            out[i * rows + j] = values[(rows - 1 - j) * cols + i];
    return out;
}
```

### C++
```cpp
std::vector<long long> rotate_grid(std::vector<long long>& values, long long cols) {
    int n = values.size();
    if (n == 0) return {};
    long long rows = n / cols;
    std::vector<long long> out(n);
    for (long long i = 0; i < cols; i++)
        for (long long j = 0; j < rows; j++)
            out[i * rows + j] = values[(rows - 1 - j) * cols + i];
    return out;
}
```

### C
```c
long long* rotate_grid(long long* values, int valuesSize, long long cols, int* returnSize) {
    int n = valuesSize;
    long long* out = malloc((n + 1) * sizeof(long long));
    *returnSize = n;
    if (n == 0) return out;
    long long rows = n / cols;
    for (long long i = 0; i < cols; i++)
        for (long long j = 0; j < rows; j++)
            out[i * rows + j] = values[(rows - 1 - j) * cols + i];
    return out;
}
```

### Rust
```rust
pub fn rotate_grid(values: Vec<i32>, cols: i32) -> Vec<i32> {
    let n = values.len();
    if n == 0 {
        return vec![];
    }
    let cols = cols as usize;
    let rows = n / cols;
    let mut out = vec![0; n];
    for i in 0..cols {
        for j in 0..rows {
            out[i * rows + j] = values[(rows - 1 - j) * cols + i];
        }
    }
    out
}
```

### Go
```go
func rotateGrid(values []int, cols int) []int {
	n := len(values)
	if n == 0 {
		return []int{}
	}
	rows := n / cols
	out := make([]int, n)
	for i := 0; i < cols; i++ {
		for j := 0; j < rows; j++ {
			out[i*rows+j] = values[(rows-1-j)*cols+i]
		}
	}
	return out
}
```

### C#
```csharp
public static int[] RotateGrid(int[] values, int cols)
{
    int n = values.Length;
    if (n == 0) return new int[0];
    int rows = n / cols;
    var output = new int[n];
    for (int i = 0; i < cols; i++)
        for (int j = 0; j < rows; j++)
            output[i * rows + j] = values[(rows - 1 - j) * cols + i];
    return output;
}
```

### Ruby
```ruby
def rotate_grid(values, cols)
  n = values.length
  return [] if n.zero?
  rows = n / cols
  out = Array.new(n, 0)
  cols.times do |i|
    rows.times do |j|
      out[i * rows + j] = values[(rows - 1 - j) * cols + i]
    end
  end
  out
end
```
