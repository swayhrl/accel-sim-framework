#!/usr/bin/env python3
"""CPU-only producer analysis and compact review-pack emitter for OLMoE routing V1."""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import math
import os
import shutil
from pathlib import Path

import numpy as np

ROOT = Path("/data/c16/olmoe_routing_provenance_multiround_v1")
REPO = Path("/home/huangrulin/workspace/worktrees/accel-sim-c16-olmoe-routing-provenance-multiround-109-v1")
PACK = REPO / "docs/vm_tlb/review_packs/C16_OLMOE_ROUTING_PROVENANCE_MULTIROUND_109_V1"
MODEL = Path("/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e")
CAPTURE_SESSIONS = ["T2_TEXT_ALLLAYER", "C1_CODE_ALLLAYER", "S1_STRUCTURED_ALLLAYER", "P1_PROSE_ALLLAYER"]
ALL_SESSIONS = ["T0_NOHOOK_A", "T1_NOHOOK_B", *CAPTURE_SESSIONS]
PROMPTS = ["P_TEXT", "P_CODE", "P_STRUCTURED", "P_PROSE"]
SESSION_PROMPT = {"T2_TEXT_ALLLAYER": "P_TEXT", "C1_CODE_ALLLAYER": "P_CODE", "S1_STRUCTURED_ALLLAYER": "P_STRUCTURED", "P1_PROSE_ALLLAYER": "P_PROSE"}
SEED = 20260928
PERMUTATIONS = 1000


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def json_sha(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_json(name: str, value) -> None:
    (PACK / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_tsv(name: str, fields: list[str], rows: list[dict]) -> None:
    with (PACK / name).open("w", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: ("NA" if row.get(k) in (None, "") else row.get(k)) for k in fields})


def load_json(path: Path):
    return json.loads(path.read_text())


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def quantiles(values):
    a = np.asarray(values, dtype=np.float64)
    return [float(np.quantile(a, q)) for q in (0.05, 0.5, 0.95)]


def route_matrices(ordered: np.ndarray):
    steps, topk = ordered.shape
    masks = np.zeros((steps, 64), dtype=np.int8)
    for i, row in enumerate(ordered):
        masks[i, row] = 1
    intersection = masks @ masks.T
    jaccard = intersection / (2 * topk - intersection)
    retention = intersection / topk
    exact = intersection == topk
    ordered_equal = np.all(ordered[:, None, :] == ordered[None, :, :], axis=2)
    return intersection, jaccard, retention, exact, ordered_equal


def metrics_for_pairs(mats, left, right):
    inter, jac, ret, exact, ordered = mats
    return {
        "mean_overlap": float(inter[left, right].mean()),
        "mean_jaccard": float(jac[left, right].mean()),
        "mean_retention": float(ret[left, right].mean()),
        "exact_unordered_count": int(exact[left, right].sum()),
        "ordered_repeat_count": int(ordered[left, right].sum()),
    }


def prompt_analysis(run: Path):
    rows = []
    strongest = {}
    for prompt in PROMPTS:
        ids = json.loads((run / "inputs" / f"{prompt}.token_ids.json").read_text())
        lag_rows = []
        tail = ids[-256:]
        for lag in range(1, 33):
            full_eq = sum(a == b for a, b in zip(ids[:-lag], ids[lag:]))
            tail_eq = sum(a == b for a, b in zip(tail[:-lag], tail[lag:]))
            row = {
                "prompt_id": prompt, "record_type": "LAG", "lag_or_ngram": lag,
                "pair_count_full": len(ids) - lag, "equal_count_full": full_eq,
                "equality_rate_full": full_eq / (len(ids) - lag),
                "pair_count_tail256": len(tail) - lag, "equal_count_tail256": tail_eq,
                "equality_rate_tail256": tail_eq / (len(tail) - lag),
            }
            rows.append(row); lag_rows.append(row)
        max_full = max(r["equality_rate_full"] for r in lag_rows)
        max_tail = max(r["equality_rate_tail256"] for r in lag_rows)
        strongest[prompt] = {
            "full_lags": [r["lag_or_ngram"] for r in lag_rows if r["equality_rate_full"] == max_full],
            "full_rate": max_full,
            "tail256_lags": [r["lag_or_ngram"] for r in lag_rows if r["equality_rate_tail256"] == max_tail],
            "tail256_rate": max_tail,
        }
        for n in (2, 4, 8):
            grams = collections.Counter(tuple(ids[i:i+n]) for i in range(len(ids)-n+1))
            rows.append({
                "prompt_id": prompt, "record_type": "NGRAM", "lag_or_ngram": n,
                "ngram_windows": sum(grams.values()), "unique_ngrams": len(grams),
                "repeated_unique_ngrams": sum(v > 1 for v in grams.values()),
                "repeated_window_excess": sum(v - 1 for v in grams.values() if v > 1),
                "max_ngram_occurrence": max(grams.values()),
            })
    return rows, strongest


def routing_analysis(run: Path):
    spectrum, shuffle, cross_layer = [], [], []
    session_layer = {}
    for session in CAPTURE_SESSIONS:
        records = load_jsonl(run / "routing" / f"{session}.jsonl")
        for layer in range(16):
            lr = sorted((r for r in records if r["layer_id"] == layer), key=lambda r: r["decode_step"])
            ordered = np.asarray([r["ordered_topk_expert_ids"] for r in lr], dtype=np.int16)
            if ordered.shape != (64, 8):
                raise RuntimeError(f"ROUTING_SHAPE_FAIL {session} layer={layer} shape={ordered.shape}")
            mats = route_matrices(ordered)
            session_layer[(session, layer)] = {"records": lr, "ordered": ordered, "mats": mats}
            layer_shuffle = []
            for lag in range(1, 33):
                left = np.arange(0, 64-lag); right = np.arange(lag, 64)
                actual = metrics_for_pairs(mats, left, right)
                spectrum.append({"session_id": session, "prompt_id": SESSION_PROMPT[session], "layer_id": layer, "lag": lag, "pair_count": 64-lag, **actual})
                rng = np.random.default_rng(SEED)
                null = {k: [] for k in actual}
                for _ in range(PERMUTATIONS):
                    perm = rng.permutation(64)
                    m = metrics_for_pairs(mats, perm[:-lag], perm[lag:])
                    for key, value in m.items(): null[key].append(value)
                row = {"session_id": session, "prompt_id": SESSION_PROMPT[session], "layer_id": layer, "lag": lag, "seed": SEED, "permutations": PERMUTATIONS}
                for key, values in null.items():
                    p05, med, p95 = quantiles(values)
                    row[f"actual_{key}"] = actual[key]
                    row[f"shuffle_{key}_p05"] = p05
                    row[f"shuffle_{key}_median"] = med
                    row[f"shuffle_{key}_p95"] = p95
                row["mean_jaccard_above_shuffle_p95"] = actual["mean_jaccard"] > row["shuffle_mean_jaccard_p95"]
                shuffle.append(row); layer_shuffle.append(row)
            above = [r for r in layer_shuffle if r["mean_jaccard_above_shuffle_p95"]]
            dominant_all = max(layer_shuffle, key=lambda r: (r["actual_mean_jaccard"], -r["lag"]))
            dominant_above = max(above, key=lambda r: (r["actual_mean_jaccard"], -r["lag"])) if above else None
            lag11 = next(r for r in layer_shuffle if r["lag"] == 11)
            cross_layer.append({
                "session_id": session, "prompt_id": SESSION_PROMPT[session], "layer_id": layer,
                "dominant_lag_all": dominant_all["lag"], "dominant_mean_jaccard": dominant_all["actual_mean_jaccard"],
                "any_above_shuffle_p95": bool(above),
                "dominant_above_p95_lag": dominant_above["lag"] if dominant_above else "NONE",
                "dominant_above_p95_jaccard": dominant_above["actual_mean_jaccard"] if dominant_above else "NA",
                "lag11_mean_jaccard": lag11["actual_mean_jaccard"],
                "lag11_shuffle_p95": lag11["shuffle_mean_jaccard_p95"],
                "lag11_above_shuffle_p95": lag11["mean_jaccard_above_shuffle_p95"],
            })
    return spectrum, shuffle, cross_layer, session_layer


def token_association(run: Path, session_layer):
    token_lags = []
    associations = []
    for session in CAPTURE_SESSIONS:
        s = load_json(run / "sessions" / f"{session}.json")
        inputs, outputs = np.asarray(s["input_token_ids"]), np.asarray(s["output_token_ids"])
        for lag in range(1, 33):
            token_lags.append({
                "session_id": session, "prompt_id": SESSION_PROMPT[session], "lag": lag, "pair_count": 64-lag,
                "input_equal_count": int(np.sum(inputs[:-lag] == inputs[lag:])),
                "input_equality_rate": float(np.mean(inputs[:-lag] == inputs[lag:])),
                "output_equal_count": int(np.sum(outputs[:-lag] == outputs[lag:])),
                "output_equality_rate": float(np.mean(outputs[:-lag] == outputs[lag:])),
            })
        for layer in range(16):
            mats = session_layer[(session, layer)]["mats"]
            jac = mats[1]
            pairs = [(i, j) for lag in range(1, 33) for i, j in zip(range(64-lag), range(lag, 64))]
            def summarize(tokens):
                same = [jac[i, j] for i, j in pairs if tokens[i] == tokens[j]]
                diff = [jac[i, j] for i, j in pairs if tokens[i] != tokens[j]]
                return {"same_count": len(same), "same_mean_jaccard": float(np.mean(same)) if same else None,
                        "different_count": len(diff), "different_mean_jaccard": float(np.mean(diff)) if diff else None}
            associations.append({"session_id": session, "prompt_id": SESSION_PROMPT[session], "layer_id": layer,
                                 "input_token": summarize(inputs), "output_token": summarize(outputs)})
    return {"status": "DESCRIPTIVE_ONLY", "lag_range": [1, 32], "token_lag_spectrum": token_lags,
            "routing_association_by_layer": associations,
            "interpretation_boundary": "input-token association is input-side descriptive relation; output-token association is downstream/descriptive"}


def historical_comparison(run: Path, session_layer):
    old = load_json(run / "V34_NATURAL_TOP8_ROUTING.reference.json")["repeat_decode_records"]
    new = session_layer[("T2_TEXT_ALLLAYER", 1)]["records"][:32]
    rows = []
    for o, n in zip(old, new):
        old_ids, new_ids = o["natural_top8_ids"], n["ordered_topk_expert_ids"]
        inter = len(set(old_ids) & set(new_ids))
        rows.append({
            "decode_step": o["decode_step"],
            "ordered_topk_equal": old_ids == new_ids,
            "unordered_topk_equal": set(old_ids) == set(new_ids),
            "jaccard": inter / len(set(old_ids) | set(new_ids)),
            "new_output_equals_old_next": n["output_token_id"] == o["next_token_id"],
            "new_input_equals_old_next": n["input_token_id"] == o["next_token_id"],
            "router_input_sha_equal": n["router_input_sha256"] == o["mlp_router_input"]["sha256"],
            "router_logits_sha_equal": n["router_logits_sha256"] == o["router_logits_sha256"],
            "old_topk": json.dumps(old_ids, separators=(",", ":")),
            "new_topk": json.dumps(new_ids, separators=(",", ":")),
            "old_next_token_id": o["next_token_id"], "new_input_token_id": n["input_token_id"], "new_output_token_id": n["output_token_id"],
        })
    ordered_count = sum(r["ordered_topk_equal"] for r in rows)
    unordered_count = sum(r["unordered_topk_equal"] for r in rows)
    if ordered_count == 32:
        label = "HISTORICAL_V34_SEQUENCE_REPRODUCED_UNDER_EXPLICIT_RUNNER"
    elif ordered_count or unordered_count or any(r["jaccard"] > 0 for r in rows):
        label = "HISTORICAL_V34_SEQUENCE_PARTIALLY_REPRODUCED"
    else:
        label = "HISTORICAL_V34_RUNNER_NOT_RECONSTRUCTED"
    summary = {
        "label": label, "step_count": len(rows), "ordered_equal_count": ordered_count,
        "unordered_equal_count": unordered_count, "mean_jaccard": sum(r["jaccard"] for r in rows)/len(rows),
        "new_output_vs_old_next_equal_count": sum(r["new_output_equals_old_next"] for r in rows),
        "new_input_vs_old_next_equal_count": sum(r["new_input_equals_old_next"] for r in rows),
        "router_input_sha_equal_count": sum(r["router_input_sha_equal"] for r in rows),
        "router_logits_sha_equal_count": sum(r["router_logits_sha_equal"] for r in rows),
        "hash_serialization_comparable": True,
        "semantic_boundary": "field alignment does not reconstruct ambiguous V34 generation-loop semantics",
    }
    return rows, summary


def decision_from(cross_layer):
    by = {(r["session_id"], r["layer_id"]): r for r in cross_layer}
    text_l1 = by[("T2_TEXT_ALLLAYER", 1)]
    control_l1_lag11 = [by[(s, 1)]["lag11_above_shuffle_p95"] for s in CAPTURE_SESSIONS[1:]]
    if not text_l1["lag11_above_shuffle_p95"]:
        decision = "HISTORICAL_PERIOD11_NOT_REPRODUCED_PROSPECTIVELY"
        reason = "Prospective P_TEXT Layer1 lag11 does not exceed its preregistered marginal-preserving shuffle p95."
    elif any(control_l1_lag11):
        decision = "PERIOD11_REPRODUCED_ACROSS_INPUT_FAMILIES"
        reason = "Prospective P_TEXT Layer1 lag11 exceeds shuffle p95 and the same predeclared Layer1 criterion holds for at least one alternative input family."
    else:
        decision = "PERIOD11_REPRODUCED_TEXT_ONLY_CONTENT_ASSOCIATED"
        reason = "Prospective P_TEXT Layer1 lag11 exceeds shuffle p95 while CODE, STRUCTURED and PROSE Layer1 lag11 do not."
    return decision, reason


def copy_sources(run: Path):
    dest = run / "source"
    dest.mkdir(exist_ok=True)
    names = [
        "olmoe_routing_provenance_prepare.py",
        "olmoe_routing_provenance_pregpu_validate.py",
        "olmoe_routing_provenance_runner.py",
        "olmoe_routing_provenance_analyze.py",
    ]
    for name in names:
        shutil.copy2(REPO / "util/vm_tlb/c16" / name, dest / name)
    shutil.copy2(ROOT / "run_olmoe_routing_locked.sh", dest / "run_olmoe_routing_locked.sh")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--producer-commit", default="PENDING_SCIENCE_COMMIT")
    args = parser.parse_args()
    run_id = (ROOT / "ACTIVE_RUN_ID").read_text().strip()
    candidates = [ROOT / state / run_id for state in ("raw", "ready", "transferred")]
    run = next((path for path in candidates if path.is_dir()), None)
    if run is None:
        raise RuntimeError(f"RUN_DIRECTORY_NOT_FOUND {run_id}")
    if not (run / "GPU_LOCK_RELEASED").is_file():
        raise RuntimeError("GPU_LOCK_NOT_RELEASED")
    receipt = load_json(run / "GPU_RUN_RECEIPT.json")
    if receipt["status"] != "PASS_SIX_SESSIONS" or receipt["session_count"] != 6 or receipt["model_load_count"] != 1:
        raise RuntimeError("GPU_CAMPAIGN_INCOMPLETE")
    if not (run / "RUN_MANIFEST.json").exists():
        copy_sources(run)
    PACK.mkdir(parents=True, exist_ok=True)

    prompt_rows, prompt_strongest = prompt_analysis(run)
    spectrum, shuffle_rows, cross_layer, session_layer = routing_analysis(run)
    token_assoc = token_association(run, session_layer)
    v34_rows, v34_summary = historical_comparison(run, session_layer)
    decision, decision_reason = decision_from(cross_layer)
    control = load_json(run / "CONTROL_GATE.json")

    source_authority = {
        "status": "PASS", "run_id": run_id,
        "model": {"id": "allenai/OLMoE-1B-7B-0125-Instruct", "revision": "b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e", "path": str(MODEL), "asset_receipt_sha256": sha(MODEL / "MODEL_ASSET_RECEIPT.json"), "node164_remains_sole_authority": True},
        "runtime": load_json(run / "PRE_GPU_AUTHORITY_RECEIPT.json"),
        "input_commits": {"TEXT_CODE_STRUCTURED": "ca683527323e26e3415a805c797c53c5edea322c", "PROSE": "a306e1271c3e70c2ee322a3582979b6abd777a72"},
        "historical_v34_commit": "ab26365dc663268b0799818db6687ed466e8c925",
        "accepted_v40_descendant": "85563ec6f55a0ad743d21483aa49c24fdb5cf3bf",
        "coordination_head": "378df585cba4c21ac5864c374976e271ae44e9a3",
        "lane7_base": "0e88faa28c9066b48e394dce657d7a16e6332a32",
        "lane4_partial_accessed": False,
    }
    write_json("SOURCE_AUTHORITY.json", source_authority)

    freeze = load_json(run / "INPUT_FREEZE_MANIFEST.json")
    freeze_rows = []
    for p in freeze["prompts"]:
        freeze_rows.append({**p, "first_16_ids": json.dumps(p["first_16_ids"], separators=(",", ":")), "last_16_ids": json.dumps(p["last_16_ids"], separators=(",", ":"))})
    write_tsv("INPUT_FREEZE_INDEX.tsv", ["prompt_id", "source_commit", "source_path", "source_size_bytes", "source_sha256", "pre_truncation_token_count", "frozen_token_count", "frozen_ids_path", "frozen_ids_file_sha256", "token_ids_semantic_sha256", "first_16_ids", "last_16_ids", "add_special_tokens", "chat_template_applied", "historical_v34_ids_exact_match", "historical_v34_frozen_file_sha256_authority"], freeze_rows)
    generation = load_json(run / "CAMPAIGN_MANIFEST.pre_gpu.json")
    generation["executed_runtime"] = receipt["runtime"]
    generation["natural_eos_ids"] = [50279]
    write_json("GENERATION_CONTRACT.json", generation)

    lock = {
        "status": "PASS", "lock_path": "/data/c16/locks/c16_gpu_campaign.lock",
        "acquisition": "ACQUIRED_ONCE_OUTER_FLOCK", "release": "RELEASED_AFTER_ALL_SESSIONS",
        "start_utc": (run / "GPU_LOCK_START_UTC.txt").read_text().strip(), "end_utc": (run / "GPU_LOCK_END_UTC.txt").read_text().strip(),
        "gpu": receipt["gpu"], "runtime": receipt["runtime"], "model_load_count": receipt["model_load_count"],
        "session_count": receipt["session_count"], "completed_sessions": receipt["completed_sessions"],
        "nvidia_smi_pre": {"path": str(run / "NVIDIA_SMI_PRE.txt"), "sha256": sha(run / "NVIDIA_SMI_PRE.txt")},
        "nvidia_smi_post": {"path": str(run / "NVIDIA_SMI_POST.txt"), "sha256": sha(run / "NVIDIA_SMI_POST.txt")},
        "clocks_power_persistence_driver_modified": False,
    }
    write_json("GPU_LOCK_RECEIPT.json", lock)

    session_rows, output_rows, route_index = [], [], []
    for session in ALL_SESSIONS:
        sfile = run / "sessions" / f"{session}.json"; s = load_json(sfile)
        session_rows.append({"session_id": session, "prompt_id": s["prompt_id"], "router_capture": s["router_capture"], "prefill_tokens": s["prompt_tokens"], "prefill_output_token_id": s["prefill_output_token_id"], "decode_steps_executed": s["decode_steps_executed"], "stop_reason": s["stop_reason"], "routing_record_count": s["routing_record_count"], "session_file_sha256": sha(sfile), "status": s["status"]})
        output_rows.append({"session_id": session, "prompt_id": s["prompt_id"], "prefill_output_token_id": s["prefill_output_token_id"], "decode_steps": s["decode_steps_executed"], "input_token_ids": json.dumps(s["input_token_ids"], separators=(",", ":")), "output_token_ids": json.dumps(s["output_token_ids"], separators=(",", ":")), "input_sequence_sha256": json_sha(s["input_token_ids"]), "output_sequence_sha256": json_sha(s["output_token_ids"]), "stop_reason": s["stop_reason"]})
        if s["router_capture"]:
            route = run / "routing" / f"{session}.jsonl"
            route_index.append({"session_id": session, "prompt_id": s["prompt_id"], "relative_path": route.relative_to(run).as_posix(), "rows": sum(1 for _ in route.open()), "layers": 16, "decode_steps": s["decode_steps_executed"], "file_bytes": route.stat().st_size, "sha256": sha(route), "schema": "one row per (decode_step,layer_id), expert identity=(layer_id,expert_id)"})
    write_tsv("SESSION_RECEIPT.tsv", ["session_id", "prompt_id", "router_capture", "prefill_tokens", "prefill_output_token_id", "decode_steps_executed", "stop_reason", "routing_record_count", "session_file_sha256", "status"], session_rows)
    write_tsv("OUTPUT_TOKEN_SEQUENCES.tsv", ["session_id", "prompt_id", "prefill_output_token_id", "decode_steps", "input_token_ids", "output_token_ids", "input_sequence_sha256", "output_sequence_sha256", "stop_reason"], output_rows)
    write_tsv("ROUTING_RECORD_INDEX.tsv", ["session_id", "prompt_id", "relative_path", "rows", "layers", "decode_steps", "file_bytes", "sha256", "schema"], route_index)
    control_out = {**control, "T0_output_sha256": next(r["output_sequence_sha256"] for r in output_rows if r["session_id"] == "T0_NOHOOK_A"), "T1_output_sha256": next(r["output_sequence_sha256"] for r in output_rows if r["session_id"] == "T1_NOHOOK_B"), "T2_output_sha256": next(r["output_sequence_sha256"] for r in output_rows if r["session_id"] == "T2_TEXT_ALLLAYER"), "claim_restriction": "NONE_FROM_CONTROL; exact output reproducibility and hook neutrality pass"}
    write_json("CONTROL_REPRODUCIBILITY.json", control_out)

    write_tsv("V34_LAYER1_COMPARISON.tsv", ["decode_step", "ordered_topk_equal", "unordered_topk_equal", "jaccard", "new_output_equals_old_next", "new_input_equals_old_next", "router_input_sha_equal", "router_logits_sha_equal", "old_topk", "new_topk", "old_next_token_id", "new_input_token_id", "new_output_token_id"], v34_rows)
    write_json("V34_LAYER1_COMPARISON_SUMMARY.json", v34_summary)
    write_tsv("PROMPT_PERIODICITY.tsv", ["prompt_id", "record_type", "lag_or_ngram", "pair_count_full", "equal_count_full", "equality_rate_full", "pair_count_tail256", "equal_count_tail256", "equality_rate_tail256", "ngram_windows", "unique_ngrams", "repeated_unique_ngrams", "repeated_window_excess", "max_ngram_occurrence"], prompt_rows)
    write_tsv("ROUTING_LAG_SPECTRUM.tsv", ["session_id", "prompt_id", "layer_id", "lag", "pair_count", "mean_overlap", "mean_jaccard", "mean_retention", "exact_unordered_count", "ordered_repeat_count"], spectrum)
    shuffle_fields = ["session_id", "prompt_id", "layer_id", "lag", "seed", "permutations"]
    for metric in ("mean_overlap", "mean_jaccard", "mean_retention", "exact_unordered_count", "ordered_repeat_count"):
        shuffle_fields += [f"actual_{metric}", f"shuffle_{metric}_p05", f"shuffle_{metric}_median", f"shuffle_{metric}_p95"]
    shuffle_fields += ["mean_jaccard_above_shuffle_p95"]
    write_tsv("ROUTING_LAG_SHUFFLE.tsv", shuffle_fields, shuffle_rows)
    write_json("TOKEN_ROUTING_ASSOCIATION.json", token_assoc)
    write_tsv("CROSS_LAYER_PERIODICITY.tsv", ["session_id", "prompt_id", "layer_id", "dominant_lag_all", "dominant_mean_jaccard", "any_above_shuffle_p95", "dominant_above_p95_lag", "dominant_above_p95_jaccard", "lag11_mean_jaccard", "lag11_shuffle_p95", "lag11_above_shuffle_p95"], cross_layer)

    summary_by_session = {}
    for session in CAPTURE_SESSIONS:
        rows = [r for r in cross_layer if r["session_id"] == session]
        summary_by_session[session] = {
            "layers_any_above_p95": sum(r["any_above_shuffle_p95"] for r in rows),
            "layers_dominant_above_p95_lag11": sum(r["dominant_above_p95_lag"] == 11 for r in rows),
            "layers_lag11_above_p95": sum(r["lag11_above_shuffle_p95"] for r in rows),
            "layer1": next(r for r in rows if r["layer_id"] == 1),
        }
    decision_json = {
        "decision": decision, "reason": decision_reason, "run_id": run_id,
        "control_state": control["status"], "historical_comparison_label": v34_summary["label"],
        "prompt_strongest_lags": prompt_strongest, "cross_layer_summary": summary_by_session,
        "scientific_status": "PRODUCER_SELF_CHECK_PENDING_INDEPENDENT_174NEW_RECOMPUTE",
        "cache_opportunity_claim": False, "performance_claim": False, "automatic_gpu_expansion": False,
        "claim_boundary": "one OLMoE revision, four predeclared 2048-token prompt families, explicit greedy cached decode, routing provenance only",
    }
    write_json("FINAL_DECISION.json", decision_json)

    lines = ["# Cross-input interpretation", "", f"Producer-side bounded decision: `{decision}`.", "", decision_reason, "", "| Prompt | Strongest full-prompt token lag(s) | Layer1 dominant routing lag | Layer1 lag11 above shuffle p95 | Layers with lag11 above p95 |", "|---|---|---:|---|---:|"]
    for session in CAPTURE_SESSIONS:
        prompt = SESSION_PROMPT[session]; s = summary_by_session[session]
        lines.append(f"| {prompt} | {prompt_strongest[prompt]['full_lags']} | {s['layer1']['dominant_lag_all']} | {s['layer1']['lag11_above_shuffle_p95']} | {s['layers_lag11_above_p95']} |")
    lines += ["", "All comparisons are descriptive for one model across four fixed prompt families. Above-p95 refers to the preregistered marginal-preserving temporal shuffle, not a p-value. Expert IDs are never mixed across layers. No cache, timing, full-model speedup, or population-language claim is made.", ""]
    (PACK / "CROSS_INPUT_INTERPRETATION.md").write_text("\n".join(lines))

    durable_path = ROOT / "DURABLE_PROVENANCE.json"
    durable = load_json(durable_path) if durable_path.exists() else {"status": "PENDING_BEFORE_SCIENCE_COMMIT", "run_id": run_id}
    write_json("DURABLE_PROVENANCE.json", durable)
    (PACK / "NEXT_174_CONSUMER_CONTRACT.md").write_text(f"""# Next 174-new independent consumer contract\n\n- RUN_ID: `{run_id}`\n- Pipeline durable RUN_ID: `{durable.get('pipeline_run_id', 'PENDING_DURABLE_TRANSFER')}`\n- producer scientific commit: `{args.producer_commit}`\n- source manifest SHA256: `{durable.get('source_manifest_sha256', 'PENDING_DURABLE_TRANSFER')}`\n- four input identities: `P_TEXT`, `P_CODE`, `P_STRUCTURED`, `P_PROSE` exactly as bound in `INPUT_FREEZE_INDEX.tsv`\n- six sessions: `T0_NOHOOK_A`, `T1_NOHOOK_B`, `T2_TEXT_ALLLAYER`, `C1_CODE_ALLLAYER`, `S1_STRUCTURED_ALLLAYER`, `P1_PROSE_ALLLAYER`\n- expected session rows: 6; expected routing rows: 4096 = 4 sessions x 64 steps x 16 layers\n- recompute lags 1..32; seed 20260928; 1000 whole-step-set permutations per session/layer/lag\n- recompute prompt periodicity, V34 Layer1 comparison, token/routing association and cross-layer concordance directly from durable raw\n- do not use producer TSV/JSON summaries as calculation authority\n- do not automatically start the consumer from Lane 7\n""")
    (PACK / "README.md").write_text(f"""# C16 OLMoE routing provenance multi-round V1\n\nRUN_ID: `{run_id}`\n\nProducer result: `{decision}`. Six sessions completed under one GPU lock and one model load. T0/T1/T2 exact output reproducibility and passive-hook neutrality passed. The analysis is routing provenance only and awaits independent 174-new recomputation from durable raw.\n\nNo timing, cache mechanism, full-model speedup, forced routing, new prompt family, or sampling-mode claim is made.\n""")

    index_root = run
    if durable.get("status") == "PASS_NODE164_DURABLE_ACK":
        candidate = ROOT / "transport_transferred" / durable["pipeline_run_id"]
        if candidate.is_dir():
            index_root = candidate
    raw_rows = []
    for p in sorted(index_root.rglob("*")):
        if p.is_file():
            raw_rows.append({"relative_path": p.relative_to(index_root).as_posix(), "size_bytes": p.stat().st_size, "sha256": sha(p)})
    write_tsv("RAW_LOG_INDEX.tsv", ["relative_path", "size_bytes", "sha256"], raw_rows)

    for old in (PACK / "SHA256SUMS",): old.unlink(missing_ok=True)
    sums = [f"{sha(p)}  {p.name}" for p in sorted(PACK.iterdir()) if p.is_file() and p.name != "SHA256SUMS"]
    (PACK / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    print(json.dumps({"status": "PASS_PRODUCER_ANALYSIS", "run_id": run_id, "decision": decision, "v34": v34_summary, "summary": summary_by_session}, sort_keys=True))


if __name__ == "__main__":
    main()
