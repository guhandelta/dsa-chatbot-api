"""Current-source curation and final context regression checks."""
from types import SimpleNamespace
from langchain_core.documents import Document
from app.services import reference_library as library, rag_pipeline
from app.services.knowledge_hygiene import quarantine_reason
from app.services.reference_semantics import balanced_results
from tools.repair_reference_sections import framework_rows, headings


def doc(name, subject='java'):
    return Document(page_content=name,metadata={'track':'language','language':'java','subject':subject,'contains_answer':False})


def test_framework_sections_are_stable_and_exclude_labs():
    first,excluded=framework_rows();second,_=framework_rows()
    assert first==second
    assert {r['metadata']['subject'] for r in first}=={'css','sass','bootstrap','tailwind','bulma','shadcn'}
    assert len({r['id'] for r in first})==len(first)
    assert all(r['metadata']['contains_answer'] is False for r in first)
    assert all('Complete runnable lab source' not in r['payload']['section'] for r in first)
    assert any('assessment' in e['reason'].lower() for e in excluded)


def test_heading_split_preserves_code():
    pieces=headings('## First\n```python\n## code comment\n```\n## Second\ntext',2)
    assert len(pieces)==2 and '## code comment' in pieces[0]


def test_active_corpus_and_generated_records():
    assert not any(quarantine_reason(r) for r in library.records())
    assert sum(r['metadata'].get('dataset_version')=='knowledge-gap-fill-v1'
               or r['metadata'].get('origin') in ('generated_batch_001','generated_batch_002')
               for r in library.records())==204


def test_balancing_deduplicates():
    assert [d.page_content for d in balanced_results([doc('a'),doc('b')],[doc('a'),doc('c')])]==['a','b','c']


async def test_context_preserves_local_and_excludes_unselected_framework(monkeypatch):
    captured=[]
    class Model:
        async def ainvoke(self,messages):
            captured.extend(messages);return SimpleNamespace(content='Explain the comparison rule.')
    monkeypatch.setattr(rag_pipeline,'get_llm',lambda _:Model())
    monkeypatch.setattr('app.services.curriculum_search.search',lambda *a,**k:[doc('CURRENT REFERENCE')])
    monkeypatch.setattr('app.services.reference_semantics.search',lambda *a,**k:[])
    vector=[doc('FRAMEWORK SECRET','spring-core')]+[doc('OLD '+str(i)) for i in range(4)]
    monkeypatch.setattr(rag_pipeline,'get_vectorstore',lambda:SimpleNamespace(similarity_search=lambda *a,**k:vector))
    await rag_pipeline.run_rag_chat('Explain','openai',[],'java',track='language')
    assert 'CURRENT REFERENCE' in captured[0].content
    assert 'FRAMEWORK SECRET' not in captured[0].content
