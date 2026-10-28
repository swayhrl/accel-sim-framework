"""Main-only private-instance composition. Import does not install anything."""
import copy,hashlib,json,pathlib,threading
from interaction_policy import augment,validate_new_phases,digest,SCHEMA,PHASES
P=pathlib.Path
TARGET_OPTIONS={'-gpgpu_cache:dl2','-gpgpu_frfcfs_dram_sched_queue_size'}
ROLE='SUPPLEMENTAL_NEW_PERFORMANCE_TRIAL'
def sha(path):return hashlib.sha256(P(path).read_bytes()).hexdigest()
def science(spec):
 return {k:copy.deepcopy(spec[k])for k in ('input_digest','input_binding_path','input_binding_sha256','cell','core_commit',
  'framework_commit','binary_sha256','expected','expected_options','configs','workload')}

def build_contract(root,source_pins):
 """Read only; Main separately publishes the returned immutable contract."""
 root=P(root);scope=json.loads((root/'control/SCOPE.json').read_bytes());points=scope['points']
 bases=[]
 for p in points:
  if p['profile']!='P0':continue
  path=root/'control/specs'/(p['cohort']+'.json');spec=json.loads(path.read_bytes())
  assert spec['core_commit']=='9eedb3131937748f0492fa83aad37d3691118d70'
  assert spec['framework_commit']=='02775fd795cde5aae1480d81cee6eb481d0a08f4'
  assert spec['binary_sha256']=='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d'
  assert spec['expected_options']['-gpgpu_cache:dl2']==['S:128:128:16,L:B:m:L:L,A:192:4,32:0,32']
  assert spec['expected_options']['-gpgpu_frfcfs_dram_sched_queue_size']==['64']
  assert spec['expected_options']['-gpgpu_clock_domains']==['1410.0:1410.0:1410.0:850.0']
  assert sha(spec['input_binding_path'])==spec['input_binding_sha256']
  for config in spec['configs']:assert sha(config['path'])==config['sha256']
  bases.append(dict(cohort=p['cohort'],spec_path=str(path),scientific_binding_sha256=digest(science(spec))))
 assert len(bases)==70
 return dict(schema='DTC_L2_MLP_INTERACTION_SCIENTIFIC_CONTRACT_V3',scope_path=str(root/'control/SCOPE.json'),
  scope_sha256=sha(root/'control/SCOPE.json'),input_ids=sorted({p['input_digest']for p in points}),
  P0_bindings=bases,source_pins=copy.deepcopy(source_pins),target_options=sorted(TARGET_OPTIONS),
  no_supplemental_union=True,initial350_unchanged=True,model_starts=0)

def check_contract(contract):
 assert contract['schema']=='DTC_L2_MLP_INTERACTION_SCIENTIFIC_CONTRACT_V3'
 assert contract['no_supplemental_union']is True and contract['initial350_unchanged']is True
 assert sha(contract['scope_path'])==contract['scope_sha256']
 assert len(contract['P0_bindings'])==70 and len(contract['input_ids'])==35
 assert contract['target_options']==sorted(TARGET_OPTIONS)
 for pin in contract['source_pins']:assert sha(pin['path'])==pin['sha256'],'Source pin changed'
 for base in contract['P0_bindings']:
  spec=json.loads(P(base['spec_path']).read_bytes())
  assert digest(science(spec))==base['scientific_binding_sha256'],'P0 scientific contract changed'
  assert sha(spec['input_binding_path'])==spec['input_binding_sha256']
  for config in spec['configs']:assert sha(config['path'])==config['sha256']

def make_projector(existing_view_module,config):
 """Capture the already installed typed view, bound to final transport9a config."""
 config=copy.deepcopy(config);project=existing_view_module.project
 assert config['verifier']['sha256']=='9a023005a1847108dfb7e05ef0bacddbadcb7558766c5847bb08d2e2f678e673'
 assert str(P(project.__code__.co_filename).resolve())==str(P(existing_view_module.__file__).resolve())
 view_sha=sha(existing_view_module.__file__)
 def wrapper(raw):
  assert sha(existing_view_module.__file__)==view_sha
  return project(raw,config['bindings'],config['verifier']['path'],config['verifier']['sha256'])
 wrapper.source_pins=[dict(path=str(existing_view_module.__file__),sha256=view_sha),copy.deepcopy(config['verifier'])]
 return wrapper

def make_extend_guard(existing_journal,host_qualifier,contract,contract_checker=check_contract):
 """Private gate before SAME journal.extend; no new budget or forecast policy.

 Main supplies an independently qualified resource callback. This module cannot
 invent peak RSS, relax a hardcap, or assume the initial eight-profile padding.
 Old non-V3 extension proposals pass unchanged to the existing journal.
 """
 original=existing_journal.extend;assert original.__self__ is existing_journal
 assert callable(host_qualifier)
 def wrapper(proposal):
  attempted=False
  try:
   contract_checker(contract)
   if proposal.get('supplementary_policy')==SCHEMA:
    assert proposal.get('phase')in PHASES
    proof=host_qualifier(copy.deepcopy(proposal))
    assert proof['status']=='PASS_SEPARATE_COMBINATION_RESOURCE_QUALIFICATION'
    assert proof['proposal_id']==proposal['proposal_id']and proof['parameters']==proposal['parameters']
    assert proof['initial_profile_padding_discount_applied']is False
    assert proof['invented_fixed_margin_used']is False and proof['existing_dynamic_admission_retained']is True
    assert proof['new_qualifier_reduces_forecast_or_limits']is False
    assert proof['ratified_original_refresh_may_adjust_resource_caps']is True
    assert isinstance(proof['source_pins'],list)and proof['source_pins']
    for pin in proof['source_pins']:assert sha(pin['path'])==pin['sha256']
    rows=proof['cell_forecasts'];assert len(rows)==35
    assert sorted((r['input_digest'],r['cell'])for r in rows)==sorted((r['input_digest'],r['cell'])for r in proposal['new_cells'])
    for row in rows:
     assert type(row['full_reserved_peak_bytes'])is int and row['full_reserved_peak_bytes']>0
     assert row['candidate_full_forecast_retained']is True and row['new_qualifier_reduces_forecast_or_limits']is False
   attempted=True;result=original(proposal);wrapper.last_issue=None;return result
  except Exception as error:
   wrapper.last_issue=dict(status='INTERACTION_EXTENSION_RESOURCE_OR_CONTRACT_HOLD',error=repr(error)[:2000],
    authority_call_attempted=attempted,new_grants='UNKNOWN_PRESERVE_EXISTING_JOURNAL_RECONCILIATION'if attempted else 0,healthy_models_continue=True)
   return [] # no grant/consume; current healthy models and prior history remain
 wrapper.previous_extend=original;wrapper.existing_journal=existing_journal;wrapper.last_issue=None
 return wrapper

def make_owner_recommend(previous_recommend,existing_journal,primary_provider,project_typed,contract,contract_checker=check_contract):
 """Outer recommend only, preserving current R2→transport9a→f21/a7 and journal.

 project_typed(raw) must be the immutable existing typed_analysis_view.project
 bound to the already approved transport9a config; returns(view, proofdict).
 primary_provider is the existing supplemental registry.primary callable.
 Main installs on that same adaptive module INSTANCE, under its own owner gate.
 """
 assert callable(previous_recommend)and callable(primary_provider)and callable(project_typed)
 assert existing_journal.guard_decision.__self__ is existing_journal
 contract=copy.deepcopy(contract)
 def wrapper(raw,scope,history=None):
  old=None
  try:
   contract_checker(contract)
   primary=primary_provider();stripped=copy.deepcopy(scope)
   extras=[p for p in stripped['points']if p.get('scientific_role')==ROLE]
   stripped['points']=[p for p in stripped['points']if p.get('scientific_role')!=ROLE]
   stripped.pop('supplemental_dispatch_view',None)
   assert stripped==primary and all(p['cohort'].endswith('-DH-M16-V2')for p in extras),'Primary/supplemental identity changed'
   assert sorted({p['input_digest']for p in primary['points']})==contract['input_ids']
   old=previous_recommend(raw,scope,history or{}) # exact prior chain sees its original dispatch view
   assert isinstance(old,dict)and isinstance(old.get('proposals'),list)
   # Never resurrect proposals after a failed prior verifier/final guard.
   if old.get('typed_negative_recommendation_hold')or old.get('state')in ('SUPPLEMENTAL_VIEW_ENGINEERING_HOLD','TYPED_NEGATIVE_ENGINEERING_HOLD_CONTINUE_HEALTHY_MODELS'):
    wrapper.last_issue=dict(status='PRIOR_CHAIN_HOLD_PRESERVED');return existing_journal.guard_decision(old)
   status=old.get('registry_journal_status',{})
   if status.get('safe_for_scientific_completion')is False:
    value=copy.deepcopy(old);value.update(proposals=[],scientific_stage_complete=False,adoption_ready=False)
    wrapper.last_issue=dict(status='REGISTRY_HOLD_PRESERVED');return existing_journal.guard_decision(value)
   view,proofs=project_typed(raw)
   assert {v['cohort']:v for v in old.get('verified_typed_engineering_negatives',[])}==proofs,'Verifier generation/proofs changed'
   value=augment(old,view,primary,history or{})
   value=validate_new_phases(value,view,primary,history or{},proofs)
   value=existing_journal.guard_decision(value) # same live object, last final gate
   assert isinstance(value,dict)
   wrapper.last_issue=None;return value
  except Exception as err:
   issue=dict(status='INTERACTION_V3_ENGINEERING_HOLD_CONTINUE_HEALTHY_MODELS',error_type=type(err).__name__,error=repr(err)[:2000],resource_provider_changed=False)
   value=copy.deepcopy(old)if isinstance(old,dict)else{}
   value.update(proposals=[],scientific_stage_complete=False,adoption_ready=False,requires_engineering_review=True,interaction_v3_hold=issue)
   try:value=existing_journal.guard_decision(value)
   except Exception as final_error:value['registry_journal_status']=dict(safe_for_scientific_completion=False,error=repr(final_error)[:2000])
   value.update(proposals=[],scientific_stage_complete=False,adoption_ready=False,requires_engineering_review=True)
   wrapper.last_issue=issue;return value
 wrapper.previous_recommend=previous_recommend;wrapper.existing_journal=existing_journal;wrapper.last_issue=None
 wrapper.contract=contract;return wrapper

class Installation:
 """Explicit Main-only instance installation; no threads, dispatch or authority."""
 def __init__(self,adaptive,wrapper,existing_journal,owner_check,lock,registry=None,extend_guard=None,recommend_only_cpu_fixture=False):
  assert callable(owner_check)and hasattr(lock,'__enter__')
  self.adaptive=adaptive;self.wrapper=wrapper;self.journal=existing_journal;self.owner_check=owner_check;self.lock=lock
  self.original=adaptive.recommend;assert wrapper.previous_recommend is self.original
  assert wrapper.existing_journal is existing_journal;self.installed=False
  self.registry=registry;self.extend_guard=extend_guard
  assert registry is not None or recommend_only_cpu_fixture is True,'Production composition requires the separate-resource extension gate'
  if registry is not None:
   assert extend_guard is not None and extend_guard.existing_journal is existing_journal
   self.original_extend=registry.extend
   assert self.original_extend==extend_guard.previous_extend,'Expected the installed same journal.extend'
 def install(self):
  self.owner_check()
  with self.lock:
   assert not self.installed and self.adaptive.recommend is self.original
   assert not hasattr(self.adaptive,'DTC_L2_MLP_INTERACTION_V3')
   if self.registry is not None:
    assert self.registry.extend==self.original_extend;self.registry.extend=self.extend_guard
   self.adaptive.recommend=self.wrapper;self.adaptive.DTC_L2_MLP_INTERACTION_V3=self;self.installed=True
  return dict(status='PRIVATE_INSTANCE_ONLY',same_journal_object=id(self.journal),no_registration=True)
 def restore(self):
  self.owner_check()
  with self.lock:
   assert self.installed and self.adaptive.recommend is self.wrapper
   assert self.adaptive.DTC_L2_MLP_INTERACTION_V3 is self
   if self.registry is not None:
    assert self.registry.extend is self.extend_guard;self.registry.extend=self.original_extend
   self.adaptive.recommend=self.original;del self.adaptive.DTC_L2_MLP_INTERACTION_V3;self.installed=False
