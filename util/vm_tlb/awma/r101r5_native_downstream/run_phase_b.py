#!/usr/bin/env python3
"""Run exactly three pre-registered L512 NCU jobs under external flock."""
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ACCEPTED = Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
NEW = Path('/data/c16/awma/r101r5_native_post_l1_downstream_20260930')
RAW = NEW / 'raw/phase_b'
WT = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101r5-native-post-l1-downstream-109-v1')
REVIEW = WT / 'docs/vm_tlb/review_packs/AWMA_R101R5_NATIVE_POST_L1_DOWNSTREAM_109_V1'
NCU = '/opt/nvidia/nsight-compute/2025.1.1/ncu'
SOURCE_SHA = 'af89eda9a0176effed99e1fe19cc1f8a1a2c9588'
INPUT_SHA = '1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234'

STALL_SUFFIXES = (
    'barrier', 'branch_resolving', 'dispatch_stall', 'drain', 'imc_miss',
    'lg_throttle', 'long_scoreboard', 'long_scoreboard_pipe_l1tex',
    'math_pipe_throttle', 'membar', 'mio_throttle', 'misc',
    'no_instruction', 'not_selected', 'selected', 'short_scoreboard',
    'sleeping', 'tex_throttle', 'wait',
)
CORE = [f'smsp__warp_issue_stalled_{x}_per_warp_active.pct' for x in STALL_SUFFIXES] + [
    'smsp__warps_eligible.avg.per_cycle_active',
    'smsp__warps_active.avg.per_cycle_active',
    'sm__sass_inst_executed_op_global_ld.sum',
    'sm__sass_inst_executed_op_global_st.sum',
    'sm__sass_inst_executed_op_ldgsts.sum',
    'l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum',
    'l1tex__t_sectors_pipe_lsu_mem_global_op_st.sum',
    'lts__t_bytes.sum', 'dram__bytes_read.sum', 'dram__bytes_write.sum',
    'sm__cycles_active.sum', 'sm__warps_active.avg.pct_of_peak_sustained_active',
]
TARGETS = (
    ('XXT_kernel', 6, '(2816, 1, 1)'),
    ('ba_plus_cAA_kernel', 7, '(2816, 1, 1)'),
    ('bmm_add_kernel', 8, '(16, 44, 1)'),
)

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def run_capture(cmd, outfile, errfile, env=None):
    with outfile.open('w') as out, errfile.open('w') as err:
        return subprocess.run(cmd, stdout=out, stderr=err, env=env).returncode

def main():
    assert os.environ.get('R101R5_GPU_LOCK_HELD') == '1'
    active = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid,process_name,used_gpu_memory', '--format=csv,noheader'], text=True)
    (RAW / 'compute_apps_at_admission.txt').write_text(active)
    assert not active.strip(), f'conflicting compute apps: {active}'
    assert shutil.disk_usage(RAW).free > 5 * 1024**3
    assert sha(ACCEPTED / 'raw/discovery_tiles_T512.pt') == INPUT_SHA
    source = ACCEPTED / 'source/himuon'
    assert subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip() == SOURCE_SHA
    query = (RAW / 'ncu_metric_query.txt').read_text().splitlines()
    available = {line.split()[0] for line in query if line and line[0].isalpha()}
    sections = (RAW / 'ncu_sections.txt').read_text()
    source_section = 'SourceCounters' in sections
    binding = []
    selected = []
    for metric in CORE:
        found = metric in available
        binding.append({'semantic': metric, 'metric': metric if found else 'COUNTER_UNAVAILABLE',
                        'status': 'SUPPORTED' if found else 'COUNTER_UNAVAILABLE', 'query_sha256': sha(RAW / 'ncu_metric_query.txt')})
        if found:
            selected.append(metric)
    assert any('long_scoreboard' in x for x in selected)
    assert any('lg_throttle' in x for x in selected)
    assert 'sm__sass_inst_executed_op_global_ld.sum' in selected
    with (REVIEW / 'METRIC_BINDING.tsv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(binding[0]), delimiter='\t', lineterminator='\n')
        w.writeheader(); w.writerows(binding)
    (REVIEW / 'NCU_CAPABILITY_QUERY.txt').write_text(
        f'Actual node109 RTX4080/SM89 NCU metric query: {RAW / "ncu_metric_query.txt"}\n'
        f'Metric query SHA256: {sha(RAW / "ncu_metric_query.txt")}\n'
        f'Section listing: {RAW / "ncu_sections.txt"}\n'
        f'Section listing SHA256: {sha(RAW / "ncu_sections.txt")}\n'
        f'SourceCounters listed: {source_section}\n'
        f'Freeze: {len(selected)} supported requested metrics, {len(CORE)-len(selected)} unavailable.\n')
    environment = os.environ.copy()
    environment.update({
        'HF_HOME': str(ACCEPTED / 'cache/hf'), 'TRITON_CACHE_DIR': str(ACCEPTED / 'cache/triton'),
        'CUDA_CACHE_PATH': str(ACCEPTED / 'cache/cuda'),
        'TORCHINDUCTOR_CACHE_DIR': str(ACCEPTED / 'cache/inductor'),
        'XDG_CACHE_HOME': str(ACCEPTED / 'cache/xdg'), 'TMPDIR': str(ACCEPTED / 'tmp'),
        'PYTHONUNBUFFERED': '1',
    })
    command_receipts = []
    for family, accepted_launch, grid in TARGETS:
        stem = RAW / family
        environment['R101R5_TARGET_FAMILY'] = family
        command = [NCU, '--nvtx', '--nvtx-include', 'R101_NCU_L512]',
                   '--devices', '0', '--target-processes', 'application-only',
                   '--kernel-name-base', 'function', '--kernel-name', family,
                   '--launch-skip', '1', '--launch-count', '1',
                   '--cache-control', 'none', '--clock-control', 'none',
                   '--pipeline-boost-state', 'dynamic', '--metrics', ','.join(selected)]
        if source_section:
            command += ['--section', 'SourceCounters']
        command += ['--force-overwrite', '--export', str(stem),
                    str(ACCEPTED / 'env/bin/python'), str(WT / 'util/vm_tlb/awma/r101r5_native_downstream/ncu_target.py')]
        receipt = {'target': family, 'accepted_launch_id': accepted_launch,
                   'occurrence_0based': 1, 'expected_grid': grid, 'expected_block': '(128, 1, 1)',
                   'command': command, 'environment': {k: environment[k] for k in (
                       'HF_HOME','TRITON_CACHE_DIR','CUDA_CACHE_PATH','TORCHINDUCTOR_CACHE_DIR','XDG_CACHE_HOME','TMPDIR')},
                   'source_section_requested': source_section,
                   'input_sha256': INPUT_SHA, 'source_commit': SOURCE_SHA}
        command_receipts.append(receipt)
        (RAW / 'command_receipts.json').write_text(json.dumps(command_receipts, indent=2, sort_keys=True) + '\n')
        print('NCU_JOB_START', family, flush=True)
        rc = run_capture(command, Path(str(stem)+'.stdout.log'), Path(str(stem)+'.stderr.log'), environment)
        receipt['returncode'] = rc
        (RAW / 'command_receipts.json').write_text(json.dumps(command_receipts, indent=2, sort_keys=True) + '\n')
        if rc:
            raise SystemExit(f'NCU job {family} failed rc={rc}; no retry performed')
        report = Path(str(stem)+'.ncu-rep')
        assert report.is_file()
        for page in ('raw', 'details', 'source'):
            out = Path(str(stem)+f'.{page}.csv')
            err = Path(str(stem)+f'.{page}.stderr.txt')
            p = subprocess.run([NCU, '--import', str(report), '--page', page, '--csv'], capture_output=True, text=True)
            out.write_text(p.stdout); err.write_text(p.stderr)
            receipt[f'{page}_import_returncode'] = p.returncode
        with Path(str(stem)+'.raw.csv').open(newline='') as f:
            reader = csv.DictReader(f); next(reader)
            rows = list(reader)
        assert len(rows) == 1, (family, len(rows))
        row = rows[0]
        assert row['Kernel Name'] == family and row['Grid Size'] == grid and row['Block Size'] == '(128, 1, 1)', row
        receipt.update({'actual_kernel': row['Kernel Name'], 'actual_grid': row['Grid Size'],
                        'actual_block': row['Block Size'], 'report_sha256': sha(report),
                        'replayer_passes': row.get('profiler__replayer_passes', 'UNAVAILABLE')})
        (RAW / 'command_receipts.json').write_text(json.dumps(command_receipts, indent=2, sort_keys=True) + '\n')
        print('NCU_JOB_COMPLETE', family, receipt['replayer_passes'], flush=True)
    print('PHASE_B_COMPLETE', flush=True)

if __name__ == '__main__': main()
