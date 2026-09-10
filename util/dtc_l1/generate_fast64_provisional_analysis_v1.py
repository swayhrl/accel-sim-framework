#!/usr/bin/env python3
"""Emit non-promoting FAST64.3/4 preliminary evidence tables."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "docs/dtc_l1/fast64/generated"
FORMAL_REPAIRED_CORE = "95ccdb7a056f2d53f740d90869785cac6d4ee0f5"


def rows():
    for path in GEN.rglob("*.json"):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        metrics, provenance = value.get("metrics", {}), value.get("provenance", {})
        if value.get("schema") != "dtc_l1_summary_v1" or metrics.get("DTC_L1_mode") not in {"PAPER_BASE", "PAPER_IO", "PAPER_OO"}:
            continue
        # FAST64.6 sensitivity acquisition is permitted to run ahead of the
        # Stage3/4 logical gates, but it is never a Stage4 primary candidate.
        # Do not let a same-workload/mode physical point create a duplicate
        # candidate or replace the frozen primary configuration in these
        # preliminary (and explicitly nonpromoting) aggregates.
        if provenance.get("config_id", "").startswith("FAST64_SENS_"):
            continue
        attempt = value.get("immutable_attempt", {})
        if not attempt.get("terminal_receipt_sha256"):
            continue
        yield path, value


def value(metrics, key):
    return metrics.get(key, "NA")


def drained(metrics):
    occupancy = metrics.get(
        "DTC_L1_pib_occupancy",
        metrics.get("DTC_L1_io_pib_occupancy", metrics.get("DTC_L1_oo_pib_occupancy")),
    )
    inflight = metrics.get("DTC_L1_io_inflight_current", metrics.get("DTC_L1_oo_inflight_current", 0))
    active_refs = metrics.get("DTC_L1_oo_active_refs", 0)
    return (metrics.get("DTC_L1_lower_outstanding") == 0 and occupancy == 0 and
            inflight == 0 and active_refs == 0)


def main():
    evidence = list(rows())
    groups = defaultdict(list)
    for path, record in evidence:
        p, m = record["provenance"], record["metrics"]
        group = (p.get("workload_id"), p.get("core_sha"), p.get("runtime_binary_sha256"), p.get("observer_overlay_sha256"), p.get("framework_sha"), record.get("external_artifacts", {}).get("trace_list_sha256"))
        groups[group].append((path, record))

    triplets = ["schema\tFAST64_PROVISIONAL_STAGE4_TRIPLETS_V1", "status\tPRELIMINARY_NONPROMOTING", "workload\tcore_sha\truntime_sha256\tobserver_sha256\tframework_sha\tpayload_sha256\tbase_candidates\tio_candidates\too_candidates\tinstruction_identity\tterminal_drain\tidentity_status"]
    speedup = ["schema\tFAST64_PROVISIONAL_STAGE4_SPEEDUP_V1", "status\tPRELIMINARY_NONPROMOTING_NO_GM", "workload\tcore_sha\tbase_cycles\tio_cycles\too_cycles\tspeedup_io\tspeedup_oo\tstatus"]
    for key, records in sorted(groups.items()):
        workload, core, runtime, observer, framework, payload = key
        by_mode = defaultdict(list)
        for path, record in records:
            by_mode[record["metrics"]["DTC_L1_mode"]].append((path, record))
        counts = [len(by_mode[mode]) for mode in ("PAPER_BASE", "PAPER_IO", "PAPER_OO")]
        selected = [by_mode[mode][0][1] if len(by_mode[mode]) == 1 else None for mode in ("PAPER_BASE", "PAPER_IO", "PAPER_OO")]
        if all(selected):
            insns = [r["metrics"].get("gpu_tot_sim_insn") for r in selected]
            drain = all(drained(r["metrics"]) for r in selected)
            # The zero-access repair map authorizes literal historical-Core
            # reuse only for source-inert Base evidence.  It does not make an
            # old-Core IO/OO pair equivalent to repaired-Core IO/OO.  Keep
            # such complete historical triplets visible, but never permit a
            # preliminary speedup candidate or downstream promotion from them.
            if core != FORMAL_REPAIRED_CORE:
                identity = "HISTORICAL_CORE_NONPROMOTING"
            else:
                identity = "COMMON_IDENTITY_CANDIDATE" if len(set(insns)) == 1 and drain else "REVIEW_REQUIRED"
            cycles = [r["metrics"].get("gpu_tot_sim_cycle") for r in selected]
            if identity == "COMMON_IDENTITY_CANDIDATE" and all(isinstance(x, int) and x > 0 for x in cycles):
                speedup.append("\t".join(map(str, (workload, core, cycles[0], cycles[1], cycles[2], f"{cycles[0]/cycles[1]:.6f}", f"{cycles[0]/cycles[2]:.6f}", "PRELIMINARY_CANDIDATE"))))
        else:
            insns, drain, identity = [], False, "INCOMPLETE_OR_MULTIPLE_CANDIDATES"
        triplets.append("\t".join(map(str, (workload, core, runtime, observer, framework, payload, *counts, "COMMON" if selected and len(set(insns)) == 1 else "PENDING", "PASS" if drain else "PENDING", identity))))

    structural = ["schema\tFAST64_PROVISIONAL_STAGE3_STRUCTURAL_V1", "status\tPRELIMINARY_NONPROMOTING", "workload\tsource_summary\tcycles\tinstructions\tpib_full\tcacheline_reserved\tmshr_entry_full\tmshr_merge_full\tdownstream_full\ttag_conflicts\tlower_acquired\tlower_released\tterminal_pib\tterminal_lower"]
    for path in sorted(GEN.rglob("FAST64_3_*_BASE_STRUCTURAL_METRICS_V1.json")):
        try:
            item = json.loads(path.read_text(encoding="utf-8")); m = item.get("metrics", {})
        except (OSError, json.JSONDecodeError):
            continue
        workload = path.name.removeprefix("FAST64_3_").removesuffix("_BASE_STRUCTURAL_METRICS_V1.json").replace("_", "-")
        structural.append("\t".join(map(str, (workload, item.get("source_summary", "NA"), value(m, "cycles"), value(m, "instructions"), value(m, "pib_full_events"), value(m, "cacheline_all_lines_reserved_events"), value(m, "mshr_entry_full_events"), value(m, "mshr_merge_full_events"), value(m, "miss_queue_downstream_full_events"), value(m, "tag_bank_conflicts"), value(m, "live_miss_lower_acquired"), value(m, "live_miss_lower_released"), value(m, "terminal_pib_occupancy"), value(m, "terminal_lower_outstanding")))))

    (GEN / "provisional_stage4_triplets.tsv").write_text("\n".join(triplets) + "\n", encoding="utf-8")
    (GEN / "provisional_stage4_speedup.tsv").write_text("\n".join(speedup) + "\n", encoding="utf-8")
    (GEN / "provisional_stage3_structural.tsv").write_text("\n".join(structural) + "\n", encoding="utf-8")
    print(f"FAST64_PROVISIONAL_ANALYSIS_V1_WRITTEN\trows={len(evidence)}\tgroups={len(groups)}")


if __name__ == "__main__":
    main()
