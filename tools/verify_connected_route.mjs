// Authoring checks for docs/curriculum/CONNECTED_JAVASCRIPT_ROUTE_DRAFT.md.
// This script is not a learner grader and has no mastery side effects.
import assert from 'node:assert/strict'

function applyToScore(score, transform) {
  return transform(score)
}
const addTwo = value => value + 2
assert.equal(applyToScore(5, addTwo), 7)
assert.equal(applyToScore(5, value => value * 3), 15)
assert.throws(() => applyToScore(5, addTwo()), TypeError)

function firstAtLeast(values, target) {
  let lo = 0
  let hi = values.length
  while (lo < hi) {
    const mid = lo + Math.floor((hi - lo) / 2)
    if (values[mid] < target) lo = mid + 1
    else hi = mid
  }
  return lo
}

for (const [values, target, expected] of [
  [[], 3, 0], [[1, 3, 3, 8], 3, 1], [[1, 3, 3, 8], 9, 4],
  [[1, 3, 3, 8], 0, 0], [[1, 3, 3, 8], 4, 3], [[3, 3, 3], 3, 0],
]) assert.equal(firstAtLeast(values, target), expected)

// Compare the reference against a linear oracle on deterministic small arrays.
for (let length = 0; length <= 12; length++) {
  const values = Array.from({length}, (_, index) => Math.floor(index / 2) - 2)
  for (let target = -4; target <= 8; target++) {
    const expected = values.findIndex(value => value >= target)
    assert.equal(firstAtLeast(values, target), expected < 0 ? length : expected)
  }
}

console.log('Connected JavaScript draft examples and binary-search boundaries passed')
