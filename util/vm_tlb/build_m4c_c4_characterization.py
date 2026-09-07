#!/usr/bin/env python3
"""Build provenance-bound C3+C4 characterization tables without replay.

Inputs are immutable C3 manifests/logs plus the C4 exporter and locality
artifacts.  This tool deliberately never launches a simulator and refuses to
overwrite an analysis directory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sqlite3
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Iterable


ARMS = tuple(
    f"{roi}-{profile}"
    for roi in ("decode1", "prefill")
    for profile in ("disabled", "ideal", "generic", "paper")
)
OBJECTS = ("WEIGHT", "KV_CACHE", "UNKNOWN")
C3_SIMULATOR_SHA256 = "100527f1d54600dcbbf7c713584512344a688521089aaa995a0b7e4106f81eda"
C3_RUNTIME_LIBCUDART_SHA256 = "fc07def22e239de9fec8a3dd83d237a607a82162cab2933d6707a37c0a208b0a"
C3_RUNTIME_LIBCUDART_REALPATH = (
    "/workspace/worktrees/gpgpu-sim-vm-llm-m4b-integration/"
    "lib/gcc-11.4.0/cuda-11080/release/libcudart.so"
)
PRE_CORRECTION_FRAMEWORK_HEAD = "7709376eb7c7358247e1868f80a143edb54ce69d"
POST_CORRECTION_FRAMEWORK_HEAD = "a7c0759be7f293ed0d5e2179c62094b6de49c1e8"
FROZEN_CORE_HEAD = "0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd"
EXPORT_FILES = (
    "KERNEL_MEMORY_STATS.tsv", "WINDOW_MEMORY_STATS.tsv",
    "L1D_OBJECT_STATS.tsv", "L1D_FAIL_PRESSURE.tsv",
    "L2_REQUEST_CLASS_STATS.tsv", "L2_QUEUE_PRESSURE.tsv",
    "L2_CLASS_REPLACEMENT_MATRIX.tsv", "DRAM_REQUEST_CLASS_STATS.tsv",
    "CROSS_LAYER_OUTCOME_MATRIX.tsv", "NATIVE_MEMORY_SYSTEM_STATS.tsv",
    "TELEMETRY_SCHEMA.md",
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manifest(path: Path) -> dict[str, str]:
    rows = list(csv.reader(path.open(newline=""), delimiter="\t"))
    if not rows or rows[0] != ["field", "value"]:
        fail(f"bad manifest header: {path}")
    result: dict[str, str] = {}
    for row in rows[1:]:
        if len(row) != 2:
            fail(f"bad manifest row: {path}")
        if row[0] in result:
            fail(f"duplicate manifest field {row[0]}: {path}")
        result[row[0]] = row[1]
    return result


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if not reader.fieldnames:
            fail(f"empty TSV: {path}")
        rows = list(reader)
    return list(reader.fieldnames), rows


def write_tsv(path: Path, header: list[str], rows: Iterable[Iterable[object]]) -> None:
    with path.open("w", newline="") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def integer(value: str, context: str) -> int:
    try:
        return int(value.strip())
    except ValueError as error:
        fail(f"non-integer {context}: {value!r}")
        raise AssertionError from error


def last_log_scalars(path: Path) -> tuple[int, int, dict[str, str]]:
    markers = 0
    telemetry = 0
    scalars: dict[str, str] = {}
    with path.open(errors="strict") as source:
        for raw in source:
            if raw.startswith("Processing kernel "):
                markers += 1
            elif raw.startswith("m4c_telemetry_schema = M4C_MEMORY_TELEMETRY_V1"):
                telemetry += 1
            elif raw.startswith(("vm_", "gpu_tot_")) and " = " in raw:
                key, value = raw.rstrip("\n").split(" = ", 1)
                scalars[key] = value.strip()
    return markers, telemetry, scalars


def profile_from_arm(arm: str) -> tuple[str, str]:
    try:
        roi, profile = arm.split("-", 1)
    except ValueError as error:
        fail(f"unsafe run name: {arm}")
        raise AssertionError from error
    if roi not in ("decode1", "prefill") or profile not in ("disabled", "ideal", "generic", "paper"):
        fail(f"unexpected run name: {arm}")
    return roi, profile


def collect_runs(root: Path) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    framework_heads: set[str] = set()
    core_heads: set[str] = set()
    for arm in ARMS:
        run_dir = root / arm
        manifest_path = run_dir / "RUN_MANIFEST.tsv"
        log_path = run_dir / "run.log"
        list_path = run_dir / "traces" / "kernelslist.g"
        if not manifest_path.is_file() or not log_path.is_file() or not list_path.is_file():
            fail(f"missing formal artifact for {arm}")
        manifest = read_manifest(manifest_path)
        roi, profile = profile_from_arm(arm)
        if manifest.get("roi") != roi or manifest.get("profile") != profile:
            fail(f"manifest identity mismatch: {arm}")
        expected = sum(1 for line in list_path.read_text().splitlines() if line)
        markers, telemetry, scalars = last_log_scalars(log_path)
        checks = [
            manifest.get("simulator_exit_status") == "0",
            markers == expected,
            telemetry == expected,
        ]
        if profile in ("generic", "paper"):
            checks.extend([
                scalars.get("vm_pte_requests") == scalars.get("vm_pte_responses"),
                scalars.get("vm_pte_response_misassociations") == "0",
                scalars.get("vm_translation_waiter_registrations") ==
                scalars.get("vm_translation_waiter_wakeups"),
                scalars.get("vm_object_attribution_conservation_pass") == "1",
                scalars.get("vm_translation_mshr_active") == "0",
                scalars.get("vm_translation_pwq_occupancy") == "0",
                scalars.get("vm_translation_walkers_active") == "0",
            ])
        if not all(checks):
            fail(f"formal terminal validation failed: {arm}")
        framework_heads.add(manifest.get("framework_head", "MISSING"))
        core_heads.add(manifest.get("core_head", "MISSING"))
        result[arm] = {
            "arm": arm, "roi": roi, "profile": profile,
            "manifest": manifest, "manifest_sha256": sha256(manifest_path),
            "log_sha256": sha256(log_path), "kernel_list_sha256": sha256(list_path),
            "expected": expected, "markers": markers, "telemetry": telemetry,
            "scalars": scalars,
        }
    # The first three decode arms predate the accepted Framework-only C4
    # exporter correction.  That correction changed docs and a log parser,
    # never the C3 simulator binary.  Preserve the original arm manifests
    # rather than rewriting them, and prove the narrow lineage separately.
    if not framework_heads.issubset({PRE_CORRECTION_FRAMEWORK_HEAD, POST_CORRECTION_FRAMEWORK_HEAD}):
        fail(f"unexpected Framework manifest lineage: {sorted(framework_heads)}")
    if core_heads != {FROZEN_CORE_HEAD}:
        fail(f"unexpected Core manifest lineage: {sorted(core_heads)}")
    return result


def validate_framework_only_correction(framework_root: Path) -> None:
    """Prove the permitted 770->a7 evolution cannot change C3 execution."""
    try:
        changed = subprocess.check_output(
            ["git", "-C", str(framework_root), "diff", "--name-only",
             PRE_CORRECTION_FRAMEWORK_HEAD, POST_CORRECTION_FRAMEWORK_HEAD],
            text=True,
        ).splitlines()
    except subprocess.CalledProcessError as error:
        fail(f"cannot inspect Framework correction lineage: {error}")
    allowed = {
        "util/vm_tlb/export_m4c_telemetry.py",
    }
    for path in changed:
        if path not in allowed and not path.startswith("docs/"):
            fail(f"Framework correction touches runtime-relevant path: {path}")
    if "util/vm_tlb/export_m4c_telemetry.py" not in changed:
        fail("Framework correction lineage is incomplete")


def arm_from_export(row: dict[str, str]) -> str:
    run_dir = Path(row.get("run_dir", ""))
    arm = run_dir.name
    profile_from_arm(arm)
    return arm


def require_export_tree(c4_root: Path, runs: dict[str, dict[str, object]]) -> None:
    summary = c4_root / "C3_SUMMARY.tsv"
    if not summary.is_file():
        fail(f"missing C4 summary: {summary}")
    for arm, data in runs.items():
        manifest = data["manifest"]
        for name in EXPORT_FILES:
            path = c4_root / "telemetry" / arm / name
            if not path.is_file():
                fail(f"missing C4 export {name}: {arm}")
        for name in ("KERNEL_MEMORY_STATS.tsv", "L1D_OBJECT_STATS.tsv",
                     "L2_REQUEST_CLASS_STATS.tsv", "NATIVE_MEMORY_SYSTEM_STATS.tsv"):
            _, rows = read_tsv(c4_root / "telemetry" / arm / name)
            if not rows:
                fail(f"empty required C4 export {name}: {arm}")
            for row in rows[:1]:
                if row.get("framework_head") != manifest.get("framework_head") or \
                   row.get("core_head") != manifest.get("core_head"):
                    fail(f"export source provenance mismatch: {arm}/{name}")
    for roi in ("decode1", "prefill"):
        for suffix in ("locality.tsv", "locality.sqlite"):
            path = c4_root / "offline" / f"{roi}_{suffix}"
            if not path.is_file():
                fail(f"missing offline locality artifact: {path}")


def run_matrix(runs: dict[str, dict[str, object]], output: Path) -> None:
    rows = []
    for arm in ARMS:
        data = runs[arm]
        manifest = data["manifest"]
        rows.append([
            arm, data["roi"], data["profile"], "PASS",
            data["expected"], data["markers"], data["telemetry"],
            manifest["simulator_exit_status"], manifest.get("telemetry_level", "MISSING"),
            manifest["framework_head"], manifest["core_head"],
            data["manifest_sha256"], data["kernel_list_sha256"], data["log_sha256"],
        ])
    write_tsv(output / "FORMAL_RUN_MATRIX.tsv", [
        "arm", "roi", "profile", "terminal_result", "expected_kernel_list_entries",
        "processing_kernel_markers", "telemetry_kernel_records", "simulator_exit_status",
        "telemetry_level", "framework_head", "core_head", "run_manifest_sha256",
        "kernel_list_sha256", "run_log_sha256",
    ], rows)


def runtime_provenance(runs: dict[str, dict[str, object]], output: Path) -> None:
    heads = sorted({str(data["manifest"]["framework_head"]) for data in runs.values()})
    write_tsv(output / "C3_RUNTIME_PROVENANCE.tsv", ["scope", "field", "value", "evidence"], [
        ("all_arms", "simulator_binary_sha256", C3_SIMULATOR_SHA256,
         "frozen C3 direct binary SHA256 record"),
        ("all_arms", "mapped_libcudart_realpath", C3_RUNTIME_LIBCUDART_REALPATH,
         "direct /proc/<pid>/maps record; supersedes host-path recording error"),
        ("all_arms", "mapped_libcudart_sha256", C3_RUNTIME_LIBCUDART_SHA256,
         "direct /proc/<pid>/maps resolved Core-local runtime SHA256"),
        ("manifest_lineage", "framework_heads", ",".join(heads),
         "original per-arm RUN_MANIFEST.tsv values; never rewritten"),
        ("manifest_lineage", "pre_correction_framework_head", PRE_CORRECTION_FRAMEWORK_HEAD,
         "first three decode arms"),
        ("manifest_lineage", "post_correction_framework_head", POST_CORRECTION_FRAMEWORK_HEAD,
         "decode1-paper and all prefill arms"),
        ("manifest_lineage", "core_head", FROZEN_CORE_HEAD,
         "uniform original per-arm RUN_MANIFEST.tsv value"),
        ("correction_scope", "770_to_a7", "docs plus export_m4c_telemetry.py only",
         "validated Git path scope; no simulator runtime source path changed"),
    ])


def config_provenance(runs: dict[str, dict[str, object]], output: Path) -> None:
    rows = []
    for arm in ARMS:
        data = runs[arm]
        for key, value in sorted(data["manifest"].items()):
            if key.startswith("sha256:"):
                rows.append([arm, data["roi"], data["profile"], key[len("sha256:"):], value])
    header = [
        "arm", "roi", "profile", "artifact_path", "sha256",
    ]
    write_tsv(output / "FORMAL_CONFIG_PROVENANCE.tsv", header, rows)
    # Window A names the same original-manifest inventory as its baseline
    # configuration matrix.  Emit both names from one source of truth.
    write_tsv(output / "BASELINE_CONFIG_MATRIX.tsv", header, rows)


def performance(runs: dict[str, dict[str, object]], output: Path) -> None:
    rows = []
    for roi in ("decode1", "prefill"):
        base: dict[str, int] = {}
        for profile in ("disabled", "ideal"):
            base[profile] = integer(runs[f"{roi}-{profile}"]["scalars"].get("gpu_tot_sim_cycle", ""),
                                    f"{roi}-{profile} cycles")
        for profile in ("disabled", "ideal", "generic", "paper"):
            data = runs[f"{roi}-{profile}"]
            scalars = data["scalars"]
            cycles = integer(scalars.get("gpu_tot_sim_cycle", ""), f"{roi}-{profile} cycles")
            instructions = integer(scalars.get("gpu_tot_sim_insn", ""), f"{roi}-{profile} instructions")
            ipc = scalars.get("gpu_tot_ipc", "MISSING")
            ideal = cycles / base["ideal"] if base["ideal"] else "NA"
            disabled = cycles / base["disabled"] if base["disabled"] else "NA"
            rows.append([roi, profile, cycles, instructions, ipc,
                         f"{ideal:.9f}" if isinstance(ideal, float) else ideal,
                         f"{disabled:.9f}" if isinstance(disabled, float) else disabled])
    write_tsv(output / "PERFORMANCE_SUMMARY.tsv", [
        "roi", "profile", "gpu_tot_sim_cycle", "gpu_tot_sim_insn", "gpu_tot_ipc",
        "slowdown_vs_ideal_identity", "slowdown_vs_vm_disabled",
    ], rows)


def translation_and_objects(runs: dict[str, dict[str, object]], output: Path) -> None:
    total_rows = []
    object_rows = []
    replacement_rows = []
    object_re = re.compile(r"^vm_object_(WEIGHT|KV_CACHE|UNKNOWN)_(.+)$")
    replace_re = re.compile(r"^vm_l2_tlb_replacement_incoming_(WEIGHT|KV_CACHE|UNKNOWN)_victim_(WEIGHT|KV_CACHE|UNKNOWN)$")
    for arm in ARMS:
        data = runs[arm]
        roi, profile, scalars = data["roi"], data["profile"], data["scalars"]
        for key, value in sorted(scalars.items()):
            match = object_re.match(key)
            if match:
                object_rows.append([roi, profile, match.group(1), match.group(2), value, "simulator_runtime_counter"])
                continue
            match = replace_re.match(key)
            if match:
                replacement_rows.append([roi, profile, match.group(1), match.group(2), value])
                continue
            if key.startswith(("vm_l1_tlb_", "vm_l2_tlb_", "vm_translation_", "vm_pwc_", "vm_pte_", "vm_object_attribution_")):
                total_rows.append([roi, profile, key, value, "simulator_runtime_counter"])
        requesters = {obj: integer(scalars.get(f"vm_object_{obj}_translation_requesters", "0"),
                                  f"{arm}/{obj} requesters") for obj in OBJECTS}
        total = sum(requesters.values())
        for obj, count in requesters.items():
            object_rows.append([roi, profile, obj, "translation_requester_share",
                                f"{count / total:.12f}" if total else "NA", "derived_from_runtime_counters"])
    write_tsv(output / "TRANSLATION_TOTALS.tsv", ["roi", "profile", "metric", "value", "provenance"], total_rows)
    write_tsv(output / "OBJECT_VM_STATS.tsv", ["roi", "profile", "object_class", "metric", "value", "provenance"], object_rows)
    write_tsv(output / "L2_TLB_REPLACEMENT_MATRIX.tsv", ["roi", "profile", "incoming_object", "victim_object", "count"], replacement_rows)


def aggregate_exports(c4_root: Path, output: Path) -> None:
    layer: defaultdict[tuple[str, str, str, str, str], int] = defaultdict(int)
    data_replacement: defaultdict[tuple[str, str, str, str], int] = defaultdict(int)
    dram: defaultdict[tuple[str, str, str, str], int] = defaultdict(int)
    cross: defaultdict[tuple[str, str, str, str, str, str, str], int] = defaultdict(int)
    queue_sum: defaultdict[tuple[str, str, str], int] = defaultdict(int)
    queue_max: defaultdict[tuple[str, str, str], int] = defaultdict(int)
    native_rows: list[list[str]] = []
    windows: defaultdict[tuple[str, str, str], int] = defaultdict(int)
    for arm in ARMS:
        roi, profile = profile_from_arm(arm)
        directory = c4_root / "telemetry" / arm
        for name, layer_name in (("L1D_OBJECT_STATS.tsv", "L1D"), ("L2_REQUEST_CLASS_STATS.tsv", "DATA_L2")):
            _, rows = read_tsv(directory / name)
            for row in rows:
                if row["scope"] == "KERNEL":
                    layer[(roi, profile, layer_name, row.get("object_or_request_class", row.get("request_class", "MISSING")), row["outcome"])] += integer(row["count"], name)
        _, rows = read_tsv(directory / "L2_CLASS_REPLACEMENT_MATRIX.tsv")
        for row in rows:
            if row["scope"] == "KERNEL":
                data_replacement[(roi, profile, row["incoming_class"], row["victim_class"])] += integer(row["count"], "data replacement")
        _, rows = read_tsv(directory / "DRAM_REQUEST_CLASS_STATS.tsv")
        for row in rows:
            if row["scope"] != "KERNEL":
                continue
            fields = row["payload"].split("\t")
            if row["record_type"] == "m4c_telemetry_dram" and len(fields) == 3:
                klass, requests, bytes_ = fields
                dram[(roi, profile, klass, "requests")] += integer(requests, "DRAM requests")
                dram[(roi, profile, klass, "bytes")] += integer(bytes_, "DRAM bytes")
            elif row["record_type"] == "m4c_telemetry_dram_rw" and len(fields) == 5:
                klass, rr, rb, wr, wb = fields
                for metric, value in (("read_requests", rr), ("read_bytes", rb), ("write_requests", wr), ("write_bytes", wb)):
                    dram[(roi, profile, klass, metric)] += integer(value, "DRAM RW")
            else:
                fail(f"unexpected DRAM payload: {arm}")
        _, rows = read_tsv(directory / "CROSS_LAYER_OUTCOME_MATRIX.tsv")
        for row in rows:
            if row["scope"] != "KERNEL":
                continue
            fields = row["payload"].split("\t")
            if row["record_type"] == "m4c_telemetry_cross_l1" and len(fields) == 4:
                klass, translation, l1, count = fields
                cross[(roi, profile, klass, translation, l1, "NA", "L1_ONLY")] += integer(count, "cross L1")
            elif row["record_type"] == "m4c_telemetry_cross_l1_l2" and len(fields) == 5:
                klass, translation, l1, l2, count = fields
                cross[(roi, profile, klass, translation, l1, l2, "L1_L2")] += integer(count, "cross L1/L2")
            else:
                fail(f"unexpected cross-layer payload: {arm}")
        _, rows = read_tsv(directory / "L2_QUEUE_PRESSURE.tsv")
        for row in rows:
            if row["scope"] != "KERNEL":
                continue
            for metric in ("samples", "icnt_to_l2_total", "l2_to_dram_total", "dram_to_l2_total", "l2_to_icnt_total"):
                queue_sum[(roi, profile, metric)] += integer(row[metric], "queue total")
            for metric in ("icnt_to_l2_hwm", "l2_to_dram_hwm", "dram_to_l2_hwm", "l2_to_icnt_hwm"):
                queue_max[(roi, profile, metric)] = max(queue_max[(roi, profile, metric)], integer(row[metric], "queue high-water"))
        _, rows = read_tsv(directory / "NATIVE_MEMORY_SYSTEM_STATS.tsv")
        for row in rows:
            native_rows.append([roi, profile, row["scope"], row["metric"], row["value"], "existing_gpgpu_sim_stat"])
        _, rows = read_tsv(directory / "WINDOW_MEMORY_STATS.tsv")
        for row in rows:
            windows[(roi, profile, row["scope"])] += 1
    write_tsv(output / "L1D_L2_OBJECT_SUMMARY.tsv", ["roi", "profile", "layer", "class", "outcome", "count"],
              [(*key, value) for key, value in sorted(layer.items())])
    write_tsv(output / "DATA_L2_REPLACEMENT_MATRIX.tsv", ["roi", "profile", "incoming_class", "victim_class", "count"],
              [(*key, value) for key, value in sorted(data_replacement.items())])
    write_tsv(output / "DRAM_CLASS_SUMMARY.tsv", ["roi", "profile", "class", "metric", "value"],
              [(*key, value) for key, value in sorted(dram.items())])
    write_tsv(output / "CROSS_LAYER_TRANSLATION_L1D_L2.tsv", ["roi", "profile", "object_class", "translation_source", "l1d_outcome", "l2_outcome", "record_scope", "count"],
              [(*key, value) for key, value in sorted(cross.items())])
    rows = [(*key, value, "sum_over_kernel_records") for key, value in sorted(queue_sum.items())]
    rows += [(*key, value, "max_over_kernel_high_water") for key, value in sorted(queue_max.items())]
    write_tsv(output / "L2_QUEUE_PRESSURE_SUMMARY.tsv", ["roi", "profile", "metric", "value", "aggregation"], rows)
    write_tsv(output / "NATIVE_DRAM_MEMORY_SYSTEM_STATS.tsv", ["roi", "profile", "scope", "metric", "value", "provenance"], native_rows)
    write_tsv(output / "WINDOW_TELEMETRY_INVENTORY.tsv", ["roi", "profile", "window_scope", "record_rows"],
              [(*key, value) for key, value in sorted(windows.items())])


def latency_summary(output: Path) -> None:
    """Retain latency/queue timing facts without conflating their sources."""
    rows: list[list[str]] = []
    _, translation = read_tsv(output / "TRANSLATION_TOTALS.tsv")
    for row in translation:
        if any(token in row["metric"] for token in ("latency", "wait", "stall")):
            rows.append(["translation_runtime_counter", row["roi"], row["profile"],
                         "GLOBAL_OR_OBJECT", row["metric"], row["value"], row["provenance"]])
    _, native = read_tsv(output / "NATIVE_DRAM_MEMORY_SYSTEM_STATS.tsv")
    for row in native:
        if "latency" in row["metric"].lower():
            rows.append(["native_memory_system_stat", row["roi"], row["profile"],
                         row["scope"], row["metric"], row["value"], row["provenance"]])
    write_tsv(output / "LATENCY_SUMMARY.tsv", [
        "source", "roi", "profile", "scope", "metric", "value", "provenance",
    ], rows)


def offline_locality(c4_root: Path, output: Path) -> None:
    rows = []
    for roi in ("decode1", "prefill"):
        _, records = read_tsv(c4_root / "offline" / f"{roi}_locality.tsv")
        aggregate: defaultdict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for row in records:
            klass = row["object_class"]
            item = aggregate[klass]
            item["kernel_rows"] += 1
            for metric in ("memory_instructions", "lane_references", "requested_bytes", "unique_128b_lines", "unique_32b_sectors", "unique_64kb_pages", "unique_2mb_pages", "prior_kernel_line_overlap"):
                item[metric] += integer(row[metric], f"locality {metric}")
            for metric in ("line_access_max", "line_access_p50", "line_access_p90", "line_access_p99"):
                item[metric] = max(item[metric], integer(row[metric], f"locality {metric}"))
        db = sqlite3.connect(f"file:{c4_root / 'offline' / f'{roi}_locality.sqlite'}?mode=ro", uri=True)
        union = {kind: (lines, pages) for kind, lines, pages in db.execute("SELECT kind, COUNT(*), COUNT(DISTINCT line / 512) FROM prior GROUP BY kind")}
        db.close()
        for klass in sorted(aggregate):
            item = aggregate[klass]
            lines, pages = union.get(klass, (0, 0))
            rows.append([roi, klass, item["kernel_rows"], item["memory_instructions"], item["lane_references"], item["requested_bytes"],
                         item["unique_128b_lines"], item["unique_32b_sectors"], item["unique_64kb_pages"], item["unique_2mb_pages"],
                         lines, pages, item["prior_kernel_line_overlap"], item["line_access_max"], item["line_access_p50"], item["line_access_p90"], item["line_access_p99"]])
    header = [
        "roi", "object_class", "kernel_rows", "sum_memory_instructions", "sum_lane_references", "sum_requested_bytes",
        "sum_per_kernel_unique_128b_lines", "sum_per_kernel_unique_32b_sectors", "sum_per_kernel_unique_64kb_pages", "sum_per_kernel_unique_2mb_pages",
        "roi_union_unique_128b_lines", "roi_union_unique_64kb_pages", "prior_union_line_overlap_sum",
        "max_kernel_line_access_max", "max_kernel_line_access_p50", "max_kernel_line_access_p90", "max_kernel_line_access_p99",
    ]
    write_tsv(output / "OFFLINE_TRACE_LOCALITY_SUMMARY.tsv", header, rows)
    write_tsv(output / "TRACE_LOCALITY_OFFLINE.tsv", header, rows)


def input_index(c3: Path, c4: Path, output: Path) -> None:
    rows = []
    for path in sorted(c4.rglob("*")):
        if path.is_file() and path.suffix in (".tsv", ".md", ".sqlite"):
            rows.append(["C4", str(path.relative_to(c4)), sha256(path)])
    for arm in ARMS:
        for relative in ("RUN_MANIFEST.tsv", "run.log", "traces/kernelslist.g"):
            path = c3 / arm / relative
            rows.append(["C3", f"{arm}/{relative}", sha256(path)])
    write_tsv(output / "INPUT_ARTIFACT_INDEX.tsv", ["stage", "relative_path", "sha256"], rows)
    raw_log_rows = [
        [relative_path.split("/", 1)[0], relative_path, digest]
        for stage, relative_path, digest in rows
        if stage == "C3" and relative_path.endswith("/run.log")
    ]
    write_tsv(output / "RAW_LOG_INDEX.tsv", ["arm", "relative_path", "sha256"], raw_log_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument("--c4-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--framework-root", type=Path, required=True,
                        help="Framework checkout used to verify the permitted C4 parser lineage")
    args = parser.parse_args()
    c3 = args.runs_root.resolve()
    c4 = args.c4_root.resolve()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        fail(f"refusing to overwrite nonempty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    runs = collect_runs(c3)
    validate_framework_only_correction(args.framework_root.resolve())
    require_export_tree(c4, runs)
    run_matrix(runs, output)
    runtime_provenance(runs, output)
    config_provenance(runs, output)
    performance(runs, output)
    translation_and_objects(runs, output)
    aggregate_exports(c4, output)
    latency_summary(output)
    offline_locality(c4, output)
    input_index(c3, c4, output)
    write_tsv(output / "C4_VALIDATION.tsv", ["check", "result", "detail"], [
        ("all_eight_formal_arms", "PASS", "exit=0; markers=kernel-list; telemetry=kernel-list"),
        ("generic_paper_vm_invariants", "PASS", "PTE/requester/object conservation and terminal quiescence"),
        ("all_required_c4_exports", "PASS", "telemetry, native-memory and offline locality artifacts present"),
        ("source_provenance", "PASS", "export provenance equals each original formal manifest; permitted Framework-only parser lineage verified"),
        ("runtime_provenance", "PASS", "frozen simulator SHA256 and direct Core-local libcudart SHA256 recorded"),
        ("replay", "NOT_PERFORMED", "analysis reads existing logs and immutable artifacts only"),
    ])
    print(f"PASS C4_characterization={output}")


if __name__ == "__main__":
    main()
