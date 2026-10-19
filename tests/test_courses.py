"""Course HTTP access uses real authentication and current language entitlements."""
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
from sqlalchemy import select

from app.db.models import InstructorLanguage, Subscription
from tests.test_language_access import account


COURSE_URLS = (
    '/courses/',
    '/courses/java',
    '/courses/java/modules/basics/sources/reading',
)


@pytest.fixture
def catalog(monkeypatch):
    # Access tests isolate content only; authentication, DB and entitlement
    # resolution still execute through the real ASGI app.
    from app.services import course_catalog
    listing = Mock(return_value=[{'language': 'java'}, {'language': 'javascript'}])
    course = Mock(return_value={'language': 'java', 'modules': []})
    lesson = Mock(return_value={'language': 'java', 'document': 'A reading.'})
    monkeypatch.setattr(course_catalog, 'list_courses', listing)
    monkeypatch.setattr(course_catalog, 'get_course', course)
    monkeypatch.setattr(course_catalog, 'get_lesson', lesson)
    return listing, course, lesson


@pytest.mark.parametrize('url', COURSE_URLS)
async def test_courses_require_authentication(client, url):
    response = await client.get(url)
    assert response.status_code == 401, response.text


@pytest.mark.parametrize('role', ['student', 'instructor', 'admin'])
async def test_course_listing_filters_by_current_role_scope(client, db, catalog, role):
    user, headers = await account(db, role=role, languages=('java',) if role == 'student' else ())
    if role == 'instructor':
        db.add(InstructorLanguage(user_id=user.id, language='java', assigned_by=user.id))
        await db.commit()
    response = await client.get('/courses/', headers=headers)
    assert response.status_code == 200, response.text
    assert {course['language'] for course in response.json()['courses']} == (
        {'java', 'javascript'} if role == 'admin' else {'java'})
    catalog[0].assert_called_once_with()


@pytest.mark.parametrize('role', ['student', 'instructor'])
@pytest.mark.parametrize('url', COURSE_URLS[1:])
async def test_unscoped_language_is_denied_before_content_lookup(client, db, catalog, role, url):
    user, headers = await account(db, role=role, languages=('javascript',) if role == 'student' else ())
    if role == 'instructor':
        db.add(InstructorLanguage(user_id=user.id, language='javascript', assigned_by=user.id))
        await db.commit()
    response = await client.get(url, headers=headers)
    assert response.status_code == 403, response.text
    catalog[1].assert_not_called()
    catalog[2].assert_not_called()


@pytest.mark.parametrize('role', ['student', 'instructor'])
async def test_no_language_access_produces_empty_course_list(client, db, catalog, role):
    _, headers = await account(db, role=role)
    response = await client.get('/courses/', headers=headers)
    assert response.status_code == 200, response.text
    assert response.json() == {'courses': []}


async def test_expired_subscription_revokes_existing_token_course_access(client, db, catalog):
    user, headers = await account(db, languages=('java',))
    for url in COURSE_URLS:
        assert (await client.get(url, headers=headers)).status_code == 200
    subscription = await db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    subscription.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    await db.commit()
    catalog[1].reset_mock()
    catalog[2].reset_mock()
    assert (await client.get('/courses/', headers=headers)).json() == {'courses': []}
    for url in COURSE_URLS[1:]:
        assert (await client.get(url, headers=headers)).status_code == 403
    catalog[1].assert_not_called()
    catalog[2].assert_not_called()


@pytest.mark.parametrize('role', ['student', 'instructor', 'admin'])
async def test_suspended_accounts_cannot_read_courses(client, db, catalog, role):
    user, headers = await account(db, role=role, languages=('java',))
    user.status = 'suspended'
    await db.commit()
    listing = await client.get('/courses/', headers=headers)
    assert listing.status_code == 200, listing.text
    assert listing.json() == {'courses': []}
    for url in COURSE_URLS[1:]:
        assert (await client.get(url, headers=headers)).status_code == 403
    catalog[1].assert_not_called()
    catalog[2].assert_not_called()


async def test_missing_authorized_course_and_lesson_return_404(client, db, catalog):
    _, headers = await account(db, languages=('java',))
    catalog[1].return_value = None
    catalog[2].return_value = None
    for url in COURSE_URLS[1:]:
        response = await client.get(url, headers=headers)
        assert response.status_code == 404, response.text
    catalog[1].assert_called_once_with('java')
    catalog[2].assert_called_once_with('java', 'basics', 'reading')


async def test_teaching_assignment_revocation_applies_to_existing_token(client, db, catalog):
    user, headers = await account(db, role='instructor')
    assignment = InstructorLanguage(user_id=user.id, language='java', assigned_by=user.id)
    db.add(assignment)
    await db.commit()
    for url in COURSE_URLS:
        assert (await client.get(url, headers=headers)).status_code == 200
    catalog[1].assert_called_once_with('java')
    catalog[2].assert_called_once_with('java', 'basics', 'reading')
    await db.delete(assignment)
    await db.commit()
    assert (await client.get('/courses/', headers=headers)).json() == {'courses': []}
    for url in COURSE_URLS[1:]:
        assert (await client.get(url, headers=headers)).status_code == 403


async def test_real_course_listing_and_outline_are_language_scoped(client, db):
    _, headers = await account(db, languages=('java',))
    response = await client.get('/courses/', headers=headers)
    assert response.status_code == 200, response.text
    summaries = response.json()['courses']
    assert [course['language'] for course in summaries] == ['java']
    response = await client.get('/courses/java', headers=headers)
    assert response.status_code == 200, response.text
    course = response.json()
    assert course['language'] == 'java'
    assert course['status'] == 'draft'
    assert course['assessment_status'] == 'missing'
    assert course['modules']
    assert summaries[0]['module_count'] == len(course['modules'])
    assert summaries[0]['source_count'] == sum(len(m['sources']) for m in course['modules']) > 0
    assert all(module['objectives'] for module in course['modules'])
    assert (await client.get('/courses/javascript', headers=headers)).status_code == 403


@pytest.mark.parametrize('collection', ['content_catalog', 'reference_library', 'curriculum'])
async def test_real_reading_returns_source_text_without_answers(client, db, collection):
    from app.services import curriculum, reference_library
    from app.services.content_access import PROTECTED, public_text
    from app.services.content_catalog import read_content

    user, headers = await account(db, languages=('java',))
    response = await client.get('/courses/java', headers=headers)
    assert response.status_code == 200, response.text
    modules = response.json()['modules']
    choices = [(m, s) for m in modules for s in m['sources'] if s['collection'] == collection]
    assert choices, f'Java must expose an actual {collection} reading'
    module, source = (next((m, s) for m, s in choices if s['id'] == 'java-path-01-values')
                      if collection == 'content_catalog' else choices[0])
    response = await client.get(
        f"/courses/java/modules/{module['id']}/sources/{source['id']}", headers=headers)
    assert response.status_code == 200, response.text
    reading = response.json()
    assert reading['language'] == reading['metadata']['language'] == 'java'
    assert reading['module_id'] == module['id']
    assert reading['source_id'] == source['id']
    assert reading['title'] == source['title']
    assert reading['metadata']['contains_answer'] is False
    assert reading['status'] == 'draft'
    assert reading['document'].strip()
    assert not {'answer', 'solution', 'solutions', 'test_cases'} & reading.keys()
    if collection == 'content_catalog':
        raw = read_content(source['id'])
        assert PROTECTED.search(raw), 'Fixture must contain an answer section to exercise redaction'
        assert reading['document'] == public_text(raw)
        assert not PROTECTED.search(reading['document'])
        assert 'test_cases:' not in reading['document']
        assert 'return price * quantity;' not in reading['document']
    else:
        rows = reference_library.records() if collection == 'reference_library' else curriculum.records()
        row = next(r for r in rows if (r['id'] if collection == 'reference_library'
                                       else 'corpus-' + r['id']) == source['id'])
        assert row['metadata']['contains_answer'] is False
        assert reading['document'] == row['document']
    profile = await client.get('/auth/me', headers=headers)
    assert profile.json()['peppercorns'] == user.peppercorns


async def test_real_source_cannot_be_read_through_another_module_or_language(client, db):
    _, headers = await account(db, languages=('java', 'javascript'))
    course = await client.get('/courses/java', headers=headers)
    assert course.status_code == 200, course.text
    modules = course.json()['modules']
    module, source, other = next(
        (module, source, other)
        for module in modules for source in module['sources'] for other in modules
        if other['id'] != module['id'] and source['id'] not in {s['id'] for s in other['sources']})
    valid = f"/courses/java/modules/{module['id']}/sources/{source['id']}"
    assert (await client.get(valid, headers=headers)).status_code == 200
    for url in (
        f"/courses/java/modules/{other['id']}/sources/{source['id']}",
        f"/courses/java/modules/missing-module/sources/{source['id']}",
        f"/courses/java/modules/{module['id']}/sources/missing-source",
        f"/courses/javascript/modules/{module['id']}/sources/{source['id']}",
    ):
        response = await client.get(url, headers=headers)
        assert response.status_code == 404, response.text
