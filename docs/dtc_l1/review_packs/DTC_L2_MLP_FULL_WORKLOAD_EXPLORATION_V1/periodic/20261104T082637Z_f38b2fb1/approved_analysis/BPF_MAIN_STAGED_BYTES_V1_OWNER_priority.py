"""Finite engineering observation priority; candidate only, import has no action.

CPU2 and its old-generation strict snapshots remain unchanged.  All grants,
scope publication and installation are Main-only, outside this component.
"""
import copy,hashlib,json,pathlib,time,uuid,threading
P=pathlib.Path
ID='FINITE_BPF_ENGINEERING_RESOURCE_PRIORITY_V1'
ROLE='ENGINEERING_OBSERVATION_CANARY'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def objsha(v):return hashlib.sha256(js(v)).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def record(cfg):return dict(status='ACTIVE_PRIORITY_ONLY',source_sha256=cfg['source_sha256'],QA_sha256=cfg['QA_sha256'],readback_sha256=cfg['readback_sha256'],contract_sha256=cfg['contract_sha256'],allowed_cohorts=cfg['allowed_cohorts'],dependency_pins=cfg['dependency_pins'],priority_only=True)

def propose_scope_append(oldcfg,q,canary_scope,contract,matrix,scope,canonical,lib):
 """Pure proposal after official registration; never extends registry/grants.

 Full record extras are retained.  Main must persist preimages/transaction,
 publish new ACTIVE and same-owner context under the existing lock order.
 """
 lib.validate(oldcfg,q);canary_scope.check_primary(matrix,scope)
 assert contract['scientific_role']==ROLE
 assert contract['role_does_not_authorize_aging_fence_bypass']is True
 assert set(contract['scope_cohorts'])==set(canary_scope.rows)
 assert len(canary_scope.rows)==4
 for c in canary_scope.rows:
  spec,h=canonical(c);canary_scope.validate(c,spec,h,q)
  assert c not in q['consumed']and c not in q.get('sealed',[])
  assert contract['scope_cohorts'][c]['primary_statistics_excluded']is True
 added=sorted(set(canary_scope.rows)-set(oldcfg['allowed_cohorts']))
 new=copy.deepcopy(oldcfg);new['allowed_cohorts']+=added
 newq=copy.deepcopy(q);oldrow=copy.deepcopy(q['additional_operational_overlays'][lib.ID])
 newrow=copy.deepcopy(oldrow);newrow.update(lib.record(new))
 newq['additional_operational_overlays'][lib.ID]=newrow;lib.validate(new,newq)
 assert {k:v for k,v in new.items()if k!='allowed_cohorts'}=={k:v for k,v in oldcfg.items()if k!='allowed_cohorts'}
 return dict(schema='BPF_ENGINEERING_EXACT_CPU2_SCOPE_APPEND_PROPOSAL_V1',old_config=copy.deepcopy(oldcfg),new_config=new,old_full_record=oldrow,new_full_record=newrow,added_cohorts=added,config_only_field='allowed_cohorts',grant_changes=0,production_changes=0)

class Priority:
 def __init__(self,frame,cfg,gate,memory,canary_scope,helper):
  self.frame=frame;self.cfg=copy.deepcopy(cfg);self.gate=gate;self.memory=memory;self.scope=canary_scope;self.helper=helper
  self.engine=frame.f_locals['engine'];self.res=frame.f_locals['res'];self.aging=gate.aging;self.root=P(cfg['root'])
  self.old_e=gate.original_choose;self.old_outer=self.res.choose_dispatch
  self.FrameUnavailable=type(gate).choose.__globals__['FrameUnavailable']
  self.enabled=True;self.last_hold=None
 def active(self):
  cfg=self.cfg;assert cfg['priority_only']is True and cfg['status']=='ACTIVE_PRIORITY_ONLY'
  assert sha(__file__)==cfg['source_sha256']
  for p,h in cfg['dependency_pins'].items():assert sha(p)==h,'SOURCE_DRIFT '+p
  assert sha(cfg['contract_path'])==cfg['contract_sha256'];contract=read(cfg['contract_path'])
  assert set(contract['scope_cohorts'])==set(cfg['allowed_cohorts'])==set(self.scope.rows)and len(cfg['allowed_cohorts'])==4
  assert sha(cfg['QA_path'])==cfg['QA_sha256']and sha(cfg['readback_path'])==cfg['readback_sha256']
  qa=read(cfg['QA_path']);back=read(cfg['readback_path'])
  assert qa['status']=='PASS'and qa['source_sha256']==cfg['source_sha256']and back['verified']is True and back['QA_sha256']==cfg['QA_sha256']and back['source_sha256']==cfg['source_sha256']
  if qa.get('qualification_only'):assert cfg.get('qualification_only')is True
  self.engine.assert_parent_lease()
  q=self.engine.registered()[2];mem=self.memory['context']['cfg'];self.memory['lib'].validate(mem,q)
  assert read(cfg['memory_active_path'])==mem
  assert set(cfg['allowed_cohorts'])<=set(mem['allowed_cohorts'])
  assert self.aging.original is self.memory['new_choose']and self.res.resources is self.memory['new_resources']
  assert all(q['additional_operational_overlays'][ID].get(k)==v for k,v in record(cfg).items())
  self.scope.check_primary(read(self.root/'control/MATRIX_CURRENT.json'),read(self.root/'control/SCOPE.json'))
  return q
 def legal(self,c,q,claims):
  if c not in self.cfg['allowed_cohorts']or c not in q['admitted_specs']or c in q['consumed']or c in q.get('sealed',[])or c in claims:return False
  if c in read(self.root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']:return False
  if any((self.root/'control/qualification_ledger'/(c+s)).exists()for s in ['.INTENT.json','.DONE.json']):return False
  if c in self.frame.f_locals.get('running',{}).values():return False
  spec=self.engine.canonical(c);self.scope.validate(c,spec,q['admitted_specs'][c],q)
  return sha(self.root/'control/specs'/(c+'.json'))==q['admitted_specs'][c]
 def old(self,args):
  try:return self.old_e(*args)
  except self.FrameUnavailable:raise
  except Exception as e:raise self.FrameUnavailable(dict(status='UPSTREAM_E_ENGINEERING_EXCEPTION',error=repr(e),resource_sample_fabricated=False))from e
 def checked(self,spec,args):
  pending,sample,claims,history,previous,policy,index=args;c=spec['cohort'];q=self.active();assert self.legal(c,q,claims)
  frame=self.aging.frame_provider(*args)
  assert not frame['pressure_reasons']and c not in frame['consumed']and c not in frame['claim_cohorts']
  assert len([x for x in frame['pending']if x['cohort']==c])==1
  value=self.aging.original([spec],sample,claims,history,previous,policy,index)
  if value is None:return None
  assert value['cohort']==c and value['new_execution_no_padding']is True
  lib=self.memory['lib'];p=value['cpu_spare_owner_proof'];lib.verify_memory_proof(p)
  assert p['config']==self.memory['context']['cfg']and p['context']==dict(cohort=c,selected_cpu=value['host_cpu'],kind='OWNER_CHOOSE')
  raw=p['base_resource_snapshot'];assert 'additional_padding_admission_proof'not in raw
  assert 0<=time.monotonic()-raw['monotonic']<=read(self.root/'control/RESOURCE_POLICY.json')['admission_resource_sample_max_age_seconds']
  rows=[x for x in raw['own_ram_forecasts']if x['cohort']==c]
  assert len(rows)==1 and rows[0]['kind']=='CLAIM_OR_CANDIDATE'and rows[0]['RSS_bytes']==0 and rows[0]['additional_reserved_bytes']==spec['estimated_peak_model_RAM_bytes']
  forecast=self.res.forecast(spec,history,policy)
  assert value['forecast']==forecast and 0<forecast['predicted_peak_RAM_bytes']<=spec['estimated_peak_model_RAM_bytes']<=spec['limits']['max_process_tree_rss_bytes']
  assert value['host_cpu']in self.res.cpu_candidates(sample,claims,previous)
  assert not p['effective_decision']['pressure_reasons']and p['effective_decision']['pass_admission']
  assert raw['physical_disk_pass']and raw['own_write_ceiling_pass']
  assert raw['native_free_bytes']>raw['required_free_bytes']and raw['free_inodes']>=100000
  assert raw['total_projected_additional_RAM_bytes']==p['growth_unchanged_bytes']<=p['effective_decision']['admission_RAM_budget_bytes']
  assert self.legal(c,self.active(),claims)
  return value
 def inner(self,pending,sample,claims,history,previous=None,policy=None,dispatch_index=0):
  args=(pending,sample,claims,history,previous,policy,dispatch_index)
  original=self.old(args) # exact original normal choice always wins
  if original is not None or not self.enabled:return original
  try:
   q=self.active();state=copy.deepcopy(self.aging.state.__dict__)
   # Preserve supplied order; only exact engineering4 already in this pool.
   for spec in pending:
    c=spec['cohort']
    if not self.legal(c,q,claims):continue
    assert spec==self.engine.canonical(c)
    first=self.checked(spec,args)
    if first is None:continue
    second=self.checked(spec,args)
    if second is None:continue
    assert self.aging.state.__dict__==state,'Priority fallback mutated R/credit/tokens'
    attempt=uuid.uuid4().hex;path=P(self.cfg['token_directory'])/(attempt+'.RESERVED.json')
    token=dict(schema=ID,stage='RESERVED_BEFORE_CPU_RETURN',cohort=c,attempt=attempt,canonical_pre_refresh_sha256=q['admitted_specs'][c],source_sha256=self.cfg['source_sha256'],contract_sha256=self.cfg['contract_sha256'],memory_config_sha256=objsha(self.memory['context']['cfg']),priority_only=True,virtual_R_mutated=False,natural_release_credit_bytes=0,full_first_decision=first,full_second_decision=second)
    self.helper.atomic_exclusive(path,token);assert read(path)==token
    return dict(second,bpf_engineering_priority_reservation=dict(path=str(path),sha256=sha(path),attempt=attempt,cohort=c))
  except self.FrameUnavailable:raise
  except Exception as e:self.last_hold=dict(stage='ENGINEERING_PRIORITY_HOLD',error=repr(e));return None
  return None
 def outer(self,*args,**kwargs):
  try:value=self.old_outer(*args,**kwargs)
  except Exception as e:self.last_hold=dict(stage='UPSTREAM_OUTER_EXCEPTION',error=repr(e));return None
  if value is None or 'bpf_engineering_priority_reservation'not in value:return value
  try:
   q=self.active();link=value['bpf_engineering_priority_reservation'];token=read(link['path']);c=value['cohort'];claims=args[2]
   assert sha(link['path'])==link['sha256']and c==link['cohort']==token['cohort']and self.legal(c,q,claims)
   assert token['canonical_pre_refresh_sha256']==q['admitted_specs'][c]and token['source_sha256']==self.cfg['source_sha256']
   assert value['host_cpu']==token['full_second_decision']['host_cpu']
   proof=token['full_second_decision']['cpu_spare_owner_proof'];self.memory['lib'].verify_memory_proof(proof)
   assert 0<=time.monotonic()-proof['base_resource_snapshot']['monotonic']<=read(self.root/'control/RESOURCE_POLICY.json')['admission_resource_sample_max_age_seconds']
   assert value['host_cpu']in self.res.cpu_candidates(args[1],claims,args[4]if len(args)>4 else kwargs.get('previous'))
   path=P(self.cfg['token_directory'])/(link['attempt']+'.CPU_RETURNED.json')
   receipt=dict(schema=ID,stage='CPU_RETURNED_BEFORE_CLAIM_INTENT',reservation=link,cohort=c,host_cpu=value['host_cpu'],returned_decision_sha256=objsha(value),canonical_pre_refresh_sha256=q['admitted_specs'][c],priority_only=True,R_mutated=False,grants_added=0)
   self.helper.atomic_exclusive(path,receipt);assert read(path)==receipt
   return dict(value,bpf_engineering_priority_dispatch=dict(path=str(path),sha256=sha(path)))
  except Exception as e:self.last_hold=dict(stage='DURABLE_CPU_RETURN_HOLD',error=repr(e));return None

def install(adapter):
 """Main only after official scope/grants/source publication; exact refs saved."""
 assert threading.current_thread()is threading.main_thread()
 with adapter.aging.lock:
  adapter.active();assert adapter.gate.original_choose is adapter.old_e and adapter.res.choose_dispatch is adapter.old_outer
  adapter.gate.original_choose=adapter.inner;adapter.res.choose_dispatch=adapter.outer
 return dict(status='INSTALLED_PRIORITY_ONLY',source_sha256=sha(__file__),model_starts=0,grants_added=0)
def restore(adapter):
 assert threading.current_thread()is threading.main_thread()
 with adapter.aging.lock:
  assert adapter.gate.original_choose==adapter.inner and adapter.res.choose_dispatch==adapter.outer
  adapter.gate.original_choose=adapter.old_e;adapter.res.choose_dispatch=adapter.old_outer;adapter.enabled=False
 return dict(status='EXACT_PRIOR_REFERENCES_RESTORED',models_touched=0)
