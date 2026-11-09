import pytest

from app.services import strategy_callback_check as checker


GOOD = """function prepareNotification(event, formatter) {
  const result = formatter(event);
  if (typeof result !== 'string') throw new TypeError('string required');
  return result;
}"""
HARDCODED = "function prepareNotification(event) { return `Alert: ${event.message}`; }"
TWICE = "function prepareNotification(event, formatter) { formatter(event); return formatter(event); }"
COPIES = "function prepareNotification(event, formatter) { return formatter({...event}); }"
NONSTRING = "function prepareNotification(event, formatter) { return formatter(event); }"


@pytest.mark.parametrize("source,expected", [
    (GOOD, "passed"), (HARDCODED, "failed"), (TWICE, "failed"),
    (COPIES, "failed"), (NONSTRING, "failed"),
    ("function prepareNotification() { while (true) {} }", "unverified"),
])
def test_strategy_behavior_check(source, expected):
    result = checker.check(source)
    assert result["status"] == expected, result
    assert "mastery" not in result


def test_strategy_check_rejects_invalid_source():
    for source in ("", " " * 3, "x" * 20_001):
        with pytest.raises(ValueError):
            checker.check(source)


def test_strategy_check_fails_closed_on_infrastructure_and_malformed_output(monkeypatch):
    monkeypatch.setattr(checker, '_run', lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError('hidden')))
    assert checker.check(GOOD)['status'] == 'unverified'
    monkeypatch.setattr(checker, '_run', lambda *args, **kwargs: (0, '{"checks":[]}', ''))
    assert checker.check(GOOD)['status'] == 'unverified'
    monkeypatch.setattr(checker, '_run', lambda *args, **kwargs: (1, '', 'failed'))
    assert checker.check(GOOD)['status'] == 'unverified'
