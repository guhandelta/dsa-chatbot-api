# Prompt caching and basic CAG

## What it does

Mentor-style prompts (Socratic mentor, RAG chat, Study Room) are built by
`app/services/prompt_cache.py` in two parts:

| Part | Contents | Cached |
|---|---|---|
| Stable prefix | rules, persona, language qualifications, CAG context pack | yes (Claude: `cache_control: ephemeral`) |
| Dynamic tail | hint tier, problem reference, retrieved chunks, learner notes | no |

Claude gets the stable prefix as its own system block with a cache breakpoint.
OpenAI and Gemini cache long prefixes automatically, so they get one plain
string with the stable part first.

**Cache-augmented generation (CAG)** adds a small, versioned context pack to
the stable prefix (`app/services/context_pack.py`). Packs are JSON manifests in
`data/context_packs/`. Two ship today:

| Pack | Content | Size |
|---|---|---|
| `python-core@2` | Python fundamentals, library notes, dicts and sets | ~4.8 K chars |
| `javascript-core@2` | JavaScript fundamentals, library notes, first values lesson | ~5.1 K chars |

Lesson files pass through `public_text`, so front matter (hidden tests) and
protected sections (solutions, hints) never reach a pack. Each manifest pins
the sha256 of its rendered text: if a lesson changes, the pack is skipped with
a warning until the version is bumped and the hash refreshed
(`python -m app.services.context_pack` prints the new hash). The retrieval
index is never loaded into a pack.

## Flags (.env)

| Variable | Default | Meaning |
|---|---|---|
| `PROMPT_CACHE_ENABLED` | `true` | stable-first layout + Claude cache breakpoint |
| `CAG_ENABLED` | `false` | preload the language's context pack |
| `CAG_PROVIDERS` | `claude` | providers that receive the pack (uncached providers pay for it on every call) |
| `CAG_PACK_IDS` | empty | allowlist of pack ids; empty allows any pack for the language |
| `CAG_PACK_DIR` | `data/context_packs` | manifest folder |
| `CAG_MAX_CHARS` | `48000` | packs above this are skipped, never truncated |

## Measuring

Every mentor, RAG chat and Study Room call writes one line on the
`app.llm_usage` logger:

```
llm_usage {"cache": true, "cache_creation": 0, "cache_read": 5600, "call_site": "mentor",
           "input_tokens": 5650, "model": "claude-sonnet-4-6", "output_tokens": 20,
           "pack": "python-core@2+8655aa9074d2", "provider": "claude", "stable_chars": 5100,
           "uncached_input": 50}
```

`input_tokens` is the whole prompt; `uncached_input` is the part billed at the
full rate. The same numbers are attached to the active trace span
(`cache_creation_tokens`, `cache_read_tokens`).

To compare against a baseline with real calls (spends tokens, needs
`ANTHROPIC_API_KEY`):

```
python tools/measure_prompt_cache.py --language python --problem two-sum --turns 4
```

## Things to know

- Claude only caches a prefix above a model-dependent minimum length. The
  configured model is `claude-sonnet-4-6`. The mentor rules alone are about 250
  tokens (RAG chat's about 300), so with CAG off the breakpoint is sent but nothing is cached
  (`cache_creation: 0`, no extra cost). CAG lifts the prefix above the line.
- The cache lives 5 minutes and every hit refreshes it. A write costs 1.25x the
  input price; each read costs 0.1x. This can save money when the *same long
  prompt* is reused, but adding a large CAG pack can cost more than a short
  RAG-only prompt even when every call is a cache hit. Measure total billed
  cost before enabling CAG.
- Default routing sends explanations to Gemini and code questions to Claude;
  only Claude calls get the explicit breakpoint and, by default, the pack.
