#!/usr/bin/env python3
"""Qualify the bounded real-trace M1F activation chain without timing claims."""
from __future__ import annotations

import argparse
import bisect
import collections
import csv
import hashlib
import json
import re
import struct
from pathlib import Path


SEED = 0x6A09E667F3BCC908
THRESHOLD = 0x0484BAF3B723B966
MASK64 = (1 << 64) - 1
PAIR = struct.Struct("<QQ")
KERNELS = {
    4490: {"layer": 0, "target_class": 1, "exact": 0x7EA94E025120,
           "run": "N2_L0_RUN1",
           "trace_sha256": "5cd1b6c8d4864b3805da2eafd9ec396983856070a28421d3db652d665e8d7e80"},
    5232: {"layer": 14, "target_class": 15, "exact": 0x7EA906000120,
           "run": "N2_L14",
           "trace_sha256": "caf40e21306946515b752f47db8f33302cca47c816ee44690373f3fdfab16125"},
    5921: {"layer": 27, "target_class": 28, "exact": 0x7EA7DE025480,
           "run": "N2_L27",
           "trace_sha256": "b6415f5daf641cedee714f6f81a7ebf4c72dae11cbaeb46883eae241a5733400"},
}


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def stable_hash(target_class: int, line_index: int) -> int:
    value = (SEED ^ (target_class << 32) ^ line_index) & MASK64
    value = (value + 0x9E3779B97F4A7C15) & MASK64
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK64
    return (value ^ (value >> 31)) & MASK64


def read_sidecar(path: Path):
    rows = []
    with path.open(encoding="utf-8") as stream:
        need(stream.readline().rstrip("\n") ==
             "ORACLE_ELASTIC_QWEIGHT_RESIDENCY_V1\t1\tMODELED_L2_GET_ADDR",
             "sidecar header drift")
        for raw in stream:
            if not raw.strip():
                continue
            begin, end, name, target_class = raw.rstrip("\n").split("\t")
            rows.append({"begin": int(begin, 0), "end": int(end, 0),
                         "name": name, "target_class": int(target_class)})
    rows.sort(key=lambda row: row["begin"])
    need(len(rows) == 28, "sidecar must have 28 regions")
    return rows, [row["begin"] for row in rows]


def lookup(address: int, regions, starts):
    index = bisect.bisect_right(starts, address) - 1
    if index >= 0 and address < regions[index]["end"]:
        return regions[index]
    return None


def read_pairs(path: Path):
    raw = path.read_bytes()
    need(len(raw) % PAIR.size == 0, f"ragged pair file: {path}")
    return [row for row in struct.iter_unpack("<QQ", raw)]


def parse_fields(line: str) -> dict[str, int]:
    result = {}
    for field in line.rstrip("\n").split("\t")[1:]:
        if "=" not in field:
            continue
        key, value = field.split("=", 1)
        result[key] = int(value)
    return result


def last_snapshot(text: str) -> list[str]:
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines)
              if line == "oracle_elastic_l2_snapshot_begin"]
    ends = [i for i, line in enumerate(lines)
            if line == "oracle_elastic_l2_snapshot_end"]
    need(starts and ends and starts[-1] < ends[-1], "oracle snapshot absent")
    return lines[starts[-1] + 1:ends[-1]]


def sum_oracle(path: Path) -> tuple[dict[str, int], dict[int, dict[str, int]]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    rows = [parse_fields(line) for line in last_snapshot(text)
            if line.startswith("oracle_elastic_l2\t")]
    need(len(rows) == 16, f"expected 16 L2 instance rows: {path}")
    need({row["instance"] for row in rows} == set(range(16)),
         "L2 instance closure failed")
    summed = collections.defaultdict(int)
    for row in rows:
        for key, value in row.items():
            if key != "instance":
                summed[key] += value
    class_rows = [parse_fields(line) for line in last_snapshot(text)
                  if line.startswith("oracle_elastic_l2_class_activity\t")]
    by_class: dict[int, dict[str, int]] = {}
    for row in class_rows:
        target_class = row.pop("target_class")
        row.pop("instance")
        bucket = by_class.setdefault(target_class, collections.defaultdict(int))
        for key, value in row.items():
            bucket[key] += value
    return dict(summed), {key: dict(value) for key, value in by_class.items()}


def scalar_metrics(path: Path) -> dict[str, int | str | bool]:
    text = path.read_text(encoding="utf-8", errors="replace")
    result: dict[str, int | str | bool] = {}
    for key in ("gpu_sim_cycle", "gpu_sim_insn", "gpu_tot_sim_cycle",
                "gpu_tot_sim_insn", "gpu_tot_issued_cta"):
        found = re.findall(rf"^{re.escape(key)}\s*=\s*(\d+)\s*$", text,
                           re.MULTILINE)
        need(bool(found), f"missing {key}: {path}")
        result[key] = int(found[-1])
    result["simulation_thread_exiting"] = (
        "GPGPU-Sim: *** simulation thread exiting ***" in text)
    result["exit_detected"] = "GPGPU-Sim: *** exit detected ***" in text
    result["max_cycle_termination"] = "break due to reaching the maximum" in text
    return result


def common_stats(path: Path) -> dict[str, str]:
    result = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"^\s*([A-Za-z][A-Za-z0-9_\[\].]+)\s*=\s*(.*?)\s*$", raw)
        if not match:
            continue
        key, value = match.groups()
        if key.startswith(("gpu_", "L2_", "total_icnt_", "max_mrq_")):
            if key in {"gpu_total_sim_rate"}:
                continue
            result[key] = value
    return result


def read_activation(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    need(bool(rows), f"empty activation log: {path}")
    return rows


def validate_activation(rows, regions, starts, expected_class, exact_address):
    selected_admitted = None
    exact = None
    decisions = {}
    non_target_rows = 0
    for row in rows:
        address = int(row["address_dec"])
        target = row["oracle_target"] == "1"
        eligible = row["protection_eligible"] == "1"
        filtered = row["selection_filtered"] == "1"
        if not target:
            non_target_rows += 1
            need(not eligible and not filtered, "non-target selection leakage")
            continue
        region = lookup(address, regions, starts)
        need(region is not None, "runtime target outside sidecar")
        target_class = int(row["target_class"])
        line_address = address & ~127
        line_index = (line_address - region["begin"]) // 128
        hashed = stable_hash(target_class, line_index)
        need(target_class == region["target_class"] == expected_class,
             "runtime target class drift")
        need(int(row["region_relative_line_index"]) == line_index,
             "runtime line index drift")
        need(int(row["selection_hash_hex"], 0) == hashed,
             "runtime stable hash drift")
        need(eligible == (hashed < THRESHOLD), "runtime selection drift")
        need(filtered == (not eligible), "runtime filtered identity drift")
        identity = (target_class, line_index, hashed, eligible)
        prior = decisions.setdefault(line_address, identity)
        need(prior == identity, "same line changed selector identity")
        if filtered:
            need(row["hard_admission_attempted"] == "0" and
                 row["protected_admitted"] == "0" and
                 row["admission_denied"] == "0",
                 "filtered target polluted hard admission")
        if (eligible and row["hard_admission_attempted"] == "1" and
                row["protected_admitted"] == "1" and selected_admitted is None):
            selected_admitted = row
        if address == exact_address and exact is None:
            exact = row
    need(exact is not None, "fixed exact canary absent from runtime log")
    need(selected_admitted is not None, "no selected/admitted runtime witness")
    need(non_target_rows > 0, "no runtime non-target sample")
    return exact, selected_admitted, decisions, non_target_rows


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sidecar", type=Path, required=True)
    parser.add_argument("--static-selector-summary", type=Path, required=True)
    parser.add_argument("--scan-root", type=Path, required=True)
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument("--non-target-probe", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    need(not args.output_dir.exists(), "output directory must be fresh")
    regions, starts = read_sidecar(args.sidecar)
    static = json.loads(args.static_selector_summary.read_text(encoding="utf-8"))
    static_by_class = {int(row["target_class"]): int(row["selected_lines"])
                       for row in static["classes"]}

    selection_rows = []
    admission_rows = []
    activation_canaries = []
    runtime_decisions = {}
    run_receipts = []
    for kernel_id, spec in KERNELS.items():
        scan_dir = args.scan_root / f"kernel_{kernel_id}"
        summary = json.loads((scan_dir / "summary.json").read_text(encoding="utf-8"))
        target_refs = selected_refs = 0
        target_unique = selected_unique = 0
        observed_classes = set()
        for address, count in read_pairs(scan_dir / "all_line_refs.u64"):
            region = lookup(address, regions, starts)
            if region is None:
                continue
            observed_classes.add(region["target_class"])
            target_refs += count
            target_unique += 1
            line_index = (address - region["begin"]) // 128
            if stable_hash(region["target_class"], line_index) < THRESHOLD:
                selected_refs += count
                selected_unique += 1
        need(observed_classes == {spec["target_class"]}, "unexpected target class in trace")
        need(target_refs == summary["target_128b_line_references"], "trace target ref drift")
        need(target_unique == summary["target_unique_128b_lines"], "trace target unique drift")
        need(selected_unique == static_by_class[spec["target_class"]],
             "trace/static selector unique-line mismatch")
        selection_rows.append({
            "kernel_id": kernel_id, "layer_index": spec["layer"],
            "target_class": spec["target_class"],
            "trace_target_line_reference_proxy": target_refs,
            "trace_selected_line_reference_proxy": selected_refs,
            "trace_reference_selected_fraction": selected_refs / target_refs,
            "target_unique_128b_lines": target_unique,
            "selected_unique_target_lines": selected_unique,
            "unique_line_selected_fraction": selected_unique / target_unique,
            "static_region_selected_lines": static_by_class[spec["target_class"]],
            "static_region_enumeration_match": True,
            "repeat_access_effect": selected_refs / target_refs - selected_unique / target_unique,
        })

        run_dir = args.runs_root / spec["run"]
        stdout = run_dir / "stdout.log"
        totals, classes = sum_oracle(stdout)
        need(spec["target_class"] in classes, "class activity row absent")
        need(totals["target_accesses"] ==
             totals["selected_target_accesses"] +
             totals["selection_filtered_target_accesses"],
             "target selection accounting does not close")
        need(totals["hard_admission_attempts"] ==
             totals["protected_admission_decisions"] +
             totals["target_protection_admission_denied"],
             "hard admission accounting does not close")
        need(totals["selection_filtered_admissions"] <=
             totals["selection_filtered_target_accesses"],
             "filtered admission attempts exceed filtered accesses")
        admission_rows.append({
            "kernel_id": kernel_id, "layer_index": spec["layer"],
            "target_class": spec["target_class"],
            "simulator_l2_totals": totals,
            "target_class_totals": classes[spec["target_class"]],
            "simulator_selected_access_fraction":
                totals["selected_target_accesses"] / totals["target_accesses"],
            "invariants": {
                "target_equals_selected_plus_filtered": True,
                "filtered_not_counted_as_denial": True,
                "hard_attempt_equals_admitted_plus_denied": True,
            },
        })
        rows = read_activation(run_dir / "activation.tsv")
        exact, admitted, decisions, non_target_count = validate_activation(
            rows, regions, starts, spec["target_class"], spec["exact"])
        runtime_decisions[kernel_id] = decisions
        activation_canaries.append({
            "kernel_id": kernel_id, "layer_index": spec["layer"],
            "target_class": spec["target_class"],
            "fixed_real_trace_address": exact,
            "selected_protected_admission_witness": admitted,
            "runtime_non_target_sample_count": non_target_count,
        })
        metrics = scalar_metrics(stdout)
        need(metrics["simulation_thread_exiting"] and metrics["exit_detected"],
             "full canary did not terminate")
        need(not metrics["max_cycle_termination"], "full canary hit max-cycle bound")
        run_receipts.append({
            "run": spec["run"], "kernel_id": kernel_id,
            "status": "PASS", "natural_termination": True,
            "trace_sha256": spec["trace_sha256"],
            "stdout_sha256": sha256(stdout),
            "activation_sha256": sha256(run_dir / "activation.tsv"),
            "command": (
                "accel-sim.out -trace RUN/kernelslist.g "
                "-config configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config "
                "-config gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config "
                f"-config configs/{spec['run']}.config"),
            "metrics": metrics,
        })

    run1 = read_activation(args.runs_root / "N2_L0_RUN1" / "activation.tsv")
    run2 = read_activation(args.runs_root / "N2_L0_RUN2" / "activation.tsv")
    def canonical(rows):
        return sorted((int(row["address_dec"]), int(row["target_class"]),
                       int(row["region_relative_line_index"]),
                       int(row["selection_hash_hex"], 0),
                       int(row["protection_eligible"]),
                       int(row["selection_filtered"]))
                      for row in rows if row["oracle_target"] == "1")
    canonical1, canonical2 = canonical(run1), canonical(run2)
    need(canonical1 == canonical2, "L0 repeated run selector identity drift")
    repeat_stdout = args.runs_root / "N2_L0_RUN2" / "stdout.log"
    repeat_metrics = scalar_metrics(repeat_stdout)
    need(repeat_metrics["simulation_thread_exiting"] and
         repeat_metrics["exit_detected"] and
         not repeat_metrics["max_cycle_termination"],
         "L0 repeat did not terminate naturally")
    run_receipts.append({
        "run": "N2_L0_RUN2", "kernel_id": 4490, "status": "PASS",
        "natural_termination": True,
        "trace_sha256": KERNELS[4490]["trace_sha256"],
        "stdout_sha256": sha256(repeat_stdout),
        "activation_sha256": sha256(
            args.runs_root / "N2_L0_RUN2" / "activation.tsv"),
        "command": (
            "accel-sim.out -trace RUN/kernelslist.g "
            "-config configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config "
            "-config gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config "
            "-config configs/N2_L0_RUN2.config"),
        "metrics": repeat_metrics,
    })
    determinism = {
        "schema": "C16_E1_M1F_REAL_TRACE_DETERMINISM_V1", "status": "PASS",
        "kernel_id": 4490, "compared_target_records": len(canonical1),
        "canonical_identity_sha256": hashlib.sha256(
            json.dumps(canonical1, separators=(",", ":")).encode()).hexdigest(),
        "address_class_line_hash_selected_filtered_exact_match": True,
        "access_order_kernel_uid_decode_id_run_count_not_in_selector_key": True,
    }

    with args.non_target_probe.open(newline="", encoding="utf-8") as stream:
        probe_rows = list(csv.DictReader(stream, delimiter="\t"))
    need(probe_rows and all(row["oracle_target"] == row["expected_target"]
                            for row in probe_rows), "probe target identity drift")
    excluded = [row for row in probe_rows if row["expected_target"] == "0"]
    need(all(row["protection_eligible"] == "0" and
             row["selection_filtered"] == "0" for row in excluded),
         "non-target exclusion failed")

    neutrality = {"schema": "C16_E1_M1F_REAL_TRACE_NEUTRALITY_V1",
                  "status": "PASS", "rows": []}
    for mode in ("N0", "N1"):
        frozen = args.runs_root / f"FROZEN_{mode}" / "stdout.log"
        instrumented = args.runs_root / f"INSTRUMENTED_{mode}" / "stdout.log"
        frozen_metrics, new_metrics = scalar_metrics(frozen), scalar_metrics(instrumented)
        need(frozen_metrics == new_metrics, f"{mode} scalar neutrality drift")
        frozen_common, new_common = common_stats(frozen), common_stats(instrumented)
        need(frozen_common == new_common, f"{mode} common cache signature drift")
        row = {"mode": mode, "status": "PASS", "metrics": frozen_metrics,
               "common_cache_signature_sha256": hashlib.sha256(
                   json.dumps(frozen_common, sort_keys=True).encode()).hexdigest(),
               "frozen_vs_instrumented_exact": True}
        if mode == "N1":
            old_oracle, _ = sum_oracle(frozen)
            new_oracle, _ = sum_oracle(instrumented)
            common_keys = sorted(set(old_oracle) & set(new_oracle))
            need({key: old_oracle[key] for key in common_keys} ==
                 {key: new_oracle[key] for key in common_keys},
                 "N1 common M1 counter drift")
            row["common_m1_counters"] = {key: old_oracle[key] for key in common_keys}
        neutrality["rows"].append(row)
    neutrality["N2_boundary"] = (
        "Only target protection eligibility and resulting admission may differ; no speed claim.")

    args.output_dir.mkdir(parents=True)
    dump(args.output_dir / "REAL_TRACE_M1F_ACTIVATION_CANARIES.json", {
        "schema": "C16_E1_REAL_TRACE_M1F_ACTIVATION_CANARIES_V1",
        "status": "PASS", "canaries": activation_canaries,
    })
    dump(args.output_dir / "M1F_REAL_TRACE_SELECTION_DISTRIBUTION.json", {
        "schema": "C16_E1_M1F_REAL_TRACE_SELECTION_DISTRIBUTION_V1",
        "status": "PASS", "expected_fraction": 131072 / 7426048,
        "claim_boundary": "TRACE_REFERENCE_PROXY_AND_UNIQUE_LINE_ELIGIBILITY_NOT_L2_TIMING",
        "kernels": selection_rows,
    })
    dump(args.output_dir / "M1F_ADMISSION_ACCOUNTING.json", {
        "schema": "C16_E1_M1F_ADMISSION_ACCOUNTING_V1", "status": "PASS",
        "claim_boundary": "SIMULATOR_L2_TRANSACTIONS_NOT_TRACE_LANE_REFERENCES",
        "kernels": admission_rows,
    })
    dump(args.output_dir / "NON_TARGET_EXCLUSION.json", {
        "schema": "C16_E1_M1F_NON_TARGET_EXCLUSION_V1", "status": "PASS",
        "core_probe_rows": probe_rows,
        "excluded_labels": [row["label"] for row in excluded],
        "runtime_non_target_samples_all_ineligible": True,
        "rule": "M1F protection eligibility is evaluated only after oracle_target=true",
    })
    dump(args.output_dir / "DETERMINISM_CHECK.json", determinism)
    dump(args.output_dir / "REAL_TRACE_NEUTRALITY.json", neutrality)
    dump(args.output_dir / "RUN_RECEIPTS.json", {
        "schema": "C16_E1_M1F_REAL_TRACE_RUN_RECEIPTS_V1", "status": "PASS",
        "runs": run_receipts,
    })
    dump(args.output_dir / "VALIDATION_SUMMARY.json", {
        "schema": "C16_E1_M1F_REAL_TRACE_VALIDATION_SUMMARY_V1",
        "status": "PASS",
        "qualification": "M1F_REAL_TRACE_ACTIVATION_QUALIFIED_V1",
        "three_full_real_canaries": True, "determinism": True,
        "non_target_exclusion": True, "N0_N1_neutrality": True,
        "full_timing_authorized": False, "performance_claim": False,
    })
    checksums = []
    for path in sorted(args.output_dir.iterdir()):
        checksums.append(f"{sha256(path)}  {path.name}")
    (args.output_dir / "SHA256SUMS").write_text(
        "\n".join(checksums) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(args.output_dir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
