#!/usr/bin/env python3
"""Compare literal-16KiB and primary-64KiB R/S classifications.

This tool is deliberately classification-only.  It validates the new 16KiB
baseline/oracle/L2=50 replay contract, joins it with already audited 64KiB
results, and scores agreement with the paper Figure-10 labels only on the
canonical 16-workload intersection.  The eight V100 extension traces remain
visible as diagnostics but are never counted as paper-label matches.
"""

import argparse
import csv
from pathlib import Path


L1_16_GEOMETRY = "S:4:128:32,L:T:m:L:L,A:512:8,16:0,32"
REQUIRED = ("gpu_tot_sim_cycle", "c2p_l1_misses", "c2p_oracle_peer_hits")


def read_tsv(path: Path):
    with path.open(newline="") as stream:
        rows = (line for line in stream if not line.startswith("#"))
        return list(csv.DictReader(rows, delimiter="\t"))


def read_csv(path: Path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def summary(run_dir: Path):
    summary_path = run_dir / "summary.txt"
    run_out = run_dir / "run.out"
    if not summary_path.is_file() or not run_out.is_file():
        raise RuntimeError(f"missing completed output: {run_dir}")
    if "GPGPU-Sim: *** exit detected ***" not in run_out.read_text(errors="replace"):
        raise RuntimeError(f"no normal simulator exit: {run_dir}")
    values = {}
    for line in summary_path.read_text().splitlines():
        fields = line.split()
        if len(fields) == 3 and fields[1] == "=":
            try:
                values[fields[0]] = int(fields[2])
            except ValueError:
                pass
    missing = [key for key in REQUIRED if key not in values]
    if missing:
        raise RuntimeError(f"missing {', '.join(missing)}: {run_dir}")
    return values


def options(run_dir: Path):
    path = run_dir / "gpgpusim.config"
    if not path.is_file():
        raise RuntimeError(f"missing resolved configuration: {run_dir}")
    result = {}
    for raw in path.read_text().splitlines():
        fields = raw.split()
        if len(fields) >= 2 and fields[0].startswith("-"):
            result[fields[0]] = " ".join(fields[1:])
    return result


def check_run(run_dir: Path, l2_latency: int):
    config = options(run_dir)
    if config.get("-gpgpu_cache:dl1") != L1_16_GEOMETRY:
        raise RuntimeError(
            f"unexpected 16KiB dl1 geometry in {run_dir}: "
            f"{config.get('-gpgpu_cache:dl1')}")
    if config.get("-gpgpu_l1_latency") != "20":
        raise RuntimeError(f"L1 latency is not 20 in {run_dir}")
    if config.get("-gpgpu_l2_rop_latency") != str(l2_latency):
        raise RuntimeError(f"L2 latency is not {l2_latency} in {run_dir}")
    return summary(run_dir)


def ratio(numerator: int, denominator: int):
    return None if denominator == 0 else numerator / denominator


def classify(redundancy, sensitivity, misses):
    r = "R0†" if misses == 0 else ("R1" if redundancy >= 0.30 else "R0")
    s = "S1" if sensitivity >= 1.10 else "S0"
    return r + s


def match(classification: str, paper: str):
    if not paper:
        return ""
    r = classification.replace("†", "")
    return "yes" if r == paper else "no"


def load_64(paper16_csv: Path, extension_csv: Path):
    result = {}
    for row in read_csv(paper16_csv):
        if row.get("mode") != "baseline":
            continue
        # The case table holds R/S once per case; use it below instead.
    for row in read_csv(paper16_csv.with_name("paper16_cases.csv")):
        result[row["case"]] = {
            "redundancy": float(row["oracle_redundancy"]),
            "sensitivity": float(row["l2_sensitivity"]),
            "classification": row["group"],
        }
    for row in read_csv(extension_csv):
        result[row["case"]] = {
            "redundancy": None if row["oracle_redundancy"] == "0/0"
            else float(row["oracle_redundancy"]),
            "sensitivity": float(row["l2_sensitivity"]),
            "classification": row["classification"],
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--l1-16-root", required=True, type=Path)
    parser.add_argument("--l1-64-paper16-csv", required=True, type=Path)
    parser.add_argument("--l1-64-extension-csv", required=True, type=Path)
    parser.add_argument("--manifest", type=Path,
                        default=Path(__file__).resolve().parents[1] /
                        "configs/c2p-cache/rs_l1_capacity_workloads.tsv")
    parser.add_argument("--paper-groups", type=Path,
                        default=Path(__file__).resolve().parents[1] /
                        "configs/c2p-cache/paper16_paper_groups.tsv")
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()

    manifest = read_tsv(args.manifest)
    paper_groups = {row["case"]: row["paper_group"]
                    for row in read_tsv(args.paper_groups)}
    l1_64 = load_64(args.l1_64_paper16_csv, args.l1_64_extension_csv)
    rows = []
    for item in manifest:
        case = item["case"]
        root = args.l1_16_root / case
        baseline = check_run(root / "l2_200" / "baseline", 200)
        oracle = check_run(root / "l2_200" / "oracle", 200)
        fast = check_run(root / "l2_50" / "baseline", 50)
        if baseline["gpu_tot_sim_cycle"] != oracle["gpu_tot_sim_cycle"]:
            raise RuntimeError(f"oracle timing changed baseline: {case}")
        misses = oracle["c2p_l1_misses"]
        peers = oracle["c2p_oracle_peer_hits"]
        if misses == 0 and peers:
            raise RuntimeError(f"impossible zero-miss peer hit: {case}")
        redundancy = ratio(peers, misses)
        sensitivity = baseline["gpu_tot_sim_cycle"] / fast["gpu_tot_sim_cycle"]
        group16 = classify(redundancy or 0.0, sensitivity, misses)
        old = l1_64.get(case)
        if old is None:
            raise RuntimeError(f"missing audited 64KiB classification: {case}")
        paper = paper_groups.get(case, "")
        rows.append({
            "case": case,
            "suite": item["suite"],
            "paper_group": paper,
            "l1_64_R": "0/0" if old["redundancy"] is None else f"{old['redundancy']:.6f}",
            "l1_64_S": f"{old['sensitivity']:.6f}",
            "l1_64_group": old["classification"],
            "l1_64_paper_match": match(old["classification"], paper),
            "l1_16_peer_hits": str(peers),
            "l1_16_eligible_l1_misses": str(misses),
            "l1_16_R": "0/0" if redundancy is None else f"{redundancy:.6f}",
            "l1_16_S": f"{sensitivity:.6f}",
            "l1_16_group": group16,
            "l1_16_paper_match": match(group16, paper),
            "l1_16_baseline_cycles": str(baseline["gpu_tot_sim_cycle"]),
            "l1_16_l2_50_cycles": str(fast["gpu_tot_sim_cycle"]),
            "baseline_dir": str(root / "l2_200" / "baseline"),
            "oracle_dir": str(root / "l2_200" / "oracle"),
            "l2_50_dir": str(root / "l2_50" / "baseline"),
        })

    canonical = [row for row in rows if row["paper_group"]]
    score64 = sum(row["l1_64_paper_match"] == "yes" for row in canonical)
    score16 = sum(row["l1_16_paper_match"] == "yes" for row in canonical)
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    report = [
        "# Table-1 L1-capacity R/S cross-validation", "",
        "This is a classification-only ambiguity check.  The primary paper "
        "point remains 64KiB (`16 set × 32 way × 128B`); the alternate point "
        "is the literal Table-1 geometry 16KiB (`4 × 32 × 128B`).  Both use "
        "the same trace, 20-cycle L1, 200/50-cycle L2 comparison, and "
        "observational oracle.  No C2P/ATA/CCD/RING performance result is "
        "changed by this experiment.", "",
        "## Contract and checks", "",
        "- `R = oracle_peer_hits / eligible_l1_misses` at L2=200; R1 iff `R >= 0.30`.",
        "- `S = baseline_cycles(L2=200) / baseline_cycles(L2=50)`; S1 iff `S >= 1.10`.",
        "- Every 16KiB replay verified normal exit, `dl1=S:4:128:32`, L1=20, "
        "the requested L2 latency, and `oracle_cycles == baseline_cycles`.",
        "- Only the canonical 16 rows have a published Figure-10 group and "
        "contribute to the match score.  The eight extension traces are "
        "diagnostic only.", "",
        "## Paper-label agreement", "",
        f"- 64KiB primary interpretation: **{score64}/{len(canonical)}** exact group matches.",
        f"- 16KiB literal interpretation: **{score16}/{len(canonical)}** exact group matches.",
        "- This score is evidence about the Table-1 ambiguity, not proof of "
        "the authors' unpublished resolved configuration: trace inputs, model "
        "version, mapping, and other parameters can also move a threshold.", "",
        "## Per-workload result", "",
        "| Workload | Paper | 64KiB R/S/group | 64 match | 16KiB R/S/group | 16 match |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        report.append(
            f"| {row['case']} | {row['paper_group'] or 'extension'} | "
            f"{row['l1_64_R']} / {row['l1_64_S']} / {row['l1_64_group']} | "
            f"{row['l1_64_paper_match'] or '—'} | "
            f"{row['l1_16_R']} / {row['l1_16_S']} / {row['l1_16_group']} | "
            f"{row['l1_16_paper_match'] or '—'} |")
    report.extend(["", "The CSV records source run directories and raw 16KiB "
                   "counters for audit.", ""])
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text("\n".join(report))


if __name__ == "__main__":
    main()
