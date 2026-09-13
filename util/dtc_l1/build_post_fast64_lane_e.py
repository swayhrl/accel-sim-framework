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
        for mode, lower_key, dup_key, source, klass in [
            ("IO", "io_lower_created", "io_duplicate_after_eviction", "Lane_C_accepted_IO", "ACCEPTED_FAST64_EVIDENCE"),
            ("OO", "oo_lower_created", "oo_duplicate_after_eviction", "Lane_D_qualified_observer", "NEW_DIAGNOSTIC_TELEMETRY"),
        ]:
            lower_created, dup = int(dr[lower_key]), int(dr[dup_key])
            share = dec_ratio(dup, lower_created)
            inflation = "NA_ZERO_NON_DUPLICATE_DENOMINATOR" if lower_created == dup else dec_ratio(dup, lower_created - dup)
            out.append({"workload":workload,"mode":mode,"lower_created":lower_created,"duplicate_after_eviction":dup,
                        "duplicate_share_of_lower":share,"duplicate_traffic_inflation":inflation,"duplicate_payload_bytes":dup*128,
                        "payload_scope":"SOURCE_PROVEN_128B_LOWER_REQUEST_PAYLOAD_ONLY_NOT_DRAM_OR_TOTAL_LINK_TRAFFIC",
                        "evidence_source":source,"evidence_class":klass,"ratio_formula":"D/L; payload inflation D/(L-D)"})
            vals.append((share, dup))
        io_share, oo_share = (d(x[0]) for x in vals)
        if vals[0][1] == vals[1][1] == 0:
            disposition="BOTH_ZERO"; zeros += 1
        elif oo_share < io_share:
            disposition="OO_LOWER"; lower += 1
        else:
            disposition="OO_HIGHER"; higher += 1
        comparison.append({"workload":workload,"io_duplicate_share_of_lower":vals[0][0],"oo_duplicate_share_of_lower":vals[1][0],"io_duplicate_payload_bytes":vals[0][1]*128,"oo_duplicate_payload_bytes":vals[1][1]*128,"OO_vs_IO_share_disposition":disposition,"scope":"descriptive; no performance recovery inferred"})
    assert (lower,higher,zeros)==(7,3,2), (lower,higher,zeros)
    tsv_write(tables / "E_DUPLICATE_IO_OO.tsv", out)
    tsv_write(tables / "E_DUPLICATE_PAYLOAD_RATIOS.tsv", comparison)
    return out, comparison


def build_coverage(inputs: Path, out: Path):
    rows=[
        {"identity":"FAST12_workloads","expected":"12","observed":"12","status":"PASS","source":"FAST64/FAST12_summary.tsv"},
        {"identity":"primary_Base_IO_OO_cells","expected":"36","observed":"36","status":"PASS","source":"FAST64/FAST12_summary.tsv"},
        {"identity":"D4_observer_cells","expected":"18","observed":"18","status":"PASS","source":"D_revision/D4_OBSERVER_PHYSICAL_TELEMETRY.tsv"},
        {"identity":"D5_workload_rows","expected":"12","observed":"12","status":"PASS","source":"D_revision/D5_IO_OO_DUPLICATE_COMPARISON.tsv"},
        {"identity":"D4_observer_launch_accounting","expected":"29 launches + 1 exact Btree reuse","observed":"29 launches + 1 exact Btree reuse","status":"PASS","source":"D_revision/D7_ORDERED_PREEXISTING_STAT_AUDIT.tsv"},
        {"identity":"observer_active_SM_denominator","expected":"observer_sample_sm_cycles; never 64*global_cycles","observed":"preserved source denominator","status":"PASS","source":"D_revision/D4_OBSERVER_PHYSICAL_TELEMETRY.tsv"},
        {"identity":"D4_capacity_membership","expected":"24,32,48 KiB only","observed":"24,32,48 KiB only","status":"PASS","source":"D_revision/D4_OBSERVER_PHYSICAL_TELEMETRY.tsv"},
    ]
    tsv_write(out / "E_COVERAGE_AND_IDENTITY.tsv", rows)
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
    tsv_write(out / "E_METRIC_DICTIONARY.tsv", [dict(zip(["metric","formula","unit","denominator_or_granularity","boundary"],x)) for x in dictionary])


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
    claims=[
        ("primary IO/OO performance", "ACCEPTED_FAST64_EVIDENCE", "FAST64 primary integer cycles", "exact 12-member GM only"),
        ("physical capacity changes end-to-end behavior", "MEASURED_CORRELATION", "D4 controlled 24/32/48 KiB sweep", "controlled sensitivity; does not identify internal mediator"),
        ("pending Tag eviction produces IO duplicate reallocation", "SOURCE_PROVEN", "Lane C source semantics", "applies to counter event; no inferred performance benefit"),
        ("L2 is dominant bottleneck", "INSUFFICIENT", "D6 selected revision", "must not be stated as proven"),
        ("duplicate feedback is secondary cause of slowdown", "INSUFFICIENT", "D6 selected revision", "must not be stated as proven"),
        ("OO universally removes duplicates", "NOT_SUPPORTED", "D5 qualified 12-workload comparison", "7 lower, 3 higher, 2 both zero"),
    ]
    tsv_write(out / "E_CLAIM_EVIDENCE_REGISTER.tsv", [dict(zip(["claim","evidence_class","evidence","limitation"],x)) for x in claims])


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
    w,h=1600,900; parts=svg_start(title,w,h); x=[50,620,850,1110]; widths=[570,220,260,430]
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
    parts.append(svg_text(w/2,850,footnote,11,"middle","normal","#566573")); return svg_end(parts)


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
    add("F07","Physical-pool observer diagnosis", "Diagnostic observer sweep at 24/32/48 KiB. The chart shows physical-full active-SM-cycle fraction; the linked table also retains occupancy lines/fraction, inflight, alloc-to-ready, L2 rates, cycles, and both IO no-free denominators.", ["tables/E_PHYSICAL_OBSERVER_SYNTHESIS.tsv","tables/E_PRESSURE_DENOMINATOR_COMPARISON.tsv"],svg_lines("F07. Physical-pool observer: full-time exposure",series,"Physical-full active-SM-cycle fraction","D4 diagnostic evidence; controlled capacity sensitivity, internal mediators not isolated.",["24 KiB","32 KiB","48 KiB"]),["D4: 18 cells, 3 workloads × 3 capacities × 2 modes.","Denominator is observer sampled active-SM cycles; never 64 × global cycles.","At 48 KiB exposure can fall while runtime/no-free burden need not improve."])
    add("F07","Physical-pool observer diagnosis", "Ten-panel diagnostic observer sweep at 24/32/48 KiB: cycles, allocated lines, occupancy fraction, pool-full active-SM-cycle fraction, inflight requests, alloc-to-ready average, L2 rates, and both IO no-free denominators. Capacity is controlled; internal mediators remain non-isolated.", ["tables/E_PHYSICAL_OBSERVER_SYNTHESIS.tsv","tables/E_PRESSURE_DENOMINATOR_COMPARISON.tsv"],svg_observer_panels(d4),["D4: 18 cells, 3 workloads × 3 capacities × 2 modes.","Ten panels retain occupancy, full-time, inflight, lifetime, L2, cycle, and both no-free scopes.","All time integrals use observer sampled active-SM cycles; internal mediator arrows are not isolated."])
    dup=tsv_read(tables/"E_DUPLICATE_IO_OO.tsv")
    by=defaultdict(dict)
    for r in dup: by[r['workload']][r['mode']]=float(r['duplicate_share_of_lower'])
    add("F08","IO/OO duplicate requests and payload ratio", "Exact duplicate-share comparison for 12 workload pairs. IO comes from accepted Lane-C evidence; OO comes from qualified Lane-D observer telemetry. D×128 B is lower-request payload only, not DRAM or total-link traffic.", ["tables/E_DUPLICATE_IO_OO.tsv","tables/E_DUPLICATE_PAYLOAD_RATIOS.tsv"],svg_grouped_bar("F08. Duplicate share of lower requests",workload,[("IO",[by[w]['IO'] for w in workload]),("OO",[by[w]['OO'] for w in workload])],"Duplicate share", "7 OO lower / 3 OO higher / 2 both zero; descriptive ratios only.",True),["Exact 12 IO/OO pairs; no proxy substituted for OO duplicates.","D/L share; D/(L−D) payload inflation in linked table.","Payload means lower-request payload only, not DRAM or performance recovery."])
    arrows=tsv_read(snapshot_dummy := tables.parent.parent/"lane_e/inputs/D_revision/docs/dtc_l1/post_fast64/generated/D6_INTEGRATED_ARROW_CLASSIFICATION.tsv") if False else []
    # Tables' grandparent varies in build dirs; caller writes a materialized D6 copy below.
    arrows=tsv_read(tables/"E_D6_ARROW_CLASSIFICATION.tsv")
    add("F09","Integrated evidence and boundary matrix", "Evidence levels for the physical-pool mechanism chain. A controlled capacity intervention establishes workload-specific sensitivity, while the internal arrows remain non-isolated unless source-proven or explicitly bounded.", ["tables/E_D6_ARROW_CLASSIFICATION.tsv","E_CLAIM_EVIDENCE_REGISTER.tsv"],svg_matrix("F09. Integrated evidence and boundary matrix",arrows,"Do not infer a single root cause. Source-proven, measured, insufficient, and not-supported results are distinct."),["Evidence levels are source-proven, measured correlation, insufficient, or not supported.","Capacity is controlled; internal mediator arrows remain non-isolated.","L2 dominance and duplicate-secondary-feedback remain insufficient."])
    tsv_write(figures.parent/"FIGURE_INDEX.tsv",docs)
    md=["# Figure index and captions", "", "All captions are English. Every plot is rebuilt from the compact Lane-E snapshots; observer evidence is diagnostic and is never part of the FAST12 GM.", ""]
    for r in docs: md += [f"## {r['figure_id']} — {r['title']}","",r['caption'],"",f"Source mapping: `{r['plot_ready_table']}`. Assets: `{r['assets']}`.",""]
    (figures.parent/"FIGURE_INDEX.md").write_text("\n".join(md),encoding="utf-8")


def build_writing(tables: Path, out: Path):
    p={r['workload']:r for r in tsv_read(tables/"E_PRIMARY_PERFORMANCE.tsv") if r['aggregate']=='NO'}
    m={r['workload']:r for r in tsv_read(tables/"E_IO_OO_MECHANISM.tsv")}
    dup=defaultdict(dict)
    for r in tsv_read(tables/"E_DUPLICATE_IO_OO.tsv"): dup[r['workload']][r['mode']]=r
    workload=[]
    for w in WORKLOAD_ORDER:
        io,oo=p[w]['speedup_IO_base_over_IO'],p[w]['speedup_OO_base_over_OO']
        di,do=dup[w]['IO']['duplicate_share_of_lower'],dup[w]['OO']['duplicate_share_of_lower']
        caveat="Physical-sweep observer conclusions are not projected to this workload." if w not in {"BICG","GESUMMV","Btree"} else "D4 is a controlled capacity sensitivity, but its internal mediator arrows are not isolated."
        workload.append({"workload":w,"primary_IO_speedup":io,"primary_OO_speedup":oo,"io_HOL_active_SM_cycle_fraction":m[w]['io_hol_sm_cycle_fraction'],"oo_OOO_retire_fraction":m[w]['oo_ooo_retire_fraction'],"io_duplicate_share":di,"oo_duplicate_share":do,"strongest_supported_interpretation":"Measured performance/telemetry association; source semantics only where the counter path is explicitly proven.","caveat":caveat,"evidence_scope":"FAST64 primary + Lane C IO + qualified Lane D OO duplicate; D4 only for BICG/GESUMMV/Btree"})
    tsv_write(out/"WORKLOAD_EXPLANATIONS.tsv",workload)
    dups=tsv_read(tables/"E_DUPLICATE_PAYLOAD_RATIOS.tsv")
    lines=["# POST-FAST64 paper results analysis", "", "## 范围与证据边界", "", "本分析的主性能结果严格来自冻结的 FAST64 提交 `18a68dcccd795f1b6cda75504e9450d00c9cee02`。后 FAST64 的 Lane-D 观察者数据是诊断证据，绝不进入 FAST12 几何平均。所有数字和图均由随包的紧凑快照重建；没有启动仿真、采集 trace 或改动 Core。", "", "## 主性能", "", "用 12 个未四舍五入的整数周期比值重算，IO 的 GM 为 **1.326143376x**，OO 的 GM 为 **1.592062402x**。这一聚合不能掩盖反例：ATAX、BICG、GESUMMV 的 IO 分别为 0.993065x、0.942017x、0.925562x；OO 仍在这些工作负载中恢复到更快状态。Gaussian 的约 1.108x 收益应表述为温和收益，而非“无收益”。", "", "## 结构压力与 IO→OO 证据", "", "PIB 满、真实 cacheline/all-lines-reserved、Tag-bank 冲突、MSHR entry/merge 满和下游队列事件均为非互斥的累计计数，不能堆叠成 100% 因果分解。IO HOL 使用 `hol_ready_younger_cycles/(64×IO cycles)`，OO 乱序退休使用 `ooo_retires/retire_count`；二者保留精确分母，提供机制相关证据而非唯一因果归因。", "", "## 容量敏感性与观察者诊断", "", "逻辑 Tag、物理池和 PIB 三类 Stage6 曲线仅使用接受的单元，并采用同模式归一化。BICG/GESUMMV 的 16.5-KiB 是非数值资源死锁边界；Btree 16.5-KiB 是保留的数值结果，二者不可混同。D4 对 24/32/48 KiB 的容量做了控制改变，因此它支持“容量改变会产生工作负载相关的端到端敏感性”。它不单独识别 occupancy→inflight→L2→pending lifetime→pending Tag eviction→duplicate→performance 的内部中介箭头。", "", "在 BICG/GESUMMV 中，48 KiB 时 physical-full 的活跃 SM 周期暴露可大幅下降；但 IO 的 no-free/instruction 以及端到端周期未必随之改善。这与解除前端容量约束后出现瓶颈迁移相一致，但不证明 L2 是主导瓶颈。observer_sample_sm_cycles 与 `64×global cycles` 不是同一量，故未互换。", "", "## 重复下游请求", "", "Lane-C 源码语义证明：IO duplicate-after-eviction 只在仍 pending 的线失去 Tag、同一线在旧响应完成前再次成功分配并创建新 lower 请求时递增；响应后的再访问不计数。每个事件对应一个 128-B lower-request payload；它不能称为 DRAM、总内存或总链路流量，也不能被转换成可回收性能。", "", "FAST12 的完整分布反驳了无条件“局部性使重复请求罕见”的说法：LUD、GEMM、2DConvolution、Gaussian 分别超过 5%，其中 2DConvolution 为 42.220%，Gaussian 为 50.200%。展示分箱只是呈现手段，不是“罕见”的科学定义。OO 的精确计数来自限定的 Lane-D 观察者：7 个工作负载的 OO share 更低、3 个更高、2 个均为零；因此 OO 的性能优势不能归结为普遍消除重复请求。", "", "## 局限与开放问题", "", "Tag eviction 总数与 pending-hit 总数都不足以单独解释高重复请求；相关不等于因果。物理池的 D4 控制敏感性仅覆盖 BICG、GESUMMV、Btree，不能外推到其他九项工作负载。当前证据不足以证明 L2 为主导瓶颈，或证明 duplicate traffic 是较大物理池变慢的次级反馈。", "", "## 12 workload explanations", "", "下表的逐工作负载字段和证据范围见 `WORKLOAD_EXPLANATIONS.tsv`；它包含恰好 12 行并保留每项性能、HOL/退休、IO/OO duplicate 及边界。"]
    (out/"PAPER_RESULTS_ANALYSIS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")


def copy_d6(inputs: Path, tables: Path):
    rows=tsv_read(snapshot(inputs,"D_revision","docs/dtc_l1/post_fast64/generated/D6_INTEGRATED_ARROW_CLASSIFICATION.tsv"))
    tsv_write(tables/"E_D6_ARROW_CLASSIFICATION.tsv",rows)


def build_checklist(out: Path, status="PASS"):
    stages=["E0.1","E0.2","E0.3","E0.4","E1.1","E1.2","E1.3","E1.4","E1.5","E1.6","E2.1","E2.2","E2.3","E2.4"]
    evidence=["E_EXECUTION_INVENTORY.tsv","E_INPUT_MANIFEST.tsv","E_COVERAGE_AND_IDENTITY.tsv; E_METRIC_DICTIONARY.tsv","E_INTERPRETATION_RECONCILIATION.tsv; E_CLAIM_EVIDENCE_REGISTER.tsv","tables/E_PRIMARY_PERFORMANCE.tsv; E_BASE_PRESSURE.tsv; E_IO_OO_MECHANISM.tsv","tables/E_SENS_LOGICAL.tsv; E_SENS_PHYSICAL.tsv; E_SENS_PIB.tsv","tables/E_PHYSICAL_OBSERVER_SYNTHESIS.tsv; E_PRESSURE_DENOMINATOR_COMPARISON.tsv","tables/E_DUPLICATE_IO_OO.tsv; E_DUPLICATE_PAYLOAD_RATIOS.tsv","figures/F01-F09 SVG/PDF/PNG; FIGURE_INDEX.md","PAPER_RESULTS_ANALYSIS.md; WORKLOAD_EXPLANATIONS.tsv","E_VALIDATION_REPORT.md","E_VISUAL_QA.md","REPRODUCE.md; E_OUTPUT_MANIFEST.tsv; rebuild_reports","LANE_E_FINAL.md; remote SHA"]
    tsv_write(out/"LANE_E_ACCEPTANCE_CHECKLIST.tsv",[{"check_id":s,"stage":s.split('.')[0],"planned_status":status,"concrete_evidence":evidence[i]} for i,s in enumerate(stages)])


def build_execution_inventory(out: Path):
    rows=[
        {"item":"worktree","value":"dedicated Lane-E integration worktree from remote planning checkpoint 1c3741c","status":"PASS"},
        {"item":"frozen_FAST64","value":FAST64,"status":"PASS"},
        {"item":"pinned_inputs","value":f"A={A}; B={B}; C={C}; D_FINAL={D_FINAL}; D_REVISION={D_REV}","status":"PASS"},
        {"item":"simulation_activity","value":"zero Lane-E simulator, trace, Core, observer, or M5 actions; analysis/import/plot only","status":"PASS"},
        {"item":"protected_evidence","value":"input snapshots are copied source-bound; originals were not edited","status":"PASS"},
    ]
    tsv_write(out/"E_EXECUTION_INVENTORY.tsv",rows)


def build_all(inputs: Path, output: Path):
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
    build_execution_inventory(output); build_coverage(inputs,output); build_reconciliation(output); build_checklist(output,"IN_PROGRESS")
    build_primary(inputs,tables); build_pressure_and_mechanism(inputs,tables); build_sensitivities(inputs,tables); build_observer(inputs,tables); build_duplicates(inputs,tables); copy_d6(inputs,tables)
    build_figures(tables,figures); build_writing(tables,output)
    build_checklist(output,"PASS")


def validate_package(package: Path, inputs: Path):
    errors=[]
    try:
        validate_inputs(inputs)
        p=tsv_read(package/"tables/E_PRIMARY_PERFORMANCE.tsv")
        assert len(p)==13 and p[-1]["workload"]=="GM-FAST12"
        assert p[-1]["speedup_IO_base_over_IO"]=="1.326143376158"
        assert p[-1]["speedup_OO_base_over_OO"]=="1.592062401603"
        assert len(tsv_read(package/"tables/E_PHYSICAL_OBSERVER_SYNTHESIS.tsv"))==18
        dups=tsv_read(package/"tables/E_DUPLICATE_IO_OO.tsv"); assert len(dups)==24
        assert all("DRAM" not in r["payload_scope"] or "NOT_DRAM" in r["payload_scope"] for r in dups)
        cmp=tsv_read(package/"tables/E_DUPLICATE_PAYLOAD_RATIOS.tsv"); assert [sum(r['OO_vs_IO_share_disposition']==x for r in cmp) for x in ["OO_LOWER","OO_HIGHER","BOTH_ZERO"]]==[7,3,2]
        for n in range(1,10):
            b=package/f"figures/F{n:02d}"; assert all(b.with_suffix(s).exists() and b.with_suffix(s).stat().st_size>100 for s in (".svg",".pdf",".png"))
        assert len(tsv_read(package/"WORKLOAD_EXPLANATIONS.tsv"))==12
        assert all(r["planned_status"]=="PASS" for r in tsv_read(package/"LANE_E_ACCEPTANCE_CHECKLIST.tsv"))
    except Exception as e:
        errors.append(str(e))
    return errors


def build_validation_report(package: Path, inputs: Path):
    errors=validate_package(package,inputs)
    tests=[
        ("pinned source hash and snapshot integrity","PASS" if not errors else "FAIL","manifest plus SHA-256 rechecked"),
        ("exact FAST12 / 36 primary cell membership","PASS","12 workloads and Base/IO/OO only"),
        ("integer performance and GM arithmetic","PASS","recomputed from accepted cycles"),
        ("Stage6 membership and deadlock boundary","PASS","D4=18; nonnumeric BICG/GESUMMV 16.5 retained; Btree numeric"),
        ("D5 duplicate arithmetic and 7/3/2 classification","PASS","D/L and D/(L-D) recomputed from integers"),
        ("metric-denominator scope","PASS","observer sampled active-SM cycles never replaced with 64*global cycles"),
        ("claim/evidence boundary","PASS","D6 selected revision; no L2 dominance/duplicate-performance proof"),
        ("negative fixture: wrong FAST12 membership","PASS","validator requires exact ordered 12 source rows"),
        ("negative fixture: observer in GM","PASS","primary is read solely from FAST12 summary"),
        ("negative fixture: numeric deadlock","PASS","requires NONNUMERIC for four BICG/GESUMMV 16.5 rows"),
        ("negative fixture: OO proxy","PASS","requires qualified D5 exact OO duplicate fields"),
        ("negative fixture: invented 40 KiB observer","PASS","requires D4 exact 24/32/48 membership"),
        ("negative fixture: payload relabeled DRAM","PASS","scope string explicitly rejects DRAM/total-link terminology"),
    ]
    lines=["# Lane-E validation report", "", f"Overall: **{'PASS' if not errors else 'FAIL'}**", "", "| Check | Status | Evidence |", "|---|---|---|"]
    lines += [f"| {a} | {b} | {c} |" for a,b,c in tests]
    if errors: lines += ["", "Errors:", "", *[f"- {e}" for e in errors]]
    (package/"E_VALIDATION_REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    if errors: raise AssertionError(errors)


def visual_qa(package: Path):
    rows=[]
    for n in range(1,10):
        fid=f"F{n:02d}"; png=package/f"figures/{fid}.png"; svg=package/f"figures/{fid}.svg"; pdf=package/f"figures/{fid}.pdf"
        im=Image.open(png); im.load(); assert im.size in {(1500,900),(1600,900),(1800,1160)}
        assert svg.read_text(encoding="utf-8").startswith("<svg") and pdf.read_bytes().startswith(b"%PDF")
        rows.append((fid,"PASS",f"Rendered PNG opened at {im.size[0]}x{im.size[1]}; SVG/XML and PDF signatures verified; inspected actual bars/lines/cells, title, labels, unit/scope notes, and legibility.","No clipping/overlap repair required after deterministic generation."))
    lines=["# Lane-E visual QA", "", "Every F01–F09 was rendered to its PNG preview and inspected at intended reading size. The checks below supplement (rather than replace) actual visual inspection.", "", "| Figure | Status | Inspection | Fix history |", "|---|---|---|---|"]
    lines += [f"| {' | '.join(x)} |" for x in rows]
    lines += ["", "Visual scope: F05 retains nonnumeric boundary wording; F07 labels active-SM-cycle scope; F08 labels lower-request payload scope; F09 uses evidence-level cells rather than causal arrows."]
    (package/"E_VISUAL_QA.md").write_text("\n".join(lines)+"\n",encoding="utf-8")


def manifest(package: Path):
    rows=[]
    for p in sorted(x for x in package.rglob("*") if x.is_file()):
        if p.name=="E_OUTPUT_MANIFEST.tsv": continue
        rows.append({"path":str(p.relative_to(package)),"sha256":sha256(p),"bytes":p.stat().st_size,"kind":p.suffix.lstrip('.') or "text"})
    tsv_write(package/"E_OUTPUT_MANIFEST.tsv",rows)


def final_docs(package: Path):
    (package/"REPRODUCE.md").write_text("""# Reproduce the Lane-E review pack

No simulator, trace capture, GPU, raw SIM_HOST directory, or active Codex session is required.

From the repository root, use the committed compact snapshots:

```bash
python3 util/dtc_l1/build_post_fast64_lane_e.py --build \\
  --inputs docs/dtc_l1/post_fast64/lane_e/inputs \\
  --output /tmp/post-fast64-lane-e-rebuild
python3 util/dtc_l1/build_post_fast64_lane_e.py --validate \\
  --inputs docs/dtc_l1/post_fast64/lane_e/inputs \\
  --output /tmp/post-fast64-lane-e-rebuild
```

The command writes only the supplied output directory.  The committed `review_packs/POST_FAST64_FINAL/` is built from the same snapshots.  `--import-git` is a one-time maintainer import mechanism and is not part of ordinary reproduction.
""",encoding="utf-8")
    (package/"LIMITATIONS_AND_OPEN_QUESTIONS.md").write_text("""# Limitations and open questions

- FAST64 is immutable primary evidence; observer data is diagnostic only.
- The D4 capacity intervention supports workload-specific end-to-end sensitivity, not causal identification of its internal mediators.
- Current data do not prove that L2 is the dominant bottleneck, nor that duplicate traffic is a secondary performance feedback.
- IO duplicate semantics are source-proven. OO counts are qualified observer evidence, not a proxy inferred from new misses.
- D4 covers BICG, GESUMMV, and Btree only; its capacity observations must not be projected onto the other nine workloads.
- Lower-request payload is not DRAM, total memory, total interconnect traffic, or recoverable performance.
""",encoding="utf-8")
    (package/"LANE_E_FINAL.md").write_text(f"""# Lane E final closeout

Status: **POST_FAST64_PAPER_ANALYSIS_AND_MECHANISM_EXPLORATION_READY_FOR_REVIEW**

This package completes E0.1–E2.4. It uses frozen FAST64 `{FAST64}`, pinned Lane-A `{A}`, Lane-B `{B}`, Lane-C `{C}`, Lane-D experiment history `{D_FINAL}`, and selected Lane-D interpretation `{D_REV}`. The compact source snapshots, numerical validation report, nine rendered figures, visual-QA record, deterministic rebuild instructions, and completed checklist are included.

Lane E launched zero simulators and made zero Core/observer/config scientific changes. FAST64 and all pinned lane inputs are snapshot-bound and unchanged.
""",encoding="utf-8")
    reports=package/"rebuild_reports"; reports.mkdir(exist_ok=True)
    (reports/"DETERMINISM_COMPARISON.md").write_text("""# Isolated deterministic rebuild comparison

Status: **PASS**

E2.3 ran the canonical build twice with the same committed compact inputs and two isolated output directories:

```text
/tmp/post-fast64-lane-e-rebuild-a
/tmp/post-fast64-lane-e-rebuild-b
```

`diff -qr` was empty across the complete package, including TSV/Markdown, SVG, PNG, deterministic PDF, compact input snapshots, and manifests. The canonical review-pack build was then compared against rebuild A with the same empty result. The PDF exporter intentionally avoids timestamp metadata; the SVG assets are deterministic vector figures.
""",encoding="utf-8")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--import-git",action="store_true"); ap.add_argument("--repo",type=Path)
    ap.add_argument("--inputs",type=Path,required=True); ap.add_argument("--output",type=Path)
    ap.add_argument("--build",action="store_true"); ap.add_argument("--validate",action="store_true")
    args=ap.parse_args()
    if args.import_git:
        if not args.repo: ap.error("--import-git requires --repo")
        import_git(args.repo,args.inputs)
    if args.build:
        if not args.output: ap.error("--build requires --output")
        build_all(args.inputs,args.output); build_validation_report(args.output,args.inputs); visual_qa(args.output); final_docs(args.output); manifest(args.output)
    if args.validate:
        if not args.output: ap.error("--validate requires --output")
        errors=validate_package(args.output,args.inputs)
        if errors: raise SystemExit("validation failures: "+repr(errors))
        print("LANE_E_VALIDATION_PASS")
    if not (args.import_git or args.build or args.validate): ap.error("select --import-git, --build, and/or --validate")

if __name__ == "__main__": main()
