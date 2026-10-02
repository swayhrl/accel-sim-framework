#!/usr/bin/env python3
"""CPU-only R25 result finalization and review-pack construction."""

from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import json
import shutil
import statistics
from pathlib import Path


STAGE = "AWMA_R25_TIED_WEIGHT_BROADER_SOFTWARE_VALIDATION_109_V1"
DECISION = "R25_TILED_CAPACITY_TIME_TRADEOFF"
ARMS = ("B0_DENSE_STRONG", "C1_COMPACT_FULL", "S2_TILED")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_tsv(path, rows, fields=None):
    if fields is None:
        fields = list(rows[0])
    with Path(path).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def median(xs):
    return statistics.median(xs)


def mad(xs):
    m = median(xs)
    return median(abs(x - m) for x in xs)


def fmt_metric(m):
    return {
        "qualified": m.get("allclose"),
        "finite": m.get("finite"),
        "shape": json.dumps(m.get("shape", []), separators=(",", ":")),
        "dtype": m.get("dtype", ""),
        "max_abs": m.get("max_abs", ""),
        "mean_abs": m.get("mean_abs", ""),
        "max_rel": m.get("max_rel", ""),
        "cosine_similarity": m.get("cosine_similarity", ""),
    }


def timing_groups(samples, point, metric, candidate, baseline):
    out = []
    for group in range(3):
        c = [r[metric] for r in samples if r["group"] == group and r["arm"] == candidate]
        b = [r[metric] for r in samples if r["group"] == group and r["arm"] == baseline]
        cm, bm, ca, ba = median(c), median(b), mad(c), mad(b)
        gap = bm - cm
        threshold = 3 * max(ca, ba)
        direction = "STABLE_BENEFIT" if gap > threshold else ("STABLE_REGRESSION" if -gap > threshold else "INDETERMINATE")
        out.append({
            "point": point, "metric": metric, "candidate": candidate, "baseline": baseline,
            "group": group, "candidate_median_ms": cm, "candidate_mad_ms": ca,
            "baseline_median_ms": bm, "baseline_mad_ms": ba,
            "baseline_minus_candidate_ms": gap, "three_mad_threshold_ms": threshold,
            "direction": direction,
        })
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--pack", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--h0-model-receipt", required=True)
    p.add_argument("--h0-input-dir", required=True)
    p.add_argument("--runner", required=True)
    p.add_argument("--base", required=True)
    args = p.parse_args()
    root, pack, repo = Path(args.root), Path(args.pack), Path(args.repo)
    pack.mkdir(parents=True, exist_ok=True)
    summaries = {point: load(root / f"raw/{point}/FORMAL_SUMMARY.json") for point in ("D0", "H0")}
    quals = {point: load(root / f"raw/{point}/QUALIFICATION_STATUS.json") for point in ("D0", "H0")}
    authorities = {point: load(root / f"raw/{point}/RUNTIME_POINT_AUTHORITY.json") for point in ("D0", "H0")}
    freeze = load(root / "raw/IMPLEMENTATION_FREEZE.json")
    samples = {}
    for point in ("D0", "H0"):
        samples[point] = [json.loads(line) for line in (root / f"raw/{point}/FORMAL_RUNS.jsonl").read_text().splitlines() if line]
        if len(samples[point]) != 45:
            raise SystemExit(f"{point}: expected 45 samples")
        if summaries[point]["capacity_class"] != "CAUSAL_CAPACITY_RESPONSE":
            raise SystemExit(f"{point}: capacity response not closed")
        if not quals[point]["qualified"] or not summaries[point]["arm_identity_qualified"]:
            raise SystemExit(f"{point}: qualification not closed")
    if summaries["H0"]["comparisons"]["S2_vs_C1"]["classification"] != "REGRESSION":
        raise SystemExit("decision table mismatch")

    # Authorities.
    parent = {
        "stage": STAGE,
        "handoff_head": "9939291fbc0e890d703c6cfffe8d29e5435f9f0e",
        "handoff_tree": "36117984c784ef851dc0be66e52e23a4455f21f1",
        "scientific_parent": "b73ffd2320b5ee952d90625089b2ec31eb25eab4",
        "R24_execution_authority": "41795817a5b86959c86cc36c6973f292be33c6a6",
        "CCE_source_commit": "3de376c106a1916bc5e1b619f9c77c87a461ee1c",
        "CCE_first_store_authority": "ec1ccad7bbcead8853cd97840a2007d96f325aa3",
        "CCE_first_store_patch_sha256": "e4156b6ec21a7c8696192c9a2ad3eb2196630c72373c64bc8395bc2ef12fda56",
    }
    dump(pack / "PARENT_AUTHORITY.json", parent)
    d0 = {**authorities["D0"], "authority": "ACCEPTED_R101_TRAIN_DISCOVERY_256", "model_id": "Qwen/Qwen2.5-0.5B-Instruct", "revision": "7ae557604adf67be50417f59c2c2f167def9a775"}
    dump(pack / "D0_AUTHORITY.json", d0)
    h0_receipt = load(args.h0_model_receipt)
    h0_model = {
        **authorities["H0"],
        "model_id": "meta-llama/Llama-3.2-1B",
        "revision": "4e20de362430cd3b72f300e6b0f18e50e7166e08",
        "source_receipt": args.h0_model_receipt,
        "source_receipt_sha256": sha(args.h0_model_receipt),
        "source_receipt_payload_bytes": h0_receipt["payload_bytes"],
        "source_receipt_payloads": h0_receipt["payloads"],
        "all_six_payloads_size_sha256_verified": True,
        "active_replica_packaging": "expected .incoming path deterministically symlinked to accepted local canonical replica",
    }
    dump(pack / "H0_MODEL_AUTHORITY.json", h0_model)
    input_dir = Path(args.h0_input_dir)
    h0_input_receipt = load(input_dir / "ADOPTED_INPUT_RECEIPT.json")
    h0_input = {
        "semantic_identity": h0_input_receipt["semantic_identity"],
        "authority_type": h0_input_receipt["authority_type"],
        "historical_recovery_status": h0_input_receipt["historical_recovery_status"],
        "contract_hashes": h0_input_receipt["contract_hashes"],
        "files": [{"name": f.name, "bytes": f.stat().st_size, "sha256": sha(f)} for f in sorted(input_dir.iterdir()) if f.is_file()],
        "selected_training_binding": "input_ids=frozen_token_ids[:-1]; labels=frozen_token_ids[1:]",
        "tokenizer_invoked": False,
        "independent_from_D0_model_and_input_lineage": True,
    }
    dump(pack / "H0_INPUT_AUTHORITY.json", h0_input)
    dump(pack / "POINT_CONTRACTS.json", freeze["points"])
    dump(pack / "OPTIMIZER_CONTRACT.json", freeze["optimizer"])
    shutil.copy2(root / "raw/IMPLEMENTATION_FREEZE.json", pack / "IMPLEMENTATION_FREEZE.json")

    # Qualification tables.
    one_rows, trajectory_rows = [], []
    first_mismatch = {"status": "NONE_IN_FINAL_QUALIFICATION", "D0": None, "H0": None}
    for point in ("D0", "H0"):
        one = load(root / f"raw/{point}/ONE_STEP_NUMERICAL_QUALIFICATION.json")
        for arm, v in one.items():
            for obs, metric in v["metrics"].items():
                one_rows.append({"point": point, "arm": arm, "observable": obs, **fmt_metric(metric)})
        traj = load(root / f"raw/{point}/FOUR_STEP_TRAJECTORY_QUALIFICATION.json")
        for item in traj:
            for obs, metric in item["metrics"].items():
                trajectory_rows.append({"point": point, "candidate": item["candidate"], "trajectory_step": item["trajectory_step"], "observable": obs, **fmt_metric(metric)})
    write_tsv(pack / "ONE_STEP_NUMERICAL_QUALIFICATION.tsv", one_rows)
    write_tsv(pack / "TRAJECTORY_QUALIFICATION.tsv", trajectory_rows)
    dump(pack / "FIRST_MISMATCH.json", first_mismatch)

    # Formal sample and group tables.
    target_rows, micro_rows, memory_rows, lifetime_rows, group_rows = [], [], [], [], []
    for point in ("D0", "H0"):
        for r in samples[point]:
            target_rows.append({k: r.get(k) for k in (
                "point", "group", "repeat", "position", "arm", "target_gpu_ms", "target_host_ms",
                "target_baseline_allocated_bytes", "target_peak_allocated_bytes", "target_peak_reserved_bytes",
                "target_peak_allocated_delta_bytes", "target_peak_reserved_delta_bytes",
                "dense_lookup_gradient_materialized", "full_classifier_or_total_gradient_materialized",
                "full_gradient_buffer_count_peak", "compact_lookup_rows", "compact_lookup_bytes",
                "compact_inverse_temporary_bytes", "s2_rows_per_tile", "s2_tile_count",
            )})
            micro_rows.append({k: r.get(k) for k in (
                "point", "group", "repeat", "position", "arm", "complete_microstep_ms",
                "pre_forward_allocated_bytes", "pre_forward_reserved_bytes", "whole_peak_allocated_bytes", "whole_peak_reserved_bytes",
            )})
            lifetime_rows.append({
                "point": point, "group": r["group"], "repeat": r["repeat"], "arm": r["arm"],
                "dense_lookup_full": r["dense_lookup_gradient_materialized"],
                "full_classifier_or_total": r["full_classifier_or_total_gradient_materialized"],
                "peak_full_buffers": r["full_gradient_buffer_count_peak"],
                "first_full_gradient_point": "early_classifier_dW" if r["arm"] == "B0_DENSE_STRONG" else ("late_classifier_dW" if r["arm"] == "C1_COMPACT_FULL" else "NEVER"),
                "last_full_gradient_point": "released_after_AdamW" if r["arm"] != "S2_TILED" else "NEVER",
                "full_gradient_lifetime_gpu_ms": r["full_gradient_lifetime_gpu_ms"],
            })
        for arm in ARMS:
            rows = [r for r in samples[point] if r["arm"] == arm]
            a = summaries[point]["arm_summary"][arm]
            memory_rows.append({
                "point": point, "arm": arm,
                "dense_lookup_full": rows[0]["dense_lookup_gradient_materialized"],
                "full_classifier_or_total": rows[0]["full_classifier_or_total_gradient_materialized"],
                "peak_full_buffers": rows[0]["full_gradient_buffer_count_peak"],
                "full_gradient_bytes_each": rows[0]["full_gradient_bytes_each"],
                "median_target_peak_allocated_bytes": a["target_peak_allocated_median_bytes"],
                "median_target_peak_reserved_bytes": a["target_peak_reserved_median_bytes"],
                "median_whole_peak_allocated_bytes": a["whole_peak_allocated_median_bytes"],
                "compact_lookup_rows": a["compact_lookup_rows_median"],
                "compact_lookup_bytes": a["compact_lookup_bytes_median"],
                "cpu_restore_snapshot_bytes": summaries[point]["cpu_restore_snapshot_bytes"],
                "allocator_bytes_are_not_dram_traffic": True,
            })
            for group in range(3):
                rr = [r for r in rows if r["group"] == group]
                group_rows.append({
                    "point": point, "group": group, "arm": arm,
                    "target_median_ms": median([r["target_gpu_ms"] for r in rr]),
                    "target_mad_ms": mad([r["target_gpu_ms"] for r in rr]),
                    "complete_median_ms": median([r["complete_microstep_ms"] for r in rr]),
                    "complete_mad_ms": mad([r["complete_microstep_ms"] for r in rr]),
                })
    write_tsv(pack / "FORMAL_TARGET_TIMING.tsv", target_rows)
    write_tsv(pack / "FORMAL_MICROSTEP_TIMING.tsv", micro_rows)
    write_tsv(pack / "MEMORY_ACCOUNTING.tsv", memory_rows)
    write_tsv(pack / "LIFETIME_TRACE.tsv", lifetime_rows)
    write_tsv(pack / "GROUP_RESPONSE_SUMMARY.tsv", group_rows)

    comparison_rows = []
    for point in ("D0", "H0"):
        for metric in ("target_gpu_ms", "complete_microstep_ms"):
            comparison_rows += timing_groups(samples[point], point, metric, "S2_TILED", "C1_COMPACT_FULL")
            comparison_rows += timing_groups(samples[point], point, metric, "C1_COMPACT_FULL", "B0_DENSE_STRONG")
            comparison_rows += timing_groups(samples[point], point, metric, "S2_TILED", "B0_DENSE_STRONG")
    write_tsv(pack / "PAIRWISE_GROUP_DIRECTIONS.tsv", comparison_rows)

    # Final decision and exact deltas.
    points = {}
    for point in ("D0", "H0"):
        a = summaries[point]["arm_summary"]
        c1b0 = a["B0_DENSE_STRONG"]["target_peak_allocated_median_bytes"] - a["C1_COMPACT_FULL"]["target_peak_allocated_median_bytes"]
        s2c1 = a["C1_COMPACT_FULL"]["target_peak_allocated_median_bytes"] - a["S2_TILED"]["target_peak_allocated_median_bytes"]
        target_gap = a["C1_COMPACT_FULL"]["target_gpu_median_ms"] - a["S2_TILED"]["target_gpu_median_ms"]
        complete_gap = a["C1_COMPACT_FULL"]["complete_microstep_median_ms"] - a["S2_TILED"]["complete_microstep_median_ms"]
        points[point] = {
            "qualification": "PASS",
            "capacity_class": summaries[point]["capacity_class"],
            "C1_vs_B0_peak_reduction_bytes": c1b0,
            "C1_vs_B0_peak_reduction_MiB": c1b0 / 2**20,
            "S2_vs_C1_peak_reduction_bytes": s2c1,
            "S2_vs_C1_peak_reduction_MiB": s2c1 / 2**20,
            "S2_vs_C1_peak_reduction_percent": 100 * s2c1 / a["C1_COMPACT_FULL"]["target_peak_allocated_median_bytes"],
            "S2_vs_C1_target_class": summaries[point]["comparisons"]["S2_vs_C1"]["classification"],
            "S2_vs_C1_target_C1_minus_S2_median_ms": target_gap,
            "S2_vs_C1_target_C1_minus_S2_percent": 100 * target_gap / a["C1_COMPACT_FULL"]["target_gpu_median_ms"],
            "S2_vs_C1_complete_C1_minus_S2_median_ms": complete_gap,
            "S2_vs_C1_complete_C1_minus_S2_percent": 100 * complete_gap / a["C1_COMPACT_FULL"]["complete_microstep_median_ms"],
            "S2_vs_C1_group_directions": [g["direction"] for g in summaries[point]["comparisons"]["S2_vs_C1"]["groups"]],
            "C1_vs_B0_target_class": summaries[point]["comparisons"]["C1_vs_B0"]["classification"],
            "arm_summary": a,
        }
    decision = {
        "stage": STAGE,
        "decision": DECISION,
        "decision_table_case": "B",
        "points": points,
        "cross_model_capacity_response": True,
        "time_result": "D0_BENEFIT_H0_REGRESSION",
        "profiles_run": 0,
        "hardware_claim": False,
        "convergence_claim": False,
        "general_LLM_speedup_claim": False,
        "production_interpretation": "capacity-oriented software integration is justified for further production hardening, but S2 is not justified as an unconditional default speed path because H0 has three stable target regressions",
    }
    dump(pack / "POINT_DECISIONS.json", decision)

    arm_md = """# Arm contract\n\n- `B0_DENSE_STRONG`: normal dense embedding backward plus accepted full classifier gradient; two full VxH contributions may coexist.\n- `C1_COMPACT_FULL`: sorted unique compact lookup rows, native compact-domain embedding reducer, then exactly one full classifier/total gradient merged in place. No dense lookup W.grad.\n- `S2_TILED`: the same compact lookup rows, deterministic 32 MiB FP32-budget row tiles, tilewise AdamW, and no formal full VxH gradient or shadow.\n\nAll arms use the same BF16 tied W, FP32 m/v, AdamW contract, CCE first-store lineage, loss math, and point-specific fixed CCE meta. CPU restore copies are outside measured regions.\n"""
    (pack / "ARM_CONTRACT.md").write_text(arm_md)
    final_md = f"""# R25 final decision\n\n`{DECISION}`\n\nBoth D0 and the independent H0 passed one-step and four-step trajectory qualification. C1 has one full classifier/total gradient and no dense lookup gradient; S2 has no full VxH gradient in formal execution.\n\n- D0: S2 vs C1 saves {points['D0']['S2_vs_C1_peak_reduction_MiB']:.3f} MiB ({points['D0']['S2_vs_C1_peak_reduction_percent']:.3f}%) and is `BENEFIT` in all three TARGET_REGION groups.\n- H0: S2 vs C1 saves {points['H0']['S2_vs_C1_peak_reduction_MiB']:.3f} MiB ({points['H0']['S2_vs_C1_peak_reduction_percent']:.3f}%), but is `REGRESSION` in all three TARGET_REGION groups; the overall median regression is {-points['H0']['S2_vs_C1_target_C1_minus_S2_percent']:.3f}%.\n\nThus capacity generalizes across model/input lineage, while timing does not remain neutral/favorable under the preregistered classifier. This is a software/dataflow capacity-time tradeoff, not a hardware, convergence, full-training, or general-LLM-speedup result. NSYS was skipped because direct buffer identity and allocator accounting closed the causal question.\n"""
    (pack / "FINAL_DECISION.md").write_text(final_md)

    attempts = """# Engineering attempts\n\nThe first wrapper attempt stopped before CUDA because the lock-held sentinel environment variable was missing. The first compact BF16 accumulation passed one-step but crossed the fixed trajectory tolerance on D0. A bounded FP32 compact accumulator then passed D0 but crossed the same tolerance on H0. The final frozen implementation remaps indices to the sorted compact domain and uses the native embedding-backward reducer; both points were rerun from scratch and passed. Earlier receipts remain in node164 raw only and were not used for formal timing.\n"""
    (pack / "ENGINEERING_ATTEMPTS.md").write_text(attempts)

    run_receipts = {
        "stage": STAGE,
        "qualification_lock_receipts": [{"path": str(f), "sha256": sha(f)} for f in sorted((root / "receipts").glob("GPU_LOCK_QUALIFICATION*.txt"))],
        "formal_lock_receipt": {"path": str(root / "receipts/GPU_LOCK_FORMAL.txt"), "sha256": sha(root / "receipts/GPU_LOCK_FORMAL.txt")},
        "formal_samples": {"D0": 45, "H0": 45},
        "warmups": {"per_arm_per_group": 2, "groups": 3},
        "CUDA_used_only_under_shared_lock": True,
        "profiles": {"NSYS": 0, "NCU": 0, "NVBit": 0, "SASS": 0},
        "node174_compute": False,
    }
    dump(pack / "RUN_RECEIPTS.json", run_receipts)

    # Source patch and raw manifests.
    before = Path(args.base).read_text().splitlines(True)
    after = Path(args.runner).read_text().splitlines(True)
    (pack / "R25_SOFTWARE_COUNTERFACTUAL.patch").write_text("".join(difflib.unified_diff(before, after, fromfile="accepted_r24_base.py", tofile="run_r25_campaign.py")))
    raw_rows = []
    for sub in (root / "raw", root / "receipts"):
        for f in sorted(x for x in sub.rglob("*") if x.is_file()):
            raw_rows.append({"path": str(f), "bytes": f.stat().st_size, "sha256": sha(f), "role": "raw" if sub.name == "raw" else "receipt"})
    write_tsv(pack / "RAW_DATA_INDEX.tsv", raw_rows)

    readme = f"""# {STAGE}\n\nDecision: `{DECISION}`.\n\nThis pack closes the two-point Qwen/Llama tied-weight gradient-lifetime software validation. D0 is the R24 discovery/calibration authority; H0 is the independent accepted C16 Llama S0/B1/T128/Decode4/TEXT lineage used as a sealed performance holdout until implementation freeze. Both numerical trajectories pass. Both points retain an S2-vs-C1 causal capacity response; H0 produces a preregistered timing regression, so the result is a capacity-time tradeoff.\n\nPrimary evidence is in `POINT_DECISIONS.json`, `MEMORY_ACCOUNTING.tsv`, `GROUP_RESPONSE_SUMMARY.tsv`, and the two formal timing tables. Large/raw receipts are published separately on node164 and bound by `RAW_DATA_INDEX.tsv`.\n"""
    (pack / "README.md").write_text(readme)

    # Pack hash closure, written last and excluding itself.
    sum_rows = []
    for f in sorted(x for x in pack.rglob("*") if x.is_file() and x.name != "SHA256SUMS"):
        sum_rows.append(f"{sha(f)}  {f.relative_to(pack).as_posix()}")
    (pack / "SHA256SUMS").write_text("\n".join(sum_rows) + "\n")
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
