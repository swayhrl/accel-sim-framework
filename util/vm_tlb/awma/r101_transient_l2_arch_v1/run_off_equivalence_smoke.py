#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


BASE = Path("/root/awma_rtx4080_v1_baseline_promotion_v1_runtime/ai_T2_V1_10_80")
RUNTIME = Path("/root/awma_r101_transient_l2_arch_174_v1_runtime")
RAW_ROOT = Path("/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/raw")
BINARY = RUNTIME / "bin/unified_accel-sim.out"
CORE_LIB = RUNTIME / "src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release"
EXPECTED = {"cycles": 93079, "instructions": 43357696, "ctas": 1216,
            "unique": 411008}
ARMS = {
    "default_off": ("off_equivalence_t2", None),
    "explicit_none": ("explicit_none_equivalence_t2", "none"),
    "oracle_no_overlap": ("oracle_no_overlap_t2", "oracle_dead_drop"),
    "m1_no_overlap": ("m1_no_overlap_t2", "bounded_live_retention"),
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def scalar(text: str, key: str) -> int:
    values = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(key + " ="):
            values.append(int(stripped.split("=", 1)[1].strip()))
    if not values:
        raise RuntimeError(f"missing {key}")
    return values[-1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=tuple(ARMS),
                        default="default_off")
    args = parser.parse_args()
    output_name, transient_mode = ARMS[args.arm]
    durable = RAW_ROOT / output_name
    accepted = json.loads((BASE / "command.json").read_text())
    if sha(Path(accepted["argv"][2])) != "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8":
        raise RuntimeError("accepted config changed")
    durable.mkdir(parents=True, exist_ok=True)
    traces = durable / "traces"
    if traces.exists():
        shutil.rmtree(traces)
    traces.mkdir()
    payload = (BASE / "traces/kernel-17039-ctx_0x5ddb6907c160.traceg.xz").resolve()
    (traces / payload.name).symlink_to(payload)
    (traces / "kernelslist.g").write_text(payload.name + "\n")
    command = list(accepted["argv"])
    command[0] = str(BINARY)
    command[2] = "/root/workspace/accel-sim-framework-awma-r101-transient-l2-arch-174-v1/configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config"
    env = os.environ.copy()
    for key in tuple(env):
        if key.startswith("AWMA_TRANSIENT_L2") or key.startswith("GPGPUSIM_"):
            env.pop(key)
    env.update({key: str(value) for key, value in accepted["environment"].items()
                if key.startswith("GPGPUSIM_")})
    env["GPGPUSIM_VM_COVERAGE_KERNEL_UID"] = "all"
    env["GPGPUSIM_ROOT"] = str(RUNTIME / "src/gpgpu-sim")
    env["GPGPUSIM_POWER_MODEL"] = str(RUNTIME / "src/gpgpu-sim/src/accelwattch") + "/"
    env["LD_LIBRARY_PATH"] = f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH', '')}"
    transient_environment = {}
    if transient_mode is not None:
        sidecar = Path("/root/workspace/accel-sim-framework-awma-r101-transient-l2-arch-174-v1/util/vm_tlb/awma/r101_transient_l2_arch_v1/directed_no_overlap_runtime.tsv")
        env["AWMA_TRANSIENT_L2_MODE"] = transient_mode
        env["AWMA_TRANSIENT_L2_DIAGNOSTICS"] = "1"
        env["AWMA_TRANSIENT_L2_SIDECAR"] = str(sidecar)
        env["AWMA_TRANSIENT_L2_DRAIN"] = "1"
        transient_environment = {key: env[key] for key in
                                 ("AWMA_TRANSIENT_L2_MODE", "AWMA_TRANSIENT_L2_DIAGNOSTICS",
                                  "AWMA_TRANSIENT_L2_SIDECAR", "AWMA_TRANSIENT_L2_DRAIN")}
    receipt = {
        "stage": "AWMA_R101_TRANSIENT_L2_ARCH_EXPLORATION_V1",
        "role": "DEFAULT_OFF_EQUIVALENCE",
        "accepted_run": str(BASE), "accepted_binary_sha256": "a866c219b7d71a3075e032c9179bcd679074d6f2e9f1750b435170aabb413b24",
        "candidate_binary_sha256": sha(BINARY), "trace_sha256": sha(payload),
        "config_sha256": sha(Path(command[2])), "argv": command,
        "transient_environment": transient_environment, "expected": EXPECTED,
    }
    (durable / "command.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    (durable / "start_utc.txt").write_text(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + "\n")
    started = time.monotonic()
    with (durable / "run.log").open("w") as stdout, (durable / "run.stderr").open("w") as stderr:
        rc = subprocess.run(command, cwd=durable, env=env, stdout=stdout, stderr=stderr,
                            timeout=7200).returncode
    (durable / "rc.txt").write_text(f"{rc}\n")
    (durable / "wall_seconds.txt").write_text(f"{time.monotonic()-started:.6f}\n")
    text = (durable / "run.log").read_text(errors="strict")
    coverage = [line for line in text.splitlines() if line.startswith("AWMA_VM_COVERAGE ")]
    passed = (rc == 0 and scalar(text, "gpu_tot_sim_cycle") == EXPECTED["cycles"] and
              scalar(text, "gpu_tot_sim_insn") == EXPECTED["instructions"] and
              scalar(text, "gpu_tot_issued_cta") == EXPECTED["ctas"] and coverage and
              "untranslated=0" in coverage[-1] and "unobserved=0" in coverage[-1] and
              f"unique={EXPECTED['unique']}" in coverage[-1] and
              "kernel_uid=1" in coverage[-1])
    if args.arm == "default_off":
        passed = passed and "awma_transient_l2_mode" not in text
    else:
        passed = (passed and f"awma_transient_l2_mode = {transient_mode}" in text and
                  "awma_transient_l2_transient_accesses = 0" in text and
                  "awma_transient_l2_terminal_quiescent = 1" in text and
                  "awma_transient_l2_launched_kernels = 1" in text and
                  "awma_transient_l2_pre_transitions = 1" in text and
                  "awma_transient_l2_post_transitions = 1" in text and
                  "awma_transient_l2_dead_eviction_drops = 0" in text and
                  "awma_transient_l2_oracle_drop_bytes = 0" in text and
                  "awma_transient_l2_outstanding_l2_writebacks = 0" in text and
                  "AWMA_TRANSIENT_L2_DRAIN enabled=1 cycles=0 gpu_active=0 "
                  "l2_writeback_active=0 max_limit_hit=0 gpu_deadlock=0"
                  in text)
    result = {"status": "PASS" if passed else "FAIL", "rc": rc,
              "cycles": scalar(text, "gpu_tot_sim_cycle"),
              "instructions": scalar(text, "gpu_tot_sim_insn"),
              "ctas": scalar(text, "gpu_tot_issued_cta"),
              "coverage": coverage[-1] if coverage else "MISSING",
              "arm": args.arm,
              "default_off_output_absent": "awma_transient_l2_mode" not in text,
              "explicit_none_terminal_quiescent":
                  "awma_transient_l2_terminal_quiescent = 1" in text}
    (durable / "OFF_EQUIVALENCE.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
