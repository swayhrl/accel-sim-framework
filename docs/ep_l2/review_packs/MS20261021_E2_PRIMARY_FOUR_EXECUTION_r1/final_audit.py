"""Independent terminal/budget/identity closure; no launch or acceptance mutation."""
from pathlib import Path
import json,sys,time,csv,subprocess
P=Path(__file__).resolve().parent;ROOT=P.parents[3];sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,runner

def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(Path(p).resolve()),sha256=c.digest(p))
def audit():
 coord=c.Coordinator();s=coord.snapshot();base=read(P/'BASELINE.json');plan=read(P/'PLAN.json');data=read(c.SHARED/'RUN_REGISTRY.json')
 assert s['controller']['state']=='STOPPED' and s['uncertain_start_intents']==0 and s['t0_unix']==base['T0'] and s['reservations']==base['reservations']
 assert 32<=s['actual_starts']<=36 and s['remaining_start_capacity']==40-s['actual_starts']
 assert s['maximum_actual_starts']==40 and s['additional_results_max_bytes']==6*c.GIB and s['old_plus_new_results_max_bytes']==20*c.GIB and s['start_deadline_unix']==c.START_DEADLINE
 assert not any(r['status'] in c.ACTIVE and r.get('experiment_id')==c.CAMPAIGN for k in ['runs','resource_leases'] for r in data[k].values())
 for old in base['prior_attempts']:
  current=next(a for a in s['attempts'] if a['attempt_id']==old['attempt_id']);assert all(current.get(k)==v for k,v in old.items())
  if old['receipt_path']:assert c.digest(old['receipt_path'])==old['receipt_sha256']
 for key,value in base['accepted_pairs'].items():assert s['accepted_pairs'][key]==value
 before={r['condition_id']:r for r in base['full_system_matrix']['matrix']['conditions']};after={r['condition_id']:r for r in s['full_system_matrix']['matrix']['conditions']}
 assert set(before)-set(after)=={'V2_FWT_7_21_F_MINUS_W','V2_btree_F'} and set(after)-set(before)=={'V2_dwt2d_F_MINUS_R','V2_vectorAdd_4M_F_RESOURCE_RETRY'}
 assert all(before[k]==after[k] for k in set(before)&set(after));assert s['full_system_matrix']['sha256']==plan['matrix']['sha256']==c.digest(plan['matrix']['path'])
 rows=[];startup=[];logical=allocated=0;seen=set()
 for a in s['attempts'][32:]:
  path=Path(a['result_directory'])
  for p in [path,*path.rglob('*')]:
   st=p.lstat();key=(st.st_dev,st.st_ino)
   if key not in seen:allocated+=st.st_blocks*512;seen.add(key)
   if p.is_file() and not p.is_symlink():logical+=st.st_size
 for number,row in enumerate(plan['profiles'],1):
  a=[a for a in s['attempts'][32:] if a['run_key']==row['run_key']];assert len(a)<=1
  result=dict(priority=number,condition=row['condition_id'],workload=row['workload'],profile=row['profile'],qualification=row['qualification'])
  assert c.digest(row['qualification']['path'])==row['qualification']['sha256'] and row['qualification_id'] in s['qualifications']
  if not a:result.update(state='NOT_STARTED',actual_start=False,accepted=False);rows.append(result);continue
  a=a[0];spec=read(row['spec']['path']);assert a['identity']==spec['identity'] and a['maximum_result_bytes']==384*2**20
  r=read(a['receipt_path']);assert c.digest(a['receipt_path'])==a['receipt_sha256']
  path=Path(a['result_directory']);size=c.retained_tree_bytes(path);assert size<=384*2**20,'Endpoint exceeded authorized maximum; precise review needed, never implicit acceptance'
  n=read(path/'NATIVE_EXIT.json');ready=read(path/'NATIVE_EXECUTION_READY.json');assert c.digest(path/'NATIVE_EXIT.json')==r['native_exit_receipt_sha256']
  assert n['binding']['attempt_id']==a['attempt_id'] and n['native_process']==r['process']==ready['native_process'] and n['guardian_process']==ready['guardian_process'] and n['native_ppid']==ready['native_ppid']==ready['guardian_process']['pid']
  if a.get('actual_start'):assert ready['at_unix']<c.START_DEADLINE
  if row['workload']=='vectorAdd_4M':assert a['prior_attempts']==['E014_7a67cdcb'] and spec['retry_previous_attempt']=='E014_7a67cdcb'
  else:assert not a['prior_attempts']
  pair=s['accepted_pairs'].get(row['pair_id']);accepted=bool(pair and pair['status']=='CURRENT_ACCEPTED')
  if accepted:
   assert r['status']=='COMPLETE_VALID' and r['independent_acceptance']=='PASS' and n['exit_code']==n['wait_status']==0 and n['stop_reason'] is None
   assert r['summary']['instructions']==row['expected_instructions'] and r['summary']['slices']==64 and r['complete_input_verified'] and runner.validate_summary(r['summary'],r['identity'])['status']=='PASS'
   assert pair['endpoints']['right']['attempt_id']==a['attempt_id'] and pair['endpoints']['left']['attempt_id']==row['anchor_attempt'];coord.require_no_hold(s,row['qualification_id'])
  result.update(attempt_id=a['attempt_id'],state=a['state'],actual_start=a['actual_start'],accepted=accepted,receipt=ref(a['receipt_path']),native_exit=ref(path/'NATIVE_EXIT.json'),native_ready=ref(path/'NATIVE_EXECUTION_READY.json'),exit_code=n['exit_code'],wait_status=n['wait_status'],stop_reason=n['stop_reason'],result_directory=str(path),retained_bytes=size,wall_seconds=r['wall_seconds'],labels=r['labels'],cycles=r.get('summary',{}).get('cycles'),instructions=r.get('summary',{}).get('instructions'),pair=pair,native_process=n['native_process'],guardian=n['guardian_process'])
  rows.append(result);startup.append(dict(queue_priority=number,condition=row['condition_id'],attempt_id=a['attempt_id'],actual_start=a['actual_start'],native_start_unix=ready['at_unix'],native_process=n['native_process'],exit_code=n['exit_code'],wait_status=n['wait_status'],budget_bucket=a['budget_bucket'],prior_attempts=a['prior_attempts']))
 usage=c.output_usage();assert usage['old_bytes']==base['output_usage']['old_bytes'] and usage['new_bytes']-base['output_usage']['new_bytes']==logical
 assert logical<=plan['maximum_total_result_bytes'] and usage['new_bytes']<=6*c.GIB and usage['total_bytes']<=20*c.GIB
 q=read(next(r['qualification']['path'] for r in plan['profiles'] if r['profile']=='F_L2_DATA_FREE'));g=q['gates']['full_data_free_finite_residual_service'];assert g['status']=='PASS' and g['production_driven'] and c.digest(g['evidence_path'])==g['evidence_sha256']
 buckets={k:sum(c.policy_v2.charged_bucket(a,s['reservations'])==k and a.get('actual_start',False) for a in s['attempts']) for k in s['reservations']};assert buckets['contingency']==8
 report=dict(schema='E2_PRIMARY_FOUR_FINAL_INDEPENDENT_TERMINAL_AUDIT_V1',status='ALL_FOUR_CURRENT_ACCEPTED' if all(r.get('accepted') for r in rows) else 'LEGAL_STOP_WITH_EXACT_PARTIAL_OR_FAILURE_NO_REPLAY',at_unix=time.time(),actual_starts=s['actual_starts'],remaining=s['remaining_start_capacity'],T0=s['t0_unix'],controller=s['controller'],source_identity=s['final_source_identity'],runtime_source_publication=c.verify_extension_binding(c.HANDOFF/'CLIENT_CONTRACT.json'),CLIENT=ref(c.HANDOFF/'CLIENT_CONTRACT.json'),bucket_usage=buckets,reservations=s['reservations'],rows=rows,startup_order=sorted(startup,key=lambda r:r['native_start_unix']),priority_note='Queue submission priority is DWT,Vector,ConvS,ConvF. Original concurrent full-input inspection/reservation may finish in a different order; exact native start times/attempt IDs are retained, never renumbered or replayed.',output_usage=usage,result_growth_logical_bytes=logical,result_allocated_bytes_including_directories=allocated,remaining_new_generation_bytes=6*c.GIB-usage['new_bytes'],remaining_total_generation_bytes=20*c.GIB-usage['total_bytes'],resources=c.local_resources(),old32_attempts_and_receipts_preserved=True,prior_accepted_pairs_unchanged=True,only_two_rows_changed=True,accepted_MAIN_pairs=sum(k.startswith('V2_MAIN_') and v['status']=='CURRENT_ACCEPTED' for k,v in s['accepted_pairs'].items()),accepted_controls=sum(k.startswith('V2_CONTROL_') and v['status']=='CURRENT_ACCEPTED' for k,v in s['accepted_pairs'].items()),F_finite_residual_service_gate=ref(g['evidence_path']),new_native_calls=0,new_builds=0,next_batch='NONE_AUTHORIZED; only PRIMARY FOUR. No automatic retry,secondary,WB64,FWT,Btree,sensitivity or extra scan.',start_deadline=c.START_DEADLINE,intake_deadline=c.INTAKE_DEADLINE,all_qualifications=[r['qualification'] for r in plan['profiles']],interpretation='L2_DATA_FREE is diagnostic finite residual service, not hardwareP1 throughput. DWT R0 separates a conditional background contrast, not unique additive V/RO critical stall. MAIN pair aggregation must retain known denominator; original seven-inputGMUNKNOWN.')
 c.write_json(P/'FINAL_INDEPENDENT_TERMINAL_AUDIT.json',report)
 with (P/'STARTUP_LEDGER.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['queue_priority','condition','attempt_id','actual_start','native_start_unix','budget_bucket','exit_code','wait_status']);w.writeheader();w.writerows([{k:r[k] for k in w.fieldnames} for r in report['startup_order']])
 print(json.dumps(report,indent=2));return report
if __name__=='__main__':audit()
