from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.db.models import SectionEntitlement, User
from app.services.section_access import require_section


async def test_section_policy_requires_both_language_and_section(db, subscribe_user):
    user = User(email='section-access@example.com', hashed_password='unused', role='student')
    db.add(user)
    await db.flush()
    await subscribe_user(user.id, 'javascript')
    now = datetime.now(timezone.utc)
    db.add(SectionEntitlement(user_id=user.id, section='dsa', status='active', source='manual',
                              starts_at=now - timedelta(days=1), expires_at=now + timedelta(days=1)))
    await db.commit()
    assert await require_section(db, user, 'dsa', 'javascript', now=now) == 'dsa'
    for section, language, status in [('design-patterns', 'javascript', 403),
                                      ('dsa', 'python', 403), ('unknown', 'javascript', 404)]:
        with pytest.raises(HTTPException) as error:
            await require_section(db, user, section, language, now=now)
        assert error.value.status_code == status
    with pytest.raises(HTTPException) as error:
        await require_section(db, user, 'dsa', 'javascript', now=now + timedelta(days=2))
    assert error.value.status_code == 403


async def test_section_policy_does_not_accept_future_or_cancelled_grants(db, subscribe_user):
    user = User(email='section-future@example.com', hashed_password='unused', role='student')
    db.add(user)
    await db.flush()
    await subscribe_user(user.id, 'javascript')
    now = datetime.now(timezone.utc)
    db.add_all([
        SectionEntitlement(user_id=user.id, section='dsa', status='active', source='manual',
                           starts_at=now + timedelta(days=1), expires_at=now + timedelta(days=2)),
        SectionEntitlement(user_id=user.id, section='dsa', status='cancelled', source='manual',
                           starts_at=now - timedelta(days=1), expires_at=now + timedelta(days=2)),
    ])
    await db.commit()
    with pytest.raises(HTTPException) as error:
        await require_section(db, user, 'dsa', 'javascript', now=now)
    assert error.value.status_code == 403


async def test_staff_policy_keeps_existing_language_scope(db):
    admin = User(email='section-admin@example.com', hashed_password='unused', role='admin')
    db.add(admin)
    await db.commit()
    assert await require_section(db, admin, 'design-patterns', 'javascript') == 'design-patterns'
    admin.status = 'suspended'
    await db.commit()
    with pytest.raises(HTTPException) as error:
        await require_section(db, admin, 'design-patterns', 'javascript')
    assert error.value.status_code == 403
