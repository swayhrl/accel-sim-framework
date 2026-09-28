#!/usr/bin/env python3
"""Lock-free analysis of the bounded timing and eight NCU profiles."""

import argparse
import csv
import json
from pathlib import Path
import statistics

KS = (2560, 3072)
SPLITS = (8, 1)
STATES = ("SHARED", "PER_MTILE")
METRICS = (
    "lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum",
    "lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum",
    "l1tex__t_bytes.sum",
    "lts__t_bytes.sum",
    "dram__bytes.sum",
    "gpu__time_duration.sum",
)


def number(value):
    if value is None or value == "":
        return None
    return float(value.replace(",", ""))


UNIT_SCALE = {
    "byte": 1.0,
    "Kbyte": 1.0e3,
    "Mbyte": 1.0e6,
    "Gbyte": 1.0e9,
    "sector": 1.0,
    "ns": 1.0,
    "us": 1.0e3,
    "ms": 1.0e6,
    "s": 1.0e9,
}


def normalized(value, unit):
    parsed = number(value)
    if parsed is None:
        return None
    if unit not in UNIT_SCALE:
        raise RuntimeError(f"unsupported NCU unit {unit!r}")
    return parsed * UNIT_SCALE[unit]


def read_profile(path):
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        units = next(reader)
        rows = list(reader)
    usable = []
    for row in rows:
        name = row.get("Kernel Name", "")
        if not name or name in ("Kernel Name",):
            continue
        if not any(number(row.get(m)) is not None for m in METRICS):
            continue
        usable.append(row)
    return units, usable


def write_tsv(path, header, rows):
    with path.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    kernel_rows = []
    gemm = {}
    launches = {}
    for k in KS:
        for split in SPLITS:
            for state in STATES:
                path = args.raw / f"ncu_K{k}_S{split}_{state}.csv"
                units, rows = read_profile(path)
                for order, row in enumerate(rows):
                    name = row["Kernel Name"]
                    kind = "GEMM" if "gemm_forward_4bit_cuda_m16n128k32" in name else ("REDUCTION" if "reduce" in name else "OTHER")
                    vals = [normalized(row.get(m), units.get(m)) for m in METRICS]
                    item = (k, split, state, order, kind, name, row.get("Grid Size", ""), row.get("Block Size", ""), *vals)
                    kernel_rows.append(item)
                    if kind == "GEMM":
                        if (k, split, state) in gemm:
                            raise RuntimeError(f"multiple GEMM rows in {path}")
                        gemm[(k, split, state)] = vals
                    launches.setdefault((k, split, state), []).append((kind, name, row.get("Grid Size", ""), row.get("Block Size", "")))
                if (k, split, state) not in gemm:
                    raise RuntimeError(f"missing GEMM row in {path}")
    write_tsv(args.out / "NCU_KERNEL_ROWS.tsv",
              ("K", "split", "state", "order", "kind", "kernel_name", "grid", "block", *METRICS), kernel_rows)

    launch_rows = []
    gemm_names = set()
    for k in KS:
        for split in SPLITS:
            for state in STATES:
                rows = launches[(k, split, state)]
                gemm_rows = [r for r in rows if r[0] == "GEMM"]
                reduction_rows = [r for r in rows if r[0] == "REDUCTION"]
                expected_grid = 49152 if split == 8 else 6144
                expected_reductions = 1 if split == 8 else 0
                passed = (len(gemm_rows) == 1 and len(reduction_rows) == expected_reductions and
                          gemm_rows[0][2].replace(" ", "") == f"({expected_grid},1,1)" and
                          gemm_rows[0][3].replace(" ", "") == "(32,2,1)")
                if split == 8:
                    passed = passed and reduction_rows[0][2].replace(" ", "") == "(24576,1,1)" and reduction_rows[0][3].replace(" ", "") == "(32,4,1)"
                gemm_names.add(gemm_rows[0][1])
                launch_rows.append((k, split, state, expected_grid, gemm_rows[0][2], gemm_rows[0][3],
                                    split * 256 * 49152 * 2, expected_reductions, passed))
                if not passed:
                    raise RuntimeError(f"launch audit failure K={k} split={split} state={state}")
    if len(gemm_names) != 1:
        raise RuntimeError("GEMM kernel identity differs across cells")
    write_tsv(args.out / "LAUNCH_AUDIT.tsv",
              ("K", "split", "state", "expected_gemm_grid", "observed_gemm_grid", "observed_gemm_block",
               "scratch_bytes", "expected_reduction_count", "pass"), launch_rows)

    timing = {}
    with (args.raw / "TIMING_SAMPLES.tsv").open(newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            key = (int(row["K"]), int(row["split"]), row["state"])
            timing.setdefault(key, []).append(float(row["ms"]))

    summary = []
    for k in KS:
        for split in SPLITS:
            sh = gemm[(k, split, "SHARED")]
            pm = gemm[(k, split, "PER_MTILE")]
            sh_hit, sh_miss, _, _, sh_dram, sh_dur = sh
            pm_hit, pm_miss, _, _, pm_dram, pm_dur = pm
            sh_frac = sh_hit / (sh_hit + sh_miss)
            pm_frac = pm_hit / (pm_hit + pm_miss)
            sh_med = statistics.median(timing[(k, split, "SHARED")])
            pm_med = statistics.median(timing[(k, split, "PER_MTILE")])
            summary.append((k, split, sh_frac, pm_frac, (sh_frac - pm_frac) * 100.0,
                            sh_miss, pm_miss, sh_dram, pm_dram, pm_dram / sh_dram,
                            sh_dur, pm_dur, sh_med, pm_med, pm_med / sh_med))
    write_tsv(args.out / "REUSE_CAUSAL_SUMMARY.tsv",
              ("K", "split", "shared_hit_fraction", "per_mtile_hit_fraction", "delta_hit_pp_shared_minus_per",
               "shared_miss_sectors", "per_mtile_miss_sectors", "shared_dram_bytes", "per_mtile_dram_bytes",
               "dram_ratio_per_over_shared", "shared_gemm_duration_ns", "per_mtile_gemm_duration_ns",
               "shared_median_ms", "per_mtile_median_ms", "timing_ratio_per_over_shared"), summary)
    result = {"status": "PASS", "rows": len(summary), "profiles": 8}
    (args.out / "ANALYSIS_RECEIPT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
