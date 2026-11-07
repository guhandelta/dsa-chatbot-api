"""Measure prompt-cache efficiency of mentor calls against a baseline. Spends real tokens.

Runs the same short sequence of mentor turns (tiers 1-4 on one problem) under
three configurations and prints input / cache-creation / cache-read tokens:

    baseline   PROMPT_CACHE_ENABLED=false, CAG_ENABLED=false
    cache      PROMPT_CACHE_ENABLED=true,  CAG_ENABLED=false
    cache+cag  PROMPT_CACHE_ENABLED=true,  CAG_ENABLED=true

Needs ANTHROPIC_API_KEY in .env. Usage (from the API folder):

    python tools/measure_prompt_cache.py --language python --problem two-sum --turns 4

Each configuration makes `--turns` Claude calls (12 calls with the defaults).
Expect `cache` to show cache_creation 0 when the mentor prefix is below the
model's minimum cacheable length (1024 tokens on Claude Sonnet 4); `cache+cag`
should show one cache write on the first turn and cache reads after it.
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings  # noqa: E402
from app.services import context_pack  # noqa: E402
from app.services.llm_router import get_llm  # noqa: E402
from app.services.mentor import mentor_reply  # noqa: E402
from app.services.prompt_cache import usage_from  # noqa: E402

CONFIGS = {"baseline": (False, False), "cache": (True, False), "cache+cag": (True, True)}


async def run(config: str, language: str, problem: str, turns: int) -> list[dict]:
    settings.prompt_cache_enabled, settings.cag_enabled = CONFIGS[config]
    context_pack.reset_cache()
    rows = []

    def factory(provider):
        llm = get_llm(provider)

        class Recorder:
            async def ainvoke(self, messages):
                response = await llm.ainvoke(messages)
                rows.append(usage_from(response) or {})
                return response
        return Recorder()

    for turn in range(turns):
        await mentor_reply(problem, "I compare every pair, which feels slow.", "", language,
                           min(turn + 1, 4), "claude", model_factory=factory)
    return rows


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", default="python")
    parser.add_argument("--problem", default="two-sum")
    parser.add_argument("--turns", type=int, default=4)
    args = parser.parse_args()
    if not settings.anthropic_api_key:
        sys.exit("ANTHROPIC_API_KEY is not set")
    summary = {}
    for config in CONFIGS:
        rows = await run(config, args.language, args.problem, args.turns)
        for i, row in enumerate(rows, 1):
            print(f"{config:10} turn {i}: {json.dumps(row, sort_keys=True)}")
        summary[config] = {k: sum(r.get(k, 0) for r in rows)
                           for k in ("input_tokens", "uncached_input", "cache_creation", "cache_read", "output_tokens")}
    print("\nTotals per configuration:")
    for config, totals in summary.items():
        print(f"  {config:10} {json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    asyncio.run(main())
