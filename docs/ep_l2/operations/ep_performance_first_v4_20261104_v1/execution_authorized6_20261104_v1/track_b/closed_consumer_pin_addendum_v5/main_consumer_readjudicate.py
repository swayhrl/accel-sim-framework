"""Main-only post-close consumer compatibility review. Default is private CPU review.
--apply performs no model start, budget reset or archive. All original postprocess checks run.
"""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,sys,types
A=Path(__file__).resolve().parent;O=A.parent;R=O/'private_runtime';ROOT=O/'private_execution/vector1700';GOAL='EP_L2_VECTOR1700_WV_DECOMPOSITION_FRESH_V4_20261104'
COHORTS={'EP_PERF_PFV4_VECTOR4M_W_ONLY_1700_V1':'W_ONLY','EP_PERF_PFV4_VECTOR4M_WV_ZERO_RO_1700_V1':'WV_ZERO_RO'}
CONSUMER_SHA='16cdb359844e1116e258dec031e3c4ed9237a2df681f95399018830436e47a5b'
HOLD_REASON="ValueError('pure package dependency drift:mode_contract.py')"
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
 need(doc['schema']=='EP_PFV4_B_CONSUMER_ONLY_MC_PIN_AMENDMENT_V1'and doc['allowed_cohorts']==sorted(COHORTS),'exact consumer amendment scope')
 need(doc['exact_Spec_refs']=={c:ref(spec_path(c))for c in sorted(COHORTS)},'amendment exact frozen Specs changed')
 need(doc['consumer_ref']==ref(A/'qualified_consumer.py')and sha(A/'qualified_consumer.py')==CONSUMER_SHA,'qualified consumer changed')
 need(doc['new_model_starts']==0 and doc['model_retry']is False and doc['budget_refund']is False,'consumer amendment cannot grant starts/refund')
 if a.apply:need(doc.get('approved_by')=='EP-MAIN'and doc.get('status')=='MAIN_APPROVED_CONSUMER_ONLY_COMPATIBILITY_AMENDMENT','Main consumer-only approval required')
 sys.path.insert(0,str(R));s=read(spec_path(a.cohort));need(s['cohort']==a.cohort and s['mode']==COHORTS[a.cohort],'exact mode/cohort')
 post=module('unchanged_original_postprocess_under_consumer_amendment',s['postprocess_module_ref']['path']);need(ref(s['postprocess_module_ref']['path'])==s['postprocess_module_ref']==doc['original_postprocess_ref'],'original postprocess pin changed')
 oldauthority=post.authority;oldtransaction=post.transaction;oldmodule=post.module;oldput=post.put;oldref=post.ref
 registry,epoch=oldauthority();row=registry['registered_future_requests'][GOAL]['consumed'][a.cohort];original_row=copy.deepcopy(row);done=post.exact(row['done_ref']);out=Path(row['output']);need(done['launcher_wait_returncode']==0 and done['stop_reason']is None and done['native_simulator_observed']is True and done['uuid']==row['uuid'],'consumer review requires exact natural exit0 observed process')
 if row['state']=='PARSE_HOLD':
  need(a.cohort.endswith('_W_ONLY_1700_V1'),'only original W PARSE_HOLD readjudication authorized')
  need(row['validation_hold_ref']==doc['original_W_validation_hold_ref'],'different original PARSE_HOLD')
  need(post.exact(row['validation_hold_ref'])['reason']==HOLD_REASON,'PARSE_HOLD is not the qualified dependency-pin incident')
 elif row['state']not in ['NATURAL_COMPLETE_PENDING_VALIDATION','ACCEPTED_PENDING_ARCHIVE','CLOSED_ACCEPTED']:
  raise ValueError('consumer review outside exact terminal states')
 qualified=module('qualified_CPU_consumer_supplement',A/'qualified_consumer.py');events=[];review=A/'review'/a.cohort;redirect={str(out/'VALIDATED_APPLICATION_BUNDLE.json'):review/'VALIDATED_APPLICATION_BUNDLE.json',str(out/'ACCEPTED_POINT.json'):review/'ACCEPTED_POINT_PROPOSAL.json'}
 def authority_view():
  reg,ep=oldauthority();reg=copy.deepcopy(reg);r=reg['registered_future_requests'][GOAL]['consumed'][a.cohort]
  if r['state']=='PARSE_HOLD':need(r==original_row,'original held row changed during review');r['state']='NATURAL_COMPLETE_PENDING_VALIDATION'
  return reg,ep
 def annotated_validate(*args,**kwargs):
  value=qualified.validate_case(*args,**kwargs);value['consumer_amendment_ref']=amref;value['qualified_consumer_ref']=ref(A/'qualified_consumer.py')
  if original_row.get('validation_hold_ref'):value['original_validation_hold_ref']=original_row['validation_hold_ref']
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
  if path.name=='VALIDATION_HOLD.json':raise ValueError('qualified review failed; preserve original HOLD, no registry transition: '+repr(value))
  need(path==out/'ACCEPTED_POINT.json','unexpected postprocess write '+str(path));value=copy.deepcopy(value);value['consumer_amendment_ref']=amref;value['qualified_consumer_ref']=ref(A/'qualified_consumer.py')
  if original_row.get('validation_hold_ref'):value['original_validation_hold_ref']=original_row['validation_hold_ref']
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
   if target['state']=='PARSE_HOLD':need(a.cohort.endswith('_W_ONLY_1700_V1')and target['validation_hold_ref']==doc['original_W_validation_hold_ref'],'wrong held endpoint');target['state']='NATURAL_COMPLETE_PENDING_VALIDATION'
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
