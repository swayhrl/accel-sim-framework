#!/usr/bin/env python3
"""Summarize final decoupled-L2 bank/occupancy statistics from matched runs."""

import argparse
import csv
import re
import sys
from pathlib import Path


DETAIL_RE = re.compile(r"decoupled_l2_detail\[(?P<slice>[^]]+)\]: (?P<body>.*)")
SUMMARY_RE = re.compile(r"decoupled_l2\[(?P<slice>[^]]+)\]: (?P<body>.*)")
CONFLICT_RE = re.compile(r"decoupled_l2_conflict\[(?P<slice>[^]]+)\]: (?P<body>.*)")
KIND_RE = re.compile(r"decoupled_l2_kind\[(?P<slice>[^]]+)\]: (?P<body>.*)")
BANK_RE = re.compile(r"decoupled_l2_bank_detail\[(?P<slice>[^]]+)\]:(?P<body>.*)")
KV_RE = re.compile(r"([A-Za-z_]+)=([^\s]+)")
TRIPLE_RE = re.compile(r"(tag_read|tag_write|tag_atomic|lower_read|lower_write|lower_atomic)=(\d+)/(\d+)/(\d+)")
BANK_TRIPLE_RE = re.compile(r"(\d+):t=(\d+)/(\d+)/(\d+),l=(\d+)/(\d+)/(\d+)")


def fail(message):
    raise RuntimeError(message)


def read_provenance(run_dir):
    result = {}
    path = run_dir / "simulator_provenance.txt"
    for line in path.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key] = value
    return result


def validate_runtime_exit(run_dir):
    path = run_dir / "runtime_metrics.txt"
    if not path.is_file():
        fail("missing runtime metrics: %s" % run_dir)
    metrics = {}
    for line in path.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            metrics[key] = value
    if metrics.get("sim_exit_status") != "0":
        fail("nonzero simulator exit: %s" % run_dir)


def normalized_config(run_dir):
    path = run_dir / "gpgpusim.config"
    return "\n".join(
        line for line in path.read_text().splitlines()
        if not line.startswith("-gpgpu_l2_backend ")
    )


def last_metric(text, name):
    values = re.findall(r"%s =\s*([0-9]+(?:\.[0-9]+)?)" % re.escape(name), text)
    if not values:
        fail("missing %s" % name)
    return float(values[-1])


def value_or_na(value):
    return "n/a" if value is None else value


def parse_decoupled(run_dir, expected_bank_hash, expected_internal_banks):
    text = (run_dir / "smoke.out").read_text(errors="replace")
    if "GPGPU-Sim: *** exit detected ***" not in text:
        fail("%s did not exit normally" % run_dir)
    slices = {}
    for line in text.splitlines():
        match = SUMMARY_RE.search(line)
        if match:
            slices.setdefault(match.group("slice"), {}).update(
                {key: value for key, value in KV_RE.findall(match.group("body"))}
            )
            continue
        match = DETAIL_RE.search(line)
        if match:
            slices.setdefault(match.group("slice"), {}).update(
                {key: value for key, value in KV_RE.findall(match.group("body"))}
            )
            continue
        match = CONFLICT_RE.search(line)
        if match:
            slices.setdefault(match.group("slice"), {}).update(
                {key: value for key, value in KV_RE.findall(match.group("body"))}
            )
            continue
        match = KIND_RE.search(line)
        if match:
            slices.setdefault(match.group("slice"), {})["kinds"] = {
                key: tuple(map(int, values))
                for key, *values in TRIPLE_RE.findall(match.group("body"))
            }
            continue
        match = BANK_RE.search(line)
        if match:
            slices.setdefault(match.group("slice"), {})["banks"] = [
                tuple(map(int, values))
                for values in BANK_TRIPLE_RE.findall(match.group("body"))
            ]
    if not slices:
        fail("%s has no decoupled detail lines" % run_dir)
    required = {"req_avg", "req_max", "tag_avg", "tag_max", "aad_avg", "aad_max",
                "fill_avg", "fill_max", "wbq_avg", "wbq_max", "bank_requeue_tag",
                "bank_requeue_lower", "kinds", "banks"}
    for name, data in slices.items():
        missing = required - set(data)
        if missing:
            fail("%s %s lacks %s" % (run_dir, name, sorted(missing)))

    row = {"slices": len(slices)}
    hashes = {data["bank_hash"] for data in slices.values()}
    if len(hashes) != 1:
        fail("%s mixes bank hashes %s" % (run_dir, hashes))
    row["bank_hash"] = hashes.pop()
    if row["bank_hash"] != expected_bank_hash:
        fail("%s has bank hash %s, expected %s" %
             (run_dir, row["bank_hash"], expected_bank_hash))
    for resource in ("req", "tag", "aad", "fill", "wbq"):
        row[resource + "_avg_sum"] = sum(float(data[resource + "_avg"])
                                          for data in slices.values())
        # Each cache slice samples its own queues.  Keep the aggregate sum for
        # capacity accounting, but report the per-slice mean beside the peak
        # of one slice; comparing an aggregate mean to a per-slice peak is
        # otherwise misleading when there are many L2 slices.
        row[resource + "_avg_per_slice"] = (
            row[resource + "_avg_sum"] / len(slices)
        )
        row[resource + "_max_slice"] = max(int(data[resource + "_max"])
                                            for data in slices.values())
    for key in ("bank_requeue_tag", "bank_requeue_lower", "tag_tag", "tag_lower",
                "tag_fill", "tag_wbq", "lower_tag", "lower_lower", "lower_fill",
                "lower_wbq", "access", "hit", "miss", "write", "wb", "atomic",
                "token_stall", "aad_stall", "read_credit_stall", "bank_stall"):
        row[key] = sum(int(data.get(key, 0)) for data in slices.values())
    # `wbq_stall` was added after the first diagnostic binary.  Treat absent
    # counters as unavailable rather than silently converting old logs to zero.
    row["wbq_stall"] = (
        sum(int(data["wbq_stall"]) for data in slices.values())
        if all("wbq_stall" in data for data in slices.values()) else None
    )
    for key in ("tag_read", "tag_write", "tag_atomic", "lower_read", "lower_write",
                "lower_atomic"):
        row[key + "_attempt"] = sum(data["kinds"][key][0] for data in slices.values())
        row[key + "_grant"] = sum(data["kinds"][key][1] for data in slices.values())
        row[key + "_requeue"] = sum(data["kinds"][key][2] for data in slices.values())

    bank_count = len(next(iter(slices.values()))["banks"])
    if bank_count != expected_internal_banks:
        fail("%s has %d internal banks, expected %d" %
             (run_dir, bank_count, expected_internal_banks))
    tag_grants = [0] * bank_count
    lower_grants = [0] * bank_count
    tag_requeues = [0] * bank_count
    lower_requeues = [0] * bank_count
    for data in slices.values():
        if len(data["banks"]) != bank_count:
            fail("%s has inconsistent internal bank counts" % run_dir)
        for bank, values in enumerate(data["banks"]):
            _, _, tag_grant, tag_requeue, _, lower_grant, lower_requeue = values
            tag_grants[bank] += tag_grant
            lower_grants[bank] += lower_grant
            tag_requeues[bank] += tag_requeue
            lower_requeues[bank] += lower_requeue
    row["internal_banks"] = bank_count
    tag_attempts = [sum(data["banks"][bank][1] for data in slices.values())
                    for bank in range(bank_count)]
    lower_attempts = [sum(data["banks"][bank][4] for data in slices.values())
                      for bank in range(bank_count)]
    for prefix, values in (("tag_grant", tag_grants), ("lower_grant", lower_grants),
                           ("tag_requeue", tag_requeues),
                           ("lower_requeue", lower_requeues)):
        total = sum(values)
        row[prefix + "_max_share"] = max(values) / total if total else 0.0
        row[prefix + "_min_share"] = min(values) / total if total else 0.0
    def share(value, values):
        total = sum(values)
        return value / total if total else 0.0

    row["_bank_rows"] = []
    for bank in range(bank_count):
        row["_bank_rows"].append({
            "bank": bank,
            "tag_attempt": tag_attempts[bank],
            "tag_attempt_share": share(tag_attempts[bank], tag_attempts),
            "tag_grant": tag_grants[bank],
            "tag_grant_share": share(tag_grants[bank], tag_grants),
            "tag_requeue": tag_requeues[bank],
            "tag_requeue_share": share(tag_requeues[bank], tag_requeues),
            "lower_attempt": lower_attempts[bank],
            "lower_attempt_share": share(lower_attempts[bank], lower_attempts),
            "lower_grant": lower_grants[bank],
            "lower_grant_share": share(lower_grants[bank], lower_grants),
            "lower_requeue": lower_requeues[bank],
            "lower_requeue_share": share(lower_requeues[bank], lower_requeues),
        })
    return row


def validate_pair(name, baseline, decoupled, expected_bank_hash,
                  expected_internal_banks):
    baseline_text = (baseline / "smoke.out").read_text(errors="replace")
    if "GPGPU-Sim: *** exit detected ***" not in baseline_text:
        fail("%s baseline did not exit normally" % name)
    validate_runtime_exit(baseline)
    validate_runtime_exit(decoupled)
    bp = read_provenance(baseline)
    dp = read_provenance(decoupled)
    for key in ("sim_bin_sha256", "gpgpusim_source_commit",
                "trace_kernelslist_sha256"):
        if bp.get(key) != dp.get(key):
            fail("%s mismatches %s" % (name, key))
    if normalized_config(baseline) != normalized_config(decoupled):
        fail("%s differs outside gpgpu_l2_backend" % name)
    if bp.get("backend") != "baseline" or dp.get("backend") != "decoupled":
        fail("%s has unexpected backend provenance" % name)
    baseline_cycles = last_metric(baseline_text, "gpu_tot_sim_cycle")
    baseline_instructions = last_metric(baseline_text, "gpu_tot_sim_insn")
    baseline_ipc = last_metric(baseline_text, "gpu_tot_ipc")
    dec_text = (decoupled / "smoke.out").read_text(errors="replace")
    decoupled_cycles = last_metric(dec_text, "gpu_tot_sim_cycle")
    decoupled_instructions = last_metric(dec_text, "gpu_tot_sim_insn")
    decoupled_ipc = last_metric(dec_text, "gpu_tot_ipc")
    row = parse_decoupled(decoupled, expected_bank_hash,
                          expected_internal_banks)
    row.update({"case": name, "baseline_cycles": int(baseline_cycles),
                "decoupled_cycles": int(decoupled_cycles),
                "baseline_instructions": int(baseline_instructions),
                "decoupled_instructions": int(decoupled_instructions),
                "baseline_ipc": baseline_ipc, "decoupled_ipc": decoupled_ipc,
                "speedup": baseline_cycles / decoupled_cycles,
                "baseline_dir": str(baseline), "decoupled_dir": str(decoupled),
                "sim_bin_sha256": bp["sim_bin_sha256"],
                "trace_kernelslist_sha256": bp["trace_kernelslist_sha256"]})
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair", action="append", nargs=3, metavar=("CASE", "BASELINE", "DECOUPLED"),
                        required=True)
    parser.add_argument("--expected-bank-hash", default="mod")
    parser.add_argument("--expected-internal-banks", type=int, default=4)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--bank-csv")
    parser.add_argument("--markdown", required=True)
    args = parser.parse_args()
    rows = [validate_pair(name, Path(baseline), Path(decoupled),
                          args.expected_bank_hash, args.expected_internal_banks)
            for name, baseline, decoupled in args.pair]
    bank_rows = []
    for row in rows:
        for bank_row in row.pop("_bank_rows"):
            bank_row.update({
                "case": row["case"],
                "bank_hash": row["bank_hash"],
                "internal_banks": row["internal_banks"],
            })
            bank_rows.append(bank_row)
    fields = sorted({key for row in rows for key in row})
    with open(args.csv, "w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    bank_csv = Path(args.bank_csv) if args.bank_csv else Path(args.csv).with_name(
        Path(args.csv).stem + "_by_bank.csv"
    )
    bank_fields = ["case", "bank_hash", "internal_banks", "bank", "tag_attempt",
                   "tag_attempt_share", "tag_grant", "tag_grant_share",
                   "tag_requeue", "tag_requeue_share", "lower_attempt",
                   "lower_attempt_share", "lower_grant", "lower_grant_share",
                   "lower_requeue", "lower_requeue_share"]
    with open(bank_csv, "w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=bank_fields)
        writer.writeheader()
        writer.writerows(bank_rows)
    with open(args.markdown, "w") as output:
        output.write("# Decoupled-L2 bank observability\n\n")
        output.write("Every pair passed normal-exit, binary-hash, trace-hash, and non-backend configuration gates.\n\n")
        output.write("`%s` contains summed per-slice attempts, grants, and requeues for every internal bank.\n\n" % bank_csv.name)
        output.write("| Case | Baseline / Decoupled IPC | Baseline / Decoupled cycles | Speedup | req avg/peak per slice | AAD avg/peak per slice | fill avg/peak per slice | WBQ avg/peak per slice | read-credit / WBQ stall | tag/lower requeue | tag max share | lower max share |\n")
        output.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for row in rows:
            output.write("| {case} | {baseline_ipc:.4f} / {decoupled_ipc:.4f} | "
                         "{baseline_cycles} / {decoupled_cycles} | {speedup:.4f}x | "
                         "{req_avg_per_slice:.2f}/{req_max_slice} | "
                         "{aad_avg_per_slice:.2f}/{aad_max_slice} | {fill_avg_per_slice:.2f}/{fill_max_slice} | "
                         "{wbq_avg_per_slice:.2f}/{wbq_max_slice} | {read_credit_stall} / {wbq_stall_display} | "
                         "{bank_requeue_tag}/{bank_requeue_lower} | "
                         "{tag_grant_max_share:.2%} | {lower_grant_max_share:.2%} |\n".format(
                             wbq_stall_display=value_or_na(row["wbq_stall"]), **row))
        output.write("\n| Case | Tag-bank owner: tag / lower / fill / WBQ | Lower-read-bank owner: tag / lower / fill / WBQ | Tag attempts R / W / atomic | Lower attempts R / W / atomic |\n")
        output.write("|---|---:|---:|---:|---:|\n")
        for row in rows:
            output.write("| {case} | {tag_tag} / {tag_lower} / {tag_fill} / {tag_wbq} | "
                         "{lower_tag} / {lower_lower} / {lower_fill} / {lower_wbq} | "
                         "{tag_read_attempt} / {tag_write_attempt} / {tag_atomic_attempt} | "
                         "{lower_read_attempt} / {lower_write_attempt} / {lower_atomic_attempt} |\n".format(**row))


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print("error: %s" % error, file=sys.stderr)
        sys.exit(1)
