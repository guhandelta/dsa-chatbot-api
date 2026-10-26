"""Rebuild framework references from explicit Markdown sections, with reversible curation.

Run with --apply to publish. No model calls or exercise ingestion. Stable heading IDs
make reruns idempotent; original mixed records remain in quarantine and backups.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil

API = Path(__file__).resolve().parents[1]
ROOT = API.parent
DATASET = 'framework-sections-v1'


def headings(text, level):
    """Split outside fenced code; retain each complete code example."""
    result, chunk, fence = [], [], None
    for line in text.splitlines(keepends=True):
        match = re.match(r'^\s*(`{3,}|~{3,})', line)
        if match:
            marker = match[1]
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
        if fence is None and re.match(r'^' + '#' * level + r' ', line):
            if chunk:
                result.append(''.join(chunk).strip())
            chunk = []
        chunk.append(line)
    if chunk:
        result.append(''.join(chunk).strip())
    if fence:
        raise ValueError('Unclosed code fence')
    return result


def framework_rows():
    configs = [
        ('output/pdf/css-sass-bootstrap-training/CSS_Sass_Bootstrap_Architecture_Curriculum.md',
         {**{n:'css' for n in range(2,9)},9:'sass',10:'sass',**{n:'bootstrap' for n in range(11,15)},
          **{n:'css' for n in range(15,22)},23:'css',24:'css',25:'sass',26:'bootstrap',27:'bootstrap',28:'sass'}),
        ('output/pdf/tailwind-bulma-shadcn-training/Tailwind_Bulma_Shadcn_Training_Curriculum.md',
         {**{n:'tailwind' for n in range(4,9)},**{n:'bulma' for n in range(9,14)},
          **{n:'shadcn' for n in range(14,18)},20:'tailwind',21:'bulma',22:'shadcn'}),
    ]
    rows, excluded = [], []
    for source, mapping in configs:
        # Clean checkouts use the versioned snapshot when operator sources
        # outside the repository are unavailable.
        source_path = ROOT/source
        if not source_path.exists():
            source_path = API/'data/reference_sources'/Path(source).name
        raw = source_path.read_text()
        digest = hashlib.sha256(raw.encode()).hexdigest()
        for section in headings(raw,2):
            match = re.match(r'## (\d+) (.+)', section)
            if not match:
                continue
            number, title = int(match[1]),match[2]
            if number not in mapping:
                excluded.append({'source':source,'section':title,'reason':'Overview, mixed integration, lab, assessment, or production metadata'})
                continue
            subject = mapping[number]
            for piece in headings(section,3):
                subtitle = piece.splitlines()[0].lstrip('# ').strip()
                if re.search(r'\b(exercises|assessment|rubric)\b',subtitle,re.I):
                    excluded.append({'source':source,'section':subtitle,'reason':'Learner exercise section deferred'})
                    continue
                if len(piece.split()) < 20:
                    continue
                rid = 'ref-framework-v1-' + hashlib.sha256((source+'\n'+title+'\n'+subtitle).encode()).hexdigest()[:24]
                rows.append({'id':rid,'document':f'{subject} reference — {title}\n\n{piece}',
                    'metadata':{'language':'css','subject':subject,'track':'language','kind':'reference',
                                'contains_answer':False,'verified':False,'executable':False,
                                'source':'reference-library','origin':source,'dataset_version':DATASET,
                                'title':subtitle,'review_status':'scope_reviewed_claims_not_certified',
                                'baseline':'Source edition 2026-10-16; inspect installed framework/browser versions'},
                    'provenance':[source], 'payload':{'source_sha256':digest,'section':title,'subsection':subtitle}})
    assert len({r['id'] for r in rows}) == len(rows)
    return rows,excluded


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    from app.services.knowledge_hygiene import quarantine_reason, VERSION
    from app.services.reference_library import eligible
    library=API/'data/reference_library'; path=library/'records.jsonl'
    original=path.read_bytes()
    old=[json.loads(line) for line in original.splitlines() if line.strip()]
    new,excluded=framework_rows()
    quarantined=[{'reason':quarantine_reason(r),'record':r} for r in old if quarantine_reason(r)]
    active=[r for r in old if not quarantine_reason(r) and r['metadata'].get('dataset_version')!=DATASET]+new
    report={'mode':'apply' if args.apply else 'dry_run','before':len(old),'after':len(active),
            'framework_records':len(new),'by_subject':dict(Counter(r['metadata']['subject'] for r in new)),
            'quarantined':len(quarantined),'reasons':dict(Counter(q['reason'] for q in quarantined)),
            'excluded_sections':excluded,'remaining':'Claim-level accuracy and runtime compatibility are not certified.'}
    if args.apply:
        backup=library/'import_backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        backup.mkdir(parents=True,mode=0o700)
        for name in ('records.jsonl','manifest.json','quarantine.jsonl'):
            if (library/name).exists():shutil.copy2(library/name,backup/name)
        archive=library/'quarantine.jsonl'
        previous=[json.loads(line) for line in archive.open() if line.strip()] if archive.exists() else []
        archive_rows={q['record']['id']:q for q in previous+quarantined}
        encoded=''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in active)
        manifest=json.loads((library/'manifest.json').read_text())
        manifest.update(record_count=len(active),retrievable_count=sum(eligible(r) for r in active),
                        by_subject=dict(Counter(r['metadata']['subject'] for r in active)),
                        curation_version=VERSION,quarantined_records=len(archive_rows),
                        active_sha256=hashlib.sha256(encoded.encode()).hexdigest())
        if path.read_bytes()!=original:raise RuntimeError('Concurrent corpus update; retry')
        for target,value in [(archive,''.join(json.dumps(q,ensure_ascii=False)+'\n' for q in archive_rows.values())),
                             (path,encoded),(library/'manifest.json',json.dumps(manifest,indent=2)+'\n')]:
            pending=target.with_suffix('.pending');pending.write_text(value);pending.replace(target)
        report['backup']=str(backup)
        output=ROOT/'reports/knowledge-base-training-2026-10-18/section-repair.json'
        if output.exists():
            output=output.with_name('section-repair-latest.json')
        output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='excluded_sections'},indent=2))

if __name__=='__main__':main()
