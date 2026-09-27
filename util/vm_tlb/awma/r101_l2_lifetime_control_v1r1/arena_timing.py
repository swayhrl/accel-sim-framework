#!/usr/bin/env python3
"""Pre-registered paired A0/D2 graph timing on the same L512 tile map."""
from __future__ import annotations

import csv
import json
import statistics
import time

import torch

from arena import Persistence, capture_arena, make_arena
from core import ROOT, Discard, load_tiles


def measure(name: str, graph: torch.cuda.CUDAGraph, output: torch.Tensor,
            expected: torch.Tensor, policy: Persistence, status: str, rep: int) -> dict:
    policy.reset()  # outside timed replay; isolate prior persisting lines for both arms
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
    assert bool(torch.isfinite(output).all()) and bool(torch.equal(output, expected))
    return {'arm': name, 'run_status': status, 'rep': rep,
            'complete_graph_gpu_ms': start.elapsed_time(end),
            'host_elapsed_ms_secondary': (host_end - host_start) / 1e6,
            'peak_allocated_bytes': torch.cuda.max_memory_allocated(),
            'persisting_reset_before_event': True, 'output_finite': True}


def main() -> None:
    prereg = json.loads((ROOT / 'D2_PERSISTENCE_PREREGISTRATION.json').read_text())
    gate = json.loads((ROOT / 'ARENA_NSYS_PATH_QUALIFICATION.json').read_text())['path_gate']
    assert gate['a0_d2_exact_nondiscard_name_grid_block_sequence_equal']
    assert gate['all_relevant_producer_consumer_nodes_policy_attached_and_readback_verified']
    assert json.loads((ROOT / 'D2_PERSISTENCE_RECEIPT.json').read_text())['output_bitwise_with_A0']
    x = load_tiles('discovery', 512)
    policy = Persistence()
    assert policy.set_limit(prereg['set_aside_requested_bytes']) == prereg['set_aside_requested_bytes']
    policy.reset()
    with torch.no_grad():
        a0_arena = make_arena(x)
        d2_arena = make_arena(x)
        a0_graph, a0, _ = capture_arena(x, a0_arena, None, None)
        d2_graph, d2, applied = capture_arena(x, d2_arena, Discard(), policy)
        assert applied == gate['attached_graph_kernel_nodes'] and torch.equal(a0, d2)
        expected = torch.load(ROOT / 'raw/semantic_outputs.pt',
                              weights_only=True, map_location='cpu')['K512_B0'].to('cuda:0')
        arms = {
            'L512_A0_ARENA_GRAPH': (a0_graph, a0),
            'L512_D2_PERSIST_DISCARD_GRAPH': (d2_graph, d2),
        }
        ordered = list(arms)
        rows = []
        for name in ordered:
            rows.append(measure(name, *arms[name], expected, policy, 'CANARY', 0))
        for rep in range(2):
            for name in ordered if rep % 2 == 0 else list(reversed(ordered)):
                rows.append(measure(name, *arms[name], expected, policy, 'WARMUP', rep))
        for rep in range(7):
            for name in ordered if rep % 2 == 0 else list(reversed(ordered)):
                row = measure(name, *arms[name], expected, policy, 'FORMAL', rep)
                rows.append(row)
                print(json.dumps({'arm': name, 'rep': rep,
                                  'gpu_ms': row['complete_graph_gpu_ms']}), flush=True)
    policy.reset()
    with (ROOT / 'ARENA_TIMING_RESULTS.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    stats = {}
    for name in ordered:
        values = [row['complete_graph_gpu_ms'] for row in rows
                  if row['arm'] == name and row['run_status'] == 'FORMAL']
        median = statistics.median(values)
        stats[name] = {'formal_values_ms': values, 'median_gpu_ms': median,
                       'max_relative_jitter': max(abs(value - median) for value in values) / median}
    a0_stat, d2_stat = (stats[name] for name in ordered)
    improvement = (a0_stat['median_gpu_ms'] - d2_stat['median_gpu_ms']) / a0_stat['median_gpu_ms']
    noise = max(a0_stat['max_relative_jitter'], d2_stat['max_relative_jitter'])
    analysis = {'arms': stats, 'd2_improvement_fraction': improvement,
                'larger_max_relative_jitter': noise,
                'effect_over_noise': improvement / noise if noise else None,
                'd2_material_speedup': improvement >= 0.05 and improvement > 3 * noise,
                'persisting_reset_outside_timed_event_before_each_replay': True,
                'policy_window_bytes': prereg['window_bytes'],
                'policy_nodes_attached': applied}
    (ROOT / 'ARENA_TIMING_ANALYSIS.json').write_text(json.dumps(analysis, indent=2, sort_keys=True) + '\n')
    print(json.dumps(analysis, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
