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


def constraints(language):
    common = ('Preserve implementation, input and version qualifiers. Do not turn a '
              'property of one implementation into a guarantee for every implementation. '
              'If a retrieved note conflicts with these qualifications, explicitly qualify '
              'the explanation; do not misattribute the correction to that note. '
              'Linked-list insertion/deletion is constant-time only with the required '
              'node/predecessor references already available; locating them may be linear.')
    if language == 'java':
        return common + (' HashMap/HashSet use hashCode and equals. TreeMap/TreeSet '
            'use comparator/natural-order comparisons for key/element equivalence. '
            'Ordering should be consistent with equals to honor the general Map/Set '
            'contract. Never say every Java Map or Set uses hashing.')
    if language == 'javascript':
        return common + (' Ordinary JavaScript Array values have object/property semantics, '
            'can be sparse and can contain references. ECMAScript does not guarantee '
            'a C-style contiguous memory layout or universal operation timings. '
            'Do not imply array assignment copies referenced objects; distinguish index '
            'assignment, append and middle insertion/deletion.')
    return common
