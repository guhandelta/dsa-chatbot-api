import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.core.security import create_access_token
from app.db.models import AdminAuditEvent, KnowledgeDocument, ServiceOperation, Subscription, TraceRecord, Transaction, User
from app.services.peppercorns import credit


async def person(db, role='student', balance=0):
    user = User(email=f'{uuid4().hex}@dashboard.example', hashed_password='unused', role=role, peppercorns=0)
    db.add(user)
    await db.flush()
    if balance:
        await credit(db, user.id, balance, 'test_seed')
    await db.commit()
    return user, {'Authorization': 'Bearer ' + create_access_token(user.id)}


@pytest.mark.parametrize('path', ['/admin/overview', '/admin/accounts', '/admin/ledger', '/admin/audit', '/admin/operations', '/admin/runtime', '/admin/routing-usage', '/admin/content-readiness', '/admin/documents', '/admin/submissions'])
async def test_dashboard_endpoints_are_admin_only(client, db, path):
    assert (await client.get(path)).status_code == 401
    for role in ('student', 'instructor'):
        _, headers = await person(db, role)
        assert (await client.get(path, headers=headers)).status_code == 403


async def test_student_gift_is_atomic_audited_and_replay_safe(client, db):
    admin, headers = await person(db, 'admin')
    student, _ = await person(db, balance=10)
    headers['Idempotency-Key'] = 'gift-once'
    body = {'amount': 75, 'reason': 'Learning milestone'}
    first = await client.post(f'/admin/users/{student.id}/gifts', headers=headers, json=body)
    assert first.status_code == 200, first.text
    assert first.json()['peppercorns'] == 85
    again = await client.post(f'/admin/users/{student.id}/gifts', headers=headers, json=body)
    assert again.json() == first.json()
    changed = await client.post(f'/admin/users/{student.id}/gifts', headers=headers, json={**body, 'amount': 76})
    assert changed.status_code == 409
    events = (await db.scalars(select(AdminAuditEvent))).all()
    assert len(events) == 1 and events[0].actor_id == admin.id and events[0].target_id == student.id
    assert json.loads(events[0].before_json)['peppercorns'] == 10
    assert json.loads(events[0].after_json)['peppercorns'] == 85
    ledger = (await client.get('/admin/ledger', headers=headers, params={'user_id': student.id})).json()
    assert ledger['total'] == 2 and sum(t['amount'] for t in ledger['items']) == 85
    assert await db.scalar(select(func.count()).select_from(Subscription)) == 0
    assert (await client.get('/admin/overview', headers=headers)).json()['ledger_mismatches'] == 0


@pytest.mark.parametrize('body', [{'amount': 0, 'reason': 'Gift'}, {'amount': -1, 'reason': 'Gift'}, {'amount': 1.5, 'reason': 'Gift'}, {'amount': True, 'reason': 'Gift'}, {'amount': 1_000_001, 'reason': 'Gift'}, {'amount': 5, 'reason': '   '}, {'amount': 5, 'reason': 'a' * 81}])
async def test_invalid_gift_never_changes_a_balance(client, db, body):
    _, headers = await person(db, 'admin')
    student, _ = await person(db)
    headers['Idempotency-Key'] = 'invalid-gift'
    response = await client.post(f'/admin/users/{student.id}/gifts', headers=headers, json=body)
    assert response.status_code == 422
    await db.refresh(student)
    assert student.peppercorns == 0
    assert await db.scalar(select(func.count()).select_from(Transaction)) == 0
    assert await db.scalar(select(func.count()).select_from(AdminAuditEvent)) == 0


async def test_gifts_require_admin_student_and_request_key(client, db):
    admin, headers = await person(db, 'admin')
    student, student_headers = await person(db)
    _, teacher_headers = await person(db, 'instructor')
    url = f'/admin/users/{student.id}/gifts'
    body = {'amount': 20, 'reason': 'Support gift'}
    assert (await client.post(url, headers=headers, json=body)).status_code == 422
    for h in ({}, student_headers, teacher_headers):
        response = await client.post(url, headers={**h, 'Idempotency-Key': 'denied'}, json=body)
        assert response.status_code == (401 if not h else 403)
    response = await client.post(f'/admin/users/{admin.id}/gifts', headers={**headers, 'Idempotency-Key': 'wrong-role'}, json=body)
    assert response.status_code == 409
    assert await db.scalar(select(func.count()).select_from(Transaction)) == 0


async def test_gift_rolls_back_if_audit_cannot_be_recorded(client, db, monkeypatch):
    _, headers = await person(db, 'admin')
    student, _ = await person(db, balance=5)
    def fail(*args, **kwargs):
        raise RuntimeError('Audit unavailable')
    monkeypatch.setattr('app.services.admin_audit.record', fail)
    response = await client.post(f'/admin/users/{student.id}/gifts', headers={**headers, 'Idempotency-Key': 'atomic-gift'}, json={'amount': 50, 'reason': 'Support gift'})
    assert response.status_code == 502
    await db.refresh(student)
    assert student.peppercorns == 5
    assert await db.scalar(select(func.count()).select_from(Transaction)) == 1


async def test_accounts_filters_details_and_role_audit(client, db):
    _, headers = await person(db, 'admin')
    student, _ = await person(db)
    teacher, _ = await person(db, 'instructor')
    page = (await client.get('/admin/accounts', headers=headers, params={'role': 'student', 'limit': 1})).json()
    assert page['total'] == 1 and page['items'][0]['id'] == student.id
    assert (await client.get('/admin/accounts', headers=headers, params={'q': '%'})).json()['total'] == 0
    detail = (await client.get(f'/admin/accounts/{student.id}', headers=headers)).json()
    assert detail['access']['languages'] == [] and detail['subscriptions'] == []
    result = await client.patch(f'/admin/users/{student.id}/role', headers=headers, json={'role': 'instructor'})
    assert result.status_code == 200
    audit = (await client.get('/admin/audit', headers=headers)).json()
    assert audit['items'][0]['action'] == 'role_change'
    assert audit['items'][0]['before']['role'] == 'student'


async def test_status_changes_are_guarded_and_audited(client, db):
    admin, headers = await person(db, 'admin')
    student, _ = await person(db)
    assert (await client.patch(f'/admin/accounts/{admin.id}/status', headers=headers, json={'status': 'suspended', 'reason': 'Test reason'})).status_code == 400
    assert (await client.patch(f'/admin/accounts/{student.id}/status', headers=headers, json={'status': 'suspended', 'reason': '   '})).status_code == 422
    for state in ('suspended', 'active'):
        result = await client.patch(f'/admin/accounts/{student.id}/status', headers=headers, json={'status': state, 'reason': 'Support review'})
        assert result.status_code == 200 and result.json()['status'] == state
    assert await db.scalar(select(func.count()).select_from(AdminAuditEvent)) == 2


async def test_long_status_notes_fit_account_column_and_retain_full_audit_reason(client, db):
    _, headers = await person(db, 'admin')
    student, _ = await person(db)
    reason = 'a' * 500
    response = await client.patch(f'/admin/accounts/{student.id}/status', headers=headers, json={'status': 'suspended', 'reason': reason})
    assert response.status_code == 200
    await db.refresh(student)
    assert len(student.suspended_reason) == 255
    event = await db.scalar(select(AdminAuditEvent))
    assert event.reason == reason


async def test_security_list_has_bounded_pagination(client, db):
    from app.db.models import SecurityEvent
    _, headers = await person(db, 'admin')
    student, _ = await person(db)
    for i in range(3):
        db.add(SecurityEvent(user_id=student.id, severity='block', reasons='Blocked operation', code_excerpt='', context='test', counted_as_strike=False))
    await db.commit()
    first = (await client.get('/admin/security-events', headers=headers, params={'limit': 1})).json()
    second = (await client.get('/admin/security-events', headers=headers, params={'limit': 1, 'offset': 1})).json()
    assert len(first) == len(second) == 1 and first[0]['id'] != second[0]['id']
    assert (await client.get('/admin/security-events', headers=headers, params={'limit': 501})).status_code == 422


async def test_overview_uses_actual_time_windows_and_entitlements(client, db):
    _, headers = await person(db, 'admin')
    student, _ = await person(db, balance=20)
    current = datetime.now(timezone.utc)
    db.add_all([
        Subscription(user_id=student.id, language='java', status='cancelled', expires_at=current+timedelta(days=2)),
        Subscription(user_id=student.id, language='javascript', status='active', expires_at=current+timedelta(days=3)),
        Subscription(user_id=student.id, language='python', status='active', expires_at=current-timedelta(days=1)),
        ServiceOperation(id='recent', user_id=student.id, scope='chat', state='completed', fingerprint='a', amount=0, created_at=current),
        ServiceOperation(id='old-error', user_id=student.id, scope='chat', state='failed', http_status=502, fingerprint='b', amount=0, created_at=current-timedelta(days=40)),
        TraceRecord(trace_id='new', name='mentor', user_id=student.id, duration_ms=1500, total_tokens=42, estimated_cost_usd=.01, payload='{}', created_at=current),
    ])
    await db.commit()
    small = (await client.get('/admin/overview', headers=headers, params={'days': 7})).json()
    assert small['entitled_students'] == 1 and small['active_students'] == 1
    assert small['expiring_subscriptions'] == 2 and small['service_failures'] == 0
    assert small['credits_added'] == 20 and small['ledger_mismatches'] == 0
    assert small['trace_sample']['p95_ms'] == 1500 and small['trace_sample']['tokens'] == 42
    large = (await client.get('/admin/overview', headers=headers, params={'days': 90})).json()
    assert large['service_failures'] == 1


async def test_runtime_lists_configuration_without_secrets(client, db, monkeypatch):
    _, headers = await person(db, 'admin')
    monkeypatch.setattr('app.core.config.settings.openai_api_key', 'NEVER-RETURN-THIS-SECRET')
    response = await client.get('/admin/runtime', headers=headers)
    assert response.status_code == 200 and 'NEVER-RETURN-THIS-SECRET' not in response.text
    assert response.json()['database'] == 'reachable'
    assert all(p['connectivity'] == 'Not probed' for p in response.json()['providers'])


async def test_manual_access_does_not_change_provider_subscription(client, db):
    _, headers = await person(db, 'admin')
    student, _ = await person(db)
    expiry = datetime.now(timezone.utc)+timedelta(days=5)
    sub = Subscription(user_id=student.id, language='java', status='cancelled', expires_at=expiry, provider_ref='provider-sub')
    db.add(sub)
    await db.commit()
    params = {'user_id': student.id, 'language': 'java', 'days': 7, 'reason': 'Access support'}
    response = await client.post('/subscriptions/admin/grant', headers={**headers, 'Idempotency-Key': 'access-grant'}, params=params)
    assert response.status_code == 200, response.text
    await db.refresh(sub)
    assert sub.status == 'cancelled' and sub.expires_at.replace(tzinfo=timezone.utc) == expiry
    assert response.json()['id'] != sub.id
    assert await db.scalar(select(func.count()).select_from(AdminAuditEvent)) == 1


async def test_document_review_is_audited_with_note(client, db, monkeypatch):
    _, headers = await person(db, 'admin')
    author, _ = await person(db, 'instructor')
    doc = KnowledgeDocument(owner_id=author.id, filename='notes.md', status='pending', language='java', text='A source excerpt')
    db.add(doc)
    await db.commit()
    async def index(*args):
        return []
    monkeypatch.setattr('app.routers.learn._index', index)
    result = await client.post(f'/learn/documents/{doc.id}/approve', headers=headers, json={'note': 'Reviewed reference wording'})
    assert result.status_code == 200 and result.json()['review_note'] == 'Reviewed reference wording'
    audit = (await client.get('/admin/audit', headers=headers)).json()['items'][0]
    assert audit['action'] == 'document_approved' and audit['reason'] == 'Reviewed reference wording'
