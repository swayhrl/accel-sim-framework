#!/usr/bin/env python3
"""Run the isolated Lane-E Line-MSHR capacity sensitivity rows.

Each case uses the frozen B0-Banked trace/config definition.  The sole modeled
change in an MSHR256 case is the ``A:128`` to ``A:256`` Line-MSHR field in its
matching D256 or D512 overlay.
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
CORE = Path(os.environ.get("EP_L2_CORE", "/workspace/worktrees/gpgpu-sim-ep-l2-mshr-causality"))
TRACE_ROOT = Path("/workspace/worktrees/accel-sim-decoupled-l2/hw_run")
EXIT_MARKER = "GPGPU-Sim: *** exit detected ***"


def trace(relative: str) -> Path:
    return TRACE_ROOT / relative / "traces/kernelslist.g"


CASES = {
    "d256_convolution_m256": {
        "workload": "convolutionSeparable", "descriptor_pool_size": 256,
        "line_mshr_entries": 256, "overlay": "b0_banked_mshr256_850.config",
        "trace": trace("decoupled-l2-pretraces/cudasdk/9.1/convolutionSeparable/__size_3072"),
        "maturity": "PROMOTED_VALID_CALIBRATION", "promotion_dependencies": [],
        "reference": "formal D256/M128 C7e row",
    },
    "d512_convolution_m256": {
        "workload": "convolutionSeparable", "descriptor_pool_size": 512,
        "line_mshr_entries": 256, "overlay": "b0_banked_d512_mshr256_850.config",
        "trace": trace("decoupled-l2-pretraces/cudasdk/9.1/convolutionSeparable/__size_3072"),
        "maturity": "SPECULATIVE_PENDING_GATE",
        "promotion_dependencies": ["D512_PREFLIGHT_PASS"],
        "reference": "frozen Lane-B D512/M128 row",
    },
    "d512_spmv_m256": {
        "workload": "spmv", "descriptor_pool_size": 512, "line_mshr_entries": 256,
        "overlay": "b0_banked_d512_mshr256_850.config",
        "trace": trace("decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-spmv/_i___data_large_input_Dubcova3_mtx_bin___data_large_input_vector_bin__o_Dubcova3_mtx_out"),
        "maturity": "SPECULATIVE_PENDING_GATE",
        "promotion_dependencies": ["D512_PREFLIGHT_PASS"],
        "reference": "frozen Lane-B D512/M128 negative-control row",
    },
    "d512_vectoradd_m128_equivalence": {
        "workload": "vectorAdd_4M", "descriptor_pool_size": 512,
        "line_mshr_entries": 128, "overlay": "b0_banked_d512_850.config",
        "trace": trace("decoupled-l2-pretraces/cudasdk/9.1/vectorAdd/__size_4000000"),
        "maturity": "VALIDATION", "promotion_dependencies": [],
        "reference": "frozen Lane-B D512/M128 row for exact-equivalence check",
    },
    "d512_convolution_m128_equivalence": {
        "workload": "convolutionSeparable", "descriptor_pool_size": 512,
        "line_mshr_entries": 128, "overlay": "b0_banked_d512_850.config",
        "trace": trace("decoupled-l2-pretraces/cudasdk/9.1/convolutionSeparable/__size_3072"),
        "maturity": "VALIDATION", "promotion_dependencies": [],
        "reference": "frozen Lane-B D512/M128 row for exact-equivalence check",
    },
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def repo_head(path: Path) -> str:
    return subprocess.check_output(("git", "-C", str(path), "rev-parse", "HEAD"), text=True).strip()


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def normal_exit(log: Path) -> tuple[bool, str | None, str | None]:
    ok, cycle, instructions = False, None, None
    with log.open(encoding="utf-8", errors="replace") as source:
        for line in source:
            ok |= EXIT_MARKER in line
            match = re.match(r"^gpu_tot_sim_cycle\s*=\s*(\d+)\s*$", line)
            if match:
                cycle = match.group(1)
            match = re.match(r"^gpu_tot_sim_insn\s*=\s*(\d+)\s*$", line)
            if match:
                instructions = match.group(1)
    return ok, cycle, instructions


def parse(directory: Path, log: Path, framework_source: str, core_source: str) -> tuple[bool, str]:
    result = subprocess.run((sys.executable, str(ROOT / "util/ep_l2/parse_epl2_b0.py"),
                             str(log), "--out", str(directory), "--framework-commit",
                             framework_source, "--core-commit", core_source,
                             "--source-log", str(log)), text=True, capture_output=True)
    (directory / "parser.stdout").write_text(result.stdout)
    (directory / "parser.stderr").write_text(result.stderr)
    if result.returncode:
        return False, result.stderr.strip() or "parser failed"
    summary = next(csv.DictReader((directory / "target_summary.csv").open()))
    if summary.get("invariants_terminal_clean") != "1" or summary.get("invariants_payload_consistent") != "1":
        return False, "terminal EPL2B0V1 invariants failed"
    for artifact in ("target_l1.csv", "target_dram.csv"):
        path = directory / artifact
        if not path.is_file() or not list(csv.DictReader(path.open(newline=""))):
            return False, "missing or empty required C7e artifact: " + artifact
    return True, ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path,
                        default=Path("/workspace/results/ep_l2_line_mshr_causality"))
    parser.add_argument("--case", choices=sorted(CASES), action="append",
                        help="one or more named rows; omit to run every required row")
    parser.add_argument("--rerun", action="store_true")
    parser.add_argument("--expected-core-sha", required=True)
    parser.add_argument("--expected-framework-sha", required=True)
    args = parser.parse_args()
    selected = args.case or sorted(CASES)
    framework_source, core_source = repo_head(ROOT), repo_head(CORE)
    if framework_source != args.expected_framework_sha or core_source != args.expected_core_sha:
        raise SystemExit("source SHA mismatch: framework=%s core=%s" % (framework_source, core_source))
    base = CORE / "configs/tested-cfgs/SM7_QV100/gpgpusim.config"
    trace_config = ROOT / "gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
    sim = ROOT / "gpu-simulator/bin/release/accel-sim.out"
    for path in (base, trace_config, sim):
        if not path.is_file():
            raise SystemExit("required runtime asset missing: " + str(path))
    for name in selected:
        case = CASES[name]
        if not case["trace"].is_file():
            raise SystemExit("missing frozen trace: " + str(case["trace"]))
        directory = args.out / name
        status_path = directory / "run_status.json"
        if status_path.is_file() and not args.rerun:
            status = json.loads(status_path.read_text()).get("status")
            if status == "COMPLETE_VALID":
                print("SKIP_COMPLETE", name, flush=True)
                continue
        directory.mkdir(parents=True, exist_ok=True)
        overlay = ROOT / "tests/ep_l2" / case["overlay"]
        config_digests = {
            "base_config_sha256": digest(base), "trace_config_sha256": digest(trace_config),
            "overlay_sha256": digest(overlay),
        }
        config_sha = hashlib.sha256(json.dumps(config_digests, sort_keys=True).encode()).hexdigest()
        audit = {
            "lane": "E", "case": name, "workload": case["workload"], "variant": "B0-Banked",
            "frequency_mhz": 850, "descriptor_pool_size": case["descriptor_pool_size"],
            "line_mshr_entries": case["line_mshr_entries"], "per_address_cap": 32,
            "framework_authoritative_source": framework_source,
            "core_authoritative_source": core_source,
            "trace": str(case["trace"]), "reference": case["reference"],
            "maturity": case["maturity"], "promotion_dependencies": case["promotion_dependencies"],
            **config_digests, "runtime_config_composite_sha256": config_sha,
        }
        write_json(directory / "manifest.json", audit)
        log = directory / "raw.log"
        command = (str(sim), "-config", str(base), "-config", str(trace_config), "-config",
                   str(overlay), "-trace", str(case["trace"]))
        env = os.environ.copy()
        env.update({"CORE": str(CORE), "FRAME": str(ROOT)})
        shell = ('set -eo pipefail; source "$CORE/setup_environment" release >/dev/null; '
                 'source "$FRAME/gpu-simulator/setup_environment.sh" release >/dev/null; exec "$@"')
        started = time.time()
        with log.open("w") as output:
            result = subprocess.run(("bash", "-lc", shell, "lane-e-run", *command), cwd=directory,
                                    stdout=output, stderr=subprocess.STDOUT, env=env)
        exited, cycles, instructions = normal_exit(log)
        valid, detail = (parse(directory, log, framework_source, core_source)
                         if result.returncode == 0 and exited else
                         (False, "simulator did not exit normally"))
        record = {"status": "COMPLETE_VALID" if valid else "FAILED", "detail": detail,
                  "exit_code": result.returncode, "normal_simulator_exit": exited,
                  "terminal_gpu_tot_sim_cycle": cycles, "terminal_gpu_tot_sim_insn": instructions,
                  "wall_seconds": round(time.time() - started, 3), "audit": audit}
        if valid:
            compressed = log.with_suffix(".log.gz")
            with log.open("rb") as source, gzip.open(compressed, "wb") as destination:
                shutil.copyfileobj(source, destination)
            log.unlink()
            record["raw_log_gz"] = str(compressed)
            record["raw_log_gz_sha256"] = digest(compressed)
        write_json(status_path, record)
        print(record["status"], name, "cycles=" + str(cycles), flush=True)
        if not valid:
            raise SystemExit("case failed: " + name + ": " + detail)


if __name__ == "__main__":
    main()
