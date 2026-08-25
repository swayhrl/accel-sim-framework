#!/usr/bin/env python3
"""Validate and summarize baseline/default/optimized Decoupled-L2 campaigns."""

import argparse
import csv
import math
import re
import sys
from pathlib import Path


CYCLE_RE = re.compile(r"gpu_tot_sim_cycle =\s*([0-9]+)")
IPC_RE = re.compile(r"gpu_tot_ipc =\s*([0-9]+(?:\.[0-9]+)?)")
MAX_RSS_RE = re.compile(r"Maximum resident set size \(kbytes\):\s*(\d+)")
EXIT_MARKER = "GPGPU-Sim: *** exit detected ***"


def fail(message):
    raise RuntimeError(message)


def provenance(run_dir):
    result = {}
    path = run_dir / "simulator_provenance.txt"
    if not path.is_file():
        fail("missing provenance: %s" % run_dir)
    for line in path.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key] = value
    return result


def measurements(run_dir):
    metrics_path = run_dir / "runtime_metrics.txt"
    if not metrics_path.is_file():
        fail("missing runtime metrics: %s" % run_dir)
    metrics = dict(line.split("=", 1) for line in metrics_path.read_text().splitlines()
                   if "=" in line)
    if metrics.get("sim_exit_status") != "0":
        fail("nonzero simulator exit: %s" % run_dir)
    try:
        wall_seconds = int(metrics["wall_seconds"])
    except (KeyError, ValueError) as error:
        raise RuntimeError("missing wall_seconds: %s" % run_dir) from error
    resource_path = run_dir / "resource_usage.txt"
    if not resource_path.is_file():
        fail("missing resource usage: %s" % run_dir)
    rss_values = MAX_RSS_RE.findall(resource_path.read_text(errors="replace"))
    if not rss_values:
        fail("missing maximum RSS: %s" % run_dir)
    path = run_dir / "smoke.out"
    text = path.read_text(errors="replace")
    if EXIT_MARKER not in text:
        fail("no normal exit: %s" % run_dir)
    values = CYCLE_RE.findall(text)
    if not values:
        fail("missing cycle count: %s" % run_dir)
    ipcs = IPC_RE.findall(text)
    if not ipcs:
        fail("missing IPC: %s" % run_dir)
    return {
        "cycles": int(values[-1]),
        "ipc": float(ipcs[-1]),
        "wall_seconds": wall_seconds,
        "max_rss_kib": int(rss_values[-1]),
    }


def read_summary(group, path):
    rows = []
    with path.open(newline="") as source:
        for row in csv.DictReader(source):
            arm = row.get("arm", row.get("backend"))
            if arm not in ("baseline", "decoupled", "optimized"):
                fail("%s has unknown arm %r" % (path, arm))
            row.update({"group": group, "arm": arm, "summary": str(path)})
            rows.append(row)
    return rows


def validate_case(group, suite, case, arms):
    expected = {"baseline", "decoupled", "optimized"}
    if set(arms) != expected:
        fail("%s/%s lacks a complete three-arm result: %s" %
             (suite, case, sorted(arms)))
    runs = {arm: Path(row["run_dir"]) for arm, row in arms.items()}
    metas = {arm: provenance(run_dir) for arm, run_dir in runs.items()}
    for arm, expected_backend in (("baseline", "baseline"),
                                  ("decoupled", "decoupled"),
                                  ("optimized", "decoupled")):
        if metas[arm].get("backend") != expected_backend:
            fail("%s/%s %s has backend %r" %
                 (suite, case, arm, metas[arm].get("backend")))
    for key in ("trace_kernelslist_sha256",):
        values = {metas[arm].get(key) for arm in expected}
        if len(values) != 1 or None in values:
            fail("%s/%s mismatches %s" % (suite, case, key))
    # The optimized binary may deliberately differ after a model change, but
    # baseline and default must remain a matched executable pair.
    for key in ("sim_bin_sha256", "gpgpusim_source_commit",
                "non_backend_config_sha256"):
        if metas["baseline"].get(key) != metas["decoupled"].get(key):
            fail("%s/%s baseline/default mismatch: %s" % (suite, case, key))
    values = {arm: measurements(run_dir) for arm, run_dir in runs.items()}
    row = {
        "group": group,
        "suite": suite,
        "case": case,
        "default_speedup": values["baseline"]["cycles"] / values["decoupled"]["cycles"],
        "optimized_speedup": values["baseline"]["cycles"] / values["optimized"]["cycles"],
        "optimized_vs_default": values["decoupled"]["cycles"] / values["optimized"]["cycles"],
        "trace_sha256": metas["baseline"]["trace_kernelslist_sha256"],
        "baseline_dir": str(runs["baseline"]),
        "decoupled_dir": str(runs["decoupled"]),
        "optimized_dir": str(runs["optimized"]),
    }
    for arm, value in values.items():
        for field, measurement in value.items():
            row["%s_%s" % (arm, field)] = measurement
    return row


def geometric_mean(values):
    return math.exp(sum(math.log(value) for value in values) / len(values))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", action="append", nargs=2,
                        metavar=("NAME", "SUMMARY_CSV"), required=True)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--markdown", required=True)
    args = parser.parse_args()

    cases = {}
    for group, name in args.group:
        path = Path(name)
        for row in read_summary(group, path):
            key = (group, row["suite"], row["case"])
            arms = cases.setdefault(key, {})
            if row["arm"] in arms:
                fail("duplicate %s arm in %s" % (row["arm"], key))
            arms[row["arm"]] = row
    rows = [validate_case(*key, arms) for key, arms in sorted(cases.items())]
    fields = list(rows[0]) if rows else []
    with open(args.csv, "w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    grouped = {}
    for row in rows:
        grouped.setdefault(row["group"], []).append(row)
    with open(args.markdown, "w") as output:
        output.write("# Decoupled-L2 three-arm results\n\n")
        output.write("Every listed case has normal exits and matched baseline/default "
                     "binary plus trace provenance. Aggregates are kept within groups.\n\n")
        for group, group_rows in grouped.items():
            output.write("## %s\n\n" % group)
            output.write("| Case | Default speedup | Optimized speedup | Optimized/default | "
                         "Baseline / Default / Optimized wall time | Baseline / Default / Optimized peak RSS |\n")
            output.write("|---|---:|---:|---:|---:|---:|\n")
            for row in group_rows:
                output.write("| %s | %.4fx | %.4fx | %.4fx | %ss / %ss / %ss | "
                             "%.2f / %.2f / %.2f GiB |\n" %
                             (row["case"], row["default_speedup"],
                              row["optimized_speedup"], row["optimized_vs_default"],
                              row["baseline_wall_seconds"], row["decoupled_wall_seconds"],
                              row["optimized_wall_seconds"],
                              row["baseline_max_rss_kib"] / (1024 * 1024),
                              row["decoupled_max_rss_kib"] / (1024 * 1024),
                              row["optimized_max_rss_kib"] / (1024 * 1024)))
            output.write("| geometric mean | %.4fx | %.4fx | %.4fx | — | — |\n\n" % (
                geometric_mean([row["default_speedup"] for row in group_rows]),
                geometric_mean([row["optimized_speedup"] for row in group_rows]),
                geometric_mean([row["optimized_vs_default"] for row in group_rows]),
            ))


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print("error: %s" % error, file=sys.stderr)
        sys.exit(1)
