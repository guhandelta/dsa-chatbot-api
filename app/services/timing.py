"""In-process timing inside the same constrained executor as correctness tests."""
import json
import re
import tempfile
from pathlib import Path
from app.core.config import settings
from app.services.code_runner import _run


def scale_cases(problem_id):
    sizes=(128,256,512,1024)
    factories={
        'two-sum':lambda n:[list(range(1,n+1)),3],
        'contains-duplicate':lambda n:[list(range(n))],
        'best-time-to-buy-and-sell-stock':lambda n:[list(range(n))],
        'maximum-subarray':lambda n:[[1]*n],
        'maximum-product-subarray':lambda n:[[1]*n],
        'product-of-array-except-self':lambda n:[[1]*n],
        'binary-search':lambda n:[list(range(n)),-1],
        'container-with-most-water':lambda n:[[1]*n],
        'longest-increasing-subsequence':lambda n:[list(range(n))],
    }
    make=factories.get(problem_id)
    return [make(n) for n in sizes] if make else []


def measure(code,fn,cases,language):
    from app.services.precision import ComplexityReport,_classify
    from app.services import exec_harness as h
    sizes=[len(c[0]) for c in cases if c and isinstance(c[0],list)]
    report=ComplexityReport()
    if len(sizes)!=len(cases) or any(b<=a for a,b in zip(sizes,sizes[1:])):
        report.note='Timing requires strictly increasing array input sizes.'
        return report
    with tempfile.TemporaryDirectory() as td:
        cwd=Path(td)
        if language=='python':
            source='''import json,time,statistics,sys
sys.setrecursionlimit(50000)
__CODE__
cases=json.loads(sys.stdin.read())
results=[]
for case in cases:
    timings=[]
    for repeat in range(7):
        args=json.loads(json.dumps(case))
        start=time.perf_counter()
        __FN__(*args)
        elapsed=time.perf_counter()-start
        if repeat>=2: timings.append(elapsed)
    results.append(statistics.median(timings))
print('__TIMES__'+json.dumps(results))
'''.replace('__CODE__',code).replace('__FN__',fn)
            (cwd/'timing.py').write_text(source)
            command=['python3','timing.py']
        elif language=='javascript':
            source='''__CODE__
const cases=JSON.parse(require('fs').readFileSync(0,'utf8'));
const times=cases.map(c=>{const samples=[];for(let repeat=0;repeat<7;repeat++){
const args=JSON.parse(JSON.stringify(c));const start=process.hrtime.bigint();
__FN__(...args);const elapsed=Number(process.hrtime.bigint()-start)/1e9;
if(repeat>=2)samples.push(elapsed);}return samples.sort((a,b)=>a-b)[2];});
console.log('__TIMES__'+JSON.stringify(times));
'''.replace('__CODE__',code).replace('__FN__',fn)
            (cwd/'timing.js').write_text(source)
            command=['node',f'--max-old-space-size={settings.exec_memory_mb}','timing.js']
        elif language=='java':
            from app.services.exec_harness import TypeSig,java_tool
            # Infer argument types from the workload; the return is discarded.
            sig=h.infer_types(cases,[0]*len(cases))
            if not sig:
                report.note='Java timing cannot express this input shape.';return report
            cls=h._java_class_name(code) or 'Solution'
            built=False
            for width,call in h.CANDIDATES['java']:
                invoke=f'{cls}.{fn}' if call=='static' else f'new {cls}().{fn}'
                blocks=[]
                for case in cases:
                    decls='\n'.join(f'{h._java_decl(t,width)} a{i}={h._java_value(v,t,width)};' for i,(v,t) in enumerate(zip(case,sig.args)))
                    args=', '.join(f'a{i}' for i in range(len(case)))
                    blocks.append('{ double[] times=new double[5]; for(int r=0;r<7;r++){'+decls+f'\nlong start=System.nanoTime(); {invoke}({args}); double elapsed=(System.nanoTime()-start)/1e9; if(r>=2)times[r-2]=elapsed;'+'} java.util.Arrays.sort(times); _emit(times[2]); _flush(); }')
                main=h._JAVA_PRELUDE.replace('__MARKER__',h.RESULT_MARKER)+'\n public static void main(String[] args){'+''.join(blocks)+'}}'
                (cwd/'Main.java').write_text(main);(cwd/f'{cls}.java').write_text(h._java_wrap(code,cls))
                rc,_,_=_run([java_tool('javac'),'-nowarn','Main.java',f'{cls}.java'],cwd,apply_address_space=False)
                if rc==0: built=True;break
            if not built:
                report.note='Could not compile Java timing driver.';return report
            command=[java_tool('java'),f'-Xmx{settings.exec_memory_mb}m','Main']
        else:
            report.note='Unsupported timing language.';return report
        rc,out,err=_run(command,cwd,stdin=json.dumps(cases),apply_address_space=language=='python')
        if rc!=0:
            report.note='Timing unavailable: '+(err or out)[:200];return report
        try:
            times=h._parse_cases(out,len(cases)) if language=='java' else json.loads(next(l[len('__TIMES__'):] for l in out.splitlines() if l.startswith('__TIMES__')))
            if times is None or len(times)!=len(cases): raise ValueError('Missing timing output')
        except (ValueError,StopIteration):
            report.note='Timing output was incomplete.';return report
        report.ran=True;report.sizes=sizes;report.timings=times;report.estimate=_classify(sizes,times)
        report.note='Median in-process timings; runtime/JIT noise may make the estimate inconclusive. This is not a proof of complexity.'
        return report
