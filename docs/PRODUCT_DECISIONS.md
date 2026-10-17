# Product decisions and open questions

## October 14, 2026 clarification

### Mentor recall — provisional

Recall may use earlier hint reasoning and material associated with verified
solves/reviews, including unfinished hint attempts. The owner plans to revisit
this policy. An unfinished attempt must not be described as a proven success.
The learner's own reasoning must remain distinguishable from AI-generated review
comments; generated comments are not evidence that the learner reasoned that way.

The current recall implementation already uses learner-written hint notes and
reflections, plus historical solved events containing reasoning. This clarification
does not introduce storage or retrieval of AI-generated review text as learner memory.

### Cross-language recall — tentative subscription bonus

Cross-language recall means reusing the learner's own earlier reasoning on a
related problem in another programming language. For example, a JavaScript
set-based insight might help with a Java exercise involving the same technique.
It does not automatically assess their thought process or compare solutions
across languages. The owner proposes offering these connections as a complimentary
bonus with multiple-language subscription plans. Allowances and enforcement remain
undecided; see the subscription packaging side note below. The current lookup can
retrieve across languages and does not enforce plan-specific recall quotas. This
note does not implement or activate the proposed bonus.

### Subscription expiry — confirmed

Remaining peppercorns are retained after expiry. They cannot purchase mentor
help without an active subscription covering the requested language. Existing
chat/review usage remains available subject to balance and normal account gates.
Do not add a peppercorn-only bypass for mentor entitlement.

### Subscription packaging — side note for later

Decide whether subscriptions cover one language or whether a plan can allow
multiple chosen languages. The number of languages, plan structure, and pricing
are undecided. Revisit after deployment strategy and AI operating costs are
properly planned. Current per-language entitlements remain the implementation;
they are not a final commitment to commercial packaging. Do not introduce new
plans or payments based on this note.

Proposed cross-language recall bonus (tentative, for later planning):

- A multiple-language plan could include **3 complimentary cross-language recall
  connections**. The exact language-count eligibility for this allowance is not
  yet confirmed.
- A plan covering **3 languages** could include **6 complimentary cross-language
  recall connections**.

These are planning examples, not finalized entitlements. Decide what counts as a
connection, when allowances renew, how usage is tracked, and what happens after
complimentary connections are exhausted. Revisit alongside deployment strategy,
AI costs, plan language counts, and pricing. No quota, billing, or access-control
change is authorized by this side note alone.


## October 15 — foundation quality across all languages

The owner clarified that basic learning and DSA material must be solid across
all languages/frameworks in the knowledge base before curriculum pathways are
arranged. Earlier JavaScript/Java prioritization does not restrict this validation
scope. The goal is proficiency and versatility, not collection size. Check topic
coverage, explanations, language-specific practice and framework behavior with
explicit evidence; do not equate ingestion with readiness. Curriculum sequencing,
subscription and payment decisions remain deferred. See
[the whole-library inventory and readiness requirements](FOUNDATION_READINESS.md).


## October 16 — immediate deliverables and deferred web learning

Immediate scope: highlight knowledge-base gaps across all subjects, recommend
additional languages, and provide detailed candidate-data prompts for HTML/CSS.
The following are recorded for later and must not be treated as finalized paths:
essential JS/TS followed by optional HTML/CSS practice and chosen UI frameworks
(ReactJS, Angular, NextJS, Remix, GatsbyJS, Astro, Solid, etc.); separately scoped Web
Fundamentals; library/framework exercise banks covering proper usage, dos/don'ts,
UI algorithms and patterns; practical Web APIs; design patterns for all languages.
No new curriculum sequence, entitlements or pricing was decided. See
[the gap report and deferred plans](KNOWLEDGE_BASE_GAPS_2026-10-16.md) and
[the HTML/CSS prompt pack](training-prompts/README.md).
