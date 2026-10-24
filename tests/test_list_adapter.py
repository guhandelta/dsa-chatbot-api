"""Linked-list adapter output per language, plus an end-to-end run of the reference."""
import re

import pytest

from app.services import content_catalog
from app.services.code_runner import available_languages, run_suite
from app.services.list_adapter import ADAPTER_FN, SUPPORTED, adapt

NEW_LANGS = ['typescript', 'cpp', 'c', 'rust', 'go', 'csharp', 'ruby']

# language -> (node type marker, helper signature fragment)
MARKERS = {
    'typescript': ('class ListNode', 'function _practiceLinkedList(values: number[]): number[]'),
    'cpp': ('struct ListNode', 'std::vector<long long> _practiceLinkedList(std::vector<long long> values)'),
    'c': ('struct ListNode', 'long long* _practiceLinkedList(long long* values, int valuesSize, int* returnSize)'),
    'rust': ('pub struct ListNode', 'fn _practiceLinkedList(values: Vec<i64>) -> Vec<i64>'),
    'go': ('type ListNode struct', 'func _practiceLinkedList(values []int) []int'),
    'csharp': ('public class ListNode', 'public static long[] _practiceLinkedList(long[] values)'),
    'ruby': ('class ListNode', 'def _practiceLinkedList(values)'),
}


_HEADING = {'typescript': 'TypeScript', 'cpp': 'C\\+\\+', 'c': 'C', 'rust': 'Rust', 'go': 'Go',
            'csharp': 'C#', 'ruby': 'Ruby'}


def _reference(lang):
    """The problem file's own reference block (reference_solution() only knows some languages)."""
    path = content_catalog.find_path('reverse-linked-list')
    m = re.search(rf'^### {_HEADING[lang]}\s*\n```{lang}\n(.*?)```', path.read_text(), re.S | re.M)
    return m.group(1)


def _fn(lang):
    return content_catalog.load_test_cases('reverse-linked-list')[2][lang]


@pytest.mark.parametrize('lang', NEW_LANGS)
def test_adapter_adds_node_type_and_helper(lang):
    code, name = adapt(lang, _reference(lang), _fn(lang))
    node, sig = MARKERS[lang]
    assert name == ADAPTER_FN and lang in SUPPORTED
    assert node in code and sig in code
    assert _fn(lang) + '(head)' in code          # the helper calls the student's entry point
    assert '100000' in code and 'Invalid output list' in code


@pytest.mark.parametrize('lang,own', [
    ('typescript', 'class ListNode { constructor(public val: number, public next: ListNode | null) {} }'),
    ('cpp', 'struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(nullptr) {} };'),
    ('c', 'struct ListNode { int val; struct ListNode* next; };'),
    ('rust', 'pub struct ListNode { pub val: i32, pub next: Option<Box<ListNode>> }\nimpl ListNode { pub fn new(val: i32) -> Self { ListNode { val, next: None } } }'),
    ('go', 'type ListNode struct { Val int; Next *ListNode }'),
    ('csharp', 'public class ListNode { public int val; public ListNode? next; public ListNode(int val = 0, ListNode? next = null) { this.val = val; this.next = next; } }'),
    ('ruby', 'class ListNode\n  attr_accessor :val, :next\n  def initialize(v = 0, n = nil); @val = v; @next = n; end\nend'),
])
def test_students_own_node_type_is_kept(lang, own):
    code, _ = adapt(lang, own + '\n' + _reference(lang), _fn(lang))
    assert len(re.findall(r'\b(?:class|struct|type)\s+ListNode\s*(?:\{|struct\b|$)', code, re.M)) == 1


def test_rust_helper_follows_impl_solution_form():
    code, _ = adapt('rust', 'impl Solution { pub fn reverse_list(h: Option<Box<ListNode>>) -> Option<Box<ListNode>> { h } }', 'reverse_list')
    assert 'impl Solution {\n    pub fn _practiceLinkedList' in code and 'Self::reverse_list(head)' in code


def test_unsupported_language_still_rejected():
    with pytest.raises(ValueError):
        adapt('perl', '', 'f')


@pytest.mark.parametrize('lang', NEW_LANGS)
def test_reference_runs_end_to_end(lang):
    if not available_languages().get(lang):
        pytest.skip(f'{lang} toolchain not installed')
    cases, expected, names, mode = content_catalog.load_test_cases('reverse-linked-list')
    result = run_suite({lang: _reference(lang)}, names, cases, expected, mode)['results'][0]
    assert (result['tier'], result['status'], result['passed_cases']) == (1, 'passed', len(cases)), result


@pytest.mark.parametrize('lang,code', [
    ('typescript', 'function reverseList(head: ListNode | null): ListNode | null { return head; }'),
    ('cpp', 'ListNode* reverse_list(ListNode* head) { return head; }'),
    ('c', 'struct ListNode* reverse_list(struct ListNode* head) { return head; }'),
    ('rust', 'pub fn reverse_list(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> { head }'),
    ('go', 'func reverseList(head *ListNode) *ListNode { return head }'),
    ('csharp', 'public static ListNode? ReverseList(ListNode? head) { return head; }'),
    ('ruby', 'def reverse_list(head); head; end'),
])
def test_identity_solution_fails_node_logic(lang, code):
    if not available_languages().get(lang):
        pytest.skip(f'{lang} toolchain not installed')
    cases, expected, names, mode = content_catalog.load_test_cases('reverse-linked-list')
    assert run_suite({lang: code}, names, cases, expected, mode)['results'][0]['status'] == 'failed'
