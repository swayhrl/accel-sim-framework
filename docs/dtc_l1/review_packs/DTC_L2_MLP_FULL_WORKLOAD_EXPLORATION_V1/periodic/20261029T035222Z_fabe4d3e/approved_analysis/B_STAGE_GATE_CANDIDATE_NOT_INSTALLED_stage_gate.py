"""Inert, fail-closed gate on the sole owner's captured adaptive recommendation.

This version has no activation branch: original recommendations are observed but
never forwarded to legacy registry.extend. Current models are not intercepted.
"""
import pathlib,json,hashlib,copy,threading,sys,os
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
ID='DTC_ADAPTIVE_STAGE_TRANSITION_GATE_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def objsha(v):return hashlib.sha256(js(v)).hexdigest()
def record(cfg):
 keys=['request','overlay_id','source_path','source_sha256','dependency_pins','prior_recommend_source_path','prior_recommend_source_sha256','mode','QA_path','QA_sha256','readback_path','readback_sha256']
 return dict({k:copy.deepcopy(cfg[k])for k in keys},configuration_sha256=objsha(cfg),status='ACTIVE_NEXT_STAGE_PROPOSALS_HELD_NO_LEGACY_EXTEND',new_grants=0)
def validate(cfg,q):
 assert cfg['schema']==cfg['overlay_id']==ID and cfg['request']==q['request']==REQ
 assert cfg['mode']=='HOLD_FOR_SEPARATELY_QUALIFIED_TRANSACTIONAL_STAGE'
 assert cfg['source_path']==str(P(__file__))and cfg['source_sha256']==sha(__file__)
 qual=cfg.get('qualification_only')is True
 assert qual and q.get('qualification_only')is True and P(cfg['root'])!=R if qual else not q.get('qualification_only',False)and P(cfg['root'])==R
 for p,h in cfg['dependency_pins'].items():assert sha(p)==h,'STAGE_GATE_SOURCE_DRIFT '+p
 assert cfg['dependency_pins'][cfg['source_path']]==cfg['source_sha256']and cfg['dependency_pins'][cfg['prior_recommend_source_path']]==cfg['prior_recommend_source_sha256']
 for k in ['QA','readback']:assert sha(cfg[k+'_path'])==cfg[k+'_sha256']
 qa=read(cfg['QA_path']);rb=read(cfg['readback_path'])
 assert qa['status']=='PASS'and qa['legacy_proposals_suppressed_qualified']is True and qa['no_false_full35_or_IR_union_qualified']is True
 assert qa['source_sha256']==rb['source_sha256']==cfg['source_sha256']and rb['verified']is True and rb['QA_sha256']==cfg['QA_sha256']
 assert qa['dependency_pins']==rb['dependency_pins']==cfg['dependency_pins']
 if qa.get('qualification_only')or rb.get('qualification_only'):assert qual
 assert all(q['additional_operational_overlays'][ID].get(k)==v for k,v in record(cfg).items()),'STAGE_GATE_RECORD_MISMATCH'
 return True
def append_locked(reg,request,before,row):
 """Pure passed-q CAS. Main invokes only through actual update_authority."""
 q=reg['registered_future_requests'][request];assert q==before and ID not in q['additional_operational_overlays']
 q['additional_operational_overlays'][ID]=copy.deepcopy(row)
 expected=copy.deepcopy(before);expected['additional_operational_overlays'][ID]=copy.deepcopy(row);assert q==expected
def hold(reason,evidence=None):
 return dict(schema='DTC_L2_MLP_ADAPTIVE_DECISIONS_V1',state='QUALIFIED_NEXT_STAGE_TRANSACTION_REQUIRED',proposals=[],decisions=[dict(action='NEXT_STAGE_HOLD',reason=reason)],formal_candidates=[],adoption_ready=False,scientific_stage_complete=False,requires_engineering_review=True,all_negative_inputs_retained=True,legacy_recommendation_evidence=evidence,scope_union_performed=False,new_grants=0,healthy_models_continue=True)
def light(original):
 return dict(original_sha256=objsha(original),state=original.get('state'),proposal_count=len(original.get('proposals',[])),proposals=[{k:p.get(k)for k in ['proposal_id','profile','cells','phase','new_cell_count']}for p in original.get('proposals',[])],adoption_ready=original.get('adoption_ready'),scientific_stage_complete=original.get('scientific_stage_complete'),pending_profiles=original.get('pending_profiles'),requires_engineering_review=original.get('requires_engineering_review'),policy_contract_sha256=objsha(original.get('contract')))
def install_on_frame(frame,cfg,owner_assert,main=None):
 assert threading.current_thread()is threading.main_thread();owner_assert();main=main or sys.modules['__main__'];assert not hasattr(main,ID)
 engine=frame.f_locals['engine'];res=frame.f_locals['res'];aging=res.DTC_LARGE_JOB_AGING_INSTALLED;adaptive=frame.f_locals['adaptive'];prior=adaptive.recommend
 assert P(prior.__code__.co_filename)==P(cfg['prior_recommend_source_path'])and sha(prior.__code__.co_filename)==cfg['prior_recommend_source_sha256']
 if not cfg.get('qualification_only'):
  assert os.getpid()==1498278 and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
  assert frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==R/'tools/l2_ops.py'
 def references():return(frame.f_locals['engine'],frame.f_locals['res'],frame.f_locals['adaptive'],frame.f_locals['registry'],frame.f_globals['worker'],res.choose_dispatch,res.resources,aging.original,aging.frame_provider,aging.state,aging.state.advance,frame.f_locals['consumer'].safe_finish,frame.f_locals['claims'],frame.f_locals['registry'].extend)
 with aging.lock:
  validate(cfg,engine.registered()[2]);refs=references();frozen=copy.deepcopy(cfg)
  state=dict(frame=frame,aging=aging,adaptive=adaptive,prior=prior,cfg=frozen,refs=refs,last_issue=None,last_original=None,calls=0,original_calls=0)
  def recommend(summary,scope,history=None):
   with aging.lock:
    state['calls']+=1
    try:
     assert cfg==frozen and references()==refs and adaptive.recommend is state['wrapper'],'STAGE_GATE_REFERENCE_OR_CONFIG_DRIFT'
     owner_assert();validate(cfg,engine.registered()[2])
     if cfg.get('next_batch_contract')is not None:
      state['last_issue']=dict(stage='UNKNOWN_BATCH_NOT_AUTHORIZED_BY_THIS_GATE',new_grants=0)
      return hold('Unknown next-batch contract: this gate has no release/registrar branch')
     # Exactly once, to preserve the old pure policy's diagnostic evidence.
     # Nothing from its proposal/completion/adoption output can reach extend.
     state['original_calls']+=1;original=prior(summary,scope,history)
     assert isinstance(original,dict),'ORIGINAL_RECOMMENDATION_NOT_MAPPING'
     evidence=light(original);state['last_original']=evidence;state['last_issue']=None
     return hold('Original terminal negatives or provisional common-population decisions do not authorize the next batch; require explicit source-bound transactional stage',evidence)
    except BaseException as error:
     state['last_issue']=dict(stage='ADAPTIVE_STAGE_GATE_FAIL_CLOSED',error=repr(error),new_grants=0)
     return hold('Gate/old recommendation unavailable; preserve all existing identities and wait for Main',state['last_original'])
  state['wrapper']=recommend;adaptive.recommend=recommend;setattr(main,ID,state)
  state['receipt']=dict(status='NEXT_STAGE_LEGACY_PROPOSAL_GATE_INSTALLED',only_changed_reference='captured adaptive.recommend',old_registry_extend_preserved=True,worker_E_R_claims_consumer_preserved=True,new_grants=0,models_started=0)
  return state
def restore_in_owner(owner_assert,main=None):
 assert threading.current_thread()is threading.main_thread();owner_assert();main=main or sys.modules['__main__'];state=getattr(main,ID)
 with state['aging'].lock:
  assert state['adaptive'].recommend is state['wrapper'],'REFUSE_NEWER_STAGE_GATE'
  state['adaptive'].recommend=state['prior'];delattr(main,ID)
 return dict(status='EXACT_PRIOR_RECOMMENDATION_REFERENCE_RESTORED',warning='Restoring this gate re-exposes the legacy automatic extend path; Main must install qualified replacement before empty-queue transition.',models_started=0,new_grants=0)
