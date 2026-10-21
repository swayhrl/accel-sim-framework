"""Independent terminal review of the exact two approved retry attempts.

Read-only with respect to execution state. No launch, release or result repair.
"""
from pathlib import Path
import json,sys,time,os
N=Path(__file__).resolve().parent;P=N.parent;ROOT=P.parents[3]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,runner

def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(Path(p).resolve()),sha256=c.digest(p))
def audit():
 s=c.Coordinator().snapshot();data=read(c.SHARED/'RUN_REGISTRY.json');plan=read(N/'PLAN.json');base=read(N/'PRE_RETRY_ACCEPTANCE_AND_BUDGET_BASELINE.json')
 assert s['controller']['state']=='STOPPED' and s['uncertain_start_intents']==0
 assert s['t0_unix']==base['T0']==1792414193 and s['maximum_actual_starts']==40 and s['reservations']==base['original_reservations']
 assert s['start_deadline_unix']==c.START_DEADLINE and s['additional_results_max_bytes']==6*c.GIB and s['old_plus_new_results_max_bytes']==20*c.GIB
 ours=lambda r:r.get('experiment_id')==c.CAMPAIGN and r['status'] in c.ACTIVE
 assert not any(ours(r) for r in data['runs'].values()) and not any(ours(r) for r in data['resource_leases'].values())
 main={k:v for k,v in s['accepted_pairs'].items() if k.startswith('V2_MAIN_') and v['status']=='CURRENT_ACCEPTED'}
 assert main==base['accepted_main_pairs'] and len(main)==4
 for aid,old in base['old_failure_receipts'].items():
  a=next(a for a in s['attempts'] if a['attempt_id']==aid)
  assert a['state']=='RESOURCE_LIMIT' and a['actual_start'] and a['receipt_sha256']==old['sha256']==c.digest(old['path'])
  n=read(Path(a['result_directory'])/'NATIVE_EXIT.json');assert n['exit_code']==-15 and n['wait_status']==15
 rows=[];logical=allocated=0;seen=set()
 for p in [Path(a['result_directory']) for a in s['attempts'][30:]]:
  for q in [p,*p.rglob('*')]:
   st=q.lstat();key=(st.st_dev,st.st_ino)
   if key not in seen:allocated+=st.st_blocks*512;seen.add(key)
   if q.is_file() and not q.is_symlink():logical+=st.st_size
 for row in plan['profiles']:
  matches=[a for a in s['attempts'][30:] if a['run_key']==row['run_key']]
  assert len(matches)<=1
  if not matches:rows.append(dict(condition_id=row['condition_id'],status='NOT_STARTED_NO_CHARGE'));continue
  a=matches[0];assert a['actual_start'] and a['budget_bucket']=='two_workload_local_diagnostics' and a['prior_attempts']==[row['previous_attempt']]
  r=read(a['receipt_path']);assert c.digest(a['receipt_path'])==a['receipt_sha256'] and r['attempt_id']==a['attempt_id'] and r['identity']==read(row['spec']['path'])['identity']
  npath=Path(a['result_directory'])/'NATIVE_EXIT.json';n=read(npath);assert c.digest(npath)==r['native_exit_receipt_sha256']
  assert n['native_process']==r['process'] and n['binding']['attempt_id']==a['attempt_id']
  review=dict(condition_id=row['condition_id'],attempt_id=a['attempt_id'],profile=r['profile'],state=a['state'],actual_start=True,previous_charged_attempt=row['previous_attempt'],receipt=dict(path=a['receipt_path'],sha256=a['receipt_sha256']),native_exit=ref(npath),native_exit_code=n['exit_code'],native_wait_status=n['wait_status'],native_process=r['process'],result_directory=a['result_directory'],wall_seconds=r['wall_seconds'],labels=r['labels'],qualification_id=r['qualification_id'])
  if r['status']=='COMPLETE_VALID':
   assert r['independent_acceptance']=='PASS' and n['exit_code']==n['wait_status']==0 and n['stop_reason'] is None
   assert r['summary']['instructions']==row['expected_full_instructions']==148684429 and r['summary']['slices']==64
   assert r['complete_input_verified'] and runner.validate_summary(r['summary'],r['identity'])['status']=='PASS'
   c.Coordinator.require_no_hold(s,r['qualification_id'])
   pair=s['accepted_pairs'][row['control_pair_id']];assert pair['status']=='CURRENT_ACCEPTED' and pair['endpoints']['right']['attempt_id']==a['attempt_id'] and pair['endpoints']['left']['attempt_id']=='E017_2bc62654'
   review.update(independent_terminal_audit='PASS',cycles=r['summary']['cycles'],instructions=r['summary']['instructions'],slices=64,accepted_pair_id=row['control_pair_id'],anchor_cycles=pair['cycles_left'],anchor_over_control=pair['ratio_left_over_right'])
  else:review.update(independent_terminal_audit='NOT_ACCEPTED',detail=r['detail'])
  rows.append(review)
 usage=c.output_usage();addition=usage['new_bytes']-base['output_usage']['new_bytes']
 assert usage['old_bytes']==base['output_usage']['old_bytes'] and usage['new_bytes']<=6*c.GIB and usage['total_bytes']<=20*c.GIB
 assert 0<=addition<=plan['maximum_total_result_addition_bytes'] and addition==logical
 buckets={k:sum(c.policy_v2.charged_bucket(a,s['reservations'])==k and a.get('actual_start',False) for a in s['attempts']) for k in s['reservations']}
 assert buckets['contingency']==8 and buckets['two_workload_local_diagnostics']==base['budget_buckets']['two_workload_local_diagnostics']+len(s['attempts'][30:])
 report=dict(schema='E2_APPROVED_DWT_RETRIES_INDEPENDENT_TERMINAL_AUDIT_V1',status='BOTH_CURRENT_ACCEPTED' if all(r.get('independent_terminal_audit')=='PASS' for r in rows) else 'PRECISE_PARTIAL_OR_FAILURE_NO_AUTOMATIC_RETRY',at_unix=time.time(),T0=s['t0_unix'],actual_starts=s['actual_starts'],remaining=s['remaining_start_capacity'],maximum=40,contingency_consumed=8,budget_buckets=buckets,controller=s['controller'],rows=rows,source_identity=s['final_source_identity'],source_tooling_publication=c.tooling_binding(),four_main_pairs_preserved=True,old_failures_preserved=True,output_usage=usage,remaining_new_result_generation_bytes=6*c.GIB-usage['new_bytes'],remaining_total_result_generation_bytes=20*c.GIB-usage['total_bytes'],new_retry_result_growth_logical_bytes=addition,new_retry_allocated_bytes_including_directories=allocated,resources=c.local_resources(),full_matrix=ref(s['full_system_matrix']['path']),adoption=ref(N/'MATRIX_ADOPTION_RECEIPT.json'),next_batch='NONE_AUTOMATIC; two-condition approval drained. Remaining8 starts are capacity, not automatic qualification or retry authority.',start_deadline=c.START_DEADLINE,intake_deadline=c.INTAKE_DEADLINE,interpretation='COPY_FREE includes physical copy services and fixed copy-staging retry delay and is diagnostic; W_ONLY retains physical P1. W_ONLY vs F is a joint V+RO/state contrast, not independent V and RO contributions. No extra MAIN pair or automatic seven-input GM.')
 c.write_json(N/'INDEPENDENT_TERMINAL_AUDIT.json',report)
 print(json.dumps(report,indent=2));return report
if __name__=='__main__':audit()
