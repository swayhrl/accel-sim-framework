"""Exact batch generation forecast + active physical metadata scheduling.
No resource guard waiver, authority change, lease or generation refund.
"""
import re,copy
import tagpressure_successor as r5
MIB=2**20;GIB=2**30;PER_CONDITION=160*MIB

def remaining(item,scope=None):
 s=r5.scope() if scope is None else scope;m=s.manifest();b=item[r5.FIELD];closed=b.get('metadata_closures',{})
 r5.require(set(closed)<=set(r5.CONDITIONS),'unapproved metadata closure condition')
 for cid,ref in closed.items():
  c=r5.read(ref);r5.require(c.get('schema')=='E2_R5_ENDPOINT_METADATA_PUBLICATION_CLOSED_V1' and c.get('status')=='E_ROOT_INDEPENDENT_POINT_AND_METADATA_CLOSED','root actual metadata closure required')
  r5.require(c.get('campaign_id')==r5.CAMPAIGN and c.get('condition_id')==cid and c.get('source_identity')==m['source_identity'],'metadata closure source/condition differs')
  attempts=[a for a in item['attempts'][55:] if a['condition_id']==cid];r5.require(len(attempts)==1,'metadata closure must have one actual paid endpoint');a=attempts[0]
  r5.require(a['state']=='COMPLETE_VALID' and a['actual_start'] is True and c.get('attempt_id')==a['attempt_id'],'no failed/unstarted metadata release')
  result=item['accepted_results'].get(a['attempt_id']);r5.require(result is not None and c.get('accepted_result_ref')=={'path':result['path'],'sha256':result['sha256']},'independently accepted exact endpoint required');r5.read(c['accepted_result_ref'])
  r5.require(type(c.get('actual_metadata_allocated_bytes')) is int and 0<=c['actual_metadata_allocated_bytes'],'actual nonnegative metadata allocation required; forecast is not a cap')
  r5.require(c.get('actual_generation_retained_in_accounting') is True and c.get('retired_remaining_forecast_bytes')==PER_CONDITION and c.get('released_forecast_is_not_generated_result_refund') is True,'forecast release cannot erase historical generation')
  r5.require(re.fullmatch('[0-9a-f]{40}',c.get('immutable_publication_commit','')),'immutable actual point/metadata publication required')
  rb=r5.read(c['publication_remote_readback_ref']);r5.require(rb.get('remote_commit')==c['immutable_publication_commit'] and rb.get('verified') is True,'actual immutable remote readback required')
 r5.require(all(c['metadata_forecast_bytes']==PER_CONDITION for c in m['conditions'].values()) and m['collector_metadata_forecast_bytes']==4*PER_CONDITION,'exact approved 640MiB metadata forecast')
 return (4-len(closed))*PER_CONDITION

def _tail_by_condition(item):
 rows={}
 for a in item['attempts'][55:]:
  cid=a.get('condition_id');r5.require(cid in r5.CONDITIONS and cid not in rows,'unexpected/duplicate exact r5 tail')
  r5.require(a.get('state') in r5.BEFORE|r5.AFTER,'unreviewed r5 attempt state')
  rows[cid]=a
 return rows

def _condition_ids(ids):
 r5.require(type(ids) in (list,tuple,set) and all(type(cid) is str and cid in r5.CONDITIONS for cid in ids),'only exact r5 condition identities')
 r5.require(len(ids)==len(set(ids)),'duplicate proposed/submitted condition identity')
 return set(ids)

def generation_endpoint_remaining(item,endpoint_retained_bytes):
 """All four potential endpoint outputs, irrespective of physical scheduling.
 Only actual active endpoint allocated bytes can reduce that endpoint's future
 cap; terminal allocations remain in actual generation. No refund/reset.
 """
 rows=_tail_by_condition(item);active={cid for cid,a in rows.items() if a['state'] in r5.ACTIVE}
 r5.require(type(endpoint_retained_bytes) is dict and set(endpoint_retained_bytes)==active,'actual allocated-byte map must name exactly active r5 endpoints')
 m=r5.scope().manifest();total=0
 for cid in r5.CONDITIONS:
  cap=m['conditions'][cid]['resources']['maximum_result_bytes'];r5.require(cap==384*MIB,'exact endpoint cap')
  if cid not in rows:total+=cap
  elif cid in active:
   value=endpoint_retained_bytes[cid];r5.require(type(value) is int and value>=0,'actual nonnegative endpoint allocated bytes')
   total+=max(0,cap-value)
  # Every terminal attempted condition is consumed/no retry. Its generated
  # bytes stay in actual usage, its outstanding metadata stays reserved below.
 return total

def physical_metadata_conditions(item,submitted_condition_ids,proposed_condition_ids):
 # Validate immutable root closure refs before excluding any forecast.
 remaining(item)
 closed=set(item[r5.FIELD].get('metadata_closures',{}));rows=_tail_by_condition(item)
 submitted=_condition_ids(submitted_condition_ids);proposed=_condition_ids(proposed_condition_ids)
 r5.require(len(proposed)<=1,'one original central proposal at a time')
 r5.require(not (proposed & closed),'closed/consumed condition cannot be proposed')
 # A finished/failed condition still needs room until its metadata publication
 # is independently closed. Completely unstarted, unsubmitted conditions do not.
 ids=(set(rows)|submitted|proposed)-closed
 return [cid for cid in r5.CONDITIONS if cid in ids]

def preflight(item,resources,usage,*,physical_pending_bytes,other_result_pending_bytes,proposed_growth_bytes,proposed_monitor_bytes,endpoint_retained_bytes,submitted_condition_ids,proposed_condition_ids):
 metadata_generation=remaining(item)
 physical_ids=physical_metadata_conditions(item,submitted_condition_ids,proposed_condition_ids)
 physical_metadata=len(physical_ids)*PER_CONDITION
 endpoint_generation=generation_endpoint_remaining(item,endpoint_retained_bytes)
 for n in (physical_pending_bytes,other_result_pending_bytes,proposed_growth_bytes,proposed_monitor_bytes):r5.require(type(n) is int and n>=0,'nonnegative exact conservative forecast')
 proposed=_condition_ids(proposed_condition_ids);rows=_tail_by_condition(item)
 r5.require(proposed_growth_bytes in (0,384*MIB) and proposed_monitor_bytes in (0,2*GIB),'exact ordinary proposed result/monitor envelope')
 if proposed_growth_bytes==0 and proposed:
  r5.require(all(cid in rows and rows[cid]['state'] in r5.ACTIVE for cid in proposed),'zero additional physical growth only for already-held endpoint')
 r5.require((proposed_growth_bytes==0)==(proposed_monitor_bytes==0),'held proposal/result-monitor must agree')
 r5.require(resources['disk_free_bytes']-physical_pending_bytes-proposed_growth_bytes-proposed_monitor_bytes-physical_metadata>=5*GIB,'R5_ACTIVE_METADATA_WORKSPACE_FORECAST')
 # The generation ledger retains the entire batch worst case, including all
 # not-yet-started endpoint caps and every unclosed metadata forecast. The
 # proposed cap is already included above; do not charge it twice here.
 r5.require(usage['new_bytes']+other_result_pending_bytes+endpoint_generation+metadata_generation<=10*GIB,'R5_FULL_BATCH_NEW10_GENERATION_FORECAST')
 r5.require(usage['total_bytes']+other_result_pending_bytes+endpoint_generation+metadata_generation<=24*GIB,'R5_FULL_BATCH_TOTAL24_GENERATION_FORECAST')
 return dict(status='R5_PHYSICAL_ACTIVE_AND_FULL_BATCH_GENERATION_PREFLIGHT_PASS',
  metadata_generation_reserve_bytes=metadata_generation,batch_endpoint_remaining_generation_bytes=endpoint_generation,
  physical_metadata_condition_ids=physical_ids,physical_metadata_forecast_bytes=physical_metadata,
  full_batch_initial_forecast_bytes=4*(384+160)*MIB,actual_usage_unchanged=True,no_virtual_or_real_lease_created=True)

def close(item,ref):
 """Called by root through original Coordinator.locked after real publication."""
 m=r5.scope().manifest();doc=r5.read(ref);cid=doc.get('condition_id')
 r5.require(cid in r5.CONDITIONS,'unapproved metadata condition')
 b=item[r5.FIELD];closures=b.setdefault('metadata_closures',{})
 r5.require(cid not in closures or closures[cid]==ref,'metadata closure ref immutable')
 candidate=copy.deepcopy(item);candidate[r5.FIELD].setdefault('metadata_closures',{})[cid]=dict(ref)
 extra=remaining(candidate)  # Validate everything before changing even the in-memory original.
 closures[cid]=dict(ref)
 return dict(condition_id=cid,remaining_metadata_forecast_bytes=extra,generated_result_bytes_refunded=0)
