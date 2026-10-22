#!/usr/bin/env python3
"""Bounded numeric projection of an already-normalized observer summary; no acceptance API."""
import argparse, copy, hashlib, json
from pathlib import Path
import legacy_semantic_report as legacy

ROOT=Path(__file__).resolve().parent
FIELDS=json.loads((ROOT/'SOURCE_BOUND_SCHEMA_r4.json').read_text())['counter_fields']
U64=2**64-1
HISTORY={
 'old_SGEMM':{'state':'KNOWN_UPSTREAM_EMPTY_CERTIFICATE','reason':'Old main61 E048 used NO_READONLY_CERTIFICATION empty fallback. Its old runtime RO opportunity remains unknown; new certificate does not backfill it.'},
 'old_FWT':{'state':'KNOWN_UPSTREAM_WHOLE_EPOCH_STORE_EXCLUSION','reason':'Exact frozen whole-commandlist128B certificate: all131072 read-containing lines and41943040 read-lane-line references share a line with a store in the same epoch; no certifiable RO lines under that scope.'},
 'other_old_positive_RO':{'state':'UNKNOWN','reason':'No historical dynamic pressure/eligibility evidence; this SGEMM point cannot recover it.'}}
LIMITS=[
 'Projection only: E remains sole application acceptance authority; decoder validity is not full application PASS.',
 'Head-cycle, way exposure, commit invocation, transaction, requester response, packet and sector units stay separate.',
 'Raw Tag pressure covers actual visible frontend heads after upstream TVD/other skipped paths; zero is not global Tag sufficiency.',
 'Exact eligible_* counters are measured conditional joints. No marginal products or guessed head-to-commit linkage.',
 'Capacity not-consulted may include a resident hit/early path; line NA is included in line unobserved, never added twice.',
 'Way first-reason bins are exclusive precedence bins; predicate masks are nonexclusive and not causal shares.',
 'Relieve may detach before later request denial. Detach, immediate acceptance, responses and retirement are different events.',
 'Phase is physical active-kernel state, never requester/victim causal kernel ownership. Decoder omits phase numeric projection.',
 'Samples are capped examples; no sample extrapolation, speedup, critical-path stall sum or later retry inference.']

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(x):return hashlib.sha256(canonical(x)).hexdigest()
def unique(p):
 d={}
 for k,v in p:
  if k in d:raise ValueError('duplicate JSON key '+k)
  d[k]=v
 return d

def panels(c):
 """Rows carry only source-supported same-population denominators; no cross-domain waterfall."""
 errors=[]; rows=[];mapped=set()
 def value(k):
  v=c.get(k)
  if v is None:return None
  if type(v) is not int or not 0<=v<=U64:errors.append('invalid uint64 '+k);return None
  return v
 vals={k:value(k) for k in FIELDS}
 def sub(a,b):
  if vals[a] is None or vals[b] is None:return None
  v=vals[a]-vals[b]
  if v<0:errors.append('negative derived '+a+'-'+b);return None
  return v
 derived={'probed_heads':sub('observed_heads','probe_skipped'),
          'live_way_exposures':sub('ways_examined','way_no_live_ro'),
          'terminal_detached_residual':sub('detach_success','detached_retired')}
 def add(names,domain,unit,den=None,note=None):
  for k in names:
   mapped.add(k);v=vals[k];dv=derived.get(den) if den in derived else vals.get(den)
   rows.append({'metric':k,'domain':domain,'unit':unit,'value':v,
    'measurement_state':'UNKNOWN_NOT_EMITTED' if v is None else 'MEASURED',
    'denominator_metric':den,'denominator_value':dv,'ratio':None if v is None or dv in (None,0) else v/dv,
    'ratio_state':'NA_NO_RATIO_DECLARED' if den is None else 'UNKNOWN_DENOMINATOR' if dv is None else 'NA_ZERO_DENOMINATOR' if dv==0 else 'MEASURED',
    'note':note})
 add(['observed_heads','probe_skipped'],'FRONTEND_HEAD_CYCLE','head_physical_cycle',note='Head UID/slice/physical-cycle deduplicated; not unique requests.')
 add(['head_absent_cycles'],'HEAD_ABSENT_CYCLE','slice_physical_cycle')
 add(['skip_tvd','skip_ideal','skip_disabled','skip_other'],'FRONTEND_HEAD_CYCLE','head_physical_cycle','probe_skipped','Upstream/alternate gate skipped; raw Tag pressure NA at this hook.')
 add([k for k in FIELDS if k.startswith('raw_') and k!='raw_tag_fail_commit'],'FRONTEND_HEAD_CYCLE','head_physical_cycle','probed_heads')
 add(['requester_ro_candidate','requester_nonro','requester_ro_runtime_off'],'FRONTEND_HEAD_CYCLE','head_physical_cycle','probed_heads')
 add(['certified_resident_hits','candidate_deferred_or_native'],'FRONTEND_HEAD_CYCLE','head_physical_cycle','requester_ro_candidate')
 add(['pressure_T_disabled','pressure_T_enabled','pressure_prod_probe_reached','pressure_prod_probe_not_reached','pressure_frontend_admitted','pressure_frontend_denied'],'PRESSURE_HEAD_CYCLE','head_physical_cycle','raw_reservation_fail')
 add(['pressure_no_live_ro','pressure_live_ro_no_eligible','pressure_eligible'],'PRESSURE_HEAD_CYCLE','head_physical_cycle','pressure_T_enabled')
 add(['pressure_rewrite_miss','pressure_rewrite_hit_reserved','pressure_kept_fail','pressure_relief_not_consulted','pressure_intermediate_other'],'PRESSURE_HEAD_CYCLE','head_physical_cycle','pressure_prod_probe_reached')
 add(['rewritten_final_admitted','rewritten_final_denied','rewritten_final_unknown'],'PRESSURE_HEAD_CYCLE','head_physical_cycle','pressure_rewrite_miss','Rewrite-to-MISS and final frontend admission; not commit acceptance.')
 add(['ways_examined'],'PRESSURE_WAY_SCAN','way_exposure')
 add([k for k in FIELDS if k.startswith('way_')],'PRESSURE_WAY_SCAN','way_exposure','ways_examined','Exclusive ordered first reason; live/attached then sticky reuse then no missing required sectors then eligible.')
 add([k for k in FIELDS if k.startswith('eligible_hist_')],'PRESSURE_HEAD_CYCLE','head_physical_cycle','pressure_T_enabled')
 add([k for k in FIELDS if k.startswith('predicate_hist_')],'PRESSURE_WAY_SCAN','way_exposure','live_way_exposures','Joint bitmask: attached=1,reuse=2,missing=4; disjoint masks, constituent predicates overlap.')
 add([k for k in FIELDS if k.startswith('preview_') or k.startswith('primary_') or k.startswith('mask_')],'FRONTEND_HEAD_CYCLE','head_physical_cycle','probed_heads','primary is first known blocker; masks/early paths are overlapping. mask_line is combined source snapshot, not dedicated line-index proof.')
 add(['ro_capacity_population'],'FRONTEND_HEAD_CYCLE','RO_candidate_head_physical_cycle','requester_ro_candidate')
 add(['ro_capacity_consulted','ro_capacity_not_consulted','ro_line_na_M_or_existing'],'FRONTEND_HEAD_CYCLE','RO_candidate_head_physical_cycle','ro_capacity_population','First actual capacity invocation; line NA M1/existing is a subset of line unobserved.')
 for p in ['descriptor','address','line_probe','line_slots']:
  add(['ro_'+p+'_checked','ro_'+p+'_unobserved'],'FRONTEND_HEAD_CYCLE','RO_candidate_head_physical_cycle','ro_capacity_population','Unobserved is not fail or pass; traditional line unobserved includes explicit line NA.')
  add(['ro_'+p+'_pass','ro_'+p+'_fail'],'FRONTEND_HEAD_CYCLE','RO_candidate_head_physical_cycle','ro_'+p+'_checked')
 add(['eligible_frontend_admitted','eligible_frontend_denied','eligible_prod_probe_reached','eligible_prod_probe_not_reached','eligible_capacity_consulted','eligible_capacity_not_consulted'],'ELIGIBLE_PRESSURE_HEAD_CYCLE','head_physical_cycle','pressure_eligible','Actual conditional joint: raw FAIL,T enabled,same-set eligible>0.')
 add(['eligible_rewrite_miss','eligible_rewrite_hit_reserved','eligible_kept_fail','eligible_relief_not_consulted','eligible_intermediate_other'],'ELIGIBLE_PRESSURE_HEAD_CYCLE','head_physical_cycle','eligible_prod_probe_reached')
 add(['eligible_descriptor_fail','eligible_address_fail','eligible_line_probe_fail','eligible_line_slots_fail'],'ELIGIBLE_PRESSURE_HEAD_CYCLE','head_physical_cycle','eligible_capacity_consulted','Conditional first-call refusal counts, not multiplied marginal percentages; predicate-specific eligible checked denominators not emitted.')
 add([k for k in FIELDS if k.startswith('eligible_early_')],'ELIGIBLE_PRESSURE_HEAD_CYCLE','head_physical_cycle','eligible_capacity_not_consulted','Actual early-return joint subsets; not every not-consulted head is blocked.')
 add(['ft_access_attempts'],'COMMIT_ACCESS','invocation')
 add([k for k in FIELDS if k.startswith('commit_')]+['raw_tag_fail_commit'],'COMMIT_ACCESS','invocation','ft_access_attempts','Branch counters may overlap across source stages; only explicit accepted/denied/exception partition is exhaustive.')
 add(['relieve_calls'],'COMMIT_ACCESS','relieve_invocation','raw_tag_fail_commit')
 add(['relieve_T_disabled','relieve_no_eligible','relieve_eligible_selected'],'COMMIT_ACCESS','relieve_invocation','relieve_calls')
 add(['detach_calls','selected_identity_mismatch'],'COMMIT_ACCESS','detach_invocation')
 add(['detach_success','detach_false','detach_exception'],'COMMIT_ACCESS','detach_invocation','detach_calls')
 add([k for k in FIELDS if k.startswith('detach_false_')],'COMMIT_ACCESS','detach_invocation','detach_false')
 add([k for k in FIELDS if k.startswith('post_relief_')],'COMMIT_ACCESS','invocation','relieve_calls','Reprobe follows every actual relieve call, including T-disabled/no-eligible calls.')
 add(['trigger_accepted_after_detach','trigger_denied_after_detach','trigger_exception_after_detach'],'TRIGGER_CALL','invocation','detach_success','Same successful detach call immediate result only; later request retry is NOT_MEASURED.')
 add([k for k in FIELDS if k.startswith('denied_')],'COMMIT_ACCESS','invocation','commit_denied','Observed refusal labels only; do not claim independent/exhaustive stall causes.')
 add(['ro_admits','ro_retired','reuse_seen_first_transition','detached_retired'],'TRANSACTION_LIFECYCLE','transaction_transition')
 add(['ro_merges'],'REQUESTER_LIFECYCLE','merged_requester')
 add(['ro_responses','detached_responses'],'VICTIM_RESPONSE','requester_response',note='Requester responses are not retired transaction counts.')
 add(['ro_fill_packets','detached_return_packets'],'RETURN_PACKET','packet')
 add(['detached_return_sectors'],'RETURN_SECTOR','sector')
 add(['response_backpressure'],'RESPONSE_COMMIT_CALL','failed_commit_response_invocation',note='Only actual commit_response(false); upstream ICNT-full waits can avoid this call.')
 add(['closure_errors'],'OBSERVER_VALIDATION','error')
 add(['samples_seen','samples_stored','samples_dropped'],'PRESSURE_SAMPLE','pressure_hook_call',note='At most64 stored examples, never population estimate.')
 add([k for k in FIELDS if k.startswith('transition_joint_')],'TRANSACTION_EVENT_MIX','admit_merge_or_fill_event',note='Actual transition snapshots; not time occupancy or additive transaction count.')
 if mapped!=set(FIELDS):errors.append('Unmapped fields '+str(sorted(set(FIELDS)-mapped)))
 return {'rows':rows,'derived':derived,'errors':errors,'counts':vals}

def project(summary,context=None):
 d=summary.get('detach_observer_diagnostic');o=d.get('observer',{}) if isinstance(d,dict) else summary
 r={'schema':'E2_DETACH_R4_NUMERIC_PROJECTION_V1','status':'INCOMPLETE','pair':False,
    'scientific_application_acceptance_granted':False,'claim_limits':LIMITS,'historical_scope':copy.deepcopy(HISTORY),
    'normalized_summary_sha256':digest(summary),'observer_status':o.get('status'),'errors':[],
    'phase_numeric_state':'UNKNOWN_DECODER_NOT_PROJECTED','phase_catalog':o.get('phase_catalog'),
    'phase_causal_kernel_attribution':'NOT_MEASURED','later_trigger_acceptance':'NOT_MEASURED',
    'victim_owner_kernel':'UNKNOWN','sample_policy':'CAPPED_EXAMPLES_NOT_DENOMINATORS'}
 if o.get('status') not in ('VALID_OBSERVER_TERMINAL_DECLARATIONS_ONLY','SYNTHETIC_OBSERVER_CONTROL_ONLY'):
  r['errors'].append('No valid normalized observer terminal declarations');return r
 p=panels(o.get('global_counters',{}));r['global']=p; r['errors']+=p['errors']
 slices=o.get('slice_counters',{});r['slices']={}
 for sid,c in slices.items():
  if sid not in map(str,range(64)):r['errors'].append('nonphysical slice '+str(sid));continue
  sp=panels(c);r['slices'][sid]=sp;r['errors']+=['slice'+sid+': '+x for x in sp['errors']]
 r['source_identity']=copy.deepcopy(d.get('source_identity')) if isinstance(d,dict) else None
 r['schema_counter_fields']=o.get('schema_counter_fields');r['r4_expected_counter_fields']=212
 r['new_field_missing']=[x for x in FIELDS[172:] if p['counts'][x] is None]
 r['coverage']={'observed_heads':p['counts']['observed_heads'],'probed_heads':p['derived']['probed_heads'],
  'skipped_heads':p['counts']['probe_skipped'],'head_absent_cycles':p['counts']['head_absent_cycles'],
  'slice_ids_projected':sorted(slices,key=lambda s:int(s) if s.isdigit() else -1),
  'observer_expected_slices':o.get('expected_slice_count'),'final_cycle':o.get('final_cycle'),
  'global_pressure_claim':'VISIBLE_PROBED_HEAD_SCOPE_ONLY_UPSTREAM_SKIPS_NA',
  'require_closed_declaration':o.get('require_closed')}
 synthetic=o.get('data_kind')=='SYNTHETIC' or o.get('status')=='SYNTHETIC_OBSERVER_CONTROL_ONLY'
 accepted=False
 if context is not None and not synthetic:
  cr=legacy.analyze(context);r['context_projection_status']=cr['status'];r['context_errors']=cr['errors']
  accepted=cr['status']=='E_ACCEPTED_SEMANTIC_PROJECTION_WITH_EXPLICIT_UNKNOWNS'
  if context.get('normalized_summary_sha256')!=r['normalized_summary_sha256']:
   r['errors'].append('context not bound to exact normalized summary');accepted=False
  if not isinstance(d,dict):r['errors'].append('E accepted context requires original normalized wrapper');accepted=False
  else:
   i=context.get('identity',{});si=d.get('source_identity',{})
   for ck,sk in [('core_commit','core_source_commit'),('framework_commit','framework_source_commit'),('binary_sha256','binary_sha256')]:
    if i.get(ck)!=si.get(sk):r['errors'].append('context source mismatch '+ck);accepted=False
   if i.get('qualification_id')!=d.get('qualification_id'):r['errors'].append('context Q mismatch');accepted=False
  r['E_acceptance_ref']=context.get('acceptance',{}).get('receipt_ref')
 if r['errors']:r['status']='INVALID_NUMERIC_PROJECTION';r['observations']=[];return r
 c=p['counts'];observations=[]
 def fact(code,keys,text):
  observations.append({'code':code,'measured_counters':{k:c[k] for k in keys},'statement':text})
 if c['detach_success'] is None:fact('DETACH_UNKNOWN',['detach_success'],'Detach count not emitted; no zero substitution.')
 elif c['detach_success']==0:fact('OBSERVED_ZERO',['detach_success'],'No successful detach transitions in exact decoded scope; report separate stage distributions and unknown linkage.')
 else:fact('OBSERVED_NONZERO',['detach_success','detached_retired','trigger_accepted_after_detach','trigger_denied_after_detach'],'Actual successful detach transitions; victim drain and immediate triggering-call result remain separate. E alone accepts closure.')
 if c['ro_admits']==0:fact('NO_NEW_RO_TRANSACTIONS',['ro_admits','ro_merges','certified_resident_hits','requester_ro_candidate'],'Zero new RO transaction admissions. Resident hits, candidate demand heads and merged requesters are distinct populations.')
 if c['raw_reservation_fail']==0:fact('NO_OBSERVED_LOCAL_PRESSURE',['raw_reservation_fail','observed_heads','probe_skipped'],'No raw all-reserved Tag probe at covered heads; skipped upstream paths remain NA, not global Tag sufficiency.')
 for k,code,text in [
  ('pressure_no_live_ro','LOCALITY_MISMATCH','Pressure observations without same-set live RO victims.'),
  ('pressure_live_ro_no_eligible','ELIGIBILITY_FILTERED','Pressure observations with local live RO but no eligible victim; inspect exclusive way reasons and joint predicate masks, not inferred per-head cause fractions.'),
  ('eligible_prod_probe_not_reached','ELIGIBLE_PRODUCTION_NOT_REACHED','Shadow-eligible pressure heads did not reach original production probe; exact head subset.'),
  ('eligible_relief_not_consulted','ELIGIBLE_RELIEF_NOT_CONSULTED','Shadow-eligible pressure heads reached original probe but did not consult production relief.'),
  ('eligible_frontend_denied','ELIGIBLE_FRONTEND_DENIED','Shadow-eligible pressure heads were denied frontend access; exact conditional count, no assumed eventual commit linkage.'),
  ('trigger_denied_after_detach','DETACH_THEN_DENIED','Actual detach succeeded before triggering invocation was denied later; this is legal, not a failed victim detach.')]:
  if c[k] is not None and c[k]>0:fact(code,[k],text)
 r['observations']=observations
 r['status']='SYNTHETIC_NUMERIC_CONTROL_ONLY' if synthetic else 'E_ACCEPTED_NUMERIC_PROJECTION' if accepted else 'PROVISIONAL_NORMALIZED_PROJECTION_NOT_APPLICATION_ACCEPTANCE'
 r['scientific_application_conclusions']=observations if accepted else []
 r['unknowns']=[k for k,v in c.items() if v is None]+['Later trigger retry linkage','Victim causal owner kernel','Historical dynamic counters for old positive-RO detach0','Phase numerical rows omitted by frozen decoder']
 return r

def load(path):
 p=Path(path)
 if p.stat().st_size>16*1024**2:raise ValueError('normalized/context metadata exceeds16MiB')
 return json.loads(p.read_text(),object_pairs_hook=unique)
def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('summary');a.add_argument('--context');a.add_argument('--out',required=True);args=a.parse_args()
 result=project(load(args.summary),load(args.context) if args.context else None)
 Path(args.out).write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
if __name__=='__main__':main()
