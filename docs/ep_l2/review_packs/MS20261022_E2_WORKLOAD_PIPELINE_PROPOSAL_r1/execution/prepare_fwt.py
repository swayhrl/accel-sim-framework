"""Prepare exact approved FWT restoration assets; never runs/registers an app."""
from pathlib import Path
import copy,hashlib,json,sys,time
E=Path(__file__).resolve().parent;P=E.parent;ROOT=P.parents[3]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def prepare(override_factory=None,bucket='EPL2_MAIN61_FWT_RESTORATION_20261022_r1'):
 proposal=json.loads((P/'PROPOSAL.json').read_text());rows=[];specs=[]
 for row in proposal['conditions'][:2]:
  old=ROOT/row['frozen_spec_reference']['path'];assert digest(old)==row['frozen_spec_reference']['sha256']
  frozen=json.loads(old.read_text());v=copy.deepcopy(frozen)
  v.update(condition_id=row['condition_id'],budget_bucket=bucket,approved_workload_batch=row['batch_id'],
    retry_previous_attempt=row['retry_previous_attempt'],retry_reason=row['retry_reason'])
  if override_factory is not None:
   v['timeout_seconds']=None;v['operational_limits_override']=override_factory(v)
  # Scientific input, config, profile, source, comparison and termination stay exact.
  permitted={'condition_id','budget_bucket','approved_workload_batch','retry_previous_attempt','retry_reason','timeout_seconds','operational_limits_override'}
  assert all(v[k]==x for k,x in frozen.items() if k not in permitted)
  assert v['identity']==frozen['identity'] and v['identity']['termination_contract']['timeout_seconds']==10800
  assert v['qualification_id']==row['qualification_id_reused'] and v['maximum_result_bytes']==384*2**20 and v['memory_bytes']==8*2**30
  dst=E/('FWT_'+row['profile']+'_SPEC.json');put(dst,v);specs.append(v)
  key=hashlib.sha256(json.dumps(v['identity'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
  rows.append(dict(condition_id=v['condition_id'],profile=v['profile'],batch_id=row['batch_id'],workload=row['workload'],run_key=key,
    qualification_id=v['qualification_id'],qualification=dict(path=str(ROOT/'docs/ep_l2/review_packs/MS20261020_E2_MAIN61_FWT_FIRST_PAIR_CONTINUATION_r1/FWT_7_21_QUALIFICATION.json'),sha256=v['qualification_id']),
    spec=dict(path=str(dst),sha256=digest(dst)),pair_id='V4_FWT_MAIN61_RESTORE_S_F',frozen_spec=row['frozen_spec_reference']))
 sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
 import coordinator as c
 assert all(c.run_key(spec['identity'])==row['run_key'] for spec,row in zip(specs,rows))
 pair=dict(pair_id='V4_FWT_MAIN61_RESTORE_S_F',left_run_key=rows[0]['run_key'],right_run_key=rows[1]['run_key'],workload='FWT_7_21',
   mechanism='MAIN61_ORIGINAL_FINITE_S_VS_FULL_F_RESTORATION; original frozen FWT input; old INCOMPLETE charged and retained')
 queue=dict(campaign_id=c.CAMPAIGN,prepared_by='E',authority_commit=c.AUTHORITY,input_and_profile_freeze_unix=time.time(),
  specs=[r['spec'] for r in rows],pairs=[pair])
 put(E/'FWT_READY_QUEUE.json',queue)
 out=dict(schema='E2_APPROVED_WORKLOAD_EXECUTION_PLAN_V1',proposal_id=proposal['proposal_id'],T0=proposal['baseline']['T0'],
  maximum_new_actual_starts=4,authorized_exact_condition_ids=[r['condition_id'] for r in proposal['conditions']],
  source_identity=proposal['common_contract']['source_identity'],conditions=rows,pairs=[pair],
  queue=dict(path=str(E/'FWT_READY_QUEUE.json'),sha256=digest(E/'FWT_READY_QUEUE.json')),
  collector_and_qualification_reserve_bytes=proposal['cost']['qualification_future_only_separate_cap_bytes']+proposal['cost']['collector_metadata_future_only_separate_cap_bytes'],
  effective_timeout_override_sealed=override_factory is not None)
 put(E/'FWT_PLAN.json',out)
 put(E/'FWT_SPEC_PREPARATION_REVIEW.json',dict(status='PREPARED_NOT_STARTED',scientific_fields_unchanged=True,
  current_operational_override_sealed=override_factory is not None,conditions=rows,application_native_build_starts=0))
 return out
if __name__=='__main__':
 print(json.dumps(prepare(),indent=2))
