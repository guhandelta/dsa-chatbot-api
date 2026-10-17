#!/usr/bin/env python3
"""Explicit container boundary/runtime checks. Refuses host execution.

No LLM calls. Uses only synthetic code, a scratch mount and a private host marker.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.core.config import settings
from app.services.code_runner import _run, run_suite
from app.services.container_executor import command


def running():
    result=subprocess.run(['docker','ps','--filter','name=dsa-run-','--format','{{.ID}}'],capture_output=True,text=True,timeout=5,check=True)
    return set(result.stdout.split())


def verify():
    if settings.exec_backend!='docker':
        raise ValueError('Refusing isolation checks: EXEC_BACKEND must be docker')
    checks={}
    before=running()
    with tempfile.TemporaryDirectory(prefix='dsa-host-proof-') as private,tempfile.TemporaryDirectory(prefix='dsa-isolation-') as scratch:
        root=Path(scratch)
        command(['python3','-V'],root,'configuration-check')
        secret=Path(private)/'host-marker';secret.write_text('MUST_NOT_BE_VISIBLE')
        programs={
            'host_file_hidden':f"from pathlib import Path\nprint(not Path({str(secret)!r}).exists())",
            'network_denied':"import socket\ntry:\n socket.create_connection(('1.1.1.1',53),.5)\n print(False)\nexcept OSError:\n print(True)",
            'root_readonly':"mounts=[line.split() for line in open('/proc/mounts')]\nprint(any(m[1]=='/' and 'ro' in m[3].split(',') for m in mounts))",
            'environment_stripped':"import os\nprint(os.getenv('DSA_ISOLATION_SECRET') is None)",
            'capabilities_dropped':"s=dict(line.split(':',1) for line in open('/proc/self/status') if ':' in line)\nprint(int(s['CapEff'].strip(),16)==0 and int(s['NoNewPrivs'].strip())==1)",
            'memory_limit':f"from pathlib import Path\nprint(int(Path('/sys/fs/cgroup/memory.max').read_text())=={settings.exec_memory_mb*1024*1024})",
            'process_limit':f"import subprocess,sys\nfrom pathlib import Path\nassert int(Path('/sys/fs/cgroup/pids.max').read_text())=={settings.exec_max_processes}\nchildren=[]\ntry:\n for _ in range({settings.exec_max_processes+8}):\n  children.append(subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)']))\n print(False)\nexcept OSError:\n print(True)\nfinally:\n for child in children: child.kill()",
        }
        os.environ['DSA_ISOLATION_SECRET']='HOST_ONLY_TEST_MARKER'
        try:
            for label,code in programs.items():
                (root/'probe.py').write_text(code)
                try:
                    rc,out,err=_run(['python3','probe.py'],root)
                    checks[label]={'passed':rc==0 and out.strip()=='True','exit_code':rc,'stderr':err[:300]}
                except RuntimeError as exc:
                    checks[label]={'passed':False,'error_type':type(exc).__name__}
            (root/'probe.py').write_text('print("x" * 1000000)')
            rc,out,err=_run(['python3','probe.py'],root)
            checks['output_bounded']={'passed':rc==0 and len(out.encode())<=settings.exec_max_output_bytes,'captured_bytes':len(out.encode())}
            (root/'probe.py').write_text('while True: pass')
            rc,out,err=_run(['python3','probe.py'],root)
            checks['timeout']={'passed':rc!=0,'exit_code':rc,'stderr':err[:300]}
            solutions={
                'python':'def add(a,b): return a+b',
                'javascript':'function add(a,b){return a+b;}',
                'java':'public int add(int a,int b){return a+b;}',
                'c':'long long add(long long a,long long b){return a+b;}',
                'cpp':'long long add(long long a,long long b){return a+b;}',
                'rust':'fn add(a:i64,b:i64)->i64 {a+b}',
            }
            report=run_suite(solutions,{lang:'add' for lang in solutions},[[1,2],[0,0],[-1,1],[2,3],[-2,-3],[100,200]],[3,0,0,5,-5,300])
            checks['six_language_execution']={'passed':report['can_publish'],'results':report['results']}
        finally:
            os.environ.pop('DSA_ISOLATION_SECRET',None)
    leftover=running()-before
    checks['container_cleanup']={'passed':not leftover,'new_running_container_count':len(leftover)}
    return {'backend':'docker','image':settings.exec_container_image,'checks':checks}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=verify()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    raise SystemExit(int(not all(c['passed'] for c in result['checks'].values())))
