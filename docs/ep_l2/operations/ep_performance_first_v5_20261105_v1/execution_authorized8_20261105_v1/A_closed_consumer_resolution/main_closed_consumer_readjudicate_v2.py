"""Main-only post-close consumer compatibility review. Default is private CPU review.
--apply performs no model start, budget reset or archive. All original postprocess checks run.
"""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,sys,types
A=Path(__file__).resolve().parent
R=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v5_20261105_v1/track_a_wv/host_private_candidate_v1/main_materialized/37e5a2db776190ee3f74')/'runtime';ROOT=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v5_20261105_v1/track_a_wv/host_private_candidate_v1/main_materialized/37e5a2db776190ee3f74')/'execution';GOAL='EP_L2_PFV5_A_FWT_G32W8_COLD_PROOF_MATCHED3_V1'
COHORTS={'EP_PERF_PFV5_A_FWT_G32W8_S_V1':'S','EP_PERF_PFV5_A_FWT_G32W8_WV_OFF_V1':'WV_ZERO_RO','EP_PERF_PFV5_A_FWT_G32W8_WV_ON_V1':'WV_ZERO_RO'}
CONSUMER_SHA='f70fac449dca71acd40a4727e1570f22263ea71a96f46ca11086e0f58cda81d5'
HOLD_REASON="InvalidEvidence('all282 actual options mismatch')"
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_bytes())
def module(n,p):sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def spec_path(c):return ROOT/'cases'/c/'control/FROZEN_SPEC.json'
def point_without(reg,c):
 v=copy.deepcopy(reg);v['registered_future_requests'][GOAL]['consumed'].pop(c);return v

def main(argv=None):
 ap=argparse.ArgumentParser();ap.add_argument('--cohort',required=True,choices=sorted(COHORTS));ap.add_argument('--amendment',default=str(A/'CONSUMER_AMENDMENT_DRAFT.json'));ap.add_argument('--apply',action='store_true');a=ap.parse_args(argv)
 doc=read(a.amendment);amref=ref(a.amendment)
 need(doc['schema']=='EP_PFV5_A_EXACT283_BUILD_METADATA_CLOSED_AMENDMENT_V2'and doc['allowed_cohorts']==sorted(COHORTS),'exact consumer amendment scope')
 need(doc['exact_Spec_refs']=={c:ref(spec_path(c))for c in sorted(COHORTS)},'amendment exact frozen Specs changed')
 need(doc['consumer_ref']==ref(A/'closed_consumer_283_banner_v2.py')and sha(A/'closed_consumer_283_banner_v2.py')==CONSUMER_SHA,'qualified consumer changed')
 need(doc['new_model_starts']==0 and doc['model_retry']is False and doc['budget_refund']is False,'consumer amendment cannot grant starts/refund')
 need(doc['readjudicator_ref']==ref(__file__),'Main reviewed postclose entry drift')
 need(doc['metadata_compatibility_approval_ref']==read(A/'MAIN_EXACT_BANNER_COMPATIBILITY_APPROVAL_REF.json'),'exact Main metadata approval changed')
 if a.apply:need(doc.get('approved_by')=='EP-MAIN'and doc.get('status')=='MAIN_APPROVED_CLOSED_CONSUMER_REVIEW_AMENDMENT_V2','Main consumer-only approval required')
 sys.path.insert(0,str(R));s=read(spec_path(a.cohort));need(s['cohort']==a.cohort and s['mode']==COHORTS[a.cohort],'exact mode/cohort')
 post=module('unchanged_original_postprocess_under_consumer_amendment',s['postprocess_module_ref']['path']);need(ref(s['postprocess_module_ref']['path'])==s['postprocess_module_ref']==doc['original_postprocess_ref'],'original postprocess pin changed')
 oldauthority=post.authority;oldtransaction=post.transaction;oldmodule=post.module;oldput=post.put;oldref=post.ref
 registry,epoch=oldauthority();row=registry['registered_future_requests'][GOAL]['consumed'][a.cohort];original_row=copy.deepcopy(row);done=post.exact(row['done_ref']);out=Path(row['output']);need(done['launcher_wait_returncode']==0 and done['stop_reason']is None and done['native_simulator_observed']is True and done['uuid']==row['uuid'],'consumer review requires exact natural exit0 observed process')
 if row['state']=='PARSE_HOLD':
  need(row['validation_hold_ref']==doc['original_validation_hold_refs'][a.cohort],'different original PARSE_HOLD')
  need(post.exact(row['validation_hold_ref'])['reason']==HOLD_REASON,'PARSE_HOLD is not the qualified dependency-pin incident')
 elif row['state']not in ['NATURAL_COMPLETE_PENDING_VALIDATION','ACCEPTED_PENDING_ARCHIVE','CLOSED_ACCEPTED']:
  raise ValueError('consumer review outside exact terminal states')
 qualified=module('qualified_CPU_consumer_supplement',A/'closed_consumer_283_banner_v2.py');events=[];review=A/'review'/a.cohort;redirect={str(out/'VALIDATED_APPLICATION_BUNDLE.json'):review/'VALIDATED_APPLICATION_BUNDLE.json',str(out/'ACCEPTED_POINT.json'):review/'ACCEPTED_POINT_PROPOSAL.json'}
 def authority_view():
  reg,ep=oldauthority();reg=copy.deepcopy(reg);r=reg['registered_future_requests'][GOAL]['consumed'][a.cohort]
  if r['state']=='PARSE_HOLD':need(r==original_row,'original held row changed during review');r['state']='NATURAL_COMPLETE_PENDING_VALIDATION'
  return reg,ep
 def annotated_validate(*args,**kwargs):
  value=qualified.validate_case(*args,**kwargs);value['consumer_amendment_ref']=amref;value['qualified_consumer_ref']=ref(A/'closed_consumer_283_banner_v2.py')
  if original_row.get('validation_hold_ref'):value['original_validation_hold_ref']=original_row['validation_hold_ref']
  value['actual_geometry']=s['geometry'];value['source_feature_profile']=s['source_feature_profile'];value['legacy_display_profile_label']=s['profile'];value['profile_label_not_hardware']=True
  return value
 def wrapped_module(item,name):
  if item==s['validation_module_ref']:
   need(ref(item['path'])==item,'original parser pin changed');return types.SimpleNamespace(validate_case=annotated_validate)
  if item==s['archive_module_ref']:
   need(ref(item['path'])==item,'original archive pin changed')
   return types.SimpleNamespace(archive_case=lambda case:dict(status='ACCEPTED_PENDING_ARCHIVE_CONSUMER_AMENDMENT_REVIEW_PASS'if a.apply else'PRIVATE_FULL_POSTPROCESS_REVIEW_PASS_NO_AUTHORITY_WRITE',cohort=case,consumer_amendment_ref=amref,next_Main_operation='original native experiment accept '+case+' --project EP_L2',archive_performed=False))
  value=oldmodule(item,name)
  if item==s['compact_module_ref']:
   original=value.exact_bundle
   def exact_bundle(bundle,destination,remaining_bytes=None):
    bundle=copy.deepcopy(bundle);bundle['consumer_amendment_ref']=amref;destination=Path(destination)if a.apply else redirect[str(Path(destination))];destination.parent.mkdir(parents=True,exist_ok=True);return original(bundle,destination,remaining_bytes)
   value.exact_bundle=exact_bundle
  return value
 def checked_put(path,value,exclusive=False):
  path=Path(path)
  if path.name=='VALIDATION_HOLD.json':
   failed=A/'review'/a.cohort/('NEW_CLOSED_CONSUMER_REVIEW_HOLD_'+str(__import__('time').time_ns())+'.json')
   failure_ref=oldput(failed,dict(original_HOLD_preserved=original_row.get('validation_hold_ref'),failure=value,science_permission=False),True)
   raise ValueError('qualified review failed; original HOLD retained; new failure '+repr(failure_ref))
  need(path==out/'ACCEPTED_POINT.json','unexpected postprocess write '+str(path));value=copy.deepcopy(value);value['consumer_amendment_ref']=amref;value['qualified_consumer_ref']=ref(A/'closed_consumer_283_banner_v2.py')
  if original_row.get('validation_hold_ref'):value['original_validation_hold_ref']=original_row['validation_hold_ref']
  value['actual_geometry']=s['geometry'];value['source_feature_profile']=s['source_feature_profile'];value['legacy_display_profile_label']=s['profile'];value['profile_label_not_hardware']=True
  if not a.apply:value['Main_review_only_not_published']=True;path=redirect[str(path)]
  return oldput(path,value,exclusive)
 def redirected_ref(path):
  p=redirect.get(str(Path(path)))if not a.apply else None
  return oldref(p if p is not None else path)
 def transaction(operation,callback):
  need(operation=='RECORD_VALIDATED_POINT_PENDING_ARCHIVE_NO_RETRY','consumer amendment forbids other authority operations')
  def allowed(reg):
   before=copy.deepcopy(reg);target=reg['registered_future_requests'][GOAL]['consumed'][a.cohort]
   need(target['state']==original_row['state']and target['done_ref']==original_row['done_ref']and target['uuid']==original_row['uuid'],'consumer terminal row changed')
   if target['state']=='PARSE_HOLD':need(a.cohort in COHORTS and target['validation_hold_ref']==doc['original_validation_hold_refs'][a.cohort],'wrong held endpoint');target['state']='NATURAL_COMPLETE_PENDING_VALIDATION'
   need(target['state']=='NATURAL_COMPLETE_PENDING_VALIDATION','only natural terminal-to-acceptance transition');callback(reg)
   target=reg['registered_future_requests'][GOAL]['consumed'][a.cohort];need(target['state']=='ACCEPTED_PENDING_ARCHIVE','wrong consumer transition endpoint')
   target['consumer_amendment_ref']=amref
   if original_row.get('validation_hold_ref'):target['old_validation_hold_ref']=original_row['validation_hold_ref'];need(target['validation_hold_ref']==original_row['validation_hold_ref'],'original HOLD ref lost')
   need(point_without(before,a.cohort)==point_without(reg,a.cohort),'other rows/budget/history changed')
   mutable={'state','accepted_point_ref','validation_ref','compact_bundle_receipt','consumer_amendment_ref','old_validation_hold_ref'}
   need({k:v for k,v in target.items()if k not in mutable}=={k:v for k,v in original_row.items()if k not in mutable},'protected consumed identity changed')
   events.append(dict(operation=operation,from_state=original_row['state'],to_state=target['state'],real_authority_write=a.apply,model_starts=0,budget_refund=False))
  if a.apply:return oldtransaction('CONSUMER_AMENDMENT_READJUDICATE_EXISTING_UUID_NO_RETRY',allowed)
  return allowed(copy.deepcopy(registry))
 post.authority=authority_view;post.transaction=transaction;post.module=wrapped_module;post.put=checked_put;post.ref=redirected_ref
 result=post.postprocess(a.cohort);result.update(mode='MAIN_APPLY'if a.apply else'CPU_ONLY_PRIVATE_REVIEW',original_postprocess_ref=s['postprocess_module_ref'],original_row_state=original_row['state'],original_validation_hold_ref=original_row.get('validation_hold_ref'),transaction_events=events,model_starts=0,refund_or_retry=False)
 print(json.dumps(result))
if __name__=='__main__':main()
