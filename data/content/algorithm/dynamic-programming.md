---
track: algorithm
difficulty: Hard
algorithms: dynamic-programming
category: Paradigm
source: authored
io_mode: function
---
# Dynamic programming framework — Hard — Paradigm

Dynamic programming applies when a problem has overlapping subproblems and optimal substructure (the best answer is built from best answers to smaller subproblems). Define four things: the state (what `dp[i]` or `dp[i][j]` means), the transition (how a state is computed from smaller ones), the base cases, and the evaluation order. Top-down memoisation is quickest to write; bottom-up tabulation avoids recursion limits and allows keeping only the previous row, cutting space from O(nm) to O(m).

| Pattern | State | Classic problems | Time |
| --- | --- | --- | --- |
| 1D linear | best for prefix i | Climbing stairs, house robber, decode ways, word break | O(n) |
| Maximum subarray | best sum ending at i | Kadane, maximum product subarray | O(n) |
| 0/1 knapsack | best for capacity w using items so far | Subset sum, partition equal subset sum, target sum | O(nW) |
| Unbounded knapsack | best for amount a | Coin change (fewest coins, number of ways) | O(n·amount) |
| Two sequences | answer for prefixes i and j | Longest common subsequence, edit distance, interleaving string | O(nm) |
| Increasing subsequence | smallest tail per length | Longest increasing subsequence, Russian doll envelopes | O(n log n) |
| Grid | best for cell (r, c) | Unique paths, minimum path sum, maximal square | O(RC) |
| Interval | answer for range \[i, j\] | Matrix-chain multiplication, burst balloons, palindrome partitioning | O(n³) |
| Bitmask | best for visited set and last node | Travelling salesman, assignment | O(2ⁿ·n²) |
| Tree | values returned from children | House robber III, tree diameter, binary tree maximum path sum | O(n) |
| State machine | best at day i in state s | Stock buy/sell with cooldown or fees | O(n) |
| Digit | (position, tight, state) | Count numbers ≤ N with a digit property | O(digits × states) |

Memoisation per language: Python `@functools.cache`; JavaScript and TypeScript a `Map` or typed array; Java and C# a `HashMap` / `Dictionary` or an array filled with a sentinel; C a static array initialised to a sentinel; C++ a `std::vector` or `std::unordered_map`; Go a `map` or a slice filled with a sentinel, used by a recursive closure declared as `var dfs func(int) int`; Rust a `Vec<Option<T>>` passed as `&mut`; Ruby a `Hash` (`@memo[key] ||= compute`, which recomputes if the stored value is `nil` or `false`).
