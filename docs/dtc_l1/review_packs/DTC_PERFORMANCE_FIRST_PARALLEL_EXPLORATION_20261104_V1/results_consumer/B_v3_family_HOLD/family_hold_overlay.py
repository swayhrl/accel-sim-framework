"""Pure report overlay for explicit unconsumed family HOLD metadata. Never mutates authority."""
from pathlib import Path
import json,hashlib,copy
P=Path
require=lambda v,msg:None if v else(_ for _ in()).throw(ValueError(msg))
sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
js=lambda v:(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def verify_unstarted_hold(row,record,q,ctx,plan,expected_ops_sha):
 c=row['cohort'];R=P(ctx['root']);require(row.get('route_key')=='28','HOLD_NOT_REMAINING28');require(q['request']==row['request']and q['budget']==28 and q['remaining']==28-len(q['consumed']),'HOLD_REQUEST_OR_BUDGET');require(c in q['admitted_specs']and c not in q['consumed'],'HOLD_CONSUMED_OR_UNREGISTERED')
 expected={'request':row['request'],'cohort':c,'input_digest':row['input_digest'],'full_input_digest':row['input_digest'],'program':row['program'],'suite':row['suite'],'profile':row['variant'],'structure_variant':row['variant'],'cell':'DH','downstream_profile':'P0','state':'UNUSED_FAMILY_HOLD','cycles':None,'uuid':None,'consumed':False,'scientific_model_starts':0,'no_budget_refund':True,'no_model_retry':True}
 for k,v in expected.items():require(k in record and record[k]==v,'HOLD_TYPED_IDENTITY:'+k)
 require(type(record['scientific_model_starts'])is int and record['no_budget_refund']is True and record['no_model_retry']is True and record['consumed']is False,'HOLD_STRICT_TYPES');require(isinstance(record.get('UTC'),str)and bool(record['UTC']),'HOLD_UTC');require(isinstance(record.get('reason'),dict)and record['reason'].get('state')=='FAILED','HOLD_FAILURE_WITNESS');sp=R/'control/specs'/(c+'.json');require(record['canonical_spec_sha256']==q['admitted_specs'][c]==sha(sp)==sha(R/'control'/(c+'_SPEC.json')),'HOLD_REGISTERED_SPEC_SHA');s=json.loads(sp.read_bytes())
 for k,v in [('request',row['request']),('cohort',c),('input_digest',row['input_digest']),('profile',row['variant']),('structure_variant',row['variant']),('cell','DH'),('downstream_profile','P0'),('host_cpu',None)]:require(s.get(k)==v,'HOLD_SPEC_TYPED:'+k)
 ops=R/'tools/perf28_ops.py';require(record['source_ops_sha256']==expected_ops_sha==sha(ops),'HOLD_SOURCE_OPS_SHA');require(any(P(x['path'])==ops and x['sha256']==expected_ops_sha for x in plan['source_pins']),'HOLD_OPS_NOT_ACTUALLY_PINNED');require(not(R/'analysis'/(c+'.RESULT.json')).exists(),'HOLD_ALREADY_HAS_RESULT');require(not(R/'control/qualification_ledger'/(c+'.INTENT.json')).exists()and not(R/'control/qualification_ledger'/(c+'.DONE.json')).exists(),'HOLD_ALREADY_HAS_NATIVE_IDENTITY')
 return {'registry':ctx['registry'],'epoch':ctx['epoch'],'canonical_SPEC':{'path':str(sp),'sha256':sha(sp)},'admission_hold_record_sha256':hashlib.sha256(js(record)).hexdigest(),'source_ops':{'path':str(ops),'sha256':expected_ops_sha},'no_model_uuid_or_performance_created':True}

def terminal_metadata(q,validated_holds):
 value=q.get('terminal_unused_family_HOLD')
 if value is None:return {'status':'NO_PARTIAL_TERMINAL_ANNOTATION','terminal_verified':False}
 unused=set(q['admitted_specs'])-set(q['consumed']);require(q['state']=='STOP_UNACCEPTED','TERMINAL_HOLD_STATE');require(isinstance(value,dict)and set(value.get('cohorts',[]))==unused and len(value.get('cohorts',[]))==len(unused),'TERMINAL_UNUSED_COHORTS');require(unused==set(validated_holds),'TERMINAL_HOLDS_NOT_ALL_VERIFIED');require(value.get('no_budget_refund')is True and value.get('no_spec_removal')is True and value.get('no_model_retries')is True,'TERMINAL_BUDGET_SPEC_RETRY_CHANGED');require(q['remaining']==len(unused)==q['budget']-len(q['consumed']),'TERMINAL_CREDIT_ACCOUNTING');return {'status':'ALL_UNUSED_FAMILY_HOLD_METADATA_VERIFIED','terminal_verified':True,'remaining_credits_preserved':q['remaining'],'no_scientific_closed_results_fabricated':True,'source':copy.deepcopy(value)}

def overlay(snapshot,captured_contexts,expected_ops_sha,base_summarize,fixed):
 out=copy.deepcopy(snapshot);ctx=captured_contexts.get('28',{});q=ctx.get('q');checked={};issues={};malformed_container=None;terminal={'status':'AWAIT_ACTUAL_REMAINING28_GRANT','terminal_verified':False}
 if q is not None and ctx.get('source_qualified')is True:
  holds=q.get('admission_holds',{})
  if not isinstance(holds,dict):malformed_container=copy.deepcopy(holds);issues['ADMISSION_HOLD_CONTAINER']='ADMISSION_HOLDS_NOT_DICT';holds={}
  plan=json.loads(P(ctx['execution_plan']['path']).read_bytes());require(sha(ctx['execution_plan']['path'])==ctx['execution_plan']['sha256'],'PLAN_CHANGED_AFTER_CAPTURE');expected_cohorts={r['cohort']for r in out['rows']if r.get('route_key')=='28'};extra=set(holds)-expected_cohorts
  if extra:issues['OUT_OF_SCOPE_RECORDS']=sorted(extra)
  for row in out['rows']:
   c=row.get('cohort')
   if row.get('route_key')!='28'or c not in holds:continue
   try:
    witness=verify_unstarted_hold(row,holds[c],q,ctx,plan,expected_ops_sha);require(not row['accepted']and row['cycles']is None,'HOLD_CONFLICTS_CLOSED_PERFORMANCE');row.update(status='UNUSED_FAMILY_HOLD',accepted=False,cycles=None,S_DH=None,Rnew=None,I=None,actual_scientific_starts=0,uuid=None,explicit_admission_hold=copy.deepcopy(holds[c]),admission_hold_verification=witness);checked[c]=holds[c]
   except Exception as e:
    if row['accepted']:row['closed_result_before_metadata_conflict']=copy.deepcopy(row)
    row.update(status='VERIFICATION_HOLD',accepted=False,cycles=None,S_DH=None,Rnew=None,I=None,admission_hold_verification_error=repr(e),unverified_admission_hold=copy.deepcopy(holds[c]),unverified_hold_registry=ctx['registry'],unverified_hold_epoch=ctx['epoch']);issues[c]=repr(e)
  try:terminal=terminal_metadata(q,checked)
  except Exception as e:terminal={'status':'TERMINAL_HOLD_METADATA_VERIFICATION_HOLD','terminal_verified':False,'error':repr(e)};issues['TERMINAL_METADATA']=repr(e)
 summary=base_summarize(out['rows'],fixed);held=sum(r['status']=='UNUSED_FAMILY_HOLD'for r in out['rows']);summary['unstarted_family_HOLD_points']=held;summary['unclosed_scientific_points']=32-summary['accepted_new_points']-summary['archived_negative_new_points'];summary['pending_nonTag_points']=summary['unclosed_scientific_points']-held;summary['family_hold_metadata_issues']=len(issues);summary['all32_nonTag_closed_verified']=summary['unclosed_scientific_points']==0 and summary['verification_HOLD_points']==0 and not issues;summary['all32_candidates_accounted']=summary['pending_nonTag_points']==0 and summary['verification_HOLD_points']==0 and not issues;summary['all32_candidates_accounted_verified']=summary['all32_candidates_accounted']and(held==0 or terminal['terminal_verified']);summary['all32_scientific_success']=summary['accepted_new_points']==32 and not issues
 for v,values in summary['variants'].items():values['unstarted_family_HOLD_n']=sum(r['variant']==v and r['status']=='UNUSED_FAMILY_HOLD'for r in out['rows'])
 out.update(schema='DTC_PERF_STRUCTURE48_CLOSED_READONLY_SNAPSHOT_V3',summary=summary,admission_hold_overlay={'record_source':'actualq.admission_holds, never globalrequeststate or speedup','verified_unused_HOLD_cohorts':sorted(checked),'issues':issues,'unverified_admission_hold_container':malformed_container,'unmatched_admission_hold_records':{key:copy.deepcopy(q.get('admission_holds',{})[key])for key in issues.get('OUT_OF_SCOPE_RECORDS',[])}if q is not None else{},'terminal_metadata':terminal,'unstarted_HOLD_is_not_scientific_negative_or_closed_result':True,'budget_remaining_includes_held_unused_credits':True});return out
