#!/usr/bin/env python3
"""Close the bounded exact-target NVBit discovery diagnostic without overclaiming.

The two raw roots stay outside Git.  This publisher verifies their independent
remote manifests locally, then publishes compact evidence that distinguishes a
target-callback-absent timeout from actual related-function discovery work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, sha256_file, valid_sha256


SCHEMA = "C16_G_RETRY570_EXACT_DISCOVERY_BOUNDARY_CLOSEOUT_V1"
STATUS = "NVBIT_RETRY570_EXACT_TARGET_DISCOVERY_INCONCLUSIVE_PRE_LAUNCH_CALLBACK_BOUNDARY"
EXACT_TARGET = (
    "_ZN2at6native44_GLOBAL__N__50c743a2_11_Indexing_cu_89862edb21"
    "indexSelectLargeIndexIN3c104HalfEljLi2ELi2ELin2ELb1EEEvNS_4cuda6detail10"
    "TensorInfoIT_T1_EENS7_IKS8_S9_EENS7_IKT0_S9_EEiiS9_S9_l"
)
ATTEMPTS = (
    {
        "key": "DISCOVERY_ONLY_INITIAL",
        "root_name": "retry570_exact_discovery_only_20260913_245fac98",
        "runtime_commit": "245fac983faf8188044b4ce6926488972fcac0f6",
        "tool_sha256": "0dece73e2609dab44794c317e6c638ddd206ade9eaf486183f16bf5bc8ed2179",
    },
    {
        "key": "PRE_TARGET_LOOKUP_BOUNDARY",
        "root_name": "retry570_exact_discovery_prelookup_20260913_845cff82",
        "runtime_commit": "845cff8256391e2d8cd0919afc3a3581353ca126",
        "tool_sha256": "910adfb0129f4df4ff7c4b451c8a27d9e47a80188dbcf95460b601348e3db8e5",
    },
)
REMOTE_MANIFEST = "REMOTE_ARTIFACT_MANIFEST.json"
RAW_INDEX = "RAW_ARTIFACT_INDEX.json"
RECEIPT = "RETRY570_EXACT_DISCOVERY_BOUNDARY_RECEIPT.json"
TRANSFER = "RETRY570_EXACT_DISCOVERY_BOUNDARY_TRANSFER_RECEIPT.json"
MATRIX = "EXACT_TARGET_DISCOVERY_MATRIX.tsv"
REPORT = "EXACT_TARGET_DISCOVERY_REPORT.md"
MANIFEST = "PUBLISH_MANIFEST.json"
VALIDATION = "PUBLISH_VALIDATION_RECEIPT.json"
PAYLOADS = (REPORT, MATRIX, RECEIPT, RAW_INDEX, TRANSFER)


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON object: {path}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"not a JSON object: {path}")
    return value


def _remote_tree_sha(rows: list[dict[str, Any]]) -> str:
    return hashlib.sha256(canonical_json(rows).encode("utf-8")).hexdigest()


def _parse_events(stdout: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in stdout.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("C16_EXACT_DISCOVERY ts_us="):
            rows.append(dict(re.findall(r"(\w+)=([^ ]+)", line)))
    return rows


def _has_child_stage(stdout: Path, stage: str) -> bool:
    return f'"stage": "{stage}"' in stdout.read_text(encoding="utf-8", errors="replace")


def _gpu_util(row: dict[str, Any]) -> int:
    try:
        return int(str(row["gpu_utilization_and_memory"]).split(",", 1)[0].strip())
    except (KeyError, ValueError, IndexError) as exc:
        raise ContractError("sample lacks parseable GPU utilization") from exc


def _tree_cpu(row: dict[str, Any]) -> float:
    tree = row.get("process_tree")
    if not isinstance(tree, list) or len(tree) != 1 or not isinstance(tree[0], dict):
        raise ContractError("process-tree evidence unexpectedly has descendants or is malformed")
    try:
        return float(tree[0]["cpu_percent"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ContractError("sample lacks process CPU evidence") from exc


def _remote_payloads(root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = _load(root / REMOTE_MANIFEST)
    rows = manifest.get("payloads")
    if (manifest.get("schema_version") != "C16_RETRY570_REMOTE_RAW_MANIFEST_V1" or
            not isinstance(rows, list) or manifest.get("payload_count") != len(rows) or
            manifest.get("payload_tree_sha256") != _remote_tree_sha(rows)):
        raise ContractError(f"remote payload manifest malformed: {root}")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ContractError("remote payload row is not an object")
        name, size, digest = row.get("logical_path"), row.get("bytes"), row.get("sha256")
        if (not isinstance(name, str) or not name or name in seen or not isinstance(size, int) or size < 0 or
                not valid_sha256(digest)):
            raise ContractError("remote payload row has invalid path/size/SHA")
        seen.add(name)
        item = root / name
        if not item.is_file() or item.stat().st_size != size or sha256_file(item) != digest:
            raise ContractError(f"local raw lacks remote existence/size/SHA closure: {item}")
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and p.name != REMOTE_MANIFEST}
    if actual != seen:
        raise ContractError("remote payload manifest does not enumerate the materialized raw tree exactly")
    return manifest, rows


def _observe_attempt(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    manifest, rows = _remote_payloads(root)
    receipt = _load(root / "receipt.json")
    if (receipt.get("status") != "BOUNDED_TIMEOUT_DISCOVERY_LAST_MARKER_RETAINED" or
            receipt.get("terminal_status") != "BOUNDED_TIMEOUT" or
            receipt.get("scientific_eligible") is not False or receipt.get("trace_generated") is not False or
            receipt.get("raw_trace_bytes") != 0 or receipt.get("wall_limit_seconds") != 60 or
            receipt.get("runtime_code_commit") != spec["runtime_commit"] or
            receipt.get("exact_target_mangled") != EXACT_TARGET or
            receipt.get("tool", {}).get("sha256") != spec["tool_sha256"]):
        raise ContractError(f"attempt identity/status differs: {root.name}")
    if not isinstance(receipt.get("stack_snapshots"), list) or not receipt["stack_snapshots"]:
        raise ContractError("non-destructive stack snapshot evidence is absent")
    stdout = root / "stdout.log"
    if not _has_child_stage(stdout, "EXACT_TARGET_SUBMISSION_BEGIN"):
        raise ContractError("exact target submission boundary is absent")
    events = _parse_events(stdout)
    prohibited = ("TARGET_CALLBACK_ENTER", "RELATED_FUNCTIONS_BEGIN", "RELATED_FUNCTIONS_END", "FUNCTION_BEGIN", "FUNCTION_END", "DISCOVERY_COMPLETE", "TARGET_REUSE_CALLBACK")
    if any(row.get("stage") in prohibited for row in events):
        raise ContractError("timeout cannot be classified pre-target-callback when target discovery markers exist")
    samples: list[dict[str, Any]] = []
    for line in (root / "samples.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ContractError("sample stream contains invalid JSON") from exc
        if not isinstance(value, dict):
            raise ContractError("sample stream row is not an object")
        if isinstance(value.get("stage"), dict) and value["stage"].get("stage") == "EXACT_TARGET_SUBMISSION_BEGIN":
            samples.append(value)
    if len(samples) < 2 or not all(_gpu_util(row) == 0 for row in samples):
        raise ContractError("post-submission samples do not prove no GPU execution progress")
    cpu = [_tree_cpu(row) for row in samples]
    return {
        "spec": spec,
        "root": root,
        "manifest": manifest,
        "manifest_sha256": sha256_file(root / REMOTE_MANIFEST),
        "rows": rows,
        "receipt": receipt,
        "events": events,
        "post_submission_samples": len(samples),
        "cpu_min_percent": min(cpu),
        "cpu_max_percent": max(cpu),
        "gpu_attached_samples": sum(bool(row.get("child_pid_present_in_gpu_processes")) for row in samples),
        "pre_lookup_begin_count": sum(row.get("stage") == "PRE_TARGET_NAME_LOOKUP_BEGIN" for row in events),
        "pre_lookup_end_count": sum(row.get("stage") == "PRE_TARGET_NAME_LOOKUP_END" for row in events),
        "pre_lookup_max_us": max((int(row.get("elapsed_us", "0")) for row in events if row.get("stage") == "PRE_TARGET_NAME_LOOKUP_END"), default=None),
    }


def observe(raw_base: Path) -> list[dict[str, Any]]:
    attempts = [_observe_attempt(raw_base / spec["root_name"], spec) for spec in ATTEMPTS]
    first, second = attempts
    if first["pre_lookup_begin_count"] or first["pre_lookup_end_count"]:
        raise ContractError("initial tool unexpectedly claims pre-lookup instrumentation")
    if second["pre_lookup_begin_count"] != 4 or second["pre_lookup_end_count"] != 4 or second["pre_lookup_max_us"] is None or second["pre_lookup_max_us"] > 1_000:
        raise ContractError("pre-target lookup boundary did not establish four bounded completed lookups")
    return attempts


def raw_index(attempts: list[dict[str, Any]], raw_base: Path) -> dict[str, Any]:
    return {
        "schema_version": "C16_G_RETRY570_EXACT_DISCOVERY_RAW_INDEX_V1",
        "status": "LOCAL_HASH_CLOSED_NONSCIENTIFIC_DIAGNOSTIC_ONLY",
        "scientific_eligible": False,
        "local_raw_base": str(raw_base),
        "attempts": [{
            "attempt": item["spec"]["key"], "remote_raw_root": str(item["manifest"]["root"]),
            "local_raw_root": str(item["root"]), "remote_manifest_sha256": item["manifest_sha256"],
            "payload_tree_sha256": item["manifest"]["payload_tree_sha256"], "payload_count": len(item["rows"]),
            "total_bytes": sum(int(row["bytes"]) for row in item["rows"]), "entries": item["rows"],
        } for item in attempts],
        "remote_only_required_artifact_count": 0,
        "raw_payloads_committed": False,
    }


def matrix(attempts: list[dict[str, Any]]) -> str:
    lines = ["attempt\truntime_source_commit\ttool_sha256\trun_id\telapsed_seconds\ttarget_submission_observed\ttarget_callback_observed\trelated_function_count\tunique_function_count\tstatic_instruction_count\tpre_lookup_begin_count\tpre_lookup_end_count\tpre_lookup_max_us\tpost_submission_samples\tcpu_min_percent\tcpu_max_percent\tgpu_attached_samples\tgpu_util_percent\tscientific_eligible\n"]
    for item in attempts:
        receipt = item["receipt"]
        lines.append("\t".join(map(str, (
            item["spec"]["key"], item["spec"]["runtime_commit"], item["spec"]["tool_sha256"], receipt["run_id"],
            receipt["elapsed_seconds"], "TRUE", "FALSE", "NOT_OBSERVED", "NOT_OBSERVED", "NOT_OBSERVED",
            item["pre_lookup_begin_count"], item["pre_lookup_end_count"], item["pre_lookup_max_us"] if item["pre_lookup_max_us"] is not None else "NA",
            item["post_submission_samples"], item["cpu_min_percent"], item["cpu_max_percent"], item["gpu_attached_samples"], 0, "FALSE",
        ))) + "\n")
    return "".join(lines)


def closeout_receipt(attempts: list[dict[str, Any]], raw_index_path: Path) -> dict[str, Any]:
    second = attempts[1]
    return {
        "schema_version": SCHEMA,
        "status": STATUS,
        "scientific_eligible": False,
        "scope": "EXACT_PYTORCH_INDEXSELECT_DISCOVERY_ONLY_NOT_MODEL_NOT_TRACE_NOT_SCIENTIFIC_CAPTURE_NOT_C_TARGET_NOT_TIMING",
        "historical_exact_target_mangled": EXACT_TARGET,
        "runtime_producer_commits": {item["spec"]["key"]: item["spec"]["runtime_commit"] for item in attempts},
        "classification": {
            "exact_boundary": "AFTER_PYTORCH_EXACT_TARGET_SUBMISSION_BEGIN_BEFORE_NVBIT_CUDA_LAUNCH_CALLBACK_ENTRY",
            "A_related_function_graph_total_expansion": "NOT_OBSERVED_TARGET_CALLBACK_ABSENT",
            "B_pathological_related_function": "NOT_OBSERVED_TARGET_CALLBACK_ABSENT",
            "C_duplicate_repeated_instruction_discovery": "NOT_OBSERVED_TARGET_CALLBACK_ABSENT",
            "D_nvbit_get_related_functions": "NOT_OBSERVED_TARGET_CALLBACK_ABSENT",
            "E_insertion_enable_launch": "NOT_REACHED_DISCOVERY_ONLY_MODE_AND_TARGET_CALLBACK_ABSENT",
        },
        "requested_answers": {
            "exact_kernel_name": EXACT_TARGET,
            "related_function_count": "NOT_OBSERVED_TARGET_CALLBACK_ABSENT",
            "unique_function_count": "NOT_OBSERVED_TARGET_CALLBACK_ABSENT",
            "enumerated_static_instruction_count": "NOT_OBSERVED_TARGET_CALLBACK_ABSENT",
            "per_function_get_instrs_timing_distribution": "NOT_OBSERVED_TARGET_CALLBACK_ABSENT",
            "pathological_function": "NOT_OBSERVED_TARGET_CALLBACK_ABSENT",
            "duplicate_repeated_discovery": "NOT_OBSERVED_TARGET_CALLBACK_ABSENT",
            "first_vs_second_identical_kernel_reuse": "NOT_OBSERVED_SECOND_OPERATION_NOT_REACHED",
            "A_to_E_class": "PRE_TARGET_CUDA_LAUNCH_CALLBACK_BOUNDARY_NOT_CLASSIFIABLE_AS_A_TO_E",
            "smallest_next_experiment": "NOT_AUTHORIZED: a bounded exact-input no-op NVBit CUDA-launch-callback arrival probe with no function-name lookup, related-function discovery, instruction enumeration, insertion, enable, trace, model, or C target",
        },
        "pre_target_lookup_control": {"completed_lookup_count": second["pre_lookup_end_count"], "maximum_elapsed_us": second["pre_lookup_max_us"], "interpretation": "four earlier CUDA-launch function-name lookups completed; the exact target emitted no PRE_TARGET_NAME_LOOKUP_BEGIN"},
        "process_evidence": {"post_submission_samples": second["post_submission_samples"], "process_cpu_percent_range": [second["cpu_min_percent"], second["cpu_max_percent"]], "gpu_utilization_percent": 0, "gpu_attached_samples": second["gpu_attached_samples"], "process_tree_descendant_count": 0, "nvdisasm_child_observed": False, "kernel_stack_symbolization": "UNAVAILABLE_PERMISSION_DENIED; non-destructive status/wchan/syscall snapshots retained"},
        "independent_c4_reference": {"source_publish_manifest_sha256": "7b803deecea24e273f3c368081174a27910e7bfd94f503232c8e61cd4129a553", "related_function_count": 89, "enumerated_function_count": 88, "static_instruction_count": 66032, "cumulative_get_instrs_seconds": 19.969523, "applicability": "GENERAL_REFERENCE_ONLY; MUST_NOT_BE_ASSIGNED_TO_THE_EXACT_INDEXSELECT_TARGET_WITHOUT_TARGET_CALLBACK_EVIDENCE"},
        "raw_artifact_index": {"path": RAW_INDEX, "sha256": sha256_file(raw_index_path)},
        "remote_only_required_artifact_count": 0,
        "active_gpu_process_count_at_closeout": 0,
        "terminal_state": "INCONCLUSIVE_NO_MODEL_TRACE_OR_C_TARGET_AUTHORIZATION",
    }


def report(attempts: list[dict[str, Any]]) -> str:
    second = attempts[1]
    return f"""# Retry570 exact-target discovery boundary closeout

Status: `{STATUS}`.

This is a bounded, diagnostic-only replay of the historical exact
`indexSelectLargeIndex` PyTorch candidate. It ran no Llama/Qwen model, trace,
scientific capture, C target, insertion, or `nvbit_enable_instrumented`; the
closed 300-second watch and the historical 6+6 windows were not rerun.

Both 60-second attempts used the same frozen R2_D0_I64_A input and runtime
identity. Each emitted `EXACT_TARGET_SUBMISSION_BEGIN` then timed out, with no
`TARGET_CALLBACK_ENTER`, related-function, per-function `get_instrs`,
insertion, enable, launch-return, or same-process reuse marker. Thus the only
supported boundary is **after PyTorch's exact target submission marker and
before this NVBit tool's CUDA-launch callback entry**. It is not evidence that
any A--E stage caused the historical delay.

The newer pre-lookup control completed four preceding function-name lookups in
at most {second['pre_lookup_max_us']} microseconds each. The exact target emitted
neither a pre-lookup BEGIN nor a target-callback marker. Across its
{second['post_submission_samples']} post-submission samples, the process remained
CPU-active ({second['cpu_min_percent']:.0f}--{second['cpu_max_percent']:.0f}%), GPU
utilization was 0%, the CUDA-attached process used 335 MiB, and no child
`nvdisasm` process was observed. Non-destructive status/wchan/syscall snapshots
were retained; kernel-stack access was denied by node policy, so this report
does not claim a symbolized native stack.

The prior C4 GEMM result (89 related functions, 88 enumerated, 66,032 static
instructions, 19.969523 s cumulative `nvbit_get_instrs`) remains a useful
general mechanism reference, but it cannot be mapped to this exact target:
the exact target callback never arrived. Therefore no related-function count,
unique count, static-instruction count, per-function timing distribution,
pathology, duplicate-discovery result, or first-vs-second reuse result exists
for the historical target.

The next smallest informative experiment is **not authorized by this
publication**: one bounded exact-input, no-op NVBit CUDA-launch-callback arrival
probe with no name lookup, `get_related_functions`, `get_instrs`, insertion,
enable, trace, model, or C target. Until explicitly authorized and successful,
the Lane-G Llama state remains
`NVBIT_RETRY570_LLAMA_MODEL_CANARY_INCONCLUSIVE_FILTERING_NOT_DISAMBIGUATED`.
"""


def manifest(directory: Path) -> dict[str, Any]:
    return {"schema_version": "C16_G_RETRY570_EXACT_DISCOVERY_PUBLISH_V1", "status": STATUS,
            "scientific_eligible": False, "producer_implementation_commits": [item["runtime_commit"] for item in ATTEMPTS],
            "raw_profiler_payloads_committed": False, "remote_only_required_artifact_count": 0,
            "files": [{"path": name, "size_bytes": (directory / name).stat().st_size, "sha256": sha256_file(directory / name)} for name in PAYLOADS]}


def validate(directory: Path) -> dict[str, Any]:
    publication = _load(directory / MANIFEST)
    rows, seen = publication.get("files"), set()
    if publication.get("status") != STATUS or publication.get("scientific_eligible") is not False or not isinstance(rows, list):
        raise ContractError("publication manifest status is malformed")
    for row in rows:
        name, size, digest = row.get("path"), row.get("size_bytes"), row.get("sha256") if isinstance(row, dict) else (None, None, None)
        if not isinstance(name, str) or name not in PAYLOADS or name in seen or not isinstance(size, int) or not valid_sha256(digest):
            raise ContractError("publication manifest has invalid/duplicate payload metadata")
        item = directory / name
        if not item.is_file() or item.stat().st_size != size or sha256_file(item) != digest:
            raise ContractError(f"publication payload lacks existence/size/SHA closure: {name}")
        seen.add(name)
    if seen != set(PAYLOADS) or _load(directory / RECEIPT).get("status") != STATUS:
        raise ContractError("publication payload set is incomplete")
    return {"schema_version": "C16_G_RETRY570_EXACT_DISCOVERY_PUBLISH_VALIDATION_V1", "status": "PASS",
            "publish_manifest": {"path": MANIFEST, "sha256": sha256_file(directory / MANIFEST)},
            "checks": {"payload_count": len(rows), "duplicate_path_count": 0, "missing_path_count": 0,
                       "size_or_sha256_failure_count": 0, "manifest_references_only_materialized_payloads": True,
                       "remote_only_required_artifact_count": 0, "scientific_eligible": False}}


def write(directory: Path, raw_base: Path) -> None:
    attempts = observe(raw_base)
    directory.mkdir(parents=True, exist_ok=True)
    index = raw_index(attempts, raw_base)
    atomic_json(directory / RAW_INDEX, index)
    atomic_json(directory / RECEIPT, closeout_receipt(attempts, directory / RAW_INDEX))
    atomic_json(directory / TRANSFER, {"schema_version": "C16_G_RETRY570_EXACT_DISCOVERY_TRANSFER_V1", "status": "PASS_REMOTE_TO_LOCAL_CHECKSUM_CLOSURE", "scientific_eligible": False,
                                       "attempts": [{"attempt": item["spec"]["key"], "remote_manifest_sha256": item["manifest_sha256"], "remote_tree_sha256": item["manifest"]["payload_tree_sha256"], "local_tree_sha256": item["manifest"]["payload_tree_sha256"], "file_count": len(item["rows"]), "total_bytes": sum(int(row["bytes"]) for row in item["rows"])} for item in attempts],
                                       "rsync_checksum_dry_run": "NO_DIFFERENCES", "remote_only_required_artifact_count": 0, "active_gpu_process_count_at_closeout": 0, "raw_payloads_committed": False})
    (directory / MATRIX).write_text(matrix(attempts), encoding="utf-8")
    (directory / REPORT).write_text(report(attempts), encoding="utf-8")
    atomic_json(directory / MANIFEST, manifest(directory))
    atomic_json(directory / VALIDATION, validate(directory))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--raw-base", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if args.write:
        write(args.directory, args.raw_base)
        print(f"PASS Retry570 exact-discovery closeout write: {args.directory}")
    else:
        print("PASS Retry570 exact-discovery closeout validation: " + canonical_json(validate(args.directory)["checks"]))


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Retry570 exact-discovery closeout: {exc}")
