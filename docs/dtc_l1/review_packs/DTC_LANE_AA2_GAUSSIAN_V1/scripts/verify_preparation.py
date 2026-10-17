"""Independent small-file audit of the AA2 held preparation and immutable lineage."""
import ast
from common import *


def rows(name):
    with (PACK/name).open() as f:return list(csv.DictReader(f,delimiter='\t'))


def main():
    plans=rows('PRE_REGISTRATION.tsv')
    assert [(r['point'],r['uuid']) for r in plans]==[(p[0],p[1]) for p in POINTS]
    assert len(plans)==len(set(r['uuid'] for r in plans))==4
    budget=json.loads((PACK/'ATTEMPT_BUDGET.json').read_text())
    assert budget['ancestor_actual_starts']==budget['AA2_actual_starts']==0
    assert budget['cumulative_total_actual_start_ceiling']==4
    specs=[]
    for r in plans:
        p=PACK/'specs'/f'{r["point"]}.json';s=json.loads(p.read_text());specs.append(s)
        assert sha(p)==r['spec_sha256']
        assert s['attempt_uuid']==r['uuid'] and s['launch_admitted'] is False
        assert s['candidate_core']==CANDIDATE_CORE and s['candidate_core']!='f8b34dd7a738caddf4f23dd417e34c0b63c206d9'
        assert s['timeout_seconds']==7200 and s['actual_start_limit']==1
        assert s['global_AA_plus_AA2_start_limit']==4
        assert s['Gaussian_members']==510 and s['expected_active_thread_instructions']==283685120
        for c in s['configs']:assert sha(c['path'])==c['sha256']
        opts=options([c['path'] for c in s['configs']]);assert opts==s['expected_effective_options']
        for k,v in {'-gpgpu_n_clusters':64,'-gpgpu_dtc_l1_oo_pib_entries':128,
           '-gpgpu_dtc_l1_physical_lines':640,'-gpgpu_dtc_l1_lower_outstanding_cap':32768,
           '-gpgpu_dtc_l1_tag_banks':4,'-gpgpu_shmem_size':98304,'-gpgpu_flush_l1_cache':1,
           '-gpgpu_dtc_l1_finite_service':1}.items():assert opts[k]==[str(v)]
        assert opts['-gpgpu_clock_domains']==['1410.0:1410.0:1410.0:850.0']
        assert opts['-gpgpu_cache:dl1']==['S:32:128:4,L:T:m:L:L,A:512:8,16:0,32']
        assert s['expected_full_default_and_config_echo']['-gpgpu_dtc_l1_debug_event_limit']==['0']
    allowed={K_OPTION,'-gpgpu_dtc_l1_logical_sets','-gpgpu_dtc_l1_logical_ways'}
    first=specs[0]['expected_full_default_and_config_echo']
    for s in specs:
        echo=s['expected_full_default_and_config_echo']
        assert {k for k in first.keys()|echo.keys() if first.get(k)!=echo.get(k)}<=allowed
    ordered=json.loads((PACK/'ORDERED_KERNELS.json').read_text());members=rows('GAUSSIAN_MEMBERS_SHA256.tsv')
    assert len(ordered)==len(members)==510
    assert [o['ordinal'] for o in ordered]==list(range(1,511))
    assert sum(o['active_instructions'] for o in ordered)==283685120
    for o,m in zip(ordered,members):assert o['member_path']==m['path'] and o['member_sha256']==m['sha256']
    assert sha(PACK/'inputs/Gaussian_kernelslist.g')=='6dc7caba6733657293e8c517467bac28890ae4eb97c732ffd245d7fd1c479fb9'
    matrix=rows('FULL_MATRIX.tsv')
    assert [(r['point'],r['uuid']) for r in matrix]==[(p[0],p[1]) for p in POINTS]
    assert all(r['actual_starts']=='0' and r['cycles']=='UNAVAILABLE' and r['strict']=='NOT_RUN' for r in matrix)
    for _,uid,*_ in POINTS:
        receipt=json.loads((ROOT/'run_receipts'/uid/'STRICT.json').read_text())
        assert receipt['actual_starts']==0 and receipt['status'].startswith('NOT_RUN')
        assert receipt['source_event_count']=='UNAVAILABLE_NOT_ZERO'
        assert (ROOT/'run_receipts'/uid/'STRICT.json').read_bytes()==(PACK/'run_receipts'/uid/'STRICT.json').read_bytes()
    assert not list(ROOT.rglob('RUN_START.json'))
    assert not (ROOT/'attempts').exists()
    binding=json.loads((PACK/'PUBLISHED_BINDINGS.json').read_text())
    assert binding['X_core_fetch_back_commit']==CANDIDATE_CORE
    assert binding['Z2_contract_sha256']==sha(PACK/'inputs/Z2/K1_INTERPRETATION_V2.md')
    assert binding['runtime_pinned_library_resolution'] is True
    for b in binding['candidate_artifacts']:assert sha(b['path'])==b['sha256']
    assert json.loads((PACK/'CPU_COUNTER_CONTRACT_CHECK.json').read_text())['status']=='PASS_CPU_COUNTER_CONTRACT_ONLY'
    source=json.loads((PACK/'PROVENANCE.json').read_text())
    for r in source:assert sha(PACK/r['destination'])==r['sha256']
    if (PACK/'EFFECTIVE_OPTIONS_CLOSURE.json').exists():
        closure=json.loads((PACK/'EFFECTIVE_OPTIONS_CLOSURE.json').read_text())
        assert closure['omitted_K0_equals_explicit_zero'] is True
        for profile in closure['points']:
            assert profile['total_actual_options']==267
            assert profile['counts']=={'CORE_CPU_PARSER':230,'CORE_RUNTIME_INHERITED':23,'FRAMEWORK_TRACE_INHERITED':14}
            assert sha(PACK/'effective_options'/f'{profile["point"]}.tsv')==profile['profile_sha256']
    if (PACK/'Y2_GATE_BINDING.json').exists():
        y=json.loads((PACK/'Y2_GATE_BINDING.json').read_text())
        assert y['target_Core']==CANDIDATE_CORE and y['exact_option']==K_OPTION
        assert y['accepted_PASS_K1_OO_MODEL_SCOPE'] and y['accepted_K0_equivalence']
        for record in y['provenance']:assert sha(PACK/record['destination'])==record['sha256']
    if (PACK/'RAW_FILES_SHA256.tsv').exists():
        for record in rows('RAW_FILES_SHA256.tsv'):
            assert sha(ROOT/record['path'])==record['sha256']
            assert (ROOT/record['path']).stat().st_size==int(record['bytes'])
    # All old AA V1 files are inherited intact, including in the old worktree.
    original_fw=Path('/workspace/worktrees/accel-sim-iscas2027-dtc-lane-aa-flush-factorial-174-v1')
    oldfiles=git(FW_REPO,'ls-tree','-r','--name-only',AA_SHA,OLD_PACK).splitlines()
    for rel in oldfiles:
        data=blob(FW_REPO,AA_SHA,rel)
        assert (FW/rel).read_bytes()==data and (original_fw/rel).read_bytes()==data
    # These audit programs never create simulator processes or modify old locks.
    for file in (PACK/'scripts').glob('*.py'):
        tree=ast.parse(file.read_text())
        for node in ast.walk(tree):
            if isinstance(node,ast.Attribute):assert node.attr not in ['Popen','kill','killpg','rmtree','unlink']
    for file in PACK.rglob('*.json'):json.loads(file.read_text())
    if (PACK/'FILES_SHA256.tsv').exists():
        fs=rows('FILES_SHA256.tsv')
        assert {r['path'] for r in fs}=={str(f.relative_to(PACK)) for f in PACK.rglob('*') if f.is_file() and f!=PACK/'FILES_SHA256.tsv'}
        for r in fs:assert sha(PACK/r['path'])==r['sha256']
    print(json.dumps(dict(status='PASS_CPU_PREPARATION_INTEGRITY_ONLY',reserved_UUIDs=4,
          Gaussian_members=510,active_thread_instructions=283685120,original_AA_files_unchanged=len(oldfiles),
          actual_full_simulator_starts=0,full_matrix_performance_PASS=False,
          executable_preregistration_complete=False),indent=2))


if __name__=='__main__':main()
