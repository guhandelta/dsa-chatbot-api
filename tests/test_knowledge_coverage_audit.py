from tools.audit_knowledge_coverage import summarize, audit


def row(rid, document, kind='concept', answer=False):
    return {'id':rid, 'document':document, 'metadata':{'language':'ruby',
        'subject':'ruby', 'kind':kind, 'contains_answer':answer}, 'provenance':['source']}


def test_private_answers_cannot_inflate_learner_topic_coverage():
    result=summarize([('reference_library',row('safe','Variables and values.')),
                      ('reference_library',row('private','Graph traversal and dynamic programming.', 'exercise',True))])
    subject=result['subjects'][0]
    assert subject['topic_evidence_ids']['values-types']==['safe']
    assert subject['topic_evidence_ids']['graphs']==[]
    assert subject['topic_evidence_ids']['dynamic-programming']==[]
    assert subject['candidate_exercises']==1 and subject['quality_status']=='not_certified'


def test_duplicate_ids_are_namespaced_and_safety_errors_are_reported():
    a=row('id','Reference')
    assert not summarize([('canonical',a),('reference_library',a)])['structural_findings']
    errors=summarize([('reference_library',a),('reference_library',a),
                      ('reference_library',row('leak','Answer', 'exercise',False))])['structural_findings']
    assert {e['issue'] for e in errors}=={'missing_or_duplicate_id','answer_bearing_kind_marked_safe'}


def test_entire_packaged_inventory_includes_all_framework_subjects_and_scoped_retrieval():
    result=audit()
    assert not result['structural_findings']
    subjects={s['subject']:s for s in result['subjects']}
    assert {'ruby','typescript','c','cpp','rust','python','java','javascript',
            'spring-core','spring-mvc','spring-boot','spring-data','spring-security','spring-testing',
            'python-django','python-fastapi','python-flask','embedded-c','embedded-python'} <= subjects.keys()
    assert all(s['quality_status']=='not_certified' for s in subjects.values())
    assert all(p['scope_ok'] for s in subjects.values() for p in s['retrieval_probes'])
    assert subjects['typescript']['execution_adapter_available_in_code'] is False
    assert subjects['ruby']['execution_adapter_available_in_code'] is False
    assert subjects['rust']['application_reference_extractor_supported'] is False
    assert subjects['python']['learner_reference_admission_gate_enabled'] is False
    assert sum(s['records'] for s in subjects.values())==result['records']
