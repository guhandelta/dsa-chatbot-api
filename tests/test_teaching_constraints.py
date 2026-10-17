from app.services.teaching_constraints import constraints
from app.services.code_runner import run_suite


def test_java_sorted_and_hashed_equivalence_are_not_interchangeable():
    code='''public int[] sizes(String a,String b){
        java.util.Set<String> hash=new java.util.HashSet<>();
        java.util.Set<String> tree=new java.util.TreeSet<>(String.CASE_INSENSITIVE_ORDER);
        hash.add(a);hash.add(b);tree.add(a);tree.add(b);
        return new int[]{hash.size(),tree.size()};
    }'''
    result=run_suite({'java':code},{'java':'sizes'},
        [['A','a'],['B','b'],['Same','Same'],['Left','Right'],['Map','map'],['X','Y']],
        [[2,1],[2,1],[1,1],[2,2],[2,1],[2,2]])
    assert result['can_publish'],result
    assert 'TreeMap/TreeSet' in constraints('java') and 'comparator' in constraints('java')


def test_javascript_arrays_have_sparse_object_property_semantics():
    code='function inspect(n){const a=[];a[n]=1;a.note=2;return [a.length,Object.keys(a).length,0 in a];}'
    cases=[[n] for n in (1,2,10,100,1000,10000)]
    expected=[[n+1,2,False] for [n] in cases]
    result=run_suite({'javascript':code},{'javascript':'inspect'},cases,expected)
    assert result['can_publish'],result
    assert 'does not guarantee' in constraints('javascript')


def test_known_overgeneralizations_are_withheld_but_qualified_claims_survive():
    from app.services.teaching_constraints import qualification_guard as guard
    assert guard('Both maps and sets use hashCode for equality.', 'java')
    assert guard('Arrays store elements in contiguous memory.', 'javascript')
    assert guard('HashMap uses hashCode; TreeMap uses comparator ordering.', 'java') is None
    assert guard('The specification does not guarantee contiguous array storage.', 'javascript') is None
    assert guard('ArrayList has resizable capacity.', 'java') is None
