"""Main-only resource bookkeeping for unused SYRK identities; no simulation."""
from pathlib import Path
import json,hashlib,os,sys,threading,copy,traceback,datetime,importlib.util
P=Path
MARKER='DTC_MAIN_PENDING_SYRK_RESOURCE_REFRESH_V1'
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,v):
 with P(p).open('xb')as f:f.write((json.dumps(v,sort_keys=True,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
def apply(config_path):
 cfg=read(config_path);assert cfg['schema']=='DTC_MAIN_PENDING_RESOURCE_REFRESH_CONFIG_V1'
 assert threading.current_thread()is threading.main_thread()and os.getpid()==1498278
 assert int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 assert cfg['installer_path']==str(P(__file__))and sha(__file__)==cfg['installer_sha256']
 for p,h in cfg['source_pins'].items():assert sha(p)==h,'RESOURCE_REFRESH_SOURCE_DRIFT '+p
 assert cfg['source_pins'][cfg['helper_path']]==cfg['helper_sha256']==sha(cfg['helper_path'])
 main=sys.modules['__main__'];assert not hasattr(main,MARKER),'OBSERVE_EXISTING_REFRESH_ATTEMPT_NO_BLIND_REAPPLY'
 frame=main.DTC_MAIN_BROAD_SHARED_CPU_INSTALL_V1['frame'];engine=frame.f_locals['engine'];res=frame.f_locals['res'];aging=res.DTC_LARGE_JOB_AGING_INSTALLED
 engine.assert_parent_lease();directory=P(cfg['directory']);directory.mkdir(parents=True,exist_ok=True)
 state=dict(frame=frame,engine=engine,res=res,aging=aging,phase='PREFLIGHT',directory=str(directory))
 setattr(main,MARKER,state)
 try:
  helper=load('Main_actual_pending_resource_refresh',cfg['helper_path']);state['helper']=helper
  with aging.lock:
   engine.assert_parent_lease();history=read(R/'control/HISTORICAL_RSS.json');policy=read(R/'control/RESOURCE_POLICY.json')
   before=engine.registered()[2];before=copy.deepcopy(before)
   protected=copy.deepcopy(aging.state.protected);tokens=copy.deepcopy(aging.state.pending_releases);calls=aging.calls
   previous=res.choose_dispatch
   def hold(*a,**kw):return None
   state.update(previous_choose=previous,hold=hold);res.choose_dispatch=hold
   state['phase']='FRESH_ADMISSION_HELD_NO_MODELS_INTERRUPTED'
   proposal=helper.prepare(R,engine,res,history,policy,cfg['scope_contract_path'],frame.f_locals['claims'])
   assert proposal['qualification_only']is False and len(proposal['items'])==10
   put(directory/'PROPOSAL.json',proposal);state['proposal']=proposal
   result=helper.apply(proposal,engine,res,history,frame.f_locals['claims'],aging,engine.assert_parent_lease)
   state.update(phase='RESOURCE_TRANSACTION_COMMITTED',transaction_result=result)
   after=engine.registered()[2];expected=copy.deepcopy(before)
   for item in proposal['items']:expected['admitted_specs'][item['cohort']]=item['new_spec_sha256']
   assert after==expected,'UNEXPECTED_NONRESOURCE_REGISTRY_CHANGE'
   assert protected==aging.state.protected and tokens==aging.state.pending_releases and calls==aging.calls
   assert res.choose_dispatch is hold
   ack=dict(schema='DTC_MAIN_PENDING_RESOURCE_REFRESH_ACK_V1',status='COMMITTED_UNUSED_SYRK_RESOURCE_ONLY_SAME_OWNER',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner_pid=os.getpid(),owner_start_ticks=977758783,configuration_sha256=sha(config_path),helper_sha256=sha(cfg['helper_path']),proposal_path=str(directory/'PROPOSAL.json'),proposal_sha256=sha(directory/'PROPOSAL.json'),items=len(proposal['items']),same_CPU_DB_count=sum(i['DB_present']for i in proposal['items']),transaction_result=result,only_RAM_RSS_AS_and_current_alias_binding_SHA_changed=True,science_and_old_negative_UUIDs_preserved=True,aging_state_and_R_tokens_unchanged=True,previous_chooser_restored=True,model_starts_by_callback=0,new_grants=0,budget=after['budget'],remaining=after['remaining'])
   put(directory/'ACK.json',ack);state.update(phase='COMMITTED_ACKED',ACK=ack)
   # Release only after every validation and durable receipt succeeds.
   res.choose_dispatch=previous
   return ack
 except BaseException as error:
  # If interrupted, retain the qualified helper's SAME immutable proposal and
  # held admission for explicit forward reconciliation. Healthy models continue.
  # Re-establish this transaction's hold only when the current reference is
  # our own hold or exact saved predecessor; never overwrite a foreign wrapper.
  admission_held=False
  with aging.lock:
   if 'hold' in state and res.choose_dispatch in (state['hold'],state['previous_choose']):
    res.choose_dispatch=state['hold'];admission_held=True
  failure=dict(admission_held=admission_held,status='RESOURCE_REFRESH_HOLD_PRESERVE_FOR_FORWARD_RECONCILIATION',phase=state['phase'],error=repr(error),traceback=traceback.format_exc(),automatic_retry=False,healthy_models_signaled=0,models_started_by_callback=0,new_grants=0,proposal_path=str(directory/'PROPOSAL.json')if(directory/'PROPOSAL.json').exists()else None)
  state.update(phase='HOLD_PRESERVE',failure=failure)
  try:put(directory/'ERROR.json',failure)
  except BaseException as e:state['error_evidence_failure']=repr(e)
  return failure
