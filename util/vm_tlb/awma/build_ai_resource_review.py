#!/usr/bin/env python3
"""Build deterministic review tables for AI resource characterization."""

from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path


PACK = Path("/root/workspace/accel-sim-framework-awma-ai-gpu-resource-bottleneck-characterization-v1/docs/vm_tlb/review_packs/AWMA_AI_GPU_RESOURCE_BOTTLENECK_CHARACTERIZATION_V1")
RAW = Path("/root/share/mnt164/huangrulin/awma_ai_gpu_resource_bottleneck_characterization_v1/raw")
BASELINE_DIRS = {
    "T0": Path("/root/share/mnt164/huangrulin/awma_post_classic_baseline_residual_discovery_v1/observatory_raw/T0_REFERENCE_OBSERVATORY_L1_10_80"),
    "T1": Path("/root/share/mnt164/huangrulin/awma_post_classic_baseline_residual_discovery_v1/observatory_raw/T1_REFERENCE_OBSERVATORY_L1_10_80"),
    "T2": Path("/root/share/mnt164/huangrulin/awma_post_classic_baseline_residual_discovery_v1/observatory_raw/T2_REFERENCE_OBSERVATORY_L1_10_80"),
    "SPLITKV": RAW / "SPLITKV__BASELINE",
    "L2": Path("/root/share/mnt164/huangrulin/awma_ai_translation_native_residual_174new_v1/raw/L2_WARP_REFERENCE_10_80"),
    "L1": Path("/root/share/mnt164/huangrulin/awma_ai_translation_native_residual_174new_v1/raw/L1_WARP_REFERENCE_10_80"),
    "M1": Path("/root/share/mnt164/huangrulin/awma_ai_translation_native_residual_174new_v1/raw/M1_WARP_REFERENCE_10_80"),
    "M2": Path("/root/share/mnt164/huangrulin/awma_ai_translation_native_residual_174new_v1/raw/M2_WARP_REFERENCE_10_80"),
}
EXPECTED = {
    "T0": (488559, 368696302, 224), "T1": (619514, 369131520, 384),
    "T2": (94034, 43357696, 1216), "SPLITKV": (72817, 36599648, 126),
    "L2": (28335, 19397000, 64), "L1": (320808, 138166272, 2048),
    "M1": (57107, 17270784, 256), "M2": (7126, 15448, 1),
}
TWO_X = [
    ("T0", "D1_EXECUTION_SFU", "SFU_2X", "SKIPPED_SOURCE_COUPLING"),
    ("T0", "D2_L1D_LATENCY", "L1_LAT_2X", "PASS"),
    ("T1", "D1_EXECUTION_TENSOR", "TENSOR_2X", "INVALID_SOURCE_COUPLING"),
    ("T1", "D3_L2_CAPACITY", "L2_CAP_2X", "PASS"),
    ("T2", "D2_L1D_RESERVATION", "L1_MSHR_2X", "PASS"),
    ("T2", "D5_DRAM_SERVICE", "DRAM_2X", "PASS"),
    ("SPLITKV", "D3_L2_RESERVATION", "L2_MSHR_2X", "PASS"),
    ("SPLITKV", "D5_DRAM_SERVICE", "DRAM_2X", "PASS"),
    ("L2", "D1_EXECUTION_SFU", "SFU_2X", "SKIPPED_SOURCE_COUPLING"),
    ("L2", "D3_L2_RESERVATION", "L2_MSHR_2X", "PASS"),
    ("L1", "D2_L1D_RESERVATION", "L1_MSHR_2X", "PASS"),
    ("L1", "D5_DRAM_SERVICE", "DRAM_2X", "PASS"),
    ("M1", "D2_L1D_RESERVATION", "L1_MSHR_2X", "PASS"),
    ("M1", "D5_DRAM_SERVICE", "DRAM_2X", "PASS"),
]
UPPER = [
    ("T0", "D2_L1D_LATENCY", "L1_LAT_UB"),
    ("T1", "D3_L2_CAPACITY", "L2_CAP_UB"),
    ("T2", "D2_L1D_RESERVATION", "L1_MSHR_UB"),
    ("SPLITKV", "D3_L2_RESERVATION", "L2_MSHR_UB"),
    ("L2", "D3_L2_RESERVATION", "L2_MSHR_UB"),
    ("L1", "D5_DRAM_SERVICE", "DRAM_UB"),
    ("M1", "D2_L1D_RESERVATION", "L1_MSHR_UB"),
]
SATURATION = {
    "T0": ("INTERVENTION_NON_MONOTONIC", "1-cycle modeled latency is slower than 16-cycle; scheduler/cache timing response is non-monotonic"),
    "T1": ("LOW_RESPONSE", "2x and 4x L2 set count both reproduce baseline cycles and pressure"),
    "T2": ("FINITE_RESOURCE_SENSITIVE;DIMINISHING_RETURN_OBSERVED;BOTTLENECK_MIGRATION_OBSERVED", "L1 reservation failures collapse, 2x and upper cycles match, dependency/DRAM pressure remains"),
    "SPLITKV": ("LOW_RESPONSE;DIMINISHING_RETURN_OBSERVED;BOTTLENECK_MIGRATION_OBSERVED", "L2 reservation failures fall sharply but cycle response is only 0.611%; DRAM/dependency pressure remains"),
    "L2": ("LOW_RESPONSE", "L2 reservation failures fall sharply without a positive cycle response"),
    "L1": ("FINITE_RESOURCE_SENSITIVE;INTERVENTION_NON_MONOTONIC", "2x DRAM ratio improves 7.634% but the stronger ratio improves only 4.725%; timing-law coupling is visible"),
    "M1": ("FINITE_RESOURCE_SENSITIVE;DIMINISHING_RETURN_OBSERVED", "2x and upper L1-MSHR cycles match at a 2.171% response"),
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def scalar(lines: list[str], name: str) -> int | None:
    values = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(name + " ="):
            values.append(int(stripped.split("=", 1)[1].strip()))
    return values[-1] if values else None


def parse(run: Path) -> dict[str, object]:
    lines = (run / "run.log").read_text(errors="strict").splitlines()
    metrics: dict[str, tuple[int, float, int]] = {}
    progress: dict[str, int] = {}
    for line in lines:
        if line.startswith("awma_observatory_metric"):
            fields = line.split("\t")
            metrics[f"{fields[1]}.{fields[2]}"] = (int(fields[4]), float(fields[6]), int(fields[7]))
        elif line.startswith("awma_observatory_progress\t"):
            fields = line.split("\t")
            progress[fields[1]] = int(fields[-1])
    coverage_lines = [line for line in lines if line.startswith("AWMA_VM_COVERAGE ")]
    coverage = None
    if coverage_lines:
        match = re.fullmatch(
            r"AWMA_VM_COVERAGE admissions=(\d+) translated=(\d+) untranslated=(\d+) unobserved=(\d+) unique=(\d+) translated_unique=(\d+) untranslated_unique=(\d+)",
            coverage_lines[-1],
        )
        if match:
            coverage = tuple(map(int, match.groups()))
    return {
        "cycles": scalar(lines, "gpu_sim_cycle"), "instructions": scalar(lines, "gpu_sim_insn"),
        "ctas": scalar(lines, "gpu_tot_issued_cta"), "duplicate": scalar(lines, "vm_ready_application_duplicate_attempts"),
        "terminal": scalar(lines, "awma_intrawarp_terminal_quiescent"),
        "quiescent": scalar(lines, "vm_translation_quiescent_invariants_hold"),
        "coverage": coverage, "metrics": metrics, "progress": progress,
    }


def metric(data: dict[str, object], name: str, field: int = 0) -> object:
    value = data["metrics"].get(name)  # type: ignore[union-attr]
    return "NA" if value is None else value[field]


def correctness(data: dict[str, object], target: str) -> bool:
    coverage = data["coverage"]
    return bool(
        data["instructions"] == EXPECTED[target][1]
        and data["ctas"] == EXPECTED[target][2]
        and data["duplicate"] == 0 and data["terminal"] == 1 and data["quiescent"] == 1
        and coverage and coverage[0] == coverage[1] and coverage[2] == 0 and coverage[3] == 0
        and coverage[4] == coverage[5] and coverage[6] == 0
    )


def response(base: int, cycles: int) -> float:
    return (base - cycles) * 100.0 / base


def tsv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, columns, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def result_row(target: str, domain: str, arm: str, status: str) -> dict[str, object]:
    base = parse(BASELINE_DIRS[target])
    run = RAW / f"{target}__{arm}"
    if status != "PASS":
        return {"target": target, "domain": domain, "arm": arm, "status": status,
                "baseline_cycles": base["cycles"], "cycles": "NA", "cycle_response_percent": "NA",
                "instructions": "NA", "ctas": "NA", "work_conserved": "NA", "correctness": "NA",
                "l1_reservation_fail": "NA", "l2_reservation_fail": "NA", "ldst_resource": "NA",
                "ldst_coal": "NA", "ldst_icnt": "NA", "dram_queue_mean": "NA",
                "eligible_structural": "NA", "dependency_scoreboard": "NA",
                "raw_dir": str(run) if run.exists() else "NOT_RUN"}
    data = parse(run); cycles = int(data["cycles"])
    return {"target": target, "domain": domain, "arm": arm, "status": status,
            "baseline_cycles": base["cycles"], "cycles": cycles,
            "cycle_response_percent": f"{response(int(base['cycles']), cycles):.6f}",
            "instructions": data["instructions"], "ctas": data["ctas"],
            "work_conserved": data["instructions"] == base["instructions"] and data["ctas"] == base["ctas"],
            "correctness": correctness(data, target),
            "l1_reservation_fail": metric(data, "memory.l1_reservation_fail"),
            "l2_reservation_fail": metric(data, "memory.l2_reservation_fail"),
            "ldst_resource": metric(data, "memory.ldst_resource_stall"),
            "ldst_coal": metric(data, "memory.ldst_coal_stall"),
            "ldst_icnt": metric(data, "memory.ldst_icnt_stall"),
            "dram_queue_mean": metric(data, "memory.dram_queue_occupancy", 1),
            "eligible_structural": metric(data, "scheduler.eligible_structural"),
            "dependency_scoreboard": metric(data, "scheduler.dependency_scoreboard"),
            "raw_dir": str(run)}


def main() -> int:
    PACK.mkdir(parents=True, exist_ok=True)
    result_columns = ["target", "domain", "arm", "status", "baseline_cycles", "cycles",
                      "cycle_response_percent", "instructions", "ctas", "work_conserved", "correctness",
                      "l1_reservation_fail", "l2_reservation_fail", "ldst_resource", "ldst_coal", "ldst_icnt",
                      "dram_queue_mean", "eligible_structural", "dependency_scoreboard", "raw_dir"]
    two_rows = [result_row(*item) for item in TWO_X]
    upper_rows = [result_row(target, domain, arm, "PASS") for target, domain, arm in UPPER]
    tsv(PACK / "RESOURCE_2X_MATRIX.tsv", two_rows, result_columns)
    tsv(PACK / "RESOURCE_UPPER_BOUND_MATRIX.tsv", upper_rows, result_columns)

    selected_2x = {row["target"]: row for row in two_rows if row["status"] == "PASS" and any(
        row["arm"] == arm for target, _, arm in UPPER if target == row["target"]
        for arm in [arm.replace("_UB", "_2X")]
    )}
    # The textual arm replacement is exact for every frozen upper selection.
    saturation = []
    for upper in upper_rows:
        target = str(upper["target"]); two = selected_2x[target]
        two_cycles = int(two["cycles"]); upper_cycles = int(upper["cycles"])
        classes, migration = SATURATION[target]
        saturation.append({
            "target": target, "selected_domain": upper["domain"], "baseline_cycles": upper["baseline_cycles"],
            "two_x_cycles": two_cycles, "upper_cycles": upper_cycles,
            "baseline_to_two_x_percent": two["cycle_response_percent"],
            "two_x_to_upper_incremental_percent": f"{(two_cycles-upper_cycles)*100.0/two_cycles:.6f}",
            "classification": classes, "pressure_migration_or_limit": migration,
        })
    tsv(PACK / "RESOURCE_SATURATION_MAP.tsv", saturation,
        ["target", "selected_domain", "baseline_cycles", "two_x_cycles", "upper_cycles",
         "baseline_to_two_x_percent", "two_x_to_upper_incremental_percent", "classification",
         "pressure_migration_or_limit"])

    raw_rows = []
    roots = [("REUSED_BASELINE", target, "BASELINE", path) for target, path in BASELINE_DIRS.items()]
    roots += [("NEW_RUN", directory.name.split("__", 1)[0], directory.name.split("__", 1)[1], directory)
              for directory in sorted(RAW.iterdir()) if directory.is_dir()]
    seen: set[Path] = set()
    for scope, target, arm, directory in roots:
        for path in sorted(directory.rglob("*")):
            if path.is_symlink() or not path.is_file() or path in seen:
                continue
            if path.suffix == ".xz":
                continue
            seen.add(path)
            raw_rows.append({"scope": scope, "target": target, "arm": arm, "path": str(path),
                             "sha256": sha(path), "bytes": path.stat().st_size})
    tsv(PACK / "RAW_DATA_INDEX.tsv", raw_rows, ["scope", "target", "arm", "path", "sha256", "bytes"])

    manifest = []
    for path in sorted(PACK.iterdir()):
        if path.is_file() and path.name != "SHA256SUMS":
            manifest.append(f"{sha(path)}  {path.name}")
    (PACK / "SHA256SUMS").write_text("\n".join(manifest) + "\n")
    print(f"two_x={len(two_rows)} upper={len(upper_rows)} raw={len(raw_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
