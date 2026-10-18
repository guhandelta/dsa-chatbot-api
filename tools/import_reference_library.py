"""Import non-JS/Java training sources without executing supplied code or paying providers.

Preserves candidate exercises and answers privately, indexes only reference-safe
views, tracks provenance, and quarantines conflicting IDs. Re-running is deterministic.
"""
import argparse
import hashlib
import io
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from app.services.document_parser import parse_pdf
from app.services.knowledge_hygiene import section_chunks, strip_contents

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT/'dsa-chatbot-api/data/reference_library'
LIMIT = 25*1024*1024
PRIMARY = {'java','javascript','js'}
ANSWER_KINDS = {'exercise','coding exercise','coding_exercise','gotcha','common gotcha','common_gotcha','common_gotchas','gotchas','coding_exercises','exercises'}
STOP = re.compile(r'^(?:\d+[.)]?\s+)?(?:coding\s+)?(?:exercises?|exercise\s+bank|practice\s+bank|assessment|answer\s+key|reference\s+solutions?|solutions?|grading)(?:\b|\s)(?![,;])',re.I)


def digest(raw): return hashlib.sha256(raw).hexdigest()


def infer_scope(source):
    low=source.lower()
    for token,lang,subject in [('embedded_c','c','embedded-c'),('embedded_c_','c','embedded-c'),
        ('embedded/','python','embedded-python'),('python django','python','python-django'),
        ('python fastapi','python','python-fastapi'),('python flask','python','python-flask'),
        ('/c++/','cpp','cpp'),('/rust/','rust','rust'),('/typescript/','typescript','typescript'),
        ('/ruby/','ruby','ruby'),('/python/','python','python'),('/c/','c','c'),
        ('tailwind','css','tailwind'),('css','css','css'),('bootstrap','css','bootstrap'),
        ('sass','css','sass'),('/html/','html','html'),('language/html','html','html'),('html','html','html')]:
        if token in low:return lang,subject
    return None


def safe_reference(text):
    """Keep introductory teaching prose before exercises/answer-bearing headings.

    Document blueprints stay unverified references; their full text is preserved
    separately. Never feed a system-prompt PDF into the learner's reference set.
    """
    lines=[]
    for line in text.splitlines():
        s=line.strip()
        is_disclaimer = bool(re.search(r'\b(?:contains?\s+no|not\s+(?:a\s+)?(?:tested\s+)?)\b', s, re.I))
        if not is_disclaimer:
            if re.search(r'answer\s+key|reference\s+solutions?|worked\s+solutions?', s, re.I):break
            if len(s)<140 and STOP.match(s):break
        if s:lines.append(s)
    return '\n'.join(lines)



def docx_text(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        info=z.getinfo('word/document.xml')
        if info.file_size>LIMIT:raise ValueError('DOCX XML exceeds import limit')
        tree=ET.fromstring(z.read(info))
    ns='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    return '\n'.join(''.join(t.text or '' for t in p.iter(ns+'t')) for p in tree.iter(ns+'p'))


def split_text(text, size=1800):
    words=text.split();parts=[];part=[];length=0
    for word in words:
        if length+len(word)+1>size and part:
            parts.append(' '.join(part));part=[];length=0
        part.append(word);length+=len(word)+1
    if part:parts.append(' '.join(part))
    return parts


def normalize(raw, source):
    m=raw.get('metadata') or {}
    language=str(m.get('language') or raw.get('language') or '').lower()
    language={'c++':'cpp','js':'javascript'}.get(language,language)
    if language in PRIMARY:return None
    scope=infer_scope(source)
    if not language:
        scope=scope or (('rust','rust') if raw.get('track')=='rust_dsa' else None)
        if not scope:return None
        language=scope[0]
    subject=language
    if m.get('track') in ('embedded','embedded_c') or raw.get('track') in ('embedded','embedded_c'):
        subject='embedded-'+language
    elif scope and scope[0]==language and ('django' in scope[1] or 'flask' in scope[1] or 'fastapi' in scope[1]):
        subject=scope[1]
    kind=str(m.get('kind') or raw.get('record_type') or 'reference').lower()
    kind={'coding exercise':'exercise','common gotcha':'gotcha','reference guide':'reference','curriculum outline':'curriculum','curriculum_outline':'curriculum','reference_guide':'reference','common_gotchas':'gotcha','coding_exercises':'exercise'}.get(kind,kind)
    contains=kind in ANSWER_KINDS or m.get('contains_answer') is not False if m else kind in ANSWER_KINDS
    text=raw.get('document')
    if not text:
        # Allowlist fields rather than serializing grading, fixes, or answers.
        text='\n'.join(str(raw[k]) for k in ['title','content','summary','invariant','key_terms','recognition_signals','objectives'] if raw.get(k))
        if not text:text=str(raw.get('prompt') or raw.get('gotcha') or '')
    if not isinstance(text,str) or not text.strip():return None
    rid=str(raw.get('id') or digest(json.dumps(raw,sort_keys=True).encode()))
    context={k:str(m.get(k,raw.get(k))) for k in ('platform','runtime','rust_edition','framework_context')
             if m.get(k,raw.get(k)) is not None}
    return {'key':(subject,rid),'document':text,'kind':kind,'language':language,'subject':subject,'context':context,
            'contains_answer':bool(contains),'payload':raw,'source':source}


def build(source_root, output):
    unique={};blocked=set();provenance={};sources=[];conflicts=[];failures=[];skips=Counter();seen_bytes={};aliases={}
    def accept(item):
        if not item:return
        key=item['key'];finger=digest(json.dumps({k:v for k,v in item.items() if k not in ('key','source')},sort_keys=True).encode())
        provenance.setdefault(key,set()).add(item['source'])
        if key in blocked:return
        if key in unique:
            if unique[key][0]!=finger:
                conflicts.append({'subject':key[0],'original_id':key[1],'sources':sorted(provenance[key])})
                unique.pop(key);blocked.add(key)
            else:skips['duplicate_records']+=1
        else:unique[key]=(finger,item)
    def consume(raw, source, suffix):
        if len(raw)>LIMIT:raise ValueError('Source member exceeds import limit')
        sha=digest(raw);sources.append({'path':source,'sha256':sha,'bytes':len(raw)})
        byte_key=(sha,infer_scope(source))
        if byte_key in seen_bytes:
            aliases.setdefault(seen_bytes[byte_key],set()).add(source)
            skips['duplicate_files']+=1
            # Preserve provenance even when a byte-identical source is skipped.
            return
        seen_bytes[byte_key]=source
        aliases.setdefault(source,set()).add(source)
        if suffix=='.jsonl':
            for number,line in enumerate(raw.decode('utf-8-sig').split('\n'),1):
                if not line.strip():continue
                try:
                    r=json.loads(line)
                    if not isinstance(r,dict):raise ValueError('Record must be an object')
                    item=normalize(r,source)
                    if item:accept(item)
                    else:skips['primary_or_unclassified_records']+=1
                except Exception as exc:failures.append({'source':source,'line':number,'error':str(exc)[:180]})
        elif suffix in ('.docx','.pdf','.md','.txt'):
            scope=infer_scope(source)
            if not scope:skips['architecture_or_unclassified_documents']+=1;return
            if suffix=='.docx': text=docx_text(raw)
            elif suffix=='.pdf': text=parse_pdf(raw)
            else: text=raw.decode('utf-8-sig', errors='ignore')
            safe=safe_reference(strip_contents(text))
            if len(safe)<80:failures.append({'source':source,'error':'No usable reference prose'});return
            for i,part in enumerate(section_chunks(safe)):
                accept({'key':(scope[1],'section-'+sha+'-'+str(i)), 'document':part,
                    'kind':'reference','language':scope[0],'subject':scope[1],'contains_answer':False,
                    'payload':{'source_sha256':sha,'full_text':text if i==0 else '', 'verification':'not_executed',
                               'chunking':'heading-sections-v1'},'source':source})
    for path in sorted(source_root.rglob('*')):
        if not path.is_file():continue
        rel=path.relative_to(source_root).as_posix();suffix=path.suffix.lower()
        # Exported candidates contain duplicate batch/combined views plus
        # evaluation-only queries. Only the dedicated validated importer may
        # promote them; a legacy source scan must never ingest the archive.
        if rel.startswith('generated/') or rel.startswith('generated-gap-fill/'):
            skips['generated_candidate_exports']+=1;continue
        if '/JS/' in '/'+rel or '/Java/' in '/'+rel:
            skips['primary_source_files']+=1;continue
        try:
            if suffix=='.zip':
                with zipfile.ZipFile(path) as z:
                    total=sum(i.file_size for i in z.infolist())
                    if total>400*1024*1024:raise ValueError('Archive expansion exceeds import limit')
                    for entry in sorted(z.infolist(),key=lambda i:i.filename):
                        ext=Path(entry.filename).suffix.lower()
                        if ext in ('.jsonl','.docx','.pdf'):
                            if entry.file_size>LIMIT:raise ValueError('Archive member exceeds import limit')
                            consume(z.read(entry),rel+'!'+entry.filename,ext)
            elif suffix in ('.jsonl','.pdf','.docx','.md','.txt'):
                consume(path.read_bytes(),rel,suffix)
            else:skips['non_corpus_files']+=1
        except Exception as exc:failures.append({'source':rel,'error':str(exc)[:180]})
    seed=ROOT/'dsa-chatbot-api/data/curriculum/spring-starter.jsonl'
    if seed.exists():
        for line in seed.read_text().splitlines():
            raw=json.loads(line);m=raw['metadata']
            accept({'key':(m['subject'],raw['id']),'document':raw['document'],'kind':'reference',
                    'language':'java','subject':m['subject'],'contains_answer':False,
                    'payload':raw,'source':m['doc_url']})
    rows=[]
    for key,(_,item) in sorted(unique.items()):
        context=item.get('context',{})
        # Verification status lives in metadata; only version/platform context is kept in the text.
        header=('Context: '+'; '.join(f'{k}: {v}' for k,v in context.items())+'\n') if context else ''
        rows.append({'id':'ref-'+digest(json.dumps(key).encode())[:24],'document':header+item['document'],
            'metadata':{'source':'reference-library','kind':item['kind'],'language':item['language'],
                'subject':item['subject'],'track':'language','contains_answer':item['contains_answer'],
                'verified':False,'executable':False,'origin':item['source'],**context},
            'provenance':sorted({alias for origin in provenance[key] for alias in aliases.get(origin,{origin})}),'payload':item['payload']})
    # Preserve previously promoted generated references, while keeping exported
    # candidates/evaluation files out of the legacy source normalization path.
    # Their stable IDs and explicit framework scopes must survive a rebuild.
    active_file = output/'records.jsonl'
    retained_generated = []
    if active_file.exists():
        from app.services.reference_library import eligible as is_public_reference
        current_ids = {r['id'] for r in rows}
        for line in active_file.open(encoding='utf-8'):
            if not line.strip(): continue
            record = json.loads(line)
            metadata = record.get('metadata', {})
            promoted = (metadata.get('dataset_version') == 'knowledge-gap-fill-v1'
                        or metadata.get('dataset_version') == 'framework-sections-v1'
                        or metadata.get('origin') in ('generated_batch_001', 'generated_batch_002')
                        or str(metadata.get('origin', '')).startswith('generated_gap_fill_'))
            if promoted and record['id'] not in current_ids and is_public_reference(record):
                retained_generated.append(record)
                current_ids.add(record['id'])
        rows.extend(retained_generated)
    from app.services.knowledge_hygiene import clean_reference_rows, VERSION
    rows, quarantine, redirects = clean_reference_rows(rows)
    from app.services.reference_library import eligible
    manifest={'format_version':1,'record_count':len(rows),'retrievable_count':sum(eligible(r) for r in rows),
        'by_subject':dict(Counter(r['metadata']['subject'] for r in rows)),
        'source_files':sources,'skipped':dict(skips),'conflicting_ids_quarantined':conflicts,'errors':failures,
        'curation_version':VERSION, 'quarantined_records':len(quarantine),
        'promoted_generated_records_preserved':len(retained_generated),
        'duplicate_redirects':redirects,
        'notes':['No supplied code was executed. Source verification claims are not executable certification.',
                 'Exercise/gotcha candidates and their answers are preserved but excluded from learner retrieval.',
                 'Blueprint reference views stop at detected exercise/answer headings; editorial review remains required.',
                 'Duplicate archive members are skipped; original archives remain the provenance record.',
                 'JavaScript and Java fundamentals were not reimported. Spring seed references are a separate requested subject.']}
    output.mkdir(parents=True,exist_ok=True)
    pending=output/'records.pending'
    pending.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows))
    pending.replace(output/'records.jsonl')
    pending=output/'manifest.pending'
    pending.write_text(json.dumps(manifest,indent=2)+'\n')
    pending.replace(output/'manifest.json')
    # Never overwrite the archive of earlier curation decisions on reimport.
    archive = output/'quarantine.jsonl'
    previous = [json.loads(line) for line in archive.open() if line.strip()] if archive.exists() else []
    retained = {(q['record']['id'], digest(json.dumps(q['record'],sort_keys=True).encode())): q for q in previous + quarantine}
    pending=output/'quarantine.pending'
    pending.write_text(''.join(json.dumps(q,ensure_ascii=False,sort_keys=True)+'\n' for q in retained.values()))
    pending.replace(archive)
    manifest['quarantined_records'] = len(retained)
    manifest['active_sha256'] = digest((output/'records.jsonl').read_bytes())
    pending=output/'manifest.pending'
    pending.write_text(json.dumps(manifest,indent=2)+'\n')
    pending.replace(output/'manifest.json')
    try:
        from app.services.training_registry import record_training_event
        record_training_event(
            technology='reference-library',
            action='import_reference_library',
            category='multi_technology',
            source=str(source_root),
            record_count=manifest['record_count'],
            status='completed',
            details={'by_subject': manifest['by_subject'], 'retrievable_count': manifest['retrievable_count']}
        )
    except Exception:
        pass
    print(json.dumps({k:manifest[k] for k in ('record_count','retrievable_count','by_subject','skipped')},indent=2))
    print('Quarantined conflicts:',len(conflicts),'Parse errors:',len(failures))
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=ROOT/'Training Data');p.add_argument('--output',type=Path,default=OUTPUT)
    args=p.parse_args();build(args.source,args.output)
