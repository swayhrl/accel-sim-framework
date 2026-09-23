#!/usr/bin/env python3
"""Independent native-timing and pressure-dose consumer for C16 E1.

This module consumes raw per-repetition producer rows.  Producer summaries are
never used as calculation authority.  The parser deliberately fails closed on
identity ambiguity, missing/duplicate samples, SHA drift, and invalid values.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


EXPECTED_REPS = 7
MIB = 1024 * 1024
STATES = (
    "WARM_A",
    "SPARSE_PAGE_PRESSURE",
    "DENSE_MEMORY_PRESSURE",
    "WARM_B",
)
DOSES_MIB = (0, 16, 32, 64, 128, 256)
DOSE_IMPLEMENTATIONS = ("RAW_FP16", "AWQ_FP16_INPUT")
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
PRIMARY_TEXT_POINTS = frozenset(
    {
        ("TEXT", "q_proj", 1, "RAW_FP16"),
        ("TEXT", "q_proj", 1, "AWQ_FP16_INPUT"),
        ("TEXT", "down_proj", 1, "RAW_FP16"),
        ("TEXT", "down_proj", 1, "AWQ_FP16_INPUT"),
        ("TEXT", "up_proj", 1, "RAW_FP16"),
        ("TEXT", "up_proj", 1, "AWQ_FP16_INPUT"),
        ("TEXT", "up_proj", 256, "RAW_FP16"),
        ("TEXT", "up_proj", 256, "AWQ_FP16_INPUT"),
    }
)

# DESIGN supplies the 5% timing threshold and 1 MiB/2x DRAM materiality
# thresholds.  It does not numerically define "DENSE exceeds SPARSE
# materially".  These two rules are the consumer's fail-closed,
# pre-registered operationalization; callers receive the rule in every result.
DENSE_SPECIFIC_TIMING_MARGIN = 0.05
DENSE_SPECIFIC_DRAM_RATIO = 2.0
DENSE_SPECIFIC_DRAM_DELTA_BYTES = MIB


class ContractError(ValueError):
    """Producer evidence does not satisfy the consumer contract."""


def _first(row: Mapping[str, Any], names: Sequence[str], label: str) -> Any:
    for name in names:
        if name in row and row[name] is not None and str(row[name]).strip() != "":
            return row[name]
    raise ContractError(f"missing {label} (accepted columns: {', '.join(names)})")


def _optional(row: Mapping[str, Any], names: Sequence[str], default: str) -> str:
    for name in names:
        if name in row and row[name] is not None and str(row[name]).strip() != "":
            return str(row[name]).strip()
    return default


def _integer(value: Any, label: str) -> int:
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ContractError(f"invalid {label}: {value!r}") from exc
    if str(value).strip() not in (str(parsed), f"{parsed}.0"):
        raise ContractError(f"non-integral {label}: {value!r}")
    return parsed


def _positive_finite(value: Any, label: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ContractError(f"invalid {label}: {value!r}") from exc
    if not math.isfinite(parsed) or parsed <= 0:
        raise ContractError(f"nonpositive/nonfinite {label}: {value!r}")
    return parsed


def _nonnegative_finite(value: Any, label: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ContractError(f"invalid {label}: {value!r}") from exc
    if not math.isfinite(parsed) or parsed < 0:
        raise ContractError(f"negative/nonfinite {label}: {value!r}")
    return parsed


def _sha(value: Any, label: str) -> str:
    parsed = str(value).strip().lower()
    if not SHA256_RE.fullmatch(parsed):
        raise ContractError(f"invalid {label}: expected 64 hex characters")
    return parsed


def _point_identity(row: Mapping[str, Any]) -> tuple[str, str, int, str]:
    domain = _optional(row, ("domain", "input_domain", "workload"), "TEXT").upper()
    role = str(_first(row, ("role", "operator_role"), "role")).strip()
    matrix_m = _integer(_first(row, ("M", "m"), "M"), "M")
    implementation = str(
        _first(row, ("implementation", "impl"), "implementation")
    ).strip()
    if not domain or not role or matrix_m <= 0 or not implementation:
        raise ContractError("invalid target point identity")
    return domain, role, matrix_m, implementation


def _identity_json(key: tuple[str, str, int, str]) -> dict[str, Any]:
    return {
        "domain": key[0],
        "role": key[1],
        "M": key[2],
        "implementation": key[3],
    }


def _statistics(rep_samples: Sequence[tuple[int, float]]) -> dict[str, Any]:
    values = [sample for _, sample in sorted(rep_samples)]
    if not values or any(not math.isfinite(value) or value <= 0 for value in values):
        raise ContractError("nonpositive/nonfinite timing sample")
    mean = statistics.fmean(values)
    return {
        "sample_count": len(values),
        "samples_ms": values,
        "min_ms": min(values),
        "median_ms": statistics.median(values),
        "max_ms": max(values),
        "mean_ms": mean,
        "cv": statistics.pstdev(values) / mean,
    }


def _combined_cv(*state_stats: Mapping[str, Any]) -> float:
    return math.sqrt(sum(float(item["cv"]) ** 2 for item in state_stats))


def analyze_timing_rows(
    rows: Iterable[Mapping[str, Any]],
    expected_reps: int = EXPECTED_REPS,
    expected_points: frozenset[tuple[str, str, int, str]] = PRIMARY_TEXT_POINTS,
) -> dict[str, Any]:
    """Validate and independently summarize raw WARM/SPARSE/DENSE/WARM rows."""
    if expected_reps <= 0:
        raise ContractError("expected_reps must be positive")

    grouped: dict[
        tuple[str, str, int, str], dict[str, list[tuple[int, float]]]
    ] = defaultdict(lambda: defaultdict(list))
    point_shas: dict[tuple[str, str, int, str], tuple[str, str]] = {}
    semantic_input_shas: dict[tuple[str, str, int], str] = {}
    seen: set[tuple[str, str, int, str, str, int]] = set()
    row_count = 0

    for row in rows:
        row_count += 1
        point = _point_identity(row)
        state = str(_first(row, ("state", "intervention_state"), "state")).strip()
        if state not in STATES:
            raise ContractError(f"invalid intervention state: {state!r}")
        rep = _integer(_first(row, ("rep", "repetition"), "rep"), "rep")
        if rep < 0:
            raise ContractError("rep must be nonnegative")
        unique = (*point, state, rep)
        if unique in seen:
            raise ContractError(f"duplicate point/state/rep: {unique!r}")
        seen.add(unique)

        timing_ms = _positive_finite(
            _first(row, ("timing_ms", "target_ms", "elapsed_ms"), "timing_ms"),
            "timing_ms",
        )
        input_sha = _sha(
            _first(
                row,
                ("input_sha256", "target_input_sha256", "activation_sha256"),
                "input SHA256",
            ),
            "input SHA256",
        )
        output_sha = _sha(
            _first(row, ("output_sha256", "target_output_sha256"), "output SHA256"),
            "output SHA256",
        )
        pair = (input_sha, output_sha)
        if point in point_shas and point_shas[point] != pair:
            raise ContractError(f"input/output SHA mismatch within target point: {point!r}")
        point_shas[point] = pair
        semantic_point = point[:3]
        if (
            semantic_point in semantic_input_shas
            and semantic_input_shas[semantic_point] != input_sha
        ):
            raise ContractError(
                f"input SHA mismatch across implementations for {semantic_point!r}"
            )
        semantic_input_shas[semantic_point] = input_sha
        grouped[point][state].append((rep, timing_ms))

    if row_count == 0:
        raise ContractError("empty timing evidence")
    if set(grouped) != set(expected_points):
        missing = sorted(set(expected_points) - set(grouped))
        extra = sorted(set(grouped) - set(expected_points))
        raise ContractError(
            f"primary timing point matrix mismatch: missing={missing}, extra={extra}"
        )

    analyses = []
    for point in sorted(grouped):
        by_state = grouped[point]
        missing = sorted(set(STATES) - set(by_state))
        extra = sorted(set(by_state) - set(STATES))
        if missing or extra:
            raise ContractError(
                f"state matrix mismatch for {point!r}: missing={missing}, extra={extra}"
            )
        stats = {}
        for state in STATES:
            samples = by_state[state]
            if len(samples) != expected_reps:
                raise ContractError(
                    f"sample-count mismatch for {point!r}/{state}: "
                    f"expected {expected_reps}, got {len(samples)}"
                )
            stats[state] = _statistics(samples)

        warm = stats["WARM_A"]
        sparse = stats["SPARSE_PAGE_PRESSURE"]
        dense = stats["DENSE_MEMORY_PRESSURE"]
        warm_b = stats["WARM_B"]
        sparse_ratio = sparse["median_ms"] / warm["median_ms"]
        dense_ratio = dense["median_ms"] / warm["median_ms"]
        recovery_ratio = warm_b["median_ms"] / warm["median_ms"]
        sparse_effect = abs(sparse_ratio - 1.0)
        dense_effect = abs(dense_ratio - 1.0)
        recovery_effect = abs(recovery_ratio - 1.0)
        dense_dispersion = _combined_cv(warm, dense)
        sparse_dispersion = _combined_cv(warm, sparse)
        recovery_dispersion = _combined_cv(warm, warm_b)
        dense_specific_dispersion = _combined_cv(warm, sparse, dense)
        dense_specific_margin = dense_effect - sparse_effect

        material_dense = dense_effect >= 0.05 and dense_effect > dense_dispersion
        reversible = recovery_effect <= max(0.05, recovery_dispersion)
        dense_specific_timing = (
            dense_specific_margin >= DENSE_SPECIFIC_TIMING_MARGIN
            and dense_specific_margin > dense_specific_dispersion
        )
        input_sha, output_sha = point_shas[point]
        analyses.append(
            {
                "point": _identity_json(point),
                "input_sha256": input_sha,
                "output_sha256": output_sha,
                "state_statistics": stats,
                "ratios": {
                    "SPARSE_over_WARM_A": sparse_ratio,
                    "DENSE_over_WARM_A": dense_ratio,
                    "WARM_B_over_WARM_A": recovery_ratio,
                },
                "effects_abs": {
                    "SPARSE_vs_WARM_A": sparse_effect,
                    "DENSE_vs_WARM_A": dense_effect,
                    "WARM_B_vs_WARM_A": recovery_effect,
                },
                "combined_dispersion": {
                    "SPARSE_WARM_A": sparse_dispersion,
                    "DENSE_WARM_A": dense_dispersion,
                    "WARM_B_WARM_A": recovery_dispersion,
                    "DENSE_SPECIFIC_WARM_SPARSE_DENSE": dense_specific_dispersion,
                },
                "dense_specific_timing_margin": dense_specific_margin,
                "MATERIAL_TIMING_PERTURBATION": material_dense,
                "REVERSIBLE": reversible,
                "DENSE_SPECIFIC_TIMING": dense_specific_timing,
            }
        )

    return {
        "status": "PASS",
        "authority": "raw_per_repetition_timing_rows",
        "expected_repetitions_per_state": expected_reps,
        "point_count": len(analyses),
        "required_primary_points": [
            _identity_json(point) for point in sorted(expected_points)
        ],
        "points": analyses,
        "rules": {
            "material_timing": (
                "abs(DENSE/WARM_A-1)>=0.05 and effect>sqrt(CV_WARM_A^2+CV_DENSE^2)"
            ),
            "recovery": (
                "abs(WARM_B/WARM_A-1)<=max(0.05,"
                "sqrt(CV_WARM_A^2+CV_WARM_B^2))"
            ),
            "dense_specific_timing": {
                "provenance": "consumer fail-closed pre-registered operationalization",
                "not_claimed_as_literal_design_threshold": True,
                "rule": (
                    "abs(DENSE/WARM_A-1)-abs(SPARSE/WARM_A-1)>=0.05 and "
                    "margin>sqrt(CV_WARM_A^2+CV_SPARSE^2+CV_DENSE^2)"
                ),
            },
        },
    }


def _rank(values: Sequence[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    index = 0
    while index < len(order):
        end = index + 1
        while end < len(order) and values[order[end]] == values[order[index]]:
            end += 1
        average_rank = (index + 1 + end) / 2.0
        for offset in range(index, end):
            ranks[order[offset]] = average_rank
        index = end
    return ranks


def _correlation(left: Sequence[float], right: Sequence[float]) -> float | None:
    left_mean = statistics.fmean(left)
    right_mean = statistics.fmean(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    left_ss = sum((a - left_mean) ** 2 for a in left)
    right_ss = sum((b - right_mean) ** 2 for b in right)
    denominator = math.sqrt(left_ss * right_ss)
    return numerator / denominator if denominator else None


def analyze_dose_rows(
    rows: Iterable[Mapping[str, Any]], expected_reps: int = EXPECTED_REPS
) -> dict[str, Any]:
    """Validate the exact up_proj M1 RAW/AWQ pressure-dose matrix."""
    if expected_reps <= 0:
        raise ContractError("expected_reps must be positive")
    grouped: dict[tuple[str, int], list[tuple[int, float]]] = defaultdict(list)
    seen: set[tuple[str, int, int]] = set()
    impl_shas: dict[str, tuple[str, str]] = {}
    row_count = 0

    for row in rows:
        row_count += 1
        domain, role, matrix_m, implementation = _point_identity(row)
        if domain != "TEXT" or role != "up_proj" or matrix_m != 1:
            raise ContractError(
                "dose evidence must be exactly TEXT/up_proj/M1"
            )
        if implementation not in DOSE_IMPLEMENTATIONS:
            raise ContractError(f"invalid dose implementation: {implementation!r}")
        dose = _integer(
            _first(row, ("dose_mib", "pressure_mib"), "dose_mib"), "dose_mib"
        )
        if dose not in DOSES_MIB:
            raise ContractError(f"invalid pressure dose: {dose} MiB")
        rep = _integer(_first(row, ("rep", "repetition"), "rep"), "rep")
        if rep < 0:
            raise ContractError("rep must be nonnegative")
        unique = (implementation, dose, rep)
        if unique in seen:
            raise ContractError(f"duplicate implementation/dose/rep: {unique!r}")
        seen.add(unique)
        timing_ms = _positive_finite(
            _first(row, ("timing_ms", "target_ms", "elapsed_ms"), "timing_ms"),
            "timing_ms",
        )
        input_sha = _sha(
            _first(
                row,
                ("input_sha256", "target_input_sha256", "activation_sha256"),
                "input SHA256",
            ),
            "input SHA256",
        )
        output_sha = _sha(
            _first(row, ("output_sha256", "target_output_sha256"), "output SHA256"),
            "output SHA256",
        )
        pair = (input_sha, output_sha)
        if implementation in impl_shas and impl_shas[implementation] != pair:
            raise ContractError(
                f"input/output SHA mismatch across doses for {implementation}"
            )
        impl_shas[implementation] = pair
        grouped[implementation, dose].append((rep, timing_ms))

    if row_count == 0:
        raise ContractError("empty dose evidence")
    expected_keys = {
        (implementation, dose)
        for implementation in DOSE_IMPLEMENTATIONS
        for dose in DOSES_MIB
    }
    if set(grouped) != expected_keys:
        missing = sorted(expected_keys - set(grouped))
        extra = sorted(set(grouped) - expected_keys)
        raise ContractError(f"dose matrix mismatch: missing={missing}, extra={extra}")

    implementations = []
    for implementation in DOSE_IMPLEMENTATIONS:
        stats_by_dose: dict[int, dict[str, Any]] = {}
        for dose in DOSES_MIB:
            samples = grouped[implementation, dose]
            if len(samples) != expected_reps:
                raise ContractError(
                    f"sample-count mismatch for {implementation}/{dose}MiB: "
                    f"expected {expected_reps}, got {len(samples)}"
                )
            stats_by_dose[dose] = _statistics(samples)
        baseline = stats_by_dose[0]
        doses = []
        medians = []
        for dose in DOSES_MIB:
            item = stats_by_dose[dose]
            ratio = item["median_ms"] / baseline["median_ms"]
            effect = abs(ratio - 1.0)
            dispersion = _combined_cv(baseline, item)
            doses.append(
                {
                    "dose_mib": dose,
                    **item,
                    "ratio_to_0MiB": ratio,
                    "effect_abs": effect,
                    "combined_dispersion_vs_0MiB": dispersion,
                    "material_vs_0MiB": effect >= 0.05 and effect > dispersion,
                }
            )
            medians.append(item["median_ms"])
        deltas = [right - left for left, right in zip(medians, medians[1:])]
        nondecreasing = all(delta >= 0 for delta in deltas)
        nonincreasing = all(delta <= 0 for delta in deltas)
        endpoint_direction = (
            "INCREASING"
            if medians[-1] > medians[0]
            else "DECREASING"
            if medians[-1] < medians[0]
            else "FLAT"
        )
        violations = []
        for index, delta in enumerate(deltas):
            violates = (
                endpoint_direction == "INCREASING" and delta < 0
            ) or (endpoint_direction == "DECREASING" and delta > 0)
            if violates:
                violations.append(
                    {
                        "from_mib": DOSES_MIB[index],
                        "to_mib": DOSES_MIB[index + 1],
                        "median_delta_ms": delta,
                    }
                )
        implementations.append(
            {
                "implementation": implementation,
                "input_sha256": impl_shas[implementation][0],
                "output_sha256": impl_shas[implementation][1],
                "doses": doses,
                "monotonicity_diagnostic": {
                    "is_pass_gate": False,
                    "nondecreasing_medians": nondecreasing,
                    "nonincreasing_medians": nonincreasing,
                    "endpoint_direction": endpoint_direction,
                    "endpoint_consistent_step_count": len(deltas) - len(violations),
                    "step_count": len(deltas),
                    "violations": violations,
                    "spearman_rho": _correlation(
                        _rank([float(value) for value in DOSES_MIB]),
                        _rank(medians),
                    ),
                },
            }
        )

    return {
        "status": "PASS",
        "authority": "raw_per_repetition_dose_timing_rows",
        "expected_repetitions_per_dose": expected_reps,
        "required_doses_mib": list(DOSES_MIB),
        "monotonicity_is_pass_gate": False,
        "implementations": implementations,
    }


def _find_primary_timing(timing_analysis: Mapping[str, Any]) -> Mapping[str, Any]:
    matches = []
    for item in timing_analysis.get("points", []):
        point = item.get("point", {})
        if (
            point.get("domain") == "TEXT"
            and point.get("role") == "up_proj"
            and int(point.get("M", -1)) == 1
            and point.get("implementation") == "AWQ_FP16_INPUT"
        ):
            matches.append(item)
    if len(matches) != 1:
        raise ContractError(
            f"expected exactly one TEXT/up_proj/M1/AWQ primary timing point, got {len(matches)}"
        )
    return matches[0]


def recompute_decision(
    timing_analysis: Mapping[str, Any], dram_bytes_by_state: Mapping[str, Any]
) -> dict[str, Any]:
    """Recompute all four booleans and the scoped intervention label."""
    if timing_analysis.get("status") != "PASS":
        raise ContractError("timing analysis is not PASS")
    primary = _find_primary_timing(timing_analysis)
    required_dram_states = (
        "WARM_A",
        "SPARSE_PAGE_PRESSURE",
        "DENSE_MEMORY_PRESSURE",
    )
    if set(dram_bytes_by_state) != set(required_dram_states):
        raise ContractError(
            "DRAM state identity must be exactly WARM_A/SPARSE_PAGE_PRESSURE/"
            "DENSE_MEMORY_PRESSURE"
        )
    dram = {
        state: _nonnegative_finite(dram_bytes_by_state[state], f"{state} DRAM bytes")
        for state in required_dram_states
    }
    warm = dram["WARM_A"]
    sparse = dram["SPARSE_PAGE_PRESSURE"]
    dense = dram["DENSE_MEMORY_PRESSURE"]
    material_timing = primary.get("MATERIAL_TIMING_PERTURBATION") is True
    material_dram = dense >= 2.0 * warm and dense - warm >= MIB
    reversible = primary.get("REVERSIBLE") is True
    dense_specific_timing = primary.get("DENSE_SPECIFIC_TIMING") is True
    dense_specific_dram = (
        dense >= DENSE_SPECIFIC_DRAM_RATIO * sparse
        and dense - sparse >= DENSE_SPECIFIC_DRAM_DELTA_BYTES
    )
    dense_specific = dense_specific_timing and dense_specific_dram

    if material_timing and material_dram and reversible and dense_specific:
        label = "RESIDENCY_INTERVENTION_STRONGLY_SUPPORTED"
    elif material_timing or material_dram:
        label = "RESIDENCY_INTERVENTION_PARTIALLY_SUPPORTED"
    else:
        label = "RESIDENCY_INTERVENTION_NOT_SUPPORTED"
    return {
        "status": "PASS",
        "scope": "tested cache/memory-state intervention only",
        "primary_point": primary["point"],
        "MATERIAL_TIMING_PERTURBATION": material_timing,
        "MATERIAL_DRAM_PERTURBATION": material_dram,
        "REVERSIBLE": reversible,
        "DENSE_SPECIFIC_TIMING": dense_specific_timing,
        "DENSE_SPECIFIC_DRAM": dense_specific_dram,
        "DENSE_SPECIFIC": dense_specific,
        "scope_label": label,
        "dram_bytes": dram,
        "dram_ratios": {
            "DENSE_over_WARM_A": dense / warm if warm else None,
            "SPARSE_over_WARM_A": sparse / warm if warm else None,
            "DENSE_over_SPARSE": dense / sparse if sparse else None,
        },
        "rules": {
            "label_truth_table": {
                "provenance": "consumer fail-closed pre-registered operationalization",
                "strong": "all four primary booleans true",
                "partial": (
                    "MATERIAL_TIMING_PERTURBATION or MATERIAL_DRAM_PERTURBATION, "
                    "unless strong"
                ),
                "not_supported": "both material perturbation booleans false",
            },
            "dense_specific_dram": {
                "provenance": "consumer fail-closed pre-registered operationalization",
                "not_claimed_as_literal_design_threshold": True,
                "rule": "DENSE>=2*SPARSE and DENSE-SPARSE>=1MiB",
            },
        },
        "interpretation_boundary": (
            "At most: controlled memory-state intervention supports a cache-line "
            "residency contribution under tested points. This does not exclude TLB, "
            "establish L2 as the sole cause, or authorize a mechanism."
        ),
    }


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    timing = subparsers.add_parser("timing")
    timing.add_argument("--raw-tsv", type=Path, required=True)
    timing.add_argument("--out", type=Path, required=True)
    dose = subparsers.add_parser("dose")
    dose.add_argument("--raw-tsv", type=Path, required=True)
    dose.add_argument("--out", type=Path, required=True)
    decision = subparsers.add_parser("decision")
    decision.add_argument("--timing-analysis", type=Path, required=True)
    decision.add_argument(
        "--dram-json",
        type=Path,
        required=True,
        help="JSON object mapping exact intervention state to independent DRAM-byte sum",
    )
    decision.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "timing":
        result = analyze_timing_rows(load_tsv(args.raw_tsv))
    elif args.command == "dose":
        result = analyze_dose_rows(load_tsv(args.raw_tsv))
    else:
        timing_payload = json.loads(args.timing_analysis.read_text(encoding="utf-8"))
        dram_payload = json.loads(args.dram_json.read_text(encoding="utf-8"))
        result = recompute_decision(timing_payload, dram_payload)
    _write_json(args.out, result)
    print(json.dumps({"status": "PASS", "command": args.command}, sort_keys=True))


if __name__ == "__main__":
    main()
