#!/usr/bin/env python3
"""Bounded A/B pilot over actual approved local sources; no embeddings or writes.

--live invokes the configured provider with zero SDK retries. At most 8 cases,
2 strategies/case, 4 model calls/case, 2400 maximum output tokens/case.
Results measure source coverage/latency/usage, not semantic teaching correctness.
"""
import argparse
import hashlib
import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.db.database import SessionLocal
from app.services.agentic_rag import ReadOnlyTools, Scope, ProviderFailure, InvalidModelOutput, run


class RecordingTools(ReadOnlyTools):
    def __init__(self,*args):
        super().__init__(*args)
        self.observed=[]
    async def search(self,tool,query):
        docs=await super().search(tool,query)
        self.observed.extend(docs)
        return docs


async def evaluate(provider,cases,output):
    from app.core.config import settings
    model_id=getattr(settings,{'openai':'openai_model','gemini':'gemini_model','claude':'anthropic_model'}[provider])
    report={'created_at':datetime.now(timezone.utc).isoformat(),'provider':provider,'live':True,
        'experiment_configuration':{'model':model_id,
            'engine_sha256':hashlib.sha256((ROOT/'app/services/agentic_rag.py').read_bytes()).hexdigest(),
            'max_searches':2,'max_model_calls':3,'max_context_sources':4,
            'planner_output_tokens':300,'answer_output_tokens':900,'input_bytes_per_call':16000,
            'call_timeout_seconds':10,'request_timeout_seconds':30,'sdk_retries':0,
            'thinking_budget':0 if provider=='gemini' else None},
        'baseline':'one-shot local retrieval over the same approved stores; no vector embeddings',
        'human_answer_review':'pending','cases':[],
        'limitations':['Small PDF-focused pilot, not a general adoption verdict.',
            'Source coverage does not establish claim correctness or instruction quality.',
            'Provider usage is reported only when SDK usage metadata is available.']}
    for case in cases:
        entry={'id':case['id'],'question':case['question'],'expected_sources':case['expected_sources'],'runs':{}}
        # Alternate order to reduce a consistent first-request warmup advantage.
        strategies=('standard_local','agentic') if len(report['cases'])%2==0 else ('agentic','standard_local')
        for strategy in strategies:
            async with SessionLocal() as session:
                tools=RecordingTools(session,Scope(case['language'],case['track']))
                run_stats={}
                started=time.monotonic()
                try:
                    result=await run(case['question'],provider,[],tools,strategy=strategy,report_sink=run_stats)
                    authorized=await tools.reauthorize(tools.observed)
                    retrieved={d.metadata.get('source') for d in authorized}
                    cited={s['filename'] for s in result.sources}
                    expected=set(case['expected_sources'])
                    entry['runs'][strategy]={'status':'completed','answer':result.answer,'sources':result.sources,
                        'retrieved_expected':sorted(expected & retrieved),
                        'cited_expected':sorted(expected & cited),
                        'retrieval_coverage':len(expected & retrieved)/len(expected),
                        'citation_coverage':len(expected & cited)/len(expected),
                        'context_coverage':len(expected & set(result.report.get('context_sources',[])))/len(expected),**result.report}
                except Exception as exc:
                    try:
                        authorized=await tools.reauthorize(tools.observed)
                        retrieved={d.metadata.get('source') for d in authorized}
                        expected=set(case['expected_sources'])
                        retrieval_metrics={'retrieved_expected':sorted(expected & retrieved),
                            'retrieval_coverage':len(expected & retrieved)/len(expected),
                            'context_coverage':len(expected & set(run_stats.get('context_sources',[])))/len(expected)}
                    except Exception:
                        retrieval_metrics={}
                    entry['runs'][strategy]={**run_stats,**retrieval_metrics,'elapsed_ms':round((time.monotonic()-started)*1000),'status':'failed','error_type':type(exc).__name__,
                        **({'provider_error_type':exc.kind,'http_status':exc.status} if isinstance(exc,ProviderFailure) else {}),
                        **({'schema_errors':exc.codes,'model_preview':exc.preview} if isinstance(exc,InvalidModelOutput) else {})}
        report['cases'].append(entry)
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({'case':case['id'],'runs':{k:v['status'] for k,v in entry['runs'].items()}}),flush=True)
        # Fail fast on transport/provider failures; do not burn a whole benchmark.
        if all(r.get('error_type')=='ProviderFailure' for r in entry['runs'].values()):
            break
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider',choices=['openai','gemini','claude'],required=True)
    parser.add_argument('--cases',type=int,default=6,choices=range(1,9))
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--case-id',action='append',help='Run selected existing question IDs only')
    parser.add_argument('--live',action='store_true')
    args=parser.parse_args()
    if not args.live:parser.error('--live is required because provider usage is incurred')
    cases=json.loads((ROOT/'data/evaluations/agentic_rag.json').read_text())
    if args.case_id:
        known={case['id'] for case in cases}
        if set(args.case_id)-known:parser.error('Unknown case ID')
        cases=[case for case in cases if case['id'] in args.case_id]
    cases=cases[:args.cases]
    result=asyncio.run(evaluate(args.provider,cases,args.output))
    raise SystemExit(int(any(r['status']=='failed' for c in result['cases'] for r in c['runs'].values())))
