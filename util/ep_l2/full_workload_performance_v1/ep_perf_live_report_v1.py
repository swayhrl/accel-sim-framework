"""Main's read-only scientific aggregation; no model starts or authority writes."""
import csv, os, sys, time
from ep_perf_common import *


def report():
    registry, epoch = authority(); q = registry['registered_future_requests'][GOAL]
    merge_ref = ref(ROOT/'agent_b/merge_performance_results.py')
    need(merge_ref['sha256'] == read(ROOT/'control/LIVE_REPORT_CONFIG.json')['merge_parent_sha256'], 'merge implementation drift')
    merger = module(merge_ref, 'pure_live_performance_merge')
    records=[]; run_rows=[]; counts={}; specs={}
    for case,digest in q['admitted_specs'].items():
        spec_ref=dict(path=str(ROOT/'cases'/case/'control/FROZEN_SPEC.json'),sha256=digest)
        s=exact(spec_ref); specs[case]=s
        row=q['consumed'].get(case,{}); state=row.get('state','NOT_STARTED')
        counts[state]=counts.get(state,0)+1
        r=merger.collect_case(spec_ref,q)
        if state!='CLOSED_ACCEPTED':
            r['accepted']=False
        else:
            need(row.get('archive_receipt_ref'), 'closed point without archive receipt')
            exact(row['archive_receipt_ref'])
        records.append(r)
        run_rows.append(dict(cohort=case, program=s['program'], input_identity_sha256=s['input_identity_sha256'], profile=s['profile'], mode=s['mode'],
            state=state, cycles=r.get('cycles',''), instructions=r.get('instructions',''), CTA=r.get('CTA',''), kernel_count=r.get('kernel_count',''),
            source_Core=s['source_identity']['core_source_commit'], ELF_sha256=s['source_identity']['binary_sha256'],
            spec_sha256=digest, archive_receipt_sha256=row.get('archive_receipt_ref',{}).get('sha256',''),
            merge_exclusion=r.get('merge_exclusion','')))
    corpus=read(ROOT/'agent_a/all_coverage/SM70_125_COMPLETE_INPUT_AND_RO_SCOPE_MAP.json')
    required=sorted({r['full_command_identity_sha256'] for r in corpus['rows'] if r['main42_selected']})
    pairs,summaries,blocked=merger.summarize_pairs(records,required)
    for p in pairs:
        p['program']=specs[p['S_cohort']]['program']
    positive_RO={s['input_identity_sha256'] for s in specs.values() if s['mode']=='F'}
    ref_pairs=[p for p in pairs if p['profile']=='REF32x8_L100' and p['treatment']=='F']
    now_utc=now()
    current=dict(goal=GOAL, utc=now_utc, status='LIVE_INTERIM_NOT_FINAL_REPORT',
        admitted_exact_points=len(q['admitted_specs']), consumed_starts=len(q['consumed']), fresh_registered_remaining=q['remaining'],
        terminal_counts=counts, fully_closed_accepted=counts.get('CLOSED_ACCEPTED',0),
        accepted_reference_S_F_input_pairs=len(ref_pairs), accepted_reference_S_F_programs=len({p['program'] for p in ref_pairs}),
        all_accepted_profile_pairs=len(pairs), main42_program_target=42, frozen_primary_input_target=35,
        deduplicated_ordinary_input_target=96, original_ordinary_record_count=100, separate_fraction_trim_records=25,
        positive_RO_inputs_with_exact_registered_F_specs=len(positive_RO),
        observed_profiles=sorted({s['profile'] for s in specs.values()}),
        full_common_set_GM=None, GM_claim_boundary='All35 is an interim coverage target, not a completed scientifically eligible F common set. No global optimum/GM claim until final eligibility and full matched population are frozen and complete.',
        scientific_scope='TRACE_DEFINED_COMPLETE_DECLARED_COMMANDLIST', numerical_output='UNKNOWN', original_capture_completeness='UNKNOWN',
        optional_pressure_lifetime_counters='NOT_OBSERVED_NOT_MEASURED_ZERO',
        registry_sha256=sha(REG), epoch_sha256=sha(EPOCH), snapshot_stable_at_begin=True,
        Source_keep=True, automatic_retry=False, model_starts_by_this_script=0, registry_writes_by_this_script=0,
        runtime_progress_ref=ref(ROOT/'control/CURRENT_PROGRESS.json'), all_scientific_results_in_genuine164=True)
    out=ROOT/'analysis/live';out.mkdir(parents=True,exist_ok=True)
    put(out/'CURRENT_STATUS.json',current)
    put(out/'MATCHED_RESULT_DETAILS.json',dict(utc=now_utc,pairs=pairs,profile_summaries=summaries,blocked=blocked,
         current_claim='INTERIM_ONLY_ALL_NEGATIVES_RETAINED', required_primary_input_target=required))
    def table(path,rows,fields):
        tmp=path.with_name('.'+path.name+'.tmp')
        with tmp.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
        os.replace(tmp,path)
    table(out/'RUN_STATUS.csv',run_rows,list(run_rows[0]) if run_rows else ['cohort'])
    table(out/'MATCHED_PERFORMANCE.csv',pairs,['program','input_identity_sha256','profile','treatment','S_cycles','F_cycles','speedup_S_over_treatment','treatment_cycle_reduction_fraction','slowdown','S_cohort','F_cohort','pair_key'])
    # Main-controlled bounded review files; neither Source nor any original scientific asset.
    review=ROOT/'review/docs/ep_l2/operations/ep_full_workload_performance_20261027_v1'
    for name in ['CURRENT_STATUS.json','RUN_STATUS.csv','MATCHED_PERFORMANCE.csv']:
        data=(out/name).read_bytes();dest=review/name
        tmp=dest.with_name('.'+name+'.tmp');tmp.write_bytes(data);os.replace(tmp,dest)
    return current


if __name__=='__main__':
    if sys.argv[1:]==['--once']:
        print(json.dumps(report()))
    else:
        with locked(ROOT/'control/UNIFIED_LIVE_REPORT.lock',True):
            deadline=time.monotonic()+24*3600
            while time.monotonic()<deadline and not (ROOT/'control/STOP_LIVE_REPORT').exists():
                try:
                    report()
                except Exception as e:
                    put(ROOT/'control/LIVE_REPORT_HOLD.json',dict(utc=now(),reason=repr(e),no_model_or_authority_mutation=True))
                time.sleep(60)
