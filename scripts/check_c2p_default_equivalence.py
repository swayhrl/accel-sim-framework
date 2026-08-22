#!/usr/bin/env python3
"""Audit default C2P equivalence across the pre/post m/k implementation.

The parameterized Snapshot Matrix implementation intentionally preserves the
paper default: 64 banks x (64 BF rows + 16 tag-mask rows), with four total
encodings.  Long paper16 replays began before Figure-13's non-default m/k
support landed, so they can contain two simulator binary identities.  This
checker proves, from paired replay bundles, that the default C2P behavior is
bit-for-bit unchanged before accepting those completed default-mode results.

It is deliberately *not* a waiver for Figure 13: use it only with the
``m5120-k4`` reference point.  Smaller or larger Snapshot Matrix points need
the corrected parameterized implementation and are rejected here.
"""

import argparse
import csv
from pathlib import Path


DEFAULT_ROWS = 5120
DEFAULT_HASHES = 4
# These fields were added as observability-only C2P diagnostics after a
# subset of the long paper16 replays had already started.  They do not change
# the default m5120-k4 execution: all architectural counters (cycles, L2
# accesses, probes, hits, and avoided requests) remain compared bit-for-bit.
# If both binaries report one of these fields it is still compared exactly;
# only an absent old-binary field is ignored.
IGNORED_ABSENT_DIAGNOSTIC_COUNTERS = {
    "c2p_ccd_false_positive",
    "c2p_ccd_false_negative",
    "c2p_ccd_true_positive",
    "c2p_ccd_true_negative",
    "c2p_peer_probe_hits",
    "c2p_peer_probe_misses",
    "c2p_target_probe_port_busy_cycles",
    "c2p_target_probe_queue_wait_cycles",
    "c2p_target_probe_queue_full_cycles",
    "c2p_requester_fill_wait_cycles",
    "c2p_fallback_queue",
}


def read_summary(run_dir):
    values = {}
    path = run_dir / "summary.txt"
    if not path.is_file():
        return None
    for line in path.read_text().splitlines():
        if " = " not in line:
            continue
        key, value = line.split(" = ", 1)
        try:
            values[key] = int(value)
        except ValueError:
            continue
    return values


def read_provenance(run_dir):
    path = run_dir / "provenance.txt"
    if not path.is_file():
        return None
    values = {}
    for line in path.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values


def read_shape(run_dir):
    """Resolve last-value m/k options, materializing old default spelling."""
    rows_per_bank, bf_hashes = 64, 3
    path = run_dir / "gpgpusim.config"
    if not path.is_file():
        return None
    for line in path.read_text().splitlines():
        fields = line.split()
        if len(fields) < 2:
            continue
        if fields[0] == "-c2p_cache_snapshot_bf_rows_per_bank":
            rows_per_bank = int(fields[1])
        elif fields[0] == "-c2p_cache_bf_hashes":
            bf_hashes = int(fields[1])
    return 64 * (16 + rows_per_bank), 1 + bf_hashes


def read_cases(path):
    with path.open(newline="") as stream:
        return [row["case"] for row in csv.DictReader(
            (line for line in stream if not line.startswith("#")), delimiter="\t")]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary-root", required=True, type=Path,
                        help="paper16 root containing default C2P runs")
    parser.add_argument("--supplemental-primary-root", action="append", type=Path,
                        default=[], help="fallback paper16 roots, canonical root first")
    parser.add_argument("--reference-root", required=True, type=Path,
                        help="Figure-13 root containing m5120-k4/C2P runs")
    parser.add_argument("--supplemental-reference-root", action="append", type=Path,
                        default=[], help="fallback Figure-13 roots, canonical root first")
    parser.add_argument("--manifest", type=Path,
                        default=Path(__file__).resolve().parents[1] /
                        "configs/c2p-cache/paper16_workloads.tsv")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--strict", action="store_true",
                        help="require every manifest workload to be paired")
    args = parser.parse_args()

    primary_roots = [args.primary_root, *args.supplemental_primary_root]
    reference_roots = [args.reference_root, *args.supplemental_reference_root]
    rows, missing, mismatches = [], [], []
    for case in read_cases(args.manifest):
        primary_dir = next((root / case / "c2p" for root in primary_roots
                            if read_summary(root / case / "c2p") is not None),
                           primary_roots[0] / case / "c2p")
        reference_dir = next((root / "m5120-k4" / case / "c2p"
                              for root in reference_roots
                              if read_summary(root / "m5120-k4" / case / "c2p") is not None),
                             reference_roots[0] / "m5120-k4" / case / "c2p")
        primary, reference = read_summary(primary_dir), read_summary(reference_dir)
        if primary is None or reference is None:
            missing.append(case)
            continue
        primary_shape, reference_shape = read_shape(primary_dir), read_shape(reference_dir)
        if primary_shape != (DEFAULT_ROWS, DEFAULT_HASHES) or \
                reference_shape != (DEFAULT_ROWS, DEFAULT_HASHES):
            mismatches.append(f"{case}: non-default shape {primary_shape}/{reference_shape}")
            continue
        compared = sorted(set(primary) | set(reference))
        case_mismatches = []
        for key in compared:
            left, right = primary.get(key), reference.get(key)
            if left is None and key in IGNORED_ABSENT_DIAGNOSTIC_COUNTERS:
                continue
            if right is None and key in IGNORED_ABSENT_DIAGNOSTIC_COUNTERS:
                continue
            if left != right:
                case_mismatches.append(f"{key}: {left} != {right}")
        primary_provenance = read_provenance(primary_dir) or {}
        reference_provenance = read_provenance(reference_dir) or {}
        rows.append({
            "case": case,
            "primary_run": str(primary_dir),
            "reference_run": str(reference_dir),
            "primary_commit": primary_provenance.get("gpgpusim_commit", ""),
            "reference_commit": reference_provenance.get("gpgpusim_commit", ""),
            "primary_sim_sha256": primary_provenance.get("sim_sha256", ""),
            "reference_sim_sha256": reference_provenance.get("sim_sha256", ""),
            "equal": "yes" if not case_mismatches else "no",
            "mismatches": "; ".join(case_mismatches),
        })
        if case_mismatches:
            mismatches.append(f"{case}: " + "; ".join(case_mismatches))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=(
            "case", "primary_run", "reference_run", "primary_commit", "reference_commit", "primary_sim_sha256",
            "reference_sim_sha256", "equal", "mismatches"))
        writer.writeheader()
        writer.writerows(rows)
    print(f"paired={len(rows)} missing={len(missing)} mismatches={len(mismatches)}")
    for item in missing:
        print(f"missing: {item}")
    for item in mismatches:
        print(f"mismatch: {item}")
    if mismatches or (args.strict and missing):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
