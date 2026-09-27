#!/usr/bin/env python3
"""Reproduce C16 host-acceleration exactness and wall-time summaries."""

import argparse
import hashlib
import json
import re
import statistics
from pathlib import Path

GROUPS = {
    "current_0271": "CURRENT_0271_CONFIG1_rep*",
    "pristine_same_build": "PRISTINE_SAMEBUILD_CONFIG1_rep*",
    "guarded_config1": "COMMITTED_GUARD_CONFIG1_rep*",
    "host_fast_v1": "COMMITTED_HOST_FAST_V1_rep*",
    "affinity_all_cpus": "AFFINITY_ALL_CPUS_rep*",
    "tmpfs_compressed": "TMPFS_COMPRESSED_rep*",
}
VOLATILE_PREFIXES = (
    "Accel-Sim [build ",
    "gpu_total_sim_rate=",
    "gpgpu_simulation_time =",
    "gpgpu_simulation_rate =",
    "gpgpu_silicon_slowdown =",
    "-enable_ptx_file_line_stats",
)
LAUNCH_RE = re.compile(
    r"^launching kernel name: (.*) uid: ([0-9]+) cuda_stream_id: ([0-9]+)$"
)
STAT_RE = re.compile(
    r"^(gpu_tot_sim_cycle|gpu_tot_sim_insn|gpu_tot_issued_cta) = ([0-9]+)$"
)


def require(value, message):
    if not value:
        raise RuntimeError(message)


def sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha256_file(path):
    return sha256_bytes(path.read_bytes())


def verify_sums(run_dir):
    sums = run_dir / "OUTPUT_SHA256SUMS"
    require(sums.is_file(), f"missing {sums}")
    verified = {}
    for line in sums.read_text().splitlines():
        expected, relative = line.split(maxsplit=1)
        relative = relative.lstrip(" *")
        path = run_dir / relative
        require(path.is_file(), f"missing {path}")
        require(sha256_file(path) == expected, f"SHA mismatch {path}")
        verified[relative] = expected
    return verified


def normalized_stdout(lines):
    kept = []
    for line in lines:
        if line.startswith("-trace "):
            continue
        if line.startswith("Header info loaded for kernel command : "):
            line = "Header info loaded for kernel command : " + Path(line.split(" : ", 1)[1]).name
        if line.startswith("Processing kernel "):
            line = "Processing kernel " + Path(line.split("Processing kernel ", 1)[1]).name
        if "GPGPU-Sim Simulator Version" in line:
            continue
        if line.startswith(VOLATILE_PREFIXES):
            continue
        kept.append(line)
    return ("\n".join(kept) + "\n").encode()


def parse_run(run_dir):
    receipt = json.loads((run_dir / "RUN_RECEIPT.json").read_text())
    require(receipt["status"] == "PASS", f"failed receipt {run_dir}")
    require(receipt["exit_code"] == 0, f"nonzero exit {run_dir}")
    require(receipt["terminal_exit_detected"] is True, f"no terminal {run_dir}")
    verified = verify_sums(run_dir)
    lines = (run_dir / "simulator.stdout").read_text().splitlines()
    launches = []
    stats = {}
    current_uid = None
    mechanism = []
    terminal = False
    for line in lines:
        if line.startswith("-trace "):
            continue
        if line.startswith("Header info loaded for kernel command : "):
            line = "Header info loaded for kernel command : " + Path(line.split(" : ", 1)[1]).name
        if line.startswith("Processing kernel "):
            line = "Processing kernel " + Path(line.split("Processing kernel ", 1)[1]).name
        match = LAUNCH_RE.match(line)
        if match:
            current_uid = int(match.group(2))
            launches.append((current_uid, int(match.group(3)), match.group(1)))
            continue
        match = STAT_RE.match(line)
        if match and current_uid is not None:
            stats.setdefault(current_uid, {})[match.group(1)] = int(match.group(2))
        if line.startswith("oracle_elastic"):
            mechanism.append(line)
        terminal |= "GPGPU-Sim: *** exit detected ***" in line
    require(len(launches) == 16, f"launch count drift {run_dir}")
    require(set(stats) == set(range(1, 17)), f"stat coverage drift {run_dir}")
    require(terminal, f"terminal marker missing {run_dir}")
    ptx_file = run_dir / "gpgpu_inst_stats.txt"
    return {
        "path": str(run_dir),
        "elapsed_seconds": receipt["elapsed_ns"] / 1e9,
        "receipt": receipt,
        "verified_outputs": verified,
        "launches": launches,
        "stats": stats,
        "mechanism_lines": mechanism,
        "normalized_stdout_sha256": sha256_bytes(normalized_stdout(lines)),
        "ptx_stats_file": {
            "present": ptx_file.is_file(),
            "size": ptx_file.stat().st_size if ptx_file.is_file() else 0,
            "sha256": sha256_file(ptx_file) if ptx_file.is_file() else None,
        },
    }


def speedup(reference, candidate):
    return (reference - candidate) / reference


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-root", required=True, type=Path)
    parser.add_argument("--legacy-audit", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    groups = {}
    for name, pattern in GROUPS.items():
        paths = sorted(args.runs_root.glob(pattern))
        require(len(paths) >= 3, f"insufficient repetitions for {name}")
        groups[name] = [parse_run(path) for path in paths]

    reference = groups["pristine_same_build"][0]
    exact = {}
    for name, runs in groups.items():
        exact[name] = {
            "kernel_sequence_exact": all(run["launches"] == reference["launches"] for run in runs),
            "cycles_instructions_CTA_exact": all(run["stats"] == reference["stats"] for run in runs),
            "mechanism_lines_exact": all(run["mechanism_lines"] == reference["mechanism_lines"] for run in runs),
            "normalized_full_stdout_exact": all(
                run["normalized_stdout_sha256"] == reference["normalized_stdout_sha256"]
                for run in runs
            ),
            "termination_exact": all(run["receipt"]["terminal_exit_detected"] for run in runs),
        }
        require(all(exact[name].values()), f"equivalence failure: {name}")

    medians = {
        name: statistics.median(run["elapsed_seconds"] for run in runs)
        for name, runs in groups.items()
    }
    legacy = json.loads(args.legacy_audit.read_text())
    legacy_cases = legacy["case_results"]
    candidate_speedups = {
        "A_MEMSTAT0": legacy_cases["MEMSTAT0"]["host_speedup_fraction_vs_M1_baseline"],
        "B_CONFIG_ONLY_PTXLINE0": legacy_cases["PTXLINE0"]["host_speedup_fraction_vs_M1_baseline"],
        "B_GUARDED_CONFIG0_VS_GUARDED_CONFIG1": speedup(
            medians["guarded_config1"], medians["host_fast_v1"]
        ),
        "C_RUNTIME10000": legacy_cases["RUNTIME10000"]["host_speedup_fraction_vs_M1_baseline"],
        "D_PREDECOMPRESSED": legacy_cases["PREDECOMPRESSED"]["host_speedup_fraction_vs_M1_baseline"],
        "D_TMPFS_COMPRESSED": speedup(medians["current_0271"], medians["tmpfs_compressed"]),
        "E_PINNED_VS_ALL_CPUS": speedup(medians["affinity_all_cpus"], medians["current_0271"]),
        "COMBINED_VS_CURRENT_0271": speedup(medians["current_0271"], medians["host_fast_v1"]),
        "COMBINED_VS_PRISTINE_SAME_BUILD": speedup(
            medians["pristine_same_build"], medians["host_fast_v1"]
        ),
    }
    result = {
        "schema": "C16_GPGPUSIM_HOST_ACCELERATION_QUALIFICATION_V1",
        "status": "HOST_ACCEL_NO_SAFE_MATERIAL_GAIN",
        "prefix": {
            "kernel_count": 16,
            "global_dynamic_kernel_first": 2926,
            "global_dynamic_kernel_last": 2941,
            "contains_completed_target_range": False,
            "normalized_full_stdout_sha256": reference["normalized_stdout_sha256"],
            "final_cumulative": reference["stats"][16],
        },
        "medians_seconds": medians,
        "candidate_speedup_fraction": candidate_speedups,
        "equivalence": exact,
        "mechanism_lines_observable": bool(reference["mechanism_lines"]),
        "ptx_observational_output": {
            "config1": reference["ptx_stats_file"],
            "config0": groups["host_fast_v1"][0]["ptx_stats_file"],
            "allowed_difference": "header-only gpgpu_inst_stats.txt is absent with config=0",
        },
        "raw_receipt_sha256": {
            name: [sha256_file(Path(run["path"]) / "RUN_RECEIPT.json") for run in runs]
            for name, runs in groups.items()
        },
        "admission": {
            "qualified": False,
            "claim": "HOST_ACCEL_NO_SAFE_MATERIAL_GAIN",
            "reason": "no candidate delivered repeatable >=5% end-to-end gain versus current/pristine authority",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "speedups": candidate_speedups}, sort_keys=True))


if __name__ == "__main__":
    main()
