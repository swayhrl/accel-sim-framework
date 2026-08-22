#!/usr/bin/env python3
"""Qualify paired exhaustive-C2P+ versus adaptive-C2P+ replays."""

import argparse
import csv
from pathlib import Path


CASES = ("2DConvolution", "lps", "btree", "bfs", "sgemm", "gaussian", "nn")
BASE = (
    "gpu_tot_sim_cycle", "l2_total_cache_accesses", "c2p_remote_hits",
    "c2p_l2_requests_avoided", "c2p_peer_probes", "c2p_peer_probe_hits",
    "c2p_peer_probe_misses", "c2p_target_tag_port_busy_cycles",
)
ADAPT = (
    "c2p_adaptive_continuation_opportunities",
    "c2p_adaptive_continue_predictor",
    "c2p_adaptive_continue_exploration",
    "c2p_adaptive_stop_predictor", "c2p_adaptive_stop_hard_cap",
    "c2p_adaptive_stop_later_peer", "c2p_adaptive_stop_no_later_peer",
    "c2p_adaptive_stop_remaining_candidates",
    "c2p_adaptive_stop_next_peer_distance_total",
    "c2p_adaptive_first_probe_hits", "c2p_adaptive_first_probe_misses",
    "c2p_adaptive_first_probe_timeouts",
    "c2p_adaptive_predictor_probe_hits",
    "c2p_adaptive_predictor_probe_misses",
    "c2p_adaptive_predictor_probe_timeouts",
    "c2p_adaptive_exploration_probe_hits",
    "c2p_adaptive_exploration_probe_misses",
    "c2p_adaptive_exploration_probe_timeouts",
)


def read_summary(path):
    values = {}
    for line in path.read_text().splitlines():
        if " = " not in line:
            continue
        key, value = line.split(" = ", 1)
        try:
            values[key] = int(value)
        except ValueError:
            pass
    return values


def pct(delta, base):
    return "" if not base else f"{100 * delta / base:.3f}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--observation-root", required=True, type=Path)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()

    rows, failures = [], []
    for case in CASES:
        control_path = args.root / case / "control" / "c2p" / "summary.txt"
        adaptive_path = args.root / case / "adaptive" / "c2p" / "summary.txt"
        observation_path = args.observation_root / case / "c2p" / "summary.txt"
        if not control_path.is_file() or not adaptive_path.is_file():
            failures.append(f"{case}: missing control or adaptive summary")
            continue
        control, adaptive = read_summary(control_path), read_summary(adaptive_path)
        missing = [field for field in (*BASE, *ADAPT)
                   if field not in control or field not in adaptive]
        if missing:
            failures.append(f"{case}: missing {', '.join(missing)}")
            continue
        for label, values in (("control", control), ("adaptive", adaptive)):
            if values["c2p_remote_hits"] != values["c2p_l2_requests_avoided"]:
                failures.append(f"{case}/{label}: remote-hit conservation failure")
        if any(control[field] for field in ADAPT):
            failures.append(f"{case}/control: adaptive counters are nonzero")
        if observation_path.is_file():
            observation = read_summary(observation_path)
            for key, value in observation.items():
                if key.startswith("c2p_adaptive_"):
                    continue
                if key in control and control[key] != value:
                    failures.append(f"{case}/control: differs from observation {key}")
                    break

        issued = (adaptive["c2p_adaptive_first_probe_hits"] +
                  adaptive["c2p_adaptive_first_probe_misses"] +
                  adaptive["c2p_adaptive_first_probe_timeouts"] +
                  adaptive["c2p_adaptive_predictor_probe_hits"] +
                  adaptive["c2p_adaptive_predictor_probe_misses"] +
                  adaptive["c2p_adaptive_predictor_probe_timeouts"] +
                  adaptive["c2p_adaptive_exploration_probe_hits"] +
                  adaptive["c2p_adaptive_exploration_probe_misses"] +
                  adaptive["c2p_adaptive_exploration_probe_timeouts"])
        if issued != adaptive["c2p_peer_probes"]:
            failures.append(f"{case}/adaptive: issue-reason probes {issued} != "
                            f"peer probes {adaptive['c2p_peer_probes']}")
        continuations = (adaptive["c2p_adaptive_continue_predictor"] +
                         adaptive["c2p_adaptive_continue_exploration"] +
                         adaptive["c2p_adaptive_stop_predictor"])
        if continuations != adaptive["c2p_adaptive_continuation_opportunities"]:
            failures.append(f"{case}/adaptive: continuation partition failure")
        stops = (adaptive["c2p_adaptive_stop_predictor"] +
                 adaptive["c2p_adaptive_stop_hard_cap"])
        classified = (adaptive["c2p_adaptive_stop_later_peer"] +
                      adaptive["c2p_adaptive_stop_no_later_peer"])
        if stops != classified:
            failures.append(f"{case}/adaptive: stopped-tail classification failure")
        if case == "nn":
            if control["gpu_tot_sim_cycle"] != adaptive["gpu_tot_sim_cycle"]:
                failures.append("nn: adaptive changed no-op cycle count")
            if any(adaptive[field] for field in ADAPT):
                failures.append("nn: adaptive activity on no-op trace")

        row = {"case": case}
        for field in BASE:
            row[f"control_{field}"] = control[field]
            row[f"adaptive_{field}"] = adaptive[field]
        for field in ADAPT:
            row[field] = adaptive[field]
        row["cycle_delta"] = adaptive["gpu_tot_sim_cycle"] - control["gpu_tot_sim_cycle"]
        row["cycle_delta_pct"] = pct(row["cycle_delta"], control["gpu_tot_sim_cycle"])
        row["l2_delta"] = (adaptive["l2_total_cache_accesses"] -
                           control["l2_total_cache_accesses"])
        row["probe_delta"] = adaptive["c2p_peer_probes"] - control["c2p_peer_probes"]
        row["saved_tail_rate"] = pct(adaptive["c2p_adaptive_stop_no_later_peer"], stops)
        row["lost_peer_rate"] = pct(adaptive["c2p_adaptive_stop_later_peer"], stops)
        rows.append(row)

    columns = ["case"] + [f"{variant}_{field}" for variant in ("control", "adaptive")
                            for field in BASE] + list(ADAPT) + [
        "cycle_delta", "cycle_delta_pct", "l2_delta", "probe_delta",
        "saved_tail_rate", "lost_peer_rate"]
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    lines = ["# C2P+ adaptive probe-depth paired result", "",
             "Every row compares the same binary, trace, and C2P+ separate-tag "
             "configuration; only adaptive confirmation is enabled in the right "
             "hand run.", "",
             "| Case | Cycle delta | L2 delta | Probe delta | Saved-tail stops | "
             "Lost-peer stops | Predictor / exploration continuation |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(
            f"| {row['case']} | {row['cycle_delta']} ({row['cycle_delta_pct']}%) | "
            f"{row['l2_delta']} | {row['probe_delta']} | "
            f"{row['saved_tail_rate']}% | {row['lost_peer_rate']}% | "
            f"{row['c2p_adaptive_continue_predictor']} / "
            f"{row['c2p_adaptive_continue_exploration']} |")
    if failures:
        lines += ["", "## Validation failures", ""]
        lines += [f"- {failure}" for failure in failures]
    else:
        lines += ["", "All paired controls reproduce the observation-only C2P+ "
                  "point, and all adaptive accounting partitions conserve."]
    args.markdown.write_text("\n".join(lines) + "\n")
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
