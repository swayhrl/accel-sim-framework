#!/usr/bin/env python3
"""Generate Lane-D causal-boundary rows from final compact D4 telemetry."""

from __future__ import annotations

import argparse
import csv
import pathlib
import sys


SCHEMA = "POST_FAST64_D6_ARROW_V1"
CLASSIFICATION = "POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT"


def read(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        result = list(csv.DictReader(handle, delimiter="\t"))
    if len(result) != 18:
        raise ValueError(f"D4 must contain exactly 18 rows, found {len(result)}")
    return result


def compact(value: str) -> str:
    return f"{float(value):.6g}"


def series(rows: dict[tuple[str, str, str], dict[str, str]], workload: str, mode: str, field: str) -> str:
    return " -> ".join(
        compact(rows[(workload, mode, point)][field]) for point in ("24", "32", "48")
    )


def cycles(rows: dict[tuple[str, str, str], dict[str, str]], workload: str, mode: str) -> str:
    return " -> ".join(rows[(workload, mode, point)]["cycles"] for point in ("24", "32", "48"))


def write(path: pathlib.Path, data: list[dict[str, str]], overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise ValueError(f"refusing to overwrite: {path}")
    mode = "w" if overwrite else "x"
    with path.open(mode, encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--d4", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        d4 = read(args.d4)
        keyed = {(r["workload"], r["mode"], r["physical_pool_kib"]): r for r in d4}
        if len(keyed) != 18:
            raise ValueError("D4 workload/mode/pool keys are not unique")
        required = {(w, m, p) for w in ("BICG", "GESUMMV", "Btree") for m in ("IO", "OO") for p in ("24", "32", "48")}
        if set(keyed) != required:
            raise ValueError("D4 is not the exact 3x2x3 final matrix")

        def row(arrow: str, verdict: str, scope: str, evidence: str, boundary: str) -> dict[str, str]:
            return {
                "schema": SCHEMA,
                "classification": CLASSIFICATION,
                "mechanism_arrow": arrow,
                "verdict": verdict,
                "evidence_scope": scope,
                "evidence_or_source": evidence,
                "interpretation_boundary": boundary,
            }

        data = [
            row(
                "physical_pool_size -> end_to_end_measured_behavior",
                "MEASURED_CORRELATION",
                "CONTROLLED_ONE_FACTOR_D4_CAPACITY_SWEEP_24_32_48_KIB",
                "Capacity is deliberately varied with frozen workload/trace/unrelated configuration. "
                f"BICG IO cycles={cycles(keyed, 'BICG', 'IO')}; GESUMMV IO cycles={cycles(keyed, 'GESUMMV', 'IO')}; "
                f"Btree IO cycles={cycles(keyed, 'Btree', 'IO')}.",
                "This establishes workload-dependent end-to-end sensitivity to the controlled capacity change; it does not identify internal mediators.",
            ),
            row(
                "physical_pool_size -> pool_full_time_exposure",
                "MEASURED_CORRELATION",
                "CONTROLLED_ONE_FACTOR_D4_CAPACITY_SWEEP_24_32_48_KIB",
                "physical_full_sample_fraction 24->32->48: "
                f"BICG IO={series(keyed, 'BICG', 'IO', 'physical_full_sample_fraction')}, OO={series(keyed, 'BICG', 'OO', 'physical_full_sample_fraction')}; "
                f"GESUMMV IO={series(keyed, 'GESUMMV', 'IO', 'physical_full_sample_fraction')}, OO={series(keyed, 'GESUMMV', 'OO', 'physical_full_sample_fraction')}.",
                "At 48 KiB pool-full time exposure falls substantially for BICG/GESUMMV, especially in OO; Btree remains a zero-full control. This is distinct from accumulated retry burden per instruction.",
            ),
            row(
                "physical_pool_size -> IO_no_free_events_per_active_SM_cycle",
                "MEASURED_CORRELATION",
                "CONTROLLED_ONE_FACTOR_D4_CAPACITY_SWEEP_IO_ONLY",
                "IO no-free events/active-SM-cycle 24->32->48: "
                f"BICG={series(keyed, 'BICG', 'IO', 'no_free_events_per_active_sm_cycle')}; "
                f"GESUMMV={series(keyed, 'GESUMMV', 'IO', 'no_free_events_per_active_sm_cycle')}.",
                "IO time-exposure rate falls at 48 KiB. Whole-line OO has no emitted compact no-free counter and is not imputed.",
            ),
            row(
                "larger_pool -> cumulative_no_free_burden_per_instruction",
                "NOT_SUPPORTED",
                "CONTROLLED_ONE_FACTOR_D4_CAPACITY_SWEEP_IO_ONLY",
                "IO no-free events/instruction 24->32->48: "
                f"BICG={series(keyed, 'BICG', 'IO', 'no_free_physical_events_per_instruction')}; "
                f"GESUMMV={series(keyed, 'GESUMMV', 'IO', 'no_free_physical_events_per_instruction')}.",
                "The claim that a larger pool lowers accumulated no-free burden per completed instruction is not supported. Program-work burden need not follow time exposure because runtime changes.",
            ),
            row(
                "physical_occupancy_or_pool_full_exposure -> lower_inflight_concurrency",
                "MEASURED_CORRELATION",
                "D4_INTERNAL_MEDIATORS",
                "Average allocated lines/inflight co-vary over local BICG/GESUMMV capacity points; Btree is invariant.",
                "Capacity is controlled, but neither mediator is independently intervened on; direction is not identified.",
            ),
            row(
                "lower_inflight_concurrency -> L2_miss_or_reservation_pressure",
                "MEASURED_CORRELATION",
                "D4_INTERNAL_MEDIATORS",
                "BICG/GESUMMV local larger-pool points jointly change inflight exposure and L2 miss/reservation-fail rates.",
                "No mediator-only intervention establishes direction or relative contribution.",
            ),
            row(
                "L2_miss_or_reservation_pressure -> alloc_to_ready_pending_lifetime",
                "MEASURED_CORRELATION",
                "D4_INTERNAL_MEDIATORS",
                "BICG IO misses/lower and alloc-to-ready cycles: "
                f"{series(keyed, 'BICG', 'IO', 'l2_misses_per_lower')} / {series(keyed, 'BICG', 'IO', 'alloc_to_ready_average_cycles')}; "
                "GESUMMV IO: "
                f"{series(keyed, 'GESUMMV', 'IO', 'l2_misses_per_lower')} / {series(keyed, 'GESUMMV', 'IO', 'alloc_to_ready_average_cycles')}.",
                "The controlled sweep supports co-variation, not L2 pressure as the independently proven cause of lifetime.",
            ),
            row(
                "alloc_to_ready_pending_lifetime -> pending_tag_eviction",
                "INSUFFICIENT",
                "D4_INTERNAL_MEDIATORS",
                "Pending-Tag-evictions per lower are not uniformly monotonic with lifetime, including BICG OO at 48 KiB.",
                "No per-allocation causal linkage or mediator intervention is measured.",
            ),
            row(
                "pending_tag_eviction -> duplicate_lower_request_traffic",
                "SOURCE_PROVEN",
                "LANE_C_IO_SOURCE_AUDIT_AND_OO_DUPLICATE_COUNTER_SEMANTICS",
                "Pending Tag eviction of a not-ready logical line is recorded; successful same-line reallocation erases that record, increments the exact duplicate counter, and creates the lower request.",
                "Exact transition semantics; it neither establishes frequency nor attributes performance.",
            ),
            row(
                "duplicate_lower_request_traffic -> performance",
                "NOT_SUPPORTED",
                "D4_D5_AND_ACCEPTED_FAST64_SPEEDUPS",
                "Duplicates co-vary with occupancy, inflight work, L2 pressure, reservation failures, and lifetimes; no duplicate-only intervention exists.",
                "No recoverable-performance estimate or primary-limiter attribution is made.",
            ),
            row(
                "OO_pending_tag_eviction -> deferred_physical_lifetime",
                "SOURCE_PROVEN",
                "OO_DUPLICATE_COUNTER_SEMANTICS_AND_OBSERVER_COUNTER_SEMANTICS",
                "A pending OO Tag eviction creates the generation-keyed deferred-eviction observer interval.",
                "Exact state/observer semantics, not a duration or performance causal claim.",
            ),
            row(
                "OO_deferred_physical_lifetime -> final_reclaim",
                "SOURCE_PROVEN",
                "OO_DUPLICATE_COUNTER_SEMANTICS",
                "The generation-matched deferred interval closes at final reclaim; stale/recycled identities cannot match.",
                "Source-defined lifecycle only.",
            ),
            row(
                "OO_final_reclaim -> exposed_concurrency",
                "INSUFFICIENT",
                "D4_INTERNAL_MEDIATORS",
                "OO deferred/reclaim lifetime and in-flight exposure co-vary at some BICG/GESUMMV points.",
                "No final-reclaim intervention establishes direction.",
            ),
            row(
                "exposed_concurrency -> performance",
                "NOT_SUPPORTED",
                "D4_INTERNAL_MEDIATORS",
                "BICG/GESUMMV cycles change with multiple mediators while Btree remains invariant.",
                "The data do not assign performance changes to concurrency alone.",
            ),
            row(
                "universal_larger_pool -> downstream_pressure_transfer",
                "NOT_SUPPORTED",
                "D4_CONTROL_AND_WORKLOAD_COMPARISON",
                "Btree is invariant/no-full at every point; BICG/GESUMMV responses are workload-dependent and non-monotonic.",
                "A universal statement is contradicted; local bottleneck-migration interpretation remains evidence-bounded.",
            ),
            row(
                "downstream_L2_pressure_primary_limiter_with_duplicate_feedback_secondary",
                "INSUFFICIENT",
                "INTEGRATED_D4_D5_EVIDENCE",
                "The sweep measures controlled capacity effects, L2/lifetime co-variation, and exact duplicate traffic, but no experiment ranks their mediator contributions.",
                "Consistent with bottleneck migration, not proof that L2 is dominant or duplicates secondary.",
            ),
        ]
        write(args.output, data, args.overwrite)
        print("POST_FAST64_D6_ANALYSIS_PASS\trows=" + str(len(data)))
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"POST_FAST64_D6_ANALYSIS_ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
