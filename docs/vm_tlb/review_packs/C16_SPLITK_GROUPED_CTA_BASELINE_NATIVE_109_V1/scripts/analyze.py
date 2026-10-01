#!/usr/bin/env python3
"""Lock-free unit-aware analysis for the grouped CTA baseline."""

import argparse
import csv
import json
from pathlib import Path
import statistics

KS, SPLITS, MAPPINGS = (3072, 4096), (8, 1), ("ROW", "GROUP_M16")
METRICS = ("lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum",
           "lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum",
           "l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum",
           "gpu__time_duration.sum")
HISTORY = {
    (3072, 8): (1.6383999586105347, 0.002174999655371307),
    (3072, 1): (1.3527040481567383, 0.0032029844064300375),
    (4096, 8): (1.9263359904289246, 0.00932058841235311),
    (4096, 1): (1.9341440200805664, 0.004419914886562949),
}
UNIT_SCALE = {"byte": 1.0, "Kbyte": 1e3, "Mbyte": 1e6, "Gbyte": 1e9,
              "sector": 1.0, "ns": 1.0, "us": 1e3, "ms": 1e6, "s": 1e9}


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
    kernel_rows, gemm, launches, gemm_names = [], {}, {}, set()
    for k in KS:
        for split in SPLITS:
            for mapping in MAPPINGS:
                path = args.raw / f"ncu_K{k}_S{split}_{mapping}.csv"
                units, rows = read_profile(path)
                for order, row in enumerate(rows):
                    name = row["Kernel Name"]
                    kind = "GEMM" if "gemm_forward_4bit_cuda_m16n128k32" in name else ("REDUCTION" if "reduce" in name else "OTHER")
                    vals = [normalized(row.get(m), units.get(m)) for m in METRICS]
                    kernel_rows.append((k, split, mapping, order, kind, name, row.get("Grid Size", ""), row.get("Block Size", ""), *vals))
                    launches.setdefault((k, split, mapping), []).append((kind, name, row.get("Grid Size", ""), row.get("Block Size", "")))
                    if kind == "GEMM":
                        if (k, split, mapping) in gemm:
                            raise RuntimeError(f"multiple GEMM rows in {path}")
                        gemm[(k, split, mapping)] = vals
                        gemm_names.add(name)
                if (k, split, mapping) not in gemm:
                    raise RuntimeError(f"missing GEMM row in {path}")
    if len(gemm_names) != 1:
        raise RuntimeError("GEMM kernel identity differs across cells")
    write_tsv(args.out / "NCU_KERNEL_ROWS.tsv",
              ("K", "split", "mapping", "order", "kind", "kernel_name", "grid", "block", *METRICS), kernel_rows)

    launch_rows = []
    for key, rows in launches.items():
        k, split, mapping = key
        gs = [r for r in rows if r[0] == "GEMM"]
        rs = [r for r in rows if r[0] == "REDUCTION"]
        grid = 49152 if split == 8 else 6144
        reductions = 1 if split == 8 else 0
        passed = len(gs) == 1 and len(rs) == reductions and gs[0][2].replace(" ", "") == f"({grid},1,1)" and gs[0][3].replace(" ", "") == "(32,2,1)"
        if split == 8:
            passed = passed and rs[0][2].replace(" ", "") == "(24576,1,1)" and rs[0][3].replace(" ", "") == "(32,4,1)"
        if not passed:
            raise RuntimeError(f"launch audit failure {key}")
        launch_rows.append((k, split, mapping, grid, gs[0][2], gs[0][3], split * 256 * 49152 * 2, reductions, passed))
    write_tsv(args.out / "LAUNCH_AUDIT.tsv",
              ("K", "split", "mapping", "expected_gemm_grid", "observed_gemm_grid", "observed_gemm_block", "scratch_bytes", "expected_reduction_count", "pass"), launch_rows)

    timing = {}
    with (args.raw / "TIMING_SAMPLES.tsv").open(newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            timing.setdefault((int(row["K"]), int(row["split"]), row["mapping"]), []).append(float(row["ms"]))

    calibration, causal, grouped_compare = [], [], []
    material = False
    for k in KS:
        for split in SPLITS:
            row_vals, group_vals = timing[(k, split, "ROW")], timing[(k, split, "GROUP_M16")]
            row_med, group_med = statistics.median(row_vals), statistics.median(group_vals)
            row_cv = statistics.pstdev(row_vals) / statistics.mean(row_vals)
            hist_med, hist_cv = HISTORY[(k, split)]
            rel = abs(row_med / hist_med - 1.0)
            bad = rel > 0.05 and rel > hist_cv and rel > row_cv
            material = material or bad
            calibration.append((k, split, hist_med, hist_cv, row_med, row_cv, rel, bad,
                                "ROW_PATCH_OVERHEAD_MATERIAL" if bad else "PASS"))
            rv, gv = gemm[(k, split, "ROW")], gemm[(k, split, "GROUP_M16")]
            rh, rm, _, _, rd, rdur = rv
            gh, gm, _, _, gd, gdur = gv
            rf, gf = rh / (rh + rm), gh / (gh + gm)
            causal.append((k, split, rf, gf, (gf-rf)*100, rm, gm, rd, gd, gd/rd,
                           rdur, gdur, row_med, group_med, group_med/row_med))
        a, b = gemm[(k, 8, "GROUP_M16")], gemm[(k, 1, "GROUP_M16")]
        ah, am, _, _, ad, _ = a
        bh, bm, _, _, bd, _ = b
        at = statistics.median(timing[(k, 8, "GROUP_M16")])
        bt = statistics.median(timing[(k, 1, "GROUP_M16")])
        grouped_compare.append((k, ah/(ah+am), bh/(bh+bm), ad, bd, bd/ad, at, bt, (at-bt)/at*100.0, at/bt))
    write_tsv(args.out / "ROW_CALIBRATION.tsv",
              ("K", "split", "historical_median_ms", "historical_cv", "row_median_ms", "row_cv", "absolute_relative_delta", "material", "decision"), calibration)
    write_tsv(args.out / "GROUPED_BASELINE_SUMMARY.tsv",
              ("K", "split", "row_hit_fraction", "grouped_hit_fraction", "grouped_minus_row_hit_pp", "row_miss_sectors", "grouped_miss_sectors", "row_dram_bytes", "grouped_dram_bytes", "dram_ratio_grouped_over_row", "row_gemm_duration_ns", "grouped_gemm_duration_ns", "row_median_ms", "grouped_median_ms", "timing_ratio_grouped_over_row"), causal)
    write_tsv(args.out / "GROUPED_SPLIT_COMPARISON.tsv",
              ("K", "split8_hit_fraction", "split1_hit_fraction", "split8_dram_bytes", "split1_dram_bytes", "split1_over_split8_dram", "split8_median_ms", "split1_median_ms", "split1_timing_gain_percent", "split8_over_split1_time"), grouped_compare)
    (args.out / "ANALYSIS_RECEIPT.json").write_text(json.dumps({"status": "ROW_PATCH_OVERHEAD_MATERIAL" if material else "PASS", "profiles": 8, "summary_rows": 4}, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
