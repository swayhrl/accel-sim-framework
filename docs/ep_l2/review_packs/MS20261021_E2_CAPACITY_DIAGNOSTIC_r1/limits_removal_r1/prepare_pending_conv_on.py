"""OWNER DRAFT: fresh-source adoption and exact single pending Conv ON publication.

No application/controller/native launch; original freeze and all nine started
specs/runkeys remain unchanged. Does not re-register input selection or Q.
"""
from pathlib import Path
import argparse,contextlib,copy,importlib.util,io,json,sys,time
ROOT=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
PACK=ROOT/'docs/ep_l2/review_packs/MS20261021_E2_CAPACITY_DIAGNOSTIC_r1';P=PACK/'limits_removal_r1';U=ROOT/'util/ep_l2/mechanism_e'
sys.path.insert(0,str(U));import coordinator as c,limits_policy,capacity_policy
read=lambda p:json.loads(Path(p).read_text())
ref=lambda p:dict(path=str(Path(p).resolve()),sha256=c.digest(p))

def safe_boundary(data):
 item=data[c.FIELD];c.require(item['controller']['state']=='STOPPED' and item['uncertain_start_intents']==0,'original controller not safely stopped')
 prior=item['controller'].get('process')
 if prior:
  try:alive=c.process_identity(prior['pid'])==prior
  except (FileNotFoundError,ProcessLookupError):alive=False
  c.require(not alive,'original controller process not gone')
 c.require(not any(r.get('experiment_id')==c.CAMPAIGN and r['status'] in c.ACTIVE for group in ('runs','resource_leases') for r in data[group].values()),'active E application or lease')
 return item

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--adopt-and-prepare-only',action='store_true',required=True);ap.parse_args()
 c.tooling_binding();coord=c.Coordinator();install=read(P/'OWNER_SOURCE_INSTALL_RECEIPT.json');remote=read(P/'SOURCE_REMOTE_READBACK.json')
 c.require(install['status']=='SOURCE_APPLIED_AT_NATURAL_STOP_PENDING_REMOTE_AND_CLIENT','missing actual source installation')
 c.require(c.verify_extension_binding(c.HANDOFF/'CLIENT_CONTRACT.json')==remote['remote_commit'],'source/CLIENT publication not verified')
 # This file must be a new Python process after installation, never an old-module callback.
 with coord.registry.locked() as data:safe_boundary(data)
 adoption=coord.adopt_start_and_time_limit_removal(P/'USER_APPROVAL.json');c.write_json(P/'ACTUAL_LIMITS_ADOPTION_RECEIPT.json',dict(status='ADOPTED_NO_APPLICATION_STARTED',at_unix=time.time(),result=adoption))
 sp=importlib.util.spec_from_file_location('publisher',PACK.parent/'MS20261020_E2_TAKEOVER_r1/publish.py');pub=importlib.util.module_from_spec(sp);sp.loader.exec_module(pub)
 with coord.registry.locked() as data:
  item=safe_boundary(data);c.require(limits_policy.active(item),'exact removal not adopted')
  old=read(PACK/'PLAN.json');queue=read(old['queue']['path'])
  frozen_queue=read(P/'QUEUE_BEFORE_DRAIN.json')
  c.require(c.digest(P/'QUEUE_BEFORE_DRAIN.json')==old['queue']['sha256'],'frozen queue backup does not match original PLAN')
  actual_without_drain=copy.deepcopy(queue);drain=actual_without_drain.pop('limits_removal_drain_request',None)
  c.require(actual_without_drain==frozen_queue and drain and drain['approval']==ref(P/'USER_APPROVAL.json'),'queue changed beyond approved drain metadata')
  c.require(len(old['conditions'])==10 and len(old['pairs'])==5,'finite ten-condition science changed')
  condition='V3_CAPACITY_convolutionSeparable_S_ON';row=next(r for r in old['conditions'] if r['condition_id']==condition)
  c.require(not any(a['run_key']==row['run_key'] for a in item['attempts']),'Conv ON already attempted; no retry grant')
  c.require(all(any(a['run_key']==r['run_key'] for a in item['attempts']) for r in old['conditions'] if r['condition_id']!=condition),'some other approved condition was never started; explicit root review needed')
  original_path=Path(row['spec']['path']);c.require(c.digest(original_path)==row['spec']['sha256'],'old Conv ON spec changed');spec=read(original_path);prior_spec=copy.deepcopy(spec)
  spec['timeout_seconds']=None;spec['operational_limits_override']=limits_policy.operational_override(spec)
  c.require(spec['identity']==prior_spec['identity'] and c.run_key(spec['identity'])==row['run_key'],'frozen scientific identity/runkey changed')
  c.require(spec['qualification_id']==row['qualification_id'] and spec['comparison_invariants_sha256']==prior_spec['comparison_invariants_sha256'],'Q/comparison changed')
  c.require(limits_policy.effective_timeout(item,spec) is None,'operational override not exact')
  limits_policy.assert_condition_unstarted(item,spec);capacity_policy.condition_check(item,spec,c.digest)
  outspec=P/'CONV_ON_SPEC.json';outqueue=P/'PENDING_CONV_ON_QUEUE.json';c.write_json(outspec,spec)
  pending=copy.deepcopy(queue);pending.pop('limits_removal_drain_request',None);pending['specs']=[ref(outspec)];pending['pairs']=copy.deepcopy(queue['pairs']);pending['operational_limits_approval']=ref(P/'USER_APPROVAL.json')
  c.require(pending['input_and_profile_freeze_unix']==queue['input_and_profile_freeze_unix'],'freeze must retain original time')
  c.require(len(pending['pairs'])==5,'all original pair requests retained for roll/dedupe');c.write_json(outqueue,pending)
  plan=copy.deepcopy(old);newrow=next(r for r in plan['conditions'] if r['condition_id']==condition);newrow['spec']=ref(outspec)
  c.require(all(x==y for x,y in zip(old['conditions'],plan['conditions']) if x['condition_id']!=condition),'started row mutation')
  plan['queue']=ref(outqueue);plan['maximum_new_starts']=None;plan['maximum_campaign_starts']=None;plan['authorized_condition_count']=10;plan['operational_limits_override']=spec['operational_limits_override']
  c.require(not (P/'PENDING_ACTIVATION_RECEIPT.json').exists(),'pending activation already recorded; root review required instead of overwrite')
  c.write_json(P/'PLAN_BEFORE_ACTIVATION.json',old);c.write_json(PACK/'PLAN.json',plan)
  if (PACK/'EXECUTION_READY_REMOTE_READBACK.json').exists():c.write_json(P/'EXECUTION_READY_BEFORE_ACTIVATION.json',read(PACK/'EXECUTION_READY_REMOTE_READBACK.json'))
  receipt=dict(status='EXACT_SINGLE_PENDING_CONV_ON_PREPARED_NOT_STARTED',at_unix=time.time(),actual_starts=item['actual_starts'],approval=ref(P/'USER_APPROVAL.json'),new_spec=ref(outspec),new_queue=ref(outqueue),new_plan=ref(PACK/'PLAN.json'),frozen_unix=pending['input_and_profile_freeze_unix'],original_nine_started_specs_unchanged=True,original_runkey=row['run_key'],original_qualification=row['qualification'],new_application_starts=0)
  c.write_json(P/'PENDING_ACTIVATION_RECEIPT.json',receipt)
  paths=[PACK/'PLAN.json',PACK/'run.py',PACK/'report.py',outspec,outqueue]+[p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
  with contextlib.redirect_stdout(io.StringIO()):rb=pub.publish('ep-l2 E2: publish exact pending Conv ON after approved limits adoption',paths)
  c.write_json(P/'ACTIVATION_REMOTE_READBACK.json',rb);c.write_json(PACK/'EXECUTION_READY_REMOTE_READBACK.json',rb)
 print(json.dumps(dict(status='PENDING_CONV_ON_REMOTE_VERIFIED_NOT_STARTED',remote_commit=rb['remote_commit'],next='Original pack run.py --execute-exact-approved-ten',actual_starts=item['actual_starts'],new_application_starts=0)),flush=True)

if __name__=='__main__':main()
