"""Pure finite-family adaptive predicates. No I/O/process/native operations."""
def decision(status,reason,**evidence):return dict(status=status,reason=reason,evidence=evidence)
def gains_ok(value,threshold):return value is not None and value>=threshold-1e-12
def evaluate_service(stage,workload,frequency,history):
 if stage=='FIRST6':return decision('RELEASE','USER_APPROVED_INITIAL_SIX')
 prev=1020 if frequency==1275 else 1275
 before=850 if frequency==1275 else 1020
 if workload=='VECTOR4M':prev,before=1275,1020
 p=history.get((workload,prev));b=history.get((workload,before))
 if p and p.get('failed'):return decision('HOLD','PREVIOUS_PAIR_FAILED_NO_RETRY_OR_REFUND')
 if not p or not p.get('accepted_and_archived'):return decision('WAIT','PREVIOUS_EXACT_PAIR_NOT_ACCEPTED_AND_ARCHIVED')
 if not b or not b.get('accepted_and_archived'):return decision('HOLD','EXACT_BASELINE_PAIR_UNKNOWN')
 if frequency==1275:
  ep_gain=b['EP_cycles']/p['EP_cycles']-1;interaction=(p['S_cycles']/p['EP_cycles'])/(b['S_cycles']/b['EP_cycles'])-1
  passed=gains_ok(ep_gain,.03)or gains_ok(interaction,.01)
  return decision('RELEASE'if passed else'PRUNE','APPROVED_3PCT_EP_ABSOLUTE_OR_1PCT_INTERACTION',EP_absolute_gain=ep_gain,EP_interaction_gain=interaction)
 sgain=b['S_cycles']/p['S_cycles']-1;egain=b['EP_cycles']/p['EP_cycles']-1;passed=gains_ok(sgain,.03)or gains_ok(egain,.03)
 return decision('RELEASE'if passed else'PRUNE','APPROVED_3PCT_EITHER_ARM_INCREMENTAL',S_incremental_gain=sgain,EP_incremental_gain=egain)
def evaluate_retention(stage,primaries,baseline,ni_results):
 if stage=='FIRST_FWT':return decision('RELEASE','USER_APPROVED_INITIAL_FWT_FOUR_NI_REQUIRED')
 if any(p.get('failed')for p in primaries):return decision('HOLD','FWT_PRIMARY_OR_NI_EXECUTION_FAILED')
 if len(primaries)!=4 or not all(p.get('accepted_and_archived')for p in primaries):return decision('WAIT','ALL_FOUR_FWT_POINTS_NOT_ACCEPTED_AND_ARCHIVED')
 if len(ni_results)!=2 or not all(n=='PASS'for n in ni_results):return decision('HOLD','BOTH_SAME_MODE_APPLICATION_NI_MUST_PASS')
 if not baseline or not baseline.get('accepted_and_archived'):return decision('HOLD','EXACT_WV_REFERENCE_UNKNOWN')
 unknown=False;summary=[];passed=False
 for p in primaries:
  if p['observer_variant']!='ON':continue
  gain=1-p['cycles']/baseline['cycles'];a=p.get('victim_read_responses');b=baseline.get('victim_read_responses')
  delta=abs(a-b)/b if a is not None and b is not None and b>0 else(0 if a==b==0 else None)
  unknown|=delta is None;passed|=gains_ok(gain,.005)or gains_ok(delta,.10);summary.append(dict(mode=p['mode'],cycle_gain_vs_WV=gain,victim_service_relative_change=delta))
 if passed:return decision('RELEASE','APPROVED_HALF_PERCENT_CYCLES_OR_10PCT_VICTIM_CHANGE',comparisons=summary)
 if unknown:return decision('HOLD','NO_CYCLE_TRIGGER_AND_VICTIM_POPULATION_UNKNOWN',comparisons=summary)
 return decision('PRUNE','ALL_KNOWN_FWT_TRIGGERS_BELOW_THRESHOLD',comparisons=summary)
