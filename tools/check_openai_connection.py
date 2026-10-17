"""Minimal credential check: sends a constant synthetic prompt, no application data."""
import asyncio
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.config import settings


async def main():
    from openai import AsyncOpenAI, APIStatusError, APIConnectionError
    async with AsyncOpenAI(api_key=settings.openai_api_key, timeout=10, max_retries=0) as client:
        try:
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[{'role':'user','content':'Reply with OK.'}],
                max_tokens=8,
                temperature=0,
            )
        except APIStatusError as exc:
            print(json.dumps({'connected':True,'succeeded':False,'http_status':exc.status_code}))
            return 1
        except APIConnectionError:
            print(json.dumps({'connected':False,'succeeded':False,'error':'connection_failed'}))
            return 1
        print(json.dumps({'connected':True,'succeeded':True,'model':response.model,
                          'usage':response.usage.model_dump() if response.usage else None}))
        return 0


if __name__=='__main__':
    raise SystemExit(asyncio.run(main()))
