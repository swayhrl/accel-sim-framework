"""Freeze typed denominators, counter availability and the held execution design."""
from common import *


def main():
    base='ccf208c723f44387160c0edfe9e4d56855dfbafd'
    path='docs/dtc_l1/review_packs/DTC_LANE_Z_FLUSH_MECHANISM_V1/METRIC_DEFINITIONS.tsv'
    provenance=copy_blob(FW_REPO,base,path,PACK/'inputs/Z2/BASELINE_TYPED_METRIC_DEFINITIONS.tsv')
    baseline=list(csv.DictReader((PACK/'inputs/Z2/BASELINE_TYPED_METRIC_DEFINITIONS.tsv').open(),delimiter='\t'))
    dictionary=[]
    for r in baseline:
        dictionary.append(dict(field=r['field'],typed_unit=r['typed_unit'],numerator=r['numerator'],
          denominator=r['denominator'],stage=r['logging_stage'],scope=r['per_kernel_or_whole'],
          availability_K0='NO_NEW_RUN',availability_K1='NO_NEW_RUN',
          definition_binding='Z_V1_TYPED_UNIT_PROVENANCE_PLUS_Z2_SOURCE_REQUEST_TIME_CONTRACT',
          definition=r['explanation'],missing_policy='UNAVAILABLE_NOT_ZERO; UNCOMPARABLE_FOR_WRONG_POPULATION; UNDEFINED_ZERO_DENOMINATOR'))
    header=blob(CORE_REPO,CANDIDATE_CORE,'src/gpgpu-sim/dtc-l1-invalidation.h').decode()
    event_fields=[('requests','source requests','1','Every actual LDST invalidate request; repeated idle calls counted'),
      ('idle','source requests','1','IDLE_CLUSTER origin under original predicate'),
      ('membar','source requests','1','MEMBAR origin under original guard'),
      ('config','source requests','1','CACHE_CONFIG_CHANGE origin'),
      ('unspecified','source requests','1','UNSPECIFIED origin; never assume zero without actual field'),
      ('ordinary_commits','ordinary commit invocations','1','Request-return or pending-to-clear observation, not actual number of ordinary Tag changes'),
      ('changed','invalidated queryable mappings','1','Sum effective lookup-visibility changes'),
      ('retained_at_event','mapping changes with live Ref','1','Changed mapping whose old allocation remains owned'),
      ('reclaimed_at_event','mapping changes reclaimed immediately','1','Changed mapping whose ready Ref0 owner-free physical allocation releases at event'),
      ('no_op_requests','requests','requests','Requests with changed0; report count and optional no-op fraction'),
      ('first_request_cycle','global core cycle','1','UINT64_MAX means UNDEFINED_NO_EVENT, not a real large timestamp'),
      ('last_request_cycle','global core cycle','1','UINT64_MAX means UNDEFINED_NO_EVENT'),
      ('first_ordinary_commit_cycle','global core cycle','1','UINT64_MAX means UNDEFINED_NO_EVENT'),
      ('last_ordinary_commit_cycle','global core cycle','1','UINT64_MAX means UNDEFINED_NO_EVENT'),
      ('pending_first_request','per-SM request sequence','1','0 means no pending coalesced ordinary request range'),
      ('pending_last_request','per-SM request sequence','1','0 means no pending coalesced ordinary request range'),
      ('event_records_omitted','detail records','1','Counts omitted request AND ordinary-commit detail records; not omitted requests alone')]
    for field,unit,den,definition in event_fields:
        assert field+'=%llu' in header,field
        dictionary.append(dict(field='DTC_INVALIDATE_V1_SUMMARY.'+field,typed_unit=unit,numerator=field,
          denominator=den,stage='K1 LDST_SOURCE_REQUEST or ordinary commit observation; print per SM cumulative snapshot',
          scope='Per SM lifetime cumulative; take each SM last terminal summary; never sum kernel snapshots',
          availability_K0='NO_SUMMARY_IN_CANDIDATE_SOURCE_UNAVAILABLE_NOT_ZERO',
          availability_K1='FIELD_EXISTS_NOT_MEASURED_YET',definition_binding=CANDIDATE_CORE,
          definition=definition,missing_policy='UNAVAILABLE_NOT_ZERO; UNDEFINED_NO_EVENT_FOR_TIMESTAMP_SENTINEL'))
    table(PACK/'METRIC_DICTIONARY.tsv',dictionary)
    write(PACK/'METRIC_BINDING.json',dict(baseline_provenance=provenance,
       source_event_counter_Core=CANDIDATE_CORE,source_header_sha256=hashlib.sha256(header.encode()).hexdigest(),
       source_event_phase='LDST source request before existing ordinary request',
       new_event_model_cost='AUTHOR_DECLARED_ZERO_EXTRA_SIMULATED_CYCLES_NOT_HARDWARE_COST_PROOF',
       same_observer_contract_PARITY='HOLD_UNRESOLVED',
       summary_enabled_by=K_OPTION,detailed_limit_option='-gpgpu_dtc_l1_debug_event_limit',
       detailed_limit_frozen=0,summary_counters_not_capped=True,
       K0_missing_event_fields_are_not_zero=True,
       all_four_new_point_values='UNAVAILABLE_NOT_RUN'))
    table(PACK/'TERMINAL_MECHANISM_COMPARISON.tsv',[
       dict(metric=r['field'],typed_unit=r['typed_unit'],denominator=r['denominator'],
          K0_32x4='UNAVAILABLE',K0_64x8='UNAVAILABLE',K1_32x4='UNAVAILABLE',K1_64x8='UNAVAILABLE',
          K_effect='UNAVAILABLE',Tag_effect='UNAVAILABLE',interaction='UNAVAILABLE',
          status='NO_NEW_ACCEPTED_POINTS') for r in dictionary])
    effects=[('K_main_effect','((c-a)+(d-b))/2','core cycles'),
             ('Tag_main_effect','((b-a)+(d-c))/2','core cycles'),
             ('additive_interaction','a+d-b-c','core cycles'),
             ('Q32','c/a','cycle quotient'),('Q64','d/b','cycle quotient'),
             ('T0','b/a','cycle quotient'),('T1','d/c','cycle quotient'),
             ('I','a*d/(b*c)','dimensionless'),('logI','ln(a)+ln(d)-ln(b)-ln(c)','natural log')]
    table(PACK/'FACTORIAL_EFFECTS.tsv',[dict(effect=e,formula=f,unit=u,value='UNAVAILABLE_INCOMPLETE_FACTORIAL',
         a='UNAVAILABLE',b='UNAVAILABLE',c='UNAVAILABLE',d='UNAVAILABLE') for e,f,u in effects])
    write(PACK/'EXECUTION_CONTRACT.json',dict(status='DRAFT_SCIENTIFIC_AND_AUTHORITY_HOLD',
         inherited_total_start_cap=4,AA_V1_starts=0,AA2_starts=0,
         max_parallel=1,parallel2_enabled=False,per_point_timeout_seconds=7200,
         timeout_clock='MONOTONIC_ABSOLUTE_FROM_FIRST_ACTUAL_START_NO_RESET',
         actual_starts_per_uuid_max=1,automatic_retry=False,
         run_order=[p[0] for p in POINTS],K1_requires_both_new_K0_strict_exact_cycles=True,
         calibration_cycles=dict(K0_32x4=3798174,K0_64x8=3278356),
         admission=dict(host_MemAvailable_min_gib=32,cgroup_headroom_min_gib=32,disk_free_min_gib=10,
              memory_full_PSI_avg10_max=1,IO_full_PSI_avg10_max=25,probe_seconds=10,
              swap_page_delta_max=0,oom_delta_max=0,foreign_DTC_authorities_allowed=0,
              unknown_control_helpers_allowed=0,old_lock_holders_allowed=0,
              check_global_proc_locks_AND_foreign_process_fdinfo=True,
              all_external_project_RSS_cgroup_swap_PSI_disk_IO_counted=True),
         monitor_seconds=30,emergency=dict(cgroup_headroom_min_gib=8,disk_free_min_gib=2,
              memory_full_PSI_avg10_max=10,consecutive_samples=3,
              own_PID_start_ticks_bound_process_group_only=True),
         no_other_process_signals=True,no_other_files_deleted=True,no_old_lock_acquisition=True,
         no_old_Goal_restart=True,production_runner='UNAVAILABLE_PENDING_ADMISSION',
         execution_guard_script='scripts/execution_guard.py',
         execution_guard_is_NOT_a_production_runner=True,
         model_value_correctness='UNAVAILABLE',W_address_scan='UNAVAILABLE_ATTRIBUTION_GAP'))
    print('Typed dictionary, formulas and held execution design frozen; no performance values consumed.')


if __name__=='__main__':main()
