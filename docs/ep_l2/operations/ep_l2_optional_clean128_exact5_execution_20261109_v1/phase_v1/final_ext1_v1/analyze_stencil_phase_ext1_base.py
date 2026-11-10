#!/usr/bin/env python3
"""Read only, bounded analysis of two accepted Stencil result streams.

Reads each accepted gzip raw stream once. Never touches trace bodies or Source.
Kernel-scope B0/M0 rows are deltas; TVDV2/TVDX1 rows are cumulative snapshots.
"""
import collections
import csv
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
REG = Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
GOAL = 'EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1'
CASES = {i: f'EP_PERF_CLEAN128_STENCIL_WV_EXT{i}_20261109_V1' for i in (0, 2)}
OUT = Path(__file__).resolve().parent

B0_KEYS = ('bank_wait_cycles', 'block_payload', 'block_bank',
           'c7e_dram_successful_read_issues', 'c7e_dram_successful_read_bytes',
           'c7e_dram_successful_write_issues',
           'c7d_payload_capacity_allocation_denial', 'c7d_payload_service_port_denial')
M0_KEYS = ('m0_frontend_head_observed_cycles', 'm0_frontend_head_any_blocked_cycles',
           'm0_frontend_head_blocked_cycles_payload_capacity',
           'm0_frontend_head_blocked_cycles_payload_service')
SNAP_KEYS = {
    'EPL2TVDV2|SUMMARY|': ('read_responses', 'directory_queries', 'lookup_wait_cycles',
                            'clean_installs', 'dirty_installs'),
    'EPL2TVDX1|SEGMENT|': ('ext_queries', 'selector_reads', 'spills', 'fallback',
                            'base_replays', 'ext_write_grants'),
    'EPL2TVDX1|CONTROL|': ('ext_indexed_reads', 'ext_read_responses',
                            'ext_clean_installs', 'ext_served_sector_bytes'),
}


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def fields(line):
    return dict(part.split('=', 1) for part in line.rstrip().split('|') if '=' in part)


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def read_case(ext, registry):
    case = CASES[ext]
    row = registry['registered_future_requests'][GOAL]['consumed'][case]
    require(row['state'] == 'CLOSED_ACCEPTED', f'{case}: not closed accepted')
    done_path = Path(row['done_ref']['path'])
    require(sha(done_path) == row['done_ref']['sha256'], f'{case}: DONE ref SHA')
    done = json.loads(done_path.read_text())
    run = Path(done['output'])
    require(run.is_relative_to(ROOT / 'cases' / case / 'run'), f'{case}: output scope')
    raw = run / 'raw.log.gz'
    require(sha(raw) == done['raw_compressed_ref']['sha256'], f'{case}: compressed raw SHA')
    bundle_path = run / 'VALIDATED_APPLICATION_BUNDLE.json'
    bundle = json.loads(bundle_path.read_text())
    require(bundle['application']['kernel_count'] == 100, f'{case}: kernel population')
    require(len(bundle['application']['ordered_kernel_catalog']) == 100, f'{case}: kernel catalog')
    require(bundle['application']['actual_options']['-gpgpu_ep_l2_victim_extension'] == str(ext), f'{case}: mode')

    cycles, total_cycles, uids = [], [], []
    b0 = collections.defaultdict(collections.Counter)
    m0 = collections.defaultdict(collections.Counter)
    counts = collections.Counter()
    seen_b0 = collections.defaultdict(set)
    seen_m0 = collections.defaultdict(set)
    snaps = {kind: collections.defaultdict(list) for kind in SNAP_KEYS}
    with gzip.open(raw, 'rt', errors='strict') as stream:
        for line in stream:
            counts['raw_lines'] += 1
            if line.startswith('gpu_sim_cycle = '):
                m = re.fullmatch(r'gpu_sim_cycle\s*=\s*(\d+)\s*', line)
                require(m is not None, f'{case}: malformed gpu_sim_cycle')
                cycles.append(int(m.group(1)))
            elif line.startswith('gpu_tot_sim_cycle = '):
                m = re.fullmatch(r'gpu_tot_sim_cycle\s*=\s*(\d+)\s*', line)
                require(m is not None, f'{case}: malformed gpu_tot_sim_cycle')
                total_cycles.append(int(m.group(1)))
            elif line.startswith('kernel_launch_uid = '):
                m = re.fullmatch(r'kernel_launch_uid\s*=\s*(\d+)\s*', line)
                if m:
                    uids.append(int(m.group(1)))
            elif line.startswith('EPL2B0V1|scope=kernel|interval=kernel_shared_delta|'):
                d = fields(line)
                uid = int(d['kernel_uid'])
                require(1 <= uid <= 100, f'{case}: B0 UID')
                slice_id = int(d['slice'])
                require(0 <= slice_id < 64 and slice_id not in seen_b0[uid],
                        f'{case}: duplicate/invalid B0 slice for UID {uid}')
                seen_b0[uid].add(slice_id)
                counts[('B0', uid)] += 1
                for key in B0_KEYS:
                    b0[uid][key] += int(d[key])
            elif line.startswith('EPL2M0AV1|scope=kernel|interval=kernel_shared_delta|'):
                d = fields(line)
                uid = int(d['kernel_uid'])
                require(1 <= uid <= 100, f'{case}: M0 UID')
                slice_id = int(d['slice'])
                require(0 <= slice_id < 64 and slice_id not in seen_m0[uid],
                        f'{case}: duplicate/invalid M0 slice for UID {uid}')
                seen_m0[uid].add(slice_id)
                counts[('M0', uid)] += 1
                for key in M0_KEYS:
                    m0[uid][key] += int(d[key])
            else:
                for kind, keys in SNAP_KEYS.items():
                    if line.startswith(kind):
                        d = fields(line)
                        s = int(d['slice'])
                        require(0 <= s < 64, f'{case}: snapshot slice')
                        if kind == 'EPL2TVDX1|SEGMENT|':
                            require(int(d['mode']) == ext and int(d['base_capacity']) == 128
                                    and int(d['ext_capacity']) == 128,
                                    f'{case}: segment identity')
                        snaps[kind][s].append({k: int(d[k]) for k in keys})
                        break

    require(uids == list(range(1, 101)), f'{case}: 100 ordered UIDs')
    require(len(cycles) == len(total_cycles) == 101 and cycles[-1] == 0,
            f'{case}: kernel and terminal cycle population')
    require(total_cycles[-1] == bundle['cycles'] and sum(cycles[:100]) + 106 == bundle['cycles'],
            f'{case}: cycle conservation')
    require(all(counts[('B0', u)] == counts[('M0', u)] == 64 for u in uids),
            f'{case}: 64 kernel-scope slice rows')
    for kind, per_slice in snaps.items():
        if ext == 0 and 'TVDX1' in kind:
            require(not per_slice, f'{case}: unexpected extension records')
        else:
            require(set(per_slice) == set(range(64)) and
                    all(len(per_slice[s]) == 101 for s in range(64)),
                    f'{case}: {kind} snapshot population')

    def snapshot(kind, key, index):
        if not snaps[kind]:
            return 0
        return sum(snaps[kind][s][index][key] for s in range(64))

    kernel_rows = []
    for i, uid in enumerate(uids):
        v = dict(uid=uid, cycles=cycles[i], total_cycles=total_cycles[i],
                 **dict(b0[uid]), **dict(m0[uid]))
        for kind, keys in SNAP_KEYS.items():
            for key in keys:
                new = snapshot(kind, key, i)
                old = snapshot(kind, key, i - 1) if i else 0
                require(new >= old, f'{case}: {key} non-monotonic')
                v[key] = new - old
        kernel_rows.append(v)

    local = bundle['model']['mechanism_metrics']['local_service']
    require(sum(v['c7e_dram_successful_read_issues'] for v in kernel_rows) == local['lower_reads'],
            f'{case}: lower read issues disagree with accepted bundle')
    require(sum(v['c7e_dram_successful_read_bytes'] for v in kernel_rows) == local['lower_read_bytes'],
            f'{case}: lower read bytes disagree with accepted bundle')
    require(sum(v['read_responses'] for v in kernel_rows) ==
            sum(v['base_raw_summary']['read_responses'] for v in bundle['segment_cost']['rows']),
            f'{case}: base response conservation')
    require(sum(v['ext_read_responses'] for v in kernel_rows) ==
            sum((v['extension_raw_control'] or {}).get('ext_read_responses', 0)
                for v in bundle['segment_cost']['rows']),
            f'{case}: extension response conservation')
    for kind, keys in SNAP_KEYS.items():
        for key in keys:
            require(snapshot(kind, key, 99) == snapshot(kind, key, 100),
                    f'{case}: terminal snapshot changed {key}')
    return dict(case=case, uuid=row['uuid'], raw_stored_sha256=sha(raw),
                accepted_bundle_sha256=sha(bundle_path), source_identity=bundle['source_identity'],
                input_identity_sha256=bundle['input_identity_sha256'],
                actual_options=bundle['application']['actual_options'],
                total_cycles=bundle['cycles'], kernel_cycles_sum=sum(cycles[:100]),
                post_kernel_cycles=bundle['cycles'] - sum(cycles[:100]),
                rows=kernel_rows)


def main():
    registry = json.loads(REG.read_text())
    cases = {ext: read_case(ext, registry) for ext in CASES}
    a, b = cases[0], cases[2]
    require(a['source_identity'] == b['source_identity'] and
            a['input_identity_sha256'] == b['input_identity_sha256'], 'cross-point identity')
    opts_a, opts_b = a['actual_options'], b['actual_options']
    require(set(opts_a) == set(opts_b) and len(opts_a) == 283 and
            [key for key in opts_a if opts_a[key] != opts_b[key]] ==
            ['-gpgpu_ep_l2_victim_extension'], 'actual option delta')

    keys = [k for k in a['rows'][0] if k not in ('uid', 'total_cycles')]
    rows = []
    for i in range(100):
        x, y = a['rows'][i], b['rows'][i]
        require(x['uid'] == y['uid'] == i + 1, 'paired UID')
        row = {'uid': i + 1, 'ext0_cycles': x['cycles'], 'ext2_cycles': y['cycles'],
               'delta_cycles': y['cycles'] - x['cycles']}
        for k in keys:
            if k != 'cycles':
                row[f'ext0_{k}'], row[f'ext2_{k}'] = x[k], y[k]
        rows.append(row)
    require(sum(v['delta_cycles'] for v in rows) == b['total_cycles'] - a['total_cycles'],
            'paired cycle delta conservation')

    evidence = dict(schema='EP_L2_STENCIL_EXACT5_PHASE_READONLY_V1',
                    population='100 paired sequential kernels, 64 slice records each',
                    source_identity=a['source_identity'], input_identity_sha256=a['input_identity_sha256'],
                    actual_option_count=283, actual_option_delta='-gpgpu_ep_l2_victim_extension: 0 -> 2',
                    points={str(k): {p: v for p, v in c.items() if p not in ('rows', 'actual_options')}
                            for k, c in cases.items()},
                    definitions={'cycles': 'gpu_sim_cycle per kernel; final 106-cycle post-kernel tail included only in application total',
                                 'B0_M0': 'kernel_shared_delta summed over 64 slices; blocked observations are not disjoint GPU cycles',
                                 'TVDV2_TVDX1': 'per-slice cumulative snapshots differenced between consecutive kernel ends; final snapshot duplicates kernel100',
                                 'lower_reads': 'c7e_dram_successful_read_issues; validated against accepted local_service',
                                 'response': 'retained sector responses, not avoided DRAM requests'},
                    rows=rows)
    (OUT / 'PHASE_EVIDENCE.json').write_text(json.dumps(evidence, indent=2, sort_keys=True) + '\n')
    with (OUT / 'PHASE_ROWS.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    print(json.dumps(dict(status='PASS', rows=len(rows), output=str(OUT),
                          cycle_delta=sum(v['delta_cycles'] for v in rows),
                          lower_read_delta=sum(v['ext2_c7e_dram_successful_read_issues'] -
                                               v['ext0_c7e_dram_successful_read_issues'] for v in rows),
                          ext_responses=sum(v['ext2_ext_read_responses'] for v in rows))))


if __name__ == '__main__':
    main()
