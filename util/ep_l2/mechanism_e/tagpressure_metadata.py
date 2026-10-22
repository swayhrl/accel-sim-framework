"""Strict additive r5 metadata forecast; never a lease or generation refund."""
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

def preflight(item,resources,usage,*,physical_pending_bytes,result_pending_bytes,proposed_growth_bytes,proposed_monitor_bytes):
 extra=remaining(item)
 for n in (physical_pending_bytes,result_pending_bytes,proposed_growth_bytes,proposed_monitor_bytes):r5.require(type(n) is int and n>=0,'nonnegative exact conservative forecast')
 r5.require(resources['disk_free_bytes']-physical_pending_bytes-proposed_growth_bytes-proposed_monitor_bytes-extra>=5*GIB,'R5_STRICT_METADATA_WORKSPACE_FORECAST')
 r5.require(usage['new_bytes']+result_pending_bytes+proposed_growth_bytes+extra<=10*GIB,'R5_STRICT_METADATA_NEW10_FORECAST')
 r5.require(usage['total_bytes']+result_pending_bytes+proposed_growth_bytes+extra<=24*GIB,'R5_STRICT_METADATA_TOTAL24_FORECAST')
 return dict(status='R5_STRICT_ADDITIVE_METADATA_PREFLIGHT_PASS',remaining_metadata_forecast_bytes=extra,actual_usage_unchanged=True,no_virtual_or_real_lease_created=True)

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
