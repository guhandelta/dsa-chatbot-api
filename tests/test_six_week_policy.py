"""Product contracts for six-week hints and non-expiring usage credits."""
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.db.models import LearningEvent, User
from app.routers.mentor import _current_tier
from app.services import entitlements
from app.services.peppercorns import debit

NOW = datetime(2026, 10, 14, tzinfo=timezone.utc)


async def hint(db, age, language='java', user='learner', problem='two-sum'):
    db.add(LearningEvent(user_id=user, problem_id=problem, language=language,
                         kind='hint', hint_tier=1, created_at=NOW-timedelta(days=age)))
    await db.commit()


async def test_default_window_is_exactly_six_weeks():
    assert settings.hint_tier_reset_hours == 42*24


async def test_recent_hint_does_not_postpone_fixed_reset(db):
    await hint(db, 42)
    await hint(db, 1)
    assert await _current_tier(db, 'learner', 'two-sum', 'java', now=NOW) == 1
    await hint(db, 0)
    assert await _current_tier(db, 'learner', 'two-sum', 'java', now=NOW) == 2


async def test_before_boundary_still_escalates_and_multiple_cycles_reset(db):
    await hint(db, 41.999)
    await hint(db, 1)
    assert await _current_tier(db, 'learner', 'two-sum', 'java', now=NOW) == 3
    assert await _current_tier(db, 'learner', 'two-sum', 'java', now=NOW+timedelta(days=85)) == 1


async def test_language_histories_are_independent(db):
    for _ in range(3):
        await hint(db, 1)
    assert await _current_tier(db, 'learner', 'two-sum', 'java', now=NOW) == 4
    assert await _current_tier(db, 'learner', 'two-sum', 'javascript', now=NOW) == 1


async def test_expiry_cancellation_and_renewal_preserve_spendable_balance(client, db, monkeypatch):
    r = await client.post('/auth/register', json={'email':'remaining@example.com','password':'password123'})
    uid = r.json()['user']['id']
    headers = {'Authorization':'Bearer '+r.json()['access_token']}
    before = r.json()['user']['peppercorns']
    monkeypatch.setattr(entitlements, '_now', lambda: NOW)
    await entitlements.grant(db, uid, 'java', days=1)
    await db.commit()
    assert await entitlements.revoke(db, uid, 'java')
    await db.commit()
    assert (await entitlements.check(db, uid, 'java'))['entitled']
    monkeypatch.setattr(entitlements, '_now', lambda: NOW+timedelta(days=2))
    assert not (await entitlements.check(db, uid, 'java'))['entitled']
    db.expire_all()
    assert (await db.get(User, uid)).peppercorns == before
    async def reply(**kwargs): return 'A variable binds a name to a value.'
    monkeypatch.setattr('app.routers.chat.run_rag_chat', reply)
    result = await client.post('/chat/', headers=headers, json={'message':'What is a variable?'})
    assert result.status_code == 200, result.text
    after = (await client.get('/auth/me', headers=headers)).json()['peppercorns']
    assert after == before-settings.chat_cost
    await entitlements.grant(db, uid, 'java', days=30)
    await db.commit()
    db.expire_all()
    assert (await db.get(User, uid)).peppercorns == after
    assert (await entitlements.check(db, uid, 'java'))['entitled']
