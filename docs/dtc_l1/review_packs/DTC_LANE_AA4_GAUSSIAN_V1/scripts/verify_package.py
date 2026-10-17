"""Read-only scientific-STOP artifact verification; not a full-run validator."""
from common import *
import ast,sys

def main():
    checks={}
    for f in (PACK/'scripts').glob('*.py'):ast.parse(f.read_text(),filename=str(f))
    checks['all_own_python_scripts_parse']=True
    proof=json.loads((PACK/'TELEMETRY_SOURCE_AND_ELF_AUDIT.json').read_text());assert all(proof['checks'].values())
    assert proof['status']=='FAIL_CLOSED_NORMAL_REPLAY_K1_EVENT_TELEMETRY_UNAVAILABLE'
    checks['scientific_STOP_supported_by_source_ELF_CPU']=True
    assert proc(1425986) is None and proc(3291777) is None
    checks['both_reviewed_watchers_absent']=True
    retire=json.loads((PACK/'WATCHER_RETIREMENT_RECEIPT.json').read_text());assert all(retire['checks'].values()) and retire['one_pidfd_SIGTERM'] and not retire['other_signals_sent']
    checks['exact_parent_only_retirement_and_natural_timer_exit']=True
    auth=json.loads((PACK/'AUTHORITY_AND_FLOCK_AUDIT.json').read_text());assert all(auth['checks'].values()) and not auth['unknown_controls']
    checks['other_DTC_controls_individually_reviewed']=True
    resource=json.loads((PACK/'RESOURCE_AUDIT.json').read_text());assert all(resource['checks'].values())
    checks['independent_resource_probe_PASS_including_zero_swap_delta']=True
    with (PACK/'PRE_REGISTRATION.tsv').open() as f:reg=list(csv.DictReader(f,delimiter='\t'))
    with (PACK/'FULL_MATRIX.tsv').open() as f:matrix=list(csv.DictReader(f,delimiter='\t'))
    assert len(reg)==len(matrix)==4
    for (point,uid,k,*_),r,m in zip(POINTS,reg,matrix):
        specpath=PACK/'specs'/f'{point}.json';spec=json.loads(specpath.read_text())
        assert r['point']==m['point']==point and r['uuid']==m['uuid']==uid
        assert sha(specpath)==r['spec_sha256'] and m['cycles']=='UNAVAILABLE' and m['actual_starts']=='0'
        assert m['strict_receipt_sha256']==sha(PACK/'run_receipts'/uid/'STRICT.json')
        assert len(spec['expected_full_default_and_config_echo'])==267
        assert spec['source_event_metric_dictionary_sha256']==sha(PACK/'METRIC_DICTIONARY.tsv')
        assert all(sha(c['path'])==c['sha256'] for c in spec['configs'])
        assert spec['production_runner_sha256']=='UNAVAILABLE_SCIENTIFIC_STOP_BEFORE_RELEASE'
        assert sha(PACK/'scripts/run_matrix.py')==spec['execution_guard_sha256']
    checks['four_fixed_UUIDs_specs_STOP_receipts_bound_no_imputed_result']=True
    for name in ['run_matrix.py','strict.py']:
        r=subprocess.run([sys.executable,'-B',str(PACK/'scripts'/name)],capture_output=True,text=True)
        assert r.returncode!=0
    assert not list(ROOT.rglob('RUN_START.*')) and not (ROOT/'attempts').exists()
    checks['guards_cannot_launch_and_no_RUN_START_exists']=True
    identity=json.loads((PACK/'EXACT_BINARY_AND_CONFIG_SHA.json').read_text())
    for k in ['executable','libcudart']:assert sha(identity[k]['path'])==identity[k]['sha256']
    for d in identity['loader_dependencies']:assert sha(d['path'])==d['sha256']
    checks['exact_runtime_and_loader_dependency_SHA']=True
    inp=json.loads((PACK/'INPUT_STAT_IDENTITY.json').read_text());assert len(inp['members'])==510
    for m in inp['members']:
        s=Path(m['path']).stat();assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(m['device'],m['inode'],m['bytes'],m['mtime_ns'],m['ctime_ns'])
    checks['510_original_member_stat_identity_unchanged_since_AA3_rehash']=True
    # Historical reports and data in the AA4 worktree are byte-identical to its fixed AA3 parent.
    parent='dab43027467d577291aabd6a5d2812d601219188';paths=git(FW_REPO,'ls-tree','-r','--name-only',parent,'docs/dtc_l1/review_packs/DTC_LANE_AA_GAUSSIAN_V1','docs/dtc_l1/review_packs/DTC_LANE_AA2_GAUSSIAN_V1','docs/dtc_l1/review_packs/DTC_LANE_AA3_GAUSSIAN_V1').splitlines()
    for path in paths:assert (FW/path).read_bytes()==blob(FW_REPO,parent,path)
    checks['all_AA_AA2_AA3_frozen_pack_bytes_unchanged']=True
    write(PACK/'VALIDATION.json',dict(status='PASS_SCIENTIFIC_STOP_ARTIFACT_INTEGRITY_NOT_FULL_RUN_ACCEPTANCE',checks=checks,historical_files_verified=len(paths),actual_full_simulator_starts=0,full_executable_registration_released=False,performance_validated=False))
    print(json.dumps(checks,sort_keys=True))

if __name__=='__main__':main()
