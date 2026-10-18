"""Read-only terminal evidence extraction. Does not repair or rerun anything."""
from common import *
from collections import deque


def main():
    run=RAW/'attempts/BASE_Gaussian_dda83076-bfa4-4b70-bfa3-0d4d9c90cd51'
    terminal=json.loads((RAW/'COHORT_TERMINAL.json').read_text())
    if terminal['status']!='STOP':raise ValueError('NOT_THE_STOPPED_COHORT')
    last=None
    for line in (run/'RESOURCE_MONITOR.jsonl').open():last=json.loads(line)
    unknown=last['authority']['unknown_controls']
    if len(unknown)!=1:raise ValueError('EXPECTED_ONE_OBSERVED_UNKNOWN_CONTROL')
    candidate=unknown[0]['pid'];root=4035496
    observed=[p for p in last['snapshot']['processes'] if p['pid'] in (candidate,root)]
    events=deque(maxlen=8);candidate_events=[]
    for line in (run/'ENGINE/MAP_EVENTS.jsonl').open():
        row=json.loads(line);events.append(row)
        if any(row.get(k)==candidate for k in ('pid','parent_pid','new_owned_pid','quarantined_wait_pid')):candidate_events.append(row)
    with (run/'simulator.stdout').open(errors='replace') as f:
        headers=sum(line.startswith('kernel_name = ') for line in f)
    engine=json.loads((run/'ENGINE/TERMINAL.json').read_text())
    receipt=dict(status='STOP_AUTHORITY_CLASSIFICATION_NOT_COMPLETE_GAUSSIAN',utc=now(),
        actual_registered_main_starts=2,reserved_points=6,full_strict_passes=1,
        first_BASE_GEMM_cycles=1071405,Gaussian_cycles='UNAVAILABLE',all_optimization_ratios='UNAVAILABLE',
        Gaussian_observed_kernel_headers_nonperformance=headers,Gaussian_expected_kernels=510,
        forced_reason=engine['forced_reason'],engine_status=engine['status'],
        Gaussian_wall_seconds_nonperformance=engine['wall_seconds_nonperformance'],
        stop_sample_utc=last['snapshot']['utc'],stop_sample_resource_decision=last['decision'],
        authority_checks=last['authority']['checks'],unknown_controls=unknown,observed_processes=observed,
        candidate_map_or_parent_event_records=candidate_events,preceding_map_events=list(events),
        inference='Likely a transient pre-exec reader-helper descendant: direct PPID, inherited image/argv, trace-stop, zero CPU and IO. Its intended exec image and ptrace parent-fork event were NOT captured; no retrospective identity acceptance.',
        source_boundary='review_authority accepts only owner child_pid/start_ticks as the own simulator; guarded_process invokes observer before draining pending wait events and does not supply its owned/quarantined descendant set to authority review.',
        resource_stop=False,unregistered_new_external_DTC_dispatcher_proven=False,
        Gaussian_performance_accepted=False,Gaussian_BASE_calibration='NOT_REACHED',
        AE_AD_launched=False,no_retry=True,no_replacement=True,no_new_attempt_budget=True,
        frozen_runtime_authority_and_runner_patched=False,
        process_cleanup_checks=[dict(pid=pid,present=(Path('/proc')/str(pid)).exists()) for pid in (3945634,root,candidate)],
        final_wait4_rusage='UNAVAILABLE',
        raw_bindings={name:dict(path=str(run/name),sha256=sha(run/name)) for name in ['STRICT.json','RUN_TERMINAL.json','ENGINE/TERMINAL.json','ENGINE/MAP_EVENTS.jsonl','RESOURCE_MONITOR.jsonl','FILES_SHA256.tsv']})
    write(PACK/'STOP_EVIDENCE.json',receipt)
    print(json.dumps({k:receipt[k] for k in ['status','actual_registered_main_starts','full_strict_passes','Gaussian_observed_kernel_headers_nonperformance','forced_reason','process_cleanup_checks']}))


if __name__=='__main__':main()
