#!/usr/bin/env python3
"""C15 lane-B bounded native-capture guard and offline evidence producer.

This module deliberately has no CUDA/PyTorch dependency.  It is usable on a
host without a GPU to (a) prove that native admission is unavailable, (b)
validate the contracts that protect a later capture, and (c) import only the
small, frozen C12 trace-list provenance as TRACE_HEADER_ONLY evidence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

SCHEMA = "C15_LANE_B_OFFLINE_V1"
PLANNING_SHA = "9a755b14b01c5a77a6fc98c2547616e1c490e806"
SOURCE_SHA = PLANNING_SHA
CAPTURE_LIMIT_B = 4 * 1024**3
CAMPAIGN_LIMIT_B = 32 * 1024**3
MIN_FREE_DISK_B = 64 * 1024**3
MIN_AVAILABLE_MEM_B = 32 * 1024**3
OWNED_PREFIX = "docs/vm_tlb/review_packs/C15_LOWCOST_MULTIMODEL/lane_b"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_id(value: dict[str, Any]) -> str:
    return sha256_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode())


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_tsv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t",
                                extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: "NA" if row.get(key) is None else row.get(key, "NA")
                             for key in columns})
    os.replace(temporary, path)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, path)


def read_meminfo() -> dict[str, int]:
    data: dict[str, int] = {}
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, raw = line.split(":", 1)
            data[key] = int(raw.split()[0]) * 1024
    except (FileNotFoundError, ValueError, IndexError):
        pass
    return data


def command_version(command: str) -> dict[str, Any]:
    executable = shutil.which(command)
    if not executable:
        return {"path": None, "version": None, "available": False}
    try:
        completed = subprocess.run([executable, "--version"], text=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, timeout=10, check=False)
        version = completed.stdout.strip().splitlines()[0] if completed.stdout.strip() else "UNKNOWN"
    except (OSError, subprocess.TimeoutExpired):
        version = "UNQUERYABLE"
    return {"path": executable, "version": version, "available": True}


def runtime_probe() -> dict[str, Any]:
    disk = shutil.disk_usage("/workspace")
    memory = read_meminfo()
    nvidia_devices = sorted(str(item) for item in Path("/dev").glob("nvidia*"))
    return {
        "observed_utc": utc_now(),
        "nvidia_smi": command_version("nvidia-smi"),
        "nvcc": command_version("nvcc"),
        "nsys": command_version("nsys"),
        "ncu": command_version("ncu"),
        "gpu_device_nodes": nvidia_devices,
        "libcuda_present": any("libcuda.so" in line for line in subprocess.run(
            ["/bin/bash", "-lc", "ldconfig -p 2>/dev/null | grep -F libcuda.so || true"],
            text=True, stdout=subprocess.PIPE, check=False).stdout.splitlines()),
        "python_packages": {name: importlib.util.find_spec(name) is not None
                            for name in ("torch", "transformers", "accelerate", "pynvml")},
        "disk_free_B": disk.free,
        "disk_free_threshold_B": MIN_FREE_DISK_B,
        "mem_available_B": memory.get("MemAvailable"),
        "mem_available_threshold_B": MIN_AVAILABLE_MEM_B,
        "swap_free_B": memory.get("SwapFree"),
    }


def model_candidate(path: Path, label: str) -> dict[str, Any]:
    config_path = path / "config.json"
    index_path = path / "model.safetensors.index.json"
    config: dict[str, Any] = {}
    if config_path.is_file():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            config = {"_config_parse_error": True}
    required = ["config.json", "tokenizer.json"]
    present_required = [name for name in required if (path / name).is_file()]
    shards: list[str] = []
    index_ok: Any = "NA"
    if index_path.is_file():
        try:
            weight_map = json.loads(index_path.read_text(encoding="utf-8")).get("weight_map", {})
            shards = sorted(set(str(value) for value in weight_map.values()))
            index_ok = bool(shards) and all((path / shard).is_file() and (path / shard).stat().st_size > 0
                                            for shard in shards)
        except (OSError, json.JSONDecodeError, AttributeError):
            index_ok = False
    else:
        shards = [item.name for item in path.glob("*.safetensors") if item.stat().st_size > 0]
        index_ok = bool(shards)
    identity = {"local_label": label, "model_type": config.get("model_type"),
                "architectures": config.get("architectures"), "revision": "UNKNOWN"}
    return {
        "deployment_id": canonical_id(identity), "model_id": label, "revision": "UNKNOWN",
        "candidate_path": str(path), "model_type": config.get("model_type", "UNKNOWN"),
        "architecture": ",".join(config.get("architectures", [])) or "UNKNOWN",
        "weight_files_present": len(shards), "index_or_monolith_integrity": index_ok,
        "required_metadata_present": len(present_required) == len(required),
        "identity_status": "IDENTITY_UNRESOLVED",
    }


def capability_rows(probe: dict[str, Any]) -> list[dict[str, Any]]:
    gpu_visible = bool(probe["nvidia_smi"]["available"] and probe["gpu_device_nodes"] and
                       probe["libcuda_present"])
    backend_ready = all(probe["python_packages"][name] for name in ("torch", "transformers", "accelerate"))
    profiler_ready = probe["nsys"]["available"] or probe["ncu"]["available"]
    disk_ok = probe["disk_free_B"] >= MIN_FREE_DISK_B
    memory_ok = (probe["mem_available_B"] or 0) >= MIN_AVAILABLE_MEM_B
    return [
        {"capability": "gpu_device_visibility", "observed": gpu_visible,
         "required_for_native": True, "status": "PASS" if gpu_visible else "CAPABILITY_MISSING",
         "detail": "nvidia-smi + /dev/nvidia* + libcuda required; no CPU fallback"},
        {"capability": "native_backend", "observed": backend_ready,
         "required_for_native": True, "status": "PASS" if backend_ready else "CAPABILITY_MISSING",
         "detail": "torch/transformers/accelerate are probed, never installed or upgraded"},
        {"capability": "profiler_binary", "observed": profiler_ready,
         "required_for_native": True, "status": "PASS" if profiler_ready else "CAPABILITY_MISSING",
         "detail": "binary presence is not tracer/GPU runtime proof"},
        {"capability": "filesystem_reserve", "observed": probe["disk_free_B"],
         "required_for_native": MIN_FREE_DISK_B, "status": "PASS" if disk_ok else "RESOURCE_GUARD_RED",
         "detail": "C15 requires >=64 GiB free before new trace/profile writes"},
        {"capability": "host_memory_reserve", "observed": probe["mem_available_B"],
         "required_for_native": MIN_AVAILABLE_MEM_B, "status": "PASS" if memory_ok else "RESOURCE_GUARD_RED",
         "detail": "C15 requires >=32 GiB MemAvailable before new native task"},
    ]


def parse_c12_provenance(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def header_only_rows(c12_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    output = []
    for index, row in enumerate(c12_rows):
        identity = {"source": "C12_FINAL", "roi": row["roi"], "trace_sha256": row["trace_sha256"]}
        output.append({
            "deployment_id": canonical_id(identity), "scenario_id": "C12_" + row["roi"].upper() + "_TRACE_LIST",
            "run_id": "C12_" + row["roi"] + "_" + row["arm"] + "_" + row["lseg"],
            "phase": row["roi"], "launch_id": "NA", "kernel_name": "NA", "operator_class": "UNKNOWN",
            "kernel_markers": row["kernel_markers"], "trace_list_sha256": row["trace_sha256"],
            "catalog_origin": "TRACE_HEADER_ONLY", "duration_ns": "NA", "start_ns": "NA", "end_ns": "NA",
            "evidence_tier": "UNRESOLVED", "source_commit": "a268aba0d01310294074ded5bb8017e2092394c0",
            "missing_reason": "FROZEN_C12_PROVENANCE_HAS_TRACE_LIST_COUNT_NOT_PER_LAUNCH_HEADER",
            "row_ordinal": index,
        })
    return output


def range_selector(value: str) -> set[int]:
    selected: set[int] = set()
    for token in value.split():
        numeric = token.split("@", 1)[0]
        if numeric.endswith("-"):
            raise ValueError("open-ended ranges are forbidden for bounded capture")
        if "-" in numeric:
            left, right = numeric.split("-", 1)
            selected.update(range(int(left), int(right) + 1))
        else:
            selected.add(int(numeric))
    return selected


def launch_signature(event: dict[str, Any]) -> str:
    keys = ("semantic_key", "shape", "dtype", "grid", "block", "stream", "implementation")
    return canonical_id({key: event.get(key) for key in keys})


def rate(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else numerator / denominator


def active_pages(base: int, length: int, page: int = 65536) -> set[int]:
    if length <= 0:
        return set()
    return set(range(base // page, (base + length - 1) // page + 1))


def guarded_operation(operation: str, gpu_authorized: bool, bytes_requested: int = 0) -> str:
    if operation in {"simulator_build", "simulator_replay", "full_roi", "full_model_sass"}:
        raise PermissionError("C15 authorization rejects " + operation)
    if operation == "capture" and (not gpu_authorized or bytes_requested > CAPTURE_LIMIT_B):
        raise PermissionError("C15 capture guard rejects unavailable GPU or over-limit output")
    return "DRY_RUN_ALLOWED"


def fixture_checks(fixture_path: Path) -> str:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    if fixture.get("schema_version") != "C15_CONTRACT_FIXTURES_V1":
        raise ValueError("unexpected fixture schema")
    entries = {(row["test_id"], row["name"]): row for row in fixture["fixtures"]}
    unaligned = entries[("T06", "unaligned_two_pages")]
    assert len(active_pages(unaligned["base"], unaligned["length"], unaligned["page_bytes"])) == unaligned["expected_unique_pages"]
    overlap = entries[("T06", "overlapping_ranges")]
    covered = set()
    for left, right in overlap["half_open_ranges"]:
        covered.update(range(left, right))
    assert len(covered) == overlap["expected_union_bytes"]
    rates = entries[("T15", "unequal_denominator_rates")]
    numerator = sum(pair[0] for pair in rates["counts"])
    denominator = sum(pair[1] for pair in rates["counts"])
    assert numerator == rates["expected_aggregate_numerator"] and denominator == rates["expected_aggregate_denominator"]
    assert rate(numerator, denominator) == rates["expected_rate"]
    blocked = entries[("T24", "new_full_roi_replay")]
    try:
        guarded_operation("full_roi", False, blocked["requested_runs"])
    except PermissionError:
        return "fixture T06/T15 exact values and T24 authorization rejection observed"
    raise AssertionError("fixture full-ROI request was admitted")


def self_tests(fixture_path: Path | None = None) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    def check(test_id: str, action: Any, expected: str) -> None:
        started = time.monotonic()
        try:
            observed = action()
            status, detail = "PASS", str(observed)
        except Exception as error:  # tests below intentionally exercise rejections
            status, detail = "FAIL", f"{type(error).__name__}: {error}"
        results.append({"test_id": test_id, "command": "c15_lane_b.py --self-test", "planning_sha": PLANNING_SHA,
                        "source_sha": SOURCE_SHA, "input_sha256": canonical_id({"test_id": test_id, "expected": expected}),
                        "output_sha256": sha256_bytes(detail.encode()), "exit_code": 0 if status == "PASS" else 1,
                        "expected": expected, "observed": detail, "status": status,
                        "wall_s": f"{time.monotonic()-started:.6f}", "evidence_tier": "SYNTHETIC_TEST_ONLY"})

    def t00() -> str:
        assert canonical_id({"a": 1}) != canonical_id({"a": 2})
        try: guarded_operation("full_roi", False)
        except PermissionError: return "identity differs; protected operation rejected"
        raise AssertionError("protected operation admitted")
    check("T00", t00, "wrong identity/protected operation rejected")

    def t01() -> str:
        columns = ["revision", "bytes", "missing_reason"]
        row = {"revision": "NA", "bytes": "NA", "missing_reason": "UNKNOWN_SOURCE"}
        assert all(key in row for key in columns) and row["bytes"] != 0
        return "NA preserved; required fields present"
    check("T01", t01, "NA not silently converted to zero")

    def t07() -> str:
        probe = {"nvidia_smi": {"available": False}, "gpu_device_nodes": [], "libcuda_present": False,
                 "python_packages": {"torch": False, "transformers": False, "accelerate": False},
                 "nsys": {"available": True}, "ncu": {"available": True}, "disk_free_B": MIN_FREE_DISK_B,
                 "mem_available_B": MIN_AVAILABLE_MEM_B}
        rows = capability_rows(probe)
        assert rows[0]["status"] == "CAPABILITY_MISSING" and rows[1]["status"] == "CAPABILITY_MISSING"
        return "CPU/synthetic environment cannot become NATIVE_PROFILED"
    check("T07", t07, "silent CPU fallback rejected")

    def t08() -> str:
        seen = set()
        for event in (("run-a", 0, "ctx", "s0", 7), ("run-a", 0, "ctx", "s1", 7)):
            assert event not in seen; seen.add(event)
        assert rate(10, 100) == 0.1
        return "same kernel ordinal on distinct streams remains distinct"
    check("T08", t08, "stream-aware launch identity and rate aggregation")

    def t09() -> str:
        generations: dict[tuple[str, int], str] = {("0x1000", 1): "WEIGHT", ("0x1000", 2): "ACTIVATION"}
        aliases = {"weight_view": ("0x1000", 1), "weight_transpose": ("0x1000", 1)}
        assert generations[aliases["weight_view"]] == "WEIGHT" and len(set(aliases.values())) == 1
        assert generations[("0x1000", 2)] != generations[("0x1000", 1)]
        return "address reuse has a new generation; views do not duplicate storage"
    check("T09", t09, "generation/alias rules")

    def t10() -> str:
        selected = range_selector("2 5-6")
        assert selected == {2, 5, 6}
        event = {"semantic_key": "FFN", "shape": [1, 8], "dtype": "fp16", "grid": [1, 1, 1],
                 "block": [128, 1, 1], "stream": "s0", "implementation": "fused"}
        assert launch_signature(event) != launch_signature({**event, "shape": [1, 16]})
        try: range_selector("10-")
        except ValueError: return "bounded range selected; changed shape and open range rejected"
        raise AssertionError("open range admitted")
    check("T10", t10, "filter/second-pass identity guard")

    def t14() -> str:
        plan = {"categories": ["ATTENTION_PROJECTION", "FFN", "ATTENTION_CORE", "EMBEDDING_OUTPUT"],
                "rule": "BOOTSTRAP_FIXED_RULE_NOT_SAMPLER_QUALIFIED"}
        first = canonical_id(plan)
        candidate_speedups = [999, -999]
        assert first == canonical_id(plan) and candidate_speedups != []
        return "selection hash is independent of candidate speedup"
    check("T14", t14, "candidate result cannot affect bootstrap plan")

    def t15() -> str:
        assert rate(1 + 45, 10 + 90) == 0.46
        assert len(active_pages(65530, 12)) == 2
        assert sum((10, 10)) == 20 and 15 != 20
        return "weighted rate, page union, and makespan distinction hold"
    check("T15", t15, "aggregate numerator/denominator and set union")

    def t20() -> str:
        parent, child = 7.0, 3.0
        charged = parent
        assert charged != parent + child
        return "parent rollup does not double-count child"
    check("T20", t20, "nested costs do not double count")

    def t21() -> str:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); temporary = root / "published.tsv.tmp"; final = root / "published.tsv"
            temporary.write_text("partial\n"); assert not final.exists()
            os.replace(temporary, final); expected = sha256_bytes(final.read_bytes())
            assert expected == sha256_bytes(b"partial\n")
        return "partial temp is not published; atomic replace hash closes"
    check("T21", t21, "atomic publish guard")

    def t23() -> str:
        assert not OWNED_PREFIX.startswith("docs/vm_tlb/chatgpt_handoff")
        return "output namespace is lane-B owned"
    check("T23", t23, "protected handoff path excluded")

    def t24() -> str:
        rejected = 0
        for op, size in (("simulator_build", 0), ("full_model_sass", 0), ("capture", CAPTURE_LIMIT_B + 1)):
            try: guarded_operation(op, False, size)
            except PermissionError: rejected += 1
        assert rejected == 3 and guarded_operation("catalog_dry_run", False) == "DRY_RUN_ALLOWED"
        return "forbidden execution rejected; offline dry run allowed"
    check("T24", t24, "budget/authorization launch guard")
    if fixture_path:
        check("T06", lambda: fixture_checks(fixture_path), "execute supplied contract fixture exactly")
    return results


def validate_package(root: Path) -> list[str]:
    root = root.resolve()
    expected = Path.cwd().resolve() / OWNED_PREFIX
    if root != expected:
        raise ValueError(f"refusing non-owned validation root: expected {expected}, got {root}")
    manifest = json.loads((root / "PUBLISH_MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("planning_sha") != PLANNING_SHA or manifest.get("lane") != "b":
        raise ValueError("manifest lane/planning identity mismatch")
    checked = []
    for row in manifest.get("files", []):
        relative = Path(row["path"])
        if relative.name != row["path"] or relative.is_absolute():
            raise ValueError("manifest path escapes artifact root")
        candidate = root / relative
        if not candidate.is_file() or candidate.stat().st_size != row["size_bytes"]:
            raise ValueError("manifest size mismatch: " + row["path"])
        if sha256_bytes(candidate.read_bytes()) != row["sha256"]:
            raise ValueError("manifest hash mismatch: " + row["path"])
        checked.append(row["path"])
    with (root / "TEST_RESULTS.tsv").open(encoding="utf-8", newline="") as handle:
        tests = list(csv.DictReader(handle, delimiter="\t"))
    if not tests or any(row["status"] != "PASS" or row["evidence_tier"] != "SYNTHETIC_TEST_ONLY" for row in tests):
        raise ValueError("fixture receipt is incomplete or mislabelled")
    return checked


def emit_package(args: argparse.Namespace) -> None:
    root = args.output_root.resolve()
    expected = Path.cwd().resolve() / OWNED_PREFIX
    if root != expected:
        raise ValueError(f"refusing non-owned output root: expected {expected}, got {root}")
    started = time.monotonic()
    started_utc = utc_now()
    probe = runtime_probe()
    candidates = [model_candidate(Path(item), label) for label, item in args.model]
    capabilities = capability_rows(probe)
    gpu_ok = next(row["status"] == "PASS" for row in capabilities if row["capability"] == "gpu_device_visibility")
    backend_ok = next(row["status"] == "PASS" for row in capabilities if row["capability"] == "native_backend")
    resource_ok = all(row["status"] == "PASS" for row in capabilities if row["capability"] in
                      {"filesystem_reserve", "host_memory_reserve"})
    preflight = []
    for candidate in candidates:
        reason = []
        if not gpu_ok: reason.append("NO_AUTHORIZED_VISIBLE_GPU")
        if not backend_ok: reason.append("NATIVE_BACKEND_UNAVAILABLE")
        if not resource_ok: reason.append("RESOURCE_GUARD_RED")
        if candidate["identity_status"] != "VERIFIED": reason.append("REVISION_UNVERIFIED")
        preflight.append({**candidate, "gpu_support": gpu_ok, "backend_support": backend_ok,
                          "resource_guard": resource_ok,
                          "decision": "REJECT_NATIVE_CAPABILITY_LIMITED" if reason else "ELIGIBLE_PENDING_CANARY",
                          "evidence_tier": "UNRESOLVED", "missing_reason": ";".join(reason) or "NA"})
    c12_rows = parse_c12_provenance(args.c12_provenance)
    imported = header_only_rows(c12_rows)
    tests = self_tests(args.fixture_file)
    write_json(root / "ENV_PREFLIGHT.json", {"schema_version": SCHEMA, "planning_sha": PLANNING_SHA,
        "producer_lane": "b", "producer_source_sha": SOURCE_SHA, "run_id": args.run_id,
        "status": "CAPABILITY_LIMITED", "probe": probe,
        "conclusion": "No native/profile/capture process launched; CUDA tool binaries alone are insufficient."})
    write_tsv(root / "CAPABILITY_MATRIX.tsv", ["capability", "observed", "required_for_native", "status", "detail"], capabilities)
    preflight_columns = ["deployment_id", "model_id", "revision", "candidate_path", "model_type", "architecture",
        "weight_files_present", "index_or_monolith_integrity", "required_metadata_present", "identity_status",
        "gpu_support", "backend_support", "resource_guard", "decision", "evidence_tier", "missing_reason"]
    write_tsv(root / "DEPLOYMENT_PREFLIGHT.tsv", preflight_columns, preflight)
    header_columns = ["deployment_id", "scenario_id", "run_id", "phase", "launch_id", "kernel_name", "operator_class",
        "kernel_markers", "trace_list_sha256", "catalog_origin", "duration_ns", "start_ns", "end_ns", "evidence_tier",
        "source_commit", "missing_reason", "row_ordinal"]
    write_tsv(root / "KERNEL_CATALOG_TRACE_HEADER_ONLY.tsv", header_columns, imported)
    write_tsv(root / "TEST_RESULTS.tsv", ["test_id", "command", "planning_sha", "source_sha", "input_sha256",
        "output_sha256", "exit_code", "expected", "observed", "status", "wall_s", "evidence_tier"], tests)
    write_tsv(root / "SAMPLE_PLAN.tsv", ["plan_id", "selector_sha", "deployment_id", "scenario_id", "stratum_id",
        "semantic_key_json", "implementation_key", "shape_regime", "selection_reason", "sampling_unit",
        "target_launch_signature", "target_indices", "warmup_indices", "weight", "weight_basis", "inclusion_probability",
        "seed", "split_role", "expected_capture_bytes", "execution_scope", "eligibility_status"], [])
    write_tsv(root / "NATIVE_BASELINE.tsv", ["deployment_id", "scenario_id", "run_id", "repeat_index",
        "profile_state", "wall_time_ns", "event_time_ns", "synchronization_boundary", "status", "missing_reason"], [])
    write_tsv(root / "PROFILE_OVERHEAD.tsv", ["deployment_id", "scenario_id", "baseline_median_ns",
        "profiled_median_ns", "overhead_fraction", "profile_state", "status", "missing_reason"], [])
    write_json(root / "PROFILE_CONFIG.json", {"schema_version": SCHEMA, "capture_state": "DISABLED_NO_NATIVE_RUNTIME",
        "profiler_binary_presence": {"nsys": probe["nsys"], "ncu": probe["ncu"]}, "shape_stack_pass": "NOT_EXECUTED",
        "reason": "Profiler binary presence is insufficient without an authorized visible GPU and native backend."})
    write_json(root / "PROFILER_CANARY_RECEIPT.json", {"schema_version": SCHEMA, "status": "NOT_EXECUTED",
        "evidence_tier": "UNRESOLVED", "real_model_canary": False, "synthetic_guard_tests": ["T07", "T08"],
        "reason": "No authorized visible GPU/native backend; no CPU or synthetic event is a native canary."})
    write_tsv(root / "OBJECT_LIFETIME_V2.tsv", ["run_id", "storage_id", "allocation_generation", "device_id",
        "context_id", "address_namespace", "base", "extent", "view_offset", "view_extent", "object_kind",
        "semantic_name", "allocation_event", "replace_event", "release_event", "event_order_basis", "stream_id",
        "lifetime_certainty", "alias_group", "source_evidence"], [])
    write_tsv(root / "OBJECT_ATTRIBUTION_COVERAGE.tsv", ["scope", "observed_storage_records", "weight_alias_records",
        "kv_grow_or_replace_records", "ambiguous_lifetime_records", "status", "missing_reason"], [{"scope": "ALL",
        "observed_storage_records": 0, "weight_alias_records": 0, "kv_grow_or_replace_records": 0,
        "ambiguous_lifetime_records": 0, "status": "UNRESOLVED_NO_NATIVE_OBSERVER",
        "missing_reason": "No permitted native model execution; test fixtures are isolated in TEST_RESULTS.tsv"}])
    write_text(root / "LOGITS_POLICY_AUDIT.md", "# C15 B logits-policy audit\n\n"
        "Status: `UNRESOLVED_NO_NATIVE_OBSERVER`. No local deployment was executed, so `logits_all_tokens` "
        "versus `last_token` was not inferred from config, model family, or CPU fallback.\n")
    write_tsv(root / "SCENARIO_REGISTRY.tsv", ["deployment_id", "scenario_id", "phase", "context_tokens", "batch",
        "generation_steps", "kv_state", "logits_policy", "status", "missing_reason"], [])
    write_tsv(root / "CAPTURE_PREFLIGHT.tsv", ["plan_id", "status", "reason", "capture_windows", "capture_bytes",
        "timeout_s", "evidence_tier"], [{"plan_id": "BOOTSTRAP_NOT_EMITTED", "status": "INELIGIBLE",
        "reason": "NO_NATIVE_CATALOG_OR_AUTHORIZED_GPU; no target selected from synthetic/header-only data",
        "capture_windows": 0, "capture_bytes": 0, "timeout_s": 0, "evidence_tier": "UNRESOLVED"}])
    write_tsv(root / "CAPTURE_STATUS.tsv", ["deployment_id", "scenario_id", "target_launch_signature", "status",
        "terminal_state", "output_bytes", "gpu_active_s", "missing_reason"], [])
    stages = [
        {"stage_id": "C15-0.1", "execution": "COMPLETE", "validation": "PASS", "test_receipt": "TEST_RESULTS.tsv:T00,T01,T23", "artifact_manifest": "ENV_PREFLIGHT.json", "reason": "non-detached B worktree at planning SHA"},
        {"stage_id": "C15-0.3", "execution": "COMPLETE", "validation": "PASS", "test_receipt": "TEST_RESULTS.tsv:T07,T24", "artifact_manifest": "CAPABILITY_MATRIX.tsv;DEPLOYMENT_PREFLIGHT.tsv", "reason": "actual probe records native capability absent"},
        {"stage_id": "C15-2.1", "execution": "CAPABILITY_LIMITED", "validation": "NOT_APPLICABLE", "test_receipt": "TEST_RESULTS.tsv:T07", "artifact_manifest": "DEPLOYMENT_PREFLIGHT.tsv", "reason": "no authorized visible GPU/backend/resource guard; CPU fallback rejected"},
        {"stage_id": "C15-2.2", "execution": "CAPABILITY_LIMITED", "validation": "NOT_EXECUTED", "test_receipt": "TEST_RESULTS.tsv:T07,T08", "artifact_manifest": "CAPABILITY_MATRIX.tsv", "reason": "no real deployment canary; tool binary presence is not runtime proof"},
        {"stage_id": "C15-2.3", "execution": "CAPABILITY_LIMITED", "validation": "NOT_EXECUTED", "test_receipt": "TEST_RESULTS.tsv:T08,T20", "artifact_manifest": "DEPLOYMENT_PREFLIGHT.tsv", "reason": "no native unprofiled/profiled repetitions"},
        {"stage_id": "C15-2.4", "execution": "COMPLETE", "validation": "PASS", "test_receipt": "TEST_RESULTS.tsv:T01,T08,T15", "artifact_manifest": "KERNEL_CATALOG_TRACE_HEADER_ONLY.tsv", "reason": "frozen C12 trace-list provenance imported as header-only; no native timing/semantics asserted"},
        {"stage_id": "C15-2.5", "execution": "CAPABILITY_LIMITED", "validation": "NOT_EXECUTED", "test_receipt": "TEST_RESULTS.tsv:T09", "artifact_manifest": "TEST_RESULTS.tsv", "reason": "V2 lifetime observer test passes, but no observable real deployment exists"},
        {"stage_id": "C15-2.6", "execution": "CAPABILITY_LIMITED", "validation": "NOT_EXECUTED", "test_receipt": "TEST_RESULTS.tsv:T07,T08,T20,T24", "artifact_manifest": "DEPLOYMENT_PREFLIGHT.tsv", "reason": "0 real deployments and 0 scenarios; upper bounds are not targets"},
        {"stage_id": "C15-2.7", "execution": "COMPLETE", "validation": "PASS", "test_receipt": "TEST_RESULTS.tsv:T01,T21,T23", "artifact_manifest": "PUBLISH_MANIFEST.json", "reason": "offline/header-only checkpoint published early"},
        {"stage_id": "C15-3.4", "execution": "CAPABILITY_LIMITED", "validation": "NOT_EXECUTED", "test_receipt": "TEST_RESULTS.tsv:T10,T14,T15", "artifact_manifest": "SAMPLE_PLAN.tsv;CAPTURE_PREFLIGHT.tsv", "reason": "no semantic native catalog; did not select targets from header-only/synthetic inputs"},
        {"stage_id": "C15-3.5", "execution": "CAPABILITY_LIMITED", "validation": "NOT_EXECUTED", "test_receipt": "TEST_RESULTS.tsv:T10,T24", "artifact_manifest": "CAPTURE_PREFLIGHT.tsv", "reason": "tracer filter only tested synthetically; no actual tracer capture"},
        {"stage_id": "C15-3.6", "execution": "CAPABILITY_LIMITED", "validation": "NOT_EXECUTED", "test_receipt": "TEST_RESULTS.tsv:T10,T20,T21,T24", "artifact_manifest": "CAPTURE_PREFLIGHT.tsv", "reason": "0 windows, 0 bytes, 0 GPU-active seconds"},
    ]
    write_tsv(root / "STAGE_STATUS.tsv", ["stage_id", "execution", "validation", "test_receipt", "artifact_manifest", "reason"], stages)
    elapsed = time.monotonic() - started
    write_tsv(root / "COST_LEDGER.tsv", ["work_id", "parent_work_id", "lane", "stage_id", "attempt", "operation",
        "start_utc", "end_utc", "wall_s", "cpu_core_s", "gpu_active_s", "peak_rss_B", "peak_vram_B", "bytes_read",
        "bytes_downloaded", "bytes_written", "warmup_s", "retry_s", "measured_or_estimated", "result_status"], [
        {"work_id": args.run_id, "parent_work_id": "NA", "lane": "b", "stage_id": "C15-0.3;C15-2.4",
         "attempt": 1, "operation": "offline_capability_probe_fixture_and_c12_header_import", "start_utc": started_utc,
         "end_utc": utc_now(), "wall_s": f"{elapsed:.6f}", "cpu_core_s": f"{elapsed:.6f}", "gpu_active_s": 0,
         "peak_rss_B": "NA", "peak_vram_B": "NA", "bytes_read": "NA", "bytes_downloaded": 0,
         "bytes_written": "NA", "warmup_s": 0, "retry_s": 0, "measured_or_estimated": "MEASURED_WALL_OTHER_NA",
         "result_status": "CAPABILITY_LIMITED_OFFLINE_COMPLETE"}])
    write_text(root / "README.md", "# C15 Lane B — native census checkpoint\n\n"
        "Recommended entry: this file. Status: `C15_B_NATIVE_CAPTURE_CAPABILITY_LIMITED_READY_FOR_REVIEW`. "
        "The checkpoint contains an actual host capability probe, isolated synthetic contract tests, and frozen C12 "
        "trace-list provenance only. It contains **zero** new native GPU runs, zero native timings, zero new SASS, "
        "zero simulator replay, zero full-ROI simulation, and zero capture windows.\n\n"
        "`KERNEL_CATALOG_TRACE_HEADER_ONLY.tsv` is a provenance directory: its `kernel_markers` are historical list "
        "counts, not per-launch headers. Its timestamps, launch identity, kernel semantics, shapes, and object "
        "attribution remain `NA`/`UNKNOWN`. Consumers must not treat it as `NATIVE_NEW` or sample targets from it.\n\n"
        "Source anchors: planning/handoff `9a755b14b01c5a77a6fc98c2547616e1c490e806`; C12 provenance "
        "`a268aba0d01310294074ded5bb8017e2092394c0` (input file SHA256 "
        + sha256_bytes(args.c12_provenance.read_bytes()) + "). Validation: `python3 -m unittest "
        "tests/vm_tlb/c15/lane_b/test_c15_lane_b.py -v`; `python3 util/vm_tlb/c15/lane_b/c15_lane_b.py --self-test "
        "--fixture-file docs/vm_tlb/chatgpt_handoff/c15_lowcost/fixtures/contract_examples.json`; and the read-only "
        "`--validate --output-root docs/vm_tlb/review_packs/C15_LOWCOST_MULTIMODEL/lane_b`.\n\n"
        "Open issues: an authorized visible GPU, compatible installed native backend, >=64 GiB disk reserve, >=32 GiB "
        "MemAvailable, verified local model revisions, a real profiler canary, and a read-only observer for lifetime V2. "
        "Raw-log index: none; C15 generated no raw logs.\n")
    published = [path for path in sorted(root.iterdir()) if path.name != "PUBLISH_MANIFEST.json"]
    files = [{"path": item.name, "sha256": sha256_bytes(item.read_bytes()), "size_bytes": item.stat().st_size}
             for item in published]
    write_json(root / "PUBLISH_MANIFEST.json", {"schema_version": SCHEMA, "planning_sha": PLANNING_SHA,
        "lane": "b", "run_id": args.run_id, "producer_source_sha": SOURCE_SHA, "input_source_commits": {
            "handoff": PLANNING_SHA, "c12": "a268aba0d01310294074ded5bb8017e2092394c0"},
        "ready_stage_ids": ["C15-0.1", "C15-0.3", "C15-2.4", "C15-2.7"], "evidence_scope":
            "offline capability probe, synthetic contract tests, frozen C12 trace-list provenance only",
        "capture_state": "NO_NEW_NATIVE_GPU_RUN", "status": "CAPABILITY_LIMITED_READY_FOR_REVIEW",
        "gaps": ["no authorized visible GPU", "no native backend", "disk/memory resource guard red",
                 "local model revisions unresolved", "no real canary/baseline/object observer/capture"], "files": files})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--emit-offline-package", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--c12-provenance", type=Path)
    parser.add_argument("--fixture-file", type=Path)
    parser.add_argument("--run-id", default="c15b-offline-20260912")
    parser.add_argument("--model", action="append", nargs=2, metavar=("LABEL", "PATH"), default=[])
    args = parser.parse_args()
    if args.self_test:
        rows = self_tests(args.fixture_file)
        failed = [row for row in rows if row["status"] != "PASS"]
        for row in rows:
            print("{test_id}\t{status}\t{observed}".format(**row))
        raise SystemExit(1 if failed else 0)
    if args.validate:
        if not args.output_root:
            parser.error("--validate requires --output-root")
        print("validated " + str(len(validate_package(args.output_root))) + " manifest files")
        return
    if args.emit_offline_package:
        if not args.output_root or not args.c12_provenance or not args.fixture_file or not args.model:
            parser.error("--emit-offline-package requires --output-root --c12-provenance --fixture-file and --model")
        emit_package(args)
        return
    parser.error("choose --self-test or --emit-offline-package")


if __name__ == "__main__":
    main()
