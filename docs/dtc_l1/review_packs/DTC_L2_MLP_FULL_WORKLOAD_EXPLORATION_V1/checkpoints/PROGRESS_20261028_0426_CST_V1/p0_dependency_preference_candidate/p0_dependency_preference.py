"""Same frozen input/design P0 tie-in after complete generic B selection.
Import has no action. Main alone may wrap aging.original. No E pool expansion,
resource override, registry write, CPU rebinding or FrameGuard change exists.
"""
import pathlib,hashlib,threading,copy
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');ID='SAME_INPUT_DESIGN_P0_DEPENDENCY_PREFERENCE_V1'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def need(v,msg):
 if not v:raise RuntimeError(msg)
def _has_sha(value,want):
 if isinstance(value,dict):return any(_has_sha(x,want)for x in value.values())
 if isinstance(value,(list,tuple)):return any(_has_sha(x,want)for x in value)
 return value==want
class Preference:
 def __init__(self,original,engine,expected_pins,root=R):
  self.original=original;self.engine=engine;self.pins=dict(expected_pins);self.root=P(root);self.source_sha256=sha(__file__);self.origin_path=P(original.__code__.co_filename);self.origin_sha256=sha(self.origin_path);self.origin_code=original.__code__;self.wrapper=self.choose;self.installed=None;self.last_status='PREPARED_NOT_INSTALLED'
 def guard(self):
  need(sha(__file__)==self.source_sha256,'preference source drift');need(self.original.__code__ is self.origin_code and sha(self.origin_path)==self.origin_sha256,'captured original callable/source drift')
  _,_,q,plan=self.engine.registered()
  for row in plan['source_pins']:need(self.pins.get(row['path'])==row['sha256']and sha(row['path'])==row['sha256'],'frozen pipeline source pin drift')
  for path,digest in self.pins.items():need(sha(path)==digest,'qualified source pin drift')
  record=q.get('additional_operational_overlays',{}).get(ID,{});need(record.get('status')=='ACTIVE'and record.get('source_sha256')==self.source_sha256,'Main active preference source record absent')
  allowed=self.pins.get(str(self.origin_path))==self.origin_sha256 or any(v.get('status')=='ACTIVE'and _has_sha(v,self.origin_sha256)for v in q.get('additional_operational_overlays',{}).values());need(allowed,'captured generic B origin not qualified');return q
 def eligible(self,s,claims,q):
  c=s['cohort'];need(c in q['admitted_specs']and c not in q['consumed']and c not in q.get('sealed',[])and c not in claims,'P0 unavailable')
  ledger=self.root/'control/qualification_ledger';need(not(ledger/(c+'.INTENT.json')).exists()and not(ledger/(c+'.DONE.json')).exists(),'P0 spent or unresolved native identity');canonical=self.engine.canonical(c)
  for k in ['cohort','input_digest','cell','profile','program','workload','expected','configs','native_simulator_argv','limits']:need(s[k]==canonical[k],'P0 pending/canonical identity or bound mismatch')
  need(s['estimated_peak_model_RAM_bytes']>=canonical['estimated_peak_model_RAM_bytes'],'P0 canonical cost reduction');return canonical
 def choose(self,pending,sample,claims,history,previous=None,policy=None,dispatch_index=0):
  try:q=self.guard()
  except(OSError,ValueError,KeyError,RuntimeError,AssertionError):self.last_status='HOLD_SOURCE_OR_AUTHORITY_EVIDENCE';return None
  decision=self.original(pending,sample,claims,history,previous,policy,dispatch_index)
  if decision is None:self.last_status='ORIGINAL_B_HOLD_UNCHANGED';return None
  selected=[s for s in pending if s.get('cohort')==decision.get('cohort')]
  if len(selected)!=1:self.last_status='HOLD_UNKNOWN_ORIGINAL_SELECTION';return None
  current=selected[0]
  if current.get('profile')=='P0':self.last_status='ORIGINAL_ALREADY_P0';return decision
  candidates=[s for s in pending if s.get('profile')=='P0'and s.get('input_digest')==current.get('input_digest')and s.get('cell')==current.get('cell')]
  if len(candidates)!=1:self.last_status='NO_UNIQUE_SAME_INPUT_DESIGN_P0_IN_SUPPLIED_POOL';return decision
  p0=candidates[0]
  try:q=self.guard()
  except(OSError,ValueError,KeyError,RuntimeError,AssertionError):self.last_status='HOLD_SOURCE_OR_AUTHORITY_EVIDENCE';return None
  try:self.eligible(p0,claims,q)
  except(OSError,ValueError,KeyError,RuntimeError,AssertionError):self.last_status='P0_INELIGIBLE_KEEP_ORIGINAL';return decision
  try:alternate=self.original([p0],sample,claims,history,previous,policy,dispatch_index)
  except(OSError,ValueError,KeyError,RuntimeError,AssertionError):
   try:self.guard()
   except(OSError,ValueError,KeyError,RuntimeError,AssertionError):self.last_status='HOLD_SOURCE_OR_AUTHORITY_EVIDENCE';return None
   self.last_status='P0_RECHECK_FAILED_KEEP_ORIGINAL';return decision
  if alternate is None:self.last_status='P0_COMPLETE_B_HOLD_KEEP_ORIGINAL';return decision
  if alternate.get('cohort')!=p0['cohort']:self.last_status='HOLD_UNEXPECTED_P0_RECHECK_SELECTION';return None
  try:q=self.guard()
  except(OSError,ValueError,KeyError,RuntimeError,AssertionError):self.last_status='HOLD_SOURCE_OR_AUTHORITY_EVIDENCE';return None
  try:self.eligible(p0,claims,q)
  except(OSError,ValueError,KeyError,RuntimeError,AssertionError):self.last_status='P0_POSTCHECK_EVIDENCE_CHANGED_KEEP_ORIGINAL';return decision
  self.last_status='SAME_INPUT_DESIGN_P0_PASSED_COMPLETE_B'
  return dict(alternate,same_input_design_p0_preference=dict(schema=ID,source_sha256=self.source_sha256,original_chosen_cohort=decision['cohort'],selected_p0_cohort=p0['cohort'],input_digest=current['input_digest'],cell=current['cell'],only_supplied_pending_pool_used=True,complete_original_B_recheck=True,no_cost_or_safety_gate_reduction=True,E_outer_protected_R_checks_unchanged=True))
 def install(self,aging,owner_assert):
  need(threading.current_thread()is threading.main_thread(),'Main owner thread only');owner_assert()
  with aging.lock:
   self.guard();need(self.installed is None and aging.original is self.original,'captured callable changed or already installed');aging.original=self.wrapper;self.installed=aging
  return dict(status='INSTALLED_AGING_ORIGINAL_ONLY',source_sha256=self.source_sha256,captured_original_path=str(self.origin_path),captured_original_sha256=self.origin_sha256,wrapper=self.wrapper,token=self)
 def restore(self,owner_assert):
  need(threading.current_thread()is threading.main_thread(),'Main owner thread only');owner_assert();aging=self.installed;need(aging is not None,'not installed')
  with aging.lock:
   need(aging.original is self.wrapper,'another wrapper now owns aging.original; refuse overwrite');aging.original=self.original;self.installed=None
  return dict(status='RESTORED_EXACT_CAPTURED_AGING_ORIGINAL',source_sha256=self.source_sha256,other_pipeline_markers_untouched=True)
def make_wrapper(original,engine,expected_pins,root=R):return Preference(original,engine,expected_pins,root).wrapper
