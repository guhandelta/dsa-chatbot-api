from types import SimpleNamespace

from app.services import code_runner


def test_scala_cli_is_not_advertised_as_legacy_class_runner(monkeypatch):
    code_runner._scala_runner_supports_classpath.cache_clear()
    monkeypatch.setattr(code_runner.subprocess, 'run',
                        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout='Scala code runner version: 1.18.0', stderr=''))
    assert code_runner._scala_runner_supports_classpath() is False
    code_runner._scala_runner_supports_classpath.cache_clear()
    monkeypatch.setattr(code_runner.subprocess, 'run',
                        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout='', stderr='Scala code runner version: 1.18.0'))
    assert code_runner._scala_runner_supports_classpath() is False
    code_runner._scala_runner_supports_classpath.cache_clear()
    monkeypatch.setattr(code_runner.subprocess, 'run',
                        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout='', stderr='Scala code runner version 2.13'))
    assert code_runner._scala_runner_supports_classpath() is True
    code_runner._scala_runner_supports_classpath.cache_clear()
