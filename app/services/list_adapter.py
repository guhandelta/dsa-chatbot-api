"""Explicit JSON-array ↔ singly-linked-list adapters for curated list exercises.

The student's function still receives nodes and must return nodes. Serialization
rejects cycles or excessive output rather than silently truncating an invalid list.
"""
import re

ADAPTER_FN = '_practiceLinkedList'


def adapt(language: str, code: str, fn: str) -> tuple[str, str]:
    if language == 'javascript':
        helpers = '''
function ListNode(val, next = null) { this.val = val; this.next = next; }
function _practiceLinkedList(values) {
  let head = null;
  for (let i = values.length-1; i >= 0; i--) head = new ListNode(values[i], head);
  let node = ENTRY(head); const seen = new Set(); const result = [];
  while (node != null) {
    if (seen.has(node) || result.length >= 100000) throw new Error('Invalid output list');
    seen.add(node); result.push(node.val); node = node.next;
  }
  return result;
}
'''.replace('ENTRY', fn)
        return code+'\n'+helpers, ADAPTER_FN
    if language == 'python':
        helpers = '''
class ListNode:
    def __init__(self, val=0, next=None): self.val, self.next = val, next

def _practiceLinkedList(values):
    head = None
    for val in reversed(values): head = ListNode(val, head)
    node = ENTRY(head)
    result, seen = [], set()
    while node is not None:
        if id(node) in seen or len(result) >= 100000: raise ValueError('Invalid output list')
        seen.add(id(node)); result.append(node.val); node = node.next
    return result
'''.replace('ENTRY', fn)
        return helpers.split('def _practiceLinkedList')[0]+code+'\n'+'def _practiceLinkedList'+helpers.split('def _practiceLinkedList',1)[1], ADAPTER_FN
    if language == 'java':
        helper = '''
    public int[] _practiceLinkedList(int[] values) {
        ListNode head = null;
        for (int i = values.length-1; i >= 0; i--) head = new ListNode(values[i], head);
        ListNode node = ENTRY(head);
        java.util.Set<ListNode> seen = java.util.Collections.newSetFromMap(new java.util.IdentityHashMap<>());
        java.util.List<Integer> valuesOut = new java.util.ArrayList<>();
        while (node != null) {
            if (!seen.add(node) || valuesOut.size() >= 100000) throw new IllegalArgumentException("Invalid output list");
            valuesOut.add(node.val); node = node.next;
        }
        return valuesOut.stream().mapToInt(Integer::intValue).toArray();
    }
'''.replace('ENTRY', fn)
        if re.search(r'\bclass\s+Solution\b', code):
            end = code.rfind('}')
            code = code[:end]+helper+code[end:]
        else:
            code = 'import java.util.*;\nclass Solution {\n'+code+helper+'\n}'
        if not re.search(r'\bclass\s+ListNode\b', code):
            code += '\nclass ListNode { int val; ListNode next; ListNode(int v, ListNode n) {val=v;next=n;} }'
        return code, ADAPTER_FN
    raise ValueError(f'Linked-list execution is unsupported for {language}')
