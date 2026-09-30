---
track: algorithm
difficulty: Easy
algorithms: dynamic-array
category: Data Structure
source: authored
io_mode: function
---
# Array and dynamic array — Easy — Data Structure

An array stores elements of one type contiguously, so index access is O(1) and iteration is cache-friendly. A dynamic array keeps spare capacity; when full it allocates 1.5–2× more and copies, which makes append O(1) amortised. Inserting or deleting in the middle shifts every later element, costing O(n). Choose it by default for ordered collections accessed by index. Common patterns: two pointers, sliding window, prefix sums, and binary search on sorted arrays.

#### Dynamic array — C

```c
#include <stdlib.h>

typedef struct { int *data; size_t len, cap; } IntVec;

int vec_push(IntVec *v, int x) {
    if (v->len == v->cap) {
        size_t ncap = v->cap ? v->cap * 2 : 8;
        int *p = realloc(v->data, ncap * sizeof *p);
        if (!p) return -1;            /* old buffer is still valid on failure */
        v->data = p; v->cap = ncap;
    }
    v->data[v->len++] = x;
    return 0;
}

void vec_free(IntVec *v) { free(v->data); v->data = NULL; v->len = v->cap = 0; }
```
