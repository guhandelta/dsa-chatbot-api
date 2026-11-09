"""Isolated authoring check for the draft JavaScript Strategy exercise.

Runs student code through the configured execution backend. Its result is
behavior evidence only; it never writes progress, rewards, or mastery.
"""

import json
import tempfile
from pathlib import Path

from app.core.config import settings
from app.services.code_runner import _run

_CHECK = r'''
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('candidate.js', 'utf8');
const checks = [];
try {
  const sandbox = vm.createContext({console: {log() {}, error() {}}});
  vm.runInContext(source, sandbox, {timeout: 1000});
  const candidate = sandbox.prepareNotification;
  if (typeof candidate !== 'function') throw new Error('prepareNotification is missing');
  const event = Object.freeze({message: 'Ready', code: 7});
  let calls = 0;
  let sameObject = true;
  const text = candidate(event, actual => {
    calls += 1;
    sameObject &&= actual === event;
    return `Alert: ${actual.message}`;
  });
  checks.push({name: 'text-and-identity', passed: text === 'Alert: Ready' && calls === 1 && sameObject});
  calls = 0;
  const alternate = candidate(event, actual => {
    calls += 1;
    sameObject &&= actual === event;
    return JSON.stringify(actual);
  });
  checks.push({name: 'alternate-formatter', passed: alternate === '{"message":"Ready","code":7}' && calls === 1 && sameObject});
  let threwTypeError = false;
  try { candidate(event, () => 7); }
  catch (error) { threwTypeError = error && error.name === 'TypeError'; }
  checks.push({name: 'non-string-rejected', passed: threwTypeError});
  checks.push({name: 'event-unchanged', passed: event.message === 'Ready' && event.code === 7});
} catch (error) {
  checks.push({name: 'candidate-error', passed: false, detail: String(error && error.message || error).slice(0, 200)});
}
process.stdout.write(JSON.stringify({checks}));
'''


def check(source: str) -> dict:
    """Return bounded behavior results, failing closed on execution errors."""
    if not isinstance(source, str) or not source.strip() or len(source) > 20_000:
        raise ValueError("JavaScript source must contain 1 to 20000 characters")
    with tempfile.TemporaryDirectory(prefix="strategy-check-") as directory:
        scratch = Path(directory)
        (scratch / "candidate.js").write_text(source, encoding="utf-8")
        (scratch / "check.cjs").write_text(_CHECK, encoding="utf-8")
        try:
            status, output, error = _run(
                ["node", f"--max-old-space-size={settings.exec_memory_mb}", "check.cjs"],
                scratch, apply_address_space=False,
            )
        except RuntimeError:
            return {"status": "unverified", "checks": [], "detail": "Execution infrastructure unavailable"}
    if status != 0:
        return {"status": "unverified", "checks": [], "detail": (error or "Execution failed")[:200]}
    try:
        result = json.loads(output)
        checks = result["checks"]
        if (not isinstance(checks, list) or not checks or
                any(not isinstance(item, dict) or not isinstance(item.get("name"), str)
                    or not isinstance(item.get("passed"), bool) for item in checks)):
            raise ValueError("invalid check results")
    except (ValueError, KeyError, TypeError):
        return {"status": "unverified", "checks": [], "detail": "Invalid check output"}
    return {"status": "passed" if all(item["passed"] for item in checks) else "failed",
            "checks": checks, "detail": "Behavior only; design reasoning and transfer remain unassessed."}
