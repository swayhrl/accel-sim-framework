#!/usr/bin/env python3
"""Reconcile the 52 historical Decoupled-L2 workload entries with trace assets.

The 159-root physical inventory is intentionally broader than this roster.  A
roster row is a historical workload/input entry, not a claim that all copies
of the same trace are experimentally interchangeable.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


R = "/workspace/worktrees/accel-sim-decoupled-l2/hw_run"
C2P = "/workspace/worktrees/accel-sim-c2p-cache/hw_run/c2p-v100-baseline-compat-smoke-v2-20260822/stage"
TLS = "/workspace/worktrees/accel-sim-tls-cache/hw_run/tls-cache-v100-staging"


def trace(path: str) -> str:
    return f"{path}/traces/kernelslist.g"


P = f"{R}/decoupled-l2-pretraces"
PB = f"{R}/decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0"
CPB = f"{R}/c2p-polybench-full-20260821/polybench/11.0"


# Fields: suite, workload, input, cohort, decision, historical runtime,
# historical RSS, RSS evidence, exact-current-asset confidence, trace path.
ROWS = [
    # CUDA SDK: complete historical closeout, direct public pretraces.
    ("CUDA SDK", "BlackScholes", "NO_ARGS", "PRIMARY_FULL", "RUN", "9-10s", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/cudasdk/9.1/BlackScholes/NO_ARGS")),
    ("CUDA SDK", "convolutionSeparable", "size=3072", "PRIMARY_FULL", "RUN", "20-25m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/cudasdk/9.1/convolutionSeparable/__size_3072")),
    ("CUDA SDK", "fastWalshTransform_11_19", "logK=11,logD=19", "PRIMARY_FULL", "RUN", "3-4m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/cudasdk/9.1/fastWalshTransform/_logK_11__logD_19")),
    ("CUDA SDK", "fastWalshTransform_7_21", "logK=7,logD=21", "PRIMARY_FULL", "RUN", "29-59m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/cudasdk/9.1/fastWalshTransform/_logK_7__logD_21")),
    ("CUDA SDK", "scalarProd_8192", "size=8192", "PRIMARY_FULL", "RUN", "5-7m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/cudasdk/9.1/scalarProd/__size_8192")),
    ("CUDA SDK", "scalarProd_13920", "size=13920", "PRIMARY_FULL", "RUN", "11-17m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/cudasdk/9.1/scalarProd/__size_13920")),
    ("CUDA SDK", "scan", "NO_ARGS", "PRIMARY_FULL", "RUN", "1h47-3h59", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/cudasdk/9.1/scan/NO_ARGS")),
    ("CUDA SDK", "sortingNetworks", "NO_ARGS", "PRIMARY_FULL", "RUN", "6-7s", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/cudasdk/9.1/sortingNetworks/NO_ARGS")),
    ("CUDA SDK", "transpose", "512x512", "PRIMARY_FULL", "RUN", "3-4m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/cudasdk/9.1/transpose/dimX512_dimY512")),
    ("CUDA SDK", "vectorAdd_4000000", "size=4000000", "PRIMARY_FULL", "RUN", "3-6m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/cudasdk/9.1/vectorAdd/__size_4000000")),
    ("CUDA SDK", "vectorAdd_6000000", "size=6000000", "PRIMARY_FULL", "RUN", "4-8m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/cudasdk/9.1/vectorAdd/__size_6000000")),
    # Microbenchmarks remain in the 52-entry pool but never in workload heterogeneity averages.
    ("Accel-Sim ubench", "atomic_add_bw", "NO_ARGS", "MICROBENCH", "UBENCH_ONLY", "33-35m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/ubench/9.1/atomic_add_bw/NO_ARGS")),
    ("Accel-Sim ubench", "atomic_add_bw_conflict", "NO_ARGS", "MICROBENCH", "UBENCH_ONLY", "1h26-1h32", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/ubench/9.1/atomic_add_bw_conflict/NO_ARGS")),
    ("Accel-Sim ubench", "l2_bw_32f", "NO_ARGS", "MICROBENCH", "UBENCH_ONLY", "1h11-1h21", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/ubench/9.1/l2_bw_32f/NO_ARGS")),
    ("Accel-Sim ubench", "l2_bw_64f", "NO_ARGS", "MICROBENCH", "UBENCH_ONLY", "2h25-2h28", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/ubench/9.1/l2_bw_64f/NO_ARGS")),
    ("Accel-Sim ubench", "mem_bw", "NO_ARGS", "MICROBENCH", "UBENCH_ONLY", "25-43m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/ubench/9.1/mem_bw/NO_ARGS")),
    ("Accel-Sim ubench", "mem_lat", "NO_ARGS", "MICROBENCH", "UBENCH_ONLY", "2.5-3m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/ubench/9.1/mem_lat/NO_ARGS")),
    # Rodinia.  SRAD is intentionally secondary because this retained asset is 1/40 derived.
    ("Rodinia", "cfd_097k", "fvcorr_097K", "PRIMARY_FULL", "RUN", "5-6m", "1.60GiB", "X", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/rodinia-first-batch/rodinia-3.1/9.1/cfd-rodinia-3.1/__data_fvcorr_domn_097K")),
    ("Rodinia", "srad_trim", "1of40 trim", "DERIVED_TRIMMED", "SECONDARY_TRIMMED", "18m", "1.18GiB", "X", "DERIVED_TRACE_NOT_FULL", trace(f"{R}/ccws-baseline-traces/srad_v1_1of40_trim")),
    ("Rodinia", "btree", "mil+command", "PRIMARY_FULL", "RUN", "8-14m", "0.41GiB", "X", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/rodinia-first-batch/rodinia-3.1/9.1/b+tree-rodinia-3.1/file___data_mil_txt_command___data_command_txt")),
    ("Rodinia", "dwt2d", "1024x1024", "PRIMARY_FULL", "RUN", "unknown", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/rodinia-first-batch/rodinia-3.1/9.1/dwt2d-rodinia-3.1/__data_rgb_bmp__d_1024x1024__f__5__l_3")),
    ("Rodinia", "gaussian", "s=256", "PRIMARY_FULL", "RUN", "19-21m", "0.38GiB", "X", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/rodinia-first-batch/rodinia-3.1/9.1/gaussian-rodinia-3.1/_s_256")),
    ("Rodinia", "hotspot1", "1024x1024,2iter", "PRIMARY_FULL", "RUN", "unknown", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/rodinia-first-batch/rodinia-3.1/9.1/hotspot-rodinia-3.1/1024_2_2___data_temp_1024___data_power_1024_output_out")),
    ("Rodinia", "lud", "matrix-512", "PRIMARY_FULL", "RUN", "unknown", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/rodinia-first-batch/rodinia-3.1/9.1/lud-rodinia-3.1/_i___data_512_dat")),
    ("Rodinia", "nn", "filelist-4", "PRIMARY_FULL", "RUN", "3-4s", "0.37GiB", "X", "PATH_MATCH_NO_BODY_SHA", trace(f"{P}/rodinia-first-batch/rodinia-3.1/9.1/nn-rodinia-3.1/__data_filelist_4__r_5__lat_30__lng_90")),
    ("Rodinia", "bfs", "graph65536", "PRIMARY_FULL", "NEEDS_REVIEW", "unknown", "unknown", "U", "HISTORY_INPUT_UNPROVEN", trace(f"{P}/rodinia-first-batch/rodinia-3.1/9.1/bfs-rodinia-3.1/__data_graph65536_txt")),
    # Parboil full archive members retained in a staged direct trace root.
    ("Parboil", "bfs", "NY graph", "PRIMARY_FULL", "RUN", "9-14m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{PB}/parboil-bfs/_i___data_NY_input_graph_input_dat__o_bfs_NY_out")),
    ("Parboil", "cutcp", "watbox-sl40", "PRIMARY_FULL", "RUN", "1h37-2h09", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{PB}/parboil-cutcp/_i___data_small_input_watbox_sl40_pqr__o_lattice_dat")),
    ("Parboil", "histo", "default img,20x4", "PRIMARY_FULL", "RUN", "45m-2h12", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{PB}/parboil-histo/_i___data_default_input_img_bin__o_ref_bmp____20_4")),
    ("Parboil", "mri-q", "32x32x32", "PRIMARY_FULL", "RUN", "9-16m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{PB}/parboil-mri-q/_i___data_small_input_32_32_32_dataset_bin__o_32_32_32_dataset_out")),
    ("Parboil", "sad", "default", "PRIMARY_FULL", "RUN", "2-5m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{PB}/parboil-sad/_i___data_default_input_reference_bin___data_default_input_frame_bin__o_out_bin")),
    ("Parboil", "sgemm", "medium", "PRIMARY_FULL", "RUN", "12-26m", "7.8GiB", "X", "PATH_MATCH_NO_BODY_SHA", trace(f"{PB}/parboil-sgemm/_i___data_medium_input_matrix1_txt___data_medium_input_matrix2t_txt___data_medium_input_matrix2t_txt__o_matrix3_txt")),
    ("Parboil", "spmv", "Dubcova3 large", "PRIMARY_FULL", "RUN", "1-2.5m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{PB}/parboil-spmv/_i___data_large_input_Dubcova3_mtx_bin___data_large_input_vector_bin__o_Dubcova3_mtx_out")),
    ("Parboil", "stencil", "128x128x32", "PRIMARY_FULL", "RUN", "43-66m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{PB}/parboil-stencil/_i___data_small_input_128x128x32_bin__o_128x128x32_out____128_128_32_100")),
    # PolyBench: direct retained full assets from C2P/archive/diagnostic staging.
    ("PolyBench", "atax", "NO_ARGS", "PRIMARY_FULL", "RUN", "13-29m", "1.53GiB", "D", "PATH_MATCH_NO_BODY_SHA", trace(f"{CPB}/polybench-atax/NO_ARGS")),
    ("PolyBench", "bicg", "NO_ARGS", "PRIMARY_FULL", "RUN", "13-16m", "1.53GiB", "D", "PATH_MATCH_NO_BODY_SHA", trace(f"{CPB}/polybench-bicg/NO_ARGS")),
    ("PolyBench", "mvt", "NO_ARGS", "PRIMARY_FULL", "RUN", "13-17m", "1.51GiB", "D", "PATH_MATCH_NO_BODY_SHA", trace(f"{R}/decoupled-l2-bank-diagnosis/20260825-b07c0ad-full/traces/polybench/11.0/polybench-mvt/NO_ARGS")),
    ("PolyBench", "gesummv", "NO_ARGS", "PRIMARY_FULL", "RUN", "16-20m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{CPB}/polybench-gesummv/NO_ARGS")),
    ("PolyBench", "2DConvolution", "NO_ARGS", "PRIMARY_FULL", "RUN", "24-46m", "0.35GiB", "X", "PATH_MATCH_NO_BODY_SHA", trace(f"{CPB}/polybench-2DConvolution/NO_ARGS")),
    ("PolyBench", "3DConvolution", "NO_ARGS", "PRIMARY_FULL", "RUN", "26-40m", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{R}/decoupled-l2-extract/polybench.rss-profile.stage/polybench/11.0/polybench-3DConvolution/NO_ARGS")),
    ("PolyBench", "3mm", "NO_ARGS", "PRIMARY_FULL", "RUN", "1h44-2h24", "unknown", "U", "PATH_MATCH_NO_BODY_SHA", trace(f"{CPB}/polybench-3mm/NO_ARGS")),
    ("PolyBench", "gemm", "NO_ARGS", "PRIMARY_FULL", "RUN", "27-67m", "6.45GiB", "X", "PATH_MATCH_NO_BODY_SHA", trace(f"{CPB}/polybench-gemm/NO_ARGS")),
    # V100 assets are compatible physical roots but bounded-only evidence remains secondary.
    ("Mars", "ss", "V100 kernel-only", "V100_BOUNDED", "SECONDARY_BOUNDED", "3h44 bounded", "0.434GiB", "X", "V100_STAGED_NO_BODY_SHA", trace(f"{TLS}/ss/tls-mars-ss")),
    ("SHOC", "fft", "size=1,pass=1", "V100_BOUNDED", "SECONDARY_BOUNDED", "bounded", "unknown", "U", "V100_STAGED_NO_BODY_SHA", trace(f"{TLS}/fft/tls-shoc-fft")),
    ("SHOC", "sort", "V100 staged", "V100_BOUNDED", "SECONDARY_BOUNDED", "bounded", "unknown", "U", "V100_STAGED_NO_BODY_SHA", trace(f"{TLS}/sort/tls-shoc-sort")),
    ("SHOC", "gemm", "V100 staged", "V100_BOUNDED", "SECONDARY_BOUNDED", "bounded", "unknown", "U", "V100_STAGED_NO_BODY_SHA", trace(f"{TLS}/gemm/tls-shoc-gemm")),
    ("SHOC", "redc", "reduction V100 staged", "V100_BOUNDED", "SECONDARY_BOUNDED", "bounded", "unknown", "U", "V100_STAGED_NO_BODY_SHA", trace(f"{TLS}/reduction/tls-shoc-reduction")),
    ("ISPASS", "ispass_bfs", "V100 staged", "V100_SPECIAL", "NEEDS_REVIEW", "unknown", "unknown", "U", "V100_STAGED_NO_BODY_SHA", trace(f"{C2P}/c2p-ispass-bfs/c2p-ispass-bfs")),
    ("ISPASS", "ispass_lps", "V100 staged", "V100_SPECIAL", "NEEDS_REVIEW", "91-146s", "0.69-0.72GiB", "X", "V100_STAGED_NO_BODY_SHA", trace(f"{C2P}/c2p-ispass-lps/c2p-ispass-lps")),
    ("ISPASS", "ispass_ray", "V100 staged", "V100_SPECIAL", "NEEDS_REVIEW", "unknown", "unknown", "U", "V100_STAGED_NO_BODY_SHA", trace(f"{C2P}/c2p-ispass-ray/c2p-ispass-ray")),
    ("ISPASS", "ispass_lib", "V100 staged", "V100_SPECIAL", "NEEDS_REVIEW", "unknown", "unknown", "U", "V100_STAGED_NO_BODY_SHA", trace(f"{C2P}/c2p-ispass-lib/c2p-ispass-lib")),
    ("Pannotia", "fw_block", "V100 staged", "V100_SPECIAL", "NEEDS_REVIEW", "unknown", "unknown", "U", "V100_STAGED_NO_BODY_SHA", trace(f"{C2P}/c2p-pannotia-fw-block/c2p-pannotia-fw-block")),
]


def runtime_tier(text: str) -> str:
    if text == "unknown" or text == "bounded":
        return "UNKNOWN_OR_BOUNDED"
    if "3h44" in text:
        return "1_TO_4H"
    # Conservative categorization from the known upper end of a range.
    if "h" in text:
        return "1_TO_4H"
    if any(unit in text for unit in ("m", "s")):
        return "LT_1H"
    return "UNKNOWN_OR_BOUNDED"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--body-manifest", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    inv = {row["trace_list"]: row for row in csv.DictReader(args.inventory.open())}
    body_hashes = {}
    if args.body_manifest:
        import json
        body_hashes = {
            item["kernelslist"]: item
            for item in json.loads(args.body_manifest.read_text())["trace_body_sha256"]
        }
    fields = [
        "suite", "workload", "input", "cohort", "round1_decision",
        "historical_runtime", "runtime_tier", "historical_peak_rss",
        "rss_evidence", "current_trace_path", "current_asset_family",
        "current_runnable", "current_trace_tree_bytes", "kernel_count",
        "kernelslist_sha256", "same_exact_trace_asset", "trace_body_sha_status",
        "trace_tree_sha256", "trace_file_count_hashed",
        "historical_result_source", "estimated_risk",
    ]
    result = []
    for suite, workload, input_name, cohort, decision, runtime, rss, rss_evidence, exact, path in ROWS:
        asset = inv.get(path)
        hashed = body_hashes.get(path)
        if asset is None:
            current_family = "MISSING_FROM_INVENTORY"
            runnable = "NO"
            size = "NA"
            kernels = "NA"
            list_sha = "NA"
            risk = "trace path must be reconciled before use"
        else:
            current_family = asset["asset_family"]
            runnable = asset["runnable_status"]
            size = asset["trace_tree_bytes"]
            kernels = asset["kernel_count"]
            list_sha = asset["kernelslist_sha256"]
            risk = ("trace-body SHA recorded for selected Wave-1 asset only"
                    if hashed else "trace-body SHA not recorded")
            if "runnable" not in runnable:
                risk = "current trace does not pass physical runnable gate"
        result.append({
            "suite": suite, "workload": workload, "input": input_name,
            "cohort": cohort, "round1_decision": decision,
            "historical_runtime": runtime, "runtime_tier": runtime_tier(runtime),
            "historical_peak_rss": rss, "rss_evidence": rss_evidence,
            "current_trace_path": path, "current_asset_family": current_family,
            "current_runnable": runnable, "current_trace_tree_bytes": size,
            "kernel_count": kernels, "kernelslist_sha256": list_sha,
            "same_exact_trace_asset": exact,
            "trace_body_sha_status": "RECORDED_WAVE1_ONLY" if hashed else "NOT_RECORDED",
            "trace_tree_sha256": hashed["trace_tree_sha256"] if hashed else "NA",
            "trace_file_count_hashed": hashed["trace_file_count"] if hashed else "NA",
            "historical_result_source": "decoupled_l2_workload_roster_under_5h.md + memory_plan",
            "estimated_risk": risk,
        })
    assert len(result) == 52, len(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(result)
    print(f"wrote {len(result)} historical workload rows to {args.output}")


if __name__ == "__main__":
    main()
