"""Deterministic reference curation; originals remain in the quarantine archive.

These checks establish data hygiene, not certification of every teaching claim.
Keep this policy shared by the importer and the one-off maintenance command.
"""
from copy import deepcopy
import hashlib
import json
import re

VERSION = 'reference-cleanup-v3'
PUBLIC_REFERENCE_KINDS = {'concept', 'reference'}
# 00b says it is "still BLOCKED for publication": evidence levels and operator-only checks.
PLANNING_SOURCES = {'html-batch-00-manifest.md', 'html-batch-00b-reference-inventory.md',
                    'html-batch-00d-ui-patterns-and-practice.md'}
QUARANTINED_IDS = {
    'ref-820a2ea30c7c8d90b644361b':
        'Undirected adjacency insertion publishes the first edge before reverse allocation succeeds; failure leaves a one-sided edge. Needs a reviewed repair.',
}
FRAMEWORK_SUBJECTS = ('python-django', 'python-fastapi', 'python-flask')

# Text that belongs to the authoring pipeline (graders, RAG schemas, page
# furniture), not to the learner. Removed line by line from section chunks.
META_LINE = re.compile(r'\bRAG\b|\bgrader\b|grading metadata|\brubric\b|\bJSONL\b|chunk (?:schema|index)'
                       r'|Training (?:Data|Blueprint) for the DSA Mentor|^Page \d+$|^\d+$'
                       r'|^(?:track|domain|level|hardware_verified|embedded_c|rust_dsa|rust_edition|safety_profile'
                       r'|algorithmic_complexity|true|false)$', re.I)
DROP_SECTION = re.compile(r'\bRAG\b|grading|rubric|schema|chunk index|ingestion|exercise formats'
                          r'|how to use this document', re.I)
# A numbered subsection that carries practice items with their answers.
ANSWER_BLOCK = re.compile(r'^\d{1,2}\.\d{1,2}\s+(?:.*\b(?:answers?|solutions?)\b|(?:practice|exercises?)\b)', re.I)
SECTION_HEADING = re.compile(r'^(?:#{1,3}\s+\S|\d{1,2}[.)]?\s+[A-Z]).{0,110}$')
TITLE_NOISE = re.compile(r'\s*(?::\s*Training (?:Data|Blueprint) for the DSA Mentor.*'
                         r'|[—-]?\s*(?:Algorithm\s+)?Training Blueprint|Algorithm Blueprint)\s*$', re.I)
SENTENCE_END = re.compile(r'[.!?:;)\]]["\')\]]*$')
LEGACY_HEADER = re.compile(r'^Imported reference; not locally executed\. Subject: [^;\n]*(?:; ([^\n]*))?\n')
CHUNK_ID = re.compile(r'\n+Chunk: ([A-Za-z0-9_.:-]+)\s*$')
# Generated "Strategy chooser" tables from these blueprint families put the
# approach to avoid in a column labelled "Why"; the Python algorithm and
# TypeScript tables use it for the reason and keep the label.
WATCH_OUT_DOCS = ('c_', 'ec_', 'ruby_', 'py_emb_')
LEVEL_CODE = re.compile(r'^L[0-9]$')
DATA_STRUCTURE_IDS = {
    'arrays': 'array', 'dynamic arrays': 'dynamic-array', 'dynamic memory buffers': 'dynamic-array',
    'strings': 'string', 'singly linked list': 'linked-list', 'singly linked lists': 'linked-list',
    'linkedlist': 'linked-list', 'linked_list': 'linked-list', 'doubly linked lists': 'doubly-linked-list',
    'doublylinkedlist': 'doubly-linked-list', 'circular linked lists': 'circular-linked-list',
    'stacks': 'stack', 'queues': 'queue', 'double-ended queues': 'deque', 'deques': 'deque',
    'priority queues': 'priority-queue', 'priorityqueue': 'priority-queue',
    'binary heaps': 'heap', 'heaps': 'heap', 'hash tables': 'hash-table', 'hashtable': 'hash-table',
    'hash sets': 'set', 'set (require "set")': 'set', 'hash': 'map',
    'binary trees': 'binary-tree', 'binarytree': 'binary-tree', 'binary_tree': 'binary-tree',
    'binary search trees': 'binary-search-tree', 'bst': 'binary-search-tree',
    'avl trees': 'avl-tree', 'avltree': 'avl-tree', 'red-black trees': 'red-black-tree',
    'redblacktree': 'red-black-tree', 'b-trees and b+ trees': 'b-tree', 'btree': 'b-tree',
    'tries (prefix trees)': 'trie', 'tries': 'trie', 'segment trees': 'segment-tree',
    'segmenttree': 'segment-tree', 'fenwick trees (binary indexed trees)': 'fenwick-tree',
    'fenwick trees': 'fenwick-tree', 'fenwicktree': 'fenwick-tree',
    'disjoint sets (union-find)': 'disjoint-set', 'disjointset': 'disjoint-set', 'union_find': 'disjoint-set',
    'bloom filters': 'bloom-filter', 'bloomfilter': 'bloom-filter',
    'adjacency lists': 'graph-adjacency-list', 'graphs stored as adjacency lists': 'graph-adjacency-list',
    'adjacency matrices': 'graph-adjacency-matrix', 'graphs stored as adjacency matrices': 'graph-adjacency-matrix',
    'edge lists': 'graph-edge-list', 'directedgraph': 'directed-graph', 'undirectedgraph': 'undirected-graph',
    'weightedgraph': 'weighted-graph', 'pointers': 'pointer',
}


def source_is_plan(filename):
    return filename.replace('\\', '/').rsplit('/', 1)[-1].lower() in PLANNING_SOURCES


def quarantine_reason(row):
    if row['id'] in QUARANTINED_IDS:
        return QUARANTINED_IDS[row['id']]
    if source_is_plan(row['metadata'].get('origin', '')):
        return 'Authoring plan, candidate contract or gap register; not learner reference knowledge.'
    # Source-specific plan/schema fragments, not blanket removal of terms such
    # as "placeholder" (a valid CSS selector) or "exercise" in ordinary prose.
    text = row['document']
    origin = row['metadata'].get('origin', '')
    if ('CSS Sass Bootstrap Curriculum' in origin or 'CSS, Sass, Bootstrap, Architecture Curriculum.pdf' in origin
            or 'Tailwind Bulma Shadcn Training Curriculum.pdf' in origin):
        return 'Mixed extracted framework chunks replaced by heading-scoped Markdown references; original preserved.'
    if (row['metadata'].get('subject') == 'embedded-c'
            and 'Preserve the hardware/software contract for ' in text
            and "['mentions " in text):
        return 'Authoring outline and keyword rubric, not an explanatory hardware reference.'
    if (row['metadata'].get('subject') == 'embedded-python'
            and ('hits.append(i)' in text or 'hits .append(i)' in text)
            and ('irq(' in text or 'irq (' in text)):
        return 'Interrupt example allocates by appending to a list without an ISR allocation contract; replaced by reviewed guidance.'
    if row['metadata'].get('subject') == 'html' and any(term in text for term in (
            '## 23. Updated gap register', '## 22. Validation checklist',
            'web-candidate-v1', '| Gap ID | Status | Current gap |')):
        return 'Candidate production/schema/gap fragment; retained privately for authoring.'
    if re.match(r'(?:Imported reference[^\n]*\n)?[^\n]*\bTraining Corpus\b', text):
        return 'Dataset manifest listing source files; not learner reference text.'
    if re.search(r'\bRAG grader\b|\bgrader should\b|Training Data for the DSA Mentor', text, re.I):
        return 'Grader rubric or dataset description, not learner reference text.'
    return None


def blueprint_title(text):
    """Readable document title; DOCX runs are joined without spaces in extraction."""
    first = next((line.strip() for line in text.splitlines() if line.strip()), '')
    first = re.sub(r'^#+\s*', '', first)
    first = re.sub(r'^(Python / (?:Django|Flask|FastAPI))(?=\S)', r'\1 ', first)
    first = re.sub(r'(?<=\S)(Training Blueprint)', r' \1', first)
    return TITLE_NOISE.sub('', first).strip(' —-:')[:120]


TITLE_PREFIX = re.compile(r'^(?:Python / (?:Django|Flask|FastAPI)|C\+\+|Rust|Ruby|TypeScript|Python on hardware,|Python'
                          r'|Embedded C -)\s*')


def title_topic(title):
    """The topic a template was filled in for, e.g. 'LRU Cache' in 'Python / Django LRU Cache'."""
    prefix = TITLE_PREFIX.match(title)
    return title[prefix.end():].strip() if prefix else ''


def strip_contents(text):
    """Remove a table of contents before exercise-heading detection and chunking.

    A contents entry such as "6. Core practice exercises with answer key" would
    otherwise stop the reference view before the sections it lists. The contents
    block ends where its first entry appears again as the real heading.
    """
    lines = text.splitlines()
    # PDF extraction prefixes contents entries with a DEL control character.
    stripped = [line.strip(' \t\x7f\u00a0') for line in lines]
    for start, line in enumerate(stripped):
        if line.lower() not in ('contents', 'table of contents'):
            continue
        entries = [i for i in range(start + 1, min(start + 4, len(lines))) if stripped[i]]
        if not entries:
            break
        first = re.sub(r'\s{2,}\d+$', '', stripped[entries[0]])
        end = next((i for i in range(entries[0] + 1, min(start + 80, len(lines)))
                    if stripped[i] == first), None)
        if end is None:
            end = start + 1
            while end < len(lines) and (not stripped[end] or re.match(r'^\d{1,2}[.)]?\s+\S', stripped[end])):
                end += 1
        return '\n'.join(lines[:start] + lines[end:])
    return text


def _split_long(lines, size, measure=len):
    """Split a section on line boundaries, preferring lines that end a sentence."""
    parts, current, length = [], [], 0
    for line in lines:
        if current and length + measure(line) + 1 > size:
            cut = max((i for i, kept in enumerate(current[:-1], 1)
                       if SENTENCE_END.search(kept) and i * 2 >= len(current)), default=len(current))
            parts.append(current[:cut])
            current = current[cut:]
            length = sum(measure(kept) + 1 for kept in current)
        current.append(line)
        length += measure(line) + 1
    if current:
        parts.append(current)
    return parts


def section_chunks(text, size=1800):
    """Chunk extracted document text on its headings instead of a word count.

    Every chunk starts at a heading or at the start of a line (after a sentence
    end where one is available) and carries the document title, so no chunk
    begins mid-sentence without context. Authoring-only sections and lines
    (grading, RAG schemas, page furniture) are left out.
    """
    title = blueprint_title(text)
    topic = title_topic(title)
    # Measure without the topic name so a template filled in for many topics
    # splits at the same lines in every copy (and duplicates are detectable).
    measure = (lambda line: len(line.replace(topic, ''))) if len(topic) > 2 else len
    sections, heading, lines, seen_title, in_answers = [], None, [], False, False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if not seen_title or re.sub(r'^#+\s*', '', line) == title:
            seen_title = True
            continue
        if SECTION_HEADING.match(line):
            sections.append((heading, lines))
            heading, lines, in_answers = line, [], False
            continue
        # Practice items and their answers stay out until the next section.
        in_answers = in_answers or bool(ANSWER_BLOCK.match(line))
        if not in_answers and not META_LINE.search(line):
            lines.append(line)
    sections.append((heading, lines))
    chunks, pending, pending_heading = [], [], None
    def flush():
        if pending and sum(len(line) for line in pending) >= 80:
            label = title + (' · ' + re.sub(r'^#+\s*', '', pending_heading) if pending_heading else '')
            chunks.append(label + '\n' + '\n'.join(pending))
    for heading, lines in sections:
        if heading and DROP_SECTION.search(heading) or not lines:
            continue
        body = ([heading] if heading else []) + lines
        if pending and sum(measure(line) + 1 for line in pending + body) <= size:
            pending.extend(body)
            continue
        flush()
        pending, pending_heading = [], heading
        for number, part in enumerate(_split_long(body, size, measure)):
            if number:
                flush()
                pending, pending_heading = [], (heading or 'Overview') + ' (continued)'
            pending = list(part)
    flush()
    return chunks


def reference_id(subject, original_id):
    """The importer's stable ID for a (subject, source ID) pair."""
    return 'ref-' + hashlib.sha256(json.dumps([subject, original_id]).encode()).hexdigest()[:24]


def _payload_metadata(row):
    raw = row.get('payload')
    meta = raw.get('metadata') if isinstance(raw, dict) else None
    return meta if isinstance(meta, dict) else {}


def _source_metadata(row):
    raw = row.get('payload', {})
    fields = raw.get('metadata', {}) if isinstance(raw, dict) else {}
    context = {}
    for key in ('doc_url', 'version', 'runtime_version', 'framework_version',
                'rust_edition', 'runtime', 'platform', 'framework_context', 'retrieved_on'):
        value = fields.get(key, raw.get(key))
        if isinstance(value, (str, bool, int, float)) and value != '':
            context[key] = value
    return context


def data_structure_id(label):
    label = str(label).strip()
    known = DATA_STRUCTURE_IDS.get(label.lower())
    return known or re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')


def normalize_reference(row):
    """Idempotent cleanup of one active row; returns the row and its previous ID if retagged."""
    m = row['metadata']
    pm = _payload_metadata(row)
    document = row['document']
    header = LEGACY_HEADER.match(document)
    if header:
        # The fixed provenance sentence lives in metadata (verified/executable);
        # only version or platform context is still useful to the reader.
        document = ('Context: ' + header.group(1) + '\n' if header.group(1) else '') + document[header.end():]
    chunk = CHUNK_ID.search(document)
    if chunk:
        m['chunk_id'] = chunk.group(1)
        document = document[:chunk.start()]
    if str(pm.get('doc', '')).startswith(WATCH_OUT_DOCS) and pm.get('section') == 'algorithms-and-strategies':
        document = re.sub(r'^Why: ', 'Watch out for: ', document, flags=re.M)
    row['document'] = document
    previous_id = None
    if m['subject'] == 'c' and (pm.get('track') == 'embedded_c' or str(pm.get('doc', '')).startswith('ec_')):
        # Embedded hardware rows were imported under plain C (track lived in nested metadata).
        original = str(row['payload'].get('id'))
        if reference_id('c', original) == row['id']:
            previous_id, row['id'] = row['id'], reference_id('embedded-c', original)
        m['subject'] = 'embedded-c'
    level = pm.get('level_code') or pm.get('level')
    if isinstance(level, str) and LEVEL_CODE.match(level) and 'level' not in m:
        m['level'] = level
        if isinstance(pm.get('level'), str) and not LEVEL_CODE.match(pm['level']):
            m['level_label'] = pm['level']
    if pm.get('data_structure') and 'data_structure' not in m:
        m['data_structure'] = str(pm['data_structure'])
    if m.get('data_structure'):
        m['data_structure_id'] = data_structure_id(m['data_structure'])
    return row, previous_id


def _near_duplicate_key(row):
    text = row['document']
    lines = text.split('\n', 1)
    if len(lines) == 2 and isinstance(row.get('payload'), dict) and 'source_sha256' in row['payload']:
        # Section chunks: drop the title line and the topic name it carries, so
        # one template filled in for many topics collapses to one copy.
        topic = title_topic(lines[0].split(' · ')[0])
        text = lines[1]
        if len(topic) > 2:
            text = re.sub(re.escape(topic), ' ', text, flags=re.I)
    text = re.sub(r'\b(?:django|flask|fastapi)\b', ' ', text, flags=re.I)
    return re.sub(r'[\W_]+', ' ', text.casefold()).strip()


def _retitle_shared(row):
    """A section kept for many topics is labelled by its family, not the first topic."""
    first, _, rest = row['document'].partition('\n')
    title, sep, section = first.partition(' · ')
    prefix = TITLE_PREFIX.match(title)
    if prefix and title_topic(title):
        row['document'] = title[:prefix.end()].strip(' ,-') + sep + section + '\n' + rest
        row['metadata']['shared_template'] = True


def clean_reference_rows(rows):
    active, quarantine, aliases, seen, near = [], [], {}, {}, {}
    for original in rows:
        reason = quarantine_reason(original)
        if reason:
            quarantine.append({'reason': reason, 'record': deepcopy(original)})
            continue
        row, previous_id = normalize_reference(deepcopy(original))
        if previous_id:
            row['previous_ids'] = sorted(set(row.get('previous_ids', [])) | {previous_id})
        m = row['metadata']
        m.update({k: v for k, v in _source_metadata(row).items() if k not in m})
        m['curation_version'] = VERSION
        m.setdefault('review_status', 'not_independently_certified')
        if m.get('dataset_version') in ('knowledge-gap-fill-v1', 'framework-sections-v1'):
            m['coverage_scope'] = 'subject-scoped-reference'
        elif m['subject'] in FRAMEWORK_SUBJECTS:
            m['coverage_scope'] = 'dsa-in-framework-context'
        elif m['subject'].startswith('spring-'):
            m['coverage_scope'] = 'starter-reference'
        elif m['subject'] == 'css':
            m['coverage_scope'] = 'css-sass-bootstrap-reference'
        elif m['subject'] == 'tailwind':
            m['coverage_scope'] = 'tailwind-bulma-shadcn-reference'
        # Never merge private exercise candidates or different scopes/kinds.
        # Identical public text has one canonical retrieval ID with unioned
        # provenance. The archived duplicate retains its entire original payload.
        key = (m['language'], m['subject'], m['kind'], m['contains_answer'],
               re.sub(r'\s+', ' ', row['document']).strip())
        near_key = (m['language'], m['subject'], m['contains_answer'], _near_duplicate_key(row))
        target = seen.get(key) if m['contains_answer'] is False else None
        reason = 'Identical public reference text in the same scope.'
        if target is None and m['contains_answer'] is False and near_key in near:
            target = near[near_key]
            reason = 'Same template text as another record in this subject once topic and framework names are removed.'
        if target is not None:
            if reason.startswith('Same template'):
                _retitle_shared(target)
            target['provenance'] = sorted(set(target['provenance']) | set(row['provenance']))
            target['duplicate_ids'] = sorted(set(target.get('duplicate_ids', [])) | {row['id']})
            aliases[row['id']] = target['id']
            quarantine.append({'reason': reason, 'canonical_id': target['id'], 'record': deepcopy(original)})
            continue
        if m['contains_answer'] is False:
            seen[key] = row
            near[near_key] = row
        active.append(row)
    return active, quarantine, aliases
