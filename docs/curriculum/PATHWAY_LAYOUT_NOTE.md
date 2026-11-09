# Pathway layout note (JavaScript Arrays pilot)

Status: authoring layout, 9 November 2026. Copy this structure for Python, Java and other languages; rewrite every prompt, contract and fixture for the destination language. A complete layout is an authoring status only: it grants no progress, publication or mastery.

## Files

| What | Where |
|---|---|
| Explain unit (lesson, worked example, guided activities) | `data/explain/<language>.json`, unit `explain:<language>:<slug>` |
| Graded quiz items | `data/curriculum/quiz/<language>.json`, `node` = the unit's `assessment_node_id` (e.g. `stage-06`) |
| Evidence map for the pathway | `data/curriculum/pathway-evidence-pilot.json` (one file per language when more are added) |
| Checker | `app/services/pathway_evidence.py`, CLI `tools/check_pathway_evidence.py` |
| Authoring templates | `UNIT_TEMPLATE.md`, `unit-template.json`, `BLUEPRINT.md`, filled example `JS_ARRAYS_EXAMPLE.md` |

## Unit structure

Each unit in the evidence map lists: `id`, `capabilities` (shared IDs such as `ordered-traversal`), `prerequisite_ids` (earlier units, same order as Explain), `external_prerequisite_nodes` (earlier learning-path nodes), four `evidence` roles, one `application` and one or more triggered `recovery` entries.

## Item types per stage

| Stage | Purpose | Source and type | Counts as independent? |
|---|---|---|---|
| Explain | Mental model, worked trace, pitfall | Explain unit body | No |
| Guided | Faded practice (`understand`/`operate`/`boundaries` activities) | Explain activities | No |
| Application | Small applied task using only taught capabilities | Explain activity (Arrays: `arrays-07`) | No (it is practice) |
| Trace | Predict state or output | Quiz `short_answer` / `mcq_code` (Arrays: `js-s06-short`) | Yes |
| Use | Implement or repair | Quiz `write_snippet` / `fix_bug` (Arrays: `ja-release-stage_06-4`) | Yes |
| Choice | Pick and justify a contract or representation | Quiz `explain` (Arrays: `js-s06-choose-copy`) | Yes |
| Transfer | Fresh problem family, same capabilities | Quiz `write_snippet` or `explain` (Arrays: `js-s06-transfer-peaks`) | Yes |
| Recovery | Targeted practice for an observed difficulty | Explain activities with a `when` trigger (Arrays: `arrays-05` boundary, `arrays-09` aliasing, `arrays-12` later review) | No |
| Independent | The four quiz-backed roles above, taken without hints | Study Room quiz | Yes, as evidence only |

## Evidence rules

- Trace/use/choice/transfer must point at graded quiz items on the unit's assessment node, with matching roles (trace; implement/debug; explain; implement/explain).
- Each role uses a distinct `family` and a distinct item; cosmetic variants of one task do not count twice.
- Guided Explain activities may never set `independent: true`; the checker rejects it.
- The application may require only capabilities declared by this or earlier units.
- Every runnable item is executed before commit: the solution passes all tests, the starter and at least one plausible wrong answer fail. Explain items carry a model answer and keyword groups; the model answer must score full marks and an off-target answer must stay below the pass score.
- Wording is our own; no copied judge or textbook text. No item, file or flag claims student mastery.

## Checker command

```bash
python tools/check_pathway_evidence.py
python -m pytest tests/test_pathway_evidence.py
python tools/audit_assessment_banks.py
```

Done for a unit means `errors: []` and `gaps: []`, the bank audit passes, and the new items' tests pass. Then still review the lesson, answer keys and a learner walkthrough before publishing.

## Copying to Python or Java

1. Author the Explain unit in `data/explain/<language>.json` with native constructs (Python lists and slicing; Java arrays vs `ArrayList` and `Arrays.copyOf`).
2. Add four graded items on that language's assessment node, one per role, in distinct families.
3. Add the unit to an evidence map with `"language": "<language>"`. The checker currently loads Explain units only for JavaScript (`explain_pathway.authored()`), so extend that lookup before a second language can pass.
4. Run the checker and tests until there are no errors or gaps.
