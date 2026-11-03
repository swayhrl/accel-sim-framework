"""Current broad-scope identity context for the unchanged primary selector.

Import is inert. Main swaps one context-provider closure cell and its diagnostic
metadata; E compiled advance, state, pending barrier and all sources stay fixed.
"""
import pathlib,json,hashlib,copy,threading,sys,importlib.util
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
ID='DTC_BROAD_PRIMARY_TARGET_CONTEXT_BRIDGE_V1'
AF='DTC_AGING_PRIMARY_TARGET_SELECTOR_V1'
AF_SHA='af09621e85945e489d6022f1b22b6c8702374af8ad81d5e14945977fed039b57'
SYNC='DTC_FUTURE_MEMORY_PRIMARY_SCOPE_SYNC_V1'
BROAD='DTC_STRACE_BROAD_SHARED_DISPATCH_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def objsha(v):return hashlib.sha256((json.dumps(v,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def closure_cell(fn,name):
 names=fn.__code__.co_freevars;assert names.count(name)==1,'UNEXPECTED_CONTEXT_CLOSURE '+name
 return fn.__closure__[names.index(name)]
def record(cfg):
 return dict(status='ACTIVE_CURRENT_SCOPE_PRIMARY_CONTEXT_ONLY',overlay_id=ID,request=REQ,configuration_sha256=objsha(cfg),source_sha256=cfg['source_sha256'],QA_sha256=cfg['QA_sha256'],readback_sha256=cfg['readback_sha256'],resource_configuration_sha256=cfg['resource_configuration_sha256'],observation_configuration_sha256=cfg['observation_configuration_sha256'],dependency_pins=cfg['dependency_pins'],new_grants=0)
def validate(cfg,q):
 assert cfg['schema']==cfg['overlay_id']==ID and cfg['request']==q['request']==REQ and sha(__file__)==cfg['source_sha256']
 qual=cfg.get('qualification_only')is True
 assert qual and q.get('qualification_only')is True and P(cfg['root'])!=R if qual else not q.get('qualification_only',False)and P(cfg['root'])==R
 for p,h in cfg['dependency_pins'].items():assert sha(p)==h,'BROAD_CONTEXT_DEPENDENCY_DRIFT '+p
 for key in ['QA','readback']:assert sha(cfg[key+'_path'])==cfg[key+'_sha256']
 qa=read(cfg['QA_path']);rb=read(cfg['readback_path']);assert qa['status']=='PASS'and qa['source_sha256']==rb['source_sha256']==cfg['source_sha256']and rb['verified']is True and rb['QA_sha256']==cfg['QA_sha256']
 if qa.get('qualification_only')or rb.get('qualification_only'):assert qual
 assert sha(cfg['resource_configuration_path'])==cfg['resource_configuration_sha256']and sha(cfg['observation_configuration_path'])==cfg['observation_configuration_sha256']
 rcfg=read(cfg['resource_configuration_path']);ocfg=read(cfg['observation_configuration_path'])
 assert rcfg['root']==ocfg['root']==cfg['root']and ocfg['resource_configuration_path']==cfg['resource_configuration_path']and ocfg['resource_configuration_sha256']==cfg['resource_configuration_sha256']
 lib=load('primary_context_real_dynamic_resource',rcfg['library_path']);assert sha(lib.__file__)==rcfg['qualified_sources']['library'];lib.validate(rcfg,q)
 producer=load('primary_context_real_observer',ocfg['source_paths']['producer']);assert sha(producer.__file__)==ocfg['qualified_sources']['producer'];producer.validate(ocfg,q)
 assert all(q['additional_operational_overlays'][ID].get(k)==v for k,v in record(cfg).items()),'CONTEXT_OPERATIONAL_RECORD_MISMATCH'
 return rcfg,ocfg,lib
def broad_live_context(root,engine,cfg,preserved_nonprimary,frame):
 """Fresh actual broad authority and raw primary files, no old Sync call."""
 root=P(root);q=engine.registered()[2];active,ocfg,lib=validate(cfg,q)
 matrix=read(root/'control/MATRIX_CURRENT.json');scope=read(root/'control/SCOPE.json')
 assert matrix['request']==REQ and matrix['base_scope_sha256']==sha(root/'control/SCOPE.json')
 points={p['cohort']:p for p in matrix['points']};assert len(points)==len(matrix['points'])
 for p in scope['points']:assert points[p['cohort']]==p,'FROZEN_PRIMARY_SCOPE_CHANGED'
 ir={x['cohort']for x in q.get('authorized_incident_recovery_trials',[])}
 engineering=set(read(ocfg['exclusion_contract_path'])['scope_cohorts']);exclude=set(preserved_nonprimary)|ir|engineering
 assert not set(points)&exclude,'NONPRIMARY_IN_RAW_PRIMARY_MATRIX'
 assert all(p.get('scientific_role')is None for p in matrix['points'])
 contract=read(active['scope_contract_path']);assert sha(active['scope_contract_path'])==active['scope_contract_sha256']
 allowed=set(active['allowed_cohorts']);specs={};hashes={};intents=set()
 for row in frame['pending']:
  c=row['cohort']
  if c not in q['admitted_specs']or c not in points or c not in allowed or c in exclude:continue
  path=root/'control/specs'/(c+'.json');alias=root/'control'/(c+'_SPEC.json');raw=path.read_bytes();s=json.loads(raw);h=hashlib.sha256(raw).hexdigest()
  assert h==sha(alias)==q['admitted_specs'][c]and s['cohort']==c and s['host_cpu']is None,'CURRENT_PRIMARY_CANONICAL_OR_ALIAS_DRIFT'
  lib.verify_science_scope(s,c,contract)
  specs[c]=s;hashes[c]=h
  if(root/'control/qualification_ledger'/(c+'.INTENT.json')).exists():intents.add(c)
 return dict(registry=q,active_memory=active,matrix_points=points,specs=specs,spec_sha256=hashes,preserved_nonprimary=exclude,initial_references=set(scope['initial_references']),INTENT_exists=intents)
def install_on_existing(aging,cfg,engine,owner_assert,main=None):
 assert threading.current_thread()is threading.main_thread();owner_assert();main=main or sys.modules['__main__'];assert not hasattr(main,ID)
 with aging.lock:
  q=engine.registered()[2];validate(cfg,q);af=getattr(main,AF);broad=getattr(main,BROAD);sync=getattr(main,SYNC)
  assert af['aging']is aging and af['state']is aging.state and broad['aging']is aging and aging.original is broad['leaf']
  wrapper=af['wrapper'];assert sha(wrapper.__code__.co_filename)==AF_SHA
  compiled=closure_cell(wrapper,'compiled').cell_contents
  assert compiled.__code__.co_filename.startswith(str(P(wrapper.__code__.co_filename).resolve())+'::')
  qualified=compiled.__globals__['_qualified_primary_choices'];assert sha(qualified.__code__.co_filename)==AF_SHA
  cell=closure_cell(qualified,'context_provider');old=cell.cell_contents;assert old is af['context_provider']
  preserved=tuple(sync.cfg['preserved_nonprimary_cohorts']);frozen=copy.deepcopy(cfg)
  def provider(frame):
   assert cfg==frozen,'BROAD_CONTEXT_CONFIG_OBJECT_DRIFT'
   current=engine.registered()[2];active,_,_=validate(cfg,current)
   if any(row['cohort']not in active['allowed_cohorts']for row in frame['pending']):return old(frame)
   return broad_live_context(cfg['root'],engine,cfg,preserved,frame)
  before=copy.deepcopy(aging.state.__dict__);calls=aging.calls;refs=(aging.original,aging.frame_provider,aging.wrapper,aging.lock,aging.state.advance)
  state=dict(aging=aging,af=af,compiled=compiled,qualified=qualified,cell=cell,previous=old,wrapper=provider,cfg=frozen,refs=refs,owner_assert=owner_assert)
  cell.cell_contents=provider;af['context_provider']=provider
  assert aging.state.__dict__==before and aging.calls==calls and refs==(aging.original,aging.frame_provider,aging.wrapper,aging.lock,aging.state.advance)
  setattr(main,ID,state);state['receipt']=dict(status='BROAD_PRIMARY_IDENTITY_CONTEXT_CELL_INSTALLED',compiled_advance_unchanged=True,aging_state_unchanged=True,pending_barrier_and_R_tokens_unchanged=True,source_af096_unchanged=True,new_grants=0,models_started=0);return state
def install_on_frame(frame,cfg,owner_assert,main=None):
 main=main or sys.modules['__main__'];aging=frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED;engine=frame.f_locals['engine']
 assert getattr(main,AF)['aging']is aging
 return install_on_existing(aging,cfg,engine,owner_assert,main)
def restore_in_owner(owner_assert,main=None):
 assert threading.current_thread()is threading.main_thread();owner_assert();main=main or sys.modules['__main__'];state=getattr(main,ID);aging=state['aging']
 with aging.lock:
  assert state['cell'].cell_contents is state['wrapper']and state['af']['context_provider']is state['wrapper']
  assert state['refs']==(aging.original,aging.frame_provider,aging.wrapper,aging.lock,aging.state.advance)
  before=copy.deepcopy(aging.state.__dict__);calls=aging.calls;state['cell'].cell_contents=state['previous'];state['af']['context_provider']=state['previous']
  assert aging.state.__dict__==before and aging.calls==calls;delattr(main,ID)
 return dict(status='EXACT_PREVIOUS_CONTEXT_PROVIDER_RESTORED',ledger_state_unchanged=True,new_grants=0,models_started=0)
