#!/usr/bin/env python3
"""Bounded metadata/S-only opportunity analysis. No trace or F result reads.

Exact read paths and byte hashes are recorded. Historical B0 observations stay
separate from current main61 S. No cross-source performance comparison or RO
qualification is performed. Requires existing worktrees; never starts simulator.
"""
import argparse
import csv
import datetime
import hashlib
import io
import json
import os
import resource
import signal
import subprocess
import time
from pathlib import Path

CURRENT = 'd010911e3174a3764791183cd108fe4664ba8731'
PRIOR = '27ec10bda848e4929181c60a7cbb40d6b007945c'
WORKLOADS = ['convolutionSeparable', 'vectorAdd_4M', 'cfd_097k', 'dwt2d',
             'sad', 'FWT_7_21', 'sgemm', 'btree', 'scan', 'spmv']
FIELDS = ['line_mshr_avg', 'line_mshr_p95', 'line_mshr_max', 'line_mshr_full_block',
          'tag_set_all_reserved_block', 'descriptor_avg', 'descriptor_max',
          'descriptor_pool_full_block', 'per_address_cap_block', 'wad_avg',
          'wad_full_events', 'resident_pending_sector_avg', 'resident_dirty_avg',
          'scheduler_causal_block']


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    started = time.monotonic()
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024**2, 256 * 1024**2))
    resource.setrlimit(resource.RLIMIT_CPU, (20, 20))
    signal.alarm(60)
    audit, total = [], 0
    sha = lambda b: hashlib.sha256(b).hexdigest()

    def read(path):
        nonlocal total
        path = Path(path)
        # Only metadata, fixed B0 CSV and the one explicitly allowed S log.
        assert path.suffix not in ('.trace', '.traceg', '.sqlite3', '.gz')
        assert not any(x.startswith('E0') and x not in ('E010_1108e4d2',)
                       for x in path.parts)
        assert path.stat().st_size <= 16 * 1024**2
        b = path.read_bytes()
        total += len(b)
        assert total <= 64 * 1024**2
        audit.append(dict(path=str(path), bytes=len(b), sha256=sha(b)))
        return b

    def js(path):
        return json.loads(read(path))

    def git(commit, path):
        repo = '/workspace/worktrees/gpgpu-sim-ep-l2-ms20261019-c-ro-v1'
        b = subprocess.check_output(['git', '-C', repo, 'show', commit + ':' + path])
        audit.append(dict(git_repository=repo, commit=commit, path=path,
                          bytes=len(b), sha256=sha(b)))
        return b

    droot = Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-d-analysis-v1')
    d = droot / 'docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d'
    b0 = Path('/workspace/worktrees/accel-sim-ep-l2-c7e/docs/ep_l2/target_baseline_results_final_850')
    reg = js('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')['mechanism_study_20261019_v1']
    # Registry used for identity/status routing only. No accepted-pair endpoint,
    # F cycles, F counters, F terminal, or F raw log is consumed by analysis.
    core_proof = {}
    for path in ['src/gpgpu-sim/ep-l2-ro-transactions.h',
                 'src/gpgpu-sim/ep-l2-ro-runtime.inc', 'src/gpgpu-sim/ep-l2-ro-store-port.h']:
        old, new = git(PRIOR, path), git(CURRENT, path)
        assert old == new
        core_proof[path] = dict(sha256=sha(new), unchanged_from_Core27=True)
    old_l2, new_l2 = git(PRIOR, 'src/gpgpu-sim/l2cache.cc'), git(CURRENT, 'src/gpgpu-sim/l2cache.cc')
    assert old_l2 == new_l2
    core_proof['src/gpgpu-sim/l2cache.cc'] = dict(sha256=sha(new_l2), unchanged_from_Core27=True)
    tx = git(CURRENT, 'src/gpgpu-sim/ep-l2-ro-transactions.h').decode()
    assert 'e.required |= mask; e.reuse_seen = true;' in tx
    assert '!e.reuse_seen' in tx
    assert 'e = entry(); e.live = e.attached = true;' in tx
    historical = {}
    comparison = list(csv.DictReader(io.StringIO(read(b0/'target_baseline_comparison.csv').decode())))
    for w in WORKLOADS:
        r = next(r for r in comparison if r['workload'] == w)
        rows = list(csv.DictReader(io.StringIO(read(b0/'B0-Legacy'/w/'target_kernel.csv').decode())))
        historical[w] = dict(variant='B0-Legacy',
            source_Core='ece1a3a77c5628763e0a4605bfd1c639ee6a1495',
            source_Framework='f08d2ce857972fad73c4e1ab7162ba94c6336507',
            counters={k:float(r['legacy_'+k]) for k in FIELDS},
            same_set_reserved_Tag_max=max(int(r['c7d_reserved_set_max']) for r in rows),
            kernel_slice_rows=len(rows), qualification='HISTORICAL_STRUCTURAL_CONTEXT_ONLY')
    offline = {}
    for path in sorted((d/'full_system_v2/readonly_evidence').glob('*/CANDIDATE.json')):
        c = js(path)
        manifest_bytes = read(c['manifest'])
        assert sha(manifest_bytes) == c['manifest_sha256']
        manifest = json.loads(manifest_bytes)
        assert manifest['epoch'] == 'whole_commandlist'
        assert c['trace_content_sha256'] == c['expected_trace_content_sha256']
        counts = c['counts']
        all_reads = sum(v for k, v in counts.items() if k.endswith('_read_lane_references'))
        read_ro = counts.get('CERTIFIED_RO_read_lane_references', 0)
        oracle_review = next((v for k,v in reg['input_oracle_reviews'].items()
                              if k.endswith('_'+path.parent.name)), None)
        if oracle_review:
            rb = read(oracle_review['path'])
            assert sha(rb) == oracle_review['sha256']
        offline[path.parent.name] = dict(
            trace_content_sha256=c['trace_content_sha256'], manifest_sha256=c['manifest_sha256'],
            manifest_epoch=manifest['epoch'], scope=c['scope'], counts=counts,
            readonly_lines=counts.get('CERTIFIED_RO_lines',0),
            readonly_read_lane_references=read_ro,all_global_read_lane_references=all_reads,
            readonly_read_lane_fraction=(read_ro/all_reads if all_reads else None),
            kernel_count=c['kernel_count'], E_artifact_review=oracle_review,
            range_sha256=manifest['artifacts']['certified_ranges.csv'],
            current_qualification='INPUT_MODEL_ONLY_NOT_NATIVE_RO_USE',
            override='INPUT_SCOPE_HOLD_NOT_RO_USABLE' if path.parent.name=='btree' else None,
            runtime_intersection='UNKNOWN_NOT_INFERRED_FROM_OFFLINE_COVERAGE')
    sdir = Path('/workspace/ep_l2_ms20261019_e_results/E010_1108e4d2')
    s = js(sdir/'run_status.json')
    assert s['profile'] == 'S' and s['status'] == 'COMPLETE_VALID'
    assert s['identity']['core_source_commit'] == CURRENT
    assert not s['identity']['feature_vector']['ro_tag_detach']
    assert not s['identity']['feature_vector']['ro_line_mshr_bypass']
    log = read(sdir/'raw.log')
    assert sha(log) == s['raw_log_sha256']
    final, observer = {}, {}
    for line in log.decode().splitlines():
        if line.startswith(('EPL2B0V1|scope=application|', 'EPL2MSV1|OBSERVER|')):
            fields = dict(part.split('=',1) for part in line.split('|')[1:] if '=' in part)
            dest = final if line.startswith('EPL2B0V1') else observer
            dest[int(fields['slice'])] = fields
    assert len(final) == len(observer) == 64
    # Last snapshot per slice only; the log contains multiple cumulative dumps.
    current_resource = dict(
        slices=64, final_snapshot_selection='LAST_APPLICATION_CUMULATIVE_RECORD_PER_SLICE',
        line_mshr_max=max(int(v['line_mshr_max']) for v in final.values()),
        descriptor_max=max(int(v['descriptor_max']) for v in final.values()),
        pending_Tag_max=max(int(v['c7d_reserved_max']) for v in final.values()),
        same_set_reserved_Tag_max=max(int(v['c7d_reserved_set_max']) for v in final.values()),
        Tag_set_all_pending_block_observations=sum(int(v['c7d_tag_set_all_reserved_block']) for v in final.values()),
        line_mshr_full_refusal_observations=sum(int(v['c7d_line_mshr_full_block']) for v in final.values()),
        descriptor_full_refusal_observations=sum(int(v['c7d_descriptor_pool_full_block']) for v in final.values()),
        wb_peak=max(int(v['wb_peak']) for v in observer.values()),
        unclassified_refusal_observations=sum(int(v['unclassified_refusal_observations']) for v in observer.values()))
    waits = {k:{f:v[f] for f in ['distinct_requests_first_block',
        'blocked_observations_over_slices','request_wait_cycle_sum','request_wait_max',
        'resolved_first_waits','unknown_while_unresolved']}
        for k,v in s['mechanism_metrics']['bottleneck'].items()}
    current = dict(attempt_id=s['attempt_id'],profile='S',status=s['status'],
        source_identity=s['source_identity'],identity=s['identity'],
        raw_log_sha256=s['raw_log_sha256'],resources=current_resource,waits=waits,
        local_service=s['mechanism_metrics']['local_service'],
        copy_counts=s['mechanism_metrics']['trigger'],
        interpretation='Nonexclusive request waits/slice observations; no saved GPU cycles or F comparison',
        actual_RO_admissions=0,successful_detach=0,avoided_line_allocations=0,
        zero_reason='T/M_DISABLED_BY_S_CONFIG; not a zero-opportunity conclusion',
        RO_ON_workload_admissions_detach_M_avoided_and_parent_sector_mix='UNKNOWN_NOT_READ_FROM_F')
    report=dict(schema='C_TM_EXISTING_INPUT_OPPORTUNITY_AUDIT_V1',
        UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        current_Core=CURRENT,core_identity_proof=core_proof,
        offline_coverage=offline,historical_B0_pressure=historical,current_Conv_S=current,
        current_registry_state_only=dict(actual_starts=reg['actual_starts'],cap=reg['maximum_actual_starts'],
            producer=reg['official_producer_current'],input_scope_holds=reg['input_scope_holds']),
        no_F_performance_or_counter_files_read=True,no_new_trace_reads=True,
        no_SQLite_scan=True,no_simulation=True,no_build=True,
        reads=audit,read_bytes=total,elapsed_seconds=time.monotonic()-started,
        raw_ru_maxrss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
        process_memory_status={k:int(v.split()[0])*1024 for k,v in
            (line.split(':',1) for line in Path('/proc/self/status').read_text().splitlines()
             if line.startswith(('VmRSS:', 'VmHWM:', 'VmPeak:')))},
        memory_interpretation='ru_maxrss may retain pre-exec launcher high-water; '
            'use current process /proc VmHWM plus enforced AS cap, not ru_maxrss as phase RSS',
        bound=dict(single_CPU_process=True,AS_bytes=256*1024**2,CPU_seconds=20,
                   wall_seconds=60,read_bytes=64*1024**2,max_single_file_bytes=16*1024**2))
    payload=(json.dumps(report,indent=2)+'\n').encode()
    assert len(payload) < 1024**2
    with a.output.open('xb') as f:
        f.write(payload)
    print(json.dumps(dict(read_bytes=total,wall_seconds=report['elapsed_seconds'],
        memory=report['process_memory_status'],current_S=current_resource,
        offline_RO_lines={w:v['readonly_lines'] for w,v in offline.items()}),indent=2))


if __name__ == '__main__':
    main()
