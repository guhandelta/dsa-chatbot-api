"""Measure the live semantic index and actual tutor prompt without generating answers.

Only public authored probe questions are embedded. The final LLM is replaced by a
capture stub; semantic retrieval and the legacy scoped vector lookup remain real.
"""
import asyncio
from contextvars import ContextVar
from datetime import datetime, timezone
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.services import reference_semantics as semantic, reference_library, rag_pipeline
from app.services.content_access import public_text

ROOT=Path(__file__).resolve().parents[2]
CAPTURE=ContextVar('evaluation_prompt')

class CaptureModel:
    async def ainvoke(self,messages):
        CAPTURE.get().append(messages[0].content)
        return SimpleNamespace(content='Evaluation capture completed.')

async def main():
    package=ROOT/'Training Data/generated/knowledge-gap-fill-v1'
    cases=[json.loads(line) for line in (package/'evaluation/retrieval_cases.jsonl').open() if line.strip()]
    rows={r['id']:r for r in reference_library.records()}
    gate=asyncio.Semaphore(4)
    original_search=semantic.search
    cached={}
    def cached_search(query,language,subject=None,k=4):
        key=(query,language,subject,k)
        if key not in cached:cached[key]=original_search(query,language,subject,k)
        return cached[key]
    async def one(case):
        async with gate:
            subject=None if case['subject']==case['language'] else case['subject']
            capture=[];token=CAPTURE.set(capture)
            try:
                docs=await asyncio.to_thread(cached_search,case['question'],case['language'],subject)
                await rag_pipeline.run_rag_chat(case['question'],'gemini',[],case['language'],track='language',subject=subject)
                ids=[d.metadata.get('problem_id') for d in docs]
                expected=case['expected_record_ids']
                return {'id':case['id'],'semantic_top4':bool(set(ids)&set(expected)),
                        'expected_in_final_prompt':any(public_text(rows[rid]['document']) in capture[0] for rid in expected),
                        'scope_safe':all(d.metadata.get('language')==case['language'] and d.metadata.get('subject')==case['subject']
                                         and d.metadata.get('contains_answer') is False for d in docs),
                        'semantic_ids':ids}
            except Exception as exc:
                return {'id':case['id'],'error_type':type(exc).__name__,'semantic_top4':False,'expected_in_final_prompt':False,'scope_safe':False}
            finally:CAPTURE.reset(token)
    with patch.object(semantic,'search',cached_search),patch.object(rag_pipeline,'get_llm',lambda _:CaptureModel()):
        results=await asyncio.gather(*(one(case) for case in cases))
    report={'checked_at':datetime.now(timezone.utc).isoformat(),'index':json.loads(semantic.MANIFEST.read_text()),
            'cases':len(results),'semantic_expected_at_4':sum(r['semantic_top4'] for r in results),
            'expected_in_actual_final_prompt':sum(r['expected_in_final_prompt'] for r in results),
            'scope_safety_passed':all(r['scope_safe'] for r in results),'live_answer_model_calls':0,
            'limitations':['Authored 60-question probe; no generated-answer correctness certification.'],
            'results':results}
    out=ROOT/'reports/knowledge-base-training-2026-10-18/semantic-retrieval-recheck.json'
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('results','index')},indent=2))
    print('Final-context misses:',[r['id'] for r in results if not r['expected_in_final_prompt']])
    if not report['scope_safety_passed']:raise SystemExit(1)

if __name__=='__main__':asyncio.run(main())
