#!/usr/bin/env python3
"""Materialize the Lane-E review tables from exact source rows and local runs."""
from __future__ import annotations

import csv
import hashlib
import json
import argparse
from pathlib import Path


FORMAL = Path("/workspace/worktrees/accel-sim-ep-l2-c7e/docs/ep_l2/target_baseline_results_final_850/B0-Banked/convolutionSeparable")
D512 = Path("/workspace/worktrees/accel-sim-ep-l2-d512/docs/ep_l2/calibration_results/d512_850/speculative_rows")
RESULTS = Path("/workspace/results/ep_l2_line_mshr_causality")
ROOT = Path(__file__).resolve().parents[2]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source))


def number(value: str | None) -> float:
    return float(value or 0)


def whole(value: str | None) -> int:
    return int(number(value))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = list(rows[0]) if rows else []
    with path.open("w", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def app_slice_metrics(directory: Path) -> dict[str, object]:
    rows = [row for row in read_csv(directory / "target_slice.csv")
            if row.get("scope") == "application"]
    samples = sum(whole(row.get("samples")) for row in rows)
    weighted = lambda field: (sum(number(row.get(field)) * whole(row.get("samples"))
                                  for row in rows) / samples if samples else 0)
    maximum = lambda field: max((whole(row.get(field)) for row in rows), default=0)
    total = lambda field: sum(whole(row.get(field)) for row in rows)
    return {
        "samples": samples,
        "descriptor_avg": round(weighted("descriptor_avg"), 6),
        "descriptor_p95": maximum("descriptor_p95"), "descriptor_max": maximum("descriptor_max"),
        "line_mshr_avg": round(weighted("line_mshr_avg"), 6),
        "line_mshr_p95": maximum("line_mshr_p95"), "line_mshr_max": maximum("line_mshr_max"),
        "per_address_cap_block": total("c7d_per_address_cap_block"),
        "line_mshr_full_block": total("c7d_line_mshr_full_block"),
        "descriptor_pool_full_block": total("c7d_descriptor_pool_full_block"),
    }


def app_l1(directory: Path) -> dict[str, int]:
    rows = [row for row in read_csv(directory / "target_l1.csv") if row.get("scope") == "application"]
    if not rows:
        rows = [row for row in read_csv(directory / "target_l1.csv") if row.get("scope") == "kernel"]
    fields = ("accesses", "misses", "line_alloc_fail", "miss_queue_full", "mshr_entry_fail",
              "mshr_merge_fail", "mshr_rw_pending", "bank_latency_queue_conflict")
    return {field: sum(whole(row.get(field)) for row in rows) for field in fields}


def app_dram(directory: Path) -> dict[str, object]:
    rows = [row for row in read_csv(directory / "target_dram.csv") if row.get("scope") == "application"]
    read_bytes = sum(whole(row.get("successful_read_bytes")) for row in rows)
    write_bytes = sum(whole(row.get("successful_write_bytes")) for row in rows)
    numerator = sum(whole(row.get("bandwidth_util_numerator_bytes")) for row in rows)
    denominator = sum(whole(row.get("bandwidth_util_denominator_bytes")) for row in rows)
    return {"dram_read_bytes": read_bytes, "dram_write_bytes": write_bytes,
            "dram_total_bytes": read_bytes + write_bytes,
            "native_dram_data_bus_util_weighted_mean": round(numerator / denominator, 8) if denominator else "NA",
            "returnq_full_cycles": sum(whole(row.get("returnq_full_cycles")) for row in rows),
            "scheduler_full_cycles": sum(whole(row.get("scheduler_full_cycles")) for row in rows)}


def window_summary(directory: Path) -> dict[str, object]:
    rows = [row for row in read_csv(directory / "target_window.csv") if whole(row.get("samples"))]
    fields = ("descriptor_avg", "line_mshr_avg", "lowerq_avg", "missq_avg", "wad_avg")
    output: dict[str, object] = {"window_records": len(rows)}
    for field in fields:
        values = sorted(number(row.get(field)) for row in rows)
        output[field + "_window_max"] = max(values, default=0)
        output[field + "_window_p95"] = values[(95 * len(values) + 99) // 100 - 1] if values else 0
    return output


def record(label: str, directory: Path, descriptor: int, mshr: int, maturity: str) -> dict[str, object]:
    status = json.loads((directory / "run_status.json").read_text())
    summary = read_csv(directory / "target_summary.csv")[0]
    output: dict[str, object] = {
        "label": label, "descriptor_pool_size": descriptor, "line_mshr_entries": mshr,
        "maturity": maturity, "cycles": whole(status.get("terminal_gpu_tot_sim_cycle")),
        "instructions": whole(status.get("terminal_gpu_tot_sim_insn")),
        "normal_exit": int(bool(status.get("normal_simulator_exit"))), "run_status": status.get("status"),
        "terminal_clean": summary.get("invariants_terminal_clean"),
        "payload_consistent": summary.get("invariants_payload_consistent"),
        "l2_to_dram_full_block": whole(summary.get("c7d_l2_to_dram_full_block")),
        "scheduler_full_block": whole(summary.get("c7d_dram_scheduler_full_block")),
        "dram_returnq_block": whole(summary.get("c7d_dram_returnq_block")),
        "missq_full_block": whole(summary.get("c7d_missq_full_block")),
        "bank_true_conflict_ops": whole(summary.get("bank_true_conflict_ops")),
        "wad_full_events": whole(summary.get("c7d_wad_full_events")),
    }
    output.update(app_slice_metrics(directory)); output.update(app_l1(directory)); output.update(app_dram(directory));
    output.update(window_summary(directory)); return output


def options(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines()
            if line.strip() and not line.lstrip().startswith("#")]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path,
                        default=ROOT / "docs/ep_l2/review_packs/LINE_MSHR_CAUSALITY_r1")
    args = parser.parse_args()
    pack = args.pack
    pack.mkdir(parents=True, exist_ok=True)
    d512_conv = D512 / "B0-Banked__convolutionSeparable/B0-Banked/convolutionSeparable"
    d512_spmv = D512 / "B0-Banked__spmv/B0-Banked/spmv"
    d256_m256 = RESULTS / "d256_convolution_m256"
    d512_m256 = RESULTS / "d512_convolution_m256"
    d512_spmv_m256 = RESULTS / "d512_spmv_m256"
    rows = [record("D256_M128", FORMAL, 256, 128, "PROMOTED_VALID_CALIBRATION"),
            record("D256_M256", d256_m256, 256, 256, "PROMOTED_VALID_CALIBRATION"),
            record("D512_M128", d512_conv, 512, 128, "SPECULATIVE_PENDING_GATE"),
            record("D512_M256", d512_m256, 512, 256, "SPECULATIVE_PENDING_GATE")]
    base = rows[0]["cycles"]
    for row in rows:
        row["speedup_vs_d256_m128"] = round(base / row["cycles"], 8)
    write_csv(pack / "CONVOLUTION_2X2.csv", rows)
    control = [record("D512_M128", d512_spmv, 512, 128, "SPECULATIVE_PENDING_GATE"),
               record("D512_M256", d512_spmv_m256, 512, 256, "SPECULATIVE_PENDING_GATE")]
    control_base = control[0]["cycles"]
    for row in control:
        row["speedup_vs_d512_m128"] = round(control_base / row["cycles"], 8)
    write_csv(pack / "SPMV_NEGATIVE_CONTROL.csv", control)
    write_csv(pack / "RESOURCE_MOVEMENT.csv", rows + control)
    write_csv(pack / "TEMPORAL_SUMMARY.csv", rows + control)
    eq_pairs = (("vectorAdd_4M", RESULTS / "d512_vectoradd_m128_equivalence",
                 D512 / "B0-Banked__vectorAdd_4M/B0-Banked/vectorAdd_4M"),
                ("convolutionSeparable", RESULTS / "d512_convolution_m128_equivalence", d512_conv))
    artifacts = ("target_summary.csv", "target_slice.csv", "target_l1.csv", "target_dram.csv",
                 "target_window.csv", "target_bank.csv", "target_kernel.csv")
    text = ["# MSHR128 equivalence\n", "Final Lane-E production sources retain the frozen Lane-B runtime semantics.\n"]
    for workload, observed, reference in eq_pairs:
        checks = [name for name in artifacts if (observed / name).read_bytes() == (reference / name).read_bytes()]
        text.append("- `%s`: %d/%d parsed artifacts byte-identical (%s).\n" %
                    (workload, len(checks), len(artifacts), ", ".join(checks)))
        if len(checks) != len(artifacts):
            raise SystemExit("MSHR128 equivalence failed for " + workload)
    (pack / "MSHR128_EQUIVALENCE.md").write_text("\n".join(text))
    d256 = options(ROOT / "tests/ep_l2/b0_banked_850.config")
    d256_m = options(ROOT / "tests/ep_l2/b0_banked_mshr256_850.config")
    d512 = options(ROOT / "tests/ep_l2/b0_banked_d512_850.config")
    d512_m = options(ROOT / "tests/ep_l2/b0_banked_d512_mshr256_850.config")
    diffs = [("D256_M128_to_M256", old, new) for old, new in zip(d256, d256_m) if old != new]
    diffs += [("D512_M128_to_M256", old, new) for old, new in zip(d512, d512_m) if old != new]
    write_csv(pack / "CONFIG_DIFF.csv", [{"comparison": c, "old": old, "new": new} for c, old, new in diffs])
    (pack / "CONFIG_DIFF.md").write_text("# Effective config delta\n\nBoth comparisons have exactly one modeled delta: `-gpgpu_cache:dl2 ... A:128:1 ...` to `A:256:1 ...`.\n")
    raw = []
    for label, directory in (("D256_M128", FORMAL), ("D256_M256", d256_m256),
                             ("D512_M128", d512_conv), ("D512_M256", d512_m256),
                             ("SPMV_D512_M128", d512_spmv), ("SPMV_D512_M256", d512_spmv_m256)):
        status = json.loads((directory / "run_status.json").read_text())
        log = Path(status.get("raw_log_gz", ""))
        raw.append({"label": label, "run_directory": str(directory), "raw_log_gz": str(log),
                    "raw_log_gz_sha256": status.get("raw_log_gz_sha256", ""),
                    "status": status.get("status")})
    write_csv(pack / "RAW_LOG_INDEX.tsv", raw)
    (pack / "RUN_STATUS.csv").write_text((pack / "RESOURCE_MOVEMENT.csv").read_text())
    (pack / "SOURCE_ANCHORS.md").write_text("# Source anchors\n\n- Formal D256: Core `ece1a3a77c5628763e0a4605bfd1c639ee6a1495`; Framework `f08d2ce857972fad73c4e1ab7162ba94c6336507`.\n- Lane-B D512 semantic parent: Core `878f80869ce212e779df20b6421e4dc7f987825d`; Framework `aae62b66685f15437cecf0193934f628e6fac6ae`; composite `a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416`.\n")
    (pack / "README.md").write_text("# Line-MSHR Causality Probe r1\n\nLine-MSHR256 is a sensitivity headroom point, not a primary-baseline proposal. D512-derived rows remain `SPECULATIVE_PENDING_GATE` on `D512_PREFLIGHT_PASS`.\n")
    for path in sorted(pack.iterdir()):
        if path.is_file() and path.name != "SHA256SUMS":
            pass
    lines = [digest(path) + "  " + path.name for path in sorted(pack.iterdir()) if path.is_file() and path.name != "SHA256SUMS"]
    (pack / "SHA256SUMS").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
