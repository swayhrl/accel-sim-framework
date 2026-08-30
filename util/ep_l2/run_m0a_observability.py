#!/usr/bin/env python3
"""Run isolated D512 M0a+M1 static equivalence and neutrality controls."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[2]
CORE = Path(os.environ.get("EP_L2_CORE", "/workspace/worktrees/gpgpu-sim-ep-l2-m0a-m1-int"))
TRACE_ROOT = Path("/workspace/worktrees/accel-sim-decoupled-l2/hw_run")
EXIT = "GPGPU-Sim: *** exit detected ***"
ROSTER = {
    "vectorAdd_4M": "decoupled-l2-pretraces/cudasdk/9.1/vectorAdd/__size_4000000",
    "scan": "decoupled-l2-pretraces/cudasdk/9.1/scan/NO_ARGS",
    "spmv": "decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-spmv/_i___data_large_input_Dubcova3_mtx_bin___data_large_input_vector_bin__o_Dubcova3_mtx_out",
    "convolutionSeparable": "decoupled-l2-pretraces/cudasdk/9.1/convolutionSeparable/__size_3072",
    "cfd_097k": "decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/cfd-rodinia-3.1/__data_fvcorr_domn_097K",
    "sad": "decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-sad/_i___data_default_input_reference_bin___data_default_input_frame_bin__o_out_bin",
}
EQUIVALENCE = ("vectorAdd_4M", "cfd_097k", "sad")
MATURE = "SPECULATIVE_PENDING_GATE"
PROMOTION_DEPENDENCIES = ("M0A_FINAL_PASS", "M1_FINAL_PASS")
MODES = {
    "BASE_M1_STATIC": {
        "overlay": "OFF",
        "m0a_stats_enabled": False,
        "ep_l2_features": {
            "payload_policy": "static",
            "unified_payload": False,
            "ro_pending_state": False,
            "tvd": False,
            "adaptive_policy": False,
        },
    },
    "M0A_ON_M1_STATIC": {
        "overlay": "ON",
        "m0a_stats_enabled": True,
        "ep_l2_features": {
            "payload_policy": "static",
            "unified_payload": False,
            "ro_pending_state": False,
            "tvd": False,
            "adaptive_policy": False,
        },
    },
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


def active_config_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines()
            if line.strip() and not line.lstrip().startswith("#")]


def terminal(log: Path) -> tuple[bool, str | None, str | None]:
    ok = False
    cycles = insn = None
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        ok |= EXIT in line
        if match := re.match(r"^gpu_tot_sim_cycle\s*=\s*(\d+)\s*$", line):
            cycles = match.group(1)
        if match := re.match(r"^gpu_tot_sim_insn\s*=\s*(\d+)\s*$", line):
            insn = match.group(1)
    return ok, cycles, insn


def run_one(task: tuple[str, str], out: Path, command: tuple[str, ...], audit: dict) -> dict:
    workload, mode = task
    directory = out / mode / workload
    directory.mkdir(parents=True, exist_ok=True)
    log = directory / "raw.log"
    started = time.time()
    env = os.environ.copy()
    env.update({"CORE": str(CORE), "FRAME": str(ROOT), "CUDA_INSTALL_PATH": "/usr/local/cuda-11.8"})
    shell = ('set -eo pipefail; source "$CORE/setup_environment" release >/dev/null; '
             'source "$FRAME/gpu-simulator/setup_environment.sh" release >/dev/null; exec "$@"')
    with log.open("w") as output:
        result = subprocess.run(("bash", "-lc", shell, "m0a-run", *command), cwd=directory,
                                stdout=output, stderr=subprocess.STDOUT, env=env)
    normal, cycles, insn = terminal(log)
    run_audit = dict(audit)
    run_audit.update({"experiment_mode": mode, "m0a_stats_enabled": MODES[mode]["m0a_stats_enabled"],
                      "ep_l2_features": MODES[mode]["ep_l2_features"], "trace": command[-1],
                      "result_root": str(directory)})
    status = {"workload": workload, "mode": mode, "exit_code": result.returncode,
              "normal_simulator_exit": normal, "terminal_gpu_tot_sim_cycle": cycles,
              "terminal_gpu_tot_sim_insn": insn, "wall_seconds": round(time.time() - started, 3),
              "audit": run_audit}
    if result.returncode or not normal:
        status.update({"status": "FAILED", "detail": "simulator did not exit normally"})
        write_json(directory / "run_status.json", status)
        return status
    if MODES[mode]["m0a_stats_enabled"]:
        parsed = subprocess.run((sys.executable, str(ROOT / "util/ep_l2/parse_epl2_m0a.py"), str(log),
                                 "--out", str(directory), "--framework-commit", audit["framework_sha"],
                                 "--core-commit", audit["core_sha"]), text=True, capture_output=True)
        (directory / "m0a_parser.stdout").write_text(parsed.stdout)
        (directory / "m0a_parser.stderr").write_text(parsed.stderr)
        if parsed.returncode:
            status.update({"status": "FAILED", "detail": parsed.stderr.strip() or "M0a parser failed"})
            write_json(directory / "run_status.json", status)
            return status
    # B0's established parser supplies terminal invariants and C7e values for
    # OFF/ON comparison without making M0a a dependency of the B0 schema.
    parsed_b0 = subprocess.run((sys.executable, str(ROOT / "util/ep_l2/parse_epl2_b0.py"), str(log),
                                "--out", str(directory), "--framework-commit", audit["framework_sha"],
                                "--core-commit", audit["core_sha"], "--source-log", str(log)),
                               text=True, capture_output=True)
    (directory / "b0_parser.stdout").write_text(parsed_b0.stdout)
    (directory / "b0_parser.stderr").write_text(parsed_b0.stderr)
    if parsed_b0.returncode:
        status.update({"status": "FAILED", "detail": parsed_b0.stderr.strip() or "B0 parser failed"})
        write_json(directory / "run_status.json", status)
        return status
    packed = log.with_suffix(".log.gz")
    with log.open("rb") as source, gzip.open(packed, "wb") as dest:
        shutil.copyfileobj(source, dest)
    log.unlink()
    status.update({"status": "COMPLETE_VALID", "raw_log_gz": str(packed),
                   "raw_log_gz_sha256": digest(packed)})
    write_json(directory / "run_status.json", status)
    return status


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("/workspace/results/ep_l2_m0a_m1_int"))
    parser.add_argument("--jobs", type=int, default=3)
    parser.add_argument("--only", choices=tuple(ROSTER))
    parser.add_argument("--full-roster", action="store_true",
                        help="opt in to all six M0a workloads; default is the compact three-workload gate")
    args = parser.parse_args()
    base = CORE / "configs/tested-cfgs/SM7_QV100/gpgpusim.config"
    trace_cfg = ROOT / "gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
    d512 = ROOT / "tests/ep_l2/b0_banked_d512_850.config"
    overlays = {"OFF": ROOT / "tests/ep_l2/m0a_off.config", "ON": ROOT / "tests/ep_l2/m0a_on.config"}
    sim = ROOT / "gpu-simulator/bin/release/accel-sim.out"
    for path in (base, trace_cfg, d512, *overlays.values(), sim):
        if not path.is_file():
            raise SystemExit("required asset missing: " + str(path))
    config_digests = {name: digest(path) for name, path in
                      {"base": base, "trace": trace_cfg, "d512": d512, **overlays}.items()}
    config_delta_pass = (active_config_lines(overlays["OFF"]) == ["-gpgpu_ep_l2_m0a_stats 0"] and
                         active_config_lines(overlays["ON"]) == ["-gpgpu_ep_l2_m0a_stats 1"])
    if not config_delta_pass:
        raise SystemExit("M0a OFF/ON overlays are not the approved one-bit config delta")
    audit = {"schema_version": "EPL2M0AV1", "semantic_base_id": "EP_L2_D512_CALIBRATED",
             "maturity": MATURE, "promotion_dependencies": PROMOTION_DEPENDENCIES,
             "framework_sha": head(ROOT), "core_sha": head(CORE),
             "frequency_mhz": 850, "runtime_config_sha256": hashlib.sha256(
                 json.dumps(config_digests, sort_keys=True).encode()).hexdigest(),
             "config_digests": config_digests, "config_delta_pass": config_delta_pass,
             "config_delta_evidence": "only -gpgpu_ep_l2_m0a_stats: 0 -> 1",
             "primary_variant": "D512_B0_Banked", "m1_substrate": "static-compatible"}
    args.out.mkdir(parents=True, exist_ok=True)
    write_json(args.out / "campaign_manifest.json", audit)
    names = ((args.only,) if args.only else
             (tuple(ROSTER) if args.full_roster else EQUIVALENCE))
    tasks = [(name, "M0A_ON_M1_STATIC") for name in names]
    tasks += [(name, mode) for name in EQUIVALENCE if name in names for mode in MODES]
    tasks = list(dict.fromkeys(tasks))
    commands = {}
    for name, mode in tasks:
        trace = TRACE_ROOT / ROSTER[name] / "traces/kernelslist.g"
        if not trace.is_file():
            raise SystemExit("missing frozen trace: " + str(trace))
        commands[(name, mode)] = (str(sim), "-config", str(base), "-config", str(trace_cfg),
                                  "-config", str(d512), "-config", str(overlays[MODES[mode]["overlay"]]),
                                  "-trace", str(trace))
    failures = []
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = {pool.submit(run_one, task, args.out, commands[task], audit): task for task in tasks}
        for future in as_completed(futures):
            status = future.result()
            print(status["status"], status["mode"], status["workload"], flush=True)
            if status["status"] != "COMPLETE_VALID": failures.append(status)
    if failures:
        raise SystemExit("M0a campaign has failed cells")


if __name__ == "__main__":
    main()
