#!/usr/bin/env python3
"""Produce the reproducible Lane-A paper analysis from frozen FAST64 evidence.

The script deliberately consumes compact, committed accepted artifacts only.  It
first verifies their FAST64.7-bound hashes and reconciliation invariants, then
emits post-FAST64 *derived* tables and lightweight SVG figures.  It never reads
raw simulator logs and never writes under docs/dtc_l1/fast64/.
"""

from __future__ import annotations

import csv
import hashlib
import html
import subprocess
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "docs/dtc_l1/fast64/review_packs/FAST64_FINAL"
STAGE = ROOT / "docs/dtc_l1/fast64/generated"
OUT = ROOT / "docs/dtc_l1/post_fast64/generated"
ANALYSIS = ROOT / "docs/dtc_l1/post_fast64/POST_FAST64_PAPER_RESULT_ANALYSIS.md"
FROZEN_FAST64_COMMIT = "18a68dcccd795f1b6cda75504e9450d00c9cee02"
SM_COUNT = 64
NAN = "NONNUMERIC"

# These values are the FAST64.7 input-manifest hashes, copied here as an
# executable freeze rather than discovered from a mutable local input.
BOUND_HASHES = {
    "docs/dtc_l1/fast64/generated/fast64_4_cap_resolved_matrix_v1/fast64_4_triplets.tsv": "d4bd71c51419e0f2be4ab045285e087455a8976834934719810d77aefca2148a",
    "docs/dtc_l1/fast64/generated/fast64_4_cap_resolved_matrix_v1/fast64_4_speedup.tsv": "9c8909d5b870d8cc9638d20e4723579e41cc3f7b9e85bb5701107b7d4f3038c2",
    "docs/dtc_l1/fast64/generated/fast64_5_causal_analysis_v1/fast12_summary.csv": "53302fbb20593d530e8d1b51c5f2cefba33687b93ef1b2fea627c41d070be1ca",
    "docs/dtc_l1/fast64/generated/fast64_5_causal_analysis_v1/fast12_stalls.csv": "410c9abeb28fc9483357281a06ae7fb2a85254488ebc37351b2c091c35cbff34",
    "docs/dtc_l1/fast64/generated/fast64_5_causal_analysis_v1/fast12_io_oo.csv": "853d2d99feb9166512420f2c52d636501adc23813bf9892a816847ad0df9aac5",
    "docs/dtc_l1/fast64/generated/fast64_5_causal_analysis_v1/fast12_traffic.csv": "1847e75084d93479c11cf261ae57ccbd64592070ae80216fe3c7868b1c1bd30b",
    "docs/dtc_l1/fast64/generated/fast64_5_causal_analysis_v1/fast64_5_causal_classification.tsv": "f1249374f564499e5c1d18ee907ab6d5ffd9523dd9e6ee92ec9fd5f15c6ea675",
    "docs/dtc_l1/fast64/generated/fast64_6_sensitivity_v3/fast64_6_logical_plot.tsv": "fee2f86f1c769c4dae16af0a4bf723ed5fc568048a6719fe8843fb848d330f0e",
    "docs/dtc_l1/fast64/generated/fast64_6_sensitivity_v3/fast64_6_physical_plot.tsv": "6f4830c101367fa180fba0436acb23dfc9e74f6bae888c061bc2af2af3af0f6b",
    "docs/dtc_l1/fast64/generated/fast64_6_sensitivity_v3/fast64_6_pib_plot.tsv": "ea50d25be55dca4f4c5f5f2d128f0e6ba7c515acc33a7d49f83c6673506b4fee",
    "docs/dtc_l1/fast64/generated/fast64_6_sensitivity_v3/fast64_6_expected_deadlocks.tsv": "6b12976e7a78883bce130048f4f4820b1ee9b80f5ecc4788df2d81a7f1ee8d47",
}

FINAL_INPUTS = (
    "FAST12_summary.tsv",
    "aggregate_membership.tsv",
    "structural_pressure.tsv",
    "io_oo_mechanism.tsv",
    "traffic_pressure.tsv",
    "causal_classification.tsv",
    "fast64_6_logical_plot.tsv",
    "fast64_6_physical_plot.tsv",
    "fast64_6_pib_plot.tsv",
    "fast64_6_expected_deadlocks.tsv",
    "FAST64_7_INPUT_MANIFEST.tsv",
)


def read_delimited(path: Path, delimiter: str = "\t") -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source, delimiter=delimiter))


def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t", extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(value: str | int | float) -> float:
    return float(value)


def text_number(value: float | int, digits: int = 9) -> str:
    if isinstance(value, int) or float(value).is_integer():
        return str(int(value))
    return f"{value:.{digits}f}"


def ratio(numerator: str | int | float, denominator: str | int | float, multiplier: float = 1.0) -> str:
    denominator_value = number(denominator)
    if denominator_value == 0:
        return "UNSUPPORTED_ZERO_DENOMINATOR"
    return text_number(number(numerator) * multiplier / denominator_value)


def base_rows() -> list[dict[str, str]]:
    return [row for row in read_delimited(FINAL / "FAST12_summary.tsv") if row["workload"] != "GM-FAST12"]


def validate_inputs() -> tuple[list[dict[str, str]], dict[str, str]]:
    """Validate the frozen source package before deriving any output."""
    for rel, expected in BOUND_HASHES.items():
        actual = digest(ROOT / rel)
        if actual != expected:
            raise ValueError(f"FAST64-bound hash mismatch for {rel}: {actual} != {expected}")

    frozen_tree = ROOT / ".git"
    if not frozen_tree.exists():
        raise ValueError("This analysis must run from a Framework Git worktree")
    for command, failure in (
        (["git", "cat-file", "-e", f"{FROZEN_FAST64_COMMIT}^{{commit}}"], "frozen FAST64 commit object is unavailable"),
        (["git", "merge-base", "--is-ancestor", FROZEN_FAST64_COMMIT, "HEAD"], "analysis branch does not descend from frozen FAST64"),
    ):
        if subprocess.run(command, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
            raise ValueError(failure)

    summary = base_rows()
    if len(summary) != 12 or len({row["workload"] for row in summary}) != 12:
        raise ValueError("FAST12 membership is not exactly 12 unique workloads")
    membership = read_delimited(FINAL / "aggregate_membership.tsv")
    if membership != [{"aggregate": "GM-FAST12", "membership": "EXACT_12_ACCEPTED_PRIMARY_MEMBERS", "source": "FAST64.5/fast12_summary.csv"}]:
        raise ValueError("FAST12 membership marker does not match frozen acceptance")

    stage4 = read_delimited(STAGE / "fast64_4_cap_resolved_matrix_v1/fast64_4_triplets.tsv")
    stage5 = read_delimited(STAGE / "fast64_5_causal_analysis_v1/fast12_summary.csv", ",")
    stage4_by_workload = {row["workload"]: row for row in stage4}
    stage5_by_workload = {row["workload"]: row for row in stage5 if row["workload"] != "GM-FAST12"}
    if set(stage4_by_workload) != {row["workload"] for row in summary} or set(stage5_by_workload) != set(stage4_by_workload):
        raise ValueError("Stage4/Stage5 membership does not reconcile to accepted FAST12")
    for row in summary:
        workload = row["workload"]
        for field in ("base_cycles", "io_cycles", "oo_cycles", "instructions"):
            if row[field] != stage4_by_workload[workload][field] or row[field] != stage5_by_workload[workload][field]:
                raise ValueError(f"{workload} {field} fails Stage4/5 reconciliation")

    gm = next(row for row in read_delimited(FINAL / "FAST12_summary.tsv") if row["workload"] == "GM-FAST12")
    if gm["speedup_io"] != "1.326143376" or gm["speedup_oo"] != "1.592062402":
        raise ValueError("Accepted FAST12 GM changed")

    for final_name, stage5_name in (
        ("structural_pressure.tsv", "fast12_stalls.csv"),
        ("io_oo_mechanism.tsv", "fast12_io_oo.csv"),
        ("traffic_pressure.tsv", "fast12_traffic.csv"),
    ):
        final_rows = read_delimited(FINAL / final_name)
        stage5_rows = read_delimited(STAGE / "fast64_5_causal_analysis_v1" / stage5_name, ",")
        if final_rows != stage5_rows:
            raise ValueError(f"{final_name} fails accepted Stage5 reconciliation")

    expected_by_path = {row["input_path"]: row["sha256"] for row in read_delimited(FINAL / "FAST64_7_INPUT_MANIFEST.tsv")}
    for rel, expected in BOUND_HASHES.items():
        if expected_by_path.get(rel) != expected:
            raise ValueError(f"FAST64.7 manifest does not bind {rel}")
    return summary, gm


def build_input_manifest(summary: list[dict[str, str]]) -> None:
    rows: list[dict[str, str]] = [{
        "item": "accepted_framework_authority",
        "input_path": "hrl/decoupled-l1-fast64-v0",
        "expected_sha256_or_commit": FROZEN_FAST64_COMMIT,
        "actual_sha256_or_commit": FROZEN_FAST64_COMMIT,
        "verification": "FROZEN_AUTHORITY_DECLARED_AND_GIT_OBJECT_REQUIRED",
        "role": "immutable completed FAST64 authority",
        "evidence_class": "ACCEPTED_FAST64_EVIDENCE",
    }, {
        "item": "FAST12_membership",
        "input_path": "docs/dtc_l1/fast64/review_packs/FAST64_FINAL/FAST12_summary.tsv",
        "expected_sha256_or_commit": "exactly_12_unique_members",
        "actual_sha256_or_commit": str(len(summary)),
        "verification": "PASS_EXACT_12",
        "role": "primary aggregate membership",
        "evidence_class": "ACCEPTED_FAST64_EVIDENCE",
    }]
    for rel, expected in BOUND_HASHES.items():
        rows.append({
            "item": "FAST64_7_bound_compact_input",
            "input_path": rel,
            "expected_sha256_or_commit": expected,
            "actual_sha256_or_commit": digest(ROOT / rel),
            "verification": "PASS_SHA256_EQUAL",
            "role": "Stage4 primary, Stage5 analysis, or Stage6 sensitivity evidence",
            "evidence_class": "ACCEPTED_FAST64_EVIDENCE",
        })
    for name in FINAL_INPUTS:
        path = FINAL / name
        rows.append({
            "item": "FAST64_FINAL_compact_presentation_input",
            "input_path": str(path.relative_to(ROOT)),
            "expected_sha256_or_commit": digest(path),
            "actual_sha256_or_commit": digest(path),
            "verification": "PASS_SHA256_FROZEN_IN_DERIVATION_MANIFEST",
            "role": "accepted review-package compact table",
            "evidence_class": "ACCEPTED_FAST64_EVIDENCE",
        })
    fields = list(rows[0])
    write_tsv(OUT / "A_ACCEPTED_INPUT_MANIFEST.tsv", rows, fields)


def build_primary(summary: list[dict[str, str]], gm: dict[str, str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source in summary:
        rows.append({
            "workload": source["workload"], "aggregate": "NO", "instructions": source["instructions"],
            "base_cycles": source["base_cycles"], "io_cycles": source["io_cycles"], "oo_cycles": source["oo_cycles"],
            "base_normalized_cycles": "1.000000000",
            "io_normalized_cycles": ratio(source["io_cycles"], source["base_cycles"]),
            "oo_normalized_cycles": ratio(source["oo_cycles"], source["base_cycles"]),
            "base_speedup": "1.000000000", "io_speedup_over_base": source["speedup_io"],
            "oo_speedup_over_base": source["speedup_oo"],
            "normalization_formula": "mode_cycles / base_cycles; Base is exactly 1.0",
            "evidence_class": "ACCEPTED_FAST64_EVIDENCE",
            "accepted_source": "FAST64_FINAL/FAST12_summary.tsv",
        })
    rows.append({
        "workload": "GM-FAST12", "aggregate": "YES_EXACT_12_MEMBERS", "instructions": "exact_12_members",
        "base_cycles": "N/A", "io_cycles": "N/A", "oo_cycles": "N/A", "base_normalized_cycles": "1.000000000",
        "io_normalized_cycles": ratio(1, gm["speedup_io"]), "oo_normalized_cycles": ratio(1, gm["speedup_oo"]),
        "base_speedup": "1.000000000", "io_speedup_over_base": gm["speedup_io"],
        "oo_speedup_over_base": gm["speedup_oo"],
        "normalization_formula": "accepted geometric mean of 12 per-workload Base/mode speedups",
        "evidence_class": "ACCEPTED_FAST64_EVIDENCE", "accepted_source": "FAST64_FINAL/FAST12_summary.tsv",
    })
    write_tsv(OUT / "paper_primary_performance.tsv", rows, list(rows[0]))
    return rows


PRESSURE_FIELDS = (
    ("pib_full_events", "PIB full"),
    ("cacheline_all_lines_reserved_events", "true cacheline/all-lines-reserved"),
    ("tag_bank_conflicts", "Tag-bank conflict"),
    ("mshr_entry_full_events", "MSHR entry full"),
    ("mshr_merge_full_events", "MSHR merge full"),
    ("miss_queue_downstream_full_events", "missqueue/downstream full"),
)


def build_pressure(summary: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    performance = {row["workload"]: row for row in summary}
    raw_rows: list[dict[str, str]] = []
    norm_rows: list[dict[str, str]] = []
    for source in read_delimited(FINAL / "structural_pressure.tsv"):
        workload = source["workload"]
        for field, category in PRESSURE_FIELDS:
            raw_rows.append({
                "workload": workload, "pressure_field": field, "pressure_category": category,
                "raw_events": source[field], "counter_domain": "Base-mode accumulated event counter",
                "exclusivity": "NONEXCLUSIVE_DO_NOT_STACK_OR_SUM_AS_A_PERCENT",
                "evidence_class": "ACCEPTED_FAST64_EVIDENCE", "accepted_source": "FAST64_FINAL/structural_pressure.tsv",
            })
            norm_rows.append({
                "workload": workload, "pressure_field": field, "pressure_category": category,
                "raw_events": source[field], "base_instructions": performance[workload]["instructions"],
                "base_cycles": performance[workload]["base_cycles"],
                "events_per_million_base_instructions": ratio(source[field], performance[workload]["instructions"], 1_000_000),
                "events_per_base_cycle": ratio(source[field], performance[workload]["base_cycles"]),
                "normalization_formulas": "raw_events / base_instructions * 1,000,000; raw_events / base_cycles",
                "denominator_provenance": "FAST64_FINAL/FAST12_summary.tsv Base instructions and cycles",
                "exclusivity": "NONEXCLUSIVE_DO_NOT_STACK_OR_SUM_AS_A_PERCENT",
                "evidence_class": "EXISTING_DATA_DERIVED_ANALYSIS",
                "accepted_source": "FAST64_FINAL/structural_pressure.tsv + FAST12_summary.tsv",
            })
    write_tsv(OUT / "paper_base_pressure_raw.tsv", raw_rows, list(raw_rows[0]))
    write_tsv(OUT / "paper_base_pressure_normalized.tsv", norm_rows, list(norm_rows[0]))
    return {"raw": raw_rows, "normalized": norm_rows}


def build_mechanism(summary: list[dict[str, str]]) -> list[dict[str, str]]:
    perf = {row["workload"]: row for row in summary}
    mechanism = {(row["workload"], row["mode"]): row for row in read_delimited(FINAL / "io_oo_mechanism.tsv")}
    rows: list[dict[str, str]] = []
    for workload, details in perf.items():
        io = mechanism[(workload, "IO")]
        oo = mechanism[(workload, "OO")]
        rows.append({
            "workload": workload,
            "io_head_not_ready_cycles": io["head_not_ready"], "io_pib_head_ready_cycles": io["head_ready"],
            "io_hol_ready_younger_count_sum": io["hol_count"], "io_hol_ready_younger_cycles": io["hol_cycles"],
            "io_cycles": details["io_cycles"], "sm_count": str(SM_COUNT),
            "io_hol_sm_cycle_fraction": ratio(io["hol_cycles"], SM_COUNT * int(details["io_cycles"])),
            "io_hol_formula": "io_hol_ready_younger_cycles / (64 * io_cycles)",
            "oo_out_of_order_retires": oo["ooo_retire"], "oo_retire_count": oo["retire"],
            "oo_ooo_retire_fraction": ratio(oo["ooo_retire"], oo["retire"]),
            "oo_ooo_formula": "oo_out_of_order_retires / oo_retire_count",
            "oo_immediate_reclaims": oo["immediate_reclaim"],
            "oo_deferred_reclaims": oo["deferred_reclaim"], "oo_final_ref_reclaims": oo["final_ref_reclaim"],
            "oo_wakeups": oo["wakeups"], "oo_instructions": details["instructions"],
            "oo_immediate_reclaims_per_million_instructions": ratio(oo["immediate_reclaim"], details["instructions"], 1_000_000),
            "oo_deferred_reclaims_per_million_instructions": ratio(oo["deferred_reclaim"], details["instructions"], 1_000_000),
            "oo_final_ref_reclaims_per_million_instructions": ratio(oo["final_ref_reclaim"], details["instructions"], 1_000_000),
            "oo_wakeups_per_million_instructions": ratio(oo["wakeups"], details["instructions"], 1_000_000),
            "reclaim_wakeup_normalization_formula": "raw_count / oo_instructions * 1,000,000",
            "reclaim_wakeup_denominator_provenance": "FAST64_FINAL/FAST12_summary.tsv instructions (identical accepted triplet payload)",
            "formula_provenance": "FAST64.5 metric provenance: raw counter identities; Lane-A stated arithmetic",
            "evidence_class": "EXISTING_DATA_DERIVED_ANALYSIS",
            "accepted_source": "FAST64_FINAL/io_oo_mechanism.tsv + FAST12_summary.tsv",
        })
    write_tsv(OUT / "paper_io_oo_mechanism.tsv", rows, list(rows[0]))
    return rows


def point_sort(value: str) -> float:
    return float(value)


def build_sensitivity(source_name: str, output_name: str, dimension: str, reference: str, deadlocks: list[dict[str, str]] | None = None) -> list[dict[str, str]]:
    source_rows = read_delimited(FINAL / source_name)
    by_key = {(row["workload"], row["mode"], row["point"]): row for row in source_rows}
    rows: list[dict[str, str]] = []
    for source in source_rows:
        reference_row = by_key[(source["workload"], source["mode"], reference)]
        rows.append({
            "workload": source["workload"], "sensitivity_dimension": dimension, "row_kind": "NUMERIC_ACCEPTED_POINT",
            "requested_point": source["point"], "mode": source["mode"], "modeled_capacity_or_entries": source["modeled_value"],
            "same_mode_reference": f"{source['mode']}@{reference}", "same_mode_reference_cycles": reference_row["cycles"],
            "cycles": source["cycles"], "cycles_over_same_mode_reference": ratio(source["cycles"], reference_row["cycles"]),
            "speedup_vs_same_mode_reference": ratio(reference_row["cycles"], source["cycles"]),
            "normalization_formula": "cycles(point, mode) / cycles(reference point, same mode)",
            "accepted_status": source["status"], "boundary_disposition": "NUMERIC",
            "evidence_class": "EXISTING_DATA_DERIVED_ANALYSIS", "accepted_source": f"FAST64_FINAL/{source_name}",
        })
    if deadlocks:
        for marker in deadlocks:
            reference_row = by_key[(marker["workload"], marker["mode"], reference)]
            rows.append({
                "workload": marker["workload"], "sensitivity_dimension": dimension, "row_kind": "NONNUMERIC_BOUNDARY_MARKER",
                "requested_point": marker["point"], "mode": marker["mode"], "modeled_capacity_or_entries": marker["modeled_value"],
                "same_mode_reference": f"{marker['mode']}@{reference}", "same_mode_reference_cycles": reference_row["cycles"],
                "cycles": NAN, "cycles_over_same_mode_reference": NAN, "speedup_vs_same_mode_reference": NAN,
                "normalization_formula": "NOT_APPLICABLE_RESOURCE_DEADLOCK_HAS_NO_NUMERIC_PERFORMANCE",
                "accepted_status": marker["disposition"], "boundary_disposition": marker["disposition"],
                "evidence_class": "ACCEPTED_FAST64_EVIDENCE", "accepted_source": "FAST64_FINAL/fast64_6_expected_deadlocks.tsv",
            })
    rows.sort(key=lambda row: (row["workload"], row["mode"], point_sort(row["requested_point"])))
    write_tsv(OUT / output_name, rows, list(rows[0]))
    return rows


def traffic_by_workload() -> dict[tuple[str, str], dict[str, str]]:
    return {(row["workload"], row["mode"]): row for row in read_delimited(FINAL / "traffic_pressure.tsv")}


INTERPRETATIONS = {
    "ATAX": ("IO regresses (0.993x), while OO is 1.825x over Base.", "The measured IO HOL fraction and OO retire/reclaim counters co-occur with OO recovery; this is not an exclusive causal proof.", "The counters are accumulated exposure measures; no average-live-miss quantity is source-defined."),
    "BICG": ("IO regresses (0.942x), while OO is 1.874x over Base.", "Measured IO HOL and OO retirement/reclaim activity accompany the IO-to-OO recovery.", "Association does not identify which individual dependency or reclamation event caused the recovery."),
    "GESUMMV": ("IO regresses (0.926x), while OO is 1.363x over Base.", "The accepted IO HOL scale is high and OO has a lower cycle count with retained reclaim activity.", "The measurement establishes correlation, not a decomposition of the performance change."),
    "GEMM": ("Both modes benefit: IO 1.788x and OO 1.906x.", "Accepted traffic counters show fewer global reads/L1 misses in measured modes while L2 misses and reservation failures remain zero.", "The traffic contrast is measured; the exact micro-causal route is not proven here."),
    "2DConvolution": ("Both modes materially benefit: IO 3.582x and OO 3.788x.", "High reported Base PIB-full pressure and a measured traffic contrast accompany the performance gain.", "Non-exclusive structural counters must not be read as a 100% stall breakdown."),
    "Btree": ("Both modes benefit: IO 1.515x and OO 2.141x.", "Reported Base PIB/MSHR-entry pressure and retained OO retire/reclaim values accompany the extra OO gain.", "The table does not prove that any one pressure category exclusively causes the gain."),
    "DWT2D": ("Both modes benefit: IO 1.426x and OO 1.467x.", "Measured L2 reservation-fail and traffic contrasts coexist with nonzero Base structural counters.", "Counters are not mutually exclusive and do not establish a unique cause."),
    "Gaussian": ("Both modes show a modest benefit: IO 1.108x and OO 1.107x.", "The accepted measurements show approximately 1.108x benefit and zero L2 misses/reservation failures; it must not be described mechanically as a non-beneficiary.", "The near-equal IO/OO result does not identify why the benefit is modest."),
    "Hotspot1": ("Both modes benefit: IO 1.874x and OO 1.907x.", "Reported Base PIB-full/cacheline-reserved pressure coexists with large gains; the IO-to-OO delta is small.", "No OO-reclaim causal claim follows from the small incremental delta."),
    "LUD": ("Both modes are near neutral: IO 1.021x and OO 1.024x.", "Accepted terminal rows retain a low-benefit observation despite reported structural fields.", "Low benefit is measured, not evidence of an implementation failure or a singular mechanism."),
    "NN": ("Both modes show modest benefit: IO 1.146x and OO 1.144x.", "The accepted Base structural table reports comparatively low named pressure fields alongside modest gain.", "This descriptive comparison is not a platform-limit claim."),
    "MRI-Q": ("Both modes are near neutral: IO 1.017x and OO 1.015x.", "The accepted structural rows have zero MSHR-entry and downstream-full events while gains remain small.", "Absence in these counters does not prove a cause of the low benefit."),
}


def build_explanations(primary: list[dict[str, str]], pressure: dict[str, list[dict[str, str]]], mechanism: list[dict[str, str]]) -> list[dict[str, str]]:
    primary_by_workload = {row["workload"]: row for row in primary if row["aggregate"] == "NO"}
    mechanism_by_workload = {row["workload"]: row for row in mechanism}
    pressure_by_workload: dict[str, list[dict[str, str]]] = {}
    for row in pressure["normalized"]:
        pressure_by_workload.setdefault(row["workload"], []).append(row)
    traffic = traffic_by_workload()
    causal = {row["workload"]: row for row in read_delimited(FINAL / "causal_classification.tsv")}
    rows: list[dict[str, str]] = []
    for workload, perf in primary_by_workload.items():
        raw_signature = "; ".join(f"{item['pressure_category']}={item['raw_events']}" for item in pressure_by_workload[workload] if item["raw_events"] != "0") or "all six reported counters are zero"
        io = mechanism_by_workload[workload]
        base_traffic, io_traffic, oo_traffic = (traffic[(workload, mode)] for mode in ("BASE", "IO", "OO"))
        behavior, interpretation, caveat = INTERPRETATIONS[workload]
        rows.append({
            "workload": workload, "performance_behavior": behavior,
            "io_speedup_over_base": perf["io_speedup_over_base"], "oo_speedup_over_base": perf["oo_speedup_over_base"],
            "base_pressure_signature_raw": raw_signature,
            "base_pressure_evidence_class": "ACCEPTED_FAST64_EVIDENCE_NONEXCLUSIVE_COUNTERS",
            "io_hol_evidence": f"HOL fraction={io['io_hol_sm_cycle_fraction']}; numerator={io['io_hol_ready_younger_cycles']}; denominator=64*{io['io_cycles']}",
            "oo_retire_reclaim_evidence": f"OOO-retire fraction={io['oo_ooo_retire_fraction']}; immediate/deferred/final-ref={io['oo_immediate_reclaims']}/{io['oo_deferred_reclaims']}/{io['oo_final_ref_reclaims']}; wakeups={io['oo_wakeups']}",
            "traffic_contrast": f"global reads Base/IO/OO={base_traffic['global_reads']}/{io_traffic['global_reads']}/{oo_traffic['global_reads']}; L2 misses={base_traffic['l2_misses']}/{io_traffic['l2_misses']}/{oo_traffic['l2_misses']}; L2 reservation fails={base_traffic['l2_reservation_fails']}/{io_traffic['l2_reservation_fails']}/{oo_traffic['l2_reservation_fails']}",
            "source_proven_scope": "No source-proven performance-causal claim is made in Lane A; source-level mechanism claims require a source audit.",
            "measured_correlation": interpretation,
            "strongest_supported_interpretation": interpretation,
            "caveat_or_alternative": caveat,
            "accepted_causal_label": causal[workload]["primary_class"],
            "claim_evidence_class": "MEASURED_CORRELATION",
            "source_proven_causal_evidence_class": "INSUFFICIENT_FOR_SOURCE_PROVEN_CAUSAL_CLAIM",
            "accepted_sources": "FAST64_FINAL/{FAST12_summary,structural_pressure,io_oo_mechanism,traffic_pressure,causal_classification}.tsv",
        })
    write_tsv(OUT / "paper_workload_explanations.tsv", rows, list(rows[0]))
    return rows


def svg_primary(primary: list[dict[str, str]]) -> None:
    rows = [row for row in primary if row["aggregate"] == "NO"]
    width, height, left, bottom = 1150, 515, 66, 96
    max_value = max(1.0, *(float(row["io_normalized_cycles"]) for row in rows), *(float(row["oo_normalized_cycles"]) for row in rows)) * 1.08
    plot_h = height - bottom - 72
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<style>text{font-family:Arial,sans-serif;fill:#172033}.small{font-size:11px}.axis{stroke:#667085}.grid{stroke:#d0d5dd}.base{fill:#98a2b3}.io{fill:#f79009}.oo{fill:#2e90fa}</style>',
             '<text x="66" y="28" font-size="19" font-weight="700">FAST12 normalized cycle count (Base = 1.0)</text>',
             '<text x="66" y="48" class="small">Lower is better. ATAX, BICG, and GESUMMV IO regressions are retained.</text>']
    for tick in range(5):
        value = max_value * tick / 4
        y = height - bottom - plot_h * tick / 4
        parts.append(f'<line class="grid" x1="{left}" x2="{width - 24}" y1="{y:.1f}" y2="{y:.1f}"/><text class="small" x="10" y="{y + 4:.1f}">{value:.2f}</text>')
    group = (width - left - 24) / len(rows)
    for index, row in enumerate(rows):
        x = left + index * group + 5
        for offset, (value, style) in enumerate(((1.0, "base"), (float(row["io_normalized_cycles"]), "io"), (float(row["oo_normalized_cycles"]), "oo"))):
            bar_h = value / max_value * plot_h
            parts.append(f'<rect class="{style}" x="{x + offset * 8:.1f}" y="{height - bottom - bar_h:.1f}" width="7" height="{bar_h:.1f}"/>')
        parts.append(f'<text class="small" transform="translate({x + 22:.1f},{height - bottom + 11}) rotate(55)">{html.escape(row["workload"])}</text>')
    parts += [f'<line class="axis" x1="{left}" x2="{width - 24}" y1="{height - bottom}" y2="{height - bottom}"/>',
              '<rect class="base" x="795" y="31" width="12" height="12"/><text class="small" x="812" y="41">Base</text>',
              '<rect class="io" x="864" y="31" width="12" height="12"/><text class="small" x="881" y="41">IO</text>',
              '<rect class="oo" x="920" y="31" width="12" height="12"/><text class="small" x="937" y="41">OO</text>', '</svg>']
    (OUT / "paper_primary_performance.svg").write_text("\n".join(parts))


def svg_mechanism(rows: list[dict[str, str]]) -> None:
    width, height, left, bottom = 1150, 515, 66, 96
    plot_h = height - bottom - 72
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<style>text{font-family:Arial,sans-serif;fill:#172033}.small{font-size:11px}.axis{stroke:#667085}.grid{stroke:#d0d5dd}.io{fill:#f79009}.oo{fill:#2e90fa}</style>',
             '<text x="66" y="28" font-size="19" font-weight="700">IO HOL and OO out-of-order retirement fractions</text>',
             '<text x="66" y="48" class="small">IO: HOL-ready-younger cycles / (64 × IO cycles). OO: OOO retires / retire count.</text>']
    for tick in range(5):
        value = tick / 4
        y = height - bottom - value * plot_h
        parts.append(f'<line class="grid" x1="{left}" x2="{width - 24}" y1="{y:.1f}" y2="{y:.1f}"/><text class="small" x="20" y="{y + 4:.1f}">{value:.2f}</text>')
    group = (width - left - 24) / len(rows)
    for index, row in enumerate(rows):
        x = left + index * group + group / 2
        for offset, (field, css) in enumerate((("io_hol_sm_cycle_fraction", "io"), ("oo_ooo_retire_fraction", "oo"))):
            y = height - bottom - float(row[field]) * plot_h
            parts.append(f'<circle class="{css}" cx="{x + (offset - .5) * 9:.1f}" cy="{y:.1f}" r="4"/>')
        parts.append(f'<text class="small" transform="translate({x:.1f},{height - bottom + 11}) rotate(55)">{html.escape(row["workload"])}</text>')
    parts += [f'<line class="axis" x1="{left}" x2="{width - 24}" y1="{height - bottom}" y2="{height - bottom}"/>',
              '<circle class="io" cx="805" cy="37" r="4"/><text class="small" x="815" y="41">IO HOL fraction</text>',
              '<circle class="oo" cx="950" cy="37" r="4"/><text class="small" x="960" y="41">OO OOO-retire fraction</text>', '</svg>']
    (OUT / "paper_io_oo_mechanism.svg").write_text("\n".join(parts))


def svg_physical(rows: list[dict[str, str]]) -> None:
    numeric = [row for row in rows if row["row_kind"] == "NUMERIC_ACCEPTED_POINT"]
    workloads = ["BICG", "GESUMMV", "Btree"]
    points = ["16.5", "24", "32", "40", "48"]
    width, height, left, bottom = 1150, 515, 70, 78
    panel_width, plot_h, y_max = (width - left - 25) / len(workloads), height - bottom - 92, 2.3
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<style>text{font-family:Arial,sans-serif;fill:#172033}.small{font-size:11px}.axis{stroke:#667085}.grid{stroke:#d0d5dd}.io{stroke:#f79009;fill:none;stroke-width:2}.oo{stroke:#2e90fa;fill:none;stroke-width:2}.io-dot{fill:#f79009}.oo-dot{fill:#2e90fa}</style>',
             '<text x="70" y="27" font-size="19" font-weight="700">Physical-pool same-mode normalized cycles</text>',
             '<text x="70" y="47" class="small">Each mode is normalized to its own 32-KiB point. BICG/GESUMMV 16.5-KiB deadlocks are boundary markers, not numeric points.</text>']
    for panel, workload in enumerate(workloads):
        x0 = left + panel * panel_width
        parts.append(f'<text x="{x0 + 4:.1f}" y="76" font-size="14" font-weight="700">{workload}</text>')
        for tick in (0, .5, 1, 1.5, 2):
            y = height - bottom - tick / y_max * plot_h
            parts.append(f'<line class="grid" x1="{x0:.1f}" x2="{x0 + panel_width - 12:.1f}" y1="{y:.1f}" y2="{y:.1f}"/>')
            if panel == 0:
                parts.append(f'<text class="small" x="{x0 - 27:.1f}" y="{y + 4:.1f}">{tick:.1f}</text>')
        for mode, css in (("IO", "io"), ("OO", "oo")):
            series = [row for row in numeric if row["workload"] == workload and row["mode"] == mode]
            coords: list[tuple[float, float]] = []
            for row in series:
                x = x0 + 18 + points.index(row["requested_point"]) * ((panel_width - 48) / 4)
                y = height - bottom - float(row["cycles_over_same_mode_reference"]) / y_max * plot_h
                coords.append((x, y))
                parts.append(f'<circle class="{css}-dot" cx="{x:.1f}" cy="{y:.1f}" r="3.5"/>')
            if coords:
                joined = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
                parts.append(f'<polyline class="{css}" points="{joined}"/>')
        for index, point in enumerate(points):
            x = x0 + 18 + index * ((panel_width - 48) / 4)
            parts.append(f'<text class="small" x="{x - 8:.1f}" y="{height - bottom + 17}">{point}</text>')
    parts += ['<circle class="io-dot" cx="920" cy="38" r="4"/><text class="small" x="930" y="42">IO</text>',
              '<circle class="oo-dot" cx="978" cy="38" r="4"/><text class="small" x="988" y="42">OO</text>', '</svg>']
    (OUT / "paper_sens_physical.svg").write_text("\n".join(parts))


def write_analysis() -> None:
    ANALYSIS.write_text("""# POST-FAST64 paper-grade result analysis

Status: `A_PAPER_RESULTS_READY` — `EXISTING_DATA_DERIVED_ANALYSIS` from
immutable `ACCEPTED_FAST64_EVIDENCE` only. The frozen accepted authority is
`hrl/decoupled-l1-fast64-v0@18a68dcccd795f1b6cda75504e9450d00c9cee02`
(`FAST64_COMPLETE_READY_FOR_REVIEW`). This Lane-A package does not modify or
reinterpret any accepted FAST64 result and contains no post-FAST64 simulator run.

## A0 — accepted-input freeze

`generated/A_ACCEPTED_INPUT_MANIFEST.tsv` records the frozen authority, exact
FAST12 membership, and every consumed Stage4/5/6 SHA-256. The generator refuses
to emit output unless those bound hashes match the FAST64.7 input manifest and
the primary cycles reconcile independently to both accepted Stage4 triplets and
Stage5 summary rows.

## A1 — primary performance

`generated/paper_primary_performance.tsv` is the paper-primary Base-normalized
table; Base is exactly 1.0 per workload. The exact accepted GM-FAST12 is IO
**1.326143376x** and OO **1.592062402x**. IO regressions are intentionally
retained: ATAX 0.993064680x, BICG 0.942016955x, and GESUMMV 0.925562007x.
`generated/paper_primary_performance.svg` is a reproducible figure generated
from that table. No leave-one-out statistic is used in primary reporting.

## A2 — Base structural pressure

The raw and denominator-qualified views are respectively
`generated/paper_base_pressure_raw.tsv` and
`generated/paper_base_pressure_normalized.tsv`. They separately preserve PIB
full, true cacheline/all-lines-reserved, Tag-bank conflict, MSHR entry full,
MSHR merge full, and missqueue/downstream full. These are non-exclusive
accumulated counters and are explicitly **not** a stackable 100% distribution.

## A3 — IO to OO mechanism evidence

`generated/paper_io_oo_mechanism.tsv` preserves the raw IO HOL and OO
retirement/reclaim/wakeup counters. Its two specified derived fields are:

```
IO_HOL_SM_CYCLE_FRACTION = io_hol_ready_younger_cycles / (64 * io_cycles)
OO_OOO_RETIRE_FRACTION  = oo_out_of_order_retires / oo_retire_count
```

The arithmetic and metric provenance are recorded per row; neither fraction is
presented as exclusive causal proof. `generated/paper_io_oo_mechanism.svg` is
the plot-ready visualization. ATAX, BICG, and GESUMMV preserve the IO-regression
to OO-recovery contrast, while rows with similar IO/OO behavior remain included.

## A4 — sensitivity presentation

`paper_sens_logical.tsv` uses IO@16 and OO@16 separately; `paper_sens_physical.tsv`
uses IO@32 and OO@32 separately; and `paper_sens_pib.tsv` uses IO@128 and OO@128
separately. The physical table preserves both requested points and modeled
capacities. Its four accepted BICG/GESUMMV 16.5-KiB resource deadlocks are
`NONNUMERIC_BOUNDARY_MARKER` rows with no fabricated performance value; the
accepted numerical Btree 16.5-KiB rows remain numerical. The physical SVG is
generated from numeric points only and its subtitle records that boundary.

## A5 — paper-facing workload interpretation

`generated/paper_workload_explanations.tsv` covers all 12 workloads with
performance, Base pressure, IO HOL, OO retire/reclaim, and traffic evidence.
It explicitly records that Lane A has no `SOURCE_PROVEN` performance-causal
claim and classifies its interpretations as `MEASURED_CORRELATION`; no counter
is promoted to a causal proof.
Gaussian is correctly described as a **modest approximately 1.108x benefit** in
both accepted modes, not as a mechanical non-beneficiary.

## Reproduction

From this Framework worktree run:

```bash
python3 tools/generate_post_fast64_paper_analysis.py
```

The script uses Python's standard library, consumes only committed compact
accepted evidence, writes only `docs/dtc_l1/post_fast64/`, and performs its
hash/membership/Stage4–5 reconciliation checks before generation.
""")


def regression_check(summary: list[dict[str, str]], primary: list[dict[str, str]], mechanism: list[dict[str, str]], physical: list[dict[str, str]]) -> None:
    if len(read_delimited(OUT / "paper_primary_performance.tsv")) != 13:
        raise ValueError("primary output lacks 12 workloads plus exact GM")
    gm = next(row for row in primary if row["workload"] == "GM-FAST12")
    if gm["io_speedup_over_base"] != "1.326143376" or gm["oo_speedup_over_base"] != "1.592062402":
        raise ValueError("generated GM does not reproduce accepted FAST12")
    regressions = {row["workload"] for row in primary if row["aggregate"] == "NO" and float(row["io_speedup_over_base"]) < 1}
    if regressions != {"ATAX", "BICG", "GESUMMV"}:
        raise ValueError("primary output lost or changed accepted IO regressions")
    if len(read_delimited(OUT / "paper_base_pressure_raw.tsv")) != 72 or len(read_delimited(OUT / "paper_base_pressure_normalized.tsv")) != 72:
        raise ValueError("Base pressure output is not 12 workloads x 6 distinct counters")
    if len(mechanism) != 12 or any("UNSUPPORTED" in row["io_hol_sm_cycle_fraction"] or "UNSUPPORTED" in row["oo_ooo_retire_fraction"] for row in mechanism):
        raise ValueError("mechanism fractions are incomplete")
    marker_rows = [row for row in physical if row["row_kind"] == "NONNUMERIC_BOUNDARY_MARKER"]
    if len(marker_rows) != 4 or any(row["cycles"] != NAN for row in marker_rows):
        raise ValueError("physical deadlock boundaries were not preserved as nonnumeric")
    gaussian = next(row for row in read_delimited(OUT / "paper_workload_explanations.tsv") if row["workload"] == "Gaussian")
    if "modest benefit" not in gaussian["performance_behavior"]:
        raise ValueError("Gaussian wording regressed to a non-beneficiary claim")


def main() -> None:
    summary, gm = validate_inputs()
    build_input_manifest(summary)
    primary = build_primary(summary, gm)
    pressure = build_pressure(summary)
    mechanism = build_mechanism(summary)
    deadlocks = read_delimited(FINAL / "fast64_6_expected_deadlocks.tsv")
    build_sensitivity("fast64_6_logical_plot.tsv", "paper_sens_logical.tsv", "logical_capacity_kib", "16")
    physical = build_sensitivity("fast64_6_physical_plot.tsv", "paper_sens_physical.tsv", "physical_pool_kib", "32", deadlocks)
    build_sensitivity("fast64_6_pib_plot.tsv", "paper_sens_pib.tsv", "pib_entries", "128")
    build_explanations(primary, pressure, mechanism)
    svg_primary(primary)
    svg_mechanism(mechanism)
    svg_physical(physical)
    write_analysis()
    regression_check(summary, primary, mechanism, physical)


if __name__ == "__main__":
    main()
