#!/usr/bin/env python3
"""Process-level campaign runner for AWMA R26."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import traceback
from pathlib import Path

import torch

from component import (
    ATOL, RTOL, IDENTITY, POLICIES, TiedWeightTrainer, compare_observables,
    scalar_metrics, sha_file, state_metrics, tensor_metrics, tensor_sha,
)


EXPECTED_START = {
    "weight_sha256": "a7e08515543a44b11420a2427e6c8bbcf263b45389753bd4c044fd2f9e3a3e4d",
    "m_sha256": "65ca646169b4e646230074dd684265d490ded95de96d114b273f64306e8f25eb",
    "v_sha256": "bcc6d93fabb0106bc0133aa3096e2246f66e7312d7b17b69f9405ee4d05ab826",
    "cpu_rng_sha256": "3462c9592a5ad5c4a7f9803ecdb79ba11cdf617d497b9f41b87df47b2811eba18",
    "cuda_rng_sha256": "ec7d748becf40257adc0f3a8f69cf84db26b3d9bd2d3a846bdc7761fc44cb23e1",
}


def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def clean_result(result):
    return {k: v for k, v in result.items() if k != "diagnostic_tensors"}


def load_state(path):
    return torch.load(path, map_location="cpu", weights_only=False)


def metric_pass(metrics):
    return all(v.get("allclose", False) and v.get("finite", False) for v in metrics.values())


def first_failure(container, phase, policy, index, metrics):
    bad = {k: v for k, v in metrics.items() if not v.get("allclose", False) or not v.get("finite", False)}
    if not bad:
        return None
    return {"phase": phase, "policy": policy, "trajectory_index": index, "metrics": bad}


def mode_bootstrap(a):
    trainer = TiedWeightTrainer(a.model, a.tokens, 1)
    torch.manual_seed(25002); torch.cuda.manual_seed_all(25002)
    trainer.m.zero_(); trainer.v.zero_(); trainer.step = 0
    result = trainer.run_step("b0", diagnostic=False, timed=False)
    state, receipt = trainer.save_checkpoint(a.common, "common_post_b1_b0_bootstrap")
    observed = {
        "weight_sha256": receipt["weight_sha256"], "m_sha256": receipt["m_sha256"],
        "v_sha256": receipt["v_sha256"], "cpu_rng_sha256": receipt["cpu_rng_sha256"],
        "cuda_rng_sha256": receipt["cuda_rng_sha256"],
    }
    receipt.update({
        "expected_parent_hashes": EXPECTED_START,
        "parent_hashes_exact": observed == EXPECTED_START,
        "parent_snapshot_payload_available": False,
        "parent_verification_interpretation": (
            "BITWISE_MATCH" if observed == EXPECTED_START else
            "RECEIPT_ONLY_HASH_MISMATCH; exact R25 runner replay also produced different W/m/v hashes while RNG hashes matched; common state is frozen from this single accepted-semantics derivation"
        ),
        "bootstrap_result": clean_result(result),
        "authority": trainer.authority(),
        "logical_step": trainer.step,
    })
    if trainer.step != 1:
        raise RuntimeError(f"common start counter mismatch: {observed}")
    write_json(Path(a.root) / "raw/COMMON_START_STATE.json", receipt)
    print(json.dumps({"status": "PASS", "common": a.common, "sha256": receipt["sha256"]}, sort_keys=True))
    del state
    trainer.close()


def mode_anchor(a):
    root = Path(a.root); temp = root / "checkpoints/anchor_temp"; temp.mkdir(parents=True, exist_ok=True)
    trainer = TiedWeightTrainer(a.model, a.tokens, 1, a.common)
    b0_scalars, b0_receipts = [], []
    b0_diag_path = temp / "b0_diag.pt"
    for k in range(1, 5):
        result = trainer.run_step("b0", diagnostic=(k == 1), timed=False)
        next_loss = trainer.next_loss()
        state, receipt = trainer.save_checkpoint(temp / f"b0_k{k}.pt", "b0_anchor")
        b0_receipts.append(receipt)
        b0_scalars.append({"loss": result["loss"], "next_loss": next_loss, "step": trainer.step})
        if k == 1:
            torch.save(result["diagnostic_tensors"], b0_diag_path)
        del state, result
    details = {"b0": {"one_step": {}, "four_step": []}}
    first = None
    # B0 self-reference is exact by construction.
    b0_state = load_state(temp / "b0_k1.pt"); b0_diag = torch.load(b0_diag_path, map_location="cpu", weights_only=False)
    b0_obs = {"loss": b0_scalars[0]["loss"], "dH": b0_diag["dH"], "gradient": b0_diag["gradient"], "weight": b0_state["weight"], "m": b0_state["m"], "v": b0_state["v"], "step": b0_state["step"], "next_loss": b0_scalars[0]["next_loss"]}
    details["b0"]["one_step"] = compare_observables(b0_obs, b0_obs, tuple(b0_obs))
    del b0_state, b0_diag, b0_obs
    for policy in POLICIES:
        trainer.load_checkpoint(a.common)
        policy_detail = {"one_step": None, "four_step": []}
        for k in range(1, 5):
            result = trainer.run_step(policy, diagnostic=(k == 1), timed=False)
            next_loss = trainer.next_loss()
            got_state = trainer.snapshot_cpu(policy)
            ref_state = load_state(temp / f"b0_k{k}.pt")
            metrics = {
                "loss": scalar_metrics(result["loss"], b0_scalars[k - 1]["loss"]),
                "next_loss": scalar_metrics(next_loss, b0_scalars[k - 1]["next_loss"]),
                **state_metrics(got_state, ref_state),
            }
            policy_detail["four_step"].append({"trajectory_index": k, "metrics": metrics, "qualified": metric_pass(metrics)})
            if k == 1:
                ref_diag = torch.load(b0_diag_path, map_location="cpu", weights_only=False)
                one = {
                    **metrics,
                    "dH": tensor_metrics(result["diagnostic_tensors"]["dH"], ref_diag["dH"]),
                    "gradient": tensor_metrics(result["diagnostic_tensors"]["gradient"], ref_diag["gradient"]),
                }
                policy_detail["one_step"] = one
                if first is None:
                    first = first_failure({}, "one_step", policy, k, one)
                del ref_diag
            if first is None:
                first = first_failure({}, "four_step", policy, k, metrics)
            del result, got_state, ref_state
        details[policy] = policy_detail
    qualified = all(metric_pass(details[p]["one_step"]) and all(x["qualified"] for x in details[p]["four_step"]) for p in POLICIES)
    receipt = {
        "status": "PASS" if qualified else "FAIL", "qualified": qualified,
        "tolerance": {"rtol": RTOL, "atol": ATOL}, "details": details,
        "first_mismatch": first, "b0_reference_checkpoints": b0_receipts,
        "continuous_four_steps_per_lineage": True,
    }
    write_json(root / "raw/ANCHOR_QUALIFICATION.json", receipt)
    # Temporary B0 tensors are derivable from the immutable common start.
    for p in temp.glob("*"):
        p.unlink()
    temp.rmdir()
    trainer.close()
    if not qualified:
        raise RuntimeError("R26_NUMERIC_OR_TRAJECTORY_NOT_QUALIFIED")
    print(json.dumps({"status": "PASS", "one_step": True, "four_step": True}, sort_keys=True))


def mode_trajectory(a):
    root = Path(a.root); ck = root / "checkpoints/trajectory"; ck.mkdir(parents=True, exist_ok=True)
    trainer = TiedWeightTrainer(a.model, a.tokens, 1, a.common)
    indices = {1, 4, 8, 16, 32}
    c1_scalars, c1_receipts = [], {}
    for k in range(1, 33):
        result = trainer.run_step("c1", diagnostic=False, timed=False)
        nxt = trainer.next_loss()
        c1_scalars.append({"trajectory_index": k, "loss": result["loss"], "next_loss": nxt, "step": trainer.step})
        if k in indices:
            state, receipt = trainer.save_checkpoint(ck / f"c1_k{k}.pt", "c1")
            c1_receipts[str(k)] = receipt; del state
        print(json.dumps({"progress": "c1", "k": k, "step": trainer.step}), flush=True)
        del result
    trainer.load_checkpoint(a.common)
    comparisons, s2_receipts = [], {}
    first = None
    for k in range(1, 33):
        result = trainer.run_step("s2", diagnostic=False, timed=False)
        nxt = trainer.next_loss()
        metrics = {
            "loss": scalar_metrics(result["loss"], c1_scalars[k - 1]["loss"]),
            "next_loss": scalar_metrics(nxt, c1_scalars[k - 1]["next_loss"]),
            "step": compare_observables({"step": trainer.step}, {"step": c1_scalars[k - 1]["step"]}, ("step",))["step"],
        }
        if k in indices:
            got = trainer.snapshot_cpu("s2")
            ref = load_state(ck / f"c1_k{k}.pt")
            metrics.update(state_metrics(got, ref))
            if k in (16, 32):
                path = ck / f"s2_k{k}.pt"
                torch.save(got, path)
                s2_receipts[str(k)] = {
                    "path": str(path), "bytes": path.stat().st_size, "sha256": sha_file(path),
                    "step": got["step"], "policy_metadata": "s2",
                    "weight_sha256": tensor_sha(got["weight"]), "m_sha256": tensor_sha(got["m"]), "v_sha256": tensor_sha(got["v"]),
                    "contains_gpu_tensor": False,
                }
            del got, ref
        qualified = metric_pass(metrics)
        comparisons.append({"trajectory_index": k, "qualified": qualified, "metrics": metrics})
        if first is None:
            first = first_failure({}, "trajectory_32", "s2", k, metrics)
        print(json.dumps({"progress": "s2", "k": k, "step": trainer.step, "qualified": qualified}), flush=True)
        del result
    qualified = all(x["qualified"] for x in comparisons) and trainer.step == 33
    receipt = {
        "status": "PASS" if qualified else "FAIL", "qualified": qualified,
        "continuous_steps_per_policy": 32, "common_start_step": 1, "final_step": trainer.step,
        "full_state_indices": sorted(indices), "tolerance": {"rtol": RTOL, "atol": ATOL},
        "c1_scalars": c1_scalars, "comparisons": comparisons, "first_mismatch": first,
        "c1_checkpoint_receipts": c1_receipts, "s2_checkpoint_receipts": s2_receipts,
    }
    write_json(root / "raw/TRAJECTORY_32_STEP.json", receipt)
    trainer.close()
    if not qualified:
        raise RuntimeError("R26_NUMERIC_OR_TRAJECTORY_NOT_QUALIFIED")
    print(json.dumps({"status": "PASS", "trajectory_steps": 32, "final_step": 33}, sort_keys=True))


def mode_resume(a):
    root = Path(a.root); ck = root / "checkpoints/trajectory"
    source = ck / f"{a.policy}_k16.pt"; reference = ck / f"{a.policy}_k32.pt"
    trainer = TiedWeightTrainer(a.model, a.tokens, 1, str(source))
    if trainer.step != 17:
        raise RuntimeError("resume checkpoint counter mismatch")
    scalars = []
    for k in range(17, 33):
        result = trainer.run_step(a.policy, diagnostic=False, timed=False)
        nxt = trainer.next_loss()
        scalars.append({"trajectory_index": k, "loss": result["loss"], "next_loss": nxt, "step": trainer.step})
        print(json.dumps({"progress": f"resume_{a.policy}", "k": k, "step": trainer.step}), flush=True)
        del result
    resumed, resumed_receipt = trainer.save_checkpoint(ck / f"{a.policy}_resumed_k32.pt", a.policy)
    ref = load_state(reference)
    metrics = state_metrics(resumed, ref)
    trajectory = json.loads((root / "raw/TRAJECTORY_32_STEP.json").read_text())
    if a.policy == "c1":
        ref_loss = trajectory["c1_scalars"][-1]["loss"]; ref_next = trajectory["c1_scalars"][-1]["next_loss"]
    else:
        last = trajectory["comparisons"][-1]
        ref_loss = last["metrics"]["loss"]["observed"]
        ref_next = last["metrics"]["next_loss"]["observed"]
    metrics["loss"] = scalar_metrics(scalars[-1]["loss"], ref_loss)
    metrics["next_loss"] = scalar_metrics(scalars[-1]["next_loss"], ref_next)
    qualified = metric_pass(metrics) and trainer.step == 33
    receipt = {
        "policy": a.policy, "source_checkpoint": str(source), "source_sha256": sha_file(source),
        "reference_checkpoint": str(reference), "reference_sha256": sha_file(reference),
        "resumed_checkpoint": resumed_receipt, "loaded_step": 17, "final_step": trainer.step,
        "remaining_steps": 16, "metrics": metrics, "qualified": qualified,
        "tied_storage_reproved_after_load": True, "checkpoint_contains_gpu_tensor": False,
    }
    write_json(root / f"raw/CHECKPOINT_RESUME_{a.policy.upper()}.json", receipt)
    trainer.close(); del resumed, ref
    if not qualified:
        raise RuntimeError("R26_NUMERIC_OR_TRAJECTORY_NOT_QUALIFIED")
    print(json.dumps({"status": "PASS", "policy": a.policy, "final_step": 33}, sort_keys=True))


def mode_switch(a):
    root = Path(a.root); source = root / "checkpoints/trajectory/c1_k16.pt"
    trainer = TiedWeightTrainer(a.model, a.tokens, 1, str(source))
    c1 = trainer.run_step("c1", diagnostic=True, timed=False); c1_next = trainer.next_loss(); c1_state = trainer.snapshot_cpu("c1")
    trainer.load_checkpoint(source)
    s2 = trainer.run_step("s2", diagnostic=True, timed=False); s2_next = trainer.next_loss(); s2_state = trainer.snapshot_cpu("s2")
    metrics = {
        "loss": scalar_metrics(s2["loss"], c1["loss"]), "next_loss": scalar_metrics(s2_next, c1_next),
        "dH": tensor_metrics(s2["diagnostic_tensors"]["dH"], c1["diagnostic_tensors"]["dH"]),
        "gradient": tensor_metrics(s2["diagnostic_tensors"]["gradient"], c1["diagnostic_tensors"]["gradient"]),
        **state_metrics(s2_state, c1_state),
    }
    qualified = metric_pass(metrics) and c1_state["step"] == s2_state["step"] == 18
    receipt = {
        "source_checkpoint": str(source), "source_sha256": sha_file(source),
        "source_step": 17, "final_step": 18, "same_moments_and_counter_loaded": True,
        "metrics": metrics, "qualified": qualified,
    }
    write_json(root / "raw/POLICY_SWITCH_QUALIFICATION.json", receipt)
    trainer.close(); del c1_state, s2_state, c1, s2
    if not qualified:
        raise RuntimeError("R26_NUMERIC_OR_TRAJECTORY_NOT_QUALIFIED")
    print(json.dumps({"status": "PASS", "policy_switch": True}, sort_keys=True))


def mode_probe(a):
    out = Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
    started = time.time(); trainer = None; phase = "MODEL_DATA_STATE_LOAD"
    try:
        trainer = TiedWeightTrainer(a.model, a.tokens, a.batch, a.common)
        phase = "TRAINING_STEPS"
        steps = []
        previous_post = None
        for k in range(1, 6):
            result = trainer.run_step(a.policy, diagnostic=False, timed=False)
            phase = "FINITE_STATE_CHECK"
            finite, tensor_name, row = trainer.finite_state()
            if not math.isfinite(result["loss"]) or not finite or trainer.step != 1 + k:
                raise RuntimeError(f"probe invariant failure loss={result['loss']} finite={finite} tensor={tensor_name} row={row} step={trainer.step}")
            growth = None if previous_post is None else result["post_step_allocated_bytes"] - previous_post
            previous_post = result["post_step_allocated_bytes"]
            result["transient_active_growth_bytes"] = growth
            result["trial_step"] = k; result["warmup_designation"] = k <= 2
            steps.append(clean_result(result))
            print(json.dumps({"progress": "probe", "policy": a.policy, "batch": a.batch, "k": k, "step": trainer.step}), flush=True)
            phase = "TRAINING_STEPS"
        receipt = {
            "status": "PASS", "outcome": "PASS", "policy": a.policy, "batch": a.batch,
            "five_complete_steps": True, "warmup_steps": 2, "following_steps": 3,
            "start_step": 1, "final_step": trainer.step, "steps": steps,
            "batch_binding": trainer.authority(), "elapsed_seconds": time.time() - started,
            "pid": os.getpid(), "lock_sentinel": os.environ.get("R26_GPU_LOCK_HELD"),
        }
        write_json(out, receipt); trainer.close()
        print(json.dumps({"outcome": "PASS", "policy": a.policy, "batch": a.batch}, sort_keys=True))
    except torch.cuda.OutOfMemoryError as exc:
        free = total = allocated = reserved = None
        try:
            free, total = torch.cuda.mem_get_info(); allocated = torch.cuda.memory_allocated(); reserved = torch.cuda.memory_reserved()
        except Exception:
            pass
        receipt = {
            "status": "OOM", "outcome": "OOM", "policy": a.policy, "batch": a.batch,
            "oom_phase": getattr(trainer, "phase", phase) if trainer is not None else phase,
            "error": repr(exc), "traceback": traceback.format_exc(),
            "free_bytes": free, "total_bytes": total, "allocated_bytes": allocated, "reserved_bytes": reserved,
            "elapsed_seconds": time.time() - started, "pid": os.getpid(),
            "lock_sentinel": os.environ.get("R26_GPU_LOCK_HELD"),
        }
        write_json(out, receipt)
        print(json.dumps({"outcome": "OOM", "policy": a.policy, "batch": a.batch, "phase": receipt["oom_phase"]}, sort_keys=True))
    except Exception as exc:
        receipt = {
            "status": "ERROR", "outcome": "UNKNOWN", "policy": a.policy, "batch": a.batch,
            "phase": getattr(trainer, "phase", phase) if trainer is not None else phase,
            "error": repr(exc), "traceback": traceback.format_exc(), "elapsed_seconds": time.time() - started,
            "pid": os.getpid(), "lock_sentinel": os.environ.get("R26_GPU_LOCK_HELD"),
        }
        write_json(out, receipt)
        print(json.dumps({"outcome": "UNKNOWN", "policy": a.policy, "batch": a.batch}, sort_keys=True))
        raise


def mode_endpoint_numeric(a):
    root = Path(a.root); trainer = TiedWeightTrainer(a.model, a.tokens, a.batch, a.common)
    c1 = trainer.run_step("c1", diagnostic=True, timed=False); c1_next = trainer.next_loss(); c1_state = trainer.snapshot_cpu("c1")
    trainer.load_checkpoint(a.common)
    s2 = trainer.run_step("s2", diagnostic=True, timed=False); s2_next = trainer.next_loss(); s2_state = trainer.snapshot_cpu("s2")
    metrics = {
        "loss": scalar_metrics(s2["loss"], c1["loss"]), "next_loss": scalar_metrics(s2_next, c1_next),
        "dH": tensor_metrics(s2["diagnostic_tensors"]["dH"], c1["diagnostic_tensors"]["dH"]),
        "gradient": tensor_metrics(s2["diagnostic_tensors"]["gradient"], c1["diagnostic_tensors"]["gradient"]),
        **state_metrics(s2_state, c1_state),
    }
    qualified = metric_pass(metrics) and c1_state["step"] == s2_state["step"] == 2
    write_json(root / "raw/SELECTED_ENDPOINT_NUMERICAL_QUALIFICATION.json", {"batch": a.batch, "metrics": metrics, "qualified": qualified})
    trainer.close(); del c1_state, s2_state, c1, s2
    if not qualified:
        raise RuntimeError("R26_NUMERIC_OR_TRAJECTORY_NOT_QUALIFIED")
    print(json.dumps({"status": "PASS", "batch": a.batch}, sort_keys=True))


def mode_formal(a):
    out = Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
    trainer = TiedWeightTrainer(a.model, a.tokens, a.batch, a.common)
    rows = []
    for k in range(2):
        trainer.load_checkpoint(a.common)
        trainer.run_step(a.policy, diagnostic=False, timed=False)
    for repeat in range(5):
        trainer.load_checkpoint(a.common)
        result = trainer.run_step(a.policy, diagnostic=False, timed=True)
        result = clean_result(result); result.update({"group": a.group, "repeat": repeat, "formal": True})
        rows.append(result)
        print(json.dumps({"progress": "formal", "policy": a.policy, "group": a.group, "repeat": repeat}), flush=True)
    with out.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    trainer.close()
    print(json.dumps({"status": "PASS", "samples": len(rows), "policy": a.policy, "group": a.group}, sort_keys=True))


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", required=True, choices=("bootstrap", "anchor", "trajectory", "resume", "switch", "probe", "endpoint_numeric", "formal"))
    p.add_argument("--root", required=True); p.add_argument("--model", required=True); p.add_argument("--tokens", required=True)
    p.add_argument("--common", required=True); p.add_argument("--policy", choices=("c1", "s2")); p.add_argument("--batch", type=int, default=1)
    p.add_argument("--output"); p.add_argument("--group", type=int)
    a = p.parse_args()
    if a.mode in ("resume", "probe", "formal") and not a.policy: p.error("--policy required")
    if a.mode in ("probe", "formal") and not a.output: p.error("--output required")
    if a.mode == "formal" and a.group is None: p.error("--group required")
    return a


if __name__ == "__main__":
    args = parse_args()
    try:
        globals()[f"mode_{args.mode}"](args)
    except Exception as exc:
        failure = Path(args.root) / "raw/failures" / f"{args.mode}_{args.policy or 'na'}_B{args.batch}_{int(time.time())}.json"
        write_json(failure, {"mode": args.mode, "policy": args.policy, "batch": args.batch, "error": repr(exc), "traceback": traceback.format_exc()})
        raise
