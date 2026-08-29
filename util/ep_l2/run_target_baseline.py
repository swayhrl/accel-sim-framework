#!/usr/bin/env python3
"""Run the frozen EP-L2 Target Baseline B0 campaign at 850 MHz only.

The runner deliberately contains no Unified/RO/TVD overlays.  It captures the
checked-out Framework and Core commits at launch, so each campaign manifest
has one authoritative, reproducible source pair.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[2]
CORE = Path("/workspace/worktrees/gpgpu-sim-ep-l2")
TRACE_ROOT = Path("/workspace/worktrees/accel-sim-decoupled-l2/hw_run")
EXIT_MARKER = "GPGPU-Sim: *** exit detected ***"


def trace(relative: str) -> Path:
    return TRACE_ROOT / relative / "traces/kernelslist.g"


# Name, source trace.  This is the review-frozen 13-workload roster.
ROSTER = (
    ("vectorAdd_4M", trace("decoupled-l2-pretraces/cudasdk/9.1/vectorAdd/__size_4000000")),
    ("scan", trace("decoupled-l2-pretraces/cudasdk/9.1/scan/NO_ARGS")),
    ("spmv", trace("decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-spmv/_i___data_large_input_Dubcova3_mtx_bin___data_large_input_vector_bin__o_Dubcova3_mtx_out")),
    ("convolutionSeparable", trace("decoupled-l2-pretraces/cudasdk/9.1/convolutionSeparable/__size_3072")),
    ("cfd_097k", trace("decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/cfd-rodinia-3.1/__data_fvcorr_domn_097K")),
    ("dwt2d", trace("decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/dwt2d-rodinia-3.1/__data_rgb_bmp__d_1024x1024__f__5__l_3")),
    ("sad", trace("decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-sad/_i___data_default_input_reference_bin___data_default_input_frame_bin__o_out_bin")),
    ("sgemm", trace("decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-sgemm/_i___data_medium_input_matrix1_txt___data_medium_input_matrix2t_txt___data_medium_input_matrix2t_txt__o_matrix3_txt")),
    ("btree", trace("decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/b+tree-rodinia-3.1/file___data_mil_txt_command___data_command_txt")),
    ("3mm", trace("c2p-polybench-full-20260821/polybench/11.0/polybench-3mm/NO_ARGS")),
    ("gemm", trace("c2p-polybench-full-20260821/polybench/11.0/polybench-gemm/NO_ARGS")),
    ("FWT_7_21", trace("decoupled-l2-pretraces/cudasdk/9.1/fastWalshTransform/_logK_7__logD_21")),
    ("FWT_11_19", trace("decoupled-l2-pretraces/cudasdk/9.1/fastWalshTransform/_logK_11__logD_19")),
)
VARIANTS = (("B0-Legacy", "b0_legacy_850.config"), ("B0-Banked", "b0_banked_850.config"))


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def repo_head(path: Path) -> str:
    return subprocess.check_output(("git", "-C", str(path), "rev-parse", "HEAD"),
                                   text=True).strip()


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def normal_exit(log: Path) -> tuple[bool, str | None]:
    ok, cycle = False, None
    with log.open(encoding="utf-8", errors="replace") as source:
        for line in source:
            ok |= EXIT_MARKER in line
            match = re.match(r"^gpu_tot_sim_cycle\s*=\s*(\d+)\s*$", line)
            if match:
                cycle = match.group(1)
    return ok, cycle


def parse(directory: Path, log: Path, framework_source: str,
          core_source: str) -> tuple[bool, str]:
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
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["characterization_started"] = True
    manifest["target_baseline"] = {"frequency_mhz": 850, "variants": [v[0] for v in VARIANTS],
                                   "framework_authoritative_source": framework_source,
                                   "core_authoritative_source": core_source}
    write_json(manifest_path, manifest)
    return True, ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path,
                        default=ROOT / "docs/ep_l2/target_baseline_results_c5c")
    parser.add_argument("--only", help="one frozen workload name")
    parser.add_argument("--variant", choices=[v[0] for v in VARIANTS])
    parser.add_argument("--rerun", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    rows = [(name, path, variant, overlay) for name, path in ROSTER for variant, overlay in VARIANTS
            if (not args.only or name == args.only) and (not args.variant or variant == args.variant)]
    missing = [str(path) for _, path, _, _ in rows if not path.is_file()]
    if missing:
        raise SystemExit("missing frozen trace assets:\n" + "\n".join(missing))
    base = CORE / "configs/tested-cfgs/SM7_QV100/gpgpusim.config"
    trace_config = ROOT / "gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
    sim = ROOT / "gpu-simulator/bin/release/accel-sim.out"
    for path in (base, trace_config, sim):
        if not path.exists():
            raise SystemExit("required runtime asset is missing: " + str(path))
    framework_source = repo_head(ROOT)
    core_source = repo_head(CORE)
    audit = {"schema_version": "EPL2B0V1", "framework_authoritative_source": framework_source,
             "core_authoritative_source": core_source, "frequency_mhz": 850,
             "base_config_sha256": digest(base), "trace_config_sha256": digest(trace_config),
             "frozen_roster": [{"workload": n, "trace": str(t)} for n, t in ROSTER]}
    args.out.mkdir(parents=True, exist_ok=True)
    write_json(args.out / "campaign_manifest.json", audit)
    for name, trace_path, variant, overlay_name in rows:
        directory = args.out / variant / name
        status_path = directory / "run_status.json"
        if status_path.is_file() and not args.rerun:
            try:
                if json.loads(status_path.read_text()).get("status") == "COMPLETE_VALID":
                    print("SKIP_COMPLETE", variant, name, flush=True); continue
            except json.JSONDecodeError:
                pass
        if args.dry_run:
            print("DRY_RUN", variant, name, trace_path); continue
        directory.mkdir(parents=True, exist_ok=True)
        log = directory / "raw.log"
        command = (str(sim), "-config", str(base), "-config", str(trace_config), "-config",
                   str(ROOT / "tests/ep_l2" / overlay_name), "-trace", str(trace_path))
        env = os.environ.copy(); env.update({"CORE": str(CORE), "FRAME": str(ROOT)})
        shell = ('set -eo pipefail; source "$CORE/setup_environment" release >/dev/null; '
                 'source "$FRAME/gpu-simulator/setup_environment.sh" release >/dev/null; exec "$@"')
        started = time.time()
        with log.open("w") as output:
            result = subprocess.run(("bash", "-lc", shell, "target-baseline-run", *command), cwd=directory,
                                    stdout=output, stderr=subprocess.STDOUT, env=env)
        exited, cycles = normal_exit(log)
        valid, detail = (parse(directory, log, framework_source, core_source)
                         if result.returncode == 0 and exited else
                         (False, "simulator did not exit normally"))
        status = "COMPLETE_VALID" if valid else "FAILED"
        write_json(status_path, {"status": status, "detail": detail, "workload": name, "variant": variant,
                                 "frequency_mhz": 850, "trace": str(trace_path), "exit_code": result.returncode,
                                 "normal_simulator_exit": exited, "terminal_gpu_tot_sim_cycle": cycles,
                                 "wall_seconds": round(time.time() - started, 3), "audit": audit})
        print(status, variant, name, "cycles=" + str(cycles), flush=True)
        if not valid:
            raise SystemExit("campaign stopped at failed run: %s/%s: %s" % (variant, name, detail))


if __name__ == "__main__":
    main()
