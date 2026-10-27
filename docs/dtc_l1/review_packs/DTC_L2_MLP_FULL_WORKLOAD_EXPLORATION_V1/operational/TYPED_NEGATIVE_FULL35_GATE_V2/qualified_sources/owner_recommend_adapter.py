"""Sole-owner recommendation adapter factory. No import-time install or models.
Existing journal OBJECT is mandatory and remains the last finalization gate.
"""
import copy
from typed_analysis_view import recommend_from_bundles

def make_owner_recommend(original_recommend,existing_journal,source_paths,source_pins,
                         bindings,verifier_path,verifier_sha256):
 assert callable(original_recommend)
 final_guard=existing_journal.guard_decision
 assert final_guard.__self__ is existing_journal
 bindings=copy.deepcopy(bindings);source_paths=copy.deepcopy(source_paths);source_pins=copy.deepcopy(source_pins)
 def wrapper(raw_summary,scope,history=None):
  try:
   value=recommend_from_bundles(raw_summary,scope,history or{},source_paths,source_pins,
     bindings,verifier_path,verifier_sha256,final_guard)
   assert isinstance(value,dict)and isinstance(value.get('proposals'),list),'Malformed recommendation'
   assert type(value.get('adoption_ready'))is bool and type(value.get('scientific_stage_complete'))is bool
   wrapper.last_issue=None
   return value
  except Exception as error:
   # Read/permission races, verifier holds and source/contract assertions all
   # pause NEW scientific proposals, never kill the sole scheduler thread.
   issue=dict(status='TYPED_NEGATIVE_RECOMMENDATION_ENGINEERING_HOLD',
    error_type=type(error).__name__,error=repr(error)[:2000],healthy_models_continue=True,
    new_proposals_blocked=True,resource_provider_changed=False)
   try:
    value=copy.deepcopy(original_recommend(raw_summary,scope,history or{}))
    assert isinstance(value,dict),'Malformed original recommendation'
    issue['original_recommendation_available']=True
   except Exception as prior_error:
    value=dict(schema='DTC_L2_MLP_RECOMMENDATION_HOLD_NO_SYNTHETIC_EVIDENCE_V1')
    issue.update(original_recommendation_available=False,
     original_recommendation_error=repr(prior_error)[:2000])
   value.update(proposals=[],adoption_ready=False,scientific_stage_complete=False,
    requires_engineering_review=True,state='TYPED_NEGATIVE_ENGINEERING_HOLD_CONTINUE_HEALTHY_MODELS',
    typed_negative_recommendation_hold=issue)
   try:
    candidate=final_guard(value)
    assert isinstance(candidate,dict),'Malformed existing final guard result'
    value=candidate
   except Exception as guard_error:
    issue['existing_final_guard_error']=repr(guard_error)[:2000]
    value['registry_journal_status']=dict(safe_for_scientific_completion=False,
     requires_engineering_review=True,error=repr(guard_error)[:2000],
     status='EXISTING_FINAL_GUARD_UNAVAILABLE_FAIL_CLOSED')
   # A broken or changing gate must never restore old proposals/final flags.
   value.update(proposals=[],adoption_ready=False,scientific_stage_complete=False,
    requires_engineering_review=True)
   wrapper.last_issue=issue
   return value
 wrapper.previous_recommend=original_recommend
 wrapper.existing_journal=existing_journal
 wrapper.existing_final_guard=final_guard
 wrapper.last_issue=None
 return wrapper
