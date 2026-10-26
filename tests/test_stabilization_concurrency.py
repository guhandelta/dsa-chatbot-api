"""Exercise independent database connections, rather than one in-memory connection."""
import asyncio

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.db.database import Base, get_session
from app.main import app


async def test_simultaneous_autosaves_and_monthly_limit(client, tmp_path, monkeypatch):
    engine = create_async_engine('sqlite+aiosqlite:///' + str(tmp_path / 'concurrent.db'))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    old = app.dependency_overrides[get_session]
    async def database():
        async with factory() as session:
            yield session
    app.dependency_overrides[get_session] = database
    try:
        registered = (await client.post('/auth/register', json={'email': 'concurrent@example.com', 'password': 'password123'})).json()
        headers = {'Authorization': 'Bearer ' + registered['access_token']}
        body = {'template': 'html-css', 'revision': None, 'files': [{'name': 'index.html', 'content': '<p>one</p>'}]}
        results = await asyncio.gather(*(client.put('/playground/shared', headers=headers, json=body) for _ in range(2)))
        assert sorted(r.status_code for r in results) == [200, 409]
        body['revision'] = 1
        results = await asyncio.gather(*(client.put('/playground/shared', headers=headers, json=body) for _ in range(2)))
        assert sorted(r.status_code for r in results) == [200, 409]
        # Grant access through the same independent database.
        from app.services.entitlements import grant
        async with factory() as session:
            await grant(session, registered['user']['id'], 'python', days=42)
            await session.commit()
        monkeypatch.setattr(settings, 'extra_practice_sets_per_month', 1)
        results = await asyncio.gather(*(client.post('/strikes/practice', headers=headers,
            json={'language': 'python', 'problem_id': 'python-path-01-values'}) for _ in range(2)))
        assert sorted(r.status_code for r in results) == [200, 429]
        # Two answers to different items must accumulate, not overwrite each other.
        import json
        from app.db.models import ChallengeSet, LearningStrike
        from app.services import quiz, learning_strikes
        mcqs = [q for q in quiz.pool('python', 'python:stage-01') if q['type'] in ('mcq', 'mcq_code')][:2]
        async with factory() as session:
            challenge = ChallengeSet(user_id=registered['user']['id'], language='python',
                node_id='python:stage-01', problem_id='python-path-01-values', kind='strike',
                items_json=json.dumps([q['id'] for q in mcqs]), required=2)
            session.add(challenge)
            await session.flush()
            session.add(LearningStrike(user_id=registered['user']['id'], language='python',
                node_id='python:stage-01', problem_id='python-path-01-values', source='evaluation', set_id=challenge.id))
            await session.commit()
            set_id = challenge.id
        results = await asyncio.gather(*(client.post(f'/strikes/sets/{set_id}/answers', headers=headers,
            json={'item_id': q['id'], 'response': q['answer']}) for q in mcqs))
        assert [r.status_code for r in results] == [200, 200]
        final = (await client.get(f'/strikes/sets/{set_id}', headers=headers)).json()
        assert final['correct'] == 2 and final['complete']
        # Concurrent evaluations must not create more than the configured cap.
        monkeypatch.setattr(settings, 'learning_strike_cap', 1)
        async def failed_evaluation():
            async with factory() as session:
                strike = await learning_strikes.add_strike(session, registered['user']['id'], 'python',
                    'python-path-01-values', 'python:stage-01', 'evaluation', {})
                await session.commit()
                return strike is not None
        assert sum(await asyncio.gather(failed_evaluation(), failed_evaluation())) == 1
    finally:
        app.dependency_overrides[get_session] = old
        await engine.dispose()
