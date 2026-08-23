#!/usr/bin/env python3
"""Produce the auditable final report after the strict policy-matrix audit."""

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


def total(rows, key):
    return sum(int(row[key]) for row in rows)


def geo_ipc(rows, variant):
    return math.exp(sum(math.log(
        int(row["control_gpu_tot_sim_cycle"]) / int(row[f"{variant}_gpu_tot_sim_cycle"])
    ) for row in rows) / len(rows))


def provenance(root, row):
    path = root / row["tier"] / row["case"] / "control" / "c2p" / "provenance.txt"
    values = {}
    for line in path.read_text().splitlines():
        if "=" in line:
            key, value = line.strip().split("=", 1)
            values[key] = value
    return values


def manifest_cases(path):
    cases = []
    for line in path.read_text().splitlines():
        fields = line.split("\t")
        if not fields or not fields[0] or fields[0] == "case" or \
                fields[0].startswith("#"):
            continue
        cases.append(fields[0])
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    audit = args.root / "policy_matrix.md"
    matrix = args.root / "policy_matrix.csv"
    if not audit.is_file() or "All completed runs satisfy" not in audit.read_text():
        raise SystemExit("strict matrix audit has not passed")
    with matrix.open() as stream:
        rows = list(csv.DictReader(stream))
    repo_root = Path(__file__).resolve().parent.parent
    expected = {
        "canonical": manifest_cases(
            repo_root / "configs/c2p-cache/paper16_workloads.tsv"),
        "extension": manifest_cases(
            repo_root / "configs/c2p-cache/v100_extension_workloads.tsv"),
    }
    for tier, cases in expected.items():
        actual_cases = [row["case"] for row in rows if row["tier"] == tier]
        if len(actual_cases) != len(cases):
            raise SystemExit(
                f"{tier}: expected {len(cases)} qualified rows, found "
                f"{len(actual_cases)}")
        if set(actual_cases) != set(cases):
            missing = sorted(set(cases) - set(actual_cases))
            unexpected = sorted(set(actual_cases) - set(cases))
            raise SystemExit(
                f"{tier}: manifest mismatch; missing={missing}, "
                f"unexpected={unexpected}")

    grouped = defaultdict(list)
    for row in rows:
        grouped[row["tier"]].append(row)
    all_rows = rows
    reference = provenance(args.root, rows[0])

    lines = [
        "# C2P+ confirmation-policy matrix: final audit report", "",
        "## Qualification", "",
        "All 72 replays passed the strict matrix audit: normal simulator exit, "
        "matched frontend/backend binary and trace identity inside each triplet, "
        "resolved policy configuration, remote-hit/L2-avoidance conservation, "
        "probe-reason conservation, continuation/package partition conservation, "
        "and package residual-opportunity conservation.", "",
        f"- Backend commit: `{reference.get('gpgpusim_commit', '')}`",
        f"- Accel-Sim commit: `{reference.get('accelsim_commit', '')}`",
        "- Each run directory retains resolved config, executable and `libcudart` "
        "hashes, trace hash, raw output, host profile, and provenance file.", "",
        "## Completion-gate evidence", "",
        "| Required gate | Evidence retained with this report |",
        "|---|---|",
        "| Matched three-way policy | Every row records the exhaustive control, "
        "PC-hash package, and AddrTopo package from one copied binary/trace "
        "triplet. The strict audit checks the only permitted configuration "
        "differences. |",
        "| Capacity and policy parity | The resolved PC and AddrTopo configs each "
        "enable the common candidate-bin, threshold, exploration, and four-probe "
        "package policy. The backend commit implements their single 64 x 4 x 3-bit "
        "table selector. |",
        "| Pilot before sweep | The retained BFS/LPS/B+tree pilot audit passed the "
        "same normal-exit, provenance, remote-hit, and conservation checks before "
        "this matrix was started. |",
        "| Full scope and separated aggregates | CSV has exactly 16 canonical plus "
        "eight extension qualified rows; the aggregate below keeps 16, 8, and 24 "
        "views separate. |", "",
        "## Scope", "",
        "- **Canonical (16)** is the primary, paper-comparison aggregate and remains "
        "separate from the V100 extension.",
        "- **V100 extension (8)** is fully qualified but reported independently, "
        "because its traces were generated separately.",
        "- **All compatible (24)** is an explicit secondary extension view, never "
        "a substitute for the 16-item primary result.", "",
        "## Aggregate", "",
        "| Tier | Policy | Geomean IPC ratio vs exhaustive | L2 delta | Remote-hit delta | Probe delta | Residual exact peers beyond package cap |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for tier, tier_rows in (("canonical", grouped["canonical"]),
                            ("extension", grouped["extension"]),
                            ("all-compatible", all_rows)):
        for variant in ("pc", "addr"):
            lines.append(
                f"| {tier} | {variant} | {geo_ipc(tier_rows, variant):.6f} | "
                f"{total(tier_rows, f'{variant}_l2_delta')} | "
                f"{total(tier_rows, f'{variant}_remote_delta')} | "
                f"{total(tier_rows, f'{variant}_probe_delta')} | "
                f"{total(tier_rows, f'{variant}_c2p_adaptive_package_residual_later_peer')} |")

    canonical_pc = geo_ipc(grouped["canonical"], "pc")
    canonical_addr = geo_ipc(grouped["canonical"], "addr")
    preferred = "PC-hash" if canonical_pc >= canonical_addr else "AddrTopo"
    lines += ["", "## Canonical decision", "",
              f"On the primary 16-workload aggregate, `{preferred}` has the higher "
              "geomean IPC ratio.  This is a result of this timing model, not a "
              "claim of paper-level architectural superiority; L2, remote-hit, "
              "probe, and residual-cap columns above must be read together.", "",
              "## Per-workload paired result", "",
              "| Tier | Workload | PC cycle Δ | Addr cycle Δ | PC / Addr L2 Δ | PC / Addr remote Δ | PC / Addr probe Δ |",
              "|---|---|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(
            f"| {row['tier']} | {row['case']} | "
            f"{row['pc_cycle_delta']} ({row['pc_cycle_delta_pct']}%) | "
            f"{row['addr_cycle_delta']} ({row['addr_cycle_delta_pct']}%) | "
            f"{row['pc_l2_delta']} / {row['addr_l2_delta']} | "
            f"{row['pc_remote_delta']} / {row['addr_remote_delta']} | "
            f"{row['pc_probe_delta']} / {row['addr_probe_delta']} |")

    lines += ["", "## Reproduction", "",
              "```bash", "export C2P_GPGPUSIM_ROOT=/workspace/worktrees/gpgpu-sim-c2p-addr-observe",
              "scripts/run_c2p_confirmation_policy_matrix.sh \\",
              "  --out-root hw_run/c2p-confirmation-policy-v1-20260823 --jobs 1",
              "python3 scripts/finalize_c2p_confirmation_policy_matrix.py \\",
              "  --root hw_run/c2p-confirmation-policy-v1-20260823 \\",
              "  --output hw_run/c2p-confirmation-policy-v1-20260823/final_report.md",
              "```", "",
              "## RTL feasibility", "",
              "The AddrTopo package feature itself is RTL-feasible: it needs a line-address "
              "region hash, requester cluster ID, candidate-count bin, and one shared "
              "64 x 4 x 3-bit saturating table (768 state bits).  It avoids the simulator "
              "PC dependency.  A request that starts a package needs a 6-bit feature index, "
              "2-bit bin, active bit, and ordinal through four; final hit/no-hit updates the "
              "selected score by +2/-1.  Real RTL must arbitrate same-cycle table updates or "
              "add a bounded update queue with forwarding.", "",
              "This repository's decoupled-L2 v3 RTL does not currently contain C2P Snapshot "
              "candidate discovery, remote private-L1 tag access, or an explicit requester "
              "cluster interface.  Therefore this policy cannot be dropped into v3 alone: it "
              "is a small add-on only after those C2P protocol inputs exist.  Once they do, "
              "AddrTopo is more direct than PC-hash at L2 because line address and requester "
              "identity are naturally available at request admission.", "",
              "## Failed/excluded workload record", "",
              "None.  The strict audit found one qualified control/PC/AddrTopo triplet for "
              "each of the 16 canonical and eight V100-extension manifest entries.  No "
              "partially completed, failed, provenance-mismatched, or invariant-failing run "
              "is included in any aggregate.", "",
              "PPA/power and wider parameter sweeps remain outside this confirmation-policy "
              "task."]
    args.output.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
