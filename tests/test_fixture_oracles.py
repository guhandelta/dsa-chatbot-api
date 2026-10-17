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
