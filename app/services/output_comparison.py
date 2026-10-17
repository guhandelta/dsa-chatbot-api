"""Explicit answer contracts. Ordered arrays/matrices stay ordered by default."""
import json
import math


def exact(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return (not isinstance(a, float) or math.isfinite(a)) and (not isinstance(b, float) or math.isfinite(b)) and a == b
    if type(a) is not type(b):
        return False
    if isinstance(a, list):
        return len(a) == len(b) and all(exact(x, y) for x, y in zip(a, b))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(exact(a[k], b[k]) for k in a)
    return a == b


def compare(a, b, mode='exact'):
    if mode == 'exact':
        return exact(a, b)
    if not isinstance(a, list) or not isinstance(b, list):
        return False
    if mode == 'unordered_nested':
        if not all(isinstance(row, list) for row in a+b):
            return False
        a = [sorted(row, key=_key) for row in a]
        b = [sorted(row, key=_key) for row in b]
    elif mode != 'unordered_flat':
        raise ValueError('Unknown output comparison mode')
    return exact(sorted(a, key=_key), sorted(b, key=_key))


def _key(value):
    return json.dumps(value, sort_keys=True)
