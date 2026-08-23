#!/usr/bin/env python3
"""Strict audit for exhaustive, PC-hash, and AddrTopo C2P+ replays."""

import argparse
import csv
import math
import re
from pathlib import Path


VARIANTS = ("control", "pc", "addr")
TIERS = ("canonical", "extension")
BASE_FIELDS = (
    "gpu_tot_sim_cycle", "l2_total_cache_accesses", "c2p_remote_hits",
    "c2p_l2_requests_avoided", "c2p_peer_probes", "c2p_peer_probe_hits",
    "c2p_peer_probe_misses",
)
PACKAGE_FIELDS = (
    "c2p_adaptive_package_opportunities",
    "c2p_adaptive_package_start_predictor",
    "c2p_adaptive_package_start_exploration",
    "c2p_adaptive_package_start_forced",
    "c2p_adaptive_package_stop_predictor",
    "c2p_adaptive_package_hit", "c2p_adaptive_package_no_hit",
    "c2p_adaptive_package_timeout",
    "c2p_adaptive_package_residual_opportunities",
    "c2p_adaptive_package_residual_later_peer",
    "c2p_adaptive_package_residual_no_later_peer",
    "c2p_adaptive_package_residual_remaining_candidates",
    "c2p_adaptive_package_residual_next_peer_distance_total",
)
REASON_FIELDS = (
    "c2p_adaptive_first_probe_hits", "c2p_adaptive_first_probe_misses",
    "c2p_adaptive_first_probe_timeouts",
    "c2p_adaptive_predictor_probe_hits",
    "c2p_adaptive_predictor_probe_misses",
    "c2p_adaptive_predictor_probe_timeouts",
    "c2p_adaptive_exploration_probe_hits",
    "c2p_adaptive_exploration_probe_misses",
    "c2p_adaptive_exploration_probe_timeouts",
    "c2p_adaptive_forced_probe_hits",
    "c2p_adaptive_forced_probe_misses",
    "c2p_adaptive_forced_probe_timeouts",
)
STAT_RE = re.compile(r"^\s*((?:c2p_[A-Za-z0-9_]+)|gpu_tot_sim_cycle|l2_total_cache_accesses) = (\d+)$")


def read_values(summary):
    values = {}
    for path in (summary, summary.parent / "run.out"):
        if not path.is_file():
            continue
        for line in path.read_text(errors="replace").splitlines():
            match = STAT_RE.match(line)
            if match:
                values[match.group(1)] = int(match.group(2))
    return values


def read_key_values(path):
    values = {}
    if not path.is_file():
        return values
    for line in path.read_text(errors="replace").splitlines():
        if "=" in line:
            key, value = line.strip().split("=", 1)
            values[key.strip()] = value.strip()
    return values


def config_options(path):
    values = {}
    for line in path.read_text(errors="replace").splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[0].startswith("-c2p_cache_"):
            values[fields[0]] = fields[1]
    return values


def percentage(delta, baseline):
    return "" if not baseline else f"{100 * delta / baseline:.3f}"


def require(values, fields, label, failures):
    missing = [field for field in fields if field not in values]
    if missing:
        failures.append(f"{label}: missing {', '.join(missing)}")
        return False
    return True


def audit_policy(values, label, failures):
    if not require(values, BASE_FIELDS + PACKAGE_FIELDS + REASON_FIELDS + (
            "c2p_adaptive_continuation_opportunities",
            "c2p_adaptive_continue_predictor",
            "c2p_adaptive_continue_exploration",
            "c2p_adaptive_continue_forced",
            "c2p_adaptive_stop_predictor", "c2p_adaptive_stop_hard_cap",
            "c2p_adaptive_stop_later_peer", "c2p_adaptive_stop_no_later_peer"),
                   label, failures):
        return
    if values["c2p_remote_hits"] != values["c2p_l2_requests_avoided"]:
        failures.append(f"{label}: remote hits != L2 avoided")
    if sum(values[field] for field in REASON_FIELDS) != values["c2p_peer_probes"]:
        failures.append(f"{label}: probe-reason partition != peer probes")
    continuations = (values["c2p_adaptive_continue_predictor"] +
                     values["c2p_adaptive_continue_exploration"] +
                     values["c2p_adaptive_continue_forced"] +
                     values["c2p_adaptive_stop_predictor"])
    if continuations != values["c2p_adaptive_continuation_opportunities"]:
        failures.append(f"{label}: continuation decision partition failure")
    package_starts = (values["c2p_adaptive_package_start_predictor"] +
                      values["c2p_adaptive_package_start_exploration"] +
                      values["c2p_adaptive_package_start_forced"])
    package_decisions = package_starts + values["c2p_adaptive_package_stop_predictor"]
    if package_decisions != values["c2p_adaptive_package_opportunities"]:
        failures.append(f"{label}: package decision partition failure")
    package_outcomes = (values["c2p_adaptive_package_hit"] +
                        values["c2p_adaptive_package_no_hit"] +
                        values["c2p_adaptive_package_timeout"])
    if package_outcomes != package_starts:
        failures.append(f"{label}: package outcome partition failure")
    residual = values["c2p_adaptive_package_residual_opportunities"]
    if residual != (values["c2p_adaptive_package_residual_later_peer"] +
                    values["c2p_adaptive_package_residual_no_later_peer"]):
        failures.append(f"{label}: package residual partition failure")
    if residual > values["c2p_adaptive_package_no_hit"]:
        failures.append(f"{label}: residual opportunities exceed package misses")
    stops = (values["c2p_adaptive_stop_predictor"] +
             values["c2p_adaptive_stop_hard_cap"])
    if stops != (values["c2p_adaptive_stop_later_peer"] +
                 values["c2p_adaptive_stop_no_later_peer"]):
        failures.append(f"{label}: stopped-tail partition failure")


def expected_options(variant):
    common = {
        "-c2p_cache_separate_target_tag_port": "1",
        "-c2p_cache_max_candidate_probes": "0",
        "-c2p_cache_adaptive_probe_observe_tail": "1",
        "-c2p_cache_adaptive_probe_initial_score": "4",
        "-c2p_cache_adaptive_probe_force_full_small_candidates": "0",
    }
    if variant == "control":
        return {**common, "-c2p_cache_adaptive_probe_policy": "0",
                "-c2p_cache_adaptive_probe_addr_topology_policy": "0"}
    return {**common, "-c2p_cache_adaptive_probe_policy": "1",
            "-c2p_cache_adaptive_probe_package_policy": "1",
            "-c2p_cache_adaptive_probe_score_threshold": "4",
            "-c2p_cache_adaptive_probe_explore_period": "64",
            "-c2p_cache_adaptive_probe_addr_topology_policy":
                "1" if variant == "addr" else "0"}


def check_policy_options(options, expected, label, failures):
    """Reject stale adaptive knobs as well as wrong required values.

    The matrix is a capacity-matched experiment, not a permissive feature
    smoke test.  In particular, accepting an old PC-ordinal side table would
    silently invalidate the AddrTopo comparison even if its required package
    options were also present.
    """
    for key, value in expected.items():
        if options.get(key) != value:
            failures.append(f"{label}: {key}={options.get(key)!r}, expected {value}")
    for key in options:
        if key.startswith("-c2p_cache_adaptive_probe_") and key not in expected:
            failures.append(f"{label}: stale or unsupported adaptive option {key}")


def manifest_cases(path):
    """Return the ordered workload names from a checked-in matrix manifest."""
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
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    parser.add_argument("--case", default="",
                        help="comma-separated manifest subset for a qualified pilot")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    expected_cases = {
        "canonical": manifest_cases(
            repo_root / "configs/c2p-cache/paper16_workloads.tsv"),
        "extension": manifest_cases(
            repo_root / "configs/c2p-cache/v100_extension_workloads.tsv"),
    }
    selected_cases = {case for case in args.case.split(",") if case}
    known_cases = set().union(*map(set, expected_cases.values()))
    unknown_cases = sorted(selected_cases - known_cases)
    if unknown_cases:
        parser.error("unknown manifest case(s): " + ", ".join(unknown_cases))
    if selected_cases:
        expected_cases = {
            tier: [case for case in cases if case in selected_cases]
            for tier, cases in expected_cases.items()
        }

    rows, failures = [], []
    # A triplet already checks its three runs against one another.  Preserve a
    # separate matrix-wide build identity as well: a campaign assembled by
    # prelaunch workers must not silently combine different simulator binaries.
    # `accelsim_commit` is deliberately not included here because it may differ
    # for a launcher-only commit while the copied executable remains identical.
    global_build = {
        "gpgpusim_commit": set(),
        "sim_sha256": set(),
        "cudart_sha256": set(),
    }
    for tier in TIERS:
        tier_root = args.root / tier
        if not tier_root.is_dir():
            if expected_cases[tier]:
                failures.append(f"missing tier directory: {tier}")
            continue
        case_dirs = {path.name: path for path in tier_root.iterdir() if path.is_dir()}
        actual_cases = set(case_dirs)
        required_cases = set(expected_cases[tier])
        missing_cases = sorted(required_cases - actual_cases)
        extra_cases = sorted(actual_cases - required_cases)
        if missing_cases:
            failures.append(f"{tier}: missing manifest cases: {', '.join(missing_cases)}")
        if extra_cases:
            failures.append(f"{tier}: unexpected cases: {', '.join(extra_cases)}")
        for case_name in expected_cases[tier]:
            case_dir = case_dirs.get(case_name)
            if case_dir is None:
                continue
            runs, provenance = {}, {}
            for variant in VARIANTS:
                run_dir = case_dir / variant / "c2p"
                summary = run_dir / "summary.txt"
                output = run_dir / "run.out"
                if not summary.is_file() or not output.is_file() or \
                        "GPGPU-Sim: *** exit detected ***" not in output.read_text(errors="replace"):
                    failures.append(f"{tier}/{case_dir.name}/{variant}: incomplete run")
                    continue
                runs[variant] = read_values(summary)
                provenance[variant] = read_key_values(run_dir / "provenance.txt")
                options = config_options(run_dir / "gpgpusim.config")
                check_policy_options(
                    options, expected_options(variant),
                    f"{tier}/{case_dir.name}/{variant}", failures)
            if len(runs) != len(VARIANTS):
                continue
            reference = provenance["control"]
            for variant in ("pc", "addr"):
                for key in ("gpgpusim_commit", "accelsim_commit", "trace_sha256",
                            "sim_sha256", "cudart_sha256"):
                    if provenance[variant].get(key) != reference.get(key):
                        failures.append(f"{tier}/{case_dir.name}: {variant} differs in {key}")
            for key, values in global_build.items():
                value = reference.get(key)
                if not value:
                    failures.append(f"{tier}/{case_dir.name}: missing {key}")
                else:
                    values.add(value)
            control = runs["control"]
            if not require(control, BASE_FIELDS + PACKAGE_FIELDS, f"{tier}/{case_dir.name}/control", failures):
                continue
            if control["c2p_remote_hits"] != control["c2p_l2_requests_avoided"]:
                failures.append(f"{tier}/{case_dir.name}/control: remote hits != L2 avoided")
            if any(control[field] for field in PACKAGE_FIELDS):
                failures.append(f"{tier}/{case_dir.name}/control: adaptive package counters are nonzero")
            for variant in ("pc", "addr"):
                audit_policy(runs[variant], f"{tier}/{case_dir.name}/{variant}", failures)

            row = {"tier": tier, "case": case_dir.name}
            for variant in VARIANTS:
                for field in BASE_FIELDS:
                    row[f"{variant}_{field}"] = runs[variant].get(field, "")
            for variant in ("pc", "addr"):
                values = runs[variant]
                row[f"{variant}_cycle_delta"] = values["gpu_tot_sim_cycle"] - control["gpu_tot_sim_cycle"]
                row[f"{variant}_cycle_delta_pct"] = percentage(row[f"{variant}_cycle_delta"], control["gpu_tot_sim_cycle"])
                row[f"{variant}_l2_delta"] = values["l2_total_cache_accesses"] - control["l2_total_cache_accesses"]
                row[f"{variant}_remote_delta"] = values["c2p_remote_hits"] - control["c2p_remote_hits"]
                row[f"{variant}_probe_delta"] = values["c2p_peer_probes"] - control["c2p_peer_probes"]
                for field in PACKAGE_FIELDS:
                    row[f"{variant}_{field}"] = values[field]
            rows.append(row)

    for key, values in global_build.items():
        if len(values) > 1:
            failures.append(
                f"matrix-wide build mismatch in {key}: {', '.join(sorted(values))}")

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    columns = ["tier", "case"] + [f"{variant}_{field}" for variant in VARIANTS
               for field in BASE_FIELDS] + [f"{variant}_{field}" for variant in ("pc", "addr")
               for field in ("cycle_delta", "cycle_delta_pct", "l2_delta", "remote_delta", "probe_delta", *PACKAGE_FIELDS)]
    with args.csv.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    scope = ("qualified pilot subset: " + ", ".join(sorted(selected_cases))
             if selected_cases else "full 16 canonical + 8 extension matrix")
    lines = ["# C2P+ PC-hash versus AddrTopo confirmation policy", "",
             f"Scope: **{scope}**.", "",
             "Every row uses one copied frontend/backend binary and identical trace. "
             "`control` is exhaustive C2P+; `pc` and `addr` each use 64 x 4 "
             "3-bit package entries, identical threshold/exploration/candidate-bin "
             "rules, and a four-probe hard cap.", "",
             "| Tier | Case | PC cycle Δ | Addr cycle Δ | PC / Addr L2 Δ | PC / Addr remote Δ | PC / Addr probe Δ | PC / Addr residual peer |",
             "|---|---|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(
            f"| {row['tier']} | {row['case']} | {row['pc_cycle_delta']} ({row['pc_cycle_delta_pct']}%) | "
            f"{row['addr_cycle_delta']} ({row['addr_cycle_delta_pct']}%) | "
            f"{row['pc_l2_delta']} / {row['addr_l2_delta']} | "
            f"{row['pc_remote_delta']} / {row['addr_remote_delta']} | "
            f"{row['pc_probe_delta']} / {row['addr_probe_delta']} | "
            f"{row['pc_c2p_adaptive_package_residual_later_peer']} / "
            f"{row['addr_c2p_adaptive_package_residual_later_peer']} |")
    for tier in TIERS + ("all",):
        subset = rows if tier == "all" else [row for row in rows if row["tier"] == tier]
        if not subset:
            continue
        lines += ["", f"## {tier} aggregate ({len(subset)} workloads)", "",
                  "| Policy | Geomean IPC ratio vs exhaustive | L2 delta | Remote-hit delta | Probe delta | Residual exact-peer opportunities |",
                  "|---|---:|---:|---:|---:|---:|"]
        for variant in ("pc", "addr"):
            ipc_ratio = math.exp(sum(math.log(
                row["control_gpu_tot_sim_cycle"] / row[f"{variant}_gpu_tot_sim_cycle"])
                for row in subset) / len(subset))
            lines.append(
                f"| {variant} | {ipc_ratio:.6f} | "
                f"{sum(row[f'{variant}_l2_delta'] for row in subset)} | "
                f"{sum(row[f'{variant}_remote_delta'] for row in subset)} | "
                f"{sum(row[f'{variant}_probe_delta'] for row in subset)} | "
                f"{sum(row[f'{variant}_c2p_adaptive_package_residual_later_peer'] for row in subset)} |")
    if failures:
        lines += ["", "## Validation failures", ""]
        lines += [f"- {failure}" for failure in failures]
    else:
        lines += ["", "All completed runs satisfy binary/trace provenance, "
                  "configuration, remote-hit, probe, continuation, package, "
                  "and residual-opportunity conservation checks."]
    args.markdown.write_text("\n".join(lines) + "\n")
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
