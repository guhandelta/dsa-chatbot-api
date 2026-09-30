---
track: language
difficulty: Easy
language: c
category: Library & APIs
source: authored
io_mode: function
---
# C data structures and algorithm APIs — Easy — Library & APIs

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Fixed array | `int a[N]`, `malloc(n * sizeof *a)` | O(1) index; size fixed at allocation |
| Dynamic array | Build with `realloc` | Double capacity on growth for O(1) amortised append |
| Stack | Build | Array plus top index |
| Queue / deque | Build | Ring buffer with head, tail and size |
| Linked list | Build | `struct Node { int val; struct Node *next; }` |
| Hash map | Build, or POSIX `hsearch` (one global table) | Custom table with FNV-1a or similar hash |
| Sorted map | Build, or POSIX `tsearch` / `tfind` / `tdelete` | Binary tree, balanced in glibc |
| Priority queue | Build | Array-backed binary heap |
| Bit set | Build | Array of `uint64_t` words |
| Third-party | `stb_ds.h`, `klib`, `uthash` | Header-only generic containers |

| Algorithm | API |
| --- | --- |
| Sort | `qsort(base, n, size, cmp)`; unstable; comparator returns `<0`, `0`, `>0` |
| Binary search | `bsearch(&key, base, n, size, cmp)`; returns a pointer to any match or `NULL`, no insertion point |
| Memory | `memcpy`, `memmove` (overlapping), `memset`, `memcmp` |
| Bits | `__builtin_popcount`, `__builtin_ctz`, `__builtin_clz` (GCC/Clang, undefined for 0); C23 `<stdbit.h>` `stdc_count_ones` |
