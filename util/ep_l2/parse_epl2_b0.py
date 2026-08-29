#!/usr/bin/env python3
"""Parse independent EPL2B0V1 records into target-baseline CSV artifacts."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

SCHEMA = "EPL2B0V1"
L1_SCHEMA = "EPL2L1V1"
DRAM_SCHEMA = "EPL2DRAMV1"
APPLICATION_UID = (1 << 64) - 1


def value(text):
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return text


def record(line):
    parts = line.rstrip().split("|")
    if len(parts) < 2 or parts[0] not in (SCHEMA, L1_SCHEMA, DRAM_SCHEMA):
        return None
    fields = {}
    kind, start = ("SNAPSHOT", 1) if "=" in parts[1] else (parts[1], 2)
    for item in parts[start:]:
        if "=" not in item:
            raise ValueError("malformed EPL2B0V1 field: " + item)
        key, raw = item.split("=", 1)
        fields[key] = value(raw)
    return parts[0], kind, fields


def write_csv(path, rows):
    keys = sorted({key for row in rows for key in row})
    with path.open("w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path):
    if not path:
        return "NA"
    h = hashlib.sha256()
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--framework-commit", default="NA")
    parser.add_argument("--core-commit", default="NA")
    parser.add_argument("--source-log", type=Path,
                        help="optional provenance input hashed into manifest")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    application, kernels, windows, invariants, l1, dram = [], [], [], [], [], []
    for line in args.log.read_text(encoding="utf-8", errors="replace").splitlines():
        parsed = record(line)
        if not parsed:
            continue
        schema, kind, fields = parsed
        fields["schema_version"] = schema
        if schema == L1_SCHEMA:
            l1.append(fields)
            continue
        if schema == DRAM_SCHEMA:
            dram.append(fields)
            continue
        if kind == "INVARIANT":
            invariants.append(fields)
        elif kind == "BANK":
            # Reserved for future explicit bank rows; current producer keeps
            # bank counters in snapshot fields, which are normalized below.
            pass
        else:
            scope = fields.get("scope")
            if scope == "application":
                application.append(fields)
            elif scope == "kernel":
                kernels.append(fields)
            elif scope == "window":
                windows.append(fields)
            else:
                raise ValueError("unknown EPL2B0V1 record type/scope: %s/%s" % (kind, scope))
    if not application:
        raise ValueError("no EPL2B0V1 application cumulative records found")

    # Application records are cumulative and may be printed at an
    # intermediate kernel-completion statistics boundary. For each slice,
    # retain only its latest completion snapshot; summing successive
    # cumulative snapshots would double count a multi-kernel run.
    terminal_application = {}
    for row in application:
        slice_id = row.get("slice")
        previous = terminal_application.get(slice_id)
        if previous is None or row.get("completion_cycle", -1) >= previous.get("completion_cycle", -1):
            terminal_application[slice_id] = row
    application = [terminal_application[key] for key in sorted(terminal_application)]
    write_csv(args.out / "target_slice.csv", application)
    write_csv(args.out / "target_kernel.csv", kernels)
    write_csv(args.out / "target_window.csv", windows)
    write_csv(args.out / "target_l1.csv", l1)
    write_csv(args.out / "target_dram.csv", dram)
    bank_rows = []
    for row in application + kernels:
        bank_rows.append({key: row.get(key, "NA") for key in
                          ("schema_version", "scope", "slice", "kernel_uid", "samples",
                           "bank_requests", "bank_logical_ops", "bank_attempts",
                           "bank_grants", "bank_retry_attempts",
                           "bank_true_conflict_ops", "bank_true_conflict_events",
                           "bank_wait_cycles", "bank_conflicts", "block_bank",
                           "c7d_bank0_logical_ops", "c7d_bank1_logical_ops",
                           "c7d_bank2_logical_ops", "c7d_bank3_logical_ops",
                           "c7d_bank0_grants", "c7d_bank1_grants",
                           "c7d_bank2_grants", "c7d_bank3_grants",
                           "c7d_bank0_true_conflict_ops",
                           "c7d_bank1_true_conflict_ops",
                           "c7d_bank2_true_conflict_ops",
                           "c7d_bank3_true_conflict_ops",
                           "c7d_bank0_wait_cycles", "c7d_bank1_wait_cycles",
                           "c7d_bank2_wait_cycles", "c7d_bank3_wait_cycles",
                           "c7d_bank_resident_hit_read", "c7d_bank_resident_write",
                           "c7d_bank_fill_write", "c7d_bank_wb_readout",
                           "c7d_bank_bypass_fill", "c7d_bank_bypass_read")})
    write_csv(args.out / "target_bank.csv", bank_rows)
    additive = ("samples", "block_descriptor", "block_wad", "block_payload",
                "block_bank", "block_l1", "block_lower", "bank_requests",
                "bank_logical_ops", "bank_attempts", "bank_grants",
                "bank_retry_attempts", "bank_true_conflict_ops",
                "bank_true_conflict_events", "bank_wait_cycles",
                "bank_conflicts", "c7d_line_alloc_eligible",
                "c7d_line_alloc_block", "c7d_tag_set_all_reserved_block",
                "c7d_line_mshr_alloc_eligible", "c7d_line_mshr_full_block",
                "c7d_descriptor_alloc_eligible",
                "c7d_descriptor_pool_full_block",
                "c7d_per_address_cap_eligible",
                "c7d_per_address_cap_block", "c7d_wad_full_events",
                "c7d_wad_hazard_events", "c7d_wad_hazard_wait_cycles",
                "c7d_payload_service_port_denial",
                "c7d_payload_capacity_allocation_denial",
                "c7d_missq_full_block", "c7d_l2_to_dram_full_block",
                "c7d_dram_issue_eligible", "c7d_dram_read_issues",
                "c7d_dram_write_issues", "c7d_dram_scheduler_full_block",
                "c7d_dram_returnq_block", "c7d_dram_credit_block",
                "c7d_dram_return_eligible", "c7d_dram_to_l2_full_block")
    # INVARIANT records are emitted at every kernel statistics boundary as
    # well as at application completion.  The application UID sentinel marks
    # the cumulative stream, but that stream itself has intermediate records;
    # retain its final row for each physical L2 slice, just as above for the
    # cumulative application snapshots.  A live WAD/payload in an earlier
    # cumulative record is valid when later kernels can still consume it.
    terminal_by_slice = {}
    for row in invariants:
        if row.get("kernel_uid") == APPLICATION_UID:
            terminal_by_slice[row.get("slice")] = row
    terminal_invariants = [terminal_by_slice[key]
                           for key in sorted(terminal_by_slice)]
    summary = {"schema_version": SCHEMA, "slice_count": len(application),
               "kernel_record_count": len(kernels),
               "invariant_records": len(invariants),
               "terminal_invariant_records": len(terminal_invariants),
               "invariants_terminal_clean": int(bool(terminal_invariants) and all(
                   r.get("terminal_clean") == 1 for r in terminal_invariants)),
               "invariants_payload_consistent": int(all(r.get("resident_tag_payload_consistent") == 1 for r in invariants))}
    for field in additive:
        emitted = [row[field] for row in application
                   if field in row and isinstance(row[field], (int, float))]
        # A newer parser may read a pre-C7d producer log.  Absence is not a
        # measured zero and must survive into any downstream analysis.
        summary[field] = sum(emitted) if emitted else "NOT_EMITTED_BY_EPL2B0V1"
    write_csv(args.out / "target_summary.csv", [summary])
    manifest = {"schema_version": SCHEMA, "framework_commit": args.framework_commit,
                "core_commit": args.core_commit, "source_log_sha256": sha256(args.source_log),
                "artifacts": ["target_summary.csv", "target_slice.csv", "target_kernel.csv",
                              "target_bank.csv", "target_window.csv", "target_l1.csv",
                              "target_dram.csv"], "characterization_started": False}
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit("EPL2B0V1 parser error: %s" % error)
