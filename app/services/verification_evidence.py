"""Persist version-bound execution evidence without claiming factual certification."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from app.core.config import settings

DATA_DIR = Path(__file__).resolve().parents[2] / 'data'
EVIDENCE_FILE = DATA_DIR / 'verification' / 'execution.json'
VERIFIER_FILES = ('content_verification.py', 'content_catalog.py', 'code_runner.py',
                  'exec_harness.py', 'script_runners.py', 'execution_adapters.py', 'container_executor.py',
                  'verification_evidence.py')


def verifier_fingerprint():
    digest=hashlib.sha256()
    for name in VERIFIER_FILES:
        digest.update(name.encode());digest.update((Path(__file__).parent/name).read_bytes())
    return digest.hexdigest()


def _read():
    try:
        value=json.loads(EVIDENCE_FILE.read_text())
        if value.get('schema_version')!=1 or not isinstance(value.get('checks'),list):
            return [],'invalid'
        required=('content_id','language','source_path','source_sha256','verifier_sha256','checked_at','status')
        if any(not isinstance(row,dict) or any(not isinstance(row.get(k),str) for k in required)
               or row.get('status') not in ('passed','failed','blocked')
               or not isinstance(row.get('case_count'),int) or row['case_count']<0
               for row in value['checks']):
            return [],'invalid'
        if len({(r['content_id'],r['language']) for r in value['checks']})!=len(value['checks']):
            return [],'invalid'
        return value['checks'],'available'
    except FileNotFoundError:
        return [],'not_recorded'
    except (OSError,ValueError,TypeError,AttributeError):
        return [],'invalid'


def publish_execution(report):
    """Publish outcomes from the offline auditor; only real passing runs earn a pass."""
    import fcntl
    from app.services.content_catalog import find_path
    EVIDENCE_FILE.parent.mkdir(parents=True,exist_ok=True)
    profile=verifier_fingerprint()
    additions=[]
    for result in report['exercises']:
        path=find_path(result['id'])
        if not path:continue
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest!=result.get('source_sha256'):
            raise ValueError('Source changed during verification: '+result['id'])
        execution=result.get('execution') or {}
        passed=(result.get('verified') is True and execution.get('can_publish') is True
                and not execution.get('unverified') and bool(execution.get('results'))
                and all(r.get('status')=='passed' for r in execution['results']))
        status='passed' if passed else ('failed' if any(r.get('status')=='failed' for r in execution.get('results',[])) else 'blocked')
        additions.append({'content_id':result['id'],'language':result['language'],
                          'source_path':path.relative_to(DATA_DIR).as_posix(),'source_sha256':digest,
                          'verifier_sha256':profile,'checked_at':report['checked_at'],'status':status,
                          'case_count':result.get('case_count',0), 'issues':result.get('issues',[]),
                          'environment':{'backend':settings.exec_backend,'container_image':settings.exec_container_image if settings.exec_backend=='docker' else None}})
    with EVIDENCE_FILE.with_suffix('.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        previous,state=_read()
        if state=='invalid':raise ValueError('Invalid existing execution evidence; repair before publication')
        checks={(r['content_id'],r['language']):r for r in previous}
        checks.update({(r['content_id'],r['language']):r for r in additions})
        payload={'schema_version':1,'updated_at':datetime.now(timezone.utc).isoformat(),
                 'scope':'Execution on recorded fixtures only; factual and teaching review are separate',
                 'checks':[checks[k] for k in sorted(checks)]}
        pending=EVIDENCE_FILE.with_suffix('.pending');pending.write_text(json.dumps(payload,indent=2)+'\n');pending.replace(EVIDENCE_FILE)
    return len(additions)


def execution_summary(source_paths):
    checks,state=_read();paths={p.relative_to(DATA_DIR).as_posix():p for p in source_paths}
    counts=Counter();by_language=defaultdict(Counter);content=set();cases=0;dates=[]
    profile=verifier_fingerprint();digests={}
    for row in checks:
        path=paths.get(row.get('source_path'))
        if path is None:continue
        if path not in digests:digests[path]=hashlib.sha256(path.read_bytes()).hexdigest()
        status=row.get('status','blocked')
        environment=row.get('environment',{})
        environment_changed=(environment.get('backend')!=settings.exec_backend
                             or (settings.exec_backend=='docker' and environment.get('container_image')!=settings.exec_container_image))
        if row.get('source_sha256')!=digests[path] or row.get('verifier_sha256')!=profile or environment_changed:
            status='stale'
        if status not in ('passed','failed','blocked','stale'):status='blocked'
        counts[status]+=1;by_language[row['language']][status]+=1
        if status!='stale':
            content.add(row['content_id']);dates.append(row['checked_at'])
            if status=='passed':cases+=row.get('case_count',0)
    return {'evidence_status':state,'passed':counts['passed'],'failed':counts['failed'],
            'blocked':counts['blocked'],'stale':counts['stale'],'checked_content_count':len(content),
            'fixture_case_checks':cases,'last_checked_at':max(dates) if dates else None,
            'by_language':{k:dict(v) for k,v in sorted(by_language.items())},
            'scope':'One check is one content item in one language; passing fixtures does not certify the whole source.'}
