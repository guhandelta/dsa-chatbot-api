"""Free hint tiers, priced operations and earn-back rewards."""
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace

from sqlalchemy import func, select

from app.core.config import settings
from app.db.models import LearningEvent, RewardGrant, Transaction
from app.models.schemas import AnalysisResult
from app.services import entitlements, rewards
from app.services.mentor import hint_cost, pricing
from app.services.operations import perform
from app.services.rate_limit import count_recent


async def register(client, db, email='pricing@example.com', languages=('python', 'javascript')):
    body = (await client.post('/auth/register', json={'email': email, 'password': 'password123'})).json()
    for language in languages:
        await entitlements.grant(db, body['user']['id'], language, days=42)
    await db.commit()
    return {'Authorization': 'Bearer ' + body['access_token']}, body['user']['id']


def stub_mentor(monkeypatch):
    class HintModel:
        async def ainvoke(self, messages):
            return SimpleNamespace(content='What does each quantity represent?')
    monkeypatch.setattr('app.services.mentor.get_llm', lambda _: HintModel())
    monkeypatch.setattr('app.services.knowledge_base.get_vectorstore',
                        lambda: SimpleNamespace(similarity_search=lambda *a, **kw: []))


def test_hint_cost_and_pricing_follow_free_tier_setting(monkeypatch):
    assert [hint_cost(t) for t in (1, 2, 3, 4)] == [0, 0, settings.mentor_cost, settings.mentor_cost]
    assert pricing(9) == {'tier': 4, 'tier_label': 'Name the shape', 'cost': settings.mentor_cost,
                          'free_tiers': 2, 'max_tier': 4}
    assert pricing(0)['tier'] == 1 and pricing(0)['cost'] == 0
    monkeypatch.setattr(settings, 'free_hint_tiers', 0)
    assert hint_cost(1) == settings.mentor_cost


async def test_next_hint_endpoint_reports_tier_and_price(client, db, monkeypatch):
    stub_mentor(monkeypatch)
    headers, _ = await register(client, db)
    url = '/mentor/next-hint'
    params = {'problem_id': 'two-sum', 'language': 'python'}
    assert (await client.get(url, headers=headers, params=params)).json()['cost'] == 0
    for _ in range(2):
        r = await client.post('/mentor/ask', headers=headers, json={**params, 'reasoning': 'a map'})
        assert r.status_code == 200 and r.json()['peppercorns_charged'] == 0
    nxt = (await client.get(url, headers=headers, params=params)).json()
    assert nxt['tier'] == 3 and nxt['cost'] == settings.mentor_cost
    missing = await client.get(url, headers=headers, params={'problem_id': 'no-such-item', 'language': 'python'})
    assert missing.status_code == 404


async def test_free_hints_still_count_against_hourly_limit(client, db, monkeypatch):
    stub_mentor(monkeypatch)
    headers, uid = await register(client, db)
    monkeypatch.setattr(settings, 'hints_per_hour', 1)
    body = {'problem_id': 'two-sum', 'language': 'python', 'reasoning': 'a map'}
    assert (await client.post('/mentor/ask', headers=headers, json=body)).status_code == 200
    assert await count_recent(db, uid, 'hint') == 1
    limited = await client.post('/mentor/ask', headers=headers, json=body)
    assert limited.status_code == 429 and 'mentor questions' in limited.json()['detail']
    free_rows = await db.scalar(select(func.count()).select_from(Transaction).where(
        Transaction.user_id == uid, Transaction.reason == 'free:mentor', Transaction.amount == 0))
    assert free_rows == 1


async def test_failed_free_operation_returns_its_free_use(client, db):
    _, uid = await register(client, db, 'free-refund@example.com')

    async def price(_):
        return 0

    async def work(balance):
        assert balance is None
        raise RuntimeError('provider failed')

    try:
        await perform(db, uid, 'study', 'k1', {'m': 1}, price, 'study', work)
    except Exception as exc:
        assert getattr(exc, 'status_code', None) == 502
    reasons = (await db.scalars(select(Transaction.reason).where(Transaction.user_id == uid,
                                                                 Transaction.amount == 0))).all()
    assert sorted(reasons) == ['free:study', 'refund:free:study']


async def test_priced_operation_charges_when_price_is_positive(client, db):
    _, uid = await register(client, db, 'paid@example.com')

    async def price(_):
        return 2

    async def work(balance):
        return {'balance': balance}

    assert await perform(db, uid, 'study', 'k2', {'m': 2}, price, 'study', work) == {
        'balance': settings.signup_bonus - 2}


async def test_practice_hints_are_free_then_charged(client, db, monkeypatch):
    stub_mentor(monkeypatch)
    headers, _ = await register(client, db, 'practice-hints@example.com')
    started = await client.post('/practice/sessions', headers={**headers, 'Idempotency-Key': 's'},
                                json={'problem_id': 'javascript-path-01-values', 'language': 'javascript'})
    assert started.status_code == 200, started.text
    path = f"/practice/sessions/{started.json()['session_id']}/actions"
    seen = []
    for n in range(3):
        r = await client.post(path, headers={**headers, 'Idempotency-Key': f'h{n}'},
                              json={'action': 'hint', 'reasoning': 'I add price and quantity'})
        assert r.status_code == 200, r.text
        seen.append((r.json()['hint_tier'], r.json()['peppercorns_charged'],
                     r.json()['peppercorns_remaining'], r.json()['next_hint_cost']))
    cost = settings.mentor_cost
    bonus = settings.signup_bonus
    assert seen == [(1, 0, bonus, 0), (2, 0, bonus, cost), (3, cost, bonus - cost, cost)]


async def test_grant_once_is_idempotent_and_skips_disabled_rewards(client, db):
    _, uid = await register(client, db, 'grants@example.com')
    first = await rewards.grant_once(db, uid, 'stage:python:1', 10, 'earn:stage')
    assert first['amount'] == 10 and first['balance'] == settings.signup_bonus + 10
    assert await rewards.grant_once(db, uid, 'stage:python:1', 10, 'earn:stage') is None
    assert await rewards.grant_once(db, uid, 'disabled', 0, 'earn:stage') is None


async def test_grant_once_loses_a_concurrent_race_without_paying(client, db, monkeypatch):
    _, uid = await register(client, db, 'race@example.com')
    db.add(RewardGrant(user_id=uid, key='race', amount=3))
    await db.commit()
    real_scalar = db.scalar
    calls = []

    async def stale_lookup(statement):
        if not calls:
            calls.append(1)
            return None  # simulates a check made before the other request committed
        return await real_scalar(statement)

    monkeypatch.setattr(db, 'scalar', stale_lookup)
    assert await rewards.grant_once(db, uid, 'race', 3, 'earn:independent_solve') is None
    monkeypatch.setattr(db, 'scalar', real_scalar)
    credits = await db.scalar(select(func.count()).select_from(Transaction).where(
        Transaction.user_id == uid, Transaction.reason == 'earn:independent_solve'))
    assert credits == 0


async def test_independent_solve_requires_no_paid_tier_hint(client, db):
    _, uid = await register(client, db, 'solo@example.com')
    db.add(LearningEvent(user_id=uid, problem_id='two-sum', kind='hint', language='python', hint_tier=2))
    await db.flush()
    assert (await rewards.independent_solve(db, uid, 'two-sum', 'python'))['amount'] == settings.reward_independent_solve
    db.add(LearningEvent(user_id=uid, problem_id='coin-change', kind='hint', language='python', hint_tier=3))
    await db.flush()
    assert await rewards.independent_solve(db, uid, 'coin-change', 'python') is None


async def test_streak_pays_on_each_full_run(client, db):
    _, uid = await register(client, db, 'streak@example.com')
    today = date(2026, 10, 18)
    for back in range(settings.reward_streak_days):
        when = datetime.combine(today - timedelta(days=back), datetime.min.time()) + timedelta(hours=12)
        db.add(LearningEvent(user_id=uid, problem_id='two-sum', kind='attempt', language='python',
                             created_at=when if back % 2 else when.replace(tzinfo=timezone.utc)))
    await db.flush()
    assert await rewards.active_run(db, uid, today) == settings.reward_streak_days
    assert await rewards.streak(db, uid, today - timedelta(days=1)) is None  # a six-day run
    assert (await rewards.streak(db, uid, today))['reason'] == 'earn:streak'
    assert await rewards.streak(db, uid, today) is None  # same day pays once
    assert await rewards.streak(db, uid, today + timedelta(days=3)) is None  # no activity


async def test_after_solve_only_pays_independent_reward_on_first_solve(client, db):
    _, uid = await register(client, db, 'after@example.com')
    db.add(LearningEvent(user_id=uid, problem_id='two-sum', kind='solved', language='python'))
    await db.flush()
    assert await rewards.has_solved(db, uid, 'two-sum', 'python')
    assert await rewards.after_solve(db, uid, 'two-sum', 'python', first_solve=False) == []
    earned = await rewards.after_solve(db, uid, 'two-sum', 'python', first_solve=True)
    assert [e['reason'] for e in earned] == ['earn:independent_solve']


async def test_analyze_returns_rewards_and_updated_balance(client, db, monkeypatch):
    headers, _ = await register(client, db, 'analyze-reward@example.com', ('javascript',))
    feedback = AnalysisResult(mistakes=[], enhancements=[], watchouts=[], interview_tips=[], overall_feedback='ok')

    async def review(**kw):
        from app.services.deep_review import gather_evidence
        return feedback, await gather_evidence(kw['problem_id'], kw['user_code'], kw['language'])

    monkeypatch.setattr('app.routers.analyze.deep_review', review)
    body = {'problem_id': 'javascript-path-01-values', 'language': 'javascript',
            'user_code': 'function totalCost(price,quantity){return price*quantity;}'}
    r = await client.post('/analyze/', headers=headers, json=body)
    assert r.status_code == 200, r.text
    assert [x['reason'] for x in r.json()['rewards']] == ['earn:independent_solve']
    expected = settings.signup_bonus - settings.analyze_cost + settings.reward_independent_solve
    assert r.json()['peppercorns_remaining'] == expected
    again = await client.post('/analyze/', headers={**headers, 'Idempotency-Key': 'second'}, json=body)
    assert again.json()['rewards'] == []
