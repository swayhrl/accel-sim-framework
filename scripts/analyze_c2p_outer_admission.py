#!/usr/bin/env python3
"""Validate and summarize canonical C2P versus outer-admission replays."""

import argparse
import csv
import re
from pathlib import Path


NUMBER_RE = re.compile(r"^\s*([A-Za-z0-9_]+) = ([0-9]+)$")
REQUIRED = (
    "gpu_tot_sim_cycle",
    "c2p_peer_probes",
    "c2p_remote_hits",
    "c2p_l2_requests_avoided",
)
POLICY_REQUIRED = REQUIRED + (
    "c2p_outer_admission_policy",
    "c2p_outer_admission_opportunities",
    "c2p_outer_admission_continue_predictor",
    "c2p_outer_admission_continue_exploration",
    "c2p_outer_admission_bypass_predictor",
    "c2p_outer_admission_train_hit",
    "c2p_outer_admission_train_no_hit",
)


def read_values(path: Path):
    values = {}
    for line in path.read_text(errors="replace").splitlines():
        match = NUMBER_RE.match(line)
        if match:
            values[match.group(1)] = int(match.group(2))
    return values


def values_for(root: Path, case: str, variant: str):
    path = root / case / variant / "c2p" / "run.out"
    if not path.is_file():
        raise FileNotFoundError(path)
    values = read_values(path)
    return values, path


def need(values, keys):
    return [key for key in keys if key not in values]


def percent(numerator, denominator):
    return "" if denominator == 0 else f"{100.0 * numerator / denominator:.2f}%"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path,
                        help="root/<case>/{control,policy}/c2p/run.out")
    parser.add_argument("--case", required=True,
                        help="comma-separated case names")
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()

    rows, failures = [], []
    for case in filter(None, args.case.split(",")):
        try:
            control, control_path = values_for(args.root, case, "control")
            policy, policy_path = values_for(args.root, case, "policy")
        except FileNotFoundError as error:
            failures.append(f"{case}: missing input ({error})")
            continue
        missing = need(control, REQUIRED) + need(policy, POLICY_REQUIRED)
        if missing:
            failures.append(f"{case}: missing counters ({', '.join(sorted(set(missing)))})")
            continue

        if policy["c2p_outer_admission_policy"] != 1:
            failures.append(f"{case}: policy replay did not enable outer admission")
        if policy["c2p_remote_hits"] != policy["c2p_l2_requests_avoided"]:
            failures.append(f"{case}: policy remote-hit/L2-avoidance invariant failed")

        opportunities = policy["c2p_outer_admission_opportunities"]
        continued = (policy["c2p_outer_admission_continue_predictor"] +
                     policy["c2p_outer_admission_continue_exploration"])
        bypassed = policy["c2p_outer_admission_bypass_predictor"]
        trained = (policy["c2p_outer_admission_train_hit"] +
                   policy["c2p_outer_admission_train_no_hit"])
        if continued + bypassed != opportunities:
            failures.append(
                f"{case}: decision partition {continued} + {bypassed} != {opportunities}")
        if trained > continued:
            failures.append(f"{case}: {trained} trained packages exceed {continued} continuations")

        rows.append({
            "case": case,
            "control_cycles": control["gpu_tot_sim_cycle"],
            "policy_cycles": policy["gpu_tot_sim_cycle"],
            "cycle_delta_pct": percent(
                policy["gpu_tot_sim_cycle"] - control["gpu_tot_sim_cycle"],
                control["gpu_tot_sim_cycle"]),
            "control_probes": control["c2p_peer_probes"],
            "policy_probes": policy["c2p_peer_probes"],
            "probe_delta_pct": percent(
                policy["c2p_peer_probes"] - control["c2p_peer_probes"],
                control["c2p_peer_probes"]),
            "control_remote_hits": control["c2p_remote_hits"],
            "policy_remote_hits": policy["c2p_remote_hits"],
            "outer_opportunities": opportunities,
            "outer_continue_predictor": policy["c2p_outer_admission_continue_predictor"],
            "outer_continue_exploration": policy["c2p_outer_admission_continue_exploration"],
            "outer_bypass_predictor": bypassed,
            "outer_bypass_share": percent(bypassed, opportunities),
            "outer_train_hit": policy["c2p_outer_admission_train_hit"],
            "outer_train_no_hit": policy["c2p_outer_admission_train_no_hit"],
            "control_run": str(control_path.parent),
            "policy_run": str(policy_path.parent),
        })

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["case"]
    with args.csv.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# C2P outer-admission result",
        "",
        "Each policy replay retains canonical C2P for requests with a local "
        "candidate.  Only an outer-only Snapshot candidate list can be admitted "
        "to probes or bypassed directly into the ordinary lower path.",
        "",
        "| Case | Canonical cycles | Policy cycles | Cycle delta | Canonical / policy probes | "
        "Canonical / policy remote hits | Outer opportunities | Bypass share |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['case']} | {row['control_cycles']} | {row['policy_cycles']} | "
            f"{row['cycle_delta_pct']} | {row['control_probes']} / {row['policy_probes']} | "
            f"{row['control_remote_hits']} / {row['policy_remote_hits']} | "
            f"{row['outer_opportunities']} | {row['outer_bypass_share']} |")
    if failures:
        lines += ["", "## Validation failures", ""]
        lines += [f"- {failure}" for failure in failures]
    else:
        lines += ["", "All decision-partition and remote-hit/L2-avoidance invariants passed."]
    args.markdown.write_text("\n".join(lines) + "\n")
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
