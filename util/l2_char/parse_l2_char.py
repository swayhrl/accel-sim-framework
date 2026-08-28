#!/usr/bin/env python3
"""Parse versioned L2CHARV1 simulator records into portable CSV artifacts."""
import argparse
import csv
import hashlib
import json
import pathlib
import subprocess
import sys
import math

from schema_v1 import REQUIRED_SLICE_FIELDS, REQUIRED_WINDOW_FIELDS, SCHEMA_VERSION, as_number


def sha256(path):
    if not path:
        return "NA"
    h = hashlib.sha256()
    with open(path, "rb") as src:
        for chunk in iter(lambda: src.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_record(line):
    parts = line.rstrip().split("|")
    if len(parts) < 3 or parts[0] != SCHEMA_VERSION:
        return None
    fields = {}
    for item in parts[2:]:
        if "=" not in item:
            raise ValueError("malformed L2CHARV1 field: %s" % item)
        key, value = item.split("=", 1)
        fields[key] = as_number(value)
    return parts[1], fields


def require(row, fields, label):
    missing = [key for key in fields if key not in row]
    if missing:
        raise ValueError("%s missing mandatory fields: %s" % (label, ",".join(missing)))


def write_csv(path, rows):
    keys = sorted({key for row in rows for key in row})
    with open(path, "w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=keys, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def git_value(repo, command):
    try:
        return subprocess.check_output(["git", "-C", repo] + command,
                                       text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "NA"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("log")
    parser.add_argument("--out", required=True)
    parser.add_argument("--workload", default="NA")
    parser.add_argument("--input", default="NA")
    parser.add_argument("--kernel", default="NA")
    parser.add_argument("--kernel-id", default="NA")
    parser.add_argument("--config")
    parser.add_argument("--trace")
    parser.add_argument("--framework-repo", default=".")
    parser.add_argument("--core-repo", default="NA")
    parser.add_argument("--command", default="NA")
    parser.add_argument("--production", action="store_true",
                        help="require complete workload and source provenance")
    args = parser.parse_args()
    pathlib.Path(args.out).mkdir(parents=True, exist_ok=True)

    # The simulator can print an intermediate per-kernel statistics snapshot
    # before the terminal drain snapshot.  A snapshot is emitted slice-major,
    # beginning at slice zero.  Keep only the final complete snapshot so a
    # multi-kernel run cannot silently duplicate temporal windows.
    snapshots = []
    slices, details, windows, invariants, hists = {}, {}, [], [], {}
    with open(args.log, encoding="utf-8", errors="replace") as source:
        for raw in source:
            parsed = parse_record(raw)
            if not parsed:
                continue
            kind, fields = parsed
            if kind == "SLICE":
                if fields.get("slice") == 0 and slices:
                    snapshots.append((slices, details, windows, invariants, hists))
                    slices, details, windows, invariants, hists = {}, {}, [], [], {}
                require(fields, REQUIRED_SLICE_FIELDS, "SLICE")
                slices[str(fields["slice"])] = fields
            elif kind == "SLICE_DETAIL":
                details[str(fields.get("slice", "NA"))] = fields
            elif kind == "WINDOW":
                require(fields, REQUIRED_WINDOW_FIELDS, "WINDOW")
                windows.append(fields)
            elif kind == "INVARIANT":
                invariants.append(fields)
            elif kind == "HIST":
                hists[(str(fields.get("slice", "NA")), fields.get("metric", "NA"))] = fields
            elif kind != "SUMMARY":
                raise ValueError("unknown L2CHARV1 record type: %s" % kind)
    if slices:
        snapshots.append((slices, details, windows, invariants, hists))
    if not snapshots:
        raise ValueError("no L2CHARV1|SLICE records found")
    slices, details, windows, invariants, hists = snapshots[-1]
    windows.sort(key=lambda r: (int(r["slice"]), int(r["window"])))
    for key, row in slices.items():
        row.update(details.get(key, {}))
        row["schema_version"] = SCHEMA_VERSION
    write_csv(pathlib.Path(args.out) / "slice.csv", list(slices.values()))
    for row in windows:
        row["schema_version"] = SCHEMA_VERSION
    write_csv(pathlib.Path(args.out) / "window.csv", windows)
    framework_commit = git_value(args.framework_repo, ["rev-parse", "HEAD"])
    core_commit = git_value(args.core_repo, ["rev-parse", "HEAD"]) if args.core_repo != "NA" else "NA"
    framework_branch = git_value(args.framework_repo, ["branch", "--show-current"])
    core_branch = git_value(args.core_repo, ["branch", "--show-current"]) if args.core_repo != "NA" else "NA"
    provenance = [args.workload, args.input, args.kernel, args.kernel_id, args.config,
                  args.trace, args.command, framework_commit, core_commit,
                  framework_branch, core_branch]
    if args.production and any(v in (None, "", "NA") for v in provenance):
        raise ValueError("production mode requires workload/input/kernel/kernel-id, config, trace, command, and both git repos")
    summary = {"schema_version": SCHEMA_VERSION, "workload": args.workload,
               "input": args.input, "kernel": args.kernel, "kernel_id": args.kernel_id,
               "framework_commit": framework_commit, "core_commit": core_commit,
               "framework_branch": framework_branch, "core_branch": core_branch,
               "command": args.command, "gpu_config": args.config or "NA", "trace": args.trace or "NA",
               "gpu_config_sha256": sha256(args.config), "trace_sha256": sha256(args.trace),
               "slice_count": len(slices), "invariant_records": len(invariants),
               "invariants_pass": int(all(r.get("status") == "PASS" for r in invariants))}
    for metric in ("reserved_util_avg", "mshr_util_avg", "missq_util_avg", "missq_wb_util_avg",
                   "draml2q_util_avg", "l2dramq_util_avg", "data_busy_ratio", "fill_busy_ratio",
                   "merge_depth_avg", "merge_limit_entries_util_avg", "set_reserved_full_ratio"):
        values = [r[metric] for r in slices.values() if metric in r and isinstance(r[metric], (int, float))]
        if values:
            mean = sum(values) / len(values)
            summary[metric] = mean
            summary[metric + "_slice_max_over_mean"] = max(values) / mean if mean else "NA"
            summary[metric + "_slice_cv"] = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values)) / mean if mean else "NA"
    for metric in ("block_set", "block_mshr_new", "block_mshr_merge", "block_missq", "block_dataport", "block_respq", "fill"):
        eligible = sum(r.get(metric + "_eligible", 0) for r in slices.values() if isinstance(r.get(metric + "_eligible", 0), (int, float)))
        blocked = sum(r.get(metric + "_blocked", 0) for r in slices.values() if isinstance(r.get(metric + "_blocked", 0), (int, float)))
        summary[metric + "_eligible"] = eligible; summary[metric + "_blocked"] = blocked
        summary[metric + "_blocking_ratio"] = blocked / eligible if eligible else "NA"
    wb_req = sum(r.get("l2dram_wb_requests", 0) for r in slices.values())
    req = sum(r.get("l2dram_requests", 0) for r in slices.values())
    wb_bytes = sum(r.get("l2dram_wb_bytes", 0) for r in slices.values())
    total_bytes = sum(r.get("l2dram_bytes", 0) for r in slices.values())
    summary["wb_request_fraction"] = wb_req / req if req else "NA"
    summary["wb_byte_fraction"] = wb_bytes / total_bytes if total_bytes else "NA"
    for metric in ("reserved", "mshr", "merge_depth", "missq", "missq_wb"):
        merged = []
        for (_, name), hist in hists.items():
            if name == metric: merged.append([int(x) for x in str(hist["bins"]).split(",")])
        if merged:
            bins = [sum(v[i] if i < len(v) else 0 for v in merged) for i in range(max(map(len, merged)))]
            samples = sum(bins); total = sum(i * n for i, n in enumerate(bins))
            def p(q):
                rank = (samples * q + 99) // 100; seen = 0
                for i, n in enumerate(bins):
                    seen += n
                    if seen >= rank: return i
            summary[metric + "_global_p50"] = p(50); summary[metric + "_global_p95"] = p(95)
            summary[metric + "_global_max"] = len(bins) - 1
            summary[metric + "_global_avg"] = total / samples
    write_csv(pathlib.Path(args.out) / "summary.csv", [summary])
    manifest = {"schema_version": SCHEMA_VERSION, "framework_commit": summary["framework_commit"],
                "core_commit": summary["core_commit"], "framework_branch": framework_branch,
                "core_branch": core_branch,
                "gpu_config": args.config or "NA", "gpu_config_sha256": summary["gpu_config_sha256"],
                "trace": args.trace or "NA", "trace_sha256": summary["trace_sha256"], "command": args.command,
                "characterization": {"enabled": True, "window_l2_cycles": "from raw records", "set_detail": "from raw records"}}
    with open(pathlib.Path(args.out) / "manifest.json", "w") as out:
        json.dump(manifest, out, indent=2, sort_keys=True)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print("L2CHARV1 parser error: %s" % error, file=sys.stderr)
        sys.exit(2)
