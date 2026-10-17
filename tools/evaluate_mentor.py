#!/usr/bin/env python3
"""Optional live-provider mentor evaluation; NOT part of offline unit tests.

Makes eight provider calls only with --live. Save responses for human review of
relevance, one-question style, tier progression, recall fidelity and answer
leakage. Mechanical checks do not certify pedagogical quality.
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.services.mentor import mentor_reply
from app.services.agentic_rag import bounded_model


async def evaluate(provider):
    results=[]
    for language in ('javascript','java'):
        for tier in range(1,5):
            async with asyncio.timeout(15):
                reply=await mentor_reply('two-sum','I compare every pair, but the large input takes too long.','',language,tier,provider,
                    recalled_moment='On a previous problem you considered remembering earlier values. This was unfinished hint reasoning, not verified success.',
                    model_factory=lambda p:bounded_model(p,350))
            results.append({'language':language,'tier':tier,'reply':reply,
                'mechanical_checks':{'asks_question':'?' in reply,'no_fenced_code':'```' not in reply,'one_question':reply.count('?')==1},
                'human_review':'pending'})
    return {'provider':provider,'live':True,'model_calls':8,'output_tokens_per_call':350,'sdk_retries':0,'bounded_factory':True,'results':results,
        'review_rubric':['responds to the stated assumption','one useful question','appropriate tier',
            'no solution/next-line leakage','does not label unfinished reasoning successful','no personality judgements']}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider',choices=['openai','gemini','claude'],required=True)
    parser.add_argument('--live',action='store_true')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if not args.live: parser.error('--live is required: this command incurs provider usage')
    report=asyncio.run(evaluate(args.provider))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print('Eight live responses saved; human pedagogical review remains pending.')
