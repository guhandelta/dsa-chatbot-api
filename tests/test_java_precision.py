import pytest
from app.services.code_runner import available_languages
from app.services.content_catalog import reference_solution
from app.services.precision import differential_fuzz,measure_complexity,extract_fn_name
from app.services.timing import scale_cases

pytestmark=pytest.mark.skipif(not available_languages().get('java'),reason='JDK unavailable')


def test_java_fuzzing_executes_reference_and_detects_bug():
    ref,fn=reference_solution('binary-search','java')
    good=differential_fuzz('binary-search',ref,fn,ref,fn,'java',iterations=30,seed=7)
    assert good.ran and good.passed==good.total==30 and not good.counterexamples,good
    bad='public int search(int[] nums, int target) { return -1; }'
    report=differential_fuzz('binary-search',bad,'search',ref,fn,'java',iterations=30,seed=7)
    assert report.ran and report.counterexamples and report.passed<report.total,report


def test_java_timing_uses_growing_workloads_and_inprocess_measurements():
    ref,fn=reference_solution('contains-duplicate','java')
    cases=scale_cases('contains-duplicate')
    assert [len(c[0]) for c in cases]==[128,256,512,1024]
    report=measure_complexity(ref,fn,cases,'java')
    assert report.ran and len(report.timings)==4,report.note
    assert report.sizes==[128,256,512,1024]
    assert extract_fn_name(ref,'java')==fn


def test_nonincreasing_workload_is_not_reported_as_a_measurement():
    report=measure_complexity('public int f(int[] a){return 1;}','f',[[[1,2]],[[1]],[[1]]],'java')
    assert not report.ran
