#!/usr/bin/env python3
"""CPU-only generator for the C16 K4096 trace/simulator preparation pack."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path
from textwrap import dedent


GOAL = "C16_SPLITK_K4096_CAPACITY_COUNTERFACTUAL_PREP_174NEW_V1"
COORD = "659a12c2576580e0ad1bd2be0401fe21dd26f624"
STATIC = "c72d28b17247f25d0c3613604ab6cab1737666e0"
NATIVE = "b17193ff6b3786fd01d5bfe83b5c1a0a03859729"
PLATFORM = "8d1f14a32f5538660d74da86ccb03a2c504c5735"
SOURCE = "c7b0e88c327694c715b0a758d9ce8fd414a1fa21"
SOURCE_BLOB = "98f49efac8626388039912e6aabc8a84d9f8303b"
CONFIG_PATH = "configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config"
CONFIG_BLOB = "3306caa589baa07c046e16fddd3066351ba10d2c"
CONFIG_SHA256 = "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8"
TRACE_CONFIG_PATH = "gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config"
TRACE_CONFIG_BLOB = "07bfd7760f9073fc31d5535535c8e8707d23a625"
TRACE_CONFIG_SHA256 = "a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b"
BASE_DL2 = "-gpgpu_cache:dl2 S:2048:128:16,L:B:m:L:X,A:192:4,32:0,32"
STATUS = "SIM_PLATFORM_NOT_ADMITTED_STOP"

M, K, N, GROUP = 256, 4096, 49152, 128
INPUT_HASH = "637ea9bfb53f35dfd4ee23edbefd589f257a29357433aaad1467d075bab95e3c"
QWEIGHT_HASH = "823e8bbe3c42568a4cae5e04779aff021ca8820ce15c377211cd6287eeb63e96"
QZEROS_HASH = "b44b5d37926f92ece80483ead456d3bd5a32705c539a5ffd624ad2b14af736a6"
SCALES_HASH = "3ca87c8a23fe937275edaf51472a71c688bf17820ceb846d36d50173b6371cb8"
OUTPUT_HASH = "43432f9cefc72f5ac5e74bb26d2fb4a601ef7abc8a2839539358e076b8550d0f"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def git_bytes(repo: Path, spec: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), "show", spec])


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_tsv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def validate_authority(repo: Path) -> None:
    if git(repo, "rev-parse", "HEAD") != COORD:
        raise RuntimeError("coordination HEAD mismatch")
    for commit in (STATIC, NATIVE, PLATFORM):
        if git(repo, "cat-file", "-t", commit) != "commit":
            raise RuntimeError(f"missing commit {commit}")
    if git(repo, "rev-parse", f"{PLATFORM}:{CONFIG_PATH}") != CONFIG_BLOB:
        raise RuntimeError("baseline config blob mismatch")
    if git(repo, "rev-parse", f"{PLATFORM}:{TRACE_CONFIG_PATH}") != TRACE_CONFIG_BLOB:
        raise RuntimeError("trace config blob mismatch")
    if sha_bytes(git_bytes(repo, f"{PLATFORM}:{CONFIG_PATH}")) != CONFIG_SHA256:
        raise RuntimeError("baseline config content mismatch")
    if sha_bytes(git_bytes(repo, f"{PLATFORM}:{TRACE_CONFIG_PATH}")) != TRACE_CONFIG_SHA256:
        raise RuntimeError("trace config content mismatch")


def build_configs(repo: Path, out: Path) -> list[dict]:
    base = git_bytes(repo, f"{PLATFORM}:{CONFIG_PATH}").decode()
    if base.count(BASE_DL2) != 1:
        raise RuntimeError("baseline dl2 line is not unique")
    dl2_line = base.splitlines().index(BASE_DL2) + 1
    config_dir = out / "configs"
    config_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for mib, sets in ((64, 2048), (128, 4096), (256, 8192)):
        replacement = BASE_DL2.replace("S:2048:128:16", f"S:{sets}:128:16")
        text = base.replace(BASE_DL2, replacement)
        path = config_dir / f"L2_{mib:03d}MiB.gpgpusim.config"
        path.write_text(text, encoding="utf-8")
        before, after = base.splitlines(), text.splitlines()
        changed = [i + 1 for i, (a, b) in enumerate(zip(before, after)) if a != b]
        if len(before) != len(after) or changed not in ([], [dl2_line]):
            raise RuntimeError(f"unexpected config changes for {mib}MiB: {changed}")
        if mib == 64 and changed:
            raise RuntimeError("64MiB copy must be byte-identical")
        if mib != 64 and changed != [dl2_line]:
            raise RuntimeError(f"counterfactual must change only dl2 line {dl2_line}")
        total = sets * 128 * 16 * 16
        if total != mib * 2**20:
            raise RuntimeError("capacity calculation mismatch")
        rows.append({
            "capacity_mib": mib,
            "sets_per_subpartition": sets,
            "line_bytes": 128,
            "associativity": 16,
            "subpartitions": 16,
            "total_bytes": total,
            "changed_config_lines_vs_64mib": ",".join(map(str, changed)) or "NONE",
            "config": str(path.relative_to(out)),
            "sha256": sha_bytes(path.read_bytes()),
            "role": "BASELINE" if mib == 64 else "DESIGN_ONLY_COUNTERFACTUAL",
            "authorized_to_run": False,
        })
    return rows


def byte_range(records: tuple[int, int], bytes_per_record: float) -> list[int]:
    return [round(records[0] * bytes_per_record), round(records[1] * bytes_per_record)]


def trace_estimates() -> dict:
    # Source-derived planning envelope. Exact SASS dynamic count requires the pilot.
    loop_warp_iterations = 786_432 * 2
    loop_sass = (160, 320)
    fixed_sass = (80, 400)
    warp_ctas = {"A_split8": 49_152 * 2, "B_split1": 6_144 * 2}
    records = {
        arm: (
            loop_warp_iterations * loop_sass[0] + warps * fixed_sass[0],
            loop_warp_iterations * loop_sass[1] + warps * fixed_sass[1],
        )
        for arm, warps in warp_ctas.items()
    }
    calibration = {
        "identity": "accepted T1 PREFILL_GEMM_PRIMARY_OCC0",
        "raw_records": 12_043_648,
        "raw_trace_uncompressed_bytes": 1_286_086_205,
        "raw_trace_xz_bytes": 114_524_372,
        "grouped_trace_uncompressed_bytes": 1_056_280_276,
        "grouped_trace_xz_bytes": 27_461_164,
        "traceg_sha256": "e36178f9a92033cd91f3c1ff4b165321b7958157c7deed2a9aaa4696e7c73e8c",
        "timing_evidence_available": False,
    }
    ratios = {
        "raw_trace_uncompressed": calibration["raw_trace_uncompressed_bytes"] / calibration["raw_records"],
        "raw_trace_xz": calibration["raw_trace_xz_bytes"] / calibration["raw_records"],
        "grouped_trace_uncompressed": calibration["grouped_trace_uncompressed_bytes"] / calibration["raw_records"],
        "grouped_trace_xz": calibration["grouped_trace_xz_bytes"] / calibration["raw_records"],
    }
    arms = {}
    for arm, full in records.items():
        pilot = (full[0] // 16, full[1] // 16)
        arms[arm] = {
            "grid": 49_152 if arm.startswith("A") else 6_144,
            "k_loop_iterations_per_cta": 16 if arm.startswith("A") else 128,
            "cta_loop_products": 786_432,
            "warps_per_cta": 2,
            "estimated_dynamic_warp_instruction_records": list(full),
            "estimated_sizes_bytes": {name: byte_range(full, ratio) for name, ratio in ratios.items()},
            "M16_pilot": {
                "grid": 3_072 if arm.startswith("A") else 384,
                "estimated_dynamic_warp_instruction_records": list(pilot),
                "estimated_sizes_bytes": {name: byte_range(pilot, ratio) for name, ratio in ratios.items()},
                "capture_time_planning_interval_minutes": [10, 45],
            },
            "M256_capture_time_planning_interval_hours": [2.5, 12],
        }
    return {
        "status": "PILOT_REQUIRED_BEFORE_ANY_FULL_CAPTURE",
        "model": {
            "loop_warp_iterations_both_arms": loop_warp_iterations,
            "exact_source_loop_structure": {
                "dequant_chunks_per_Ktile": 8,
                "packed_half_sub_and_fma_operations_per_chunk": 8,
                "tensor_mma_instructions_per_warp_Ktile": 16,
                "Ktile_width": 32,
            },
            "source_derived_loop_sass_per_warp_iteration_planning_range": list(loop_sass),
            "fixed_sass_per_warp_cta_planning_range": list(fixed_sass),
            "qualification": "Envelope brackets compiler expansion around exact CUDA/PTX loop structure; it is not measured SASS and exact dynamic count must come from the pilot.",
        },
        "accepted_trace_calibration": calibration,
        "bytes_per_raw_record": ratios,
        "arms": arms,
        "pilot_policy": {
            "required": True,
            "scientific_use": False,
            "shape": {"M": 16, "K": K, "N": N},
            "scale_to_M256": 16,
            "full_capture_stop_if_extrapolated_raw_uncompressed_bytes_gt": 64 * 2**30,
            "full_capture_stop_if_extrapolated_raw_xz_bytes_gt": 8 * 2**30,
            "full_capture_stop_if_extrapolated_grouped_xz_bytes_gt": 2 * 2**30,
            "full_capture_stop_if_extrapolated_hours_per_arm_gt": 12,
            "current_gate_authorizes_pilot": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo, out = args.repo.resolve(), args.out.resolve()
    validate_authority(repo)
    out.mkdir(parents=True, exist_ok=True)
    configs = build_configs(repo, out)

    authority = {
        "goal": GOAL,
        "status": STATUS,
        "coordination_commit": COORD,
        "static_audit": {
            "commit": STATIC,
            "gate_sha256": "d19dc83ae5257ee089ca3bcc54ad6a666efbd906d19104d429883dad887ab915f",
            "status": "SUPPORTED_PROCEED_NATIVE_THRESHOLD_SCREEN",
            "K4096_split1_bytes": 104_595_456,
            "K4096_split8_each_bytes": 14_548_992,
        },
        "native_threshold": {
            "commit": NATIVE,
            "manifest_sha256": "0ea418edcbdb3c555fb1d9f3cf9c359604827854ea1aee16783efbce86209deba",
            "launch_audit_sha256": "faea2daa71ff316cdcac07690118242998300679d6a5d09e00e6e94a186f846f2",
            "correctness_sha256": "0b41e278c8eee6c308226eaf93ea52788f96d475f4ad74796d7bf36e0ff5fa455",
            "K4096_output_sha256_both_arms": OUTPUT_HASH,
            "accepted_binary_sha256": {
                "A_split8": "9e8d38a04c28770338fcef8ae0f9a90a984b7a8f95bcb98a407738594e1c08d7",
                "B_split1": "1aa8db13f5fd10651aa4241f58200e3a7075214d34cca4d70fbcbe7cbbc07887",
            },
            "node174_binary_paths_present": False,
            "binding": "accepted commit receipts; binaries must be re-hashed on any future capture node",
        },
        "kernel_source": {
            "repo": "casper-hansen/AutoAWQ_kernels",
            "commit": SOURCE,
            "path": "awq_ext/quantization/gemm_cuda_gen.cu",
            "blob": SOURCE_BLOB,
            "sha256": "974980f34d7269c9a33ccd642d9dc9bc8700f58e9afc63d65634dedd9c5fc5a6",
            "verified_cpu_only": True,
        },
        "shape": {"M": M, "K": K, "N": N, "group_size": GROUP},
        "synthetic": {
            "version": "GPT3_SHAPE_SYNTH_V1",
            "same_assets_required_for_both_arms": True,
            "tensors": {
                "input": {"bytes": 2_097_152, "sha256": INPUT_HASH},
                "qweight": {"bytes": 100_663_296, "sha256": QWEIGHT_HASH},
                "qzeros": {"bytes": 786_432, "sha256": QZEROS_HASH},
                "scales": {"bytes": 3_145_728, "sha256": SCALES_HASH},
            },
        },
        "resource_attestation": {
            "cpu_only": True,
            "gpu_used": False,
            "cuda_context_created": False,
            "gpu_lock_requested": False,
            "sass_capture_started": False,
            "simulation_started": False,
            "lane4_partial_accessed": False,
        },
    }
    dump(out / "AUTHORITY_AUDIT.json", authority)

    platform = {
        "status": STATUS,
        "branch": "hrl/awma-174-rtx4080-v1-baseline-promotion-v1",
        "commit": PLATFORM,
        "promotion_decision": "AWMA_RTX4080_SIM_BASELINE_V1_PROMOTED_WITH_SCOPE",
        "promotion_scope": "QUALIFIED_FOR_AWMA_MEMORY_TRANSLATION_STUDIES",
        "requested_scope": "GEMM data-cache L2 capacity counterfactual",
        "scope_compatible": False,
        "blocking_evidence": {
            "underlying_platform_decision": "RTX4080_ADA_PLATFORM_NOT_QUALIFIED",
            "H_CACHE_absolute_runtime_error_percent": 43.48,
            "predeclared_scoped_ceiling_percent": 35.0,
            "qualification_decision_blob": "0d67820d67c24101d78dd5363abe0497374f447e",
            "qualification_decision_sha256": "98a7756d4cc4c37e55b41402529c48988369a89cf6a0f796b15aaaf1d3714b7a",
        },
        "baseline_config": {"path": CONFIG_PATH, "blob": CONFIG_BLOB, "sha256": CONFIG_SHA256},
        "trace_config": {"path": TRACE_CONFIG_PATH, "blob": TRACE_CONFIG_BLOB, "sha256": TRACE_CONFIG_SHA256},
        "topology": {"memory_channels": 8, "subpartitions_per_channel": 2, "subpartitions": 16, "line_bytes": 128, "associativity": 16, "sets_per_subpartition": 2048, "total_l2_bytes": 67_108_864},
        "sm89_trace_parser": {
            "admitted_for_format_and_opcode_parsing": True,
            "binary_version": 89,
            "opcode_map": "Ampere_OpcodeMap",
            "addresses_are_uint64": True,
            "memory_operands_are_preserved": True,
            "accepted_T0_T1_T2_runs_completed": True,
            "this_does_not_admit_L2_scientific_fidelity": True,
        },
        "source_anchors": {
            "tracer_tool_blob": "1f73084fdf98a9ecc905ba3bc6cfdd6991fc32043",
            "trace_parser_cc_blob": "36b2d5ee4153c0b1821920016af8315ddfb110450",
            "trace_parser_h_blob": "a84f6aada226842256617dc6d0ecc3a0097810e4e",
            "trace_driven_blob": "3c08d869014ed6054c14e60f4193ab6ffd29572a7",
            "ada_opcode_blob": "7ca60db1b2aafd7b61e2fd4307a74256f2aa10e5",
        },
        "telemetry": {
            "aggregate_supported": ["gpu_sim_cycle", "gpu_sim_insn", "gpu_tot_issued_cta", "L2_total_cache_accesses", "L2_total_cache_misses", "L2_total_cache_miss_rate", "total dram reads", "total dram writes", "quiescence"],
            "object_range_L2_hit_miss_dram_supported": False,
            "object_range_note": "Trace addresses can be joined to qweight ranges for coverage, but the accepted simulator exposes no per-object L2/DRAM counters.",
        },
        "counterfactual_configs": configs,
        "configuration_claim": "Changing dl2 sets also changes set-index range; this is an L2 configuration counterfactual, not pure physical-capacity isolation.",
    }
    dump(out / "PLATFORM_BINDING.json", platform)

    contract = dedent(f"""
        # K4096 GEMM-only SASS capture contract

        This is a design contract only. The current gate is `{STATUS}` and authorizes no capture.

        ## Frozen identity

        - Shape: M={M}, K={K}, N={N}, W4 group size={GROUP}.
        - Arm A: split8, GEMM grid `[49152,1,1]`, block `[32,2,1]`, 16 K-loop iterations per CTA.
        - Arm B: split1, GEMM grid `[6144,1,1]`, block `[32,2,1]`, 128 K-loop iterations per CTA.
        - Kernel family: `gemm_forward_4bit_cuda_m16n128k32` from `{SOURCE}` / blob `{SOURCE_BLOB}`.
        - A and B must use the same `GPT3_SHAPE_SYNTH_V1` tensor bytes and the hashes in `AUTHORITY_AUDIT.json`.

        ## Mandatory GEMM-only harness

        A future, separately authorized capture must build a trace-only wrapper from the exact source above. The wrapper may only expose and return `_out_feats` (the GEMM scratch) before `.sum(0)`; it must not alter the GEMM kernel body, launch arguments, compile flags, or SM89 target. It then performs `scratch.sum(0)` only after `cudaProfilerStop()` to obtain the final output hash. For split1, the returned `[1,M,N]` scratch and its plane-0 output share storage.

        Before capture, extract the target kernel SASS from the accepted A binary, accepted B binary, and trace-only wrapper. Canonical target-kernel SASS digests must match exactly. Any mismatch is a STOP. This wrapper removes the reduction launch from the active trace region and makes the scratch VA/range/hash observable without mixing reduction traffic into the mechanism trace.

        ## Two-pass selection

        1. Discovery only: set `DYNAMIC_KERNEL_RANGE=1000000`; emit `stats.csv` without a trace and close the exact dynamic ID/name/grid/block.
        2. Capture: intersect the exact ID with an anchored regex for `gemm_forward_4bit_cuda_m16n128k32`, set `ACTIVE_FROM_START=0`, `C16_EXACT_ROOT_FUNCTION_ONLY=1`, and bracket exactly one GEMM launch with `cudaProfilerStart/Stop` plus synchronization.
        3. Require exactly one kernel in `kernelslist.g`, the frozen grid/block, binary version 89, zero unsupported opcodes, and no `reduce_kernel` trace or memory records.

        ## Object binding

        Record half-open 64-bit VA ranges, sizes, dtype/shape, and SHA256 for input, qweight, qzeros, scales, scratch, and post-region output while all tensors are live. Reject overlaps, zero pointers, size/hash mismatch, or any qweight/qzeros/scales trace address outside its recorded range. Trace addresses are suitable for object coverage joins; current simulator telemetry is not suitable for per-object L2 hit/miss claims.

        ## Mandatory size pilot after platform re-admission

        Full M256 capture is forbidden until an M16/K4096/N49152 pilot is captured for each arm. The pilot is only for records/bytes/time extrapolation and carries no scientific result. Apply the stop thresholds in `TRACE_SIZE_ESTIMATE.json`; exceeding any threshold requires a reduced mechanism proxy and a new gate.

        ## Failure rules

        Stop on authority/hash drift, SASS mismatch, more than one traced kernel, any reduction record, missing scratch binding, parser rejection, unsupported opcode, address-width truncation, dropped/overflowed records, incomplete CTA count, or failed output equality. Do not expand to a full model or another K/M/N.
        """).strip() + "\n"
    (out / "TRACE_CAPTURE_CONTRACT.md").write_text(contract, encoding="utf-8")
    dump(out / "TRACE_SIZE_ESTIMATE.json", trace_estimates())

    matrix = []
    for row in configs:
        for arm, split, grid in (("A", 8, 49_152), ("B", 1, 6_144)):
            matrix.append({
                "arm": arm,
                "split_k_iters": split,
                "gemm_grid": grid,
                "capacity_mib": row["capacity_mib"],
                "sets_per_subpartition": row["sets_per_subpartition"],
                "line_bytes": 128,
                "associativity": 16,
                "subpartitions": 16,
                "config": row["config"],
                "config_sha256": row["sha256"],
                "only_dl2_sets_changed": True,
                "authorized_to_run": False,
            })
    write_tsv(out / "L2_CONFIG_MATRIX.tsv", matrix)

    metrics = dedent("""
        # Simulator metric contract

        No run is authorized by this pack. If a future platform-scope review explicitly admits this counterfactual, each arm must replay the exact same GEMM trace at 64/128/256 MiB; only the `dl2` set count may differ.

        Pre-registered aggregate observables are completion/return code, quiescence, `gpu_sim_cycle`, `gpu_sim_insn`, issued CTA count, L2 accesses/misses/miss rate, pending hits/reservation failures, and total DRAM reads/writes. Compare deltas within an arm from 64 to 128 and 256 MiB; do not compare absolute cycles to native RTX4080 timing.

        The capacity explanation is strengthened only if split1 shows a material, monotonic L2-miss/DRAM reduction and cycle improvement with larger L2 while split8 is substantially less sensitive. A flat, reversed, non-monotonic, incomplete, or non-quiescent result rejects or weakens the proposed mechanism.

        The accepted simulator does not expose qweight-range-specific L2 hit/miss/DRAM counters. Recorded 64-bit VA ranges can prove trace coverage and classify trace operands, but aggregate cache counters must not be relabeled as qweight-only telemetry. Adding object counters would be a separate instrumentation/neutrality task and is outside this gate.

        Changing sets changes both modeled capacity and set-index range. Results may be called an L2 configuration counterfactual, never pure physical-capacity isolation or cycle-perfect Ada prediction.
        """).strip() + "\n"
    (out / "SIM_METRIC_CONTRACT.md").write_text(metrics, encoding="utf-8")

    issues = dedent("""
        # Open issues and STOP reason

        1. The promoted baseline scope is limited to AWMA memory-translation studies. The requested experiment is a data-cache L2 capacity mechanism study.
        2. The underlying RTX4080 platform qualification remains negative: its sole scale-comparable H_CACHE held-out point has 43.48% absolute runtime error against a 35% ceiling. Parser success does not repair this scientific admission failure.
        3. No authoritative target-kernel static SASS count or capture wall time is present on node 174-new. A separately authorized M16 pilot is mandatory before any M256 capture.
        4. The current simulator has aggregate L2/DRAM statistics but no admitted object-range-specific cache telemetry.

        Recovery requires an explicit, reviewable admission for directional L2 capacity counterfactual use of the frozen platform (without tuning to these results). After that, reissue a gate for the trace-only wrapper/SASS check and M16 pilot. This pack does not authorize those actions.
        """).strip() + "\n"
    (out / "OPEN_ISSUES.md").write_text(issues, encoding="utf-8")

    gate = {
        "goal": GOAL,
        "status": STATUS,
        "decision_chinese": "现有RTX4080 Accel-Sim资格范围不覆盖GEMM数据L2容量机制，停止capture和simulation。",
        "mechanical_readiness": {
            "authority_closed": True,
            "same_synthetic_contract_closed": True,
            "gemm_only_trace_design_closed": True,
            "qweight_qzeros_scales_va_binding_feasible": True,
            "scratch_binding_feasible_with_trace_only_wrapper": True,
            "sm89_trace_encoding_parser_compatible": True,
            "isolated_64_128_256MiB_configs_valid": True,
            "trace_size_pilot_required": True,
        },
        "scientific_admission": {
            "platform_scope_compatible": False,
            "promotion_scope": "QUALIFIED_FOR_AWMA_MEMORY_TRANSLATION_STUDIES",
            "requested_scope": "GEMM data-cache L2 capacity counterfactual",
            "underlying_platform_decision": "RTX4080_ADA_PLATFORM_NOT_QUALIFIED",
            "H_CACHE_error_percent": 43.48,
            "ceiling_percent": 35.0,
        },
        "authorization": {"lane7_capture": False, "M16_size_pilot": False, "M256_capture": False, "simulation": False},
        "recovery": "Obtain explicit platform-scope admission, then publish a new gate before any GPU action.",
        "gpu_used": False,
        "gpu_lock_requested": False,
    }
    dump(out / "SIM_TRACE_PREP_GATE.json", gate)

    checksum_lines = []
    for path in sorted(out.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            checksum_lines.append(f"{sha_bytes(path.read_bytes())}  {path.relative_to(out).as_posix()}")
    (out / "SHA256SUMS").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": STATUS, "files": len(checksum_lines), "configs": len(configs)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
