"""Check curated expected answers with independent small-input oracles.

These do not execute or copy the published reference implementations. Exhaustive
search and basic mathematical definitions catch shared mistakes in fixtures and
reference code, which merely running those two against each other cannot catch.
"""
from collections import deque
from functools import lru_cache
from itertools import combinations
from math import comb, prod

import pytest

from app.services.content_catalog import list_content, load_test_cases


def coin_change(coins, amount):
    distance = {0:0}
    queue = deque([0])
    while queue:
        value = queue.popleft()
        if value == amount:
            return distance[value]
        for coin in coins:
            nxt = value + coin
            if nxt <= amount and nxt not in distance:
                distance[nxt] = distance[value] + 1
                queue.append(nxt)
    return -1


def count_sequences(nums, target):
    @lru_cache(None)
    def count(n):
        return 1 if n == 0 else sum(count(n-x) for x in nums if x <= n)
    return count(target)


def subsequences(text):
    return {''.join(text[i] for i in indices) for n in range(len(text)+1) for indices in combinations(range(len(text)),n)}


def word_break(text, words):
    @lru_cache(None)
    def possible(start):
        return start == len(text) or any(text.startswith(word,start) and possible(start+len(word)) for word in words if word)
    return possible(0)


def subarrays(values):
    return [values[i:j] for i in range(len(values)) for j in range(i+1,len(values)+1)]


def avl_height(values):
    """Second, recursive AVL written separately from the published references."""
    class N:
        def __init__(self, key): self.key, self.left, self.right, self.h = key, None, None, 1
    def h(n): return n.h if n else 0
    def fix(n): n.h = 1 + max(h(n.left), h(n.right))
    def rot_right(y):
        x = y.left; y.left = x.right; x.right = y; fix(y); fix(x); return x
    def rot_left(x):
        y = x.right; x.right = y.left; y.left = x; fix(x); fix(y); return y
    def insert(n, key):
        if n is None: return N(key)
        if key < n.key: n.left = insert(n.left, key)
        elif key > n.key: n.right = insert(n.right, key)
        else: return n
        fix(n)
        bal = h(n.left) - h(n.right)
        if bal > 1 and key < n.left.key: return rot_right(n)
        if bal < -1 and key > n.right.key: return rot_left(n)
        if bal > 1: n.left = rot_left(n.left); return rot_right(n)
        if bal < -1: n.right = rot_right(n.right); return rot_left(n)
        return n
    root = None
    for v in values: root = insert(root, v)
    return h(root)


def rb_black_height(values):
    """Second CLRS red-black insertion, written separately from the published reference.
    Black height: black nodes on the leftmost root-to-NIL path, root counted, NIL not counted."""
    class N:
        def __init__(self, k):
            self.k, self.red, self.l, self.r, self.p = k, True, None, None, None
    class T:
        root = None
    t = T()
    def rot_left(x):
        y = x.r; x.r = y.l
        if y.l: y.l.p = x
        y.p = x.p
        if x.p is None: t.root = y
        elif x is x.p.l: x.p.l = y
        else: x.p.r = y
        y.l = x; x.p = y
    def rot_right(x):
        y = x.l; x.l = y.r
        if y.r: y.r.p = x
        y.p = x.p
        if x.p is None: t.root = y
        elif x is x.p.r: x.p.r = y
        else: x.p.l = y
        y.r = x; x.p = y
    for k in values:
        z, parent, cur = N(k), None, t.root
        while cur is not None:
            parent, cur = cur, (cur.l if k < cur.k else cur.r)
        z.p = parent
        if parent is None: t.root = z
        elif k < parent.k: parent.l = z
        else: parent.r = z
        x = z
        while x.p is not None and x.p.red:
            g = x.p.p
            if x.p is g.l:
                u = g.r
                if u is not None and u.red:
                    x.p.red = False; u.red = False; g.red = True; x = g
                else:
                    if x is x.p.r:
                        x = x.p; rot_left(x)
                    x.p.red = False; g.red = True; rot_right(g)
            else:
                u = g.l
                if u is not None and u.red:
                    x.p.red = False; u.red = False; g.red = True; x = g
                else:
                    if x is x.p.l:
                        x = x.p; rot_right(x)
                    x.p.red = False; g.red = True; rot_left(g)
        t.root.red = False
    count, n = 0, t.root
    while n is not None:
        if not n.red: count += 1
        n = n.l
    return count


def btree_height(values, order):
    """Second B-tree insertion (reactive split at `order` keys), written separately."""
    if not values: return 0
    class Node:
        def __init__(self, leaf): self.keys, self.kids, self.leaf = [], [], leaf
    root = Node(True)
    def insert_into(node, key):
        if node.leaf:
            node.keys.append(key); node.keys.sort()
        else:
            i = sum(1 for k in node.keys if key > k)
            split = insert_into(node.kids[i], key)
            if split is not None:
                mid_key, right = split
                node.keys.insert(i, mid_key); node.kids.insert(i + 1, right)
        return split_node(node) if len(node.keys) >= order else None
    def split_node(node):
        mid = len(node.keys) // 2
        mid_key = node.keys[mid]
        right = Node(node.leaf)
        right.keys = node.keys[mid + 1:]
        if not node.leaf:
            right.kids = node.kids[mid + 1:]
            node.kids = node.kids[:mid + 1]
        node.keys = node.keys[:mid]
        return mid_key, right
    for key in values:
        split = insert_into(root, key)
        if split is not None:
            new_root = Node(False)
            new_root.keys = [split[0]]; new_root.kids = [root, split[1]]
            root = new_root
    levels, node = 1, root
    while not node.leaf:
        node = node.kids[0]; levels += 1
    return levels


def rotate_grid(values, cols):
    if not values: return []
    rows = len(values) // cols
    grid = [values[r * cols:(r + 1) * cols] for r in range(rows)]
    return [x for row in zip(*grid[::-1]) for x in row]


def dll_remove_all(values, target):
    return [v for v in values if v != target]


def o_has_repeat(values):
    return any(values.count(v) >= 2 for v in values)


def o_are_rearrangements(first, second):
    return sorted(first) == sorted(second)


def o_find_pair_indices(values, target):
    n = len(values)
    for i in range(n):
        for j in range(i + 1, n):
            if values[i] + values[j] == target:
                return [i, j]
    return []


def o_count_word_families(words):
    groups = []
    for w in words:
        key = sorted(w)
        if key not in groups:
            groups.append(key)
    return len(groups)


def o_top_frequent(values, k):
    distinct = set(values)
    freq = {v: values.count(v) for v in distinct}
    ranked = sorted(distinct, key=lambda v: (-freq[v], v))
    return ranked[:k]


def o_product_except_index(values):
    out = []
    for i in range(len(values)):
        p = 1
        for j, v in enumerate(values):
            if j != i:
                p *= v
        out.append(p)
    return out


def o_grid_is_consistent(cells):
    units = [[cells[r * 9 + c] for c in range(9)] for r in range(9)]
    units += [[cells[r * 9 + c] for r in range(9)] for c in range(9)]
    units += [[cells[(br * 3 + i) * 9 + bc * 3 + j] for i in range(3) for j in range(3)] for br in range(3) for bc in range(3)]
    return all(len(set(d for d in u if d)) == len([d for d in u if d]) for u in units)


def o_encoded_length(words):
    return sum(len(f"{len(w)}#{w}") for w in words)


def o_longest_run(values):
    s = set(values)
    best = 0
    for x in s:
        if x - 1 in s:
            continue
        length = 1
        while x + length in s:
            length += 1
        best = max(best, length)
    return best


ORACLES = {
    'best-time-to-buy-and-sell-stock': lambda a:max([0]+[a[j]-a[i] for i in range(len(a)) for j in range(i+1,len(a))]),
    'binary-search': lambda a,t:a.index(t) if t in a else -1,
    'climbing-stairs': lambda n:sum(comb(n-k,k) for k in range(n//2+1)),
    'contains-duplicate': lambda a:len(set(a)) != len(a),
    'counting-bits': lambda n:[bin(i).count('1') for i in range(n+1)],
    'missing-number': lambda a:next(i for i in range(len(a)+1) if i not in a),
    'number-of-1-bits': lambda n:bin(n & 0xffffffff).count('1'),
    'reverse-bits': lambda n:int(f'{n & 0xffffffff:032b}'[::-1],2),
    'reverse-linked-list': lambda a:a[::-1],
    '3sum': lambda a:sorted({tuple(sorted(v)) for v in combinations(a,3) if sum(v)==0}),
    'coin-change':coin_change,
    'combination-sum-iv':count_sequences,
    'container-with-most-water':lambda a:max([0]+[(j-i)*min(a[i],a[j]) for i,j in combinations(range(len(a)),2)]),
    'find-minimum-in-rotated-sorted-array': min,
    'longest-common-subsequence':lambda a,b:max(map(len,subsequences(a)&subsequences(b))),
    'longest-increasing-subsequence':lambda a:max(n for n in range(len(a)+1) for v in combinations(a,n) if all(x<y for x,y in zip(v,v[1:]))),
    'maximum-product-subarray':lambda a:max(map(prod,subarrays(a))),
    'maximum-subarray':lambda a:max(map(sum,subarrays(a))),
    'product-of-array-except-self':lambda a:[prod(a[:i]+a[i+1:]) for i in range(len(a))],
    'search-in-rotated-sorted-array':lambda a,t:a.index(t) if t in a else -1,
    'sum-of-two-integers':lambda a,b:((a+b+2**31)%2**32)-2**31,
    'word-break':word_break,
    'avl-tree': avl_height,
    'red-black-tree': rb_black_height,
    'b-tree': btree_height,
    'matrix-and-grid': rotate_grid,
    'doubly-linked-list': dll_remove_all,
    'duplicate-presence': o_has_repeat,
    'rearranged-letters': o_are_rearrangements,
    'complement-indices': o_find_pair_indices,
    'word-families': o_count_word_families,
    'most-frequent-values': o_top_frequent,
    'all-but-one-product': o_product_except_index,
    'grid-consistency': o_grid_is_consistent,
    'encoded-length': o_encoded_length,
    'longest-run': o_longest_run,
}


@pytest.mark.parametrize('problem_id', sorted([*ORACLES,'two-sum']))
def test_every_fixture_matches_independent_oracle(problem_id):
    cases, expected, _, _ = load_test_cases(problem_id)
    assert len(cases) >= 6
    assert len({repr(value) for value in expected}) > 1, 'A constant-answer mutant would pass this suite'
    for args, answer in zip(cases,expected):
        if problem_id == 'two-sum':
            values,target = args
            pairs = [(i,j) for i,j in combinations(range(len(values)),2) if values[i]+values[j]==target]
            assert (tuple(sorted(answer)) in pairs) if pairs else answer == []
        elif problem_id == '3sum':
            assert sorted(tuple(sorted(v)) for v in answer) == ORACLES[problem_id](*args)
        else:
            result = ORACLES[problem_id](*args)
            assert type(result) is type(answer) and result == answer, (problem_id,args,answer,result)


def test_oracles_cover_entire_current_dsa_catalog():
    assert {item.id for item in list_content() if item.track=='dsa'} == {*ORACLES,'two-sum'}
