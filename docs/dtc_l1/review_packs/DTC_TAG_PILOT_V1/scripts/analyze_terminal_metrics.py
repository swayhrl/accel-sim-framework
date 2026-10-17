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


def main():
    assert (ROOT/'AUTHORITY_TERMINAL.json').exists(), 'No partial discovery counters or rankings'
    controls=json.loads((PACK/'ACCEPTED_CONTROLS.json').read_text())
    rows=[]
    for key,mode in [('GEMM_IO256','io'),('GEMM_OO128','oo'),('Gaussian_OO128','oo')]:
        c=controls[key]
        rows.append(summarize('accepted_'+key,c['spec']['workload'],mode,Path(c['run_dir']),
                              'ACCEPTED_REFERENCE',c['uuid']))
    with (PACK/'PRE_REGISTRATION.tsv').open() as f:plan=list(csv.DictReader(f,delimiter='\t'))
    for point in plan:
        receipt=ROOT/(point['attempt_uuid']+'.strict.json')
        if not receipt.exists():continue
        strict=json.loads(receipt.read_text())
        if strict['status']!='PASS_STRICT_EXPLORATORY_SCOPE':continue
        spec=json.loads(Path(point['spec_path']).read_text())
        row=summarize(point['candidate'],point['workload'],spec['dtc_mode'],
                      ROOT/'attempts'/(point['label']+'_'+point['attempt_uuid']),strict['status'],point['attempt_uuid'])
        original=next(r for r in rows if r['point']=='accepted_'+point['workload']+'_OO128')
        assert row['accepted_reference_balance'] is True
        assert row['completion_dependency_count']==original['completion_dependency_count']
        assert row['fully_ready_cacheable_retired']==original['fully_ready_cacheable_retired']
        assert row['collected_sectors']==original['collected_sectors']
        rows.append(row)
    table(PACK/'TERMINAL_MECHANISM_COMPARISON.tsv',rows)
    t0=next((r for r in rows if r['point']=='T0'),None)
    if t0:
        oo=controls['GEMM_OO128']['cycles'];io256=controls['GEMM_IO256']['cycles']
        table(PACK/'T0_MATCHED128.tsv',[dict(workload='GEMM',new_io128_uuid=t0['uuid'],
              io128_cycles=t0['cycles'],accepted_oo128_uuid=controls['GEMM_OO128']['uuid'],oo128_cycles=oo,
              OO128_speedup_over_IO128=t0['cycles']/oo,
              IO128_speedup_over_IO256=io256/t0['cycles'],
              active_depths='128/128; organization metadata differs; not equal area',
              inference='DTC internal organization/depth only, not explanation of OO versus CPLUS')])
    print('Final-only typed mechanism comparison',len(rows),'rows; no extra runs, tuning, or selection')


if __name__=='__main__':
    main()
