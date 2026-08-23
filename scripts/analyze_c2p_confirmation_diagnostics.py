#!/usr/bin/env python3
"""Audit and summarize the compact C2P+ confirmation-policy diagnosis set."""

import argparse
import csv
import re
import sys
from pathlib import Path


CASES = ("btree", "c2p-ispass-bfs", "c2p-ispass-lps")
OBSERVE = ("control", "pc", "addr")
EXPERIMENT = ("smallfull", "initial6", "initial7")
BASE = ("gpu_tot_sim_cycle", "l2_total_cache_accesses", "c2p_remote_hits",
        "c2p_l2_requests_avoided", "c2p_peer_probes", "c2p_peer_probe_hits",
        "c2p_peer_probe_misses")
REASON = ("c2p_adaptive_first_probe_hits", "c2p_adaptive_first_probe_misses",
          "c2p_adaptive_first_probe_timeouts",
          "c2p_adaptive_predictor_probe_hits", "c2p_adaptive_predictor_probe_misses",
          "c2p_adaptive_predictor_probe_timeouts",
          "c2p_adaptive_exploration_probe_hits", "c2p_adaptive_exploration_probe_misses",
          "c2p_adaptive_exploration_probe_timeouts",
          "c2p_adaptive_forced_probe_hits", "c2p_adaptive_forced_probe_misses",
          "c2p_adaptive_forced_probe_timeouts")
STAT = re.compile(r"^\s*((?:c2p_[A-Za-z0-9_]+)|gpu_tot_sim_cycle|l2_total_cache_accesses) = (\d+)$")


def values(run_dir):
    summary, output = run_dir / "summary.txt", run_dir / "run.out"
    if not summary.is_file() or not output.is_file():
        return None
    text = output.read_text(errors="replace")
    if "GPGPU-Sim: *** exit detected ***" not in text:
        return None
    result = {}
    for path in (summary, output):
        for line in path.read_text(errors="replace").splitlines():
            match = STAT.match(line)
            if match:
                result[match.group(1)] = int(match.group(2))
    return result


def config(path):
    result = {}
    if not path.is_file():
        return result
    for line in path.read_text(errors="replace").splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[0].startswith("-c2p_cache_"):
            result[fields[0]] = fields[1]
    return result


def provenance(path):
    result = {}
    if path.is_file():
        for line in path.read_text(errors="replace").splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                result[key] = value
    return result


def need(data, fields, label, failures):
    absent = [field for field in fields if field not in data]
    if absent:
        failures.append(f"{label}: missing {', '.join(absent)}")
        return False
    return True


def audit_adaptive(data, label, failures):
    fields = BASE + REASON + (
        "c2p_adaptive_continuation_opportunities",
        "c2p_adaptive_continue_predictor", "c2p_adaptive_continue_exploration",
        "c2p_adaptive_continue_forced", "c2p_adaptive_stop_predictor",
        "c2p_adaptive_package_opportunities",
        "c2p_adaptive_package_start_predictor",
        "c2p_adaptive_package_start_exploration",
        "c2p_adaptive_package_start_forced",
        "c2p_adaptive_package_stop_predictor", "c2p_adaptive_package_hit",
        "c2p_adaptive_package_no_hit", "c2p_adaptive_package_timeout")
    if not need(data, fields, label, failures):
        return
    if data["c2p_remote_hits"] != data["c2p_l2_requests_avoided"]:
        failures.append(f"{label}: remote hit / avoided-L2 mismatch")
    if sum(data[field] for field in REASON) != data["c2p_peer_probes"]:
        failures.append(f"{label}: probe reason partition mismatch")
    starts = (data["c2p_adaptive_package_start_predictor"] +
              data["c2p_adaptive_package_start_exploration"] +
              data["c2p_adaptive_package_start_forced"])
    decisions = starts + data["c2p_adaptive_package_stop_predictor"]
    if decisions != data["c2p_adaptive_package_opportunities"]:
        failures.append(f"{label}: package decision partition mismatch")
    if starts != (data["c2p_adaptive_package_hit"] +
                  data["c2p_adaptive_package_no_hit"] +
                  data["c2p_adaptive_package_timeout"]):
        failures.append(f"{label}: package outcome partition mismatch")
    continuation = (data["c2p_adaptive_continue_predictor"] +
                    data["c2p_adaptive_continue_exploration"] +
                    data["c2p_adaptive_continue_forced"] +
                    data["c2p_adaptive_stop_predictor"])
    if continuation != data["c2p_adaptive_continuation_opportunities"]:
        failures.append(f"{label}: continuation partition mismatch")
    complete = data["c2p_peer_probe_hits"] + data["c2p_peer_probe_misses"]
    bins = 0
    for candidate_bin in range(4):
        for ordinal in range(4):
            bins += data.get(
                f"c2p_candidate_bin_{candidate_bin}_probe_ordinal_{ordinal + 1}_hits", 0)
            bins += data.get(
                f"c2p_candidate_bin_{candidate_bin}_probe_ordinal_{ordinal + 1}_misses", 0)
        bins += data.get(f"c2p_candidate_bin_{candidate_bin}_probe_ordinal_overflow_hits", 0)
        bins += data.get(f"c2p_candidate_bin_{candidate_bin}_probe_ordinal_overflow_misses", 0)
    if bins != complete:
        failures.append(f"{label}: candidate-bin/ordinal probe partition mismatch")
    early = later = no_later = delay_samples = 0
    for candidate_bin in range(4):
        early += data.get(f"c2p_adaptive_early_stop_bin_{candidate_bin}_opportunities", 0)
        later += data.get(f"c2p_adaptive_early_stop_bin_{candidate_bin}_later_peer", 0)
        no_later += data.get(f"c2p_adaptive_early_stop_bin_{candidate_bin}_no_later_peer", 0)
    for pressure in range(4):
        delay_samples += data.get(
            f"c2p_adaptive_early_stop_lower_pressure_{pressure}_samples", 0)
    if early != later + no_later:
        failures.append(f"{label}: early-stop exact-tail partition mismatch")
    if early != delay_samples:
        failures.append(f"{label}: early-stop delay samples mismatch")


def pct(delta, baseline):
    return "n/a" if not baseline else f"{100.0 * delta / baseline:+.2f}%"


def ordinal(data, candidate_bin, ordinal, outcome):
    name = (f"c2p_candidate_bin_{candidate_bin}_probe_ordinal_"
            f"{'overflow' if ordinal == 4 else ordinal + 1}_{outcome}")
    return data.get(name, 0)


def run(root, phase, case, variant):
    return root / phase / case / variant / "c2p"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--require-experiments", action="store_true")
    args = parser.parse_args()

    all_runs, failures = {}, []
    required = [("observe", variant) for variant in OBSERVE]
    if args.require_experiments:
        required += [("experiment", variant) for variant in EXPERIMENT]
    for case in CASES:
        all_runs[case] = {}
        for phase, variant in required:
            directory = run(args.root, phase, case, variant)
            data = values(directory)
            label = f"{phase}/{case}/{variant}"
            if data is None:
                failures.append(f"{label}: incomplete run")
                continue
            all_runs[case][variant] = data
            if variant == "control":
                if not need(data, BASE, label, failures):
                    continue
                if data["c2p_remote_hits"] != data["c2p_l2_requests_avoided"]:
                    failures.append(f"{label}: remote hit / avoided-L2 mismatch")
            else:
                audit_adaptive(data, label, failures)
            opts = config(directory / "gpgpusim.config")
            expected_initial = {"pc": "4", "addr": "4", "smallfull": "4",
                                "initial6": "6", "initial7": "7"}.get(variant)
            if expected_initial and opts.get("-c2p_cache_adaptive_probe_initial_score") != expected_initial:
                failures.append(f"{label}: incorrect initial score")
            expected_force = "1" if variant == "smallfull" else "0"
            if expected_initial and opts.get("-c2p_cache_adaptive_probe_force_full_small_candidates") != expected_force:
                failures.append(f"{label}: incorrect small-candidate rule")
        if all(variant in all_runs[case] for variant in OBSERVE):
            reference = provenance(run(args.root, "observe", case, "control") / "provenance.txt")
            for variant in ("pc", "addr"):
                actual = provenance(run(args.root, "observe", case, variant) / "provenance.txt")
                for key in ("gpgpusim_commit", "accelsim_commit", "trace_sha256",
                            "sim_sha256", "cudart_sha256"):
                    if actual.get(key) != reference.get(key):
                        failures.append(f"observe/{case}/{variant}: differs in {key}")
        if args.require_experiments and "pc" in all_runs[case]:
            reference = provenance(run(args.root, "observe", case, "pc") / "provenance.txt")
            for variant in EXPERIMENT:
                actual = provenance(run(args.root, "experiment", case, variant) / "provenance.txt")
                for key in ("gpgpusim_commit", "accelsim_commit", "trace_sha256",
                            "sim_sha256", "cudart_sha256"):
                    if actual.get(key) != reference.get(key):
                        failures.append(f"experiment/{case}/{variant}: differs from pc in {key}")

    rows = []
    for case in CASES:
        for variant, data in all_runs[case].items():
            row = {"case": case, "variant": variant}
            row.update({field: data.get(field, "") for field in BASE})
            rows.append(row)
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=("case", "variant") + BASE)
        writer.writeheader()
        writer.writerows(rows)

    lines = ["# C2P+ confirmation-policy compact diagnosis", "",
             "This report is observational except for the two explicitly labelled PC-hash",
             "policy variants.  Exact-tail scans and queue-pressure accounting never feed a",
             "simulated timing or routing decision.", "",
             "## Audit", ""]
    lines.append("PASS: all requested completed runs satisfy provenance and counter conservation."
                 if not failures else "FAIL: see diagnostics below.")
    if failures:
        lines += ["", "```text"] + failures + ["```"]
    lines += ["", "## Observation modes", "",
              "| workload | mode | cycles | L2 accesses | remote hits | probes |"]
    for case in CASES:
        for variant in OBSERVE:
            data = all_runs[case].get(variant)
            if data:
                lines.append("| {case} | {variant} | {cycles} | {l2} | {remote} | {probes} |".format(
                    case=case, variant=variant, cycles=data["gpu_tot_sim_cycle"],
                    l2=data["l2_total_cache_accesses"], remote=data["c2p_remote_hits"],
                    probes=data["c2p_peer_probes"]))
    for variant in ("pc", "addr"):
        aggregate = [[0, 0] for _ in range(4 * 5)]
        for data in (all_runs[case].get(variant) for case in CASES):
            if not data:
                continue
            for candidate_bin in range(4):
                for ordinal_index in range(5):
                    index = candidate_bin * 5 + ordinal_index
                    aggregate[index][0] += ordinal(data, candidate_bin, ordinal_index, "hits")
                    aggregate[index][1] += ordinal(data, candidate_bin, ordinal_index, "misses")
        lines += ["", f"## {variant}: candidate-bin × probe-ordinal remote-hit distribution", "",
                  "| candidate bin | ordinal | hits | misses | hit rate |"]
        for candidate_bin in range(4):
            for ordinal_index in range(5):
                hits, misses = aggregate[candidate_bin * 5 + ordinal_index]
                total = hits + misses
                ordinal_label = "5+" if ordinal_index == 4 else str(ordinal_index + 1)
                rate = "n/a" if not total else f"{100.0 * hits / total:.2f}%"
                lines.append(f"| {candidate_bin} | {ordinal_label} | {hits} | {misses} | {rate} |")
        lines += ["", f"## {variant}: learned-stop exact-peer distance", "",
                  "| candidate bin | later peer | none | distance 1 | distance 2 | distance 3 | distance 4 | distance 5+ |"]
        for candidate_bin in range(4):
            total_later = total_none = 0
            distances = [0] * 5
            for data in (all_runs[case].get(variant) for case in CASES):
                if not data:
                    continue
                total_later += data.get(f"c2p_adaptive_early_stop_bin_{candidate_bin}_later_peer", 0)
                total_none += data.get(f"c2p_adaptive_early_stop_bin_{candidate_bin}_no_later_peer", 0)
                for distance in range(5):
                    suffix = "overflow" if distance == 4 else str(distance + 1)
                    distances[distance] += data.get(
                        f"c2p_adaptive_early_stop_bin_{candidate_bin}_distance_{suffix}", 0)
            lines.append("| {} | {} | {} | {} |".format(
                candidate_bin, total_later, total_none,
                " | ".join(str(value) for value in distances)))
        lines += ["", f"## {variant}: stop-to-lower delay by fallback pressure", "",
                  "Pressure is the number of already waiting C2P fallbacks at the learned stop: `0`, `1`, `2–3`, `4+`.", "",
                  "| pressure | samples | total cycles | mean cycles | nonzero waits |"]
        for pressure in range(4):
            samples = cycles = waited = 0
            for data in (all_runs[case].get(variant) for case in CASES):
                if not data:
                    continue
                samples += data.get(f"c2p_adaptive_early_stop_lower_pressure_{pressure}_samples", 0)
                cycles += data.get(f"c2p_adaptive_early_stop_lower_pressure_{pressure}_cycles", 0)
                waited += data.get(f"c2p_adaptive_early_stop_lower_pressure_{pressure}_waited", 0)
            mean = "n/a" if not samples else f"{cycles / samples:.3f}"
            lines.append(f"| {(0, 1, '2–3', '4+')[pressure]} | {samples} | {cycles} | {mean} | {waited} |")
    if args.require_experiments:
        lines += ["", "## Conservative PC-hash variants versus normal PC-hash", "",
                  "| workload | variant | cycle delta | L2 delta | remote-hit delta | probe delta |"]
        for case in CASES:
            base = all_runs[case].get("pc")
            if not base:
                continue
            for variant in EXPERIMENT:
                data = all_runs[case].get(variant)
                if not data:
                    continue
                lines.append("| {} | {} | {} | {} | {} | {} |".format(
                    case, variant,
                    pct(data["gpu_tot_sim_cycle"] - base["gpu_tot_sim_cycle"], base["gpu_tot_sim_cycle"]),
                    pct(data["l2_total_cache_accesses"] - base["l2_total_cache_accesses"], base["l2_total_cache_accesses"]),
                    data["c2p_remote_hits"] - base["c2p_remote_hits"],
                    pct(data["c2p_peer_probes"] - base["c2p_peer_probes"], base["c2p_peer_probes"])))
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text("\n".join(lines) + "\n")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
