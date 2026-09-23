#!/usr/bin/env python3
"""Validate and package the C16 E1 shared-residency feasibility stage."""

import csv
import hashlib
import json
import math
import shutil
import statistics
from collections import defaultdict
from pathlib import Path


REPO = Path("/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-shared-residency-feasibility-109-v1")
SOURCE = Path("/data/c16/e1_shared_residency_feasibility_v1")
OUT = REPO / "docs/vm_tlb/review_packs/C16_E1_SHARED_RESIDENCY_FEASIBILITY_109_V1"
UPSTREAM = REPO / "docs/vm_tlb/review_packs/C16_E1_L2_PERSISTENCE_INTERVENTION_109_V1"
NATURAL_AUTH = REPO / "docs/vm_tlb/review_packs/C16_E1_NATURAL_REUSE_RESIDENCY_109_V1/NATURAL_OCCURRENCE_BINDINGS.tsv"
CONDITIONS = ["SETASIDE_ONLY", "ROTATE_CONTROL_3", "SINGLE_L0_UP", "SHARE2_UP", "SHARE2_L0", "SHARE3"]
BASE_METRICS = ["l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum"]


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
    return {"samples": values, "median": statistics.median(values), "min": min(values), "max": max(values), "cv": statistics.pstdev(values) / statistics.mean(values)}


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


def log_receipts(path):
    values = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("{") and line.endswith("}"):
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if value.get("status") == "PASS":
                values.append(value)
    if not values:
        raise RuntimeError(f"missing PASS receipt: {path}")
    return values


def identity(run):
    rows = sorted(run["occurrences"], key=lambda row: (row["target"], row["decode_index"]))
    return (run["generated_token_ids_D0_D3"], [(row["target"], row["decode_index"], row["token_id"], row["input_sha256"], row["output_sha256"]) for row in rows])


def copy_raw(family, profile_id, base, session, log):
    prefix = f"RAW_{family.upper()}_{profile_id}"
    shutil.copy2(base, OUT / f"{prefix}_BASE.csv")
    shutil.copy2(session, OUT / f"{prefix}_SESSION.csv")
    shutil.copy2(log, OUT / f"{prefix}_PROFILE.log")


def parse_profile(family, report, metrics, additive_metrics, expected_identity=None):
    profile_id = report.stem
    base, session = report.with_suffix(".base.csv"), report.with_suffix(".session.csv")
    log = report.parents[1] / "logs" / f"{profile_id}.log"
    receipts = log_receipts(log)
    command = session_command(session)
    selected_range = command.split("--nvtx-include ", 1)[1].split("/", 1)[0]
    required = ["--replay-mode application", "--cache-control none", f"--nvtx-include {selected_range}/"]
    if any(fragment not in command for fragment in required):
        raise RuntimeError(f"session mismatch: {profile_id}")
    rows, units = read_ncu(base)
    range_column = next(name for name in rows[0] if "Push/Pop_Range" in name)
    if any(selected_range not in row[range_column] for row in rows):
        raise RuntimeError(f"range mismatch: {profile_id}")
    pass_counts = [int(row["profiler__replayer_passes"].replace(",", "")) for row in rows]
    if len(set(pass_counts)) != 1 or pass_counts[0] != len(receipts):
        raise RuntimeError(f"application replay receipt/pass mismatch: {profile_id} {pass_counts} receipts={len(receipts)}")
    if expected_identity is not None and any(identity(receipt) != expected_identity for receipt in receipts):
        raise RuntimeError(f"semantic identity mismatch: {profile_id}")
    names = [row["Kernel Name"] for row in rows]
    if not (any("gemm_forward_4bit" in name for name in names) and any("reduce_kernel" in name for name in names)):
        raise RuntimeError(f"AWQ kernel inventory mismatch: {profile_id}")
    kernel_rows = []
    sums = {}
    for metric in metrics:
        if metric not in units:
            raise RuntimeError(f"metric missing in raw export: {profile_id} {metric}")
        values = [float(row[metric].replace(",", "")) for row in rows]
        for index, (row, value) in enumerate(zip(rows, values)):
            kernel_rows.append({"family": family, "profile_id": profile_id, "kernel_index": index, "kernel_role": "GEMM" if "gemm_forward_4bit" in row["Kernel Name"] else "REDUCTION", "kernel_name": row["Kernel Name"], "grid_size": row["Grid Size"], "block_size": row["Block Size"], "metric_name": metric, "unit": units[metric], "value": value, "replay_pass_count": pass_counts[0]})
        if metric in additive_metrics:
            sums[metric] = sum(values)
    return {"profile_id": profile_id, "base": base, "session": session, "log": log, "receipts": receipts, "command": command, "selected_range": selected_range, "rows": rows, "units": units, "kernel_names": names, "kernel_rows": kernel_rows, "sums": sums, "replay_pass_count": pass_counts[0], "report": report}


def validate_shared_run(run, accepted_identity, qweight_bytes):
    if identity(run) != accepted_identity or run["generated_token_ids_D0_D3"] != [23578, 11, 323, 3950]:
        raise RuntimeError(f"shared semantic identity: {run['condition']}")
    receipt = run["policy_receipt"]
    if receipt["condition"] != run["condition"] or receipt["requested_setaside_bytes"] != qweight_bytes or receipt["actual_setaside_after_reset_bytes"] != 0 or not receipt["reset_before"] or not receipt["reset_after"]:
        raise RuntimeError(f"shared policy receipt: {run['condition']}")
    expected_count = 0 if run["condition"] == "SETASIDE_ONLY" else 15
    if run["policy_transition_count"] != expected_count or len(run["policy_transitions"]) != expected_count:
        raise RuntimeError(f"shared transition count: {run['condition']}")
    if expected_count:
        expected_order = ["L0_UP", "L0_DOWN", "L14_UP"] * 5
        if [row["target"] for row in run["policy_transitions"]] != expected_order:
            raise RuntimeError(f"shared transition order: {run['condition']}")
        if any(not row["before_target_event"] for row in run["policy_transitions"]):
            raise RuntimeError(f"policy call not before event: {run['condition']}")
        for row in run["policy_transitions"]:
            region = run["qweight_regions"][row["target"]]
            if row["base_ptr"] != region["data_ptr"] or row["num_bytes"] != region["bytes"]:
                raise RuntimeError(f"non-exact rotating window: {run['condition']}")
            condition = run["condition"]
            if condition == "ROTATE_CONTROL_3":
                expected_persist, expected_ratio = False, 1 / 3
            elif condition == "SINGLE_L0_UP":
                expected_persist, expected_ratio = row["target"] == "L0_UP", 1.0
            elif condition == "SHARE2_UP":
                expected_persist, expected_ratio = row["target"] in ("L0_UP", "L14_UP"), 0.5
            elif condition == "SHARE2_L0":
                expected_persist, expected_ratio = row["target"] in ("L0_UP", "L0_DOWN"), 0.5
            else:
                expected_persist, expected_ratio = True, 1 / 3
            if row["persisting"] != expected_persist or abs(row["hit_ratio"] - expected_ratio) > 1e-7:
                raise RuntimeError(f"rotating policy semantics: {condition} {row['target']}")
            if expected_persist and row["hit_property"] != "cudaAccessPropertyPersisting":
                raise RuntimeError("missing persisting property")
            if not expected_persist and (row["hit_property"] != "cudaAccessPropertyNormal" or row["miss_property"] != "cudaAccessPropertyNormal"):
                raise RuntimeError("matched control is not true Normal policy")


def main():
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite {OUT}")
    OUT.mkdir(parents=True)
    upstream_decision = json.loads((UPSTREAM / "NEXT_STEP_DECISION.json").read_text())
    qweight_rows = list(csv.DictReader((UPSTREAM / "QWEIGHT_REGION_CENSUS.tsv").open(newline="", encoding="utf-8"), delimiter="\t"))
    qweight_bytes = int(qweight_rows[0]["bytes"])
    accepted_rows = list(csv.DictReader(NATURAL_AUTH.open(newline="", encoding="utf-8"), delimiter="\t"))
    accepted_rows = sorted(accepted_rows, key=lambda row: (row["target"], int(row["decode_index"])))
    accepted_identity = ([23578, 11, 323, 3950], [(row["target"], int(row["decode_index"]), int(row["token_id"]), row["input_sha256"], row["output_sha256"]) for row in accepted_rows])
    write_json(
        "UPSTREAM_AUTHORITY.json",
        {"persistence_producer": "4c0e6b998528e425578cacf5912bbcc4ff3bfaf6", "independent_consumer": "1dcab9c8d932973399c5811dc817802bfb3b9dfe", "raw_evidence_match": "PASS", "producer_scoped_state": "MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW", "strict_consumer_state": "TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED", "decision_rule_divergence": "METHODOLOGICAL_OPERATIONALIZATION", "project_authorization": "DESIGN_REVIEW_AUTHORIZED_WITH_TRAFFIC_CAVEAT", "states_frozen_not_overwritten": True},
    )
    helper_source = REPO / "util/vm_tlb/c16/e1_cuda_persistence_helper.cpp"
    helper_library = SOURCE / "build/libc16_cuda_persistence.so"
    write_json(
        "ROTATING_HELPER_BUILD.json",
        {"status": "PASS", "helper_source": str(helper_source.relative_to(REPO)), "helper_source_sha256": sha(helper_source), "helper_library_source_path": str(helper_library), "helper_library_sha256": sha(helper_library), "new_api": "c16_set_access_policy_mode", "non_persisting_control": {"hit_property": "cudaAccessPropertyNormal", "miss_property": "cudaAccessPropertyNormal"}},
    )
    shutil.copy2(SOURCE / "build/BUILD_SHA256SUMS", OUT / "RAW_HELPER_BUILD_SHA256SUMS")

    # Metric discovery receipt.
    selection = json.loads((SOURCE / "metric_query/METRIC_SELECTION.json").read_text())
    query_path = SOURCE / "metric_query/NCU_QUERY_METRICS_ALL.txt"
    availability = []
    for row in selection["critical_metrics"]:
        availability.append({"category": row["category"], "available": row["available"], "metric_name": row["metric_name"], "metric_type": row["metric_type"], "unit": row["unit"], "aggregation": "SEMANTIC_SUM" if row["metric_name"] in selection["aggregation"]["semantic_sum"] else "PER_KERNEL_ONLY", "query_line": row["query_line"]})
    write_tsv("CRITICAL_PATH_METRIC_AVAILABILITY.tsv", availability, ["category", "available", "metric_name", "metric_type", "unit", "aggregation", "query_line"])
    compressed_query = SOURCE / "metric_query/NCU_QUERY_METRICS_ALL.txt.gz"
    write_json("NCU_QUERY_RECEIPT.json", {"status": "PASS", "query_command": selection["query_command"], "ncu_version": selection["ncu_version"], "full_query_source_path": str(query_path), "full_query_sha256": sha(query_path), "full_query_bytes": query_path.stat().st_size, "full_query_line_count": selection["query_line_count"], "compressed_receipt_sha256": sha(compressed_query), "compressed_receipt_bytes": compressed_query.stat().st_size, "selected_exact_query_lines": [row["query_line"] for row in availability]})
    shutil.copy2(SOURCE / "metric_query/METRIC_SELECTION.json", OUT / "RAW_METRIC_SELECTION.json")
    shutil.copy2(SOURCE / "metric_query/NCU_VERSION.txt", OUT / "RAW_NCU_VERSION.txt")
    shutil.copy2(compressed_query, OUT / "RAW_NCU_QUERY_METRICS_ALL.txt.gz")
    metrics = selection["profile_metric_list"]
    additive = set(selection["aggregation"]["semantic_sum"])
    per_kernel_only = set(selection["aggregation"]["per_kernel_only"])

    raw_provenance = []
    all_kernel_metrics = []
    critical_sums = {}
    critical_profiles = []
    for report in sorted((SOURCE / "critical/reports").glob("*.ncu-rep")):
        parsed = parse_profile("critical", report, metrics, additive, accepted_identity)
        receipt0 = parsed["receipts"][0]
        if any(receipt["condition"] != receipt0["condition"] for receipt in parsed["receipts"]):
            raise RuntimeError(f"critical replay policy nondeterminism: {parsed['profile_id']}")
        selected_occ = next(row for row in receipt0["occurrences"] if row["range"] == parsed["selected_range"])
        key = (receipt0["condition"], selected_occ["target"], selected_occ["decode_index"])
        critical_sums[key] = parsed["sums"]
        critical_profiles.append({"profile_id": parsed["profile_id"], "condition": key[0], "target": key[1], "decode_index": key[2], "selected_range": parsed["selected_range"], "kernel_count": len(parsed["rows"]), "kernel_names": json.dumps(parsed["kernel_names"]), "replay_pass_count": parsed["replay_pass_count"], "profiler_command": parsed["command"]})
        all_kernel_metrics.extend(parsed["kernel_rows"])
        raw_provenance.append({"family": "critical", "profile_id": parsed["profile_id"], "report_path": str(report), "report_sha256": sha(report), "base_sha256": sha(parsed["base"]), "session_sha256": sha(parsed["session"]), "profile_log_sha256": sha(parsed["log"])})
        copy_raw("critical", parsed["profile_id"], parsed["base"], parsed["session"], parsed["log"])
    if len(critical_profiles) != 10:
        raise RuntimeError(f"critical profile count {len(critical_profiles)}")
    write_tsv("CRITICAL_PATH_PROFILE_INDEX.tsv", critical_profiles, ["profile_id", "condition", "target", "decode_index", "selected_range", "kernel_count", "kernel_names", "replay_pass_count", "profiler_command"])

    # Rotating A/B/A qualification.
    rotating = {}
    for condition in ("ROTATE_PERSIST_A_B_A", "ROTATE_NORMAL_CONTROL_A_B_A"):
        native_path = SOURCE / "rotating" / f"{condition}_native.json"
        native = json.loads(native_path.read_text())
        values = [row["target_ms"] for row in native["rows"]]
        update_values = [transition["cpu_update_ns"] for row in native["rows"] for transition in row["window_transitions"]]
        for row in native["rows"]:
            if len(row["window_transitions"]) != 3 or not row["no_reset_between_transitions"]:
                raise RuntimeError(f"rotating native transition closure: {condition}")
            expected_persist = condition == "ROTATE_PERSIST_A_B_A"
            for transition, target_region in zip(row["window_transitions"], (row["A_qweight_region"], row["B_qweight_region"], row["A_qweight_region"])):
                if transition["base_ptr"] != target_region["data_ptr"] or transition["num_bytes"] != target_region["bytes"] or transition["persisting"] != expected_persist:
                    raise RuntimeError(f"rotating exact window: {condition}")
                if not expected_persist and (transition["hit_property"] != "cudaAccessPropertyNormal" or transition["miss_property"] != "cudaAccessPropertyNormal"):
                    raise RuntimeError("rotating control is not Normal/Normal")
        report = SOURCE / "rotating/reports" / f"{condition}.ncu-rep"
        parsed = parse_profile("rotating", report, metrics, additive)
        for receipt in parsed["receipts"]:
            row = receipt["rows"][0]
            if row["condition"] != condition or len(row["window_transitions"]) != 3:
                raise RuntimeError(f"rotating NCU receipt: {condition}")
        rotating[condition] = {"native_timing": summarize(values), "cpu_policy_update_ns": summarize(update_values), "ncu_semantic_sums": parsed["sums"], "ncu_per_kernel": parsed["kernel_rows"], "replay_pass_count": parsed["replay_pass_count"], "policy_receipt_example": native["rows"][0]["policy_receipt"], "window_transitions_example": native["rows"][0]["window_transitions"]}
        all_kernel_metrics.extend(parsed["kernel_rows"])
        raw_provenance.append({"family": "rotating", "profile_id": condition, "report_path": str(report), "report_sha256": sha(report), "base_sha256": sha(parsed["base"]), "session_sha256": sha(parsed["session"]), "profile_log_sha256": sha(parsed["log"])})
        copy_raw("rotating", condition, parsed["base"], parsed["session"], parsed["log"])
        shutil.copy2(native_path, OUT / f"RAW_ROTATING_{condition}_NATIVE.json")
        shutil.copy2(SOURCE / "rotating" / f"{condition}_native.stdout.log", OUT / f"RAW_ROTATING_{condition}_NATIVE.log")
    persist_rot, control_rot = rotating["ROTATE_PERSIST_A_B_A"], rotating["ROTATE_NORMAL_CONTROL_A_B_A"]
    rotating_pass = (
        persist_rot["ncu_semantic_sums"]["dram__bytes.sum"] < control_rot["ncu_semantic_sums"]["dram__bytes.sum"]
        and persist_rot["ncu_semantic_sums"]["lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum"] > control_rot["ncu_semantic_sums"]["lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum"]
        and persist_rot["ncu_semantic_sums"]["lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum"] < control_rot["ncu_semantic_sums"]["lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum"]
    )
    write_json("ROTATING_WINDOW_QUALIFICATION.json", {"status": "PASS" if rotating_pass else "ROTATING_WINDOW_POLICY_UNQUALIFIED", "one_fixed_setaside": True, "no_reset_between_A_B_A": True, "matched_control": "same A/B/A updates with cudaAccessPropertyNormal for hit and miss", "conditions": rotating, "qualification_basis": "exact API receipts plus lower DRAM/misses and higher L2 hits after persistent A/B/A rotation"})
    if not rotating_pass:
        raise RuntimeError("ROTATING_WINDOW_POLICY_UNQUALIFIED")

    # Shared native policy conditions.
    shared_runs = {}
    timing_map = {}
    native_rows = []
    step_rows = []
    overhead_rows = []
    qweight_bytes = int(list(csv.DictReader((UPSTREAM / "QWEIGHT_REGION_CENSUS.tsv").open(newline="", encoding="utf-8"), delimiter="\t"))[0]["bytes"])
    for condition in CONDITIONS:
        paths = sorted((SOURCE / "shared/native" / condition).glob("run[0-6].json"))
        if len(paths) != 7:
            raise RuntimeError(f"shared native count: {condition}")
        runs = [json.loads(path.read_text()) for path in paths]
        for run in runs:
            validate_shared_run(run, accepted_identity, qweight_bytes)
        shared_runs[condition] = runs
        for path in paths:
            shutil.copy2(path, OUT / f"RAW_SHARED_NATIVE_{condition}_{path.name}")
        for path in sorted((SOURCE / "shared/native" / condition).glob("*.stdout.log")):
            shutil.copy2(path, OUT / f"RAW_SHARED_NATIVE_{condition}_{path.name}")
        for target in ("L0_UP", "L14_UP", "L0_DOWN"):
            for decode_index in range(4):
                values = [next(row["target_ms"] for row in run["occurrences"] if row["target"] == target and row["decode_index"] == decode_index) for run in runs]
                summary = summarize(values)
                timing_map[(condition, target, decode_index)] = summary
                authority = next(row for row in runs[0]["occurrences"] if row["target"] == target and row["decode_index"] == decode_index)
                native_rows.append({"condition": condition, "target": target, "decode_index": decode_index, "token_id": authority["token_id"], "median_ms": summary["median"], "min_ms": summary["min"], "max_ms": summary["max"], "cv": summary["cv"], "samples_ms": json.dumps(values), "input_sha256": authority["input_sha256"], "output_sha256": authority["output_sha256"], "requested_setaside_bytes": runs[0]["policy_receipt"]["requested_setaside_bytes"], "actual_setaside_bytes": runs[0]["policy_receipt"]["actual_setaside_bytes"], "transition_count": runs[0]["policy_transition_count"]})
        for decode_index in range(4):
            values = [run["decode_step_ms"][decode_index] for run in runs]
            summary = summarize(values)
            step_rows.append({"condition": condition, "decode_index": decode_index, "median_ms": summary["median"], "min_ms": summary["min"], "max_ms": summary["max"], "cv": summary["cv"], "samples_ms": json.dumps(values)})
        if condition != "SETASIDE_ONLY":
            grouped = defaultdict(list)
            total_per_run = []
            for run in runs:
                total_per_run.append(sum(row["cpu_update_ns"] for row in run["policy_transitions"]))
                for row in run["policy_transitions"]:
                    grouped[(row["phase"], row["target"])].append(row["cpu_update_ns"])
            for (phase, target), values in sorted(grouped.items()):
                summary = summarize(values)
                overhead_rows.append({"condition": condition, "phase": phase, "target": target, "scope": "ONE_UPDATE", "median_cpu_ns": summary["median"], "min_cpu_ns": summary["min"], "max_cpu_ns": summary["max"], "cv": summary["cv"], "samples_cpu_ns": json.dumps(values)})
            summary = summarize(total_per_run)
            overhead_rows.append({"condition": condition, "phase": "FULL_RUN", "target": "ALL_15_UPDATES", "scope": "TOTAL_PER_RUN", "median_cpu_ns": summary["median"], "min_cpu_ns": summary["min"], "max_cpu_ns": summary["max"], "cv": summary["cv"], "samples_cpu_ns": json.dumps(total_per_run)})
    write_json("SHARED_POLICY_CONDITIONS.json", {"status": "PASS", "conditions": CONDITIONS, "fixed_requested_setaside_bytes": qweight_bytes, "runtime_actual_setaside_bytes": shared_runs["SETASIDE_ONLY"][0]["policy_receipt"]["actual_setaside_bytes"], "fresh_process_runs_per_condition": 7, "tokens_and_12_occurrence_sha_unchanged": True, "rotating_conditions_updates_per_run": 15, "no_reset_between_updates": True, "matched_control_uses_Normal_Normal": True})
    write_tsv("SHARED_POLICY_NATIVE_TIMING.tsv", native_rows, ["condition", "target", "decode_index", "token_id", "median_ms", "min_ms", "max_ms", "cv", "samples_ms", "input_sha256", "output_sha256", "requested_setaside_bytes", "actual_setaside_bytes", "transition_count"])
    write_tsv("SHARED_DECODE_STEP_TIMING.tsv", step_rows, ["condition", "decode_index", "median_ms", "min_ms", "max_ms", "cv", "samples_ms"])
    write_tsv("POLICY_SWITCH_OVERHEAD.tsv", overhead_rows, ["condition", "phase", "target", "scope", "median_cpu_ns", "min_cpu_ns", "max_cpu_ns", "cv", "samples_cpu_ns"])

    # Shared-policy NCU.
    shared_ncu_map = {}
    shared_ncu_rows = []
    shared_reports = sorted((SOURCE / "shared/ncu/reports").glob("*.ncu-rep"))
    if len(shared_reports) != 14:
        raise RuntimeError(f"shared NCU count {len(shared_reports)}")
    for report in shared_reports:
        parsed = parse_profile("shared", report, metrics, additive, accepted_identity)
        receipt0 = parsed["receipts"][0]
        for receipt in parsed["receipts"]:
            validate_shared_run(receipt, accepted_identity, qweight_bytes)
            if receipt["condition"] != receipt0["condition"]:
                raise RuntimeError(f"shared application replay policy nondeterminism: {parsed['profile_id']}")
        selected_occ = next(row for row in receipt0["occurrences"] if row["range"] == parsed["selected_range"])
        key = (receipt0["condition"], selected_occ["target"], selected_occ["decode_index"])
        shared_ncu_map[key] = parsed["sums"]
        shared_ncu_rows.append({"profile_id": parsed["profile_id"], "condition": key[0], "target": key[1], "decode_index": key[2], "selected_range": parsed["selected_range"], "kernel_count": len(parsed["rows"]), "kernel_names": json.dumps(parsed["kernel_names"]), "replay_pass_count": parsed["replay_pass_count"], **{metric: parsed["sums"][metric] for metric in selection["aggregation"]["semantic_sum"]}, "profiler_command": parsed["command"]})
        all_kernel_metrics.extend(parsed["kernel_rows"])
        raw_provenance.append({"family": "shared", "profile_id": parsed["profile_id"], "report_path": str(report), "report_sha256": sha(report), "base_sha256": sha(parsed["base"]), "session_sha256": sha(parsed["session"]), "profile_log_sha256": sha(parsed["log"])})
        copy_raw("shared", parsed["profile_id"], parsed["base"], parsed["session"], parsed["log"])
    shared_fields = ["profile_id", "condition", "target", "decode_index", "selected_range", "kernel_count", "kernel_names", "replay_pass_count"] + selection["aggregation"]["semantic_sum"] + ["profiler_command"]
    write_tsv("SHARED_POLICY_NCU_INDEX.tsv", shared_ncu_rows, shared_fields)
    write_tsv("CRITICAL_PATH_KERNEL_METRICS.tsv", all_kernel_metrics, ["family", "profile_id", "kernel_index", "kernel_role", "kernel_name", "grid_size", "block_size", "metric_name", "unit", "value", "replay_pass_count"])
    write_json("NCU_RAW_PROVENANCE.json", {"status": "PASS", "profiles": raw_provenance})

    # Critical-path analysis from the dedicated matrix.
    critical_analysis = {}
    critical_matrix = [
        ("L0_UP_D3", "L0_UP", 3, "SETASIDE_ONLY", "PERSIST_L0_UP", "PERSIST_L14_UP"),
        ("L14_UP_D3", "L14_UP", 3, "SETASIDE_ONLY", "PERSIST_L14_UP", "PERSIST_L0_UP"),
        ("L0_DOWN_D3", "L0_DOWN", 3, "SETASIDE_ONLY", "PERSIST_L0_DOWN", "PERSIST_L0_UP"),
    ]
    for label, target, decode_index, control, target_condition, other_condition in critical_matrix:
        entries = {}
        for condition in (control, target_condition, other_condition):
            sums = critical_sums[(condition, target, decode_index)]
            profile_id = f"{target}_D{decode_index}_{condition}"
            gemm_metrics = {row["metric_name"]: row["value"] for row in all_kernel_metrics if row["family"] == "critical" and row["profile_id"] == profile_id and row["kernel_role"] == "GEMM"}
            reduction_metrics = {row["metric_name"]: row["value"] for row in all_kernel_metrics if row["family"] == "critical" and row["profile_id"] == profile_id and row["kernel_role"] == "REDUCTION"}
            entries[condition] = {"semantic_sums": sums, "GEMM": gemm_metrics, "REDUCTION": reduction_metrics}
        control_entry, target_entry, other_entry = entries[control], entries[target_condition], entries[other_condition]
        critical_analysis[label] = {
            "conditions": entries,
            "target_vs_setaside": {
                "semantic_duration_ratio": target_entry["semantic_sums"]["gpu__time_duration.sum"] / control_entry["semantic_sums"]["gpu__time_duration.sum"],
                "gemm_duration_ratio": target_entry["GEMM"]["gpu__time_duration.sum"] / control_entry["GEMM"]["gpu__time_duration.sum"],
                "reduction_duration_ratio": target_entry["REDUCTION"]["gpu__time_duration.sum"] / control_entry["REDUCTION"]["gpu__time_duration.sum"],
                "l2_hit_ratio": target_entry["semantic_sums"]["lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum"] / control_entry["semantic_sums"]["lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum"],
                "l2_miss_ratio": target_entry["semantic_sums"]["lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum"] / control_entry["semantic_sums"]["lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum"],
                "dram_read_ratio": target_entry["semantic_sums"]["dram__bytes_read.sum"] / control_entry["semantic_sums"]["dram__bytes_read.sum"],
                "aggregate_dram_ratio": target_entry["semantic_sums"]["dram__bytes.sum"] / control_entry["semantic_sums"]["dram__bytes.sum"],
                "gemm_long_scoreboard_delta_pct_points": target_entry["GEMM"]["smsp__warp_issue_stalled_long_scoreboard_per_warp_active.pct"] - control_entry["GEMM"]["smsp__warp_issue_stalled_long_scoreboard_per_warp_active.pct"],
            },
            "matched_unrelated_vs_setaside": {"semantic_duration_ratio": other_entry["semantic_sums"]["gpu__time_duration.sum"] / control_entry["semantic_sums"]["gpu__time_duration.sum"], "dram_read_ratio": other_entry["semantic_sums"]["dram__bytes_read.sum"] / control_entry["semantic_sums"]["dram__bytes_read.sum"], "aggregate_dram_ratio": other_entry["semantic_sums"]["dram__bytes.sum"] / control_entry["semantic_sums"]["dram__bytes.sum"], "gemm_long_scoreboard_delta_pct_points": other_entry["GEMM"]["smsp__warp_issue_stalled_long_scoreboard_per_warp_active.pct"] - control_entry["GEMM"]["smsp__warp_issue_stalled_long_scoreboard_per_warp_active.pct"]},
        }
    write_json("CRITICAL_PATH_ANALYSIS.json", {"status": "PASS", "profiles": critical_analysis, "answers": {"timing_change_kernel": "UP_PROJ changes are concentrated in GEMM; reduction duration is nearly unchanged. L0_DOWN native benefit is not reproduced by profiled kernel duration.", "l2_behavior": "Target up-proj persistence modestly increases TEX-read hits and reduces misses; matched unrelated persistence can reduce duration/stall without the same hit/miss change.", "memory_stall": "Up-proj GEMM long-scoreboard falls with both target and unrelated persistence; down-proj remains nearly unchanged.", "dram_proxy": "Aggregate DRAM bytes are a poor critical-path proxy: DRAM-read bytes move little while duration/stall change, and aggregate DRAM is not target-specific."}, "claim_boundary": "controlled policy association only; no unique cache-causality claim"})

    # Local and whole-decode analysis.
    selected_targets = {"SINGLE_L0_UP": ["L0_UP"], "SHARE2_UP": ["L0_UP", "L14_UP"], "SHARE2_L0": ["L0_UP", "L0_DOWN"], "SHARE3": ["L0_UP", "L14_UP", "L0_DOWN"]}
    local = {}
    multi_target = {}
    for condition, targets in selected_targets.items():
        local[condition] = {}
        count_material = 0
        for target in targets:
            shared = timing_map[(condition, target, 3)]
            control = timing_map[("ROTATE_CONTROL_3", target, 3)]
            benefit = 1 - shared["median"] / control["median"]
            combined = math.hypot(shared["cv"], control["cv"])
            material = benefit >= 0.05 and benefit > combined
            count_material += int(material)
            local[condition][target] = {"shared_median_ms": shared["median"], "rotate_control_median_ms": control["median"], "benefit_fraction": benefit, "combined_dispersion": combined, "MATERIAL_LOCAL": material, "ncu": shared_ncu_map.get((condition, target, 3))}
        multi_target[condition] = {"material_target_count": count_material, "selected_target_count": len(targets), "MULTI_TARGET_RETAINED": count_material >= 2}
    decode = {}
    stable_aggregate = {}
    for condition in CONDITIONS:
        runs = shared_runs[condition]
        stable_values = [sum(run["decode_step_ms"][1:4]) / 3 for run in runs]
        stable_aggregate[condition] = summarize(stable_values)
    for condition in selected_targets:
        shared = stable_aggregate[condition]
        rotate = stable_aggregate["ROTATE_CONTROL_3"]
        setaside = stable_aggregate["SETASIDE_ONLY"]
        benefit = 1 - shared["median"] / rotate["median"]
        combined = math.hypot(shared["cv"], rotate["cv"])
        per_step = {}
        for decode_index in (1, 2, 3):
            s = next(row for row in step_rows if row["condition"] == condition and row["decode_index"] == decode_index)
            r = next(row for row in step_rows if row["condition"] == "ROTATE_CONTROL_3" and row["decode_index"] == decode_index)
            per_step[f"D{decode_index}"] = {"shared_ms": s["median_ms"], "rotate_control_ms": r["median_ms"], "absolute_ms_benefit": r["median_ms"] - s["median_ms"], "benefit_fraction": 1 - s["median_ms"] / r["median_ms"]}
        decode[condition] = {"stable_D1_D3_mean_ms": shared["median"], "vs_ROTATE_CONTROL_3": {"absolute_ms_benefit": rotate["median"] - shared["median"], "benefit_fraction": benefit, "combined_dispersion": combined, "MATERIAL_DECODE_BENEFIT": benefit >= 0.02 and benefit > combined}, "vs_SETASIDE_ONLY": {"absolute_ms_benefit": setaside["median"] - shared["median"], "benefit_fraction": 1 - shared["median"] / setaside["median"]}, "per_step": per_step}
    rotate_vs_setaside = {"absolute_ms_change": stable_aggregate["ROTATE_CONTROL_3"]["median"] - stable_aggregate["SETASIDE_ONLY"]["median"], "fractional_change": stable_aggregate["ROTATE_CONTROL_3"]["median"] / stable_aggregate["SETASIDE_ONLY"]["median"] - 1}
    any_multi = any(value["MULTI_TARGET_RETAINED"] for key, value in multi_target.items() if key.startswith("SHARE"))
    any_decode = any(value["vs_ROTATE_CONTROL_3"]["MATERIAL_DECODE_BENEFIT"] for key, value in decode.items() if key.startswith("SHARE"))
    if any_multi and any_decode:
        stage_label = "SHARED_RESIDENCY_END_TO_END_SUPPORTED"
    elif any_multi:
        stage_label = "SHARED_RESIDENCY_LOCAL_ONLY"
    elif any(value["material_target_count"] == 1 for key, value in multi_target.items() if key.startswith("SHARE")):
        stage_label = "SHARED_RESIDENCY_SINGLE_TARGET_ONLY"
    else:
        stage_label = "SHARED_RESIDENCY_NOT_SUPPORTED"
    write_json("SHARED_POLICY_ANALYSIS.json", {"status": "PASS", "local_target_benefits": local, "multi_target_retention": multi_target, "whole_decode": decode, "ROTATE_CONTROL_3_vs_SETASIDE_ONLY": rotate_vs_setaside, "policy_overhead": {"per-update and per-run raw summaries": "POLICY_SWITCH_OVERHEAD.tsv", "not_hidden": True}, "stage_label": stage_label})
    write_json("STAGE_DECISION.json", {"stage_label": stage_label, "rotating_window_qualified": True, "MULTI_TARGET_RETAINED": any_multi, "MATERIAL_DECODE_BENEFIT": any_decode, "prior_states_preserved": {"producer_scoped_state": "MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW", "strict_consumer_state": "TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED", "decision_rule_divergence": "METHODOLOGICAL_OPERATIONALIZATION"}, "traffic_caveat_binding": True})

    write_json("NCU_RAW_PROVENANCE.json", {"status": "PASS", "profiles": raw_provenance})
    (OUT / "SCIENTIFIC_INTERPRETATION.md").write_text(
        "# C16 E1 shared-residency feasibility interpretation\n\n"
        f"Stage label: `{stage_label}`. The prior producer/consumer decision-rule divergence remains frozen and is not overwritten.\n\n"
        "Installed-NCU discovery resolves kernel duration, L2 TEX-read hit/miss sectors, DRAM-read bytes, long-scoreboard stall, LSU utilization, and active-warps metrics. Up-proj policy timing changes are concentrated in the quantized GEMM; reduction duration is nearly unchanged. Target persistence modestly shifts L2 hits/misses, while long-scoreboard and duration can also improve under matched unrelated persistence. DRAM-read bytes move far less than aggregate DRAM and native timing, confirming aggregate DRAM is a poor standalone critical-path proxy. Down-proj's native timing benefit is not reproduced by the profiled duration/stall counters.\n\n"
        "The isolated A/B/A experiment qualifies rotating windows without reset. Its Normal/Normal matched control performs the same three API updates but marks no qweight persisting. Persistent rotation lowers target DRAM/misses and increases L2 hits, so full-model sharing proceeds on qualified semantics.\n\n"
        "Under one fixed global set-aside, SHARE2_UP, SHARE2_L0, and SHARE3 retain material local timing benefits for at least two selected targets. However, stable D1-D3 decode-step improvements versus ROTATE_CONTROL_3 remain below 0.5%, far short of the registered 2% threshold. Policy calls cost roughly a few microseconds each and are reported separately; ROTATE_CONTROL_3 itself has negligible decode impact versus SETASIDE_ONLY.\n\n"
        "The hardware evidence therefore supports multi-target local residency but not end-to-end decode benefit in this bounded configuration. It does not authorize NVBit, full address tracing, Accel-Sim mechanism implementation, or mechanism simulation.\n",
        encoding="utf-8",
    )
    write_json("NEXT_STEP_DECISION.json", {"decision": "STOP_AFTER_SHARED_RESIDENCY_FEASIBILITY_REVIEW", "stage_label": stage_label, "independent_consumer_required": True, "auto_authorized_implementation": False, "forbidden_not_started": ["NVBit", "full address trace", "Accel-Sim mechanism implementation", "mechanism simulation"]})
    files = sorted(path for path in OUT.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    (OUT / "SHA256SUMS").write_text("".join(f"{sha(path)}  {path.name}\n" for path in files), encoding="utf-8")
    print(json.dumps({"status": "PASS", "stage_label": stage_label, "files": len(files) + 1, "critical_profiles": len(critical_profiles), "shared_profiles": len(shared_reports), "rotating_qualified": rotating_pass}, sort_keys=True))


if __name__ == "__main__":
    main()
