#!/usr/bin/env python3
"""Run speculative Lane-C D512 x L1 interaction cells from frozen Lane-B SHAs."""
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


ROOT = Path(__file__).resolve().parents[2]
CORE = Path(os.environ.get("EP_L2_CORE", "/workspace/worktrees/gpgpu-sim-ep-l2-l1-causality-d512"))
TRACE_ROOT = Path("/workspace/worktrees/accel-sim-decoupled-l2/hw_run")
EXPECTED_FRAMEWORK = "aae62b66685f15437cecf0193934f628e6fac6ae"
EXPECTED_CORE = "878f80869ce212e779df20b6421e4dc7f987825d"
MATURITY = "SPECULATIVE_PENDING_GATE"
PROMOTION_DEPENDENCIES = ["D256_EQ_SCAN_PASS", "D512_PREFLIGHT_PASS"]
EXIT_MARKER = "GPGPU-Sim: *** exit detected ***"


def trace(relative: str) -> Path:
    return TRACE_ROOT / relative / "traces/kernelslist.g"


ROSTER = {
    "vectorAdd_4M": trace("decoupled-l2-pretraces/cudasdk/9.1/vectorAdd/__size_4000000"),
    "scan": trace("decoupled-l2-pretraces/cudasdk/9.1/scan/NO_ARGS"),
    "spmv": trace("decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-spmv/_i___data_large_input_Dubcova3_mtx_bin___data_large_input_vector_bin__o_Dubcova3_mtx_out"),
    "convolutionSeparable": trace("decoupled-l2-pretraces/cudasdk/9.1/convolutionSeparable/__size_3072"),
    "btree": trace("decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/b+tree-rodinia-3.1/file___data_mil_txt_command___data_command_txt"),
    "sad": trace("decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-sad/_i___data_default_input_reference_bin___data_default_input_frame_bin__o_out_bin"),
    "FWT_7_21": trace("decoupled-l2-pretraces/cudasdk/9.1/fastWalshTransform/_logK_7__logD_21"),
}
CELLS = {"D512-META-HR": "l1_meta_hr.config", "D512-BANK-HR": "l1_bank_hr.config"}
BASE_L1 = {"sets": 4, "ways": 128, "line_bytes": 128, "mshr": 512, "merge": 8, "missq": 16, "banks": 4, "latency": 20}
EXPECTED = {
    "D512-META-HR": {**BASE_L1, "mshr": 1024, "merge": 32, "missq": 64},
    "D512-BANK-HR": {**BASE_L1, "banks": 8},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def head(path: Path) -> str:
    return subprocess.check_output(("git", "-C", str(path), "rev-parse", "HEAD"), text=True).strip()


def validate_source(framework: str, core: str) -> list[str]:
    if core != EXPECTED_CORE:
        raise ValueError("Core is not the frozen Lane-B D512 candidate: " + core)
    if subprocess.run(("git", "-C", str(ROOT), "merge-base", "--is-ancestor", EXPECTED_FRAMEWORK, framework), check=False).returncode:
        raise ValueError("Framework is not derived from the frozen Lane-B D512 candidate: " + framework)
    changed = subprocess.check_output(("git", "-C", str(ROOT), "diff", "--name-only", EXPECTED_FRAMEWORK, framework), text=True).splitlines()
    allowed = {"util/ep_l2/run_l1_d512_interaction.py", "tests/ep_l2/l1_meta_hr.config", "tests/ep_l2/l1_bank_hr.config"}
    if not set(changed).issubset(allowed):
        raise ValueError("D512 Lane-C worktree contains non-scaffolding changes: " + repr(changed))
    return changed


def effective(paths: list[Path]) -> tuple[dict[str, int], int]:
    dl1 = None
    banks = latency = descriptor = None
    for path in paths:
        for raw in path.read_text().splitlines():
            line = raw.strip()
            if line.startswith("-gpgpu_cache:dl1"):
                dl1 = line.split(None, 1)[1]
            elif line.startswith("-gpgpu_l1_banks"):
                banks = int(line.split()[1])
            elif line.startswith("-gpgpu_l1_latency"):
                latency = int(line.split()[1])
            elif line.startswith("-gpgpu_ep_l2_descriptor_pool_size"):
                descriptor = int(line.split()[1])
    if not dl1 or banks is None or latency is None or descriptor is None:
        raise ValueError("incomplete effective runtime configuration")
    match = re.fullmatch(r"S:(\d+):(\d+):(\d+),[^,]+,A:(\d+):(\d+),(\d+):0,32", dl1)
    if not match:
        raise ValueError("unexpected DL1 syntax: " + dl1)
    sets, line_bytes, ways, mshr, merge, missq = map(int, match.groups())
    return ({"sets": sets, "ways": ways, "line_bytes": line_bytes, "mshr": mshr, "merge": merge, "missq": missq, "banks": banks, "latency": latency}, descriptor)


def audit(cell: str, paths: list[Path]) -> dict:
    l1, descriptor = effective(paths)
    if l1 != EXPECTED[cell] or descriptor != 512:
        raise ValueError("unauthorized D512 interaction effective config: " + repr((l1, descriptor)))
    delta = {key: {"base": BASE_L1[key], "effective": l1[key]} for key in BASE_L1 if BASE_L1[key] != l1[key]}
    expected = {key for key in BASE_L1 if BASE_L1[key] != EXPECTED[cell][key]}
    if set(delta) != expected:
        raise ValueError("unexpected L1 delta: " + repr(delta))
    return {"cell": cell, "l1_class": cell.removeprefix("D512-"), "descriptor_capacity": 512,
            "candidate_framework_commit": EXPECTED_FRAMEWORK, "candidate_core_commit": EXPECTED_CORE,
            "maturity": MATURITY, "promotion_dependencies": PROMOTION_DEPENDENCIES,
            "baseline_l1": BASE_L1, "effective_l1": l1, "effective_delta": {"descriptor_pool_size": {"base": 256, "effective": 512}, **delta},
            "config_files": [{"path": str(path), "sha256": sha256(path)} for path in paths]}


def normal_exit(log: Path) -> tuple[bool, str | None, str | None]:
    exited = False; cycles = instructions = None
    with log.open(encoding="utf-8", errors="replace") as source:
        for line in source:
            exited |= EXIT_MARKER in line
            if match := re.match(r"^gpu_tot_sim_cycle\s*=\s*(\d+)\s*$", line): cycles = match.group(1)
            if match := re.match(r"^gpu_tot_sim_insn\s*=\s*(\d+)\s*$", line): instructions = match.group(1)
    return exited, cycles, instructions


def parse(directory: Path, log: Path, framework: str, core: str) -> tuple[bool, str]:
    result = subprocess.run((sys.executable, str(ROOT / "util/ep_l2/parse_epl2_b0.py"), str(log), "--out", str(directory), "--framework-commit", framework, "--core-commit", core, "--source-log", str(log)), text=True, capture_output=True)
    (directory / "parser.stdout").write_text(result.stdout); (directory / "parser.stderr").write_text(result.stderr)
    if result.returncode: return False, result.stderr.strip() or "parser failed"
    summary = next(csv.DictReader((directory / "target_summary.csv").open()))
    if summary.get("invariants_terminal_clean") != "1" or summary.get("invariants_payload_consistent") != "1": return False, "terminal invariants failed"
    for name in ("target_l1.csv", "target_dram.csv", "target_window.csv"):
        if not (directory / name).is_file(): return False, "missing telemetry: " + name
    return True, ""


def compress(log: Path) -> tuple[Path, str]:
    destination = log.with_suffix(".log.gz")
    with log.open("rb") as source, gzip.open(destination, "wb") as target: shutil.copyfileobj(source, target)
    log.unlink(); return destination, sha256(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True); parser.add_argument("--cell", choices=CELLS, required=True)
    parser.add_argument("--only", choices=ROSTER); parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    base = CORE / "configs/tested-cfgs/SM7_QV100/gpgpusim.config"
    trace_config = ROOT / "gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
    d512_overlay = ROOT / "tests/ep_l2/b0_banked_d512_850.config"
    sensitivity = ROOT / "tests/ep_l2" / CELLS[args.cell]
    paths = [base, trace_config, d512_overlay, sensitivity]
    if not all(path.is_file() for path in paths): raise SystemExit("missing runtime config")
    framework, core = head(ROOT), head(CORE)
    try:
        scaffolding = validate_source(framework, core); config_audit = audit(args.cell, paths)
    except ValueError as error: raise SystemExit(str(error))
    config_audit.update({"framework_commit": framework, "core_commit": core, "lane_c_scaffolding_paths": scaffolding, "frequency_mhz": 850, "payload_variant": "B0-Banked"})
    if args.audit_only:
        print(json.dumps(config_audit, sort_keys=True)); return
    sim = ROOT / "gpu-simulator/build/release/accel-sim.out"
    if not sim.is_file(): raise SystemExit("missing isolated Lane-C D512 release binary")
    for workload in ([args.only] if args.only else list(ROSTER)):
        trace_path = ROSTER[workload]; directory = args.out / args.cell / workload; status_path = directory / "run_status.json"
        if status_path.is_file() and json.loads(status_path.read_text()).get("status") == "COMPLETE_VALID": print("SKIP_COMPLETE", args.cell, workload); continue
        directory.mkdir(parents=True, exist_ok=True); (directory / "effective_config.json").write_text(json.dumps(config_audit, indent=2, sort_keys=True) + "\n")
        log = directory / "raw.log"; command = [str(sim), "-config", str(base), "-config", str(trace_config), "-config", str(d512_overlay), "-config", str(sensitivity), "-trace", str(trace_path)]
        env = os.environ.copy(); env.update({"CORE": str(CORE), "FRAME": str(ROOT)}); shell = 'set -eo pipefail; source "$CORE/setup_environment" release >/dev/null; source "$FRAME/gpu-simulator/setup_environment.sh" release >/dev/null; exec "$@"'
        started = time.time()
        with log.open("w") as output: result = subprocess.run(["bash", "-lc", shell, "lane-c-d512", *command], cwd=directory, stdout=output, stderr=subprocess.STDOUT, env=env)
        exited, cycles, instructions = normal_exit(log); valid, detail = (parse(directory, log, framework, core) if result.returncode == 0 and exited else (False, "simulator did not exit normally"))
        record = {"status": "COMPLETE_VALID" if valid else "FAILED", "detail": detail, "cell": args.cell, "workload": workload, "variant": "B0-Banked", "trace": str(trace_path), "exit_code": result.returncode, "normal_simulator_exit": exited, "terminal_gpu_tot_sim_cycle": cycles, "terminal_gpu_tot_sim_insn": instructions, "wall_seconds": round(time.time() - started, 3), "audit": config_audit, "maturity": MATURITY, "promotion_dependencies": PROMOTION_DEPENDENCIES}
        if valid:
            compressed, digest = compress(log); record.update({"raw_log_gz": str(compressed), "raw_log_gz_sha256": digest})
        status_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n"); print(record["status"], args.cell, workload, "cycles=" + str(cycles), flush=True)
        if not valid: raise SystemExit("Lane C D512 stopped at failed run %s/%s: %s" % (args.cell, workload, detail))


if __name__ == "__main__": main()
