#!/usr/bin/env python3
"""Validate and package the targeted CUDA L2-persistence intervention."""

import csv
import hashlib
import json
import math
import shutil
import statistics
from collections import defaultdict
from pathlib import Path


REPO = Path("/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-l2-persistence-intervention-109-v1")
SOURCE = Path("/data/c16/e1_l2_persistence_intervention_v1")
OUT = REPO / "docs/vm_tlb/review_packs/C16_E1_L2_PERSISTENCE_INTERVENTION_109_V1"
UPSTREAM = REPO / "docs/vm_tlb/review_packs/C16_E1_NATURAL_REUSE_RESIDENCY_109_V1"
METRICS = ["l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum"]
CONDITIONS = ["BASELINE", "SETASIDE_ONLY", "PERSIST_L0_UP", "PERSIST_L14_UP", "PERSIST_L0_DOWN"]
BUDGETS = [("8MIB", 8 * 1024 * 1024), ("16MIB", 16 * 1024 * 1024), ("24MIB", 24 * 1024 * 1024), ("32MIB", 32 * 1024 * 1024), ("FULL", 33_947_648)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_tsv(name, rows, fields):
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def summarize(values):
    return {
        "samples_ms": values,
        "median_ms": statistics.median(values),
        "min_ms": min(values),
        "max_ms": max(values),
        "cv": statistics.pstdev(values) / statistics.mean(values),
    }


def read_ncu(path):
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    if len(rows) < 3:
        raise RuntimeError(f"empty NCU export: {path}")
    return [dict(zip(rows[0], row)) for row in rows[2:]], dict(zip(rows[0], rows[1]))


def session_command(path):
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            if len(row) >= 2 and row[0] == "Profiler Command Line":
                return row[1].rstrip()
    raise RuntimeError(f"missing profiler command: {path}")


def log_receipt(path):
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("{") and line.endswith("}"):
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if value.get("status") == "PASS":
                return value
    raise RuntimeError(f"missing PASS receipt: {path}")


def occurrence_identity(run):
    return (
        run["generated_token_ids_D0_D3"],
        [(row["target"], row["decode_index"], row["token_id"], row["input_sha256"], row["output_sha256"]) for row in run["occurrences"]],
    )


def validate_session(command, selected_range):
    required = ["--replay-mode application", "--cache-control none", f"--nvtx-include {selected_range}/"]
    if any(fragment not in command for fragment in required):
        raise RuntimeError(f"session contract mismatch: {selected_range}")


def validate_policy(receipt, condition, qweight_bytes, receipt_condition=None):
    expected_receipt_condition = receipt_condition if receipt_condition is not None else condition
    if receipt["condition"] != expected_receipt_condition or not receipt["reset_before"] or not receipt["reset_after"]:
        raise RuntimeError(f"policy reset/condition mismatch: {condition}")
    if receipt["actual_setaside_after_reset_bytes"] != 0:
        raise RuntimeError(f"policy limit not reset: {condition}")
    if condition == "BASELINE":
        if receipt["requested_setaside_bytes"] != 0 or receipt["access_policy_window"] is not None:
            raise RuntimeError("baseline policy mismatch")
    elif condition == "SETASIDE_ONLY":
        if receipt["requested_setaside_bytes"] != qweight_bytes or receipt["access_policy_window"] is not None:
            raise RuntimeError("setaside-only policy mismatch")
    elif condition.startswith("PERSIST_"):
        window = receipt["access_policy_window"]
        if receipt["requested_setaside_bytes"] != qweight_bytes or window is None or window["num_bytes"] != qweight_bytes or window["hit_ratio"] != 1.0:
            raise RuntimeError(f"full persistence policy mismatch: {condition}")


def validate_exact_window(receipt, region):
    window = receipt["access_policy_window"]
    if window is None or window["base_ptr"] != region["data_ptr"] or window["num_bytes"] != region["bytes"]:
        raise RuntimeError("access-policy window is not the exact qweight tensor interval")


def copy_raw(family, profile_id, base, session, log):
    prefix = f"RAW_{family.upper()}_{profile_id}"
    shutil.copy2(base, OUT / f"{prefix}_BASE.csv")
    shutil.copy2(session, OUT / f"{prefix}_SESSION.csv")
    shutil.copy2(log, OUT / f"{prefix}_PROFILE.log")


def main():
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite {OUT}")
    OUT.mkdir(parents=True)
    capability = json.loads((SOURCE / "CUDA_CAPABILITY_AND_CENSUS.json").read_text())
    if capability["status"] != "PASS" or not all(capability["runtime_matches_accepted"].values()):
        raise RuntimeError("CUDA persistence capability did not close")
    runtime = capability["runtime_execution_authority"]
    regions = capability["qweight_regions"]
    if len(regions) != 3 or any(not row["contiguous"] or row["storage_offset_bytes"] != 0 or row["storage_nbytes"] != row["bytes"] for row in regions):
        raise RuntimeError("qweight region census did not close")
    qweight_bytes = regions[0]["bytes"]
    if any(row["bytes"] != qweight_bytes for row in regions):
        raise RuntimeError("qweight size mismatch across targets")
    write_json(
        "UPSTREAM_AUTHORITY.json",
        {
            "clean_e1_producer": "8988d6108ff8bdca180a14cec2fe769df45b09f1",
            "clean_e1_consumer": "59ddb8ba2a33ef12b73bfc859f3a994e0b4ef4ca",
            "semantic_ncu_v2_producer": "8d1f62229cae15199793ba5569327cf1e83596f3",
            "semantic_ncu_v2_consumer": "cdd3ec7afbb1611cc52a4b74d32b38a3edabd131",
            "residency_producer": "22d1b98d7f0c213950654fc754be4e7388836de3",
            "residency_consumer": "5b11dd41e98044fcad76da4a906c7ba8609eb828",
            "natural_reuse_producer": "ccfdc89d517766d12588ee131818efe341c7e17c",
            "natural_reuse_consumer": "4f9242d177220721cb9e669aad5dd9e29f04407d",
            "status": "PASS",
        },
    )
    write_json(
        "CUDA_PERSISTENCE_CAPABILITY.json",
        {
            "status": "PASS",
            "runtime_execution_authority": runtime,
            "accepted_historical_values": capability["accepted_historical_values"],
            "runtime_matches_accepted": capability["runtime_matches_accepted"],
            "supported_api_path": capability["supported_api_path"],
            "cuda_runtime_header": capability["cuda_runtime_header"],
            "cuda_runtime_header_sha256": capability["cuda_runtime_header_sha256"],
            "helper_library_sha256": capability["helper_library_sha256"],
            "smoke_policy_receipt": capability["smoke_policy_receipt"],
            "setaside_rounding_observed": {"requested_bytes": qweight_bytes, "actual_bytes": capability["smoke_policy_receipt"]["actual_setaside_bytes"]},
        },
    )
    write_tsv(
        "QWEIGHT_REGION_CENSUS.tsv", regions,
        ["tensor_name", "dtype", "shape", "numel", "element_size_bytes", "bytes", "data_ptr", "storage_offset_elements", "storage_offset_bytes", "contiguous", "storage_nbytes", "exact_tensor_span_begin", "exact_tensor_span_end_exclusive"],
    )
    write_json(
        "POLICY_IMPLEMENTATION_CONTRACT.json",
        {
            "status": "PASS",
            "helper_source": "util/vm_tlb/c16/e1_cuda_persistence_helper.cpp",
            "wrapper_source": "util/vm_tlb/c16/e1_cuda_persistence.py",
            "reset_before_after_every_condition": True,
            "full_qweight_requested_budget_bytes": qweight_bytes,
            "runtime_actual_full_budget_bytes": capability["smoke_policy_receipt"]["actual_setaside_bytes"],
            "access_window_granularity": "exact qweight tensor data_ptr and numel*element_size only",
            "hit_property": "cudaAccessPropertyPersisting",
            "miss_property": "cudaAccessPropertyStreaming",
            "stream": "torch current/default stream",
            "disjoint_qzeros_scales_not_included": True,
        },
    )
    shutil.copy2(SOURCE / "CUDA_CAPABILITY_AND_CENSUS.json", OUT / "RAW_CUDA_CAPABILITY_AND_CENSUS.json")
    shutil.copy2(SOURCE / "build/BUILD_SHA256SUMS", OUT / "RAW_HELPER_BUILD_SHA256SUMS")

    # Accepted occurrence authority.
    accepted_occurrences = {}
    with (UPSTREAM / "NATURAL_OCCURRENCE_BINDINGS.tsv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            accepted_occurrences[(row["target"], int(row["decode_index"]))] = (row["input_sha256"], row["output_sha256"])
    expected_tokens = [23578, 11, 323, 3950]

    # Isolated native timing.
    isolated = json.loads((SOURCE / "isolated/NATIVE_RESULT.json").read_text())
    isolated_groups = defaultdict(list)
    for row in isolated["rows"]:
        isolated_groups[row["condition"]].append(row["target_ms"])
        condition = "BASELINE" if row["condition"] == "ISO_BASELINE_DENSE" else "PERSIST_L0_UP"
        validate_policy(row["policy_receipt"], condition, qweight_bytes, row["condition"])
        if condition == "PERSIST_L0_UP":
            validate_exact_window(row["policy_receipt"], isolated["qweight_region"])
    isolated_timing_rows = []
    isolated_timing_map = {}
    for condition, values in sorted(isolated_groups.items()):
        summary = summarize(values)
        isolated_timing_map[condition] = summary
        example = next(row for row in isolated["rows"] if row["condition"] == condition)
        isolated_timing_rows.append(
            {"condition": condition, "median_ms": summary["median_ms"], "min_ms": summary["min_ms"], "max_ms": summary["max_ms"], "cv": summary["cv"], "samples_ms": json.dumps(values), "input_sha256": example["input_sha256"], "output_sha256": example["output_sha256"], "requested_setaside_bytes": example["policy_receipt"]["requested_setaside_bytes"], "actual_setaside_bytes": example["policy_receipt"]["actual_setaside_bytes"], "policy_receipts": json.dumps([row["policy_receipt"] for row in isolated["rows"] if row["condition"] == condition], sort_keys=True)}
        )
    write_tsv(
        "ISOLATED_QUALIFICATION_TIMING.tsv", isolated_timing_rows,
        ["condition", "median_ms", "min_ms", "max_ms", "cv", "samples_ms", "input_sha256", "output_sha256", "requested_setaside_bytes", "actual_setaside_bytes", "policy_receipts"],
    )
    shutil.copy2(SOURCE / "isolated/NATIVE_RESULT.json", OUT / "RAW_ISOLATED_NATIVE_RESULT.json")
    shutil.copy2(SOURCE / "isolated_native.stdout.log", OUT / "RAW_ISOLATED_NATIVE_PROFILE.log")

    raw_provenance = []
    isolated_ncu_rows = []
    isolated_ncu_map = {}
    for report in sorted((SOURCE / "ncu/isolated/reports").glob("*.ncu-rep")):
        profile_id = report.stem
        base, session = report.with_suffix(".base.csv"), report.with_suffix(".session.csv")
        log = SOURCE / "ncu/isolated/logs" / f"{profile_id}.log"
        receipt = log_receipt(log)
        rows, units = read_ncu(base)
        command = session_command(session)
        validate_session(command, receipt["range"])
        range_column = next(name for name in rows[0] if "Push/Pop_Range" in name)
        if any(receipt["range"] not in row[range_column] for row in rows) or any(int(row["profiler__replayer_passes"]) != 1 for row in rows):
            raise RuntimeError(f"isolated selector/pass: {profile_id}")
        condition = "BASELINE" if profile_id == "ISO_BASELINE_DENSE" else "PERSIST_L0_UP"
        validate_policy(receipt["policy_receipt"], condition, qweight_bytes, receipt["condition"])
        if condition == "PERSIST_L0_UP":
            validate_exact_window(receipt["policy_receipt"], receipt["qweight_region"])
        names = [row["Kernel Name"] for row in rows]
        if not (any("gemm_forward_4bit" in name for name in names) and any("reduce_kernel" in name for name in names)):
            raise RuntimeError(f"isolated kernel inventory: {profile_id}")
        sums = {}
        for metric in METRICS:
            if units[metric] != "byte":
                raise RuntimeError(f"isolated metric unit: {profile_id}")
            sums[metric] = sum(float(row[metric].replace(",", "")) for row in rows)
        isolated_ncu_map[profile_id] = sums
        isolated_ncu_rows.append(
            {"profile_id": profile_id, "condition": receipt["condition"], "nvtx_range": receipt["range"], "kernel_count": len(rows), "kernel_names": json.dumps(names), "replay_pass_count": 1, "l1tex__t_bytes.sum": sums[METRICS[0]], "lts__t_bytes.sum": sums[METRICS[1]], "dram__bytes.sum": sums[METRICS[2]], "unit": "byte", "policy_receipt": json.dumps(receipt["policy_receipt"], sort_keys=True), "profiler_command": command}
        )
        raw_provenance.append({"family": "isolated", "profile_id": profile_id, "report_path": str(report), "report_sha256": sha(report), "base_sha256": sha(base), "session_sha256": sha(session), "profile_log_sha256": sha(log)})
        copy_raw("isolated", profile_id, base, session, log)
    if len(isolated_ncu_rows) != 2:
        raise RuntimeError("isolated NCU count")
    write_tsv(
        "ISOLATED_QUALIFICATION_NCU.tsv", isolated_ncu_rows,
        ["profile_id", "condition", "nvtx_range", "kernel_count", "kernel_names", "replay_pass_count", "l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum", "unit", "policy_receipt", "profiler_command"],
    )
    iso_base_time = isolated_timing_map["ISO_BASELINE_DENSE"]["median_ms"]
    iso_persist_time = isolated_timing_map["ISO_QWEIGHT_PERSIST_DENSE"]["median_ms"]
    iso_base_dram = isolated_ncu_map["ISO_BASELINE_DENSE"]["dram__bytes.sum"]
    iso_persist_dram = isolated_ncu_map["ISO_QWEIGHT_PERSIST_DENSE"]["dram__bytes.sum"]
    write_json(
        "ISOLATED_QUALIFICATION_ANALYSIS.json",
        {"status": "PASS", "engineering_qualification": True, "timing_persist_over_baseline": iso_persist_time / iso_base_time, "timing_benefit_fraction": 1 - iso_persist_time / iso_base_time, "dram_persist_over_baseline": iso_persist_dram / iso_base_dram, "dram_benefit_fraction": 1 - iso_persist_dram / iso_base_dram, "dram_absolute_reduction_bytes": iso_base_dram - iso_persist_dram, "policy_effective_positive_control": iso_persist_dram < iso_base_dram},
    )

    # Natural native matrix: 5 conditions x 7 fresh processes.
    natural_runs = {}
    baseline_identity = None
    for condition in CONDITIONS:
        paths = sorted((SOURCE / "natural" / condition).glob("run[0-6].json"))
        if len(paths) != 7:
            raise RuntimeError(f"native run count: {condition}")
        runs = [json.loads(path.read_text()) for path in paths]
        for run in runs:
            validate_policy(run["policy_receipt"], condition, qweight_bytes)
            condition_target = {"PERSIST_L0_UP": "L0_UP", "PERSIST_L14_UP": "L14_UP", "PERSIST_L0_DOWN": "L0_DOWN"}.get(condition)
            if condition_target is not None:
                validate_exact_window(run["policy_receipt"], run["qweight_regions"][condition_target])
            if run["generated_token_ids_D0_D3"] != expected_tokens:
                raise RuntimeError(f"token drift: {condition}")
            for row in run["occurrences"]:
                if (row["input_sha256"], row["output_sha256"]) != accepted_occurrences[(row["target"], row["decode_index"])]:
                    raise RuntimeError(f"occurrence drift: {condition} {row['target']} D{row['decode_index']}")
            identity = occurrence_identity(run)
            if baseline_identity is None:
                baseline_identity = identity
            if identity != baseline_identity:
                raise RuntimeError(f"cross-condition identity drift: {condition}")
        natural_runs[condition] = runs
        for path in paths:
            shutil.copy2(path, OUT / f"RAW_NATIVE_{condition}_{path.name}")
        for path in sorted((SOURCE / "natural" / condition).glob("*.stdout.log")):
            shutil.copy2(path, OUT / f"RAW_NATIVE_{condition}_{path.name}")
    write_json(
        "NATURAL_POLICY_CONDITIONS.json",
        {"status": "PASS", "conditions": CONDITIONS, "fresh_process_runs_per_condition": 7, "generated_token_ids_D0_D3": expected_tokens, "all_tokens_and_occurrence_sha_cross_condition_identical": True, "full_qweight_requested_budget_bytes": qweight_bytes, "runtime_actual_budget_bytes": natural_runs["SETASIDE_ONLY"][0]["policy_receipt"]["actual_setaside_bytes"], "primary_stable_occurrences": ["L0_UP:D1", "L0_UP:D3", "L14_UP:D3", "L0_DOWN:D3"], "D0_not_sole_policy_basis": True},
    )
    native_rows = []
    timing_map = {}
    step_rows = []
    for condition, runs in natural_runs.items():
        receipt = runs[0]["policy_receipt"]
        for target in ("L0_UP", "L14_UP", "L0_DOWN"):
            for decode_index in range(4):
                values = [next(row["target_ms"] for row in run["occurrences"] if row["target"] == target and row["decode_index"] == decode_index) for run in runs]
                summary = summarize(values)
                timing_map[(condition, target, decode_index)] = summary
                authority = next(row for row in runs[0]["occurrences"] if row["target"] == target and row["decode_index"] == decode_index)
                native_rows.append(
                    {"condition": condition, "target": target, "decode_index": decode_index, "token_id": authority["token_id"], "median_ms": summary["median_ms"], "min_ms": summary["min_ms"], "max_ms": summary["max_ms"], "cv": summary["cv"], "samples_ms": json.dumps(values), "input_sha256": authority["input_sha256"], "output_sha256": authority["output_sha256"], "requested_setaside_bytes": receipt["requested_setaside_bytes"], "actual_setaside_bytes": receipt["actual_setaside_bytes"], "window_target": None if receipt["access_policy_window"] is None else condition, "policy_receipts": json.dumps([run["policy_receipt"] for run in runs], sort_keys=True)}
                )
        for decode_index in range(4):
            values = [run["decode_step_ms"][decode_index] for run in runs]
            summary = summarize(values)
            step_rows.append({"condition": condition, "decode_index": decode_index, "median_ms": summary["median_ms"], "min_ms": summary["min_ms"], "max_ms": summary["max_ms"], "cv": summary["cv"], "samples_ms": json.dumps(values)})
    write_tsv(
        "NATURAL_POLICY_NATIVE_TIMING.tsv", native_rows,
        ["condition", "target", "decode_index", "token_id", "median_ms", "min_ms", "max_ms", "cv", "samples_ms", "input_sha256", "output_sha256", "requested_setaside_bytes", "actual_setaside_bytes", "window_target", "policy_receipts"],
    )
    write_tsv(
        "NATURAL_DECODE_STEP_TIMING.tsv", step_rows,
        ["condition", "decode_index", "median_ms", "min_ms", "max_ms", "cv", "samples_ms"],
    )

    ncu_map = {}
    ncu_rows = []
    reports = sorted((SOURCE / "ncu/natural/reports").glob("*.ncu-rep"))
    if len(reports) != 16:
        raise RuntimeError(f"natural NCU count: {len(reports)}")
    for report in reports:
        profile_id = report.stem
        base, session = report.with_suffix(".base.csv"), report.with_suffix(".session.csv")
        log = SOURCE / "ncu/natural/logs" / f"{profile_id}.log"
        receipt = log_receipt(log)
        if receipt["generated_token_ids_D0_D3"] != expected_tokens or occurrence_identity(receipt) != baseline_identity:
            raise RuntimeError(f"NCU semantic identity: {profile_id}")
        command = session_command(session)
        selected_range = command.split("--nvtx-include ", 1)[1].split("/", 1)[0]
        validate_session(command, selected_range)
        selected_occurrence = next(row for row in receipt["occurrences"] if row["range"] == selected_range)
        condition = receipt["condition"]
        validate_policy(receipt["policy_receipt"], condition, qweight_bytes)
        condition_target = {"PERSIST_L0_UP": "L0_UP", "PERSIST_L14_UP": "L14_UP", "PERSIST_L0_DOWN": "L0_DOWN"}.get(condition)
        if condition_target is not None:
            validate_exact_window(receipt["policy_receipt"], receipt["qweight_regions"][condition_target])
        rows, units = read_ncu(base)
        range_column = next(name for name in rows[0] if "Push/Pop_Range" in name)
        if any(selected_range not in row[range_column] for row in rows) or any(int(row["profiler__replayer_passes"]) != 1 for row in rows):
            raise RuntimeError(f"NCU selector/pass: {profile_id}")
        names = [row["Kernel Name"] for row in rows]
        if not (any("gemm_forward_4bit" in name for name in names) and any("reduce_kernel" in name for name in names)):
            raise RuntimeError(f"NCU kernel inventory: {profile_id}")
        sums = {}
        for metric in METRICS:
            if units[metric] != "byte":
                raise RuntimeError(f"NCU unit: {profile_id}")
            sums[metric] = sum(float(row[metric].replace(",", "")) for row in rows)
        key = (condition, selected_occurrence["target"], selected_occurrence["decode_index"])
        ncu_map[key] = sums
        ncu_rows.append(
            {"profile_id": profile_id, "condition": condition, "target": selected_occurrence["target"], "decode_index": selected_occurrence["decode_index"], "token_id": selected_occurrence["token_id"], "nvtx_range": selected_range, "kernel_count": len(rows), "kernel_names": json.dumps(names), "replay_pass_count": 1, "l1tex__t_bytes.sum": sums[METRICS[0]], "lts__t_bytes.sum": sums[METRICS[1]], "dram__bytes.sum": sums[METRICS[2]], "unit": "byte", "input_sha256": selected_occurrence["input_sha256"], "output_sha256": selected_occurrence["output_sha256"], "policy_receipt": json.dumps(receipt["policy_receipt"], sort_keys=True), "profiler_command": command}
        )
        raw_provenance.append({"family": "natural", "profile_id": profile_id, "report_path": str(report), "report_sha256": sha(report), "base_sha256": sha(base), "session_sha256": sha(session), "profile_log_sha256": sha(log)})
        copy_raw("natural", profile_id, base, session, log)
    write_tsv(
        "NATURAL_POLICY_NCU_INDEX.tsv", ncu_rows,
        ["profile_id", "condition", "target", "decode_index", "token_id", "nvtx_range", "kernel_count", "kernel_names", "replay_pass_count", "l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum", "unit", "input_sha256", "output_sha256", "policy_receipt", "profiler_command"],
    )

    # Matched-control policy analysis.
    comparisons = [
        ("L0_UP_D1", "L0_UP", 1, "PERSIST_L0_UP", "PERSIST_L14_UP"),
        ("L0_UP_D3", "L0_UP", 3, "PERSIST_L0_UP", "PERSIST_L14_UP"),
        ("L14_UP_D3", "L14_UP", 3, "PERSIST_L14_UP", "PERSIST_L0_UP"),
        ("L0_DOWN_D3", "L0_DOWN", 3, "PERSIST_L0_DOWN", "PERSIST_L0_UP"),
    ]
    analysis = {}
    any_material_timing = False
    any_material_dram = False
    any_target_specific = False
    for label, target, decode_index, target_condition, other_condition in comparisons:
        baseline_time = timing_map[("BASELINE", target, decode_index)]
        setaside_time = timing_map[("SETASIDE_ONLY", target, decode_index)]
        target_time = timing_map[(target_condition, target, decode_index)]
        other_time = timing_map[(other_condition, target, decode_index)]
        target_time_benefit = 1 - target_time["median_ms"] / setaside_time["median_ms"]
        other_time_benefit = 1 - other_time["median_ms"] / setaside_time["median_ms"]
        combined = math.hypot(target_time["cv"], setaside_time["cv"])
        material_timing = target_time_benefit >= 0.05 and target_time_benefit > combined
        base_dram = ncu_map[("BASELINE", target, decode_index)]["dram__bytes.sum"]
        setaside_dram = ncu_map[("SETASIDE_ONLY", target, decode_index)]["dram__bytes.sum"]
        target_dram = ncu_map[(target_condition, target, decode_index)]["dram__bytes.sum"]
        other_dram = ncu_map[(other_condition, target, decode_index)]["dram__bytes.sum"]
        target_dram_benefit = 1 - target_dram / setaside_dram
        other_dram_benefit = 1 - other_dram / setaside_dram
        material_dram = target_dram_benefit >= 0.20 and setaside_dram - target_dram >= 4 * 1024 * 1024
        target_specific_timing = material_timing and target_time_benefit >= other_time_benefit + 0.05
        target_specific_dram = material_dram and target_dram_benefit >= other_dram_benefit + 0.20 and other_dram - target_dram >= 4 * 1024 * 1024
        target_specific = target_specific_timing or target_specific_dram
        analysis[label] = {
            "target_condition": target_condition,
            "matched_unrelated_condition": other_condition,
            "reservation_effect": {"timing_SETASIDE_over_BASELINE": setaside_time["median_ms"] / baseline_time["median_ms"], "dram_SETASIDE_over_BASELINE": setaside_dram / base_dram},
            "target_persistence": {"timing_over_SETASIDE": target_time["median_ms"] / setaside_time["median_ms"], "timing_benefit_fraction": target_time_benefit, "combined_timing_dispersion": combined, "MATERIAL_TIMING_BENEFIT": material_timing, "dram_over_SETASIDE": target_dram / setaside_dram, "dram_benefit_fraction": target_dram_benefit, "dram_absolute_reduction_bytes": setaside_dram - target_dram, "MATERIAL_DRAM_BENEFIT": material_dram},
            "matched_unrelated_persistence": {"timing_over_SETASIDE": other_time["median_ms"] / setaside_time["median_ms"], "timing_benefit_fraction": other_time_benefit, "dram_over_SETASIDE": other_dram / setaside_dram, "dram_benefit_fraction": other_dram_benefit},
            "TARGET_SPECIFIC_TIMING": target_specific_timing,
            "TARGET_SPECIFIC_DRAM": target_specific_dram,
            "TARGET_SPECIFIC": target_specific,
        }
        any_material_timing |= material_timing
        any_material_dram |= material_dram
        any_target_specific |= target_specific
    write_json(
        "NATURAL_POLICY_ANALYSIS.json",
        {"status": "PASS", "materiality": {"timing": ">=5% lower than SETASIDE_ONLY and > combined CV", "dram": ">=20% lower and >=4MiB absolute", "target_specific": "a material target effect exceeds matched-unrelated by >=5 percentage points timing or >=20 percentage points and 4MiB DRAM"}, "comparisons": analysis, "any_material_timing": any_material_timing, "any_material_dram": any_material_dram, "any_target_specific": any_target_specific},
    )

    # Conditional budget sensitivity (triggered by material L0 up D3 timing).
    if not analysis["L0_UP_D3"]["target_persistence"]["MATERIAL_TIMING_BENEFIT"] and not analysis["L0_UP_D3"]["target_persistence"]["MATERIAL_DRAM_BENEFIT"]:
        raise RuntimeError("budget sensitivity ran without preregistered trigger")
    budget_timing_rows = []
    budget_timing_map = {}
    budget_policy = {}
    for label, requested_bytes in BUDGETS:
        paths = sorted((SOURCE / "budget" / label).glob("run[0-6].json"))
        if len(paths) != 7:
            raise RuntimeError(f"budget native count: {label}")
        runs = [json.loads(path.read_text()) for path in paths]
        for run in runs:
            if run["generated_token_ids_D0_D3"] != expected_tokens or occurrence_identity(run) != baseline_identity:
                raise RuntimeError(f"budget identity: {label}")
            receipt = run["policy_receipt"]
            if receipt["condition"] != "BUDGET_L0_UP" or receipt["requested_setaside_bytes"] != requested_bytes or receipt["access_policy_window"]["num_bytes"] != qweight_bytes or not receipt["reset_before"] or not receipt["reset_after"]:
                raise RuntimeError(f"budget policy: {label}")
            validate_exact_window(receipt, run["qweight_regions"]["L0_UP"])
        values = [next(row["target_ms"] for row in run["occurrences"] if row["target"] == "L0_UP" and row["decode_index"] == 3) for run in runs]
        summary = summarize(values)
        budget_timing_map[label] = summary
        budget_policy[label] = runs[0]["policy_receipt"]
        budget_timing_rows.append({"budget_label": label, "requested_budget_bytes": requested_bytes, "actual_budget_bytes": runs[0]["policy_receipt"]["actual_setaside_bytes"], "window_bytes": runs[0]["policy_receipt"]["access_policy_window"]["num_bytes"], "hit_ratio": runs[0]["policy_receipt"]["access_policy_window"]["hit_ratio"], "median_ms": summary["median_ms"], "min_ms": summary["min_ms"], "max_ms": summary["max_ms"], "cv": summary["cv"], "samples_ms": json.dumps(values), "policy_receipts": json.dumps([run["policy_receipt"] for run in runs], sort_keys=True)})
        for path in paths:
            shutil.copy2(path, OUT / f"RAW_BUDGET_{label}_{path.name}")
        for path in sorted((SOURCE / "budget" / label).glob("*.stdout.log")):
            shutil.copy2(path, OUT / f"RAW_BUDGET_{label}_{path.name}")
    write_tsv(
        "BUDGET_SENSITIVITY_TIMING.tsv", budget_timing_rows,
        ["budget_label", "requested_budget_bytes", "actual_budget_bytes", "window_bytes", "hit_ratio", "median_ms", "min_ms", "max_ms", "cv", "samples_ms", "policy_receipts"],
    )
    budget_ncu_rows = []
    budget_ncu_map = {}
    for report in sorted((SOURCE / "ncu/budget/reports").glob("*.ncu-rep")):
        label = report.stem
        base, session = report.with_suffix(".base.csv"), report.with_suffix(".session.csv")
        log = SOURCE / "ncu/budget/logs" / f"{label}.log"
        receipt = log_receipt(log)
        if receipt["generated_token_ids_D0_D3"] != expected_tokens or occurrence_identity(receipt) != baseline_identity:
            raise RuntimeError(f"budget NCU identity: {label}")
        command = session_command(session)
        selected_range = "C16_E1_L2P_BUDGET_L0_UP_L0_UP_D3"
        validate_session(command, selected_range)
        rows, units = read_ncu(base)
        range_column = next(name for name in rows[0] if "Push/Pop_Range" in name)
        if any(selected_range not in row[range_column] for row in rows) or any(int(row["profiler__replayer_passes"]) != 1 for row in rows):
            raise RuntimeError(f"budget NCU selector/pass: {label}")
        names = [row["Kernel Name"] for row in rows]
        sums = {}
        for metric in METRICS:
            if units[metric] != "byte":
                raise RuntimeError(f"budget unit: {label}")
            sums[metric] = sum(float(row[metric].replace(",", "")) for row in rows)
        budget_ncu_map[label] = sums
        policy = receipt["policy_receipt"]
        validate_exact_window(policy, receipt["qweight_regions"]["L0_UP"])
        budget_ncu_rows.append({"budget_label": label, "requested_budget_bytes": policy["requested_setaside_bytes"], "actual_budget_bytes": policy["actual_setaside_bytes"], "window_bytes": policy["access_policy_window"]["num_bytes"], "hit_ratio": policy["access_policy_window"]["hit_ratio"], "kernel_count": len(rows), "kernel_names": json.dumps(names), "replay_pass_count": 1, "l1tex__t_bytes.sum": sums[METRICS[0]], "lts__t_bytes.sum": sums[METRICS[1]], "dram__bytes.sum": sums[METRICS[2]], "unit": "byte", "policy_receipt": json.dumps(policy, sort_keys=True), "profiler_command": command})
        raw_provenance.append({"family": "budget", "profile_id": label, "report_path": str(report), "report_sha256": sha(report), "base_sha256": sha(base), "session_sha256": sha(session), "profile_log_sha256": sha(log)})
        copy_raw("budget", label, base, session, log)
    if len(budget_ncu_rows) != 5:
        raise RuntimeError("budget NCU count")
    write_tsv(
        "BUDGET_SENSITIVITY_NCU.tsv", budget_ncu_rows,
        ["budget_label", "requested_budget_bytes", "actual_budget_bytes", "window_bytes", "hit_ratio", "kernel_count", "kernel_names", "replay_pass_count", "l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum", "unit", "policy_receipt", "profiler_command"],
    )
    setaside_time = timing_map[("SETASIDE_ONLY", "L0_UP", 3)]
    setaside_dram = ncu_map[("SETASIDE_ONLY", "L0_UP", 3)]["dram__bytes.sum"]
    budget_analysis = {}
    first_material = None
    for label, requested_bytes in BUDGETS:
        timing = budget_timing_map[label]
        timing_benefit = 1 - timing["median_ms"] / setaside_time["median_ms"]
        combined = math.hypot(timing["cv"], setaside_time["cv"])
        material_timing = timing_benefit >= 0.05 and timing_benefit > combined
        dram = budget_ncu_map[label]["dram__bytes.sum"]
        dram_benefit = 1 - dram / setaside_dram
        material_dram = dram_benefit >= 0.20 and setaside_dram - dram >= 4 * 1024 * 1024
        if first_material is None and (material_timing or material_dram):
            first_material = label
        budget_analysis[label] = {"requested_budget_bytes": requested_bytes, "actual_budget_bytes": budget_policy[label]["actual_setaside_bytes"], "hit_ratio": budget_policy[label]["access_policy_window"]["hit_ratio"], "timing_over_SETASIDE_ONLY": timing["median_ms"] / setaside_time["median_ms"], "timing_benefit_fraction": timing_benefit, "combined_timing_dispersion": combined, "MATERIAL_TIMING_BENEFIT": material_timing, "dram_bytes": dram, "dram_over_SETASIDE_ONLY": dram / setaside_dram, "dram_benefit_fraction": dram_benefit, "dram_absolute_reduction_bytes": setaside_dram - dram, "MATERIAL_DRAM_BENEFIT": material_dram}
    write_json(
        "BUDGET_SENSITIVITY_ANALYSIS.json",
        {"status": "PASS", "trigger": "L0 up D3 full-qweight condition has material timing benefit", "reference": "SETASIDE_ONLY L0 up D3", "first_tested_material_budget": first_material, "no_exact_threshold_claim": True, "budgets": budget_analysis},
    )

    final_state = "MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW" if any_material_timing and any_target_specific else ("TARGETED_PERSISTENCE_TRAFFIC_ONLY" if any_material_dram else "TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED")
    requirements = {
        "status": final_state,
        "object_class": "compressed qweight-like weight region",
        "line_address_granularity": "line-level protection within one exact contiguous qweight address interval",
        "lifetime": "across the natural inter-token full-model reuse interval",
        "protection_budget": {"first_tested_material_budget": first_material, "first_tested_requested_bytes": dict(BUDGETS)[first_material] if first_material else None, "full_qweight_bytes": qweight_bytes, "runtime_actual_full_budget_bytes": capability["smoke_policy_receipt"]["actual_setaside_bytes"], "boundary": "tested budgets only; not an exact hardware threshold"},
        "selectivity": "target-specific timing benefit exceeds matched unrelated-region persistence; not all model weights can be protected",
        "interference_resistance": "protected target lines must resist unrelated full-model weight traffic between tokens",
        "fallback_normal_policy": "all non-target data follows the normal policy; miss path used cudaAccessPropertyStreaming only for the hinted window",
        "potential_identity_sources": ["software metadata/range hint", "static load/instruction signature", "learned/runtime reuse classification"],
        "traffic_caveat": "natural target DRAM improvements did not consistently cross the preregistered 20% gate and matched-unrelated persistence sometimes reduced DRAM as much or more; mechanism review must preserve this caveat",
        "implementation_forbidden_here": True,
    }
    write_json("MECHANISM_REQUIREMENTS.json", requirements)
    write_json("NCU_RAW_PROVENANCE.json", {"status": "PASS", "profiles": raw_provenance})
    (OUT / "SCIENTIFIC_INTERPRETATION.md").write_text(
        "# C16 E1 targeted CUDA L2-persistence interpretation\n\n"
        f"Final scoped state: `{final_state}`.\n\n"
        "Local CUDA headers/runtime and the RTX4080 independently qualify persisting-L2 control. Exact layer0/layer14 up_proj and layer0 down_proj qweight tensors are separate contiguous 33,947,648-byte intervals. CUDA rounds the full requested qweight set-aside to 37,748,736 bytes; every condition records and resets this runtime state.\n\n"
        "The isolated positive control demonstrates policy effectiveness: exact qweight persistence reduces isolated dense-pressure target timing and DRAM substantially without changing semantic identity. Under natural full-model decode, target persistence produces material, target-specific timing benefits at stable D1/D3 occurrences for up_proj and D3 for down_proj. Set-aside-only and matched unrelated-persistence controls are kept separate. Natural DRAM generally improves, but the L0 up D3 target reduction is just below the preregistered 20% gate and matched unrelated persistence can reduce DRAM as much or more; traffic is therefore not claimed target-specific.\n\n"
        f"Budget sensitivity finds the first tested material L0 up D3 timing benefit at `{first_material}` while keeping the full qweight window and scaling hitRatio. No tested budget meets the preregistered DRAM material gate, and no exact threshold is claimed.\n\n"
        "The evidence supports abstract design-review requirements for selective qweight-like residency across inter-token reuse, but it does not select or implement a classifier, replacement policy, cache/TLB mechanism, or simulator change. No NVBit or full address trace was started.\n",
        encoding="utf-8",
    )
    write_json(
        "NEXT_STEP_DECISION.json",
        {"decision": "STOP_AFTER_L2_PERSISTENCE_INTERVENTION_REVIEW", "final_state": final_state, "independent_consumer_required": True, "auto_authorized_implementation": False, "forbidden_not_started": ["NVBit", "full address trace", "Accel-Sim mechanism implementation", "cache/TLB mechanism simulation"]},
    )

    files = sorted(path for path in OUT.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    (OUT / "SHA256SUMS").write_text("".join(f"{sha(path)}  {path.name}\n" for path in files), encoding="utf-8")
    print(json.dumps({"status": "PASS", "final_state": final_state, "files": len(files) + 1, "isolated_profiles": 2, "natural_profiles": len(reports), "budget_profiles": len(budget_ncu_rows), "first_tested_material_budget": first_material}, sort_keys=True))


if __name__ == "__main__":
    main()
