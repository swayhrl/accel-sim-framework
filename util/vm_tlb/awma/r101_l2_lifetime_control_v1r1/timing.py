#!/usr/bin/env python3
"""Pre-registered paired/interleaved complete CUDA Graph timing."""
from __future__ import annotations

import csv
import json
import statistics
import time

import torch

from core import ROOT, Discard, capture, load_tiles


def measure(name: str, graph: torch.cuda.CUDAGraph, output: torch.Tensor,
            status: str, rep: int) -> dict:
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    host_start = time.perf_counter_ns()
    start.record()
    graph.replay()
    end.record()
    torch.cuda.synchronize()
    host_end = time.perf_counter_ns()
    assert bool(torch.isfinite(output).all())
    return {
        'arm': name, 'run_status': status, 'rep': rep,
        'complete_graph_gpu_ms': start.elapsed_time(end),
        'host_elapsed_ms_secondary': (host_end - host_start) / 1e6,
        'peak_allocated_bytes': torch.cuda.max_memory_allocated(),
        'output_finite': True,
    }


def main() -> None:
    prereg = json.loads((ROOT / 'PREREGISTRATION.json').read_text())
    assert prereg['repetitions'] == {'canary': 1, 'warmup': 2, 'formal': 7}
    assert json.loads((ROOT / 'SEMANTIC_RECEIPT.json').read_text())['discovery_bitwise_and_liveness_qualified']
    path = json.loads((ROOT / 'NSYS_PATH_QUALIFICATION.json').read_text())
    assert path['K128_PATH_GATE']['b0_d1_exact_nondiscard_name_grid_block_sequence_equal']
    assert path['K512_PATH_GATE']['b0_d1_exact_nondiscard_name_grid_block_sequence_equal']
    discard = Discard()
    records = []
    analysis = {}
    with torch.no_grad():
        for edge in (128, 512):
            shape = 'K128' if edge == 128 else 'L512'
            x = load_tiles('discovery', edge)
            b0_graph, b0 = capture(x, None)
            d1_graph, d1 = capture(x, discard)
            assert torch.equal(b0, d1)
            arms = {
                f'{shape}_B0_GRAPH': (b0_graph, b0),
                f'{shape}_D1_DISCARD_GRAPH': (d1_graph, d1),
            }
            ordered = list(arms)
            for name in ordered:
                records.append(measure(name, *arms[name], 'CANARY', 0))
            for rep in range(2):
                for name in ordered if rep % 2 == 0 else list(reversed(ordered)):
                    records.append(measure(name, *arms[name], 'WARMUP', rep))
            for rep in range(7):
                for name in ordered if rep % 2 == 0 else list(reversed(ordered)):
                    row = measure(name, *arms[name], 'FORMAL', rep)
                    records.append(row)
                    print(json.dumps({'arm': name, 'rep': rep,
                                      'gpu_ms': row['complete_graph_gpu_ms']}), flush=True)
            summaries = {}
            for name in ordered:
                values = [row['complete_graph_gpu_ms'] for row in records
                          if row['arm'] == name and row['run_status'] == 'FORMAL']
                median = statistics.median(values)
                summaries[name] = {
                    'formal_values_ms': values,
                    'median_gpu_ms': median,
                    'max_relative_jitter': max(abs(value - median) for value in values) / median,
                }
            b0_stat, d1_stat = (summaries[name] for name in ordered)
            improvement = (b0_stat['median_gpu_ms'] - d1_stat['median_gpu_ms']) / b0_stat['median_gpu_ms']
            noise = max(b0_stat['max_relative_jitter'], d1_stat['max_relative_jitter'])
            analysis[shape] = {
                'arms': summaries,
                'd1_improvement_fraction': improvement,
                'larger_max_relative_jitter': noise,
                'effect_over_noise': improvement / noise if noise else None,
                'd1_material_speedup': improvement >= 0.05 and improvement > 3 * noise,
                'nsys_discard_kernel_count': path[f'K{edge}_D1']['family_counts']['DISCARD_128B'],
                'nsys_discard_kernel_duration_sum_ms_profiler_only':
                    path[f'K{edge}_D1']['family_kernel_duration_sum_ms_profiler_only']['DISCARD_128B'],
            }
            print(json.dumps({'shape': shape, **analysis[shape]}, sort_keys=True), flush=True)
    with (ROOT / 'TIMING_RESULTS.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(records)
    (ROOT / 'TIMING_ANALYSIS.json').write_text(json.dumps(analysis, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
