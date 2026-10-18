"""Save a small live-answer probe for manual review; never auto-certify correctness."""
import asyncio
from datetime import datetime,timezone
import json
from pathlib import Path
from app.services.rag_pipeline import run_rag_chat
ROOT=Path(__file__).resolve().parents[2]

async def main():
    cases=[json.loads(l) for l in (ROOT/'Training Data/generated/knowledge-gap-fill-v1/evaluation/retrieval_cases.jsonl').open()]
    selected={'java-generics','java-map','js-number','embedded-python','embedded-c'}
    gate=asyncio.Semaphore(2)
    async def one(c):
        async with gate:
            try:
                answer=await asyncio.wait_for(run_rag_chat(c['question'],'gemini',[],c['language'],track='language',subject=None if c['subject']==c['language'] else c['subject']),timeout=60)
                return {'id':c['id'],'question':c['question'],'answer':answer,'review_status':'requires_manual_review'}
            except Exception as exc:return {'id':c['id'],'error_type':type(exc).__name__}
    results=await asyncio.gather(*(one(c) for c in cases if c['id'] in selected))
    report={'checked_at':datetime.now(timezone.utc).isoformat(),'provider':'gemini','cases':len(results),'results':results,
            'limitations':'Five public questions; manual review required, not exhaustive correctness certification.'}
    (ROOT/'reports/knowledge-base-training-2026-10-18/live-answer-probe.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':asyncio.run(main())
