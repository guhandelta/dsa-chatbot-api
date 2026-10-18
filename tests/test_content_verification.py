"""Reject unverifiable references before spending credits or teaching from them."""
import pytest

from app.services import content_catalog, training_pipeline
from app.services.code_runner import run_suite
from app.services.content_verification import fixture_errors, verify_reference


@pytest.mark.parametrize('pid,lang', [('reverse-linked-list','javascript'),('reverse-linked-list','java'),
                                    ('word-break','java'),('reverse-bits','java'),('number-of-1-bits','java')])
def test_previously_incomplete_references_execute(pid, lang):
    result = verify_reference(pid, lang)
    assert result['verified'], result
    assert result['case_count'] >= 6


@pytest.mark.parametrize('lang,code', [
    ('javascript','function reverseList(head){return head;}'),
    ('java','public ListNode reverseList(ListNode head){return head;}'),
    ('python','def reverse_list(head): return head'),
])
def test_list_adapter_tests_node_logic_not_just_serialization(lang, code):
    cases, expected, names, mode = content_catalog.load_test_cases('reverse-linked-list')
    result = run_suite({lang: code}, names, cases, expected, mode)
    assert not result['can_publish']
    assert result['results'][0]['status'] == 'failed'


def test_python_list_reference_executes():
    reference = content_catalog.reference_solution('reverse-linked-list', 'python')
    cases, expected, names, mode = content_catalog.load_test_cases('reverse-linked-list')
    assert run_suite({'python':reference[0]}, names, cases, expected, mode)['can_publish']


def test_repeated_fixtures_are_not_sufficient_coverage():
    assert fixture_errors([[1]]*6, [2]*6)
    assert fixture_errors([[float('nan')]], [0])


def test_empty_suite_and_unknown_language_cannot_publish():
    assert not run_suite({'python':'def f(): return 0'}, {'python':'f'}, [], [])['can_publish']
    assert not run_suite({'unknown':'code'}, {}, [[1]], [1])['can_publish']


def test_missing_and_duplicate_publication_languages_are_rejected():
    from types import SimpleNamespace
    from app.services.training import SolutionOut, TestCase
    solution = SolutionOut(language='javascript', function_name='doubleValue',
        code='function doubleValue(x){return x*2;}', explanation='Multiply.', was_supplied=False)
    for solutions in ([solution], [solution,solution]):
        problem = SimpleNamespace(solutions=solutions,
                    test_cases=[TestCase(args=[i],expected=i*2) for i in range(6)])
        report = training_pipeline._validate(problem)
        assert not report['can_publish'] and report['validation_errors']


async def test_failed_reference_preflight_does_not_charge_or_call_provider(client, monkeypatch, subscribe_user):
    r = await client.post('/auth/register',json={'email':'blocked-reference@example.com','password':'password123'})
    await subscribe_user(r.json()['user']['id'], 'java')
    headers = {'Authorization':'Bearer '+r.json()['access_token']}
    before = r.json()['user']['peppercorns']
    monkeypatch.setattr('app.services.content_verification.verify_reference',
                        lambda *args: {'verified':False,'issues':['Reference failed']})
    async def forbidden(**kwargs): raise AssertionError('Provider must not be called')
    monkeypatch.setattr('app.routers.analyze.deep_review',forbidden)
    response = await client.post('/analyze/',headers=headers,json={'problem_id':'two-sum',
                            'language':'java','user_code':'public int[] twoSum(int[] n,int t){return n;}'})
    assert response.status_code == 422
    assert (await client.get('/auth/me',headers=headers)).json()['peppercorns'] == before
    response = await client.post('/practice/sessions',headers=headers,json={'problem_id':'two-sum','language':'java'})
    assert response.status_code == 422


async def test_index_failure_does_not_publish_file(tmp_path, monkeypatch):
    from types import SimpleNamespace
    async def enrich(*args):
        return SimpleNamespace(issues_found=[],solutions=[],test_cases=[])
    monkeypatch.setattr(training_pipeline.training,'enrich_problem',enrich)
    monkeypatch.setattr(training_pipeline,'_validate',lambda p: {'can_publish':True,
        'agreement_detail':'agree','results':[],'unverified':[]})
    monkeypatch.setattr(training_pipeline.training,'to_markdown',lambda p:'# unpublished')
    monkeypatch.setattr(training_pipeline,'PROBLEMS_DIR',tmp_path)
    def fail(*args): raise RuntimeError('index unavailable')
    monkeypatch.setattr(training_pipeline,'upsert_problem',fail)
    with pytest.raises(RuntimeError,match='index unavailable'):
        await training_pipeline.run_pipeline('must-not-publish','test',{})
    assert not list(tmp_path.iterdir())


def test_ordered_matrices_and_boolean_return_types_cannot_false_pass():
    from app.services.output_comparison import compare
    assert not compare([[2,1],[4,3]], [[1,2],[3,4]])
    assert not compare(1, True)
    assert not compare([1], [True], 'unordered_flat')
    assert not compare(float('nan'), 0)
    assert compare([1,0], [0,1], 'unordered_flat')
    assert compare([[2,0,-2],[1,0,-1]], [[-1,0,1],[-2,0,2]], 'unordered_nested')


@pytest.mark.parametrize('language,code', [
    ('javascript','function twoSum(n,t){for(let i=0;i<n.length;i++)for(let j=i+1;j<n.length;j++)if(n[i]+n[j]===t)return [j,i];}'),
    ('java','public int[] twoSum(int[] n,int t){for(int i=0;i<n.length;i++)for(int j=i+1;j<n.length;j++)if(n[i]+n[j]==t)return new int[]{j,i};return new int[0];}'),
])
async def test_curated_grader_accepts_valid_reversed_two_sum_indices(language, code):
    from app.services.deep_review import gather_evidence
    result = await gather_evidence('two-sum', code, language)
    assert result['curated']['results'][0]['status'] == 'passed'
