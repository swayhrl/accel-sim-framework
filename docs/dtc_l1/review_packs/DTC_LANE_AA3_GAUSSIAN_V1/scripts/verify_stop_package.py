"""Read-only verification of the AA3 terminal STOP artifact, not simulation validation."""
from common import *
import ast

def main():
    checks={}
    for p in (PACK/'scripts').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    checks['python_scripts_parse']=True
    with (PACK/'PRE_REGISTRATION.tsv').open() as f:reg=list(csv.DictReader(f,delimiter='\t'))
    with (PACK/'FULL_MATRIX.tsv').open() as f:matrix=list(csv.DictReader(f,delimiter='\t'))
    assert len(reg)==len(matrix)==4
    for (point,uid,k,sets,ways,cal),r,m in zip(POINTS,reg,matrix):
        s=json.loads((PACK/'specs'/f'{point}.json').read_text())
        assert r['point']==m['point']==point and r['uuid']==m['uuid']==uid
        assert sha(PACK/'specs'/f'{point}.json')==r['spec_sha256']
        assert len(s['expected_full_default_and_config_echo'])==267
        assert not s['launch_admitted'] and not s['full_execution_admitted']
        assert m['actual_starts']=='0' and m['cycles']=='UNAVAILABLE'
        assert sha(PACK/'run_receipts'/uid/'STRICT.json')==m['strict_receipt_sha256']
        assert s['source_event_metric_dictionary_sha256']==sha(PACK/'METRIC_DICTIONARY.tsv')
        assert all(sha(c['path'])==c['sha256'] for c in s['configs'])
    checks['all_four_draft_specs_STOP_receipts_bound']=True
    checks['267_effective_options']=True
    guard=subprocess.run([sys.executable,'-B',str(PACK/'scripts/execution_guard.py')],capture_output=True,text=True)
    assert guard.returncode!=0 and 'STOP_OTHER_DISPATCH_CAPABLE_AUTHORITY_UNRESOLVED' in guard.stderr
    checks['guard_fails_closed_without_launch']=True
    assert not list(ROOT.rglob('RUN_START.*')) and not (ROOT/'attempts').exists()
    checks['no_AA3_actual_start_or_attempt_directory']=True
    release=json.loads((PACK/'WATCHER_RELEASE_RECEIPT.json').read_text())
    assert release['original_inode_unchanged'] and release['no_remaining_fdinfo_FLOCK_holders']
    assert not proc(1425986)
    checks['authorized_watcher_is_absent_original_lock_preserved']=True
    assert Path(release['lock_path']).stat().st_ino==37920070
    auth=json.loads((PACK/'OTHER_AUTHORITY_REVIEW.json').read_text())
    assert auth['status']=='STOP_LEGAL_EXECUTION_AUTHORITY_NOT_CLOSED'
    p=proc(3291777);assert p and p['start_ticks']==550530984
    checks['other_pending_dispatcher_still_present_NOT_silently_retired']=True
    baseline=git(FW_REPO,'ls-tree','-r','--name-only','fa7bd9ee7667ebb94e919295755311a2a2da4541',OLD_PACK,'docs/dtc_l1/review_packs/DTC_LANE_AA2_GAUSSIAN_V1').splitlines()
    for name in baseline:assert (FW/name).read_bytes()==blob(FW_REPO,'fa7bd9ee7667ebb94e919295755311a2a2da4541',name)
    checks['all_AA_AA2_baseline_files_byte_unchanged']=True
    with (PACK/'METRIC_DICTIONARY.tsv').open() as f:metrics=list(csv.DictReader(f,delimiter='\t'))
    assert len([r for r in metrics if r['comparability_class']=='K1_ONLY_NONCOMPARATIVE_DIAGNOSTIC'])==17
    checks['17_K1_diagnostics_noncomparative']=True
    formulas=json.loads((PACK/'Z2_INDEPENDENT_RECALCULATION.json').read_text())
    assert formulas['historical_controls_not_substituted'] and formulas['actual_effects']=='UNAVAILABLE'
    checks['no_historical_K0_imputation_or_factorial_performance_claim']=True
    write(PACK/'VALIDATION.json',dict(status='PASS_TERMINAL_STOP_PACK_INTEGRITY_ONLY',checks=checks,AA_AA2_baseline_files_verified=len(baseline),actual_simulator_strict_pass=False,full_executable_preregistration=False,no_extra_authorization_inferred=True))
    print(json.dumps(checks,sort_keys=True))

if __name__=='__main__':
    import sys
    main()
