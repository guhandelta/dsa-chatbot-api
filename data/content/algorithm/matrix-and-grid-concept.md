---
track: algorithm
difficulty: Medium
algorithms: matrix-and-grid-concept
category: Data Structure
source: authored
io_mode: function
---
# Matrices and grids — Medium — Data Structure

A matrix or grid is a rectangular table of values with a fixed number of rows and columns. Each element is addressed by its row and column, and the way that pair maps to memory decides how fast reads, row scans and column scans are.

| Layout | Element (r, c) | Typical use |
| --- | --- | --- |
| Array of rows | `grid[r][c]` | Everyday code; each row can be its own allocation |
| Flat row-major | `flat[r * cols + c]` | One contiguous block; fast, easy to pass as one array |
| Fortran / column-major | `flat[c * rows + r]` | Fortran and column-oriented numeric code |

## What the structure guarantees
- Every row has the same length, so the shape is `rows × cols` and the index formula is exact.
- In flat row-major storage, each row is contiguous, so row scans are cache-friendly. A column scan jumps by `cols` on every step.
- Any element can be reached in O(1) once `rows` and `cols` are known. The grid itself stores no index structure.

## Operations
| Operation | Flat row-major cost |
| --- | --- |
| Read or write (r, c) | O(1) |
| Scan one row | O(cols), contiguous |
| Scan one column | O(rows), stride `cols` |
| Transpose (rows × cols → cols × rows) | O(rows · cols) time and space into a new buffer |
| Rotate 90° clockwise | O(rows · cols) time and space into a new buffer |
| Build 2D prefix sums | O(rows · cols) |
| Sum of any rectangle after prefix sums | O(1) |

Rotating a square grid can be done in place by swapping layers of four cells. A non-square grid changes its shape, so the simple in-place swap no longer works; use a separate output buffer, or a cycle-following permutation.

## Common mistakes
- Swapping `rows` and `cols` in the index formula. Non-square inputs expose this immediately; square inputs hide it.
- Writing `r * rows + c` for row-major storage. The stride is the number of columns.
- Dividing `len(values)` by `cols` without checking for an empty input or `cols = 0`.
- Using the square-matrix swap loop on a non-square grid.
- Trusting ragged input. If rows have different lengths, `grid[r][c]` is not a rectangle; check the lengths before indexing.
- Forgetting that `[[0] * cols] * rows` in Python makes every row the same list. Build each row separately.

## Languages

### Python
Python has no built-in matrix type. A list of lists is the usual form, and `[[0] * cols for _ in range(rows)]` allocates a grid with separate rows. `zip(*grid)` transposes it. The numpy package is third-party and not part of the standard library.

```python
rows, cols = 2, 3
grid = [[1, 2, 3], [4, 5, 6]]              # list of lists: grid[r][c]
flat = [v for row in grid for v in row]    # row-major: flat[r * cols + c]
print(grid[1][2], flat[1 * cols + 2])      # 6 6
print(list(zip(*grid)))                    # transpose: [(1, 4), (2, 5), (3, 6)]
```

### JavaScript
JavaScript has no built-in matrix type. Arrays of arrays are the common choice. For a contiguous flat grid, use a typed array such as `Int32Array`; it stores fixed-width 32-bit integers and wraps values outside that range, so use `BigInt64Array` when 64-bit values are needed.

```javascript
const rows = 2, cols = 3;
const grid = [[1, 2, 3], [4, 5, 6]];        // array of arrays
const flat = new Int32Array(rows * cols);    // contiguous flat buffer
grid.forEach((row, r) => row.forEach((v, c) => { flat[r * cols + c] = v; }));
console.log(grid[1][2], flat[1 * cols + 2]); // 6 6
```

### TypeScript
TypeScript has no matrix type either. `number[][]` is the usual annotation, but the compiler does not check that the rows have equal length. The same typed-array approach as JavaScript gives a flat buffer, and types are erased at run time.

```typescript
const rows: number = 2, cols: number = 3;
const grid: number[][] = [[1, 2, 3], [4, 5, 6]];
const flat = new Int32Array(rows * cols);
grid.forEach((row, r) => row.forEach((v, c) => { flat[r * cols + c] = v; }));
console.log(grid[1][2], flat[1 * cols + 2]); // 6 6
```

### Java
`java.util` has no matrix type. `int[][]` is an array of `int[]` rows, and `new int[rows][cols]` allocates a rectangular one. A flat `int[rows * cols]` gives the contiguous layout and is what most performance-sensitive code uses.

```java
public class Main {
    public static void main(String[] args) {
        int rows = 2, cols = 3;
        int[][] grid = {{1, 2, 3}, {4, 5, 6}};
        int[] flat = new int[rows * cols];
        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++) flat[r * cols + c] = grid[r][c];
        System.out.println(grid[1][2] + " " + flat[1 * cols + 2]); // 6 6
    }
}
```

### C
C has no matrix type. A fixed-size `int grid[ROWS][COLS]` is one contiguous block in row-major order, so `&grid[0][0]` can be used as a flat pointer. For sizes known only at run time, call `malloc(rows * cols * sizeof(int))` and index the block yourself.

```c
#include <stdio.h>
int main(void) {
    enum { ROWS = 2, COLS = 3 };
    int grid[ROWS][COLS] = {{1, 2, 3}, {4, 5, 6}};
    int *flat = &grid[0][0];
    printf("%d %d\n", grid[1][2], flat[1 * COLS + 2]); /* 6 6 */
    return 0;
}
```

### C++
The standard library has no dynamic matrix type. `std::vector<std::vector<int>>` is the common grid, but each row is a separate allocation. `std::array<std::array<int, 3>, 2>` is a fixed-size grid stored contiguously, and a flat `std::vector<int>` gives the same layout as C.

```cpp
#include <iostream>
#include <vector>
int main() {
    std::vector<std::vector<int>> grid = {{1, 2, 3}, {4, 5, 6}};
    std::vector<int> flat;
    for (const auto& row : grid) flat.insert(flat.end(), row.begin(), row.end());
    std::cout << grid[1][2] << ' ' << flat[1 * 3 + 2] << '\n'; // 6 6
}
```

### Rust
The standard library has no matrix type. `Vec<Vec<T>>` is the dynamic form, and `[[T; C]; R]` is a fixed-size grid stored contiguously. Indexing is bounds-checked, so an out-of-range row or column panics instead of reading memory outside the grid.

```rust
fn main() {
    let cols = 3usize;
    let grid: Vec<Vec<i32>> = vec![vec![1, 2, 3], vec![4, 5, 6]];
    let flat: Vec<i32> = grid.iter().flatten().copied().collect(); // row-major
    println!("{} {}", grid[1][2], flat[1 * cols + 2]); // 6 6
}
```

### Go
Go has no matrix type. `[][]int` is the common form, but each inner slice is separate, so `make([]int, rows*cols)` with manual `r*cols + c` indexing gives a contiguous grid. Fixed-size arrays such as `[2][3]int` are also contiguous.

```go
package main

import "fmt"

func main() {
	rows, cols := 2, 3
	grid := [][]int{{1, 2, 3}, {4, 5, 6}}
	flat := make([]int, rows*cols)
	for r := range grid {
		for c := range grid[r] {
			flat[r*cols+c] = grid[r][c]
		}
	}
	fmt.Println(grid[1][2], flat[1*cols+2]) // 6 6
}
```

### C#
C# has built-in rectangular arrays, `int[,]`, indexed as `grid[r, c]`, with `GetLength(dimension)` for the sizes. Jagged arrays, `int[][]`, are arrays of rows like Java's, and each row can have its own length.

```csharp
using System;
var grid = new int[2, 3] { { 1, 2, 3 }, { 4, 5, 6 } };
var flat = new int[grid.Length];
for (int r = 0; r < grid.GetLength(0); r++)
    for (int c = 0; c < grid.GetLength(1); c++) flat[r * grid.GetLength(1) + c] = grid[r, c];
Console.WriteLine($"{grid[1, 2]} {flat[1 * 3 + 2]}"); // 6 6
```

### Ruby
Ruby's core has no matrix type, so arrays of arrays are the everyday choice. The standard library's `matrix` library provides `Matrix`, which has `transpose` and arithmetic. Allocate rows with a block, `Array.new(rows) { Array.new(cols, 0) }`, so each row is separate.

```ruby
require 'matrix'
grid = [[1, 2, 3], [4, 5, 6]]
flat = grid.flatten
puts "#{grid[1][2]} #{flat[1 * 3 + 2]}"           # 6 6
p Matrix[[1, 2, 3], [4, 5, 6]].transpose         # Matrix[[1, 4], [2, 5], [3, 6]]
```
