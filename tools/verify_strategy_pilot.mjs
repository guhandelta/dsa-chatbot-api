// Authoring check for docs/curriculum/STRATEGY_JAVASCRIPT_PILOT.md.
// This is not wired into learner execution or mastery.
import assert from 'node:assert/strict'

function reference(event, formatter) {
  const result = formatter(event)
  if (typeof result !== 'string') throw new TypeError('formatter must return a string')
  return result
}

function hardCoded(event) {
  return `Alert: ${event.message}`
}

function behaviorPasses(candidate) {
  const event = { message: 'Ready', code: 7 }
  let calls = 0
  const text = candidate(event, actual => {
    calls += 1
    assert.equal(actual, event)
    return `Alert: ${actual.message}`
  })
  assert.equal(text, 'Alert: Ready')
  assert.equal(calls, 1)
  assert.deepEqual(event, { message: 'Ready', code: 7 })
  assert.equal(candidate(event, actual => JSON.stringify(actual)), '{"message":"Ready","code":7}')
  assert.throws(() => candidate(event, () => 7), TypeError)
}

behaviorPasses(reference)
assert.throws(() => behaviorPasses(hardCoded))
console.log('Strategy pilot: reference passed; hard-coded formatting rejected')
