"""Trusted teaching qualifiers; source review links live in remaining-checks report."""
import re


def qualification_guard(answer, language):
    """Withhold known unsafe generalizations, not a general factual verifier.

    Return a trusted clarification without attributing it to retrieved sources.
    Conservative false positives are preferable to repeating these known errors.
    """
    if language == 'java' and re.search(r'\b(?:maps?|sets?|both)\b', answer, re.I):
        if re.search(r'hashcode|hash codes?|hashing', answer, re.I) and not re.search(
                r'TreeMap|TreeSet|comparator|ordered collections|hash-based', answer, re.I):
            return ('Equality depends on the collection implementation: hash-based and '
                    'ordered collections can use different equivalence rules. Which '
                    'Java Map or Set implementation are you using?')
    if language == 'javascript' and re.search(r'contiguous', answer, re.I):
        if not re.search(r'not guarante|no guarantee|not necessarily|engine|implementation', answer, re.I):
            return ('JavaScript arrays can be sparse and contain object references; '
                    'storage layout and performance depend on the implementation. '
                    'Which operation or JavaScript engine should we examine?')
    return None


def constraints(language, subject=None):
    common = (f'Teach and write code only in {language}. Do not switch languages at the '
              'learner’s request or copy a different language from reference material. '
              'Preserve implementation, input and version qualifiers. Do not turn a '
              'property of one implementation into a guarantee for every implementation. '
              'If a retrieved note conflicts with these qualifications, explicitly qualify '
              'the explanation; do not misattribute the correction to that note. '
              'A reference version or baseline is not execution evidence: do not call '
              'it tested or hardware-verified without an actual execution result. '
              'Linked-list insertion/deletion is constant-time only with the required '
              'node/predecessor references already available; locating them may be linear.')
    if subject == 'embedded-c':
        common += (' Volatile access semantics are compiler-defined; do not promise that '
                   'every source expression emits exactly one memory instruction or that '
                   'volatile accesses can never be combined. Volatile alone guarantees '
                   'neither atomic read-modify-write nor memory ordering or DMA cache coherence. '
                   'Use the exact MCU, cache policy, compiler and DMA documentation before '
                   'giving cache-line sizes, barrier sequences or alignment requirements. '
                   'Write-through memory alone does not solve stale CPU cache lines after '
                   'DMA writes. Describe buffer ownership and platform-specific cache maintenance.')
    if subject == 'embedded-python':
        common += (' Distinguish MicroPython hard IRQs, soft callbacks and scheduled callbacks. '
                   'Hard IRQs must avoid heap allocation. Scheduled callbacks may allocate '
                   'but must remain bounded; they are not necessarily the main application loop. '
                   'Preallocated buffer examples need an explicit overflow policy and '
                   'must keep every ISR counter/index bounded: an unbounded Python '
                   'integer counter can eventually allocate even when the buffer is fixed. '
                   'Use appropriate synchronization when state is shared with foreground code. '
                   'Do not invent board pins.')
    if language == 'java':
        return common + (' HashMap/HashSet use hashCode and equals. TreeMap/TreeSet '
            'use comparator/natural-order comparisons for key/element equivalence. '
            'Ordering should be consistent with equals to honor the general Map/Set '
            'contract. For TreeMap.put with a comparison-equivalent existing key, '
            'the existing key object remains and its value is replaced; do not print '
            'an example as if the newly supplied key object replaced the old key. '
            'Never say every Java Map or Set uses hashing.')
    if language == 'javascript':
        return common + (' Ordinary JavaScript Array values have object/property semantics, '
            'can be sparse and can contain references. ECMAScript does not guarantee '
            'a C-style contiguous memory layout or universal operation timings. '
            'Do not imply array assignment copies referenced objects; distinguish index '
            'assignment, append and middle insertion/deletion. Number cannot represent '
            'arbitrary integers exactly; some integers outside the safe-integer range '
            'are still exactly representable. BigInt(5.5) throws RangeError; it does '
            'not truncate a fractional Number. BigInt division truncates toward zero. '
            'Construct large exact integers from strings or bigint literals rather '
            'than already-rounded Number values.')
    return common
