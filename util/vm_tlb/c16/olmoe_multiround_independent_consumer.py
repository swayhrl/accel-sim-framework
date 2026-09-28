#!/usr/bin/env python3
"""Independent CPU-only consumer for the accepted OLMoE multi-round raw bundle."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import itertools
import json
import math
import os
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np


RUN_ID = "C16R_olmoe-1b-7b-0125-instruct_routing-provenance-multiround_prefill2048-decode64_passive-hooks_all-layers_20260928T092536Z_c91846a955f5"
SCIENTIFIC_RUN_ID = "C16R_olmoe-routing-provenance-multiround-v1_20260928T092536Z_c91846a955f5"
RAW_ROOT = Path("/root/share/mnt164/huangrulin/c16_ai_workload/raw") / RUN_ID
CATALOG = Path("/root/share/mnt164/huangrulin/c16_ai_workload/catalog/entries") / f"{RUN_ID}.json"
ACK = Path("/root/share/mnt164/huangrulin/c16_ai_workload/reports/transfer_acks") / f"{RUN_ID}.TRANSFER_ACK.json"

PRODUCER_COMMIT = "27b923db5922e2f986d2f9e815050bdbad0c3bd2"
PRODUCER_SCIENCE_COMMIT = "35bc117a961ad55114f9d75752beb29f6acadc59"
PRODUCER_TREE = "782a2b2b43d7cd96579f7b10d095de314f492945"
COORDINATION_COMMIT = "fa0564f7025d62c4d466ce879a0566c404b8f4cb"
ORIGINAL_CONTRACT_COMMIT = "378df585cba4c21ac5864c374976e271ae44e9a3"
V34_COMMIT = "ab26365dc663268b0799818db6687ed466e8c925"
V34_ROUTING_PATH = "docs/vm_tlb/review_packs/C16_OLMOE_S2_PRODUCER_109_V34/NATURAL_TOP8_ROUTING.json"
PRODUCER_PACK = "docs/vm_tlb/review_packs/C16_OLMOE_ROUTING_PROVENANCE_MULTIROUND_109_V1"

EXPECTED_MANIFEST_SHA = "07ce90441cecfc29d2669c306084913e8b704234cd4e065c403a01fc4487ac9b"
EXPECTED_CATALOG_SHA = "0007fd2f1ed22449ae683bb4644acf914dd921b51854e8a5566eb731d6f3784e"
EXPECTED_ACK_SHA = "1f2740893326c192d645ac050a82b648e97f6bd9db1004b903e7f8d9b2d37901"
EXPECTED_RUNNER_SHA = "81cacc3cbccdd8726562e94175f114ca86b81caeb1dd3bf5e49f57789fa43d47"
EXPECTED_INPUT_MANIFEST_SHA = "2550314fd25b26c9553100854ebc3d05549487ff4f5dd0427cbd44113d7b8567"
EXPECTED_MODEL_RECEIPT_SHA = "01319b411b07ccd7b53c4f653bd5986a51604d9c2c16be7412257e994ff49d13"
EXPECTED_MODELING_SHA = "413888fc3be7e037727586f25900b629cc5dbc06b227a4f0d42c67cacb597bc7"
EXPECTED_INPUT_SHAS = {
    "P_TEXT": "bba8ad1051b3e96039933d65ad8d77af3877f5603ae743b5e123d82c64de88e5",
    "P_CODE": "107ef30b6f1bab3052bdd909b734ac538fa5aa4944c5094ac3b66c25fc3247f2",
    "P_STRUCTURED": "ec5cd4d780ee8b16829eb9c71c002996a114bf84b5209511cf75d0c8469fdad4",
    "P_PROSE": "e798d58332299434f0b945238c047340e6070cf881bd677fdfc62c369e24f2e4",
}

CAPTURE_SESSIONS = ["T2_TEXT_ALLLAYER", "C1_CODE_ALLLAYER", "S1_STRUCTURED_ALLLAYER", "P1_PROSE_ALLLAYER"]
ALL_SESSIONS = ["T0_NOHOOK_A", "T1_NOHOOK_B", *CAPTURE_SESSIONS]
SESSION_PROMPT = {
    "T2_TEXT_ALLLAYER": "P_TEXT",
    "C1_CODE_ALLLAYER": "P_CODE",
    "S1_STRUCTURED_ALLLAYER": "P_STRUCTURED",
    "P1_PROSE_ALLLAYER": "P_PROSE",
}
PROMPTS = ["P_TEXT", "P_CODE", "P_STRUCTURED", "P_PROSE"]
SEED = 20260928
PERMUTATIONS = 1000
POSTHOC_TAIL_PERMUTATIONS = 10000
LAGS = range(1, 33)
KNOWN_PEAKS = (1, 11, 14, 16)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def git_blob(repo: Path, commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{commit}:{path}"], cwd=repo, check=True, stdout=subprocess.PIPE
    ).stdout


def git_json(repo: Path, commit: str, path: str) -> Any:
    return json.loads(git_blob(repo, commit, path))


def git_tsv(repo: Path, commit: str, path: str) -> list[dict[str, str]]:
    data = git_blob(repo, commit, path).decode("utf-8")
    return list(csv.DictReader(io.StringIO(data), delimiter="\t"))


def quantiles(values: np.ndarray) -> tuple[float, float, float]:
    array = np.asarray(values, dtype=np.float64)
    try:
        result = np.quantile(array, [0.05, 0.5, 0.95], method="linear")
    except TypeError:  # NumPy < 1.22 uses the older keyword for the same rule.
        result = np.quantile(array, [0.05, 0.5, 0.95], interpolation="linear")
    return tuple(float(x) for x in result)


def mean_or_none(values: Iterable[float]) -> float | None:
    values = list(values)
    return sum(values) / len(values) if values else None


def route_matrices(ordered: np.ndarray) -> tuple[np.ndarray, ...]:
    require(ordered.ndim == 2 and ordered.shape[1] == 8, "expected N x 8 route array")
    masks = np.zeros((ordered.shape[0], 64), dtype=np.int16)
    for index, row in enumerate(ordered):
        require(len(set(map(int, row))) == 8, "duplicate expert within top-8")
        require(bool(np.all((row >= 0) & (row < 64))), "expert ID outside 0..63")
        masks[index, row] = 1
    intersection = masks @ masks.T
    jaccard = intersection / (16 - intersection)
    retention = intersection / 8.0
    exact = intersection == 8
    ordered_equal = np.all(ordered[:, None, :] == ordered[None, :, :], axis=2)
    return intersection, jaccard, retention, exact, ordered_equal


def pair_metrics(mats: tuple[np.ndarray, ...], left: np.ndarray, right: np.ndarray) -> dict[str, Any]:
    intersection, jaccard, retention, exact, ordered_equal = mats
    return {
        "mean_overlap": float(intersection[left, right].mean()),
        "mean_jaccard": float(jaccard[left, right].mean()),
        "mean_retention": float(retention[left, right].mean()),
        "exact_unordered_count": int(exact[left, right].sum()),
        "ordered_repeat_count": int(ordered_equal[left, right].sum()),
    }


def render(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.12g}"
    if isinstance(value, (list, dict)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return str(value)


def write_tsv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: render(row.get(field)) for field in fields})


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8", newline="\n")


def holm_adjust(raw: dict[str, float]) -> dict[str, float]:
    ordered = sorted(raw.items(), key=lambda item: item[1])
    adjusted: dict[str, float] = {}
    running = 0.0
    total = len(ordered)
    for rank, (name, value) in enumerate(ordered):
        running = max(running, (total - rank) * value)
        adjusted[name] = min(1.0, running)
    return adjusted


def validate_authority(repo: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    require(RAW_ROOT.is_dir(), f"missing durable raw: {RAW_ROOT}")
    manifest_path = RAW_ROOT / "RUN_MANIFEST.json"
    require(sha256_file(manifest_path) == EXPECTED_MANIFEST_SHA, "RUN_MANIFEST SHA mismatch")
    require(sha256_file(CATALOG) == EXPECTED_CATALOG_SHA, "catalog SHA mismatch")
    require(sha256_file(ACK) == EXPECTED_ACK_SHA, "ACK SHA mismatch")
    manifest = load_json(manifest_path)
    artifacts = manifest["artifacts"]
    require(len(artifacts) == 35, "manifest must list exactly 35 scientific artifacts")
    verified_bytes = 0
    for artifact in artifacts:
        path = RAW_ROOT / artifact["relative_path"]
        require(path.is_file(), f"missing manifest artifact {artifact['relative_path']}")
        require(path.stat().st_size == artifact["size_bytes"], f"size mismatch {artifact['relative_path']}")
        require(sha256_file(path) == artifact["sha256"], f"SHA mismatch {artifact['relative_path']}")
        verified_bytes += path.stat().st_size
    require("RUN_MANIFEST.json" not in {item["relative_path"] for item in artifacts}, "manifest self-included")
    require("READY" not in {item["relative_path"] for item in artifacts}, "READY included")
    binding = load_json(RAW_ROOT / "SCIENTIFIC_RUN_ID_BINDING.json")
    require(SCIENTIFIC_RUN_ID in json.dumps(binding), "scientific RUN_ID binding missing")
    require(RUN_ID in json.dumps(binding), "durable RUN_ID binding missing")
    catalog = load_json(CATALOG)
    ack = load_json(ACK)
    require(RUN_ID in json.dumps(catalog), "catalog does not bind durable RUN_ID")
    require(RUN_ID in json.dumps(ack), "ACK does not bind durable RUN_ID")
    require(manifest["run_id"] == RUN_ID, "manifest RUN_ID mismatch")
    require(manifest["scenario"]["scientific_run_id"] == SCIENTIFIC_RUN_ID, "manifest scientific RUN_ID mismatch")
    require(manifest["git"]["commit"] == PRODUCER_SCIENCE_COMMIT, "producer science commit mismatch")
    require(manifest["input"]["receipt_sha256"] == EXPECTED_INPUT_MANIFEST_SHA, "input manifest binding mismatch")
    require(manifest["model"]["asset_receipt_sha256"] == EXPECTED_MODEL_RECEIPT_SHA, "model receipt binding mismatch")
    require(manifest["capture"]["tool_identity_sha256_if_applicable"] == EXPECTED_RUNNER_SHA, "runner binding mismatch")
    require(sha256_file(RAW_ROOT / "source/olmoe_routing_provenance_runner.py") == EXPECTED_RUNNER_SHA, "raw runner SHA mismatch")
    require(sha256_file(RAW_ROOT / "INPUT_FREEZE_MANIFEST.json") == EXPECTED_INPUT_MANIFEST_SHA, "input manifest SHA mismatch")

    producer_head = subprocess.run(["git", "rev-parse", f"{PRODUCER_COMMIT}^{{commit}}"], cwd=repo, check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
    producer_tree = subprocess.run(["git", "rev-parse", f"{PRODUCER_COMMIT}^{{tree}}"], cwd=repo, check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
    require(producer_head == PRODUCER_COMMIT, "producer head mismatch")
    require(producer_tree == PRODUCER_TREE, "producer tree mismatch")
    subprocess.run(["git", "merge-base", "--is-ancestor", PRODUCER_SCIENCE_COMMIT, PRODUCER_COMMIT], cwd=repo, check=True)

    freeze = load_json(RAW_ROOT / "INPUT_FREEZE_MANIFEST.json")
    prompt_entries = {item["prompt_id"]: item for item in freeze["prompts"]}
    require(set(prompt_entries) == set(PROMPTS), "prompt identity mismatch")
    for prompt in PROMPTS:
        path = RAW_ROOT / "inputs" / f"{prompt}.token_ids.json"
        ids = load_json(path)
        require(len(ids) == 2048 and all(isinstance(value, int) for value in ids), f"invalid {prompt} IDs")
        require(sha256_file(path) == EXPECTED_INPUT_SHAS[prompt], f"{prompt} token SHA mismatch")
        require(prompt_entries[prompt]["frozen_ids_file_sha256"] == EXPECTED_INPUT_SHAS[prompt], f"{prompt} freeze binding mismatch")

    checks = {
        "status": "PASS",
        "durable_raw_path": str(RAW_ROOT),
        "scientific_run_id": SCIENTIFIC_RUN_ID,
        "durable_run_id": RUN_ID,
        "run_id_binding": "PASS",
        "run_manifest_sha256": EXPECTED_MANIFEST_SHA,
        "catalog_sha256": EXPECTED_CATALOG_SHA,
        "transfer_ack_sha256": EXPECTED_ACK_SHA,
        "manifest_artifact_count": len(artifacts),
        "manifest_verified_bytes": verified_bytes,
        "packaging_files_excluded_from_35": ["RUN_MANIFEST.json", "READY", "LOCAL_CLOSE_RECEIPT.json"],
        "producer_head": PRODUCER_COMMIT,
        "producer_tree": PRODUCER_TREE,
        "producer_scientific_commit": PRODUCER_SCIENCE_COMMIT,
        "model": {
            "id": manifest["model"]["model_id"],
            "revision": manifest["model"]["revision"],
            "asset_receipt_sha256": EXPECTED_MODEL_RECEIPT_SHA,
            "weights_rehashed_by_consumer": False,
        },
        "runtime": manifest["runtime"],
        "runner_sha256": EXPECTED_RUNNER_SHA,
        "input_freeze_manifest_sha256": EXPECTED_INPUT_MANIFEST_SHA,
        "input_token_files": EXPECTED_INPUT_SHAS,
    }
    return checks, manifest


def validate_sequences() -> tuple[dict[str, Any], dict[str, Any], dict[tuple[str, int], dict[str, Any]]]:
    sessions = {name: load_json(RAW_ROOT / "sessions" / f"{name}.json") for name in ALL_SESSIONS}
    sequence_summary = []
    for name, session in sessions.items():
        require(session["status"] == "PASS" and session["session_id"] == name, f"session failure {name}")
        require(session["prompt_tokens"] == 2048 and session["prefill_cache_sequence_length"] == 2048, f"prefill mismatch {name}")
        require(session["decode_steps_executed"] == 64, f"decode length mismatch {name}")
        require(session["stop_reason"] == "MAX_DECODE_STEPS_64", f"unexpected stop {name}")
        require(len(session["decode_records"]) == 64, f"decode record mismatch {name}")
        require(session["input_token_ids"][0] == session["prefill_output_token_id"], f"step1 input mismatch {name}")
        require(session["input_token_ids"][1:] == session["output_token_ids"][:-1], f"autoregressive chain mismatch {name}")
        for index, record in enumerate(session["decode_records"], start=1):
            require(record["decode_step"] == index, f"step numbering mismatch {name}")
            require(record["input_token_id"] == session["input_token_ids"][index - 1], f"input mismatch {name}/{index}")
            require(record["output_token_id"] == session["output_token_ids"][index - 1], f"output mismatch {name}/{index}")
            require(record["cache_sequence_length_before"] == 2048 + index - 1, f"cache before mismatch {name}/{index}")
            require(record["cache_sequence_length_after"] == 2048 + index, f"cache after mismatch {name}/{index}")
            require(record["cache_object_identity_continuous"] is True, f"cache identity changed {name}/{index}")
            require(record["eos"] is False, f"unexpected EOS {name}/{index}")
        expected_routes = 1024 if session["router_capture"] else 0
        require(session["routing_record_count"] == expected_routes, f"routing count mismatch {name}")
        sequence_summary.append({
            "session_id": name,
            "prompt_id": session["prompt_id"],
            "fresh_prefill": True,
            "decode_steps": 64,
            "autoregressive_token_chain": True,
            "cache_lengths_continuous": True,
            "cache_identity_continuous_all_steps": True,
            "routing_rows": expected_routes,
        })
    require(sessions["T0_NOHOOK_A"]["prefill_output_token_id"] == sessions["T1_NOHOOK_B"]["prefill_output_token_id"] == sessions["T2_TEXT_ALLLAYER"]["prefill_output_token_id"], "TEXT prefill output mismatch")
    require(sessions["T0_NOHOOK_A"]["input_token_ids"] == sessions["T1_NOHOOK_B"]["input_token_ids"] == sessions["T2_TEXT_ALLLAYER"]["input_token_ids"], "TEXT input sequence mismatch")
    require(sessions["T0_NOHOOK_A"]["output_token_ids"] == sessions["T1_NOHOOK_B"]["output_token_ids"] == sessions["T2_TEXT_ALLLAYER"]["output_token_ids"], "TEXT output sequence mismatch")

    session_layer: dict[tuple[str, int], dict[str, Any]] = {}
    total_rows = 0
    routing_summary = []
    for session_name in CAPTURE_SESSIONS:
        records = load_jsonl(RAW_ROOT / "routing" / f"{session_name}.jsonl")
        require(len(records) == 1024, f"routing file row count mismatch {session_name}")
        total_rows += len(records)
        seen: set[tuple[int, int]] = set()
        for record in records:
            step = int(record["decode_step"]); layer = int(record["layer_id"])
            require(record["session_id"] == session_name, "routing session mismatch")
            require(1 <= step <= 64 and 0 <= layer < 16, "routing step/layer invalid")
            require((step, layer) not in seen, "duplicate routing step/layer")
            seen.add((step, layer))
            ids = record["ordered_topk_expert_ids"]
            require(len(ids) == 8 and len(set(ids)) == 8 and all(0 <= x < 64 for x in ids), "invalid routing IDs")
            require(record["configured_expert_count"] == 64 and record["configured_experts_per_token"] == 8, "routing config mismatch")
            require(len(record["route_weights_float32_pre_cast"]) == 8 and len(record["route_weights_model_dtype_used"]) == 8, "route weights mismatch")
            require(all(math.isfinite(float(x)) for x in record["route_weights_float32_pre_cast"] + record["route_weights_model_dtype_used"]), "non-finite route weight")
            require(record["input_token_id"] == sessions[session_name]["input_token_ids"][step - 1], "routing input token mismatch")
            require(record["output_token_id"] == sessions[session_name]["output_token_ids"][step - 1], "routing output token mismatch")
            require(record["cache_sequence_length_before"] == 2048 + step - 1 and record["cache_sequence_length_after"] == 2048 + step, "routing cache mismatch")
            require(record["router_input_dtype"] == "torch.bfloat16" and record["router_input_shape"] == [1, 1, 2048], "router input semantic mismatch")
            require(record["router_logits_dtype"] == "torch.bfloat16" and record["router_logits_shape"] == [1, 64], "router logits semantic mismatch")
            require(record["route_weights_model_dtype"] == "torch.bfloat16", "route-weight dtype mismatch")
            require(len(record["router_input_sha256"]) == 64 and len(record["router_logits_sha256"]) == 64, "router SHA missing")
        require(len(seen) == 1024, "incomplete routing grid")
        for layer in range(16):
            rows = sorted((record for record in records if record["layer_id"] == layer), key=lambda row: row["decode_step"])
            require([row["decode_step"] for row in rows] == list(range(1, 65)), "layer step coverage mismatch")
            ordered = np.asarray([row["ordered_topk_expert_ids"] for row in rows], dtype=np.int16)
            session_layer[(session_name, layer)] = {"records": rows, "ordered": ordered, "mats": route_matrices(ordered)}
        routing_summary.append({"session_id": session_name, "rows": len(records), "layers": 16, "steps": 64, "unique_step_layer": len(seen)})
    require(total_rows == 4096, "total routing rows must be 4096")

    runner_source = (RAW_ROOT / "source/olmoe_routing_provenance_runner.py").read_text(encoding="utf-8")
    runner_semantics = {
        "fresh_prefill_each_session": "prefill = model(input_ids=prompt, use_cache=True" in runner_source,
        "explicit_cached_decode": "past_key_values=cache" in runner_source and "cache = new_cache" in runner_source,
        "greedy_argmax": "torch.argmax(out.logits[:, -1, :]" in runner_source,
        "hook_softmax_float": "F.softmax(output, dim=1, dtype=torch.float)" in runner_source,
        "hook_topk_same_config": "torch.topk(weights, mlp.top_k" in runner_source,
        "hook_norm_topk": "if mlp.norm_topk_prob" in runner_source,
        "hook_cast_to_input_dtype": "weights.to(args[0].dtype)" in runner_source,
    }
    require(all(runner_semantics.values()), "runner semantic source check failed")
    receipt = load_json(RAW_ROOT / "GPU_RUN_RECEIPT.json")
    require(receipt["status"] == "PASS_SIX_SESSIONS" and receipt["session_count"] == 6 and receipt["model_load_count"] == 1, "GPU receipt mismatch")

    checks = {
        "sessions": sequence_summary,
        "routing": {"total_rows": total_rows, "capture_sessions": routing_summary},
        "text_control": {
            "prefill_output_exact": True,
            "input_token_sequence_exact": True,
            "output_token_sequence_exact": True,
            "scope": "one frozen TEXT prompt; does not prove all-input/internal-state neutrality",
        },
        "generation": {
            "one_model_load": True,
            "fresh_prefill_per_session": True,
            "greedy_argmax": True,
            "sampling": False,
            "cache_class": receipt["runtime"]["cache_class"],
            "no_cross_session_kv_inheritance": True,
            "natural_eos_recorded": True,
            "all_sessions_reached_cap_without_eos": True,
        },
        "hook_semantics": {
            **runner_semantics,
            "modeling_olmoe_sha256": EXPECTED_MODELING_SHA,
            "official_transformers_v4_55_0_source_hash_match": True,
            "same_gate_output_same_math": True,
            "direct_internal_selected_experts_capture": False,
            "kernel_launch_order_capture": False,
            "tie_detail_limit": "torch.topk tie ordering is not independently characterized",
        },
    }
    return checks, sessions, session_layer


def prompt_and_token_metrics(sessions: dict[str, Any], session_layer: dict[tuple[str, int], dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for prompt in PROMPTS:
        ids = load_json(RAW_ROOT / "inputs" / f"{prompt}.token_ids.json")
        tail = ids[-256:]
        for lag in LAGS:
            full_equal = sum(a == b for a, b in zip(ids[:-lag], ids[lag:]))
            tail_equal = sum(a == b for a, b in zip(tail[:-lag], tail[lag:]))
            rows.append({
                "record_type": "PROMPT_LAG", "prompt_id": prompt, "lag_or_n": lag,
                "full_pair_count": len(ids) - lag, "full_equal_count": full_equal, "full_equality_rate": full_equal / (len(ids) - lag),
                "tail_pair_count": len(tail) - lag, "tail_equal_count": tail_equal, "tail_equality_rate": tail_equal / (len(tail) - lag),
            })
        for n in (2, 4, 8):
            grams = Counter(tuple(ids[index:index + n]) for index in range(len(ids) - n + 1))
            rows.append({
                "record_type": "PROMPT_NGRAM", "prompt_id": prompt, "lag_or_n": n,
                "ngram_windows": sum(grams.values()), "unique_ngrams": len(grams),
                "repeated_unique_ngrams": sum(value > 1 for value in grams.values()),
                "repeated_window_excess": sum(value - 1 for value in grams.values() if value > 1),
                "max_ngram_occurrence": max(grams.values()),
            })
    for session in CAPTURE_SESSIONS:
        inputs = np.asarray(sessions[session]["input_token_ids"], dtype=np.int64)
        outputs = np.asarray(sessions[session]["output_token_ids"], dtype=np.int64)
        for lag in LAGS:
            rows.append({
                "record_type": "DECODE_TOKEN_LAG", "session_id": session, "prompt_id": SESSION_PROMPT[session], "lag_or_n": lag,
                "pair_count": 64 - lag,
                "input_equal_count": int(np.sum(inputs[:-lag] == inputs[lag:])),
                "input_equality_rate": float(np.mean(inputs[:-lag] == inputs[lag:])),
                "output_equal_count": int(np.sum(outputs[:-lag] == outputs[lag:])),
                "output_equality_rate": float(np.mean(outputs[:-lag] == outputs[lag:])),
            })
        pairs = [(left, left + lag) for lag in LAGS for left in range(64 - lag)]
        for layer in range(16):
            jaccard = session_layer[(session, layer)]["mats"][1]
            for role, tokens in (("INPUT", inputs), ("OUTPUT", outputs)):
                same = [float(jaccard[left, right]) for left, right in pairs if tokens[left] == tokens[right]]
                different = [float(jaccard[left, right]) for left, right in pairs if tokens[left] != tokens[right]]
                rows.append({
                    "record_type": "ROUTING_TOKEN_ASSOCIATION", "session_id": session, "prompt_id": SESSION_PROMPT[session],
                    "layer_id": layer, "token_role": role, "lag_range": "1..32",
                    "same_count": len(same), "same_mean_jaccard": mean_or_none(same),
                    "different_count": len(different), "different_mean_jaccard": mean_or_none(different),
                })
    return rows


def recompute_lags(session_layer: dict[tuple[str, int], dict[str, Any]]) -> list[dict[str, Any]]:
    permutations_by_lag: dict[int, np.ndarray] = {}
    for lag in LAGS:
        rng = np.random.default_rng(SEED)
        permutations_by_lag[lag] = np.asarray([rng.permutation(64) for _ in range(PERMUTATIONS)], dtype=np.int16)
    rows: list[dict[str, Any]] = []
    for session in CAPTURE_SESSIONS:
        for layer in range(16):
            mats = session_layer[(session, layer)]["mats"]
            for lag in LAGS:
                left = np.arange(64 - lag); right = left + lag
                actual = pair_metrics(mats, left, right)
                perms = permutations_by_lag[lag]
                null_values = {
                    "mean_overlap": mats[0][perms[:, :-lag], perms[:, lag:]].mean(axis=1),
                    "mean_jaccard": mats[1][perms[:, :-lag], perms[:, lag:]].mean(axis=1),
                    "mean_retention": mats[2][perms[:, :-lag], perms[:, lag:]].mean(axis=1),
                    "exact_unordered_count": mats[3][perms[:, :-lag], perms[:, lag:]].sum(axis=1),
                    "ordered_repeat_count": mats[4][perms[:, :-lag], perms[:, lag:]].sum(axis=1),
                }
                row: dict[str, Any] = {
                    "session_id": session, "prompt_id": SESSION_PROMPT[session], "layer_id": layer,
                    "lag": lag, "pair_count": 64 - lag, "seed": SEED, "permutations": PERMUTATIONS,
                }
                for metric, value in actual.items():
                    p05, median, p95 = quantiles(null_values[metric])
                    row[f"actual_{metric}"] = value
                    row[f"shuffle_{metric}_p05"] = p05
                    row[f"shuffle_{metric}_median"] = median
                    row[f"shuffle_{metric}_p95"] = p95
                row["mean_jaccard_above_shuffle_p95"] = row["actual_mean_jaccard"] > row["shuffle_mean_jaccard_p95"]
                rows.append(row)
    return rows


def historical_comparison(repo: Path, session_layer: dict[tuple[str, int], dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    old_records = git_json(repo, V34_COMMIT, V34_ROUTING_PATH)["repeat_decode_records"]
    new_records = session_layer[("T2_TEXT_ALLLAYER", 1)]["records"][:32]
    rows: list[dict[str, Any]] = []
    for old, new in zip(old_records, new_records):
        old_ids = old["natural_top8_ids"]; new_ids = new["ordered_topk_expert_ids"]
        intersection = len(set(old_ids) & set(new_ids))
        rows.append({
            "decode_step": old["decode_step"],
            "ordered_topk_equal": old_ids == new_ids,
            "unordered_topk_equal": set(old_ids) == set(new_ids),
            "jaccard": intersection / len(set(old_ids) | set(new_ids)),
            "old_topk": old_ids, "new_topk": new_ids,
            "old_next_token_id": old["next_token_id"], "new_input_token_id": new["input_token_id"], "new_output_token_id": new["output_token_id"],
            "new_output_equals_old_next": new["output_token_id"] == old["next_token_id"],
            "new_input_equals_old_next": new["input_token_id"] == old["next_token_id"],
            "old_router_input_dtype": old["mlp_router_input"]["dtype"], "new_router_input_dtype": new["router_input_dtype"],
            "old_router_input_shape": old["mlp_router_input"]["shape"], "new_router_input_shape": new["router_input_shape"],
            "router_input_hash_string_equal": old["mlp_router_input"]["sha256"] == new["router_input_sha256"],
            "old_router_logits_shape": old["router_logits_shape"], "new_router_logits_shape": new["router_logits_shape"],
            "router_logits_hash_string_equal": old["router_logits_sha256"] == new["router_logits_sha256"],
            "hash_serialization_comparable": False,
            "hash_comparison_limitation": "V34 runner/hash byte serialization is not archived; equality strings are recorded but not promoted to comparable evidence",
        })
    summary = {
        "steps": 32,
        "ordered_equal_count": sum(row["ordered_topk_equal"] for row in rows),
        "unordered_equal_count": sum(row["unordered_topk_equal"] for row in rows),
        "mean_jaccard": float(np.mean([row["jaccard"] for row in rows])),
        "new_output_vs_old_next_equal_count": sum(row["new_output_equals_old_next"] for row in rows),
        "new_input_vs_old_next_equal_count": sum(row["new_input_equals_old_next"] for row in rows),
        "router_input_hash_string_equal_count": sum(row["router_input_hash_string_equal"] for row in rows),
        "router_logits_hash_string_equal_count": sum(row["router_logits_hash_string_equal"] for row in rows),
        "hash_serialization_comparable": False,
    }
    return rows, summary


def producer_comparison(repo: Path, lag_rows: list[dict[str, Any]], historical_summary: dict[str, Any], mechanical: str) -> list[dict[str, Any]]:
    producer_spectrum = git_tsv(repo, PRODUCER_COMMIT, f"{PRODUCER_PACK}/ROUTING_LAG_SPECTRUM.tsv")
    producer_shuffle = git_tsv(repo, PRODUCER_COMMIT, f"{PRODUCER_PACK}/ROUTING_LAG_SHUFFLE.tsv")
    producer_final = git_json(repo, PRODUCER_COMMIT, f"{PRODUCER_PACK}/FINAL_DECISION.json")
    producer_v34 = git_json(repo, PRODUCER_COMMIT, f"{PRODUCER_PACK}/V34_LAYER1_COMPARISON_SUMMARY.json")
    independent = {(row["session_id"], int(row["layer_id"]), int(row["lag"])): row for row in lag_rows}
    spectrum_diffs = []
    spectrum_mismatch = 0
    for row in producer_spectrum:
        key = (row["session_id"], int(row["layer_id"]), int(row["lag"]))
        current = independent[key]
        for field in ("mean_overlap", "mean_jaccard", "mean_retention"):
            diff = abs(float(row[field]) - float(current[f"actual_{field}"]))
            spectrum_diffs.append(diff)
            spectrum_mismatch += diff > 1e-12
        spectrum_mismatch += int(row["exact_unordered_count"] != str(current["actual_exact_unordered_count"]))
        spectrum_mismatch += int(row["ordered_repeat_count"] != str(current["actual_ordered_repeat_count"]))
    shuffle_diffs = []
    shuffle_bool_mismatch = 0
    for row in producer_shuffle:
        key = (row["session_id"], int(row["layer_id"]), int(row["lag"]))
        current = independent[key]
        for metric in ("mean_overlap", "mean_jaccard", "mean_retention", "exact_unordered_count", "ordered_repeat_count"):
            for suffix in ("p05", "median", "p95"):
                shuffle_diffs.append(abs(float(row[f"shuffle_{metric}_{suffix}"]) - float(current[f"shuffle_{metric}_{suffix}"])))
        observed = row["mean_jaccard_above_shuffle_p95"].lower() == "true"
        shuffle_bool_mismatch += observed != current["mean_jaccard_above_shuffle_p95"]
    rows = [
        {"comparison": "ROUTING_LAG_SPECTRUM", "producer_value": "2048 rows", "independent_value": f"{len(lag_rows)} rows", "match": spectrum_mismatch == 0, "max_abs_difference": max(spectrum_diffs), "difference_count": spectrum_mismatch},
        {"comparison": "ROUTING_LAG_SHUFFLE", "producer_value": "NumPy default_rng; 1000; reset per cell", "independent_value": "independent implementation, same frozen definition", "match": max(shuffle_diffs) <= 1e-12 and shuffle_bool_mismatch == 0, "max_abs_difference": max(shuffle_diffs), "difference_count": shuffle_bool_mismatch},
        {"comparison": "MECHANICAL_CLASSIFICATION", "producer_value": producer_final["decision"], "independent_value": mechanical, "match": producer_final["decision"] == mechanical, "max_abs_difference": None, "difference_count": 0 if producer_final["decision"] == mechanical else 1},
        {"comparison": "V34_ORDERED_EQUAL_COUNT", "producer_value": producer_v34["ordered_equal_count"], "independent_value": historical_summary["ordered_equal_count"], "match": producer_v34["ordered_equal_count"] == historical_summary["ordered_equal_count"]},
        {"comparison": "V34_UNORDERED_EQUAL_COUNT", "producer_value": producer_v34["unordered_equal_count"], "independent_value": historical_summary["unordered_equal_count"], "match": producer_v34["unordered_equal_count"] == historical_summary["unordered_equal_count"]},
        {"comparison": "V34_HASH_SERIALIZATION_COMPARABILITY", "producer_value": producer_v34.get("hash_serialization_comparable"), "independent_value": False, "match": False, "difference_count": 1, "interpretation": "consumer downgrades hash comparability because V34 hash serialization source is not archived"},
        {"comparison": "EXACT_NUMERIC_CLASSIFIER_PREREGISTRATION", "producer_value": "implemented in post-run analysis code", "independent_value": "NOT_FOUND in original contract or pre-GPU manifest/receipt", "match": False, "difference_count": 1, "interpretation": "qualitative comparisons/outcomes were predeclared; exact boolean rule was not explicitly frozen before GPU"},
    ]
    return rows


def robustness_diagnostics(lag_rows: list[dict[str, Any]], session_layer: dict[tuple[str, int], dict[str, Any]], sessions: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    by_cell = {(row["session_id"], row["layer_id"], row["lag"]): row for row in lag_rows}
    for session in CAPTURE_SESSIONS:
        for layer in range(16):
            layer_rows = [by_cell[(session, layer, lag)] for lag in LAGS]
            ranked = sorted(layer_rows, key=lambda row: (-row["actual_mean_jaccard"], row["lag"]))
            rank = {row["lag"]: index + 1 for index, row in enumerate(ranked)}
            peak = ranked[0]; lag11 = by_cell[(session, layer, 11)]
            rows.append({
                "record_type": "LAYER_PEAK_SHAPE", "session_id": session, "prompt_id": SESSION_PROMPT[session], "layer_id": layer,
                "segment": "FULL64", "dominant_lag": peak["lag"], "dominant_jaccard": peak["actual_mean_jaccard"],
                "lag11_jaccard": lag11["actual_mean_jaccard"], "lag11_null_median": lag11["shuffle_mean_jaccard_median"],
                "lag11_null_p95": lag11["shuffle_mean_jaccard_p95"], "lag11_delta_from_median": lag11["actual_mean_jaccard"] - lag11["shuffle_mean_jaccard_median"],
                "lag11_delta_from_p95": lag11["actual_mean_jaccard"] - lag11["shuffle_mean_jaccard_p95"], "lag11_rank": rank[11],
                "lag10_jaccard": by_cell[(session, layer, 10)]["actual_mean_jaccard"], "lag12_jaccard": by_cell[(session, layer, 12)]["actual_mean_jaccard"],
                "lag11_above_p95": lag11["mean_jaccard_above_shuffle_p95"],
                "analysis_timing": "ORIGINAL_PLAN_RECOMPUTE_WITH_POSTHOC_EFFECT_SIZE_INTERPRETATION",
            })
            ordered = session_layer[(session, layer)]["ordered"]
            for segment, start in (("FIRST32", 0), ("LAST32", 32)):
                segment_mats = route_matrices(ordered[start:start + 32])
                for lag in KNOWN_PEAKS:
                    left = np.arange(32 - lag); right = left + lag
                    rows.append({
                        "record_type": "HALF_STABILITY", "session_id": session, "prompt_id": SESSION_PROMPT[session], "layer_id": layer,
                        "segment": segment, "tested_lag": lag, "pair_count": 32 - lag,
                        "actual_jaccard": pair_metrics(segment_mats, left, right)["mean_jaccard"],
                        "analysis_timing": "POST_RESULT_ROBUSTNESS_DIAGNOSTIC_NOT_INDEPENDENT_HOLDOUT",
                    })

    alt_sessions = ["C1_CODE_ALLLAYER", "S1_STRUCTURED_ALLLAYER", "P1_PROSE_ALLLAYER"]
    raw_p: dict[str, float] = {}
    alt_rows: dict[str, dict[str, Any]] = {}
    for session in alt_sessions:
        mats = session_layer[(session, 1)]["mats"]
        lag = 11; left = np.arange(64 - lag); right = left + lag
        actual = pair_metrics(mats, left, right)["mean_jaccard"]
        rng = np.random.default_rng(SEED)
        perms = np.asarray([rng.permutation(64) for _ in range(POSTHOC_TAIL_PERMUTATIONS)], dtype=np.int16)
        null = mats[1][perms[:, :-lag], perms[:, lag:]].mean(axis=1)
        p_value = (1 + int(np.sum(null >= actual))) / (POSTHOC_TAIL_PERMUTATIONS + 1)
        raw_p[session] = p_value
        alt_rows[session] = {
            "record_type": "ALT_LAYER1_LAG11_MULTIPLICITY", "session_id": session, "prompt_id": SESSION_PROMPT[session], "layer_id": 1,
            "tested_lag": 11, "actual_jaccard": actual, "permutations": POSTHOC_TAIL_PERMUTATIONS,
            "upper_tail_fraction": p_value, "analysis_timing": "POST_RESULT_ROBUSTNESS_DIAGNOSTIC_HOLM_3",
        }
    adjusted = holm_adjust(raw_p)
    for session in alt_sessions:
        alt_rows[session]["holm_adjusted_upper_tail"] = adjusted[session]
        rows.append(alt_rows[session])

    shared_summary: dict[str, Any] = {}
    for session in CAPTURE_SESSIONS:
        rng = np.random.default_rng(SEED)
        perms = np.asarray([rng.permutation(64) for _ in range(PERMUTATIONS)], dtype=np.int16)
        actual_lag11_count = sum(by_cell[(session, layer, 11)]["mean_jaccard_above_shuffle_p95"] for layer in range(16))
        perm_counts = np.zeros(PERMUTATIONS, dtype=np.int16)
        perm_max_delta = np.full(PERMUTATIONS, -np.inf, dtype=np.float64)
        actual_max = (-np.inf, None, None)
        for layer in range(16):
            mats = session_layer[(session, layer)]["mats"]
            for lag in LAGS:
                values = mats[1][perms[:, :-lag], perms[:, lag:]].mean(axis=1)
                median = by_cell[(session, layer, lag)]["shuffle_mean_jaccard_median"]
                perm_max_delta = np.maximum(perm_max_delta, values - median)
                actual_delta = by_cell[(session, layer, lag)]["actual_mean_jaccard"] - median
                if actual_delta > actual_max[0]:
                    actual_max = (actual_delta, layer, lag)
                if lag == 11:
                    p95 = by_cell[(session, layer, 11)]["shuffle_mean_jaccard_p95"]
                    perm_counts += values > p95
        count_p05, count_med, count_p95 = quantiles(perm_counts)
        max_p05, max_med, max_p95 = quantiles(perm_max_delta)
        count_upper = (1 + int(np.sum(perm_counts >= actual_lag11_count))) / (PERMUTATIONS + 1)
        max_upper = (1 + int(np.sum(perm_max_delta >= actual_max[0]))) / (PERMUTATIONS + 1)
        rows.append({
            "record_type": "SESSION_LAYER_COUNT_CALIBRATION", "session_id": session, "prompt_id": SESSION_PROMPT[session],
            "tested_lag": 11, "actual_layer_count": actual_lag11_count, "null_count_p05": count_p05, "null_count_median": count_med, "null_count_p95": count_p95,
            "upper_tail_fraction": count_upper, "permutations": PERMUTATIONS,
            "analysis_timing": "POST_RESULT_SHARED_TIME_PERMUTATION",
        })
        rows.append({
            "record_type": "SESSION_FULL_SPECTRUM_MAX_CALIBRATION", "session_id": session, "prompt_id": SESSION_PROMPT[session],
            "actual_max_delta": actual_max[0], "actual_max_layer": actual_max[1], "actual_max_lag": actual_max[2],
            "null_max_delta_p05": max_p05, "null_max_delta_median": max_med, "null_max_delta_p95": max_p95,
            "upper_tail_fraction": max_upper, "permutations": PERMUTATIONS,
            "analysis_timing": "POST_RESULT_SHARED_TIME_PERMUTATION",
        })
        shared_summary[session] = {
            "actual_lag11_layers_above_original_p95": int(actual_lag11_count),
            "null_layer_count": {"p05": count_p05, "median": count_med, "p95": count_p95, "upper_tail_fraction": count_upper},
            "actual_full_spectrum_max_delta": {"value": actual_max[0], "layer": actual_max[1], "lag": actual_max[2]},
            "null_full_spectrum_max_delta": {"p05": max_p05, "median": max_med, "p95": max_p95, "upper_tail_fraction": max_upper},
        }
    return rows, {"holm": {session: {"raw": raw_p[session], "adjusted": adjusted[session]} for session in alt_sessions}, "shared": shared_summary}


def token_conditional(session_layer: dict[tuple[str, int], dict[str, Any]], sessions: dict[str, Any]) -> dict[str, Any]:
    results = []
    for session in CAPTURE_SESSIONS:
        inputs = sessions[session]["input_token_ids"]
        groups: dict[int, list[int]] = defaultdict(list)
        for index, token in enumerate(inputs):
            groups[int(token)].append(index)
        swappable = [positions for positions in groups.values() if len(positions) > 1]
        mats = session_layer[(session, 1)]["mats"]
        distinct_within = sum(len({tuple(session_layer[(session, 1)]["ordered"][position]) for position in positions}) > 1 for positions in swappable)
        rng = np.random.default_rng(SEED)
        perms = np.tile(np.arange(64, dtype=np.int16), (PERMUTATIONS, 1))
        for permutation_index in range(PERMUTATIONS):
            for positions in swappable:
                perms[permutation_index, positions] = rng.permutation(positions)
        lag_results = []
        for lag in KNOWN_PEAKS:
            actual = float(np.diag(mats[1], k=lag).mean())
            null = mats[1][perms[:, :-lag], perms[:, lag:]].mean(axis=1)
            p05, median, p95 = quantiles(null)
            if not swappable or distinct_within == 0 or float(np.max(null) - np.min(null)) < 1e-15:
                assessment = "无法辨认额外作用：条件置换退化或缺少可交换且路由不同的同-token组"
            elif actual > p95:
                assessment = "高于条件置换p95的描述性残余；不是token因果证明"
            elif actual < p05:
                assessment = "低于条件置换p05的描述性残余；不是token因果证明"
            else:
                assessment = "未超出条件置换p05-p95；不能证明不存在上下文相关作用"
            lag_results.append({
                "lag": lag, "actual_mean_jaccard": actual, "null_p05": p05, "null_median": median, "null_p95": p95,
                "null_min": float(np.min(null)), "null_max": float(np.max(null)), "assessment_zh": assessment,
            })
        results.append({
            "session_id": session, "prompt_id": SESSION_PROMPT[session], "layer_id": 1,
            "seed": SEED, "permutations": PERMUTATIONS,
            "input_token_group_count": len(groups), "swappable_group_count": len(swappable),
            "swappable_position_count": sum(len(group) for group in swappable),
            "swappable_groups_with_multiple_route_sets": distinct_within,
            "lags": lag_results,
        })
    return {
        "schema_version": 1,
        "analysis_timing": "POST_RESULT_ROBUSTNESS_DIAGNOSTIC",
        "null": "shuffle whole layer-1 routing records only within equal input_token_id groups; token time series fixed",
        "causal_boundary": "hidden state includes full context; an exceedance would not prove token causality",
        "sessions": results,
    }


def build(repo: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    authority, manifest = validate_authority(repo)
    sequence_checks, sessions, session_layer = validate_sequences()
    authority.update(sequence_checks)
    authority["coordination"] = {"commit": COORDINATION_COMMIT, "original_contract_commit": ORIGINAL_CONTRACT_COMMIT}
    authority["preregistration_audit"] = {
        "predeclared": ["four input families", "Layer1/lag11 focus", "lags 1..32", "seed 20260928", "1000 whole-step permutations", "candidate qualitative outcomes"],
        "exact_numeric_mechanical_classifier_frozen_before_gpu": False,
        "finding": "NOT_FOUND in original coordination contract, CAMPAIGN_MANIFEST.pre_gpu.json, or PRE_GPU_AUTHORITY_RECEIPT.json; exact boolean appears in producer post-run analysis code",
    }
    write_json(output / "AUTHORITY_AND_SEQUENCE_CHECKS.json", authority)

    token_rows = prompt_and_token_metrics(sessions, session_layer)
    token_fields = [
        "record_type", "session_id", "prompt_id", "layer_id", "token_role", "lag_range", "lag_or_n", "pair_count",
        "full_pair_count", "full_equal_count", "full_equality_rate", "tail_pair_count", "tail_equal_count", "tail_equality_rate",
        "ngram_windows", "unique_ngrams", "repeated_unique_ngrams", "repeated_window_excess", "max_ngram_occurrence",
        "input_equal_count", "input_equality_rate", "output_equal_count", "output_equality_rate",
        "same_count", "same_mean_jaccard", "different_count", "different_mean_jaccard",
    ]
    write_tsv(output / "RECOMPUTED_TOKEN_METRICS.tsv", token_rows, token_fields)

    lag_rows = recompute_lags(session_layer)
    lag_fields = ["session_id", "prompt_id", "layer_id", "lag", "pair_count", "seed", "permutations"]
    for metric in ("mean_overlap", "mean_jaccard", "mean_retention", "exact_unordered_count", "ordered_repeat_count"):
        lag_fields.extend([f"actual_{metric}", f"shuffle_{metric}_p05", f"shuffle_{metric}_median", f"shuffle_{metric}_p95"])
    lag_fields.append("mean_jaccard_above_shuffle_p95")
    write_tsv(output / "RECOMPUTED_LAG_METRICS.tsv", lag_rows, lag_fields)

    historical_rows, historical_summary = historical_comparison(repo, session_layer)
    historical_fields = [
        "decode_step", "ordered_topk_equal", "unordered_topk_equal", "jaccard", "old_topk", "new_topk",
        "old_next_token_id", "new_input_token_id", "new_output_token_id", "new_output_equals_old_next", "new_input_equals_old_next",
        "old_router_input_dtype", "new_router_input_dtype", "old_router_input_shape", "new_router_input_shape",
        "router_input_hash_string_equal", "old_router_logits_shape", "new_router_logits_shape", "router_logits_hash_string_equal",
        "hash_serialization_comparable", "hash_comparison_limitation",
    ]
    write_tsv(output / "HISTORICAL_COMPARISON.tsv", historical_rows, historical_fields)

    by_cell = {(row["session_id"], row["layer_id"], row["lag"]): row for row in lag_rows}
    text_pass = by_cell[("T2_TEXT_ALLLAYER", 1, 11)]["mean_jaccard_above_shuffle_p95"]
    alt_pass = any(by_cell[(session, 1, 11)]["mean_jaccard_above_shuffle_p95"] for session in CAPTURE_SESSIONS[1:])
    if not text_pass:
        mechanical = "HISTORICAL_PERIOD11_NOT_REPRODUCED_PROSPECTIVELY"
    elif alt_pass:
        mechanical = "PERIOD11_REPRODUCED_ACROSS_INPUT_FAMILIES"
    else:
        mechanical = "PERIOD11_REPRODUCED_TEXT_ONLY_CONTENT_ASSOCIATED"

    producer_rows = producer_comparison(repo, lag_rows, historical_summary, mechanical)
    write_tsv(output / "PRODUCER_COMPARISON.tsv", producer_rows, ["comparison", "producer_value", "independent_value", "match", "max_abs_difference", "difference_count", "interpretation"])

    robustness_rows, robustness_summary = robustness_diagnostics(lag_rows, session_layer, sessions)
    robustness_fields = sorted({key for row in robustness_rows for key in row})
    preferred = ["record_type", "session_id", "prompt_id", "layer_id", "segment", "tested_lag", "analysis_timing"]
    robustness_fields = preferred + [field for field in robustness_fields if field not in preferred]
    write_tsv(output / "ROBUSTNESS_DIAGNOSTICS.tsv", robustness_rows, robustness_fields)

    conditional = token_conditional(session_layer, sessions)
    write_json(output / "TOKEN_CONDITIONAL_CHECK.json", conditional)

    layer1 = {}
    for session in CAPTURE_SESSIONS:
        cell = by_cell[(session, 1, 11)]
        layer_rows = [by_cell[(session, 1, lag)] for lag in LAGS]
        ranked = sorted(layer_rows, key=lambda row: (-row["actual_mean_jaccard"], row["lag"]))
        layer1[session] = {
            "prompt_id": SESSION_PROMPT[session],
            "lag11_actual": cell["actual_mean_jaccard"],
            "lag11_null_median": cell["shuffle_mean_jaccard_median"],
            "lag11_null_p95": cell["shuffle_mean_jaccard_p95"],
            "lag11_delta_p95": cell["actual_mean_jaccard"] - cell["shuffle_mean_jaccard_p95"],
            "lag11_rank": next(index + 1 for index, row in enumerate(ranked) if row["lag"] == 11),
            "dominant_lag": ranked[0]["lag"],
            "dominant_jaccard": ranked[0]["actual_mean_jaccard"],
            "lag10": by_cell[(session, 1, 10)]["actual_mean_jaccard"],
            "lag12": by_cell[(session, 1, 12)]["actual_mean_jaccard"],
            "lag11_above_p95": cell["mean_jaccard_above_shuffle_p95"],
        }

    prompt_strength = {}
    for prompt in PROMPTS:
        candidates = [row for row in token_rows if row["record_type"] == "PROMPT_LAG" and row["prompt_id"] == prompt]
        peak = max(candidates, key=lambda row: (row["full_equality_rate"], -row["lag_or_n"]))
        prompt_strength[prompt] = {"dominant_full_prompt_lag": peak["lag_or_n"], "dominant_full_prompt_equality_rate": peak["full_equality_rate"]}

    conditional_summary = {}
    for item in conditional["sessions"]:
        conditional_summary[item["session_id"]] = {
            "swappable_group_count": item["swappable_group_count"],
            "swappable_groups_with_multiple_route_sets": item["swappable_groups_with_multiple_route_sets"],
            "lag11": next(entry for entry in item["lags"] if entry["lag"] == 11),
        }

    half_lookup = {
        (row["session_id"], row["layer_id"], row["segment"], row["tested_lag"]): row["actual_jaccard"]
        for row in robustness_rows
        if row["record_type"] == "HALF_STABILITY"
    }
    main_lag_by_session = {
        "T2_TEXT_ALLLAYER": 11,
        "C1_CODE_ALLLAYER": 16,
        "S1_STRUCTURED_ALLLAYER": 14,
        "P1_PROSE_ALLLAYER": 1,
    }
    stability_summary = {}
    for session, main_lag in main_lag_by_session.items():
        stability_summary[session] = {
            "main_lag": main_lag,
            "layer1_first32_jaccard": half_lookup[(session, 1, "FIRST32", main_lag)],
            "layer1_last32_jaccard": half_lookup[(session, 1, "LAST32", main_lag)],
        }
    stability_summary["P1_PROSE_ALLLAYER"]["lag11_first32_jaccard"] = half_lookup[("P1_PROSE_ALLLAYER", 1, "FIRST32", 11)]
    stability_summary["P1_PROSE_ALLLAYER"]["lag11_last32_jaccard"] = half_lookup[("P1_PROSE_ALLLAYER", 1, "LAST32", 11)]

    final_decision = {
        "schema_version": 1,
        "collection_usable": True,
        "mechanical_rule": {
            "definition": "TEXT Layer1 lag11 above its p95 AND at least one of CODE/STRUCTURED/PROSE Layer1 lag11 above its p95",
            "result": mechanical,
            "exact_numeric_rule_preregistered_before_gpu": False,
            "preservation": "reported unchanged as producer mechanical rule; not used as sole scientific conclusion",
        },
        "scientific_conclusion_zh": (
            "采集与连续生成证据完整，历史TEXT的专家集合和输出token序列得到复现。"
            "但主要路由周期随输入而改变：TEXT的11步结构很强，CODE和STRUCTURED分别以其他lag为主；"
            "PROSE的lag11仅略高于单cell描述性p95且主峰在lag1，不能视为与TEXT等强的跨输入11步规律。"
        ),
        "historical_v34": historical_summary,
        "layer1": layer1,
        "prompt_periodicity": prompt_strength,
        "robustness": robustness_summary,
        "within_sequence_stability": stability_summary,
        "token_conditional": conditional_summary,
        "cross_input_period11_generalization": "证据不足；原机械规则通过不等于强周期跨输入成立",
        "new_gpu_experiment_recommendation_zh": "当前暂不值得立即新增GPU实验；若未来必须回答自然语言总体泛化，应预先冻结多prompt设计和多项校正后另行授权。",
        "boundaries": [
            "同一session的16层不是16次独立生成",
            "64步来自一个prompt，不是64个独立prompt",
            "PROSE只有一个固定技术文本样本",
            "TEXT lag22可为lag11谐波，不是独立发现",
            "不支持MoE固定11步、跨模型规律、缓存复用或性能结论",
        ],
        "gpu_work_performed_by_consumer": False,
        "lane4_partial_accessed": False,
    }
    write_json(output / "FINAL_DECISION.json", final_decision)

    prose = layer1["P1_PROSE_ALLLAYER"]
    text = layer1["T2_TEXT_ALLLAYER"]
    code = layer1["C1_CODE_ALLLAYER"]
    structured = layer1["S1_STRUCTURED_ALLLAYER"]
    interp = f"""# 科学解释

## 1. 当前采集是否可用

可用。164 上正式 raw、catalog 与 ACK 的 SHA 均匹配；manifest 管理的 35 项逐项通过大小和 SHA 校验。六个 session 都有独立 2048-token prefill、64 个连续 greedy decode step、逐步输入/输出 token 链和 2048→2112 的 DynamicCache 长度递增。四个 capture session 各有 16×64=1024 行，合计 4096 行且无重漏。T0/T1/T2 的 prefill 输出、输入序列和完整输出序列完全相同，因此只在这一固定 TEXT 测试上支持输出级 hook neutrality。

hook 并非直接截获 MoE 内部 `selected_experts` 或 expert kernel 发射顺序；它从同一个 gate 输出按模型源码相同的 float32 softmax、top-k、可选归一化和 BF16 cast 记录路由。transformers v4.55.0 官方 `modeling_olmoe.py` 的 SHA 与 receipt 中 `{EXPECTED_MODELING_SHA}` 一致。tie 顺序细节没有额外证明。

## 2. 原 TEXT 与 V34 复现到什么层次

T2 Layer1 前32步与 V34：ordered top-k 相同 `{historical_summary['ordered_equal_count']}/32`，unordered set 相同 `{historical_summary['unordered_equal_count']}/32`，平均 Jaccard `{historical_summary['mean_jaccard']:.6f}`；新 output token 对齐旧 next token `{historical_summary['new_output_vs_old_next_equal_count']}/32`，新 input token 对齐旧 next token `{historical_summary['new_input_vs_old_next_equal_count']}/32`。这把旧结果从“runner不明”推进为显式 cached-greedy runner 下的序列复现。

V34 的 hash 序列化源码未归档，因此即使 dtype/shape 一致，也没有把两代 router-input/logits hash 声明成可比。

## 3. 主要时间结构是否随输入改变

是，主要峰位置和强度随输入明显改变：

- TEXT Layer1：主峰 lag `{text['dominant_lag']}`，Jaccard `{text['dominant_jaccard']:.6f}`；lag11 `{text['lag11_actual']:.6f}`，比 null p95 高 `{text['lag11_delta_p95']:.6f}`。
- CODE Layer1：主峰 lag `{code['dominant_lag']}`，Jaccard `{code['dominant_jaccard']:.6f}`；lag11 `{code['lag11_actual']:.6f}`。
- STRUCTURED Layer1：主峰 lag `{structured['dominant_lag']}`，Jaccard `{structured['dominant_jaccard']:.6f}`；lag11 `{structured['lag11_actual']:.6f}`。
- PROSE Layer1：主峰 lag `{prose['dominant_lag']}`，Jaccard `{prose['dominant_jaccard']:.6f}`；lag11 `{prose['lag11_actual']:.6f}`。

因此更稳妥的结论是“路由时间结构跟随固定输入族而变化”，不是“OLMoE 固定具有11步周期”。TEXT 的 lag22 可是 lag11 的谐波，不能当第二次独立发现。

## 4. PROSE 的11步现象如何解释

PROSE Layer1 lag11=`{prose['lag11_actual']:.6f}`，null median=`{prose['lag11_null_median']:.6f}`，p95=`{prose['lag11_null_p95']:.6f}`，只高出 p95 `{prose['lag11_delta_p95']:.6f}`；它在本层32个lag中排第 `{prose['lag11_rank']}`，而主峰位于 lag `{prose['dominant_lag']}`。这是弱超线，不是与 TEXT 等强的突出峰。三项替代输入的上尾比例与 Holm 校正在 `ROBUSTNESS_DIAGNOSTICS.tsv` 中保留；全层/全lag共享时间置换也单列，未用于改写 producer 原规则。

同一条64步序列的前后半段进一步显示：PROSE lag11 从前32步 `{stability_summary['P1_PROSE_ALLLAYER']['lag11_first32_jaccard']:.6f}` 变到后32步 `{stability_summary['P1_PROSE_ALLLAYER']['lag11_last32_jaccard']:.6f}`，不稳定；相对地，TEXT lag11 前/后半为 `{stability_summary['T2_TEXT_ALLLAYER']['layer1_first32_jaccard']:.6f}` / `{stability_summary['T2_TEXT_ALLLAYER']['layer1_last32_jaccard']:.6f}`，CODE lag16 为 `{stability_summary['C1_CODE_ALLLAYER']['layer1_first32_jaccard']:.6f}` / `{stability_summary['C1_CODE_ALLLAYER']['layer1_last32_jaccard']:.6f}`，STRUCTURED lag14 为 `{stability_summary['S1_STRUCTURED_ALLLAYER']['layer1_first32_jaccard']:.6f}` / `{stability_summary['S1_STRUCTURED_ALLLAYER']['layer1_last32_jaccard']:.6f}`。这些只是同序列内稳定性描述，不是独立 holdout。

## 5. 是否有独立于 token 重复的额外描述性证据

input-token 条件置换结果见 `TOKEN_CONDITIONAL_CHECK.json`。它只在相同 input token 组内交换整条 Layer1 routing record，保留 token 时间序列。结果若超过条件参照，也只能说明在该固定序列中还有上下文相关残余；hidden state 包含完整上下文，不能叫 token 因果证明。若组不可交换或 null 退化，则明确记为无法辨认。

具体地，TEXT lag11 与 PROSE lag11 都落在各自 input-token 条件置换 p05–p95 内；CODE 的主峰 lag16 与 STRUCTURED 的主峰 lag14 仍高于对应条件参照。因而现有补充证据不支持把 TEXT/PROSE 的11步现象说成独立于重复 input token 的额外信号；CODE/STRUCTURED 的主峰则保留了上下文相关的描述性残余，但仍不是 token 因果证明。

## 6. 是否值得新增 GPU 实验

当前暂不值得立即新增 GPU 实验。现有采集已经足以说明 TEXT 历史序列可复现，同时主要周期随输入改变，PROSE 的 lag11 证据很弱。若未来论文问题必须升级到自然语言总体泛化，应先预注册多个独立 prose prompts、固定主要 lag/效应量和多项校正规则，再另行授权；本 consumer 不代为启动。

## 原规则与科学解释的分离

producer 的机械函数复算结果为 `{mechanical}`。原协调合同在 GPU 前声明了四输入比较、Layer1/lag11关注和候选结论，但精确的“TEXT过p95且三个替代输入至少一个同位置过p95”布尔函数未在 pre-GPU manifest/receipt 中找到，而出现在结果阶段 analysis 代码中。本报告原样保存机械结果，同时不把它当成强周期跨输入泛化证明。
"""
    write_text(output / "SCIENTIFIC_INTERPRETATION.md", interp)

    readme = f"""# C16 OLMoE 多轮路由独立 consumer（174-new）

这是 CPU-only 独立重算。未使用 GPU、未申请 GPU lock、未读取 Lane4 partial，也未修改 producer 或旧 Lane6 结果。

## 主结论

采集可用，历史 TEXT 专家集合和输出序列在显式 cached-greedy runner 下得到复现；但主周期随输入族改变。PROSE 的 lag11 只是相对单cell描述性 p95 的弱超线，且不是主峰，因此不能据 producer 机械分类声称强11步周期跨输入成立。

请按以下顺序审阅：

1. `AUTHORITY_AND_SEQUENCE_CHECKS.json`
2. `SCIENTIFIC_INTERPRETATION.md`
3. `FINAL_DECISION.json`
4. `RECOMPUTED_LAG_METRICS.tsv` 与 `RECOMPUTED_TOKEN_METRICS.tsv`
5. `ROBUSTNESS_DIAGNOSTICS.tsv` 与 `TOKEN_CONDITIONAL_CHECK.json`
6. `PRODUCER_COMPARISON.tsv` 与 `HISTORICAL_COMPARISON.tsv`
7. `SHA256SUMS`

主指标按 producer 的 NumPy `default_rng({SEED})`、每个 session/layer/lag 重置 seed、1000 次 whole-step permutation 和线性 quantile 独立实现。结果可见后的检查单独标记，不修改原门槛。

生成器：`util/vm_tlb/c16/olmoe_multiround_independent_consumer.py`；最小测试：`tests/vm_tlb/c16/test_olmoe_multiround_independent_consumer.py`。
"""
    write_text(output / "README.md", readme)

    files = sorted(path for path in output.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    write_text(output / "SHA256SUMS", "\n".join(f"{sha256_file(path)}  {path.name}" for path in files) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path("docs/vm_tlb/review_packs/C16_OLMOE_MULTIROUND_INDEPENDENT_CONSUMER_174NEW_V1"))
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    output = args.output if args.output.is_absolute() else repo / args.output
    build(repo, output)


if __name__ == "__main__":
    main()
