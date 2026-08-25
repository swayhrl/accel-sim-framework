#!/usr/bin/env python3
"""Gate and summarize a config-only Decoupled-L2 bank optimization."""

import argparse
import csv
import hashlib
import sys
from pathlib import Path

from analyze_decoupled_l2_bank_observability import (
    fail,
    last_metric,
    parse_decoupled,
    read_provenance,
    validate_runtime_exit,
)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_case(name, default_dir, optimized_dir, overlay, bank_hash, banks):
    default_dir = Path(default_dir)
    optimized_dir = Path(optimized_dir)
    validate_runtime_exit(default_dir)
    validate_runtime_exit(optimized_dir)
    default_meta = read_provenance(default_dir)
    optimized_meta = read_provenance(optimized_dir)
    for arm, meta in (("default", default_meta), ("optimized", optimized_meta)):
        if meta.get("backend") != "decoupled":
            fail("%s %s arm has backend %r" % (name, arm, meta.get("backend")))
    for key in ("sim_bin_sha256", "gpgpusim_source_commit",
                "trace_kernelslist_sha256"):
        if default_meta.get(key) != optimized_meta.get(key):
            fail("%s changes %s outside the config-only experiment" % (name, key))
    if default_meta.get("config_extra_sha256") not in (None, ""):
        fail("%s default arm unexpectedly has a config overlay" % name)
    if optimized_meta.get("config_extra_sha256") != sha256(overlay):
        fail("%s optimized arm does not record the requested overlay" % name)

    default = parse_decoupled(default_dir, "mod", 4)
    optimized = parse_decoupled(optimized_dir, bank_hash, banks)
    default_text = (default_dir / "smoke.out").read_text(errors="replace")
    optimized_text = (optimized_dir / "smoke.out").read_text(errors="replace")
    row = {
        "case": name,
        "trace_kernelslist_sha256": default_meta["trace_kernelslist_sha256"],
        "sim_bin_sha256": default_meta["sim_bin_sha256"],
        "gpgpusim_source_commit": default_meta["gpgpusim_source_commit"],
        "default_cycles": int(last_metric(default_text, "gpu_tot_sim_cycle")),
        "optimized_cycles": int(last_metric(optimized_text, "gpu_tot_sim_cycle")),
        "default_ipc": last_metric(default_text, "gpu_tot_ipc"),
        "optimized_ipc": last_metric(optimized_text, "gpu_tot_ipc"),
        "default_tag_requeue": default["bank_requeue_tag"],
        "optimized_tag_requeue": optimized["bank_requeue_tag"],
        "default_lower_requeue": default["bank_requeue_lower"],
        "optimized_lower_requeue": optimized["bank_requeue_lower"],
        "default_tag_max_share": default["tag_grant_max_share"],
        "optimized_tag_max_share": optimized["tag_grant_max_share"],
        "default_lower_max_share": default["lower_grant_max_share"],
        "optimized_lower_max_share": optimized["lower_grant_max_share"],
        "default_dir": str(default_dir),
        "optimized_dir": str(optimized_dir),
    }
    row["speedup"] = row["default_cycles"] / row["optimized_cycles"]
    row["tag_requeue_change"] = (
        row["optimized_tag_requeue"] / row["default_tag_requeue"]
        if row["default_tag_requeue"] else 0.0
    )
    row["lower_requeue_change"] = (
        row["optimized_lower_requeue"] / row["default_lower_requeue"]
        if row["default_lower_requeue"] else 0.0
    )
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair", action="append", nargs=3,
                        metavar=("CASE", "DEFAULT", "OPTIMIZED"), required=True)
    parser.add_argument("--optimized-config-extra", required=True)
    parser.add_argument("--expected-bank-hash", default="mod")
    parser.add_argument("--expected-internal-banks", type=int, default=8)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--markdown", required=True)
    args = parser.parse_args()
    if not Path(args.optimized_config_extra).is_file():
        fail("missing optimized config overlay: %s" % args.optimized_config_extra)
    rows = [validate_case(name, default_dir, optimized_dir,
                          args.optimized_config_extra, args.expected_bank_hash,
                          args.expected_internal_banks)
            for name, default_dir, optimized_dir in args.pair]
    fields = list(rows[0]) if rows else []
    with Path(args.csv).open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with Path(args.markdown).open("w") as output:
        output.write("# Decoupled-L2 bank optimization gate\n\n")
        output.write("Each result has normal exits, a matched decoupled binary/source/trace, "
                     "a default four-bank mod arm, and only the named optimized overlay.\n\n")
        output.write("| Case | Default / optimized IPC | Default / optimized cycles | "
                     "Speedup | Tag requeue change | Lower-read requeue change |\n")
        output.write("|---|---:|---:|---:|---:|---:|\n")
        for row in rows:
            output.write("| {case} | {default_ipc:.4f} / {optimized_ipc:.4f} | "
                         "{default_cycles} / {optimized_cycles} | {speedup:.4f}x | "
                         "{tag_requeue_change:.4f}x | {lower_requeue_change:.4f}x |\n".format(**row))


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print("error: %s" % error, file=sys.stderr)
        sys.exit(1)
