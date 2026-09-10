#!/usr/bin/env python3
"""Close C12 only after the frozen 22-arm matrix has independently passed.

This is a post-processing daemon, not an experiment launcher.  It never edits
Core, a config, a trace, a registration artifact, or a binary.  It watches the
small C12 validation JSON/TSV artifacts emitted by c12_c5_replay.py, reruns that
parser in validation-only mode once the 22 raw logs are terminal, and then emits
the C12 review-pack summaries.  The final explicit git stage deliberately
excludes raw logs, traces, and simulator outputs.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


F = Path("/workspace/worktrees/accel-sim-vm-m4b-speculative")
C = Path("/workspace/worktrees/gpgpu-sim-vm-m4b-speculative")
PACK = F / "docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_C5_FULL_ROI_FAIR_PERFORMANCE"
MATRIX = F / "docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C11_C5_PREFILL_PROVENANCE_CLOSURE/C5_ARM_MATRIX.tsv"
COMMANDS = F / "docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C11_C5_PREFILL_PROVENANCE_CLOSURE/C5_COMMAND_MANIFEST.tsv"
RESOURCE = Path("/workspace/vm-m4b-speculative/c12/RESOURCE_HISTORY_V3_TRUE_SIM.tsv")
OWNER_DIR = Path("/workspace/vm-m4b-speculative/c12/arm_owners")
RUN_ROOT = Path("/workspace/vm-m4b-speculative/c5-results/C11_AUTHORIZED_NOT_RUN")
RUNNER = F / "util/vm_tlb/c12_c5_replay.py"
LATEST = F / "docs/vm_tlb/codex_handoff/spec_m4b/LATEST_REPORT.md"

EXPECTED = 22
CORE = "57bb71ecd015b6ec0ab32e45b0815e5beaf69172"
BINARY = "2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a"
ANCHOR = "d64408a97d76a320a6d49468653d416e33677af8"


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n",
                                extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "NOT_EMITTED") for field in fields})


def identity_ok(row: dict[str, str]) -> bool:
    return (row.get("terminal_status") == "PASS" and row.get("core_head") == CORE and
            row.get("binary_sha256") == BINARY and row.get("framework_anchor") == ANCHOR)


def all_pass(rows: list[dict[str, str]]) -> bool:
    points = {(row.get("roi"), row.get("arm"), row.get("lseg")) for row in rows}
    return len(rows) == EXPECTED and len(points) == EXPECTED and all(identity_ok(row) for row in rows)


def numeric(row: dict[str, str], field: str) -> float | None:
    try:
        return float(row[field])
    except (KeyError, TypeError, ValueError):
        return None


def format_ratio(value: float | None) -> str:
    return "NOT_EMITTED" if value is None else f"{value:.9f}"


COMPARISON_COUNTERS = (
    "vm_l2_tlb_misses", "vm_l2_tlb_port_stalls",
    "vm_translation_mshr_allocations", "vm_translation_mshr_full_events",
    "vm_translation_walk_starts", "vm_pwc_misses", "vm_pte_requests",
    "vm_pte_dram_responses", "vm_pte_memory_wait_cycles_total",
    "vm_translation_requester_latency_cycles_total",
)


def key_for(row: dict[str, str]) -> tuple[str, str, str]:
    return row["roi"], row["arm"], row["lseg"]


def change(candidate: dict[str, str], reference: dict[str, str], field: str) -> str:
    """Candidate-versus-reference percentage; preserve absent telemetry explicitly."""
    c_value = numeric(candidate, field)
    r_value = numeric(reference, field)
    if c_value is None or r_value is None:
        return "NOT_EMITTED"
    if r_value == 0.0:
        return "0.000%" if c_value == 0.0 else "REFERENCE_ZERO"
    return f"{(c_value / r_value - 1.0) * 100.0:+.3f}%"


def comparison_table(title: str, candidate: dict[str, str], reference: dict[str, str]) -> list[str]:
    """Render a factual, multilevel comparison without asserting causality."""
    lines = [f"### {title}", "",
             f"Compared point: `{candidate['roi']} {candidate['arm']} Lseg={candidate['lseg']}` "
             f"against `{reference['roi']} {reference['arm']} Lseg={reference['lseg']}`.", "",
             "| Observable | reference | compared point | compared/reference change |",
             "|---|---:|---:|---:|"]
    fields = ("gpu_tot_sim_cycle", "gpu_tot_ipc", *COMPARISON_COUNTERS)
    for field in fields:
        lines.append("| %s | %s | %s | %s |" %
                     (field, reference.get(field, "NOT_EMITTED"),
                      candidate.get(field, "NOT_EMITTED"), change(candidate, reference, field)))
    lines.extend(["", "Cache / queue / memory summaries (preserved verbatim; interpret only with the numeric "
                  "translation counters above):", "",
                  "| Layer | reference | compared point |", "|---|---|---|"])
    for field in ("l1d_summary", "l2_summary", "l2_queue_summary", "native_memory_latency_summary"):
        lines.append("| %s | %s | %s |" % (field, reference.get(field, "NOT_EMITTED"),
                                                candidate.get(field, "NOT_EMITTED")))
    lines.extend(["", "Interpretation boundary: this is a measured association across TLB, MSHR/PTW/PWC/PTE, requester, "
                  "cache/queue, and memory observables; it does not alone establish a unique causal bottleneck.", ""])
    return lines


def emit_comparison_analysis(rows: list[dict[str, str]]) -> None:
    """Emit every Gate-G comparison directly from the validated result matrix.

    The text is deliberately mechanical: it preserves the required cross-layer
    observables but makes no unvalidated architectural-causality claim.
    """
    by_key = {key_for(row): row for row in rows}
    lines = ["# C12 required fair-comparison analysis", "",
             "Labels: `MEASURED_FULL_ROI_FACT`, `SPECULATIVE_CANDIDATE`, "
             "`REFERENCE_APPROX_SUBENTRY_16`.", "",
             "All percentages are the compared-point value divided by the named reference minus one. "
             "Cycles/IPC are reported with the raw counters; formal speedup remains same-ROI F0 only.", "",
             "## MEASURED_FULL_ROI_FACT", ""]
    for roi in ("prefill", "decode1"):
        f0 = by_key[(roi, "F0", "NONE")]
        lines.extend(comparison_table(f"{roi}: F1 versus F2", by_key[(roi, "F1", "NONE")],
                                      by_key[(roi, "F2", "NONE")]))
        lines.extend(comparison_table(f"{roi}: F5 versus F0", by_key[(roi, "F5", "NONE")], f0))
        lines.extend(comparison_table(f"{roi}: F7 Lseg=10 versus F0", by_key[(roi, "F7", "10")], f0))
        lines.extend(comparison_table(f"{roi}: F8 Lseg=10 versus F9", by_key[(roi, "F8", "10")],
                                      by_key[(roi, "F9", "NONE")]))
        lines.extend(comparison_table(f"{roi}: F8 Lseg=10 versus F1", by_key[(roi, "F8", "10")],
                                      by_key[(roi, "F1", "NONE")]))
        for family in ("F7", "F8"):
            lines.extend([f"### {roi}: {family} Lseg sensitivity (L5 / L10 / L20)", "",
                          "| Lseg | cycles | same-ROI F0 speedup | Segment attempts | Segment hits | Segment L2 suppressed |",
                          "|---:|---:|---:|---:|---:|---:|"])
            for lseg in ("5", "10", "20"):
                row = by_key[(roi, family, lseg)]
                f0_cycles = numeric(f0, "gpu_tot_sim_cycle")
                cycles = numeric(row, "gpu_tot_sim_cycle")
                speed = format_ratio(f0_cycles / cycles if f0_cycles is not None and cycles not in (None, 0.0) else None)
                lines.append("| %s | %s | %s | %s | %s | %s |" %
                             (lseg, row.get("gpu_tot_sim_cycle"), speed,
                              row.get("segment_lookup_attempts", "NOT_EMITTED"),
                              row.get("segment_hits", "NOT_EMITTED"),
                              row.get("segment_l2_suppressed", "NOT_EMITTED")))
            lines.append("")
    lines.extend(["## Prefill versus Decode1", "",
                  "Absolute cycles are not cross-ROI comparable because Prefill and Decode1 have different immutable "
                  "kernel lists. This table compares each arm's *same-ROI F0-normalized* speedup and preserves the "
                  "relevant translation signal.", "",
                  "| arm | lseg | Prefill speedup vs Prefill F0 | Decode1 speedup vs Decode1 F0 | Prefill L2 TLB misses | Decode1 L2 TLB misses | Prefill PTE requests | Decode1 PTE requests |",
                  "|---|---|---:|---:|---:|---:|---:|---:|"])
    for arm, lseg in sorted({(row["arm"], row["lseg"]) for row in rows}):
        prefill = by_key[("prefill", arm, lseg)]
        decode = by_key[("decode1", arm, lseg)]
        pf0 = numeric(by_key[("prefill", "F0", "NONE")], "gpu_tot_sim_cycle")
        df0 = numeric(by_key[("decode1", "F0", "NONE")], "gpu_tot_sim_cycle")
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" %
                     (arm, lseg,
                      format_ratio(pf0 / numeric(prefill, "gpu_tot_sim_cycle") if pf0 is not None and numeric(prefill, "gpu_tot_sim_cycle") not in (None, 0.0) else None),
                      format_ratio(df0 / numeric(decode, "gpu_tot_sim_cycle") if df0 is not None and numeric(decode, "gpu_tot_sim_cycle") not in (None, 0.0) else None),
                      prefill.get("vm_l2_tlb_misses", "NOT_EMITTED"), decode.get("vm_l2_tlb_misses", "NOT_EMITTED"),
                      prefill.get("vm_pte_requests", "NOT_EMITTED"), decode.get("vm_pte_requests", "NOT_EMITTED")))
    lines.extend(["", "## SUPPORTED_MECHANISM_SIGNAL", "",
                  "The tables intentionally require concordant variation in TLB, MSHR/PTW/PWC/PTE, requester and "
                  "cache/queue/memory observables before describing a mechanism signal. They do not treat a miss-rate, "
                  "IPC, queue, or Segment counter in isolation as causal proof.", "",
                  "## UNRESOLVED", "",
                  "`REFERENCE_APPROX_SUBENTRY_16` remains a reference approximation. `SPECULATIVE_CANDIDATE` and "
                  "`MODELED_DRIVER_PA` remain modeled simulator constructs, not a proof of a fabricated hardware PPA "
                  "or of real-hardware PA behavior.", ""])
    (PACK / "COMPARISON_ANALYSIS.md").write_text("\n".join(lines))


def owner_sidecar(row: dict[str, str]) -> dict[str, str]:
    suffix = row["arm"].lower()
    if row["lseg"] != "NONE":
        suffix += "_lseg" + row["lseg"]
    path = OWNER_DIR / (row["roi"] + "__" + suffix + ".json")
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text())
        return {key: str(value) for key, value in raw.items()}
    except (OSError, TypeError, ValueError):
        return {}


def validation_sidecar(row: dict[str, str]) -> dict[str, Any]:
    """Read immutable per-arm validation metadata not carried by ARM_RESULTS.

    ARM_RESULTS intentionally stays compact and omits run_dir.  The C12 run
    root/arm naming is frozen by the manifest, so derive it deterministically
    rather than treating the missing TSV presentation field as lost evidence.
    """
    try:
        suffix = row["arm"].lower()
        if row["lseg"] != "NONE":
            suffix += "_lseg" + row["lseg"]
        return json.loads((RUN_ROOT / row["roi"] / suffix / "C12_ARM_VALIDATION.json").read_text())
    except (KeyError, OSError, TypeError, ValueError):
        return {}


def emit_early_promotion_audit(rows: list[dict[str, str]]) -> bool:
    """Close the aggressive-addendum baseline promotion gate explicitly.

    F0 is a global C12 baseline gate: early independent arms become formal PASS
    only if both F0 identity records pass and every arm's own immutable result
    gate has passed.  The lock owner sidecar records the one legal launcher
    owner; the raw checksum and validation JSON record the immutable outcome.
    """
    f0_rows = {row["roi"]: row for row in rows if row["arm"] == "F0"}
    # ARM_RESULTS deliberately contains only result-table fields.  The
    # validation timestamp belongs to each immutable sidecar, so read it
    # there rather than treating an absent TSV column as a failed baseline.
    global_f0_time = max(str(validation_sidecar(f0_rows["prefill"]).get("validated_utc", "")),
                         str(validation_sidecar(f0_rows["decode1"]).get("validated_utc", "")))
    fields = ["roi", "arm", "lseg", "owner_pid", "owner_start_time", "baseline_gate_utc",
              "early_before_both_f0", "f0_identity_match", "arm_terminal_gate", "raw_log_bound",
              "single_owner_evidence", "promotion_decision", "detail"]
    audit: list[dict[str, Any]] = []
    okay = True
    for row in sorted((item for item in rows if item["arm"] != "F0"), key=key_for):
        owner = owner_sidecar(row)
        started = owner.get("start_time", "")
        early = bool(started and global_f0_time and started < global_f0_time)
        f0 = f0_rows[row["roi"]]
        f0_identity = all(row.get(field) == f0.get(field) == expected
                          for field, expected in (("framework_anchor", ANCHOR),
                                                  ("core_head", CORE),
                                                  ("binary_sha256", BINARY),
                                                  ("trace_sha256", f0.get("trace_sha256", "")),
                                                  ("registration_sha256", f0.get("registration_sha256", ""))))
        run_validation = validation_sidecar(row)
        arm_gate = (row.get("terminal_status") == "PASS" and
                    run_validation.get("simulator_exit") == "0" and
                    row.get("kernel_markers") == ("692" if row["roi"] == "prefill" else "740") and
                    row.get("telemetry_records") == ("692" if row["roi"] == "prefill" else "740") and
                    run_validation.get("object_conservation_pass") == "1" and
                    run_validation.get("pte_conservation_pass") == "PASS")
        raw_bound = bool(row.get("raw_log_sha256") and row.get("raw_log_sha256") != "MISSING")
        owner_ok = (owner.get("schema") == "C12_ARM_OWNER_V1" and bool(owner.get("owner_pid")) and
                    bool(owner.get("lock_path")))
        if early:
            promoted = f0_identity and arm_gate and raw_bound and owner_ok
            decision = "PROMOTED_PASS" if promoted else "QUARANTINE_REQUIRED"
            okay = okay and promoted
        else:
            decision = "NOT_EARLY_FORMAL_PASS" if f0_identity and arm_gate and raw_bound else "POST_F0_GATE_FAILURE"
            okay = okay and decision == "NOT_EARLY_FORMAL_PASS"
        audit.append({"roi": row["roi"], "arm": row["arm"], "lseg": row["lseg"],
                      "owner_pid": owner.get("owner_pid", "MISSING"), "owner_start_time": started or "MISSING",
                      "baseline_gate_utc": global_f0_time or "MISSING", "early_before_both_f0": str(early),
                      "f0_identity_match": "PASS" if f0_identity else "FAIL",
                      "arm_terminal_gate": "PASS" if arm_gate else "FAIL",
                      "raw_log_bound": "PASS" if raw_bound else "FAIL",
                      "single_owner_evidence": "PASS" if owner_ok else "FAIL",
                      "promotion_decision": decision,
                      "detail": "C12_ADDENDUM_PROMOTION_AUDIT"})
    write_tsv(PACK / "EARLY_EXECUTION_PROMOTION_AUDIT.tsv", fields, audit)
    return okay


def emit_summaries(rows: list[dict[str, str]]) -> None:
    ordered = sorted(rows, key=lambda row: (row["roi"], row["arm"], row["lseg"]))
    f0 = {row["roi"]: numeric(row, "gpu_tot_sim_cycle") for row in ordered if row["arm"] == "F0"}
    speed: list[dict[str, Any]] = []
    for row in ordered:
        cycles = numeric(row, "gpu_tot_sim_cycle")
        base = f0.get(row["roi"])
        speed.append({"roi": row["roi"], "arm": row["arm"], "lseg": row["lseg"],
                      "cycles": row.get("gpu_tot_sim_cycle"), "instructions": row.get("gpu_tot_sim_insn"),
                      "ipc": row.get("gpu_tot_ipc"), "speedup_vs_same_roi_f0":
                      format_ratio(base / cycles if base is not None and cycles not in (None, 0.0) else None),
                      "baseline": f"{row['roi']}:F0:NONE"})
    write_tsv(PACK / "SPEEDUP_SUMMARY.tsv",
              ["roi", "arm", "lseg", "cycles", "instructions", "ipc", "speedup_vs_same_roi_f0", "baseline"], speed)

    mechanism_fields = ["vm_l1_tlb_accesses", "vm_l1_tlb_hits", "vm_l1_tlb_misses",
                        "vm_l2_tlb_accesses", "vm_l2_tlb_hits", "vm_l2_tlb_misses",
                        "vm_l2_tlb_evictions", "vm_l2_tlb_port_stalls",
                        "vm_translation_mshr_allocations", "vm_translation_mshr_merges",
                        "vm_translation_mshr_full_events", "vm_translation_walk_starts",
                        "vm_pwc_accesses", "vm_pwc_hits", "vm_pwc_misses",
                        "vm_pte_requests", "vm_pte_responses", "vm_pte_dram_responses",
                        "segment_lookup_attempts", "segment_hits", "segment_l2_suppressed",
                        "subentry_hits", "subentry_misses"]
    mechanism = [{"roi": row["roi"], "arm": row["arm"], "lseg": row["lseg"],
                  **{field: row.get(field, "NOT_EMITTED") for field in mechanism_fields}}
                 for row in ordered]
    write_tsv(PACK / "TRANSLATION_MECHANISM_SUMMARY.tsv", ["roi", "arm", "lseg", *mechanism_fields], mechanism)

    sensitivity = [{"roi": row["roi"], "family": row["arm"], "lseg": row["lseg"],
                    "cycles": row.get("gpu_tot_sim_cycle"), "speedup_vs_same_roi_f0":
                    next(item["speedup_vs_same_roi_f0"] for item in speed if item["roi"] == row["roi"] and
                         item["arm"] == row["arm"] and item["lseg"] == row["lseg"]),
                    "segment_attempts": row.get("segment_lookup_attempts"),
                    "segment_hits": row.get("segment_hits"),
                    "segment_l2_suppressed": row.get("segment_l2_suppressed")}
                   for row in ordered if row["arm"] in ("F7", "F8")]
    write_tsv(PACK / "LSEG_SENSITIVITY.tsv", ["roi", "family", "lseg", "cycles", "speedup_vs_same_roi_f0",
                                                "segment_attempts", "segment_hits", "segment_l2_suppressed"], sensitivity)

    cross_fields = ["vm_translation_requester_mshr_wait_cycles_total",
                    "vm_translation_requester_latency_cycles_total", "vm_pte_memory_wait_cycles_total",
                    "l1d_summary", "l2_summary", "l2_queue_summary", "native_memory_latency_summary",
                    "object_conservation_pass", "pte_conservation_pass"]
    cross = [{"roi": row["roi"], "arm": row["arm"], "lseg": row["lseg"],
              **{field: row.get(field, "NOT_EMITTED") for field in cross_fields}}
             for row in ordered]
    write_tsv(PACK / "CROSS_LAYER_SUMMARY.tsv", ["roi", "arm", "lseg", *cross_fields], cross)

    provenance_fields = ["framework_anchor", "core_head", "binary_sha256", "config_sha256",
                         "trace_sha256", "registration_sha256", "charged_bits", "raw_log_sha256",
                         "kernel_markers", "telemetry_records", "peak_rss_kb", "elapsed_seconds",
                         "terminal_status"]
    provenance = [{"roi": row["roi"], "arm": row["arm"], "lseg": row["lseg"],
                   **{field: row.get(field, "NOT_EMITTED") for field in provenance_fields}}
                  for row in ordered]
    write_tsv(PACK / "PROVENANCE_MATRIX.tsv", ["roi", "arm", "lseg", *provenance_fields], provenance)

    emit_comparison_analysis(ordered)

    write_tsv(PACK / "RESOURCE_HISTORY.tsv", list(read_tsv(RESOURCE)[0].keys()) if RESOURCE.is_file() and read_tsv(RESOURCE) else ["note"],
              read_tsv(RESOURCE) if RESOURCE.is_file() else [{"note": "RESOURCE_HISTORY_MISSING"}])

    readme = ["# C12 C5 full-ROI fair performance replay", "",
              "状态：`C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW`。", "",
              "该 review pack 保存冻结 C11 identity 下 22/22 C5 full-ROI arms 的小型、可提交结果；原始 "
              "simulator logs 和 traces 留在工作区结果根，`RAW_LOG_INDEX.tsv` 将每项与 SHA-256 绑定。", "",
              "性能比较仅限同 ROI 的 C5 F0。所有 arms 共用每 ROI 的 `MODELED_DRIVER_PA`、Core、binary、trace "
              "list 和 registration；不同 identity 的数值不得混合。", "",
              "推荐阅读顺序：`FINAL_REPORT.md` → `COMPARISON_ANALYSIS.md` → "
              "`EARLY_EXECUTION_PROMOTION_AUDIT.tsv` → `ARM_STATUS.tsv` → `SPEEDUP_SUMMARY.tsv` → "
              "`TRANSLATION_MECHANISM_SUMMARY.tsv` → `CROSS_LAYER_SUMMARY.tsv` → `PROVENANCE_MATRIX.tsv` → "
              "`RAW_LOG_INDEX.tsv`。", "",
              "标签保持：`SPECULATIVE_CANDIDATE`；F1/F8 保持 `REFERENCE_APPROX_SUBENTRY_16`。F6、KV "
              "segmentation、12K、M5 和 Window A/B 均不在本轮范围内。"]
    (PACK / "README.md").write_text("\n".join(readme) + "\n")

    facts = ["# C12 / C5 paper-facing findings", "",
             "## MEASURED_FULL_ROI_FACT", "",
             "- 22/22 frozen C5 arms terminally passed the parser/conservation contract.",
             "- All reported speedups are relative only to the same-ROI C5 F0 baseline in `SPEEDUP_SUMMARY.tsv`.",
             "- Full counters are preserved in `ARM_RESULTS.tsv`, `TRANSLATION_MECHANISM_SUMMARY.tsv`, and `CROSS_LAYER_SUMMARY.tsv`.",
             "", "## SUPPORTED_MECHANISM_SIGNAL", "",
             "- Any mechanism interpretation must be based on concordant TLB, MSHR/PTW/PWC/PTE, requester, cache/queue, and DRAM telemetry; no single counter is causal proof.",
             "", "## UNRESOLVED", "",
             "- `REFERENCE_APPROX_SUBENTRY_16` remains a speculative reference approximation.",
             "- `SPECULATIVE_CANDIDATE` and modeled driver-PA semantics do not establish a fabricated hardware cost or causal optimum."]
    (PACK / "PAPER_FACING_FINDINGS.md").write_text("\n".join(facts) + "\n")

    report = ["# C12 C5 full-ROI fair performance replay", "",
              "Status: `C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW`", "",
              "- primary matrix: 22/22 terminal PASS", f"- Core: `{CORE}`", f"- binary SHA-256: `{BINARY}`",
              f"- functional/config anchor: `{ANCHOR}`", "- labels: `SPECULATIVE_CANDIDATE`, `REFERENCE_APPROX_SUBENTRY_16`", "",
              "All numerical comparison tables are machine-readable in the accompanying TSV files.  The report intentionally does not infer causality from a single telemetry counter.",
              "", "## Required comparison coverage", "",
              "- F1 vs F2: `COMPARISON_ANALYSIS.md` + `TRANSLATION_MECHANISM_SUMMARY.tsv`", 
              "- F5 vs F0: `COMPARISON_ANALYSIS.md` + `CROSS_LAYER_SUMMARY.tsv`",
              "- F7 L5/L10/L20 and F8 L5/L10/L20: `COMPARISON_ANALYSIS.md` + `LSEG_SENSITIVITY.tsv`",
              "- F8-L10 vs F9 / F1 and Prefill vs Decode: `COMPARISON_ANALYSIS.md`.",
              "", "`COMPARISON_ANALYSIS.md` mechanically presents the required multi-layer deltas while keeping measured facts, supported mechanism signals, and unresolved questions separate."]
    (PACK / "FINAL_REPORT.md").write_text("\n".join(report) + "\n")
    LATEST.write_text("# Window C — SPECULATIVE M4B DEVELOPMENT current handoff\n\n"
                      "Status: `C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW` / "
                      "`SPECULATIVE_CANDIDATE` / `REFERENCE_APPROX_SUBENTRY_16`.\n\n"
                      "C12 completed the frozen 22-arm C5 full-ROI fair matrix.  The authoritative "
                      "review artifacts are in `docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/"
                      "C12_C5_FULL_ROI_FAIR_PERFORMANCE/`; use its `FINAL_REPORT.md`, provenance matrix, "
                      "speedup summary, mechanism tables, and raw-log index together.  Speedups are "
                      "only relative to same-ROI C5 F0 baselines.\n")


def terminal_status(rows: list[dict[str, str]]) -> str:
    if len(rows) == EXPECTED and all_pass(rows):
        return "READY"
    failures = [row for row in rows if row.get("terminal_status") not in ("PASS", "PENDING")]
    if failures:
        (PACK / "FINALIZER_FAILURE_SNAPSHOT.json").write_text(json.dumps(failures, indent=2, sort_keys=True) + "\n")
        return "FAILED_ARM_NEEDS_DIAGNOSIS"
    return "WAITING_FOR_22_TERMINAL_ARMS"


def validate_all() -> int:
    command = [sys.executable, str(RUNNER), "--framework", str(F), "--core", str(C), "--matrix", str(MATRIX),
               "--commands", str(COMMANDS), "--review-pack", str(PACK), "--resource-history", str(RESOURCE), "--validate"]
    return subprocess.run(command, check=False).returncode


def write_state(status: str, detail: str = "") -> None:
    (PACK / "C12_FINALIZER_STATE.json").write_text(json.dumps({"utc": utc(), "status": status, "detail": detail},
                                                                 indent=2, sort_keys=True) + "\n")


def git_closeout() -> None:
    # Explicit paths only: never stage raw output, traces, an unrelated user
    # edit, or the mutable finalizer heartbeat.  The latter is deliberately
    # excluded so that the post-push COMMITTED_AND_PUSHED state cannot leave a
    # tracked worktree modification behind.
    pack_root = "docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_C5_FULL_ROI_FAIR_PERFORMANCE/"
    required_pack_files = [
        "README.md", "ARM_STATUS.tsv", "ARM_RESULTS.tsv", "RAW_LOG_INDEX.tsv",
        "FAILURE_RETRY_AUDIT.md", "SPEEDUP_SUMMARY.tsv", "TRANSLATION_MECHANISM_SUMMARY.tsv",
        "LSEG_SENSITIVITY.tsv", "CROSS_LAYER_SUMMARY.tsv", "PROVENANCE_MATRIX.tsv",
        "RESOURCE_HISTORY.tsv", "PAPER_FACING_FINDINGS.md", "FINAL_REPORT.md",
        "COMPARISON_ANALYSIS.md", "EARLY_EXECUTION_PROMOTION_AUDIT.tsv", "C12_LIVE_ARM_STATE.tsv",
    ]
    paths = ["util/vm_tlb/c12_c5_replay.py", "util/vm_tlb/c12_c5_scheduler.py", "util/vm_tlb/c12_c5_finalize.py",
             *(pack_root + name for name in required_pack_files),
             "docs/vm_tlb/codex_handoff/spec_m4b/LATEST_REPORT.md"]
    staged = subprocess.run(["git", "-C", str(F), "diff", "--cached", "--quiet"], check=False)
    if staged.returncode != 0:
        raise RuntimeError("refusing to commit pre-existing staged changes")
    subprocess.run(["git", "-C", str(F), "add", "-f", *paths], check=True)
    subprocess.run(["git", "-C", str(F), "commit", "-m", "C12: close 22-arm C5 fair replay"], check=True)
    subprocess.run(["git", "-C", str(F), "push", "origin", "hrl/vm-m4b-speculative-v0"], check=True)


def finalize_once() -> int:
    results = PACK / "ARM_RESULTS.tsv"
    if not results.is_file():
        write_state("WAITING_FOR_RESULTS")
        return 0
    rows = read_tsv(results)
    status = terminal_status(rows)
    write_state(status)
    if status != "READY":
        return 0 if status.startswith("WAITING") else 2
    if validate_all() != 0:
        write_state("FINAL_PARSER_AUDIT_FAILED")
        return 2
    rows = read_tsv(results)
    if not all_pass(rows):
        write_state("POST_AUDIT_MATRIX_NOT_PASS")
        return 2
    if not emit_early_promotion_audit(rows):
        write_state("EARLY_EXECUTION_PROMOTION_AUDIT_FAILED")
        return 2
    emit_summaries(rows)
    write_state("REVIEW_PACK_EMITTED")
    try:
        git_closeout()
    except (RuntimeError, subprocess.CalledProcessError) as error:
        write_state("REVIEW_PACK_EMITTED_PUSH_OR_COMMIT_FAILED", str(error))
        return 3
    write_state("COMMITTED_AND_PUSHED")
    return 0


def main() -> int:
    once = "--once" in sys.argv[1:]
    while True:
        code = finalize_once()
        state = json.loads((PACK / "C12_FINALIZER_STATE.json").read_text()).get("status")
        if once or state == "COMMITTED_AND_PUSHED":
            return code
        # A terminal arm can be temporarily FAILED_DIAGNOSING solely because
        # its raw log awaits a parser-only revalidation.  Keep this lightweight
        # supervisor alive so a later atomic collector update is observed;
        # simulator execution is never owned or signalled here.  A genuine
        # closeout/commit failure (code 3) still exits for explicit repair.
        if code not in (0, 2):
            return code
        if state == "COMMITTED_AND_PUSHED":
            return 0
        time.sleep(60)


if __name__ == "__main__":
    raise SystemExit(main())
