"""Independent read-only closure check for the single consumed attempt and no valid performance."""
from pathlib import Path
import sys,json,csv,importlib.util,hashlib
P=Path('/workspace/worktrees/accel-sim-iscas2027-dtc-lane-aa5-gaussian-convergence-174-v1/docs/dtc_l1/review_packs/DTC_LANE_AA5_GAUSSIAN_V1');C=P/'continuations/USER_RECHECK_20261018T030133Z';Q=Path('/workspace/dtc-lane-aa5-gaussian-174-v1/user_recheck_20261018T030133Z')
sys.path.insert(0,str(C/'scripts'));sys.path.append(str(P/'scripts'));from common import *
from strict_matrix import require,input_check,BASELINES
from run_matrix import check_budget,registration_check

def main():
 original=json.loads((P/'EXECUTABLE_PREREGISTRATION.json').read_text());cont=json.loads((C/'CONTINUATION_PREREGISTRATION.json').read_text())
 for root,m in [(P,original),(C,cont)]:
  for path,h in m['files'].items():require(sha(root/path)==h,'immutable_registered_file:'+str(root/path))
 require(sha(P/'EXECUTABLE_PREREGISTRATION.json')==cont['original_registration_sha256'],'original_manifest_SHA')
 pub=json.loads((Q/'CONTINUATION_PUBLICATION_READBACK.json').read_text());require(sha(C/'CONTINUATION_PREREGISTRATION.json')==pub['manifest_sha256'],'preperformance_manifest_SHA')
 require(pub['commit']==git(FW,'rev-parse','refs/aa5-bindings/USER_RECHECK_20261018T030133Z'),'continuation_remote_readback')
 starts=check_budget();require(len(starts)==1,'shared_actual_budget')
 require(starts[0]['uuids']==['d0a29a82-c171-46e4-b077-d7ccfd2c4b7a'],'one_consumed_original_UUID')
 run=ROOT/'attempts/K0_32x4_d0a29a82-c171-46e4-b077-d7ccfd2c4b7a'
 term=json.loads((run/'RUN_TERMINAL.json').read_text());strict=json.loads((run/'STRICT.json').read_text());begin=json.loads((run/'RESOURCE_START.json').read_text());finish=json.loads((run/'RESOURCE_FINAL.json').read_text())
 require(term['returncode']==-15 and term['forced_reason']=='NEW_SYSTEM_SWAP_ACTIVITY' and not term['natural_exit'],'real_resource_abort')
 require(not strict['performance_accepted'] and strict['failure']=="ValueError('natural_exit0')",'no_false_strict')
 require(finish['pswpin']-begin['pswpin']==1 and finish['pswpout']==begin['pswpout'],'host_global_swap_delta')
 require(term['identity_pass'],'real_loaded_identity')
 require(not (run/'NORMAL_EVENT_SNAPSHOTS.json').exists(),'no_fake_full_event_receipt')
 source_specs=[]
 for label,uid,k,sets,ways,cal in POINTS:
  spec=json.loads((C/'specs'/f'{label}.json').read_text());source_specs.append(spec);input_check(spec)
  require(spec['attempt_uuid']==uid and spec['K']==k and spec['sets']==sets and spec['ways']==ways,'fixed_UUID_factor')
  require(sha(spec['runtime_path'])==spec['runtime_sha256'],'binary')
  require(sha(spec['runtime_library_path'])==spec['runtime_library_sha256'],'library')
  require(spec['production_runner_sha256']==sha(C/'scripts/run_matrix.py'),'actual_runnerSHA')
  require(spec['strict_collector_sha256']==sha(C/'scripts/strict_matrix.py')==sha(P/'scripts/strict_matrix.py'),'unchanged_strict')
  point=ROOT/'attempts'/(label+'_'+uid)
  require((point/'RUN_START.json').exists()==(label=='K0_32x4'),'other_points_not_started')
  if label=='K0_32x4':
   require(sha(point/'immutable_runner.py')==spec['production_runner_sha256'],'frozen_runner_in_raw')
   require(sha(point/'immutable_strict.py')==spec['strict_collector_sha256'],'frozen_strict_in_raw')
   for c in json.loads((point/'RUN_START.json').read_text())['config_copies']:require(sha(c['path'])==c['sha256'],'actual_configSHA')
 require(len({s['runtime_sha256'] for s in source_specs})==len({s['runtime_library_sha256'] for s in source_specs})==1,'one_runtime')
 diff={key for key in source_specs[0]['expected_full_default_and_config_echo'] if len({tuple(s['expected_full_default_and_config_echo'][key]) for s in source_specs})>1}
 require(diff=={K_OPTION,'-gpgpu_dtc_l1_logical_sets','-gpgpu_dtc_l1_logical_ways'},'only_K_and_Tag')
 for item in csv.DictReader((run/'FILES_SHA256.tsv').open(),delimiter='\t'):require(sha(run/item['path'])==item['sha256'],'raw_immutable:'+item['path'])
 require(json.loads((C/'FINAL_AUTHORITY_RELEASE.json').read_text())['own_lock_holders']==[],'own_lock_released')
 for p in [term['PID'],json.loads((Q/'AUTHORITY_ACTIVE.json').read_text())]:
  live=proc(p['pid']);require(live is None or live['start_ticks']!=p['start_ticks'],'original_process_live')
 try:registration_check()
 except ValueError as e:require(str(e)=='continuation_already_terminal_NO_AUTOMATIC_RESTART','wrong_guard_rejection')
 else:raise AssertionError('terminal_guard_accepted')
 partial=json.loads((C/'PARTIAL_CONTROL_DIAGNOSTIC.json').read_text());require(partial['completed_snapshot_count']==67 and partial['counter_differences']==[] and partial['config267_match'],'prefix_diagnostic')
 oldhash=json.loads((P/'HISTORICAL_PARSER_CPU_CHECK.json').read_text())['rows'][0]['stdout_sha256'];require(sha(BASELINES[32])==oldhash,'same_accepted_old_reference')
 require(partial['last_completed_raw_cycles']==657230 and partial['last_completed_active_thread_instructions']==60326860 and partial['last_completed_CTA']==8516,'typed_partial_values')
 matrix=list(csv.DictReader((P/'FULL_MATRIX.tsv').open(),delimiter='\t'));require(len(matrix)==4 and sum(int(r['actual_starts']) for r in matrix)==1,'complete_fourcell_ledger')
 require(all(r['accepted_cycles']=='UNAVAILABLE' for r in matrix),'no_unaccepted_perf')
 ev=list(csv.DictReader((P/'ACTUAL_EVENTS.tsv').open(),delimiter='\t'));require(all(r['requests']=='UNAVAILABLE' and r['reclaimed_at_event']=='UNAVAILABLE' for r in ev),'no_invented_events')
 effects=list(csv.DictReader((P/'FACTORIAL_EFFECTS.tsv').open(),delimiter='\t'));require(all(r['exact_value']=='UNAVAILABLE' and r['accepted_new_cells']=='0' for r in effects),'no_invented_effects')
 if (P/'FILES_SHA256.tsv').exists() and '--with-manifest' in sys.argv:
  rows=list(csv.DictReader((P/'FILES_SHA256.tsv').open(),delimiter='\t'));actual={str(p.relative_to(P)) for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=P/'FILES_SHA256.tsv'}
  require({r['path'] for r in rows}==actual,'full_pack_manifest_population')
  for row in rows:require(sha(P/row['path'])==row['sha256'],'pack_SHA:'+row['path'])
 print(json.dumps(dict(status='PASS_RESOURCE_ABORT_DELIVERY_NOT_PERFORMANCE_PASS',actual_shared_starts=1,shared_total_cap=4,accepted_full_points=0,normal_export_gate='PASS_PRIOR_INDEPENDENT_QUALIFICATION',attempt='K0_32x4_SIGTERM_EXIT_MINUS15_HOST_GLOBAL_SWAPIN_PLUS1PAGE',other_points='THREE_HOLD_NOT_STARTED',prefix='67_COMPLETED_SAME_TAG_PUBLIC_COUNTER_MATCH_NOT_FULL_EQUIVALENCE',immutable_original_files=len(original['files']),immutable_continuation_files=len(cont['files']),source_config_input_runtime='PASS_IDENTITY_UNCHANGED',own_authority='TERMINAL_FLOCK_RELEASED',terminal_restart_guard='REJECTED',extra_attempts_or_UUIDs=False),indent=2))
if __name__=='__main__':main()
