#!/usr/bin/env python3
"""Read committed, independently closed C16 E1 review packs into paper tables.

No GPU or simulator is invoked. An uncommitted or unqualified source is an error;
an absent future simulator result is a PENDING row, never a zero.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PACKS = Path("docs/vm_tlb/review_packs")
OUT = PACKS / "C16_E1_PAPER_EVIDENCE_AND_RESULT_INFRASTRUCTURE_V1"
PREFIX = "C16_E1_"
BUDGETS = ("B8", "B16", "B24", "BFULL")
AUTHORITY_SNAPSHOT = "8dfd9c0fdc98314c2aa11710da9b89f59e4c7a66"
FIELDS = ("domain", "condition", "metric", "value", "unit", "status", "source_stage",
          "source_path", "source_sha256", "source_commit")


class SourceError(ValueError):
    pass


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


def committed_source(root: Path, relative: Path) -> tuple[dict, str, str]:
    if relative.is_absolute() or ".." in relative.parts:
        raise SourceError(f"unsafe source path: {relative}")
    path = root / relative
    if not path.is_file():
        raise SourceError(f"required source missing: {relative}")
    name = relative.as_posix()
    try:
        git(root, "ls-files", "--error-unmatch", "--", name)
        committed = git(root, "show", f"HEAD:{name}")
        commit = git(root, "log", "-1", "--format=%H", "--", name).decode().strip()
    except subprocess.CalledProcessError as exc:
        raise SourceError(f"source is not committed: {name}") from exc
    actual = path.read_bytes()
    if actual != committed or len(commit) != 40:
        raise SourceError(f"source differs from committed HEAD: {name}")
    try:
        value = json.loads(actual)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SourceError(f"invalid JSON: {name}") from exc
    if not isinstance(value, dict):
        raise SourceError(f"source root must be an object: {name}")
    return value, hashlib.sha256(actual).hexdigest(), commit


def require(obj: dict, key: str, kind: type, where: str):
    value = obj.get(key)
    if type(value) is not kind:
        raise SourceError(f"{where}.{key} must be {kind.__name__}")
    return value


def number(obj: dict, key: str, where: str) -> float:
    value = obj.get(key)
    if type(value) not in (int, float) or not math.isfinite(value):
        raise SourceError(f"{where}.{key} must be finite numeric data")
    return value


def qualified(root: Path, stage: str, decision_file: str, expected: dict) -> None:
    decision, _, _ = committed_source(root, PACKS / stage / decision_file)
    for key, value in expected.items():
        if decision.get(key) != value:
            raise SourceError(f"{stage} failed qualification: {key} != {value!r}")


def row(domain, condition, metric, value, unit, stage, path, sha, commit):
    return dict(domain=domain, condition=condition, metric=metric, value=value, unit=unit,
                status="ACCEPTED", source_stage=stage, source_path=path.as_posix(),
                source_sha256=sha, source_commit=commit)


def native_rows(root: Path) -> list[dict]:
    rows = []
    cost = PREFIX + "RESIDENCY_COST_BENEFIT_CLOSURE_CONSUMER_174NEW_V1"
    qualified(root, cost, "FINAL_DECISION.json", {
        "status": "PASS", "stage_label": "RESIDENCY_OFFSET_LOCALIZED",
        "all_four_budgets_closed": True, "all_top_level_decompositions_qualified": True,
        "scientific_mismatch": False})
    path = PACKS / cost / "INDEPENDENT_BUDGET_EFFECT_ANALYSIS.json"
    data, sha, commit = committed_source(root, path)
    if data.get("authority") != "INDEPENDENT_RAW_NATIVE_POLICY_ONLY":
        raise SourceError("cost authority mismatch")
    budgets = require(data, "budgets", dict, "cost")
    if set(budgets) != set(BUDGETS):
        raise SourceError("cost budget matrix must contain exactly B8/B16/B24/BFULL")
    cost_metrics = {
        "direct_up_saving_ms": "ms", "observed_decode_saving_ms": "ms",
        "measured_non_up_offset_ms": "ms", "self_attn_saving_ms": "ms",
        "unexplained_residual_ms": "ms", "localized_offset_fraction": "fraction",
        "mlp_top_saving_ms": "ms", "norm_saving_ms": "ms",
        "final_stage_saving_ms": "ms", "gate_saving_ms": "ms", "down_saving_ms": "ms",
    }
    for budget in BUDGETS:
        point = require(budgets, budget, dict, "cost.budgets")
        if point.get("decomposition_qualified") is not True or point.get("material_local_up_count") != 28:
            raise SourceError(f"cost {budget} lacks independent closure")
        medians = require(point, "medians", dict, budget)
        for metric, unit in cost_metrics.items():
            rows.append(row("native_budget", budget, metric, number(medians, metric, budget),
                            unit, cost, path, sha, commit))
        local = require(point, "local_up_d3_effect", dict, budget)
        if local.get("material") is not True:
            raise SourceError(f"cost {budget} local benefit not material")
        rows.append(row("native_budget", budget, "local_up_d3_benefit_fraction",
                        number(local, "benefit_fraction", budget), "fraction", cost, path, sha, commit))

    operator = PREFIX + "OPERATOR_FAMILY_EXPANSION_CONSUMER_174NEW_V1"
    qualified(root, operator, "FINAL_DECISION.json", {
        "status": "OPERATOR_FAMILY_INDEPENDENT_CLOSURE_PASS",
        "independent_stage_label": "OPERATOR_FAMILY_NOT_SUPPORTED",
        "raw_evidence_match": "PASS"})
    path = PACKS / operator / "INDEPENDENT_RESIDUAL_DECOMPOSITION.json"
    data, sha, commit = committed_source(root, path)
    for condition, local_metric in (("UP28", "direct_up_saving_ms"),
                                    ("GUD84", "direct_ffn_saving_ms")):
        point = require(data, condition, dict, "operator")
        for metric in (local_metric, "outside_ffn_residual_ms"):
            summary = require(point, metric, dict, condition)
            rows.append(row("operator_family", condition, metric,
                            number(summary, "median", condition), "ms", operator, path, sha, commit))
        effect = require(point, "whole_decode_effect", dict, condition)
        if effect.get("material_system") is not False:
            raise SourceError(f"operator {condition} closure changed")
        rows.append(row("operator_family", condition, "whole_decode_benefit_fraction",
                        number(effect, "benefit_fraction", condition), "fraction", operator, path, sha, commit))

    semantic = PREFIX + "SEMANTIC_NCU_V2_CONSUMER_174NEW_V1"
    qualified(root, semantic, "FINAL_DECISION.json", {
        "status": "C16_E1_SEMANTIC_NCU_V2_CONSUMER_PASS",
        "raw_recompute_matches_producer": True, "cache_causality_proven": False})
    path = PACKS / semantic / "CAPACITY_RESIDENCY_CONSISTENCY.json"
    data, sha, commit = committed_source(root, path)
    if (data.get("AWQ_packed_less_than_L2") is not True
            or data.get("RAW_dense_greater_than_L2") is not True
            or data.get("assessment") != "CONSISTENT_WITH_WARM_CACHE_CAPACITY_RESIDENCY_HYPOTHESIS_NOT_CAUSAL_PROOF"):
        raise SourceError("semantic capacity interpretation changed")
    for metric in ("AWQ_packed_storage_bytes", "RAW_FP16_dense_weight_bytes", "device_L2_bytes"):
        rows.append(row("footprint", "M1", metric, number(data, metric, "semantic"),
                        "bytes", semantic, path, sha, commit))
    return rows


def simulator_rows(root: Path) -> list[dict]:
    """Future pack contract: add one committed accepted JSON, then rerun this consumer."""
    candidate_paths = sorted((root / PACKS).glob("C16_E1_*/PAPER_SIM_RESULTS_ACCEPTED.json"),
                             key=lambda p: p.as_posix())
    if len(candidate_paths) > 1:
        raise SourceError("multiple accepted simulator result packs: select one authority")
    if not candidate_paths:
        return [dict(domain="simulator", condition=budget, metric=metric, value=None,
                     unit=unit, status="PENDING", source_stage="PENDING_B16_TIMING_RESULT" if budget == "B16" else "PENDING_FUTURE_BUDGET",
                     source_path="", source_sha256="", source_commit="")
                for budget in BUDGETS for metric, unit in (
                    ("window_speedup", "ratio"), ("baseline_cycles", "cycles"),
                    ("candidate_cycles", "cycles"), ("mechanism_activations", "count"),
                    ("protected_hits", "count"), ("admission_denials", "count"))]
    path = candidate_paths[0].relative_to(root)
    data, sha, commit = committed_source(root, path)
    expected_keys = {"schema", "status", "framework_commit", "core_commit",
                     "trace_sha256", "independent_review_pack", "results"}
    if set(data) != expected_keys:
        raise SourceError("simulator publication keys differ from V1 schema")
    if data.get("schema") != "C16_E1_PAPER_SIM_RESULTS_ACCEPTED_V1" or data.get("status") != "INDEPENDENT_ACCEPTED":
        raise SourceError("simulator source is not independently accepted")
    for key in ("framework_commit", "core_commit", "trace_sha256", "independent_review_pack"):
        if not isinstance(data.get(key), str) or not data[key]:
            raise SourceError(f"simulator provenance missing: {key}")
    for key in ("framework_commit", "core_commit"):
        if not re.fullmatch("[0-9a-f]{40}", data[key]):
            raise SourceError(f"simulator commit invalid: {key}")
    if not re.fullmatch("[0-9a-f]{64}", data["trace_sha256"]):
        raise SourceError("simulator trace SHA invalid")
    if data["independent_review_pack"] != path.parent.name:
        raise SourceError("simulator review pack identity mismatch")
    results = require(data, "results", dict, "simulator")
    if not results or not set(results).issubset(BUDGETS):
        raise SourceError("unexpected simulator budget")
    rows = []
    for budget in BUDGETS:
        if budget not in results:
            rows.extend(dict(domain="simulator", condition=budget, metric=metric, value=None,
                             unit=unit, status="PENDING", source_stage="PENDING_B16_TIMING_RESULT" if budget == "B16" else "PENDING_FUTURE_BUDGET",
                             source_path="", source_sha256="", source_commit="")
                        for metric, unit in (("window_speedup", "ratio"), ("baseline_cycles", "cycles"),
                                             ("candidate_cycles", "cycles"), ("mechanism_activations", "count"),
                                             ("protected_hits", "count"), ("admission_denials", "count")))
            continue
        point = require(results, budget, dict, "simulator.results")
        if set(point) != {"correctness_pass", "terminal_pass", "baseline_cycles",
                          "candidate_cycles", "mechanism_activations", "protected_hits",
                          "admission_denials"}:
            raise SourceError(f"simulator {budget} point keys differ from V1 schema")
        if point.get("correctness_pass") is not True or point.get("terminal_pass") is not True:
            raise SourceError(f"simulator {budget} correctness/terminal gate failed")
        baseline = number(point, "baseline_cycles", budget)
        candidate = number(point, "candidate_cycles", budget)
        if baseline <= 0 or candidate <= 0:
            raise SourceError(f"simulator {budget} cycles must be positive")
        values = {"window_speedup": baseline / candidate, "baseline_cycles": baseline,
                  "candidate_cycles": candidate}
        for counter in ("mechanism_activations", "protected_hits", "admission_denials"):
            value = number(point, counter, budget)
            if value < 0 or int(value) != value:
                raise SourceError(f"simulator {budget} counter invalid: {counter}")
            values[counter] = value
        for metric, value in values.items():
            unit = "ratio" if metric == "window_speedup" else "cycles" if metric.endswith("cycles") else "count"
            rows.append(row("simulator", budget, metric, value, unit,
                            path.parent.name, path, sha, commit))
    return rows


def build(root: Path) -> dict:
    try:
        git(root, "merge-base", "--is-ancestor", AUTHORITY_SNAPSHOT, "HEAD")
    except subprocess.CalledProcessError as exc:
        raise SourceError("repository does not descend from the frozen evidence snapshot") from exc
    rows = native_rows(root) + simulator_rows(root)
    return {"schema": "C16_E1_PAPER_RESULTS_V1", "authority_framework_head": AUTHORITY_SNAPSHOT,
            "rows": rows}


def write_tables(result: dict, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "PAPER_RESULTS_CURRENT.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (output / "PAPER_RESULTS_CURRENT.tsv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for item in result["rows"]:
            line = {**item, "value": "PENDING" if item["value"] is None else item["value"]}
            if item["status"] == "PENDING":
                for field in ("source_path", "source_sha256", "source_commit"):
                    line[field] = "PENDING"
            writer.writerow(line)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    write_tables(build(root), args.output or root / OUT)


if __name__ == "__main__":
    main()
