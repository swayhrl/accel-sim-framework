#!/usr/bin/env python3
"""Frozen-provenance EPL2SRV1 runner with strict terminal parsing."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
CORE = Path(os.environ.get("EP_L2_CORE", "/workspace/worktrees/gpgpu-sim-ep-l2-streaming-reuse"))
TRACE_ROOT = Path("/workspace/worktrees/accel-sim-decoupled-l2/hw_run")
EXIT = "GPGPU-Sim: *** exit detected ***"
ORIGINAL = ("scan", "vectorAdd_4M", "convolutionSeparable", "spmv", "FWT_7_21",
            "cfd_097k", "dwt2d", "sad", "btree", "gemm")
ROSTER = {
    "scan": "decoupled-l2-pretraces/cudasdk/9.1/scan/NO_ARGS",
    "vectorAdd_4M": "decoupled-l2-pretraces/cudasdk/9.1/vectorAdd/__size_4000000",
    "vectorAdd_6M": "decoupled-l2-pretraces/cudasdk/9.1/vectorAdd/__size_6000000",
    "convolutionSeparable": "decoupled-l2-pretraces/cudasdk/9.1/convolutionSeparable/__size_3072",
    "spmv": "decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-spmv/_i___data_large_input_Dubcova3_mtx_bin___data_large_input_vector_bin__o_Dubcova3_mtx_out",
    "FWT_7_21": "decoupled-l2-pretraces/cudasdk/9.1/fastWalshTransform/_logK_7__logD_21",
    "cfd_097k": "decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/cfd-rodinia-3.1/__data_fvcorr_domn_097K",
    "dwt2d": "decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/dwt2d-rodinia-3.1/__data_rgb_bmp__d_1024x1024__f__5__l_3",
    "sad": "decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-sad/_i___data_default_input_reference_bin___data_default_input_frame_bin__o_out_bin",
    "btree": "decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/b+tree-rodinia-3.1/file___data_mil_txt_command___data_command_txt",
    "gemm": "c2p-polybench-full-20260821/polybench/11.0/polybench-gemm/NO_ARGS",
    "BlackScholes": "decoupled-l2-pretraces/cudasdk/9.1/BlackScholes/NO_ARGS",
    "histogram": "decoupled-l2-pretraces/cudasdk/9.1/histogram/NO_ARGS",
    "mergeSort": "decoupled-l2-pretraces/cudasdk/9.1/mergeSort/NO_ARGS",
    "sortingNetworks": "decoupled-l2-pretraces/cudasdk/9.1/sortingNetworks/NO_ARGS",
    "transpose": "decoupled-l2-pretraces/cudasdk/9.1/transpose/dimX512_dimY512",
    "bfs_65536": "decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/bfs-rodinia-3.1/__data_graph65536_txt",
    "nn": "decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/nn-rodinia-3.1/__data_filelist_4__r_5__lat_30__lng_90",
    "hotspot": "decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/hotspot-rodinia-3.1/1024_2_2___data_temp_1024___data_power_1024_output_out",
    "hybridsort": "decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/hybridsort-rodinia-3.1/__data_500000_txt",
}

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def head(path: Path) -> str:
    return subprocess.check_output(("git", "-C", str(path), "rev-parse", "HEAD"), text=True).strip()

def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")

def terminal(log: Path) -> tuple[bool, str | None, str | None]:
    normal = False; cycles = instructions = None
    with log.open(encoding="utf-8", errors="replace") as source:
        for line in source:
            normal |= EXIT in line
            match = re.match(r"^gpu_tot_sim_cycle\s*=\s*(\d+)\s*$", line)
            if match: cycles = match.group(1)
            match = re.match(r"^gpu_tot_sim_insn\s*=\s*(\d+)\s*$", line)
            if match: instructions = match.group(1)
    return normal, cycles, instructions

def observable_digest(log: Path) -> str:
    h = hashlib.sha256()
    prefixes = (b"EPL2B0V1|", b"EPL2M0AV1|", b"EPL2MOTV1|", b"EPL2DRAMV1|", b"L2_char_resource_leak_free")
    with log.open("rb") as source:
        for line in source:
            if line.startswith(prefixes): h.update(line)
    return h.hexdigest()

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("/workspace/results/ep_l2_streaming_reuse"))
    parser.add_argument("--label", required=True, help="new immutable result subdirectory")
    parser.add_argument("--workloads", nargs="+", required=True, choices=tuple(ROSTER))
    parser.add_argument("--modes", nargs="+", choices=("off", "on"), default=("on",))
    parser.add_argument("--expected-framework-sha", required=True)
    parser.add_argument("--expected-core-sha", required=True)
    args = parser.parse_args()
    if head(ROOT) != args.expected_framework_sha or head(CORE) != args.expected_core_sha:
        raise SystemExit("source SHA differs from frozen launch expectation")
    result_root = args.out / args.label
    if result_root.exists():
        raise SystemExit("refusing to overwrite existing evidence root: " + str(result_root))
    sim = ROOT / "gpu-simulator/bin/release/accel-sim.out"
    base = CORE / "configs/tested-cfgs/SM7_QV100/gpgpusim.config"
    trace_cfg = ROOT / "gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
    model = ROOT / "tests/ep_l2/b0_banked_d512_850.config"
    overlays = {"off": ROOT / "tests/ep_l2/streaming_reuse_off.config",
                "on": ROOT / "tests/ep_l2/streaming_reuse_on.config"}
    for asset in (sim, base, trace_cfg, model, *overlays.values()):
        if not asset.is_file(): raise SystemExit("missing runtime asset: " + str(asset))
    config = {key: digest(path) for key, path in {"base": base, "trace": trace_cfg, "model": model, **overlays}.items()}
    config_sha = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    campaign = {"framework_commit": head(ROOT), "core_commit": head(CORE),
                "config_sha256": config_sha, "config_sha256s": config,
                "simulator": str(sim), "label": args.label, "workloads": args.workloads,
                "modes": args.modes, "schema": ["EPL2MOTV1", "EPL2SRV1"]}
    result_root.mkdir(parents=True); write_json(result_root / "campaign_manifest.json", campaign)
    shell = ('set -eo pipefail; source "$CORE/setup_environment" release >/dev/null; '
             'source "$FRAME/gpu-simulator/setup_environment.sh" release >/dev/null; exec "$@"')
    for workload in args.workloads:
        trace = TRACE_ROOT / ROSTER[workload] / "traces/kernelslist.g"
        if not trace.is_file(): raise SystemExit("missing trace: " + str(trace))
        for mode in args.modes:
            directory = result_root / workload / mode; directory.mkdir(parents=True)
            log, resource = directory / "raw.log", directory / "resource.txt"
            command = (str(sim), "-config", str(base), "-config", str(trace_cfg), "-config", str(model),
                       "-config", str(overlays[mode]), "-trace", str(trace))
            env = os.environ.copy(); env.update({"CORE": str(CORE), "FRAME": str(ROOT), "CUDA_INSTALL_PATH": "/usr/local/cuda-11.8"})
            started = time.time()
            with log.open("w") as output:
                completed = subprocess.run(("/usr/bin/time", "-o", str(resource), "-f", "%e %M", "bash", "-lc", shell, "epl2srv1", *command), cwd=directory, stdout=output, stderr=subprocess.STDOUT, env=env)
            normal, cycles, instructions = terminal(log)
            status = {"workload": workload, "mode": mode, "exit_code": completed.returncode,
                      "normal_simulator_exit": normal, "cycles": cycles, "instructions": instructions,
                      "wall_seconds": round(time.time() - started, 3), "trace": str(trace),
                      "trace_kernelslist_sha256": digest(trace), "trace_id": str(trace),
                      "framework_commit": campaign["framework_commit"], "core_commit": campaign["core_commit"],
                      "config_sha256": config_sha, "epl2motv1_enabled": True,
                      "epl2srv1_enabled": mode == "on"}
            if completed.returncode or not normal:
                status.update({"status": "FAILED", "detail": "simulator did not exit normally"})
                write_json(directory / "run_status.json", status); continue
            common = ("--workload", workload, "--framework-commit", campaign["framework_commit"],
                      "--core-commit", campaign["core_commit"])
            motivation = subprocess.run((sys.executable, str(ROOT / "util/ep_l2/parse_epl2_motivation.py"), str(log), "--out", str(directory / "motivation"), *common), text=True, capture_output=True)
            (directory / "motivation_parser.stdout").write_text(motivation.stdout)
            (directory / "motivation_parser.stderr").write_text(motivation.stderr)
            b0 = subprocess.run((sys.executable, str(ROOT / "util/ep_l2/parse_epl2_b0.py"), str(log), "--out", str(directory / "b0"), *common, "--source-log", str(log)), text=True, capture_output=True)
            (directory / "b0_parser.stdout").write_text(b0.stdout)
            (directory / "b0_parser.stderr").write_text(b0.stderr)
            sector = None
            if mode == "on":
                sector = subprocess.run((sys.executable, str(ROOT / "util/ep_l2/parse_epl2_sector_reuse.py"), str(log), "--out", str(directory / "sector"), *common, "--config-sha256", config_sha, "--trace-id", str(trace)), text=True, capture_output=True)
                (directory / "sector_parser.stdout").write_text(sector.stdout)
                (directory / "sector_parser.stderr").write_text(sector.stderr)
            status["observable_digest"] = observable_digest(log)
            status["raw_log_sha256"] = digest(log)
            if motivation.returncode or b0.returncode or (sector and sector.returncode):
                status.update({"status": "FAILED", "detail": "terminal parser failure"})
            else:
                status["status"] = "COMPLETE_VALID"
            write_json(directory / "run_status.json", status)
            print(status["status"], workload, mode, flush=True)

if __name__ == "__main__":
    main()
