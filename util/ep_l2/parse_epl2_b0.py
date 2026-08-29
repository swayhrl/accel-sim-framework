#!/usr/bin/env python3
"""Parse independent EPL2B0V1 records into target-baseline CSV artifacts."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

SCHEMA = "EPL2B0V1"
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
    if len(parts) < 2 or parts[0] != SCHEMA:
        return None
    fields = {}
    kind, start = ("SNAPSHOT", 1) if "=" in parts[1] else (parts[1], 2)
    for item in parts[start:]:
        if "=" not in item:
            raise ValueError("malformed EPL2B0V1 field: " + item)
        key, raw = item.split("=", 1)
        fields[key] = value(raw)
    return kind, fields


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

    application, kernels, invariants = [], [], []
    for line in args.log.read_text(encoding="utf-8", errors="replace").splitlines():
        parsed = record(line)
        if not parsed:
            continue
        kind, fields = parsed
        fields["schema_version"] = SCHEMA
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
    bank_rows = []
    for row in application + kernels:
        bank_rows.append({key: row.get(key, "NA") for key in
                          ("schema_version", "scope", "slice", "kernel_uid", "samples",
                           "bank_requests", "bank_grants", "bank_conflicts", "block_bank")})
    write_csv(args.out / "target_bank.csv", bank_rows)
    additive = ("samples", "block_descriptor", "block_wad", "block_payload",
                "block_bank", "block_l1", "block_lower", "bank_requests",
                "bank_grants", "bank_conflicts")
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
        summary[field] = sum(row.get(field, 0) for row in application
                             if isinstance(row.get(field, 0), (int, float)))
    write_csv(args.out / "target_summary.csv", [summary])
    manifest = {"schema_version": SCHEMA, "framework_commit": args.framework_commit,
                "core_commit": args.core_commit, "source_log_sha256": sha256(args.source_log),
                "artifacts": ["target_summary.csv", "target_slice.csv", "target_kernel.csv",
                              "target_bank.csv"], "characterization_started": False}
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit("EPL2B0V1 parser error: %s" % error)
