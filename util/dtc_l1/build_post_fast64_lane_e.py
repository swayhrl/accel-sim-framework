#!/usr/bin/env python3
"""Build the compact, source-bound POST-FAST64 Lane-E review package.

This program deliberately has two separate modes.  ``--import-git`` is only
used to create the committed compact snapshots from the six pinned Git
objects.  The ordinary build/validation modes consume those snapshots only:
they never invoke a simulator, scrape a run directory, or require a GPU.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import math
import shutil
import subprocess
import sys
import zlib
import xml.etree.ElementTree as ET
from collections import defaultdict
from decimal import Decimal, getcontext
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

getcontext().prec = 50

FAST64 = "18a68dcccd795f1b6cda75504e9450d00c9cee02"
A = "c1774a452e244d431c215010b1039e9d3e074f2a"
B = "757b8cbf2c536b04f8a6ef4db847af04f337378d"
C = "18800873478576309b08b538974c3872fc2cb6df"
D_FINAL = "d33d236c0338d7ab4420c6ceceae3d5733e0a3ad"
D_REV = "dfdf09850f133927d98aba51accd8ef082a4b6b0"

# This deliberately small closure contains the source data needed to recreate
# every Lane-E numerical table/claim.  It contains no raw SIM_HOST output.
IMPORTS = {
    "fast64": (FAST64, "ACCEPTED_FAST64_EVIDENCE", "immutable primary performance and sensitivity authority", [
        "docs/dtc_l1/fast64/review_packs/FAST64_FINAL/FAST12_summary.tsv",
        "docs/dtc_l1/fast64/review_packs/FAST64_FINAL/FAST64_7_INPUT_MANIFEST.tsv",
        "docs/dtc_l1/fast64/review_packs/FAST64_FINAL/aggregate_membership.tsv",
        "docs/dtc_l1/fast64/review_packs/FAST64_FINAL/fast64_6_expected_deadlocks.tsv",
        "docs/dtc_l1/fast64/review_packs/FAST64_FINAL/fast64_6_logical_plot.tsv",
        "docs/dtc_l1/fast64/review_packs/FAST64_FINAL/fast64_6_physical_plot.tsv",
        "docs/dtc_l1/fast64/review_packs/FAST64_FINAL/fast64_6_pib_plot.tsv",
        "docs/dtc_l1/fast64/review_packs/FAST64_FINAL/io_oo_mechanism.tsv",
        "docs/dtc_l1/fast64/review_packs/FAST64_FINAL/limitations_boundary.md",
        "docs/dtc_l1/fast64/review_packs/FAST64_FINAL/structural_pressure.tsv",
        "docs/dtc_l1/fast64/review_packs/FAST64_FINAL/traffic_pressure.tsv",
    ]),
    "A": (A, "EXISTING_DATA_DERIVED_ANALYSIS", "paper tables and reviewed FAST64 presentation", [
        "docs/dtc_l1/post_fast64/POST_FAST64_PAPER_RESULT_ANALYSIS.md",
        "docs/dtc_l1/post_fast64/generated/A_ACCEPTED_INPUT_MANIFEST.tsv",
        "docs/dtc_l1/post_fast64/generated/paper_base_pressure_raw.tsv",
        "docs/dtc_l1/post_fast64/generated/paper_base_pressure_normalized.tsv",
        "docs/dtc_l1/post_fast64/generated/paper_io_oo_mechanism.tsv",
        "docs/dtc_l1/post_fast64/generated/paper_primary_performance.tsv",
        "docs/dtc_l1/post_fast64/generated/paper_sens_logical.tsv",
        "docs/dtc_l1/post_fast64/generated/paper_sens_physical.tsv",
        "docs/dtc_l1/post_fast64/generated/paper_sens_pib.tsv",
        "docs/dtc_l1/post_fast64/generated/paper_workload_explanations.tsv",
    ]),
    "B": (B, "EXISTING_DATA_DERIVED_ANALYSIS", "pre-observer physical-pool source audit and accepted sweep analysis", [
        "docs/dtc_l1/post_fast64/PHYSICAL_POOL_CAUSAL_HANDOFF.md",
        "docs/dtc_l1/post_fast64/PHYSICAL_POOL_SOURCE_AUDIT.md",
        "generated/post_fast64/physical_pool_mechanism_normalization_dictionary.tsv",
        "generated/post_fast64/physical_pool_mechanism_normalized.tsv",
        "generated/post_fast64/physical_pool_mechanism_raw.tsv",
    ]),
    "C": (C, "EXISTING_DATA_DERIVED_ANALYSIS", "accepted IO duplicate-request semantics and FAST12 extraction", [
        "docs/dtc_l1/post_fast64/DUPLICATE_MISS_HANDOFF.md",
        "docs/dtc_l1/post_fast64/DUPLICATE_MISS_SOURCE_SEMANTICS.md",
        "generated/post_fast64/duplicate_miss_fast12_io.tsv",
        "generated/post_fast64/duplicate_miss_input_manifest.tsv",
        "generated/post_fast64/duplicate_miss_oo_semantic_gap.tsv",
        "generated/post_fast64/duplicate_miss_stage6_io_correlations.tsv",
        "generated/post_fast64/duplicate_miss_stage6_io_physical.tsv",
    ]),
    "D_final": (D_FINAL, "NEW_DIAGNOSTIC_TELEMETRY", "complete diagnostic experiment history; retained for lineage", [
        "docs/dtc_l1/post_fast64/D4_D5_OBSERVER_PROVENANCE.md",
        "docs/dtc_l1/post_fast64/LANE_D_OBSERVER_FINAL.md",
        "docs/dtc_l1/post_fast64/generated/D4_D5_OBSERVER_RAW_RUN_INDEX.tsv",
        "docs/dtc_l1/post_fast64/generated/D5_OO_DUPLICATE_FAST12.tsv",
    ]),
    "D_revision": (D_REV, "NEW_DIAGNOSTIC_TELEMETRY", "selected reviewed D4/D5/D6/D7 interpretation", [
        "docs/dtc_l1/post_fast64/LANE_D_ANALYSIS_REVISION.md",
        "docs/dtc_l1/post_fast64/LANE_D_OBSERVER_COUNTER_SEMANTICS.md",
        "docs/dtc_l1/post_fast64/LANE_D_OBSERVER_FINAL.md",
        "docs/dtc_l1/post_fast64/generated/D4_OBSERVER_PHYSICAL_TELEMETRY.tsv",
        "docs/dtc_l1/post_fast64/generated/D5_DUPLICATE_TRAFFIC_INFLATION.tsv",
        "docs/dtc_l1/post_fast64/generated/D5_IO_OO_DUPLICATE_COMPARISON.tsv",
        "docs/dtc_l1/post_fast64/generated/D5_OO_DUPLICATE_FAST12.tsv",
        "docs/dtc_l1/post_fast64/generated/D6_INTEGRATED_ARROW_CLASSIFICATION.tsv",
        "docs/dtc_l1/post_fast64/generated/D7_ORDERED_PREEXISTING_STAT_AUDIT.tsv",
    ]),
}

WORKLOAD_ORDER = ["ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree", "DWT2D", "Gaussian", "Hotspot1", "LUD", "MRI-Q", "NN"]
COLORS = ["#355C7D", "#C06C84", "#6C8EAD", "#F8B195", "#5B8E7D", "#8D6E63"]

# The claim IDs below are intentionally explicit: a paper-facing result may
# point to one or more of these IDs, but never to an unnamed implication.
REQUIRED_CLAIM_IDS = (
    "C01_PRIMARY_FAST12_GM", "C02_IO_REGRESSIONS", "C03_GAUSSIAN_MODEST_BENEFIT",
    "C04_PRESSURE_NONEXCLUSIVE", "C05_IO_HOL_SCOPE", "C06_OO_RETIRE_SCOPE",
    "C07_LOGICAL_SENSITIVITY", "C08_PHYSICAL_SENSITIVITY", "C09_PIB_SENSITIVITY",
    "C10_PHYSICAL_16P5_BOUNDARY", "C11_D4_CONTROLLED_CAPACITY", "C12_POOL_FULL_EXPOSURE",
    "C13_NO_FREE_DENOMINATORS", "C14_OCCUPANCY_TO_INFLIGHT", "C15_INFLIGHT_TO_L2",
    "C16_L2_TO_LIFETIME", "C17_LIFETIME_TO_PENDING_TAG", "C18_PENDING_TAG_TO_DUPLICATE",
    "C19_DUPLICATE_TO_PERFORMANCE", "C20_OO_LIFECYCLE", "C21_FINAL_RECLAIM_PERFORMANCE",
    "C22_LARGER_POOL_TRANSFER", "C23_L2_AND_DUPLICATE_INSUFFICIENT",
    "C24_D5_7_3_2", "C25_PAYLOAD_SCOPE", "C26_D4_WORKLOAD_SCOPE",
    "C27_DIAGNOSTIC_NOT_PRIMARY", "C28_REPAIR_ZERO_SIMULATION", "C29_BTREE_ABSOLUTE_SCALE",
)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git(repo: Path, *args: str, text=False):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=text)


def tsv_read(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def tsv_write(path: Path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def copy_text(source: Path, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(source.read_bytes())


def input_path(inputs: Path, lane: str, original: str) -> Path:
    return inputs / lane / original


def import_git(repo: Path, inputs: Path):
    """Create source-bound snapshots; this has no relationship to simulation."""
    rows = []
    for lane, (commit, evidence, role, files) in IMPORTS.items():
        for original in files:
            blob = git(repo, "rev-parse", f"{commit}:{original}", text=True).strip()
            data = git(repo, "show", f"{commit}:{original}")
            dest = input_path(inputs, lane, original)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            rows.append({
                "source_lane": lane, "source_commit": commit, "original_repository_path": original,
                "git_blob_sha": blob, "sha256": sha256(dest), "local_snapshot_path": str(dest.relative_to(inputs.parent)),
                "evidence_class": evidence, "scientific_role": role,
            })
    tsv_write(inputs.parent / "E_INPUT_MANIFEST.tsv", rows)


def d(s):
    return Decimal(str(s))


def num(s):
    if s in ("", "NA", "NONNUMERIC", "UNSUPPORTED", "NA_NOT_APPLICABLE", "NA_NOT_REPORTED_IN_WHOLE_LINE_OO_COMPACT"):
        return None
    return float(s)


def dec_ratio(n, den):
    if int(n) == 0 and int(den) == 0:
        return "NA_ZERO_DENOMINATOR"
    if int(den) == 0:
        return "NA_ZERO_DENOMINATOR"
    return f"{d(n) / d(den):.12f}"


def snapshot(inputs: Path, lane: str, original: str) -> Path:
    p = input_path(inputs, lane, original)
    if not p.exists():
        raise ValueError(f"missing compact snapshot: {p}")
    return p


def validate_inputs(inputs: Path):
    manifest = tsv_read(inputs.parent / "E_INPUT_MANIFEST.tsv")
    expected = sum(len(v[3]) for v in IMPORTS.values())
    assert len(manifest) == expected, (len(manifest), expected)
    seen = set()
    for row in manifest:
        p = inputs.parent / row["local_snapshot_path"]
        assert p.exists() and sha256(p) == row["sha256"], row["local_snapshot_path"]
        assert row["source_lane"] in IMPORTS
        assert row["source_commit"] == IMPORTS[row["source_lane"]][0]
        seen.add((row["source_lane"], row["original_repository_path"]))
    expected_paths={(lane,path) for lane,(_,_,_,paths) in IMPORTS.items() for path in paths}
    assert seen == expected_paths


def build_primary(inputs: Path, tables: Path):
    rows = tsv_read(snapshot(inputs, "fast64", "docs/dtc_l1/fast64/review_packs/FAST64_FINAL/FAST12_summary.tsv"))
    # FAST64 retains its aggregate row in this compact file.  It must not
    # enter the GM computation; use only the exact named 12 members.
    by_workload = {r["workload"]: r for r in rows if r["workload"] != "GM-FAST12"}
    assert set(by_workload) == set(WORKLOAD_ORDER) and len(by_workload) == 12
    rows = [by_workload[w] for w in WORKLOAD_ORDER]
    out = []
    io_product, oo_product = Decimal(1), Decimal(1)
    for r in rows:
        base, io, oo = (int(r[x]) for x in ("base_cycles", "io_cycles", "oo_cycles"))
        io_s, oo_s = d(base) / d(io), d(base) / d(oo)
        io_product *= io_s; oo_product *= oo_s
        out.append({"workload": r["workload"], "aggregate": "NO", "instructions": r["instructions"], "base_cycles": base,
                    "io_cycles": io, "oo_cycles": oo, "speedup_IO_base_over_IO": f"{io_s:.12f}",
                    "speedup_OO_base_over_OO": f"{oo_s:.12f}", "Base_normalized_cycles": "1.000000000000",
                    "IO_normalized_cycles": f"{d(io)/d(base):.12f}", "OO_normalized_cycles": f"{d(oo)/d(base):.12f}",
                    "formula": "speedup_mode = Base_cycles / mode_cycles", "evidence_class": "ACCEPTED_FAST64_EVIDENCE"})
    n = Decimal(len(rows)); gm_io, gm_oo = io_product ** (Decimal(1)/n), oo_product ** (Decimal(1)/n)
    assert abs(gm_io - d("1.326143376")) < d("0.00000001")
    assert abs(gm_oo - d("1.592062402")) < d("0.00000001")
    out.append({"workload":"GM-FAST12", "aggregate":"YES_EXACT_12", "instructions":"NA", "base_cycles":"NA", "io_cycles":"NA", "oo_cycles":"NA",
                "speedup_IO_base_over_IO":f"{gm_io:.12f}", "speedup_OO_base_over_OO":f"{gm_oo:.12f}",
                "Base_normalized_cycles":"NA", "IO_normalized_cycles":"NA", "OO_normalized_cycles":"NA",
                "formula":"geometric mean of 12 unrounded Base_cycles/mode_cycles ratios", "evidence_class":"EXISTING_DATA_DERIVED_ANALYSIS"})
    tsv_write(tables / "E_PRIMARY_PERFORMANCE.tsv", out)
    return out


def build_pressure_and_mechanism(inputs: Path, tables: Path):
    raw = tsv_read(snapshot(inputs, "A", "docs/dtc_l1/post_fast64/generated/paper_base_pressure_raw.tsv"))
    norm = tsv_read(snapshot(inputs, "A", "docs/dtc_l1/post_fast64/generated/paper_base_pressure_normalized.tsv"))
    assert len(raw) == 72 and {r["workload"] for r in raw} == set(WORKLOAD_ORDER)
    assert all(r["exclusivity"] == "NONEXCLUSIVE_DO_NOT_STACK_OR_SUM_AS_A_PERCENT" for r in raw)
    tsv_write(tables / "E_BASE_PRESSURE.tsv", raw)
    tsv_write(tables / "E_BASE_PRESSURE_NORMALIZED.tsv", norm)
    mech = tsv_read(snapshot(inputs, "A", "docs/dtc_l1/post_fast64/generated/paper_io_oo_mechanism.tsv"))
    assert len(mech) == 12 and all(r["io_hol_formula"] == "io_hol_ready_younger_cycles / (64 * io_cycles)" for r in mech)
    assert all(r["oo_ooo_formula"] == "oo_out_of_order_retires / oo_retire_count" for r in mech)
    tsv_write(tables / "E_IO_OO_MECHANISM.tsv", mech)
    return raw, norm, mech


def build_sensitivities(inputs: Path, tables: Path):
    files = {"logical":"paper_sens_logical.tsv", "physical":"paper_sens_physical.tsv", "pib":"paper_sens_pib.tsv"}
    collected = {}
    for short, name in files.items():
        rows = tsv_read(snapshot(inputs, "A", "docs/dtc_l1/post_fast64/generated/" + name))
        assert rows
        if short == "physical":
            dead = [r for r in rows if r["row_kind"] == "NONNUMERIC_BOUNDARY_MARKER"]
            assert len(dead) == 4 and all(r["cycles"] == "NONNUMERIC" for r in dead)
            btree = [r for r in rows if r["workload"] == "Btree" and r["requested_point"] == "16.5"]
            assert len(btree) == 2 and all(r["row_kind"] == "NUMERIC_ACCEPTED_POINT" for r in btree)
        tsv_write(tables / f"E_SENS_{short.upper()}.tsv", rows)
        collected[short] = rows
    return collected


def build_observer(inputs: Path, tables: Path):
    rows = tsv_read(snapshot(inputs, "D_revision", "docs/dtc_l1/post_fast64/generated/D4_OBSERVER_PHYSICAL_TELEMETRY.tsv"))
    assert len(rows) == 18
    assert {(r["workload"], r["physical_pool_kib"], r["mode"]) for r in rows} == {(w, str(p), m) for w in ("BICG", "GESUMMV", "Btree") for p in (24,32,48) for m in ("IO","OO")}
    assert all(r["classification"] == "POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT" for r in rows)
    tsv_write(tables / "E_PHYSICAL_OBSERVER_SYNTHESIS.tsv", rows)
    pfields = ["workload","mode","physical_pool_kib","cycles","instructions","observer_sample_sm_cycles","physical_full_sample_fraction","average_physical_allocated_lines_per_sample","average_physical_occupancy_fraction_of_capacity","average_inflight_requests_per_sample","alloc_to_ready_average_cycles","alloc_to_ready_max_cycles","l2_misses_per_lower","l2_reservation_fails_per_lower","no_free_physical_events_per_instruction","no_free_events_per_active_sm_cycle"]
    tsv_write(tables / "E_PRESSURE_DENOMINATOR_COMPARISON.tsv", [{k:r[k] for k in pfields} for r in rows], pfields)
    return rows


def build_duplicates(inputs: Path, tables: Path):
    io = tsv_read(snapshot(inputs, "C", "generated/post_fast64/duplicate_miss_fast12_io.tsv"))
    d5 = tsv_read(snapshot(inputs, "D_revision", "docs/dtc_l1/post_fast64/generated/D5_IO_OO_DUPLICATE_COMPARISON.tsv"))
    assert len(io) == len(d5) == 12
    io_by, d5_by = {r["workload"]:r for r in io}, {r["workload"]:r for r in d5}
    assert set(io_by) == set(d5_by) == set(WORKLOAD_ORDER)
    out, comparison = [], []
    lower=higher=zeros=0
    for workload in WORKLOAD_ORDER:
        ir, dr = io_by[workload], d5_by[workload]
        assert int(ir["io_lower_created"]) == int(dr["io_lower_created"])
        assert int(ir["io_duplicate_after_eviction"]) == int(dr["io_duplicate_after_eviction"])
        vals = []
        for mode, lower_key, dup_key, source, klass, qualification in [
            ("IO", "io_lower_created", "io_duplicate_after_eviction", "Lane_C_accepted_IO", "ACCEPTED_FAST64_EVIDENCE", dr["io_evidence_status"]),
            ("OO", "oo_lower_created", "oo_duplicate_after_eviction", "Lane_D_qualified_observer", "NEW_DIAGNOSTIC_TELEMETRY", dr["oo_evidence_status"]),
        ]:
            lower_created, dup = int(dr[lower_key]), int(dr[dup_key])
            share = dec_ratio(dup, lower_created)
            inflation = "NA_ZERO_NON_DUPLICATE_DENOMINATOR" if lower_created == dup else dec_ratio(dup, lower_created - dup)
            out.append({"workload":workload,"mode":mode,"lower_created":lower_created,"duplicate_after_eviction":dup,
                        "duplicate_share_of_lower":share,"duplicate_traffic_inflation":inflation,"duplicate_payload_bytes":dup*128,
                        "payload_scope":"SOURCE_PROVEN_128B_LOWER_REQUEST_PAYLOAD_ONLY_NOT_DRAM_OR_TOTAL_LINK_TRAFFIC",
                        "evidence_source":source,"qualified_evidence_status":qualification,
                        "source_row_kind":dr["oo_source_row_kind"],"evidence_class":klass,
                        "ratio_formula":"D/L; payload inflation D/(L-D)"})
            vals.append((share, dup))
        io_share, oo_share = (d(x[0]) for x in vals)
        if vals[0][1] == vals[1][1] == 0:
            disposition="BOTH_ZERO"; zeros += 1
        elif oo_share < io_share:
            disposition="OO_LOWER"; lower += 1
        else:
            disposition="OO_HIGHER"; higher += 1
        comparison.append({"workload":workload,"io_duplicate_count":vals[0][1],"oo_duplicate_count":vals[1][1],"io_duplicate_share_of_lower":vals[0][0],"oo_duplicate_share_of_lower":vals[1][0],"io_duplicate_payload_bytes":vals[0][1]*128,"oo_duplicate_payload_bytes":vals[1][1]*128,"OO_vs_IO_share_disposition":disposition,"scope":"descriptive; no performance recovery inferred"})
    assert (lower,higher,zeros)==(7,3,2), (lower,higher,zeros)
    tsv_write(tables / "E_DUPLICATE_IO_OO.tsv", out)
    tsv_write(tables / "E_DUPLICATE_PAYLOAD_RATIOS.tsv", comparison)
    return out, comparison


def write_coverage_and_metric_dictionary(inputs: Path, package: Path, audit_rows):
    """Emit coverage from the real audit values, never embedded observations."""
    coverage_ids = {
        "A01_FAST12_ORDER", "A02_PRIMARY_CELLS_AND_GM", "A03_D4_CARTESIAN_AND_DENOMINATOR",
        "A04_D4_LAUNCH_REUSE", "A05_D5_QUALIFIED_PAIRS", "A06_LOGICAL_MEMBERSHIP",
        "A07_PHYSICAL_MEMBERSHIP_AND_BOUNDARY", "A08_PIB_MEMBERSHIP",
    }
    rows = [{"identity": r["check_id"], "expected": r["expected"], "observed": r["observed"],
             "status": r["status"], "source": r["evidence_path"], "detail": r["detail"]}
            for r in audit_rows if r["check_id"] in coverage_ids]
    tsv_write(package / "E_COVERAGE_AND_IDENTITY.tsv", rows)
    dictionary=[
        ("speedup_mode","Base_cycles/mode_cycles","x","accepted integer cycles","primary performance"),
        ("IO_HOL_SM_CYCLE_FRACTION","io_hol_ready_younger_cycles/(64*io_cycles)","fraction","64 SMs times global IO cycles","not an exclusive stall probability"),
        ("OO_OOO_RETIRE_FRACTION","oo_out_of_order_retires/oo_retire_count","fraction","OO retires","not an exclusive causal fraction"),
        ("physical_full_sample_fraction","physical_full_sm_cycles/observer_sample_sm_cycles","fraction","sampled active SM cycles","not 64*global cycles"),
        ("no_free_per_instruction","no_free_physical_events/instructions","events/instruction","completed instructions","accumulated burden"),
        ("no_free_per_active_SM_cycle","no_free_physical_events/observer_sample_sm_cycles","events/active-SM-cycle","observer sampled active SM cycles","time exposure"),
        ("duplicate_share_of_lower","duplicate/lower_created","descriptive ratio","lower-created requests","not a probability"),
        ("duplicate_traffic_inflation","duplicate/(lower_created-duplicate)","descriptive ratio","nonduplicate lower requests","not recoverable performance"),
        ("duplicate_payload_bytes","duplicate*128","B","source-proven request payload","not DRAM/total-link traffic"),
    ]
    tsv_write(package / "E_METRIC_DICTIONARY.tsv", [dict(zip(["metric","formula","unit","denominator_or_granularity","boundary"],x)) for x in dictionary])


def build_reconciliation(out: Path):
    rows=[
        {"topic":"Lane D interpretation","historical_source":"D_FINAL d33d236c","selected_source":"D_REVISION dfdf0985","resolution":"Use revision for current causal wording; retain d33 as experimental/history authority.","status":"RECONCILED"},
        {"topic":"Gaussian wording","historical_source":"performance table","selected_source":"A + primary recomputation","resolution":"Approximate 1.108x IO and OO benefit is paper-facing modest benefit, not no benefit.","status":"RECONCILED"},
        {"topic":"16.5 KiB physical","historical_source":"FAST64 Stage6","selected_source":"A sensitivity table","resolution":"BICG/GESUMMV are nonnumeric resource boundaries; Btree 16.5-KiB rows remain numeric.","status":"RECONCILED"},
        {"topic":"duplicate payload","historical_source":"Lane C source semantics","selected_source":"C + D5","resolution":"D*128 is lower-request payload only, never DRAM/total-link traffic.","status":"RECONCILED"},
        {"topic":"observer time","historical_source":"D4","selected_source":"D revision","resolution":"observer_sample_sm_cycles is retained; 64*global_cycles is not substituted.","status":"RECONCILED"},
        {"topic":"Lane B historical chain","historical_source":"B","selected_source":"D6 revision","resolution":"controlled capacity sensitivity is retained while internal mediator arrows remain non-isolated.","status":"RECONCILED"},
    ]
    tsv_write(out / "E_INTERPRETATION_RECONCILIATION.tsv", rows)
    claims = [
        ("C01_PRIMARY_FAST12_GM", "IO/OO GM is recomputed only from the exact 12 accepted FAST12 integer-cycle rows.", "ACCEPTED_FAST64_EVIDENCE", "FAST64_FINAL/FAST12_summary.tsv", "all 12 primary workloads", "Do not enter diagnostic observer rows into GM."),
        ("C02_IO_REGRESSIONS", "ATAX, BICG, and GESUMMV retain IO regressions while OO is faster than Base.", "ACCEPTED_FAST64_EVIDENCE", "FAST64_FINAL/FAST12_summary.tsv", "ATAX,BICG,GESUMMV", "Do not hide negative IO rows."),
        ("C03_GAUSSIAN_MODEST_BENEFIT", "Gaussian has an approximately 1.108x modest benefit in paper-facing wording.", "EXISTING_DATA_DERIVED_ANALYSIS", "Lane A paper_primary_performance.tsv", "Gaussian", "Do not call the accepted benefit no benefit."),
        ("C04_PRESSURE_NONEXCLUSIVE", "Base pressure counters are separate nonexclusive accumulated exposure counters.", "ACCEPTED_FAST64_EVIDENCE", "Lane A paper_base_pressure_raw.tsv", "all FAST12 workloads", "Do not stack them into a causal 100% breakdown."),
        ("C05_IO_HOL_SCOPE", "IO HOL exposure is hol_ready_younger_cycles/(64*io_cycles).", "EXISTING_DATA_DERIVED_ANALYSIS", "Lane A paper_io_oo_mechanism.tsv", "all FAST12 IO rows", "Not an exclusive stall probability or causal share."),
        ("C06_OO_RETIRE_SCOPE", "OO out-of-order-retire fraction is ooo_retires/retire_count.", "EXISTING_DATA_DERIVED_ANALYSIS", "Lane A paper_io_oo_mechanism.tsv", "all FAST12 OO rows", "Not exclusive causal attribution."),
        ("C07_LOGICAL_SENSITIVITY", "Logical-capacity curves use accepted same-mode normalized points.", "EXISTING_DATA_DERIVED_ANALYSIS", "Lane A paper_sens_logical.tsv", "BICG,GESUMMV,Btree", "No universal optimum."),
        ("C08_PHYSICAL_SENSITIVITY", "Physical-pool curves retain only accepted numeric points and explicit boundaries.", "EXISTING_DATA_DERIVED_ANALYSIS", "Lane A paper_sens_physical.tsv", "BICG,GESUMMV,Btree", "No universal optimum or invented observer point."),
        ("C09_PIB_SENSITIVITY", "PIB curves use accepted same-mode normalized points.", "EXISTING_DATA_DERIVED_ANALYSIS", "Lane A paper_sens_pib.tsv", "BICG,GESUMMV,Btree", "No area/PPA optimum claim."),
        ("C10_PHYSICAL_16P5_BOUNDARY", "BICG/GESUMMV 16.5-KiB physical cases are nonnumeric boundaries; Btree 16.5-KiB remains numeric.", "ACCEPTED_FAST64_EVIDENCE", "FAST64_FINAL/fast64_6_expected_deadlocks.tsv; Lane A paper_sens_physical.tsv", "physical 16.5 KiB", "Never plot BICG/GESUMMV boundary as numeric performance."),
        ("C11_D4_CONTROLLED_CAPACITY", "D4 deliberately controls 24/32/48-KiB capacity and measures workload-specific end-to-end sensitivity.", "MEASURED_CORRELATION", "D revision D4,D6", "BICG,GESUMMV,Btree only", "It does not identify internal mediators."),
        ("C12_POOL_FULL_EXPOSURE", "At 48 KiB pool-full active-SM-cycle exposure can fall strongly for BICG/GESUMMV.", "MEASURED_CORRELATION", "D revision D4,D6", "BICG,GESUMMV D4", "Distinct from accumulated no-free burden."),
        ("C13_NO_FREE_DENOMINATORS", "No-free/instruction, no-free/active-SM-cycle, and pool-full time are distinct quantities.", "EXISTING_DATA_DERIVED_ANALYSIS", "D revision D4", "IO no-free; D4", "Never substitute 64*global cycles for observer_sample_sm_cycles."),
        ("C14_OCCUPANCY_TO_INFLIGHT", "Occupancy/pool-full and lower inflight co-vary in D4.", "MEASURED_CORRELATION", "D revision D6", "D4 only", "Internal arrow is not isolated causal evidence."),
        ("C15_INFLIGHT_TO_L2", "Inflight and L2 miss/reservation pressure co-vary in D4.", "MEASURED_CORRELATION", "D revision D6", "D4 only", "Not independently intervened on."),
        ("C16_L2_TO_LIFETIME", "L2 pressure and alloc-to-ready lifetime co-vary in D4.", "MEASURED_CORRELATION", "D revision D6", "D4 only", "No L2-dominant causal proof."),
        ("C17_LIFETIME_TO_PENDING_TAG", "Pending lifetime to pending Tag eviction remains insufficiently identified.", "INSUFFICIENT", "D revision D6", "D4 mechanism chain", "Do not fill this gap with pending-hit totals."),
        ("C18_PENDING_TAG_TO_DUPLICATE", "Pending Tag eviction followed by same-line pre-response reallocation increments the duplicate lower-request counter.", "SOURCE_PROVEN", "Lane C DUPLICATE_MISS_SOURCE_SEMANTICS.md", "IO counter semantics", "Does not prove event frequency or performance effect."),
        ("C19_DUPLICATE_TO_PERFORMANCE", "Duplicate lower traffic to performance is not supported as an isolated effect.", "NOT_SUPPORTED", "D revision D6", "D4/D5 interpretation", "No recoverable-performance estimate."),
        ("C20_OO_LIFECYCLE", "OO immediate/deferred/final-ref reclaim lifecycle is source-proven observer semantics.", "SOURCE_PROVEN", "Lane D observer counter semantics", "OO lifecycle", "Does not establish a performance-causal arrow."),
        ("C21_FINAL_RECLAIM_PERFORMANCE", "Final reclaim/concurrency to performance remains bounded rather than causal.", "INSUFFICIENT", "D revision D6", "OO D4", "Do not infer performance from reclaim counts."),
        ("C22_LARGER_POOL_TRANSFER", "A universal larger-pool-to-downstream-pressure-transfer story is not supported.", "NOT_SUPPORTED", "Lane B handoff; D revision", "physical sweeps", "Keep workload/mode-specific nonmonotonicity."),
        ("C23_L2_AND_DUPLICATE_INSUFFICIENT", "L2 dominance and duplicate-secondary-feedback remain insufficient.", "INSUFFICIENT", "D revision D6", "integrated interpretation", "Never promote either to a root cause."),
        ("C24_D5_7_3_2", "Qualified D5 exact duplicate shares yield 7 OO-lower, 3 OO-higher, and 2 both-zero workloads.", "NEW_DIAGNOSTIC_TELEMETRY", "D revision D5_IO_OO_DUPLICATE_COMPARISON.tsv", "12 IO/OO pairs", "OO does not universally remove duplicates."),
        ("C25_PAYLOAD_SCOPE", "duplicate*128 B is lower-request payload only.", "SOURCE_PROVEN", "Lane C duplicate semantics; D5", "duplicate payload", "Never label it DRAM, total-link, total-memory traffic, or recoverable performance."),
        ("C26_D4_WORKLOAD_SCOPE", "D4 capacity findings apply only to BICG, GESUMMV, and Btree.", "NEW_DIAGNOSTIC_TELEMETRY", "D revision D4", "three D4 workloads", "Do not project D4 to the other nine workloads."),
        ("C27_DIAGNOSTIC_NOT_PRIMARY", "Observer evidence is diagnostic and never enters the FAST12 primary GM.", "NEW_DIAGNOSTIC_TELEMETRY", "D4/D5 provenance", "all observer evidence", "Do not relabel as primary FAST64."),
        ("C28_REPAIR_ZERO_SIMULATION", "This bounded Lane-E repair runs no simulation or scientific/Core change.", "SOURCE_PROVEN", "Lane E execution inventory", "repair scope", "No new scientific evidence is created."),
        ("C29_BTREE_ABSOLUTE_SCALE", "Btree can be OO-higher by ratio while both duplicate shares are tiny in absolute scale.", "NEW_DIAGNOSTIC_TELEMETRY", "D5 comparison", "Btree", "Do not interpret the ratio without absolute shares."),
    ]
    fields = ["claim_id", "claim_text", "evidence_class", "source_artifact", "supported_scope", "forbidden_overclaim"]
    tsv_write(out / "E_CLAIM_EVIDENCE_REGISTER.tsv", [dict(zip(fields, row)) for row in claims], fields)


def esc(s): return html.escape(str(s), quote=True)
def svg_text(x,y,s,size=13,anchor="start",weight="normal",fill="#17202A"):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="DejaVu Sans,Arial,sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}">{esc(s)}</text>'
def svg_start(title, w=1400, h=850):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">', '<rect width="100%" height="100%" fill="#ffffff"/>', svg_text(w/2,38,title,23,"middle","bold"), f'<desc>{esc(title)}. Deterministic Lane-E plot; source mapping is in FIGURE_INDEX.md.</desc>']
def svg_end(parts): return "\n".join(parts+["</svg>"])+"\n"


def svg_grouped_bar(title,categories,series,ylabel,footnote="",percent=False):
    w,h=1500,900; x0,y0,x1,y1=130,100,1450,720; parts=svg_start(title,w,h)
    maxv=max(max(v for v in vals if v is not None) for _,vals in series) or 1
    maxv*=1.08
    for i in range(6):
        y=y1-(y1-y0)*i/5; v=maxv*i/5
        parts += [f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="#D5D8DC"/>',svg_text(x0-10,y+4,(f"{v*100:.0f}%" if percent else f"{v:.2f}"),11,"end")]
    n=len(categories); group=(x1-x0)/n; bw=group/(len(series)+1)
    for si,(name,vals) in enumerate(series):
        color=COLORS[si]
        parts.append(f'<rect x="{x0+si*160}" y="748" width="18" height="18" fill="{color}"/>'); parts.append(svg_text(x0+25+si*160,762,name,12))
        for i,v in enumerate(vals):
            if v is None: continue
            bh=(v/maxv)*(y1-y0); x=x0+i*group+(si+.5)*bw; y=y1-bh
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw*.84:.1f}" height="{bh:.1f}" fill="{color}"/>')
    for i,c in enumerate(categories): parts.append(svg_text(x0+(i+.5)*group,y1+24,c,10,"middle"))
    # Keep the y-unit inside the canvas.  SVG text rotation would add a second
    # renderer-specific code path; an in-plot unit label is more legible.
    parts += [svg_text(x0,y0-12,ylabel,13,"start","normal", "#34495E"), svg_text(w/2,820,footnote,12,"middle","normal","#566573")]
    return svg_end(parts)


def svg_lines(title, series, ylabel, footnote="", xlabels=None, w=1500,h=900):
    xlabels=xlabels or [str(i) for i in range(max(len(v) for _,v in series))]
    x0,y0,x1,y1=130,100,w-50,700; parts=svg_start(title,w,h)
    values=[v for _,vals in series for v in vals if v is not None]; mn=min(values); mx=max(values); pad=(mx-mn)*.1 or 1; mn-=pad; mx+=pad
    for i in range(6):
        y=y1-(y1-y0)*i/5; v=mn+(mx-mn)*i/5
        parts += [f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="#D5D8DC"/>', svg_text(x0-10,y+4,f"{v:.3g}",11,"end")]
    n=max(len(v) for _,v in series); step=(x1-x0)/(max(1,n-1))
    for si,(name,vals) in enumerate(series):
        pts=[]
        for i,v in enumerate(vals):
            if v is not None: pts.append((x0+i*step,y1-(v-mn)/(mx-mn)*(y1-y0)))
        if len(pts)>1: parts.append('<polyline points="'+" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)+f'" fill="none" stroke="{COLORS[si%len(COLORS)]}" stroke-width="3"/>')
        for x,y in pts: parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{COLORS[si%len(COLORS)]}"/>')
        parts += [f'<rect x="{x0+si*200}" y="742" width="18" height="18" fill="{COLORS[si%len(COLORS)]}"/>',svg_text(x0+25+si*200,756,name,12)]
    for i,l in enumerate(xlabels): parts.append(svg_text(x0+i*step,y1+25,l,11,"middle"))
    parts += [svg_text(x0,y0-12,ylabel,13,"start"),svg_text(w/2,820,footnote,12,"middle","normal","#566573")]
    return svg_end(parts)


def svg_heatmap(title,rowlabels,collabels,values,footnote="",log_color=False):
    w,h=1500,900; x0,y0=260,110; cw,ch=150,46; parts=svg_start(title,w,h)
    flat=[v for row in values for v in row]; vmax=max(flat) or 1
    for j,l in enumerate(collabels): parts.append(svg_text(x0+(j+.5)*cw,y0-15,l,12,"middle","bold"))
    for i,label in enumerate(rowlabels):
        parts.append(svg_text(x0-12,y0+i*ch+30,label,12,"end"))
        for j,v in enumerate(values[i]):
            q=(math.log10(v+1)/math.log10(vmax+1)) if log_color and vmax else (v/vmax)
            q=min(1,max(0,q)); r=int(242-140*q); g=int(246-80*q); b=int(248-30*q)
            parts.append(f'<rect x="{x0+j*cw}" y="{y0+i*ch}" width="{cw-2}" height="{ch-2}" fill="rgb({r},{g},{b})"/>')
            parts.append(svg_text(x0+(j+.5)*cw,y0+i*ch+29,f"{v:.2g}",11,"middle"))
    parts.append(svg_text(w/2,820,footnote,12,"middle","normal","#566573")); return svg_end(parts)


def svg_matrix(title, rows, footnote=""):
    # columns: arrow, verdict, scope; colors convey evidence classification.
    # D6 currently has sixteen evidence rows.  Give every source row its
    # fixed-height cell plus a bottom note; a 900-pixel canvas would silently
    # crop the last seven rows in PNG/PDF review previews.
    w,h=1600,max(900, 122 + len(rows)*82 + 58); parts=svg_start(title,w,h); x=[50,620,850,1110]; widths=[570,220,260,430]
    headers=["Mechanism link", "Evidence level", "Scope", "Boundary"]
    for i,hdr in enumerate(headers): parts += [f'<rect x="{x[i]}" y="85" width="{widths[i]}" height="36" fill="#34495E"/>',svg_text(x[i]+8,109,hdr,12,"start","bold","white")]
    cmap={"SOURCE_PROVEN":"#B8E0C8","MEASURED_CORRELATION":"#C9DAF0","NOT_SUPPORTED":"#F6D6AD","INSUFFICIENT":"#E7C3D9"}
    y=122
    for r in rows:
        cells=[r["mechanism_arrow"],r["verdict"],r["evidence_scope"],r["interpretation_boundary"]]
        y += 0
        for i,c in enumerate(cells):
            fill=cmap.get(r["verdict"],"#F4F6F7") if i==1 else "#FFFFFF"
            parts.append(f'<rect x="{x[i]}" y="{y}" width="{widths[i]}" height="82" fill="{fill}" stroke="#D5D8DC"/>')
            words=str(c).replace("_"," ").split(); lines=[]; line=""
            limit=44 if i in (0,3) else 22
            for wd in words:
                if len(line)+len(wd)+1>limit: lines.append(line);line=wd
                else: line=(line+" "+wd).strip()
            lines.append(line)
            for k,line in enumerate(lines[:4]): parts.append(svg_text(x[i]+7,y+19+k*16,line,10,"start","bold" if i==1 else "normal"))
        y +=82
    parts.append(svg_text(w/2,h-28,footnote,11,"middle","normal","#566573")); return svg_end(parts)


def svg_observer_panels(rows):
    """Ten compact diagnostic panels for the exact 18-cell D4 sweep."""
    w,h=1800,1160; parts=svg_start("F07. Physical-pool observer diagnosis",w,h)
    groups=[(ww,mm) for ww in ("BICG","GESUMMV","Btree") for mm in ("IO","OO")]
    by={(r['workload'],r['mode'],int(r['physical_pool_kib'])):r for r in rows}
    def field(name,scale=1.0,io_only=False):
        def f(r):
            if io_only and r['mode']!='IO': return None
            v=num(r[name]); return None if v is None else v/scale
        return f
    metrics=[
        ("Cycles (millions)",field("cycles",1e6),"M cycles"),
        ("Allocated physical lines",field("average_physical_allocated_lines_per_sample"),"lines"),
        ("Occupancy / capacity",field("average_physical_occupancy_fraction_of_capacity"),"fraction"),
        ("Pool-full active-SM time",field("physical_full_sample_fraction"),"fraction"),
        ("Inflight lower / active-SM",field("average_inflight_requests_per_sample"),"requests"),
        ("Alloc-to-ready average",field("alloc_to_ready_average_cycles"),"cycles"),
        ("L2 misses / lower",field("l2_misses_per_lower"),"ratio"),
        ("L2 reservation fails / lower",field("l2_reservation_fails_per_lower"),"ratio"),
        ("IO no-free / active-SM",field("no_free_events_per_active_sm_cycle",io_only=True),"events/active-SM-cycle"),
        ("IO no-free / instruction",field("no_free_physical_events_per_instruction",io_only=True),"events/instruction"),
    ]
    for mi,(title,fun,unit) in enumerate(metrics):
        col,row=mi%5,mi//5; px,py=55+col*350,92+row*420; gx,gy,gw,gh=px+47,py+42,275,250
        vals=[fun(r) for r in rows]; vals=[v for v in vals if v is not None]; lo=min(vals); hi=max(vals); pad=(hi-lo)*.08 or max(.05,hi*.08); lo=max(0,lo-pad); hi+=pad
        parts += [svg_text(px,py,title,13,"start","bold"),svg_text(px,py+17,unit,9,"start","normal","#566573")]
        for tick in range(4):
            yy=gy+gh-gh*tick/3; vv=lo+(hi-lo)*tick/3
            parts += [f'<line x1="{gx}" y1="{yy:.1f}" x2="{gx+gw}" y2="{yy:.1f}" stroke="#D5D8DC"/>',svg_text(gx-5,yy+3,f"{vv:.3g}",9,"end")]
        for gi,(ww,mm) in enumerate(groups):
            pts=[]
            for pi,pool in enumerate((24,32,48)):
                val=fun(by[(ww,mm,pool)])
                if val is not None: pts.append((gx+pi*gw/2,gy+gh-(val-lo)/(hi-lo)*gh))
            color=COLORS[gi]
            if len(pts)>1: parts.append('<polyline points="'+" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="2"/>')
            for x,y in pts: parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{color}"/>')
        for pi,pool in enumerate((24,32,48)): parts.append(svg_text(gx+pi*gw/2,gy+gh+17,f"{pool}",9,"middle"))
    for gi,(ww,mm) in enumerate(groups):
        x=65+gi*285; parts += [f'<rect x="{x}" y="1000" width="16" height="16" fill="{COLORS[gi]}"/>',svg_text(x+23,1013,f"{ww} {mm}",12)]
    parts += [svg_text(w/2,1060,"D4 diagnostic evidence: 3 workloads × 24/32/48 KiB × IO/OO. All time integrals use observer_sample_sm_cycles, never 64×global cycles.",11,"middle","normal","#566573"),svg_text(w/2,1082,"Capacity is deliberately controlled; these co-varying internal mediator measures are not individually causal interventions.",11,"middle","normal","#566573")]
    return svg_end(parts)


def write_svg_and_preview(path: Path, svg: str, preview_title: str, notes):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(svg,encoding="utf-8")
    # Rasterize the subset of SVG primitives emitted by this builder.  This
    # makes PNG/PDF actual figure previews with the same bars/lines/labels as
    # the vector SVG without adding a browser, a simulator, or a heavyweight
    # plotting dependency to the reproducibility contract.
    img=rasterize_our_svg(svg)
    png=path.with_suffix(".png"); pdf=path.with_suffix(".pdf")
    img.save(png,format="PNG",optimize=False,compress_level=9)
    write_deterministic_image_pdf(img, pdf)


def _svg_number(value, default=0.0, percentage_base=None):
    if value is None: return default
    if value.endswith("%") and percentage_base is not None: return float(value[:-1]) * percentage_base / 100.0
    return float(value)


def _svg_color(value, default="#000000"):
    value = value or default
    if value == "none": return None
    if value == "white": return "#ffffff"
    if value.startswith("rgb("):
        return tuple(int(x) for x in value[4:-1].split(","))
    return value


def _svg_font(size, bold=False):
    base = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(base, max(1, round(size))) if Path(base).exists() else ImageFont.load_default()


def rasterize_our_svg(svg: str):
    root=ET.fromstring(svg)
    w=round(_svg_number(root.attrib.get("width"),1500)); h=round(_svg_number(root.attrib.get("height"),900))
    image=Image.new("RGB",(w,h),"white"); draw=ImageDraw.Draw(image)
    for elem in root:
        tag=elem.tag.rsplit("}",1)[-1]; a=elem.attrib
        if tag in ("desc",): continue
        if tag == "rect":
            x=_svg_number(a.get("x"),0,w); y=_svg_number(a.get("y"),0,h); ew=_svg_number(a.get("width"),w,w); eh=_svg_number(a.get("height"),h,h)
            draw.rectangle((x,y,x+ew,y+eh),fill=_svg_color(a.get("fill"),"#ffffff"),outline=_svg_color(a.get("stroke")) if a.get("stroke") else None,width=max(1,round(_svg_number(a.get("stroke-width"),1))))
        elif tag == "line":
            draw.line((_svg_number(a.get("x1")),_svg_number(a.get("y1")),_svg_number(a.get("x2")),_svg_number(a.get("y2"))),fill=_svg_color(a.get("stroke"),"#000000"),width=max(1,round(_svg_number(a.get("stroke-width"),1))))
        elif tag == "polyline":
            pts=[]
            for pair in a.get("points","").split():
                x,y=pair.split(","); pts.append((float(x),float(y)))
            if len(pts)>1: draw.line(pts,fill=_svg_color(a.get("stroke"),"#000000"),width=max(1,round(_svg_number(a.get("stroke-width"),1))),joint="curve")
        elif tag == "circle":
            x,y,r=_svg_number(a.get("cx")),_svg_number(a.get("cy")),_svg_number(a.get("r"))
            draw.ellipse((x-r,y-r,x+r,y+r),fill=_svg_color(a.get("fill"),"#000000"),outline=_svg_color(a.get("stroke")) if a.get("stroke") else None)
        elif tag == "text":
            text="".join(elem.itertext())
            size=_svg_number(a.get("font-size"),13); font=_svg_font(size,a.get("font-weight")=="bold")
            x,y=_svg_number(a.get("x")),_svg_number(a.get("y")); anchor=a.get("text-anchor","start")
            bbox=draw.textbbox((0,0),text,font=font); tw=bbox[2]-bbox[0]
            if anchor=="middle": x-=tw/2
            elif anchor=="end": x-=tw
            draw.text((x,y-size*.82),text,font=font,fill=_svg_color(a.get("fill"),"#17202A"))
    return image


def write_deterministic_image_pdf(image: Image.Image, path: Path):
    """Write a small timestamp-free image PDF.

    Pillow's PDF backend injects wall-clock metadata, which would make the
    otherwise identical review package non-deterministic.  The SVG remains the
    vector figure; this stable PDF is its portable reading preview.
    """
    image = image.convert("RGB")
    w, h = image.size
    payload = zlib.compress(image.tobytes(), level=9)
    content = f"q\n{w} 0 0 {h} 0 0 cm\n/Im0 Do\nQ\n".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {w} {h}] /Resources << /XObject << /Im0 5 0 R >> >> /Contents 4 0 R >>".encode(),
        f"<< /Length {len(content)} >>\nstream\n".encode()+content+b"endstream",
        f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length {len(payload)} >>\nstream\n".encode()+payload+b"\nendstream",
    ]
    chunks=[b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]; offsets=[0]
    for i,obj in enumerate(objects,1):
        offsets.append(sum(len(x) for x in chunks)); chunks.append(f"{i} 0 obj\n".encode()+obj+b"\nendobj\n")
    start=sum(len(x) for x in chunks)
    chunks.append(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    chunks.extend(f"{o:010d} 00000 n \n".encode() for o in offsets[1:])
    chunks.append(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n".encode())
    path.write_bytes(b"".join(chunks))


def build_figures(tables: Path, figures: Path):
    primary=tsv_read(tables/"E_PRIMARY_PERFORMANCE.tsv")[:-1]
    workload=[r["workload"] for r in primary]
    docs=[]
    def add(fid,title,caption,sources,svg,notes):
        base=figures/fid
        write_svg_and_preview(base.with_suffix(".svg"),svg,f"{fid} — {title}",notes)
        docs.append({"figure_id":fid,"title":title,"caption":caption,"plot_ready_table":", ".join(sources),"evidence_scope":"see caption/source mapping","assets":f"figures/{fid}.svg; figures/{fid}.pdf; figures/{fid}.png"})
    add("F01","Primary performance: Base, IO, and OO", "Base-normalized primary performance across the exact FAST12 membership. Bars are Base/IO and Base/OO speedups recomputed from accepted integer cycles; the final group is reported in the table, not mixed with workload bars.", ["tables/E_PRIMARY_PERFORMANCE.tsv"], svg_grouped_bar("F01. Primary performance",workload,[("Base",[1]*12),("IO",[float(r['speedup_IO_base_over_IO']) for r in primary]),("OO",[float(r['speedup_OO_base_over_OO']) for r in primary])],"Speedup vs Base","Exact FAST12; IO regressions ATAX/BICG/GESUMMV intentionally retained."),["Exact FAST12 primary cells; no observer data in GM.","IO GM = 1.326143376x; OO GM = 1.592062402x.","ATAX, BICG, GESUMMV retain IO regression."])
    pressure=tsv_read(tables/"E_BASE_PRESSURE_NORMALIZED.tsv")
    categories=[("PIB full","PIB full"),("true cacheline/all-lines-reserved","Cacheline reservation"),("Tag-bank conflict","Tag-bank"),("MSHR entry full","MSHR entry"),("MSHR merge full","MSHR merge"),("missqueue/downstream full","Downstream")]
    vals=[]
    for w in workload:
        by={r['pressure_category']:float(r['events_per_million_base_instructions']) for r in pressure if r['workload']==w}
        vals.append([by.get(source,0) for source,_ in categories])
    add("F02","Base structural pressure", "Base-mode accumulated event counters normalized per million instructions. Categories are separate, nonexclusive counters and must not be added into a causal 100% breakdown.", ["tables/E_BASE_PRESSURE.tsv","tables/E_BASE_PRESSURE_NORMALIZED.tsv"],svg_heatmap("F02. Base structural pressure (events per million instructions)",workload,[label for _,label in categories],vals,"Color uses log10(events per 1M Base instructions + 1); labels retain source-unit values.",True),["Six source-defined pressure categories shown separately.","Values are events per million Base instructions (color log-scaled for readability).","Not a stacked or exhaustive causal distribution."])
    mech=tsv_read(tables/"E_IO_OO_MECHANISM.tsv")
    add("F03","IO to OO mechanism evidence", "Paired descriptive mechanism measures: IO HOL ready-younger active-SM-cycle exposure and OO out-of-order retirement fraction. They do not provide exclusive causal attribution.", ["tables/E_IO_OO_MECHANISM.tsv","tables/E_PRIMARY_PERFORMANCE.tsv"],svg_grouped_bar("F03. IO-to-OO mechanism evidence",workload,[("IO HOL exposure",[float(r['io_hol_sm_cycle_fraction']) for r in mech]),("OO OOO retire",[float(r['oo_ooo_retire_fraction']) for r in mech])],"Fraction","Distinct numerator/denominator semantics; retained as mechanism evidence, not causal partition."),["IO HOL = hol_ready_younger_cycles / (64 × IO cycles).","OO fraction = OOO retires / OO retire count.","Measures are descriptive and nonexclusive."])
    for fid,short,title in [("F04","LOGICAL","Logical tag capacity sensitivity"),("F05","PHYSICAL","Physical pool performance sensitivity"),("F06","PIB","PIB sensitivity")]:
        r=tsv_read(tables/f"E_SENS_{short}.tsv")
        nums=[x for x in r if x['row_kind']=='NUMERIC_ACCEPTED_POINT']
        points=sorted({float(x['requested_point']) for x in nums})
        series=[]
        for w in ("BICG","GESUMMV","Btree"):
            for m in ("IO","OO"):
                a={float(x['requested_point']):float(x['speedup_vs_same_mode_reference']) for x in nums if x['workload']==w and x['mode']==m}
                series.append((f"{w} {m}",[a.get(p) for p in points]))
        note="Same-mode normalized speedup; accepted numeric points only."
        if fid=="F05": note="16.5-KiB BICG/GESUMMV markers are nonnumeric resource boundaries; Btree 16.5 stays numeric."
        add(fid,title, f"Accepted Stage6 {title.lower()} with same-mode normalization. {note} No universal optimum is inferred.",[f"tables/E_SENS_{short}.tsv"],svg_lines(f"{fid}. {title}",series,"Speedup vs same-mode reference",note,[str(p).rstrip('0').rstrip('.') for p in points]),["Accepted Stage6 points only.",note,"Curves are workload- and mode-specific, not universal optimum claims."])
    d4=tsv_read(tables/"E_PHYSICAL_OBSERVER_SYNTHESIS.tsv")
    add("F07","Physical-pool observer diagnosis", "Ten-panel diagnostic observer sweep at 24/32/48 KiB: cycles, allocated lines, occupancy fraction, pool-full active-SM-cycle fraction, inflight requests, alloc-to-ready average, L2 rates, and both IO no-free denominators. Capacity is controlled; internal mediators remain non-isolated.", ["tables/E_PHYSICAL_OBSERVER_SYNTHESIS.tsv","tables/E_PRESSURE_DENOMINATOR_COMPARISON.tsv"],svg_observer_panels(d4),["D4: 18 cells, 3 workloads × 3 capacities × 2 modes.","Ten panels retain occupancy, full-time, inflight, lifetime, L2, cycle, and both no-free scopes.","All time integrals use observer sampled active-SM cycles; internal mediator arrows are not isolated."])
    dup=tsv_read(tables/"E_DUPLICATE_IO_OO.tsv")
    by=defaultdict(dict)
    for r in dup: by[r['workload']][r['mode']]=float(r['duplicate_share_of_lower'])
    add("F08","IO/OO duplicate requests and payload ratio", "Exact duplicate-share comparison for 12 workload pairs. IO comes from accepted Lane-C evidence; OO comes from qualified Lane-D observer telemetry. D×128 B is lower-request payload only, not DRAM or total-link traffic.", ["tables/E_DUPLICATE_IO_OO.tsv","tables/E_DUPLICATE_PAYLOAD_RATIOS.tsv"],svg_grouped_bar("F08. Duplicate share of lower requests",workload,[("IO",[by[w]['IO'] for w in workload]),("OO",[by[w]['OO'] for w in workload])],"Duplicate share", "7 OO lower / 3 OO higher / 2 both zero; descriptive ratios only.",True),["Exact 12 IO/OO pairs; no proxy substituted for OO duplicates.","D/L share; D/(L−D) payload inflation in linked table.","Payload means lower-request payload only, not DRAM or performance recovery."])
    arrows=tsv_read(snapshot_dummy := tables.parent.parent/"lane_e/inputs/D_revision/docs/dtc_l1/post_fast64/generated/D6_INTEGRATED_ARROW_CLASSIFICATION.tsv") if False else []
    # Tables' grandparent varies in build dirs; caller writes a materialized D6 copy below.
    arrows=tsv_read(tables/"E_D6_ARROW_CLASSIFICATION.tsv")
    add("F09","Integrated evidence and boundary matrix", "Evidence levels for the physical-pool mechanism chain. A controlled capacity intervention establishes workload-specific sensitivity, while the internal arrows remain non-isolated unless source-proven or explicitly bounded.", ["tables/E_D6_ARROW_CLASSIFICATION.tsv","E_CLAIM_EVIDENCE_REGISTER.tsv"],svg_matrix("F09. Integrated evidence and boundary matrix",arrows,"Do not infer a single root cause. Source-proven, measured, insufficient, and not-supported results are distinct."),["Evidence levels are source-proven, measured correlation, insufficient, or not supported.","Capacity is controlled; internal mediator arrows remain non-isolated.","L2 dominance and duplicate-secondary-feedback remain insufficient."])
    assert [row["figure_id"] for row in docs] == [f"F{i:02d}" for i in range(1,10)]
    figure_claims = {
        "F01":"C01_PRIMARY_FAST12_GM,C02_IO_REGRESSIONS,C03_GAUSSIAN_MODEST_BENEFIT,C27_DIAGNOSTIC_NOT_PRIMARY",
        "F02":"C04_PRESSURE_NONEXCLUSIVE", "F03":"C05_IO_HOL_SCOPE,C06_OO_RETIRE_SCOPE",
        "F04":"C07_LOGICAL_SENSITIVITY", "F05":"C08_PHYSICAL_SENSITIVITY,C10_PHYSICAL_16P5_BOUNDARY",
        "F06":"C09_PIB_SENSITIVITY", "F07":"C11_D4_CONTROLLED_CAPACITY,C12_POOL_FULL_EXPOSURE,C13_NO_FREE_DENOMINATORS,C26_D4_WORKLOAD_SCOPE",
        "F08":"C24_D5_7_3_2,C25_PAYLOAD_SCOPE,C29_BTREE_ABSOLUTE_SCALE",
        "F09":"C14_OCCUPANCY_TO_INFLIGHT,C15_INFLIGHT_TO_L2,C16_L2_TO_LIFETIME,C17_LIFETIME_TO_PENDING_TAG,C18_PENDING_TAG_TO_DUPLICATE,C19_DUPLICATE_TO_PERFORMANCE,C22_LARGER_POOL_TRANSFER,C23_L2_AND_DUPLICATE_INSUFFICIENT",
    }
    for row in docs:
        row["claim_ids"] = figure_claims[row["figure_id"]]
    tsv_write(figures.parent/"FIGURE_INDEX.tsv",docs)
    md=["# Figure index and captions", "", "All captions are English. Every plot is rebuilt from the compact Lane-E snapshots; observer evidence is diagnostic and is never part of the FAST12 GM.", ""]
    for r in docs: md += [f"## {r['figure_id']} — {r['title']}","",r['caption'],"",f"Source mapping: `{r['plot_ready_table']}`. Assets: `{r['assets']}`.",""]
    (figures.parent/"FIGURE_INDEX.md").write_text("\n".join(md),encoding="utf-8")


def build_writing(inputs: Path, tables: Path, out: Path):
    """Preserve the rich pinned Lane-A explanation row and add C/D facts."""
    lane_a = {r["workload"]: r for r in tsv_read(snapshot(inputs, "A", "docs/dtc_l1/post_fast64/generated/paper_workload_explanations.tsv"))}
    assert set(lane_a) == set(WORKLOAD_ORDER) and len(lane_a) == 12
    primary={r['workload']:r for r in tsv_read(tables/"E_PRIMARY_PERFORMANCE.tsv") if r['aggregate']=='NO'}
    mechanism={r['workload']:r for r in tsv_read(tables/"E_IO_OO_MECHANISM.tsv")}
    duplicates=defaultdict(dict)
    for r in tsv_read(tables/"E_DUPLICATE_IO_OO.tsv"):
        duplicates[r['workload']][r['mode']]=r
    compare={r['workload']:r for r in tsv_read(tables/"E_DUPLICATE_PAYLOAD_RATIOS.tsv")}
    d4=defaultdict(list)
    for r in tsv_read(tables/"E_PHYSICAL_OBSERVER_SYNTHESIS.tsv"):
        d4[r['workload']].append(r)
    workload=[]
    for w in WORKLOAD_ORDER:
        a=dict(lane_a[w]); io=duplicates[w]['IO']; oo=duplicates[w]['OO']; claims=["C01_PRIMARY_FAST12_GM","C04_PRESSURE_NONEXCLUSIVE","C05_IO_HOL_SCOPE","C06_OO_RETIRE_SCOPE","C18_PENDING_TAG_TO_DUPLICATE","C19_DUPLICATE_TO_PERFORMANCE","C24_D5_7_3_2","C25_PAYLOAD_SCOPE","C27_DIAGNOSTIC_NOT_PRIMARY"]
        if w in {"ATAX","BICG","GESUMMV"}: claims.append("C02_IO_REGRESSIONS")
        if w == "Gaussian": claims.append("C03_GAUSSIAN_MODEST_BENEFIT")
        if w == "Btree": claims.append("C29_BTREE_ABSOLUTE_SCALE")
        row={**a,
             "primary_IO_speedup_recomputed":primary[w]['speedup_IO_base_over_IO'],
             "primary_OO_speedup_recomputed":primary[w]['speedup_OO_base_over_OO'],
             "IO_HOL_active_SM_cycle_fraction":mechanism[w]['io_hol_sm_cycle_fraction'],
             "OO_OOO_retire_fraction":mechanism[w]['oo_ooo_retire_fraction'],
             "io_duplicate_count_exact":io['duplicate_after_eviction'], "io_duplicate_share_exact":io['duplicate_share_of_lower'],
             "oo_duplicate_count_exact":oo['duplicate_after_eviction'], "oo_duplicate_share_exact":oo['duplicate_share_of_lower'],
             "duplicate_direction":compare[w]['OO_vs_IO_share_disposition'],
             "duplicate_scope":"IO accepted Lane-C exact counter; OO qualified Lane-D exact observer counter; descriptive only.",
             "source_proven_duplicate_semantics":"C18_PENDING_TAG_TO_DUPLICATE; C25_PAYLOAD_SCOPE",
             "d4_scope":"NOT_COVERED_BY_D4", "d4_capacity_observation":"NOT_COVERED_BY_D4; do not project BICG/GESUMMV/Btree capacity results here.",
             "paper_safe_interpretation":a['strongest_supported_interpretation'],
             "forbidden_overclaim":"Do not infer a unique performance cause or recoverable duplicate-performance benefit.",
             "source_lineage":f"Lane A {A}; Lane C {C}; D revision {D_REV}", "claim_ids":",".join(claims)}
        if w == "Gaussian":
            row['paper_safe_interpretation'] = a['strongest_supported_interpretation'] + " Paper-facing wording: approximately 1.108x modest benefit, not no benefit."
        if w in d4:
            cells=sorted(d4[w], key=lambda r:(r['mode'],int(r['physical_pool_kib'])))
            io_cells=[r for r in cells if r['mode']=='IO']
            row['d4_scope']="D4_CONTROLLED_24_32_48_KIB"
            row['d4_capacity_observation']=("Controlled D4 capacity sensitivity: IO cycles " + " -> ".join(r['cycles'] for r in io_cells) +
                "; IO pool-full active-SM fraction " + " -> ".join(r['physical_full_sample_fraction'] for r in io_cells) +
                ". Internal mediators are not isolated.")
            row['claim_ids'] += ",C11_D4_CONTROLLED_CAPACITY,C12_POOL_FULL_EXPOSURE,C13_NO_FREE_DENOMINATORS,C26_D4_WORKLOAD_SCOPE"
        workload.append(row)
    tsv_write(out/"WORKLOAD_EXPLANATIONS.tsv",workload)
    lines=[
        "# POST-FAST64 paper results analysis", "", "## 范围与证据边界（C01, C27, C28）", "",
        "主性能严格来自冻结 FAST64；Lane-D 观察者证据仅作诊断，绝不进入 FAST12 GM。本 Lane-E repair 只做快照、表格、图形和 QA，不启动仿真或修改科学源。", "",
        "## 主性能与机制证据（C01–C06）", "",
        "12 个未四舍五入整数周期比值给出 IO GM 1.326143376x、OO GM 1.592062402x。ATAX、BICG、GESUMMV 的 IO 回归被完整保留；Gaussian 的约 1.108x 应表述为温和收益。Base pressure、IO HOL 和 OO retire/reclaim 是按各自分母定义的非互斥测量证据，不能拼成唯一因果解释。", "",
        "## 敏感性与 D4（C07–C17, C22–C23, C26）", "",
        "逻辑/物理/PIB 均只使用接受的同模式归一化单元。BICG/GESUMMV 16.5 KiB 是非数值资源边界，Btree 16.5 KiB 保持数值。D4 是容量的受控敏感性，覆盖仅限 BICG/GESUMMV/Btree；其内部 occupancy、inflight、L2、lifetime 和 pending-Tag 箭头仍是相关或不足，不能称为 L2 主导。", "",
        "## 重复请求（C18–C21, C24–C25, C29）", "",
        "IO pending-Tag eviction→pre-response same-line reallocation 的计数语义由源码证明；duplicate×128 B 仅为 lower-request payload。D5 的限定 OO 计数给出 7 个更低、3 个更高、2 个均为零；这不支持“OO 普遍消除重复”或由重复消除解释 OO 性能。Btree 的 OO/IO 比值较大仍须结合两边极小的绝对 duplicate share 解读。", "",
        "## 12-workload explanations", "", "`WORKLOAD_EXPLANATIONS.tsv` 保留了每个 Lane-A 的 performance behavior、pressure、HOL、retire/reclaim、traffic、interpretation 与 caveat，并逐项追加 C/D 的精确 duplicate 和 D4 范围。"
    ]
    (out/"PAPER_RESULTS_ANALYSIS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")


def copy_d6(inputs: Path, tables: Path):
    rows=tsv_read(snapshot(inputs,"D_revision","docs/dtc_l1/post_fast64/generated/D6_INTEGRATED_ARROW_CLASSIFICATION.tsv"))
    tsv_write(tables/"E_D6_ARROW_CLASSIFICATION.tsv",rows)


def build_execution_inventory(out: Path):
    rows=[
        {"item":"worktree_scope","value":"dedicated Lane-E bounded repair worktree","status":"DECLARED_SCOPE"},
        {"item":"frozen_FAST64","value":FAST64,"status":"PINNED"},
        {"item":"pinned_inputs","value":f"A={A}; B={B}; C={C}; D_FINAL={D_FINAL}; D_REVISION={D_REV}","status":"PINNED"},
        {"item":"simulation_activity","value":"Lane-E builder/QA has no simulator/trace/GPU/Core invocation path","status":"SOURCE_AUDITED_SCOPE"},
        {"item":"protected_evidence","value":"input snapshots are source-bound and validated against manifest hashes","status":"SOURCE_AUDITED_SCOPE"},
    ]
    tsv_write(out/"E_EXECUTION_INVENTORY.tsv",rows)


def _audit_row(check_id, expected, observed, condition, evidence_path, detail):
    return {"check_id":check_id, "expected":str(expected), "observed":str(observed),
            "status":"PASS" if condition else "FAIL", "evidence_path":evidence_path, "detail":detail}


def _source_sensitivity(inputs, short):
    return tsv_read(snapshot(inputs, "A", "docs/dtc_l1/post_fast64/generated/paper_sens_" + short + ".tsv"))


def core_audit(package: Path, inputs: Path):
    """Independent, data-driven audit of a built core package."""
    rows=[]
    try:
        validate_inputs(inputs); input_ok=True; input_detail="manifest SHA-256 and pinned commit/path closure match"
    except Exception as exc:
        input_ok=False; input_detail=repr(exc)
    rows.append(_audit_row("A00_PINNED_INPUTS", "exact manifest closure", "validated" if input_ok else "rejected", input_ok, "E_INPUT_MANIFEST.tsv", input_detail))

    source_primary=tsv_read(snapshot(inputs,"fast64","docs/dtc_l1/fast64/review_packs/FAST64_FINAL/FAST12_summary.tsv"))
    source_by={r['workload']:r for r in source_primary if r['workload']!='GM-FAST12'}
    primary=tsv_read(package/"tables/E_PRIMARY_PERFORMANCE.tsv")
    actual_order=[r['workload'] for r in primary[:-1]] if len(primary)==13 else []
    rows.append(_audit_row("A01_FAST12_ORDER", "|".join(WORKLOAD_ORDER), "|".join(actual_order), actual_order==WORKLOAD_ORDER and set(source_by)==set(WORKLOAD_ORDER), "tables/E_PRIMARY_PERFORMANCE.tsv", "order is derived from pinned FAST12 source; aggregate is excluded"))
    primary_ok=len(primary)==13 and primary[-1].get('workload')=='GM-FAST12'
    if primary_ok:
        for r in primary[:-1]:
            s=source_by.get(r['workload']); primary_ok &= bool(s) and all(str(r[k])==str(s[k]) for k in ('instructions','base_cycles','io_cycles','oo_cycles')) and r['aggregate']=='NO' and r['evidence_class']=='ACCEPTED_FAST64_EVIDENCE'
        io_prod=Decimal(1); oo_prod=Decimal(1)
        for s in (source_by[w] for w in WORKLOAD_ORDER):
            io_prod*=d(s['base_cycles'])/d(s['io_cycles']); oo_prod*=d(s['base_cycles'])/d(s['oo_cycles'])
        gm_io=io_prod**(Decimal(1)/Decimal(12)); gm_oo=oo_prod**(Decimal(1)/Decimal(12))
        primary_ok &= primary[-1]['speedup_IO_base_over_IO']==f"{gm_io:.12f}" and primary[-1]['speedup_OO_base_over_OO']==f"{gm_oo:.12f}"
    rows.append(_audit_row("A02_PRIMARY_CELLS_AND_GM", "12 workloads x Base/IO/OO = 36; integer GM", f"{max(0,len(primary)-1)} workloads x 3; rows={len(primary)}", primary_ok, "tables/E_PRIMARY_PERFORMANCE.tsv", "cycles and GM are recomputed from pinned integers; diagnostic rows are rejected"))

    d4_source=tsv_read(snapshot(inputs,"D_revision","docs/dtc_l1/post_fast64/generated/D4_OBSERVER_PHYSICAL_TELEMETRY.tsv")); d4=tsv_read(package/"tables/E_PHYSICAL_OBSERVER_SYNTHESIS.tsv")
    expected_d4={(w,str(p),m) for w in ('BICG','GESUMMV','Btree') for p in (24,32,48) for m in ('IO','OO')}; observed_d4={(r['workload'],r['physical_pool_kib'],r['mode']) for r in d4}
    denom_ok=all(int(r['observer_sample_sm_cycles'])>0 for r in d4) and all('64*global' not in r.get('observer_sample_sm_cycles','') for r in d4)
    rows.append(_audit_row("A03_D4_CARTESIAN_AND_DENOMINATOR", sorted(expected_d4), sorted(observed_d4), len(d4)==len(expected_d4) and observed_d4==expected_d4 and d4==d4_source and denom_ok, "tables/E_PHYSICAL_OBSERVER_SYNTHESIS.tsv", "exact D4 cartesian coverage and source observer_sample_sm_cycles field"))
    index=tsv_read(snapshot(inputs,"D_final","docs/dtc_l1/post_fast64/generated/D4_D5_OBSERVER_RAW_RUN_INDEX.tsv")); d7=tsv_read(snapshot(inputs,"D_revision","docs/dtc_l1/post_fast64/generated/D7_ORDERED_PREEXISTING_STAT_AUDIT.tsv"))
    exp_new=sum(r['source_row_kind']=='NEW_DIAGNOSTIC_RUN' for r in index); exp_reuse=sum(r['source_row_kind']=='D3B_EXACT_REUSE' for r in index)
    obs_new=sum(r['source_row_kind']=='NEW_DIAGNOSTIC_RUN' for r in d7); obs_reuse=sum(r['source_row_kind']=='D3B_EXACT_REUSE' for r in d7)
    rows.append(_audit_row("A04_D4_LAUNCH_REUSE", f"new={exp_new}; reuse={exp_reuse}", f"new={obs_new}; reuse={obs_reuse}", (exp_new,exp_reuse)==(obs_new,obs_reuse)==(29,1) and len(index)==len(d7)==30, "inputs/D_final/.../D4_D5_OBSERVER_RAW_RUN_INDEX.tsv; inputs/D_revision/.../D7_ORDERED_PREEXISTING_STAT_AUDIT.tsv", "counts computed from pinned rows, not a handwritten observed phrase"))

    d5=tsv_read(snapshot(inputs,"D_revision","docs/dtc_l1/post_fast64/generated/D5_IO_OO_DUPLICATE_COMPARISON.tsv")); dup=tsv_read(package/"tables/E_DUPLICATE_IO_OO.tsv"); comp=tsv_read(package/"tables/E_DUPLICATE_PAYLOAD_RATIOS.tsv")
    by_d5={r['workload']:r for r in d5}; by_dup={(r['workload'],r['mode']):r for r in dup}
    d5_ok=set(by_d5)==set(WORKLOAD_ORDER) and len(dup)==24 and len(comp)==12
    for w in WORKLOAD_ORDER:
        if w not in by_d5 or (w,'OO') not in by_dup or (w,'IO') not in by_dup: d5_ok=False; continue
        d5_ok &= by_dup[(w,'OO')]['evidence_source']=='Lane_D_qualified_observer' and by_dup[(w,'OO')]['qualified_evidence_status']==by_d5[w]['oo_evidence_status']
        d5_ok &= by_dup[(w,'OO')]['duplicate_after_eviction']==by_d5[w]['oo_duplicate_after_eviction'] and by_dup[(w,'IO')]['duplicate_after_eviction']==by_d5[w]['io_duplicate_after_eviction']
    d5_ok &= all(r['payload_scope'] == 'SOURCE_PROVEN_128B_LOWER_REQUEST_PAYLOAD_ONLY_NOT_DRAM_OR_TOTAL_LINK_TRAFFIC' for r in dup)
    directions=[r['OO_vs_IO_share_disposition'] for r in comp]; d5_ok &= [directions.count(x) for x in ('OO_LOWER','OO_HIGHER','BOTH_ZERO')]==[7,3,2]
    rows.append(_audit_row("A05_D5_QUALIFIED_PAIRS", "12 pairs; OO qualifier exact; lower/higher/zero=7/3/2", f"pairs={len(comp)}; lower/higher/zero={directions.count('OO_LOWER')}/{directions.count('OO_HIGHER')}/{directions.count('BOTH_ZERO')}", d5_ok, "tables/E_DUPLICATE_IO_OO.tsv; tables/E_DUPLICATE_PAYLOAD_RATIOS.tsv", "D5 exact OO metric required; proxy substitution is rejected"))

    for short, cid in (("logical","A06_LOGICAL_MEMBERSHIP"),("physical","A07_PHYSICAL_MEMBERSHIP_AND_BOUNDARY"),("pib","A08_PIB_MEMBERSHIP")):
        source=_source_sensitivity(inputs,short); actual=tsv_read(package/f"tables/E_SENS_{short.upper()}.tsv")
        detail="output rows equal pinned Lane-A table; numeric plot membership is row_kind=NUMERIC_ACCEPTED_POINT"
        ok=actual==source and bool(source)
        if short=='physical':
            dead={(r['workload'],r['mode'],r['requested_point']) for r in actual if r['row_kind']=='NONNUMERIC_BOUNDARY_MARKER'}
            btree=[r for r in actual if r['workload']=='Btree' and r['requested_point']=='16.5']
            ok &= dead=={(w,m,'16.5') for w in ('BICG','GESUMMV') for m in ('IO','OO')} and len(btree)==2 and all(r['row_kind']=='NUMERIC_ACCEPTED_POINT' for r in btree)
            detail += "; BICG/GESUMMV 16.5 nonnumeric and Btree 16.5 numeric verified"
        rows.append(_audit_row(cid, f"pinned rows={len(source)}", f"output rows={len(actual)}; numeric={sum(r['row_kind']=='NUMERIC_ACCEPTED_POINT' for r in actual)}", ok, f"tables/E_SENS_{short.upper()}.tsv", detail))

    figures=tsv_read(package/"FIGURE_INDEX.tsv"); ids=[r['figure_id'] for r in figures]; figure_ok=ids==[f"F{i:02d}" for i in range(1,10)] and len(set(ids))==9
    for fid in ids:
        figure_ok &= all((package/f"figures/{fid}{suffix}").exists() for suffix in ('.svg','.pdf','.png'))
    md=(package/'FIGURE_INDEX.md').read_text(encoding='utf-8'); figure_ok &= all(md.count(f"## F{i:02d} —")==1 for i in range(1,10))
    rows.append(_audit_row("A09_FIGURE_IDENTITY", "unique ordered F01..F09 with three assets and one heading each", f"ids={','.join(ids)}", figure_ok, "FIGURE_INDEX.tsv; FIGURE_INDEX.md; figures/", "F07 duplicate index/stale series path is prohibited"))
    workload=tsv_read(package/"WORKLOAD_EXPLANATIONS.tsv"); rich={"performance_behavior","base_pressure_signature_raw","io_hol_evidence","oo_retire_reclaim_evidence","traffic_contrast","caveat_or_alternative","io_duplicate_count_exact","oo_duplicate_count_exact","duplicate_direction","d4_scope","source_lineage"}
    workload_ok=len(workload)==12 and [r['workload'] for r in workload]==WORKLOAD_ORDER and all(rich<=set(r) and r['performance_behavior'] for r in workload)
    rows.append(_audit_row("A10_RICH_WORKLOAD_EXPLANATIONS", "12 Lane-A-rich rows plus C/D fields", f"rows={len(workload)}; fields={len(workload[0]) if workload else 0}", workload_ok, "WORKLOAD_EXPLANATIONS.tsv", "Lane-A performance/pressure/HOL/reclaim/traffic/caveat fields are retained per workload"))
    return rows


def machine_figure_checks(package: Path):
    rows=[]
    for n in range(1,10):
        fid=f"F{n:02d}"; svg=package/f"figures/{fid}.svg"; png=package/f"figures/{fid}.png"; pdf=package/f"figures/{fid}.pdf"; detail=[]; ok=True
        try:
            ET.fromstring(svg.read_text(encoding='utf-8')); detail.append("SVG XML parsed")
            im=Image.open(png); im.load(); ok &= im.width>=1400 and im.height>=850; detail.append(f"PNG={im.width}x{im.height}")
            ok &= pdf.read_bytes().startswith(b'%PDF'); detail.append("PDF signature")
        except Exception as exc:
            ok=False; detail.append(repr(exc))
        rows.append({"figure_id":fid,"machine_status":"PASS" if ok else "FAIL","checks":"; ".join(detail),"scope":"machine existence/XML/raster/PDF checks only; not a visual review"})
    tsv_write(package/"E_MACHINE_FIGURE_CHECKS.tsv",rows)
    return rows


def claim_audit(package: Path):
    claims=tsv_read(package/"E_CLAIM_EVIDENCE_REGISTER.tsv"); ids={r['claim_id'] for r in claims}; rows=[]
    rows.append({"audit_id":"required_claim_id_set","expected":"|".join(REQUIRED_CLAIM_IDS),"observed":"|".join(sorted(ids)),"status":"PASS" if ids==set(REQUIRED_CLAIM_IDS) else "FAIL","detail":"required register coverage"})
    refs=[]
    for source, path, field in (("figure",package/"FIGURE_INDEX.tsv","claim_ids"),("workload",package/"WORKLOAD_EXPLANATIONS.tsv","claim_ids")):
        for r in tsv_read(path): refs.extend((source,x) for x in r[field].split(',') if x)
    unknown=sorted({x for _,x in refs if x not in ids})
    rows.append({"audit_id":"artifact_claim_references","expected":"all figure/workload IDs registered","observed":"unknown="+",".join(unknown) if unknown else "unknown=NONE","status":"PASS" if not unknown else "FAIL","detail":"explicit figure/workload claim-id mapping; no NLP inference"})
    prose=(package/"PAPER_RESULTS_ANALYSIS.md").read_text(encoding='utf-8')
    prose_ok=all(x in prose for x in ("C01", "C18", "C24", "C25", "C26", "C27"))
    rows.append({"audit_id":"paper_section_traceability","expected":"core claim IDs named in paper sections","observed":"present" if prose_ok else "missing","status":"PASS" if prose_ok else "FAIL","detail":"paper prose references scoped claim groups"})
    tsv_write(package/"E_CLAIM_AUDIT.tsv",rows)
    return rows


def write_core_audits(inputs: Path, package: Path):
    audit=core_audit(package,inputs); tsv_write(package/"E_COVERAGE_SENSITIVITY_AUDIT.tsv",audit)
    write_coverage_and_metric_dictionary(inputs,package,audit)
    figures=machine_figure_checks(package); claims=claim_audit(package)
    return audit, figures, claims


def build_core(inputs: Path, output: Path):
    validate_inputs(inputs)
    if output.exists():
        # The caller supplies a dedicated output directory; only Lane-E build
        # products inside it may be replaced, never a source worktree.
        shutil.rmtree(output)
    output.mkdir(parents=True)
    # Keep the complete compact dependency closure with the review package so
    # an offline reviewer does not need raw simulator directories or Git-object
    # access to inspect/rebuild it.  This is a 1.9-MiB snapshot, not raw logs.
    shutil.copytree(inputs, output / "inputs")
    copy_text(inputs.parent / "E_INPUT_MANIFEST.tsv", output / "E_INPUT_MANIFEST.tsv")
    tables=output/"tables"; figures=output/"figures"; tables.mkdir(); figures.mkdir()
    build_execution_inventory(output); build_reconciliation(output)
    build_primary(inputs,tables); build_pressure_and_mechanism(inputs,tables); build_sensitivities(inputs,tables); build_observer(inputs,tables); build_duplicates(inputs,tables); copy_d6(inputs,tables)
    build_figures(tables,figures); build_writing(inputs,tables,output)
    return write_core_audits(inputs,output)


def _all_pass(rows, field="status"):
    return bool(rows) and all(r[field]=="PASS" for r in rows)


def validate_core(package: Path, inputs: Path):
    errors=[]
    try:
        audit=core_audit(package,inputs); errors += [f"{r['check_id']}: {r['detail']}" for r in audit if r['status']!='PASS']
        figures=machine_figure_checks(package); errors += [f"machine {r['figure_id']}: {r['checks']}" for r in figures if r['machine_status']!='PASS']
        claims=claim_audit(package); errors += [f"claim {r['audit_id']}: {r['observed']}" for r in claims if r['status']!='PASS']
    except Exception as exc:
        errors.append(repr(exc))
    return errors


def _load_qa_records(qa_dir: Path, package: Path):
    negative=tsv_read(qa_dir/"E_NEGATIVE_FIXTURE_RESULTS.tsv")
    visual=tsv_read(qa_dir/"E_VISUAL_REVIEW.tsv")
    determinism=tsv_read(qa_dir/"E_DETERMINISM_EXECUTION.tsv")
    if len(negative)!=6 or not _all_pass(negative): raise ValueError("negative fixture record is missing or has non-PASS result")
    if len(visual)!=9 or [r['figure_id'] for r in visual] != [f"F{i:02d}" for i in range(1,10)] or not _all_pass(visual, "review_status"):
        raise ValueError("explicit nine-figure visual review is missing or non-PASS")
    for r in visual:
        for key,suffix in (("svg_sha256",'.svg'),("png_sha256",'.png'),("pdf_sha256",'.pdf')):
            if r[key] != sha256(package/f"figures/{r['figure_id']}{suffix}"): raise ValueError(f"visual record hash mismatch: {r['figure_id']} {key}")
    if len(determinism)!=1 or determinism[0].get('status')!='PASS': raise ValueError("measured determinism record is missing or non-PASS")
    return negative,visual,determinism


def build_provenance(package: Path, inputs: Path):
    import platform
    builder=Path(__file__).resolve(); font_paths=[Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')]
    rows=[
        {"component":"python","value":sys.version.replace('\n',' '),"sha256_or_version":sys.implementation.name,"scope":"actual builder runtime"},
        {"component":"Pillow","value":Image.__version__,"sha256_or_version":Image.__file__,"scope":"actual SVG raster/PDF renderer dependency"},
        {"component":"builder","value":str(builder),"sha256_or_version":sha256(builder),"scope":"Lane-E builder source"},
        {"component":"input_manifest","value":"E_INPUT_MANIFEST.tsv","sha256_or_version":sha256(inputs.parent/'E_INPUT_MANIFEST.tsv'),"scope":"pinned compact dependency closure"},
        {"component":"platform","value":platform.platform(),"sha256_or_version":platform.machine(),"scope":"interpret renderer reproducibility"},
    ]
    for p in font_paths:
        rows.append({"component":"font","value":str(p) if p.exists() else "FALLBACK_PIL_DEFAULT", "sha256_or_version":sha256(p) if p.exists() else "NOT_PRESENT", "scope":"actual DejaVu font selection/fallback"})
    tsv_write(package/"E_BUILD_PROVENANCE.tsv",rows)


def write_visual_qa(package: Path, visual_rows):
    lines=["# Lane-E visual QA", "", "This report is derived from the explicit agent visual-review record in `qa/E_VISUAL_REVIEW.tsv`. Machine signature/dimension checks are separately recorded in `E_MACHINE_FIGURE_CHECKS.tsv`; the builder does not assert human inspection.", "", "| Figure | Status | Findings | Repair / re-review |", "|---|---|---|---|"]
    for r in visual_rows: lines.append(f"| {r['figure_id']} | {r['review_status']} | {r['findings']} | {r['repair_history']} |")
    (package/"E_VISUAL_QA.md").write_text("\n".join(lines)+"\n",encoding="utf-8")


def write_validation_report(package: Path, audit, machine, claims, negative, determinism):
    rows=[]
    rows += [(r['check_id'],r['status'],r['detail']) for r in audit]
    rows += [("MACHINE_"+r['figure_id'],r['machine_status'],r['checks']) for r in machine]
    rows += [("CLAIM_"+r['audit_id'],r['status'],r['detail']) for r in claims]
    rows += [("NEGATIVE_"+r['fixture_id'],r['status'],r['observed_result']) for r in negative]
    rows += [("DETERMINISM_EXECUTION",determinism[0]['status'],determinism[0]['detail'])]
    overall=all(status=='PASS' for _,status,_ in rows)
    lines=["# Lane-E validation report", "", f"Overall: **{'PASS' if overall else 'FAIL'}**", "", "| Check | Status | Measured evidence |", "|---|---|---|"]
    lines += [f"| {a} | {b} | {c} |" for a,b,c in rows]
    (package/"E_VALIDATION_REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return overall


def build_checklist(package: Path, audit, machine, claims, negative, visual, determinism):
    pass_audit={r['check_id']:r['status']=='PASS' for r in audit}; pass_machine=_all_pass(machine,'machine_status'); pass_claims=_all_pass(claims); pass_negative=_all_pass(negative); pass_visual=_all_pass(visual,'review_status'); pass_det=_all_pass(determinism)
    stages=[
        ("E0.1","E0","ownership_and_freeze",pass_audit.get('A00_PINNED_INPUTS',False),"E_EXECUTION_INVENTORY.tsv","core input audit"),
        ("E0.2","E0","source_import",pass_audit.get('A00_PINNED_INPUTS',False),"E_INPUT_MANIFEST.tsv","source-bound manifest audit"),
        ("E0.3","E0","coverage_identity_units",all(pass_audit.get(x,False) for x in ('A01_FAST12_ORDER','A02_PRIMARY_CELLS_AND_GM','A03_D4_CARTESIAN_AND_DENOMINATOR','A04_D4_LAUNCH_REUSE')),"E_COVERAGE_AND_IDENTITY.tsv","data-driven coverage audit"),
        ("E0.4","E0","interpretation_reconciliation",pass_claims,"E_INTERPRETATION_RECONCILIATION.tsv; E_CLAIM_EVIDENCE_REGISTER.tsv","claim audit"),
        ("E1.1","E1","primary_and_mechanisms",all(pass_audit.get(x,False) for x in ('A01_FAST12_ORDER','A02_PRIMARY_CELLS_AND_GM')),"tables/E_PRIMARY_PERFORMANCE.tsv; tables/E_IO_OO_MECHANISM.tsv","integer-cycle audit"),
        ("E1.2","E1","three_sensitivities",all(pass_audit.get(x,False) for x in ('A06_LOGICAL_MEMBERSHIP','A07_PHYSICAL_MEMBERSHIP_AND_BOUNDARY','A08_PIB_MEMBERSHIP')),"E_COVERAGE_SENSITIVITY_AUDIT.tsv","source membership/row-kind audit"),
        ("E1.3","E1","pool_observer",pass_audit.get('A03_D4_CARTESIAN_AND_DENOMINATOR',False),"tables/E_PHYSICAL_OBSERVER_SYNTHESIS.tsv","D4 cartesian/denominator audit"),
        ("E1.4","E1","duplicates",pass_audit.get('A05_D5_QUALIFIED_PAIRS',False),"tables/E_DUPLICATE_IO_OO.tsv","qualified D5 audit"),
        ("E1.5","E1","actual_figures",pass_audit.get('A09_FIGURE_IDENTITY',False) and pass_machine,"FIGURE_INDEX.tsv; E_MACHINE_FIGURE_CHECKS.tsv","unique figure and machine checks"),
        ("E1.6","E1","writing",pass_audit.get('A10_RICH_WORKLOAD_EXPLANATIONS',False) and pass_claims,"WORKLOAD_EXPLANATIONS.tsv; E_CLAIM_AUDIT.tsv","rich workload and claim audit"),
        ("E2.1","E2","automated_acceptance",pass_negative and _all_pass(audit) and pass_claims,"E_VALIDATION_REPORT.md; qa/E_NEGATIVE_FIXTURE_RESULTS.tsv","actual core/negative/claim checks"),
        ("E2.2","E2","visual_QA",pass_visual,"E_VISUAL_QA.md; qa/E_VISUAL_REVIEW.tsv","explicit nine-figure visual record"),
        ("E2.3","E2","reproduction_package",pass_det,"rebuild_reports/DETERMINISM_COMPARISON.md; E_BUILD_PROVENANCE.tsv","measured isolated-core comparison"),
        ("E2.4","E2","final_closeout",all((pass_negative,pass_visual,pass_det,_all_pass(audit),pass_machine,pass_claims)),"LANE_E_FINAL.md; E_VALIDATION_REPORT.md","all independent mandatory checks"),
    ]
    out=[]
    for cid,stage,purpose,ok,evidence,command in stages:
        out.append({"check_id":cid,"stage":stage,"purpose":purpose,"status":"PASS" if ok else "NOT_RUN_OR_FAIL","evidence_path":evidence,"check_lineage":command})
    tsv_write(package/"LANE_E_ACCEPTANCE_CHECKLIST.tsv",out)
    return out


def final_docs(package: Path, determinism):
    (package/"REPRODUCE.md").write_text("""# Reproduce the Lane-E review pack

No simulator, trace capture, GPU, raw SIM_HOST directory, or active Codex session is required. Python 3 and Pillow are required; exact build/font provenance is in `E_BUILD_PROVENANCE.tsv`.

```bash
python3 util/dtc_l1/build_post_fast64_lane_e.py --build-core --inputs docs/dtc_l1/post_fast64/lane_e/inputs --output /tmp/lane-e-core
python3 util/dtc_l1/build_post_fast64_lane_e.py --validate-core --inputs docs/dtc_l1/post_fast64/lane_e/inputs --output /tmp/lane-e-core
python3 util/dtc_l1/build_post_fast64_lane_e.py --build --inputs docs/dtc_l1/post_fast64/lane_e/inputs --qa-dir docs/dtc_l1/post_fast64/lane_e/qa_records --output /tmp/lane-e-final
python3 util/dtc_l1/build_post_fast64_lane_e.py --validate --inputs docs/dtc_l1/post_fast64/lane_e/inputs --output /tmp/lane-e-final
```

The final command consumes frozen compact inputs and explicit QA records only; it never launches a simulator.
""",encoding="utf-8")
    (package/"LIMITATIONS_AND_OPEN_QUESTIONS.md").write_text("""# Limitations and open questions

- FAST64 is immutable primary evidence; observer data is diagnostic only.
- D4 controlled capacity sensitivity does not causally identify its internal mediators.
- L2 dominance and duplicate-secondary feedback remain insufficient.
- IO duplicate semantics are source-proven; OO counts are qualified observer evidence, never a new-miss proxy.
- D4 covers BICG, GESUMMV, and Btree only.
- Lower-request payload is not DRAM, total memory/interconnect traffic, or recoverable performance.
""",encoding="utf-8")
    det=determinism[0]
    reports=package/"rebuild_reports"; reports.mkdir(exist_ok=True)
    (reports/"DETERMINISM_COMPARISON.md").write_text(f"""# Measured isolated core determinism comparison

Status: **{det['status']}**

This record is copied from the executed QA runner result `qa/E_DETERMINISM_EXECUTION.tsv`, not generated as a claimed build step.

- Compared files: {det['compared_file_count']}
- SHA-256/byte mismatches: {det['mismatch_count']}
- Detail: {det['detail']}

The comparison is performed on the deterministic build core before this report is materialized, avoiding self-reference. Formal package tree comparison is independently executed during closeout and recorded outside the generator command log.
""",encoding="utf-8")
    (package/"LANE_E_FINAL.md").write_text(f"""# Lane E final closeout

Status: **POST_FAST64_PAPER_ANALYSIS_AND_MECHANISM_EXPLORATION_READY_FOR_REVIEW**

This package is generated only after independent data audits, executed negative fixtures, explicit visual-review records, and measured isolated determinism records all pass. It uses frozen FAST64 `{FAST64}`, A `{A}`, B `{B}`, C `{C}`, D history `{D_FINAL}`, and selected D revision `{D_REV}`.

The artifact QA repair does not alter accepted scientific inputs, primary results, Core, observer semantics, configuration, or simulator state.
""",encoding="utf-8")


def manifest(package: Path):
    rows=[]
    for p in sorted(x for x in package.rglob("*") if x.is_file()):
        if p.name=="E_OUTPUT_MANIFEST.tsv": continue
        rows.append({"path":str(p.relative_to(package)),"sha256":sha256(p),"bytes":p.stat().st_size,"kind":p.suffix.lstrip('.') or "text"})
    tsv_write(package/"E_OUTPUT_MANIFEST.tsv",rows)


def build_final(inputs: Path, qa_dir: Path, output: Path):
    audit,machine,claims=build_core(inputs,output)
    negative,visual,determinism=_load_qa_records(qa_dir,output)
    qa_out=output/"qa"; shutil.copytree(qa_dir,qa_out)
    build_provenance(output,inputs); write_visual_qa(output,visual)
    overall=write_validation_report(output,audit,machine,claims,negative,determinism)
    checklist=build_checklist(output,audit,machine,claims,negative,visual,determinism)
    if not overall or not _all_pass(checklist): raise AssertionError("mandatory Lane-E result map is not all PASS")
    final_docs(output,determinism); manifest(output)


def validate_package(package: Path, inputs: Path):
    errors=validate_core(package,inputs)
    try:
        qa=package/"qa"; negative,visual,determinism=_load_qa_records(qa,package)
        if not (package/"E_BUILD_PROVENANCE.tsv").exists(): errors.append("missing build provenance")
        if not (package/"E_VISUAL_QA.md").exists(): errors.append("missing visual QA derived from record")
        checklist=tsv_read(package/"LANE_E_ACCEPTANCE_CHECKLIST.tsv")
        if len(checklist)!=14 or not _all_pass(checklist): errors.append("checklist has a non-PASS row")
        manifest_rows=tsv_read(package/"E_OUTPUT_MANIFEST.tsv") if (package/"E_OUTPUT_MANIFEST.tsv").exists() else []
        if manifest_rows:
            for r in manifest_rows:
                p=package/r['path']
                if not p.exists() or sha256(p)!=r['sha256']: errors.append("output manifest mismatch: "+r['path'])
    except Exception as exc:
        errors.append(repr(exc))
    return errors


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--import-git",action="store_true"); ap.add_argument("--repo",type=Path)
    ap.add_argument("--inputs",type=Path,required=True); ap.add_argument("--output",type=Path)
    ap.add_argument("--qa-dir",type=Path)
    ap.add_argument("--build-core",action="store_true"); ap.add_argument("--validate-core",action="store_true")
    ap.add_argument("--build",action="store_true"); ap.add_argument("--validate",action="store_true")
    args=ap.parse_args()
    if args.import_git:
        if not args.repo: ap.error("--import-git requires --repo")
        import_git(args.repo,args.inputs)
    if args.build_core:
        if not args.output: ap.error("--build-core requires --output")
        audit,machine,claims=build_core(args.inputs,args.output)
        if not (_all_pass(audit) and _all_pass(machine,'machine_status') and _all_pass(claims)): raise SystemExit("core build audit failed")
        print("LANE_E_CORE_BUILD_PASS")
    if args.validate_core:
        if not args.output: ap.error("--validate-core requires --output")
        errors=validate_core(args.output,args.inputs)
        if errors: raise SystemExit("core validation failures: "+repr(errors))
        print("LANE_E_CORE_VALIDATION_PASS")
    if args.build:
        if not args.output or not args.qa_dir: ap.error("--build requires --output and --qa-dir")
        build_final(args.inputs,args.qa_dir,args.output)
        print("LANE_E_FINAL_BUILD_PASS")
    if args.validate:
        if not args.output: ap.error("--validate requires --output")
        errors=validate_package(args.output,args.inputs)
        if errors: raise SystemExit("final validation failures: "+repr(errors))
        print("LANE_E_FINAL_VALIDATION_PASS")
    if not (args.import_git or args.build_core or args.validate_core or args.build or args.validate): ap.error("select an action")


if __name__ == "__main__": main()
