#!/usr/bin/env python3
"""Compare canonical C2P with the target-port-bypass diagnostic control.

The bypass control is a counterfactual explanation tool only.  It preserves
candidate generation and fixed communication latency while removing C2P probe
use of the target L1 data port and its probe FIFO.  This script deliberately
reads final ``run.out`` C2P statistics, because early compact summaries did
not carry every diagnostic counter.
"""

import argparse
import re
from pathlib import Path


STAT = re.compile(r"^\s*([A-Za-z0-9_]+) = (\d+)$")
CONFIG = re.compile(r"^\s*(-c2p_cache_[A-Za-z0-9_]+)\s+(\S+)")
REQUIRED = (
    "gpu_tot_sim_cycle", "l2_total_cache_accesses", "c2p_candidate_total",
    "c2p_candidate_queries", "c2p_peer_probes", "c2p_peer_probe_hits",
    "c2p_peer_probe_misses", "c2p_remote_hits",
    "c2p_l2_requests_avoided", "c2p_target_probe_port_busy_cycles",
    "c2p_target_probe_queue_wait_cycles",
    "c2p_target_probe_queue_full_cycles", "c2p_requester_fill_wait_cycles",
)


def read_run(run_dir):
    output = run_dir / "run.out"
    config = run_dir / "gpgpusim.config"
    if not output.is_file() or not config.is_file():
        return None
    values = {}
    for line in output.read_text(errors="replace").splitlines():
        match = STAT.match(line)
        if match:
            key = match.group(1)
            if key == "L2_total_cache_accesses":
                key = "l2_total_cache_accesses"
            values[key] = int(match.group(2))
    options = {}
    for line in config.read_text(errors="replace").splitlines():
        match = CONFIG.match(line)
        if match:
            options[match.group(1)] = match.group(2)
    return values, options


def locate(roots, case):
    for root in roots:
        run_dir = root / case / "c2p"
        result = read_run(run_dir)
        if result is not None:
            return run_dir, *result
    return None, None, None


def ratio(numerator, denominator):
    return "—" if denominator == 0 else f"{numerator / denominator:.4f}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--normal-root", action="append", type=Path,
                        required=True,
                        help="canonical C2P root; searched in order")
    parser.add_argument("--bypass-root", required=True, type=Path)
    parser.add_argument("--cases", default="sgemm,btree,nn")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    failures = []
    rows = []
    for case in [item for item in args.cases.split(",") if item]:
        normal_dir, normal, normal_options = locate(args.normal_root, case)
        bypass_dir, bypass, bypass_options = locate([args.bypass_root], case)
        if normal is None or bypass is None:
            failures.append(f"{case}: missing normal or bypass run")
            continue
        for label, values in (("normal", normal), ("bypass", bypass)):
            absent = [field for field in REQUIRED if field not in values]
            if absent:
                failures.append(f"{case}/{label}: missing counters {', '.join(absent)}")
            if values.get("c2p_remote_hits") != values.get("c2p_l2_requests_avoided"):
                failures.append(f"{case}/{label}: remote hit != avoided L2")
        if normal_options.get("-c2p_cache_diagnostic_target_port_bypass", "0") != "0":
            failures.append(f"{case}/normal: target-port bypass is unexpectedly enabled")
        if bypass_options.get("-c2p_cache_diagnostic_target_port_bypass") != "1":
            failures.append(f"{case}/bypass: target-port bypass is not enabled")
        rows.append((case, normal_dir, normal, bypass_dir, bypass))

    lines = ["# C2P target-port contention diagnostic", "",
             "This is a counterfactual diagnostic, not a paper-figure point. "
             "Normal and bypass use the same C2P candidate path; bypass removes "
             "only target L1 data-port/FIFO contention.", "",
             "| Case | Normal cycles | Bypass cycles | Bypass IPC / normal | "
             "Normal L2 | Bypass L2 | Normal remote hit | Bypass remote hit | "
             "Normal probe | Bypass probe | Normal port-busy cycles | "
             "Normal FIFO-wait cycles | Normal requester-fill wait |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for case, _, normal, _, bypass in rows:
        lines.append(
            "| {case} | {nc} | {bc} | {ipc} | {nl2} | {bl2} | {nrh} | {brh} | "
            "{np} | {bp} | {busy} | {fifo} | {fill} |".format(
                case=case, nc=normal["gpu_tot_sim_cycle"],
                bc=bypass["gpu_tot_sim_cycle"],
                ipc=ratio(normal["gpu_tot_sim_cycle"], bypass["gpu_tot_sim_cycle"]),
                nl2=normal["l2_total_cache_accesses"],
                bl2=bypass["l2_total_cache_accesses"],
                nrh=normal["c2p_remote_hits"], brh=bypass["c2p_remote_hits"],
                np=normal["c2p_peer_probes"], bp=bypass["c2p_peer_probes"],
                busy=normal["c2p_target_probe_port_busy_cycles"],
                fifo=normal["c2p_target_probe_queue_wait_cycles"],
                fill=normal["c2p_requester_fill_wait_cycles"]))
    if failures:
        lines.extend(["", "## Validation failures", ""])
        lines.extend(f"- {failure}" for failure in failures)
    else:
        lines.extend(["", "All requested normal/bypass pairs passed the "
                      "configuration and remote-hit ownership checks."])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n")
    if failures and args.strict:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
