"""Build an isolated, explicitly labelled supplemental semantic collection.

Every learner-retrievable reference record is indexed, so semantic search covers
each subject and not only the curated supplements. Reruns resume: records already
in the collection for the same source hash are not embedded again.
"""
import hashlib
import json
import time
from collections import Counter
from datetime import datetime, timezone
from app.core.config import settings
from app.services.reference_library import records, eligible
from app.services.reference_semantics import embeddings, MODEL, MANIFEST

BATCH = 100


def embed_with_retry(embed, texts, attempts=6):
    for attempt in range(1, attempts + 1):
        try:
            return embed.embed_documents(texts)
        except Exception as exc:
            message = str(exc).lower()
            if attempt == attempts or not ('429' in message or 'quota' in message or 'exhausted' in message
                                           or 'timeout' in message or 'unavailable' in message):
                raise
            wait = min(90, 10 * 2 ** (attempt - 1))
            print(f'Embedding provider busy ({exc.__class__.__name__}); retrying in {wait}s', flush=True)
            time.sleep(wait)


def main():
    if settings.vector_store != 'chroma':raise SystemExit('This maintenance command requires the local Chroma backend')
    rows=[r for r in records() if eligible(r)]
    identity=hashlib.sha256(json.dumps([(r['id'],r['document'],r['metadata']) for r in rows],sort_keys=True).encode()).hexdigest()
    name='curated_refs_'+identity[:20]
    import chromadb
    client=chromadb.PersistentClient(path=settings.chroma_persist_dir)
    collection=client.get_or_create_collection(name,metadata={'embedding_model':MODEL,'source_sha256':identity,'hnsw:space':'cosine'})
    if collection.metadata.get('embedding_model')!=MODEL:raise RuntimeError('Embedding identity mismatch')
    existing=set(collection.get(include=[])['ids'])
    pending=[r for r in rows if r['id'] not in existing]
    embed=embeddings()
    for start in range(0,len(pending),BATCH):
        batch=pending[start:start+BATCH]
        vectors=embed_with_retry(embed,[r['document'] for r in batch])
        # Chroma metadata values must be scalars.
        metadatas=[{k:v for k,v in {**r['metadata'],'problem_id':r['id']}.items()
                    if isinstance(v,(str,int,float,bool))} for r in batch]
        collection.add(ids=[r['id'] for r in batch],documents=[r['document'] for r in batch],embeddings=vectors,
                       metadatas=metadatas)
        print(f'Indexed {min(start+BATCH,len(pending))}/{len(pending)} pending references',flush=True)
    assert collection.count()==len(rows)
    report={'collection':name,'provider':'google','model':MODEL,'source_sha256':identity,
            'records':len(rows),'by_subject':dict(sorted(Counter(r['metadata']['subject'] for r in rows).items())),
            'completed_at':datetime.now(timezone.utc).isoformat(),
            'scope':'All learner-retrievable reference records; legacy collection preserved'}
    MANIFEST.parent.mkdir(parents=True,exist_ok=True)
    temp=MANIFEST.with_suffix('.pending');temp.write_text(json.dumps(report,indent=2)+'\n');temp.replace(MANIFEST)
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
