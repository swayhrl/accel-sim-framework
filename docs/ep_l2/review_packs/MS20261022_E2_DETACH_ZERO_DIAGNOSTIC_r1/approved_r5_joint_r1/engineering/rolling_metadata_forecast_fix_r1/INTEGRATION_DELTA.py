"""Root-review replacement helper in original Coordinator, not a new API/controller.
Apply only after review against actual current source/pins; this file is not run.
"""
def r5_metadata_preflight(data,spec,*,already_reserved=False,authority_data=None):
    if not detach_policy.tagpressure.is_spec(spec):return None
    actual=data if authority_data is None else authority_data
    if authority_data is not None:validate_successor_forecast_view(data,actual)
    item=actual[FIELD];detach_policy.active(item)
    r5=detach_policy.tagpressure;m=r5.scope().manifest()
    # Only original validated virtual forecasts enter physical scheduling.
    # They never alter the actual generation/tail or become canonical leases.
    keys={run_key(c['identity']):cid for cid,c in m['conditions'].items()}
    virtual_prefix='READONLY_SUBMITTED_FORECAST_'
    submitted=[]
    for key in set(data['runs'])-set(actual['runs']):
        require(key.startswith(virtual_prefix) and key[len(virtual_prefix):] in keys,'unapproved metadata submitted forecast')
        submitted.append(keys[key[len(virtual_prefix):]])
    retained={}
    for a in item['attempts'][55:]:
        if a['state'] in ACTIVE:retained[a['condition_id']]=retained_tree_bytes(Path(a['result_directory']))
    # Only other real campaign outputs remain in this term; r5 active+unstarted
    # endpoint reserves are calculated once from actual tail by the new module.
    active_other=[r for k,r in actual['runs'].items() if r['status'] in ACTIVE and r.get('experiment_id')==CAMPAIGN and k not in keys]
    leases=[r for r in actual['resource_leases'].values() if r['status'] in ACTIVE and r.get('experiment_id')==CAMPAIGN]
    other_pending=sum(max(0,r.get('disk_growth_bytes',FULL_GROWTH)-retained_tree_bytes(Path(r['result_directory']))) for r in active_other)
    other_pending+=sum(r.get('result_growth_bytes',0) for r in leases)
    return tagpressure_metadata.preflight(item,local_resources(),output_usage(),physical_pending_bytes=pending_growth(data),other_result_pending_bytes=other_pending,proposed_growth_bytes=0 if already_reserved else spec['maximum_result_bytes'],proposed_monitor_bytes=0 if already_reserved else 2*GIB,endpoint_retained_bytes=retained,submitted_condition_ids=submitted,proposed_condition_ids=[spec['condition_id']])
