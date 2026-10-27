"""CPU candidate only: explicit once-per-aged-target priority exception.
No install/apply/launch/IO. Caller must preserve every non-priority chooser gate,
CPU rebinding and final frame guard in a separately qualified integration.
"""
import copy
G=1024**3
POLICY=dict(max_cost_bytes=12*G,max_history_elapsed_seconds=1800,min_matched_completed=2)
def propose(aging,candidates,tokens,modeled_30min_release_bytes,policy=None):
 p=dict(POLICY,**(policy or{}));t=aging.get('target')
 if not t or aging.get('pressure_reasons')or aging.get('phase')!='ACCUMULATING_PROTECTED_RELEASE'or aging.get('backfill_cohorts'):return None
 key=(t['cohort'],t['first_eligible_monotonic']);C=aging['current_slack_bytes'];cost=t['cost_bytes']
 if key in tokens or C>=cost or C+modeled_30min_release_bytes>=cost:return None
 eligible=[c for c in candidates if c['cell']=='DH'and c['profile']=='P0'and c['cohort']!=t['cohort']and c['admitted']and not c['consumed']and not c['claimed']and not c['INTENT_exists']and 0<c['full_max_cost_bytes']<=min(p['max_cost_bytes'],C)and c['matched_closed_count']>=p['min_matched_completed']and c['max_closed_elapsed_seconds']<=p['max_history_elapsed_seconds']]
 if not eligible:return None
 c=min(eligible,key=lambda x:(x['median_closed_elapsed_seconds'],x['full_max_cost_bytes'],x['cohort']))
 return dict(candidate=copy.deepcopy(c),target_generation=key,protected_R_preserved_bytes=aging['protected_bytes'],target_cost_bytes=cost,modeled_30min_release_bytes=modeled_30min_release_bytes,scheduling_estimate_not_deadline=True,priority_exception_only=True)
def choose_with_full_gates(proposal,tokens,downstream_choose,fresh_state):
 if proposal is None:return None
 key=tuple(proposal['target_generation'])
 if key in tokens:return None
 candidate=proposal['candidate'];decision=downstream_choose([candidate])
 if decision is None:return None
 assert decision['cohort']==candidate['cohort'];fresh=fresh_state();current=fresh['candidates'][candidate['cohort']]
 if fresh['pressure_reasons']or fresh['target_generation']!=key or current['consumed']or current['claimed']or current['INTENT_exists']or not current['admitted']:return None
 cost=current['full_max_cost_bytes']
 if cost>POLICY['max_cost_bytes']or cost>fresh['physical_slack_bytes']:return None
 # Reserve one operational attempt only, no scientific credit. Main must append
 # durable owner token receipt before a decision is passed to existing claims.
 tokens[key]=dict(cohort=candidate['cohort'],state='ONE_SHOT_DECISION_RESERVED',full_max_cost_bytes=cost)
 return dict(decision,one_shot_priority_exception=dict(proposal,full_fresh_cost_bytes=cost,all_original_physical_gates_retained=True,actual_protected_state_mutated=False))
