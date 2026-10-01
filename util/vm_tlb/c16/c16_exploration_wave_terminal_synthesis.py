#!/usr/bin/env python3
"""Build the CPU-only terminal synthesis for the C16 AI-workload wave."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path


PACK = "docs/vm_tlb/review_packs/C16_AI_WORKLOAD_EXPLORATION_WAVE_TERMINAL_SYNTHESIS_174NEW_V1"
AUTHORITIES = {
    "e1_shared": ("1e701f013fc174b5b4df9febb5c33500f9ea586e", "baf96db27ec7d15aecaa4c44261ade08c2d3b4db", "docs/vm_tlb/review_packs/C16_E1_SHARED_RESIDENCY_FEASIBILITY_109_V1"),
    "e1_operator": ("eae1cc4d831ae8459da558cf1358bb8daf8d76e6", "901247e13618af53057e4c557a3be0bcf63a647f", "docs/vm_tlb/review_packs/C16_E1_OPERATOR_FAMILY_EXPANSION_109_V1"),
    "m1": ("71324d46435293edab3b7a0ff6ee999e675be0d0", "9d022115e0407eceb145e4f6f6dc69b1907f865f", "docs/vm_tlb/review_packs/C16_E1_ORACLE_ELASTIC_B16_REUSE_PERFORMANCE_CANARY_174NEW_V1"),
    "m1_review": ("f6ce663e2a2d6759050ee6f5b0e2cf42bc9f243b", "95e8a91876ff905200b8d95cc179b37265f45c9f", "docs/vm_tlb/review_packs/C16_E1_LANE4_TERMINAL_REVIEW_V1"),
    "m1f": ("5f7a2b831d87606c693c29934bb520b8ccf02d43", "ff12b8af5dc0db47bab86e894e2cb593927ffba7", "docs/vm_tlb/review_packs/C16_E1_M1F_HEADROOM_ADMISSION_174NEW_V1"),
    "split_threshold": ("6d226cd99946d3bd7b41c5ee005285183efbb915", "656a7e28ac007f93148eac13c36a8720cd885bde", "docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_THRESHOLD_CONSUMER_174NEW_V1"),
    "crossm": ("2113422f7e6b7e5a851469511d26a9ddf7123d4e", "2bdde15291a0f221a9ee4aad15cbbd3f494d96b8", "docs/vm_tlb/review_packs/C16_SPLITK_CROSSM_REUSE_CAUSAL_CONSUMER_174NEW_V1"),
    "grouped": ("e7855278076c7e0360d39b18424cc8f048f51da5", "709cfdda397a89c9cef9ed781d6105938eb0653b", "docs/vm_tlb/review_packs/C16_SPLITK_GROUPED_CTA_BASELINE_CONSUMER_174NEW_V1"),
    "residual_native": ("ab84399012c89fce2c21fabac8d6f9fa8688d164", "dd7b4a5dfa7082c54057584177c2b864f197e88e", "docs/vm_tlb/review_packs/C16_GROUPED_RESIDUAL_PARALLELISM_NATIVE_109_V1"),
    "residual_consumer": ("a3a36e64ae4a3a316df2bf4dfc9cac95caf8e164", "ec0783b5d39c129c986e20c6e5aecfa0a0756921", "docs/vm_tlb/review_packs/C16_GROUPED_RESIDUAL_PARALLELISM_CONSUMER_174NEW_V1"),
    "conversion": ("9ff9e9b3580d8d24a56c8d3beebc41e9f4975f47", "dc77a6ae1fc3867ccb80474f753bc6f7a0a9a954", "docs/vm_tlb/review_packs/C16_LOWBIT_CONVERSION_REUSE_HEADROOM_174NEW_V1"),
    "conversion_native": ("797477f2c7f365bac1930808125957a8c06af091", "8aa7568ba46aca9432165fc7751f04521b52ad14", "docs/vm_tlb/review_packs/C16_LOWBIT_CONVERSION_NATIVE_HEADROOM_ORACLE_109_V1"),
    "ffn_timeline": ("071297ae7f4aa772a27fae0cf31ad47ab7d967be", "1e6a4f5ed19dfc76f91795524a29ac652156c653", "docs/vm_tlb/review_packs/C16_FFN_TIMELINE_AUTHORITY_CAPTURE_109_V1"),
    "ffn_headroom": ("30b3016a7ad5b5ef86a3494c784e072938dee6c5", "b111d2147d2aa4d8656695aa321b7c31517e1927", "docs/vm_tlb/review_packs/C16_FFN_TIMELINE_HEADROOM_QUALIFICATION_174NEW_V2"),
    "merged_guard": ("3c3f667bbab8f3ae227dc3bc8eaa6c642b97a453", "e4be7386c697b33e4f429b833216fdb0bd65f17d", "docs/vm_tlb/review_packs/C16_MERGED_GATE_UP_STRONG_BASELINE_GUARD_174NEW_V1"),
    "merged_native": ("6c92e9cd868df48594f1c80f8f2294e404af6933", "128468f3e4825b8375685eeb1cea804fefcaac97", "docs/vm_tlb/review_packs/C16_MERGED_GATE_UP_NATIVE_STRONG_BASELINE_109_V1"),
    "two_stream_v1": ("ef517d8e5a0e3659abe71b49beeba1559cd5f2ce", "12b002aeb3376a340ac15f848e1e97b3d52a5937", "docs/vm_tlb/review_packs/C16_FFN_GATE_UP_CONCURRENCY_NATIVE_DIAGNOSTIC_109_V1"),
    "two_stream_repair": ("ee8cadd4a9a0be31186fcc0bdc8fb47dd515dbf8", "44fcf5e689125061a3a80bcb677a8a5292a68a32", "docs/vm_tlb/review_packs/C16_FFN_TWO_STREAM_CORRECTNESS_ROOT_CAUSE_AND_REPAIR_174NEW_V2"),
    "two_stream_v2": ("e8a2553f5c7a9861ddd2a31ae50e79e79d78d3a7", "9671f56fcbd80562a862ae44858459e0a1c69dca", "docs/vm_tlb/review_packs/C16_FFN_GATE_UP_CONCURRENCY_NATIVE_DIAGNOSTIC_109_V2"),
    "ada": ("5a8bcd63638847c0f2a0951046ec9cb2ba1994a2", "d1d52cbf890f2b4f8bf31189c86d3d381a68e8d2", "docs/vm_tlb/review_packs/C16_ADA_W4_DECODE_UTILIZATION_MULTIVIEW_SCREEN_V1"),
    "pascal": ("5289c7b6d8ef16cd926f2c63f64bbe79ef43cc89", "cd09ae9ed63253a05e38d7616442c5911561965f", "docs/vm_tlb/review_packs/C16_PARALLEL_SCAN_POLICY_INDEPENDENT_CACHE_HEADROOM_V1"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(repo: Path, commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=repo)


def doc(repo: Path, key: str, name: str) -> dict:
    commit, _, pack = AUTHORITIES[key]
    return json.loads(git_bytes(repo, commit, f"{pack}/{name}"))


def verify(repo: Path) -> dict:
    receipts = {}
    for key, (commit, expected_tree, pack) in AUTHORITIES.items():
        tree = subprocess.check_output(["git", "rev-parse", f"{commit}^{{tree}}"], cwd=repo, text=True).strip()
        if tree != expected_tree:
            raise AssertionError(f"tree mismatch for {key}")
        manifest = git_bytes(repo, commit, f"{pack}/SHA256SUMS").decode()
        count = 0
        for line in manifest.splitlines():
            expected, name = line.split("  ", 1)
            artifact_path = name if name.startswith(("docs/", "util/")) else f"{pack}/{name}"
            if sha256(git_bytes(repo, commit, artifact_path)) != expected:
                raise AssertionError(f"manifest mismatch: {key}/{name}")
            count += 1
        receipts[key] = {"commit": commit, "tree": tree, "pack": pack, "manifest_sha256": sha256(manifest.encode()), "manifest_count": count}

    m1 = doc(repo, "m1", "B16_REUSE_WINDOW_PERFORMANCE.json")
    m1f = doc(repo, "m1f", "FINAL_DECISION.json")
    split = doc(repo, "split_threshold", "FINAL_DECISION.json")
    grouped = doc(repo, "grouped", "FINAL_DECISION.json")
    residual = doc(repo, "residual_consumer", "FINAL_DECISION.json")
    conversion = doc(repo, "conversion", "FINAL_DECISION.json")
    conversion_native = doc(repo, "conversion_native", "FINAL_DECISION.json")
    ffn = doc(repo, "ffn_headroom", "FINAL_DECISION.json")
    merged_guard = doc(repo, "merged_guard", "FINAL_DECISION.json")
    merged_native = doc(repo, "merged_native", "FINAL_DECISION.json")
    two_v1 = doc(repo, "two_stream_v1", "FINAL_DECISION.json")
    repair = doc(repo, "two_stream_repair", "FINAL_DECISION.json")
    two_v2 = doc(repo, "two_stream_v2", "FINAL_REPORT_FACTS.json")
    ada = doc(repo, "ada", "FINAL_DECISION.json")
    pascal = doc(repo, "pascal", "FINAL_DECISION.json")
    checks = [
        abs(m1["metrics"]["C_window"]["response_fraction"] - (-0.0020543388284633025)) < 1e-15,
        m1f["decision"] == "M1F_FULL_TIMING_NOT_JUSTIFIED_BY_CURRENT_HEADROOM",
        abs(split["K2560_to_3072"]["split1_dram_growth"] - 4.036466869544065) < 1e-12,
        grouped["new_split_mechanism_story"] == "关闭",
        residual["splitk_branch_should_close"],
        conversion["strict_repeated_conversion_exists"] and abs(conversion["zero_cost_decode_ceiling"] - 1.0177078795916403) < 1e-12,
        conversion_native["decision"] == "NO_LOCAL_ORACLE_HEADROOM_STOP_VALIDATION",
        abs(ffn["legal_ffn_wall_fraction"] - 0.2847969071067202) < 1e-15,
        merged_guard["decision"] == "PLAIN_GATE_UP_CONCURRENCY_NOT_NOVEL_MECHANISM",
        merged_native["status"] == "CORRECTNESS_TOLERANCE_FAILED_STOP",
        two_v1["status"] == "CORRECTNESS_MISMATCH_STOP",
        repair["root_cause_classification"] == "PREFILL_SCOPE_CONTAMINATION_CONFIRMED",
        abs(two_v2["primary"]["observed"]["b0_median_ms"] - 74.2159194946289) < 1e-12,
        abs(two_v2["primary"]["observed"]["b1_median_ms"] - 81.43391799926758) < 1e-12,
        two_v2["overlap"]["overlap_count"] == 10 and two_v2["overlap"]["total_overlap_ns"] == 544929,
        ada["status"] == "PASS_STOP",
        pascal["overall_decision"] == "REPLACEMENT_POLICY_HEADROOM_SMALL",
    ]
    if not all(checks):
        raise AssertionError("terminal scientific facts did not close")
    return {"receipts": receipts, "two_v2": two_v2}


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "NA") or "NA" for field in fields})


def build(repo: Path, out: Path) -> None:
    verified = verify(repo)
    out.mkdir(parents=True, exist_ok=True)
    rows = [
        {"id": "E1_SHARED_RESIDENCY", "stage": "residency", "authority": "1e701f013", "evidence_class": "ACTUAL_EXPERIMENT", "confirmed_finding": "fixed quota retains multiple local qweight benefits", "strong_software_baseline": "SETASIDE/rotation controls", "oracle_or_headroom": "local benefits but whole decode <2%", "actual_result": "SHARED_RESIDENCY_LOCAL_ONLY", "mechanism_state": "CLOSED_SYSTEM_CASE_WEAK", "claim_boundary": "local only; traffic is not critical-path timing"},
        {"id": "E1_OPERATOR_FAMILY", "stage": "residency", "authority": "eae1cc4d8", "evidence_class": "ACTUAL_EXPERIMENT", "confirmed_finding": "up-proj local benefit does not generalize to gate/down", "strong_software_baseline": "all 84 FFN projections measured", "oracle_or_headroom": "GUD84 direct saving mostly up; no 2% system gate", "actual_result": "OPERATOR_FAMILY_NOT_SUPPORTED", "mechanism_state": "CLOSED", "claim_boundary": "negative residual not uniquely cache collateral"},
        {"id": "M1_B16", "stage": "residency", "authority": "71324d464", "evidence_class": "ACTUAL_EXPERIMENT", "confirmed_finding": "mechanism activated; class retention lost with protected churn", "strong_software_baseline": "R0 matched baseline", "oracle_or_headroom": "target/window signs nonpositive", "actual_result": "window -0.2054%; local -0.2777%", "mechanism_state": "CLOSED_CURRENT_SCOPE", "claim_boundary": "old-address survival and unique cause remain unknown"},
        {"id": "M1F_ADMISSION", "stage": "residency", "authority": "5f7a2b831", "evidence_class": "ORACLE_HEADROOM", "confirmed_finding": "selector covers 1.7917% with no heat enrichment", "strong_software_baseline": "frozen selector and R0", "oracle_or_headroom": "hard target-zero window ceiling 0.9557%; modeled response 0.0171%", "actual_result": "no run; 166 slot-hour primary+diagnostic cost", "mechanism_state": "CLOSED_NOT_JUSTIFIED", "claim_boundary": "no M1F full timing or mechanism claim"},
        {"id": "SPLITK_CAPACITY", "stage": "split_grouped", "authority": "6d226cd99", "evidence_class": "CONFIRMED_PHENOMENON", "confirmed_finding": "K2560->3072 split1 DRAM 4.04x and timing 1.60x for 1.2x K", "strong_software_baseline": "split8 comparison", "oracle_or_headroom": "capacity is a factor; no hard 64MiB threshold", "actual_result": "nonlinear split1 transition", "mechanism_state": "SUPERSEDED_BY_STRONG_MAPPING", "claim_boundary": "not all DRAM=qweight; not uniquely L2"},
        {"id": "SPLITK_CROSSM", "stage": "split_grouped", "authority": "2113422f7", "evidence_class": "ACTUAL_EXPERIMENT", "confirmed_finding": "shared physical weight-side addresses cause high L2 reuse", "strong_software_baseline": "PER_MTILE counterfactual", "oracle_or_headroom": "miss*32B tracks extra GEMM DRAM", "actual_result": "reuse collapses when sharing is destroyed", "mechanism_state": "PHENOMENON_CONFIRMED", "claim_boundary": "combined weight-side only; no replacement-detail claim"},
        {"id": "GROUPED_CTA", "stage": "split_grouped", "authority": "e78552780", "evidence_class": "STRONG_SOFTWARE_BASELINE", "confirmed_finding": "GROUP_M16 restores split1 hit to 95.95%", "strong_software_baseline": "classic grouped/swizzled mapping", "oracle_or_headroom": "split1 then 38.7%/30.9% faster than split8", "actual_result": "most split1 locality loss removed", "mechanism_state": "NEW_SPLIT_MECHANISM_CLOSED", "claim_boundary": "mapping baseline absorbs cache-aware split story"},
        {"id": "RESIDUAL_PARALLELISM", "stage": "split_grouped", "authority": "a3a36e64a", "evidence_class": "ACTUAL_EXPERIMENT", "confirmed_finding": "split8 advantage decays with CTA supply; M64 split1 +4.93%", "strong_software_baseline": "GROUP_FULL_M", "oracle_or_headroom": "low-CTA/partial-tile/reduction tradeoff", "actual_result": "M64 CI [4.50%,5.13%] for split1", "mechanism_state": "SPLITK_BRANCH_CLOSED", "claim_boundary": "parallel decomposition, not new cache mechanism"},
        {"id": "CONVERSION_CENSUS", "stage": "conversion", "authority": "9ff9e9b35", "evidence_class": "CONFIRMED_PHENOMENON", "confirmed_finding": "strict cross-CTA repeated conversion exists (M64 Rdup 75%)", "strong_software_baseline": "register/shared-memory CTA-local elimination", "oracle_or_headroom": "natural target f=1.74%; zero-cost ceiling 1.0177x", "actual_result": "remaining expanded footprint/sync cost large", "mechanism_state": "DEQUANT_CACHE_CLOSED", "claim_boundary": "repeat count is not time saved"},
        {"id": "CONVERSION_NATIVE_ORACLE", "stage": "conversion", "authority": "797477f2c", "evidence_class": "ACTUAL_EXPERIMENT", "confirmed_finding": "isolated local oracle is slower", "strong_software_baseline": "compressed baseline and predecoded diagnostic", "oracle_or_headroom": "oracle speedup 0.8262x; predecode 1.0929x changes representation/kernel", "actual_result": "NO_LOCAL_ORACLE_HEADROOM", "mechanism_state": "CLOSED", "claim_boundary": "predecode is not a free conversion upper bound"},
        {"id": "FFN_TIMELINE", "stage": "ffn", "authority": "071297ae7", "evidence_class": "MEASUREMENT_AUTHORITY", "confirmed_finding": "560 semantic ranges/112 legal FFN windows", "strong_software_baseline": "instrumentation-neutral accepted runtime", "oracle_or_headroom": "legal wall union can be reconstructed", "actual_result": "timeline authority PASS", "mechanism_state": "AUTHORITY_ONLY", "claim_boundary": "no headroom computed by producer"},
        {"id": "FFN_HEADROOM", "stage": "ffn", "authority": "30b3016a7", "evidence_class": "ORACLE_HEADROOM", "confirmed_finding": "legal FFN wall=28.4797%, not 44.5747% additive module sum", "strong_software_baseline": "same natural CONTROL_GUD84", "oracle_or_headroom": "F1 elementwise 0.221%; gate/up ideal 7.893%", "actual_result": "oracle only", "mechanism_state": "F2A_WAS_QUALIFIED", "claim_boundary": "oracle is not prediction"},
        {"id": "MERGED_GUARD", "stage": "ffn", "authority": "3c3f667bb", "evidence_class": "STRONG_SOFTWARE_BASELINE", "confirmed_finding": "vLLM merged gate_up is mature and same-checkpoint compatible", "strong_software_baseline": "MergedColumnParallelLinear+SiluAndMul", "oracle_or_headroom": "not performance-estimated", "actual_result": "source qualification", "mechanism_state": "PLAIN_CONCURRENCY_NOT_NOVEL", "claim_boundary": "cross-runtime capability is not strict A/B"},
        {"id": "MERGED_NATIVE", "stage": "ffn", "authority": "6c92e9cd8", "evidence_class": "ACTUAL_EXPERIMENT", "confirmed_finding": "canonical quant identity and tokens pass; 14/336 occurrences fail tolerance", "strong_software_baseline": "MarlinLinearKernel merged path", "oracle_or_headroom": "none admitted", "actual_result": "CORRECTNESS_TOLERANCE_FAILED_STOP", "mechanism_state": "NO_PERFORMANCE_CLASSIFICATION", "claim_boundary": "no B0/B2 attribution or ranking"},
        {"id": "TWO_STREAM_V1", "stage": "ffn", "authority": "ef517d8e5", "evidence_class": "CORRECTNESS_GATE", "confirmed_finding": "prefill scope contamination changes first token", "strong_software_baseline": "B0 accepted path", "oracle_or_headroom": "quarantined", "actual_result": "CORRECTNESS_MISMATCH_STOP", "mechanism_state": "FAILED_PRESERVED", "claim_boundary": "overlap cannot be used scientifically"},
        {"id": "TWO_STREAM_REPAIR", "stage": "ffn", "authority": "ee8cadd4a", "evidence_class": "SOURCE_QUALIFICATION", "confirmed_finding": "prefill restored; D0-D3 DAG unchanged", "strong_software_baseline": "canary-first V2", "oracle_or_headroom": "unchanged 7.893% ideal", "actual_result": "source qualified", "mechanism_state": "V2_CANARY_ONLY", "claim_boundary": "awq_ext low-level cause not uniquely proven"},
        {"id": "TWO_STREAM_V2", "stage": "ffn", "authority": "e8a2553f5", "evidence_class": "ACTUAL_EXPERIMENT", "confirmed_finding": "10/112 overlap windows; gate/up duration inflation", "strong_software_baseline": "correctness-passing B0/B1 ABBA", "oracle_or_headroom": "oracle realization -0.9334", "actual_result": "74.2159->81.4339ms; speedup 0.91136x", "mechanism_state": "CONCURRENCY_PATH_CLOSED", "claim_boundary": "contention observed but does not prove entire slowdown; coordination/limited overlap remain possible"},
        {"id": "ADA_MULTIVIEW", "stage": "utilization", "authority": "5a8bcd636", "evidence_class": "ORACLE_SCREEN", "confirmed_finding": "M1 useful tile fill 6.25%; decode limitation is mixed", "strong_software_baseline": "Marlin/QUICK/FLUTE/FlashDecoding++ guards", "oracle_or_headroom": "only gate/up cleared; no second candidate", "actual_result": "PASS_STOP", "mechanism_state": "NO_REMAINING_CANDIDATE_AFTER_TWO_STREAM", "claim_boundary": "efficiency metric is not elapsed-time oracle"},
        {"id": "PASCAL_CACHE_GATE", "stage": "cache_gate", "authority": "5289c7b6d", "evidence_class": "POLICY_INDEPENDENT_BOUND", "confirmed_finding": "raw ROW exposes traffic gap; GROUP_FULL_M reaches aligned one-fill reference", "strong_software_baseline": "grouped mapping", "oracle_or_headroom": "replacement-policy residual small", "actual_result": "REPLACEMENT_POLICY_HEADROOM_SMALL", "mechanism_state": "CACHE_PREDICTOR_CLOSED", "claim_boundary": "observed phases unknown; traffic and timing kept separate"},
    ]
    write_tsv(out / "C16_ACCEPTED_EVIDENCE_LEDGER.tsv", rows, ["id", "stage", "authority", "evidence_class", "confirmed_finding", "strong_software_baseline", "oracle_or_headroom", "actual_result", "mechanism_state", "claim_boundary"])

    timeline = """# C16 AI-workload exploration wave timeline

## Terminal state

The wave ends with `NO_CURRENT_C16_MECHANISM_READY_FOR_PROMOTION`. This is a completed exploration cycle: each initially plausible mechanism was either bounded below material system headroom, absorbed by a mature software baseline, rejected by correctness, or measured as non-beneficial.

## Chronology

1. **E1 residency and policy scaling (2026-09-23/24).** Compressed W4 projections showed strong state/shape sensitivity and selective persistence produced local timing effects. Fixed-budget sharing and broader coverage remained below the 2% whole-decode gate; gate/down expansion failed. This established a phenomenon, not a system mechanism.
2. **M1/M1F terminal review (2026-09-30).** B16 activated and generated protected churn, but the selected local and whole window were nonpositive. Class-level retention disappeared; exact old-address survival remained unknown. M1F's hard target-zero ceiling was below 1%, its model response about 0.017%, and its cost high, so full timing was not justified.
3. **Split-K/cross-M/grouped sequence (2026-09-28/29).** Capacity-sensitive nonlinear traffic and cross-M address sharing were real. Classic GROUP_M16 restored split1 L2 reuse and made split1 faster than split8 at the frozen large-K points. The residual sweep reduced to low-CTA supply, partial-tile utilization and reduction cost; the new cache-aware split story closed.
4. **Conversion reuse (2026-09-29).** Strict repeated conversion existed, primarily cross-CTA, but expanded footprint and natural timing weight bounded whole-decode opportunity. Native isolation made the local oracle slower; the faster predecoded diagnostic changed representation and kernel. Dequant-cache promotion stopped.
5. **FFN timeline and oracle (2026-09-30).** Correlated GPU activity replaced the invalid additive module share: legal FFN wall was 28.4797%, not 44.5747%. Explicit elementwise removal was only 0.221% of decode; gate/up no-contention concurrency exposed a 7.893% ideal ceiling.
6. **Software guards and native tests (2026-10-01).** vLLM merged gate/up established that plain merge is mature, but the exact native merged run failed the frozen numerical tolerance and yielded no performance classification. Two-stream V1 failed correctness because it contaminated prefill; V2 repaired scope and passed correctness, activated limited overlap, yet slowed D0-D3 from 74.2159 to 81.4339 ms. Kernel-duration inflation was observed, but does not uniquely explain the full slowdown.
7. **Ada multiview and PASCAL cache gate (2026-10-01).** The Ada screen found mixed tile-fill/supply/stall/service limits and no second qualified candidate. PASCAL bounds plus grouped controls showed replacement-policy headroom small under the accepted strong baseline. No cache predictor was authorized.
"""
    (out / "C16_EXPLORATION_WAVE_TIMELINE.md").write_text(timeline)

    closed = """# Closed directions

- **Broad selective-residency/cache policy mechanism:** local effects did not become material system benefit; M1 was nonpositive and M1F headroom/cost failed admission.
- **Cache-aware/new Split-K mechanism:** grouped/swizzled CTA mapping solved the dominant locality loss; remaining behavior is ordinary parallel decomposition.
- **Conversion-result/dequant cache:** strict duplication exists, but system weight is small and the isolated oracle is slower.
- **FFN materialization elimination as the main opportunity:** explicit elementwise zero is only 0.221% of decode; traffic bytes do not identify critical-path time.
- **Two-stream gate/up as a performance mechanism:** correctness-passing V2 activates limited overlap but slows decode by 9.7257%.
- **Plain merged gate/up novelty or performance ranking:** merge is mature software; the exact native strong-baseline canary failed tolerance, so no ranking is admitted.
- **New generic Ada W4 flat-GEMM, reduction-removal or attention split/combine mechanism:** strong neighbors and small/unknown legal headroom close these stories.
- **Replacement-policy/PASCAL cache predictor for the frozen split workload:** grouped mapping reaches the aligned one-fill reference and leaves small residual headroom.

Closed means closed for the accepted C16 identities and contracts. It is not a universal claim about every model, GPU, shape or workload.
"""
    (out / "C16_CLOSED_DIRECTIONS.md").write_text(closed)

    lessons = """# Method lessons from negative and bounded results

1. **Oracle-first.** A mechanism is not promoted until a legal whole-scope ceiling is material. M1F, elementwise FFN removal and reduction removal stopped cheaply at this gate.
2. **Strong-software-first.** GROUP_M16 absorbed the Split-K locality story; vLLM merged gate/up blocks novelty claims before hardware design.
3. **Traffic is not timing.** DRAM/L2 bytes, hit fractions and long-scoreboard percentages cannot be converted directly into critical-path speedup. Identical TEX read-hit behavior can coexist with large timing differences.
4. **Module-duration sum is not legal wall union.** Additive gate/up/down timing reported 44.5747%; correlated producer-to-final-consumer windows yield 28.4797%. Admission must use the latter.
5. **Correctness before performance.** Two-stream V1 overlap was quarantined when prefill tokens drifted; merged native timing was rejected when 14/336 occurrences exceeded tolerance.
6. **Cross-runtime capability is not strict A/B.** A vLLM Marlin merged path proves capability but simultaneously changes kernel, reduction, layout and fused epilogue; it cannot isolate merge-only causality.
7. **Negative experiments are mechanism evidence.** V2 directly shows that overlap activation can coexist with slowdown and inflated kernels. The careful conclusion is that contention is observed, not that it explains every millisecond; stream/event coordination and limited realized overlap remain possible contributors.
8. **Unknown stays unknown.** Missing old-address survival, per-CTA phase history, tile-ready dependencies and exact extension internals were not filled with names, ratios or public-source assumptions.
"""
    (out / "C16_METHOD_LESSONS.md").write_text(lessons)

    surviving = """# Surviving questions

## Active promotion candidates: 0

No current C16 mechanism has both a material legal headroom and a missing strong software capability. `NO_CURRENT_C16_MECHANISM_READY_FOR_PROMOTION` is therefore the terminal decision.

## Future-question parking lot: 1

| Field | Heterogeneous tile handoff after strong kernels |
|---|---|
| phenomenon | No accepted C16 performance phenomenon yet; only the logical producer→product→down DAG and the absence of tile-ready authority are established. |
| nearest neighbor | Kitsune queues/spatial dataflow, VTC virtual tensors, ComFuse staged fusion, and NVIDIA tile-ready triggering. |
| missing authority | Exact producer/consumer tile mapping, readiness granularity, layout compatibility, partial-sum ownership, synchronization/scratch cost, and a material whole-scope oracle after strong software. |
| minimum next experiment | None authorized now. First perform a source/static dependency qualification for one already-important pair; only if a legal local oracle and whole-scope ceiling survive should a single bounded native canary be proposed. |
| potential paper claim | None today. A future claim would require that existing fusion/virtual-tensor/queue baselines cannot preserve both fast layouts and that a measured net benefit survives an independent pair/shape. |

This parking-lot item is not an active mechanism candidate and does not authorize GPU, trace or simulator work.
"""
    (out / "C16_SURVIVING_QUESTIONS.md").write_text(surviving)

    claims = """# Paper claim boundaries

## Supported

- Compressed W4 execution has real shape/state sensitivity; capacity and access policy matter, but no single L2-only cause is established.
- Cross-M physical address sharing materially controls observed reuse, and grouped CTA scheduling is the decisive strong baseline for the frozen Split-K points.
- Legal FFN wall union is 28.4797% of the accepted timeline; additive module timing is not an admission weight.
- Correctness-passing two-stream execution activates overlap in 10/112 windows but slows full D0-D3 by 9.7257%; gate and up kernel durations inflate.
- Resource contention is directly observed through kernel-duration inflation. It is not proven to explain the entire whole-decode slowdown; stream/event coordination and limited realized overlap remain possible contributors.
- The exploration methodology—oracle-first, strong-software-first, and correctness-first—eliminated several attractive but nonviable mechanism stories.

## Not supported

- A new cache/replacement/dequant/split/concurrency mechanism ready for promotion.
- A hard 64 MiB threshold, all DRAM being qweight, or L2 as the unique cause.
- A performance ranking for the merged vLLM path, or bitwise equivalence across its different backend.
- Plain gate/up concurrency, merged gate/up, tile-ready triggering, generic Stream-K, or fused FFN as novel by itself.
- `resource contention explains all of the two-stream slowdown`.
- A legal cross-tile producer→down pipeline ceiling.
- Generalization from these frozen Qwen2.5/AWQ/RTX4080 points to all GEMMs, LLMs, GPUs or quantization formats.
"""
    (out / "C16_PAPER_CLAIM_BOUNDARIES.md").write_text(claims)

    final = {
        "schema_version": 1,
        "status": "TERMINAL_SYNTHESIS_PASS",
        "decision": "NO_CURRENT_C16_MECHANISM_READY_FOR_PROMOTION",
        "interpretation": "CURRENT_EXPLORATION_WAVE_COMPLETE_NOT_FAILURE",
        "active_promotion_candidate_count": 0,
        "future_question_parking_lot_count": 1,
        "closed_direction_count": 8,
        "authority_count": len(AUTHORITIES),
        "two_stream_v2": {
            "classification": "CONCURRENCY_ACTIVATED_BUT_RESOURCE_CONTENTION_LIMITED",
            "B0_median_ms": 74.2159194946289,
            "B1_median_ms": 81.43391799926758,
            "speedup": 0.911363732926327,
            "time_reduction_fraction": -0.09725674159653909,
            "oracle_realization": -0.9334203350716757,
            "overlap_windows": 10,
            "overlap_total_ns": 544929,
            "gate_inflation": 1.024771606336511,
            "up_inflation": 1.1938476820071748,
            "heldout_D3_direction": "B1_SLOWER",
            "causal_boundary": "resource contention directly observed but not proven to explain entire slowdown; stream/event coordination and limited realized overlap remain possible contributors",
        },
        "new_experiment_authorized": False,
        "gpu_used": False,
        "accel_sim_used": False,
        "lane4_partial_accessed": False,
        "authority_receipts": verified["receipts"],
    }
    (out / "FINAL_PROJECT_STATE.json").write_text(json.dumps(final, indent=2, sort_keys=True) + "\n")

    names = sorted(path.name for path in out.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    (out / "SHA256SUMS").write_text("".join(f"{sha256((out / name).read_bytes())}  {name}\n" for name in names))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[3]
    if args.check:
        verify(repo)
        return
    build(repo, args.output_dir or repo / PACK)


if __name__ == "__main__":
    main()
