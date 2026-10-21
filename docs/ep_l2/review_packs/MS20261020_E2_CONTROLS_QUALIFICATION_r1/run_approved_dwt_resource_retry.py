"""Finite two-condition user-approved intake through the original controller.

Uses the original registry, locks, resource guards, execution and acceptance.
No retry loop, detached supervisor or production source change.
"""
from pathlib import Path
import copy,json,sys,time,subprocess
P=Path(__file__).resolve().parent;ROOT=P.parents[3];N=P/'APPROVED_DWT_RESOURCE_RETRY'
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'));sys.path.insert(0,str(P))
import coordinator as c,runner,controller
from report_approved_controls import checkpoint

def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(Path(p).resolve()),sha256=c.digest(p))
def published(commit,path):
 path=Path(path)
 assert subprocess.check_output(['git','-C',str(ROOT),'show',commit+':'+str(path.relative_to(ROOT))])==path.read_bytes()

def main():
 coord=c.Coordinator();s=coord.snapshot();plan=read(N/'PLAN.json')
 publication=read(N/'EXECUTION_READY_REMOTE_READBACK.json')['remote_commit']
 for path in [Path(__file__),P/'report_approved_controls.py',N/'PLAN.json']:
  published(publication,path)
 for artifact in [plan['user_approval'],plan['proposal'],plan['approved_matrix'],plan['queue']]:
  assert c.digest(artifact['path'])==artifact['sha256'];published(publication,artifact['path'])
 approval=read(plan['user_approval']['path']);proposal=read(plan['proposal']['path'])
 assert approval['approved'] is True and approval['user_answer']=='批准这2项重分配'
 assert s['actual_starts']==30 and s['remaining_start_capacity']==10 and s['uncertain_start_intents']==0
 assert s['controller']['state']=='STOPPED' and s['t0_unix']==plan['T0']==1792414193
 assert s['full_system_matrix']==proposal['original_matrix_record']
 assert time.time()<c.START_DEADLINE and time.time()+10800<=c.INTAKE_DEADLINE
 data=read(c.SHARED/'RUN_REGISTRY.json')
 assert not any(r['status'] in c.ACTIVE and r.get('experiment_id')==c.CAMPAIGN for r in data['runs'].values())
 resources=c.local_resources();usage=c.output_usage();first=read(plan['profiles'][0]['spec']['path'])
 c.resource_gate(data,'simulation',1,first['memory_bytes'],first['maximum_result_bytes'],resources,usage)
 assert usage['new_bytes']<=plan['new_result_capacity_must_be_at_most'] and usage['total_bytes']<=plan['total_result_capacity_must_be_at_most']
 matrix=read(plan['approved_matrix']['path']);cells=c.policy_v2.validate_matrix(matrix)
 before={r['condition_id']:r for r in s['full_system_matrix']['matrix']['conditions']};after={r['condition_id']:r for r in cells}
 assert set(before)-set(after)=={r['old_unstarted_condition_id'] for r in proposal['changes']}
 assert set(after)-set(before)=={r['new_condition_id'] for r in proposal['changes']}
 assert all(before[k]==after[k] for k in set(before)&set(after))
 for row,change in zip(plan['profiles'],proposal['changes']):
  for artifact in [row['spec'],row['qualification']]:
   assert c.digest(artifact['path'])==artifact['sha256'];published(publication,artifact['path'])
  spec=read(row['spec']['path']);old=[a for a in s['attempts'] if a['run_key']==row['run_key']]
  assert len(old)==1 and old[0]['attempt_id']==row['previous_attempt'] and old[0]['state']=='RESOURCE_LIMIT'
  assert spec['retry_previous_attempt']==old[0]['attempt_id'] and spec['identity']==old[0]['identity']
  assert spec['profile_semantics']==read(change['spec']['path'])['profile_semantics']
  assert spec['budget_bucket']=='two_workload_local_diagnostics' and spec['qualification_id']==row['qualification_id']
  assert not any(a.get('condition_id')==change['old_unstarted_condition_id'] or (a['identity']['workload']=='FWT_7_21' and a['profile']==change['old_profile']) for a in s['attempts'])
 # Adopt only the approved bookkeeping revision. No scientific receipts, charges,
 # T0, group limits or production identities are changed.
 with coord.locked() as (all_data,item):
  assert item['controller']['state']=='STOPPED' and item['actual_starts']==30 and item['full_system_matrix']==proposal['original_matrix_record']
  old=copy.deepcopy(item['full_system_matrix'])
  history=dict(previous=old,user_approval=plan['user_approval'],proposal=plan['proposal'],publication=publication,at_unix=time.time(),exact_replacements=proposal['changes'],actual_starts=30,remaining=10,T0=item['t0_unix'],reservations_unchanged=copy.deepcopy(item['reservations']),reason=proposal['scientific_slot_semantics'])
  item.setdefault('user_approved_matrix_revision_history',[]).append(history)
  item['full_system_matrix']=dict(path=plan['approved_matrix']['path'],sha256=plan['approved_matrix']['sha256'],matrix=matrix,D_publication=old['D_publication'],E_user_approved_revision_publication=publication,status='USER_APPROVED_EXACT_TWO_DWT_RESOURCE_RETRY_LOCAL_DIAGNOSTIC_REALLOCATION')
  item['target_simulators']=1
 adoption=N/'MATRIX_ADOPTION_RECEIPT.json'
 c.write_json(adoption,dict(schema='E2_EXACT_TWO_RETRY_MATRIX_ADOPTION_V1',status='ADOPTED',at_unix=time.time(),history=history,actual_starts=30,remaining=10,matrix=plan['approved_matrix'],old_attempts_preserved=['E027_a4c2f04e','E028_f9b6ca83'],single_lane=True,no_starts_by_adoption=True))
 audits=[]
 for row in plan['profiles']:
  audit=runner.inspect(read(row['spec']['path']),coord)
  assert audit['expected_full_instructions']==row['expected_full_instructions'] and audit['run_key']==row['run_key']
  audits.append(dict(condition_id=row['condition_id'],audit=audit))
 # Same immutable production binary/archive and original build/native proofs.
 source=s['final_source_identity'];archive=Path('/workspace/build/ep-l2-ms20261020-a-wad-pending-r40/libgpgpusim.a')
 assert c.digest(archive)=='3c6ce15b88ae16c17c30718618aedc769495168d6e3d0c371270ba95b7b0aca8'
 resources=c.local_resources();usage=c.output_usage();data=read(c.SHARED/'RUN_REGISTRY.json')
 c.resource_gate(data,'simulation',1,first['memory_bytes'],first['maximum_result_bytes'],resources,usage)
 admission=N/'QUALIFIED_ADMISSION.json'
 c.write_json(admission,dict(status='PASS',at_unix=time.time(),resources=resources,output_usage=usage,actual_starts=30,remaining=10,single_lane=True,audits=audits,source_identity=source,archive=ref(archive),approval=plan['user_approval'],matrix_adoption=ref(adoption),qualification_reused_no_native_rebuild=True))
 checkpoint('DWT_RETRY_USER_APPROVED_QUALIFIED_ADMISSION',extra=[adoption,admission])
 notice=dict(status='USER_APPROVED_AND_QUALIFIED_NOT_YET_STARTED',publication=read(P/'DWT_RETRY_USER_APPROVED_QUALIFIED_ADMISSION_REMOTE_READBACK.json')['remote_commit'],plan=ref(N/'PLAN.json'),new_pair_ids=[r['control_pair_id'] for r in plan['profiles']],old_attempts_unchanged=['E027_a4c2f04e','E028_f9b6ca83'],request='Use new retry condition/pair/attempt provenance and retained DWT S anchor. Old resource stops remain invalid and charged. Incremental accepted notices follow only real independent terminal acceptance.')
 for channel in [c.HANDOFF/'events',c.HANDOFF/'inbox',Path('/workspace/ep_l2_ms20261019_shared')]:
  c.write_json(channel/'E2_TO_A2_D_APPROVED_DWT_RETRY_ALLOCATION.json',notice)
 original=controller.roll_pairs
 def immediate(coord,requests):
  pairs=original(coord,requests)
  for pair in pairs:checkpoint(pair['pair_id']+'_CURRENT_ACCEPTED',pair)
  return pairs
 controller.roll_pairs=immediate
 result=controller.step(coord,plan['queue']['path'])
 rp=N/'CONTROLLER_RESULT.json';c.write_json(rp,result)
 checkpoint('DWT_APPROVED_TWO_RETRIES_TERMINAL',extra=[rp])
 s=coord.snapshot()
 print(json.dumps(dict(status='BOTH_CURRENT_ACCEPTED' if all(s['accepted_pairs'].get(row['control_pair_id'],{}).get('status')=='CURRENT_ACCEPTED' for row in plan['profiles']) else 'PRECISE_TERMINAL_REVIEW_REQUIRED_NO_AUTOMATIC_REPLAY',actual_starts=s['actual_starts'],remaining=s['remaining_start_capacity'],controller=s['controller'],result=result)),flush=True)
if __name__=='__main__':main()
