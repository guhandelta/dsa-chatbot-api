"""Explicit JSON-array ↔ singly-linked-list adapters for curated list exercises.

The student's function still receives nodes and must return nodes. Serialization
rejects cycles or excessive output rather than silently truncating an invalid list.
"""
import re

ADAPTER_FN = '_practiceLinkedList'

# Languages with an adapter (kept in sync with the branches of adapt()).
SUPPORTED = ('python', 'javascript', 'java', 'typescript', 'cpp', 'c', 'rust', 'go', 'csharp', 'ruby')


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
    if language == 'typescript':
        # Harness: tsc --strict, calls fn(number[]) and JSON-serialises the result,
        # so the helper is a plain number[] -> number[] function. The list is built
        # with object literals so it works whether the student's ListNode is a
        # class, interface or type alias with val/next.
        node = '' if re.search(r'\b(class|interface|type)\s+ListNode\b', code) else '''
class ListNode {
  val: number; next: ListNode | null;
  constructor(val: number = 0, next: ListNode | null = null) { this.val = val; this.next = next; }
}
'''
        helper = '''
function _practiceLinkedList(values: number[]): number[] {
  let head: ListNode | null = null;
  for (let i = values.length - 1; i >= 0; i--) head = { val: values[i], next: head };
  let node: ListNode | null = ENTRY(head);
  const seen = new Set<ListNode>(); const result: number[] = [];
  while (node !== null) {
    if (seen.has(node) || result.length >= 100000) throw new Error('Invalid output list');
    seen.add(node); result.push(node.val); node = node.next;
  }
  return result;
}
'''.replace('ENTRY', fn)
        return node + code + '\n' + helper, ADAPTER_FN
    if language == 'cpp':
        # Harness tries 64-bit first: int[] is std::vector<long long> (narrow would be
        # std::vector<int>). The student code never touches the element type, so the
        # wide candidate always compiles and is the one used. The harness prelude has
        # no `using namespace std`, so every library name is qualified.
        node = '' if re.search(r'\b(struct|class)\s+ListNode\b', code) else '''
struct ListNode {
    long long val; ListNode* next;
    ListNode(long long v = 0, ListNode* n = nullptr) : val(v), next(n) {}
};
'''
        helper = '''
#include <stdexcept>
#include <unordered_set>
std::vector<long long> _practiceLinkedList(std::vector<long long> values) {
    ListNode* head = nullptr;
    for (size_t i = values.size(); i-- > 0;) { ListNode* n = new ListNode(0); n->val = values[i]; n->next = head; head = n; }
    ListNode* node = ENTRY(head);
    std::unordered_set<ListNode*> seen; std::vector<long long> result;
    while (node != nullptr) {
        if (!seen.insert(node).second || result.size() >= 100000) throw std::runtime_error("Invalid output list");
        result.push_back(node->val); node = node->next;
    }
    return result;
}
'''.replace('ENTRY', fn)
        return node + code + '\n' + helper, ADAPTER_FN
    if language == 'c':
        # Harness convention (render_c): an int[] argument expands to (ptr, size) and an
        # int[] return adds a trailing `int* returnSize`; wide candidate => long long.
        # A bad list has no exception in C, so the helper prints to stderr and exits
        # non-zero, which the runner reports as a crash. Cycle guard: a pointer that
        # advances every other step must never meet the walker; plus the node limit.
        node = '' if re.search(r'\bstruct\s+ListNode\s*\{', code) else '''
struct ListNode { long long val; struct ListNode* next; };
'''
        helper = '''
long long* _practiceLinkedList(long long* values, int valuesSize, int* returnSize) {
    struct ListNode* head = NULL;
    for (int i = valuesSize - 1; i >= 0; i--) {
        struct ListNode* n = (struct ListNode*)malloc(sizeof(struct ListNode));
        n->val = values[i]; n->next = head; head = n;
    }
    struct ListNode* node = ENTRY(head);
    long long count = 0; struct ListNode* p = node; struct ListNode* slow = node;
    while (p != NULL) {
        if (++count > 100000) { fprintf(stderr, "Invalid output list\\n"); exit(1); }
        p = p->next;
        if (count % 2 == 0) slow = slow->next;
        if (p != NULL && p == slow) { fprintf(stderr, "Invalid output list\\n"); exit(1); }
    }
    long long* result = (long long*)malloc(sizeof(long long) * (count > 0 ? count : 1));
    long long k = 0;
    for (p = node; p != NULL; p = p->next) result[k++] = p->val;
    *returnSize = (int)count;
    return result;
}
'''.replace('ENTRY', fn)
        return node + code + '\n' + helper, ADAPTER_FN
    if language == 'rust':
        # Harness: int[] is Vec<i64> (wide, tried first; i32 only if wide fails to
        # compile). The student's entry point is either a bare fn or inside
        # `impl Solution`, and the harness calls the helper the same way, so the helper
        # is placed in the matching form. `as _` lets a student-defined ListNode use
        # any integer width for val.
        node = '' if re.search(r'\bstruct\s+ListNode\b', code) else '''
#[derive(Debug)]
pub struct ListNode { pub val: i64, pub next: Option<Box<ListNode>> }
impl ListNode { pub fn new(val: i64) -> Self { ListNode { val, next: None } } }
'''
        body = '''(values: Vec<i64>) -> Vec<i64> {
        let mut head: Option<Box<ListNode>> = None;
        for &v in values.iter().rev() {
            let mut n = Box::new(ListNode::new(0)); n.val = v as _; n.next = head; head = Some(n);
        }
        let list = CALL(head);
        let mut seen = std::collections::HashSet::new(); let mut result: Vec<i64> = Vec::new();
        let mut cur = list.as_deref();
        while let Some(n) = cur {
            if !seen.insert(n as *const ListNode as usize) || result.len() >= 100000 { panic!("Invalid output list"); }
            result.push(n.val as i64); cur = n.next.as_deref();
        }
        result
    }
'''
        if re.search(r'\bimpl\s+Solution\b', code):
            helper = '\nimpl Solution {\n    pub fn _practiceLinkedList' + body.replace('CALL', 'Self::' + fn) + '}\n'
        else:
            helper = '\npub fn _practiceLinkedList' + body.replace('CALL', fn).replace('\n    ', '\n')
        return node + code + '\n' + helper, ADAPTER_FN
    if language == 'go':
        # Harness: an int[] argument/return is []int (the only Go candidate for slices).
        # Field names Val/Next are the exported Go spelling the reference uses. The
        # helper is an unexported package-level func, which main.go can call.
        node = '' if re.search(r'\btype\s+ListNode\b', code) else '''
type ListNode struct {
	Val  int
	Next *ListNode
}
'''
        helper = '''
func _practiceLinkedList(values []int) []int {
	var head *ListNode
	for i := len(values) - 1; i >= 0; i-- {
		head = &ListNode{Val: values[i], Next: head}
	}
	node := ENTRY(head)
	seen := map[*ListNode]bool{}
	result := []int{}
	for node != nil {
		if seen[node] || len(result) >= 100000 {
			panic("Invalid output list")
		}
		seen[node] = true
		result = append(result, node.Val)
		node = node.Next
	}
	return result
}
'''.replace('ENTRY', fn)
        return node + code + '\n' + helper, ADAPTER_FN
    if language == 'csharp':
        # Harness: Solution.<fn>(long[]) -> long[] (wide, tried first; int[] is the narrow
        # fallback). The harness calls Solution.<fn>, so the helper is a public static
        # member of the Solution class (created here when the code has none) and
        # ListNode is a top-level class beside it. Nullable context is enabled.
        helper = '''
    public static long[] _practiceLinkedList(long[] values) {
        ListNode? head = null;
        for (int i = values.Length - 1; i >= 0; i--) head = new ListNode(values[i], head);
        ListNode? node = ENTRY(head);
        var seen = new System.Collections.Generic.HashSet<ListNode>();
        var result = new System.Collections.Generic.List<long>();
        while (node != null) {
            if (!seen.Add(node) || result.Count >= 100000) throw new System.InvalidOperationException("Invalid output list");
            result.Add(node.val); node = node.next;
        }
        return result.ToArray();
    }
'''.replace('ENTRY', fn)
        if re.search(r'\bclass\s+Solution\b', code):
            end = code.rfind('}')
            code = code[:end] + helper + code[end:]
        else:
            code = 'public static class Solution {\n' + code + helper + '\n}'
        if not re.search(r'\bclass\s+ListNode\b', code):
            code += '\npublic class ListNode {\n    public long val; public ListNode? next;\n    public ListNode(long val = 0, ListNode? next = null) { this.val = val; this.next = next; }\n}\n'
        return code, ADAPTER_FN
    if language == 'ruby':
        # Harness: Ruby receives each case's args as plain JSON data (an Array of
        # Integers) and JSON-serialises the return value, so the helper takes and
        # returns a plain Array. Top-level methods are callable from the harness.
        node = '' if re.search(r'\bclass\s+ListNode\b', code) else '''
class ListNode
  attr_accessor :val, :next
  def initialize(val = 0, nxt = nil)
    @val = val
    @next = nxt
  end
end
'''
        helper = '''
def _practiceLinkedList(values)
  head = nil
  values.reverse_each { |v| head = ListNode.new(v, head) }
  node = ENTRY(head)
  seen = {}.compare_by_identity
  result = []
  while node
    raise 'Invalid output list' if seen.key?(node) || result.length >= 100000
    seen[node] = true
    result << node.val
    node = node.next
  end
  result
end
'''.replace('ENTRY', fn)
        return node + code + '\n' + helper, ADAPTER_FN
    raise ValueError(f'Linked-list execution is unsupported for {language}')
