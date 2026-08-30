#!/usr/bin/env python3
"""Fail-closed aggregation for the independent EPL2MOTV1 telemetry family."""
import argparse, csv, hashlib, json
from collections import defaultdict
from pathlib import Path

SCHEMA = "EPL2MOTV1"
BINS = ("<=8", "9-16", "17-32", "33-64", "65-128", "129-256",
        "257-512", "513-1024", ">1024")
BIN_KEYS = ("reuse_le8", "reuse_9_16", "reuse_17_32", "reuse_33_64",
            "reuse_65_128", "reuse_129_256", "reuse_257_512",
            "reuse_513_1024", "reuse_gt1024")

def parse(line):
    p = line.rstrip().split("|")
    if not p or p[0] != SCHEMA: return None
    row = {}
    for item in p[1:]:
        if "=" not in item: raise ValueError("malformed EPL2MOTV1 field: " + item)
        k, v = item.split("=", 1)
        if k in row: raise ValueError("duplicate field " + k)
        row[k] = v if k == "scope" else int(v)
    return row

def write(path, rows):
    keys = sorted({k for row in rows for k in row})
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("log", type=Path); ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--workload", required=True); ap.add_argument("--framework-commit", required=True)
    ap.add_argument("--core-commit", required=True); args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    apps, duplicate_terminal_records = {}, 0
    # Deliberately one-pass over the raw log: broad-campaign logs can be GBs.
    with args.log.open("r", encoding="utf-8", errors="replace") as source:
        for line in source:
            row = parse(line)
            if row is None or row["scope"] != "application": continue
            if row["slice"] in apps:
                # GPGPU-Sim can invoke the terminal stats printer twice.  A
                # byte-for-byte equivalent terminal record is a repeat of the
                # same observation, not another epoch; retain the first.  A
                # differing repeat is ambiguous and must fail closed.
                if row != apps[row["slice"]]:
                    raise ValueError("conflicting application slice record %d" % row["slice"])
                duplicate_terminal_records += 1
                continue
            apps[row["slice"]] = row
    if len(apps) != 64: raise ValueError("expected exactly 64 application slice records, found %d" % len(apps))
    vals = list(apps.values()); total = defaultdict(int)
    for row in vals:
        for k, v in row.items():
            if isinstance(v, int) and k not in ("slice", "kernel_uid"): total[k] += v
    if total["wb_packets_lower_accepted"] > total["wb_packets_created"]:
        raise ValueError("shadow WBUF accepted more packets than it created")
    terminal_wbuf_outstanding = total["wb_packets_created"] - total["wb_packets_lower_accepted"]
    reuse = {"workload": args.workload, "reuse_instances": total["reuse_instances"]}
    for label, key in zip(BINS, BIN_KEYS): reuse[label] = (total[key] / total["reuse_instances"] if total["reuse_instances"] else "NA")
    if total["reuse_instances"] and abs(sum(reuse[x] for x in BINS) - 1.0) > 1e-12: raise ValueError("reuse normalization failed")
    coverage = {"workload": args.workload, "eligible_demand_references": total["eligible_demand_references"],
        "reuse_instances": total["reuse_instances"], "unique_lines": total["unique_lines"],
        "unique_lines_reused_at_least_once": total["unique_lines_reused"], "one_touch_unique_lines": total["one_touch_unique_lines"],
        "reuse_instance_fraction": total["reuse_instances"] / total["eligible_demand_references"] if total["eligible_demand_references"] else "NA",
        "line_reuse_coverage": total["unique_lines_reused"] / total["unique_lines"] if total["unique_lines"] else "NA",
        "one_touch_line_fraction": total["one_touch_unique_lines"] / total["unique_lines"] if total["unique_lines"] else "NA"}
    blocking, sensitivity = [], []
    for c in (4, 8, 16):
        denom = total["blocked_miss_cycles_%d" % c]
        cats = ("set_assoc", "mshr_meta", "missq_lower", "wb_path", "other")
        counts = [total["%s_%d" % (x, c)] for x in cats]
        if sum(counts) != denom: raise ValueError("exclusive accounting failed for WBUF%d" % c)
        blocking.append(dict(workload=args.workload, wbuf_capacity=c, projected_blocked_miss_admission_cycles=denom,
            eligible_miss_admission_cycles=total["eligible_miss_cycles_%d" % c], **dict(zip(cats, counts))))
        sensitivity.append({"workload": args.workload, "wbuf_capacity": c,
            "wbuf_alloc_opportunities": total["wbuf_opportunities_%d" % c],
            "wbuf_trace_projected_would_block_cycles": total["wbuf_would_block_%d" % c],
            "projected_blocked_miss_admission_cycles": denom})
    post = {"workload": args.workload, "real_evictions": total["post_evictions"], "post_eviction_rereferences": total["post_eviction_rerefs"],
        "post_eviction_referenced_fraction": total["post_eviction_rerefs"] / total["post_evictions"] if total["post_evictions"] else "NA",
        "post_eviction_sequence_distance_avg": total["post_eviction_seq_sum"] / total["post_eviction_rerefs"] if total["post_eviction_rerefs"] else "NA",
        "post_eviction_cycle_distance_avg": total["post_eviction_cycle_sum"] / total["post_eviction_rerefs"] if total["post_eviction_rerefs"] else "NA"}
    life = {"workload": args.workload, "wb_packets_created": total["wb_packets_created"], "wb_packets_lower_accepted": total["wb_packets_lower_accepted"], "wb_packets_terminally_outstanding": terminal_wbuf_outstanding,
        "wb_packet_creation_to_lower_accept_cycles_avg": total["wb_lifetime_sum"] / total["wb_packets_lower_accepted"] if total["wb_packets_lower_accepted"] else "NA", "max": total["wb_lifetime_max"]}
    write(args.out / "reuse_distance.csv", [reuse]); write(args.out / "reuse_coverage.csv", [coverage]); write(args.out / "blocking_breakdown.csv", blocking)
    write(args.out / "wbuf_sensitivity.csv", sensitivity); write(args.out / "post_eviction_reuse.csv", [post]); write(args.out / "wbuf_lifetime.csv", [life])
    write(args.out / "motivation_summary.csv", [dict(workload=args.workload, terminal_record_duplicates_ignored=duplicate_terminal_records, **total)])
    args.out.joinpath("manifest.json").write_text(json.dumps({"schema_version": SCHEMA, "workload": args.workload, "framework_commit": args.framework_commit, "core_commit": args.core_commit, "source_log_sha256": digest(args.log), "identical_terminal_records_ignored": duplicate_terminal_records}, indent=2, sort_keys=True) + "\n")

if __name__ == "__main__":
    try: main()
    except (OSError, ValueError) as e: raise SystemExit("EPL2MOTV1 parser error: %s" % e)
