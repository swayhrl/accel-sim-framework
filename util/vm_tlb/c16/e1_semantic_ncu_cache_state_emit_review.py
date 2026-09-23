#!/usr/bin/env python3
"""Validate V1/V2 NCU contexts and emit the bounded cache-state repair pack."""

import csv
import hashlib
import json
import shutil
from pathlib import Path


REPO = Path("/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-semantic-ncu-cache-state-repair-109-v1")
SOURCE = Path("/data/c16/e1_semantic_ncu_cache_state_repair_v1")
REPORTS = SOURCE / "reports"
V1 = REPO / "docs/vm_tlb/review_packs/C16_E1_SEMANTIC_NCU_109_V1"
OUT = REPO / "docs/vm_tlb/review_packs/C16_E1_SEMANTIC_NCU_CACHE_STATE_REPAIR_109_V1"

POINTS = {
    "M1_RAW": {
        "M": 1,
        "implementation": "RAW_FP16",
        "replay_impl": "RAW_FP16",
        "range": "C16_E1_NCU_UP_M1_RAW_FP16",
        "input_sha256": "b3999f6fe161d47efdff4c7d88aa044e2cec3396f9c69fde63c53f2ba208f82e",
        "output_sha256": "50d389317ff126f2aa1e18dbf36bbf17bd66ddac2753552fc73517c1b7c3d394",
        "expected_kernel_count": 1,
    },
    "M1_AWQ": {
        "M": 1,
        "implementation": "AWQ_FP16_INPUT",
        "replay_impl": "AWQ",
        "range": "C16_E1_NCU_UP_M1_AWQ",
        "input_sha256": "b3999f6fe161d47efdff4c7d88aa044e2cec3396f9c69fde63c53f2ba208f82e",
        "output_sha256": "5618125fc9563f42860d5df37ae9b4b6569dfc4af1d995eeb7922d9f60b31d99",
        "expected_kernel_count": 2,
    },
    "M256_RAW": {
        "M": 256,
        "implementation": "RAW_FP16",
        "replay_impl": "RAW_FP16",
        "range": "C16_E1_NCU_UP_M256_RAW_FP16",
        "input_sha256": "eeae491edfdbee761de47aa6c4ea35b293bb2796227927778fa51c9e58ef1b41",
        "output_sha256": "01dbbf90e7d43b86ba49ce61805f11717b7ec9f28e67d7da0ff5f73065757413",
        "expected_kernel_count": 1,
    },
    "M256_AWQ": {
        "M": 256,
        "implementation": "AWQ_FP16_INPUT",
        "replay_impl": "AWQ",
        "range": "C16_E1_NCU_UP_M256_AWQ",
        "input_sha256": "eeae491edfdbee761de47aa6c4ea35b293bb2796227927778fa51c9e58ef1b41",
        "output_sha256": "59b56af85d0480542fa396a655f23179f879eccaa9ab32a7b98ba88e8cb33d50",
        "expected_kernel_count": 2,
    },
}

METRICS = ["l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum"]
TIMING = {
    "M1_AWQ_over_RAW": 0.4002389918887601,
    "M256_AWQ_over_RAW": 1.868764789921065,
    "shape_interaction_ratio": 4.6691222689279055,
}
SIMILAR_RELATIVE_TOLERANCE = 0.25


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name: str, value: object) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_ncu_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    if len(rows) < 3:
        raise RuntimeError(f"no data rows in {path}")
    header, units = rows[:2]
    return [dict(zip(header, row)) for row in rows[2:]], dict(zip(header, units))


def profiler_command(path: Path) -> str:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    for row in rows:
        if len(row) >= 2 and row[0] == "Profiler Command Line":
            return row[1]
    raise RuntimeError(f"missing profiler command in {path}")


def replay_receipt(path: Path) -> dict:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("{") and line.endswith("}"):
            value = json.loads(line)
            if value.get("status") == "PASS":
                return value
    raise RuntimeError(f"missing PASS replay receipt in {path}")


def direction(value: float) -> str:
    if value < 1.0:
        return "AWQ_LT_RAW"
    if value > 1.0:
        return "AWQ_GT_RAW"
    return "AWQ_EQ_RAW"


def main() -> None:
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite {OUT}")
    OUT.mkdir(parents=True)

    v1_sums = {}
    v1_audit_points = []
    for point_id, point in POINTS.items():
        records, units = read_ncu_csv(V1 / f"RAW_{point_id}_NCU_BASE.csv")
        command = profiler_command(V1 / f"RAW_{point_id}_NCU_SESSION.csv")
        passes = [int(record["profiler__replayer_passes"].replace(",", "")) for record in records]
        if "--replay-mode application" in command or "--cache-control none" in command:
            raise RuntimeError(f"V1 profiler mode audit failed for {point_id}")
        if passes != [7] * len(records):
            raise RuntimeError(f"V1 replay-pass audit failed for {point_id}: {passes}")
        for metric in METRICS:
            if units[metric] != "byte":
                raise RuntimeError(f"V1 metric unit mismatch: {metric} {units[metric]}")
            v1_sums[(point_id, metric)] = sum(float(row[metric].replace(",", "")) for row in records)
        v1_audit_points.append(
            {
                "point_id": point_id,
                "profiler_command": command,
                "replay_passes_per_selected_kernel": passes,
                "kernel_count": len(records),
            }
        )

    v1_ratios = {}
    for metric in METRICS:
        v1_ratios[metric] = {
            "M1_AWQ_over_RAW": v1_sums[("M1_AWQ", metric)] / v1_sums[("M1_RAW", metric)],
            "M256_AWQ_over_RAW": v1_sums[("M256_AWQ", metric)] / v1_sums[("M256_RAW", metric)],
        }
    write_json(
        "UPSTREAM_V1_AUDIT.json",
        {
            "producer": "hrl/c16-e1-semantic-ncu-109-v1@9ad003fff0d42b544d3a703eca4846364c13ccb6",
            "clean_e1_producer": "hrl/c16-e1-clean-baseline-109-v1@8988d6108ff8bdca180a14cec2fe769df45b09f1",
            "clean_e1_independent_consumer": "hrl/c16-e1-clean-baseline-consumer-prep-174new-v1@59ddb8ba2a33ef12b73bfc859f3a994e0b4ef4ca",
            "semantic_ncu_consumer_hardening": "hrl/c16-e1-semantic-ncu-consumer-hardening-v1@396233ca250c20be834aa0c50d2504e6017953bc",
            "status": "PASS",
            "interpretation": "COLD_CACHE_KERNEL_REPLAY_DIAGNOSTIC",
            "arithmetic_unchanged": True,
            "default_kernel_replay": True,
            "cache_control_none_explicit": False,
            "points": v1_audit_points,
            "raw_recomputed_ratios": v1_ratios,
        },
    )

    kernel_rows = []
    traffic_rows = []
    report_receipts = []
    point_bindings = []
    v2_sums = {}
    profiler_commands = {}
    all_pass_counts = {}
    for point_id, point in POINTS.items():
        base_path = REPORTS / f"{point_id}.base.csv"
        session_path = REPORTS / f"{point_id}.session.csv"
        report_path = REPORTS / f"{point_id}.ncu-rep"
        log_path = SOURCE / "logs" / f"{point_id}.log"
        records, units = read_ncu_csv(base_path)
        command = profiler_command(session_path)
        receipt = replay_receipt(log_path)
        if len(records) != point["expected_kernel_count"]:
            raise RuntimeError(f"V2 kernel-count mismatch for {point_id}")
        required_fragments = ["--replay-mode application", "--cache-control none", f"--nvtx-include {point['range']}/"]
        if any(fragment not in command for fragment in required_fragments):
            raise RuntimeError(f"V2 command contract mismatch for {point_id}: {command}")
        if not (
            receipt["M"] == point["M"]
            and receipt["impl"] == point["replay_impl"]
            and receipt["range"] == point["range"]
            and receipt["input_sha256"] == point["input_sha256"]
            and receipt["output_sha256"] == point["output_sha256"]
        ):
            raise RuntimeError(f"V2 semantic receipt mismatch for {point_id}")
        range_column = next(name for name in records[0] if "Push/Pop_Range" in name)
        pass_counts = []
        for index, record in enumerate(records):
            if point["range"] not in record[range_column]:
                raise RuntimeError(f"V2 NVTX range mismatch for {point_id}")
            pass_count = int(record["profiler__replayer_passes"].replace(",", ""))
            pass_counts.append(pass_count)
            kernel_name = record["Kernel Name"]
            if point["implementation"] == "AWQ_FP16_INPUT":
                expected_fragment = "gemm_forward_4bit" if index == 0 else "reduce_kernel"
                if expected_fragment not in kernel_name:
                    raise RuntimeError(f"V2 AWQ kernel inventory mismatch for {point_id}: {kernel_name}")
            kernel_rows.append(
                {
                    "point_id": point_id,
                    "M": point["M"],
                    "implementation": point["implementation"],
                    "nvtx_range": point["range"],
                    "kernel_index": index,
                    "kernel_name": kernel_name,
                    "grid_size": record["Grid Size"],
                    "block_size": record["Block Size"],
                    "profiler_replayer_passes": pass_count,
                }
            )
            for metric in METRICS:
                if units[metric] != "byte":
                    raise RuntimeError(f"V2 metric unit mismatch: {metric} {units[metric]}")
        if pass_counts != [1] * len(records):
            raise RuntimeError(f"V2 application replay-pass count mismatch for {point_id}: {pass_counts}")
        all_pass_counts[point_id] = pass_counts
        profiler_commands[point_id] = command
        for metric in METRICS:
            total = sum(float(row[metric].replace(",", "")) for row in records)
            v2_sums[(point_id, metric)] = total
            traffic_rows.append(
                {
                    "point_id": point_id,
                    "M": point["M"],
                    "implementation": point["implementation"],
                    "metric_name": metric,
                    "unit": "byte",
                    "semantic_module_sum": total,
                    "kernel_count": len(records),
                }
            )
        point_bindings.append(
            {
                "point_id": point_id,
                "M": point["M"],
                "implementation": point["implementation"],
                "nvtx_range": point["range"],
                "input_sha256": point["input_sha256"],
                "output_sha256": point["output_sha256"],
                "selected_kernel_count": len(records),
                "replay_pass_count": max(pass_counts),
            }
        )
        report_receipts.append(
            {
                "point_id": point_id,
                "report_source_path": str(report_path),
                "report_sha256": sha(report_path),
                "base_csv_sha256": sha(base_path),
                "session_csv_sha256": sha(session_path),
                "profile_log_sha256": sha(log_path),
            }
        )
        shutil.copy2(base_path, OUT / f"RAW_{point_id}_BASE.csv")
        shutil.copy2(session_path, OUT / f"RAW_{point_id}_SESSION.csv")
        shutil.copy2(log_path, OUT / f"RAW_{point_id}_PROFILE.log")

    v2_comparison = {}
    for metric in METRICS:
        raw1, awq1 = v2_sums[("M1_RAW", metric)], v2_sums[("M1_AWQ", metric)]
        raw256, awq256 = v2_sums[("M256_RAW", metric)], v2_sums[("M256_AWQ", metric)]
        v2_comparison[metric] = {
            "unit": "byte",
            "M1_AWQ_over_RAW": awq1 / raw1,
            "M256_AWQ_over_RAW": awq256 / raw256,
            "RAW_M256_over_M1": raw256 / raw1,
            "AWQ_M256_over_M1": awq256 / awq1,
            "shape_interaction_ratio": (awq256 / raw256) / (awq1 / raw1),
        }
    write_json(
        "TRAFFIC_COMPARISON.json",
        {
            "profiler_context": "APPLICATION_REPLAY_CACHE_CONTROL_NONE",
            "metrics": v2_comparison,
            "accepted_native_timing": TIMING,
            "timing_direction_match": {
                metric: {
                    "M1": direction(values["M1_AWQ_over_RAW"]) == direction(TIMING["M1_AWQ_over_RAW"]),
                    "M256": direction(values["M256_AWQ_over_RAW"]) == direction(TIMING["M256_AWQ_over_RAW"]),
                    "shape_interaction": (values["shape_interaction_ratio"] > 1) == (TIMING["shape_interaction_ratio"] > 1),
                }
                for metric, values in v2_comparison.items()
            },
            "claim_boundary": "Traffic/timing directional association does not establish cache or TLB causality.",
        },
    )

    classifications = {}
    for metric in METRICS:
        v1_values, v2_values = v1_ratios[metric], v2_comparison[metric]
        same_direction = all(
            direction(v1_values[key]) == direction(v2_values[key])
            for key in ("M1_AWQ_over_RAW", "M256_AWQ_over_RAW")
        )
        relative_changes = {
            key: abs(v2_values[key] / v1_values[key] - 1.0)
            for key in ("M1_AWQ_over_RAW", "M256_AWQ_over_RAW")
        }
        if not same_direction:
            category = "QUALITATIVE_DIRECTION_CHANGED"
        elif all(value <= SIMILAR_RELATIVE_TOLERANCE for value in relative_changes.values()):
            category = "SAME_DIRECTION_SIMILAR_MAGNITUDE"
        else:
            category = "SAME_DIRECTION_DIFFERENT_MAGNITUDE"
        classifications[metric] = {
            "classification": category,
            "V1": v1_values,
            "V2": {
                "M1_AWQ_over_RAW": v2_values["M1_AWQ_over_RAW"],
                "M256_AWQ_over_RAW": v2_values["M256_AWQ_over_RAW"],
            },
            "relative_change_abs": relative_changes,
        }
    write_json(
        "V1_V2_COMPARISON.json",
        {
            "V1_context": "COLD_CACHE_KERNEL_REPLAY_DIAGNOSTIC",
            "V2_context": "APPLICATION_REPLAY_CACHE_CONTROL_NONE",
            "similar_magnitude_policy": f"both M1 and M256 relative changes <= {SIMILAR_RELATIVE_TOLERANCE:.2f}",
            "metrics": classifications,
        },
    )

    write_json(
        "PROFILER_MODE_CONTRACT.json",
        {
            "status": "PASS",
            "ncu_version": (SOURCE / "environment/NCU_VERSION.txt").read_text().strip(),
            "replay_mode": "application",
            "cache_control": "none",
            "metrics": METRICS,
            "metric_unit": "byte",
            "warmups_outside_nvtx_range": 2,
            "target_semantic_invocations_per_application_pass": 1,
            "unique_target_nvtx_ranges_per_process": 1,
            "replay_source": "util/vm_tlb/c16/e1_semantic_ncu_replay.py",
            "replay_source_sha256": sha(REPO / "util/vm_tlb/c16/e1_semantic_ncu_replay.py"),
            "commands": profiler_commands,
            "replay_pass_counts_per_selected_kernel": all_pass_counts,
            "ncu_help_raw_source_sha256": sha(SOURCE / "environment/NCU_HELP.txt"),
        },
    )
    write_json(
        "SELECTOR_QUALIFICATION.json",
        {
            "status": "PASS",
            "warmups_selected": 0,
            "other_semantic_invocations_selected": 0,
            "raw_complete_kernel": True,
            "awq_complete_gemm_plus_reduction_sequence": True,
            "application_replay_preserved_semantic_selector_identity": True,
            "identity_basis": "single push/pop range and one module call in the frozen replay source, plus exact selected range rows and kernel inventory",
            "report_receipts": report_receipts,
        },
    )
    shutil.copy2(SOURCE / "environment/NCU_VERSION.txt", OUT / "NCU_VERSION.txt")
    help_lines = SOURCE.joinpath("environment/NCU_HELP.txt").read_text(encoding="utf-8").splitlines()
    while help_lines and not help_lines[-1].strip():
        help_lines.pop()
    (OUT / "NCU_HELP.txt").write_text("\n".join(line.rstrip() for line in help_lines) + "\n", encoding="utf-8")

    def write_tsv(name: str, rows: list, fields: list) -> None:
        with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    write_tsv(
        "REPLAY_POINT_BINDINGS.tsv",
        point_bindings,
        ["point_id", "M", "implementation", "nvtx_range", "input_sha256", "output_sha256", "selected_kernel_count", "replay_pass_count"],
    )
    write_tsv(
        "SELECTED_KERNELS.tsv",
        kernel_rows,
        ["point_id", "M", "implementation", "nvtx_range", "kernel_index", "kernel_name", "grid_size", "block_size", "profiler_replayer_passes"],
    )
    write_tsv(
        "TRAFFIC_SUMS.tsv",
        traffic_rows,
        ["point_id", "M", "implementation", "metric_name", "unit", "semantic_module_sum", "kernel_count"],
    )
    write_json("REPORT_RECEIPTS.json", {"status": "PASS", "reports": report_receipts})

    (OUT / "SCIENTIFIC_INTERPRETATION.md").write_text(
        "# C16 E1 semantic-NCU cache-state repair interpretation\n\n"
        "V1 selector identity and raw arithmetic remain valid and unchanged. Its seven-pass default kernel replay is now explicitly interpreted as `COLD_CACHE_KERNEL_REPLAY_DIAGNOSTIC`.\n\n"
        "V2 used Nsight Compute 2025.1.1 application replay with `--cache-control none`. Each selected kernel reports one application replay pass; every application run rebuilt the accepted module state, performed two warmups outside the target range, and reproduced the accepted output SHA for its single in-range semantic invocation. RAW retained one complete target kernel and AWQ retained its GEMM plus reduction sequence.\n\n"
        "L1/TEX and L2 AWQ/RAW ratios preserve V1 direction and similar magnitude. DRAM preserves the qualitative directions but changes magnitude materially at M1: the V2 AWQ semantic-module DRAM request is 640 bytes versus 138,156,416 bytes for RAW. M256 AWQ remains above RAW for all three traffic metrics. All V2 traffic interactions retain the accepted native timing interaction direction.\n\n"
        "These results describe profiler-context-sensitive semantic-module traffic. They do not establish cache causality, TLB causality, or a mechanism opportunity. No NVBit, full address trace, shape sweep, role reselection, or cache/TLB mechanism experiment was started.\n",
        encoding="utf-8",
    )
    write_json(
        "NEXT_STEP_DECISION.json",
        {
            "decision": "STOP_AFTER_BOUNDED_CACHE_STATE_REPAIR",
            "status": "PASS",
            "V1_status": "COLD_CACHE_KERNEL_REPLAY_DIAGNOSTIC",
            "V2_status": "APPLICATION_REPLAY_CACHE_CONTROL_NONE",
            "next_authority_action": "Independent consumer verification may resume from raw V2 reports/exports/session evidence.",
            "forbidden_not_started": ["NVBit", "full address trace", "TLB/cache mechanism", "new shape sweep", "role reselection"],
        },
    )

    files = sorted(path for path in OUT.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    (OUT / "SHA256SUMS").write_text("".join(f"{sha(path)}  {path.name}\n" for path in files), encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(OUT), "files": len(files) + 1, "classifications": classifications}, sort_keys=True))


if __name__ == "__main__":
    main()
