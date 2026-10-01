#!/usr/bin/env python3
"""Engineering-only nested wp.capture_if inside wp.capture_while canary."""

import json
import os
from pathlib import Path

import warp as wp


ROOT = Path("/data/c16/awma/r20r5_hybrid_native_20261002")


@wp.kernel
def late_predicate(current_count: wp.array(dtype=wp.int32), late: wp.array(dtype=wp.int32)):
    late[0] = int(current_count[0] <= 304)


@wp.kernel
def record_branch(current_count: wp.array(dtype=wp.int32), index: wp.array(dtype=wp.int32),
                  branch_code: int, trace_count: wp.array(dtype=wp.int32),
                  trace_branch: wp.array(dtype=wp.int32), branch_tally: wp.array(dtype=wp.int32)):
    i = index[0]
    trace_count[i] = current_count[0]
    trace_branch[i] = branch_code
    branch_tally[branch_code] += 1


@wp.kernel
def advance(current_count: wp.array(dtype=wp.int32), index: wp.array(dtype=wp.int32)):
    old = current_count[0]
    index[0] += 1
    if old <= 302:
        current_count[0] = 0
    else:
        current_count[0] = old - 1


def main():
    if os.environ.get("R20R5_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU lock receipt absent")
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    device = wp.get_device("cuda:0")
    with wp.ScopedDevice(device):
        count = wp.array([306], dtype=wp.int32, device=device)
        late = wp.zeros(1, dtype=wp.int32, device=device)
        index = wp.zeros(1, dtype=wp.int32, device=device)
        trace_count = wp.zeros(8, dtype=wp.int32, device=device)
        trace_branch = wp.zeros(8, dtype=wp.int32, device=device)
        tally = wp.zeros(3, dtype=wp.int32, device=device)

        def record_early():
            wp.launch(record_branch, dim=1, inputs=[count, index, 1],
                      outputs=[trace_count, trace_branch, tally])

        def record_late():
            wp.launch(record_branch, dim=1, inputs=[count, index, 2],
                      outputs=[trace_count, trace_branch, tally])

        def body():
            wp.launch(late_predicate, dim=1, inputs=[count], outputs=[late])
            wp.capture_if(condition=late, on_true=record_late, on_false=record_early)
            wp.launch(advance, dim=1, inputs=[count], outputs=[index])

        with wp.ScopedCapture() as graph:
            wp.capture_while(count, while_body=body)
        wp.capture_launch(graph.graph)
        wp.synchronize()
        n = int(index.numpy()[0])
        counts = trace_count.numpy()[:n].astype(int).tolist()
        branches = trace_branch.numpy()[:n].astype(int).tolist()
        tallies = tally.numpy().astype(int).tolist()
        result = {"initial_count": 306, "threshold": 304, "final_count": int(count.numpy()[0]),
                  "iterations": n, "counts_before_branch": counts, "branch_codes": branches,
                  "branch_code_meaning": {"1": "EARLY", "2": "LATE"},
                  "tallies": tallies, "host_per_iteration_decisions": 0,
                  "nested_capture_replay_qualified": (n == 5 and counts == [306, 305, 304, 303, 302]
                                                      and branches == [1, 1, 2, 2, 2]
                                                      and tallies == [0, 2, 3] and int(count.numpy()[0]) == 0)}
        (ROOT / "raw/NESTED_CONDITIONAL_CANARY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, sort_keys=True), flush=True)
        if not result["nested_capture_replay_qualified"]:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
