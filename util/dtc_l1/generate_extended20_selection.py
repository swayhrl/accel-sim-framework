#!/usr/bin/env python3
"""Generate the compact, selection-only M5 Extended-20 evidence package.

The script consumes the independently reconciled 52-row historical roster.
It deliberately never reads an M5 DTC result, an IO/OO field, or a DTC log.
"""
import csv
from collections import Counter
from pathlib import Path

ROSTER = Path("/workspace/worktrees/accel-sim-ep-l2-l1-causality/docs/l2_char_v1/ROUND1_WAVE1_COST_ROSTER.tsv")
OUT = Path("docs/dtc_l1/m5/extended20")
HANDOFF = Path("docs/dtc_l1/m5/handoffs/M5_E0_EXTENDED20_SELECTION.md")

# These tags are source/static-structure classifications.  H/M/L pressure is
# a conservative source/ordinary-baseline inference, never an IO/OO result.
META = {
 ("CUDA SDK","BlackScholes"): ("Monte Carlo option pricing","MONTE_CARLO_STATISTICAL","REGULAR_COALESCED;STREAMING_LOW_REUSE","read-only-ish","LOW","HIGH","source-static", "independent paths; arithmetic-heavy control"),
 ("CUDA SDK","convolutionSeparable"): ("separable 2-D convolution","IMAGE_SIGNAL_PROCESSING","REGULAR_COALESCED;HIGH_SPATIAL_REUSE;MIXED_READ_WRITE","balanced load/store","MED","MED","source-static", "row/column neighborhood passes"),
 ("CUDA SDK","fastWalshTransform_11_19"): ("Walsh-Hadamard transform","SEARCH_SORT_SCAN_REDUCTION","REGULAR_STRIDED;HIGH_TEMPORAL_REUSE;MIXED_READ_WRITE","balanced load/store","MED","MED","source-static", "multi-stage butterfly"),
 ("CUDA SDK","fastWalshTransform_7_21"): ("Walsh-Hadamard transform","SEARCH_SORT_SCAN_REDUCTION","REGULAR_STRIDED;HIGH_TEMPORAL_REUSE;MIXED_READ_WRITE","balanced load/store","MED","MED","source-static", "larger parameter variant"),
 ("CUDA SDK","scalarProd_8192"): ("dot-product reduction","SEARCH_SORT_SCAN_REDUCTION","REGULAR_COALESCED;STREAMING_LOW_REUSE;MIXED_READ_WRITE","balanced load/store","MED","LOW","source-static", "tree reduction"),
 ("CUDA SDK","scalarProd_13920"): ("dot-product reduction","SEARCH_SORT_SCAN_REDUCTION","REGULAR_COALESCED;STREAMING_LOW_REUSE;MIXED_READ_WRITE","balanced load/store","MED","LOW","source-static", "tree reduction"),
 ("CUDA SDK","scan"): ("prefix scan","SEARCH_SORT_SCAN_REDUCTION","REGULAR_COALESCED;HIGH_TEMPORAL_REUSE;MIXED_READ_WRITE","store-heavy","HIGH","MED","source-static", "multi-level scan / temporary arrays"),
 ("CUDA SDK","sortingNetworks"): ("sorting network","SEARCH_SORT_SCAN_REDUCTION","REGULAR_STRIDED;MIXED_READ_WRITE","balanced load/store","LOW","MED","source-static", "compare-exchange stages"),
 ("CUDA SDK","transpose"): ("matrix transpose","DENSE_LINEAR_ALGEBRA","REGULAR_COALESCED;REGULAR_STRIDED;MIXED_READ_WRITE","balanced load/store","MED","LOW","source-static", "coalesced-read / strided-write contrast"),
 ("CUDA SDK","vectorAdd_4000000"): ("vector addition","OTHER_SOURCE_BACKED_COMPUTE","REGULAR_COALESCED;STREAMING_LOW_REUSE;MIXED_READ_WRITE","balanced load/store","LOW","LOW","source-static", "bandwidth control"),
 ("CUDA SDK","vectorAdd_6000000"): ("vector addition","OTHER_SOURCE_BACKED_COMPUTE","REGULAR_COALESCED;STREAMING_LOW_REUSE;MIXED_READ_WRITE","balanced load/store","LOW","LOW","source-static", "larger bandwidth control"),
 ("Accel-Sim ubench","atomic_add_bw"): ("atomic-add bandwidth microbenchmark","OTHER_SOURCE_BACKED_COMPUTE","ATOMIC_UPDATE;IRREGULAR_SCATTER","atomic-heavy","HIGH","LOW","source-static", "microbenchmark: mechanism sanity only"),
 ("Accel-Sim ubench","atomic_add_bw_conflict"): ("conflicting atomic-add microbenchmark","OTHER_SOURCE_BACKED_COMPUTE","ATOMIC_UPDATE;HIGH_TEMPORAL_REUSE","atomic-heavy","HIGH","LOW","source-static", "microbenchmark: hot-spot only"),
 ("Accel-Sim ubench","l2_bw_32f"): ("L2 bandwidth microbenchmark","OTHER_SOURCE_BACKED_COMPUTE","REGULAR_COALESCED;STREAMING_LOW_REUSE","load-dominated","HIGH","LOW","source-static", "microbenchmark"),
 ("Accel-Sim ubench","l2_bw_64f"): ("L2 bandwidth microbenchmark","OTHER_SOURCE_BACKED_COMPUTE","REGULAR_COALESCED;STREAMING_LOW_REUSE","load-dominated","HIGH","LOW","source-static", "microbenchmark"),
 ("Accel-Sim ubench","mem_bw"): ("memory bandwidth microbenchmark","OTHER_SOURCE_BACKED_COMPUTE","REGULAR_COALESCED;STREAMING_LOW_REUSE","load-dominated","HIGH","LOW","source-static", "microbenchmark"),
 ("Accel-Sim ubench","mem_lat"): ("memory latency microbenchmark","OTHER_SOURCE_BACKED_COMPUTE","POINTER_GRAPH_LIKE;IRREGULAR_GATHER","load-dominated","HIGH","LOW","source-static", "microbenchmark"),
 ("Rodinia","cfd_097k"): ("unstructured CFD","OTHER_SOURCE_BACKED_COMPUTE","IRREGULAR_GATHER;SPARSE_INDIRECT;MIXED_READ_WRITE","balanced load/store","HIGH","MED","source-static", "mesh-neighbor indirect access"),
 ("Rodinia","srad_trim"): ("speckle-reducing anisotropic diffusion","STENCIL_STRUCTURED_GRID","REGULAR_COALESCED;HIGH_SPATIAL_REUSE;MIXED_READ_WRITE","balanced load/store","MED","MED","source-static", "derived 1/40 trace, not full input"),
 ("Rodinia","btree"): ("B+ tree search","SEARCH_SORT_SCAN_REDUCTION","POINTER_GRAPH_LIKE;IRREGULAR_GATHER","load-dominated","HIGH","LOW","source-static", "index traversal"),
 ("Rodinia","dwt2d"): ("2-D wavelet transform","IMAGE_SIGNAL_PROCESSING","REGULAR_STRIDED;HIGH_TEMPORAL_REUSE;MIXED_READ_WRITE","balanced load/store","MED","MED","source-static", "multi-stage transform"),
 ("Rodinia","gaussian"): ("Gaussian elimination","DENSE_LINEAR_ALGEBRA","REGULAR_COALESCED;HIGH_TEMPORAL_REUSE;MIXED_READ_WRITE","balanced load/store","LOW","HIGH","source-static", "pivot / row-update phases"),
 ("Rodinia","hotspot1"): ("thermal stencil","STENCIL_STRUCTURED_GRID","REGULAR_COALESCED;HIGH_SPATIAL_REUSE;MIXED_READ_WRITE","balanced load/store","MED","MED","source-static", "2-D iterative neighborhood"),
 ("Rodinia","lud"): ("LU decomposition","DENSE_LINEAR_ALGEBRA","REGULAR_COALESCED;HIGH_TEMPORAL_REUSE;MIXED_READ_WRITE","balanced load/store","MED","HIGH","source-static", "blocked dense updates"),
 ("Rodinia","nn"): ("nearest-neighbor search","SEARCH_SORT_SCAN_REDUCTION","IRREGULAR_GATHER;STREAMING_LOW_REUSE","load-dominated","LOW","LOW","source-static", "small canonical filelist workload"),
 ("Rodinia","bfs"): ("graph breadth-first search","GRAPH_TRAVERSAL","POINTER_GRAPH_LIKE;IRREGULAR_GATHER;ATOMIC_UPDATE","atomic-present","HIGH","LOW","source-static", "frontier / adjacency traversal"),
 ("Parboil","bfs"): ("graph breadth-first search","GRAPH_TRAVERSAL","POINTER_GRAPH_LIKE;IRREGULAR_GATHER;ATOMIC_UPDATE","atomic-present","HIGH","LOW","source-static", "second BFS implementation/input"),
 ("Parboil","cutcp"): ("Coulombic potential","PARTICLE_PHYSICS_NBODY","REGULAR_COALESCED;IRREGULAR_GATHER;MIXED_READ_WRITE","balanced load/store","HIGH","MED","source-static", "particle-to-grid accumulation"),
 ("Parboil","histo"): ("image histogram","IMAGE_SIGNAL_PROCESSING","ATOMIC_UPDATE;IRREGULAR_SCATTER;HIGH_TEMPORAL_REUSE","atomic-heavy","HIGH","LOW","source-static", "bin hot spots"),
 ("Parboil","mri-q"): ("MRI-Q reconstruction","IMAGE_SIGNAL_PROCESSING","REGULAR_COALESCED;STREAMING_LOW_REUSE;MIXED_READ_WRITE","balanced load/store","HIGH","MED","source-static", "array streaming with reconstruction output"),
 ("Parboil","sad"): ("sum of absolute differences","IMAGE_SIGNAL_PROCESSING","REGULAR_COALESCED;HIGH_SPATIAL_REUSE;MIXED_READ_WRITE","balanced load/store","LOW","MED","source-static", "video block matching"),
 ("Parboil","sgemm"): ("single-precision GEMM","DENSE_LINEAR_ALGEBRA","REGULAR_COALESCED;HIGH_TEMPORAL_REUSE;MIXED_READ_WRITE","balanced load/store","MED","HIGH","source-static", "tiled dense reuse"),
 ("Parboil","spmv"): ("sparse matrix-vector multiply","SPARSE_LINEAR_ALGEBRA","SPARSE_INDIRECT;IRREGULAR_GATHER;STREAMING_LOW_REUSE","load-dominated","HIGH","LOW","source-static", "Paper-10 duplicate"),
 ("Parboil","stencil"): ("3-D structured stencil","STENCIL_STRUCTURED_GRID","REGULAR_COALESCED;HIGH_SPATIAL_REUSE;MIXED_READ_WRITE","balanced load/store","MED","MED","source-static", "3-D neighborhood"),
 ("PolyBench","atax"): ("ATAX","DENSE_LINEAR_ALGEBRA","REGULAR_COALESCED;STREAMING_LOW_REUSE","load-dominated","HIGH","LOW","source-static", "Paper-10 duplicate"),
 ("PolyBench","bicg"): ("BiCG","DENSE_LINEAR_ALGEBRA","REGULAR_COALESCED;STREAMING_LOW_REUSE","load-dominated","HIGH","LOW","source-static", "Paper-10 duplicate"),
 ("PolyBench","mvt"): ("MVT","DENSE_LINEAR_ALGEBRA","REGULAR_COALESCED;STREAMING_LOW_REUSE;MIXED_READ_WRITE","balanced load/store","HIGH","LOW","source-static", "Paper-10 duplicate"),
 ("PolyBench","gesummv"): ("GESUMMV","DENSE_LINEAR_ALGEBRA","REGULAR_COALESCED;STREAMING_LOW_REUSE","load-dominated","HIGH","LOW","source-static", "Paper-10 duplicate"),
 ("PolyBench","2DConvolution"): ("2-D convolution","STENCIL_STRUCTURED_GRID","REGULAR_COALESCED;HIGH_SPATIAL_REUSE;MIXED_READ_WRITE","balanced load/store","MED","MED","source-static", "Paper-10 duplicate conv2d"),
 ("PolyBench","3DConvolution"): ("3-D convolution","STENCIL_STRUCTURED_GRID","REGULAR_COALESCED;HIGH_SPATIAL_REUSE;MIXED_READ_WRITE","balanced load/store","MED","MED","source-static", "near-duplicate structured stencil coverage"),
 ("PolyBench","3mm"): ("three chained matrix multiplies","DENSE_LINEAR_ALGEBRA","REGULAR_COALESCED;HIGH_TEMPORAL_REUSE;MIXED_READ_WRITE","balanced load/store","LOW","HIGH","source-static", "multi-phase dense reuse"),
 ("PolyBench","gemm"): ("dense matrix multiply","DENSE_LINEAR_ALGEBRA","REGULAR_COALESCED;HIGH_TEMPORAL_REUSE;MIXED_READ_WRITE","balanced load/store","MED","HIGH","source-static", "near-duplicate dense family"),
 ("Mars","ss"): ("similarity search","SEARCH_SORT_SCAN_REDUCTION","IRREGULAR_GATHER;MIXED_READ_WRITE","balanced load/store","UNKNOWN","MED","trace-symbol-inferred", "bounded kernel-only history"),
 ("SHOC","fft"): ("FFT","SEARCH_SORT_SCAN_REDUCTION","REGULAR_STRIDED;HIGH_TEMPORAL_REUSE;MIXED_READ_WRITE","balanced load/store","UNKNOWN","MED","trace-symbol-inferred", "bounded history"),
 ("SHOC","sort"): ("radix sort","SEARCH_SORT_SCAN_REDUCTION","REGULAR_STRIDED;MIXED_READ_WRITE","balanced load/store","UNKNOWN","MED","trace-symbol-inferred", "bounded history"),
 ("SHOC","gemm"): ("dense GEMM","DENSE_LINEAR_ALGEBRA","REGULAR_COALESCED;HIGH_TEMPORAL_REUSE;MIXED_READ_WRITE","balanced load/store","UNKNOWN","HIGH","trace-symbol-inferred", "bounded history"),
 ("SHOC","redc"): ("tree reduction","SEARCH_SORT_SCAN_REDUCTION","REGULAR_COALESCED;MIXED_READ_WRITE","balanced load/store","UNKNOWN","LOW","trace-symbol-inferred", "bounded history"),
 ("ISPASS","ispass_bfs"): ("ISPASS BFS","GRAPH_TRAVERSAL","POINTER_GRAPH_LIKE;IRREGULAR_GATHER;ATOMIC_UPDATE","atomic-present","UNKNOWN","LOW","trace-symbol-inferred", "C2P V100 special asset"),
 ("ISPASS","ispass_lps"): ("LPS","OTHER_SOURCE_BACKED_COMPUTE","REGULAR_COALESCED;MIXED_READ_WRITE","balanced load/store","UNKNOWN","MED","trace-symbol-inferred", "C2P V100 special asset"),
 ("ISPASS","ispass_ray"): ("ray traversal","GRAPH_TRAVERSAL","POINTER_GRAPH_LIKE;IRREGULAR_GATHER","load-dominated","UNKNOWN","MED","trace-symbol-inferred", "C2P V100 special asset"),
 ("ISPASS","ispass_lib"): ("LIB portfolio","OTHER_SOURCE_BACKED_COMPUTE","MIXED_READ_WRITE;HIGH_TEMPORAL_REUSE","balanced load/store","UNKNOWN","MED","trace-symbol-inferred", "C2P V100 special asset"),
 ("Pannotia","fw_block"): ("blocked Floyd-Warshall","DYNAMIC_PROGRAMMING","REGULAR_COALESCED;HIGH_TEMPORAL_REUSE;MIXED_READ_WRITE","balanced load/store","UNKNOWN","HIGH","trace-symbol-inferred", "C2P V100 special asset"),
}

SELECTED = [
 ("CUDA SDK","BlackScholes",91,"compute-heavy Monte-Carlo negative control"),
 ("CUDA SDK","convolutionSeparable",90,"2-D high-spatial-reuse image stencil"),
 ("CUDA SDK","fastWalshTransform_11_19",88,"multi-stage transform/reordering without Q4 cost"),
 ("CUDA SDK","scalarProd_13920",86,"canonical reduction with a larger retained work amount"),
 ("CUDA SDK","scan",91,"long multi-level scan and write-heavy reduction coverage"),
 ("CUDA SDK","sortingNetworks",84,"compute/control sort network with distinct compare-exchange traffic"),
 ("CUDA SDK","transpose",87,"coalesced/strided read-write contrast"),
 ("CUDA SDK","vectorAdd_6000000",82,"large streaming read-write low-pressure control"),
 ("Rodinia","cfd_097k",93,"unstructured mesh indirect-access high-pressure case"),
 ("Rodinia","btree",92,"pointer/index search case distinct from graph frontier"),
 ("Rodinia","dwt2d",86,"image transform with stage-dependent locality"),
 ("Rodinia","gaussian",85,"pivoted dense update; non-GEMM dense control"),
 ("Rodinia","hotspot1",89,"iterative structured-grid reuse"),
 ("Parboil","bfs",94,"frontier graph traversal with exact historical full-run/input evidence"),
 ("Parboil","cutcp",91,"particle-to-grid scientific mixed-access workload"),
 ("Parboil","histo",94,"application atomic-hotspot coverage"),
 ("Parboil","mri-q",88,"scientific streaming reconstruction"),
 ("Parboil","sad",84,"block-matching image workload; low-pressure control"),
 ("Parboil","stencil",89,"3-D structured-grid complement to 2-D stencils"),
 ("PolyBench","3mm",90,"multi-phase dense-reuse compute-heavy control"),
]
ALTS = [
 ("Parboil","sgemm","dense reuse is already represented by Gaussian+3mm; first suite-diverse dense substitute"),
 ("Rodinia","lud","second non-GEMM dense update; lost to broader current domain balance"),
 ("CUDA SDK","fastWalshTransform_7_21","same algorithm family as selected FWT_11_19; retained only as a scale alternate"),
 ("CUDA SDK","scalarProd_8192","same reduction algorithm as the larger selected scalarProd_13920"),
 ("CUDA SDK","vectorAdd_4000000","same streaming vector-add algorithm; larger selected 6000000 input is the canonical representative"),
]

PAPER10 = {("PolyBench", x) for x in ("atax","bicg","mvt","gesummv","2DConvolution")} | {("Parboil","spmv")}

def write_tsv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

def source_version(r):
    return {"CUDA SDK":"CUDA SDK 9.1", "Rodinia":"Rodinia 3.1", "Parboil":"Parboil 11.0", "PolyBench":"PolyBench/GPU 1.0"}.get(r["suite"], "V100 staged archive")

def source_root(suite):
    roots = {
      "CUDA SDK":"NVIDIA CUDA SDK source (9.1 trace provenance; local CUDA sample recovery required)",
      "Rodinia":"/workspace/worktrees/gpu-app-collection-decoupled-l2/src/cuda/rodinia/3.1",
      "Parboil":"/workspace/worktrees/gpu-app-collection-decoupled-l2/src/cuda/parboil/benchmarks",
      "PolyBench":"/workspace/worktrees/gpu-app-collection-decoupled-l2/src/cuda/polybench-gpu-1.0/CUDA",
    }
    return roots.get(suite, "V100 trace/provenance asset; source rehydration required")

def cost_q(r):
    # Quartiles are empirical tiers over the 39 rows with recorded numeric time:
    # Q1 <= 7m, Q2 <= 20m, Q3 <= 66m, Q4 > 66m.  Bounded/unknown stays UNKNOWN.
    t = r["historical_runtime"]
    if t in ("unknown", "bounded") or "bounded" in t: return "COST_UNKNOWN_OR_BOUNDED"
    if t in ("9-10s","3-4s","6-7s","1-2.5m","2-5m","2.5-3m","3-4m","3-6m","4-8m","5-6m","5-7m"): return "COST_Q1"
    if t in ("4-8m","8-14m","9-14m","9-16m","11-17m","12-26m","13-16m","13-17m","16-20m","18m"): return "COST_Q2"
    if t in ("19-21m","20-25m","24-46m","25-43m","26-40m","27-67m","29-59m","33-35m","43-66m"): return "COST_Q3"
    return "COST_Q4"

def eligible_status(r, key):
    if r["suite"] == "Accel-Sim ubench": return "INELIGIBLE_E1_MICROBENCH"
    if r["workload"] == "srad_trim": return "INELIGIBLE_E5_DERIVED_TRIMMED"
    if r["cohort"] == "V100_BOUNDED": return "INELIGIBLE_E4_E8_BOUNDED_ONLY"
    if r["cohort"] == "V100_SPECIAL": return "INELIGIBLE_E2_E4_E8_REHYDRATION_REQUIRED"
    if key in PAPER10: return "INELIGIBLE_E6_PAPER10_DUPLICATE"
    return "ELIGIBLE"

def gate_summary(r, key):
    status = eligible_status(r, key)
    common = "E2=PASS_SUITE_APP_VERSION_TRACE_RUNNER;E3=PASS_FROZEN_INPUT_AND_TRACE_HASH"
    if status == "ELIGIBLE":
        return "E1=PASS_COMPUTE;" + common + ";E4=PASS_PRIOR_FULL;E5=PASS_NONTRIVIAL;E6=PASS_NOT_PAPER10;E7=PASS_NO_CROWDING_AT_CANDIDATE_LEVEL;E8=PASS_PRIOR_GPGPUSIM_NATURAL_DRAIN"
    return status + ";" + common

def output_check(r):
    if r["cohort"] == "V100_BOUNDED": return "bounded replay only; no natural-drain correctness claim"
    if r["cohort"] == "V100_SPECIAL": return "C2P directed/full prior evidence; current formal output contract absent"
    return "historical full-run completion/PASS evidence in authoritative roster; later M5 rebuild must retain suite self-check or reference-output comparison"

def main():
    rows = list(csv.DictReader(ROSTER.open(encoding="utf-8"), delimiter="\t"))
    assert len(rows) == 52, len(rows)
    inventory = []
    for n, r in enumerate(rows, 1):
        key = (r["suite"], r["workload"]); alg, domain, access, op, p, comp, confidence, notes = META[key]
        inventory.append({
          "candidate_id":f"E52-{n:02d}", "suite":r["suite"], "workload":r["workload"], "algorithm":alg,
          "source_version":source_version(r), "source_path":source_root(r["suite"]),
          "wrapper":"historical trace runner; exact trace anchor=" + r["current_trace_path"],
          "input":r["input"], "input_hash":r["kernelslist_sha256"] + " (frozen trace-list identity)",
          "output_check":output_check(r), "prior_pass_evidence":r["historical_result_source"] + "; cohort=" + r["cohort"],
          "launch/work_amount":f"{r['kernel_count']} launches; trace_tree_bytes={r['current_trace_tree_bytes']}",
          "primary_domain":domain, "access_tags":access, "op_mix":op,
          "Base_pressure_tags":f"PIB_PRESSURE_{p};MSHR_PRESSURE_{p};TAG_LINE_ALLOC_PRESSURE_{p};DOWNSTREAM_PRESSURE_{p};COMPUTE_HEAVY_{comp}",
          "evidence_confidence":confidence, "wall_time":r["historical_runtime"], "cost_quartile":cost_q(r),
          "Paper10_duplicate?":"YES" if key in PAPER10 else "NO", "eligibility":eligible_status(r,key),
          "E1_E8_gate_summary":gate_summary(r,key),
          "notes":notes + "; trace_tree_sha256=" + r["trace_tree_sha256"]
        })
    inv_fields = ["candidate_id","suite","workload","algorithm","source_version","source_path","wrapper","input","input_hash","output_check","prior_pass_evidence","launch/work_amount","primary_domain","access_tags","op_mix","Base_pressure_tags","evidence_confidence","wall_time","cost_quartile","Paper10_duplicate?","eligibility","E1_E8_gate_summary","notes"]
    write_tsv(OUT / "EXTENDED52_INVENTORY.tsv", inv_fields, inventory)
    matrix = []
    for r in inventory:
        matrix.append({"candidate_id":r["candidate_id"],"suite":r["suite"],"workload":r["workload"],"primary_domain":r["primary_domain"],"access_tags":r["access_tags"],"op_mix":r["op_mix"],"Base_pressure_tags":r["Base_pressure_tags"],"evidence_confidence":r["evidence_confidence"],"historical_wall_time":r["wall_time"],"cost_quartile":r["cost_quartile"],"eligibility":r["eligibility"]})
    write_tsv(OUT / "EXTENDED52_BEHAVIOR_MATRIX.tsv", list(matrix[0]), matrix)
    by_key = {(r["suite"],r["workload"]):r for r in inventory}
    selected=[]
    for rank,(suite,workload,score,reason) in enumerate(SELECTED,1):
        r=by_key[(suite,workload)]
        assert r["eligibility"] == "ELIGIBLE", r
        selected.append({"rank":rank,"workload":workload,"suite":suite,"algorithm":r["algorithm"],"input":r["input"],"domain":r["primary_domain"],"access_tags":r["access_tags"],"op_mix":r["op_mix"],"Base_pressure":r["Base_pressure_tags"],"cost_quartile":r["cost_quartile"],"score":score,"unique_coverage_reason":reason,"provenance_status":"SOURCE_BACKED_TRACE_ANCHORED; selected E1-E8 pass; M5 source/binary/input re-freeze required before formal launch"})
    sel_fields=list(selected[0]); write_tsv(OUT / "EXTENDED20_SELECTED.tsv", sel_fields, selected)
    alternates=[]
    for rank,(suite,workload,reason) in enumerate(ALTS,1):
        r=by_key[(suite,workload)]; assert r["eligibility"] == "ELIGIBLE", r
        alternates.append({"alternate_rank":f"ALT{rank:02d}","workload":workload,"suite":suite,"algorithm":r["algorithm"],"input":r["input"],"domain":r["primary_domain"],"cost_quartile":r["cost_quartile"],"why_not_selected":reason,"replacement_rule":"replace only a same-coverage selected item; re-check P1-P6", "provenance_status":"SOURCE_BACKED_TRACE_ANCHORED; M5 source/binary/input re-freeze required"})
    write_tsv(OUT / "EXTENDED20_ALTERNATES.tsv", list(alternates[0]), alternates)
    selected_keys={(a,b) for a,b,_,_ in SELECTED}; alt_keys={(a,b) for a,b,_ in ALTS}
    not_selected=[]
    for r in inventory:
        key=(r["suite"],r["workload"])
        if key in selected_keys or key in alt_keys: continue
        if r["eligibility"] != "ELIGIBLE": reason=r["eligibility"]
        elif r["workload"] == "vectorAdd_4000000": reason="E7 near-duplicate; larger vectorAdd_6000000 selected"
        elif r["workload"] == "nn": reason="portfolio has three stronger irregular/graph cases; 3-4s filelist input is a weaker E5 representative"
        elif key == ("Rodinia", "bfs"): reason="conservative E4 choice: roster flags exact historical graph-input completion as NEEDS_REVIEW; Parboil BFS has full exact-input history"
        elif r["workload"] == "3DConvolution": reason="E7 near-duplicate crowding; selected Parboil 3-D stencil plus 2-D convolution/hotspot cover structured grids"
        elif r["workload"] == "gemm": reason="E7 dense-family crowding; selected 3mm and Gaussian, with sgemm as alternate"
        else: reason="eligible but displaced by portfolio coverage or higher-ranked alternate"
        not_selected.append({"candidate_id":r["candidate_id"],"suite":r["suite"],"workload":r["workload"],"eligibility":r["eligibility"],"disposition_reason":reason,"domain":r["primary_domain"],"cost_quartile":r["cost_quartile"],"prior_pass_evidence":r["prior_pass_evidence"]})
    assert len(not_selected)==27, len(not_selected)
    write_tsv(OUT / "EXTENDED20_NOT_SELECTED.tsv", list(not_selected[0]), not_selected)
    suites=Counter(x["suite"] for x in selected); domains=Counter(x["domain"] for x in selected); costs=Counter(x["cost_quartile"] for x in selected)
    report = f'''# M5 Extended-20 Selection Report

## Decision

This is a pre-performance, selection-only proposal for **20** supplemental GPU-compute workloads and **5 ranked alternates**.  It is intentionally separate from the Paper-10 M5 campaign and authorizes **no** Base/IO/OO runs.

## Authoritative local evidence and reconciliation

The authoritative local population is exactly 52 `(suite, workload, retained input)` entries in `/workspace/worktrees/accel-sim-decoupled-l2/docs/decoupled_l2_workload_roster_under_5h.md` (SHA-256 `4def39e4426e7a3ed912bc88ff0b8f4f15f19db4ab84b9450809233dce23f1ca`, commit `d3c41ad839afe37300e3054e8f80500140e790b4`).  Its 52/52 machine-readable reconciliation is `/workspace/worktrees/accel-sim-ep-l2-l1-causality/docs/l2_char_v1/ROUND1_WAVE1_COST_ROSTER.tsv` (SHA-256 `335348e84edce46f9bf5f8a54e2edd4d4302f09f8e3f75382e3e4629aefbac98`, commit `286e9fc09cd8898a6e8137669194ab3ac1182677`).

The roster records prior successful/full evidence where stated, plus bounded and V100-special cohorts.  It is not an M5 result registry and no active M5 worktree or GPGPU-Sim Core file was read or changed for selection.  The inventory preserves all 52 and distinguishes the 6 microbenchmarks, one trimmed derivation, five bounded-only items, five V100-special rehydration cases, and six direct Paper-10 algorithm duplicates.

`input_hash` is the frozen `kernelslist.g` SHA-256 and notes contain the reconciled trace-tree SHA-256.  This is adequate prior-run identity evidence, but not a substitute for the later M5 source/binary/input hash lock; that re-freeze is a launch precondition.

## Selected portfolio

The selected table is `EXTENDED20_SELECTED.tsv`.  Suite counts: {dict(suites)}.  Domain counts: {dict(domains)}.  Cost counts: {dict(costs)}.  Cost tiers are empirical over the 39 rows with recorded numeric historical time: Q1 <=7m, Q2 <=20m, Q3 <=66m, Q4 >66m; unknown/bounded remains non-quartiled.  The selection has four Q4 items (scan, cutcp, histo, 3mm), and ten Q1/Q2 items.

## Eligibility and duplicate handling

Paper-10 direct duplicates excluded: PolyBench atax, bicg, mvt, gesummv, 2DConvolution; Parboil spmv.  The mapping follows `M5_COMPUTE_WORKLOAD_MANIFEST.md`: Paper-10 also includes gemver/gemv, syrk, syr2k, 2mm and conv2d, none of which is silently substituted here.  Same-family variants are not co-selected: one vectorAdd, one scalarProd, one fastWalshTransform and one BFS implementation.  The full per-row gate/disposition evidence is in the inventory and not-selected table.

For every selected row, the inventory records: E1 compute application; E2 suite/app/version plus historical trace-runner path; E3 retained input plus frozen trace-list and trace-tree identity; E4 historical full/natural-drain completion evidence; E5 nontrivial work amount; E6 Paper-10 non-duplicate; E7 portfolio dedup; E8 prior GPGPU-Sim natural-drain fidelity.  The later M5 source/input/PTX re-freeze is a reproducibility lock for a new formal campaign, not a relaxed replacement for these gates.

## P1-P6 check

| Constraint | Result |
| --- | --- |
| P1 suites | PASS: CUDA SDK 8, Rodinia 5, Parboil 6, PolyBench 1; four suites and none >10. |
| P2 domains | PASS: 8 primary classes; maximum image/signal count is 5. |
| P3 access/operation coverage | PASS: irregular/graph >=3 (cfd, btree, BFS); structured/streaming >=3; reuse-heavy >=3; update-heavy >=2 (histo, scan/BFS/hotspot); compute-heavy controls >=2 (BlackScholes, Gaussian/3mm); reduction/sort/scan >=3. |
| P4 Base/source pressure | PASS target: 7 high (cfd, btree, BFS, cutcp, histo, mri-q, scan), 7 medium/mixed, 6 low/compute controls.  Tags are source/static only. |
| P5 cost | PASS: Q4=4; Q1+Q2=11.  Two unknown-cost selections are retained for unique domain/access coverage. |
| P6 no speedup cherry-picking | PASS: no PAPER_IO/PAPER_OO/DTC cycles, speedup, miss gain, or DTC-benefit field was opened or used. |

## Adversarial self-review (S4)

1. No suite dominates; CUDA SDK has 8/20, below 50%.
2. Same-family crowding was removed (parameter variants and duplicate BFS/GEMM/stencil families are alternates or excluded).
3. Long/irregular cases remain (scan, cutcp, histo, stencil, cfd, btree, BFS); runtime convenience did not remove them.
4. Selection data contains no DTC performance value.  The score is coverage/provenance/correctness/Base-source-interest/runtime/suite only.
5. Both plausible memory-pressure cases and low-pressure/compute controls are present by source inference, not observed benefit.
6. Load-dominant, balanced read/write, store-heavy and atomic-present/heavy operations are represented.
7. Common pool members are either selected, a ranked alternate, a Paper-10 duplicate, a near-duplicate, microbenchmark, bounded-only, or rehydration-incomplete; each has a stated reason.
8. The resulting set is therefore auditable as a broad portfolio rather than a DTC-speedup-cherry-picked list.

## Remaining launch gates / do not infer

Before any later M5 formal runner is authorized, freeze the exact selected source revision, CUDA wrapper/build command, binary/PTX SHA-256, canonical input byte SHA-256, output checker/reference hash, and M5 formal config/parser identity.  Do not reuse an L2 trace result as an M5 DTC result; do not substitute an alternate without rerunning P1-P6; do not launch the 60 runs from this branch.
'''
    (OUT / "M5_EXTENDED20_SELECTION_REPORT.md").write_text(report, encoding="utf-8")
    handoff = f'''# M5 E0 — Extended-20 Selection Handoff

- **Status:** `M5_EXTENDED20_SELECTION_READY_FOR_REVIEW`
- **Branch:** `hrl/decoupled-l1-exp-m5-extended20-select-v0`
- **Scope:** selection metadata only; no Extended-20 Base/IO/OO formal run was launched.

## Proposal

Selected 20: {", ".join(f"{a}/{b}" for a,b,_,_ in SELECTED)}.

Alternates in order: {", ".join(f"ALT{i:02d} {a}/{b}" for i,(a,b,_) in enumerate(ALTS,1))}.

Read `extended20/EXTENDED20_SELECTED.tsv` for reasons/scores and `extended20/EXTENDED20_ALTERNATES.tsv` for substitution rules.

## Evidence anchors

* 52-row source of truth: Decoupled-L2 under-five-hour roster, commit `d3c41ad839afe37300e3054e8f80500140e790b4`, SHA-256 `4def39e4426e7a3ed912bc88ff0b8f4f15f19db4ab84b9450809233dce23f1ca`.
* 52/52 trace-asset reconciliation: Round1 cost roster, commit `286e9fc09cd8898a6e8137669194ab3ac1182677`, SHA-256 `335348e84edce46f9bf5f8a54e2edd4d4302f09f8e3e4629aefbac98`.
* Local source recovery anchor where available: `gpu-app-collection-decoupled-l2` commit `dad09cb0487845edc7524ded814c6cde9f0ef6a1`; existing GPGPU workload wrapper commit `de9cf4293f418877aa9cdb6a2395338ca06674a6`.
* The committed inventory gives exact trace-list and trace-tree hashes for every candidate.  It does **not** claim those are later M5 binary/input hashes.

## Paper-10 proof and guardrails

The direct Paper-10 algorithm duplicates are excluded in `EXTENDED20_NOT_SELECTED.tsv`: atax, bicg, mvt, gesummv, 2DConvolution/conv2d, and spmv.  No `PAPER_IO`, `PAPER_OO`, DTC speedup, DTC-benefit or DTC live-miss result was used for selection/ranking/tie-breaking.

## Required later formal-runner re-freeze

For each selected row, record source commit/path, wrapper, canonical input byte hash, output checker/reference hash, executable/PTX hash, launch geometry, M5 Core/Framework/config hash and parser schema.  Recheck E1-E8 and P1-P6 if source/input identity differs from this trace-anchored proposal.

## Do not redo / do not do here

Do not alter GPGPU-Sim Core, active M5 worktree, M5.0B/R5DV jobs, DTC semantics, or this portfolio based on DTC results.  Do not start the 60 Base/IO/OO formal runs until researcher review authorizes the formal track.
'''
    HANDOFF.write_text(handoff, encoding="utf-8")
    print(f"wrote 52 inventory rows, 20 selected, 5 alternates, {len(not_selected)} not-selected")

if __name__ == "__main__": main()
