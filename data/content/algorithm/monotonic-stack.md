---
track: algorithm
difficulty: Medium
algorithms: monotonic-stack
category: Data Structure
source: authored
io_mode: function
---
# Monotonic stack and monotonic deque — Medium — Data Structure

A monotonic stack keeps elements in sorted order by popping everything that would break the order before each push. Every index is pushed and popped once, so a full pass is O(n). It answers next greater or smaller element, daily temperatures, and largest rectangle in a histogram. A monotonic deque applies the same rule with removal from the front when indices leave the window, giving sliding-window maximum in O(n).

#### Next greater element and sliding-window maximum — Python

```python
from collections import deque

def next_greater(nums):
    res, st = [-1] * len(nums), []        # st holds indices with decreasing values
    for i, x in enumerate(nums):
        while st and nums[st[-1]] < x:
            res[st.pop()] = x
        st.append(i)
    return res

def window_max(nums, k):
    dq, out = deque(), []                  # dq holds indices with decreasing values
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out
```
