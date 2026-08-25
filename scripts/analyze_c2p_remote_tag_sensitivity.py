#!/usr/bin/env python3
"""Audit the staged global C2P remote-tag 7-to-14-cycle sensitivity."""

import argparse
import csv
import re
from pathlib import Path


NUMBER_RE = re.compile(r"^\s*([A-Za-z0-9_]+) = ([0-9]+)$")
COMMON = ("gpu_tot_sim_cycle", "c2p_remote_hits", "c2p_l2_requests_avoided",
          "c2p_peer_probes", "L2_total_cache_accesses")


def values(path):
    result = {}
    for line in path.read_text(errors="replace").splitlines():
        match = NUMBER_RE.match(line)
        if match:
            result[match.group(1)] = int(match.group(2))
    return result


def config(path):
    result = {}
    for line in path.read_text(errors="replace").splitlines():
        words = line.split()
        if len(words) >= 2 and words[0].startswith("-") and not words[0].startswith("#"):
            result[words[0]] = words[1]
    return result


def read_run(root, case, variant):
    run = root / case / variant / "c2p" / "run.out"
    cfg = run.parent / "gpgpusim.config"
    if not run.is_file() or not cfg.is_file():
        raise FileNotFoundError(run)
    return values(run), config(cfg), run


def required(item, keys):
    return [key for key in keys if key not in item]


def percent(now, base):
    return "" if base == 0 else f"{100.0 * (now - base) / base:.2f}%"


def check_common(case, label, item, cfg, tag, locality, policy, failures):
    missing = required(item, COMMON)
    if missing:
        failures.append(f"{case}/{label}: missing counters {', '.join(missing)}")
        return
    if item["c2p_remote_hits"] != item["c2p_l2_requests_avoided"]:
        failures.append(f"{case}/{label}: remote-hit/L2-avoidance invariant failed")
    expected = {
        "-c2p_cache_remote_tag_latency": str(tag),
        "-c2p_cache_remote_return_latency": "2",
        "-gpgpu_l2_rop_latency": "200",
        "-c2p_cache_locality_aware_candidate_order": str(locality),
        "-c2p_cache_outer_admission_policy": str(policy),
    }
    for key, value in expected.items():
        if cfg.get(key) != value:
            failures.append(f"{case}/{label}: {key}={cfg.get(key)!r}, expected {value}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--phase", required=True, choices=("canonical", "locality", "admission"))
    parser.add_argument("--case", required=True)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()

    if args.phase == "canonical":
        variants = (("tag7", 7, 0, 0), ("tag14", 14, 0, 0))
    elif args.phase == "locality":
        variants = (("tag7", 7, 1, 0), ("tag14", 14, 1, 0))
    else:
        variants = (("control7", 7, 1, 0), ("policy7", 7, 1, 1),
                    ("control14", 14, 1, 0), ("policy14", 14, 1, 1))
    failures, rows = [], []
    for case in filter(None, args.case.split(",")):
        data = {}
        for label, tag, locality, policy in variants:
            try:
                item, cfg, path = read_run(args.root, case, label)
                data[label] = (item, cfg, path)
                check_common(case, label, item, cfg, tag, locality, policy, failures)
            except FileNotFoundError as error:
                failures.append(f"{case}/{label}: missing input ({error})")
        if len(data) != len(variants):
            continue
        if args.phase == "admission":
            for tag in (7, 14):
                item = data[f"policy{tag}"][0]
                keys = ("c2p_outer_admission_opportunities",
                        "c2p_outer_admission_continue_predictor",
                        "c2p_outer_admission_continue_exploration",
                        "c2p_outer_admission_bypass_predictor",
                        "c2p_outer_admission_train_hit",
                        "c2p_outer_admission_train_no_hit")
                missing = required(item, keys)
                if missing:
                    failures.append(f"{case}/policy{tag}: missing policy counters")
                    continue
                cont = (item["c2p_outer_admission_continue_predictor"] +
                        item["c2p_outer_admission_continue_exploration"])
                if cont + item["c2p_outer_admission_bypass_predictor"] != item["c2p_outer_admission_opportunities"]:
                    failures.append(f"{case}/policy{tag}: admission decision partition failed")
                if item["c2p_outer_admission_train_hit"] + item["c2p_outer_admission_train_no_hit"] > cont:
                    failures.append(f"{case}/policy{tag}: train count exceeds continuations")
            row = {"case": case}
            for tag in (7, 14):
                for kind in ("control", "policy"):
                    item = data[f"{kind}{tag}"][0]
                    row[f"{kind}{tag}_cycles"] = item["gpu_tot_sim_cycle"]
                    row[f"{kind}{tag}_probes"] = item["c2p_peer_probes"]
                    row[f"{kind}{tag}_hits"] = item["c2p_remote_hits"]
                    row[f"{kind}{tag}_l2"] = item["L2_total_cache_accesses"]
                row[f"policy{tag}_delta_pct"] = percent(row[f"policy{tag}_cycles"], row[f"control{tag}_cycles"])
            rows.append(row)
        else:
            tag7, tag14 = data["tag7"][0], data["tag14"][0]
            rows.append({
                "case": case,
                "tag7_cycles": tag7["gpu_tot_sim_cycle"],
                "tag14_cycles": tag14["gpu_tot_sim_cycle"],
                "cycle_delta_pct": percent(tag14["gpu_tot_sim_cycle"], tag7["gpu_tot_sim_cycle"]),
                "tag7_probes": tag7["c2p_peer_probes"], "tag14_probes": tag14["c2p_peer_probes"],
                "tag7_hits": tag7["c2p_remote_hits"], "tag14_hits": tag14["c2p_remote_hits"],
                "tag7_l2": tag7["L2_total_cache_accesses"], "tag14_l2": tag14["L2_total_cache_accesses"],
            })

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["case"]
    with args.csv.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    if args.phase == "admission":
        lines = ["# C2P outer-admission global remote-tag sensitivity", "",
                 "Every paired point keeps remote return latency at two cycles and shared L2 latency at 200 cycles.  Only the global remote target-tag lookup changes from seven to fourteen cycles.", "",
                 "| Case | Control 7 / policy 7 cycles | Policy delta 7 | Control 14 / policy 14 cycles | Policy delta 14 |", "|---|---:|---:|---:|---:|"]
        for row in rows:
            lines.append(f"| {row['case']} | {row['control7_cycles']} / {row['policy7_cycles']} | {row['policy7_delta_pct']} | {row['control14_cycles']} / {row['policy14_cycles']} | {row['policy14_delta_pct']} |")
    else:
        title = "canonical C2P" if args.phase == "canonical" else "4-SM local-first C2P"
        lines = [f"# C2P global remote-tag sensitivity: {title}", "",
                 "The `tag14` point changes only global remote target-tag lookup latency from seven to fourteen cycles.  Remote return remains two cycles; shared L2 remains 200 cycles.", "",
                 "| Case | Tag7 cycles | Tag14 cycles | Cycle delta | Tag7 / tag14 probes | Tag7 / tag14 remote hits | Tag7 / tag14 L2 accesses |", "|---|---:|---:|---:|---:|---:|---:|"]
        for row in rows:
            lines.append(f"| {row['case']} | {row['tag7_cycles']} | {row['tag14_cycles']} | {row['cycle_delta_pct']} | {row['tag7_probes']} / {row['tag14_probes']} | {row['tag7_hits']} / {row['tag14_hits']} | {row['tag7_l2']} / {row['tag14_l2']} |")
    if failures:
        lines += ["", "## Validation failures", ""] + [f"- {failure}" for failure in failures]
    else:
        lines += ["", "All resolved timing, policy, and remote-hit/L2-avoidance invariants passed."]
    args.markdown.write_text("\n".join(lines) + "\n")
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
