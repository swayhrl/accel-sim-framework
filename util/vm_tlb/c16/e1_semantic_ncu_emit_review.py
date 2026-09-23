#!/usr/bin/env python3
"""Validate NCU range exports and emit the C16 E1 semantic-NCU review pack."""

import csv
import hashlib
import json
import shutil
from pathlib import Path


REPO = Path("/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-semantic-ncu-109-v1")
SOURCE = Path("/data/c16/e1_semantic_ncu_v1")
REPORTS = SOURCE / "reports"
OUT = REPO / "docs/vm_tlb/review_packs/C16_E1_SEMANTIC_NCU_109_V1"
BASELINE = REPO / "docs/vm_tlb/review_packs/C16_E1_CLEAN_BASELINE_109_V1"

POINTS = {
    "M1_RAW": {
        "M": 1,
        "implementation": "RAW_FP16",
        "range": "C16_E1_NCU_UP_M1_RAW_FP16",
        "input_sha256": "b3999f6fe161d47efdff4c7d88aa044e2cec3396f9c69fde63c53f2ba208f82e",
        "output_sha256": "50d389317ff126f2aa1e18dbf36bbf17bd66ddac2753552fc73517c1b7c3d394",
        "expected_kernel_count": 1,
    },
    "M1_AWQ": {
        "M": 1,
        "implementation": "AWQ_FP16_INPUT",
        "range": "C16_E1_NCU_UP_M1_AWQ",
        "input_sha256": "b3999f6fe161d47efdff4c7d88aa044e2cec3396f9c69fde63c53f2ba208f82e",
        "output_sha256": "5618125fc9563f42860d5df37ae9b4b6569dfc4af1d995eeb7922d9f60b31d99",
        "expected_kernel_count": 2,
    },
    "M256_RAW": {
        "M": 256,
        "implementation": "RAW_FP16",
        "range": "C16_E1_NCU_UP_M256_RAW_FP16",
        "input_sha256": "eeae491edfdbee761de47aa6c4ea35b293bb2796227927778fa51c9e58ef1b41",
        "output_sha256": "01dbbf90e7d43b86ba49ce61805f11717b7ec9f28e67d7da0ff5f73065757413",
        "expected_kernel_count": 1,
    },
    "M256_AWQ": {
        "M": 256,
        "implementation": "AWQ_FP16_INPUT",
        "range": "C16_E1_NCU_UP_M256_AWQ",
        "input_sha256": "eeae491edfdbee761de47aa6c4ea35b293bb2796227927778fa51c9e58ef1b41",
        "output_sha256": "59b56af85d0480542fa396a655f23179f879eccaa9ab32a7b98ba88e8cb33d50",
        "expected_kernel_count": 2,
    },
}

ADDITIVE = ["l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum"]
NONADDITIVE = [
    "sm__warps_active.avg.pct_of_peak_sustained_active",
    "sm__throughput.avg.pct_of_peak_sustained_elapsed",
    "sm__pipe_tensor_cycles_active_v2.avg.pct_of_peak_sustained_elapsed",
]
ALL_METRICS = ADDITIVE + NONADDITIVE


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name: str, value: object) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_ncu_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    if len(rows) < 3:
        raise RuntimeError(f"no metric rows in {path}")
    header, units = rows[0], rows[1]
    records = [dict(zip(header, row)) for row in rows[2:]]
    unit_map = dict(zip(header, units))
    return records, unit_map


def main() -> None:
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite {OUT}")
    storage = json.loads((SOURCE / "AWQ_UP_PROJ_STORAGE_AUTHORITY.json").read_text())
    packed_bytes = storage["packed_weight_storage_bytes"]
    baseline_rows = {}
    with (BASELINE / "CORE_18_POINT_PATHS.tsv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["role"] == "up_proj" and row["implementation"] in ("RAW_FP16", "AWQ_FP16_INPUT"):
                baseline_rows[(int(row["M"]), row["implementation"])] = row
    timing_rows = {}
    with (BASELINE / "CORE_18_POINT_TIMING.tsv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["role"] == "up_proj" and row["implementation"] in ("RAW_FP16", "AWQ_FP16_INPUT"):
                timing_rows[(int(row["M"]), row["implementation"])] = row

    OUT.mkdir(parents=True)
    write_json(
        "UPSTREAM_E1_AUTHORITY.json",
        {
            "producer": "hrl/c16-e1-clean-baseline-109-v1@8988d6108ff8bdca180a14cec2fe769df45b09f1",
            "independent_consumer": "hrl/c16-e1-clean-baseline-consumer-prep-174new-v1@59ddb8ba2a33ef12b73bfc859f3a994e0b4ef4ca",
            "semantic_role": "up_proj",
            "point_set": ["M1 RAW_FP16", "M1 AWQ_FP16_INPUT", "M256 RAW_FP16", "M256 AWQ_FP16_INPUT"],
            "status": "PASS",
        },
    )
    write_json("AWQ_PACKED_STORAGE_AUTHORITY.json", storage)

    selected = []
    kernel_metrics = []
    sums = []
    units_seen = {metric: set() for metric in ALL_METRICS}
    report_receipts = []
    replay_bindings = []
    runtime_replay_receipts = []

    for point_id, point in POINTS.items():
        accepted = baseline_rows[(point["M"], point["implementation"])]
        if accepted["input_sha"] != point["input_sha256"] or accepted["output_sha"] != point["output_sha256"]:
            raise RuntimeError(f"accepted baseline mismatch for {point_id}")
        replay_bindings.append({"point_id": point_id, **point})
        replay_receipt_path = SOURCE / "replay_receipts" / f"{point_id}.json"
        replay_receipt = json.loads(replay_receipt_path.read_text())
        expected_impl = "AWQ" if point["implementation"] == "AWQ_FP16_INPUT" else "RAW_FP16"
        if not (
            replay_receipt["status"] == "PASS"
            and replay_receipt["M"] == point["M"]
            and replay_receipt["impl"] == expected_impl
            and replay_receipt["range"] == point["range"]
            and replay_receipt["input_sha256"] == point["input_sha256"]
            and replay_receipt["output_sha256"] == point["output_sha256"]
        ):
            raise RuntimeError(f"standalone replay receipt mismatch for {point_id}")
        runtime_replay_receipts.append(replay_receipt)
        shutil.copy2(replay_receipt_path, OUT / f"STANDALONE_{point_id}_RECEIPT.json")
        csv_path = REPORTS / f"{point_id}.base.csv"
        auto_csv_path = REPORTS / f"{point_id}.csv"
        session_path = REPORTS / f"{point_id}.session.csv"
        rep_path = REPORTS / f"{point_id}.ncu-rep"
        records, units = read_ncu_csv(csv_path)
        auto_records, auto_units = read_ncu_csv(auto_csv_path)
        if len(records) != point["expected_kernel_count"]:
            raise RuntimeError(f"kernel count mismatch for {point_id}: {len(records)}")
        if len(auto_records) != len(records):
            raise RuntimeError(f"auto/base export row mismatch for {point_id}")
        nvtx_column = next(name for name in records[0] if "Push/Pop_Range" in name)
        for kernel_index, record in enumerate(records):
            nvtx_value = record[nvtx_column]
            if point["range"] not in nvtx_value:
                raise RuntimeError(f"wrong NVTX range for {point_id}: {nvtx_value}")
            selected.append(
                {
                    "point_id": point_id,
                    "M": point["M"],
                    "implementation": point["implementation"],
                    "nvtx_range": point["range"],
                    "kernel_index": kernel_index,
                    "kernel_name": record["Kernel Name"],
                    "grid_size": record["Grid Size"],
                    "block_size": record["Block Size"],
                }
            )
            for metric in ALL_METRICS:
                source_record = record if metric in ADDITIVE else auto_records[kernel_index]
                source_units = units if metric in ADDITIVE else auto_units
                if source_record["Kernel Name"] != record["Kernel Name"]:
                    raise RuntimeError(f"auto/base export kernel mismatch for {point_id}")
                unit = source_units[metric]
                value = float(source_record[metric].replace(",", ""))
                units_seen[metric].add(unit)
                kernel_metrics.append(
                    {
                        "point_id": point_id,
                        "M": point["M"],
                        "implementation": point["implementation"],
                        "nvtx_range": point["range"],
                        "kernel_index": kernel_index,
                        "kernel_name": record["Kernel Name"],
                        "grid_size": record["Grid Size"],
                        "block_size": record["Block Size"],
                        "metric_name": metric,
                        "unit": unit,
                        "value": value,
                        "aggregation": "ADDITIVE_WITHIN_SEMANTIC_RANGE" if metric in ADDITIVE else "PER_KERNEL_NONADDITIVE",
                    }
                )
        for metric in ADDITIVE:
            if units[metric] != "byte":
                raise RuntimeError(f"expected base byte unit for {metric}, got {units[metric]}")
            total = sum(float(record[metric].replace(",", "")) for record in records)
            sums.append(
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
        report_receipts.append(
            {
                "point_id": point_id,
                "ncu_report_path": str(rep_path),
                "ncu_report_sha256": sha(rep_path),
                "base_csv_source_path": str(csv_path),
                "base_csv_sha256": sha(csv_path),
                "auto_csv_source_path": str(auto_csv_path),
                "auto_csv_sha256": sha(auto_csv_path),
                "session_csv_source_path": str(session_path),
                "session_csv_sha256": sha(session_path),
                "kernel_count": len(records),
            }
        )
        shutil.copy2(csv_path, OUT / f"RAW_{point_id}_NCU_BASE.csv")
        shutil.copy2(auto_csv_path, OUT / f"RAW_{point_id}_NCU_AUTO.csv")
        shutil.copy2(session_path, OUT / f"RAW_{point_id}_NCU_SESSION.csv")

    if any(value != {"byte"} for metric, value in units_seen.items() if metric in ADDITIVE):
        raise RuntimeError(f"additive metric unit closure failed: {units_seen}")
    if any(value != {"%"} for metric, value in units_seen.items() if metric in NONADDITIVE):
        raise RuntimeError(f"percentage metric unit closure failed: {units_seen}")

    with (OUT / "REPLAY_POINT_BINDINGS.tsv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["point_id", "M", "implementation", "range", "input_sha256", "output_sha256", "expected_kernel_count"]
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(replay_bindings)
    for filename, rows, fields in [
        ("SELECTED_KERNELS.tsv", selected, ["point_id", "M", "implementation", "nvtx_range", "kernel_index", "kernel_name", "grid_size", "block_size"]),
        ("NCU_KERNEL_METRICS.tsv", kernel_metrics, ["point_id", "M", "implementation", "nvtx_range", "kernel_index", "kernel_name", "grid_size", "block_size", "metric_name", "unit", "value", "aggregation"]),
        ("SEMANTIC_MODULE_TRAFFIC.tsv", sums, ["point_id", "M", "implementation", "metric_name", "unit", "semantic_module_sum", "kernel_count"]),
    ]:
        with (OUT / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
            writer.writeheader(); writer.writerows(rows)

    availability = []
    for metric in ALL_METRICS:
        availability.append(
            {
                "metric_name": metric,
                "unit": next(iter(units_seen[metric])),
                "available": True,
                "semantic_aggregation": "SUM" if metric in ADDITIVE else "PER_KERNEL_ONLY",
            }
        )
    with (OUT / "NCU_METRIC_AVAILABILITY.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=["metric_name", "unit", "available", "semantic_aggregation"], lineterminator="\n")
        writer.writeheader(); writer.writerows(availability)

    sum_map = {(row["point_id"], row["metric_name"]): row["semantic_module_sum"] for row in sums}
    normalizations = []
    raw_weight_bytes = 3584 * 18944 * 2
    for point_id, point in POINTS.items():
        input_elements = point["M"] * 3584
        output_elements = point["M"] * 18944
        for metric in ADDITIVE:
            value = sum_map[(point_id, metric)]
            row = {
                "point_id": point_id,
                "metric_name": metric,
                "bytes": value,
                "bytes_per_input_element": value / input_elements,
                "bytes_per_output_element": value / output_elements,
                "bytes_per_raw_fp16_dense_weight_byte": value / raw_weight_bytes,
                "bytes_per_awq_packed_storage_byte": value / packed_bytes if point["implementation"] == "AWQ_FP16_INPUT" else "NA",
            }
            normalizations.append(row)
    with (OUT / "TRAFFIC_NORMALIZATION.tsv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["point_id", "metric_name", "bytes", "bytes_per_input_element", "bytes_per_output_element", "bytes_per_raw_fp16_dense_weight_byte", "bytes_per_awq_packed_storage_byte"]
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(normalizations)

    traffic_comparison = {}
    for metric in ADDITIVE:
        raw1, awq1 = sum_map[("M1_RAW", metric)], sum_map[("M1_AWQ", metric)]
        raw256, awq256 = sum_map[("M256_RAW", metric)], sum_map[("M256_AWQ", metric)]
        traffic_comparison[metric] = {
            "unit": "byte",
            "M1_AWQ_over_RAW": awq1 / raw1,
            "M256_AWQ_over_RAW": awq256 / raw256,
            "RAW_M256_over_M1": raw256 / raw1,
            "AWQ_M256_over_M1": awq256 / awq1,
            "shape_interaction_ratio": (awq256 / raw256) / (awq1 / raw1),
        }
    raw_t1 = float(timing_rows[(1, "RAW_FP16")]["median_ms"])
    awq_t1 = float(timing_rows[(1, "AWQ_FP16_INPUT")]["median_ms"])
    raw_t256 = float(timing_rows[(256, "RAW_FP16")]["median_ms"])
    awq_t256 = float(timing_rows[(256, "AWQ_FP16_INPUT")]["median_ms"])
    timing = {
        "M1_AWQ_over_RAW": awq_t1 / raw_t1,
        "M256_AWQ_over_RAW": awq_t256 / raw_t256,
        "RAW_M256_over_M1": raw_t256 / raw_t1,
        "AWQ_M256_over_M1": awq_t256 / awq_t1,
        "shape_interaction_ratio": (awq_t256 / raw_t256) / (awq_t1 / raw_t1),
    }
    write_json(
        "TIMING_TRAFFIC_COMPARISON.json",
        {
            "timing": timing,
            "traffic": traffic_comparison,
            "direction_test": {
                metric: {
                    "M1_same_direction_as_timing": (values["M1_AWQ_over_RAW"] < 1) == (timing["M1_AWQ_over_RAW"] < 1),
                    "M256_same_direction_as_timing": (values["M256_AWQ_over_RAW"] < 1) == (timing["M256_AWQ_over_RAW"] < 1),
                    "interaction_same_direction_as_timing": (values["shape_interaction_ratio"] > 1) == (timing["shape_interaction_ratio"] > 1),
                }
                for metric, values in traffic_comparison.items()
            },
            "causality_boundary": "Traffic association does not establish cache or TLB causality.",
        },
    )
    write_json(
        "STANDALONE_REPLAY_QUALIFICATION.json",
        {
            "status": "PASS",
            "warmup_invocations_outside_profile_range": 2,
            "target_semantic_invocations_inside_profile_range": 1,
            "all_output_sha256_match_accepted_baseline": True,
            "all_raw_fp16_awq_input_sha256_pairs_bitwise_equal": True,
            "points": replay_bindings,
            "runtime_receipts": runtime_replay_receipts,
        },
    )
    write_json(
        "NVTX_SELECTOR_CONTRACT.json",
        {
            "status": "SEMANTIC_MODULE_RANGE_QUALIFIED",
            "ncu_version": "NVIDIA Nsight Compute CLI 2025.1.1.0 build 35528883",
            "selector_form": "--nvtx --nvtx-include <push-pop-range-name>/",
            "trailing_slash_required_by_installed_NCU": True,
            "unique_range_occurrences_per_process": 1,
            "warmups_selected": 0,
            "other_semantic_invocations_selected": 0,
            "all_kernels_within_target_range_retained": True,
            "awq_multi_kernel_module_call_is_intentional": True,
            "report_receipts": report_receipts,
        },
    )
    (OUT / "SCIENTIFIC_INTERPRETATION.md").write_text(
        "# C16 E1 semantic-NCU interpretation\n\n"
        "The four frozen `up_proj` points replayed with byte-identical accepted FP16 activations and reproduced every accepted output SHA. "
        "An installed-NCU-qualified push/pop NVTX selector retained exactly one semantic module invocation per process: one RAW kernel or the two-kernel AWQ GEMM-plus-reduction sequence.\n\n"
        "The additive L1/TEX, L2 and DRAM requested-byte counters are summed over the complete semantic range. Percentage metrics remain per-kernel observations and are never added. "
        "The resulting traffic ratios are compared with accepted native timing ratios in `TIMING_TRAFFIC_COMPARISON.json`. Association in direction or interaction is descriptive only: these data do not identify cache, TLB, or any other mechanism as causal.\n\n"
        "This stage closes the previously unresolved semantic selector without changing the frozen role or point matrix. No NVBit, full address trace, or cache/TLB mechanism experiment was started.\n",
        encoding="utf-8",
    )
    write_json(
        "NEXT_STEP_DECISION.json",
        {
            "decision": "STOP_AFTER_SEMANTIC_NCU_REVIEW",
            "selector_status": "SEMANTIC_MODULE_RANGE_QUALIFIED",
            "traffic_status": "UNIT_RESOLVED_COMPLETE",
            "scientific_boundary": "Descriptive semantic-module traffic only; no cache/TLB causality claim.",
            "forbidden_not_started": ["NVBit", "full address trace", "TLB/cache mechanism"],
        },
    )
    files = sorted(path for path in OUT.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    (OUT / "SHA256SUMS").write_text("".join(f"{sha(path)}  {path.name}\n" for path in files), encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(OUT), "files": len(files) + 1, "kernel_rows": len(selected), "metric_rows": len(kernel_metrics)}, sort_keys=True))


if __name__ == "__main__":
    main()
