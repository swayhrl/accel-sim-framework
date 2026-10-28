"""Pure factories for the qualified IR11 runtime-only outer view. No install."""
import copy,hashlib,importlib.util,pathlib
P=pathlib.Path
IR_SOURCE_SHA='c5e22c4d78eb092121ba0cc12f7846387dac7911762730ecda750956428cadc1'
IR_PLAN_SHA='72ce5472b5d3fc76d4f8d27c3aa3f4f7ad3d224a5ada3eaba88b3f1a2e6feff5'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def make_optional_hooks(previous_reader,previous_recommend,current_sources,target_path,source_path,plan_path,legacy_nonprimary_cohorts):
 """Return inert callables; Main alone may assign them to its private frame.

 current_sources()->(raw_primary_matrix,raw_frozen_scope,q,canonical) must read
 sources directly, never recursively through the returned reader. canonical(c)
 returns (current CPU-unbound spec, q-admitted canonical SHA), outside EX.
 """
 assert sha(source_path)==IR_SOURCE_SHA and sha(plan_path)==IR_PLAN_SHA
 s=importlib.util.spec_from_file_location('qualified_IR11_outer_view',source_path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 import json
 scoped=m.IncidentScope(json.loads(P(plan_path).read_bytes()),legacy_nonprimary_cohorts)
 def reader(path):
  value=previous_reader(path)
  if str(path)!=str(target_path):return value
  try:
   matrix,scope,q,canonical=current_sources()
   optional=scoped.optional_dispatch_view(value,matrix,scope,q,canonical)
   reader.last_status=optional['status'];reader.last_issue=optional.get('error')
   # Exact previous355 is preserved if optional IR identity/scope is not ready.
   if optional['legacy_queue_usable']:return optional['view']
   # A contaminated prior view is retained as evidence; do not invent a clean
   # scientific matrix or let optional IR validation mutate it. Main diagnoses.
   reader.last_issue='CONTAMINATED_PRIOR_VIEW_NONFINAL_HOLD '+str(optional.get('error'))
   return value
  except Exception as error:
   reader.last_status='OPTIONAL_IR_METADATA_HOLD_PREVIOUS_QUEUE_UNCHANGED';reader.last_issue=repr(error);return value
 reader.last_status='NOT_CALLED';reader.last_issue=None
 def recommend(summary,view,history=None):
  try:
   matrix,scope,q,canonical=current_sources();scoped.assert_primary_summary(summary,matrix,scope)
   if m.MARKER in view:clean=scoped.primary_view(view,matrix,scope,q,canonical)
   else:
    assert not any(p['cohort']in scoped.rows or p.get('scientific_role')==m.ROLE for p in view['points'])
    clean=view
   value=previous_recommend(summary,clean,history or{})
   for proposal in value.get('proposals',[]):
    for point in proposal.get('new_cells',[]):assert point.get('cohort')not in scoped.rows and point.get('scientific_role')!=m.ROLE
   recommend.last_issue=None;return value
  except Exception as error:
   recommend.last_issue=repr(error)
   return dict(state='IR_PRIMARY_EXCLUSION_NONFINAL_HOLD',proposals=[],scientific_stage_complete=False,adoption_ready=False,healthy_models_continue=True,error=repr(error))
 recommend.last_issue=None
 return dict(reader=reader,recommend=recommend,scoped=scoped,previous_reader=previous_reader,previous_recommend=previous_recommend,source_sha256=IR_SOURCE_SHA,plan_sha256=IR_PLAN_SHA,production_changes=0)
