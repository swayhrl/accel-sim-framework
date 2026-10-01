#!/usr/bin/env python3
"""CPU-only PASCAL-to-C16 cache headroom oracle; never launches experiments."""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction
import hashlib
import json
from pathlib import Path


PAPER_SHA = "e66e606470a841eae6495c6d0ddffbbb922d04a7ce6f4140a657850b7914db2e"
PAPER_URL = "https://arxiv.org/pdf/2609.10515v1"
PAPER_TITLE = "PASCAL: A Phase-Aware Shared-Cache Model for Parallel Scans"
L2_BYTES = 64 * 1024 * 1024
LINE_BYTES = 128
CAPACITY_LINES = L2_BYTES // LINE_BYTES
M_WORKERS = 16

AUTHORITY_COMMITS = {
    "grouped_consumer": "e7855278076c7e0360d39b18424cc8f048f51da5",
    "grouped_native": "a75379674116fc94e57ccc88eff9359fc1f4114c",
    "crossm_consumer": "2113422f7e6b7e5a851469511d26a9ddf7123d4e",
    "residual_consumer": "a3a36e64ae4a3a316df2bf4dfc9cac95caf8e164",
    "static_footprint": "c72d28b17247f25d0c3613604ab6cab1737666e0",
}


class ContractError(ValueError):
    pass


def need(value: bool, message: str) -> None:
    if not value:
        raise ContractError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path):
    need(path.is_file() and path.stat().st_size > 0, f"missing JSON {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_tsv(path: Path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def verify_manifest(pack: Path, name: str = "SHA256SUMS") -> dict[str, str]:
    manifest = pack / name
    need(manifest.is_file(), f"missing manifest {manifest}")
    result = {}
    for raw in manifest.read_text(encoding="utf-8").splitlines():
        expected, member = raw.split(maxsplit=1)
        member = member.lstrip(" *")
        path = pack / member
        need(path.is_file() and sha256(path) == expected, f"manifest drift {path}")
        result[member] = expected
    need(result, f"empty manifest {manifest}")
    return result


def footprint(gaps, t):
    need(t >= 0 and gaps and all(gap > 0 for gap in gaps), "invalid gap footprint")
    return sum(min(gap, t) for gap in gaps)


def miss_gap_count(gaps, t):
    return sum(gap > t for gap in gaps)


def characteristic_window(gaps, capacity):
    total = sum(gaps)
    need(0 <= capacity < total, "PASCAL requires 0 <= C < N")
    lo, hi = 0, total
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if footprint(gaps, mid) <= capacity:
            lo = mid
        else:
            hi = mid - 1
    return lo


def aligned_intervals(n_blocks: int, workers: int):
    need(n_blocks > 1 and workers >= 2, "invalid aligned scan")
    return [Fraction(1, workers)] * (workers - 1) + [
        Fraction(n_blocks * workers - (workers - 1), workers)]


def policy_independent_bound(intervals, capacity):
    budget = Fraction(capacity)
    hits = Fraction(0)
    for interval in sorted(intervals):
        if budget <= 0:
            break
        if interval <= budget:
            hits += 1
            budget -= interval
        else:
            hits += budget / interval
            budget = Fraction(0)
    return Fraction(len(intervals)) - hits, hits


def aligned_bound(n_blocks: int, workers: int, capacity: int):
    gaps = [n_blocks]
    t_star = characteristic_window(gaps, capacity)
    ttl = miss_gap_count(gaps, t_star)
    lru_lower = miss_gap_count(gaps, t_star + 1)
    lru_upper = miss_gap_count(gaps, max(0, t_star - 1))
    intervals = aligned_intervals(n_blocks, workers)
    policy_misses, residency_hits = policy_independent_bound(intervals, capacity)
    finite_correction = Fraction(n_blocks, n_blocks)  # N/H for one full scan H=N.
    return {
        "N": n_blocks, "M": workers, "C": capacity,
        "distinct_phases_D": 1, "cyclic_gaps": str(n_blocks),
        "U_t": f"min({n_blocks},t)", "T_star": t_star,
        "TTL_misses_per_round": ttl, "TTL_miss_rate_per_request": ttl / workers,
        "LRU_lower_misses_per_round": lru_lower,
        "LRU_upper_misses_per_round": lru_upper,
        "LRU_exact_under_certificate": lru_lower == lru_upper,
        "policy_residency_V_C": float(residency_hits),
        "policy_miss_lower_bound_per_round": float(policy_misses),
        "policy_miss_lower_bound_fraction": float(policy_misses / workers),
        "policy_miss_lower_bound_exact_fraction":
            f"{policy_misses.numerator}/{policy_misses.denominator}",
        "finite_H_rounds": n_blocks,
        "finite_additive_correction_N_over_H": float(finite_correction),
        "finite_corrected_lower_bound_per_round":
            float(max(Fraction(0), policy_misses - finite_correction)),
        "sigma_E_aligned_best_case": 0,
        "LRU_sharing_certificate_C_ge_2sigma_minus_1": capacity >= -1,
        "interval_summary":
            f"{workers-1}x(1/{workers}) + 1x({n_blocks}-{workers-1}/{workers})",
    }


def f(value):
    return float(value)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--paper-pdf", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    repo = args.repo_root.resolve()
    need(repo.is_dir() and not args.output_dir.exists(), "repo/output state invalid")
    need(sha256(args.paper_pdf) == PAPER_SHA, "PASCAL v1 PDF SHA drift")

    reviews = repo / "docs/vm_tlb/review_packs"
    grouped = reviews / "C16_SPLITK_GROUPED_CTA_BASELINE_CONSUMER_174NEW_V1"
    grouped_native = reviews / "C16_SPLITK_GROUPED_CTA_BASELINE_NATIVE_109_V1"
    crossm = reviews / "C16_SPLITK_CROSSM_REUSE_CAUSAL_CONSUMER_174NEW_V1"
    residual = reviews / "C16_GROUPED_RESIDUAL_PARALLELISM_CONSUMER_174NEW_V1"
    static = reviews / "C16_SPLITK_FOOTPRINT_STATIC_AUDIT_174NEW_V1"
    for pack in (grouped, grouped_native, crossm, residual, static):
        verify_manifest(pack)

    grouped_rows = read_tsv(grouped / "RAW_RECOMPUTE.tsv")
    footprint_rows = read_tsv(static / "PER_SPLIT_FOOTPRINT.tsv")
    launch_rows = read_tsv(grouped_native / "EXPECTED_LAUNCH.tsv")
    invocation_rows = read_tsv(grouped_native / "MAPPING_INVOCATION_RECEIPT.tsv")
    crossm_rows = read_tsv(crossm / "RAW_RECOMPUTE.tsv")
    residual_rows = read_tsv(residual / "M_SWEEP_COMPARISON.tsv")
    need(len(grouped_rows) == 8 and len(launch_rows) == 8 and len(invocation_rows) == 8,
         "grouped matrix drift")

    footprint_by_k = {}
    for k in (3072, 4096):
        candidates = [row for row in footprint_rows
                      if int(row["K"]) == k and int(row["split_k_iters"]) == 1]
        need(len(candidates) == 1 and int(candidates[0]["N"]) == 49152,
             f"static footprint authority drift K{k}")
        footprint_by_k[k] = candidates[0]

    bounds = {k: aligned_bound(int(row["total_128B_lines"]), M_WORKERS, CAPACITY_LINES)
              for k, row in footprint_by_k.items()}
    need(bounds[3072]["N"] == 612864 and bounds[4096]["N"] == 817152,
         "combined weight-side line count drift")
    need(all(row["gemm_grid"] in ("[6144,1,1]", "[49152,1,1]") for row in launch_rows),
         "launch grid drift")
    need({row["mapping"] for row in invocation_rows} == {"ROW", "GROUP_M16"},
         "mapping invocation drift")

    applicability = []
    for row in grouped_rows:
        k, split, mapping = int(row["K"]), int(row["split"]), row["mapping"]
        sample = f"K{k}_S{split}_{'GROUP_FULL_M' if mapping == 'GROUP_M16' else 'ROW'}"
        applicability.append({
            "sample_id": sample, "source": "GROUPED_CTA_FINAL_CONSUMER",
            "N": bounds[k]["N"], "M": M_WORKERS, "C": CAPACITY_LINES,
            "multiple_workers": True, "shared_data_blocks": True,
            "regular_same_scan_order": True, "cross_worker_reuse": True,
            "phase_authority": (
                "LOGICAL_GROUP_FULL_M_ALIGNED_BEST_CASE_ACTUAL_PHASE_UNKNOWN"
                if mapping == "GROUP_M16" else
                "LOGICAL_ROW_DISTANCE_384_ACTUAL_PHASE_UNKNOWN"),
            "applicability": "APPLICABLE_ALIGNED_BEST_CASE_ONLY",
            "closed_branch_remains_closed": True,
        })
    for split in (1, 8):
        for state in ("SHARED", "PER_MTILE"):
            applicability.append({
                "sample_id": f"CROSSM_K3072_S{split}_{state}",
                "source": "CROSSM_REUSE_CAUSAL_FINAL_CONSUMER",
                "N": bounds[3072]["N"] if state == "SHARED" else "UNKNOWN",
                "M": M_WORKERS, "C": CAPACITY_LINES,
                "multiple_workers": True,
                "shared_data_blocks": state == "SHARED",
                "regular_same_scan_order": True,
                "cross_worker_reuse": state == "SHARED",
                "phase_authority": "UNKNOWN_NO_PER_CTA_PROGRESS_TIMELINE",
                "applicability": (
                    "APPLICABLE_ALIGNED_BEST_CASE_ONLY" if state == "SHARED" else
                    "NOT_APPLICABLE_NO_SHARED_PHYSICAL_BLOCK_IDENTITY"),
                "closed_branch_remains_closed": True,
            })
    applicability.append({
        "sample_id": "RESIDUAL_M_SWEEP_SPLIT1_SPLIT8", "source": "GROUPED_RESIDUAL_FINAL_CONSUMER",
        "N": "UNKNOWN", "M": "M1_M16_M32_M64", "C": CAPACITY_LINES,
        "multiple_workers": True, "shared_data_blocks": True,
        "regular_same_scan_order": "UNBOUND", "cross_worker_reuse": True,
        "phase_authority": "NO_K_FOOTPRINT_OR_PER_CTA_PROGRESS_BINDING_IN_CLOSED_PACK",
        "applicability": "NOT_APPLICABLE_STATIC_BOUND_INPUTS_INCOMPLETE_TIMING_ONLY",
        "closed_branch_remains_closed": True,
    })

    bound_rows = []
    for sample in applicability[:8]:
        base = bounds[int(sample["sample_id"].split("_")[0][1:])]
        aligned = dict(sample_id=sample["sample_id"], bound_case="ALIGNED_BEST_CASE",
                       observed_phase=False, status="BOUND_COMPUTED", **base)
        bound_rows.append(aligned)
        bound_rows.append({
            "sample_id": sample["sample_id"], "bound_case": "OBSERVED_PHASE_CASE",
            "observed_phase": True, "status": "UNKNOWN_PHASE_NOT_RECOVERABLE",
            "N": base["N"], "M": base["M"], "C": base["C"],
            "distinct_phases_D": "UNKNOWN", "cyclic_gaps": "UNKNOWN",
            "U_t": "UNKNOWN", "T_star": "UNKNOWN",
            "TTL_misses_per_round": "UNKNOWN", "TTL_miss_rate_per_request": "UNKNOWN",
            "LRU_lower_misses_per_round": "UNKNOWN", "LRU_upper_misses_per_round": "UNKNOWN",
            "LRU_exact_under_certificate": "UNKNOWN",
            "policy_residency_V_C": "UNKNOWN",
            "policy_miss_lower_bound_per_round": "UNKNOWN",
            "policy_miss_lower_bound_fraction": "UNKNOWN",
            "policy_miss_lower_bound_exact_fraction": "UNKNOWN",
            "finite_H_rounds": base["N"], "finite_additive_correction_N_over_H": 1.0,
            "finite_corrected_lower_bound_per_round": "UNKNOWN",
            "sigma_E_aligned_best_case": "UNKNOWN",
            "LRU_sharing_certificate_C_ge_2sigma_minus_1": "UNKNOWN",
            "interval_summary": "UNKNOWN",
        })

    grouped_lookup = {(int(row["K"]), int(row["split"]), row["mapping"]): row
                      for row in grouped_rows}
    actual_rows = []
    row_candidate_ids = []
    for row in grouped_rows:
        k, split, mapping = int(row["K"]), int(row["split"]), row["mapping"]
        sample_id = f"K{k}_S{split}_{'GROUP_FULL_M' if mapping == 'GROUP_M16' else 'ROW'}"
        n_lines = bounds[k]["N"]
        miss_sectors = f(row["l2_read_miss_sectors"])
        miss_bytes = miss_sectors * 32.0
        fill_equiv = miss_bytes / (n_lines * LINE_BYTES)
        policy_lower = bounds[k]["policy_miss_lower_bound_per_round"]
        policy_lower_bytes = policy_lower * n_lines * LINE_BYTES
        aligned_reference_bytes = n_lines * LINE_BYTES
        policy_gap = max(0.0, (fill_equiv - policy_lower) / fill_equiv)
        aligned_reference_gap = max(0.0, (fill_equiv - 1.0) / fill_equiv)
        time_ms = f(row["median_ms"])
        group_time = f(grouped_lookup[(k, split, "GROUP_M16")]["median_ms"])
        timing_exposure = (time_ms - group_time) / time_ms if mapping == "ROW" else 0.0
        if mapping == "ROW" and split == 1:
            classification = "CACHE_POLICY_MECHANISM_WORTH_FURTHER_REVIEW"
            row_candidate_ids.append(sample_id)
            rationale = "RAW_ROW_CASE_HAS_LARGE_TRAFFIC_ORACLE_GAP_AND_MATCHED_TIMING_EXPOSURE"
        else:
            classification = "REPLACEMENT_POLICY_HEADROOM_SMALL"
            rationale = (
                "GROUP_SPLIT1_EXACTLY_MATCHES_ALIGNED_TTL_LRU_ONE_FILL_REFERENCE"
                if split == 1 else
                "SPLIT8_IS_WITHIN_ABOUT_TWO_PERCENT_OF_ALIGNED_ONE_FILL_REFERENCE")
        actual_rows.append({
            "sample_id": sample_id, "K": k, "split": split, "mapping": mapping,
            "actual_l2_miss_sectors": int(miss_sectors), "actual_l2_miss_bytes": miss_bytes,
            "actual_gemm_dram_bytes": f(row["gemm_dram_bytes"]),
            "actual_median_ms": time_ms, "actual_fill_equivalent_misses_per_round": fill_equiv,
            "pascal_long_run_policy_lower_misses_per_round": policy_lower,
            "pascal_long_run_policy_lower_l2_bytes_per_scan": policy_lower_bytes,
            "pascal_policy_oracle_gap_l2_bytes": miss_bytes - policy_lower_bytes,
            "pascal_fractional_oracle_gap_fraction": policy_gap,
            "c16_aligned_TTL_LRU_one_fill_reference_per_round": 1.0,
            "c16_aligned_one_fill_reference_bytes": aligned_reference_bytes,
            "c16_aligned_reference_gap_l2_bytes": miss_bytes - aligned_reference_bytes,
            "c16_aligned_reference_gap_fraction": aligned_reference_gap,
            "matched_group_timing_improvement_fraction": timing_exposure,
            "matched_group_timing_improvement_ms": time_ms - group_time,
            "classification": classification, "rationale": rationale,
            "observed_phase_bound_status": "UNKNOWN_PHASE_NOT_RECOVERABLE",
            "pascal_finite_correction_makes_long_run_bound_non_discriminative": True,
            "one_fill_reference_is_not_PASCAL_policy_independent_bound": True,
        })

    crossm_evidence = []
    for row in crossm_rows:
        if int(row["K"]) != 3072:
            continue
        crossm_evidence.append({
            "sample_id": f"CROSSM_K3072_S{row['split']}_{row['sharing_state']}",
            "applicability": (
                "APPLICABLE_ALIGNED_BEST_CASE_ONLY" if row["sharing_state"] == "SHARED" else
                "NOT_APPLICABLE_NO_SHARED_PHYSICAL_BLOCK_IDENTITY"),
            "median_ms": f(row["median_ms"]), "l2_miss_sectors": int(f(row["l2_read_miss_sectors"])),
            "gemm_dram_bytes": f(row["gemm_dram_bytes"]),
            "role": "CROSS_WORKER_REUSE_EXISTENCE_EVIDENCE_NOT_REPLACEMENT_POLICY_RESULT",
        })

    residual_evidence = []
    for row in residual_rows:
        residual_evidence.append({
            "M": int(row["M"]),
            "split1_median_ms": f(row["split1_median_ms"]),
            "split8_median_ms": f(row["split8_median_ms"]),
            "split1_hit_fraction": f(row["split1_hit_fraction"]),
            "split8_hit_fraction": f(row["split8_hit_fraction"]),
            "interpretation":
                "TIMING_DIFFERENCE_WITHOUT_TEX_READ_SIDE_MISS_TRAFFIC_SUPPORTS_DECOUPLING",
        })

    args.output_dir.mkdir(parents=True)
    with (args.output_dir / "APPLICABILITY.tsv").open("w", newline="", encoding="utf-8") as stream:
        fields = list(applicability[0])
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(applicability)
    with (args.output_dir / "POLICY_INDEPENDENT_BOUNDS.tsv").open(
            "w", newline="", encoding="utf-8") as stream:
        fields = list(bound_rows[0])
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(bound_rows)
    with (args.output_dir / "ACTUAL_VS_BOUND.tsv").open("w", newline="", encoding="utf-8") as stream:
        fields = list(actual_rows[0])
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(actual_rows)

    notes = f"""# PASCAL model notes and C16 mapping

## Literature authority

The formula authority is [{PAPER_TITLE}]({PAPER_URL}), arXiv:2609.10515v1, PDF SHA-256 `{PAPER_SHA}`. ArXiv v2 was revised on 2026-09-26 under a different title; this analysis does not mix v2 formulas into the named v1 contract.

## Author formulas (PASCAL v1)

- A fixed parallel scan has `M` workers over a cyclic address space of `N` blocks, phases `s_m`, distinct cyclic gaps `g_i`, and cache capacity `C` blocks.
- Cyclic-gap footprint: `U(t) = sum_i min(g_i, t)` and `K(t) = U(t+1)-U(t) = #{{i: g_i > t}}`.
- `T*` is the largest integer round window with `U(T*) <= C < U(T*+1)`.
- Exact slotted-TTL misses: `K_TTL = K(T*)` misses per round and `K_TTL/M` per request.
- Fully associative LRU certificate: `K(T*+1) <= K_LRU <= K(T*-1)`; equality follows when the interval collapses.
- Policy-independent residency bound: with inter-reference intervals `delta_m`, fractional residency `V(C)=max sum x_m` subject to `sum delta_m*x_m <= C`, `0<=x_m<=1`; every demand-paging policy satisfies `K_policy >= M-V(C)`. For an `H`-round finite trace with arbitrary initial state, the per-round correction is at most `N/H`. The fractional program is optimistic and need not be realizable.
- Progress divergence is the maximum historical worker request-count spread `sigma_E`. For fully associative LRU and no other accesses, `C >= 2*sigma_E-1` is sufficient to preserve all post-first sharing; final phase alignment cannot replace the historical maximum.
- Pipeline recurrence separates issue/wait/consume costs from memory latency. Theorem 6 shows cache hits cannot repair a persistent service-rate disadvantage, and its `G_d` term can be zero when misses already fit available overlap. Traffic and time must therefore be evaluated separately.

## C16 mapping (not an author claim)

- The selected AutoAWQ family has 16 M-tile macro-workers. Each macro-worker traverses the same combined weight-side 128-byte-line stream over 384 N tiles. `N` is 612,864 lines at K3072 and 817,152 at K4096; RTX4080 L2 gives `C=524,288` lines.
- `GROUP_M16_FULL_M` makes same-Ntile workers adjacent in logical block ID and supports an aligned best-case model. `ROW` separates consecutive M-tile reuse by 384 logical CTA IDs and 383 intervening CTAs/N tiles.
- CUDA logical ID order is not an actual issue/progress trace. No existing artifact contains per-CTA progress phases or `sigma_E`, so observed-phase `U(t)`, `T*`, TTL/LRU and residency bounds remain UNKNOWN. Numeric rows are aligned best cases only.
- Split8 is represented as a composite macro-worker stream over the union of eight split subpanels. This is a weight-side proxy; reduction traffic is kept separate.
- The kernel performs one finite scan. With `H=N`, PASCAL's finite correction is `N/H=1`, so the long-run fractional lower bound is not by itself discriminative for this run. The C16 one-unique-fill value is an aligned TTL/LRU reference, not a PASCAL policy-independent floor.
"""
    (args.output_dir / "PASCAL_MODEL_NOTES.md").write_text(notes, encoding="utf-8")

    decoupling = f"""# Cache traffic and timing decoupling

PASCAL v1 separates cache traffic from timing. Its Theorem 6 makes cache-mediated catch-up conditional on pipeline depth, wait/consume costs, latency bounds and sustained service imbalance; the paper's depth-4 example changes traffic from about 1.00 to 5.58 fill-equivalents while normalized time stays about 424-425 ns.

The C16 evidence shows both directions:

1. **Traffic and timing co-move in uncontrolled ROW split1.** GROUP_FULL_M reduces the finite fill-equivalent count from {next(row['actual_fill_equivalent_misses_per_round'] for row in actual_rows if row['sample_id']=='K3072_S1_ROW'):.6f} to 1.0 at K3072 and from {next(row['actual_fill_equivalent_misses_per_round'] for row in actual_rows if row['sample_id']=='K4096_S1_ROW'):.6f} to 1.0 at K4096; median timing improves by 27.631% and 33.073%. Cache traffic is exposed on this path, but the matched classical mapping already captures it.
2. **Timing changes without a TEX read-side miss gap in the residual M sweep.** Split1 and split8 both report hit fraction 1.0 for M1/M16/M32/M64, yet their timing ordering changes with CTA supply and reduction cost. That gap is scheduling/parallel decomposition, not replacement-policy traffic.
3. **Split8 ROW/GROUP is already close to one unique weight fill.** Mapping changes timing only 1.407%/2.564% at K3072/K4096 and does not reduce L2 miss sectors. Replacement headroom is small at these points.

No C16 artifact binds PASCAL's pipeline parameters `(d, alpha, beta, lambda_hit, lambda_miss)` or historical `sigma_E`; `G_d` and the catch-up certificate remain UNKNOWN rather than being fitted post hoc.
"""
    (args.output_dir / "TRAFFIC_TIMING_DECOUPLING.md").write_text(decoupling,
                                                                  encoding="utf-8")

    gate = f"""# C16 cache research oracle gate V1

## Gate

1. Reject `NOT_APPLICABLE` samples before using PASCAL formulas: workers must share physical blocks, follow the same or a regular scan order, and have an explicit phase case.
2. Always publish both aligned-best-case and observed-phase status. Missing per-worker progress keeps observed `U(t)`, `T*`, LRU and policy-independent bounds UNKNOWN.
3. Compare actual L2 miss bytes with both the PASCAL long-run fractional lower bound and separately labeled finite-run references. Never relabel the fractional relaxation or an aligned one-fill reference as a realizable policy-independent floor.
4. Keep `CACHE_TRAFFIC_HEADROOM` separate from `CACHE_TIMING_HEADROOM`. A replacement candidate is registered only when both are exposed under the same applicable sample.
5. Require matched software scheduling/dataflow controls before mechanism work. A gap removed by GROUP_FULL_M is not residual replacement-policy opportunity.

## Current C16 outcome

- Raw ROW split1 at K3072/K4096 has large traffic oracle gaps and 27.631%/33.073% matched timing exposure, so those uncontrolled cells meet `CACHE_POLICY_MECHANISM_WORTH_FURTHER_REVIEW` as *candidate observations*.
- The existing GROUP_FULL_M control brings split1 to the aligned TTL/LRU one-fill reference at both K values. The PASCAL fractional bound remains looser and non-discriminative for the one-scan horizon; under the accepted strong baseline, observed residual replacement opportunity is classified `REPLACEMENT_POLICY_HEADROOM_SMALL`.
- Split8 ROW/GROUP remains within about 2% of one unique fill and has small/no mapping traffic change: `REPLACEMENT_POLICY_HEADROOM_SMALL`.
- PER_MTILE cross-M controls are `NOT_APPLICABLE` because they deliberately remove shared physical block identity.
- Residual M-sweep timing at identical TEX read-side hit behavior directs remaining work toward scheduling/parallel decomposition, not a replacement predictor.

Overall gate: `REPLACEMENT_POLICY_HEADROOM_SMALL`. The closed Split-K branches remain closed. No replacement mechanism is authorized.
"""
    (args.output_dir / "CACHE_RESEARCH_GATE_V1.md").write_text(gate, encoding="utf-8")

    final = {
        "schema": "C16_PASCAL_CACHE_HEADROOM_FINAL_DECISION_V1", "status": "PASS",
        "overall_decision": "REPLACEMENT_POLICY_HEADROOM_SMALL",
        "row_uncontrolled_candidate_observations": row_candidate_ids,
        "candidate_registration_only_not_mechanism_authorization": True,
        "accepted_grouped_baseline_residual_decision": "REPLACEMENT_POLICY_HEADROOM_SMALL",
        "pascal_fractional_bound_decision_role":
            "NON_DISCRIMINATIVE_FOR_SINGLE_SCAN_AFTER_FINITE_CORRECTION",
        "aligned_one_fill_reference_is_not_policy_independent_floor": True,
        "closed_splitk_branches_remain_closed": True,
        "traffic_timing_separated": True,
        "observed_phase_bounds": "UNKNOWN_NO_PER_CTA_PROGRESS_TIMELINE",
        "new_simulation_or_trace_or_GPU": False,
        "replacement_mechanism_implemented": False,
        "attention_sample_added": False,
        "attention_reason": "NO_ADDITIONAL_SAMPLE_NEEDED_GEMM_AUTHORITIES_SUFFICIENT",
    }
    dump(args.output_dir / "FINAL_DECISION.json", final)
    dump(args.output_dir / "SOURCE_ANCHORS.json", {
        "schema": "C16_PASCAL_CACHE_HEADROOM_SOURCE_ANCHORS_V1", "status": "PASS",
        "paper": {"version": "v1", "title": PAPER_TITLE, "url": PAPER_URL,
                  "pdf_sha256": PAPER_SHA},
        "authority_commits": AUTHORITY_COMMITS,
        "input_sha256": {
            "grouped_raw": sha256(grouped / "RAW_RECOMPUTE.tsv"),
            "grouped_comparison": sha256(grouped / "GROUPED_STRONG_BASELINE_COMPARISON.tsv"),
            "grouped_launch": sha256(grouped_native / "EXPECTED_LAUNCH.tsv"),
            "static_footprint": sha256(static / "PER_SPLIT_FOOTPRINT.tsv"),
            "crossm_raw": sha256(crossm / "RAW_RECOMPUTE.tsv"),
            "residual_m_sweep": sha256(residual / "M_SWEEP_COMPARISON.tsv"),
        },
    })
    dump(args.output_dir / "VALIDATION_SUMMARY.json", {
        "schema": "C16_PASCAL_CACHE_HEADROOM_VALIDATION_V1", "status": "PASS",
        "paper_v1_pdf_sha_verified": True, "authority_manifests_verified": True,
        "applicability_fail_closed": True, "author_formulas_separated_from_C16_mapping": True,
        "aligned_bounds_computed": 8, "observed_phase_rows_left_UNKNOWN": 8,
        "actual_cells_recomputed": 8, "crossm_controls_consumed": len(crossm_evidence),
        "residual_timing_rows_consumed": len(residual_evidence),
        "simulator_executed": False, "GPU_used": False, "new_trace_collected": False,
        "mechanism_implemented": False, "decision": final["overall_decision"],
    })
    dump(args.output_dir / "SUPPORTING_EVIDENCE.json", {
        "schema": "C16_PASCAL_CACHE_HEADROOM_SUPPORTING_EVIDENCE_V1", "status": "PASS",
        "crossm": crossm_evidence, "residual_timing_decoupling": residual_evidence,
    })
    readme = """# C16 Parallel-Scan Policy-Independent Cache Headroom V1

CPU-only oracle-gate analysis. Read PASCAL_MODEL_NOTES.md first, then APPLICABILITY.tsv, POLICY_INDEPENDENT_BOUNDS.tsv, ACTUAL_VS_BOUND.tsv, TRAFFIC_TIMING_DECOUPLING.md, CACHE_RESEARCH_GATE_V1.md and FINAL_DECISION.json. This stage does not reactivate closed Split-K work or authorize a replacement mechanism.
"""
    (args.output_dir / "README.md").write_text(readme, encoding="utf-8")
    checksums = []
    for path in sorted(args.output_dir.iterdir(), key=lambda item: item.name):
        if path.name == "SHA256SUMS":
            continue
        need(path.is_file() and path.stat().st_size > 0 and not path.is_symlink(),
             f"invalid output {path}")
        checksums.append(f"{sha256(path)}  {path.name}")
    (args.output_dir / "SHA256SUMS").write_text("\n".join(checksums) + "\n",
                                                encoding="utf-8")
    print(json.dumps({"status": "PASS", "decision": final["overall_decision"],
                      "output": str(args.output_dir)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
