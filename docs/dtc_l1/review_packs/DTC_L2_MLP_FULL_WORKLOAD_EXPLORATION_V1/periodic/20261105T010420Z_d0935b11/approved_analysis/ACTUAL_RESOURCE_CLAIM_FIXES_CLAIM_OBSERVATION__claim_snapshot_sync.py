"""Main-only claim observation bookkeeping. No import-time mutation.

Only observed_model bool differences may be persisted, using the current
scheduler's unchanged saveclaims closure. No claim is added, removed or repriced.
"""
import pathlib,json,hashlib,copy,os,threading,sys,types
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
ID='OWNER_CLAIM_SNAPSHOT_SYNC_V1'
OPS_SHA='a53f4933d2f0a7479a15d0e6dd8aa0501c4762d6b2161363b9467472a43fc1dc'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def objsha(v):return hashlib.sha256((json.dumps(v,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
def birth():return int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])
def record(cfg):
 keys=['request','overlay_id','source_path','source_sha256','ops_source_path','ops_source_sha256','prior_choose_source_path','prior_choose_source_sha256','dependency_pins','owner','scheduler_thread_ident','QA_path','QA_sha256','readback_path','readback_sha256']
 return dict({k:copy.deepcopy(cfg[k])for k in keys},configuration_sha256=objsha(cfg),status='ACTIVE_OPERATIONAL_BOOKKEEPING_ONLY',new_grants=0)
def validate(cfg,q):
 assert cfg['schema']==cfg['overlay_id']==ID and cfg['request']==q['request']and cfg['status']=='ACTIVE_OPERATIONAL_BOOKKEEPING_ONLY'
 assert cfg['source_path']==str(P(__file__))and cfg['source_sha256']==sha(__file__)
 assert cfg['ops_source_path']==str(R/'tools/l2_ops.py')and cfg['ops_source_sha256']==sha(cfg['ops_source_path'])==OPS_SHA
 qual=cfg.get('qualification_only')is True
 assert qual and q.get('qualification_only')is True and P(cfg['root'])!=R if qual else not q.get('qualification_only',False)and P(cfg['root'])==R
 for path,h in cfg['dependency_pins'].items():assert sha(path)==h,'CLAIM_SYNC_SOURCE_DRIFT '+path
 assert cfg['dependency_pins'][cfg['source_path']]==cfg['source_sha256']and cfg['dependency_pins'][cfg['ops_source_path']]==OPS_SHA
 for key in ['QA','readback']:assert sha(cfg[key+'_path'])==cfg[key+'_sha256']
 qa=read(cfg['QA_path']);rb=read(cfg['readback_path']);assert qa['status']=='PASS'and qa['saveclaims_real_serialization_qualified']is True and qa['observation_flags_only_qualified']is True
 assert rb['verified']is True and rb['QA_sha256']==cfg['QA_sha256']
 for d in [qa,rb]:assert d['source_sha256']==cfg['source_sha256']and d['dependency_pins']==cfg['dependency_pins']
 if qa.get('qualification_only')or rb.get('qualification_only'):assert qual
 assert all(q['additional_operational_overlays'][ID].get(k)==v for k,v in record(cfg).items()),'CLAIM_SYNC_OPERATIONAL_ROW_MISMATCH'
 return True
def code_shape(code):
 return dict(bytecode=code.co_code.hex(),names=code.co_names,varnames=code.co_varnames,freevars=code.co_freevars,cellvars=code.co_cellvars,argcount=code.co_argcount,kwonlyargcount=code.co_kwonlyargcount,consts=[code_shape(x)if isinstance(x,types.CodeType)else repr(x)for x in code.co_consts])
def expected_saveclaims_code(path):
 module=compile(P(path).read_bytes(),str(path),'exec');parent=next(c for c in module.co_consts if isinstance(c,types.CodeType)and c.co_name=='run_scheduler');return next(c for c in parent.co_consts if isinstance(c,types.CodeType)and c.co_name=='saveclaims')
def observation_delta(disk,live):
 assert isinstance(disk,dict)and set(disk)=={'claims'}and isinstance(disk['claims'],dict)and isinstance(live,dict)
 assert set(disk['claims'])==set(live),'CLAIM_SYNC_STRUCTURAL_KEY_DIFFERENCE'
 changed=[]
 for cohort,memory in live.items():
  persisted=disk['claims'][cohort]
  assert isinstance(memory,dict)and isinstance(persisted,dict)and set(memory)==set(persisted),'CLAIM_SYNC_STRUCTURAL_ROW_DIFFERENCE'
  assert type(memory['observed_model'])is bool and type(persisted['observed_model'])is bool,'CLAIM_SYNC_OBSERVATION_NOT_BOOL'
  assert objsha({k:v for k,v in memory.items()if k!='observed_model'})==objsha({k:v for k,v in persisted.items()if k!='observed_model'}),'CLAIM_SYNC_COST_CPU_OR_OTHER_FIELD_DIFFERENCE'
  if memory['observed_model']!=persisted['observed_model']:changed.append(cohort)
 return sorted(changed)
def install_on_frame(frame,cfg,owner_assert,main=None):
 assert threading.current_thread()is threading.main_thread(),'MAIN_THREAD_ONLY'
 owner_assert();main=main or sys.modules['__main__'];assert not hasattr(main,ID)
 engine=frame.f_locals['engine'];res=frame.f_locals['res'];aging=res.DTC_LARGE_JOB_AGING_INSTALLED;claims=frame.f_locals['claims'];saveclaims=frame.f_locals['saveclaims'];previous=res.choose_dispatch
 assert os.getpid()==cfg['owner']['pid']and birth()==cfg['owner']['start_ticks'],'WRONG_OWNER_BIRTH'
 assert previous.__code__.co_filename==cfg['prior_choose_source_path']and sha(previous.__code__.co_filename)==cfg['prior_choose_source_sha256']
 expected=code_shape(expected_saveclaims_code(cfg['ops_source_path']))
 def refs():return(frame.f_locals['claims'],frame.f_locals['saveclaims'],frame.f_globals['worker'],res.resources,aging.original,aging.frame_provider,aging.state,aging.state.advance)
 original_refs=refs()
 def guard():
  assert os.getpid()==cfg['owner']['pid']and birth()==cfg['owner']['start_ticks']
  assert refs()==original_refs and frame.f_locals['claims']is claims and frame.f_locals['saveclaims']is saveclaims,'CLAIM_SYNC_OWNER_REFERENCE_DRIFT'
  assert saveclaims.__code__.co_filename==cfg['ops_source_path']and saveclaims.__qualname__=='run_scheduler.<locals>.saveclaims'and code_shape(saveclaims.__code__)==expected,'CLAIM_SYNC_ORIGINAL_SAVECLAIMS_CODE_DRIFT'
  names=saveclaims.__code__.co_freevars;assert names.count('claims')==1 and saveclaims.__closure__[names.index('claims')].cell_contents is claims,'CLAIM_SYNC_CLOSURE_NOT_CURRENT_CLAIMS'
  assert P(saveclaims.__globals__['R'])==P(cfg['root']),'CLAIM_SYNC_WRITER_ROOT_DRIFT'
  if not cfg.get('qualification_only'):assert frame.f_code.co_name=='run_scheduler'and frame.f_code.co_filename==cfg['ops_source_path']
  engine.assert_parent_lease();validate(cfg,engine.registered()[2])
 with aging.lock:
  guard();assert res.choose_dispatch is previous
  state=dict(frame=frame,res=res,aging=aging,claims=claims,saveclaims=saveclaims,previous=previous,cfg=copy.deepcopy(cfg),refs=original_refs,last_issue=None,last_sync=None,sync_count=0,delegated_count=0)
  def choose(pending,sample,claim_arg,history,previous_sample=None,policy=None,dispatch_index=0):
   with aging.lock:
    try:
     assert threading.get_ident()==cfg['scheduler_thread_ident'],'CLAIM_SYNC_WRONG_SCHEDULER_THREAD'
     assert cfg==state['cfg']and claim_arg is claims,'CLAIM_SYNC_CONFIG_OR_CLAIMS_ARGUMENT_DRIFT'
     guard();path=P(cfg['root'])/'control/POOL_DISPATCH_RESERVATIONS.json';disk=read(path);before_live=copy.deepcopy(claims);changed=observation_delta(disk,claims)
     if changed:
      # This is the exact existing serializer; it sees the same claims object.
      # No manual replacement dictionary or speculative model claim is written.
      saveclaims();persisted=read(path);assert persisted==dict(claims=claims)and claims==before_live,'CLAIM_SYNC_READBACK_OR_OWNER_CHANGED'
      state['sync_count']+=1
     state.update(last_issue=None,last_sync=dict(changed_observation_cohorts=changed,disk_sha256=sha(path),claim_count=len(claims),new_claims=0,new_grants=0))
    except Exception as error:
     state['last_issue']=dict(status='OWNER_CLAIM_SNAPSHOT_SYNC_HOLD',error=repr(error),claim_changes=0,models_interrupted=False);return None
    # Keep all existing error/rollback semantics in the original chooser chain.
    state['delegated_count']+=1
    return previous(pending,sample,claim_arg,history,previous_sample,policy,dispatch_index)
  state['wrapper']=choose;res.choose_dispatch=choose;setattr(main,ID,state)
  state['receipt']=dict(status='OWNER_CLAIM_OBSERVATION_SNAPSHOT_SYNC_INSTALLED',only_changed_reference='res.choose_dispatch',uses_unchanged_saveclaims=True,allowed_disk_difference='observed_model bool only',new_grants=0,models_started=0)
  return state
def restore_in_owner(owner_assert,main=None):
 assert threading.current_thread()is threading.main_thread(),'MAIN_THREAD_ONLY'
 owner_assert();main=main or sys.modules['__main__'];state=getattr(main,ID)
 with state['aging'].lock:
  assert state['res'].choose_dispatch is state['wrapper'],'REFUSE_NEWER_CHOOSER'
  state['res'].choose_dispatch=state['previous'];delattr(main,ID)
 return dict(status='EXACT_PREVIOUS_CHOOSER_RESTORED',persisted_claim_observations_retained=True,new_grants=0,models_started=0)
