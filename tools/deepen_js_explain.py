"""Publish a static, authored JavaScript practice ladder. No models or network calls."""
import json
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / 'data/explain/javascript.json'

# Rows are distinct teaching tasks, not randomized copies of a problem statement.
BASIC = {
'arrays': [
 'Start with values = [2, 4]. Trace values.push(6), values.pop(), then values[0] = 9. Write the array contents and each expression’s result separately after every step.',
 'Compare [0, false, "", null] filtered by truthiness with a filter that removes only null. Explain which contract each filter satisfies.',
 'Implement countAbove for finite numeric readings and a threshold. Count strictly greater values; include empty input and values equal to the threshold.',
 'Return a new array with one valid index replaced, leaving the input unchanged. Explain what is and is not copied if an element is itself an object.',
 'Specify an index-replacement contract that throws RangeError for non-integer or out-of-range indices. Test -1, length, fractional indices and an empty array.',
 'Remove only null entries while retaining 0, false and empty strings in their original order. Explain why the choice of predicate matters.',
 'Find the longest consecutive run of readings strictly above a threshold. Empty input returns 0 and an equal reading breaks the run. Trace [2, 8, 9, 1, 7] with threshold 5.',
 'Rotate a dense array right by nonnegative integer k without mutating it. Define empty-input behavior and support k larger than the array length.',
 'A function does const copy = values; copy.push(7), but promises not to change values. Diagnose the violated contract and propose a test that checks the original input.',
 'Compare filter followed by map with one traversal producing the same output. Count inspected elements and intermediate collections; explain a readability trade-off.',
 'Find the second-largest distinct finite number without sorting. Return null if fewer than two distinct numbers exist. Explain your maintained state for duplicates and negative values.',
 'Without notes, revisit ordered readings with a changed contract: return the second-smallest distinct value, or null if absent. Explain how the earlier invariant must change; this is deliberate review.',
],
'strings': [
 'Start with text = "  Cat  ". Trace text.trim().toLowerCase().slice(0, 2), showing the value after each call. State whether the original text changes.',
 'Compare the length and iteration count of a string containing an emoji. Distinguish UTF-16 code units from code points and visible graphemes without treating them as interchangeable.',
 'For ASCII-only input, count occurrences of one specified character. State whether case matters, and test empty text, no match and repeated matches.',
 'Return an ASCII string with only leading and trailing spaces removed while preserving internal spacing. Explain how this differs from removing every space.',
 'Design a first-match contract returning -1 if a nonempty literal fragment is absent. Test empty text, a match at index 0 and repeated fragments.',
 'Validate a nonempty ASCII identifier under the explicit rule: letters first, then letters or digits. Explain why accepting a prefix does not validate the whole string.',
 'Normalize an ASCII search phrase by trimming, lowercasing and collapsing internal runs of spaces to one. Preserve the original and specify the all-space case.',
 'Truncate a title by a stated code-point limit rather than a code-unit limit. Explain what still needs a separate policy for combining marks and grapheme clusters.',
 'A helper loops over text[i] and calls each item a complete character. Diagnose which declared text contracts make that assumption unsafe and propose a revealing input.',
 'Compare repeatedly concatenating one character with collecting pieces and joining. Explain the observable equivalence and avoid claiming a universal engine-specific performance guarantee.',
 'For an ASCII string, report the longest run of the same character and its length; choose the earliest on ties and return null for empty input. Explain the reset rule.',
 'Review the earlier normalization task with a new requirement: preserve original capitalization for display while keeping a separate normalized search value. State which value each comparison uses.',
],
'objects': [
 'Start with record = { points: 0 }, alias = record and copy = { ...record }. Trace alias.points += 1, then copy.points += 2. State each value and which variables refer to the same object.',
 'Compare a missing property with one explicitly set to undefined, and compare || with ??. Explain which observations distinguish absence from a falsy value.',
 'Create an updated settings record from a patch without mutating the original. Only allow known keys and retain explicit false, 0 and empty-string values.',
 'Project a record to a small allowed list of fields, returning a new record. Define whether missing source properties are omitted or included as undefined.',
 'Define validation for a plain input record with a required nonempty name and nonnegative finite score. State the handling of null, arrays and unexpected properties.',
 'Explain a duplicate-field update policy and the difference between deleting a property and assigning undefined. Write examples under each contract.',
 'Implement a state transition from a valid ticket record to another valid ticket state. Reject unsupported transitions and preserve the original record.',
 'Update a nested contact address while keeping the original address independent. Identify every level that must be copied under this contract.',
 'A shallow-copied profile and its original share the same preferences object. Diagnose why editing a nested flag changes both and propose a regression test.',
 'Compare a fixed-shape record with an arbitrary-key Map for storing user-defined labels. Explain the data model, missing-key handling and identity assumptions before choosing.',
 'Given a finite numeric price record, compute a new validated quote with a discount and surcharge. Specify rounding, allowed ranges and the failure contract before coding.',
 'Review record updates with an explicit undo requirement. Explain what history must preserve and why storing the same mutable reference repeatedly is insufficient.',
],
'maps': [
 'Start with new Map([["a", 1]]). Trace set("b", 2), set("a", 3), has("b"), delete("b") and get("b"). Distinguish each result, the remaining entries and ordinary object properties.',
 'Use two separately created object keys with equal fields. Predict which lookups succeed, then contrast object identity with using a stable string identifier.',
 'Count visits per ASCII page key using Map. Start absent keys at zero, preserve existing counts and test an empty input.',
 'Merge two numeric counters under an explicit sum-on-duplicate policy without mutating either input Map. State the output’s iteration order.',
 'Design a lookup result that distinguishes an absent key from a present entry whose value is undefined. Demonstrate both cases.',
 'Validate an update contract that accepts only finite nonnegative counts. Explain what should happen when an update tries to delete a missing key.',
 'Maintain inventory counts under add, reserve and release commands. Reject negative resulting stock and explain which commands leave state unchanged.',
 'Implement a small bounded key/value cache with a stated FIFO eviction policy. State what updating an existing key does to its eviction position; do not silently call it LRU.',
 'A counter writes counts[key] = 1 and then reads counts.get(key). Diagnose the missing entry and specify a regression test.',
 'Compare scanning a list for every lookup with building an index once. Discuss one-time construction, repeated queries and consistency after updates.',
 'Process a stream of key/value updates into final per-key balances under a reject-invalid-command contract. Preserve earlier valid state when a command fails.',
 'Review indexing with a changed duplicate policy: reject duplicate keys instead of overwriting. Explain which earlier assumptions and tests must change.',
],
'sets': [
 'Start with new Set(["a"]). Trace add("a"), add("b"), has("b") and delete("a"), writing the members and size after each operation.',
 'Predict the size of a Set containing two separate objects with identical id fields. Explain identity versus deduplication by a chosen field.',
 'Return the first occurrence of each primitive identifier while preserving input order. State the accepted primitive types and equality contract.',
 'Compute union and intersection of two Sets using loops and existing membership operations, preserving each input.',
 'Specify behavior for empty sets, identical sets and disjoint sets. Author tests that distinguish union, intersection and difference.',
 'Explain why turning records into a Set does not enforce uniqueness of their id field. Describe a stable-key contract without silently changing equality.',
 'Reconcile current and requested permissions into additions and removals. Keep each set independent and define the behavior of an unchanged permission.',
 'Design a case-insensitive ASCII tag collection that preserves a chosen display spelling. Specify how normalization affects lookup and duplicates.',
 'Two groups accidentally reference the same Set, so adding a member to one changes both. Diagnose the shared-state defect and design a test for independence.',
 'Compare a Set with an array when order, duplicate counts and membership queries each matter. Explain information lost by converting representations.',
 'Given allowed and submitted identifiers, produce valid unique submissions and rejected identifiers under an explicit duplicate-reporting policy.',
 'Review permissions reconciliation with an explicit protected-permission rule. Explain how the earlier difference operation must be constrained.',
],
'stacks': [
 'Starting from an empty array-backed stack, trace push("a"), push("b"), pop(), pop() and pop(). State the top, result and remaining contents after each operation, including the empty pop.',
 'Contrast LIFO and FIFO by tracing the same three input actions. Explain which behavior represents undo and which represents a waiting line.',
 'Implement a stack wrapper with push, pop, peek and size. Choose and document one empty-result contract for pop and peek.',
 'Implement an independent stack snapshot. State whether the contract copies only the outer collection or also mutable stored values.',
 'Test empty, one-item and repeated-value stacks. Explain why duplicate values do not make distinct pushes one operation.',
 'Define a capacity-limited stack that rejects a push at capacity without changing prior state. State the zero-capacity and invalid-capacity contracts.',
 'Model undo and redo with two stacks. A fresh edit clears redo history. Trace edits, two undos, one redo and a new edit.',
 'Support grouped edits as one undo action. Explain what data the group must capture and how a partial failed edit should behave.',
 'An undo history repeatedly stores one mutable record, so every snapshot shows the latest value. Diagnose why the stack order can be correct while history is wrong.',
 'Compare an explicit stack with recursive processing at the level of represented pending work. State which input-depth assumptions matter without promising unlimited recursion.',
 'Process a command sequence supporting push, pop and peek under an explicit invalid-command policy. Preserve order and explain each empty-state transition.',
 'Review undo with a changed requirement: redo only survives navigation, not a new edit. Design a minimal trace that proves the distinction.',
],
'queues': [
 'Starting from an empty FIFO queue, trace enqueue("a"), enqueue("b"), dequeue(), enqueue("c") and peek(). Write the head and pending order after every operation and declare the peek contract.',
 'Trace a queue represented by an array and a head index. Distinguish logical pending length from allocated backing-array length.',
 'Implement a FIFO wrapper with an explicit empty-result contract and a pending-count operation.',
 'Implement a head-index queue and explain when consumed storage can be reclaimed without changing pending order.',
 'Test empty, one-item and repeated-value queues. Demonstrate that a newly enqueued value does not jump ahead of older work.',
 'Specify a bounded queue that rejects overflow without losing pending work. Explain how capacity and empty behavior interact.',
 'Simulate a service desk processing at most two waiting requests per tick. New arrivals go to the tail; define within-tick arrival order.',
 'Design a round-robin queue for unfinished jobs. State when a job is re-enqueued and how completed jobs leave the system.',
 'A queue computes size from backingArray.length after advancing head. Diagnose the incorrect pending count and propose a revealing test.',
 'Compare repeatedly removing the first array element with advancing a head index. Discuss bookkeeping and retained storage under a stated collection cost model.',
 'Process enqueue, serve and cancel-oldest commands. Define all empty cases, preserve FIFO order and explain a trace with duplicate-valued jobs.',
 'Review the service desk with cancellations by stable identifier. Explain why efficient cancellation introduces a new representation decision and belongs in a composition unit.',
],
'linked-lists': [
 'Draw a three-node chain and trace value and next references. Distinguish a node’s identity from the value it stores.',
 'Draw two references to the same tail and predict which observations change after editing that tail’s value.',
 'Count nodes in an acyclic singly linked list. Empty input returns zero; state the acyclic precondition explicitly.',
 'Prepend one new node without losing the old head. State whether existing nodes are reused and whether the input head node is mutated.',
 'Define removal of the first matching value, including empty input, no match and head removal. State the mutation contract.',
 'Explain what changes when duplicates are allowed and only the first match may be removed. Author a trace that distinguishes removing one from removing every match.',
 'Append to a list that keeps both head and tail references. Define how both change for empty and one-node states.',
 'Design a list snapshot with fresh nodes rather than copied head references. State whether node values themselves are copied.',
 'A removal overwrites current.next before preserving the rest of the chain. Diagnose the lost-reference risk using a small drawing and a regression test.',
 'Compare indexed array access with following next references. Explain which operations need traversal and which require an already-known node.',
 'Split an acyclic chain after a specified count under a contract that reuses nodes. Preserve both resulting chains and explain the zero and beyond-length cases.',
 'Review append with an explicit delete-last requirement. Explain the additional information or traversal needed to maintain head/tail invariants.',
],
}

# Extra combinations have authored models, correct examples, and specific contracts.
EXTRA = [
 ('maps-arrays','Map with Arrays',['maps','arrays'],
  'Group records by key while preserving event order and independent per-key collections.',
  'The Map chooses a group; each array preserves that group’s event order. Define a group’s lifetime and the order of updates.',
  'const groups = new Map([["web", ["open"]]]);\ngroups.get("web").push("save");\nconsole.log(JSON.stringify([...groups]));', '[["web",["open","save"]]]',
  'Group timestamped events by a validated owner key, preserving input order within groups. Specify missing keys, empty input and whether output arrays share input records.',
  'Reusing one array for every group makes later appends affect unrelated groups.',
  'Separate grouping from the later algorithm; grouping/indexing can prepare independent DSA practice.'),
 ('arrays-sets','Arrays with Set',['arrays','sets'],
  'Reconcile ordered identifiers against membership rules without losing the intended order or duplicate policy.',
  'The array carries sequence; the Set answers membership. Converting between them can lose duplicate information.',
  'const requested = ["b", "a", "b"];\nconst allowed = new Set(["a"]);\nconsole.log(JSON.stringify(requested.filter(id => allowed.has(id))));', '["a"]',
  'Reconcile requested and current identifiers into additions and removals. Preserve requested order for additions and define whether duplicates are reported or ignored.',
  'A membership filter alone does not deduplicate repeated allowed identifiers.',
  'Explain the visited/seen invariant before using membership to avoid repeated scans.'),
 ('strings-maps','Strings with Map',['strings','maps'],
  'Count tokens under a declared normalization and character contract.',
  'The text contract defines tokens; the Map records their counts. Normalization and identity are separate decisions.',
  'const counts = new Map();\nfor (const letter of "aba") counts.set(letter, (counts.get(letter) ?? 0) + 1);\nconsole.log(JSON.stringify([...counts]));', '[["a",2],["b",1]]',
  'Count normalized ASCII words in a text input. Declare splitting, case, punctuation and tie rules before returning the most frequent word.',
  'A character-frequency map and a word-frequency map answer different questions; normalization must be explicit.',
  'Use frequency invariants as preparation for matching and anagram-style problems.'),
 ('strings-sets','Strings with Set',['strings','sets'],
  'Validate vocabulary and uniqueness while stating which text units are compared.',
  'The text parser supplies tokens; the Set records allowed or observed tokens without storing their frequencies.',
  'const vocabulary = new Set(["red", "blue"]);\nconst tokens = "red green red".split(" ");\nconsole.log(JSON.stringify(tokens.filter(token => !vocabulary.has(token))));', '["green"]',
  'Report unknown normalized ASCII words against an allowed vocabulary. Choose first-occurrence order versus occurrence-by-occurrence reporting.',
  'Set membership discards frequency information; repeated invalid words need a separate reporting contract.',
  'Contrast membership with counts before selecting a structure for a new text problem.'),
 ('nested-maps','Nested Maps',['maps'],
  'Design a two-level lookup whose nesting order matches the queries and update lifecycle.',
  'An outer key selects an inner index. Region-first and product-first representations support different direct queries.',
  'const stock = new Map([["west", new Map([["book", 3]])]]);\nconsole.log(stock.get("west").get("book"));', '3',
  'Maintain stock by region and product. Define absent pairs, duplicate updates and whether empty inner Maps remain after removing the last product.',
  'Creating or sharing one inner Map can join states that should be independent.',
  'Model multi-key state carefully before optimizing query cost or adding algorithmic constraints.'),
 ('stacks-strings','Stacks with Strings',['stacks','strings'],
  'Trace restricted delimiter nesting with a declared token contract.',
  'Each opening delimiter represents pending work. A closing token must satisfy the current nesting contract.',
  'const pending = [];\nfor (const token of "((") pending.push(token);\nconsole.log(pending.length);', '2',
  'Validate only parentheses in an ASCII text under a stated ignore-other-characters rule. Then specify what would change for several delimiter types and quoted literals.',
  'A delimiter scanner is not automatically a full language parser; quotes and escapes require their own token rules.',
  'The stack invariant connects nested structures to later parsing and traversal work.'),
 ('queues-maps','Queues with Map',['queues','maps'],
  'Maintain pending order and identifier lookup under cancellation and repeated updates.',
  'The queue defines service order; the Map identifies current jobs. Both representations must agree on the meaning of pending.',
  'const order = ["a", "b"];\nconst jobs = new Map([["a", { status: "pending" }], ["b", { status: "done" }]]);\nconsole.log(JSON.stringify(order.filter(id => jobs.get(id).status === "pending")));', '["a"]',
  'Design enqueue, cancel and serve commands for uniquely identified jobs. Specify repeated IDs, cancelled queue entries and whether re-enqueued IDs reuse an old position.',
  'An entry can remain in queue storage after its lookup record changes; stale entries need an explicit lifecycle policy.',
  'State consistency and amortized cleanup matter before choosing a more advanced scheduling algorithm.'),
 ('record-index','Arrays, Objects and Map',['arrays-objects','objects-map'],
  'Build a small editable record collection with one authoritative representation and an index.',
  'Choose which representation owns the truth. Every accepted edit must preserve record identity, ordering and index consistency.',
  'const records = [{ id: "a", points: 0 }];\nconst byId = new Map(records.map(record => [record.id, record]));\nbyId.get("a").points += 1;\nconsole.log(records[0].points);', '1',
  'Build a bounded record-store model supporting create, rename, update and delete. Define duplicate IDs, ordering, aliasing and failed-command behavior; demonstrate consistency after each command.',
  'Updating one representation while forgetting the other creates a convincing but inconsistent result.',
  'Use this as a small composition capstone before tackling larger independent DSA or application projects.'),
]

COMBINED = {
'arrays-strings': [
 'Trace trimming, lowercasing and filtering of [" Ada ", "", "BO"]. State which transformation changes membership versus spelling.',
 'Build an ordered text-cleaning pipeline under explicit ASCII, empty-string and duplicate rules. Preserve the original list and original display spellings.',
 'Extend a text group with a new normalized word. Define whether duplicates are kept and demonstrate that one group’s changes cannot change another’s contents.',
 'Compare an array of display strings with a keyed grouping representation. Choose one for ordered display and one for repeated group lookup, explaining the extra structure’s prerequisite.',
],
'strings-objects': [
 'Trace valid JSON text representing null, an array and a record. Explain why successful parsing alone does not establish the required record shape.',
 'Design a text-to-profile import requiring name and a nonnegative finite visit count. Define malformed text, missing fields and unexpected-property handling.',
 'Apply a validated text patch to a profile without losing valid 0 and false values or partially applying a rejected patch.',
 'Compare storing raw input text, parsed values and validated records. Explain which form is appropriate for error messages, editing and trusted application use.',
],
'objects-map': [
 'Trace two Map entries referring to records, including two separate records with equal IDs. Distinguish identifier equality from object identity.',
 'Build an index by validated record ID with an explicit reject-or-overwrite duplicate policy and no silent loss of the earlier record.',
 'Update and remove an indexed record. Define whether another reference sees the update and how the index behaves when an identifier changes.',
 'Compare repeated record scans with a reusable index. Explain the consistency work required when records can be edited.',
],
'arrays-objects': [
 'Trace filter and map over order records. Draw the outer arrays and identify which resulting records still share references.',
 'Summarize validated orders by a stated rule, preserving source records and correctly handling no orders, zero totals and repeated customers.',
 'Update one selected record and its nested address without changing other records or the original nested address under an immutable-update contract.',
 'Compare an array of records with parallel arrays of fields. Explain how insertions or deletions can preserve or break relationships.',
],
'maps-sets': [
 'Trace membership updates for two groups and show why each group must own a separate Set.',
 'Build unique group memberships from validated owner/member pairs. State duplicate-pair and missing-owner behavior.',
 'Remove a member and then the last member of a group. Choose whether empty groups remain and preserve independence of other groups.',
 'Compare a Map of Sets with a flat list of relationship pairs. Explain membership lookup, duplicate rules and iteration needs.',
],
'nested-arrays': [
 'Trace row-wise traversal of [[1, 2], [3], []]. Explain which rectangular-grid assumptions would be invalid.',
 'Validate and summarize ragged numeric rows, returning row totals and an overall total without changing input rows.',
 'Update one cell under a nonmutating rectangular-grid contract. Define bounds, empty grids and row independence.',
 'Compare a nested grid with a flat array plus width. Explain shape validation, coordinate mapping and the costs of changing shape.',
],
'maps-arrays': [
 'Trace three interleaved events assigned to two owners. Show each owner’s event order and distinguish it from overall input order.',
 'Build per-owner event histories from validated events, defining duplicate event IDs and whether original event objects may be shared.',
 'Delete an event from one history and append another. Define empty-history retention and verify other owners are unaffected.',
 'Compare owner-first grouping with a single chronological event list. Explain which queries become direct and which require merging or scanning.',
],
'arrays-sets': [
 'Trace membership filtering for a request list containing duplicates. Explain why filtering and deduplication are separate operations.',
 'Compute ordered additions and removals between current and requested IDs, with a documented duplicate and equality policy.',
 'Apply a change batch containing repeated adds and removals. Choose rejection or idempotent handling and preserve the final sequence contract.',
 'Compare keeping only a Set with keeping an ordered array plus a Set. Explain what information each representation loses or must keep synchronized.',
],
'strings-maps': [
 'Trace frequency updates for repeated normalized ASCII tokens. Write the count state after each token.',
 'Implement word counts under explicit splitting, punctuation and case rules. Return a result consistent with an empty-text contract.',
 'Update counts when a text segment is added or removed. Reject a removal that would make a count negative and define zero-count key retention.',
 'Compare a token-frequency Map with a Set of tokens. Explain which questions about repeated words each can and cannot answer.',
],
'strings-sets': [
 'Trace known and unknown vocabulary tokens with repeats. Distinguish per-occurrence errors from unique unknown-token reports.',
 'Produce unique unknown normalized ASCII tokens in first-occurrence order, preserving the original text for display.',
 'Update the allowed vocabulary and reevaluate text. State whether existing reports are snapshots or derived results that must be refreshed.',
 'Compare a vocabulary Set with a frequency Map for spell-check-style feedback. Explain when membership alone is insufficient.',
],
'nested-maps': [
 'Trace queries and updates for region/product stock, distinguishing an absent region, absent product and present zero stock.',
 'Build a validated two-key stock index with explicit behavior for duplicate input pairs and invalid quantities.',
 'Remove a product, remove a region’s last product and move stock between regions. Define atomic failure behavior and inner-Map cleanup.',
 'Compare region-first with product-first nesting under two different query workloads. Explain the cost of maintaining both indexes.',
],
'stacks-strings': [
 'Trace pending delimiters for a short parenthesis-only input, showing the stack after each relevant character.',
 'Validate parentheses while ignoring other ASCII characters. State empty-input behavior and report the first position that breaks the contract.',
 'Extend the contract to several delimiter types. Explain mismatched closers and remaining openers before adding quote or escape rules.',
 'Compare a simple count with an explicit stack. Explain which restricted contracts a count can handle and which require remembered nesting types.',
],
'queues-maps': [
 'Trace enqueue, cancel and serve on jobs a and b, distinguishing queue storage from the current job lookup.',
 'Build a pending-job model with validated unique IDs, a specified duplicate policy and an explicit empty-queue contract.',
 'Cancel and re-enqueue the same ID. Prevent an old queue entry from silently giving the new job an obsolete position.',
 'Compare eager removal with lazy cancellation markers. Explain service-order correctness, stale storage and cleanup responsibilities.',
],
'record-index': [
 'Trace create, update and delete operations across a record array and its Map index. Identify the authoritative state after each operation.',
 'Build a validated record store with stable IDs, deterministic display order and one chosen duplicate policy.',
 'Support ID renaming and a failing edit batch. Specify rollback or rejection so the display collection and index cannot disagree.',
 'Compare shared record references with immutable record replacement. Explain how each design keeps the index synchronized and how a test would expose drift.',
],
}

DSA_START = {
 'dsa-linear-scans': (
  'For the linked stock-price problem, trace [7, 1, 5, 3, 6, 4] and an always-decreasing input. State why a sale cannot precede its purchase and what the no-profitable-sale result should mean.',
  'Compare enumerating every allowed buy/sell pair with maintaining a summary of the processed price prefix. Explain what information the summary must preserve and why future prices cannot repair an invalid time order.'),
 'dsa-hashing': (
  'For Two Sum, trace [3, 3] with target 6 and distinguish two equal values at different positions from reusing one position. Also state the duplicate-detection contract of Contains Duplicate.',
  'Explain what a lookup entry represents in your Two Sum approach and when it becomes eligible to match. Compare that state with the simpler membership state used for duplicate detection.'),
 'dsa-linked-lists': (
  'For Reverse Linked List, draw a three-node chain and an empty chain. For each reference change in your proposed approach, identify which nodes remain reachable.',
  'Compare rebuilding fresh nodes with changing existing next references under the linked problem’s contract. State what each approach preserves and justify the reference invariant of the approach you choose.'),
 'dsa-search': (
  'For Binary Search, trace [1, 4, 8] with target 4, target 0 and target 9. State whether your interval includes its right endpoint before describing any update.',
  'Compare scanning sorted values with shrinking a candidate interval. Explain why each proposed interval update preserves every possible match and guarantees progress; only then consider the rotated-search extension.'),
 'dsa-two-pointers': (
  'For Container With Most Water, draw a short height input and identify the two indices defining each candidate. Distinguish the candidate’s width from its limiting height.',
  'Explain why your proposed pointer movement can discard candidates safely for the container problem. Then explain why 3Sum needs its own ordering and duplicate-handling argument rather than blindly copying that rule.'),
 'dsa-prefix-state': (
  'For Product of Array Except Self, trace a short nonzero input and a version containing one zero. State exactly which positions each output excludes.',
  'Compare recomputing the product for every position with reusing information about ranges. State the included and excluded boundaries of each summary, and explain why a division shortcut needs a separate zero contract.'),
 'dsa-intro-dp': (
  'For Climbing Stairs, enumerate small cases before writing a recurrence. For Coin Change, distinguish a valid zero-coin result from an unreachable amount.',
  'Write one sentence defining the state for each linked recurrence problem. Explain its base cases, dependency order and whether it minimizes a count or counts possible sequences.'),
}

STEPS = ('understand','understand','operate','operate','boundaries','boundaries','apply','apply','justify','justify','transfer','review')
KINDS = ('trace','trace','implement','implement','implement','explain','implement','design','debug','explain','implement','review')
NAMES = ('Trace the structure','Contrast a second case','Practice the operation','Preserve the contract','Handle boundaries','Make assumptions explicit','Solve an applied task','Extend the same structure','Diagnose a defect','Compare approaches','Transfer independently','Return for review')
CHECKS = {
 'understand': ['Show the state or output at each relevant step.', 'Explain the rule behind the first surprising result.'],
 'operate': ['State inputs, outputs and the mutation contract.', 'Demonstrate an ordinary input and a boundary case.'],
 'boundaries': ['Make missing, empty, duplicate and invalid cases explicit where relevant.', 'Explain why the chosen test distinguishes the required behavior.'],
 'apply': ['Trace a small case before implementing.', 'State the maintained state and test the failure or reset case.'],
 'justify': ['Support the diagnosis or choice with a counterexample or trace.', 'Explain one alternative and its trade-off.'],
 'transfer': ['Try the task before requesting a hint.', 'Explain why the approach works and check a fresh boundary case.'],
 'review': ['Attempt from memory before revisiting the lesson.', 'Explain how the changed contract affects the earlier approach.'],
}

def activity(unit, suffix, title, prompt, step, kind, route):
    return dict(id=unit['slug']+'-'+suffix, family_id='javascript:'+unit['slug']+':'+step,
      title=title, prompt=prompt, step=step, kind=kind, route=route,
      checklist=CHECKS[step], assessment='ungraded', source='authored')


def main():
    data=json.loads(PATH.read_text())
    by_slug={u['slug']:u for u in data['units']}
    for slug,title,prereqs,objective,mental,code,output,task,pitfall,bridge in EXTRA:
        by_slug[slug]=dict(id='explain:javascript:'+slug,slug=slug,tier=2,title=title,
          prerequisite_ids=['explain:javascript:'+p for p in prereqs],objective=objective,
          mental_model=mental,structure=dict(code=code,expected_output=output),applied_task=task,
          pitfall=pitfall,dsa_bridge=bridge,practice_ids=[],assessment_node_id=None)
    # Stable ordering preserves original IDs and prerequisite order.
    data['units']=sorted(by_slug.values(),key=lambda u:u['tier'])
    for u in data['units']:
        if u['tier']==1:
            u['activities']=[activity(u,str(i+1).zfill(2),NAMES[i],prompt,STEPS[i],KINDS[i],
              'review' if i==11 else 'extension' if i in (1,7,9) else 'core') for i,prompt in enumerate(BASIC[u['slug']])]
        elif u['tier']==2:
            u['activities']=[activity(u,slug,title,prompt,step,kind,route) for (slug,title,step,kind,route),prompt in zip([
              ('trace','Trace the relationship','understand','trace','core'),
              ('build','Build under a clear contract','operate','implement','core'),
              ('update','Preserve the relationship during updates','apply','design','core'),
              ('compare','Compare another representation','justify','explain','extension')],COMBINED[u['slug']])]
        else:
            prompts=[
              DSA_START[u['slug']][0],
              DSA_START[u['slug']][1],
              u['applied_task']+' After drafting your approach, design a counterexample to a plausible wrong implementation and explain which assumption it breaks.',
              'Later, return to a linked problem or a related fresh variant without notes. State what you remember, explain the invariant, and record whether you needed hints. This is deliberate review, not another independent solve credit.',
            ]
            u['activities']=[activity(u,slug,title,prompt,step,kind,route) for (slug,title,step,kind,route),prompt in zip([
              ('trace','Start with a contract and trace','understand','trace','core'),
              ('reason','From brute force to a justified approach','justify','explain','core'),
              ('test','Challenge your approach with a counterexample','apply','design','core'),
              ('review','Return for deliberate review','review','review','review')],prompts)]
    data['version']=2
    data['authoring_profile']=dict(version=1,
      progression=['understand','operate','boundaries','apply','justify','transfer','review'],
      routes=['core','extension','review'],assessment='ungraded',
      note='A reusable activity format, instantiated and reviewed per language or framework. Task counts do not confer mastery.')
    PATH.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    print(f"Published {len(data['units'])} authored units and {sum(len(u['activities']) for u in data['units'])} guided activities. No automatic grading or new solve credit.")

if __name__=='__main__':
    main()
