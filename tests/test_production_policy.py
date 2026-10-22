"""Production startup refuses unsafe configuration; development is unaffected."""
import pytest
from app.core.config import Settings

GOOD = dict(openai_api_key='k', app_env='production', exec_backend='docker', jwt_secret='x' * 40,
            cors_origins='https://app.example-school.org', auto_create_tables=False, admin_emails='teacher@school.org',
            database_url='postgresql+asyncpg://u:p@db/app')


def make(**over):
    return Settings(_env_file=None, **{**GOOD, **over})


def test_a_safe_configuration_passes():
    assert make().production_problems() == []
    make().validate_production_policy()


@pytest.mark.parametrize('over,fragment', [
    ({'jwt_secret': 'dev-secret-change-me'}, 'JWT_SECRET'),
    ({'jwt_secret': 'short'}, 'JWT_SECRET'),
    ({'cors_origins': 'http://localhost:5173,http://127.0.0.1:3000'}, 'local origins'),
    ({'cors_origins': '*'}, 'must not contain *'),
    ({'auto_create_tables': True}, 'AUTO_CREATE_TABLES'),
    ({'admin_emails': 'you@example.com'}, 'placeholder'),
    ({'database_url': 'sqlite+aiosqlite:///./x.db'}, 'SQLite'),
    ({'exec_backend': 'subprocess'}, 'EXEC_BACKEND'),
])
def test_each_unsafe_setting_is_refused_in_production(over, fragment):
    settings = make(**over)
    assert any(fragment in p for p in settings.production_problems())
    with pytest.raises(RuntimeError, match='Unsafe production configuration'):
        settings.validate_production_policy()


def test_development_is_not_blocked_by_the_same_settings():
    settings = make(app_env='development', jwt_secret='dev-secret-change-me', database_url='sqlite+aiosqlite:///./x.db')
    assert settings.production_problems()
    settings.validate_production_policy()


async def test_startup_refuses_before_touching_the_database(monkeypatch):
    import app.main as main
    from app.core.config import settings
    monkeypatch.setattr(settings, 'app_env', 'production')
    monkeypatch.setattr(settings, 'exec_backend', 'docker')
    monkeypatch.setattr(settings, 'jwt_secret', 'dev-secret-change-me')
    monkeypatch.setattr(main, 'command_check', None, raising=False)
    monkeypatch.setattr('app.services.container_executor.command', lambda *a, **k: ['true'])
    async def forbidden_db():
        pytest.fail('database startup preceded the production policy check')
    monkeypatch.setattr(main, 'init_db', forbidden_db)
    with pytest.raises(RuntimeError, match='Unsafe production configuration'):
        async with main.lifespan(main.app):
            pytest.fail('unsafe application started')
