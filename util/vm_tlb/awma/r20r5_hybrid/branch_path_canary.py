#!/usr/bin/env python3
"""Engineering-only exact 1024/305/304/1/0 device-branch/list boundary test."""

import json
import os
from pathlib import Path

import numpy as np
import warp as wp


ROOT = Path("/data/c16/awma/r20r5_hybrid_native_20261002")


@wp.kernel
def branch_receipt(code: int, branch_out: wp.array(dtype=wp.int32)):
    branch_out[0] = code


@wp.kernel
def stop_after_branch(nsolving: wp.array(dtype=wp.int32)):
    nsolving[0] = 0


def main():
    if os.environ.get("R20R5_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU lock receipt absent")
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    from mujoco_warp._src import solver
    from hashlib import sha256
    source = Path(solver.__file__).resolve()
    if source != ROOT / "source_overlay/mujoco_warp/_src/solver.py":
        raise RuntimeError("Hybrid source not selected")
    if sha256(source.read_bytes()).hexdigest() != "aba0862337371bb1f09b24d2089654b5571b5be59e8f6695e97409c22e1680e8":
        raise RuntimeError("Hybrid source SHA changed")
    device = wp.get_device("cuda:0")
    with wp.ScopedDevice(device):
        nsolving = wp.zeros(1, dtype=wp.int32, device=device)
        late_cond = wp.zeros(1, dtype=wp.int32, device=device)
        done = wp.zeros(1024, dtype=wp.bool, device=device)
        active_ids = wp.empty(1024, dtype=wp.int32, device=device)
        active_count = wp.empty(1, dtype=wp.int32, device=device)
        branch = wp.empty(1, dtype=wp.int32, device=device)

        def early():
            wp.launch(branch_receipt, dim=1, inputs=[1], outputs=[branch])

        def late():
            wp.launch(solver._r20r3p1_build_active_ids, dim=1, inputs=[done, 1024], outputs=[active_ids, active_count])
            wp.launch(branch_receipt, dim=1, inputs=[2], outputs=[branch])

        def body():
            wp.launch(solver._r20r5_late_condition, dim=1, inputs=[nsolving], outputs=[late_cond])
            wp.capture_if(late_cond, on_true=late, on_false=early)
            wp.launch(stop_after_branch, dim=1, inputs=[nsolving], outputs=[])

        with wp.ScopedCapture() as graph:
            wp.capture_while(nsolving, while_body=body)
        rows = []
        for count in (1024, 305, 304, 1, 0):
            nsolving.assign(np.array([count], dtype=np.int32))
            done.assign(np.arange(1024) >= count)
            active_ids.fill_(-1)
            active_count.fill_(-1)
            branch.fill_(0)
            late_cond.fill_(-1)
            wp.capture_launch(graph.graph)
            wp.synchronize()
            actual_branch = int(branch.numpy()[0])
            actual_active = int(active_count.numpy()[0])
            actual_late = int(late_cond.numpy()[0])
            expected_branch = 0 if count == 0 else (1 if count > 304 else 2)
            expected_active = count if expected_branch == 2 else -1
            prefix = active_ids.numpy()[:max(0, actual_active)].copy()
            ids_exact = bool(np.array_equal(prefix, np.arange(count))) if expected_branch == 2 else bool(np.all(active_ids.numpy() == -1))
            row = {"initial_nsolving": count, "expected_branch": expected_branch,
                   "observed_branch": actual_branch, "late_condition": actual_late,
                   "active_list_count": actual_active, "expected_active_list_count": expected_active,
                   "active_ids_exact_or_untouched": ids_exact,
                   "final_nsolving": int(nsolving.numpy()[0]),
                   "pass": (actual_branch == expected_branch and actual_active == expected_active and ids_exact
                            and int(nsolving.numpy()[0]) == 0 and (count == 0 or actual_late == int(count <= 304)))}
            rows.append(row)
            if not row["pass"]:
                break
        result = {"stage": "AWMA_R20R5_HYBRID_ACTIVE_WORLD_NATIVE_109_V1",
                  "threshold": 304, "worker_count": 304, "host_per_iteration_branch_decisions": 0,
                  "cases": rows, "all_five_pass": len(rows) == 5 and all(x["pass"] for x in rows)}
        (ROOT / "raw/BRANCH_PATH_CANARY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, sort_keys=True), flush=True)
        if not result["all_five_pass"]:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
