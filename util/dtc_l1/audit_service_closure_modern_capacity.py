#!/usr/bin/env python3
"""CPU-only allocation proposal audit. Does not create executable configs or jobs."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--spec-dir', required=True)
    ap.add_argument('--attempt-root', required=True)
    ap.add_argument('--core-root', required=True)
    ap.add_argument('--inventory', required=True)
    ap.add_argument('--output-dir', required=True)
    a = ap.parse_args()
    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    evidence = []
    for spec_path in sorted(Path(a.spec_dir).glob('*.json')):
        s = json.loads(spec_path.read_text())
        starts = [p for p in Path(a.attempt_root).glob('*/RUN_START.json')
                  if json.loads(p.read_text())['spec']['label'] == s['label']]
        assert len(starts) == 1
        run = starts[0].parent
        assert (run/'RUN_TERMINAL.json').exists()
        log = (run/'simulator.stdout').read_text(errors='strict')
        sizes = list(map(int, re.findall(r'Reconfigure L1 cache to (\d+)KB', log)))
        # max_cta prints the architectural result BEFORE its small-grid clamp.
        printed_ctas = list(map(int, re.findall(r'CTA/core = (\d+)', log)))
        assert printed_ctas and set(printed_ctas) == {6}
        assert len(sizes) == len(s['members'])
        for counter in ['L1T_total_cache_accesses', 'L1C_total_cache_accesses']:
            vals = re.findall(r'^\s*'+counter+r'\s*=\s*(\d+)', log, re.M)
            assert vals and int(vals[-1]) == 0
        for ordinal, member in enumerate(s['members']):
            p = Path(member['path'])
            assert p.stat().st_size == member['bytes']
            assert sha(p) == member['sha256']
            header = {}
            coords = set()
            tb_count = 0
            with p.open('rb') as f:
                for line in f:
                    if line.startswith(b'-') and b' = ' in line:
                        key, value = line.decode().strip().split(' = ', 1)
                        header[key] = value
                    elif line.startswith(b'#BEGIN_TB'):
                        tb_count += 1
                    elif line.startswith(b'thread block = '):
                        coord = tuple(map(int, line.decode().split(' = ')[1].split(',')))
                        assert coord not in coords
                        coords.add(coord)
            grid = tuple(map(int, header['-grid dim'].strip('()').split(',')))
            block = tuple(map(int, header['-block dim'].strip('()').split(',')))
            assert len(coords) == tb_count == math.prod(grid)
            assert all(all(0 <= v < dim for v, dim in zip(c, grid)) for c in coords)
            threads = math.prod(block)
            padded = math.ceil(threads/32)*32
            smem = int(header['-shmem'])
            regs = int(header['-nregs'])
            thread_bound = 1536//padded
            reg_bound = 65536//(padded*((regs+3)//4*4)) if regs else 2**32-1
            base_bound = min(thread_bound, reg_bound, 24, 102400//smem if smem else 2**32-1)
            proposed_bound = min(thread_bound, reg_bound, 24, 32768//smem if smem else 2**32-1)
            grid_bound = math.ceil(math.prod(grid)/76)
            base_ctas = min(base_bound, grid_bound)
            proposed_ctas = min(proposed_bound, grid_bound)
            assert base_bound == 6
            assert base_ctas == proposed_ctas
            shared = smem*proposed_ctas
            base_partition = next(x for x in [0,8,16,32,64,100] if shared <= x*1024)
            proposal_partition = next(x for x in [0,8,16,32] if shared <= x*1024)
            assert 128-base_partition == sizes[ordinal]
            conventional = 48-proposal_partition
            assert conventional >= 16
            assert 80+conventional+proposal_partition == 128
            rows.append(dict(workload=s['workload'], ordinal=ordinal+1,
                kernel=header['-kernel name'], member_sha256=member['sha256'],
                grid=header['-grid dim'], block=header['-block dim'],
                complete_unique_trace_ctas=tb_count, smem_per_cta_bytes=smem,
                registers_per_thread=regs, thread_cta_bound=thread_bound,
                register_cta_bound=reg_bound, architectural_cta_bound=base_bound,
                post_grid_cta_cap_baseline=base_ctas, post_grid_cta_cap_proposal=proposed_ctas,
                shared_resident_bytes=shared, baseline_shared_partition_kib=base_partition,
                observed_baseline_l1_kib=sizes[ordinal], proposed_dtc_kib=80,
                proposed_shared_partition_kib=proposal_partition,
                proposed_conventional_kib=conventional,
                proposed_conventional_associativity=conventional*2,
                total_data_shared_kib=128,
                qualification='CPU_ARITHMETIC_AND_BASELINE_LOG_ONLY_NOT_DTC_EXECUTION'))
        for file in [spec_path, run/'RUN_START.json', run/'RUN_TERMINAL.json',
                     run/'VALIDATION.json', run/'simulator.stdout', run/'simulator.stderr',
                     Path(s['trace_list'])]:
            evidence.append(dict(path=str(file),bytes=file.stat().st_size,sha256=sha(file)))
    for relative in ['src/gpgpu-sim/shader.cc', 'src/gpgpu-sim/shader.h',
                     'src/gpgpu-sim/gpu-cache.h', 'src/gpgpu-sim/gpu-sim.cc']:
        p = Path(a.core_root)/relative
        evidence.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
    inventory_rows = []
    with Path(a.inventory).open() as f:
        inventory = list(csv.DictReader(f,delimiter='\t'))
    for r in inventory:
        grid = math.prod(map(int,r['grid'].strip('()').split(',')))
        threads = math.prod(map(int,r['block'].strip('()').split(',')))
        padded = math.ceil(threads/32)*32
        smem = int(r['shared_bytes']); regs = int(r['registers'])
        cap = min(1536//padded,65536//(padded*((regs+3)//4*4)) if regs else 2**32-1,
                  24,102400//smem if smem else 2**32-1,math.ceil(grid/76))
        shared = next(s for s in [0,8,16,32,64,100] if cap*smem <= s*1024)
        l1 = 128-shared
        inventory_rows.append(dict(workload=r['workload'],ordinal=r['ordinal'],kernel=r['kernel'],
            member_sha256=r['actual_sha256'],shared_per_cta_bytes=smem,
            computed_cta_cap=cap,computed_resident_shared_bytes=cap*smem,
            computed_shared_partition_kib=shared,computed_effective_l1_kib=l1,
            proposed_dtc_kib=80,proposed_remaining_conventional_kib=l1-80,
            proposed_total_data_shared_kib=128,
            capacity_arithmetic='FITS' if l1-80>=16 else 'DOES_NOT_FIT_WITH_16K_CONVENTIONAL',
            service_and_execution='NOT_QUALIFIED_MODERN_DTC_HOLD',
            scope='CPU_HEADER_AND_SOURCE_CALCULATION_NOT_MODERN_EXECUTION'))
    evidence.append(dict(path=a.inventory,bytes=Path(a.inventory).stat().st_size,sha256=sha(a.inventory)))
    for name, data in [('ALLOCATION_PROPOSAL_AUDIT_V1.tsv',rows),
                       ('FROZEN629_CAPACITY_CALCULATION_V1.tsv',inventory_rows),
                       ('EVIDENCE_HASHES_V1.tsv',evidence)]:
        with (out/name).open('x') as f:
            w = csv.DictWriter(f, fieldnames=list(data[0]),delimiter='\t',lineterminator='\n')
            w.writeheader(); w.writerows(data)
    (out/'AUDIT_SCOPE.json').write_text(json.dumps(dict(
        status='ARITHMETIC_ONLY_MODERN_DTC_HOLD_PENDING_STORAGE_AND_SERVICE_ORGANIZATION',
        total_data_shared_kib=128, fixed_dtc_kib=80, minimum_conventional_kib=16,
        maximum_shared_kib_for_this_proposal=32,
        original_platform_shared_options_kib=[0,8,16,32,64,100],
        original_platform_shared_per_block_kib=48,
        domain_warning='Do not restrict the platform to this32KiB proposal or silently remove64/100KiB options.',
        assumptions='1536 threads,65536 registers,24 CTAs,76 SMs; frozen geometry and max_cta integer rounding',
        excluded='metadata,reference/waiter/search ports; no equal area claim',
        coverage='all trace CTA coordinates present; not native/source shapes or a steady-state timing proof',
        modern_dtc_launches=0),indent=2)+'\n')
    print(json.dumps(dict(kernels=len(rows),workloads=len({r['workload'] for r in rows}),modern_dtc_launches=0)))


if __name__ == '__main__':
    main()
