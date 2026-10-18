"""Semantic references keep current curation, exact scopes and safe initialization."""
import json
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from time import sleep
from types import SimpleNamespace
from langchain_core.documents import Document
from app.services import reference_semantics as semantic


def test_semantic_search_checks_current_scope(tmp_path,monkeypatch):
    path=tmp_path/'index.json';path.write_text(json.dumps({'collection':'test','model':semantic.MODEL}))
    monkeypatch.setattr(semantic,'MANIFEST',path)
    monkeypatch.setattr(semantic.settings,'vector_store','chroma')
    raw=[Document(page_content='valid',metadata={'language':'java','subject':'java'}),
         Document(page_content='foreign',metadata={'language':'python','subject':'python'}),
         Document(page_content='withdrawn',metadata={'language':'java','subject':'java'})]
    filters=[]
    def lookup(query,k,filter):filters.append(filter);return raw
    monkeypatch.setattr(semantic,'_store',lambda *a:SimpleNamespace(similarity_search=lookup))
    monkeypatch.setattr(semantic,'current_document',lambda d:None if d.page_content=='withdrawn' else d)
    # The global no-provider fixture replaces search; use its original wrapped
    # implementation saved before that fixture is applied at test execution.
    results=REAL_SEARCH('query','java')
    assert [d.page_content for d in results]==['valid']
    assert filters==[{'$and':[{'language':'java'},{'subject':'java'},{'contains_answer':False}]}]


REAL_SEARCH=semantic.search


def test_concurrent_store_open_is_serialized(tmp_path,monkeypatch):
    path=tmp_path/'index.json';path.write_text(json.dumps({'collection':'test','model':semantic.MODEL}))
    monkeypatch.setattr(semantic,'MANIFEST',path)
    monkeypatch.setattr(semantic.settings,'vector_store','chroma')
    state={'active':0,'peak':0};lock=Lock()
    def factory(*args):
        with lock:
            state['active']+=1;state['peak']=max(state['peak'],state['active'])
        sleep(.01)
        with lock:state['active']-=1
        return SimpleNamespace(similarity_search=lambda *a,**k:[])
    monkeypatch.setattr(semantic,'_store',factory)
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert list(pool.map(lambda _:REAL_SEARCH('query','java'),range(8)))==[[]]*8
    assert state['peak']==1
