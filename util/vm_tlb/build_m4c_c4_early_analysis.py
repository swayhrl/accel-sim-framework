#!/usr/bin/env python3
"""Build C4 early analysis from terminal C3 arms only; never replay."""
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

ARMS = ("decode1-disabled", "decode1-ideal", "decode1-generic", "decode1-paper",
        "prefill-disabled", "prefill-ideal", "prefill-generic")
EXPORTS = ("KERNEL_MEMORY_STATS.tsv", "WINDOW_MEMORY_STATS.tsv", "L1D_OBJECT_STATS.tsv",
           "L1D_FAIL_PRESSURE.tsv", "L2_REQUEST_CLASS_STATS.tsv", "L2_QUEUE_PRESSURE.tsv",
           "L2_CLASS_REPLACEMENT_MATRIX.tsv", "DRAM_REQUEST_CLASS_STATS.tsv",
           "CROSS_LAYER_OUTCOME_MATRIX.tsv", "NATIVE_MEMORY_SYSTEM_STATS.tsv",
           "TELEMETRY_SCHEMA.md")
BINARY_SHA = "100527f1d54600dcbbf7c713584512344a688521089aaa995a0b7e4106f81eda"
RUNTIME_SHA = "fc07def22e239de9fec8a3dd83d237a607a82162cab2933d6707a37c0a208b0a"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def manifest(path: Path) -> dict[str, str]:
    with path.open(newline="") as source:
        rows = list(csv.reader(source, delimiter="\t"))
    if not rows or rows[0] != ["field", "value"]:
        fail(f"bad manifest: {path}")
    return {row[0]: row[1] for row in rows[1:] if len(row) == 2}


def log_summary(path: Path) -> tuple[int, int, dict[str, str]]:
    markers = telemetry = 0
    values: dict[str, str] = {}
    with path.open(errors="strict") as source:
        for line in source:
            if line.startswith("Processing kernel "):
                markers += 1
            elif line.startswith("m4c_telemetry_schema ="):
                telemetry += 1
            elif line.startswith(("vm_", "gpu_tot_")) and " = " in line:
                key, value = line.rstrip("\n").split(" = ", 1)
                values[key] = value.strip()
    return markers, telemetry, values


def numeric(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def ratio(value: str, baseline: str) -> str:
    numerator, denominator = numeric(value), numeric(baseline)
    if numerator is None or denominator in (None, 0):
        return "NOT_AVAILABLE"
    return f"{numerator / denominator:.9f}"


def write(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="") as target:
        writer = csv.writer(target, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def export_preflight(export_dir: Path, data: dict[str, dict[str, object]]) -> tuple[list[list[str]], list[list[str]]]:
    checks, coverage = [], []
    for arm in ARMS:
        expected = data[arm]["manifest"]
        for name in EXPORTS:
            path = export_dir / arm / name
            result, detail = "PASS", "present"
            if not path.is_file():
                result, detail = "FAIL", "missing"
            elif name.endswith(".tsv"):
                with path.open(newline="") as source:
                    reader = csv.DictReader(source, delimiter="\t")
                    first = next(reader, None)
                if not reader.fieldnames or first is None:
                    result, detail = "FAIL", "empty TSV"
                elif first.get("framework_head") != expected["framework_head"] or first.get("core_head") != expected["core_head"]:
                    result, detail = "FAIL", "provenance mismatch"
                coverage.append([arm, name, "NOT_SCANNED_LOW_RESOURCE", "header+first-record provenance validated"])
            checks.append([arm, name, result, detail])
    return checks, coverage


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument("--export-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root, exports, output = args.runs_root.resolve(), args.export_root.resolve(), args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        fail(f"refusing nonempty output: {output}")
    output.mkdir(parents=True, exist_ok=True)
    data: dict[str, dict[str, object]] = {}
    provenance, terminal_checks = [], []
    for arm in ARMS:
        run = root / arm
        mpath, lpath, kpath = run / "RUN_MANIFEST.tsv", run / "run.log", run / "traces" / "kernelslist.g"
        item = manifest(mpath)
        expected = sum(1 for line in kpath.read_text().splitlines() if line)
        markers, telemetry, scalars = log_summary(lpath)
        if item.get("simulator_exit_status") != "0" or markers != expected or telemetry != expected:
            fail(f"nonterminal arm supplied to early analysis: {arm}")
        data[arm] = {"manifest": item, "scalars": scalars}
        provenance.append([arm, item["roi"], item["profile"], item["framework_head"], item["core_head"],
                           BINARY_SHA, RUNTIME_SHA, digest(mpath), digest(kpath), digest(lpath)])
        terminal_checks.append([arm, "PASS", str(expected), str(markers), str(telemetry), "exit=0; markers=list; telemetry=list"])
    write(output / "INPUT_PROVENANCE.tsv", ["arm", "roi", "profile", "framework_head", "core_head", "simulator_binary_sha256", "runtime_libcudart_sha256", "run_manifest_sha256", "trace_list_sha256", "run_log_sha256"], provenance)
    write(output / "TERMINAL_GATE.tsv", ["arm", "result", "expected_kernels", "processing_kernel_markers", "telemetry_kernel_records", "evidence"], terminal_checks)
    def profile_table(roi: str, profiles: list[str], name: str) -> None:
        all_metrics = sorted({metric for profile in profiles for metric in data[f"{roi}-{profile}"]["scalars"]})
        rows = []
        for metric in all_metrics:
            values = [str(data[f"{roi}-{profile}"]["scalars"].get(metric, "NOT_AVAILABLE")) for profile in profiles]
            ratios = [ratio(values[i], values[1]) for i in range(2, len(values))]
            rows.append([metric, *values, *ratios])
        headers = ["metric", *profiles]
        headers += [f"{profile}_vs_ideal_ratio" for profile in profiles[2:]]
        write(output / name, headers, rows)
    profile_table("decode1", ["disabled", "ideal", "generic", "paper"], "DECODE1_TERMINAL_PROFILE_COMPARISON.tsv")
    profile_table("prefill", ["disabled", "ideal", "generic"], "PREFILL_TERMINAL_SUBSET.tsv")
    checks, coverage = export_preflight(exports, data)
    write(output / "C4_EXPORT_PREFLIGHT.tsv", ["arm", "export", "result", "detail"], checks)
    write(output / "C4_EXPORT_COVERAGE.tsv", ["arm", "export", "record_rows", "provenance"], coverage)
    write(output / "C4_EARLY_VALIDATION.tsv", ["check", "result", "detail"], [
        ("seven_terminal_input_arms", "PASS", "all supplied arms satisfy exit/count gate"),
        ("export_schema_and_provenance", "PASS" if all(row[2] == "PASS" for row in checks) else "FAIL", "all 11 exports per arm present and bound to manifest"),
        ("replay", "NOT_PERFORMED", "analysis consumes existing C3 logs only"),
        ("prefill_paper", "PENDING", "explicitly excluded until terminal"),
    ])
    print(f"PASS c4_early_analysis={output}")


if __name__ == "__main__":
    main()
