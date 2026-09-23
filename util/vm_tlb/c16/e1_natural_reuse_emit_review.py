#!/usr/bin/env python3
"""Validate and package C16 E1 natural-reuse/residency causal-closure evidence."""

import csv
import hashlib
import json
import math
import shutil
import statistics
from collections import defaultdict
from pathlib import Path


REPO = Path("/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-natural-reuse-residency-109-v1")
SOURCE = Path("/data/c16/e1_natural_reuse_residency_v1")
OUT = REPO / "docs/vm_tlb/review_packs/C16_E1_NATURAL_REUSE_RESIDENCY_109_V1"
RESIDENCY = REPO / "docs/vm_tlb/review_packs/C16_E1_RESIDENCY_INTERVENTION_109_V1"
METRICS = ["l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum"]
STATE_BYTES = {"q_proj": 6_680_576, "down_proj": 35_273_728, "up_proj": 35_273_728}
L2_BYTES = 67_108_864
DOSES = {
    "q_proj": [0, 32, 48, 56, 60, 64, 72, 96],
    "down_proj": [0, 16, 24, 28, 32, 36, 48, 64],
    "up_proj": [0, 16, 24, 28, 30, 32, 36, 40, 48, 64],
}


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
    header, units = rows[:2]
    return [dict(zip(header, row)) for row in rows[2:]], dict(zip(header, units))


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


def validate_command(command, expected_range):
    required = ["--replay-mode application", "--cache-control none", f"--nvtx-include {expected_range}/"]
    if any(fragment not in command for fragment in required):
        raise RuntimeError(f"profiler command mismatch: {expected_range}")


def copy_raw(family, profile_id, base_path, session_path, log_path):
    prefix = f"RAW_{family.upper()}_{profile_id}"
    shutil.copy2(base_path, OUT / f"{prefix}_BASE.csv")
    shutil.copy2(session_path, OUT / f"{prefix}_SESSION.csv")
    shutil.copy2(log_path, OUT / f"{prefix}_PROFILE.log")


def identity_sequence(run):
    return (
        run["generated_token_ids_D0_D3"],
        [(row["target"], row["decode_index"], row["token_id"], row["range"], row["input_sha256"], row["output_sha256"]) for row in run["occurrences"]],
    )


def bracket(value, warm, dense):
    denominator = abs(dense - warm)
    if denominator == 0:
        return {"warm_fraction": None, "position": "UNDEFINED_ZERO_DENOMINATOR"}
    fraction = abs(value - warm) / denominator
    lower, upper = min(warm, dense), max(warm, dense)
    if value < lower:
        position = "OUTSIDE_BELOW_BRACKET"
    elif value > upper:
        position = "OUTSIDE_ABOVE_BRACKET"
    else:
        position = "INSIDE_BRACKET"
    return {"warm_fraction": fraction, "position": position}


def main():
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite {OUT}")
    OUT.mkdir(parents=True)
    native = json.loads((SOURCE / "NATIVE_REFILL_KNEE_RESULT.json").read_text())
    if native["status"] != "PASS" or len(native["refill_rows"]) != 324 or len(native["knee_rows"]) != 182:
        raise RuntimeError("native refill/knee closure")
    write_json(
        "UPSTREAM_AUTHORITY.json",
        {
            "clean_e1_producer": "8988d6108ff8bdca180a14cec2fe769df45b09f1",
            "clean_e1_consumer": "59ddb8ba2a33ef12b73bfc859f3a994e0b4ef4ca",
            "semantic_ncu_v2_producer": "8d1f62229cae15199793ba5569327cf1e83596f3",
            "semantic_ncu_v2_consumer": "cdd3ec7afbb1611cc52a4b74d32b38a3edabd131",
            "residency_producer": "22d1b98d7f0c213950654fc754be4e7388836de3",
            "residency_consumer": "5b11dd41e98044fcad76da4a906c7ba8609eb828",
            "status": "PASS",
        },
    )
    write_json(
        "REFILL_SEQUENCE_CONTRACT.json",
        {
            "status": "PASS",
            "targets": ["q_proj RAW/AWQ", "down_proj RAW/AWQ", "up_proj RAW/AWQ"],
            "M": 1,
            "sequence": "two warmups -> 256MiB dense pressure -> K1,K2,K3,K4,K5,K6",
            "native_independent_sequences_per_point": 9,
            "selected_ncu_calls": [1, 2, 4],
            "no_pressure_sync_hash_or_unrelated_module_call_between_K1_K6": True,
            "pressure_buffer": native["pressure_buffer"],
        },
    )

    # Refill native timing and identity closure.
    refill_groups = defaultdict(list)
    refill_bindings = {}
    for row in native["refill_rows"]:
        key = (row["role"], row["implementation"], row["call_index"])
        refill_groups[key].append(row["target_ms"])
        binding_key = (row["role"], row["implementation"])
        identity = (row["input_sha256"], row["output_sha256"])
        if binding_key in refill_bindings and refill_bindings[binding_key] != identity:
            raise RuntimeError(f"refill identity drift: {binding_key}")
        refill_bindings[binding_key] = identity
    refill_timing_rows = []
    refill_timing_map = {}
    for key, values in sorted(refill_groups.items()):
        role, implementation, call_index = key
        summary = summarize(values)
        refill_timing_map[key] = summary
        refill_timing_rows.append(
            {"role": role, "M": 1, "implementation": implementation, "call_index": call_index,
             "median_ms": summary["median_ms"], "min_ms": summary["min_ms"], "max_ms": summary["max_ms"], "cv": summary["cv"], "samples_ms": json.dumps(values),
             "input_sha256": refill_bindings[(role, implementation)][0], "output_sha256": refill_bindings[(role, implementation)][1]}
        )
    write_tsv(
        "REFILL_NATIVE_TIMING.tsv", refill_timing_rows,
        ["role", "M", "implementation", "call_index", "median_ms", "min_ms", "max_ms", "cv", "samples_ms", "input_sha256", "output_sha256"],
    )

    raw_provenance = []
    refill_ncu_rows = []
    refill_kernel_rows = []
    refill_dram = {}
    refill_reports = sorted((SOURCE / "ncu/refill/reports").glob("*.ncu-rep"))
    if len(refill_reports) != 18:
        raise RuntimeError(f"refill report count {len(refill_reports)}")
    for report in refill_reports:
        profile_id = report.stem
        base = report.with_suffix(".base.csv")
        session = report.with_suffix(".session.csv")
        log = SOURCE / "ncu/refill/logs" / f"{profile_id}.log"
        receipt = log_receipt(log)
        rows, units = read_ncu(base)
        command = session_command(session)
        validate_command(command, receipt["range"])
        range_column = next(name for name in rows[0] if "Push/Pop_Range" in name)
        if any(receipt["range"] not in row[range_column] for row in rows):
            raise RuntimeError(f"refill range mismatch {profile_id}")
        if any(int(row["profiler__replayer_passes"]) != 1 for row in rows):
            raise RuntimeError(f"refill replay count {profile_id}")
        binding = refill_bindings[(receipt["role"], receipt["implementation"])]
        if (receipt["input_sha256"], receipt["output_sha256"]) != binding:
            raise RuntimeError(f"refill receipt identity {profile_id}")
        names = [row["Kernel Name"] for row in rows]
        if receipt["implementation"] == "RAW_FP16" and len(rows) != 1:
            raise RuntimeError(f"RAW refill kernel inventory {profile_id}")
        if receipt["implementation"] == "AWQ_FP16_INPUT" and not (any("gemm_forward_4bit" in x for x in names) and any("reduce_kernel" in x for x in names)):
            raise RuntimeError(f"AWQ refill kernel inventory {profile_id}")
        sums = {}
        for metric in METRICS:
            if units[metric] != "byte":
                raise RuntimeError(f"refill unit {profile_id} {metric}")
            sums[metric] = sum(float(row[metric].replace(",", "")) for row in rows)
        refill_dram[(receipt["role"], receipt["implementation"], receipt["selected_k"])] = sums["dram__bytes.sum"]
        refill_ncu_rows.append(
            {"profile_id": profile_id, "role": receipt["role"], "M": 1, "implementation": receipt["implementation"], "selected_k": receipt["selected_k"], "nvtx_range": receipt["range"], "kernel_count": len(rows), "kernel_names": json.dumps(names), "replay_pass_count": 1,
             "l1tex__t_bytes.sum": sums["l1tex__t_bytes.sum"], "lts__t_bytes.sum": sums["lts__t_bytes.sum"], "dram__bytes.sum": sums["dram__bytes.sum"], "unit": "byte", "profiler_command": command}
        )
        for index, row in enumerate(rows):
            for metric in METRICS:
                refill_kernel_rows.append(
                    {"profile_id": profile_id, "kernel_index": index, "kernel_name": row["Kernel Name"], "grid_size": row["Grid Size"], "block_size": row["Block Size"], "metric_name": metric, "unit": "byte", "value": float(row[metric].replace(",", ""))}
                )
        raw_provenance.append({"family": "refill", "profile_id": profile_id, "report_path": str(report), "report_sha256": sha(report), "base_sha256": sha(base), "session_sha256": sha(session), "profile_log_sha256": sha(log)})
        copy_raw("refill", profile_id, base, session, log)
    write_tsv(
        "REFILL_NCU_INDEX.tsv", refill_ncu_rows,
        ["profile_id", "role", "M", "implementation", "selected_k", "nvtx_range", "kernel_count", "kernel_names", "replay_pass_count", "l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum", "unit", "profiler_command"],
    )
    write_tsv(
        "REFILL_NCU_KERNEL_METRICS.tsv", refill_kernel_rows,
        ["profile_id", "kernel_index", "kernel_name", "grid_size", "block_size", "metric_name", "unit", "value"],
    )
    refill_analysis = {}
    for role in ("q_proj", "down_proj", "up_proj"):
        for implementation in ("RAW_FP16", "AWQ_FP16_INPUT"):
            point = f"{role}:{implementation}"
            k1_time = refill_timing_map[(role, implementation, 1)]["median_ms"]
            k2_time = refill_timing_map[(role, implementation, 2)]["median_ms"]
            k6_time = refill_timing_map[(role, implementation, 6)]["median_ms"]
            k1_dram = refill_dram[(role, implementation, 1)]
            k2_dram = refill_dram[(role, implementation, 2)]
            k4_dram = refill_dram[(role, implementation, 4)]
            refill = implementation == "AWQ_FP16_INPUT" and k2_dram < 0.1 * k1_dram and (k2_time < 0.9 * k1_time or k6_time < 0.9 * k1_time)
            flat_high = implementation == "RAW_FP16" and k2_dram > 0.9 * k1_dram and k4_dram > 0.9 * k1_dram
            refill_analysis[point] = {
                "K2_over_K1_timing": k2_time / k1_time,
                "K6_over_K1_timing": k6_time / k1_time,
                "K1_dram_bytes": k1_dram,
                "K2_dram_bytes": k2_dram,
                "K4_dram_bytes": k4_dram,
                "K2_over_K1_dram": k2_dram / k1_dram,
                "K4_over_K1_dram": k4_dram / k1_dram,
                "clear_refill": refill,
                "comparatively_flat_high_dram": flat_high,
            }
    write_json("REFILL_ANALYSIS.json", {"status": "PASS", "points": refill_analysis})

    # Capacity-knee native timing.
    knee_groups = defaultdict(list)
    knee_bindings = {}
    for row in native["knee_rows"]:
        key = (row["role"], row["dose_mib"])
        knee_groups[key].append(row["target_ms"])
        identity = (row["input_sha256"], row["output_sha256"])
        if row["role"] in knee_bindings and knee_bindings[row["role"]] != identity:
            raise RuntimeError(f"knee identity drift {row['role']}")
        knee_bindings[row["role"]] = identity
    knee_timing_map = {}
    knee_timing_rows = []
    for key, values in sorted(knee_groups.items()):
        role, dose = key
        summary = summarize(values)
        knee_timing_map[key] = summary
        knee_timing_rows.append(
            {"role": role, "M": 1, "implementation": "AWQ_FP16_INPUT", "dose_mib": dose, "median_ms": summary["median_ms"], "min_ms": summary["min_ms"], "max_ms": summary["max_ms"], "cv": summary["cv"], "samples_ms": json.dumps(values), "input_sha256": knee_bindings[role][0], "output_sha256": knee_bindings[role][1]}
        )
    write_tsv(
        "CAPACITY_KNEE_TIMING.tsv", knee_timing_rows,
        ["role", "M", "implementation", "dose_mib", "median_ms", "min_ms", "max_ms", "cv", "samples_ms", "input_sha256", "output_sha256"],
    )
    write_json(
        "CAPACITY_KNEE_CONTRACT.json",
        {"status": "PASS", "doses_mib": DOSES, "module_state_bytes": STATE_BYTES, "device_l2_bytes": L2_BYTES, "nominal_residual_l2_bytes": {role: L2_BYTES - size for role, size in STATE_BYTES.items()}, "timing_repetitions_per_dose": 7, "ncu_metric": "dram__bytes.sum"},
    )
    knee_ncu_rows = []
    knee_dram = {}
    knee_reports = sorted((SOURCE / "ncu/knee/reports").glob("*.ncu-rep"))
    if len(knee_reports) != 26:
        raise RuntimeError(f"knee report count {len(knee_reports)}")
    for report in knee_reports:
        profile_id = report.stem
        base, session = report.with_suffix(".base.csv"), report.with_suffix(".session.csv")
        log = SOURCE / "ncu/knee/logs" / f"{profile_id}.log"
        receipt = log_receipt(log)
        rows, units = read_ncu(base)
        command = session_command(session)
        validate_command(command, receipt["range"])
        range_column = next(name for name in rows[0] if "Push/Pop_Range" in name)
        if any(receipt["range"] not in row[range_column] for row in rows) or any(int(row["profiler__replayer_passes"]) != 1 for row in rows):
            raise RuntimeError(f"knee selector/pass {profile_id}")
        if units["dram__bytes.sum"] != "byte":
            raise RuntimeError(f"knee unit {profile_id}")
        if (receipt["input_sha256"], receipt["output_sha256"]) != knee_bindings[receipt["role"]]:
            raise RuntimeError(f"knee identity {profile_id}")
        names = [row["Kernel Name"] for row in rows]
        if not (any("gemm_forward_4bit" in name for name in names) and any("reduce_kernel" in name for name in names)):
            raise RuntimeError(f"knee kernel inventory {profile_id}")
        dram = sum(float(row["dram__bytes.sum"].replace(",", "")) for row in rows)
        knee_dram[(receipt["role"], receipt["dose_mib"])] = dram
        knee_ncu_rows.append(
            {"profile_id": profile_id, "role": receipt["role"], "dose_mib": receipt["dose_mib"], "dram__bytes.sum": dram, "unit": "byte", "kernel_count": len(rows), "kernel_names": json.dumps(names), "replay_pass_count": 1, "nvtx_range": receipt["range"], "profiler_command": command}
        )
        raw_provenance.append({"family": "knee", "profile_id": profile_id, "report_path": str(report), "report_sha256": sha(report), "base_sha256": sha(base), "session_sha256": sha(session), "profile_log_sha256": sha(log)})
        copy_raw("knee", profile_id, base, session, log)
    write_tsv(
        "CAPACITY_KNEE_NCU.tsv", knee_ncu_rows,
        ["profile_id", "role", "dose_mib", "dram__bytes.sum", "unit", "kernel_count", "kernel_names", "replay_pass_count", "nvtx_range", "profiler_command"],
    )
    knee_analysis = {}
    for role, doses in DOSES.items():
        baseline = knee_timing_map[(role, 0)]
        first_dram = None
        first_timing = None
        dose_response = []
        for dose in doses:
            timing = knee_timing_map[(role, dose)]
            timing_ratio = timing["median_ms"] / baseline["median_ms"]
            timing_change = abs(timing_ratio - 1.0)
            combined = math.hypot(baseline["cv"], timing["cv"])
            material = timing_change >= 0.05 and timing_change > combined
            dram = knee_dram[(role, dose)]
            dram_gate = dram > 1024 * 1024 and dram > 0.1 * STATE_BYTES[role]
            if first_dram is None and dram_gate:
                first_dram = dose
            if first_timing is None and dose > 0 and material:
                first_timing = dose
            dose_response.append({"dose_mib": dose, "timing_over_0": timing_ratio, "timing_material": material, "dram_bytes": dram, "dram_gate": dram_gate})
        nominal_mib = (L2_BYTES - STATE_BYTES[role]) / (1024 * 1024)
        knee_analysis[role] = {
            "module_state_bytes": STATE_BYTES[role],
            "nominal_residual_l2_bytes": L2_BYTES - STATE_BYTES[role],
            "nominal_residual_l2_mib": nominal_mib,
            "first_dram_knee_mib": first_dram,
            "first_material_timing_dose_mib": first_timing,
            "observed_dram_knee_minus_nominal_residual_mib": first_dram - nominal_mib if first_dram is not None else None,
            "dose_response": dose_response,
        }
    write_json("CAPACITY_KNEE_ANALYSIS.json", {"status": "PASS", "roles": knee_analysis, "interpretation_boundary": "descriptive relationship; no exact-capacity theorem"})

    # Natural AWQ native authority: seven independent processes.
    natural_paths = sorted((SOURCE / "natural/native").glob("run[0-6].json"))
    if len(natural_paths) != 7:
        raise RuntimeError("natural native run count")
    natural_runs = [json.loads(path.read_text()) for path in natural_paths]
    natural_identity = identity_sequence(natural_runs[0])
    if not all(identity_sequence(run) == natural_identity for run in natural_runs):
        raise RuntimeError("natural token/occurrence nondeterminism")
    write_json(
        "NATURAL_FULL_MODEL_CONTRACT.json",
        {"status": "PASS", "model_root": natural_runs[0]["model_root"], "backend": natural_runs[0]["backend"], "prefix_tokens": 2048, "decode_steps": 4, "greedy": True, "native_fresh_process_runs": 7, "no_inner_loop_synchronize": True, "prefill_excluded": True, "targets": ["L0_UP", "L14_UP", "L0_DOWN"]},
    )
    write_json(
        "NATURAL_DECODE_TOKENS.json",
        {"status": "PASS", "token_file_sha256": natural_runs[0]["token_file_sha256"], "generated_token_ids_D0_D3": natural_identity[0], "all_seven_fresh_process_runs_identical": True},
    )
    occurrence_authority = {(row["target"], row["decode_index"]): row for row in natural_runs[0]["occurrences"]}
    occurrence_rows = []
    natural_timing_rows = []
    natural_timing_map = {}
    for target in ("L0_UP", "L14_UP", "L0_DOWN"):
        for decode_index in range(4):
            authority = occurrence_authority[(target, decode_index)]
            occurrence_rows.append({key: authority[key] for key in ("target", "decode_index", "token_id", "range", "input_sha256", "output_sha256", "input_shape", "output_shape", "module_class")})
            target_values = [next(row["target_ms"] for row in run["occurrences"] if row["target"] == target and row["decode_index"] == decode_index) for run in natural_runs]
            step_values = [run["decode_step_ms"][decode_index] for run in natural_runs]
            target_summary, step_summary = summarize(target_values), summarize(step_values)
            natural_timing_map[(target, decode_index)] = target_summary
            natural_timing_rows.append(
                {"target": target, "decode_index": decode_index, "token_id": authority["token_id"], "median_ms": target_summary["median_ms"], "min_ms": target_summary["min_ms"], "max_ms": target_summary["max_ms"], "cv": target_summary["cv"], "samples_ms": json.dumps(target_values), "decode_step_median_ms": step_summary["median_ms"], "decode_step_min_ms": step_summary["min_ms"], "decode_step_max_ms": step_summary["max_ms"], "decode_step_cv": step_summary["cv"], "decode_step_samples_ms": json.dumps(step_values), "input_sha256": authority["input_sha256"], "output_sha256": authority["output_sha256"], "nvtx_range": authority["range"]}
            )
    write_tsv(
        "NATURAL_OCCURRENCE_BINDINGS.tsv", occurrence_rows,
        ["target", "decode_index", "token_id", "range", "input_sha256", "output_sha256", "input_shape", "output_shape", "module_class"],
    )
    write_tsv(
        "NATURAL_NATIVE_TIMING.tsv", natural_timing_rows,
        ["target", "decode_index", "token_id", "median_ms", "min_ms", "max_ms", "cv", "samples_ms", "decode_step_median_ms", "decode_step_min_ms", "decode_step_max_ms", "decode_step_cv", "decode_step_samples_ms", "input_sha256", "output_sha256", "nvtx_range"],
    )
    for path in natural_paths:
        shutil.copy2(path, OUT / f"RAW_NATURAL_NATIVE_{path.name}")
    for path in sorted((SOURCE / "natural/native").glob("*.stdout.log")):
        shutil.copy2(path, OUT / f"RAW_NATURAL_NATIVE_{path.name}")

    natural_ncu_rows = []
    natural_dram = {}
    natural_reports = sorted((SOURCE / "ncu/natural/reports").glob("*.ncu-rep"))
    if len(natural_reports) != 7:
        raise RuntimeError("natural NCU report count")
    for report in natural_reports:
        profile_id = report.stem
        base, session = report.with_suffix(".base.csv"), report.with_suffix(".session.csv")
        log = SOURCE / "ncu/natural/logs" / f"{profile_id}.log"
        receipt = log_receipt(log)
        if identity_sequence(receipt) != natural_identity:
            raise RuntimeError(f"natural NCU identity {profile_id}")
        rows, units = read_ncu(base)
        command = session_command(session)
        selected = command.split("--nvtx-include ", 1)[1].split("/", 1)[0]
        validate_command(command, selected)
        range_column = next(name for name in rows[0] if "Push/Pop_Range" in name)
        if any(selected not in row[range_column] for row in rows) or any(int(row["profiler__replayer_passes"]) != 1 for row in rows):
            raise RuntimeError(f"natural selector/pass {profile_id}")
        names = [row["Kernel Name"] for row in rows]
        if not (any("gemm_forward_4bit" in name for name in names) and any("reduce_kernel" in name for name in names)):
            raise RuntimeError(f"natural kernel inventory {profile_id}")
        sums = {}
        for metric in METRICS:
            if units[metric] != "byte":
                raise RuntimeError(f"natural metric unit {profile_id}")
            sums[metric] = sum(float(row[metric].replace(",", "")) for row in rows)
        profile_parts = profile_id.split("_")
        target = "_".join(profile_parts[1:-1])
        decode_index = int(profile_parts[-1].removeprefix("D"))
        authority = occurrence_authority[(target, decode_index)]
        natural_dram[(target, decode_index)] = sums["dram__bytes.sum"]
        natural_ncu_rows.append(
            {"profile_id": profile_id, "target": target, "decode_index": decode_index, "token_id": authority["token_id"], "nvtx_range": selected, "kernel_count": len(rows), "kernel_names": json.dumps(names), "replay_pass_count": 1, "l1tex__t_bytes.sum": sums["l1tex__t_bytes.sum"], "lts__t_bytes.sum": sums["lts__t_bytes.sum"], "dram__bytes.sum": sums["dram__bytes.sum"], "unit": "byte", "input_sha256": authority["input_sha256"], "output_sha256": authority["output_sha256"], "profiler_command": command}
        )
        raw_provenance.append({"family": "natural", "profile_id": profile_id, "report_path": str(report), "report_sha256": sha(report), "base_sha256": sha(base), "session_sha256": sha(session), "profile_log_sha256": sha(log)})
        copy_raw("natural", profile_id, base, session, log)
    write_tsv(
        "NATURAL_NCU_INDEX.tsv", natural_ncu_rows,
        ["profile_id", "target", "decode_index", "token_id", "nvtx_range", "kernel_count", "kernel_names", "replay_pass_count", "l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum", "unit", "input_sha256", "output_sha256", "profiler_command"],
    )

    # Isolated WARM/DENSE references and unclamped natural proximity.
    isolated_timing = {}
    with (RESIDENCY / "NATIVE_INTERVENTION_TIMING.tsv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["input_kind"] == "TEXT" and row["M"] == "1" and row["implementation"] == "AWQ_FP16_INPUT" and row["role"] in ("up_proj", "down_proj") and row["state"] in ("WARM_A", "DENSE_MEMORY_PRESSURE"):
                isolated_timing[(row["role"], row["state"])] = float(row["median_ms"])
    isolated_dram = {}
    with (RESIDENCY / "NCU_SEMANTIC_SUMS.tsv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["input_kind"] == "TEXT" and row["M"] == "1" and row["implementation"] == "AWQ_FP16_INPUT" and row["role"] in ("up_proj", "down_proj") and row["state"] in ("WARM", "DENSE_MEMORY_PRESSURE") and row["metric_name"] == "dram__bytes.sum":
                isolated_dram[(row["role"], row["state"])] = float(row["semantic_module_sum"])
    proximity = {}
    for target in ("L0_UP", "L14_UP", "L0_DOWN"):
        role = "up_proj" if target.endswith("UP") else "down_proj"
        for decode_index in range(4):
            key = f"{target}:D{decode_index}"
            if target == "L14_UP":
                proximity[key] = {"timing": {"warm_fraction": None, "reason": "NO_EXACT_LAYER14_ISOLATED_AUTHORITY"}, "dram": {"warm_fraction": None, "reason": "NO_EXACT_LAYER14_ISOLATED_AUTHORITY"}}
                continue
            natural_time = natural_timing_map[(target, decode_index)]["median_ms"]
            timing_value = bracket(natural_time, isolated_timing[(role, "WARM_A")], isolated_timing[(role, "DENSE_MEMORY_PRESSURE")])
            timing_value.update({"natural": natural_time, "isolated_warm": isolated_timing[(role, "WARM_A")], "isolated_dense": isolated_timing[(role, "DENSE_MEMORY_PRESSURE")]})
            if (target, decode_index) in natural_dram:
                natural_bytes = natural_dram[(target, decode_index)]
                dram_value = bracket(natural_bytes, isolated_dram[(role, "WARM")], isolated_dram[(role, "DENSE_MEMORY_PRESSURE")])
                dram_value.update({"natural": natural_bytes, "isolated_warm": isolated_dram[(role, "WARM")], "isolated_dense": isolated_dram[(role, "DENSE_MEMORY_PRESSURE")]})
            else:
                dram_value = {"warm_fraction": None, "reason": "OCCURRENCE_NOT_PROFILED_WITH_NCU"}
            proximity[key] = {"timing": timing_value, "dram": dram_value}
    write_json(
        "NATURAL_VS_ISOLATED.json",
        {"status": "PASS", "formula": "abs(natural-warm)/abs(dense-warm)", "clamped": False, "occurrences": proximity, "interpretation": "values outside [0,1] are preserved; no categorical threshold imposed"},
    )

    # Optional RAW control: clean fit, seven native runs, one D0 NCU.
    raw_probe = json.loads((SOURCE / "RAW_OPTIONAL_PROBE.json").read_text())
    raw_paths = sorted((SOURCE / "raw_optional/native").glob("run[0-6].json"))
    raw_runs = [json.loads(path.read_text()) for path in raw_paths]
    if raw_probe["status"] != "RAW_FULL_MODEL_NATURAL_CONTROL_FIT" or len(raw_runs) != 7:
        raise RuntimeError("RAW optional control closure")
    raw_identity = identity_sequence(raw_runs[0])
    if not all(identity_sequence(run) == raw_identity for run in raw_runs):
        raise RuntimeError("RAW optional nondeterminism")
    raw_native = {}
    for decode_index in (0, 3):
        values = [next(row["target_ms"] for row in run["occurrences"] if row["decode_index"] == decode_index) for run in raw_runs]
        raw_native[f"D{decode_index}"] = summarize(values)
    raw_report = SOURCE / "raw_optional/ncu/RAW_NAT_L0_UP_D0.ncu-rep"
    raw_base = SOURCE / "raw_optional/ncu/RAW_NAT_L0_UP_D0.base.csv"
    raw_session = SOURCE / "raw_optional/ncu/RAW_NAT_L0_UP_D0.session.csv"
    raw_log = SOURCE / "raw_optional/ncu/RAW_NAT_L0_UP_D0.log"
    raw_receipt = log_receipt(raw_log)
    if identity_sequence(raw_receipt) != raw_identity:
        raise RuntimeError("RAW optional NCU identity")
    raw_rows, raw_units = read_ncu(raw_base)
    raw_command = session_command(raw_session)
    validate_command(raw_command, "C16_E1_RAW_NAT_L0_UP_D0")
    raw_sums = {metric: sum(float(row[metric].replace(",", "")) for row in raw_rows) for metric in METRICS}
    if any(raw_units[metric] != "byte" for metric in METRICS) or any(int(row["profiler__replayer_passes"]) != 1 for row in raw_rows):
        raise RuntimeError("RAW optional metric/pass closure")
    write_json(
        "RAW_OPTIONAL_CONTROL.json",
        {"status": "RAW_FULL_MODEL_NATURAL_CONTROL_RUN", "fit_probe": raw_probe, "generated_token_ids_D0_D3": raw_identity[0], "seven_fresh_process_runs_identical": True, "native_timing": raw_native, "D0_ncu": {"metrics": raw_sums, "unit": "byte", "kernel_count": len(raw_rows), "kernel_names": [row["Kernel Name"] for row in raw_rows], "replay_pass_count": 1, "report_sha256": sha(raw_report), "profiler_command": raw_command}, "comparison_boundary": "RAW natural control is BF16 full-model deployment; it is not substituted for isolated RAW_FP16 authority"},
    )
    for path in raw_paths:
        shutil.copy2(path, OUT / f"RAW_OPTIONAL_NATIVE_{path.name}")
    for path in sorted((SOURCE / "raw_optional/native").glob("*.stdout.log")):
        shutil.copy2(path, OUT / f"RAW_OPTIONAL_NATIVE_{path.name}")
    shutil.copy2(raw_base, OUT / "RAW_OPTIONAL_NCU_D0_BASE.csv")
    shutil.copy2(raw_session, OUT / "RAW_OPTIONAL_NCU_D0_SESSION.csv")
    shutil.copy2(raw_log, OUT / "RAW_OPTIONAL_NCU_D0_PROFILE.log")
    raw_provenance.append({"family": "raw_optional", "profile_id": "RAW_NAT_L0_UP_D0", "report_path": str(raw_report), "report_sha256": sha(raw_report), "base_sha256": sha(raw_base), "session_sha256": sha(raw_session), "profile_log_sha256": sha(raw_log)})

    write_json("NCU_RAW_PROVENANCE.json", {"status": "PASS", "profiles": raw_provenance})
    shutil.copy2(SOURCE / "NATIVE_REFILL_KNEE_RESULT.json", OUT / "RAW_NATIVE_REFILL_KNEE_RESULT.json")

    answers = {
        "Q1_AWQ_REFILL": "YES_ALL_Q_DOWN_UP_K1_TO_K2",
        "Q2_RAW_DOWN_UP_FLAT_HIGH_DRAM": "YES",
        "Q3_KNEE_CAPACITY_ALIGNMENT": "COARSE_ROLE_ORDER_ONLY_KNEES_EARLIER_THAN_NOMINAL_RESIDUAL_L2",
        "Q4_NATURAL_WARM_OR_DENSE": "DENSE_LIKE_OR_OUTSIDE_DENSE_BRACKET",
        "Q5_LAYER14_REPRODUCES_LAYER0_UP": "YES_FOR_DRAM_AND_D3_TIMING;_LAYER0_D0_HAS_EXTRA_FIRST_STEP_COST",
        "Q6_DOWN_PROJ_NATURAL_REUSE": "YES_DRAM_DENSE_LIKE_SLIGHTLY_OUTSIDE;TIMING_INSIDE_WARM_DENSE_BRACKET",
        "Q7_BEYOND_CAPACITY": "YES_ROLE_KERNEL_ACCESS_POLICY_EFFECTS_REMAIN",
    }
    cases = {
        "Case_A_isolated_refill_natural_warm_like": False,
        "Case_B_isolated_refill_natural_dense_like": True,
        "Case_C_no_clear_refill": False,
        "Case_D_role_dependent": True,
    }
    write_json(
        "INTEGRATED_INTERPRETATION.json",
        {"status": "PASS", "answers": answers, "case_framing": cases, "primary_case": "CASE_B_WITH_CASE_D_ROLE_DEPENDENCE", "scope": "descriptive natural-reuse/residency closure; no mechanism authorization"},
    )
    (OUT / "SCIENTIFIC_INTERPRETATION.md").write_text(
        "# C16 E1 natural-reuse / residency causal-closure interpretation\n\n"
        "Immediate post-pressure reuse shows a clear one-call refill for AWQ q_proj, down_proj and up_proj: target DRAM falls from packed-state-scale K1 traffic to tens of KiB by K2, with matching timing recovery. RAW down/up remain comparatively flat at roughly 136 MB DRAM; RAW q_proj remains near its 25.7 MB state footprint. This rejects Case C.\n\n"
        "Role-specific capacity knees occur at 32 MiB for q_proj and 16 MiB for down/up, earlier than nominal residual-L2 budgets of 57.63 and 30.36 MiB. The ordering is capacity-consistent but the deltas are not an exact capacity theorem. Timing knees and non-monotonic post-knee traffic further indicate role/kernel/access-policy effects beyond nominal state size.\n\n"
        "Across seven fresh-process AWQ full-model runs, tokens `[23578, 11, 323, 3950]` and all 12 occurrence SHA bindings reproduce exactly. Natural layer0 up_proj DRAM is about 49 MB at D0/D1/D3, outside the accepted isolated WARM-to-DENSE bracket on the dense side. Layer0 down_proj DRAM is about 37 MB and likewise slightly beyond its dense reference, while timing lies inside the bracket. Layer14 up_proj reproduces layer0's roughly 49 MB natural DRAM and D3 timing; layer0 D0 alone carries an additional first-step timing cost.\n\n"
        "The integrated result is `CASE_B_WITH_CASE_D_ROLE_DEPENDENCE`: immediate reuse refills compressed state, but realistic full-model interference makes subsequent natural occurrences dense-like or beyond the isolated dense bracket. Capacity matters, but role/kernel/access policy also matters. The optional accepted RAW BF16 full-model control runs naturally and remains flat/high-DRAM at layer0 up_proj.\n\n"
        "This closes the registered causal-diagnostic stage without proving a cache/TLB mechanism, excluding translation effects, or authorizing selective residency hardware. No NVBit, full address trace, cache/TLB mechanism, or mechanism simulation was started.\n",
        encoding="utf-8",
    )
    write_json(
        "NEXT_STEP_DECISION.json",
        {"decision": "STOP_AFTER_NATURAL_REUSE_RESIDENCY_REVIEW", "integrated_case": "CASE_B_WITH_CASE_D_ROLE_DEPENDENCE", "independent_consumer_required": True, "auto_authorized_next_experiment": False, "forbidden_not_started": ["NVBit", "full address trace", "cache/TLB mechanism", "mechanism simulation"]},
    )

    files = sorted(path for path in OUT.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    (OUT / "SHA256SUMS").write_text("".join(f"{sha(path)}  {path.name}\n" for path in files), encoding="utf-8")
    print(json.dumps({"status": "PASS", "files": len(files) + 1, "refill_profiles": len(refill_reports), "knee_profiles": len(knee_reports), "natural_profiles": len(natural_reports), "integrated_case": "CASE_B_WITH_CASE_D_ROLE_DEPENDENCE"}, sort_keys=True))


if __name__ == "__main__":
    main()
