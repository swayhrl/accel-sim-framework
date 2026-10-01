#!/usr/bin/env python3
"""CPU/source-only contract, runtime, model, and frozen-input qualification."""

import argparse
import ast
import csv
import hashlib
import json
import subprocess
from pathlib import Path


CONTRACT_COMMIT = "fad9da8116c8ad794f99a93f153b0866162158a4"
CONTRACT_TREE = "c657f1655ffabbeb0942732bdff08c8df8e79987"
CONTRACT_SHA = "a71349283b1661cb23d86cc61dfad6ab5ea2cd8752ca4252bbc1d2feee5acb08"
CONTRACT_DIR = "docs/vm_tlb/review_packs/C16_STAGEA_DENSE_FIRST_TIER0_CONTRACT_FINALIZATION_174NEW_V1"
ASSET_DIR = Path("docs/vm_tlb/review_packs/C16_MEASUREMENT_CAMPAIGN_STAGEA_ASSET_INPUT_CLOSURE_174NEW_V1")
ENV_PYTHON = Path("/data/c16/envs/c16-vllm-v0.30.0-sm89-v1/bin/python")
MODEL_PATHS = {
    "QWEN_BF16": Path("/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct/aa8e72537993ba99e69dfaafa59ed015b17504d1"),
    "QWEN_AWQ": Path("/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct-awq/3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd"),
}
AUTHORITIES = {
    "scope_revision_commit": "137e3414c9c8e59cf1b167e5acc14149fb6273d6",
    "awq_observer_v2_runtime_pass_commit": "9d5aa2f36e22a1a8fcc253d6df865160b5dba797",
    "asset_input_closure_commit": "c3f625e46adb8d5c4082ded8b61858c710e1f4e9",
    "runtime_qualification_commit": "3f62f909a474e4c56695ffacf36ddcb5d7b5f147",
    "observer_v2_source_commit": "f63d39c8d90ced038445c264fa8242c524a1aa6f",
    "olmoe_diagnostic_commit": "8b677cfa541877f559614f7bf22a40dd11cebd56",
    "campaign_design_commit": "5f0335b5f991890348e60e1f23a546f393f86d8b",
}


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def git(repo, *args, binary=False):
    return subprocess.check_output(["git", *args], cwd=repo, text=not binary)


def read_tsv_text(text):
    return list(csv.DictReader(text.splitlines(), delimiter="\t"))


def write_tsv(path, rows, fields):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--contract-gate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    repo, gate, out = args.repo.resolve(), args.contract_gate.resolve(), args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    checks = {}

    receipt = json.loads((gate / "CONTRACT_DISCOVERY_RECEIPT.json").read_text())
    contract_path = gate / "C16_STAGEA_DENSE_FIRST_TIER0_109_CONTRACT_V1.json"
    contract_raw = contract_path.read_bytes()
    contract = json.loads(contract_raw)
    contract_git_path = receipt["contract_path_in_commit"]
    checks["contract_commit_exact"] = receipt["contract_commit"] == CONTRACT_COMMIT
    checks["contract_tree_exact"] = receipt["contract_tree"] == CONTRACT_TREE and git(repo, "rev-parse", f"{CONTRACT_COMMIT}^{{tree}}").strip() == CONTRACT_TREE
    checks["contract_sha_exact"] = hashlib.sha256(contract_raw).hexdigest() == CONTRACT_SHA
    checks["contract_bytes_match_commit"] = git(repo, "show", f"{CONTRACT_COMMIT}:{contract_git_path}", binary=True) == contract_raw
    checks["contract_schema_exact"] = contract["schema"] == "C16_STAGEA_DENSE_FIRST_TIER0_109_CONTRACT_V1"
    checks["contract_authorized"] = contract["status"] == "AUTHORIZED_BY_PROJECT_REVIEW" and contract["execution_authorized"] is True
    checks["allowlist_exact"] = contract["point_allowlist_in_order"] == ["MP01", "MP02", "MP03", "MP05"]
    checks["denylist_exact"] = contract["point_denylist"] == ["MP04", "MP06", "MP07", "MP08"]
    checks["authorities_exact"] = contract["authority"] == AUTHORITIES
    checks["budget_exact"] = (contract["gpu_budget"]["total_gpu_active_seconds_cap"] == 540
                              and contract["gpu_budget"]["per_point_seconds"] == {"MP01": 120, "MP02": 120, "MP03": 120, "MP05": 180}
                              and contract["gpu_budget"]["unused_time_transfer_between_points"] is False)
    checks["sample_protocol_exact"] = (contract["arms"]["GRAPH_ON_NATIVE"]["warmup_requests"] == 1
                                       and contract["arms"]["GRAPH_ON_NATIVE"]["measured_requests"] == 3
                                       and contract["arms"]["GRAPH_OFF_NATIVE"]["warmup_requests"] == 1
                                       and contract["arms"]["GRAPH_OFF_NATIVE"]["measured_requests"] == 3
                                       and contract["arms"]["GRAPH_OFF_OBSERVED"]["warmup_requests"] == 1
                                       and contract["arms"]["GRAPH_OFF_OBSERVED"]["observed_requests"] == 1)
    checks["native_endpoint_exact"] = (contract["native_protocol"]["primary_field"] == "request_cuda_event_ms"
                                       and contract["native_protocol"]["primary_estimator"] == "median_of_three_measured_requests_per_point_and_native_graph_mode"
                                       and contract["native_protocol"]["per_mode_process_order"] == ["GRAPH_ON_NATIVE", "GRAPH_OFF_NATIVE", "GRAPH_OFF_OBSERVED"])
    checks["nsys_scope_exact"] = (contract["nsys"]["max_captures_per_point"] == 1
                                  and contract["nsys"]["domains"] == ["cuda", "nvtx"]
                                  and contract["nsys"]["arm"] == "GRAPH_OFF_OBSERVED"
                                  and contract["nsys"]["native_timing_estimator_input"] is False)
    checks["stop_rules_exact"] = (contract["stop_rules"]["local_wall_fraction_lt"] == 0.03
                                  and contract["stop_rules"]["zero_cost_whole_run_incremental_ceiling_lt"] == 0.02
                                  and contract["stop_rules"]["graph_control_absorption_gte"] == 0.85)
    matched = contract["matched_graph_control_gap"]
    checks["matched_estimator_exact"] = (matched["only_predefined_pair"] == ["MP02", "MP03"]
                                         and matched["endpoint"] == "instrumentation_OFF_native_CUDA_event_median_ms"
                                         and "MP02 = 32, MP03 = 128" in matched["normalizer"]
                                         and matched["stop_if"] == "absorption_fraction >= 0.85")
    checks["tools_exact"] = (contract["tool_denylist"] == ["NCU", "NVBit", "SASS", "Accel-Sim"]
                             and contract["holdout_execution_authorized"] is False
                             and contract["tier1_authorized"] is False
                             and contract["mechanism_design_authorized"] is False)

    model_identity = contract["model_runtime_identity"]
    checks["runtime_identity_exact"] = (model_identity["accepted_runtime_environment"] == str(ENV_PYTHON.parent.parent)
                                        and model_identity["vllm_tag"] == "v0.30.0"
                                        and model_identity["vllm_source_commit"] == "ced6857afa0ea7b2e3f0846a62e1394e90f15607")
    package_info = json.loads(subprocess.check_output([
        str(ENV_PYTHON), "-c", "import json,importlib.metadata as m; print(json.dumps({'vllm':m.version('vllm'),'torch':m.version('torch')},sort_keys=True))"
    ], text=True))
    checks["runtime_packages_exact"] = package_info["vllm"] == "0.30.0"

    v1 = repo / "util/vm_tlb/c16/stagea_runtime_qualification/runner.py"
    v2 = repo / "util/vm_tlb/c16/stagea_dense_first_tier0/observer_v2_authority.py"
    checks["bf16_observer_v1_exact"] = sha(v1) == contract["observer"]["bf16_v1_runner_sha256"]
    checks["awq_observer_v2_exact"] = sha(v2) == contract["observer"]["awq_v2_runner_sha256"]

    # Freeze and validate auxiliary contract artifacts.
    auxiliary = {}
    for name in ("POINT_TOKEN_BINDINGS.tsv", "RESULT_SCHEMA.json", "EXECUTION_AND_ESTIMATOR_NOTES.md", "FINAL_DECISION.json", "AUTHORITY_VERIFICATION.json"):
        raw = git(repo, "show", f"{CONTRACT_COMMIT}:{CONTRACT_DIR}/{name}", binary=True)
        path = out / name
        path.write_bytes(raw)
        auxiliary[name] = hashlib.sha256(raw).hexdigest()
    final_contract_decision = json.loads((out / "FINAL_DECISION.json").read_text())
    checks["final_contract_decision_exact"] = (final_contract_decision["status"] == "STAGEA_DENSE_FIRST_TIER0_CONTRACT_FINALIZED"
                                               and final_contract_decision["execution_authorized"] is True)

    bindings = read_tsv_text((out / "POINT_TOKEN_BINDINGS.tsv").read_text())
    receipt_text = git(repo, "show", f"c3f625e46adb8d5c4082ded8b61858c710e1f4e9:{ASSET_DIR}/TOKENIZATION_RECEIPTS.tsv")
    receipt_rows = read_tsv_text(receipt_text)
    receipt_map = {(row["model_key"], row["source_text_id"]): row for row in receipt_rows}
    token_rechecks = []
    point_inputs = {point: [] for point in contract["point_allowlist_in_order"]}
    for binding in bindings:
        authority = receipt_map[(binding["model_key"], binding["source_text_id"])]
        relative = ASSET_DIR / binding["token_ids_relative_path"]
        path = repo / relative
        tokens = json.loads(path.read_text())
        file_digest = sha(path)
        token_digest = sha_json(tokens)
        commit_bytes = git(repo, "show", f"c3f625e46adb8d5c4082ded8b61858c710e1f4e9:{relative}", binary=True)
        status = "PASS" if (
            binding["source_utf8_sha256"] == authority["source_utf8_sha256"]
            and binding["tokenizer_revision"] == authority["tokenizer_revision"]
            and binding["token_ids_sha256"] == authority["token_ids_sha256"] == token_digest
            and binding["token_id_file_sha256"] == authority["token_id_file_sha256"] == file_digest
            and commit_bytes == path.read_bytes() and len(tokens) == 512
        ) else "FAIL"
        row = {
            "point": binding["point_id"], "source_id": binding["source_text_id"],
            "model_key": binding["model_key"], "model_revision": model_identity[binding["model_key"]]["revision"],
            "tokenizer_revision": binding["tokenizer_revision"], "source_utf8_sha256": binding["source_utf8_sha256"],
            "token_ids_sha256": token_digest, "token_id_file_sha256": file_digest,
            "token_count": len(tokens), "path": str(path), "status": status,
        }
        token_rechecks.append(row)
        point_inputs[binding["point_id"]].append(row)
    checks["all_token_bindings_exact"] = all(row["status"] == "PASS" for row in token_rechecks)
    checks["binding_counts_exact"] = {point: len(rows) for point, rows in point_inputs.items()} == {"MP01": 1, "MP02": 1, "MP03": 4, "MP05": 1}
    write_tsv(out / "TOKENIZATION_RECHECK.tsv", token_rechecks,
              ["point", "source_id", "model_key", "model_revision", "tokenizer_revision", "source_utf8_sha256", "token_ids_sha256", "token_id_file_sha256", "token_count", "path", "status"])

    asset_checks = []
    for model_key, receipt_name in (("QWEN_BF16", "QWEN_BF16_ASSET_RECEIPT.json"), ("QWEN_AWQ", "QWEN_AWQ_ASSET_RECEIPT.json")):
        asset = json.loads((repo / ASSET_DIR / receipt_name).read_text())
        root = MODEL_PATHS[model_key]
        for row in asset["files"]:
            path = root / row["path"]
            ok = path.is_file() and path.stat().st_size == row["size_bytes"] and sha(path) == row["sha256"]
            asset_checks.append({"model_key": model_key, "path": row["path"], "pass": ok})
    checks["all_model_asset_hashes_exact"] = all(row["pass"] for row in asset_checks)

    points = {}
    for point in contract["point_allowlist_in_order"]:
        spec = contract["points"][point]
        model_key = spec["target"]
        decode = 1 if point == "MP01" else 32
        points[point] = {
            "model_kind": model_key,
            "model_revision": model_identity[model_key]["revision"],
            "model_path": str(MODEL_PATHS[model_key]),
            "phase": spec["phase"],
            "batch_size": spec["batch"],
            "decode_tokens": decode,
            "native_timing_endpoint": "prefill_request_cuda_event_ms" if point == "MP01" else "natural_request_D0_D31_cuda_event_ms",
            "gpu_active_cap_seconds": spec["cap_seconds"],
            "observer_identity": "V2" if point == "MP05" else "V1",
            "observer_source": str(v2 if point == "MP05" else v1),
            "observer_source_sha256": sha(v2 if point == "MP05" else v1),
            "per_occurrence_cuda_events": 0 if point == "MP05" else 2,
            "input_jsons": [row["path"] for row in point_inputs[point]],
            "inputs": point_inputs[point],
            "expected_semantic_occurrences": 144 if point == "MP01" else 4608,
            "no_requantization": True if point == "MP05" else "NOT_APPLICABLE",
        }
    campaign_config = {
        "status": "READY_FOR_LOCKED_GPU_CAMPAIGN" if all(checks.values()) else "CPU_PREFLIGHT_FAILED",
        "contract_commit": CONTRACT_COMMIT, "contract_tree": CONTRACT_TREE,
        "contract_json_sha256": CONTRACT_SHA,
        "point_allowlist": contract["point_allowlist_in_order"],
        "total_gpu_active_cap_seconds": contract["gpu_budget"]["total_gpu_active_seconds_cap"],
        "python": str(ENV_PYTHON),
        "runner": str(repo / "util/vm_tlb/c16/stagea_dense_first_tier0/runner.py"),
        "nsys_extract": str(repo / "util/vm_tlb/c16/stagea_dense_first_tier0/nsys_extract.py"),
        "gpu_name": "NVIDIA GeForce RTX 4080", "gpu_uuid": "GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59",
        "driver_version": "580.178.04",
        "graph_control_estimator": "MP02_MP03_PER_GENERATED_TOKEN_NATIVE_MEDIAN",
        "points": points,
    }
    write_json(out / "POINT_CONFIG.json", campaign_config)
    authority = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "contract_commit": CONTRACT_COMMIT, "contract_tree": CONTRACT_TREE,
        "contract_json_sha256": CONTRACT_SHA, "contract_path_in_commit": contract_git_path,
        "authority_commits": AUTHORITIES, "auxiliary_artifact_sha256": auxiliary,
        "checks": checks,
    }
    write_json(out / "CONTRACT_AUTHORITY.json", authority)
    preflight = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks, "runtime_packages": package_info,
        "asset_file_checks": asset_checks,
        "cuda_initialized": False, "model_loaded": False, "gpu_lock_acquired": False,
    }
    write_json(out / "CPU_PREFLIGHT.json", preflight)
    print(json.dumps({"status": preflight["status"], "checks": checks}, sort_keys=True))
    if preflight["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
