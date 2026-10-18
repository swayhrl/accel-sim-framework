"""Read-only final bundle verification; no simulator invocation, lock or signal."""
from common import *
from strict_matrix import require,input_check
from run_matrix import check_budget,registration_check

def main():
    m=json.loads((PACK/'EXECUTABLE_PREREGISTRATION.json').read_text())
    for p,h in m['files'].items():require(sha(PACK/p)==h,'registered_file_hash:'+p)
    require(check_budget()==[],'actual_starts_not_zero')
    require(not (ROOT/'attempts').exists(),'UUID_attempt_directory_created')
    require(not (ROOT/'AA5_execution.lock').exists(),'AA5_execution_authority_acquired')
    require(git(FW,'rev-parse','refs/aa5-bindings/GATE_PUBLISHED')=='5c3a40ff81b366bc6fe362518ae4adc23f0597cc','gate_remote_readback')
    g=json.loads((PACK/'NORMAL_TERMINAL_EXPORT_GATE.json').read_text());require(g['status']=='PASS_NORMAL_TERMINAL_EXPORT_GATE','normal_gate')
    require(sha(PACK/'scripts/normal_export_fixture.cc')==g['fixture_source_sha256'],'fixture_source')
    require(sha(PACK/'scripts/event_snapshots.py')==g['decoder_sha256'],'qualified_decoder')
    binding=json.loads((PACK/'PUBLISHED_X2_BINDING.json').read_text())
    require(binding['Core_commit']==g['Core_commit'],'qualified_Core_binding')
    require(git(CORE_REPO,'rev-parse','refs/aa5-bindings/X2_Core')==binding['Core_commit'],'Core_fetch_back')
    require(git(FW_REPO,'rev-parse','refs/aa5-bindings/X2_Framework')==binding['producer_Framework_commit'],'X2_review_fetch_back')
    spec_list=[]
    for n,u,k,s,w,c in POINTS:
        spec=json.loads((PACK/'specs'/f'{n}.json').read_text());require(spec['point']==n and spec['attempt_uuid']==u and spec['K']==k and spec['sets']==s and spec['ways']==w,'fixed_spec')
        require(spec['runtime_sha256']==sha(spec['runtime_path'])==binding['trace_executable_sha256'],'trace_binary')
        require(spec['runtime_library_sha256']==sha(spec['runtime_library_path'])==binding['libcudart_sha256'],'actual_library')
        require(spec['source_Core_commit']==binding['Core_commit'],'same_Core')
        require(spec['production_runner_sha256']==sha(PACK/'scripts/run_matrix.py'),'runnerSHA')
        require(spec['strict_collector_sha256']==sha(PACK/'scripts/strict_matrix.py'),'strictSHA')
        require(spec['event_decoder_source_sha256']==sha(PACK/'scripts/event_snapshots.py'),'decoderSHA')
        require(len(spec['expected_full_default_and_config_echo'])==267,'267_effective_options')
        require(not spec['launch_admitted'],'terminal_not_admitted')
        input_check(spec);spec_list.append(spec)
    varied={key for key in spec_list[0]['expected_full_default_and_config_echo'] if len({tuple(s['expected_full_default_and_config_echo'][key]) for s in spec_list})>1}
    require(varied=={K_OPTION,'-gpgpu_dtc_l1_logical_sets','-gpgpu_dtc_l1_logical_ways'},'controlled_delta_only_K_Tag')
    resource=json.loads((PACK/'RESOURCE_AUDIT.json').read_text());require({k for k,v in resource['checks'].items() if not v}=={'first_io_PSI','second_io_PSI'},'actual_resource_failure_not_relabelled')
    require(resource['probe_seconds']>=10,'two_probe_gap')
    authority=json.loads((PACK/'AUTHORITY_AND_FLOCK_AUDIT.json').read_text());require(all(authority['checks'].values()),'read_only_authority_review')
    for n in ['RESOURCE_AUDIT.json','AUTHORITY_AND_FLOCK_AUDIT.json','EXECUTION_RESOURCES.tsv']:require(sha(PACK/n)==sha(ROOT/'authority-preflight'/n),'current_probe_bytes:'+n)
    try:registration_check()
    except ValueError as e:require(str(e)=='TERMINAL_RESOURCE_STOP_NO_AUTOMATIC_CONTINUATION','wrong_guard_failure')
    else:raise AssertionError('STOP_latch_did_not_reject')
    for row in csv.DictReader((PACK/'FULL_MATRIX.tsv').open(),delimiter='\t'):
        require(row['actual_starts']=='0' and row['cycles']=='UNAVAILABLE' and row['strict']=='NOT_RUN','matrix_fake_performance')
    for row in csv.DictReader((PACK/'ACTUAL_EVENTS.tsv').open(),delimiter='\t'):require(row['requests']=='UNAVAILABLE' and row['reclaimed_at_event']=='UNAVAILABLE','fake_event_observation')
    require(json.loads((PACK/'Z2_INDEPENDENT_RECALCULATION.json').read_text())['accepted_new_cells']==0,'formula_denominator')
    if (PACK/'FILES_SHA256.tsv').exists():
        rows=list(csv.DictReader((PACK/'FILES_SHA256.tsv').open(),delimiter='\t'))
        expected={str(p.relative_to(PACK)) for p in PACK.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=PACK/'FILES_SHA256.tsv'}
        require({r['path'] for r in rows}==expected,'complete_pack_manifest')
        for r in rows:require(sha(PACK/r['path'])==r['sha256'],'pack_SHA:'+r['path'])
    print(json.dumps(dict(status='PASS_FINAL_STOP_BUNDLE_NOT_PERFORMANCE',registered_files=len(m['files']),controlled_delta=sorted(varied),new_full_actual_starts=0,four_cells='HOLD_NOT_STARTED_RESOURCE_STOP',normal_export_gate='PASS',resource='FAIL_PRESERVED_IO_FULL_PSI_32.42_28.98_GT25',authority='PASS_READ_ONLY',guard='REJECTED_TERMINAL_STOP',all_manifest_checks='PASS'),indent=2))

if __name__=='__main__':main()
