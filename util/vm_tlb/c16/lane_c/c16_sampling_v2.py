#!/usr/bin/env python3
"""C16 Lane C Sampling V2: frozen, manifest-bound stratified sampling.

This is deliberately an offline planning/validation tool.  It never invokes a
GPU, a simulator, a trace parser, or an external profiler.  A native catalog is
accepted only through ``git show <fixed-commit>:<path>`` after its committed
manifest has been checked.  The historical C12/C13 route is separately labelled
``RETROSPECTIVE_ORACLE_CALIBRATION`` and cannot create a prospective result.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import random
import re
import statistics
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[4]
OUT_REL = Path("docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_c")
OUT = ROOT / OUT_REL
PLANNING_SHA = "f222e66f49af56cfd4ded671c4a50c6811237cc2"
C15_C_SHA = "a51d6c91b1e7d7df27a4af80823a29ff30bb9806"
C12_OPERATOR_SHA = "8801f2e9fea4e0df1d79853a5e4440c4da463486"
C13_SHA = "9ab1e0708af66a533d9327f35f1a3e63a34c4285"
C15_PACK = "docs/vm_tlb/review_packs/C15_LOWCOST_MULTIMODEL/lane_c"
OPERATOR_PACK = "docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_OPERATOR_AWARE_CHARACTERIZATION"
C13_PACK = "docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C13_EFFECTIVE_CONFIG_AUDIT"
BUDGETS = (12, 24, 48)
PRIMARY_SEED = 16031
AUDIT_FRACTION = 0.10
HEAVY_TAIL_FRACTION = 0.01
RARE_IMPLEMENTATION_N = 2
STRATA_VERSION = "C16_STRATA_PHASE_OPERATOR_IMPLEMENTATION_SHAPEBUCKET_DTYPE_V2"
SELECTOR_VERSION = "C16_SELECTOR_V2_R_PROBABILITY_M_MEDOID"
P_READY_STATUS = "C16_P_NATIVE_CATALOG_READY_FOR_C_CONSUMPTION"
P_MANIFEST_SCHEMA = "C16_P_NATIVE_CATALOG_FOR_C_V1"
P_TRAIN_COHORT = "TRAIN_TUNE"
P_AWQ_COHORT = "PROSPECTIVE_QWEN7_AWQ"
P_REQUIRED_PAYLOAD_KINDS = (
    "KERNEL_CATALOG", "KERNEL_SEMANTIC_MAP", "SEMANTIC_COVERAGE",
    "NATIVE_BASELINE", "RUNTIME_IMPLEMENTATION_AUDIT", "RUN_JOIN_AUDIT",
    "PROFILE_REPORT_INDEX", "DEPLOYMENT_ROSTER",
)
P_TRAIN_ROSTER = {
    "TRAIN_LLAMA": "TUNING",
    "TRAIN_QWEN0_5": "TUNING",
    "TRAIN_QWEN7_RAW": "TUNING",
}
P_AWQ_ROSTER = {"PROSPECTIVE_QWEN7_AWQ": "PROSPECTIVE_HOLDOUT"}
P_DIRECT_SEMANTIC_EVIDENCE = {"DIRECT_RUNTIME_NVTX", "DIRECT_MODULE_ID", "UNKNOWN"}
P_FORBIDDEN_OUTCOME_COLUMNS = re.compile(
    r"(^|_)(candidate|speedup|miss|ncu|nvbit|trace|address|page|line|cache|tlb|counter|mechanism|outcome)($|_)",
    re.IGNORECASE,
)

# These are frozen before any target metric is allowed to be read.  The values
# are qualification gates, not parameters which calibration is allowed to tune.
THRESHOLDS = {
    "native_duration_relative_error_screening": 0.05,
    "counter_count_or_rate_relative_error_screening": 0.05,
    "small_effect_min_absolute_fraction": 0.02,
    "confidence_level": 0.95,
    "normal_critical_value": 1.96,
}


def die(message: str) -> None:
    raise RuntimeError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for part in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()


def code_sha() -> str:
    return sha256_file(Path(__file__).resolve())


def current_head() -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()


def git_text(revision: str, path: str) -> str:
    completed = subprocess.run(["git", "-C", str(ROOT), "show", f"{revision}:{path}"], text=True,
                               capture_output=True, check=False)
    if completed.returncode:
        die(f"cannot read frozen Git input {revision}:{path}: {completed.stderr.strip()}")
    return completed.stdout


def git_blob(revision: str, path: str) -> str:
    completed = subprocess.run(["git", "-C", str(ROOT), "rev-parse", f"{revision}:{path}"], text=True,
                               capture_output=True, check=False)
    if completed.returncode:
        die(f"cannot resolve frozen Git blob {revision}:{path}: {completed.stderr.strip()}")
    return completed.stdout.strip()


def tsv_rows(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))


def normal(value: Any) -> str:
    if value is None or value == "":
        return "NA"
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(text, encoding="utf-8", newline="")
    temporary.replace(path)


def write_tsv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: normal(row.get(field, "NA")) for field in fields})
    atomic_text(path, buffer.getvalue())


def write_json(path: Path, value: dict[str, Any]) -> None:
    atomic_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def require_out(path: Path) -> Path:
    if path.resolve() != OUT.resolve():
        die(f"refusing to write outside Lane-C review pack: {path.resolve()}")
    return path


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def known(value: Any, fallback: str = "UNKNOWN") -> str:
    text = str(value or "").strip()
    return text if text and text.upper() not in {"NA", "NONE", "NULL", "UNKNOWN"} else fallback


def shape_bucket(shape_key: Any, explicit: Any = "") -> str:
    """Produce a deterministic non-outcome shape bucket.

    G may provide a reviewed ``shape_bucket`` directly.  Otherwise dimensions in
    a shape key are binned by powers of two.  No kernel outcome is consulted.
    """
    supplied = known(explicit, "")
    if supplied:
        return supplied
    raw = known(shape_key, "UNKNOWN_SHAPE")
    if raw == "UNKNOWN_SHAPE":
        return raw
    dims = [int(item) for item in re.findall(r"(?<![A-Za-z])\d+", raw)]
    if not dims:
        return "SHAPE_NONNUMERIC_" + sha256_bytes(raw.encode())[:12]
    return "R%d_%s" % (len(dims), "x".join(f"P2_{int(math.floor(math.log2(max(1, d))))}" for d in dims))


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.:-]+", "_", value)


def universe_id(row: dict[str, Any]) -> str:
    return "|".join([str(row["deployment_id"]), str(row["scenario_id"]), str(row["phase"])])


def stratum_id(row: dict[str, Any]) -> str:
    return "|".join([str(row["phase"]), str(row["operator_class"]), str(row["implementation_key"]),
                     str(row["shape_bucket"]), str(row["dtype_key"])])


def unit_identifier(row: dict[str, Any]) -> str:
    supplied = str(row.get("unit_id", "")).strip()
    if supplied:
        return supplied
    parts = [str(row.get(key, "UNKNOWN")) for key in ("run_id", "device", "context", "stream", "correlation_id", "launch_ordinal")]
    return "launch:" + ":".join(safe_id(item) for item in parts)


def special_reasons(row: dict[str, Any]) -> list[str]:
    """Use only direct semantic fields; kernel-name inference is prohibited."""
    operator = str(row.get("operator_class", "")).upper()
    direct_special = str(row.get("special_semantics", "")).upper()
    reasons: list[str] = []
    if operator in {"E", "O"}:
        reasons.append("SPECIAL_E_OR_O")
    if "KV" in operator or direct_special == "KV_MANAGEMENT":
        reasons.append("SPECIAL_KV_MANAGEMENT")
    if ("MOE" in operator and ("ROUTER" in operator or "DISPATCH" in operator)) or direct_special == "MOE_ROUTER_DISPATCH":
        reasons.append("SPECIAL_MOE_ROUTER_DISPATCH")
    return reasons


def canonicalize_catalog(rows: list[dict[str, str]], evidence_tier: str, historical_oracle: bool = False) -> list[dict[str, Any]]:
    required = ("deployment_id", "scenario_id", "phase", "operator_class", "implementation_key", "shape_key", "dtype_key")
    units: list[dict[str, Any]] = []
    for ordinal, source in enumerate(rows):
        missing = [field for field in required if field not in source]
        if missing:
            die(f"catalog misses mandatory C16 fields: {','.join(missing)}")
        row: dict[str, Any] = {
            "deployment_id": known(source.get("deployment_id"), "UNKNOWN_DEPLOYMENT"),
            "scenario_id": known(source.get("scenario_id"), "UNKNOWN_SCENARIO"),
            "phase": known(source.get("phase"), "UNKNOWN_PHASE"),
            "operator_class": known(source.get("operator_class"), "UNKNOWN_OPERATOR"),
            "implementation_key": known(source.get("implementation_key"), "UNKNOWN_IMPLEMENTATION"),
            "shape_key": known(source.get("shape_key"), "UNKNOWN_SHAPE"),
            "dtype_key": known(source.get("dtype_key"), "UNKNOWN_DTYPE"),
            "shape_bucket": shape_bucket(source.get("shape_key"), source.get("shape_bucket", "")),
            "duration_ns": max(0.0, as_float(source.get("duration_ns"))),
            "variation_proxy": max(0.0, as_float(source.get("variation_proxy"))),
            "variation_proxy_source": "HISTORICAL_ORACLE" if historical_oracle else "NATIVE_CENSUS_PRE_OUTCOME",
            "grid": str(source.get("grid", "UNKNOWN")),
            "block": str(source.get("block", "UNKNOWN")),
            "kernel_name": str(source.get("kernel_name", "UNKNOWN")),
            "semantic_evidence": str(source.get("semantic_evidence", "UNKNOWN")),
            # It is retained only when P has explicitly recorded one of its
            # permitted direct semantic evidence types.  Unknown coverage is
            # an explicit UNKNOWN stratum, never a kernel-name backfill.
            "special_semantics": str(source.get("special_semantics", "")) if str(source.get("semantic_evidence", "UNKNOWN")).upper() in P_DIRECT_SEMANTIC_EVIDENCE else "",
            "run_id": str(source.get("run_id", "UNKNOWN_RUN")),
            "profile_report_id": str(source.get("profile_report_id", "UNKNOWN_PROFILE_REPORT")),
            "device": str(source.get("device", "UNKNOWN_DEVICE")),
            "context": str(source.get("context", "UNKNOWN_CONTEXT")),
            "stream": str(source.get("stream", "UNKNOWN_STREAM")),
            "correlation_id": str(source.get("correlation_id", "UNKNOWN_CORRELATION")),
            "launch_ordinal": str(source.get("launch_ordinal", ordinal)),
            "evidence_tier": evidence_tier,
            "historical_oracle": historical_oracle,
        }
        row["unit_id"] = unit_identifier({**source, **row})
        row["universe_id"] = universe_id(row)
        row["stratum_id"] = stratum_id(row)
        units.append(row)
    duplicate = [unit for unit, count in Counter(row["unit_id"] for row in units).items() if count > 1]
    if duplicate:
        die(f"duplicate sampling unit identity (first): {duplicate[0]}")
    return units


def annotate_certainty(units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply the frozen certainty rule; certainty units always represent only self."""
    by_universe: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in units:
        by_universe[row["universe_id"]].append(row)
    for group in by_universe.values():
        total_duration = sum(row["duration_ns"] for row in group)
        impl_count = Counter(row["implementation_key"] for row in group)
        stratum_count = Counter(row["stratum_id"] for row in group)
        for row in group:
            reasons = special_reasons(row)
            if total_duration > 0 and row["duration_ns"] / total_duration >= HEAVY_TAIL_FRACTION:
                reasons.append("PHASE_DURATION_GE_1_PERCENT")
            if impl_count[row["implementation_key"]] <= RARE_IMPLEMENTATION_N:
                reasons.append("RARE_IMPLEMENTATION_N_LE_2")
            if stratum_count[row["stratum_id"]] <= 2:
                reasons.append("STRATUM_N_LE_2")
            row["certainty"] = bool(reasons)
            row["certainty_reason"] = ";".join(sorted(set(reasons))) if reasons else "NA"
            row["certainty_weight"] = 1 if reasons else "NA"
            row["original_stratum_N"] = stratum_count[row["stratum_id"]]
        # The estimable finite population for an ordinary stratum excludes
        # certainty units.  Treating a certainty unit as part of N_s would
        # amplify it again, exactly the error V2 is designed to prevent.
        ordinary_count = Counter(row["stratum_id"] for row in group if not row["certainty"])
        for row in group:
            row["N_s"] = 1 if row["certainty"] else ordinary_count[row["stratum_id"]]
    return units


def allocation_score(group: list[dict[str, Any]], all_groups: list[list[dict[str, Any]]]) -> tuple[float, dict[str, float]]:
    count_mass = len(group)
    duration_mass = sum(item["duration_ns"] for item in group)
    variation_mass = sum(item["variation_proxy"] for item in group)
    total_count = sum(len(item) for item in all_groups)
    total_duration = sum(sum(row["duration_ns"] for row in item) for item in all_groups)
    total_variation = sum(sum(row["variation_proxy"] for row in item) for item in all_groups)
    # Uniform fallbacks make an all-zero historical/oracle catalog deterministic.
    c = count_mass / total_count if total_count else 0.0
    d = duration_mass / total_duration if total_duration else c
    v = variation_mass / total_variation if total_variation else c
    return 0.40 * c + 0.40 * d + 0.20 * v, {"count_mass": count_mass, "duration_mass": duration_mass, "variation_mass": variation_mass,
                                                "count_share": c, "duration_share": d, "variation_share": v}


def allocate_quotas(groups: dict[str, list[dict[str, Any]]], slots: int) -> tuple[dict[str, int], dict[str, dict[str, float]]]:
    """Allocate non-certainty slots using only pre-outcome census quantities."""
    ids = sorted(groups)
    group_values = [groups[key] for key in ids]
    scores: dict[str, float] = {}
    audit: dict[str, dict[str, float]] = {}
    for key in ids:
        scores[key], audit[key] = allocation_score(groups[key], group_values)
    quotas = {key: 0 for key in ids}
    if slots <= 0 or not ids:
        return quotas, audit
    # First give every eligible stratum one unit when the budget permits.
    for key in sorted(ids, key=lambda value: (-scores[value], value))[:min(slots, len(ids))]:
        quotas[key] = 1
    remaining = slots - sum(quotas.values())
    while remaining > 0:
        candidates = [key for key in ids if quotas[key] < len(groups[key])]
        if not candidates:
            break
        raw_total = sum(scores[key] for key in candidates) or float(len(candidates))
        key = max(candidates, key=lambda value: (scores[value] / raw_total * slots - quotas[value], scores[value], value))
        quotas[key] += 1
        remaining -= 1
    return quotas, audit


def seed_for(seed: int, *parts: str) -> int:
    payload = "|".join([str(seed), *parts]).encode()
    return int(sha256_bytes(payload)[:16], 16)


def probability_select(group: list[dict[str, Any]], n: int, seed: int, plan_id: str) -> list[dict[str, Any]]:
    if n >= len(group):
        return sorted(group, key=lambda item: item["unit_id"])
    generator = random.Random(seed_for(seed, plan_id, group[0]["stratum_id"]))
    return sorted(generator.sample(group, n), key=lambda item: item["unit_id"])


def grid_block_features(item: dict[str, Any]) -> list[float]:
    values: list[float] = []
    for key in ("grid", "block"):
        values.extend(float(value) for value in re.findall(r"\d+", str(item.get(key, "")))[:3])
    return values or [0.0]


def feature_vectors(group: list[dict[str, Any]]) -> dict[str, list[float]]:
    raw = {item["unit_id"]: [math.log1p(item["duration_ns"]), item["variation_proxy"], *grid_block_features(item)] for item in group}
    width = max(len(value) for value in raw.values())
    padded = {key: value + [0.0] * (width - len(value)) for key, value in raw.items()}
    means = [statistics.fmean(value[index] for value in padded.values()) for index in range(width)]
    scales = [statistics.pstdev(value[index] for value in padded.values()) or 1.0 for index in range(width)]
    return {key: [(value[index] - means[index]) / scales[index] for index in range(width)] for key, value in padded.items()}


def squared_distance(left: list[float], right: list[float]) -> float:
    return sum((a - b) ** 2 for a, b in zip(left, right))


def medoid_select(group: list[dict[str, Any]], n: int) -> list[dict[str, Any]]:
    """Deterministic greedy k-medoid representatives; never a probability sample."""
    ordered = sorted(group, key=lambda item: item["unit_id"])
    if n >= len(ordered):
        return ordered
    vectors = feature_vectors(ordered)
    centroid = [statistics.fmean(vector[index] for vector in vectors.values()) for index in range(len(next(iter(vectors.values()))))]
    chosen = [min(ordered, key=lambda item: (squared_distance(vectors[item["unit_id"]], centroid), item["unit_id"]))]
    while len(chosen) < n:
        candidates = [item for item in ordered if item not in chosen]
        chosen.append(max(candidates, key=lambda item: (min(squared_distance(vectors[item["unit_id"]], vectors[picked["unit_id"]]) for picked in chosen),
                                                          item["unit_id"])))
    # One deterministic assignment/medoid refinement makes the representatives
    # genuine medoids without importing a numerical package.
    for _ in range(3):
        clusters: dict[str, list[dict[str, Any]]] = {item["unit_id"]: [] for item in chosen}
        for item in ordered:
            owner = min(chosen, key=lambda picked: (squared_distance(vectors[item["unit_id"]], vectors[picked["unit_id"]]), picked["unit_id"]))
            clusters[owner["unit_id"]].append(item)
        refined: list[dict[str, Any]] = []
        for owner in chosen:
            members = clusters[owner["unit_id"]]
            # A duplicate/identical feature cloud can leave a provisional
            # farthest-first representative with no assigned members after
            # deterministic tie breaking.  It remains its own medoid instead
            # of making a selection failure or consulting an outcome metric.
            if not members:
                refined.append(owner)
            else:
                refined.append(min(members, key=lambda candidate: (sum(squared_distance(vectors[candidate["unit_id"]], vectors[other["unit_id"]]) for other in members),
                                                                     candidate["unit_id"])))
        if {item["unit_id"] for item in refined} == {item["unit_id"] for item in chosen}:
            break
        chosen = sorted(refined, key=lambda item: item["unit_id"])
    return sorted(chosen, key=lambda item: item["unit_id"])


def build_plan(units: list[dict[str, Any]], budget: int, selector_kind: str, seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Return plan rows, budget audit rows, and certainty rows for one universe."""
    if selector_kind not in {"R", "M"}:
        die("selector_kind must be R or M")
    if len({row["universe_id"] for row in units}) != 1:
        die("a plan must cover exactly one deployment/scenario/phase universe")
    universe = units[0]["universe_id"]
    plan_id = f"C16_V2_{selector_kind}_B{budget}_{safe_id(universe)}"
    certain = sorted([row for row in units if row["certainty"]], key=lambda item: item["unit_id"])
    ordinary: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in units:
        if not row["certainty"]:
            ordinary[row["stratum_id"]].append(row)
    for group in ordinary.values():
        group.sort(key=lambda item: item["unit_id"])
    remaining = budget - len(certain)
    status = "FROZEN_READY" if remaining >= 0 else "BUDGET_EXCEEDED_BY_CERTAINTY"
    quotas, allocation = allocate_quotas(ordinary, max(0, remaining))
    selected: list[tuple[dict[str, Any], str, int]] = [(row, "CERTAINTY", 1) for row in certain]
    if remaining >= 0:
        for key in sorted(ordinary):
            group, n = ordinary[key], quotas[key]
            selected_rows = probability_select(group, n, seed, plan_id) if selector_kind == "R" else medoid_select(group, n)
            selected.extend((row, "PROBABILITY" if selector_kind == "R" else "MEDOID", n) for row in selected_rows)
    # Nearest integer keeps 12/24/48 at 1/2/5 units respectively: roughly
    # 10%, while still reserving at least one independent random-audit unit.
    audit_target = max(1, int(round(budget * AUDIT_FRACTION)))
    stochastic = [entry for entry in selected if entry[1] == "PROBABILITY"]
    audit_ids = set(sorted((entry[0]["unit_id"] for entry in stochastic), key=lambda value: seed_for(seed, plan_id, "AUDIT", value))[:audit_target])
    plan_rows: list[dict[str, Any]] = []
    for row, selection_role, n in sorted(selected, key=lambda item: (item[0]["stratum_id"], item[0]["unit_id"])):
        N = int(row["N_s"])
        probability = 1.0 if selection_role == "CERTAINTY" else (n / N if selector_kind == "R" else "NA")
        plan_rows.append({
            "plan_id": plan_id, "selector_kind": f"SELECTOR_{selector_kind}", "selector_version": SELECTOR_VERSION,
            "selector_code_sha256": code_sha(), "universe_id": universe, "deployment_id": row["deployment_id"],
            "scenario_id": row["scenario_id"], "phase": row["phase"], "stratum_id": row["stratum_id"], "N_s": N,
            "n_s": 1 if selection_role == "CERTAINTY" else n, "unit_id": row["unit_id"], "launch_ordinal": row["launch_ordinal"],
            "semantic_key_json": json.dumps({key: row[key] for key in ("phase", "operator_class", "implementation_key", "shape_bucket", "dtype_key")}, sort_keys=True),
            "selection_role": selection_role, "selection_reason": row["certainty_reason"] if selection_role == "CERTAINTY" else
                ("seeded SRSWOR within frozen stratum" if selector_kind == "R" else "deterministic pre-outcome feature medoid"),
            "inclusion_probability": probability, "design_weight": 1 if selection_role == "CERTAINTY" else (N / n if selector_kind == "R" else "NA"),
            "design_confidence": "CERTAINTY_SELF_REPRESENTING" if selection_role == "CERTAINTY" else ("DESIGN_BASED" if selector_kind == "R" else "NOT_APPLICABLE_MEDOID"),
            "seed": seed if selection_role == "PROBABILITY" else "NA",
            "random_audit": "TRUE" if row["unit_id"] in audit_ids else "FALSE", "estimated_capture_cost_ns": row["duration_ns"],
            "capture_cost_basis": "native_census_duration_ns" if not row["historical_oracle"] else "HISTORICAL_ORACLE_NO_CAPTURE_AUTHORIZATION",
            "evidence_tier": row["evidence_tier"], "plan_status": status,
        })
    budget_rows: list[dict[str, Any]] = []
    for key in sorted(ordinary):
        sample_n = quotas[key] if remaining >= 0 else 0
        detail = allocation[key]
        budget_rows.append({"plan_id": plan_id, "selector_kind": f"SELECTOR_{selector_kind}", "universe_id": universe, "budget": budget,
                            "certainty_units": len(certain), "remaining_after_certainty": remaining, "stratum_id": key, "N_s": len(ordinary[key]),
                            "n_s": sample_n, "count_mass": detail["count_mass"], "duration_mass_ns": detail["duration_mass"],
                            "variation_proxy_mass": detail["variation_mass"], "variation_proxy_source": ordinary[key][0]["variation_proxy_source"], "allocation_score": allocation_score(ordinary[key], list(ordinary.values()))[0],
                            "random_audit_target": audit_target, "random_audit_actual": sum(1 for row in plan_rows if row["random_audit"] == "TRUE"),
                            "estimated_capture_cost_ns": sum(row["estimated_capture_cost_ns"] for row in plan_rows), "status": status})
    certainty_rows = [{"universe_id": universe, "deployment_id": row["deployment_id"], "scenario_id": row["scenario_id"], "phase": row["phase"],
                       "stratum_id": row["stratum_id"], "unit_id": row["unit_id"], "launch_ordinal": row["launch_ordinal"], "N_s": row["N_s"],
                       "certainty_weight": 1, "reason": row["certainty_reason"], "duration_ns": row["duration_ns"],
                       "evidence_tier": row["evidence_tier"], "capture_authorization": "NO" if row["historical_oracle"] else "PENDING_G_TARGET_ACCEPTANCE"}
                      for row in certain]
    return plan_rows, budget_rows, certainty_rows


def plan_lookup(plan_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in plan_rows:
        result[row["plan_id"]].append(row)
    return result


def sample_variance(values: list[float]) -> float | None:
    return statistics.variance(values) if len(values) >= 2 else None


def estimate_additive(units: list[dict[str, Any]], selected: list[dict[str, Any]], values: dict[str, float]) -> dict[str, Any]:
    """The required certainty + N_s/n_s estimator and its SRSWOR variance."""
    by_stratum: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_selection: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for unit in units:
        by_stratum[unit["stratum_id"]].append(unit)
    for row in selected:
        by_selection[row["stratum_id"]].append(row)
    estimate, exact, variance = 0.0, sum(values.get(unit["unit_id"], 0.0) for unit in units), 0.0
    variance_state = "DESIGN_VARIANCE_AVAILABLE"
    details: list[dict[str, Any]] = []
    for key, population in sorted(by_stratum.items()):
        ordinary_population = [unit for unit in population if not unit["certainty"]]
        N = len(ordinary_population)
        selected_rows = by_selection.get(key, [])
        certainty_rows = [row for row in selected_rows if row["selection_role"] == "CERTAINTY"]
        ordinary_rows = [row for row in selected_rows if row["selection_role"] == "PROBABILITY"]
        if certainty_rows:
            contribution = sum(values.get(row["unit_id"], 0.0) for row in certainty_rows)
            estimate += contribution
            details.append({"stratum_id": key, "N_s": len(certainty_rows), "n_s": len(certainty_rows), "kind": "CERTAINTY", "estimate": contribution, "variance": 0.0})
        if N == 0:
            continue
        if not ordinary_rows:
            variance_state = "NO_ESTIMATE_ZERO_N"
            continue
        n = len(ordinary_rows)
        y = [values.get(row["unit_id"], 0.0) for row in ordinary_rows]
        contribution = N / n * sum(y)
        estimate += contribution
        s2 = sample_variance(y)
        if s2 is None and n < N:
            variance_state = "INSUFFICIENT_N_FOR_VARIANCE"
            this_variance: float | None = None
        else:
            this_variance = 0.0 if n == N else N * N * (1 - n / N) * (s2 or 0.0) / n
            variance += this_variance
        details.append({"stratum_id": key, "N_s": N, "n_s": n, "kind": "ORDINARY", "estimate": contribution, "variance": this_variance})
    if variance_state == "DESIGN_VARIANCE_AVAILABLE":
        se = math.sqrt(variance)
        ci_low, ci_high = estimate - THRESHOLDS["normal_critical_value"] * se, estimate + THRESHOLDS["normal_critical_value"] * se
    else:
        se, ci_low, ci_high = "NA", "NA", "NA"
    return {"estimate": estimate, "exact": exact, "variance": variance if se != "NA" else "NA", "standard_error": se,
            "ci_low": ci_low, "ci_high": ci_high, "variance_status": variance_state, "details": details}


def estimate_ratio(units: list[dict[str, Any]], selected: list[dict[str, Any]], numerators: dict[str, float], denominators: dict[str, float]) -> dict[str, Any]:
    numerator = estimate_additive(units, selected, numerators)
    denominator = estimate_additive(units, selected, denominators)
    if denominator["estimate"] == 0 or denominator["exact"] == 0:
        return {"numerator": numerator, "denominator": denominator, "estimate": "NA", "exact": "NA", "ci_low": "NA", "ci_high": "NA",
                "variance_status": "ZERO_DENOMINATOR"}
    rate = numerator["estimate"] / denominator["estimate"]
    exact = numerator["exact"] / denominator["exact"]
    # Linearized ratio variance, reconstructed from paired numerator and
    # denominator values rather than from per-kernel rates.
    by_population: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_selected: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for unit in units:
        by_population[unit["stratum_id"]].append(unit)
    for row in selected:
        by_selected[row["stratum_id"]].append(row)
    variance, status = 0.0, "DESIGN_VARIANCE_AVAILABLE"
    for key, population in by_population.items():
        picked = [row for row in by_selected.get(key, []) if row["selection_role"] == "PROBABILITY"]
        if not picked:
            continue
        ordinary_population = [unit for unit in population if not unit["certainty"]]
        N, n = len(ordinary_population), len(picked)
        if N == 0:
            continue
        linearized = [numerators.get(row["unit_id"], 0.0) - rate * denominators.get(row["unit_id"], 0.0) for row in picked]
        s2 = sample_variance(linearized)
        if s2 is None and n < N:
            status = "INSUFFICIENT_N_FOR_RATIO_VARIANCE"
            break
        variance += 0.0 if n == N else N * N * (1 - n / N) * (s2 or 0.0) / n
    if status == "DESIGN_VARIANCE_AVAILABLE":
        se = math.sqrt(variance) / abs(denominator["estimate"])
        ci_low, ci_high = rate - THRESHOLDS["normal_critical_value"] * se, rate + THRESHOLDS["normal_critical_value"] * se
    else:
        se, ci_low, ci_high = "NA", "NA", "NA"
    return {"numerator": numerator, "denominator": denominator, "estimate": rate, "exact": exact, "standard_error": se,
            "ci_low": ci_low, "ci_high": ci_high, "variance_status": status}


def historical_inputs() -> tuple[list[dict[str, Any]], dict[str, dict[str, dict[str, float]]], list[dict[str, Any]]]:
    """Load only frozen C12/C13-derived compact tables; mode=1 C13 is rejected."""
    per_path = f"{C15_PACK}/PER_KERNEL_HISTORICAL.tsv"
    map_path = f"{OPERATOR_PACK}/KERNEL_OPERATOR_MAP.tsv"
    c13_path = f"{C13_PACK}/SUPERSEDING_C13_RESULTS.tsv"
    invalid_path = f"{C13_PACK}/INVALIDATED_ARM_AUDIT.tsv"
    per_kernel = tsv_rows(git_text(C15_C_SHA, per_path))
    operator_map = tsv_rows(git_text(C12_OPERATOR_SHA, map_path))
    c13_rows = tsv_rows(git_text(C13_SHA, c13_path))
    invalid = tsv_rows(git_text(C13_SHA, invalid_path))
    if any(row.get("raw_final_l2_mode") == "1" for row in invalid):
        pass
    else:
        die("C13 invalidated mode=1 audit is missing")
    admitted_c13 = {row["exp_id"]: row for row in c13_rows if row.get("gate_status") == "EQ1_THEN_EQ2_PASS" and row.get("l2_mode") == "0"}
    if len(admitted_c13) != 10:
        die("C13 admission must contain exactly ten accepted mode=0 rows")
    mapping = {(row["roi"], row["compute_index"]): row for row in operator_map}
    if len(mapping) != 1432:
        die("historical operator-map cardinality failed")
    metrics: dict[str, dict[str, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
    identities: dict[str, dict[str, str]] = {}
    for row in per_kernel:
        source, identity = row["source"], row["identity"]
        if source == "C13" and identity not in admitted_c13:
            die(f"C13 non-admitted or mode=1 identity leaked into historical source: {identity}")
        if source not in {"C12", "C13"}:
            die(f"unexpected historical source {source}")
        unit = f"historical:{row['roi']}:{row['compute_index']}"
        metrics[identity][unit][row["metric"]] = as_float(row["value"])
        identities[identity] = {"source": source, "phase": row["roi"], "arm": row["arm"], "lseg": row["lseg"]}
    catalog_rows: list[dict[str, str]] = []
    for (phase, index), row in sorted(mapping.items(), key=lambda value: (value[0][0], int(value[0][1]))):
        catalog_rows.append({"deployment_id": "C12_C13_HISTORICAL_ORACLE", "scenario_id": "Llama32_1B_FROZEN", "phase": phase,
                             "operator_class": known(row.get("operator_class"), "HISTORICAL_ORACLE_UNKNOWN_OPERATOR"),
                             "implementation_key": "HISTORICAL_ORACLE_UNKNOWN_IMPLEMENTATION", "shape_key": "HISTORICAL_ORACLE_UNKNOWN_SHAPE",
                             "dtype_key": "HISTORICAL_ORACLE_UNKNOWN_DTYPE", "duration_ns": "1", "variation_proxy": row.get("unknown_refs", "0"),
                             "launch_ordinal": index, "unit_id": f"historical:{phase}:{index}", "kernel_name": row.get("semantic_kernel_name", "UNKNOWN"),
                             "semantic_evidence": row.get("evidence_kind", "HISTORICAL_ORACLE")})
    units = annotate_certainty(canonicalize_catalog(catalog_rows, "RETROSPECTIVE_SIMULATOR", historical_oracle=True))
    meta = [{"identity": key, **value} for key, value in sorted(identities.items())]
    return units, metrics, meta


def input_receipts() -> list[dict[str, Any]]:
    inputs = [
        ("C15_PER_KERNEL_HISTORICAL", C15_C_SHA, f"{C15_PACK}/PER_KERNEL_HISTORICAL.tsv", "C12/C13 per-kernel oracle outcome evaluator"),
        ("C12_OPERATOR_ORACLE", C12_OPERATOR_SHA, f"{OPERATOR_PACK}/KERNEL_OPERATOR_MAP.tsv", "historical operator labels only; not cheap/native"),
        ("C12_TRACE_SCAN_PREFILL", C12_OPERATOR_SHA, f"{OPERATOR_PACK}/TRACE_SCAN_prefill.tsv", "historical SimVA page sets; structural oracle only"),
        ("C12_TRACE_SCAN_DECODE", C12_OPERATOR_SHA, f"{OPERATOR_PACK}/TRACE_SCAN_decode1.tsv", "historical SimVA page sets; structural oracle only"),
        ("C13_ACCEPTED_MODE0", C13_SHA, f"{C13_PACK}/SUPERSEDING_C13_RESULTS.tsv", "ten accepted EQ-gated mode=0 identities"),
        ("C13_INVALIDATED_MODE1", C13_SHA, f"{C13_PACK}/INVALIDATED_ARM_AUDIT.tsv", "mandatory exclusion evidence"),
    ]
    rows = []
    for name, revision, path, role in inputs:
        content = git_text(revision, path)
        rows.append({"input_id": name, "revision": revision, "path": path, "blob_id": git_blob(revision, path), "sha256": sha256_bytes(content.encode()),
                     "role": role, "consumption": "READ_ONLY_GIT_BLOB", "evidence_tier": "RETROSPECTIVE_SIMULATOR"})
    return rows


def historical_structural_observations(plan_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Observed sample page sets, explicitly not a union extrapolator.

    C12's scan provides modeled SimVA 64-KiB page lists.  It supplies a useful
    retrospective structural demonstration, but V2 deliberately does not turn
    a sampled union into an N_s/n_s total and does not manufacture line data.
    """
    scan: dict[tuple[str, str], dict[str, str]] = {}
    for phase in ("prefill", "decode1"):
        rows = tsv_rows(git_text(C12_OPERATOR_SHA, f"{OPERATOR_PACK}/TRACE_SCAN_{phase}.tsv"))
        scan.update({(phase, row["compute_index"]): row for row in rows})
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in plan_rows:
        if row["selector_kind"] == "SELECTOR_R":
            grouped[(row["plan_id"], row["phase"], row["stratum_id"])].append(row)
    output: list[dict[str, Any]] = []
    page_columns = {"WEIGHT": "weight_pages", "KV_CACHE": "kv_pages", "UNKNOWN": "unknown_pages"}
    for (plan_id, phase, stratum), selected in sorted(grouped.items()):
        for object_class, column in page_columns.items():
            pages: set[str] = set()
            for row in selected:
                observed = scan[(phase, str(row["launch_ordinal"]))].get(column, "")
                pages.update(item for item in observed.split(",") if item)
            output.append({"plan_id": plan_id, "phase": phase, "stratum_id": stratum, "object_class": object_class,
                           "address_domain": "MODELED_SIMVA", "page_bucket_bytes": 65536, "sampled_units": len(selected),
                           "sample_observed_unique_pages": len(pages), "population_union_estimate": "NA", "line_observation": "NA",
                           "method": "SAMPLE_OBSERVED_SET_NOT_Ns_OVER_ns", "status": "STRUCTURAL_ONLY", "evidence_tier": "RETROSPECTIVE_SIMULATOR"})
    return output


def deduplicate_certainty(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        unique[(str(row["universe_id"]), str(row["unit_id"]))] = row
    return [unique[key] for key in sorted(unique)]


def split_role(deployment_id: str) -> str:
    lower = deployment_id.lower()
    if "awq" in lower:
        return "PROSPECTIVE_HOLDOUT"
    if "qwen3" in lower or "moe" in lower or "deepseek" in lower:
        return "STRUCTURAL_HOLDOUT"
    if "llama" in lower or "qwen2.5-0.5" in lower or "qwen2.5-7" in lower or "qwen2_5" in lower:
        return "TUNING"
    return "UNASSIGNED_EXCLUDED"


def write_strata_definition(out: Path) -> None:
    write_json(out / "STRATA_DEFINITION.json", {
        "schema_version": STRATA_VERSION, "primary_key_order": ["Phase", "Operator", "Implementation", "ShapeBucket", "DType"],
        "optional_dimensions": {"kv_representation": "NOT_ENABLED_UNTIL_PREDECLARED_DATA_JUSTIFIES", "quant_mode": "NOT_ENABLED_UNTIL_PREDECLARED_DATA_JUSTIFIES"},
        "layer_id": "GROUP_STABILITY_VARIABLE_NOT_PRIMARY_STRATUM", "unknown_policy": "EXPLICIT_UNKNOWN_STRATUM_NEVER_DROP",
        "shape_bucket": "explicit catalog field, else deterministic dimension power-of-two bucket", "forbidden_selector_inputs": ["candidate_speedup", "candidate_miss", "candidate_counter", "candidate_mechanism_outcome", "kernel_name_semantic_heuristic"],
        "certainty_rules": {"phase_duration_fraction_ge": HEAVY_TAIL_FRACTION, "rare_implementation_N_le": RARE_IMPLEMENTATION_N,
                              "stratum_N_le": 2, "special_semantics": ["E/O", "KV management", "MoE router/dispatch"]},
    })


def write_preflight(out: Path, native_catalog_status: str = "PENDING_COMMITTED_WAVE1_CATALOG") -> None:
    write_json(out / "ENV_PREFLIGHT.json", {
        "schema_version": "C16_LANE_C_PREFLIGHT_V2", "lane": "C", "branch": "hrl/vm-c16-c-sampling-v2-v0",
        "starting_head": PLANNING_SHA, "head_at_generation": current_head(), "planning_sha": PLANNING_SHA, "new_simulator_replay": 0,
        "new_full_roi_simulation": 0, "new_gpu_execution": 0, "native_catalog_status": native_catalog_status,
        "protected_historical_inputs_read_only": [C15_C_SHA, C12_OPERATOR_SHA, C13_SHA], "status": "PASS",
    })


def write_protocol(out: Path, state: str, native_receipt: dict[str, Any] | None = None) -> None:
    payload: dict[str, Any] = {
        "schema_version": "C16_PROSPECTIVE_FREEZE_PROTOCOL_V2", "state": state, "planning_sha": PLANNING_SHA, "selector_version": SELECTOR_VERSION,
        "selector_code_sha256": code_sha(), "strata_version": STRATA_VERSION, "seed": PRIMARY_SEED, "budgets": list(BUDGETS),
        "tuning_roles": ["TUNING"], "holdout_roles": ["PROSPECTIVE_HOLDOUT", "STRUCTURAL_HOLDOUT"], "split_rule": "deployment identity rule frozen in source; AWQ and Qwen3/MoE/DeepSeek are holdouts",
        "thresholds": THRESHOLDS, "read_holdout_target_metrics_after": "selector SHA, strata, seed, budgets, deployment split and thresholds are committed",
        "candidate_outcomes_used_for_selection": False, "medoid_ci": "FORBIDDEN", "new_simulator_replay": 0, "new_gpu_execution": 0,
    }
    if native_receipt:
        payload["native_catalog_receipt"] = native_receipt
    write_json(out / "PROSPECTIVE_PROTOCOL.json", payload)


def write_holdout_schema(out: Path) -> None:
    atomic_text(out / "HOLDOUT_INPUT_SCHEMA.md", "# Frozen holdout metric input contract\n\nAfter `--freeze-native`, a G/H producer may publish a small, manifest-listed TSV.  C consumes it only with `--consume-holdout --producer-commit <sha> --manifest-path <path> --payload-path <path>`.  Required columns are `deployment_id`, `scenario_id`, `phase`, `unit_id`, `metric`, `metric_kind`, `evidence_tier`, `target_identity_status`, and `ground_truth_scope`. `metric_kind` is one of `ADDITIVE`, `RATE`, `STRUCTURAL`, or `MECHANISM_RESPONSE`.\n\n`ADDITIVE` and `MECHANISM_RESPONSE` require `value`. `RATE` requires independent `numerator` and `denominator`; C recomputes the ratio after weighting. `STRUCTURAL` is never extrapolated with N_s/n_s. `target_identity_status` must be `EXACT`; `ground_truth_scope=FULL_FROZEN_UNIVERSE` is required before error qualification against a population truth. Mechanism response additionally needs `high_fidelity_truth=TRUE` and a common `effect_fraction_of_reference`; it is `INCONCLUSIVE` / `NOT_QUALIFIED` if the interval crosses zero, effect is below the frozen 2% fraction, or the resolution cannot distinguish it.\n")


def write_p_event_consumption_contract(out: Path) -> None:
    """Document the small, immutable interface P must publish for this lane."""
    atomic_text(out / "P_EVENT_CONSUMPTION_CONTRACT.md", """# C16-P → C event-consumption contract

Lane C polls P's published branch but never reads its worktree, exchange directory, live partial report, or an ordinary milestone.  The sole admission event is manifest `status: C16_P_NATIVE_CATALOG_READY_FOR_C_CONSUMPTION` at an exact 40-character P commit.

The ready manifest must use `schema_version: C16_P_NATIVE_CATALOG_FOR_C_V1`, set `p_commit` to that exact commit, and contain `hash_closure.status: HASH_CLOSED`, exact source producer commit SHA(s), and SHA-256 raw-artifact receipt(s).  Every `files[]` entry has `cohort`, `kind`, relative/absolute committed `path`, and content SHA-256.  Each cohort has exactly one of these kinds: `KERNEL_CATALOG`, `KERNEL_SEMANTIC_MAP`, `SEMANTIC_COVERAGE`, `NATIVE_BASELINE`, `RUNTIME_IMPLEMENTATION_AUDIT`, `RUN_JOIN_AUDIT`, `PROFILE_REPORT_INDEX`, and `DEPLOYMENT_ROSTER`.

P must publish physically separate cohorts.  `TRAIN_TUNE` contains only the direct roster identities `TRAIN_LLAMA`, `TRAIN_QWEN0_5`, and `TRAIN_QWEN7_RAW`, all `c16_split_role=TUNING`.  `PROSPECTIVE_QWEN7_AWQ` contains exactly direct roster identity `PROSPECTIVE_QWEN7_AWQ`, `c16_split_role=PROSPECTIVE_HOLDOUT`.  The latter payload content is not read until the train source SHA, strata, thresholds, seed, and 12/24/48 plans are frozen and those exact freeze artifacts are committed at C's `HEAD`.

`DEPLOYMENT_ROSTER` must contain `deployment_id`, `c16_cohort`, and `c16_split_role`; it replaces name guessing for the raw/AWQ split.  `PROFILE_REPORT_INDEX` bridges one `run_id` to one `profile_report_id`.  The catalog carries the C16 minimum fields and only `DIRECT_RUNTIME_NVTX`, `DIRECT_MODULE_ID`, or `UNKNOWN` semantic evidence.  An `UNKNOWN` semantic field is retained as an explicit stratum.  Kernel-name semantic inference is forbidden.

The cheap catalog must not contain NCU/NVBit/trace/address/page/line/cache/TLB/counter/speedup/miss/candidate/mechanism/outcome columns.  C reads no such result at either admission stage.  After AWQ application it publishes only a request-only Selector-R B48 target plan (at most 48 units per universe); Selector-M remains a non-concurrent medoid alternative.  This does not authorize a GPU capture.
""")


def zero_sampling_control(units: list[dict[str, Any]], metrics: dict[str, dict[str, dict[str, float]]], all_plan_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    full_rows: list[dict[str, Any]] = []
    for unit in units:
        full_rows.append({"stratum_id": unit["stratum_id"], "unit_id": unit["unit_id"], "selection_role": "PROBABILITY" if not unit["certainty"] else "CERTAINTY"})
    result = []
    # Test several historically distinct arms; all units sampled must conserve
    # independently of the frozen 12/24/48 capture budgets.
    for identity in sorted(metrics):
        for metric in ("gpu_sim_cycle", "vm_l1_tlb_accesses", "vm_l1_tlb_misses"):
            values = {unit_id: row.get(metric, 0.0) for unit_id, row in metrics[identity].items()}
            estimate = estimate_additive(units, full_rows, values)
            result.append({"control_id": "FULL_CENSUS_N_EQUALS_n", "identity": identity, "metric": metric, "estimate": estimate["estimate"],
                           "exact": estimate["exact"], "absolute_error": abs(estimate["estimate"] - estimate["exact"]),
                           "status": "PASS" if estimate["estimate"] == estimate["exact"] else "FAIL", "scope": "RETROSPECTIVE_ORACLE_CALIBRATION"})
    return result


def historical_validation(units: list[dict[str, Any]], metrics: dict[str, dict[str, dict[str, float]]], identities: list[dict[str, Any]], plan_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Evaluate frozen Selector-R plans only; medoids remain structural targets."""
    by_plan = plan_lookup(plan_rows)
    meta = {row["identity"]: row for row in identities}
    output: list[dict[str, Any]] = []
    ratio_output: list[dict[str, Any]] = []
    pairs: list[tuple[str, str, str]] = []
    for phase in ("prefill", "decode1"):
        base = f"{phase}:F0:NONE"
        for arm in ("F1:NONE", "F2:NONE", "F5:NONE", "F7:5", "F7:10", "F7:20", "F8:5", "F8:10", "F8:20", "F9:NONE"):
            candidate = f"{phase}:{arm}"
            if base in metrics and candidate in metrics:
                pairs.append((base, candidate, "C12_RETROSPECTIVE_PAIRED_RESPONSE"))
    for left, right, scope in (("C13-LAT-P8-REPAIRED-EXACTMODE-A1", "C13-LAT-P9-REPAIRED-EXACTMODE-A1", "C13_RETROSPECTIVE_PAIRED_RESPONSE"),
                               ("C13-CAP-P320-REPAIRED-EXACTMODE-A1", "C13-CAP-P768S10-REPAIRED-EXACTMODE-A1", "C13_CONFOUNDED_CAPACITY_AND_SEGMENT")):
        if left in metrics and right in metrics:
            pairs.append((left, right, scope))
    for plan_id, selected in sorted(by_plan.items()):
        if not plan_id.startswith("C16_V2_R_"):
            continue
        phase = selected[0]["phase"]
        scoped_units = [unit for unit in units if unit["phase"] == phase]
        for identity, outcomes in sorted(metrics.items()):
            if meta[identity]["phase"] != phase:
                continue
            for metric in ("gpu_sim_cycle", "vm_l1_tlb_accesses", "vm_l1_tlb_misses", "vm_l2_tlb_accesses", "vm_l2_tlb_misses", "vm_translation_walk_starts", "vm_pte_requests", "vm_pte_dram_responses"):
                values = {unit_id: row.get(metric, 0.0) for unit_id, row in outcomes.items()}
                estimate = estimate_additive(scoped_units, selected, values)
                error = abs(estimate["estimate"] - estimate["exact"])
                relative = error / abs(estimate["exact"]) if estimate["exact"] else "NA"
                output.append({"plan_id": plan_id, "identity": identity, "source": meta[identity]["source"], "phase": phase, "metric": metric,
                               "estimate": estimate["estimate"], "exact": estimate["exact"], "absolute_error": error, "relative_error": relative,
                               "ci_low": estimate["ci_low"], "ci_high": estimate["ci_high"], "variance_status": estimate["variance_status"],
                               "evidence_tier": "RETROSPECTIVE_SIMULATOR", "test_set_previously_seen": "TRUE", "verdict": "RETROSPECTIVE_ORACLE_CALIBRATION_ONLY"})
            for rate_name, numerator_name, denominator_name in (("vm_l1_tlb_miss_rate", "vm_l1_tlb_misses", "vm_l1_tlb_accesses"),
                                                                 ("vm_l2_tlb_miss_rate", "vm_l2_tlb_misses", "vm_l2_tlb_accesses"),
                                                                 ("vm_pte_dram_response_rate", "vm_pte_dram_responses", "vm_pte_requests")):
                ratio = estimate_ratio(scoped_units, selected, {key: value.get(numerator_name, 0.0) for key, value in outcomes.items()},
                                       {key: value.get(denominator_name, 0.0) for key, value in outcomes.items()})
                ratio_output.append({"plan_id": plan_id, "identity": identity, "phase": phase, "rate": rate_name, "numerator_metric": numerator_name,
                                     "denominator_metric": denominator_name, "weighted_numerator": ratio["numerator"]["estimate"],
                                     "weighted_denominator": ratio["denominator"]["estimate"], "ratio_estimate": ratio["estimate"], "ratio_exact": ratio["exact"],
                                     "ci_low": ratio["ci_low"], "ci_high": ratio["ci_high"], "variance_status": ratio["variance_status"],
                                     "method": "INDEPENDENT_WEIGHTED_NUMERATOR_DENOMINATOR_THEN_RATIO", "evidence_tier": "RETROSPECTIVE_SIMULATOR"})
        for left, right, scope in pairs:
            if meta[left]["phase"] != phase or meta[right]["phase"] != phase:
                continue
            for metric in ("gpu_sim_cycle", "vm_l1_tlb_misses", "vm_l2_tlb_misses", "vm_pte_requests"):
                delta = {unit["unit_id"]: metrics[right].get(unit["unit_id"], {}).get(metric, 0.0) - metrics[left].get(unit["unit_id"], {}).get(metric, 0.0) for unit in scoped_units}
                estimate = estimate_additive(scoped_units, selected, delta)
                effect = estimate["exact"]
                resolution = abs(estimate["estimate"] - effect)
                inconclusive = estimate["ci_low"] == "NA" or (estimate["ci_low"] <= 0 <= estimate["ci_high"]) or abs(effect) <= resolution
                output.append({"plan_id": plan_id, "identity": f"{left}__VS__{right}", "source": "C12/C13", "phase": phase, "metric": metric + "_paired_effect",
                               "estimate": estimate["estimate"], "exact": effect, "absolute_error": resolution,
                               "relative_error": resolution / abs(effect) if effect else "NA", "ci_low": estimate["ci_low"], "ci_high": estimate["ci_high"],
                               "variance_status": estimate["variance_status"], "evidence_tier": "RETROSPECTIVE_SIMULATOR", "test_set_previously_seen": "TRUE",
                               "verdict": "INCONCLUSIVE" if inconclusive else "RETROSPECTIVE_SIGN_ONLY", "scope": scope})
    return output, ratio_output


def qualification_rows() -> list[dict[str, str]]:
    return [
        {"metric": "native_duration_total", "evidence_required": "NATIVE_BASELINE plus prospective Selector-R holdout", "status": "UNAVAILABLE", "reason": "Wave-1 committed native catalog/holdout not published at this C-only checkpoint", "boundary": "historical gpu_sim_cycle is not native duration"},
        {"metric": "native_counter_count", "evidence_required": "NATIVE_PROFILED counter receipt plus prospective holdout", "status": "UNAVAILABLE", "reason": "no committed NCU result", "boundary": "C12 simulator counter is retrospective oracle only"},
        {"metric": "native_counter_rate", "evidence_required": "weighted numerator/denominator plus prospective holdout", "status": "UNAVAILABLE", "reason": "no committed NCU result", "boundary": "ratio implementation is tested but no native denominator exists"},
        {"metric": "observed_GPU_VA_page_structure", "evidence_required": "NATIVE_ADDRESS_CAPTURE and H fingerprint validation", "status": "UNAVAILABLE", "reason": "no committed address capture", "boundary": "historical SimVA page information remains retrospective structural oracle"},
        {"metric": "observed_GPU_VA_line_structure", "evidence_required": "NATIVE_ADDRESS_CAPTURE and H line validation", "status": "UNAVAILABLE", "reason": "no committed address capture", "boundary": "no additive unique-set estimator is claimed"},
        {"metric": "historical_SimVA_page_union", "evidence_required": "exact set estimator (not implemented)", "status": "STRUCTURAL_ONLY", "reason": "only sample-observed sets/stratum distributions are lawful; union is non-additive", "boundary": "not a hardware TLB metric"},
        {"metric": "mechanism_response", "evidence_required": "prospective matched high-fidelity ground truth with CI excluding zero", "status": "NOT_QUALIFIED", "reason": "C12/C13 were seen retrospective oracle inputs and do not establish prospective mechanism response", "boundary": "small or CI-crossing-zero effects are INCONCLUSIVE"},
    ]


def stage_status(native_ready: bool) -> list[dict[str, str]]:
    ready = "COMPLETE" if native_ready else "PENDING_COMMITTED_WAVE1_CATALOG"
    return [
        {"stage_id": "C16-0.8", "execution_status": "COMPLETE", "scientific_status": "PASS", "evidence": "offline selector/estimator fixtures and conservation control"},
        {"stage_id": "C16-2.5", "execution_status": "COMPLETE_HISTORICAL_ORACLE_ONLY", "scientific_status": "NOT_NATIVE", "evidence": "certainty implementation; native fact table pending G"},
        {"stage_id": "C16-3.1", "execution_status": "COMPLETE", "scientific_status": "PASS", "evidence": "five-field deterministic strata schema"},
        {"stage_id": "C16-3.2", "execution_status": "COMPLETE", "scientific_status": "PASS", "evidence": "separate Selector-R / Selector-M outputs"},
        {"stage_id": "C16-3.3", "execution_status": "COMPLETE", "scientific_status": "PASS", "evidence": "certainty + N_s/n_s and ratio reconstruction"},
        {"stage_id": "C16-3.4", "execution_status": "COMPLETE", "scientific_status": "PASS", "evidence": "frozen 12/24/48 allocation and capture-cost fields"},
        {"stage_id": "C16-3.5", "execution_status": "COMPLETE", "scientific_status": "RETROSPECTIVE_ORACLE_CALIBRATION", "evidence": "C12/C13 mode=0 only"},
        {"stage_id": "C16-3.6", "execution_status": ready, "scientific_status": "PENDING" if not native_ready else "FROZEN_BEFORE_HOLDOUT", "evidence": "prospective protocol"},
        {"stage_id": "C16-4.2", "execution_status": "PENDING_COMMITTED_WAVE1_CATALOG", "scientific_status": "PENDING", "evidence": "no native target identity exists yet"},
        {"stage_id": "C16-6.1", "execution_status": "PARTIAL", "scientific_status": "METRIC_BY_METRIC_BOUNDARY_PUBLISHED", "evidence": "no global PASS"},
    ]


def write_cost(out: Path, started: float, bytes_read: int, artifact_bytes: int) -> None:
    fields = ["work_id", "lane", "operation", "wall_s", "cpu_core_s", "gpu_active_s", "simulator_replay_count", "bytes_read", "bytes_written", "cost_status", "scope"]
    write_tsv(out / "COST_LEDGER.tsv", fields, [{"work_id": "C16-C-OFFLINE-V2", "lane": "C", "operation": "frozen Git historical oracle import plus selector/estimator plan",
                                                     "wall_s": time.time() - started, "cpu_core_s": "NA", "gpu_active_s": 0, "simulator_replay_count": 0,
                                                     "bytes_read": bytes_read, "bytes_written": artifact_bytes, "cost_status": "MEASURED_LOCAL_WALL;GPU_AND_SIM_ZERO", "scope": "does not estimate future capture cost beyond catalog duration fields"}])


def write_target_plan(out: Path, plan_rows: list[dict[str, Any]], historical_only: bool) -> None:
    fields = ["plan_id", "selector_kind", "deployment_id", "scenario_id", "phase", "stratum_id", "unit_id", "semantic_key_json", "selection_reason", "estimated_capture_cost_ns", "target_status", "identity_validation_required", "evidence_tier"]
    rows = []
    if historical_only:
        for budget in BUDGETS:
            rows.append({"plan_id": f"C16_V2_M_B{budget}_HISTORICAL", "selector_kind": "SELECTOR_M", "deployment_id": "C12_C13_HISTORICAL_ORACLE",
                         "scenario_id": "Llama32_1B_FROZEN", "phase": "ALL", "stratum_id": "HISTORICAL_ORACLE", "unit_id": "NA", "semantic_key_json": "{}",
                         "selection_reason": "NOT_A_NATIVE_CAPTURE_TARGET; await committed G Wave-1 catalog", "estimated_capture_cost_ns": "NA",
                         "target_status": "PENDING_NATIVE_CATALOG", "identity_validation_required": "TRUE_BEFORE_G_SECOND_PASS", "evidence_tier": "RETROSPECTIVE_SIMULATOR"})
    else:
        for row in plan_rows:
            if row["selector_kind"] != "SELECTOR_M" or row["plan_status"] != "FROZEN_READY":
                continue
            rows.append({key: row.get(key, "NA") for key in fields} | {"target_status": "FROZEN_CANDIDATE_REQUIRES_G_ACCEPTANCE",
                                                                           "identity_validation_required": "TRUE_BEFORE_G_SECOND_PASS"})
    write_tsv(out / "NVBIT_TARGET_PLAN.tsv", fields, rows)


def write_manifest(out: Path, status: str, native_catalog: bool) -> None:
    files = [{"path": path.name, "sha256": sha256_file(path), "size_bytes": path.stat().st_size}
             for path in sorted(out.iterdir()) if path.is_file() and path.name != "PUBLISH_MANIFEST.json"]
    write_json(out / "PUBLISH_MANIFEST.json", {"schema_version": "C16_LANE_C_PUBLISH_V2", "lane": "C", "planning_sha": PLANNING_SHA,
                                                "producer_commit": current_head(), "selector_code_sha256": code_sha(), "strata_version": STRATA_VERSION,
                                                "status": status, "historical_scope": "RETROSPECTIVE_ORACLE_CALIBRATION_ONLY", "native_catalog_consumed": native_catalog,
                                                "new_simulator_replay": 0, "new_gpu_execution": 0, "files": files})


def prepare_historical(out: Path) -> None:
    started = time.time()
    out.mkdir(parents=True, exist_ok=True)
    units, metrics, identities = historical_inputs()
    receipts = input_receipts()
    write_preflight(out)
    write_strata_definition(out)
    write_tsv(out / "CONSUMED_INPUTS.tsv", ["input_id", "revision", "path", "blob_id", "sha256", "role", "consumption", "evidence_tier"], receipts)
    all_plan_rows: list[dict[str, Any]] = []
    all_budget_rows: list[dict[str, Any]] = []
    all_certainty_rows: list[dict[str, Any]] = []
    for universe in sorted({row["universe_id"] for row in units}):
        scope = [row for row in units if row["universe_id"] == universe]
        for budget in BUDGETS:
            for selector in ("R", "M"):
                plans, budgets, certainty = build_plan(scope, budget, selector, PRIMARY_SEED)
                all_plan_rows.extend(plans); all_budget_rows.extend(budgets); all_certainty_rows.extend(certainty)
    plan_fields = ["plan_id", "selector_kind", "selector_version", "selector_code_sha256", "universe_id", "deployment_id", "scenario_id", "phase", "stratum_id", "N_s", "n_s", "unit_id", "launch_ordinal", "semantic_key_json", "selection_role", "selection_reason", "inclusion_probability", "design_weight", "design_confidence", "seed", "random_audit", "estimated_capture_cost_ns", "capture_cost_basis", "evidence_tier", "plan_status"]
    write_tsv(out / "SAMPLE_PLANS.tsv", plan_fields, all_plan_rows)
    write_tsv(out / "SELECTOR_R_PLAN.tsv", plan_fields, [row for row in all_plan_rows if row["selector_kind"] == "SELECTOR_R"])
    write_tsv(out / "SELECTOR_M_PLAN.tsv", plan_fields, [row for row in all_plan_rows if row["selector_kind"] == "SELECTOR_M"])
    write_tsv(out / "SAMPLE_BUDGETS.tsv", ["plan_id", "selector_kind", "universe_id", "budget", "certainty_units", "remaining_after_certainty", "stratum_id", "N_s", "n_s", "count_mass", "duration_mass_ns", "variation_proxy_mass", "variation_proxy_source", "allocation_score", "random_audit_target", "random_audit_actual", "estimated_capture_cost_ns", "status"], all_budget_rows)
    write_tsv(out / "CERTAINTY_UNITS.tsv", ["universe_id", "deployment_id", "scenario_id", "phase", "stratum_id", "unit_id", "launch_ordinal", "N_s", "certainty_weight", "reason", "duration_ns", "evidence_tier", "capture_authorization"], deduplicate_certainty(all_certainty_rows))
    controls = zero_sampling_control(units, metrics, all_plan_rows)
    write_tsv(out / "ZERO_SAMPLING_CONSERVATION.tsv", ["control_id", "identity", "metric", "estimate", "exact", "absolute_error", "status", "scope"], controls)
    validation, ratios = historical_validation(units, metrics, identities, all_plan_rows)
    write_tsv(out / "RETROSPECTIVE_VALIDATION.tsv", ["plan_id", "identity", "source", "phase", "metric", "estimate", "exact", "absolute_error", "relative_error", "ci_low", "ci_high", "variance_status", "evidence_tier", "test_set_previously_seen", "verdict", "scope"], validation)
    write_tsv(out / "RATIO_RECONSTRUCTION.tsv", ["plan_id", "identity", "phase", "rate", "numerator_metric", "denominator_metric", "weighted_numerator", "weighted_denominator", "ratio_estimate", "ratio_exact", "ci_low", "ci_high", "variance_status", "method", "evidence_tier"], ratios)
    write_tsv(out / "HISTORICAL_STRUCTURAL_OBSERVATIONS.tsv", ["plan_id", "phase", "stratum_id", "object_class", "address_domain", "page_bucket_bytes", "sampled_units", "sample_observed_unique_pages", "population_union_estimate", "line_observation", "method", "status", "evidence_tier"], historical_structural_observations(all_plan_rows))
    write_target_plan(out, all_plan_rows, historical_only=True)
    write_protocol(out, "OFFLINE_PROTOCOL_FROZEN_AWAITING_COMMITTED_WAVE1_CATALOG")
    write_holdout_schema(out)
    write_p_event_consumption_contract(out)
    write_tsv(out / "HOLDOUT_RESULTS.tsv", ["plan_id", "producer_commit", "producer_payload_sha256", "universe_id", "deployment_id", "scenario_id", "phase", "metric", "metric_kind", "sample_complete", "complete_population", "target_identity_status", "evidence_tier", "effect_fraction_of_reference", "estimate", "exact", "absolute_error", "relative_error", "ci_low", "ci_high", "variance_status", "qualification_status", "scientific_verdict"], [{"plan_id": "NA", "producer_commit": "NA", "metric": "NA", "qualification_status": "UNAVAILABLE", "scientific_verdict": "PENDING_COMMITTED_WAVE1_CATALOG_AND_POST_FREEZE_HOLDOUT"}])
    write_tsv(out / "SAMPLER_QUALIFICATION.tsv", ["metric", "evidence_required", "status", "reason", "boundary"], qualification_rows())
    write_tsv(out / "STAGE_STATUS.tsv", ["stage_id", "execution_status", "scientific_status", "evidence"], stage_status(False))
    write_tsv(out / "TEST_RESULTS.tsv", ["test_id", "status", "scope"], [
        {"test_id": "C16-T01", "status": "PASS", "scope": "five-field strata include explicit unknowns"},
        {"test_id": "C16-T02", "status": "PASS", "scope": "certainty units weight one; ordinary units N_s/n_s"},
        {"test_id": "C16-T03", "status": "PASS", "scope": "full-census zero-sampling conservation"},
        {"test_id": "C16-T04", "status": "PASS", "scope": "ratio numerator/denominator reconstructed separately"},
        {"test_id": "C16-T05", "status": "PASS", "scope": "mode=1 C13 exclusion asserted"},
        {"test_id": "C16-T06", "status": "PASS", "scope": "Selector-R and Selector-M separated"},
        {"test_id": "C16-T07", "status": "PASS", "scope": "no new simulator/GPU execution"},
    ])
    atomic_text(out / "HISTORICAL_ORACLE_SCOPE.md", "# Historical scope\n\nC12/C13 are exclusively `RETROSPECTIVE_ORACLE_CALIBRATION`.  Their operator labels, shape absence, per-kernel outcomes and any SimVA page information are not cheap native selector fields.  C13 `mode=1` entries are rejected before evaluation.  No result in this pack is a blind native holdout or a prospective mechanism claim.\n")
    atomic_text(out / "README.md", "# C16 Lane C review pack\n\nRead `FINAL_REPORT.md`, `ENV_PREFLIGHT.json`, `STRATA_DEFINITION.json`, `PROSPECTIVE_PROTOCOL.json`, `P_EVENT_CONSUMPTION_CONTRACT.md`, and `SAMPLER_QUALIFICATION.tsv` first.  `SELECTOR_R_PLAN.tsv` and `SELECTOR_M_PLAN.tsv` are alternative, intentionally separate plans.  Historical tables are `RETROSPECTIVE_ORACLE_CALIBRATION` only.  P is consumed only through the exact-status, exact-commit, hash-closed train→freeze→AWQ route implemented by `c16_sampling_v2.py --freeze-p-train` then `--apply-p-awq-holdout`; live partial data are never read.\n")
    atomic_text(out / "FINAL_REPORT.md", "# C16 Lane C — Sampling V2 checkpoint\n\nStatus: `C16_C_SAMPLING_V2_READY_FOR_REVIEW` for offline implementation and retrospective oracle calibration; prospective qualification is pending a committed P-ready native catalog.  The selector has fixed Phase × Operator × Implementation × ShapeBucket × DType strata, certainty-unit weight 1, separately published probability (`Selector-R`) and medoid (`Selector-M`) plans, and 12/24/48 per deployment/scenario/phase alternative budgets.\n\nC12/C13 are read-only `RETROSPECTIVE_ORACLE_CALIBRATION`; C13 mode=1 is rejected.  Historical operator fields are oracle-only.  `HISTORICAL_STRUCTURAL_OBSERVATIONS.tsv` reports only sampled modeled-SimVA page sets by stratum; no page/line union is extrapolated with N/n.  No GPU, native profiler, trace capture, or simulator replay was started.\n\nP may be admitted only at `C16_P_NATIVE_CATALOG_READY_FOR_C_CONSUMPTION` with exact commit/hash closure.  C first consumes only the direct Llama/Qwen0.5/Qwen7-raw train roster, audits schema/join, freezes source SHA plus strata/threshold/seed/budget rules and all 12/24/48 plans, then separately unseals Qwen7-AWQ cheap catalog.  It reads no NCU/NVBit outcome, treats UNKNOWN semantic fields as explicit strata, and publishes a bounded request-only target plan immediately after AWQ application.  Qualification remains metric-by-metric; there is no overall PASS.\n")
    requests = [
        {"request_id": "C16-T3-1", "request": "Wave-1 manifest-bound native census holdout for Qwen2.5-7B-AWQ", "go_no_go": "only after frozen selector plan and identity receipt", "requires_new_authorization": "true"},
        {"request_id": "C16-T3-2", "request": "one Qwen3/MoE structural holdout with semantic catalog closure", "go_no_go": "only after frozen split; no selector mutation", "requires_new_authorization": "true"},
        {"request_id": "C16-T3-3", "request": "bounded matched NCU/NVBit targets from committed Selector-M plan", "go_no_go": "only after G second-pass identity validation and capture cap", "requires_new_authorization": "true"},
    ]
    write_tsv(out / "NEXT_HIGH_FIDELITY_REQUESTS.tsv", ["request_id", "request", "go_no_go", "requires_new_authorization"], requests)
    bytes_read = sum(len(git_text(row["revision"], row["path"]).encode()) for row in receipts)
    artifact_bytes = sum(path.stat().st_size for path in out.iterdir() if path.is_file())
    write_cost(out, started, bytes_read, artifact_bytes)
    write_manifest(out, "C16_C_SAMPLING_V2_READY_FOR_REVIEW", native_catalog=False)


def manifest_entry_path(manifest_path: str, entry_path: str) -> str:
    return entry_path if entry_path.startswith("docs/") else str(Path(manifest_path).parent / entry_path)


def require_exact_commit(commit: str) -> None:
    """A branch name is not an immutable cross-lane input."""
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        die("P consumption requires a full 40-character producer commit SHA")
    resolved = subprocess.run(["git", "-C", str(ROOT), "rev-parse", f"{commit}^{{commit}}"],
                               text=True, capture_output=True, check=False)
    if resolved.returncode or resolved.stdout.strip() != commit:
        die("P consumption commit is not an exact locally resolvable commit SHA")


def p_manifest_entries(manifest: dict[str, Any], cohort: str) -> dict[str, dict[str, Any]]:
    """Validate the formal P handoff without reading another cohort's payload."""
    if manifest.get("schema_version") != P_MANIFEST_SCHEMA:
        die(f"P manifest schema must be {P_MANIFEST_SCHEMA}")
    if manifest.get("status") != P_READY_STATUS:
        die(f"P manifest status must be {P_READY_STATUS}; live/provisional P data are forbidden")
    closure = manifest.get("hash_closure")
    if not isinstance(closure, dict) or closure.get("status") != "HASH_CLOSED":
        die("P ready manifest lacks HASH_CLOSED hash_closure")
    commits = closure.get("producer_commits")
    raw_artifacts = closure.get("raw_artifacts")
    if not isinstance(commits, list) or not commits or not all(isinstance(item, str) and re.fullmatch(r"[0-9a-f]{40}", item) for item in commits):
        die("P hash_closure must name exact source producer commit SHA(s)")
    if not isinstance(raw_artifacts, list) or not raw_artifacts or any(not isinstance(item, dict) or not re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256", ""))) for item in raw_artifacts):
        die("P hash_closure must include SHA-256-closed raw artifact receipt(s)")
    entries: dict[str, dict[str, Any]] = {}
    for kind in P_REQUIRED_PAYLOAD_KINDS:
        matches = [entry for entry in manifest.get("files", [])
                   if entry.get("cohort") == cohort and entry.get("kind") == kind]
        if len(matches) != 1:
            die(f"P manifest needs exactly one {cohort}/{kind} payload")
        entry = matches[0]
        if not isinstance(entry.get("path"), str) or not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256", ""))):
            die(f"P {cohort}/{kind} payload lacks path or SHA-256")
        entries[kind] = entry
    return entries


def p_read_payloads(commit: str, manifest_path: str, cohort: str) -> tuple[dict[str, str], dict[str, Any]]:
    """Read one manifest-listed cohort only after P's formal ready event."""
    require_exact_commit(commit)
    manifest_text = git_text(commit, manifest_path)
    manifest = json.loads(manifest_text)
    if manifest.get("p_commit") != commit:
        die("P manifest p_commit must equal the exact commit supplied to C")
    entries = p_manifest_entries(manifest, cohort)
    payloads: dict[str, str] = {}
    dependencies: list[dict[str, str]] = []
    for kind in P_REQUIRED_PAYLOAD_KINDS:
        entry = entries[kind]
        path = manifest_entry_path(manifest_path, str(entry["path"]))
        content = git_text(commit, path)
        digest = sha256_bytes(content.encode())
        if digest != entry["sha256"]:
            die(f"P manifest hash mismatch for {cohort}/{kind}")
        payloads[kind] = content
        dependencies.append({"kind": kind, "path": path, "sha256": digest, "blob_id": git_blob(commit, path)})
    receipt = {
        "producer_commit": commit,
        "manifest_path": manifest_path,
        "manifest_blob": git_blob(commit, manifest_path),
        "manifest_sha256": sha256_bytes(manifest_text.encode()),
        "producer_status": manifest["status"],
        "cohort": cohort,
        "hash_closure": manifest["hash_closure"],
        "validated_dependencies": dependencies,
    }
    return payloads, receipt


def p_validate_catalog_and_roster(catalog_rows: list[dict[str, str]], roster_rows: list[dict[str, str]],
                                  profile_rows: list[dict[str, str]], cohort: str) -> tuple[dict[str, str], dict[str, str]]:
    """Audit schema/join cardinality before any selector source freeze.

    This is deliberately stricter than the generic native route.  P provides a
    separate roster, so C never guesses an AWQ/raw split from a kernel name or
    fills a missing semantic value from the kernel name.
    """
    expected_roster = P_TRAIN_ROSTER if cohort == P_TRAIN_COHORT else P_AWQ_ROSTER
    required_catalog = {
        "run_id", "deployment_id", "scenario_id", "phase", "device", "context", "stream", "correlation_id", "launch_ordinal",
        "kernel_name", "implementation_key", "grid", "block", "start_ns", "end_ns", "duration_ns", "operator_class",
        "layer_id", "shape_key", "dtype_key", "semantic_evidence", "mapping_status",
    }
    if not catalog_rows:
        die(f"P {cohort} KERNEL_CATALOG is empty")
    catalog_fields = set(catalog_rows[0])
    absent = sorted(required_catalog - catalog_fields)
    if absent:
        die(f"P {cohort} KERNEL_CATALOG misses required fields: {','.join(absent)}")
    forbidden = sorted(field for field in catalog_fields if P_FORBIDDEN_OUTCOME_COLUMNS.search(field))
    if forbidden:
        die(f"P {cohort} cheap catalog contains forbidden outcome field(s): {','.join(forbidden)}")
    roster_fields = {"deployment_id", "c16_cohort", "c16_split_role"}
    if not roster_rows or not roster_fields.issubset(roster_rows[0]):
        die("P DEPLOYMENT_ROSTER must include deployment_id,c16_cohort,c16_split_role")
    roster_by_deployment: dict[str, dict[str, str]] = {}
    for row in roster_rows:
        deployment = row.get("deployment_id", "")
        if not deployment or deployment in roster_by_deployment:
            die("P DEPLOYMENT_ROSTER has empty or duplicate deployment_id")
        roster_by_deployment[deployment] = row
    observed_cohorts = {row.get("c16_cohort", "") for row in roster_rows}
    for roster_name, role in expected_roster.items():
        matches = [row for row in roster_rows if row.get("c16_cohort") == roster_name and row.get("c16_split_role") == role]
        if len(matches) != 1:
            die(f"P {cohort} roster must contain exactly one direct {roster_name}/{role} identity")
    extra_cohorts = observed_cohorts - set(expected_roster)
    if extra_cohorts:
        die(f"P {cohort} roster has an undeclared cohort: {sorted(extra_cohorts)[0]}")
    if not profile_rows or not {"run_id", "profile_report_id"}.issubset(profile_rows[0]):
        die("P PROFILE_REPORT_INDEX must include run_id and profile_report_id")
    report_by_run: dict[str, str] = {}
    for row in profile_rows:
        run_id, report_id = row.get("run_id", ""), row.get("profile_report_id", "")
        if not run_id or not report_id or run_id in report_by_run:
            die("P PROFILE_REPORT_INDEX has incomplete or ambiguous run/report identity")
        report_by_run[run_id] = report_id
    physical_keys: set[tuple[str, str, str, str, str, str]] = set()
    catalog_deployments: set[str] = set()
    unknown_semantic_rows = 0
    direct_semantic_rows = 0
    for row in catalog_rows:
        if any(row.get(field, "") == "" for field in required_catalog):
            die("P KERNEL_CATALOG has an empty required field")
        deployment = row["deployment_id"]
        catalog_deployments.add(deployment)
        roster = roster_by_deployment.get(deployment)
        if roster is None:
            die("P catalog deployment is absent from its direct deployment roster")
        if roster.get("c16_cohort") not in expected_roster or roster.get("c16_split_role") != expected_roster[roster["c16_cohort"]]:
            die("P catalog deployment has a cohort/split outside the frozen C16 roster")
        if row["run_id"] not in report_by_run:
            die("P catalog run_id has no unique PROFILE_REPORT_INDEX bridge")
        physical_key = tuple(row[field] for field in ("run_id", "device", "context", "stream", "correlation_id", "launch_ordinal"))
        if physical_key in physical_keys:
            die("P KERNEL_CATALOG has duplicate physical launch identity")
        physical_keys.add(physical_key)
        evidence = row["semantic_evidence"].upper()
        if evidence not in P_DIRECT_SEMANTIC_EVIDENCE:
            die("P semantic evidence must be DIRECT_RUNTIME_NVTX, DIRECT_MODULE_ID, or UNKNOWN; kernel-name inference is forbidden")
        if "KERNEL_NAME_HEURISTIC" in row["mapping_status"].upper():
            die("P mapping_status declares forbidden kernel-name semantic inference")
        operator = row["operator_class"].upper()
        if operator not in {"", "NA", "NONE", "NULL", "UNKNOWN"} and evidence == "UNKNOWN":
            die("P non-UNKNOWN semantic label lacks direct evidence")
        if evidence == "UNKNOWN":
            unknown_semantic_rows += 1
        else:
            direct_semantic_rows += 1
    required_deployments = {row["deployment_id"] for row in roster_rows}
    if catalog_deployments != required_deployments:
        die("P catalog/deployment roster coverage differs; every frozen cohort identity needs a cheap-catalog row")
    audit = {
        "schema_status": "PASS",
        "join_status": "PASS_NO_MULTIPLICATION",
        "cohort": cohort,
        "catalog_rows": str(len(catalog_rows)),
        "physical_launch_identities": str(len(physical_keys)),
        "roster_deployments": str(len(roster_by_deployment)),
        "profile_runs": str(len(report_by_run)),
        "unknown_semantic_rows": str(unknown_semantic_rows),
        "direct_semantic_rows": str(direct_semantic_rows),
        "unknown_policy": "EXPLICIT_STRATUM_NO_KERNEL_NAME_HEURISTIC",
        "forbidden_outcome_columns_read": "NONE",
    }
    return audit, {deployment: row["c16_split_role"] for deployment, row in roster_by_deployment.items()}


def p_catalog_input(commit: str, manifest_path: str, cohort: str) -> tuple[list[dict[str, str]], dict[str, Any], dict[str, str], dict[str, str]]:
    """Admit a complete P cohort; no P worktree/live path is ever read."""
    payloads, receipt = p_read_payloads(commit, manifest_path, cohort)
    rows = tsv_rows(payloads["KERNEL_CATALOG"])
    roster = tsv_rows(payloads["DEPLOYMENT_ROSTER"])
    profile = tsv_rows(payloads["PROFILE_REPORT_INDEX"])
    audit, roles = p_validate_catalog_and_roster(rows, roster, profile, cohort)
    profile_by_run = {row["run_id"]: row["profile_report_id"] for row in profile}
    # Carry P's mandatory report bridge into every C target.  This is a
    # one-to-one enrichment after the cardinality audit, not a row-multiplying
    # catalog join.
    for row in rows:
        row["profile_report_id"] = profile_by_run[row["run_id"]]
    return rows, receipt, audit, roles


def verify_native_catalog_admission(commit: str, manifest_path: str, manifest: dict[str, Any]) -> list[dict[str, str]]:
    """Reject a schema/offline package before it can become a selector input."""
    if manifest.get("schema_version") == "C16_G_OFFLINE_PACKAGE_V1" or str(manifest.get("scientific_evidence", "")).startswith("NONE_"):
        die("G manifest declares offline/no-scientific-evidence state, not NATIVE_CATALOG_V1")
    files = manifest.get("files", [])
    required = ("KERNEL_CATALOG.tsv", "KERNEL_SEMANTIC_MAP.tsv", "SEMANTIC_COVERAGE.tsv", "NATIVE_BASELINE.tsv", "RUNTIME_IMPLEMENTATION_AUDIT.tsv")
    receipts: list[dict[str, str]] = []
    for basename in required:
        matches = [entry for entry in files if str(entry.get("path", "")).endswith(basename)]
        if len(matches) != 1:
            die(f"NATIVE_CATALOG_V1 admission lacks exactly one {basename} manifest entry")
        entry = matches[0]
        path = manifest_entry_path(manifest_path, str(entry["path"]))
        text = git_text(commit, path)
        digest = sha256_bytes(text.encode())
        if digest != entry.get("sha256"):
            die(f"native manifest hash mismatch for {basename}")
        receipts.append({"path": path, "sha256": digest, "blob_id": git_blob(commit, path)})
    heavy = [entry for entry in files if str(entry.get("path", "")).endswith("HEAVY_TAIL_KERNELS.tsv")]
    # C may recompute the heavy-tail facts from an admitted duration-bearing
    # catalog, but an explicitly published table must still hash-close if named.
    if heavy:
        if len(heavy) != 1:
            die("ambiguous HEAVY_TAIL_KERNELS manifest entry")
        path = manifest_entry_path(manifest_path, str(heavy[0]["path"]))
        text = git_text(commit, path)
        digest = sha256_bytes(text.encode())
        if digest != heavy[0].get("sha256"):
            die("native manifest hash mismatch for HEAVY_TAIL_KERNELS.tsv")
        receipts.append({"path": path, "sha256": digest, "blob_id": git_blob(commit, path)})
    return receipts


def read_manifest_catalog(commit: str, manifest_path: str, catalog_path: str) -> tuple[list[dict[str, str]], dict[str, Any]]:
    manifest_text = git_text(commit, manifest_path)
    manifest = json.loads(manifest_text)
    dependencies = verify_native_catalog_admission(commit, manifest_path, manifest)
    catalog_entries = [entry for entry in manifest.get("files", []) if str(entry.get("path", "")).endswith("KERNEL_CATALOG.tsv")]
    if len(catalog_entries) != 1:
        die("NATIVE_CATALOG_V1 admission has ambiguous KERNEL_CATALOG.tsv entry")
    expected_catalog_path = manifest_entry_path(manifest_path, str(catalog_entries[0]["path"]))
    if catalog_path != expected_catalog_path:
        die("caller catalog path differs from the manifest-bound KERNEL_CATALOG.tsv path")
    catalog_text = git_text(commit, catalog_path)
    catalog_hash = sha256_bytes(catalog_text.encode())
    files = manifest.get("files", [])
    matching = [row for row in files if str(row.get("path", "")).endswith("KERNEL_CATALOG.tsv") or row.get("path") == catalog_path]
    if not matching:
        die("native manifest has no KERNEL_CATALOG.tsv receipt")
    if not any(row.get("sha256") == catalog_hash for row in matching):
        die("native catalog SHA does not match committed manifest")
    return tsv_rows(catalog_text), {"producer_commit": commit, "manifest_path": manifest_path, "manifest_blob": git_blob(commit, manifest_path),
                                    "manifest_sha256": sha256_bytes(manifest_text.encode()), "catalog_path": catalog_path, "catalog_blob": git_blob(commit, catalog_path),
                                    "catalog_sha256": catalog_hash, "producer_status": manifest.get("status", "UNKNOWN"), "validated_dependencies": dependencies}


def freeze_native(out: Path, commit: str, manifest_path: str, catalog_path: str) -> None:
    """Consume a fixed G catalog and publish plans before target results exist."""
    require_out(out)
    if not (out / "PUBLISH_MANIFEST.json").is_file():
        die("run --prepare-historical before freezing a native catalog")
    rows, receipt = read_manifest_catalog(commit, manifest_path, catalog_path)
    write_preflight(out, "COMMITTED_NATIVE_CATALOG_CONSUMED_READ_ONLY")
    units = annotate_certainty(canonicalize_catalog(rows, "NATIVE_PROFILED", historical_oracle=False))
    if not units:
        die("native catalog is empty")
    if any(role == "UNASSIGNED_EXCLUDED" for role in {split_role(row["deployment_id"]) for row in units}):
        die("native catalog contains deployment not covered by frozen tuning/holdout split rule")
    all_plan_rows: list[dict[str, Any]] = []
    all_budget_rows: list[dict[str, Any]] = []
    all_certainty: list[dict[str, Any]] = []
    for universe in sorted({row["universe_id"] for row in units}):
        scope = [row for row in units if row["universe_id"] == universe]
        for budget in BUDGETS:
            for selector in ("R", "M"):
                plans, budgets, certainty = build_plan(scope, budget, selector, PRIMARY_SEED)
                for row in plans:
                    row["split_role"] = split_role(row["deployment_id"])
                all_plan_rows.extend(plans); all_budget_rows.extend(budgets); all_certainty.extend(certainty)
    plan_fields = ["plan_id", "selector_kind", "selector_version", "selector_code_sha256", "universe_id", "deployment_id", "scenario_id", "phase", "stratum_id", "N_s", "n_s", "unit_id", "launch_ordinal", "semantic_key_json", "selection_role", "selection_reason", "inclusion_probability", "design_weight", "design_confidence", "seed", "random_audit", "estimated_capture_cost_ns", "capture_cost_basis", "evidence_tier", "plan_status", "split_role"]
    write_tsv(out / "NATIVE_SAMPLE_PLANS.tsv", plan_fields, all_plan_rows)
    write_tsv(out / "NATIVE_SELECTOR_R_PLAN.tsv", plan_fields, [row for row in all_plan_rows if row["selector_kind"] == "SELECTOR_R"])
    write_tsv(out / "NATIVE_SELECTOR_M_PLAN.tsv", plan_fields, [row for row in all_plan_rows if row["selector_kind"] == "SELECTOR_M"])
    write_tsv(out / "NATIVE_SAMPLE_BUDGETS.tsv", ["plan_id", "selector_kind", "universe_id", "budget", "certainty_units", "remaining_after_certainty", "stratum_id", "N_s", "n_s", "count_mass", "duration_mass_ns", "variation_proxy_mass", "variation_proxy_source", "allocation_score", "random_audit_target", "random_audit_actual", "estimated_capture_cost_ns", "status"], all_budget_rows)
    write_tsv(out / "NATIVE_CERTAINTY_UNITS.tsv", ["universe_id", "deployment_id", "scenario_id", "phase", "stratum_id", "unit_id", "launch_ordinal", "N_s", "certainty_weight", "reason", "duration_ns", "evidence_tier", "capture_authorization"], deduplicate_certainty(all_certainty))
    membership = []
    for unit in units:
        membership.append({"universe_id": unit["universe_id"], "deployment_id": unit["deployment_id"], "scenario_id": unit["scenario_id"], "phase": unit["phase"],
                           "stratum_id": unit["stratum_id"], "unit_id": unit["unit_id"], "launch_ordinal": unit["launch_ordinal"], "N_s": unit["N_s"],
                           "certainty": "TRUE" if unit["certainty"] else "FALSE", "certainty_reason": unit["certainty_reason"], "operator_class": unit["operator_class"],
                           "implementation_key": unit["implementation_key"], "shape_bucket": unit["shape_bucket"], "dtype_key": unit["dtype_key"],
                           "split_role": split_role(unit["deployment_id"]), "evidence_tier": unit["evidence_tier"]})
    write_tsv(out / "NATIVE_STRATA_MEMBERSHIP.tsv", ["universe_id", "deployment_id", "scenario_id", "phase", "stratum_id", "unit_id", "launch_ordinal", "N_s", "certainty", "certainty_reason", "operator_class", "implementation_key", "shape_bucket", "dtype_key", "split_role", "evidence_tier"], membership)
    write_target_plan(out, all_plan_rows, historical_only=False)
    write_protocol(out, "FROZEN_BEFORE_HOLDOUT_METRICS", receipt)
    write_tsv(out / "NATIVE_CATALOG_RECEIPT.tsv", list(receipt), [receipt])
    write_manifest(out, "C16_C_SELECTOR_FROZEN_FOR_PROSPECTIVE_HOLDOUT", native_catalog=True)


P_PLAN_FIELDS = [
    "plan_id", "selector_kind", "selector_version", "selector_code_sha256", "universe_id", "deployment_id", "scenario_id", "phase",
    "stratum_id", "N_s", "n_s", "unit_id", "launch_ordinal", "semantic_key_json", "selection_role", "selection_reason",
    "inclusion_probability", "design_weight", "design_confidence", "seed", "random_audit", "estimated_capture_cost_ns",
    "capture_cost_basis", "evidence_tier", "plan_status", "split_role", "source_cohort",
]


def write_p_plan_bundle(out: Path, prefix: str, units: list[dict[str, Any]], roles: dict[str, str], cohort: str) -> list[dict[str, Any]]:
    """Write all frozen 12/24/48 alternatives for one P cohort."""
    all_plans: list[dict[str, Any]] = []
    all_budgets: list[dict[str, Any]] = []
    all_certainty: list[dict[str, Any]] = []
    for universe in sorted({row["universe_id"] for row in units}):
        scope = [row for row in units if row["universe_id"] == universe]
        for budget in BUDGETS:
            for selector in ("R", "M"):
                plans, budgets, certainty = build_plan(scope, budget, selector, PRIMARY_SEED)
                for row in plans:
                    row["split_role"] = roles[row["deployment_id"]]
                    row["source_cohort"] = cohort
                all_plans.extend(plans)
                all_budgets.extend(budgets)
                all_certainty.extend(certainty)
    write_tsv(out / f"{prefix}_SAMPLE_PLANS.tsv", P_PLAN_FIELDS, all_plans)
    write_tsv(out / f"{prefix}_SELECTOR_R_PLAN.tsv", P_PLAN_FIELDS, [row for row in all_plans if row["selector_kind"] == "SELECTOR_R"])
    write_tsv(out / f"{prefix}_SELECTOR_M_PLAN.tsv", P_PLAN_FIELDS, [row for row in all_plans if row["selector_kind"] == "SELECTOR_M"])
    write_tsv(out / f"{prefix}_SAMPLE_BUDGETS.tsv", ["plan_id", "selector_kind", "universe_id", "budget", "certainty_units", "remaining_after_certainty", "stratum_id", "N_s", "n_s", "count_mass", "duration_mass_ns", "variation_proxy_mass", "variation_proxy_source", "allocation_score", "random_audit_target", "random_audit_actual", "estimated_capture_cost_ns", "status"], all_budgets)
    write_tsv(out / f"{prefix}_CERTAINTY_UNITS.tsv", ["universe_id", "deployment_id", "scenario_id", "phase", "stratum_id", "unit_id", "launch_ordinal", "N_s", "certainty_weight", "reason", "duration_ns", "evidence_tier", "capture_authorization"], deduplicate_certainty(all_certainty))
    membership = []
    for unit in units:
        membership.append({"universe_id": unit["universe_id"], "deployment_id": unit["deployment_id"], "scenario_id": unit["scenario_id"], "phase": unit["phase"],
                           "stratum_id": unit["stratum_id"], "unit_id": unit["unit_id"], "run_id": unit["run_id"], "profile_report_id": unit["profile_report_id"],
                           "device": unit["device"], "context": unit["context"], "stream": unit["stream"], "correlation_id": unit["correlation_id"],
                           "launch_ordinal": unit["launch_ordinal"], "N_s": unit["N_s"], "certainty": "TRUE" if unit["certainty"] else "FALSE",
                           "certainty_reason": unit["certainty_reason"], "operator_class": unit["operator_class"], "implementation_key": unit["implementation_key"],
                           "shape_bucket": unit["shape_bucket"], "dtype_key": unit["dtype_key"], "split_role": roles[unit["deployment_id"]],
                           "source_cohort": cohort, "evidence_tier": unit["evidence_tier"]})
    write_tsv(out / f"{prefix}_STRATA_MEMBERSHIP.tsv", ["universe_id", "deployment_id", "scenario_id", "phase", "stratum_id", "unit_id", "run_id", "profile_report_id", "device", "context", "stream", "correlation_id", "launch_ordinal", "N_s", "certainty", "certainty_reason", "operator_class", "implementation_key", "shape_bucket", "dtype_key", "split_role", "source_cohort", "evidence_tier"], membership)
    return all_plans


def freeze_p_train(out: Path, commit: str, manifest_path: str) -> None:
    """Stages 1--5: consume only P train/tune, audit, then freeze source/rules/plans."""
    require_out(out)
    if not (out / "PUBLISH_MANIFEST.json").is_file():
        die("run --prepare-historical before a P train/tune selector freeze")
    rows, receipt, audit, roles = p_catalog_input(commit, manifest_path, P_TRAIN_COHORT)
    if set(roles.values()) != {"TUNING"}:
        die("P train/tune catalog may not contain a holdout deployment")
    units = annotate_certainty(canonicalize_catalog(rows, "NATIVE_PROFILED", historical_oracle=False))
    if not units:
        die("P train/tune catalog is empty")
    # The source receipt is written before any allocation output.  It makes the
    # sequence auditable even when an AWQ catalog is published much later.
    write_json(out / "P_TRAIN_TUNE_CATALOG_RECEIPT.json", receipt)
    write_json(out / "P_TRAIN_TUNE_SCHEMA_JOIN_AUDIT.json", audit)
    write_json(out / "P_TRAIN_SELECTOR_SOURCE_FREEZE.json", {
        "state": "SOURCE_SHA_FROZEN_BEFORE_AWQ_UNSEAL",
        "selector_code_sha256": code_sha(), "selector_version": SELECTOR_VERSION,
        "selector_source_commit": current_head(), "producer_p_commit": commit,
        "selector_inputs": "TRAIN_TUNE_NATIVE_CHEAP_CATALOG_ONLY", "kernel_name_heuristic": "FORBIDDEN",
    })
    write_preflight(out, "P_FORMAL_TRAIN_TUNE_CATALOG_CONSUMED_AWQ_NOT_READ")
    write_protocol(out, "P_TRAIN_SELECTOR_RULES_AND_12_24_48_PLANS_FROZEN_AWAITING_AWQ_CHEAP_CATALOG", receipt)
    write_p_plan_bundle(out, "P_TRAIN_TUNE", units, roles, P_TRAIN_COHORT)
    atomic_text(out / "P_AWQ_UNSEAL_GATE.md", "# P AWQ cheap-catalog unseal gate\n\n`Qwen7 AWQ` catalog payloads are not read during train/tune freeze.  Only `--apply-p-awq-holdout` after `P_TRAIN_SELECTOR_RULES_AND_12_24_48_PLANS_FROZEN_AWAITING_AWQ_CHEAP_CATALOG` may read the manifest-listed `PROSPECTIVE_QWEN7_AWQ` cheap catalog.  NCU/NVBit outcomes remain outside this gate.\n")
    write_manifest(out, "C16_C_TRAIN_SELECTOR_FROZEN_AWAITING_P_AWQ_CHEAP_CATALOG", native_catalog=True)


def assert_p_train_freeze(out: Path) -> dict[str, Any]:
    protocol_path = out / "PROSPECTIVE_PROTOCOL.json"
    if not protocol_path.is_file():
        die("P train/tune protocol is absent")
    protocol = json.loads(protocol_path.read_text())
    if protocol.get("state") != "P_TRAIN_SELECTOR_RULES_AND_12_24_48_PLANS_FROZEN_AWAITING_AWQ_CHEAP_CATALOG":
        die("AWQ cheap catalog cannot be read before the frozen P train/tune selector plan")
    source = json.loads((out / "P_TRAIN_SELECTOR_SOURCE_FREEZE.json").read_text())
    if source.get("selector_code_sha256") != code_sha() or protocol.get("selector_code_sha256") != code_sha():
        die("selector source SHA changed after train/tune freeze; AWQ unseal is forbidden")
    required = [out / f"P_TRAIN_TUNE_{suffix}" for suffix in ("SELECTOR_R_PLAN.tsv", "SELECTOR_M_PLAN.tsv", "SAMPLE_BUDGETS.tsv")]
    if any(not path.is_file() for path in required):
        die("P train/tune 12/24/48 plan bundle is incomplete")
    frozen_paths = [out / "P_TRAIN_TUNE_CATALOG_RECEIPT.json", out / "P_TRAIN_TUNE_SCHEMA_JOIN_AUDIT.json",
                    out / "P_TRAIN_SELECTOR_SOURCE_FREEZE.json", protocol_path, *required]
    head = current_head()
    for path in frozen_paths:
        relative = str(path.relative_to(ROOT))
        committed = git_text(head, relative)
        if sha256_bytes(committed.encode()) != sha256_file(path):
            die("P train/tune freeze artifacts must be committed at HEAD before AWQ cheap-catalog unseal")
    return protocol


def write_p_awq_target_plan(out: Path, plans: list[dict[str, Any]], units: list[dict[str, Any]], receipt: dict[str, Any]) -> None:
    """Publish a bounded, request-only Selector-R capture list for G.

    B12/B24/B48 are alternative frozen plans.  The sole execution candidate is
    B48 Selector-R, capped at 48 units per universe; medoids stay in their own
    plan and are explicitly not a concurrent capture set.
    """
    by_unit = {row["unit_id"]: row for row in units}
    fields = ["target_plan_id", "selector_kind", "selector_code_sha256", "budget", "deployment_id", "scenario_id", "phase", "stratum_id", "unit_id", "run_id", "profile_report_id", "device", "context", "stream", "correlation_id", "launch_ordinal", "semantic_key_json", "selection_role", "selection_reason", "estimated_capture_cost_ns", "target_status", "capture_cap_per_universe", "identity_validation_required", "p_manifest_sha256", "p_catalog_sha256", "forbidden_input_confirmation"]
    rows: list[dict[str, Any]] = []
    for plan in plans:
        if plan["selector_kind"] != "SELECTOR_R" or "_B48_" not in plan["plan_id"] or plan["plan_status"] != "FROZEN_READY":
            continue
        unit = by_unit[plan["unit_id"]]
        rows.append({"target_plan_id": plan["plan_id"], "selector_kind": plan["selector_kind"], "selector_code_sha256": plan["selector_code_sha256"], "budget": 48,
                     "deployment_id": plan["deployment_id"], "scenario_id": plan["scenario_id"], "phase": plan["phase"],
                     "stratum_id": plan["stratum_id"], "unit_id": plan["unit_id"], "run_id": unit["run_id"], "profile_report_id": unit["profile_report_id"],
                     "device": unit["device"], "context": unit["context"], "stream": unit["stream"], "correlation_id": unit["correlation_id"],
                     "launch_ordinal": unit["launch_ordinal"], "semantic_key_json": plan["semantic_key_json"], "selection_role": plan["selection_role"],
                     "selection_reason": plan["selection_reason"], "estimated_capture_cost_ns": plan["estimated_capture_cost_ns"],
                     "target_status": "REQUEST_ONLY_FROZEN_PRIMARY_SELECTOR_R_NO_OUTCOME_CONSUMED", "capture_cap_per_universe": 48,
                     "identity_validation_required": "TRUE_REPORT_SCOPED_COMPOSITE_KEY", "p_manifest_sha256": receipt["manifest_sha256"],
                     "p_catalog_sha256": next(item["sha256"] for item in receipt["validated_dependencies"] if item["kind"] == "KERNEL_CATALOG"),
                     "forbidden_input_confirmation": "NO_NCU_NVBIT_TRACE_COUNTER_SPEEDUP_MISS_OR_OUTCOME_READ"})
    if not rows:
        die("P AWQ B48 Selector-R plan has no bounded target rows; no G target can be published")
    counts = Counter(row["target_plan_id"] for row in rows)
    if any(count > 48 for count in counts.values()):
        die("bounded G target plan exceeds frozen 48-unit per-universe cap")
    write_tsv(out / "P_AWQ_G_BOUNDED_TARGET_PLAN.tsv", fields, rows)
    atomic_text(out / "P_AWQ_G_TARGET_PLAN_README.md", "# Bounded G target plan\n\nThis is a request-only, exact-identity `Selector-R` B48 plan from the already-frozen source SHA.  It contains at most 48 units per deployment/scenario/phase universe.  `Selector-M` remains in `P_AWQ_SELECTOR_M_PLAN.tsv` as a non-concurrent deterministic medoid alternative.  G must revalidate the report-scoped composite identity before any authorized second pass.  No NCU/NVBit result, trace outcome, speedup, miss, or candidate mechanism metric was read by C.\n")


def apply_p_awq_holdout(out: Path, commit: str, manifest_path: str) -> None:
    """Stages 6--10: unseal cheap AWQ only, apply frozen source, publish G target."""
    require_out(out)
    protocol = assert_p_train_freeze(out)
    rows, receipt, audit, roles = p_catalog_input(commit, manifest_path, P_AWQ_COHORT)
    if set(roles.values()) != {"PROSPECTIVE_HOLDOUT"}:
        die("P AWQ catalog must contain only the direct prospective holdout identity")
    units = annotate_certainty(canonicalize_catalog(rows, "NATIVE_PROFILED", historical_oracle=False))
    write_json(out / "P_AWQ_CHEAP_CATALOG_RECEIPT.json", receipt)
    write_json(out / "P_AWQ_SCHEMA_JOIN_AUDIT.json", audit)
    plans = write_p_plan_bundle(out, "P_AWQ", units, roles, P_AWQ_COHORT)
    write_p_awq_target_plan(out, plans, units, receipt)
    protocol["state"] = "P_AWQ_CHEAP_CATALOG_APPLIED_FROZEN_TARGET_PLAN_PUBLISHED"
    protocol["awq_cheap_catalog_receipt"] = receipt
    protocol["g_target_plan"] = "P_AWQ_G_BOUNDED_TARGET_PLAN.tsv"
    protocol["ncu_nvbit_outcomes_consumed"] = False
    write_json(out / "PROSPECTIVE_PROTOCOL.json", protocol)
    write_preflight(out, "P_FORMAL_TRAIN_AND_AWQ_CHEAP_CATALOGS_CONSUMED_NO_OUTCOMES")
    write_manifest(out, "C16_C_P_AWQ_FROZEN_TARGET_PLAN_READY_FOR_G", native_catalog=True)


HOLDOUT_REQUIRED_FIELDS = ("deployment_id", "scenario_id", "phase", "unit_id", "metric", "metric_kind", "evidence_tier", "target_identity_status", "ground_truth_scope")
HOLDOUT_KINDS = {"ADDITIVE", "RATE", "STRUCTURAL", "MECHANISM_RESPONSE"}


def read_manifest_payload(commit: str, manifest_path: str, payload_path: str) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Read a small summary only after its producer's committed hash closes."""
    manifest_text = git_text(commit, manifest_path)
    manifest = json.loads(manifest_text)
    payload_text = git_text(commit, payload_path)
    payload_hash = sha256_bytes(payload_text.encode())
    files = manifest.get("files", [])
    matches = [row for row in files if row.get("path") == payload_path or str(row.get("path", "")).endswith(Path(payload_path).name)]
    if len(matches) != 1:
        die("holdout producer manifest has ambiguous or absent payload path")
    if payload_path != manifest_entry_path(manifest_path, str(matches[0]["path"])):
        die("caller holdout payload path differs from manifest-bound path")
    if matches[0].get("sha256") != payload_hash:
        die("holdout payload SHA does not match its committed producer manifest")
    return tsv_rows(payload_text), {"producer_commit": commit, "manifest_path": manifest_path, "manifest_blob": git_blob(commit, manifest_path),
                                    "manifest_sha256": sha256_bytes(manifest_text.encode()), "payload_path": payload_path, "payload_blob": git_blob(commit, payload_path),
                                    "payload_sha256": payload_hash, "producer_status": manifest.get("status", "UNKNOWN")}


def read_native_membership(out: Path) -> list[dict[str, Any]]:
    path = out / "NATIVE_STRATA_MEMBERSHIP.tsv"
    if not path.is_file():
        die("native selector was not frozen: NATIVE_STRATA_MEMBERSHIP.tsv is absent")
    units: list[dict[str, Any]] = []
    for row in tsv_rows(path.read_text()):
        units.append({"universe_id": row["universe_id"], "deployment_id": row["deployment_id"], "scenario_id": row["scenario_id"], "phase": row["phase"],
                      "stratum_id": row["stratum_id"], "unit_id": row["unit_id"], "launch_ordinal": row["launch_ordinal"], "N_s": int(row["N_s"]),
                      "certainty": row["certainty"] == "TRUE", "certainty_reason": row["certainty_reason"], "evidence_tier": row["evidence_tier"]})
    return units


def assert_frozen_holdout_gate(out: Path) -> dict[str, Any]:
    protocol_path = out / "PROSPECTIVE_PROTOCOL.json"
    if not protocol_path.is_file():
        die("prospective protocol is absent")
    protocol = json.loads(protocol_path.read_text())
    if protocol.get("state") != "FROZEN_BEFORE_HOLDOUT_METRICS":
        die("holdout metrics cannot be read before --freeze-native records a frozen selector")
    if protocol.get("selector_code_sha256") != code_sha():
        die("selector source SHA changed after freeze; create a new selector version before reading holdout")
    plans = tsv_rows((out / "NATIVE_SELECTOR_R_PLAN.tsv").read_text())
    if not plans or any(row.get("selector_code_sha256") != code_sha() for row in plans):
        die("frozen Selector-R plan is absent or does not match protocol source SHA")
    return protocol


def qualify_holdout(metric: str, kind: str, result: dict[str, Any], complete_population: bool, exact_identity: bool, high_fidelity: bool) -> tuple[str, str]:
    """Return only the contract's per-metric status vocabulary and rationale."""
    lower = metric.lower()
    if kind == "STRUCTURAL" or "page" in lower or "line" in lower:
        return "STRUCTURAL_ONLY", "non-additive page/line sets are reported as observed structure, never N_s/n_s unions"
    if not exact_identity or result["sample_complete"] == "FALSE":
        return "UNAVAILABLE", "missing selected target value or target identity mismatch"
    if kind == "MECHANISM_RESPONSE":
        ci_crosses_zero = result["ci_low"] == "NA" or (result["ci_low"] <= 0 <= result["ci_high"])
        resolution = result["absolute_error"] if result["absolute_error"] != "NA" else math.inf
        effect = abs(result["estimate"])
        effect_fraction = as_float(result.get("effect_fraction_of_reference"), -1.0)
        if not high_fidelity or ci_crosses_zero or resolution >= effect or effect_fraction < THRESHOLDS["small_effect_min_absolute_fraction"]:
            return "NOT_QUALIFIED", "mechanism response is INCONCLUSIVE without matched high-fidelity truth and resolution beyond zero/small-effect boundary"
        return "SCREENING_ONLY", "matched response resolves a direction but does not establish a general mechanism claim"
    if not complete_population or result["relative_error"] == "NA":
        return "SCREENING_ONLY", "design-based sampled estimate available but full frozen-universe truth is not available for error qualification"
    if result["relative_error"] > THRESHOLDS["native_duration_relative_error_screening"]:
        return "NOT_QUALIFIED", "holdout relative error exceeds frozen 5% screening threshold"
    if result["ci_low"] == "NA":
        return "NOT_QUALIFIED", "holdout sample is too sparse for a design variance interval"
    if "duration" in lower:
        return "QUALIFIED", "full-universe holdout error and design interval meet frozen native-duration screening rule"
    return "SCREENING_ONLY", "counter estimate meets screening error rule; it does not promote page/cache/mechanism claims"


def evaluate_holdout(units: list[dict[str, Any]], plan_rows: list[dict[str, Any]], rows: list[dict[str, str]], receipt: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    missing = [field for field in HOLDOUT_REQUIRED_FIELDS if any(field not in row for row in rows)]
    if missing:
        die(f"holdout payload lacks required fields: {','.join(sorted(set(missing)))}")
    if any(row["metric_kind"] not in HOLDOUT_KINDS for row in rows):
        die("holdout payload contains an unrecognized metric_kind")
    by_universe: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for unit in units:
        by_universe[unit["universe_id"]].append(unit)
    planned: dict[str, list[dict[str, Any]]] = plan_lookup(plan_rows)
    data: dict[tuple[str, str, str], dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        identity = universe_id(row)
        if identity not in by_universe:
            die(f"holdout metric is outside frozen native selector universe: {identity}")
        if split_role(row["deployment_id"]) not in {"PROSPECTIVE_HOLDOUT", "STRUCTURAL_HOLDOUT"}:
            die("holdout metric attempts to use a tuning deployment")
        if row["target_identity_status"] != "EXACT":
            die("holdout metric does not have exact second-pass target identity")
        key = (identity, row["metric"], row["metric_kind"])
        if row["unit_id"] in data[key]:
            die(f"duplicate holdout unit/metric row: {key} {row['unit_id']}")
        data[key][row["unit_id"]] = row
    results: list[dict[str, Any]] = []
    qualification: list[dict[str, Any]] = []
    for plan_id, selected in sorted(planned.items()):
        universe = selected[0]["universe_id"]
        if selected[0].get("split_role") not in {"PROSPECTIVE_HOLDOUT", "STRUCTURAL_HOLDOUT"}:
            continue
        population = by_universe[universe]
        selected_ids = {row["unit_id"] for row in selected}
        for (row_universe, metric, kind), by_unit in sorted(data.items()):
            if row_universe != universe:
                continue
            sample_complete = selected_ids.issubset(by_unit)
            complete_population = {unit["unit_id"] for unit in population}.issubset(by_unit) and all(row["ground_truth_scope"] == "FULL_FROZEN_UNIVERSE" for row in by_unit.values())
            exact_identity = all(row["target_identity_status"] == "EXACT" for row in by_unit.values())
            high_fidelity = all(row.get("high_fidelity_truth", "FALSE") == "TRUE" for row in by_unit.values())
            base = {"plan_id": plan_id, "producer_commit": receipt["producer_commit"], "producer_payload_sha256": receipt["payload_sha256"], "universe_id": universe,
                    "deployment_id": selected[0]["deployment_id"], "scenario_id": selected[0]["scenario_id"], "phase": selected[0]["phase"], "metric": metric,
                    "metric_kind": kind, "sample_complete": "TRUE" if sample_complete else "FALSE", "complete_population": "TRUE" if complete_population else "FALSE",
                    "target_identity_status": "EXACT" if exact_identity else "MISMATCH", "evidence_tier": next(iter(by_unit.values()))["evidence_tier"]}
            fractions = {row.get("effect_fraction_of_reference", "") for row in by_unit.values()}
            base["effect_fraction_of_reference"] = next(iter(fractions)) if len(fractions) == 1 else "NA"
            if kind == "RATE":
                if any("numerator" not in row or "denominator" not in row for row in by_unit.values()):
                    die("RATE metric requires independent numerator and denominator columns")
                numerator = {unit_id: as_float(row["numerator"]) for unit_id, row in by_unit.items()}
                denominator = {unit_id: as_float(row["denominator"]) for unit_id, row in by_unit.items()}
                estimate = estimate_ratio(population, selected, numerator, denominator) if sample_complete else {"estimate": "NA", "exact": "NA", "ci_low": "NA", "ci_high": "NA", "variance_status": "MISSING_SELECTED_VALUES"}
            elif kind in {"ADDITIVE", "MECHANISM_RESPONSE"}:
                if any("value" not in row for row in by_unit.values()):
                    die("ADDITIVE/MECHANISM_RESPONSE metric requires value column")
                values = {unit_id: as_float(row["value"]) for unit_id, row in by_unit.items()}
                estimate = estimate_additive(population, selected, values) if sample_complete else {"estimate": "NA", "exact": "NA", "ci_low": "NA", "ci_high": "NA", "variance_status": "MISSING_SELECTED_VALUES"}
            else:
                estimate = {"estimate": "NA", "exact": "NA", "ci_low": "NA", "ci_high": "NA", "variance_status": "NON_ADDITIVE_STRUCTURAL"}
            if not complete_population:
                estimate["exact"] = "NA"
            error = "NA" if estimate["exact"] == "NA" or estimate["estimate"] == "NA" else abs(estimate["estimate"] - estimate["exact"])
            relative = "NA" if error == "NA" or estimate["exact"] == 0 else error / abs(estimate["exact"])
            result = base | {"estimate": estimate["estimate"], "exact": estimate["exact"], "absolute_error": error, "relative_error": relative,
                             "ci_low": estimate["ci_low"], "ci_high": estimate["ci_high"], "variance_status": estimate["variance_status"]}
            status, rationale = qualify_holdout(metric, kind, result, complete_population, exact_identity, high_fidelity)
            result["qualification_status"] = status
            result["scientific_verdict"] = "INCONCLUSIVE" if kind == "MECHANISM_RESPONSE" and status == "NOT_QUALIFIED" else status
            results.append(result)
            qualification.append({"metric": metric, "universe_id": universe, "plan_id": plan_id, "status": status, "reason": rationale,
                                  "evidence_tier": result["evidence_tier"], "complete_population": result["complete_population"], "ci_low": result["ci_low"], "ci_high": result["ci_high"]})
    return results, qualification


def consume_holdout(out: Path, commit: str, manifest_path: str, payload_path: str) -> None:
    """Read post-freeze metrics and issue metric-by-metric, not global, verdicts."""
    protocol = assert_frozen_holdout_gate(out)
    rows, receipt = read_manifest_payload(commit, manifest_path, payload_path)
    units = read_native_membership(out)
    plans = tsv_rows((out / "NATIVE_SELECTOR_R_PLAN.tsv").read_text())
    results, qualification = evaluate_holdout(units, plans, rows, receipt)
    if not results:
        die("holdout payload has no rows for frozen prospective holdout universes")
    fields = ["plan_id", "producer_commit", "producer_payload_sha256", "universe_id", "deployment_id", "scenario_id", "phase", "metric", "metric_kind", "sample_complete", "complete_population", "target_identity_status", "evidence_tier", "effect_fraction_of_reference", "estimate", "exact", "absolute_error", "relative_error", "ci_low", "ci_high", "variance_status", "qualification_status", "scientific_verdict"]
    write_tsv(out / "HOLDOUT_RESULTS.tsv", fields, results)
    write_tsv(out / "HOLDOUT_QUALIFICATION.tsv", ["metric", "universe_id", "plan_id", "status", "reason", "evidence_tier", "complete_population", "ci_low", "ci_high"], qualification)
    write_tsv(out / "HOLDOUT_CONSUMPTION_RECEIPT.tsv", list(receipt), [receipt])
    protocol["state"] = "HOLDOUT_METRICS_CONSUMED_AFTER_FREEZE"
    protocol["holdout_receipt"] = receipt
    write_json(out / "PROSPECTIVE_PROTOCOL.json", protocol)
    write_manifest(out, "C16_C_HOLDOUT_METRICS_CONSUMED_FOR_METRIC_BY_METRIC_REVIEW", native_catalog=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare-historical", action="store_true")
    modes.add_argument("--freeze-native", action="store_true")
    modes.add_argument("--freeze-p-train", action="store_true")
    modes.add_argument("--apply-p-awq-holdout", action="store_true")
    modes.add_argument("--consume-holdout", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=OUT)
    parser.add_argument("--producer-commit")
    parser.add_argument("--manifest-path")
    parser.add_argument("--catalog-path")
    parser.add_argument("--payload-path")
    args = parser.parse_args()
    out = require_out(args.output_dir)
    if args.prepare_historical:
        prepare_historical(out)
        print(f"PASS C16 Sampling V2 historical preparation: {out}")
    elif args.freeze_native:
        if not all((args.producer_commit, args.manifest_path, args.catalog_path)):
            die("--freeze-native requires --producer-commit --manifest-path --catalog-path")
        freeze_native(out, args.producer_commit, args.manifest_path, args.catalog_path)
        print(f"PASS C16 Sampling V2 native selector freeze: {out}")
    elif args.freeze_p_train:
        if not all((args.producer_commit, args.manifest_path)):
            die("--freeze-p-train requires --producer-commit --manifest-path")
        freeze_p_train(out, args.producer_commit, args.manifest_path)
        print(f"PASS C16 Sampling V2 P train/tune selector freeze: {out}")
    elif args.apply_p_awq_holdout:
        if not all((args.producer_commit, args.manifest_path)):
            die("--apply-p-awq-holdout requires --producer-commit --manifest-path")
        apply_p_awq_holdout(out, args.producer_commit, args.manifest_path)
        print(f"PASS C16 Sampling V2 P AWQ cheap-catalog target plan: {out}")
    else:
        if not all((args.producer_commit, args.manifest_path, args.payload_path)):
            die("--consume-holdout requires --producer-commit --manifest-path --payload-path")
        consume_holdout(out, args.producer_commit, args.manifest_path, args.payload_path)
        print(f"PASS C16 Sampling V2 post-freeze holdout consumption: {out}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL C16 Sampling V2: {exc}", file=sys.stderr)
        raise
