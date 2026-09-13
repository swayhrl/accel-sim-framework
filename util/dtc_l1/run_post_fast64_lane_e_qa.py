#!/usr/bin/env python3
"""Execute, rather than merely describe, bounded Lane-E artifact QA.

This helper only invokes the compact-input Lane-E builder in isolated temporary
directories.  It has no simulator, trace, GPU, Core, or configuration path.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def rows(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, data, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(data[0]) if data else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)


def invoke(builder: Path, *args):
    return subprocess.run([sys.executable, str(builder), *map(str, args)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def build_core(builder: Path, inputs: Path, output: Path):
    result = invoke(builder, "--build-core", "--inputs", inputs, "--output", output)
    if result.returncode:
        raise RuntimeError("core build failed:\n" + result.stdout)
    return result


def validate_core(builder: Path, inputs: Path, output: Path):
    return invoke(builder, "--validate-core", "--inputs", inputs, "--output", output)


def mutate_tsv(path: Path, edit):
    data = rows(path)
    if not data:
        raise ValueError("cannot mutate empty TSV: " + str(path))
    fields = list(data[0])
    edit(data)
    write(path, data, fields)


def compact_output(result):
    text = " ".join(result.stdout.strip().split())
    return text[-500:] if text else "validator returned no output"


def negative_fixtures(builder: Path, inputs: Path, qa_dir: Path):
    """Create six independently malformed packages and require rejection."""
    fixture_specs = [
        (
            "N01_FAST12_ORDER",
            "Swap ATAX and BICG rows in E_PRIMARY_PERFORMANCE.tsv.",
            lambda root: mutate_tsv(root / "tables/E_PRIMARY_PERFORMANCE.tsv", lambda data: data.__setitem__(slice(0, 2), [data[1], data[0]])),
        ),
        (
            "N02_PRIMARY_OBSERVER_CONTAMINATION",
            "Relabel one primary FAST12 row as NEW_DIAGNOSTIC_TELEMETRY.",
            lambda root: mutate_tsv(root / "tables/E_PRIMARY_PERFORMANCE.tsv", lambda data: data[0].__setitem__("evidence_class", "NEW_DIAGNOSTIC_TELEMETRY")),
        ),
        (
            "N03_PHYSICAL_16P5_NUMERIC",
            "Turn BICG/IO 16.5 KiB nonnumeric boundary into a numeric point.",
            lambda root: mutate_tsv(root / "tables/E_SENS_PHYSICAL.tsv", _make_bicg_16p5_numeric),
        ),
        (
            "N04_OO_DUPLICATE_PROXY",
            "Replace qualified OO duplicate evidence source with new-miss proxy label.",
            lambda root: mutate_tsv(root / "tables/E_DUPLICATE_IO_OO.tsv", _make_oo_proxy),
        ),
        (
            "N05_INVENTED_D4_40KIB",
            "Append an invented 40 KiB D4 observer row.",
            lambda root: _append_invented_d4(root / "tables/E_PHYSICAL_OBSERVER_SYNTHESIS.tsv"),
        ),
        (
            "N06_PAYLOAD_RELABEL_DRAM",
            "Relabel source-proven lower-request payload as DRAM traffic.",
            lambda root: mutate_tsv(root / "tables/E_DUPLICATE_IO_OO.tsv", lambda data: data[0].__setitem__("payload_scope", "DRAM traffic")),
        ),
    ]
    records = []
    with tempfile.TemporaryDirectory(prefix="lane-e-negative-") as temp:
        temp = Path(temp)
        core = temp / "core"
        build_core(builder, inputs, core)
        for fixture_id, description, mutation in fixture_specs:
            candidate = temp / fixture_id
            shutil.copytree(core, candidate)
            mutation(candidate)
            result = validate_core(builder, inputs, candidate)
            rejected = result.returncode != 0
            records.append({
                "fixture_id": fixture_id,
                "exact_mutation": description,
                "validator_invoked": "build_post_fast64_lane_e.py --validate-core",
                "expected_result": "REJECT_NONZERO",
                "observed_exit_code": result.returncode,
                "observed_result": compact_output(result),
                "status": "PASS" if rejected else "FAIL",
            })
    write(qa_dir / "E_NEGATIVE_FIXTURE_RESULTS.tsv", records)
    if not all(r["status"] == "PASS" for r in records):
        raise SystemExit("one or more negative fixtures were accepted")


def _make_bicg_16p5_numeric(data):
    target = next(r for r in data if r["workload"] == "BICG" and r["mode"] == "IO" and r["requested_point"] == "16.5")
    target["row_kind"] = "NUMERIC_ACCEPTED_POINT"
    target["cycles"] = "1"


def _make_oo_proxy(data):
    next(r for r in data if r["mode"] == "OO")["evidence_source"] = "OO_new_misses_proxy"


def _append_invented_d4(path: Path):
    data = rows(path)
    fields = list(data[0])
    invented = dict(data[0])
    invented["physical_pool_kib"] = "40"
    data.append(invented)
    write(path, data, fields)


def file_map(root: Path):
    return {
        str(path.relative_to(root)): (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_size)
        for path in sorted(path for path in root.rglob("*") if path.is_file())
    }


def compare_trees(left: Path, right: Path):
    first, second = file_map(left), file_map(right)
    names = sorted(set(first) | set(second))
    mismatch = [name for name in names if first.get(name) != second.get(name)]
    return len(names), mismatch


def core_determinism(builder: Path, inputs: Path, qa_dir: Path):
    with tempfile.TemporaryDirectory(prefix="lane-e-core-a-") as left_temp, tempfile.TemporaryDirectory(prefix="lane-e-core-b-") as right_temp:
        left, right = Path(left_temp) / "package", Path(right_temp) / "package"
        build_a = build_core(builder, inputs, left)
        validate_a = validate_core(builder, inputs, left)
        build_b = build_core(builder, inputs, right)
        validate_b = validate_core(builder, inputs, right)
        count, mismatch = compare_trees(left, right)
        status = "PASS" if not mismatch and validate_a.returncode == validate_b.returncode == 0 else "FAIL"
        detail = f"two isolated core builds; build exit codes={build_a.returncode}/{build_b.returncode}; validation exit codes={validate_a.returncode}/{validate_b.returncode}; recursive SHA-256 plus byte-size comparison"
        record = [{"status": status, "compared_file_count": count, "mismatch_count": len(mismatch), "detail": detail}]
    write(qa_dir / "E_DETERMINISM_EXECUTION.tsv", record)
    if status != "PASS":
        raise SystemExit("core determinism comparison failed: " + ",".join(mismatch[:10]))


def claim_audit_execution(builder: Path, inputs: Path, qa_dir: Path):
    with tempfile.TemporaryDirectory(prefix="lane-e-claim-") as temp:
        core = Path(temp) / "core"
        build_core(builder, inputs, core)
        result = validate_core(builder, inputs, core)
        audit = rows(core / "E_CLAIM_AUDIT.tsv")
        pass_rows = bool(audit) and all(r["status"] == "PASS" for r in audit)
        status = "PASS" if result.returncode == 0 and pass_rows else "FAIL"
        detail = f"isolated core validator exit={result.returncode}; claim audit rows={len(audit)}; all claim checks={pass_rows}"
    write(qa_dir / "E_CLAIM_AUDIT_EXECUTION.tsv", [{"status": status, "detail": detail, "validator_output": compact_output(result)}])
    if status != "PASS":
        raise SystemExit("claim audit execution failed")


def final_determinism(builder: Path, inputs: Path, qa_dir: Path):
    """Compare two complete final packages, then record that executed result."""
    with tempfile.TemporaryDirectory(prefix="lane-e-final-seed-a-") as one, tempfile.TemporaryDirectory(prefix="lane-e-final-seed-b-") as two:
        left, right = Path(one) / "package", Path(two) / "package"
        a = invoke(builder, "--build", "--inputs", inputs, "--qa-dir", qa_dir, "--output", left)
        va = invoke(builder, "--validate", "--inputs", inputs, "--output", left)
        b = invoke(builder, "--build", "--inputs", inputs, "--qa-dir", qa_dir, "--output", right)
        vb = invoke(builder, "--validate", "--inputs", inputs, "--output", right)
        count, mismatch = compare_trees(left, right)
        initial_status = "PASS" if a.returncode == b.returncode == va.returncode == vb.returncode == 0 and not mismatch else "FAIL"
    write(qa_dir / "E_FINAL_PACKAGE_DETERMINISM_EXECUTION.tsv", [{
        "status": initial_status,
        "compared_file_count": count,
        "mismatch_count": len(mismatch),
        "detail": "two isolated complete final-package builds; recursive SHA-256 plus byte-size comparison; both final validators executed",
    }])
    # Verify a second pair with the final-determinism record itself included.
    with tempfile.TemporaryDirectory(prefix="lane-e-final-a-") as one, tempfile.TemporaryDirectory(prefix="lane-e-final-b-") as two:
        left, right = Path(one) / "package", Path(two) / "package"
        a = invoke(builder, "--build", "--inputs", inputs, "--qa-dir", qa_dir, "--output", left)
        va = invoke(builder, "--validate", "--inputs", inputs, "--output", left)
        b = invoke(builder, "--build", "--inputs", inputs, "--qa-dir", qa_dir, "--output", right)
        vb = invoke(builder, "--validate", "--inputs", inputs, "--output", right)
        count, mismatch = compare_trees(left, right)
        status = "PASS" if a.returncode == b.returncode == va.returncode == vb.returncode == 0 and not mismatch else "FAIL"
    write(qa_dir / "E_FINAL_PACKAGE_DETERMINISM_EXECUTION.tsv", [{
        "status": status,
        "compared_file_count": count,
        "mismatch_count": len(mismatch),
        "detail": "two isolated complete final-package builds (record included); recursive SHA-256 plus byte-size comparison; both final validators executed",
    }])
    if status != "PASS":
        raise SystemExit("final-package determinism comparison failed: " + ",".join(mismatch[:10]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--builder", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--qa-dir", type=Path, required=True)
    parser.add_argument("--negative", action="store_true")
    parser.add_argument("--core-determinism", action="store_true")
    parser.add_argument("--claim-audit", action="store_true")
    parser.add_argument("--final-determinism", action="store_true")
    args = parser.parse_args()
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    if args.negative:
        negative_fixtures(args.builder, args.inputs, args.qa_dir)
    if args.core_determinism:
        core_determinism(args.builder, args.inputs, args.qa_dir)
    if args.claim_audit:
        claim_audit_execution(args.builder, args.inputs, args.qa_dir)
    if args.final_determinism:
        final_determinism(args.builder, args.inputs, args.qa_dir)
    if not any((args.negative, args.core_determinism, args.claim_audit, args.final_determinism)):
        parser.error("select at least one QA execution")


if __name__ == "__main__":
    main()
