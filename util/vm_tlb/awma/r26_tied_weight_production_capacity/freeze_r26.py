#!/usr/bin/env python3
"""CPU-only R26 implementation/classifier freeze."""

import argparse
import hashlib
import importlib.metadata
import json
import sys
from pathlib import Path


STAGE = "AWMA_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_BOUNDARY_109_V1"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path): return json.loads(Path(path).read_text())
def dump(path, value): Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True); p.add_argument("--repo", required=True)
    p.add_argument("--component", required=True); p.add_argument("--runner", required=True); p.add_argument("--search", required=True)
    p.add_argument("--cce-root", required=True); p.add_argument("--common", required=True)
    a = p.parse_args(); root = Path(a.root); repo = Path(a.repo)
    anchor = load(root / "raw/ANCHOR_QUALIFICATION.json")
    trajectory = load(root / "raw/TRAJECTORY_32_STEP.json")
    resumes = {x: load(root / f"raw/CHECKPOINT_RESUME_{x.upper()}.json") for x in ("c1", "s2")}
    switch = load(root / "raw/POLICY_SWITCH_QUALIFICATION.json")
    if not anchor["qualified"] or not trajectory["qualified"] or not all(x["qualified"] for x in resumes.values()) or not switch["qualified"]:
        raise SystemExit("qualification gate not closed")
    files = [
        Path(a.component), Path(a.runner), Path(a.search),
        Path(a.cce_root) / "cut_cross_entropy/cce_backward.py",
        Path(a.cce_root) / "cut_cross_entropy/tl_utils.py",
        Path(a.cce_root) / "cut_cross_entropy/tl_autotune.py",
        repo / "util/vm_tlb/awma/r25_tied_weight_broader_validation/run_r25_campaign.py",
        repo / "util/vm_tlb/awma/r25_tied_weight_broader_validation/accepted_r24_base.py",
        repo / "docs/vm_tlb/chatgpt_handoff/awma/r26_tied_weight_production_capacity_v1/R26_EXPERIMENT_CONTRACT.json",
        repo / "docs/vm_tlb/chatgpt_handoff/awma/r26_tied_weight_production_capacity_v1/PARENT_AUTHORITY.json",
    ]
    common_receipt = load(root / "raw/COMMON_START_STATE.json")
    frozen = {
        "stage": STAGE, "status": "IMPLEMENTATION_AND_CLASSIFIER_FROZEN",
        "qualification": {
            "one_step": True, "four_step": True, "trajectory_32": True,
            "resume_c1": True, "resume_s2": True, "policy_switch": True,
            "rtol": 0.01, "atol": 0.01,
        },
        "files": [{"path": str(x), "bytes": x.stat().st_size, "sha256": sha(x)} for x in files],
        "common_start": {
            "path": a.common, "bytes": Path(a.common).stat().st_size,
            "sha256": sha(a.common), "logical_step": 1,
            "weight_sha256": common_receipt["weight_sha256"],
            "m_sha256": common_receipt["m_sha256"], "v_sha256": common_receipt["v_sha256"],
            "CPU_only": True, "persistent_GPU_snapshot_bytes": 0,
        },
        "component": {
            "default_policy": "c1", "capacity_opt_in": "s2", "automatic_fallback": False,
            "scope": "tied W only; frozen full backbone remains in dH path",
            "compact_reducer": "sorted unique IDs remapped to compact domain; aten.embedding_dense_backward",
            "C1_full_gradient_buffers": 1, "C1_dense_lookup_gradient": False,
            "S2_full_gradient_buffers": 0, "S2_dense_lookup_gradient": False,
            "tile_fp32_budget_bytes": 33554432, "rows_per_tile": 4096, "tile_count": 32,
        },
        "batch": {
            "range": [1, 512], "only_variable": "physical batch",
            "construction": "materialized identical copies of frozen 127-position shifted sequence",
            "context": 127, "loss_reduction": "mean over B*127 valid labels",
        },
        "search": {
            "exponential": [1,2,4,8,16,32,64,128,256,512],
            "refinement": "floor midpoint until U=L+1", "max_distinct_trials_per_policy": 19,
            "policy_order": ["c1", "s2"], "trial_steps": 5, "warmup_designation": 2,
            "fresh_process_per_trial": True, "endpoint_confirmations": 3,
            "confirmation_majority_vote": False, "max_batch": 512,
        },
        "capacity_outcomes_in_priority_order": [
            "R26_CAPACITY_BOUNDARY_UNSTABLE",
            "R26_INTEGRATED_BATCH_CAPACITY_EXTENSION_SUPPORTED",
            "R26_S2_BATCH_CAPACITY_REGRESSION",
            "R26_CAPACITY_SEARCH_RIGHT_CENSORED",
            "R26_NO_BATCH_CAPACITY_EXTENSION",
        ],
        "formal": {
            "point": "B_common", "policies": ["c1", "s2"], "groups": 3,
            "warmups_per_policy_group": 2, "samples_per_policy_group": 5,
            "orders": [["c1","s2"],["s2","c1"],["c1","s2"]],
            "stable_threshold": "3*max(group MADs)",
            "BENEFIT": ">=2 benefit and <2 regression groups",
            "REGRESSION": ">=2 regression groups", "MIXED": "otherwise",
        },
        "runtime": {
            "python": sys.version,
            "torch": importlib.metadata.version("torch"),
            "transformers": importlib.metadata.version("transformers"),
            "triton": importlib.metadata.version("triton"),
            "CCE_AUTOTUNE": 0,
        },
        "behavior_changes_after_freeze_allowed": False,
    }
    out = root / "raw/IMPLEMENTATION_FREEZE.json"; dump(out, frozen)
    print(str(out)); print(sha(out))


if __name__ == "__main__": main()
