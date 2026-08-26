#!/usr/bin/env python3
"""Create the auditable R/S classification for the V100 extension traces.

The six originally completed extension cases retain their matching 200-cycle
baseline/oracle and 50-cycle baseline evidence.  ColorMax and PageRank use
the later, current-branch classification replays.  This tool refuses to mix
partial or wrongly configured output into the table.
"""

import argparse
import csv
from pathlib import Path


CASES = (
    ("c2p-ispass-bfs", "ISPASS BFS", "legacy"),
    ("c2p-ispass-lib", "ISPASS LIB", "legacy"),
    ("c2p-ispass-lps", "ISPASS LPS", "legacy"),
    ("c2p-ispass-ray", "ISPASS RAY", "legacy"),
    ("c2p-pannotia-color-max", "Pannotia ColorMax", "fresh"),
    ("c2p-pannotia-fw-block", "Pannotia FW-block", "legacy"),
    ("c2p-pannotia-mis", "Pannotia MIS", "legacy"),
    ("c2p-pannotia-pagerank", "Pannotia PageRank", "fresh"),
)


def read_summary(run_dir: Path) -> dict[str, int]:
    summary = run_dir / "summary.txt"
    run_out = run_dir / "run.out"
    if not summary.is_file() or not run_out.is_file():
        raise RuntimeError(f"missing completed output: {run_dir}")
    if "GPGPU-Sim: *** exit detected ***" not in run_out.read_text(
            errors="replace"):
        raise RuntimeError(f"no normal simulator exit: {run_dir}")
    result: dict[str, int] = {}
    for line in summary.read_text().splitlines():
        fields = line.split()
        if len(fields) == 3 and fields[1] == "=":
            try:
                result[fields[0]] = int(fields[2])
            except ValueError:
                pass
    for key in ("gpu_tot_sim_cycle", "c2p_l1_misses", "c2p_oracle_peer_hits"):
        if key not in result:
            raise RuntimeError(f"missing {key}: {run_dir}")
    return result


def check_config(run_dir: Path, expected_l2: int) -> None:
    config = run_dir / "gpgpusim.config"
    if not config.is_file():
        raise RuntimeError(f"missing resolved configuration: {run_dir}")
    values: dict[str, str] = {}
    for line in config.read_text().splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[0] in {
                "-gpgpu_l1_latency", "-gpgpu_l2_rop_latency"}:
            values[fields[0]] = fields[1]
    if values.get("-gpgpu_l1_latency") != "20":
        raise RuntimeError(f"L1 latency is not 20: {run_dir}")
    if values.get("-gpgpu_l2_rop_latency") != str(expected_l2):
        raise RuntimeError(f"L2 latency is not {expected_l2}: {run_dir}")


def run(main_root: Path, fast_root: Path, fresh_root: Path, case: str,
        source: str) -> tuple[dict[str, int], dict[str, int], dict[str, int],
                              tuple[Path, Path, Path]]:
    if source == "legacy":
        baseline = main_root / case / "baseline"
        oracle = main_root / case / "oracle"
        fast = fast_root / case / "baseline"
    else:
        baseline = fresh_root / case / "l2_200" / "baseline"
        oracle = fresh_root / case / "l2_200" / "oracle"
        fast = fresh_root / case / "l2_50" / "baseline"
    for directory in (baseline, oracle):
        check_config(directory, 200)
    check_config(fast, 50)
    return (read_summary(baseline), read_summary(oracle), read_summary(fast),
            (baseline, oracle, fast))


def ratio(numerator: int, denominator: int) -> str:
    return "" if denominator == 0 else f"{numerator / denominator:.6f}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy-main-root", type=Path, required=True)
    parser.add_argument("--legacy-fast-root", type=Path, required=True)
    parser.add_argument("--fresh-root", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()

    rows: list[dict[str, str]] = []
    for case, label, source in CASES:
        baseline, oracle, fast, dirs = run(args.legacy_main_root,
                                           args.legacy_fast_root,
                                           args.fresh_root, case, source)
        base_cycles = baseline["gpu_tot_sim_cycle"]
        oracle_cycles = oracle["gpu_tot_sim_cycle"]
        if oracle_cycles != base_cycles:
            raise RuntimeError(
                f"oracle timing changed baseline for {case}: "
                f"{oracle_cycles} != {base_cycles}")
        misses = oracle["c2p_l1_misses"]
        peers = oracle["c2p_oracle_peer_hits"]
        redundancy = ratio(peers, misses)
        sensitivity = ratio(base_cycles, fast["gpu_tot_sim_cycle"])
        if misses == 0:
            if peers != 0:
                raise RuntimeError(f"impossible zero-miss oracle peer hit: {case}")
            r_class = "R0†"
            r_note = "no eligible L1 misses (0/0), excluded from R-rate means"
        else:
            r_class = "R1" if float(redundancy) >= 0.30 else "R0"
            r_note = ""
        s_class = "S1" if float(sensitivity) >= 1.10 else "S0"
        rows.append({
            "case": case,
            "workload": label,
            "evidence": source,
            "oracle_peer_hits": str(peers),
            "eligible_l1_misses": str(misses),
            "oracle_redundancy": redundancy or "0/0",
            "baseline_l2_200_cycles": str(base_cycles),
            "baseline_l2_50_cycles": str(fast["gpu_tot_sim_cycle"]),
            "l2_sensitivity": sensitivity,
            "classification": f"{r_class}{s_class}",
            "note": r_note,
            "baseline_dir": str(dirs[0]),
            "oracle_dir": str(dirs[1]),
            "l2_50_dir": str(dirs[2]),
        })

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0])
    with args.csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    report = [
        "# V100 extension R/S classification", "",
        "This table completes the paper-style R/S classification for the eight "
        "V100-generated ISPASS/Pannotia extension traces.  It is an extension "
        "dataset, not part of the canonical paper16 aggregate.", "",
        "## Fixed measurement contract", "",
        "- L1 latency is fixed at 20 cycles.",
        "- `R = oracle_peer_hits / eligible_l1_misses` at L2=200; R1 iff "
        "`R >= 0.30`.",
        "- `S = baseline_cycles(L2=200) / baseline_cycles(L2=50)`; because "
        "the trace and instruction count are fixed, this equals "
        "`IPC50 / IPC200`.  S1 iff `S >= 1.10`.",
        "- Every input was checked for normal simulator exit, resolved L1/L2 "
        "latencies, and `oracle_cycles == baseline_cycles`.", "",
        "## Results", "",
        "| Workload | Oracle peer / eligible L1 miss | R | Cycles 200 / 50 | S | Group | Evidence |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        report.append(
            f"| {row['workload']} | {int(row['oracle_peer_hits']):,} / "
            f"{int(row['eligible_l1_misses']):,} | {row['oracle_redundancy']} | "
            f"{int(row['baseline_l2_200_cycles']):,} / "
            f"{int(row['baseline_l2_50_cycles']):,} | {row['l2_sensitivity']} | "
            f"{row['classification']} | {row['evidence']} |")
    report.extend([
        "",
        "`R0†` is deliberate: LIB has no eligible C2P L1 miss, hence no "
        "well-defined redundancy ratio.  It is semantically a no-sharing R0 "
        "case, but must not be silently treated as a numeric zero in a group "
        "mean.", "",
        "The CSV includes the exact three source directories per workload so "
        "the raw counters and resolved configurations remain auditable.", "",
    ])
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text("\n".join(report))


if __name__ == "__main__":
    main()
