"""Small CPU-only owner exception-containment and guard-preservation cases."""
import hashlib,json,pathlib,types
from unittest.mock import patch
import owner_recommend_adapter as owner
HERE=pathlib.Path(__file__).resolve().parent
class Journal:
 def __init__(self):self.calls=0;self.error=None
 def guard_decision(self,value):
  self.calls+=1
  if self.error:raise self.error
  return dict(value,JOURNAL_FINAL_GUARD_PRESERVED=True)
checks=[];old_calls=[]
def original(*args):old_calls.append(True);return dict(proposals=[{'OLD_PROPOSAL':True}],adoption_ready=True,scientific_stage_complete=True,oldflag='retained')
j=Journal();w=owner.make_owner_recommend(original,j,{}, {},[], 'PINNED_VERIFIER_PATH','PIN')
def success(*args):return args[-1](dict(proposals=[],scientific_stage_complete=False,adoption_ready=False))
with patch.object(owner,'recommend_from_bundles',side_effect=success):
 result=w({'ACTUAL_RAW_SUMMARY':True},{})
assert result['JOURNAL_FINAL_GUARD_PRESERVED']and j.calls==1 and w.existing_journal is j and w.previous_recommend is original
checks.append('normal_chain_calls_same_existing_journal_finalguard_last')
for error in (PermissionError('CPU proc unreadable'),OSError('CPU archive IO'),AssertionError('CPU source drift'),RuntimeError('HOLD CPU verifier')):
 with patch.object(owner,'recommend_from_bundles',side_effect=error):result=w({'ACTUAL_RAW_SUMMARY':True},{})
 assert not result['proposals']and not result['scientific_stage_complete']and not result['adoption_ready']and result['requires_engineering_review']
 assert result['oldflag']=='retained'and result['JOURNAL_FINAL_GUARD_PRESERVED']and w.last_issue['error_type']==type(error).__name__
checks.append('proc_IO_source_assert_and_verifier_HOLD_never_escape_owner_or_create_proposal')
def failing_original(*args):raise AssertionError('CPU original pipeline source drift')
w2=owner.make_owner_recommend(failing_original,j,{}, {},[],'PATH','PIN')
with patch.object(owner,'recommend_from_bundles',side_effect=OSError('CPU transient')):result=w2({}, {})
assert not result['proposals']and result['requires_engineering_review']and not w2.last_issue['original_recommendation_available']
checks.append('old_pipeline_failure_returns_explicit_hold_without_fake_scientific_summary')
j.error=PermissionError('CPU journal IO')
with patch.object(owner,'recommend_from_bundles',side_effect=OSError('CPU transient')):result=w2({}, {})
assert not result['registry_journal_status']['safe_for_scientific_completion']and result['requires_engineering_review']and not result['proposals']
class MalformedJournal:
 def guard_decision(self,value):return None
with patch.object(owner,'recommend_from_bundles',return_value=None):
 malformed=owner.make_owner_recommend(failing_original,MalformedJournal(),{}, {},[],'PATH','PIN')
 result=malformed({}, {})
assert not result['proposals']and result['requires_engineering_review']and not result['registry_journal_status']['safe_for_scientific_completion']
checks.append('journal_failure_explicitly_failclosed_no_thread_exception_or_false_pass')
output=dict(status='PASS',count=len(checks),checks=checks,
 source_sha256=hashlib.sha256((HERE/'owner_recommend_adapter.py').read_bytes()).hexdigest(),
 models_started=0,signals_sent=0,production_mutations=0)
(HERE/'OWNER_RECOMMEND_CPU_QUALIFICATION.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))
