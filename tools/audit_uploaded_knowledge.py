#!/usr/bin/env python3
"""Audit approved local extracted reference projections without changing sources.

This verifies mechanical retrieval/source separation; it is not a human review
of every pedagogical assertion. Run after upload/replacement or projection edits.
"""
import asyncio
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from app.db.database import SessionLocal
from app.db.models import KnowledgeDocument
from app.services.uploaded_knowledge import ALL_LANGUAGES, project, infer_language, search, PROJECTION_VERSION
from app.services.knowledge_hygiene import source_is_plan


async def audit():
    benchmarks = {r['expected_filename']: r for r in json.loads((Path(__file__).resolve().parents[1]/'data/evaluations/uploaded_retrieval.json').read_text())}
    report = {'projection_version': PROJECTION_VERSION, 'documents': [], 'failures': []}
    async with SessionLocal() as session:
        rows = list((await session.scalars(select(KnowledgeDocument).where(KnowledgeDocument.status=='published'))).all())
        for row in rows:
            if source_is_plan(row.filename):
                docs = project(row.id, row.filename, row.text, row.track, row.language)
                report['documents'].append({'document_id': row.id, 'filename': row.filename,
                    'language': row.language or infer_language(row.filename),
                    'excluded_by_curation': True, 'reference_chunks': len(docs),
                    'reason': 'Authoring plan; intentionally withheld from learner retrieval.'})
                if docs:
                    report['failures'].append(row.id)
                continue
            docs = project(row.id, row.filename, row.text, row.track, row.language)
            # Report the scope actually used by the learner retrieval projection,
            # including validated front matter on older uploads with a NULL DB tag.
            language = (docs[0].metadata['language'] if docs else
                        row.language or infer_language(row.filename) or ALL_LANGUAGES)
            subject = docs[0].metadata.get('subject') if docs else None
            # Expected source is known independently from the ranking result.
            question = benchmarks.get(row.filename, {}).get('question') or 'Explain ' + row.filename.rsplit('.',1)[0].replace(' — Curriculum Blueprint','')
            # Compare within the declared subject when present. Searching the
            # entire multi-language upload pool can bury a correct framework
            # reference beneath unrelated lexical matches and produce false fails.
            retrieved = await search(session, question, row.track, language, subject=subject)
            wrong = await search(session, question, row.track, 'javascript' if language=='java' else 'java', subject=subject)
            found = any(d.metadata['document_id']==row.id for d in retrieved)
            no_cross_language = language == ALL_LANGUAGES or all(d.metadata['document_id']!=row.id for d in wrong)
            safe_meta = all(d.metadata['contains_answer'] is False and d.metadata['language'] in (language, ALL_LANGUAGES) and d.metadata['verified'] is False for d in docs)
            item = {'document_id':row.id, 'filename':row.filename, 'track':row.track,
                'stored_language':row.language, 'language':language,
                'original_characters':len(row.text), 'original_sha256':hashlib.sha256(row.text.encode()).hexdigest(),
                'reference_chunks':len(docs), 'reference_characters':sum(len(d.page_content) for d in docs),
                'question':question, 'source_found_at_4':found, 'wrong_language_excluded':no_cross_language,
                'approval_fingerprint':hashlib.sha256(json.dumps([row.status,row.reviewed_by,str(row.reviewed_at),row.review_note]).encode()).hexdigest(),
                'revision':docs[0].metadata['revision'] if docs else None}
            report['documents'].append(item)
            if not (found and no_cross_language and safe_meta):
                report['failures'].append(row.id)
    return report


if __name__ == '__main__':
    result = asyncio.run(audit())
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result['failures']))
