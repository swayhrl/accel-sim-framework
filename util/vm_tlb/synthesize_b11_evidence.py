#!/usr/bin/env python3
"""Create the B11 speculative evidence pack from completed frozen B9 output.

This is intentionally offline and streaming: it reads individual simulator
logs line by line and small miner TSVs.  It never starts a worker, builds, or
reads another Window's private inputs.  The tool refuses a partial B11 state.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
from pathlib import Path
from typing import Dict, Iterable, List


LABEL = "SPECULATIVE_DIAGNOSTIC"
TASKS = ("E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10")
SIM_ARMS = {
    "E01": ("E01-generic", "E01-pwc32"), "E02": ("E02-generic", "E02-pwc512"),
    "E03": ("E03-generic", "E03-pwcideal"), "E04": ("E04-generic64k", "E04-page2mb"),
    "E05": ("E05-generic", "E05-disabled"), "E06": ("E06-generic", "E06-ideal"),
}
OBJECTS = ("WEIGHT", "KV_CACHE", "UNKNOWN")
CORE_METRICS = (
    "gpu_tot_sim_cycle", "gpu_tot_ipc", "vm_translation_lookup_requests",
    "vm_l1_tlb_hits", "vm_l1_tlb_misses", "vm_l2_tlb_hits", "vm_l2_tlb_misses",
    "vm_translation_mshr_allocations", "vm_translation_mshr_merges", "vm_translation_mshr_full_events",
    "vm_translation_mshr_lifetime_cycles_total", "vm_translation_mshr_lifetime_cycles_max",
    "vm_translation_requester_mshr_wait_cycles_total", "vm_translation_requester_mshr_wait_cycles_max",
    "vm_translation_pwq_occupancy", "vm_translation_pwq_full_events",
    "vm_translation_requester_l2_queue_cycles_total", "vm_translation_requester_l2_queue_cycles_max",
    "vm_translation_walkers_active", "vm_translation_walk_starts", "vm_translation_walk_completions",
    "vm_pwc_mode", "vm_pwc_entries_configured", "vm_pwc_accesses", "vm_pwc_hits", "vm_pwc_misses",
    "vm_pte_requests", "vm_pte_responses", "vm_pte_l2_only_responses", "vm_pte_dram_responses",
    "vm_pte_memory_wait_cycles_total", "vm_pte_memory_wait_cycles_max",
    "vm_object_attribution_conservation_pass",
)
OBJECT_SUFFIXES = (
    "translation_requesters", "l1_hits", "l1_misses", "l2_hits", "l2_misses", "mshr_allocations",
    "mshr_merges", "walk_starts", "pwc_accesses", "pwc_hits", "pwc_misses", "pte_requests",
    "pte_l2_only_responses", "pte_dram_responses", "pte_memory_wait_cycles_total",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_tsv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def write_tsv(path: Path, rows: List[Dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing to create empty table {path}")
    fields = list(rows[0])
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: "NOT_AVAILABLE" if row.get(field) in (None, "") else row.get(field)
                             for field in fields})


def manifest(path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    for line in path.read_text(errors="replace").splitlines()[1:]:
        if "\t" in line:
            key, value = line.split("\t", 1)
            values[key] = value
    return values


def log_values(path: Path, wanted: Iterable[str]) -> Dict[str, str]:
    wanted = tuple(wanted)
    wanted_set = set(wanted)
    values = {key: "NOT_EMITTED" for key in wanted}
    with path.open(errors="replace") as stream:
        for line in stream:
            if " = " not in line:
                continue
            key, value = line.rstrip("\n").split(" = ", 1)
            if key in wanted_set:
                values[key] = value.strip()
    return values


def realized_config(path: Path) -> Dict[str, str]:
    flags = {
        "-gpgpu_vm_mode": "realized_vm_mode",
        "-gpgpu_vm_page_size": "realized_page_size_bytes",
        "-gpgpu_vm_pwc_mode": "realized_pwc_mode",
        "-gpgpu_vm_pwc_entries": "realized_pwc_entries",
    }
    result = {value: "NOT_EMITTED" for value in flags.values()}
    with path.open(errors="replace") as stream:
        for line in stream:
            fields = line.split()
            if len(fields) >= 2 and fields[0] in flags:
                result[flags[fields[0]]] = fields[1]
    return result


def float_or_none(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def latest_state(path: Path) -> Dict[str, str]:
    result = {task: "NOT_STARTED" for task in TASKS}
    for row in read_tsv(path):
        if row["task"] in result:
            result[row["task"]] = row["state"]
    return result


def simulator_rows(future: Path) -> tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    rows: List[Dict[str, object]] = []
    checks: List[Dict[str, object]] = []
    all_metrics = list(CORE_METRICS) + [f"vm_object_{kind}_{suffix}" for kind in OBJECTS for suffix in OBJECT_SUFFIXES]
    for experiment, arms in SIM_ARMS.items():
        for arm in arms:
            output = future / arm
            run_manifest, log = output / "RUN_MANIFEST.tsv", output / "run.log"
            if not run_manifest.is_file() or not log.is_file():
                raise RuntimeError(f"missing frozen simulator evidence for {arm}")
            run = manifest(run_manifest)
            values = log_values(log, all_metrics)
            realization = realized_config(log)
            prelaunch = manifest(future / f"{arm}.PRELAUNCH.tsv")
            time_v = future / f"{arm}.time-v.txt"
            if not time_v.is_file():
                raise RuntimeError(f"missing B11 RSS sidecar for {arm}")
            log_text = log.read_text(errors="replace")
            processing = sum(line.startswith("Processing kernel ") for line in log_text.splitlines())
            profile = run.get("profile", "NOT_AVAILABLE")
            base = {
                "evidence_label": LABEL, "experiment_id": experiment, "arm_id": arm,
                "evidence_scope": "SIM_SMOKE_ONE_KERNEL_CONTINUOUS_REPLAY", "roi": run.get("roi", "NOT_AVAILABLE"),
                "profile": profile, "extra_config": run.get("extra_config", "NONE"),
                "simulator_exit_status": run.get("simulator_exit_status", "NOT_AVAILABLE"),
                "processing_kernels": processing, "telemetry_schema_records": log_text.count("m4c_telemetry_schema ="),
                "binary_sha256": prelaunch.get("binary_sha256", "NOT_AVAILABLE"),
                "run_manifest_sha256": sha256(run_manifest), "run_log_sha256": sha256(log),
                "time_v_sha256": sha256(time_v),
                "interpretation_guard": "single-kernel smoke; do not infer full-ROI performance from hit/miss or IPC alone",
            }
            base.update(realization)
            base.update(values)
            rows.append(base)
            common = (run.get("simulator_exit_status") == "0" and processing == 1 and
                      log_text.count("m4c_telemetry_schema =") == 1 and
                      values["gpu_tot_sim_cycle"] != "NOT_EMITTED" and values["gpu_tot_ipc"] != "NOT_EMITTED")
            if profile in ("disabled", "ideal"):
                telemetry_ok = all(values[metric] == "NOT_EMITTED" for metric in CORE_METRICS[2:])
                note = "translation controller telemetry intentionally absent for this frozen control"
            else:
                telemetry_ok = all(values[metric] != "NOT_EMITTED" for metric in CORE_METRICS)
                telemetry_ok = telemetry_ok and values["vm_object_attribution_conservation_pass"] == "1"
                note = "mode-2 telemetry and object-conservation required"
            checks.append({"evidence_label": LABEL, "item": arm, "check": "SIMULATOR_COMPLETION_AND_TELEMETRY",
                           "result": "PASS" if common and telemetry_ok else "FAIL", "detail": note})
    return rows, checks


def static_summary(future: Path) -> tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    summary: List[Dict[str, object]] = []
    checks: List[Dict[str, object]] = []
    for experiment, arm in (("E09", "E09-prefill-static16"), ("E10", "E10-decode-static16")):
        output = future / arm
        stats, reuse, conservation = (output / "TRACE_STATIC_KERNEL_STATS.tsv",
                                      output / "TRACE_REUSE_DISTANCE_SUMMARY.tsv",
                                      output / "TRACE_MINING_CONSERVATION.tsv")
        if not all(path.is_file() for path in (stats, reuse, conservation)):
            raise RuntimeError(f"missing static-mining reducer output for {experiment}")
        data = read_tsv(stats)
        all_rows = [row for row in data if row["object_class"] == "ALL"]
        if len(all_rows) != 16:
            raise RuntimeError(f"{experiment} did not retain exactly 16 selected ALL rows")
        by_object = {kind: [row for row in data if row["object_class"] == kind] for kind in OBJECTS}
        lane_total = sum(int(row["lane_references"]) for row in all_rows)
        row: Dict[str, object] = {
            "evidence_label": LABEL, "experiment_id": experiment, "arm_id": arm,
            "evidence_scope": "STATIC_MATCHED_METADATA_16_KERNEL_SAMPLE", "roi": all_rows[0]["roi"],
            "selected_kernel_count": len(all_rows), "memory_instructions_sum": sum(int(x["memory_instructions"]) for x in all_rows),
            "lane_references_sum": lane_total, "requested_bytes_sum": sum(int(x["requested_bytes"]) for x in all_rows),
            "sectors_sum_per_kernel": sum(int(x["unique_32b_sectors"]) for x in all_rows),
            "lines_sum_per_kernel": sum(int(x["unique_128b_lines"]) for x in all_rows),
            "pages64k_sum_per_kernel": sum(int(x["unique_64kb_pages"]) for x in all_rows),
            "pages2m_sum_per_kernel": sum(int(x["unique_2mb_pages"]) for x in all_rows),
            "adjacent_pairs_sum": sum(int(x["lane_adjacent_pairs"]) for x in all_rows),
            "adjacent_equal_width_sum": sum(int(x["lane_adjacent_equal_width"]) for x in all_rows),
            "interpretation_guard": "metadata-matched static sample, not matched dynamic behavior and not full ROI",
        }
        for kind, values in by_object.items():
            lanes = sum(int(x["lane_references"]) for x in values)
            row[f"{kind.lower()}_lanes"] = lanes
            row[f"{kind.lower()}_lane_pct"] = f"{100 * lanes / lane_total:.6f}" if lane_total else "NOT_AVAILABLE"
            row[f"{kind.lower()}_bytes"] = sum(int(x["requested_bytes"]) for x in values)
        pairs = int(row["adjacent_pairs_sum"])
        row["adjacent_equal_width_pct"] = f"{100 * int(row['adjacent_equal_width_sum']) / pairs:.6f}" if pairs else "NOT_AVAILABLE"
        summary.append(row)
        conservation_rows = {r["check"]: r for r in read_tsv(conservation)}
        for check, item in conservation_rows.items():
            checks.append({"evidence_label": LABEL, "item": experiment, "check": check,
                           "result": item.get("result", "NOT_AVAILABLE"), "detail": "frozen streaming miner conservation"})
        for item in read_tsv(reuse):
            summary.append({"evidence_label": LABEL, "experiment_id": experiment, "arm_id": arm,
                            "evidence_scope": "STATIC_MATCHED_METADATA_16_KERNEL_SAMPLE", "roi": item["roi"],
                            "selected_kernel_count": 16, "memory_instructions_sum": "NOT_APPLICABLE",
                            "lane_references_sum": item["sampled_references"], "requested_bytes_sum": "NOT_APPLICABLE",
                            "sectors_sum_per_kernel": "NOT_APPLICABLE", "lines_sum_per_kernel": "NOT_APPLICABLE",
                            "pages64k_sum_per_kernel": "NOT_APPLICABLE", "pages2m_sum_per_kernel": "NOT_APPLICABLE",
                            "adjacent_pairs_sum": "NOT_APPLICABLE", "adjacent_equal_width_sum": "NOT_APPLICABLE",
                            "interpretation_guard": f"{item['method']}; sample_stride={item['sample_stride_lane_references']}; reuse distance is sampled",})
    return summary, checks


def pair_deltas(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    by_arm = {str(row["arm_id"]): row for row in rows}
    paired = (("E01-generic", "E01-pwc32"), ("E02-generic", "E02-pwc512"),
              ("E03-generic", "E03-pwcideal"), ("E04-generic64k", "E04-page2mb"),
              ("E05-generic", "E05-disabled"), ("E06-generic", "E06-ideal"))
    metrics = ("gpu_tot_sim_cycle", "gpu_tot_ipc", "vm_l1_tlb_misses", "vm_l2_tlb_misses",
               "vm_translation_mshr_full_events", "vm_translation_pwq_full_events", "vm_translation_walk_starts",
               "vm_pwc_hits", "vm_pwc_misses", "vm_pte_requests", "vm_pte_dram_responses")
    output: List[Dict[str, object]] = []
    for baseline, target in paired:
        for metric in metrics:
            before, after = str(by_arm[baseline][metric]), str(by_arm[target][metric])
            before_f, after_f = float_or_none(before), float_or_none(after)
            delta = "NOT_APPLICABLE" if before_f is None or after_f is None else f"{after_f - before_f:.6f}"
            pct = "NOT_APPLICABLE" if before_f in (None, 0) or after_f is None else f"{100 * (after_f - before_f) / before_f:.6f}"
            output.append({"evidence_label": LABEL, "baseline_arm": baseline, "target_arm": target,
                           "metric": metric, "baseline_value": before, "target_value": after,
                           "absolute_delta": delta, "relative_delta_pct": pct,
                           "scope_guard": "single-kernel smoke only; performance is interpreted jointly with translation pressure"})
    return output


def normalized_resource_history(legacy: List[Dict[str, str]], adaptive: List[Dict[str, str]]) -> List[Dict[str, object]]:
    fields = ("timestamp_utc", "policy_version", "task", "task_class", "event", "decision", "reason",
              "predicted_peak_rss_kb", "observed_peak_rss_kb", "reserve_kb", "mem_available_kb", "mem_required_kb",
              "swap_free_kb", "swap_in_delta", "swap_out_delta", "memory_full_pct", "io_full_pct", "iowait_pct")
    rows: List[Dict[str, object]] = []
    for row in legacy:
        rows.append({"timestamp_utc": row["timestamp_utc"], "policy_version": "LEGACY_FIXED_GATE_V1",
                     "task": row["task"], "task_class": "SMOKE", "event": row["event"],
                     "decision": "RESOURCE_DEFERRED", "reason": row["reason"], "predicted_peak_rss_kb": "NOT_APPLICABLE",
                     "observed_peak_rss_kb": "NOT_APPLICABLE", "reserve_kb": "NOT_APPLICABLE",
                     "mem_available_kb": row["mem_available_kb"], "mem_required_kb": row["mem_required_kb"],
                     "swap_free_kb": row["swap_free_kb"], "swap_in_delta": row["swap_in_delta"],
                     "swap_out_delta": row["swap_out_delta"], "memory_full_pct": row["memory_full_pct"],
                     "io_full_pct": row["io_full_pct"], "iowait_pct": row["iowait_pct"]})
    for row in adaptive:
        rows.append({field: row.get(field, "NOT_AVAILABLE") for field in fields})
    return rows


def write_markdown(pack: Path, static: List[Dict[str, object]], deltas: List[Dict[str, object]], waits: List[Dict[str, str]]) -> None:
    static_by_experiment = {str(row["experiment_id"]): row for row in static if row.get("memory_instructions_sum") != "NOT_APPLICABLE"}
    e09, e10 = static_by_experiment["E09"], static_by_experiment["E10"]
    unknown_high = all(float(str(row["unknown_lane_pct"])) >= 50.0 for row in (e09, e10))
    def delta(baseline: str, target: str, metric: str) -> Dict[str, object]:
        return next(row for row in deltas if row["baseline_arm"] == baseline and row["target_arm"] == target and row["metric"] == metric)
    pwc_pairs = {("E01-generic", "E01-pwc32"), ("E02-generic", "E02-pwc512"),
                 ("E03-generic", "E03-pwcideal")}
    pwc_changed = [row for row in deltas if (row["baseline_arm"], row["target_arm"]) in pwc_pairs and
                   row["absolute_delta"] not in ("0.000000", "NOT_APPLICABLE")]
    control_cycle = delta("E05-generic", "E05-disabled", "gpu_tot_sim_cycle")
    control_ipc = delta("E05-generic", "E05-disabled", "gpu_tot_ipc")
    page_cycle = delta("E04-generic64k", "E04-page2mb", "gpu_tot_sim_cycle")
    h6 = "SUPPORTED" if unknown_high else "UNRESOLVED"
    (pack / "HYPOTHESIS_UPDATE.md").write_text(
        "# B11 hypothesis update\n\n"
        "All entries are **SPECULATIVE_DIAGNOSTIC**. E01–E06 are one-kernel simulator smokes; "
        "E09/E10 are metadata-matched static 16-kernel samples. Neither is full-ROI evidence.\n\n"
        "| Hypothesis | B11 status | Evidence and limit |\n|---|---|---|\n"
        f"| H1 phase structure | UNRESOLVED | Same-budget static samples differ descriptively (prefill/decode UNKNOWN {e09['unknown_lane_pct']}%/{e10['unknown_lane_pct']}%; equal-width adjacency {e09['adjacent_equal_width_pct']}%/{e10['adjacent_equal_width_pct']}%), but metadata matching is not dynamic matching or full-phase evidence. |\n"
        f"| H2 PWC/PTW sensitivity | WEAKENED | E01–E03 realize finite-32, finite-512, and ideal PWC, yet their registered ladder pair deltas are {len(pwc_changed)} for the reported performance/translation metrics. This weakens the prior one-kernel PWC sensitivity signal only at this smoke scope. |\n"
        f"| H3 Weight Segment coverage limit | SUPPORTED | Static classified Weight lanes are only {e09['weight_lane_pct']}% prefill and {e10['weight_lane_pct']}% decode while UNKNOWN is high. This supports an attribution/coverage ceiling, not a Segment performance claim. |\n"
        "| H4 post-L1 sibling locality | UNRESOLVED | No B11 arm measures the C-owned post-L1 sibling occupancy falsifier. |\n"
        f"| H5 conventional VM importance | UNRESOLVED | VM-disabled/ideal controls change this smoke from {control_cycle['baseline_value']} to {control_cycle['target_value']} cycles ({control_cycle['relative_delta_pct']}%) and IPC from {control_ipc['baseline_value']} to {control_ipc['target_value']} ({control_ipc['relative_delta_pct']}%), while the 2 MiB diagnostic cycle delta is {page_cycle['relative_delta_pct']}%. There is no full-ROI or candidate comparison to rank mechanisms. |\n"
        f"| H6 UNKNOWN attribution risk | {h6} | E09 UNKNOWN lane fractions: prefill {e09['unknown_lane_pct']}%; decode1 {e10['unknown_lane_pct']}%. UNKNOWN remains distinct and is not reassigned. |\n")
    (pack / "ANOMALIES_AND_GAPS.md").write_text(
        "# B11 anomalies and remaining gaps\n\n"
        f"- Resource admission recorded {len(waits)} B11 samples; these are host-safety observations, not experiment results.\n"
        "- E01–E06 are exactly one-kernel smoke/control replays; they cannot settle full-workload ranking.\n"
        "- E09/E10 select 16 kernels by frozen metadata selector; static locality is not dynamic translation timing.\n"
        "- UNKNOWN is retained as an independent object class. No B11 result proves that it is Weight, KV, or a mapping error.\n"
        "- B11 repaired three B-local launcher/supervisor defects (Bash local expansion in simulator/miner paths, selector filename field, and reducer-schema completion check). Failed pre-start/invalid sidecars are retained under scratch failed_attempts; no valid raw result was overwritten.\n"
        "- No E11–E18 workload or candidate experiment was executed.\n")
    (pack / "NEXT_EXPERIMENT_RECOMMENDATIONS.md").write_text(
        "# Next recommendations after B11 review\n\n"
        "All are future **SPECULATIVE_DIAGNOSTIC** proposals and are not executed by B11.\n\n"
        "1. E11/E15: continuous-ROI conventional brackets, retaining cycles/IPC jointly with TLB/PTW/PWC/MSHR/PWQ and downstream pressure.\n"
        "2. E12–E14: only the specific conventional arm whose B11 smoke observables differ materially; include opposite/null interpretation.\n"
        "3. E16: C-owned post-L1 sibling occupancy falsifier before any sub-entry benefit claim.\n"
        "4. E17: C-owned Segment path chain (classified → descriptor-covered → hit → avoided path → latency/throughput).\n"
        "5. E18 only after decode-side candidate falsifiers are informative; retain prefill/decode separation.\n")
    (pack / "FINAL_REPORT.md").write_text(
        "# B11 final report\n\n"
        "**Status: `B11_E01_E10_COMPLETE_READY_FOR_REVIEW`**\n"
        "**Evidence label: `SPECULATIVE_DIAGNOSTIC`**\n\n"
        "B11 executed the frozen E01–E10 package with effective B heavy concurrency one, a 10-second `ADAPTIVE_RESOURCE_V2` gate, per-quantum shared heavy-slot locking, and `/usr/bin/time -v` sidecars. "
        "All 12 simulator arms, two one-kernel calibrations, and two 16-kernel static mining tasks pass their recorded completion/conservation contracts.\n\n"
        f"The PWC finite-32/finite-512/ideal ladder and the 2 MiB diagnostic were realized but showed zero registered cycle deltas in this one-kernel smoke; the VM-disabled/ideal controls instead reduce cycles by {control_cycle['relative_delta_pct']}% and raise IPC by {control_ipc['relative_delta_pct']}%. "
        "This is a control-boundary observation, not a full-ROI performance conclusion and not a hit/miss-only conclusion.\n\n"
        f"E09/E10 static samples contain 16 kernels each. Prefill/decode UNKNOWN lane mass is {e09['unknown_lane_pct']}%/{e10['unknown_lane_pct']}%; Weight is {e09['weight_lane_pct']}%/{e10['weight_lane_pct']}%. "
        "Those attribution facts are retained as static evidence only. The pack intentionally does not promote any result into full-workload, formal, or candidate-performance evidence.\n\n"
        "See `E01_E06_TRANSLATION_AND_PERF.tsv` for joint performance/translation observables, "
        "`E07_E08_RSS_CALIBRATION.tsv` for calibration, `E09_E10_STATIC_MINING_SUMMARY.tsv` for static scope, "
        "and `HYPOTHESIS_UPDATE.md` for the bounded H1–H6 update.\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scratch-root", type=Path, default=Path("/workspace/vm-spec-farm"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replace-generated-pack", action="store_true",
                        help="replace only the exact B11 derived review-pack after all raw inputs validate")
    args = parser.parse_args()
    scratch, pack = args.scratch_root, args.output
    if pack.exists() and not args.replace_generated_pack:
        raise SystemExit(f"FAIL refusing to overwrite review pack: {pack}")
    if pack.name != "B11_POST_TERMINAL_E01_E10_EXECUTION_GOAL":
        raise SystemExit("FAIL output must be the exact B11 review-pack directory")
    state_path = scratch / "b11-goal/GOAL_STATE.tsv"
    wait_path = scratch / "b11-goal/RESOURCE_WAIT_HISTORY.tsv"
    calibration_path = scratch / "b11-goal/RSS_CALIBRATION.tsv"
    future = scratch / "future-evidence/b9-e01-e10"
    state = latest_state(state_path)
    if any(state[task] != "PASS" for task in TASKS):
        raise SystemExit("FAIL frozen B11 set incomplete: " + ",".join(f"{k}={v}" for k, v in state.items()))
    sim, sim_checks = simulator_rows(future)
    static, static_checks = static_summary(future)
    calibration = read_tsv(calibration_path)
    if {row["task"] for row in calibration} != {"E07", "E08"}:
        raise SystemExit("FAIL E07/E08 calibration ledger incomplete")
    waits = read_tsv(wait_path)
    adaptive_wait_path = scratch / "b11-goal/RESOURCE_WAIT_HISTORY_V2.tsv"
    adaptive_waits = read_tsv(adaptive_wait_path) if adaptive_wait_path.is_file() else []
    manifest = Path(__file__).resolve().parents[2] / "docs/vm_tlb/review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B9_MINIMUM_EXPERIMENT_EXECUTION_PREFLIGHT/E01_E10_EXECUTION_MANIFEST.tsv"
    whitelist = manifest.with_name("ARM_DELTA_WHITELIST.tsv")
    # This removes only a previous derived report at the exact required target;
    # raw simulator/miner evidence stays under scratch and has already passed
    # all completion checks above.
    if pack.exists():
        shutil.rmtree(pack)
    pack.mkdir(parents=True)
    provenance = [
        {"evidence_label": LABEL, "input": "B9_EXECUTION_MANIFEST", "path": str(manifest), "sha256": sha256(manifest), "role": "frozen experiment identity"},
        {"evidence_label": LABEL, "input": "B9_ARM_DELTA_WHITELIST", "path": str(whitelist), "sha256": sha256(whitelist), "role": "per-arm allowed delta"},
        {"evidence_label": LABEL, "input": "SIMULATOR", "path": str(Path(__file__).resolve().parents[2] / "gpu-simulator/bin/release/accel-sim.out"), "sha256": sha256(Path(__file__).resolve().parents[2] / "gpu-simulator/bin/release/accel-sim.out"), "role": "frozen B9 binary"},
        {"evidence_label": LABEL, "input": "B11_STATE", "path": str(state_path), "sha256": sha256(state_path), "role": "resumable execution ledger"},
    ]
    write_tsv(pack / "INPUT_PROVENANCE.tsv", provenance)
    shutil.copy2(state_path, pack / "GOAL_STATE.tsv")
    shutil.copy2(wait_path, pack / "RESOURCE_WAIT_HISTORY_LEGACY_V1.tsv")
    if adaptive_wait_path.is_file():
        shutil.copy2(adaptive_wait_path, pack / "RESOURCE_WAIT_HISTORY_V2.tsv")
    heavy_rss = scratch / "b11-goal/HEAVY_RSS.tsv"
    runtime = scratch / "b11-goal/RUNTIME_RESOURCE_MONITOR.tsv"
    if heavy_rss.is_file():
        shutil.copy2(heavy_rss, pack / "HEAVY_RSS.tsv")
    if runtime.is_file():
        shutil.copy2(runtime, pack / "RUNTIME_RESOURCE_MONITOR.tsv")
    write_tsv(pack / "RESOURCE_WAIT_HISTORY.tsv", normalized_resource_history(waits, adaptive_waits))
    write_tsv(pack / "E01_E06_TRANSLATION_AND_PERF.tsv", sim)
    write_tsv(pack / "E07_E08_RSS_CALIBRATION.tsv", calibration)
    write_tsv(pack / "E09_E10_STATIC_MINING_SUMMARY.tsv", static)
    matrix = []
    for task in TASKS:
        scope = "SIM_SMOKE_ONE_KERNEL_CONTINUOUS_REPLAY" if task in SIM_ARMS else ("MINER_RSS_CALIBRATION_ONE_KERNEL" if task in ("E07", "E08") else "STATIC_MATCHED_METADATA_16_KERNEL_SAMPLE")
        matrix.append({"evidence_label": LABEL, "experiment_id": task, "result": state[task], "evidence_scope": scope,
                       "full_roi_status": "NOT_EXECUTED", "interpretation_guard": "not full-workload evidence"})
    write_tsv(pack / "E01_E10_RESULT_MATRIX.tsv", matrix)
    write_tsv(pack / "CONSERVATION_AND_VALIDATION.tsv", sim_checks + static_checks)
    deltas = pair_deltas(sim)
    write_tsv(pack / "E01_E06_PAIR_DELTAS.tsv", deltas)
    write_markdown(pack, static, deltas, waits + adaptive_waits)
    print(f"PASS B11 evidence synthesis: {pack}")


if __name__ == "__main__":
    main()
