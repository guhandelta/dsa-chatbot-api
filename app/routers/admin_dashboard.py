"""Admin workspace: bounded lists, measured aggregates, and audited student gifts."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import case, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import require_admin
from app.db.database import get_session
from app.db.models import (AdminAuditEvent, KnowledgeDocument, LearningEvent,
    PracticeSession, ServiceOperation, Submission, Subscription, TraceRecord,
    Transaction, User, VectorCleanupJob)
from app.models.schemas import UserOut
from app.services import admin_audit
from app.services.language_access import access_view
from app.services.operations import perform
from app.services.peppercorns import credit

router = APIRouter(prefix='/admin', tags=['admin'], dependencies=[Depends(require_admin)])
STARTED_AT = datetime.now(timezone.utc)


def source_fingerprint():
    import hashlib
    root = Path(__file__).resolve().parents[1]
    digest = hashlib.sha256()
    for path in sorted(root.rglob('*.py')):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()[:12]


LOADED_SOURCE = source_fingerprint()


def now():
    return datetime.now(timezone.utc)


def encoded_time(value):
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc).isoformat() if value.tzinfo is None else value.isoformat()


def account_out(user):
    return {**UserOut.model_validate(user).model_dump(), 'created_at': encoded_time(user.created_at)}


async def target_user(session, user_id):
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(404, 'User not found.')
    return user


@router.get('/accounts')
async def accounts(q: str = Query(default='', max_length=150),
                   role: Literal['student', 'instructor', 'admin'] | None = None,
                   status: Literal['active', 'suspended'] | None = None,
                   offset: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100),
                   session: AsyncSession = Depends(get_session)):
    conditions = []
    if q.strip():
        conditions.append(User.email.ilike('%' + q.strip().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%', escape='\\'))
    if role:
        conditions.append(User.role == role)
    if status:
        conditions.append(User.status == status)
    total = await session.scalar(select(func.count()).select_from(User).where(*conditions))
    users = (await session.scalars(select(User).where(*conditions).order_by(User.created_at.desc(), User.id).offset(offset).limit(limit))).all()
    return {'items': [account_out(u) for u in users], 'total': total, 'offset': offset, 'limit': limit}


@router.get('/accounts/{user_id}')
async def account_detail(user_id: str, session: AsyncSession = Depends(get_session)):
    user = await target_user(session, user_id)
    subscriptions = (await session.scalars(select(Subscription).where(Subscription.user_id == user_id).order_by(Subscription.expires_at.desc()))).all()
    return {'user': account_out(user), 'access': await access_view(session, user),
            'subscriptions': [{'id': s.id, 'language': s.language, 'status': s.status,
                'expires_at': encoded_time(s.expires_at), 'source': 'provider' if s.provider_ref else 'manual'} for s in subscriptions]}


@router.get('/ledger')
async def ledger(user_id: str | None = None, offset: int = Query(default=0, ge=0),
                 limit: int = Query(default=20, ge=1, le=100), session: AsyncSession = Depends(get_session)):
    conditions = [Transaction.user_id == user_id] if user_id else []
    total = await session.scalar(select(func.count()).select_from(Transaction).where(*conditions))
    rows = (await session.execute(select(Transaction, User.email).join(User, User.id == Transaction.user_id)
        .where(*conditions).order_by(Transaction.created_at.desc(), Transaction.id).offset(offset).limit(limit))).all()
    return {'items': [{'id': t.id, 'user_id': t.user_id, 'email': email, 'amount': t.amount,
        'balance_after': t.balance_after, 'reason': t.reason, 'created_at': encoded_time(t.created_at)} for t, email in rows],
        'total': total, 'offset': offset, 'limit': limit}


class GiftRequest(BaseModel):
    amount: int = Field(strict=True, gt=0, le=1_000_000)
    reason: str = Field(min_length=3, max_length=80)


@router.post('/users/{user_id}/gifts', response_model=UserOut)
async def gift(user_id: str, request: GiftRequest,
               idempotency_key: str = Header(..., alias='Idempotency-Key'),
               admin: User = Depends(require_admin), session: AsyncSession = Depends(get_session)):
    reason = request.reason.strip()
    if len(reason) < 3:
        raise HTTPException(422, 'Please give a reason of at least 3 characters.')
    await target_user(session, user_id)

    async def prepare():
        role = await session.scalar(select(User.role).where(User.id == user_id))
        if role != 'student':
            raise HTTPException(409, 'Peppercorn gifts can only be assigned to students.')

    async def work(_):
        balance = await credit(session, user_id, request.amount, 'admin:gift:' + reason)
        admin_audit.record(session, admin.id, 'peppercorn_gift', user_id, reason=reason,
            before={'peppercorns': balance - request.amount}, after={'peppercorns': balance, 'amount': request.amount})
        user = await target_user(session, user_id)
        await session.refresh(user)
        return UserOut.model_validate(user)

    return await perform(session, admin.id, 'admin:gift', idempotency_key,
        {'user_id': user_id, 'amount': request.amount, 'reason': reason}, 0, 'admin:gift', work, prepare=prepare)


class StatusRequest(BaseModel):
    status: Literal['active', 'suspended']
    reason: str = Field(min_length=3, max_length=500)


@router.patch('/accounts/{user_id}/status', response_model=UserOut)
async def account_status(user_id: str, request: StatusRequest, admin: User = Depends(require_admin),
                         session: AsyncSession = Depends(get_session)):
    if user_id == admin.id:
        raise HTTPException(400, 'You cannot suspend your own admin account.')
    if len(request.reason.strip()) < 3:
        raise HTTPException(422, 'A reason is required.')
    user = await target_user(session, user_id)
    before = {'status': user.status, 'strikes': user.strikes}
    if request.status == 'active':
        from app.services.strikes import reinstate
        await reinstate(session, user)
    else:
        user.status, user.suspended_reason = 'suspended', request.reason.strip()[:255]
    admin_audit.record(session, admin.id, 'account_status', user_id, reason=request.reason.strip(),
                       before=before, after={'status': user.status, 'strikes': user.strikes})
    await session.commit()
    return UserOut.model_validate(user)


@router.get('/audit')
async def audit(offset: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100),
                session: AsyncSession = Depends(get_session)):
    total = await session.scalar(select(func.count()).select_from(AdminAuditEvent))
    rows = (await session.execute(select(AdminAuditEvent, User.email).join(User, User.id == AdminAuditEvent.actor_id)
        .order_by(AdminAuditEvent.created_at.desc(), AdminAuditEvent.id).offset(offset).limit(limit))).all()
    return {'items': [{'id': a.id, 'actor_email': email, 'action': a.action, 'target_id': a.target_id,
        'reason': a.reason, 'before': json.loads(a.before_json), 'after': json.loads(a.after_json),
        'created_at': encoded_time(a.created_at)} for a, email in rows], 'total': total, 'offset': offset, 'limit': limit}


@router.get('/operations')
async def operations(days: int = Query(default=7, ge=1, le=90),
                     offset: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100),
                     state: Literal['running', 'failed', 'completed'] | None = None,
                     session: AsyncSession = Depends(get_session)):
    conditions = [ServiceOperation.created_at >= now() - timedelta(days=days)]
    if state:
        conditions.append(ServiceOperation.state == state)
    total = await session.scalar(select(func.count()).select_from(ServiceOperation).where(*conditions))
    rows = (await session.execute(select(ServiceOperation, User.email).join(User, User.id == ServiceOperation.user_id)
        .where(*conditions).order_by(ServiceOperation.created_at.desc(), ServiceOperation.id).offset(offset).limit(limit))).all()
    return {'items': [{'id': o.id, 'email': email, 'scope': o.scope, 'state': o.state, 'amount': o.amount,
        'http_status': o.http_status, 'created_at': encoded_time(o.created_at)} for o, email in rows],
        'total': total, 'offset': offset, 'limit': limit}


@router.get('/overview')
async def overview(days: int = Query(default=7, ge=1, le=90), session: AsyncSession = Depends(get_session)):
    current = now()
    since = current - timedelta(days=days)
    async def count(model, *conditions):
        return await session.scalar(select(func.count()).select_from(model).where(*conditions)) or 0

    roles = dict((await session.execute(select(User.role, func.count()).group_by(User.role))).all())
    subscription_conditions = (Subscription.status.in_(('active', 'cancelled')), Subscription.expires_at > current)
    entitled = await session.scalar(select(func.count(func.distinct(Subscription.user_id))).join(User, User.id == Subscription.user_id)
        .where(*subscription_conditions, User.role == 'student', User.status == 'active')) or 0
    active = await session.scalar(select(func.count(func.distinct(ServiceOperation.user_id))).join(User, User.id == ServiceOperation.user_id)
        .where(ServiceOperation.created_at >= since, ServiceOperation.state == 'completed', User.role == 'student',
            (ServiceOperation.scope.in_(('chat', 'analyze', 'mentor')) | ServiceOperation.scope.like('practice:%')))) or 0
    op_rows = (await session.execute(select(ServiceOperation.state, func.count()).where(ServiceOperation.created_at >= since).group_by(ServiceOperation.state))).all()
    operation_counts = dict(op_rows)
    failures = await count(ServiceOperation, ServiceOperation.created_at >= since, ServiceOperation.http_status >= 500)
    pending = await count(KnowledgeDocument, KnowledgeDocument.status == 'pending')
    oldest = await session.scalar(select(func.min(KnowledgeDocument.created_at)).where(KnowledgeDocument.status == 'pending'))
    ledger_sum = select(Transaction.user_id.label('uid'), func.sum(Transaction.amount).label('balance')).group_by(Transaction.user_id).subquery()
    mismatch_count = await session.scalar(select(func.count()).select_from(User).outerjoin(ledger_sum, User.id == ledger_sum.c.uid)
        .where(User.peppercorns != func.coalesce(ledger_sum.c.balance, 0))) or 0
    credits, spent, refunded = (await session.execute(select(
        func.coalesce(func.sum(case((Transaction.amount > 0, Transaction.amount), else_=0)), 0),
        func.coalesce(func.sum(case((Transaction.amount < 0, -Transaction.amount), else_=0)), 0),
        func.coalesce(func.sum(case((Transaction.reason.like('refund:%'), Transaction.amount), else_=0)), 0)
    ).where(Transaction.created_at >= since))).one()
    learning = (await session.execute(select(LearningEvent.kind, func.count()).where(LearningEvent.created_at >= since).group_by(LearningEvent.kind))).all()
    trace_rows = (await session.execute(select(TraceRecord.duration_ms, TraceRecord.estimated_cost_usd, TraceRecord.total_tokens)
        .where(TraceRecord.created_at >= since).order_by(TraceRecord.created_at.desc()).limit(1000))).all()
    trace_total = await count(TraceRecord, TraceRecord.created_at >= since)
    durations = sorted(r.duration_ms for r in trace_rows)
    return {'generated_at': current.isoformat(), 'days': days, 'users_by_role': roles,
        'entitled_students': entitled, 'active_students': active, 'pending_documents': pending,
        'oldest_pending_at': encoded_time(oldest), 'training_needs_review': await count(Submission, Submission.status == 'needs_review'),
        'expiring_subscriptions': await count(Subscription, *subscription_conditions, Subscription.expires_at <= current + timedelta(days=7)),
        'operations': operation_counts, 'service_failures': failures,
        'stuck_operations': await count(ServiceOperation, ServiceOperation.state == 'running', ServiceOperation.created_at < current - timedelta(minutes=30)),
        'cleanup_jobs': await count(VectorCleanupJob), 'busy_practice_sessions': await count(PracticeSession, PracticeSession.busy.is_(True)),
        'suspended_users': await count(User, User.status == 'suspended'), 'ledger_mismatches': mismatch_count,
        'credits_added': credits, 'credits_spent': spent, 'credits_refunded': refunded, 'learning_events': dict(learning),
        'trace_sample': {'sampled': len(trace_rows), 'total': trace_total,
            'p95_ms': round(durations[min(int(len(durations)*0.95), len(durations)-1)], 1) if durations else None,
            'estimated_cost_usd': round(sum(r.estimated_cost_usd for r in trace_rows), 6) if trace_rows else None,
            'tokens': sum(r.total_tokens for r in trace_rows) if trace_rows else None,
            'coverage': 'Persisted mentor and analysis traces only; latest 1,000 in the selected period. Not total provider billing.'}}


@router.get('/runtime')
async def runtime(session: AsyncSession = Depends(get_session)):
    from app.services.chat_model_routing import configured_providers, model_name
    await session.execute(text('SELECT 1'))
    revision = (await session.execute(text('SELECT version_num FROM alembic_version'))).scalars().all() if not settings.auto_create_tables else ['test-schema']
    return {'api_version': '2.0.0', 'loaded_at': STARTED_AT.isoformat(), 'source_fingerprint': LOADED_SOURCE,
        'database': 'reachable', 'migrations': revision, 'execution_backend': settings.exec_backend,
        'execution_image': settings.exec_container_image or None,
        'agentic_enabled': settings.agentic_rag_enabled, 'tracing_enabled': settings.tracing_enabled,
        'providers': [{'provider': p, 'model': model_name(p), 'configured': True, 'connectivity': 'Not probed'} for p in configured_providers()],
        'routing_preferences': {'explanations': settings.chat_explain_provider, 'code': settings.chat_code_provider, 'reasoning': settings.chat_reasoning_provider},
        'model_timeout_seconds': settings.chat_model_timeout_seconds,
        'backup_status': 'Not monitored', 'readiness_note': 'Configuration is not a live provider, sandbox, or vector-store readiness check.'}


@router.get('/routing-usage')
async def routing_usage(days: int = Query(default=7, ge=1, le=90), session: AsyncSession = Depends(get_session)):
    conditions = [ServiceOperation.scope == 'chat', ServiceOperation.state == 'completed', ServiceOperation.created_at >= now()-timedelta(days=days)]
    total = await session.scalar(select(func.count()).select_from(ServiceOperation).where(*conditions)) or 0
    rows = (await session.scalars(select(ServiceOperation.response_json).where(*conditions).order_by(ServiceOperation.created_at.desc()).limit(1000))).all()
    buckets = {}
    measured = 0
    for raw in rows:
        try:
            info = json.loads(raw).get('model_routing')
        except (ValueError, AttributeError):
            continue
        if not info:
            continue
        measured += 1
        key = (info.get('provider'), info.get('model'), info.get('task') or 'manual')
        bucket = buckets.setdefault(key, {'provider': key[0], 'model': key[1], 'task': key[2], 'answers': 0, 'fallbacks': 0})
        bucket['answers'] += 1
        bucket['fallbacks'] += bool(info.get('fallback_used'))
    return {'items': list(buckets.values()), 'sampled': len(rows), 'measured': measured, 'total_completed_chats': total,
        'note': 'Latest 1,000 successful chat receipts in this period. Failed attempts and older receipts may have no routing metadata. Quality is not inferred from completion.'}


@router.get('/content-readiness')
async def content_readiness():
    """Read recorded audit artifacts; never trigger code execution or model calls."""
    root = Path(__file__).resolve().parents[2] / 'docs'
    files = ('knowledge-coverage-audit.json', 'exercise-audit.json', 'container-isolation-evaluation.json',
             'agentic-rag-summary.json', 'mentor-openai-live-evaluation.json', 'mentor-gemini-live-evaluation.json')
    artifacts = []
    for name in files:
        path = root / name
        if not path.exists():
            artifacts.append({'name': name, 'available': False})
            continue
        try:
            data = json.loads(path.read_text())
            # Summary only; do not publish provider responses or learner content.
            summaries = {key: value for key, value in data.items() if key in ('summary', 'totals', 'generated_at', 'created_at', 'status')} if isinstance(data, dict) else {}
            artifacts.append({'name': name, 'available': True, 'file_updated_at': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(), 'summary': summaries})
        except (OSError, ValueError):
            artifacts.append({'name': name, 'available': False})
    return {'artifacts': artifacts, 'note': 'Recorded audit evidence, not a current readiness certification. File update time is not necessarily evaluation time.'}


@router.get('/documents')
async def documents(status: Literal['pending', 'published', 'rejected'] | None = None,
                    offset: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100),
                    session: AsyncSession = Depends(get_session)):
    from app.routers.learn import _out
    conditions = [KnowledgeDocument.status == status] if status else []
    total = await session.scalar(select(func.count()).select_from(KnowledgeDocument).where(*conditions))
    rows = (await session.execute(select(KnowledgeDocument, User.email).join(User, User.id == KnowledgeDocument.owner_id)
        .where(*conditions).order_by(KnowledgeDocument.created_at.desc(), KnowledgeDocument.id).offset(offset).limit(limit))).all()
    return {'items': [_out(doc, email) for doc, email in rows], 'total': total, 'offset': offset, 'limit': limit}


@router.get('/submissions')
async def submissions(status: Literal['needs_review', 'failed', 'published'] | None = None,
                      offset: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100),
                      session: AsyncSession = Depends(get_session)):
    conditions = [Submission.status == status] if status else []
    total = await session.scalar(select(func.count()).select_from(Submission).where(*conditions))
    rows = (await session.execute(select(Submission, User.email).join(User, User.id == Submission.user_id)
        .where(*conditions).order_by(Submission.created_at.desc(), Submission.id).offset(offset).limit(limit))).all()
    items = []
    for s, email in rows:
        try:
            report = json.loads(s.report_json)
        except ValueError:
            report = {'note': 'Report could not be decoded.'}
        items.append({'id': s.id, 'email': email, 'problem_id': s.problem_id, 'status': s.status,
                      'report': report, 'created_at': encoded_time(s.created_at)})
    return {'items': items, 'total': total, 'offset': offset, 'limit': limit}
