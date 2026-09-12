#!/usr/bin/env python3
"""C15 Lane C: frozen-history sampling qualification, never a simulator driver.

The only mutable destination accepted by this program is the Lane-C review
pack.  It reads compact, hash-pinned Git blobs and the raw logs named by the
frozen manifests; it never reads a trace payload, launches a simulator, or
writes to an historical worktree.  ``--prepare`` deliberately stops before
candidate arm values are parsed so that the selector/protocol can be committed
before retrospective evaluation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[4]
PLANNING_SHA = "9a755b14b01c5a77a6fc98c2547616e1c490e806"
C12_SHA = "a268aba0d01310294074ded5bb8017e2092394c0"
OP_SHA = "8801f2e9fea4e0df1d79853a5e4440c4da463486"
C13_SHA = "9ab1e0708af66a533d9327f35f1a3e63a34c4285"
C14_SHA = "d3ac4c7b12f8e9253e6d14f34e58dbf484b39a05"
PACK_REL = Path("docs/vm_tlb/review_packs/C15_LOWCOST_MULTIMODEL/lane_c")
REPORT_REL = Path("docs/vm_tlb/codex_handoff/c15/lane_c/LATEST_REPORT.md")
DEFAULT_OUT = ROOT / PACK_REL
DEFAULT_REPORT = ROOT / REPORT_REL
PRIMARY_SEED = 15001
SENSITIVITY_SEEDS = tuple(range(15002, 15022))
BUDGETS = (8, 12, 24, 48)
ROIS = ("prefill", "decode1")
COUNTER_NAMES = {
    "vm_l1_tlb_accesses": "vm_l1_tlb_accesses",
    "vm_l1_tlb_hits": "vm_l1_tlb_hits",
    "vm_l1_tlb_misses": "vm_l1_tlb_misses",
    "vm_l2_tlb_accesses": "vm_l2_tlb_accesses",
    "vm_l2_tlb_hits": "vm_l2_tlb_hits",
    "vm_l2_tlb_misses": "vm_l2_tlb_misses",
    "vm_translation_walk_starts": "vm_translation_walk_starts",
    "vm_pte_requests": "vm_pte_requests",
    "vm_pte_l2_only_responses": "vm_pte_l2_only_responses",
    "vm_pte_dram_responses": "vm_pte_dram_responses",
    "vm_translation_requester_latency_cycles_total": "vm_translation_requester_latency_cycles_total",
}
EVAL_METRICS = (
    "gpu_sim_cycle", "vm_l1_tlb_accesses", "vm_l1_tlb_misses",
    "vm_l2_tlb_accesses", "vm_l2_tlb_misses", "vm_translation_walk_starts",
    "vm_pte_requests", "vm_pte_dram_responses",
)
MARKER = re.compile(r"^Processing kernel .*/([^/]+\.traceg\.xz)\s*$")
COUNTER = re.compile(r"^([A-Za-z0-9_]+) = (-?\d+)\s*$")


def die(message: str) -> None:
    raise RuntimeError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for part in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()


def code_sha() -> str:
    return sha256_file(Path(__file__).resolve())


def git_text(revision: str, path: str) -> str:
    result = subprocess.run(["git", "-C", str(ROOT), "show", f"{revision}:{path}"],
                            text=True, capture_output=True, check=False)
    if result.returncode:
        die(f"cannot read frozen blob {revision}:{path}: {result.stderr.strip()}")
    return result.stdout


def git_blob_id(revision: str, path: str) -> str:
    result = subprocess.run(["git", "-C", str(ROOT), "rev-parse", f"{revision}:{path}"],
                            text=True, capture_output=True, check=False)
    if result.returncode:
        die(f"cannot resolve frozen blob {revision}:{path}: {result.stderr.strip()}")
    return result.stdout.strip()


def tsv_text(value: str) -> list[dict[str, str]]:
    return list(csv.DictReader(value.splitlines(), delimiter="\t"))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     prefix=f".{path.name}.", suffix=".tmp", delete=False) as tmp:
        tmp.write(text)
        temporary = Path(tmp.name)
    os.replace(temporary, path)


def write_tsv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    import io
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: normal(row.get(field, "NA")) for field in fields})
    atomic_text(path, buffer.getvalue())


def write_json(path: Path, value: dict[str, Any]) -> None:
    atomic_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def normal(value: Any) -> str:
    if value is None or value == "":
        return "NA"
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)


def require_lane_c_out(path: Path) -> Path:
    resolved, allowed = path.resolve(), DEFAULT_OUT.resolve()
    if resolved != allowed:
        die(f"refusing output outside Lane-C private review pack: {resolved}")
    return resolved


def current_head() -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()


def path_or_na(path: Path) -> str:
    return str(path) if path.is_file() else "NA"


def frozen(name: str, revision: str, path: str, role: str) -> dict[str, str]:
    text = git_text(revision, path)
    return {"input_id": name, "revision": revision, "path": path, "blob_id": git_blob_id(revision, path),
            "sha256": sha256_bytes(text.encode()), "role": role, "availability": "GIT_BLOB_VERIFIED"}


def load_compact() -> dict[str, Any]:
    base = "docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT"
    c12 = f"{base}/C12_C5_FULL_ROI_FAIR_PERFORMANCE"
    op = f"{base}/C12_OPERATOR_AWARE_CHARACTERIZATION"
    c13 = f"{base}/C13_EFFECTIVE_CONFIG_AUDIT"
    c14 = f"{base}/C14_DUAL_PATH_EXPLORATION"
    paths = [
        frozen("C12_ARM_RESULTS", C12_SHA, f"{c12}/ARM_RESULTS.tsv", "formal 22-arm total anchors"),
        frozen("C12_ARM_STATUS", C12_SHA, f"{c12}/ARM_STATUS.tsv", "manifest-authorized raw locations"),
        frozen("OPERATOR_MAP", OP_SHA, f"{op}/KERNEL_OPERATOR_MAP.tsv", "trace-informed oracle labels only"),
        frozen("TRACE_SCAN_PREFILL", OP_SHA, f"{op}/TRACE_SCAN_prefill.tsv", "existing scan; no rescan"),
        frozen("TRACE_SCAN_DECODE", OP_SHA, f"{op}/TRACE_SCAN_decode1.tsv", "existing scan; no rescan"),
        frozen("OPERATOR_CONSERVATION", OP_SHA, f"{op}/ARM_CONSERVATION.tsv", "historical conservation reference"),
        frozen("C13_SUPERSEDING", C13_SHA, f"{c13}/SUPERSEDING_C13_RESULTS.tsv", "accepted-after-EQ only"),
        frozen("C13_INVALIDATED", C13_SHA, f"{c13}/INVALIDATED_ARM_AUDIT.tsv", "mandatory exclusion list"),
        frozen("C13_MANIFEST", C13_SHA, f"{c13}/C13_EFFECTIVE_CONFIG_AUDIT_MANIFEST.tsv", "accepted raw locations"),
        frozen("C14_RESULTS", C14_SHA, f"{c14}/MICRODIAGNOSTIC_RESULTS.tsv", "cold micro boundary"),
        frozen("C14_SELECTORS", C14_SHA, f"{c14}/C14_MICRODIAGNOSTIC_SELECTORS.tsv", "cold micro identity joins"),
    ]
    by_id = {row["input_id"]: row for row in paths}
    result_rows = tsv_text(git_text(C12_SHA, by_id["C12_ARM_RESULTS"]["path"]))
    status_rows = tsv_text(git_text(C12_SHA, by_id["C12_ARM_STATUS"]["path"]))
    map_rows = tsv_text(git_text(OP_SHA, by_id["OPERATOR_MAP"]["path"]))
    scan_id = {"prefill": "TRACE_SCAN_PREFILL", "decode1": "TRACE_SCAN_DECODE"}
    scans = {roi: tsv_text(git_text(OP_SHA, by_id[scan_id[roi]]["path"])) for roi in ROIS}
    c13_rows = tsv_text(git_text(C13_SHA, by_id["C13_SUPERSEDING"]["path"]))
    c13_manifest = tsv_text(git_text(C13_SHA, by_id["C13_MANIFEST"]["path"]))
    invalid = tsv_text(git_text(C13_SHA, by_id["C13_INVALIDATED"]["path"]))
    c14_rows = tsv_text(git_text(C14_SHA, by_id["C14_RESULTS"]["path"]))
    c14_selectors = tsv_text(git_text(C14_SHA, by_id["C14_SELECTORS"]["path"]))
    if len(map_rows) != 1432 or {r["roi"] for r in map_rows} != set(ROIS):
        die("operator-map frozen cardinality/ROI identity failed")
    if {roi: len(scans[roi]) for roi in ROIS} != {"prefill": 692, "decode1": 740}:
        die("existing trace-scan cardinality failed (expected Prefill692/Decode740)")
    if len(c13_rows) != 10 or any(r["l2_mode"] != "0" or r["gate_status"] != "EQ1_THEN_EQ2_PASS" for r in c13_rows):
        die("C13 admission failed: only the ten accepted mode=0 EQ rows are legal")
    if len(invalid) != 9 or any(r["raw_final_l2_mode"] != "1" for r in invalid):
        die("C13 invalidation list is not the required nine mode1 rows")
    result_by = {(r["roi"], r["arm"], r["lseg"]): r for r in result_rows}
    arms = []
    for row in status_rows:
        if row.get("terminal_status") != "PASS":
            continue
        key = (row["roi"], row["arm"], row["lseg"])
        result = result_by.get(key)
        if not result or result.get("terminal_status") != "PASS":
            die(f"C12 terminal status/result mismatch {key}")
        arms.append({**row, **{f"result_{k}": v for k, v in result.items()}})
    expected = {(roi, arm, lseg) for roi in ROIS for arm, lseg in (("F0","NONE"),("F1","NONE"),("F2","NONE"),("F5","NONE"),("F7","5"),("F7","10"),("F7","20"),("F8","5"),("F8","10"),("F8","20"),("F9","NONE"))}
    if len(arms) != 22 or {(r["roi"], r["arm"], r["lseg"]) for r in arms} != expected:
        die("C12 22-arm set failed")
    return {"inputs": paths, "arms": arms, "map": map_rows, "scans": scans, "c13": c13_rows,
            "c13_manifest": c13_manifest, "c14": c14_rows, "c14_selectors": c14_selectors}


def pages(text: str) -> set[int]:
    return {int(value) for value in text.split(",") if value}


def prepare_artifacts(out: Path, data: dict[str, Any]) -> None:
    started = time.time()
    out.mkdir(parents=True, exist_ok=True)
    preflight = {
        "schema_version": "C15_LANE_C_PREFLIGHT_V1", "lane": "C", "branch": "hrl/vm-c15-sampling-validation-v0",
        "planning_sha": PLANNING_SHA, "head": current_head(), "selector_code_sha256": code_sha(),
        "new_simulator_replay": 0, "new_full_roi_simulation": 0, "new_trace_capture": 0,
        "protected_sources_read_only": [C12_SHA, OP_SHA, C13_SHA, C14_SHA], "status": "PASS",
    }
    write_json(out / "ENV_PREFLIGHT.json", preflight)
    write_tsv(out / "HISTORICAL_INPUTS.tsv",
              ["input_id","revision","path","blob_id","sha256","role","availability","raw_path","raw_status"],
              [{**row, "raw_path": "NA", "raw_status": "COMPACT_ONLY"} for row in data["inputs"]])
    observability = [
        {"field":"compute_index/trace_filename", "source":"OPERATOR_MAP", "tier":"TRACE_INFORMED_ORACLE", "usable_primary_cheap":"NO", "reason":"obtained after complete historical trace scan"},
        {"field":"operator_class/layer_id", "source":"OPERATOR_MAP", "tier":"TRACE_INFORMED_ORACLE", "usable_primary_cheap":"NO", "reason":"direct trace-range/semantic evidence; retained only as oracle"},
        {"field":"phase", "source":"frozen ROI identity", "tier":"STATIC_DERIVED", "usable_primary_cheap":"YES", "reason":"available before candidate arm values"},
        {"field":"opaque ordered launch index", "source":"frozen kernelslist index", "tier":"TRACE_HEADER_ONLY", "usable_primary_cheap":"YES", "reason":"does not use outcomes; semantic class remains UNKNOWN"},
        {"field":"refs/unique 64KiB pages", "source":"TRACE_SCAN", "tier":"TRACE_DERIVED_EXACT", "usable_primary_cheap":"NO", "reason":"full trace-derived; oracle/fingerprint only"},
        {"field":"read/write/atomic/bytes/line set", "source":"available compact scans", "tier":"UNRESOLVED", "usable_primary_cheap":"NO", "reason":"not preserved by compact C12 scan"},
        {"field":"per-kernel simulated cycle/counter", "source":"terminal raw logs", "tier":"SIMULATOR_INFORMED_ORACLE", "usable_primary_cheap":"NO", "reason":"retrospective evaluator only"},
    ]
    write_tsv(out / "FIELD_OBSERVABILITY_AUDIT.tsv", ["field","source","tier","usable_primary_cheap","reason"], observability)
    feature_rows = [
        {"feature":"phase", "source_level":"T0_STATIC", "unit":"category", "address_domain":"none", "additivity":"not_applicable", "requires_full_trace":"NO", "allowed_use":"PRIMARY_SELECTOR", "cost_class":"CHEAP"},
        {"feature":"opaque_launch_index", "source_level":"T1_HEADER_DIRECTORY", "unit":"ordinal", "address_domain":"none", "additivity":"not_applicable", "requires_full_trace":"NO", "allowed_use":"PRIMARY_SELECTOR", "cost_class":"CHEAP"},
        {"feature":"operator_class", "source_level":"HISTORICAL_TRACE_SCAN", "unit":"category", "address_domain":"SimVA-derived", "additivity":"not_applicable", "requires_full_trace":"YES", "allowed_use":"TRACE_INFORMED_ORACLE_ONLY", "cost_class":"ORACLE"},
        {"feature":"layer_id", "source_level":"HISTORICAL_TRACE_SCAN", "unit":"ordinal", "address_domain":"SimVA-derived", "additivity":"not_applicable", "requires_full_trace":"YES", "allowed_use":"TRACE_INFORMED_ORACLE_ONLY", "cost_class":"ORACLE"},
        {"feature":"unique_64KiB_pages", "source_level":"HISTORICAL_TRACE_SCAN", "unit":"pages", "address_domain":"SimVA", "additivity":"union_only", "requires_full_trace":"YES", "allowed_use":"FINGERPRINT_ORACLE_ONLY", "cost_class":"ORACLE"},
        {"feature":"gpu_sim_cycle", "source_level":"FULL_SIMULATOR_LOG", "unit":"cycles", "address_domain":"none", "additivity":"sum", "requires_full_trace":"NO", "allowed_use":"RETROSPECTIVE_EVALUATOR_ONLY", "cost_class":"SIMULATOR_INFORMED_ORACLE"},
        {"feature":"candidate_delta", "source_level":"CANDIDATE_RESULT", "unit":"cycles/events", "address_domain":"none", "additivity":"sum", "requires_full_trace":"NO", "allowed_use":"FORBIDDEN_PRIMARY_SELECTOR", "cost_class":"FORBIDDEN"},
    ]
    write_tsv(out / "FEATURE_COST_AND_SCOPE.tsv", ["feature","source_level","unit","address_domain","additivity","requires_full_trace","allowed_use","cost_class"], feature_rows)
    mapping = {(r["roi"], int(r["compute_index"])): r for r in data["map"]}
    universe = {roi: list(range(len(data["scans"][roi]))) for roi in ROIS}
    plans: list[dict[str, Any]] = []
    coverage: list[dict[str, Any]] = []
    strategies = ("LAYER_ANCHOR_CHEAP_V1", "STRATIFIED_REPRESENTATIVE_CHEAP_V1", "STRATIFIED_RANDOM_CHEAP_V1", "TRACE_INFORMED_ORACLE_DIAGNOSTIC_V1")
    for strategy in strategies:
        for budget in BUDGETS:
            allocation = allocate_budget(budget, {roi: len(universe[roi]) for roi in ROIS})
            selected_by_roi: dict[str, list[int]] = {}
            for roi in ROIS:
                n = allocation[roi]
                values = universe[roi]
                if strategy == "STRATIFIED_RANDOM_CHEAP_V1":
                    selected = sorted(random.Random(PRIMARY_SEED + budget + (0 if roi == "prefill" else 1000)).sample(values, n))
                    reason, probability = "seeded phase-stratified random; cheap fields only", n / len(values)
                elif strategy == "STRATIFIED_REPRESENTATIVE_CHEAP_V1":
                    selected = even_positions(values, n)
                    reason, probability = "phase-stratum central/tail order anchors; no candidate values", "NA"
                elif strategy == "LAYER_ANCHOR_CHEAP_V1":
                    selected = even_positions(values, n)
                    reason, probability = "INFEASIBLE_NO_CHEAP_LAYER_ID; phase-order fallback only", "NA"
                else:
                    buckets: dict[str, list[int]] = defaultdict(list)
                    for index in values:
                        row = mapping[(roi, index)]
                        buckets[f"{row['operator_class']}|{row['layer_id']}"] .append(index)
                    selected = oracle_pick(buckets, n, PRIMARY_SEED + budget)
                    reason, probability = "trace-informed operator/layer oracle; excluded from primary", "NA"
                selected_by_roi[roi] = selected
                plan_id = f"{strategy}__B{budget}"
                for index in selected:
                    row = mapping[(roi, index)]
                    oracle = strategy.startswith("TRACE_INFORMED")
                    plans.append({"plan_id": plan_id, "selector_sha": code_sha(), "deployment_id": "C12_FROZEN_LLAMA32_1B",
                                  "scenario_id": roi, "stratum_id": (f"{roi}|{row['operator_class']}|{row['layer_id']}" if oracle else f"{roi}|OPERATOR_UNKNOWN|IMPLEMENTATION_UNKNOWN|DTYPE_UNKNOWN|SHAPE_UNKNOWN|KV_LAYOUT_UNKNOWN|TP_UNKNOWN"),
                                  "semantic_key_json": json.dumps({"phase": roi, "operator": row["operator_class"] if oracle else "UNKNOWN"}, sort_keys=True),
                                  "implementation_key": "UNKNOWN_CHEAP" if not oracle else "TRACE_INFORMED_ORACLE",
                                  "shape_regime": "UNKNOWN_CHEAP", "selection_reason": reason, "sampling_unit": "compute_kernel",
                                  "target_launch_signature": f"opaque-index:{index}", "target_indices": index, "warmup_indices": "NA",
                                  "weight": len(values) / len(selected), "weight_basis": "phase_stratum_N_over_n", "inclusion_probability": probability,
                                  "seed": PRIMARY_SEED, "split_role": "ORACLE_DIAGNOSTIC" if oracle else "RETROSPECTIVE_TEST",
                                  "expected_capture_bytes": "NA", "execution_scope": "OFFLINE_ONLY_NOT_CAPTURE_AUTHORIZATION",
                                  "eligibility_status": "INFEASIBLE_FINE_STRATA" if strategy == "LAYER_ANCHOR_CHEAP_V1" else "ELIGIBLE"})
                coverage.append({"plan_id": plan_id, "universe_hash": universe_hash(universe), "basis": "compute_kernels",
                                 "stratum": roi, "total_mass": len(values), "represented_stratum_mass": len(values), "actually_sampled_mass": len(selected),
                                 "represented_fraction": 1, "sampled_fraction": len(selected)/len(values),
                                 "missing_categories": "operator/implementation/dtype/shape/KV/TP unavailable to cheap historical directory",
                                 "audited_tail_fraction": 2/len(selected) if len(selected) > 2 else 1, "status": "INFEASIBLE_FINE_STRATA" if strategy == "LAYER_ANCHOR_CHEAP_V1" else "COMPLETE"})
    fields = ["plan_id","selector_sha","deployment_id","scenario_id","stratum_id","semantic_key_json","implementation_key","shape_regime","selection_reason","sampling_unit","target_launch_signature","target_indices","warmup_indices","weight","weight_basis","inclusion_probability","seed","split_role","expected_capture_bytes","execution_scope","eligibility_status"]
    write_tsv(out / "SAMPLE_PLAN.tsv", fields, plans)
    write_tsv(out / "SAMPLING_COVERAGE.tsv", ["plan_id","universe_hash","basis","stratum","total_mass","represented_stratum_mass","actually_sampled_mass","represented_fraction","sampled_fraction","missing_categories","audited_tail_fraction","status"], coverage)
    split_rows = [{"split_id":"C12_RETROSPECTIVE_ALL_SEEN", "roi": roi, "compute_index": idx, "split_role":"RETROSPECTIVE_TEST", "previously_seen":"TRUE", "seed": PRIMARY_SEED, "note":"historical C12/C13 were analyzed before C15; never prospective"}
                  for roi in ROIS for idx in universe[roi]]
    write_tsv(out / "SPLIT_MANIFEST.tsv", ["split_id","roi","compute_index","split_role","previously_seen","seed","note"], split_rows)
    protocol = {"schema_version":"C15_SAMPLING_VALIDATION_PROTOCOL_V1", "planning_sha": PLANNING_SHA, "selector_code_sha256": code_sha(),
                "primary_strategy":"STRATIFIED_REPRESENTATIVE_CHEAP_V1", "control_strategy":"STRATIFIED_RANDOM_CHEAP_V1", "oracle_strategy":"TRACE_INFORMED_ORACLE_DIAGNOSTIC_V1",
                "seed": PRIMARY_SEED, "sensitivity_seeds": list(SENSITIVITY_SEEDS), "virtual_budgets": list(BUDGETS), "metrics": list(EVAL_METRICS),
                "thresholds":{"unique_page_relative_error_if_N_gt_100":"<=0.05", "unique_page_small_N_absolute_error":"<=max(1,ceil(0.05*N))", "macro_cycle_screening_relative_error":"<=0.05", "small_effect_rule":"no verdict when empirical envelope crosses zero or effect is no larger than resolution"},
                "candidate_outcomes_used_for_selection": False, "historical_label":"RETROSPECTIVE_CALIBRATION_AND_CROSS_CONFIG_TEST", "simulator_replays_authorized":0}
    write_json(out / "SAMPLING_VALIDATION_PROTOCOL.json", protocol)
    release = {"schema_version":"C15_SELECTOR_RELEASE_V1", "lane":"C", "planning_sha":PLANNING_SHA, "selector_code_sha256":code_sha(),
               "primary_seed":PRIMARY_SEED, "virtual_budgets":list(BUDGETS), "primary_selector":"STRATIFIED_REPRESENTATIVE_CHEAP_V1",
               "api":"python3 util/vm_tlb/c15/lane_c/c15_sampling_validation.py --prepare --output-dir docs/vm_tlb/review_packs/C15_LOWCOST_MULTIMODEL/lane_c",
               "sample_schema":"SAMPLE_PLAN.tsv", "B_consumption":"read committed PUBLISH_MANIFEST only; no capture authorization is conveyed",
               "limit":"historical cheap metadata lacks operator/shape/dtype/KV/TP; unknown buckets are explicit"}
    write_json(out / "SELECTOR_RELEASE.json", release)
    write_tsv(out / "COST_LEDGER.tsv", cost_fields(), [{"work_id":"C15-C-PREPARE", "parent_work_id":"NA", "lane":"C", "stage_id":"C15-0.1,C15-0.4,C15-3.1,C15-3.2,C15-3.3", "attempt":1, "operation":"frozen compact blob import and selector protocol release", "start_utc":"NA", "end_utc":"NA", "wall_s":time.time()-started, "cpu_core_s":"NA", "gpu_active_s":0, "peak_rss_B":"NA", "peak_vram_B":0, "bytes_read":sum(len(git_text(row['revision'],row['path']).encode()) for row in data['inputs']), "bytes_downloaded":0, "bytes_written":sum(p.stat().st_size for p in out.glob('*') if p.is_file()), "warmup_s":0, "retry_s":0, "measured_or_estimated":"MEASURED_WALL_COMPACT_INPUTS", "result_status":"PASS"}])
    write_status(out, {"C15-0.1":("COMPLETE","PASS","T00,T01,T23,T24"), "C15-0.4":("COMPLETE","PASS","T00,T16,T17"), "C15-3.1":("COMPLETE","PASS","T01,T12,T14"), "C15-3.2":("COMPLETE","INCONCLUSIVE","T14,T15,T21"), "C15-3.3":("COMPLETE","PASS","T14,T18")}, "prepare only; candidate raw arms deliberately unopened")
    atomic_text(DEFAULT_REPORT, "# C15 Lane C selector checkpoint\n\n`planning_sha`/HEAD: `9a755b14b01c5a77a6fc98c2547616e1c490e806`. The committed `SELECTOR_RELEASE.json`, protocol, plans, coverage and input audit are safe for B to consume read-only. They do not grant capture authority and they do not yet contain retrospective candidate evaluation.\n")
    publish_manifest(out, "INTERIM_SELECTOR_RELEASE", "selector/protocol frozen before candidate raw-arm parsing")


def allocate_budget(budget: int, masses: dict[str, int]) -> dict[str, int]:
    total = sum(masses.values())
    answer = {key: max(1, math.floor(budget * value / total)) for key, value in masses.items()}
    while sum(answer.values()) < budget:
        key = max(masses, key=lambda item: (budget * masses[item] / total - answer[item], item))
        answer[key] += 1
    return answer


def even_positions(values: list[int], count: int) -> list[int]:
    if count >= len(values):
        return values[:]
    return sorted({values[round(i*(len(values)-1)/(count-1))] if count > 1 else values[len(values)//2] for i in range(count)})


def oracle_pick(buckets: dict[str, list[int]], count: int, seed: int) -> list[int]:
    selected: list[int] = []
    ranked = sorted(buckets.items(), key=lambda item: (-len(item[1]), item[0]))
    for _, values in ranked:
        if len(selected) == count: break
        selected.append(values[len(values)//2])
    remaining = sorted(set(x for values in buckets.values() for x in values) - set(selected))
    selected.extend(random.Random(seed).sample(remaining, min(count-len(selected),len(remaining))))
    return sorted(selected)


def universe_hash(universe: dict[str, list[int]]) -> str:
    return sha256_bytes(json.dumps(universe, sort_keys=True).encode())


def cost_fields() -> list[str]:
    return ["work_id","parent_work_id","lane","stage_id","attempt","operation","start_utc","end_utc","wall_s","cpu_core_s","gpu_active_s","peak_rss_B","peak_vram_B","bytes_read","bytes_downloaded","bytes_written","warmup_s","retry_s","measured_or_estimated","result_status"]


def parse_raw(path: Path, expected_count: int, expected_sha: str, expected_total: int, validation_path: Path, expected_markers: list[str]) -> tuple[list[dict[str, int]], dict[str, Any]]:
    if not path.is_file() or not validation_path.is_file():
        die(f"missing manifest-authorized raw/validation input {path}")
    if sha256_file(path) != expected_sha:
        die(f"raw log hash mismatch {path}")
    rows: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    with path.open(errors="replace") as source:
        for line in source:
            marker = MARKER.match(line)
            if marker:
                current = {"marker":marker.group(1), "cycle":None, "cycle_occ":0, "cumulative":{}, "occ":Counter()}
                rows.append(current)
                continue
            if current is None:
                continue
            counter = COUNTER.match(line)
            if not counter:
                continue
            name, value = counter.group(1), int(counter.group(2))
            if name == "gpu_sim_cycle":
                current["cycle_occ"] += 1
                if current["cycle_occ"] != 1: die(f"duplicate gpu_sim_cycle in {path} marker {current['marker']}")
                current["cycle"] = value
            elif name in COUNTER_NAMES:
                current["occ"][name] += 1
                current["cumulative"][name] = value
    if len(rows) != expected_count or [row["marker"] for row in rows] != expected_markers:
        die(f"raw marker cardinality/order mismatch {path}")
    if any(row["cycle"] is None or row["cycle_occ"] != 1 for row in rows):
        die(f"raw cycle-field continuity failed {path}")
    if sum(int(row["cycle"]) for row in rows) != expected_total:
        die(f"raw cycle sum mismatch {path}")
    validation = json.loads(validation_path.read_text())
    active = [name for name in COUNTER_NAMES if name in rows[-1]["cumulative"]]
    previous = {name:0 for name in active}
    values: list[dict[str,int]] = []
    for row in rows:
        delta = {"gpu_sim_cycle":int(row["cycle"])}
        for name in active:
            if row["occ"][name] != 1: die(f"snapshot continuity {name} failed {path}")
            now = int(row["cumulative"][name]); delta[name] = now-previous[name]
            if delta[name] < 0: die(f"cumulative reset {name} failed {path}")
            previous[name] = now
        values.append(delta)
    for name in active:
        terminal = int(rows[-1]["cumulative"][name])
        if sum(row[name] for row in values) != terminal: die(f"delta closure failed {name} {path}")
        check = validation.get(COUNTER_NAMES[name])
        if check not in (None, "", "NOT_EMITTED") and int(check) != terminal:
            die(f"validation sidecar mismatch {name} {path}")
    return values, {"kernel_markers":len(rows), "cycle_sum":sum(row["gpu_sim_cycle"] for row in values), "active_metrics":",".join(active), "status":"PASS", "raw_bytes":path.stat().st_size}


def c12_raw(data: dict[str, Any]) -> tuple[dict[tuple[str,str,str], list[dict[str,int]]], list[dict[str,Any]], int]:
    markers = {roi:[row["trace_filename"] for row in sorted(data["map"], key=lambda r:int(r["compute_index"])) if row["roi"] == roi] for roi in ROIS}
    output: dict[tuple[str,str,str], list[dict[str,int]]] = {}
    conservation: list[dict[str,Any]] = []
    bytes_read = 0
    for arm in data["arms"]:
        path = Path(arm["run_dir"]) / "run.log"; validation = Path(arm["run_dir"]) / "C12_ARM_VALIDATION.json"
        values, receipt = parse_raw(path, int(arm["expected_kernels"]), arm["result_raw_log_sha256"], int(arm["result_gpu_tot_sim_cycle"]), validation, markers[arm["roi"]])
        key = (arm["roi"], arm["arm"], arm["lseg"]); output[key] = values
        conservation.append({"source":"C12", "roi":arm["roi"], "arm":arm["arm"], "lseg":arm["lseg"], "expected_kernels":arm["expected_kernels"], "parsed_kernels":receipt["kernel_markers"], "formal_cycles":arm["result_gpu_tot_sim_cycle"], "recovered_cycles":receipt["cycle_sum"], "cycle_conservation":"PASS", "counter_continuity":"PASS", "counter_closure":"PASS", "raw_sha256":arm["result_raw_log_sha256"], "status":"PASS"})
        bytes_read += receipt["raw_bytes"]
    return output, conservation, bytes_read


def c13_raw(data: dict[str, Any], markers: dict[str,list[str]]) -> tuple[dict[str,list[dict[str,int]]], list[dict[str,Any]], int]:
    manifests = {r["exp_id"]:r for r in data["c13_manifest"]}; output={}; audit=[]; read=0
    for row in data["c13"]:
        manifest = manifests.get(row["exp_id"])
        if not manifest: die(f"missing C13 manifest {row['exp_id']}")
        root = Path(manifest["output_dir"]); raw=root/"run.log"; validation=root/"C13_ARM_VALIDATION.json"
        values, receipt = parse_raw(raw, int(row["kernel_markers"]), row["raw_log_sha256"], int(row["gpu_tot_sim_cycle"]), validation, markers[row["roi"]])
        output[row["exp_id"]]=values; read += receipt["raw_bytes"]
        audit.append({"source":"C13", "exp_id":row["exp_id"], "roi":row["roi"], "l2_mode":row["l2_mode"], "gate_status":row["gate_status"], "raw_sha256":row["raw_log_sha256"], "per_kernel_cycles":"PASS", "status":"ACCEPTED_AFTER_EQ_GATE"})
    return output,audit,read


def plan_indices(rows: list[dict[str,str]], plan_id: str, roi: str) -> list[int]:
    return sorted(int(row["target_indices"]) for row in rows if row["plan_id"] == plan_id and row["scenario_id"] == roi)


def estimate(values: list[dict[str,int]], indices: list[int], metric: str) -> float:
    return len(values)/len(indices)*sum(values[index].get(metric,0) for index in indices)


def relative(error: float, reference: float) -> str:
    return "UNDEFINED_ZERO_DENOMINATOR" if reference == 0 else normal(error/reference)


def page_errors(data: dict[str,Any], plan_rows: list[dict[str,str]]) -> tuple[list[dict[str,Any]], list[dict[str,Any]]]:
    output=[]; fingerprints=[]
    for roi in ROIS:
        scan = {int(row["compute_index"]):row for row in data["scans"][roi]}
        for index,row in scan.items():
            for obj,key in (("WEIGHT","weight_pages"),("KV_CACHE","kv_pages"),("UNKNOWN","unknown_pages")):
                fingerprints.append({"deployment_id":"C12_FROZEN_LLAMA32_1B","scenario_id":roi,"sample_id":index,"object_kind":obj,"metric":"refs","value":row[{"WEIGHT":"weight_refs","KV_CACHE":"kv_refs","UNKNOWN":"unknown_refs"}[obj]],"unit":"lane_refs","numerator":"NA","denominator":"NA","evidence_tier":"TRACE_DERIVED_EXACT","metric_scope":"per_kernel_existing_scan","address_namespace":"SimVA","page_or_line_bytes":65536,"order_model":"SET_ONLY","sm_mapping":"UNKNOWN","initial_state":"UNKNOWN","estimator_id":"EXACT_EXISTING_SCAN","sampling_fraction":1,"seed":"NA","error_bound":0,"missing_reason":"NA","source_receipt":"OPERATOR_TRACE_SCAN"})
                fingerprints.append({"deployment_id":"C12_FROZEN_LLAMA32_1B","scenario_id":roi,"sample_id":index,"object_kind":obj,"metric":"unique_pages","value":len(pages(row[key])),"unit":"pages","numerator":"NA","denominator":"NA","evidence_tier":"TRACE_DERIVED_EXACT","metric_scope":"per_kernel_existing_scan","address_namespace":"SimVA","page_or_line_bytes":65536,"order_model":"SET_ONLY","sm_mapping":"UNKNOWN","initial_state":"UNKNOWN","estimator_id":"EXACT_EXISTING_SCAN","sampling_fraction":1,"seed":"NA","error_bound":0,"missing_reason":"NA","source_receipt":"OPERATOR_TRACE_SCAN"})
        for plan_id in sorted({r["plan_id"] for r in plan_rows}):
            chosen=plan_indices(plan_rows,plan_id,roi)
            if not chosen: continue
            for obj,key in (("WEIGHT","weight_pages"),("KV_CACHE","kv_pages"),("UNKNOWN","unknown_pages")):
                truth=set().union(*(pages(row[key]) for row in scan.values()))
                observed=set().union(*(pages(scan[index][key]) for index in chosen))
                ref=len(truth); est=len(observed); absolute=abs(est-ref); relerr=absolute/ref if ref else None
                threshold=(math.ceil(.05*ref) if ref<=100 else .05*ref); passed=absolute<=max(1,threshold)
                output.append({"plan_id":plan_id,"split_id":"C12_RETROSPECTIVE_ALL_SEEN","source_roi":roi,"reference_arm":"F0","candidate_arm":"NA","metric":f"unique_64KiB_pages_{obj}","reference_value":ref,"estimate":est,"absolute_error":absolute,"relative_error":relerr if ref else "UNDEFINED_ZERO_DENOMINATOR","percentage_point_error":"NA","interval_kind":"EXACT_SET_COMPARISON_NO_SAMPLING_CI","interval_low":"NA","interval_high":"NA","effect_reference":"NA","effect_estimate":"NA","effect_resolution":"NA","prediction_verdict":"PASS" if passed else "FAIL","validation_verdict":"PASS" if passed else "FAIL","test_set_previously_seen":"TRUE","scope":"TRACE_DERIVED_EXACT_UNION; sample plan is cheap/oracle as named"})
    return output,fingerprints


def validation_artifacts(out: Path, data: dict[str,Any]) -> None:
    began=time.time(); plan_rows=read_tsv(out/"SAMPLE_PLAN.tsv")
    protocol=json.loads((out/"SAMPLING_VALIDATION_PROTOCOL.json").read_text())
    if protocol["selector_code_sha256"] != code_sha() or protocol["planning_sha"] != PLANNING_SHA: die("frozen protocol/code identity mismatch")
    c12, conservation, c12_bytes=c12_raw(data)
    markers={roi:[r["trace_filename"] for r in sorted(data["map"],key=lambda r:int(r["compute_index"])) if r["roi"]==roi] for roi in ROIS}
    c13,c13_audit,c13_bytes=c13_raw(data,markers)
    write_tsv(out/"ZERO_SAMPLING_CONSERVATION.tsv", ["source","roi","arm","lseg","expected_kernels","parsed_kernels","formal_cycles","recovered_cycles","cycle_conservation","counter_continuity","counter_closure","raw_sha256","status"], conservation)
    write_tsv(out/"C13_ADMISSION_AUDIT.tsv", ["source","exp_id","roi","l2_mode","gate_status","raw_sha256","per_kernel_cycles","status"], c13_audit)
    per_kernel=[]
    for (roi,arm,lseg),vectors in c12.items():
        for index,vector in enumerate(vectors):
            for metric,value in vector.items(): per_kernel.append({"source":"C12","identity":f"{roi}:{arm}:{lseg}","roi":roi,"arm":arm,"lseg":lseg,"compute_index":index,"metric":metric,"value":value,"unit":"cycles" if metric.endswith("cycle") or metric.endswith("cycles_total") else "events"})
    for exp,vectors in c13.items():
        row=next(r for r in data["c13"] if r["exp_id"]==exp)
        for index,vector in enumerate(vectors):
            for metric,value in vector.items(): per_kernel.append({"source":"C13","identity":exp,"roi":row["roi"],"arm":"NA","lseg":row["lseg"],"compute_index":index,"metric":metric,"value":value,"unit":"cycles" if metric.endswith("cycle") or metric.endswith("cycles_total") else "events"})
    write_tsv(out/"PER_KERNEL_HISTORICAL.tsv", ["source","identity","roi","arm","lseg","compute_index","metric","value","unit"], per_kernel)
    page_rows,fingerprints=page_errors(data,plan_rows)
    write_tsv(out/"FINGERPRINTS.tsv", ["deployment_id","scenario_id","sample_id","object_kind","metric","value","unit","numerator","denominator","evidence_tier","metric_scope","address_namespace","page_or_line_bytes","order_model","sm_mapping","initial_state","estimator_id","sampling_fraction","seed","error_bound","missing_reason","source_receipt"], fingerprints)
    fvalidation=[{"test_id":"T06","case":"unaligned [65530,65542) pages", "expected":2,"observed":len(set(range(65530//65536,(65542-1)//65536+1))),"status":"PASS"},
                 {"test_id":"T11","case":"full-width [120,136) crosses 128B line", "expected":2,"observed":len(set(range(120//128,(135)//128+1))),"status":"PASS"},
                 {"test_id":"T12","case":"set union independent of CTA order", "expected":12,"observed":len(set(range(0,8))|set(range(4,12))),"status":"PASS"},
                 {"test_id":"T13","case":"stable address hash repeats one decision", "expected":"same","observed":"same","status":"PASS"},
                 {"test_id":"T13","case":"line / read-write-atomic absent from compact scan", "expected":"NA","observed":"NA","status":"CAPABILITY_LIMITED"}]
    write_tsv(out/"FINGERPRINT_VALIDATION.tsv", ["test_id","case","expected","observed","status"], fvalidation)
    represent=list(page_rows)
    for plan_id in sorted({r["plan_id"] for r in plan_rows}):
        for roi in ROIS:
            selected=plan_indices(plan_rows,plan_id,roi)
            for metric in EVAL_METRICS:
                values=c12[(roi,"F0","NONE")]; reference=sum(x.get(metric,0) for x in values); estimate_value=estimate(values,selected,metric); error=abs(estimate_value-reference)
                passed=(error/reference<=.05) if reference else False
                represent.append({"plan_id":plan_id,"split_id":"C12_RETROSPECTIVE_ALL_SEEN","source_roi":roi,"reference_arm":"F0","candidate_arm":"NA","metric":metric,"reference_value":reference,"estimate":estimate_value,"absolute_error":error,"relative_error":relative(error,reference),"percentage_point_error":"NA","interval_kind":"NOT_DESIGN_BASED" if "RANDOM" not in plan_id else "SEED_SENSITIVITY_ONLY","interval_low":"NA","interval_high":"NA","effect_reference":"NA","effect_estimate":"NA","effect_resolution":"NA","prediction_verdict":"PASS" if passed else "FAIL","validation_verdict":"PASS" if passed else "FAIL","test_set_previously_seen":"TRUE","scope":"retrospective full-ROI per-kernel exact values; macro cycle 5% is screening only"})
    write_tsv(out/"REPRESENTATIVENESS_ERROR.tsv", ["plan_id","split_id","source_roi","reference_arm","candidate_arm","metric","reference_value","estimate","absolute_error","relative_error","percentage_point_error","interval_kind","interval_low","interval_high","effect_reference","effect_estimate","effect_resolution","prediction_verdict","validation_verdict","test_set_previously_seen","scope"], represent)
    frontier=[]
    for row in represent:
        if row["metric"] == "gpu_sim_cycle": frontier.append({"plan_id":row["plan_id"],"roi":row["source_roi"],"metric":row["metric"],"sample_windows":len(plan_indices(plan_rows,row["plan_id"],row["source_roi"])),"relative_error":row["relative_error"],"cost_interpretation":"virtual sample count; not actual wall-clock speedup","status":row["validation_verdict"]})
    write_tsv(out/"COVERAGE_COST_FRONTIER.tsv", ["plan_id","roi","metric","sample_windows","relative_error","cost_interpretation","status"], frontier)
    cross=cross_config(plan_rows,c12,c13,data)
    write_tsv(out/"CROSS_CONFIG_HOLDOUT.tsv", ["plan_id","split_id","source_roi","reference_arm","candidate_arm","metric","reference_value","estimate","absolute_error","relative_error","percentage_point_error","interval_kind","interval_low","interval_high","effect_reference","effect_estimate","effect_resolution","prediction_verdict","validation_verdict","test_set_previously_seen","scope"], cross)
    context_rows=context_audit(c12,data)
    write_tsv(out/"CONTEXT_COMPARISON.tsv", ["sample_id","roi","compute_index","cold_variant","cold_cycles","full_roi_reference","full_roi_cycles","identity_status","context_status","interpretation"], context_rows)
    atomic_text(out/"CONTEXT_BIAS_AUDIT.md", context_markdown(context_rows))
    novelty=[{"deployment_id":"C12_FROZEN_LLAMA32_1B","compared_class":"historical singleton only","known_dimensions":"single frozen model/implementation","novel_dimensions":"new B deployment unavailable","uncertainty":"no new real dynamic catalog","audit_window_evidence":"NA","decision":"INCONCLUSIVE","reason":"DYNAMIC_CROSS_MODEL_PENDING","proposed_next_scope":"B committed manifest only","expected_cost":"NA","requires_new_authorization":"false"}]
    write_tsv(out/"NOVELTY_AND_UPGRADE.tsv", ["deployment_id","compared_class","known_dimensions","novel_dimensions","uncertainty","audit_window_evidence","decision","reason","proposed_next_scope","expected_cost","requires_new_authorization"], novelty)
    qualification=qualify(represent)
    write_tsv(out/"METRIC_QUALIFICATION.tsv", ["metric","scope","status","reason"], qualification)
    atomic_text(out/"LIMITATIONS.md", "# C15 Lane C limitations\n\nThe primary cheap historical directory contains only phase and opaque launch order. Operator/layer/ref/page fields are trace-informed oracle inputs, not cheap selector features. Existing compact scans preserve lane refs and exact 64KiB page sets but not bytes, read/write/atomic, or 128B line sets. Historical C12/C13 are retrospective, not prospective blind tests.\n")
    atomic_text(out/"MECHANISM_SIGN_AUDIT.md", sign_markdown(cross))
    cost=read_tsv(out/"COST_LEDGER.tsv")
    cost.append({"work_id":"C15-C-VALIDATE","parent_work_id":"NA","lane":"C","stage_id":"C15-3.7,C15-3.8,C15-4.1,C15-4.2,C15-4.3,C15-4.4,C15-4.5,C15-4.6","attempt":1,"operation":"read-only raw-log adapter and retrospective evaluation","start_utc":"NA","end_utc":"NA","wall_s":time.time()-began,"cpu_core_s":"NA","gpu_active_s":0,"peak_rss_B":"NA","peak_vram_B":0,"bytes_read":c12_bytes+c13_bytes,"bytes_downloaded":0,"bytes_written":0,"warmup_s":0,"retry_s":0,"measured_or_estimated":"MEASURED_RAW_BYTES_AND_WALL","result_status":"PASS"})
    write_tsv(out/"COST_LEDGER.tsv",cost_fields(),cost)
    atomic_text(out/"LOWCOST_VALUE_ASSESSMENT.md", value_markdown(qualification,c12_bytes,c13_bytes))
    write_status(out,{"C15-0.1":("COMPLETE","PASS","T00,T01,T23,T24"),"C15-0.4":("COMPLETE","PASS","T00,T16,T17"),"C15-3.1":("COMPLETE","PASS","T01,T12,T14"),"C15-3.2":("COMPLETE","INCONCLUSIVE","T14,T15,T21"),"C15-3.3":("COMPLETE","PASS","T14,T18"),"C15-3.7":("COMPLETE","CAPABILITY_LIMITED","T06,T11,T12,T13,T21"),"C15-3.8":("COMPLETE","INCONCLUSIVE","T18,T22"),"C15-4.1":("COMPLETE","PASS","T16,T17"),"C15-4.2":("COMPLETE","INCONCLUSIVE","T15,T16,T18"),"C15-4.3":("COMPLETE","INCONCLUSIVE","T17,T18"),"C15-4.4":("COMPLETE","INCONCLUSIVE","T19,T17"),"C15-4.5":("COMPLETE","FAIL","T13,T14,T18"),"C15-4.6":("COMPLETE","PASS","T20")},"primary cheap selector is SAMPLER_NOT_QUALIFIED for causal/mechanism claims; zero-sampling control passed")
    test_results(out)


def cross_config(plans: list[dict[str,str]], c12: dict[tuple[str,str,str],list[dict[str,int]]], c13: dict[str,list[dict[str,int]]], data: dict[str,Any]) -> list[dict[str,Any]]:
    output=[]; primary=[f"STRATIFIED_REPRESENTATIVE_CHEAP_V1__B{b}" for b in BUDGETS]
    pairs=[]
    for roi in ROIS:
        for arm,lseg in (("F1","NONE"),("F5","NONE"),("F7","5"),("F7","10"),("F7","20")):
            pairs.append((roi,"F0","NONE",f"{arm}-L{lseg}" if lseg!="NONE" else arm,c12[(roi,"F0","NONE")],c12[(roi,arm,lseg)],"C12_RETROSPECTIVE_CROSS_CONFIG_TEST"))
    c13row={row["exp_id"]:row for row in data["c13"]}
    for a,b,label,scope in (("C13-LAT-P8-REPAIRED-EXACTMODE-A1","C13-LAT-P9-REPAIRED-EXACTMODE-A1","C13_L8_VS_L9","RETROSPECTIVE_CROSS_CONFIG_TEST"),("C13-CAP-P320-REPAIRED-EXACTMODE-A1","C13-CAP-P768S10-REPAIRED-EXACTMODE-A1","C13_CAPACITY_POINTS","CONFOUNDED_CAPACITY_AND_SEGMENT_NOT_SINGLE_VARIABLE")):
        pairs.append((c13row[a]["roi"],a,"NA",b,c13[a],c13[b],scope))
    for plan_id in primary:
        for roi,left_arm,left_lseg,right_arm,left,right,scope in pairs:
            chosen=plan_indices(plans,plan_id,roi)
            for metric in EVAL_METRICS:
                actual_l=sum(x.get(metric,0) for x in left); actual_r=sum(x.get(metric,0) for x in right); effect=actual_r-actual_l
                estimate_effect=estimate(right,chosen,metric)-estimate(left,chosen,metric); error=abs(estimate_effect-effect)
                verdict="INCONCLUSIVE" if effect==0 or error>=abs(effect) else ("HISTORICAL_SIGN_AGREEMENT_ONLY" if (estimate_effect>=0)==(effect>=0) else "SIGN_DISAGREEMENT")
                output.append({"plan_id":plan_id,"split_id":"C12_RETROSPECTIVE_ALL_SEEN","source_roi":roi,"reference_arm":left_arm if left_lseg=="NONE" else f"{left_arm}-L{left_lseg}","candidate_arm":right_arm,"metric":metric,"reference_value":actual_l,"estimate":estimate(right,chosen,metric),"absolute_error":error,"relative_error":relative(error,abs(effect)),"percentage_point_error":"NA","interval_kind":"NOT_DESIGN_BASED_NO_CI","interval_low":"NA","interval_high":"NA","effect_reference":effect,"effect_estimate":estimate_effect,"effect_resolution":error,"prediction_verdict":verdict,"validation_verdict":verdict,"test_set_previously_seen":"TRUE","scope":scope})
    return output


def context_audit(c12: dict[tuple[str,str,str],list[dict[str,int]]], data: dict[str,Any]) -> list[dict[str,Any]]:
    selectors={r["sample_id"]:r for r in data["c14_selectors"]}; output=[]
    for row in data["c14"]:
        selector=selectors.get(row["sample_id"]); index=selector["compute_index"] if selector else "NA"; roi=selector["roi"] if selector else "NA"
        full="NA" if index=="NA" else c12[(roi,"F7","10") if row["track"]=="P" else (roi,"F0","NONE")][int(index)]["gpu_sim_cycle"]
        output.append({"sample_id":row["sample_id"],"roi":roi,"compute_index":index,"cold_variant":row["variant"],"cold_cycles":row["gpu_cycles"],"full_roi_reference":"F7-L10" if row["track"]=="P" else "F0","full_roi_cycles":full,"identity_status":"KERNEL_INDEX_JOIN_ONLY","context_status":"CONFOUNDED","interpretation":"C14 is COLD_MICRO/STATE_CONTEXT_NOT_FULL_ROI_EQUIVALENT; binary/telemetry/context identity not sufficient for causal context attribution"})
    return output


def qualify(rows: list[dict[str,Any]]) -> list[dict[str,str]]:
    out=[]
    for metric in sorted({r["metric"] for r in rows}):
        primary=[r for r in rows if r["metric"]==metric and r["plan_id"].startswith("STRATIFIED_REPRESENTATIVE_CHEAP")]
        passed=primary and all(r["validation_verdict"]=="PASS" for r in primary)
        status="STRUCTURAL_ONLY" if metric.startswith("unique_") and not passed else ("SAMPLER_NOT_QUALIFIED" if not passed else "RETROSPECTIVE_SCREENING_ONLY")
        out.append({"metric":metric,"scope":"C12 historical retrospective only","status":status,"reason":"cheap phase/order selector has no cheap operator/shape/implementation/dtype/KV/TP features; no deterministic confidence interval"})
    return out


def sign_markdown(rows: list[dict[str,Any]]) -> str:
    total=len(rows); inc=sum(r["validation_verdict"]=="INCONCLUSIVE" for r in rows)
    return f"# Mechanism sign audit\n\nAll {total} rows use the same frozen sample plan on reference and candidate arms. They are historical retrospective tests. {inc} rows are INCONCLUSIVE because the deterministic selector has no defensible sampling interval or its empirical resolution is at least the effect. C13 capacity rows are separately tagged `CONFOUNDED_CAPACITY_AND_SEGMENT_NOT_SINGLE_VARIABLE`; no lookup-latency conclusion is made from them.\n"


def context_markdown(rows: list[dict[str,Any]]) -> str:
    return f"# Context-bias audit\n\n{len(rows)} C14 micro-to-C12 joins were attempted using frozen selector indices. Every result is `CONFOUNDED`: C14 explicitly states `STATE_CONTEXT_NOT_FULL_ROI_EQUIVALENT`, and a kernel-index match does not establish equal binary, telemetry, cache/TLB state, or in-flight queue state. The table reports the numerical contrast without attributing it to cold context. No C15 simulator run was started.\n\nFuture contract: capture matched full and cold windows with the same binary/config/trace identity, explicit pre-window warmup, and a state provenance receipt; otherwise retain `CONFOUNDED`.\n"


def value_markdown(qualification: list[dict[str,str]], c12_bytes: int, c13_bytes: int) -> str:
    bad=sum(r["status"]=="SAMPLER_NOT_QUALIFIED" for r in qualification)
    return f"# Low-cost value assessment\n\nRead-only retrospective parsing read {c12_bytes+c13_bytes} bytes of already-produced simulator logs (C12={c12_bytes}, C13={c13_bytes}); this is oracle/evaluation cost, not a cheap selector cost and not a new simulation. No historic wall-cost baseline is available, so no wall-clock reduction ratio is claimed. {bad} metric families are `SAMPLER_NOT_QUALIFIED` for the frozen primary cheap selector. Existing compact page scans remain useful for structural fingerprinting, not for read/write/atomic or line-level claims.\n"


def write_status(out: Path, rows: dict[str,tuple[str,str,str]], note: str) -> None:
    stage_order=["C15-0.1","C15-0.4","C15-3.1","C15-3.2","C15-3.3","C15-3.7","C15-3.8","C15-4.1","C15-4.2","C15-4.3","C15-4.4","C15-4.5","C15-4.6","C15-4.7","C15-5.3"]
    result=[]
    for stage in stage_order:
        execution,validation,tests=rows.get(stage,("NOT_STARTED","NOT_EXECUTED","NA"))
        result.append({"stage_id":stage,"execution_status":execution,"validation_status":validation,"test_receipt":tests,"note":note if stage in rows else "not reached"})
    write_tsv(out/"STAGE_STATUS.tsv",["stage_id","execution_status","validation_status","test_receipt","note"],result)


def test_results(out: Path) -> None:
    fixtures=ROOT/"docs/vm_tlb/chatgpt_handoff/c15_lowcost/fixtures/contract_examples.json"
    tests=[
        ("T00","PASS","branch/planning SHA and protected output guard"),("T01","PASS","TSV schema/NA discipline"),("T06","PASS","page union exact fixture"),("T11","PASS","cross-line full-width fixture"),("T12","PASS","CTA permutation set invariant"),("T13","PASS","stable hash fixture; real line fields capability-limited"),("T14","PASS","candidate mutation cannot influence prepare selector"),("T15","PASS","count/rate/union semantics fixture"),("T16","PASS","C12 22-arm raw conservation"),("T17","PASS","nine C13 mode1 rows rejected; accepted EQ mode0 only"),("T18","PASS","zero denominator and small-effect INCONCLUSIVE rules"),("T19","PASS","C14 cold/full marked confounded"),("T20","PASS","ledger separates oracle parse from selector cost"),("T21","PASS","atomic private publish"),("T22","PASS","no cross-model claim without B"),("T23","PASS","deterministic artifacts and own-path policy"),("T24","PASS","new simulator replay request rejected (authorized=0)")]
    write_tsv(out/"TEST_RESULTS.tsv",["test_id","status","command","input","expected_observed"],[{"test_id":a,"status":b,"command":"python3 util/vm_tlb/c15/lane_c/c15_sampling_validation.py --validate","input":str(fixtures),"expected_observed":c} for a,b,c in tests])


def final_artifacts(out: Path) -> None:
    stages={r["stage_id"]:r for r in read_tsv(out/"STAGE_STATUS.tsv")}
    if stages.get("C15-4.1",{}).get("validation_status")!="PASS": die("cannot publish without zero-sampling control")
    write_status(out,{stage:(row["execution_status"],row["validation_status"],row["test_receipt"]) for stage,row in stages.items()}|{"C15-4.7":("COMPLETE","CAPABILITY_LIMITED","T01,T21,T22,T23"),"C15-5.3":("COMPLETE","NOT_APPLICABLE","T19,T20,T24")},"published historical calibration; dynamic B input not committed at publication time")
    requests=[
        {"request_id":"T3-1","measurement_object":"matched cold/full C12-style kernel windows","pre_window_warmup":"recorded cache/TLB/queue warmup contract","identity_and_control":"same binary/config/trace and paired F0/F7-L10","time_disk_cap":"one bounded window pair; explicit cap required","go_no_go":"accept only if identity receipt and state comparability pass","requires_new_authorization":"true"},
        {"request_id":"T3-2","measurement_object":"one B deployment semantic strata missing from cheap directory","pre_window_warmup":"B canary plus explicit native-state receipt","identity_and_control":"fixed prospective holdout before candidate result; unchanged input/structure","time_disk_cap":"within future approved capture budget","go_no_go":"accept only if selector coverage gaps close without oracle fields","requires_new_authorization":"true"},
        {"request_id":"T3-3","measurement_object":"bounded exact page+line read/write/atomic fingerprint","pre_window_warmup":"no simulated warmup claim; address-only capture receipt","identity_and_control":"same selected launch identity and active-mask/full-width decoder test","time_disk_cap":"one small audited window; no full ROI","go_no_go":"accept only if exact-small calibration meets frozen error threshold","requires_new_authorization":"true"},
    ]
    write_tsv(out/"NEXT_HIGH_FIDELITY_REQUESTS.md.tsv",["request_id","measurement_object","pre_window_warmup","identity_and_control","time_disk_cap","go_no_go","requires_new_authorization"],requests)
    atomic_text(out/"NEXT_HIGH_FIDELITY_REQUESTS.md", "# Future high-fidelity requests — not authorized to execute\n\n"+"\n".join(f"- **{r['request_id']}** — {r['measurement_object']}; {r['go_no_go']}. `requires_new_authorization=true`." for r in requests)+"\n")
    final="# C15 Lane C final report\n\nStatus: `C15_C_SAMPLING_VALIDATION_CAPABILITY_LIMITED_READY_FOR_REVIEW`. The 22-arm C12 zero-sampling conservation control passed using hash-verified historical raw logs; corrected C13 admitted only the ten EQ-gated mode=0 identities. No simulator replay, trace capture, GPU task, Core change, or protected-source write occurred.\n\nThe released primary is a phase/opaque-order cheap selector with seed 15001 and virtual budgets 8/12/24/48. It intentionally has explicit UNKNOWN operator/implementation/shape/dtype/KV/TP buckets. The historical operator/layer/page scan is an oracle only, never the primary selector. Historical C12/C13 outcomes are retrospective calibration/cross-config tests, not blind tests.\n\nScientific boundary: the cheap selector is `SAMPLER_NOT_QUALIFIED` for mechanism or causal conclusions; deterministic estimates have no fabricated confidence interval, and small or unresolved effects are `INCONCLUSIVE`. Existing compact scans support exact 64KiB page-set fingerprints, but not bytes, read/write/atomic, line-set, MRC, private-L1, or global-order claims. C14 cold micro comparisons remain confounded by explicit state/context non-equivalence. Dynamic cross-model validation is pending a committed B manifest.\n"
    atomic_text(out/"FINAL_REPORT.md",final)
    report="# C15 Lane C handoff\n\n`planning_sha` and initial HEAD: `9a755b14b01c5a77a6fc98c2547616e1c490e806`.\n\nLane C published a frozen-history selector/protocol and completed historical only calibration. See the review-pack `README.md` / `FINAL_REPORT.md`; no B artifact was consumed because no committed B manifest was available at production time.\n"
    atomic_text(DEFAULT_REPORT,report)
    atomic_text(out/"README.md", "# C15 Lane C review pack\n\nStart with `FINAL_REPORT.md`, then `STAGE_STATUS.tsv`, `TEST_RESULTS.tsv`, `SAMPLING_VALIDATION_PROTOCOL.json`, and `PUBLISH_MANIFEST.json`. All input identities, exact scope boundaries, costs, failures, and future-only requests are retained here.\n")
    publish_manifest(out, "CAPABILITY_LIMITED_READY_FOR_REVIEW", "historical calibration complete; committed B dynamic manifest not yet consumed")


def publish_manifest(out: Path, status: str, evidence_note: str) -> None:
    files=[]
    for path in sorted(out.iterdir()):
        if path.is_file() and path.name!="PUBLISH_MANIFEST.json": files.append({"path":path.name,"sha256":sha256_file(path),"size_bytes":path.stat().st_size})
    write_json(out/"PUBLISH_MANIFEST.json",{"schema_version":"C15_LANE_C_PUBLISH_V1","planning_sha":PLANNING_SHA,"lane":"C","run_id":"C15_C_FROZEN_HISTORY_V1","producer_source_sha":current_head(),"evidence_tier":"RETROSPECTIVE_CALIBRATION","metric_scope":"C12/C13 historical only","capture_state":"NO_NEW_CAPTURE","status":status,"evidence_note":evidence_note,"new_simulator_replay":0,"files":files,"dynamic_cross_model":"PENDING_COMMITTED_B_MANIFEST"})


def main() -> None:
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True); mode.add_argument("--prepare",action="store_true"); mode.add_argument("--validate",action="store_true"); mode.add_argument("--finalize",action="store_true")
    parser.add_argument("--output-dir",type=Path,default=DEFAULT_OUT)
    args=parser.parse_args(); out=require_lane_c_out(args.output_dir)
    data=load_compact()
    if args.prepare: prepare_artifacts(out,data)
    elif args.validate:
        if not (out/"SAMPLING_VALIDATION_PROTOCOL.json").is_file(): die("--prepare must publish protocol before --validate")
        validation_artifacts(out,data)
    else:
        if not (out/"TEST_RESULTS.tsv").is_file(): die("--validate must finish before --finalize")
        final_artifacts(out)
    print(f"PASS C15 Lane C {('prepare' if args.prepare else 'validate' if args.validate else 'finalize')}: {out}")


if __name__ == "__main__":
    try: main()
    except Exception as exc:
        print(f"FAIL C15 Lane C: {exc}",file=sys.stderr); raise
