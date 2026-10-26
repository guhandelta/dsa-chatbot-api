# Practice workspace

`/workspace/{problem_id}?language=` opens a learner's workspace for one problem
in one language: the autosaved draft, project templates, checkpoints, progress
and the solution reveal rule. All routes require the same language access as
the problem itself.

| Route | Purpose |
| --- | --- |
| `PUT /workspace/{id}` | Autosave. Sends the revision the edit was based on; a stale revision gets 409 so another tab's save is never overwritten silently. `force: true` overwrites after the learner chooses to. |
| `POST /workspace/{id}/run` | Free test run of the curated cases. No review, no LLM, no peppercorns, and it never unlocks a solution. Capped by `WORKSPACE_RUNS_PER_HOUR`. Returns numbered pass/fail per case and a compiler/runtime diagnostic, never hidden inputs or expected values. |
| `POST /workspace/{id}/checkpoints` | Named snapshot. Each evaluation also stores one. At most `WORKSPACE_MAX_CHECKPOINTS` are kept; automatic ones are pruned first. |
| `POST /workspace/{id}/checkpoints/{cid}/restore` | Restore. The current files are saved as a checkpoint first. |
| `POST /workspace/{id}/reset` | Start again from the starter code in a template. The current files are saved as a checkpoint first. |
| `GET /practice/sessions/{sid}/summary` | Recap of one practice session from recorded events. |

`POST /practice/sessions/{sid}/actions` accepts `files` and `entry` for
`submit` and `hint`; the server bundles them into one program.

## Multiple files

Runners execute one program, so a workspace is bundled: helper files first,
the entry file last, and imports of the learner's own files blanked in place
so every line keeps its number. The response's `source_map` maps a diagnostic
line back to its file. Bundling is offered where concatenation is sound
(Python, JavaScript, TypeScript, C, C++, Rust, Ruby). Java, Go and C# keep one
source file plus notes. Notes files (`.md`, `.txt`) are never executed. A
workspace holds at most 8 files and 20,000 characters.

## Learning strikes

Reference solutions are hidden (`SOLUTION_REVEAL_POLICY=disabled`, the
default). Instead, a failed paid evaluation earns a learning strike
(`app/services/learning_strikes.py`, routes under `/strikes`). Free test runs
never do. Each strike records where the mistake happened and has its own set
of 2 or 3 quiz-bank questions on the same path stage (multiple choice, coding
or debugging, mixed). The set has 3 questions when the learner is struggling
on the topic. Solving the original problem does not clear a strike. A wrong
answer to a clearing question adds another strike, up to
`LEARNING_STRIKE_CAP` (4), and the missed question is replaced. What happens
at the cap is still undecided; `LEARNING_STRIKE_CAP_ACTION` is the hook, and
the default offers an earlier lesson and the mentor. Open strikes block
starting a different problem in that language (`LEARNING_STRIKES_GATE_PROGRESS`)
and keep the path node from counting as mastered. Retrying the original
problem is always allowed.

Learners can ask for extra practice on a topic at any time
(`POST /strikes/practice`), within `EXTRA_PRACTICE_SETS_PER_MONTH`. It is not
split by section yet. Extra practice is recorded and shown, but the mastery
formula does not use it until that rule is framed.

## Open product decisions

- What happens at the strike cap, how extra practice counts toward mastery,
  and how the monthly cap is split across sections.
- **Retention.** Drafts, checkpoints, run history and strikes are included in
  the profile export. Erasing the learning profile keeps them, like practice
  sessions; `app.services.workspace.delete_for_user` is ready once a retention
  rule is chosen.
