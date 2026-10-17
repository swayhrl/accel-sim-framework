"""Read final-only counters with Lane M definitions; no execution or selection changes."""
from common import *


def summarize(name, workload, mode, run, status, uuid):
    text=(run/'simulator.stdout').read_text()
    values={k:int(v) for k,v in re.findall(r'^\s*(\w+)\s*=\s*(\d+)\s*$',text,re.M)}
    def n(key):return values.get(key)
    prefix='DTC_L1_'+mode+'_'
    svc='DTC_SERVICE_V1_'
    ready,pending=(n(prefix+s) for s in ['valid_hits','pending_hits'])
    allocation_field=prefix+('physical_allocations' if mode=='io' else 'new_misses')
    misses=n(allocation_field)
    references=n(prefix+'completion_dependency_count')
    accepted=ready+pending+misses if None not in [ready,pending,misses] else None
    retired=n(svc+'retired')
    samples=n(svc+'samples')
    def divided(k,den):return n(k)/den if n(k) is not None and den else 'UNAVAILABLE'
    row=dict(point=name,workload=workload,mode=mode,uuid=uuid,status=status,
             cycles=n('gpu_tot_sim_cycle'),active_instructions=n('gpu_tot_sim_insn'),
             accepted_128b_reference_count=accepted,completion_dependency_count=references,
             ready_reference_outcomes=ready,pending_reference_outcomes=pending,new_allocation_outcomes=misses,
             new_allocation_source_field=allocation_field,
             accepted_reference_balance=(accepted==references) if accepted is not None else 'UNAVAILABLE',
             ready_fraction=ready/accepted if accepted else 'UNAVAILABLE',
             pending_fraction=pending/accepted if accepted else 'UNAVAILABLE',
             new_fraction=misses/accepted if accepted else 'UNAVAILABLE',
             tag_evictions=n(prefix+'tag_evictions'),dtc_lower_created=n(prefix+'lower_created'),
             fully_ready_cacheable_retired=retired,
             all64sm_cycle_mean_pib=divided(svc+'pib_integral',samples),
             all64sm_cycle_mean_physical=divided(svc+'physical_integral',samples),
             ready_to_collect_per_cacheable_warp=divided(svc+'ready_to_collect_sum',retired),
             collection_per_cacheable_warp=divided(svc+'collection_cycles',retired),
             wb_wait_per_cacheable_warp=divided(svc+'wb_wait',retired),
             fully_ready_to_complete_per_cacheable_warp=divided(svc+'fully_ready_to_complete_sum',retired),
             mean_completed_map_loss_to_free=divided(svc+'map_loss_to_free_sum',n(svc+'map_loss_to_free_count')),
             collected_sectors=n(svc+'collected_sectors'),
             oo_tag_or_pool_reject_cycles='UNAVAILABLE',oo_duplicate_inflight_addresses='UNAVAILABLE',
             dram_payload='NOT_DERIVED_FROM_DTC_CREDITS',source_stdout_sha256=sha(run/'simulator.stdout'))
    return row
