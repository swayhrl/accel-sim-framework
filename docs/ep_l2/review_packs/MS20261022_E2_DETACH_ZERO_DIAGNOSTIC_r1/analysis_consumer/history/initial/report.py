#!/usr/bin/env python3
"""Consume E-accepted semantic counters; never parse native data or grant acceptance."""
import argparse
import copy
import json
from pathlib import Path
import re

SCHEMA = 'E2_DETACH_SEMANTIC_ANALYSIS_INPUT_V1'
IDENTITY = ('run_id','workload','profile','cohort','core_commit','framework_commit','binary_sha256','config_sha256',
            'input_sha256','oracle_manifest_sha256','oracle_ranges_sha256','qualification_id')
# These are analysis semantics, not asserted A2 native field names.
SEMANTICS = {
 'accepted_global_reads': ('REQUEST_ACCEPTANCE','request','acceptance'),
 'accepted_oracle_candidates': ('REQUEST_ACCEPTANCE','request','acceptance'),
 'accepted_ro': ('REQUEST_ACCEPTANCE','request','acceptance'),
 'raw_probe_reservation_fail': ('FRONTEND_HEAD_CYCLE','head_cycle','exposure'),
 'pressure_no_live_ro_tag': ('PRESSURE_HEAD_CYCLE','head_cycle','exposure'),
 'pressure_live_ro_but_none_eligible': ('PRESSURE_HEAD_CYCLE','head_cycle','exposure'),
 'pressure_with_eligible_victim': ('PRESSURE_HEAD_CYCLE','head_cycle','exposure'),
 'relief_preview_not_consulted': ('PRESSURE_HEAD_CYCLE','head_cycle','exposure'),
 'sticky_reuse_first_reason': ('PRESSURE_WAY_SCAN','way_exposure','exclusive_first_reason'),
 'no_required_not_ready_sector_first_reason': ('PRESSURE_WAY_SCAN','way_exposure','exclusive_first_reason'),
 'sticky_reuse_predicate': ('PRESSURE_WAY_SCAN','way_exposure','nonexclusive_predicate'),
 'no_required_not_ready_sector_predicate': ('PRESSURE_WAY_SCAN','way_exposure','nonexclusive_predicate'),
 'relieve_calls': ('COMMIT_ACCESS','invocation','invocation'),
 'relieve_no_eligible': ('COMMIT_ACCESS','invocation','invocation'),
 'detach_success': ('TRANSACTION_LIFECYCLE','transaction','transition'),
 'detached_victim_retired': ('TRANSACTION_LIFECYCLE','transaction','transition'),
 'live_detached_terminal': ('TRANSACTION_LIFECYCLE','transaction','state'),
 'detached_victim_response_count': ('VICTIM_RESPONSE','response','response'),
 'trigger_first_call_accepted_after_detach': ('TRIGGER_CALL','invocation','invocation'),
 'trigger_first_call_refused_after_detach': ('TRIGGER_CALL','invocation','invocation'),
 'trigger_later_accepted_after_prior_detach': ('TRIGGER_LATER_ACCEPTANCE','request','acceptance'),
}
LIMITS = [
 'This report consumes E acceptance; it does not independently accept a run or decode native records.',
 'Head-cycle and way-exposure counts are repeated observations, never unique requests or summed program stall.',
 'Nonexclusive predicates may overlap. Exclusive first-reason bins depend on declared precedence.',
 'Sticky reuse remains set after a merged waiter retires; it differs from having no missing required sectors.',
 'A selected or detached victim and its response/retirement differ from the triggering request and later retry outcome.',
 'No cross-binary speedup, old-S/new-F performance, T-isolated gain, hardware upper bound, or zero-fill.',
 'One new SGEMM diagnostic cannot recover missing historical pressure/eligibility counts for other positive-RO workloads.',
 'Old SGEMM empty certificate and old FWT whole-epoch store exclusion remain separate known upstream explanations; new counters never backfill them.',
]


def template():
 return {'schema':SCHEMA,'data_kind':'TEMPLATE_NOT_OBSERVED',
 'acceptance':{'status':None,'owner':'E2','receipt_ref':None,'adapter_ref':None,
               'producer_schema_ref':None,'semantic_mapping_reviewed_by_E':False},
 'identity':{key:None for key in IDENTITY},'coverage':{},'metrics':{},
 'explanation':'Populate only from E independently accepted decoded and semantically mapped counters. No real application data is present.'}


def analyze(doc):
 report={'schema':'E2_DETACH_MECHANISM_ANALYSIS_REPORT_V1','status':'INCOMPLETE',
 'data_kind':doc.get('data_kind'),'scientific_application_conclusions':[],
 'synthetic_observations':[],'measured_facts':{},'unknowns':[], 'errors':[],
 'claim_limits':LIMITS.copy(),'run_id':doc.get('identity',{}).get('run_id'),
 'input_identity':copy.deepcopy(doc.get('identity',{})),
 'unconsumed_semantic_fields':sorted(set(doc.get('metrics',{}))-set(SEMANTICS)),
 'historical_scope':{'old_SGEMM':'Upstream empty-fallback no RO candidate/transaction under E048 exact condition; not Tag abundance.',
 'old_FWT':'Whole-commandlist128B certification excludes every read-containing line due to a store in the same epoch; not Tag abundance.',
 'other_old_positive_RO':'Unmeasured dynamic causes remain UNKNOWN; new SGEMM cannot establish their historical counts.'}}
 if doc.get('schema')!=SCHEMA:
  report['errors'].append('unrecognized semantic input schema');report['status']='INVALID';return report
 synthetic=doc.get('data_kind')=='SYNTHETIC'
 if not synthetic and doc.get('data_kind')!='REAL_ACCEPTED':
  report['unknowns'].append('No real accepted application data supplied.');return report
 a=doc.get('acceptance',{})
 if not synthetic and (a.get('status')!='CURRENT_ACCEPTED' or a.get('owner')!='E2' or
  a.get('semantic_mapping_reviewed_by_E') is not True or not all(a.get(k) for k in ('receipt_ref','adapter_ref','producer_schema_ref'))):
  report['unknowns'].append('Missing exact E accepted record/adapter/schema mapping.');return report
 ident=doc.get('identity',{})
 if not all(isinstance(ident.get(k),str) and ident[k] for k in IDENTITY):
  report['unknowns'].append('Exact source/binary/config/input/oracle/Q identity missing.');return report
 for key in ('core_commit','framework_commit'):
  if not re.fullmatch('[0-9a-f]{40}',ident[key]):report['errors'].append('invalid identity '+key)
 for key in ('binary_sha256','config_sha256','input_sha256','oracle_manifest_sha256','oracle_ranges_sha256'):
  if not re.fullmatch('[0-9a-f]{64}',ident[key]):report['errors'].append('invalid identity '+key)
 usable={};contexts={};metric_map=doc.get('metrics',{})
 for name,expected in SEMANTICS.items():
  m=metric_map.get(name)
  if m is None:
   report['unknowns'].append(name+': UNKNOWN_NOT_EMITTED');continue
  if m.get('status')!='MEASURED':
   if m.get('value') is not None:report['errors'].append(name+': unmeasured/NA has numerical value')
   report['unknowns'].append(name+': '+str(m.get('status','UNKNOWN_NOT_EMITTED'))+' '+str(m.get('reason','')));continue
  value=m.get('value')
  if type(value) is not int or value<0:
   report['errors'].append(name+': counter must be nonnegative integer, bool forbidden');continue
  if (m.get('domain'),m.get('unit'),m.get('measurement_kind'))!=expected:
   report['errors'].append(name+': semantic domain/unit/measurement kind mismatch');continue
  c=doc.get('coverage',{}).get(m.get('coverage_id'),{})
  if c.get('overflow') is True:
   report['errors'].append(name+': INVALID_OVERFLOW');continue
  if not (c.get('complete') is True and c.get('overflow') is False and c.get('run_id')==ident['run_id'] and
   c.get('domain')==expected[0] and c.get('scope_id')==m.get('scope_id') and isinstance(c.get('interval'),list) and
   len(c['interval'])==2 and all(type(i) is int for i in c['interval']) and c['interval'][0]<c['interval'][1] and
   c.get('level')=='GLOBAL' and c.get('accepted_slice_ids')==list(range(64)) and m.get('mapping_evidence_ref')):
   report['unknowns'].append(name+': incomplete/mismatched interval,64slice,scope or mapping coverage');continue
  usable[name]=value;contexts[name]=(c['run_id'],c['scope_id'],tuple(c['interval']))
  report['measured_facts'][name]={'value':value,'domain':expected[0],'unit':expected[1],
   'measurement_kind':expected[2],'scope_id':m['scope_id'],'interval':c['interval'],
   'scope_warning':'Nonexclusive; do not sum or derive exclusive percentages.' if expected[2]=='nonexclusive_predicate' else None}
 def joint(*keys):
  return all(k in usable for k in keys) and len({contexts[k] for k in keys})==1
 claims=[]
 if joint('accepted_global_reads','accepted_ro') and usable['accepted_ro']==0:
  claims.append({'code':'NO_RUNTIME_RO','text':'Zero accepted RO requests in this covered request-acceptance interval; no Tag-abundance inference.'})
 if joint('accepted_ro','raw_probe_reservation_fail') and usable['accepted_ro']>0 and usable['raw_probe_reservation_fail']==0:
  claims.append({'code':'NO_OBSERVED_PRESSURE','text':'RO acceptance occurred but no raw reservation-fail head cycles were observed in the covered frontend scope. This is not global Tag sufficiency.'})
 for name,code,text in [
  ('pressure_no_live_ro_tag','LOCALITY_MISMATCH','Pressure head cycles without local live RO Tags were observed; no another-set or counterfactual conclusion.'),
  ('pressure_live_ro_but_none_eligible','ELIGIBILITY_FILTERED','Pressure head cycles with live RO but no eligible victim were observed; examine separate sticky-reuse and required-not-ready predicates.'),
  ('relief_preview_not_consulted','PREVIEW_NOT_CONSULTED','Some pressure observations did not consult production relief; this differs from an evaluated no-eligible result.'),
  ('trigger_first_call_refused_after_detach','DETACH_THEN_DENIED','Some matched triggering invocations were denied after a victim detach; this does not undo the victim Tag release or prove later retry acceptance.')]:
  if name in usable and usable[name]>0:claims.append({'code':code,'text':text,'metric':name})
 # Zero alone is a bounded valid observation, not a complete root-cause explanation.
 if 'detach_success' in usable:
  if usable['detach_success']==0:claims.append({'code':'OBSERVED_ZERO','text':'Zero successful detach transitions in this exact covered scope; missing upstream stages remain UNKNOWN.'})
  else:claims.append({'code':'OBSERVED_NONZERO','text':'Successful detach transitions are reported by the E-accepted diagnostic; victim retirement and trigger acceptance retain separate domains.'})
 if report['errors']:
  report['status']='INVALID';report['measured_facts']={};return report
 target='synthetic_observations' if synthetic else 'scientific_application_conclusions'
 report[target]=claims
 report['status']='SYNTHETIC_CONTROL_ONLY' if synthetic else 'E_ACCEPTED_SEMANTIC_PROJECTION_WITH_EXPLICIT_UNKNOWNS'
 report['input_acceptance_ref']=copy.deepcopy(a.get('receipt_ref'));return report


def no_duplicates(pairs):
 result={}
 for key,value in pairs:
  if key in result:raise ValueError('duplicate JSON key: '+key)
  result[key]=value
 return result


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',nargs='?');p.add_argument('--template',action='store_true');p.add_argument('--out');args=p.parse_args()
 if args.template:result=template()
 elif args.input:
  src=Path(args.input)
  if src.stat().st_size>4*1024**2:raise ValueError('semantic input exceeds4MiB bound')
  result=analyze(json.loads(src.read_text(),object_pairs_hook=no_duplicates))
 else:p.error('give an accepted semantic input or --template')
 text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
 if args.out:Path(args.out).write_text(text)
 else:print(text,end='')

if __name__=='__main__':main()
