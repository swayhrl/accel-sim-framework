"""Independent small-file consistency checks; no trace re-scan or simulation."""
import ast
from prepare_cpu import PACK, ROOT, CORE, BASE_CORE, sha, read_options, git, write
import csv
import json
from pathlib import Path
import subprocess


def rows(name):
    with (PACK/name).open() as f:
        return list(csv.DictReader(f,delimiter='\t'))


def main():
    plan=rows('PRE_REGISTRATION.tsv')
    assert len(plan)==4 and len({r['uuid'] for r in plan})==4
    expected=[('K0_32x4','0','32','4'),('K0_64x8','0','64','8'),
              ('K1_32x4','1','32','4'),('K1_64x8','1','64','8')]
    assert [(r['point'],r['K'],r['sets'],r['ways']) for r in plan]==expected
    specs=[]
    for r in plan:
        f=PACK/'specs'/f'{r["point"]}.json'
        assert sha(f)==r['spec_sha256']
        s=json.loads(f.read_text())
        assert s['attempt_uuid']==r['uuid'] and s['label']==r['point']
        assert s['status']=='RESERVED_UNBOUND_DO_NOT_EXECUTE'
        assert s['new_core_sha']==s['new_binary_sha256']=='UNAVAILABLE'
        assert s['K_option_name']=='UNAVAILABLE_PENDING_LANE_X'
        assert s['wall_timeout_seconds']==7200 and s['actual_start_limit']==1
        assert s['expected_kernel_count']==510 and s['expected_active_thread_instructions']==283685120
        for c in s['configs']:assert sha(c['path'])==c['sha256']
        assert read_options([c['path'] for c in s['configs']])==s['expected_common_and_tag_effective_options']
        assert s['members_manifest_sha256']==sha(PACK/'GAUSSIAN_MEMBERS_SHA256.tsv')
        assert s['ordered_kernel_manifest_sha256']==sha(PACK/'ORDERED_KERNELS.json')
        raw=ROOT/'receipts'/r['uuid']/'STRICT.json'
        strict=json.loads(raw.read_text())
        assert strict['status']=='NOT_RUN' and strict['actual_starts']==0
        assert strict['event_count']==strict['invalidated_mapping_count']=='UNAVAILABLE'
        assert raw.read_bytes()==(PACK/'run_receipts'/r['uuid']/'STRICT.json').read_bytes()
        specs.append(s)
    allowed={'-gpgpu_dtc_l1_logical_sets','-gpgpu_dtc_l1_logical_ways'}
    first=specs[0]['expected_common_and_tag_effective_options']
    for s in specs:
        current=s['expected_common_and_tag_effective_options']
        diffs={k for k in first.keys()|current.keys() if first.get(k)!=current.get(k)}
        assert diffs<=allowed
    assert specs[0]['expected_common_and_tag_effective_options']==specs[2]['expected_common_and_tag_effective_options']
    assert specs[1]['expected_common_and_tag_effective_options']==specs[3]['expected_common_and_tag_effective_options']
    matrix=rows('FULL_MATRIX.tsv')
    assert len(matrix)==4 and [r['uuid'] for r in matrix]==[r['uuid'] for r in plan]
    assert all(r['actual_starts']=='0' and r['cycles']=='UNAVAILABLE' and r['strict']=='NOT_RUN' for r in matrix)
    ordered=json.loads((PACK/'ORDERED_KERNELS.json').read_text())
    members=rows('GAUSSIAN_MEMBERS_SHA256.tsv')
    assert len(ordered)==len(members)==510
    assert sum(r['active_instructions'] for r in ordered)==283685120
    assert [r['ordinal'] for r in ordered]==list(range(1,511))
    for o,m in zip(ordered,members):
        assert o['member_path']==m['path'] and o['member_sha256']==m['sha256']
    assert sha(PACK/'inputs/Gaussian_kernelslist.g')=='6dc7caba6733657293e8c517467bac28890ae4eb97c732ffd245d7fd1c479fb9'
    assert len([s for s in (PACK/'inputs/Gaussian_kernelslist.g').read_text().splitlines() if s.startswith('kernel-')])==510
    assert len([m for m in rows('METRIC_DICTIONARY.tsv') if m['finite11']=='True'])==11
    stop=json.loads((PACK/'STOP_RECORD.json').read_text())
    assert stop['launch_admitted'] is False and stop['actual_full_starts']==0
    assert stop['upstream_X_implemented'] is False
    x=json.loads((PACK/'inputs/LANE_X/SOURCE_AND_BINARY_IDENTITY.json').read_text())
    assert x['k1_implemented'] is False and x['new_option_registered'] is False
    assert not (ROOT/'attempts').exists()
    for source in json.loads((PACK/'SOURCE_EVENT_OBSERVATION.json').read_text())['baseline_files']:
        rel=str(Path(source['path']).relative_to(CORE))
        import hashlib
        data=subprocess.check_output(['git','-C',str(CORE),'show',BASE_CORE+':'+rel])
        assert hashlib.sha256(data).hexdigest()==source['sha256']
    # The only subprocesses in these evidence programs must be git reads.
    for f in [PACK/'scripts/prepare_cpu.py', PACK/'scripts/close_stop.py']:
        tree=ast.parse(f.read_text())
        for node in ast.walk(tree):
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name) and node.func.value.id=='subprocess':
                assert node.func.attr in ['check_output','run','CalledProcessError']
                if node.func.attr!='CalledProcessError':
                    assert isinstance(node.args[0],ast.List)
                    assert node.args[0].elts[0].value=='git'
    for r in rows('RAW_FILES_SHA256.tsv'):
        assert sha(ROOT/r['path'])==r['sha256']
        assert (ROOT/r['path']).stat().st_size==int(r['bytes'])
    for f in PACK.rglob('*.json'):json.loads(f.read_text())
    if (PACK/'FILES_SHA256.tsv').exists():
        files=rows('FILES_SHA256.tsv')
        assert {r['path'] for r in files}=={str(f.relative_to(PACK)) for f in PACK.rglob('*') if f.is_file() and f.name!='FILES_SHA256.tsv'}
        for r in files:assert sha(PACK/r['path'])==r['sha256']
        print('PASS_CPU_STOP_PACKAGE_INTEGRITY; manifest checked; no performance PASS.')
    else:
        write(PACK/'VALIDATION.json',dict(status='PASS_CPU_STOP_PACKAGE_INTEGRITY_ONLY',
              reserved_UUIDs=4,original_kernel_count=510,actual_simulator_starts=0,
              full_execution_preregistration_complete=False,performance_PASS=False,
              checks=['spec_hashes','unique_fixed_design','only_Tag_common_option_differences',
                      'same_Tag_K0_K1_common_configs','ordered_510_identity_binding',
                      'active_instruction_total','explicit_unbound_binary_and_event_contract',
                      'bound_X_scientific_STOP','eleven_finite_fields','raw_receipt_hashes',
                      'baseline_source_git_object_identity','no_simulator_subprocess_path']))
        print('PASS_CPU_STOP_PACKAGE_INTEGRITY; no performance PASS.')


if __name__=='__main__':
    main()
