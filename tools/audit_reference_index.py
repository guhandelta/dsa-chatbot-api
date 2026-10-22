"""Read-only consistency check of the published index against active references.

No provider calls. A stale, withdrawn or missing document is reported rather than
re-embedded or silently repaired.
"""
import argparse
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path
from app.core.config import settings
from app.services.reference_library import records,eligible
from app.services.reference_semantics import MANIFEST,MODEL

ROOT=Path(__file__).resolve().parents[2]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reconcile-manifest',action='store_true',help='Repair snapshot metadata only after every stored document and scalar metadata field matches')
    args=parser.parse_args()
    import chromadb
    manifest=json.loads(MANIFEST.read_text())
    rows=[r for r in records() if eligible(r)]
    digest=hashlib.sha256(json.dumps([(r['id'],r['document'],r['metadata']) for r in rows],sort_keys=True).encode()).hexdigest()
    collection=chromadb.PersistentClient(path=settings.chroma_persist_dir).get_collection(manifest['collection'])
    stored=collection.get(include=['documents','metadatas'])
    by_id={rid:(text,meta) for rid,text,meta in zip(stored['ids'],stored['documents'],stored['metadatas'])}
    active={r['id']:r for r in rows}
    missing=sorted(active.keys()-by_id.keys())
    stale=sorted(by_id.keys()-active.keys())
    mismatches=[]
    for rid in active.keys()&by_id.keys():
        row=active[rid];text,meta=by_id[rid];expected=row['metadata']
        if text!=row['document'] or {k:v for k,v in meta.items() if k!='problem_id'}!=expected:
            mismatches.append(rid)
    result={'checked_at':datetime.now(timezone.utc).isoformat(),'collection':manifest['collection'],
            'eligible_active_records':len(rows),'indexed_records':len(by_id),
            'source_hash_matches':digest==manifest['source_sha256'],
            'model_matches':manifest['model']==MODEL==collection.metadata.get('embedding_model'),
            'missing_ids':missing,'withdrawn_ids_still_indexed':stale,'content_or_scope_mismatches':sorted(mismatches),
            'provider_calls':0}
    if args.reconcile_manifest and not(missing or stale or mismatches) and result['model_matches'] and not result['source_hash_matches']:
        previous=manifest['source_sha256']
        manifest.update(source_sha256=digest,revalidated_at=result['checked_at'],previous_source_sha256=previous,
                        snapshot_reconciliation='All stored documents and metadata exactly matched the active corpus; no embedding changes')
        manifest['embedding_build_source_sha256']=collection.metadata.get('source_sha256')
        pending=MANIFEST.with_suffix('.pending');pending.write_text(json.dumps(manifest,indent=2)+'\n');pending.replace(MANIFEST)
        result.update(source_hash_matches=True,previous_source_sha256=previous,snapshot_reconciled=True)
    result['passed']=result['source_hash_matches'] and result['model_matches'] and not(missing or stale or mismatches)
    path=ROOT/'reports/knowledge-base-training-2026-10-18/semantic-index-integrity.json'
    path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    if not result['passed']:raise SystemExit(1)

if __name__=='__main__':main()
