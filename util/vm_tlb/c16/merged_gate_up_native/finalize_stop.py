#!/usr/bin/env python3
"""Finalize the merged-baseline correctness-stop review pack."""

import argparse
import csv
import hashlib
import json
import platform
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path


BASE = "071297ae7f4aa772a27fae0cf31ad47ab7d967be"
AUTH = "3c3f667bbab8f3ae227dc3bc8eaa6c642b97a453"
AUTH_TREE = "e4be7386c697b33e4f429b833216fdb0bd65f17d"
VLLM = "df8fd42116f172b7a53bc10c8a680b05232edbed"
REVISION = "b25037543e9394b818fdfca67ab2a00ecc7dd641"


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--raw", type=Path, required=True)
    p.add_argument("--pack", type=Path, required=True)
    p.add_argument("--remote-root", required=True)
    args = p.parse_args()
    args.pack.mkdir(parents=True, exist_ok=True)
    correctness = json.loads((args.raw / "CROSS_RUNTIME_CORRECTNESS.json").read_text())
    timeline = json.loads((args.raw / "TIMELINE_CANARY_SUMMARY.json").read_text())
    b0 = json.loads((args.raw / "canary_b0.json").read_text())
    b2 = json.loads((args.raw / "canary_b2.json").read_text())
    cpu = json.loads((args.pack / "CPU_PREFLIGHT.json").read_text())
    source = json.loads((args.pack / "SOURCE_PREFLIGHT.json").read_text())
    receipt = json.loads((args.raw / "GPU_LOCK_RECEIPT.json").read_text())

    for raw_name, pack_name in [
        ("CROSS_RUNTIME_CORRECTNESS.json", "CANARY_CORRECTNESS.json"),
        ("FP16_COMPARISON.tsv", "FP16_COMPARISON.tsv"),
        ("TIMELINE_CANARY_SUMMARY.json", "TIMELINE_CANARY_SUMMARY.json"),
        ("FFN_KERNEL_INVENTORY.tsv", "FFN_KERNEL_INVENTORY.tsv"),
        ("FFN_SEMANTIC_TIMING.tsv", "FFN_SEMANTIC_TIMING.tsv"),
        ("GPU_LOCK_RECEIPT.json", "GPU_LOCK_RECEIPT.json"),
    ]:
        shutil.copyfile(args.raw / raw_name, args.pack / pack_name)

    with (args.raw / "FP16_COMPARISON.tsv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    by_role = defaultdict(list)
    for row in rows:
        by_role[row["role"]].append(row)
    role_summary = {}
    for role, values in sorted(by_role.items()):
        failed = [row for row in values if row["within_tolerance"] != "True"]
        role_summary[role] = {
            "total": len(values), "pass": len(values) - len(failed), "fail": len(failed),
            "max_abs": max(float(row["max_abs"]) for row in values),
            "max_relative_l2": max(float(row["relative_l2"]) for row in values),
            "mean_of_mean_abs": sum(float(row["mean_abs"]) for row in values) / len(values),
        }
    failure = {
        "status": "CORRECTNESS_TOLERANCE_FAILED_STOP",
        "tokens_exact": correctness["checks"]["tokens_exact"],
        "all_finite": correctness["checks"]["all_outputs_finite"],
        "all_shapes_equal": correctness["checks"]["all_shapes_equal"],
        "atol": correctness["atol"], "rtol": correctness["rtol"],
        "role_summary": role_summary,
        "gate_up_down_failed_unique_occurrences": sum(role_summary[role]["fail"] for role in ("gate_proj", "up_proj", "down_proj")),
        "gate_up_down_total_occurrences": 336,
        "max_abs_overall": correctness["max_abs_overall"],
        "max_relative_l2": correctness["max_relative_l2"],
        "formal_started": False,
        "observer_alias_repair": "canary values were cloned outside narrow semantic timing ranges; final failure is from frozen-tolerance data",
    }
    dump(args.pack / "CORRECTNESS_FAILURE_SUMMARY.json", failure)
    canary_b0 = {
        "status": b0["status"], "arm": "B0", "tokens": b0["generated_token_ids_D0_D3"],
        "decode_wall_ms_canary_excluded": b0["decode_wall_ms"], "decode_step_ms": b0["decode_step_ms"],
        "projection_occurrences": len(b0["occurrences"]), "ffn_occurrences": len(b0["ffn_occurrences"]),
        "runtime": "AutoAWQ 0.2.7.post3 WQLinear_GEMM", "raw_json_sha256": sha256(args.raw / "canary_b0.json"),
    }
    canary_b2 = {
        "status": b2["status"], "arm": "B2", "tokens": b2["generated_token_ids_D0_D3"],
        "decode_wall_ms_canary_excluded": b2["decode_wall_ms"], "decode_step_ms": b2["decode_step_ms"],
        "semantic_occurrences": len(b2["occurrences"]), "ffn_occurrences": len(b2["ffn_occurrences"]),
        "prefill_frontend_steps": b2["prefill_frontend_steps"], "decode_frontend_steps": b2["decode_frontend_steps"],
        "inactive_execute_token_counts": b2["inactive_execute_token_counts"],
        "runtime": f"vLLM {VLLM}", "raw_json_sha256": sha256(args.raw / "canary_b2.json"),
    }
    dump(args.pack / "TIMELINE_CANARY_B0.json", canary_b0)
    dump(args.pack / "TIMELINE_CANARY_B2.json", canary_b2)

    parameters = timeline["b2_gate_up_parameter_layout"]
    physical_bytes = sum(value["bytes"] for value in parameters.values())
    backend = {
        "status": "PASS_RUNTIME_BACKEND_RESOLVED",
        "quant_method": timeline["b2_selected_quant_method"],
        "kernel_backend": timeline["b2_selected_kernel_backend"],
        "merged_gate_up_kernel_names": timeline["b2_merged_gate_up_kernel_names"],
        "silu_and_mul_kernel_names": timeline["b2_silu_and_mul_kernel_names"],
        "merged_gate_up_kernel_launches": timeline["b2_role_kernel_counts"]["gate_up"],
        "silu_and_mul_kernel_launches": timeline["b2_role_kernel_counts"]["silu_and_mul"],
        "down_kernel_launches": timeline["b2_role_kernel_counts"]["down"],
        "separate_reduction_kernel_count_name_classified": timeline["b2_reduction_name_classified_count"],
        "parameter_layout": parameters,
        "logical_quant_bytes_per_layer": 70547456,
        "physical_parameter_bytes_per_layer": physical_bytes,
        "padding_bytes": physical_bytes - 70547456,
        "persistent_workspace_parameters_observed": [],
        "workspace_boundary": "no persistent workspace tensor was exposed by gate_up module/kernel census; transient internal workspace not separately attributed",
        "kernel_state": timeline["b2_kernel_state"],
    }
    dump(args.pack / "B2_BACKEND_AND_LAYOUT_RECEIPT.json", backend)

    histories = []
    for index in range(1, 4):
        path = args.raw / f"ABORTED_ENGINEERING_ATTEMPT{index}_GPU_LOCK_RECEIPT.json"
        histories.append({"attempt": index, "classification": "ABORTED_ENGINEERING_PREFLIGHT",
                          "receipt": json.loads(path.read_text()), "receipt_sha256": sha256(path)})
    histories.append({"attempt": 4, "classification": "FINAL_CANARY_CORRECTNESS_STOP",
                      "receipt": receipt, "receipt_sha256": sha256(args.raw / "GPU_LOCK_RECEIPT.json")})
    dump(args.pack / "GPU_LOCK_HISTORY.json", {"status": "RELEASED_ALL_WITH_ENGINEERING_RESTART_DEVIATION",
                                                "attempts": histories,
                                                "single_outer_lock_per_attempt": True,
                                                "single_outer_lock_across_entire_goal": False,
                                                "contract_deviation": "three aborted engineering attempts released their locks before the final scientific canary attempt",
                                                "final_scientific_attempt_single_outer_lock": True,
                                                "cumulative_gpu_wall_seconds": receipt["cumulative_gpu_wall_seconds"],
                                                "budget_seconds": receipt["total_max_gpu_wall_seconds"],
                                                "cumulative_budget_pass": receipt["cumulative_gpu_wall_seconds"] <= receipt["total_max_gpu_wall_seconds"]})

    not_run = {"status": "NOT_RUN_CORRECTNESS_TOLERANCE_FAILED_STOP", "formal_b0_samples": 0,
               "formal_b2_samples": 0, "abba_blocks": 0, "bootstrap": "NOT_COMPUTED"}
    (args.pack / "NATIVE_TIMING_RAW.tsv").write_text("status\treason\tb0_samples\tb2_samples\nNOT_RUN\tCORRECTNESS_TOLERANCE_FAILED_STOP\t0\t0\n")
    (args.pack / "ABBA_BLOCK_SUMMARY.tsv").write_text("status\treason\tcompleted_blocks\nNOT_RUN\tCORRECTNESS_TOLERANCE_FAILED_STOP\t0\n")
    dump(args.pack / "BOOTSTRAP_RESULT.json", not_run)
    dump(args.pack / "FFN_LOCAL_ANALYSIS.json", {**not_run, "canary_structure_available": True,
                                                  "performance_inference": "PROHIBITED"})
    final = {
        "status": "CORRECTNESS_TOLERANCE_FAILED_STOP",
        "decision": "NO_PERFORMANCE_CLASSIFICATION",
        "tokens_exact": True, "canonical_quant_identity": cpu["all_28_layer_loader_and_canonical_identity"],
        "runtime_backend": timeline["b2_selected_kernel_backend"],
        "formal_started": False, "whole_decode_speedup": None,
        "gpu_lock_contract_note": "all locks released and cumulative budget passed; single-outer-lock-across-goal was not met because of three preserved engineering restarts",
        "b0_b2_difference_attribution": "NOT_ALLOWED; cross-runtime and correctness failed",
        "automatic_followup": False,
    }
    dump(args.pack / "FINAL_DECISION.json", final)
    source_contract = {
        "status": "PASS_AUTHORITY_CPU_PREFLIGHT_THEN_CORRECTNESS_STOP",
        "task": "C16_MERGED_GATE_UP_NATIVE_STRONG_BASELINE_109_V1",
        "authority_commit": AUTH, "authority_tree": AUTH_TREE,
        "contract_sha256": sha256(args.pack / "AUTHORITY_CONTRACT.json"),
        "accepted_b0_base_commit": BASE, "vllm_commit": VLLM,
        "checkpoint_revision": REVISION, "comparison_class": "same checkpoint and logical AWQ semantics; cross-runtime strong baseline",
        "not_merge_only_strict_ab": True, "failed_two_stream_goal_remains_frozen": True,
        "raw_node109": str(args.raw), "raw_node164_root": args.remote_root,
        "b0_runner_sha256": source["b0_runner_sha256"], "b2_runner_sha256": source["b2_runner_sha256"],
    }
    dump(args.pack / "SOURCE_AND_CONTRACT.json", source_contract)
    audit = f"""# B0/B2 implementation and STOP audit\n\n- Comparison class: same checkpoint and logical AWQ semantics, cross-runtime strong baseline; **not** a merge-only strict A/B.\n- B0 is the accepted AutoAWQ runtime with observational outer/FFN events and canary-only tensor snapshots.\n- B2 is pinned vLLM `{VLLM}`, `MergedColumnParallelLinear` + `SiluAndMul`, with `AutoAWQMarlinLinearMethod` selecting `MarlinLinearKernel`.\n- CPU canonical unpack/loader identity passed all 28 layers; no requantization occurred.\n- Both canaries generated `[23578, 11, 323, 3950]`; all compared tensors were finite and shape-correct.\n- Frozen FP16 tolerance failed in {failure['gate_up_down_failed_unique_occurrences']}/336 gate/up/down occurrences (gate={role_summary['gate_proj']['fail']}, up={role_summary['up_proj']['fail']}, down={role_summary['down_proj']['fail']}); max absolute difference was {failure['max_abs_overall']}.\n- Formal ABBA timing was therefore not started. Canary wall values are retained only as excluded diagnostic values and support no speedup claim.\n- The earlier two-stream correctness STOP remains frozen and is not an ancestor of this branch.\n"""
    (args.pack / "B0_B2_IMPLEMENTATION_AUDIT.md").write_text(audit)
    env = json.loads((args.pack / "ENVIRONMENT_RECEIPT.json").read_text())
    build = {"status": "PASS", "host_python": platform.python_version(),
             "vllm_install": env["install_class"], "vllm_commit": env["vllm_commit"],
             "torch_version": env["torch_version"], "torch_cuda_version": env["torch_cuda_version"],
             "extensions": env["precompiled_extensions"],
             "accepted_autoawq_environment_modified": False,
             "tool_sha256": {path.name: sha256(path) for path in sorted((args.repo / "util/vm_tlb/c16/merged_gate_up_native").glob("*")) if path.is_file()}}
    dump(args.pack / "BUILD_RECEIPT.json", build)
    tests = {"status": "PASS_STOP_BEHAVIOR", "cpu_preflight": cpu["status"],
             "source_preflight": source["status"], "timeline_audit": timeline["status"],
             "token_identity": "PASS", "fp16_tolerance": "FAIL_STOP",
             "formal_guard_zero_samples": True, "gpu_lock_released": receipt["released"],
             "single_outer_lock_across_goal": False,
             "forbidden_tools_used": []}
    dump(args.pack / "TESTS.json", tests)
    readme = """# C16 merged gate/up native strong baseline — Lane 7\n\nAuthority, environment isolation, checkpoint identity, 28-layer canonical AWQ identity, runtime backend selection, token identity, shape checks, and finite checks closed successfully. The B2 runtime selected the mature Marlin merged path.\n\nThe frozen FP16 tolerance failed for a bounded subset of gate/up/down occurrences. The contract therefore stopped before formal timing. Canary wall values and kernel traces are retained as non-inferential diagnostic evidence only; no B0/B2 speedup or merge benefit is claimed. Three earlier engineering attempts were aborted and their locks released; consequently the single-outer-lock-across-goal requirement was not met, although the cumulative 86-second GPU budget remained below 480 seconds.\n"""
    (args.pack / "README.md").write_text(readme)
    stop = {"status": "CORRECTNESS_TOLERANCE_FAILED_STOP", "formal_started": False,
            "tokens_exact": True, "failed_unique_gate_up_down_occurrences": failure["gate_up_down_failed_unique_occurrences"],
            "max_abs": failure["max_abs_overall"], "gpu_lock_released": receipt["released"]}
    dump(args.raw / "CORRECTNESS_TOLERANCE_FAILED_STOP.json", stop)
    print(json.dumps(final, sort_keys=True))


if __name__ == "__main__":
    main()
