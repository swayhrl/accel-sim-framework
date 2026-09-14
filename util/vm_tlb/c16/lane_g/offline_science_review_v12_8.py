#!/usr/bin/env python3
"""Build the C16 V12.8 offline science-review pack from immutable local data.

This is deliberately a read-only consumer of recovered raw artifacts.  It never
opens a CUDA context and does not mutate a historical receipt or raw payload.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path("/root/share/c16_recovery_v3")
PACK = Path("docs/vm_tlb/review_packs/C16_H_MEMORY_FINGERPRINT/ROUTE_B_CAPTURE_CONTRACT_V1")
MANIFEST_NAME = "OFFLINE_SCIENCE_REVIEW_V12_8_PUBLISH_MANIFEST.json"
DELIVERABLE_NAMES = ("C16_ROUTE_A_BRIDGE_REFERENCE_V1.json", "ROUTE_B_Q2_BRIDGE_CLOSEOUT_V1.json",
                     "CUTLASS_IDENTITY_AND_COVERAGE_AUDIT_V1.md", "ROUTE_B_SELECTION_SENSITIVITY_V1.json",
                     "Q2_ANCHOR_MEMORY_CHARACTERIZATION_V1.md", "GPU_RESUME_DECISION_PACKAGE_V1.md")
RECOVERY_PACK = Path("/workspace/worktrees/accel-sim-vm-c16-g-post-restart-recovery-v12-6") / \
    "docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_nvbit175_recovery_v2/llama_3p2_1b"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dump(path: Path, data: object) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return sha256(path)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def bit(mask: int, lane: int) -> bool:
    return bool(mask & (1 << lane))


def mask_value(value: object) -> int:
    return int(value, 0) if isinstance(value, str) else int(value)


def percentile(values: list[int], p: float) -> int | None:
    if not values:
        return None
    values.sort()
    return values[min(len(values) - 1, round((len(values) - 1) * p))]


def parse_q2(path: Path) -> dict:
    """Stream a Q2 JSONL; event order is explicitly callback observation order."""
    events, widths = Counter(), Counter()
    tuple_counts = Counter()
    vas, lines, pages4k, pages2m = set(), set(), set(), set()
    per_launch = defaultdict(lambda: {"events": 0, "vas": set(), "lines": set(), "pages4k": set(), "pages2m": set()})
    masks = Counter()
    last_seen, distances = {}, []
    terminal = None
    functions, phases = set(), set()
    sequence_last = -1
    sequence_monotonic = True
    for text in path.open(encoding="utf-8"):
        row = json.loads(text)
        if row.get("record_kind") == "TERMINAL":
            terminal = row
            continue
        if row.get("record_kind") != "LANE_EVENT":
            continue
        functions.add(row.get("function_mangled_name")); phases.add(row.get("phase"))
        sequence = int(row["observed_event_sequence"])
        sequence_monotonic &= sequence > sequence_last
        sequence_last = sequence
        lane = int(row["lane_id"])
        active = mask_value(row.get("active_mask", 0))
        pred = mask_value(row.get("predicate_mask", 0))
        executing = mask_value(row.get("executing_mask", 0))
        masks["active_lane_events"] += bit(active, lane)
        masks["predicate_true_lane_events"] += bit(pred, lane)
        masks["predicate_false_lane_events"] += not bit(pred, lane)
        masks["executing_lane_events"] += bit(executing, lane)
        events[row.get("access_kind", "UNKNOWN")] += 1
        widths[str(row.get("width_bytes", "UNKNOWN"))] += 1
        key = (int(row["static_index"]), int(row["mref_ordinal"]))
        tuple_counts[key] += 1
        va = int(row["gpu_va"], 0) if isinstance(row["gpu_va"], str) else int(row["gpu_va"])
        vas.add(va); lines.add(va >> 7); pages4k.add(va >> 12); pages2m.add(va >> 21)
        launch = str(row["kernel_launch_id"])
        summary = per_launch[launch]
        summary["events"] += 1
        summary["vas"].add(va); summary["lines"].add(va >> 7); summary["pages4k"].add(va >> 12); summary["pages2m"].add(va >> 21)
        if va in last_seen:
            distances.append(sequence - last_seen[va])
        last_seen[va] = sequence
    launches = []
    for launch, item in sorted(per_launch.items(), key=lambda pair: int(pair[0])):
        launches.append({"kernel_launch_id": launch, "lane_event_count": item["events"], "unique_gpu_va": len(item["vas"]),
                         "unique_128b_lines": len(item["lines"]), "unique_4k_pages": len(item["pages4k"]),
                         "unique_2m_pages": len(item["pages2m"])})
    return {
        "raw_path": str(path), "raw_bytes": path.stat().st_size, "raw_sha256": sha256(path),
        "lane_event_count": sum(events.values()), "access_kind_counts": dict(sorted(events.items())),
        "width_bytes_counts": dict(sorted(widths.items(), key=lambda item: int(item[0]) if item[0].isdigit() else -1)),
        "events_by_static_index_mref_ordinal": [{"static_index": index, "mref_ordinal": mref, "lane_event_count": count}
                                                  for (index, mref), count in sorted(tuple_counts.items())],
        "unique_gpu_va": len(vas), "unique_128b_lines": len(lines), "unique_4k_pages": len(pages4k), "unique_2m_pages": len(pages2m),
        "per_launch_footprint": launches, "aggregate_footprint": {"bytes_at_128b_granularity": len(lines) * 128,
                                                                        "bytes_at_4k_granularity": len(pages4k) * 4096,
                                                                        "bytes_at_2m_granularity": len(pages2m) * 2097152},
        "lane_and_predicate_statistics": dict(masks),
        "observed_callback_order_reuse": {"definition": "same GPU VA recurrence distance in OBSERVED_CALLBACK_ORDER; not hardware global order",
                                             "reused_lane_events": len(distances), "reuse_fraction": len(distances) / max(1, sum(events.values())),
                                             "distance_min": min(distances) if distances else None, "distance_median": percentile(distances, .5),
                                             "distance_p95": percentile(distances, .95), "distance_max": max(distances) if distances else None},
        "observed_event_sequence_strictly_monotonic": sequence_monotonic, "terminal": terminal,
        "observed_function_mangled_names": sorted(functions), "observed_phases": sorted(phases),
    }


def parse_legacy_trace(path: Path) -> dict:
    """Legacy NVBit trace has one instruction row containing up to 32 lane VAs."""
    vas, lines, pages4k, pages2m = set(), set(), set(), set()
    instruction_rows = address_lanes = 0
    for text in path.open(errors="replace"):
        if text.startswith("#") or text.startswith("-") or not text.strip():
            continue
        words = text.split()
        # Address columns are fixed-width lowercase/uppercase hex words; keep only 64-bit-like values.
        addresses = [word for word in words if word.startswith("0x") and len(word) >= 10 and
                     all(ch in "0123456789abcdefABCDEF" for ch in word[2:])]
        if not addresses:
            continue
        instruction_rows += 1
        for raw in addresses:
            va = int(raw, 16)
            vas.add(va); lines.add(va >> 7); pages4k.add(va >> 12); pages2m.add(va >> 21)
            address_lanes += 1
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path), "instruction_rows": instruction_rows,
            "address_lane_fields": address_lanes, "unique_gpu_va": len(vas), "unique_128b_lines": len(lines),
            "unique_4k_pages": len(pages4k), "unique_2m_pages": len(pages2m)}


def route_a_reference() -> dict:
    prefill_target = load(RECOVERY_PACK / "LARGE_INDEX_PREFILL_TARGET.json")
    decode_target = load(RECOVERY_PACK / "DECODE_INDEX_TARGET.json")
    prefill = [parse_legacy_trace(path) for path in sorted((ROOT / "raw/llama_3p2_1b/S0/recovery_v2/formal").glob("s*_prefill/*.trace"))]
    decode = [parse_legacy_trace(path) for path in sorted((ROOT / "raw/llama_3p2_1b/S0/recovery_v2/formal").glob("s5_decode*/*.trace"))]
    raw_index = RECOVERY_PACK / "RAW_ARTIFACT_INDEX.json"
    def anchor(phase: str, target: dict, traces: list[dict]) -> dict:
        target_instruction = target["target_instruction"]
        return {"phase": phase, "exact_function": target["function"]["mangled_name"], "function_full_name": target["function"]["full_name"],
                "selected_static_instruction": {"static_index": target_instruction["nvbit_static_index"], "opcode": target_instruction["opcode"],
                    "offset": target_instruction.get("instruction_offset"), "mref": target_instruction["has_mref"]},
                "route_a_target_source": {"path": str(RECOVERY_PACK / ("LARGE_INDEX_PREFILL_TARGET.json" if phase == "PREFILL" else "DECODE_INDEX_TARGET.json")),
                                          "sha256": sha256(RECOVERY_PACK / ("LARGE_INDEX_PREFILL_TARGET.json" if phase == "PREFILL" else "DECODE_INDEX_TARGET.json"))},
                "route_a_source_receipt": {"path": str(raw_index), "sha256": sha256(raw_index),
                                           "role": "Git-published Route-A raw artifact index with endpoint/hash closure"},
                "historical_trace_artifacts": traces,
                "aggregate_historical_footprint": {key: sum(x[key] for x in traces) for key in ("instruction_rows", "address_lane_fields")},
                "footprint_scope": "Per-trace bucket cardinalities are retained; cross-process absolute GPU VA equality is not required."}
    return {"schema_version": "C16_ROUTE_A_BRIDGE_REFERENCE_V1", "scientific_authority": "ef0d89b1ce297518f86c51cddce190abd47e7364",
            "recovery_authority": "62428f2cea9ed4cd2def11339311d4347282d9c7", "anchors": {
                "PREFILL": anchor("PREFILL", prefill_target, prefill), "DECODE": anchor("DECODE", decode_target, decode)}}


def phase_duration_catalog(path: Path) -> dict[str, int]:
    result = Counter()
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            phase = row.get("phase") or row.get("phase_id")
            duration = row.get("duration_ns") or row.get("kernel_duration_ns")
            if phase and duration:
                result[phase.upper()] += int(float(duration))
    return dict(result)


def selection_sensitivity(map_results: dict, catalog: Path) -> dict:
    denominator = phase_duration_catalog(catalog)
    rows = map_results["results"]
    output = {"schema_version": "ROUTE_B_SELECTION_SENSITIVITY_V1", "frozen_catalog": {"path": str(catalog), "sha256": sha256(catalog)}, "phases": {}}
    for phase in ("PREFILL", "DECODE"):
        phase_rows = [(row, row.get("phase_observations", {}).get(phase)) for row in rows if phase in row.get("phase_observations", {})]
        mapped = sum(observation["phase_duration_ns"] for row, observation in phase_rows if row["status"] == "MAPPED_EXACT")
        failed = [dict(request_id=row["request_id"], exact_full_function=row["exact_full_function"], duration_ns=observation["phase_duration_ns"],
                       failure_reason=row.get("failure_reason")) for row, observation in phase_rows if row["status"] == "FAILED_CLOSED"]
        failed_duration = sum(item["duration_ns"] for item in failed)
        total = denominator.get(phase, 0)
        output["phases"][phase] = {"full_frozen_duration_denominator_ns": total, "failed_cutlass_rows": failed,
              "failed_cutlass_duration_share": failed_duration / total if total else None,
              "mapped_exact_request_duration_ns": mapped, "mapped_exact_lower_bound_duration_coverage": mapped / total if total else None,
              "mapped_only_mathematical_upper_bound_duration_coverage": (total - failed_duration) / total if total else None,
              "current_duration_prefix_ge_70_percent": "BLOCKED: required CUTLASS row is FAILED_CLOSED; frozen denominator retained",
              "memory_opportunity_proxy_ge_80_percent": "UNRESOLVED: failed CUTLASS rows have no admissible static MREF map; no MREF count is invented",
              "unknown_due_to_failed_rows": ["GLOBAL+MREF instruction counts", "memory-opportunity proxy contribution", "admissible dynamic target eligibility"]}
    return output


def bridge_closeout(reference: dict, q2: dict[str, dict]) -> dict:
    findings = {}
    result = "PASS"
    for phase, anchor in reference["anchors"].items():
        selected = anchor["selected_static_instruction"]["static_index"]
        q = q2[phase]
        selected_events = next((x["lane_event_count"] for x in q["events_by_static_index_mref_ordinal"] if x["static_index"] == selected), 0)
        legacy_lanes = sum(trace["address_lane_fields"] for trace in anchor["historical_trace_artifacts"])
        legacy_per_trace = [trace["address_lane_fields"] for trace in anchor["historical_trace_artifacts"]]
        bucket_relation = {key: {"route_a_per_trace": [trace[key] for trace in anchor["historical_trace_artifacts"]], "route_b_q2_aggregate": q[key],
                                 "relation": "cardinality-only; absolute GPU VAs are intentionally not compared across processes"}
                           for key in ("unique_128b_lines", "unique_4k_pages", "unique_2m_pages")}
        function_ok = q["observed_function_mangled_names"] == [anchor["exact_function"]]
        cardinality = "EQUAL_TO_ROUTE_A_AGGREGATE" if selected_events == legacy_lanes else (
            "EQUAL_TO_EACH_ROUTE_A_INDEPENDENT_REPLICATE" if selected_events in legacy_per_trace else "NOT_EQUAL_OR_NOT_PROVEN")
        status = "PASS" if function_ok and selected_events and cardinality != "NOT_EQUAL_OR_NOT_PROVEN" else "PARTIAL"
        if status != "PASS": result = "PARTIAL"
        findings[phase] = {"status": status, "exact_function": anchor["exact_function"], "selected_static_index": selected,
                           "selected_static_presence_in_q2": selected_events > 0, "q2_selected_static_lane_events": selected_events,
                           "route_a_address_lane_fields": legacy_lanes,
                           "exact_function_identity_match": function_ok,
                           "executing_lane_event_cardinality_relation": cardinality,
                           "bucket_cardinality_relation": bucket_relation,
                           "limitations": "Comparison is structural. Q2 captures all GLOBAL+MREF instructions; Route-A is a selected-static-instruction trace. No cross-process absolute VA equality or timing claim is made."}
    return {"schema_version": "ROUTE_B_Q2_BRIDGE_CLOSEOUT_V1", "status": result, "basis": "Recovered Route-A raw plus hash-closed Q2 dynamic raw; structural comparison only.", "phases": findings}


def markdown_characterization(q2: dict[str, dict]) -> str:
    lines = ["# Q2 anchor memory characterization V1", "", "These are dynamic address anchors, not phase-wide population claims. Reuse metrics use **OBSERVED_CALLBACK_ORDER**, never hardware global order.", ""]
    for phase, item in q2.items():
        lines += [f"## {phase}", "", f"- LANE_EVENT: {item['lane_event_count']}", f"- Access split: `{item['access_kind_counts']}`", f"- Access-width bytes: `{item['width_bytes_counts']}`", f"- Unique VA / 128B lines / 4KiB pages / 2MiB pages: {item['unique_gpu_va']} / {item['unique_128b_lines']} / {item['unique_4k_pages']} / {item['unique_2m_pages']}",
                  f"- Predicate true / false, executing: {item['lane_and_predicate_statistics']['predicate_true_lane_events']} / {item['lane_and_predicate_statistics']['predicate_false_lane_events']} / {item['lane_and_predicate_statistics']['executing_lane_events']}",
                  f"- Callback-order reuse fraction: {item['observed_callback_order_reuse']['reuse_fraction']:.6f}; median distance: {item['observed_callback_order_reuse']['distance_median']}", "", "Static/MREF event counts:", "", "| static index | MREF ordinal | lane events |", "|---:|---:|---:|"]
        lines += [f"| {x['static_index']} | {x['mref_ordinal']} | {x['lane_event_count']} |" for x in item["events_by_static_index_mref_ordinal"]]
        lines += ["", "Per-launch footprint:", "", "| launch | lane events | unique VA | 128B lines | 4KiB pages | 2MiB pages |", "|---:|---:|---:|---:|---:|---:|"]
        lines += [f"| {x['kernel_launch_id']} | {x['lane_event_count']} | {x['unique_gpu_va']} | {x['unique_128b_lines']} | {x['unique_4k_pages']} | {x['unique_2m_pages']} |" for x in item["per_launch_footprint"]]
        lines += [""]
    prefill, decode = q2["PREFILL"], q2["DECODE"]
    lines += ["## Conservative interpretation", "", f"For these anchors, Prefill spans {prefill['unique_128b_lines']:,} 128B lines and {prefill['unique_4k_pages']} 4KiB buckets, while Decode spans {decode['unique_128b_lines']:,} and {decode['unique_4k_pages']}. The observed callback-order reuse fractions differ ({prefill['observed_callback_order_reuse']['reuse_fraction']:.6f} Prefill vs {decode['observed_callback_order_reuse']['reuse_fraction']:.6f} Decode), and their access-width mixes are reported above. These are anchor-local cache/TLB/footprint observations only: they do not establish whole-phase cache, TLB, or reuse behavior before representative coverage closes.", ""]
    return "\n".join(lines)


def audit_markdown(closure: dict, sensitivity: dict, registry_paths: list[Path]) -> str:
    cutlass_rows = closure["bounded_rechecks"]
    registry = [{"path": str(path), "sha256": sha256(path), "bytes": path.stat().st_size,
                 "exact_function_string_present": any(row["function_mangled_name"] in text for text in path.read_text(errors="replace").splitlines() for row in cutlass_rows)} for path in registry_paths]
    lines = ["# CUTLASS identity and coverage audit V1", "", "## Result", "", "No recovered artifact establishes a reproducible actual code-object identity for either required CUTLASS function. The existing failed-closed result remains intact. The fatbin registries were recovered and hash-closed, but neither is an admissible function-to-image binding. No default DSO, spelling, geometry, or kernel-name inference is used.", "", "## Recovered observer evidence", "", "| phase | exact function | status | terminal reason | CULibrary chain |", "|---|---|---|---|---|"]
    for row in cutlass_rows:
        lines.append(f"| {row['phase_observation']} | `{row['function_mangled_name']}` | {row['status']} | {row['terminal_reason']} | {row['culibrary_owner_registry']} |")
    lines += ["", "## Registry audit", ""]
    for item in registry:
        lines.append(f"- `{item['path']}` — {item['bytes']} bytes, SHA256 `{item['sha256']}`, exact unresolved-function text present: `{item['exact_function_string_present']}`.")
    lines += ["", "The registry cannot by itself prove an observed `CUmodule -> immutable image bytes/hash -> target CUfunction` relation. Therefore it is not a new identity path.", "", "## Frozen coverage sensitivity", ""]
    for phase, item in sensitivity["phases"].items():
        lines += [f"### {phase}", "", f"- Full frozen denominator: {item['full_frozen_duration_denominator_ns']:,} ns", f"- Failed CUTLASS duration: {sum(x['duration_ns'] for x in item['failed_cutlass_rows']):,} ns ({item['failed_cutlass_duration_share']:.4%})", f"- MAPPED_EXACT lower-bound coverage from current request set: {item['mapped_exact_lower_bound_duration_coverage']:.4%}", f"- Mathematical upper bound if every nonfailed duration later mapped: {item['mapped_only_mathematical_upper_bound_duration_coverage']:.4%}", f"- >=70% prefix: {item['current_duration_prefix_ge_70_percent']}", f"- >=80% proxy: {item['memory_opportunity_proxy_ge_80_percent']}", ""]
    lines += ["## Candidate paths", "", "1. **Identity-path repair (recommended):** add a bounded loader observer that records an actual immutable loaded image/fatbin/cubin hash and binds the observed target `CUfunction` through its `CUmodule` before selection. Run one prefill and one decode exact-function map-only window after a one-run tiny observer validation. Acceptance: exact module/image relation, immutable SHA, successful exact static map, and no DSO/name fallback. This preserves the frozen denominator and needs at most three diagnostic GPU windows; it produces no scientific memory capture.", "2. **Coverage-contract revision:** requires independent pre-outcome scientific rationale, application to every row, and explicit user approval. It cannot be activated by this review.", "3. **Partial mapped subset:** can report only mapped-anchor evidence, but cannot claim whole-phase representative selection under the current contract.", "", "## Bias controls", "", "Failed CUTLASS rows remain in both frozen duration denominators. No MREF proxy contribution, owner, or mapping is fabricated.", ""]
    return "\n".join(lines)


def decision_markdown() -> str:
    return """# GPU resume decision package V1

## Recommendation

`RESUME_GPU_FOR_BOUNDED_IDENTITY_REPAIR`

The recovered Q2 traces are locally hash-closed and remain valid anchor evidence. The only blocker to the frozen representative-selection contract is two CUTLASS rows with no admissible actual runtime code-object identity. A narrow identity repair preserves the contract; neither a denominator reduction nor a kernel-name/DSO inference is permitted.

## Minimum bounded GPU work

1. One tiny loader-observer validation (no model trace): prove the observer emits `CUmodule -> actual loaded image/fatbin/cubin bytes -> SHA256` before map selection.
2. One Llama S0 Prefill map-only window for the frozen unresolved CUTLASS function.
3. One Llama S0 Decode map-only window for the frozen unresolved CUTLASS function.

Each is a diagnostic-only, single-process window. It must use the frozen runtime profile and exact function identity, write only compact owner/map receipts, and make no target, coverage, timing, or memory-capture outcome claim.

## Acceptance criteria

- The target `CUfunction` is bound through the observed `CUmodule` to immutable image bytes or a cubin/fatbin payload SHA256.
- The binding is collected before selection and is reproducible on a second identical observer use if a retry is necessary.
- Exact static map validation succeeds with that actual owner token; no default `libtorch_cuda.so`, name-only, or geometry-only fallback occurs.
- If either exact row remains unresolved, retain its failed-closed state, keep it in the denominator, stop the repair path, and return a partial-mapped-subset report rather than broadening GPU exploration.

No formal capture is authorized by this recommendation.

RESUME_GPU_FOR_BOUNDED_IDENTITY_REPAIR
"""


def validate(output: Path) -> None:
    manifest = load(output / MANIFEST_NAME)
    payloads = manifest["payloads"]
    paths = [item["path"] for item in payloads]
    assert len(paths) == len(set(paths)), "duplicate publication payload"
    for item in payloads:
        path = Path.cwd() / item["path"]
        assert path.is_file(), f"missing payload: {path}"
        assert path.stat().st_size == item["bytes"], f"size mismatch: {path}"
        assert sha256(path) == item["sha256"], f"sha mismatch: {path}"
    required = set(DELIVERABLE_NAMES)
    assert required <= {Path(path).name for path in paths}, "missing required deliverable"
    decision = (output / "GPU_RESUME_DECISION_PACKAGE_V1.md").read_text(encoding="utf-8").strip().splitlines()[-1]
    assert decision in {"RESUME_GPU_FOR_BOUNDED_IDENTITY_REPAIR", "REQUEST_USER_APPROVAL_FOR_REVISED_COVERAGE_CONTRACT",
                        "KEEP_GPU_OFF_AND_REPORT_PARTIAL_MAPPED_SUBSET"}, "invalid terminal recommendation"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=PACK)
    parser.add_argument("--validate", action="store_true", help="validate an existing review pack without writing")
    parser.add_argument("--write-bridge", action="store_true", help="write the basic bridge artifacts (normally use the stricter bridge producer)")
    args = parser.parse_args()
    output = args.output_dir
    if args.validate:
        validate(output)
        print(json.dumps({"validation": "PASS", "output_dir": str(output)}, sort_keys=True))
        return
    q2_paths = {"PREFILL": ROOT / "raw/llama32_1b/S0/ROUTE_B_Q2_PREFILL_DYNAMIC/91e27027-eb2d-4572-a4b0-b9baf4fd34fb/raw.jsonl",
                "DECODE": ROOT / "raw/llama32_1b/S0/ROUTE_B_Q2_DECODE_DYNAMIC/391deb99-0430-4a19-8a2d-b2bf62243266/raw.jsonl"}
    q2 = {phase: parse_q2(path) for phase, path in q2_paths.items()}
    reference = route_a_reference()
    bridge = bridge_closeout(reference, q2)
    maps = load(PACK / "llama_s0_g1_campaign/ROUTE_B_MAP_RESULTS_V2.json")
    catalog = ROOT / "raw/llama32_1b/S0/G1_CAMPAIGN/a843ad4a-eba5-472a-ad75-a75f18f050ca/catalog/KERNEL_CATALOG.tsv"
    sensitivity = selection_sensitivity(maps, catalog)
    closure = load(PACK / "ROUTE_B_CUTLASS_OWNER_CLOSURE_V122.json")
    registry_paths = [ROOT / "raw/llama32_1b/S0/ROUTE_B_V122_CUTLASS_OWNER_PREFILL/89d3eb7c-3b5f-44f0-bf2e-9df8cd969b87/raw/FATBIN_OWNER_REGISTRY.tsv",
                      ROOT / "raw/llama32_1b/S0/ROUTE_B_V122_CUTLASS_OWNER_DECODE/f69bc1a7-55df-47fb-ad46-e0f79b7bb944/raw/FATBIN_OWNER_REGISTRY.tsv"]
    if args.write_bridge:
        dump(output / "C16_ROUTE_A_BRIDGE_REFERENCE_V1.json", reference)
        dump(output / "ROUTE_B_Q2_BRIDGE_CLOSEOUT_V1.json", bridge)
    dump(output / "ROUTE_B_SELECTION_SENSITIVITY_V1.json", sensitivity)
    (output / "Q2_ANCHOR_MEMORY_CHARACTERIZATION_V1.md").write_text(markdown_characterization(q2), encoding="utf-8")
    (output / "CUTLASS_IDENTITY_AND_COVERAGE_AUDIT_V1.md").write_text(audit_markdown(closure, sensitivity, registry_paths), encoding="utf-8")
    (output / "GPU_RESUME_DECISION_PACKAGE_V1.md").write_text(decision_markdown(), encoding="utf-8")
    cwd = Path.cwd().resolve()
    publication = {"schema_version": "C16_OFFLINE_SCIENCE_REVIEW_V12_8", "scientific_authority": "ef0d89b1ce297518f86c51cddce190abd47e7364",
                   "recovery_authority": "62428f2cea9ed4cd2def11339311d4347282d9c7", "raw_mutated": False,
                   "payloads": [{"path": str((output / name).resolve().relative_to(cwd)), "bytes": (output / name).stat().st_size,
                                 "sha256": sha256(output / name)} for name in DELIVERABLE_NAMES]}
    dump(output / MANIFEST_NAME, publication)
    print(json.dumps({"output_dir": str(output), "bridge_status": bridge["status"], "q2_events": {key: value["lane_event_count"] for key, value in q2.items()}}, sort_keys=True))


if __name__ == "__main__":
    main()
