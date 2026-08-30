#!/usr/bin/env python3
"""Run Lane-C L1 causality cells from the exact C7e B0-Banked baseline.

Only the named L1 sensitivity overlay is appended to the frozen baseline
configuration.  Each output directory carries the source, trace, effective
configuration, and parser provenance needed for the Lane-C review pack.
"""
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
CORE = Path(os.environ.get("EP_L2_CORE", "/workspace/worktrees/gpgpu-sim-ep-l2-l1-causality"))
TRACE_ROOT = Path("/workspace/worktrees/accel-sim-decoupled-l2/hw_run")
EXIT_MARKER = "GPGPU-Sim: *** exit detected ***"
EXPECTED_FRAMEWORK = "f08d2ce857972fad73c4e1ab7162ba94c6336507"
EXPECTED_CORE = "ece1a3a77c5628763e0a4605bfd1c639ee6a1495"


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

CELLS = {
    "BASE": None,
    "META-HR": "l1_meta_hr.config",
    "BANK-HR": "l1_bank_hr.config",
    "MSHR-ONLY": "l1_mshr_hr.config",
    "MERGE-ONLY": "l1_merge_hr.config",
    "MISSQ-ONLY": "l1_missq_hr.config",
}
BASE_L1 = {"sets": 4, "ways": 128, "line_bytes": 128, "mshr": 512,
           "merge": 8, "missq": 16, "banks": 4, "latency": 20}
EXPECTED = {
    "BASE": BASE_L1,
    "META-HR": {**BASE_L1, "mshr": 1024, "merge": 32, "missq": 64},
    "BANK-HR": {**BASE_L1, "banks": 8},
    "MSHR-ONLY": {**BASE_L1, "mshr": 1024},
    "MERGE-ONLY": {**BASE_L1, "merge": 32},
    "MISSQ-ONLY": {**BASE_L1, "missq": 64},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def repo_head(path: Path) -> str:
    return subprocess.check_output(("git", "-C", str(path), "rev-parse", "HEAD"), text=True).strip()


def c7e_semantic_base(framework_source: str, core_source: str) -> list[str]:
    """Fail closed unless the simulator pair is C7e plus Lane-C scaffolding only."""
    if core_source != EXPECTED_CORE:
        raise ValueError("Core is not the exact C7e commit: " + core_source)
    ancestor = subprocess.run(("git", "-C", str(ROOT), "merge-base", "--is-ancestor",
                               EXPECTED_FRAMEWORK, framework_source), check=False)
    if ancestor.returncode:
        raise ValueError("Framework is not derived from the exact C7e commit: " + framework_source)
    changed = subprocess.check_output(("git", "-C", str(ROOT), "diff", "--name-only",
                                       EXPECTED_FRAMEWORK, framework_source), text=True).splitlines()
    allowed = {"util/ep_l2/run_l1_causality.py", "util/ep_l2/analyze_l1_causality.py", "tests/ep_l2/l1_meta_hr.config",
               "tests/ep_l2/l1_bank_hr.config", "tests/ep_l2/l1_mshr_hr.config",
               "tests/ep_l2/l1_merge_hr.config", "tests/ep_l2/l1_missq_hr.config"}
    if not set(changed).issubset(allowed):
        raise ValueError("Framework changes beyond Lane-C runner/config scaffolding: " + repr(changed))
    return changed


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def config_values(paths: list[Path]) -> dict[str, int]:
    """Resolve just the options Lane C is authorized to vary."""
    dl1 = None
    banks = None
    latency = None
    for path in paths:
        for line in path.read_text().splitlines():
            line = line.strip()
            if line.startswith("-gpgpu_cache:dl1"):
                dl1 = line.split(None, 1)[1]
            elif line.startswith("-gpgpu_l1_banks"):
                banks = int(line.split()[1])
            elif line.startswith("-gpgpu_l1_latency"):
                latency = int(line.split()[1])
    if not dl1 or banks is None or latency is None:
        raise ValueError("unable to resolve complete L1 effective configuration")
    match = re.fullmatch(r"S:(\d+):(\d+):(\d+),[^,]+,A:(\d+):(\d+),(\d+):0,32", dl1)
    if not match:
        raise ValueError("unexpected DL1 config syntax: " + dl1)
    sets, line_bytes, ways, mshr, merge, missq = map(int, match.groups())
    return {"sets": sets, "ways": ways, "line_bytes": line_bytes, "mshr": mshr,
            "merge": merge, "missq": missq, "banks": banks, "latency": latency}


def delta(before: dict[str, int], after: dict[str, int]) -> dict[str, dict[str, int]]:
    return {key: {"base": before[key], "effective": after[key]} for key in before if before[key] != after[key]}


def audit_cell(cell: str, base: Path, overlay: Path, sensitivity: Path | None) -> dict:
    effective_paths = [base, overlay] + ([sensitivity] if sensitivity else [])
    baseline = config_values([base, overlay])
    effective = config_values(effective_paths)
    if baseline != BASE_L1:
        raise ValueError("frozen B0-Banked L1 baseline mismatch: " + repr(baseline))
    if effective != EXPECTED[cell]:
        raise ValueError("unauthorized or malformed %s effective config: %r" % (cell, effective))
    changed = delta(baseline, effective)
    allowed = set(delta(BASE_L1, EXPECTED[cell]))
    if set(changed) != allowed:
        raise ValueError("config delta is not exact for %s: %r" % (cell, changed))
    return {"cell": cell, "l1_class": cell, "descriptor_capacity": 256,
            "effective_l1": effective, "baseline_l1": baseline,
            "effective_delta": changed,
            "config_files": [{"path": str(path), "sha256": sha256(path)} for path in effective_paths]}


def normal_exit(log: Path) -> tuple[bool, str | None, str | None]:
    exited = False
    cycles = instructions = None
    with log.open(encoding="utf-8", errors="replace") as source:
        for line in source:
            exited |= EXIT_MARKER in line
            match = re.match(r"^gpu_tot_sim_cycle\s*=\s*(\d+)\s*$", line)
            if match:
                cycles = match.group(1)
            match = re.match(r"^gpu_tot_sim_insn\s*=\s*(\d+)\s*$", line)
            if match:
                instructions = match.group(1)
    return exited, cycles, instructions


def parse(directory: Path, log: Path, framework_source: str, core_source: str) -> tuple[bool, str]:
    result = subprocess.run((sys.executable, str(ROOT / "util/ep_l2/parse_epl2_b0.py"), str(log),
                             "--out", str(directory), "--framework-commit", framework_source,
                             "--core-commit", core_source, "--source-log", str(log)),
                            text=True, capture_output=True)
    (directory / "parser.stdout").write_text(result.stdout)
    (directory / "parser.stderr").write_text(result.stderr)
    if result.returncode:
        return False, result.stderr.strip() or "parser failed"
    summary = next(csv.DictReader((directory / "target_summary.csv").open()))
    if summary.get("invariants_terminal_clean") != "1" or summary.get("invariants_payload_consistent") != "1":
        return False, "terminal EPL2B0V1 invariants failed"
    for name in ("target_l1.csv", "target_dram.csv", "target_window.csv"):
        path = directory / name
        if not path.is_file() or not list(csv.DictReader(path.open(newline=""))):
            return False, "missing or empty required telemetry: " + name
    with (directory / "target_l1.csv").open(newline="") as source:
        if not any(row.get("scope") == "application" for row in csv.DictReader(source)):
            return False, "missing L1 application record"
    with (directory / "target_dram.csv").open(newline="") as source:
        if not any(row.get("scope") == "window" and row.get("interval") == "5000_cycle"
                   for row in csv.DictReader(source)):
            return False, "missing DRAM 5K window telemetry"
    return True, ""


def compress(log: Path) -> tuple[Path, str]:
    compressed = log.with_suffix(".log.gz")
    with log.open("rb") as source, gzip.open(compressed, "wb") as destination:
        shutil.copyfileobj(source, destination)
    log.unlink()
    return compressed, sha256(compressed)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cell", choices=CELLS, required=True)
    parser.add_argument("--only", choices=ROSTER)
    parser.add_argument("--rerun", action="store_true")
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    base = CORE / "configs/tested-cfgs/SM7_QV100/gpgpusim.config"
    trace_config = ROOT / "gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
    overlay = ROOT / "tests/ep_l2/b0_banked_850.config"
    sensitivity = ROOT / "tests/ep_l2" / CELLS[args.cell] if CELLS[args.cell] else None
    for path in [base, trace_config, overlay] + ([sensitivity] if sensitivity else []):
        if not path or not path.is_file():
            raise SystemExit("required runtime config is missing: " + str(path))
    framework_source, core_source = repo_head(ROOT), repo_head(CORE)
    try:
        lane_c_scaffolding = c7e_semantic_base(framework_source, core_source)
    except ValueError as error:
        raise SystemExit(str(error))
    audit = audit_cell(args.cell, base, overlay, sensitivity)
    audit.update({"framework_commit": framework_source, "core_commit": core_source,
                  "c7e_framework_semantic_base": EXPECTED_FRAMEWORK,
                  "c7e_core_semantic_base": EXPECTED_CORE,
                  "lane_c_scaffolding_paths": lane_c_scaffolding,
                  "frequency_mhz": 850, "payload_variant": "B0-Banked"})
    if args.audit_only:
        print(json.dumps(audit, sort_keys=True))
        return
    sim_candidates = (ROOT / "gpu-simulator/bin/release/accel-sim.out",
                      ROOT / "gpu-simulator/build/release/accel-sim.out")
    sim = next((path for path in sim_candidates if path.is_file()), None)
    if not sim:
        raise SystemExit("missing Lane-C release simulator binary")
    selected = [args.only] if args.only else list(ROSTER)
    for workload in selected:
        trace_path = ROSTER[workload]
        if not trace_path.is_file():
            raise SystemExit("missing frozen trace: " + str(trace_path))
        directory = args.out / args.cell / workload
        status_path = directory / "run_status.json"
        if status_path.is_file() and not args.rerun:
            try:
                if json.loads(status_path.read_text()).get("status") == "COMPLETE_VALID":
                    print("SKIP_COMPLETE", args.cell, workload, flush=True)
                    continue
            except json.JSONDecodeError:
                pass
        directory.mkdir(parents=True, exist_ok=True)
        write_json(directory / "effective_config.json", audit)
        log = directory / "raw.log"
        command = [str(sim), "-config", str(base), "-config", str(trace_config),
                   "-config", str(overlay)]
        if sensitivity:
            command += ["-config", str(sensitivity)]
        command += ["-trace", str(trace_path)]
        env = os.environ.copy()
        env.update({"CORE": str(CORE), "FRAME": str(ROOT)})
        shell = ('set -eo pipefail; source "$CORE/setup_environment" release >/dev/null; '
                 'source "$FRAME/gpu-simulator/setup_environment.sh" release >/dev/null; exec "$@"')
        started = time.time()
        with log.open("w") as output:
            result = subprocess.run(["bash", "-lc", shell, "lane-c-run", *command], cwd=directory,
                                    stdout=output, stderr=subprocess.STDOUT, env=env)
        exited, cycles, instructions = normal_exit(log)
        valid, detail = (parse(directory, log, framework_source, core_source)
                         if result.returncode == 0 and exited else
                         (False, "simulator did not exit normally"))
        record = {"status": "COMPLETE_VALID" if valid else "FAILED", "detail": detail,
                  "cell": args.cell, "workload": workload, "variant": "B0-Banked",
                  "trace": str(trace_path), "exit_code": result.returncode,
                  "normal_simulator_exit": exited, "terminal_gpu_tot_sim_cycle": cycles,
                  "terminal_gpu_tot_sim_insn": instructions,
                  "wall_seconds": round(time.time() - started, 3), "audit": audit}
        if valid:
            compressed, digest = compress(log)
            record.update({"raw_log_gz": str(compressed), "raw_log_gz_sha256": digest})
        write_json(status_path, record)
        print(record["status"], args.cell, workload, "cycles=" + str(cycles), flush=True)
        if not valid:
            raise SystemExit("Lane C stopped at failed run %s/%s: %s" % (args.cell, workload, detail))


if __name__ == "__main__":
    main()
