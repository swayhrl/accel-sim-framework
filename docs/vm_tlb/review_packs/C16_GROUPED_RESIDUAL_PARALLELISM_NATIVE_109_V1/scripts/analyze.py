#!/usr/bin/env python3
"""Unit-aware lock-free analysis for residual parallelism screen."""

import argparse
import csv
import json
from pathlib import Path
import statistics

MS, SPLITS = (1, 16, 32, 64), (8, 1)
SM_COUNT = 76
METRICS = ("lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum",
           "lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum",
           "l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum",
           "gpu__time_duration.sum", "sm__warps_active.avg.pct_of_peak_sustained_elapsed")
UNIT_SCALE = {"byte": 1.0, "Kbyte": 1e3, "Mbyte": 1e6, "Gbyte": 1e9,
              "sector": 1.0, "ns": 1.0, "us": 1e3, "ms": 1e6, "s": 1e9, "%": 1.0}


def number(value):
    return None if value in (None, "") else float(value.replace(",", ""))


def normalized(value, unit):
    value = number(value)
    if value is None:
        return None
    if unit not in UNIT_SCALE:
        raise RuntimeError(f"unsupported NCU unit {unit!r}")
    return value * UNIT_SCALE[unit]


def read_profile(path):
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        units = next(reader)
        rows = list(reader)
    return units, [r for r in rows if r.get("Kernel Name") and any(number(r.get(m)) is not None for m in METRICS)]


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
    kernel_rows, by_kind, launches, gemm_names = [], {}, {}, set()
    for m in MS:
        for split in SPLITS:
            path = args.raw / f"ncu_M{m}_S{split}.csv"
            units, rows = read_profile(path)
            for order, row in enumerate(rows):
                name = row["Kernel Name"]
                kind = "GEMM" if "gemm_forward_4bit_cuda_m16n128k32" in name else ("REDUCTION" if "reduce" in name else "OTHER")
                vals = [normalized(row.get(metric), units.get(metric)) for metric in METRICS]
                waves = number(row.get("launch__waves_per_multiprocessor"))
                item = (m, split, order, kind, name, row.get("Grid Size", ""), row.get("Block Size", ""), waves, *vals)
                kernel_rows.append(item)
                launches.setdefault((m, split), []).append((kind, name, row.get("Grid Size", ""), row.get("Block Size", "")))
                if kind in ("GEMM", "REDUCTION"):
                    if (m, split, kind) in by_kind:
                        raise RuntimeError(f"multiple {kind} rows in {path}")
                    by_kind[(m, split, kind)] = (waves, *vals)
                if kind == "GEMM":
                    gemm_names.add(name)
            if (m, split, "GEMM") not in by_kind:
                raise RuntimeError(f"missing GEMM row in {path}")
    if len(gemm_names) != 1:
        raise RuntimeError("GEMM kernel identity differs")
    write_tsv(args.out / "NCU_KERNEL_ROWS.tsv",
              ("M", "split", "order", "kind", "kernel_name", "grid", "block", "launch__waves_per_multiprocessor", *METRICS), kernel_rows)

    launch_rows = []
    for m in MS:
        mt = (m + 15) // 16
        for split in SPLITS:
            rows = launches[(m, split)]
            gs, rs = [r for r in rows if r[0] == "GEMM"], [r for r in rows if r[0] == "REDUCTION"]
            grid, red_grid = mt * 96 * split, ((m * 12288 + 511) // 512 if split == 8 else 0)
            passed = len(gs) == 1 and len(rs) == (1 if split == 8 else 0) and gs[0][2].replace(" ", "") == f"({grid},1,1)" and gs[0][3].replace(" ", "") == "(32,2,1)"
            if split == 8:
                passed = passed and rs[0][2].replace(" ", "") == f"({red_grid},1,1)" and rs[0][3].replace(" ", "") == "(32,4,1)"
            if not passed:
                raise RuntimeError(f"launch audit failure M={m} split={split}")
            launch_rows.append((m, split, grid, gs[0][2], gs[0][3], split*m*12288*2, red_grid, passed))
    write_tsv(args.out / "LAUNCH_AUDIT.tsv",
              ("M", "split", "expected_gemm_grid", "observed_gemm_grid", "observed_gemm_block", "scratch_bytes", "expected_reduction_grid", "pass"), launch_rows)

    timing = {}
    with (args.raw / "TIMING_SAMPLES.tsv").open(newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            timing.setdefault((int(row["M"]), int(row["split"])), []).append(float(row["ms"]))
    summary = []
    for m in MS:
        med8 = statistics.median(timing[(m, 8)])
        med1 = statistics.median(timing[(m, 1)])
        g8 = by_kind[(m, 8, "GEMM")]
        g1 = by_kind[(m, 1, "GEMM")]
        red = by_kind[(m, 8, "REDUCTION")]
        # tuple: waves, hit, miss, l1, l2, dram, duration_ns, active_warps_pct
        w8, h8, miss8, _, _, dram8, dur8, active8 = g8
        w1, h1, miss1, _, _, dram1, dur1, active1 = g1
        wr, _, _, _, _, dramr, durr, activer = red
        hf8, hf1 = h8/(h8+miss8), h1/(h1+miss1)
        reduction_fraction = durr / (dur8 + durr)
        summary.append((m, (m+15)//16, (m+15)//16*96, (m+15)//16*768,
                        (m+15)//16*96/SM_COUNT, (m+15)//16*768/SM_COUNT,
                        med8, med1, 1.0-med1/med8, dur8, dur1, dur8/dur1,
                        durr, dramr, reduction_fraction, hf8, hf1, dram8, dram1,
                        dram8/dram1, w8, w1, wr, active8, active1, activer))
    write_tsv(args.out / "RESIDUAL_PARALLELISM_SUMMARY.tsv",
              ("M", "m_tiles", "split1_gemm_cta", "split8_gemm_cta", "split1_cta_per_sm", "split8_cta_per_sm",
               "split8_module_median_ms", "split1_module_median_ms", "split1_relative_gain",
               "split8_gemm_duration_ns", "split1_gemm_duration_ns", "split8_over_split1_gemm_duration",
               "split8_reduction_duration_ns", "split8_reduction_dram_bytes", "split8_reduction_fraction_profile_kernel_time",
               "split8_gemm_hit_fraction", "split1_gemm_hit_fraction", "split8_gemm_dram_bytes", "split1_gemm_dram_bytes",
               "split8_over_split1_gemm_dram", "split8_gemm_launch_waves_per_sm", "split1_gemm_launch_waves_per_sm",
               "reduction_launch_waves_per_sm", "split8_gemm_active_warps_pct_elapsed", "split1_gemm_active_warps_pct_elapsed",
               "reduction_active_warps_pct_elapsed"), summary)
    (args.out / "ANALYSIS_RECEIPT.json").write_text(json.dumps({"status": "PASS", "profiles": 8, "summary_rows": 4}, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
