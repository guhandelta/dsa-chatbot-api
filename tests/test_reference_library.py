"""Reference ingestion never promotes source claims or leaks exercise answers."""
import json
import zipfile
from pathlib import Path

from app.services import reference_library
from app.services.curriculum_search import search
from tools.import_reference_library import build, safe_reference


def canonical(rid, language='python', answer=False):
    return {'id':rid,'document':'Unique reference about Python lists and lookup.',
            'metadata':{'language':language,'kind':'exercise' if answer else 'concept',
                        'contains_answer':answer,'verified':True}, 'payload':{'answer':'SECRET-SOLUTION'}}


def test_all_requested_subjects_are_available_as_reference_only():
    subjects={s['id']:s for s in reference_library.subjects()}
    required={'python','c','cpp','rust','ruby','typescript','embedded-python','embedded-c',
              'python-flask','python-django','python-fastapi','spring-core','spring-mvc','spring-boot'}
    assert required <= subjects.keys()
    assert all(not subjects[s]['executable'] and subjects[s]['retrievable_records']>0 for s in required)
    rows=reference_library.records()
    assert all(r['metadata']['verified'] is False for r in rows)
    assert all(r['metadata']['language'] not in ('java','javascript') or r['metadata']['subject'].startswith('spring-') for r in rows)


def test_queries_stay_in_selected_language_and_subject():
    for language,subject,query in [('rust','rust','ownership borrowing move'),('python','python-flask','Flask request worker'),
                                   ('java','spring-mvc','DispatcherServlet controller mapping'),('c','embedded-c','interrupt register')]:
        docs=search(query,'language',language,subject=subject)
        assert docs
        assert all(d.metadata['language']==language and d.metadata['subject']==subject for d in docs)
        assert all(d.metadata['contains_answer'] is False and d.metadata['kind'] not in ('exercise','gotcha') for d in docs)
    assert not search('Flask','language','java',subject='python-flask')
    assert not search('anything','language','java',subject='does-not-exist')
    # Default Java/JS learning cannot accidentally retrieve Spring/framework material.
    assert not any(d.metadata.get('subject','').startswith('spring-') for d in search('DispatcherServlet','language','java'))


def test_import_is_deterministic_deduplicates_and_preserves_unicode_separators(tmp_path):
    source=tmp_path/'source';source.mkdir();output=tmp_path/'out'
    record=canonical('separator');record['document']='A valid JSON string has a Unicode separator: a\u2028b.'
    (source/'one.jsonl').write_text(json.dumps(record,ensure_ascii=False)+'\n')
    (source/'two.jsonl').write_text(json.dumps(record,ensure_ascii=False)+'\n')
    (source/'answers.jsonl').write_text(json.dumps(canonical('answer',answer=True))+'\n')
    # Supplied scripts are data, never imported or executed.
    (source/'payload.py').write_text('raise RuntimeError("must not run")')
    report=build(source,output)
    assert not report['errors']
    rows=[json.loads(l) for l in (output/'records.jsonl').open()]
    refs=[r for r in rows if r['metadata']['subject']=='python']
    assert len(refs)==2
    assert any('\u2028' in r['document'] for r in refs)
    assert len(next(r for r in refs if reference_library.eligible(r))['provenance'])==2 # duplicate files retain both source aliases
    assert len([r for r in refs if reference_library.eligible(r)])==1
    before=(output/'records.jsonl').read_bytes()
    build(source,output)
    assert (output/'records.jsonl').read_bytes()==before


def test_conflicting_record_ids_are_quarantined(tmp_path):
    source=tmp_path/'source';source.mkdir()
    a=canonical('same');b=canonical('same');b['document']='An incompatible different candidate.'
    (source/'a.jsonl').write_text(json.dumps(a)+'\n')
    (source/'b.jsonl').write_text(json.dumps(b)+'\n')
    report=build(source,tmp_path/'out')
    assert len(report['conflicting_ids_quarantined'])==1
    rows=[json.loads(l) for l in (tmp_path/'out/records.jsonl').open()]
    assert not any(r['metadata']['subject']=='python' for r in rows)


def test_blueprint_solutions_are_not_in_retrieval_view():
    assert safe_reference('Concept\nUseful teaching prose.\n8. Coding Exercises\nSECRET-SOLUTION')=='Concept\nUseful teaching prose.'


async def test_reference_subject_api_and_chat_validate_before_debit(client, monkeypatch, subscribe_user):
    response=await client.post('/auth/register',json={'email':'library@example.com','password':'password123'})
    await subscribe_user(response.json()['user']['id'], 'java', 'python')
    headers={'Authorization':'Bearer '+response.json()['access_token']}
    balance=response.json()['user']['peppercorns'];calls=[]
    async def reply(**kwargs):calls.append(kwargs);return 'Scoped reference explanation.'
    monkeypatch.setattr('app.routers.chat.run_rag_chat',reply)
    assert (await client.get('/tracks/reference-subjects')).status_code==401
    subjects=(await client.get('/tracks/reference-subjects',headers=headers)).json()['subjects']
    assert any(s['id']=='spring-boot' and s['executable'] is False for s in subjects)
    request={'message':'Explain MVC','language':'python','track':'language','subject':'spring-mvc'}
    assert (await client.post('/chat/',headers=headers,json=request)).status_code==422
    assert calls==[]
    assert (await client.get('/auth/me',headers=headers)).json()['peppercorns']==balance
    request['language']='java'
    response=await client.post('/chat/',headers=headers,json=request)
    assert response.status_code==200,response.text
    assert calls[0]['subject']=='spring-mvc'


def test_plural_source_gotcha_kinds_cannot_enter_retrieval():
    from tools.import_reference_library import normalize
    row=normalize({'id':'unsafe','record_type':'common_gotchas','track':'embedded_c',
                   'title':'A diagnosis','gotchas':[{'fix':'SECRET'}]}, 'embedded/Embedded_C_corpus.zip!records.jsonl')
    assert row['kind']=='gotcha' and row['contains_answer'] is True
    assert safe_reference('Intro material.\n6. Core practice exercises with answer key\nSECRET')=='Intro material.'


def test_imported_source_replacement_invalidates_local_search(tmp_path,monkeypatch):
    from app.services.reference_library import LIBRARY_DIR
    monkeypatch.setattr(reference_library,'LIBRARY_DIR',tmp_path)
    row={'id':'reference-one','document':'uniquetermold', 'metadata':{
        'kind':'reference','subject':'python','language':'python','contains_answer':False}}
    path=tmp_path/'records.jsonl';path.write_text(json.dumps(row)+'\n')
    assert search('uniquetermold','language','python',subject='python')
    row['document']='uniquetermreplacementlonger';path.write_text(json.dumps(row)+'\n')
    assert not search('uniquetermold','language','python',subject='python')
    assert search('uniquetermreplacementlonger','language','python',subject='python')


async def test_vector_results_are_rechecked_for_subject_and_answer_safety(monkeypatch):
    from types import SimpleNamespace
    from app.services import rag_pipeline as rp
    from langchain_core.documents import Document
    captured=[]
    class Model:
        async def ainvoke(self,messages):
            captured.extend(messages);return SimpleNamespace(content='Scoped answer')
    class Store:
        def similarity_search(self,*args,**kwargs):
            return [Document(page_content=text,metadata={
                'subject':subject,'language':language,'contains_answer':False,'kind':kind,'track':'language'})
                for text,subject,language,kind in [
                    ('SAFE-MVC','spring-mvc','java','reference'),
                    ('WRONG-FRAMEWORK','python-flask','python','reference'),
                    ('EXERCISE-ANSWER','spring-mvc','java','exercise')]]
    monkeypatch.setattr(rp,'get_llm',lambda p:Model())
    monkeypatch.setattr(rp,'get_vectorstore',lambda:Store())
    monkeypatch.setattr('app.services.curriculum_search.search',lambda *args,**kwargs:[])
    await rp.run_rag_chat('MVC','openai',[],'java',track='language',subject='spring-mvc')
    prompt=captured[0].content
    assert 'SAFE-MVC' in prompt
    assert 'WRONG-FRAMEWORK' not in prompt and 'EXERCISE-ANSWER' not in prompt
