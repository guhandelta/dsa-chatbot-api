"""Release-wide content audit and subscription boundary regressions."""
from datetime import datetime, timedelta, timezone
import json
import pytest
from sqlalchemy import select
from fastapi import HTTPException
from app.db.models import ChatThread, ChatMessage, QuizSession, Subscription, StudyNote
from app.services import language_access as access, quiz
from app.services.content_access import scoped_markdown, learner_document
from tests.test_language_access import account
from tools.audit_language_integrity import audit

LANGUAGES = ('python', 'javascript', 'java', 'typescript', 'c', 'cpp', 'rust', 'go', 'csharp', 'ruby', 'html', 'css')


def test_entire_release_has_no_language_mixups():
    report = audit()
    assert report['counts']['quiz_items'] >= 1470
    assert not report['errors'], report['errors']


def test_shared_examples_keep_only_the_selected_language():
    text = '# Algorithm\nShared explanation.\n## Examples\n### Python\n```python\nprint(1)\n```\n### Java\n```java\nSystem.out.println(1);\n```\n## Complexity\nO(n)\n'
    result = scoped_markdown(text, 'java')
    assert 'Shared explanation' in result and 'System.out' in result and 'O(n)' in result
    assert 'print(1)' not in result and '### Python' not in result
    assert 'print(1)' in scoped_markdown(text, 'python')
    assert 'System.out' not in scoped_markdown(text, 'python')


def test_shared_algorithm_view_never_shows_other_languages():
    for language in LANGUAGES[:10]:
        text = learner_document('merge-sort', language)
        assert '```' + language in text
        if language != 'python':
            assert '```python' not in text


@pytest.mark.parametrize('language', LANGUAGES)
async def test_every_subscription_is_exactly_language_scoped(client, db, language):
    user, headers = await account(db, languages=(language,))
    view = await client.get('/auth/me/access', headers=headers)
    assert view.status_code == 200 and view.json()['languages'] == [language]
    catalog = await client.get(f'/tracks/language/items?language={language}', headers=headers)
    assert catalog.status_code == 200
    assert all(item['language'] in (None, language) for item in catalog.json())
    assert await access.allowed_languages(db, user) == [language]
    assert await access.resolve_language(db, user) == language
    for foreign in LANGUAGES:
        if foreign != language:
            with pytest.raises(HTTPException) as exc:
                await access.require_language(db, user, foreign)
            assert exc.value.status_code == 403


@pytest.mark.parametrize('language', LANGUAGES)
async def test_all_learning_entry_points_reject_unsubscribed_language(client, db, language):
    subscribed = 'python' if language != 'python' else 'java'
    user, headers = await account(db, languages=(subscribed,))
    requests = [
        ('GET', f'/study/path?language={language}', None),
        ('GET', f'/study/nodes/{language}:stage-01/lesson?language={language}', None),
        ('GET', f'/study/next?language={language}', None),
        ('GET', f'/study/notes?language={language}', None),
        ('GET', f'/study/insights?language={language}', None),
        ('GET', f'/courses/{language}', None),
        ('GET', f'/tracks/language/items?language={language}', None),
        ('GET', f'/problems/two-sum?language={language}', None),
        ('GET', f'/problems/two-sum/solution?language={language}', None),
        ('POST', '/study/quiz', {'language': language}),
        ('POST', '/study/message', {'language': language, 'message': 'Teach values'}),
        ('POST', '/study/message', {'language': subscribed, 'mode': 'compare', 'compare_language': language, 'message': 'Compare values'}),
        ('POST', '/chat/', {'language': language, 'message': 'Teach values'}),
        ('POST', '/practice/sessions', {'language': language, 'problem_id': 'two-sum'}),
        ('POST', '/analyze/', {'language': language, 'problem_id': 'two-sum', 'user_code': 'unused'}),
        ('POST', '/mentor/ask', {'language': language, 'problem_id': 'two-sum', 'reasoning': 'Explain values'}),
        ('PATCH', '/auth/me/language', {'language': language}),
    ]
    for method, url, body in requests:
        response = await client.request(method, url, headers=headers, **({'json': body} if body else {}))
        assert response.status_code == 403, (language, method, url, response.text)
    assert (await client.get('/auth/me', headers=headers)).json()['peppercorns'] == 50


async def test_saved_comparison_and_notes_recheck_both_subscriptions(client, db):
    user, headers = await account(db, languages=('java', 'javascript'))
    thread = ChatThread(user_id=user.id, language='java', compare_language='javascript', track='study-compare')
    db.add(thread)
    await db.flush()
    db.add(ChatMessage(thread_id=thread.id, role='assistant', content='Java and JavaScript examples'))
    db.add(StudyNote(user_id=user.id, language='java', mode='compare', title='Comparison', body_json=json.dumps({'first':'java','second':'javascript'})))
    await db.commit()
    assert (await client.get(f'/chat/threads/{thread.id}/messages', headers=headers)).status_code == 200
    sub = await db.scalar(select(Subscription).where(Subscription.user_id == user.id, Subscription.language == 'javascript'))
    sub.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    await db.commit()
    assert (await client.get(f'/chat/threads/{thread.id}/messages', headers=headers)).status_code == 403
    assert (await client.get('/chat/threads', headers=headers)).json() == []
    assert (await client.get('/study/notes?language=java', headers=headers)).json()['notes'] == []


async def test_saved_quiz_cannot_be_read_or_answered_after_expiry(client, db):
    user, headers = await account(db, languages=('java',))
    row = QuizSession(user_id=user.id, language='java', node_id='java:stage-01')
    db.add(row)
    await db.commit()
    sub = await db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    sub.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    await db.commit()
    assert (await client.get(f'/study/quiz/{row.id}', headers=headers)).status_code == 403
    response = await client.post(f'/study/quiz/{row.id}/answer', headers=headers, json={'item_id':'java-s01-code','response':1})
    assert response.status_code == 403


def test_knowledge_base_snippet_annotations_use_the_right_comment_syntax():
    doc = 'Incorrect:\nbad()\nCorrect:\ngood()'
    assert quiz.lesson_code(doc, 'java').startswith('// Incorrect')
    assert quiz.lesson_code(doc, 'ruby').startswith('# Incorrect')


@pytest.mark.parametrize('route', ['/tracks/items/merge-sort', '/problems/merge-sort'])
async def test_shared_content_api_uses_subscription_language_and_blocks_override(client, db, route):
    user, headers = await account(db, languages=('java',))
    response = await client.get(route, headers=headers)
    assert response.status_code == 200, response.text
    text = response.json()['markdown']
    assert '```java\n' in text
    assert '```python' not in text and '```javascript' not in text
    response = await client.get(route, headers=headers, params={'language': 'python'})
    assert response.status_code == 403
