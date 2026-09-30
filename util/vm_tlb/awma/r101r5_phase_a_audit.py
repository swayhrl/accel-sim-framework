#!/usr/bin/env python3
"""Offline audit of the immutable accepted R101 L512 NCU report."""
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
OLD = ROOT / 'raw/ncu/L512'
NEW = Path('/data/c16/awma/r101r5_native_post_l1_downstream_20260930')
RAW = NEW / 'raw/phase_a'
REVIEW = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101r5-native-post-l1-downstream-109-v1/docs/vm_tlb/review_packs/AWMA_R101R5_NATIVE_POST_L1_DOWNSTREAM_109_V1')
NCU = '/opt/nvidia/nsight-compute/2025.1.1/ncu'
EXPECTED = {
    'L512.ncu-rep': 'a73f9db4638171b5236194d1541c1943c849714c9671a85e82e5700a1ae403d8',
    'L512.raw.csv': 'fba83ccbc68a7b833a4d645a3d4f4044672337a68a403fe41a43478a712894d5',
    'PROFILE_TARGET_RECEIPT.json': '30e6226256c7d8bdc8e89d90e88493798e67f673ab14173c829890f000a5738d',
}
PAYLOAD_SHA = '1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234'
SOURCE_SHA = 'af89eda9a0176effed99e1fe19cc1f8a1a2c9588'

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def tsv(path, columns, records):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=columns, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(records)

def main():
    RAW.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)
    checked = {}
    for filename, expected in EXPECTED.items():
        actual = sha(OLD / filename)
        assert actual == expected, (filename, actual, expected)
        checked[filename] = actual
    assert sha(ROOT / 'raw/discovery_tiles_T512.pt') == PAYLOAD_SHA
    accepted = json.loads((OLD / 'PROFILE_TARGET_RECEIPT.json').read_text())
    assert accepted['source_commit'] == SOURCE_SHA and accepted['input_payload_sha256'] == PAYLOAD_SHA
    checkout = ROOT / 'source/himuon'
    if checkout.is_dir():
        commit = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
        assert commit == SOURCE_SHA, commit
    for page in ('details', 'session'):
        p = subprocess.run([NCU, '--import', str(OLD / 'L512.ncu-rep'), '--page', page, '--csv'], capture_output=True, text=True)
        (RAW / f'accepted_L512_{page}.csv').write_text(p.stdout)
        (RAW / f'accepted_L512_{page}.stderr.txt').write_text(p.stderr)
        assert p.returncode == 0, (page, p.stderr)
    with (RAW / 'accepted_L512_details.csv').open(newline='') as f:
        details = list(csv.DictReader(f))
    metric_units = sorted({(r['Section Name'], r['Metric Name'], r['Metric Unit']) for r in details})
    assert {x[0] for x in metric_units} == {'Command line profiler metrics'}
    assert {x[1] for x in metric_units} == {
        'dram__bytes_read.sum', 'dram__bytes_write.sum', 'lts__t_bytes.sum',
        'sm__cycles_active.sum', 'sm__warps_active.avg.pct_of_peak_sustained_active'
    }
    tsv(REVIEW / 'EXISTING_METRIC_INVENTORY.tsv', ['section', 'metric', 'unit', 'scope'],
        [dict(zip(['section', 'metric', 'unit'], x), scope='18 accepted launches') for x in metric_units])
    with (OLD / 'L512.raw.csv').open(newline='') as f:
        reader = csv.DictReader(f)
        next(reader)  # units row, not a launch
        rows = list(reader)
    assert len(rows) == 18 and [int(r['ID']) for r in rows] == list(range(18))
    expected_functions = ['XXT_kernel', 'ba_plus_cAA_kernel', 'bmm_add_kernel']
    assert [r['Kernel Name'] for r in rows[3:]] == expected_functions * 5
    targets = []
    for index, family in zip((6, 7, 8), expected_functions):
        r = rows[index]
        grid = '(16, 44, 1)' if family == 'bmm_add_kernel' else '(2816, 1, 1)'
        assert r['Kernel Name'] == family and r['Grid Size'] == grid and r['Block Size'] == '(128, 1, 1)'
        targets.append({
            'target': family, 'recurrence_1based': 2, 'occurrence_0based': 1,
            'accepted_global_launch_id': index, 'exact_function': r['Kernel Name'],
            'grid': r['Grid Size'], 'block': r['Block Size'],
            'context': r['Context'], 'stream': r['Stream'],
            'input_sha256': PAYLOAD_SHA, 'source_commit': SOURCE_SHA,
            'accepted_report_sha256': checked['L512.ncu-rep'],
            'accepted_cubin_sha256': 'NOT_RECORDED_IN_ACCEPTED_RECEIPT',
            'dram_read_mbyte': r['dram__bytes_read.sum'],
            'dram_write_mbyte': r['dram__bytes_write.sum'],
            'l2_requested_mbyte': r['lts__t_bytes.sum'],
            'sm_active_cycles_sum': r['sm__cycles_active.sum'],
            'occupancy_pct': r['sm__warps_active.avg.pct_of_peak_sustained_active'],
        })
    tsv(REVIEW / 'TARGET_BINDING.tsv', list(targets[0]), targets)
    audit = f'''# Existing accepted L512 NCU evidence audit

Phase A is CPU-only. Accepted report, CSV, and receipt SHA256 values were verified exactly against the accepted raw index: `{json.dumps(checked, sort_keys=True)}`. The L512 payload SHA256 is `{PAYLOAD_SHA}`; the receipt pins HiMuon `{SOURCE_SHA}` and five NS steps. Accepted NCU uses cache-control none, clock-control none, dynamic pipeline boost and a natural eager L512 invocation after three warmups.

NCU import contains 18 launches: 3 normalization launches then five ordered repetitions of `XXT_kernel → ba_plus_cAA_kernel → bmm_add_kernel`. The second recurrence is report IDs 6, 7 and 8 respectively. Functions, grid/block, context/stream and traffic are closed in `TARGET_BINDING.tsv`. The accepted receipt does **not** contain a cubin SHA; this is explicitly an unrecorded binding, not a guessed one.

Report sections: **Command line profiler metrics only**. Five explicitly requested counters are listed in `EXISTING_METRIC_INVENTORY.tsv`: DRAM read/write bytes, L2 requested bytes, SM active cycles, and active-warp occupancy. The raw report also carries passive launch/device attributes (grid, block, registers, shared memory, replay-pass count); those are not additional requested issue counters. Installed NCU version is 2025.1.1; the accepted report targets RTX4080 SM89 / CUDA 13.0 as exported by the report.

The accepted report has **no** warp issue/stall composition, no eligible-warp issue state, no L1/TEX global load/store request counters, no direct LDG/ST/LDGSTS dynamic instruction counts, and no SourceCounters or per-PC sampled attribution. These cannot be inferred from high L2 traffic. Source/cubin identity is pinned at the HiMuon source commit and accepted runtime receipt level, but exact cubin SHA was not preserved.

**Phase A decision: Phase B required.** Core issue/stall evidence is absent; this is the specific scientific gap. Do not interpret the old NCU traffic as proof of downstream pressure. The accepted numerical/launch authority remains frozen.
'''
    (REVIEW / 'EXISTING_NCU_AUDIT.md').write_text(audit)
    decision = {'phase_a': 'CORE_ISSUE_STALL_EVIDENCE_MISSING', 'phase_b_required': True,
                'accepted_hashes': checked, 'target_launch_ids': [6,7,8],
                'new_gpu_activity_so_far': False}
    (RAW / 'PHASE_A_DECISION.json').write_text(json.dumps(decision, indent=2, sort_keys=True) + '\n')
    print(json.dumps(decision, sort_keys=True))

if __name__ == '__main__': main()
