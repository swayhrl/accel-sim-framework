#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import run_post_classic_l1_zero_diagnostic as common


DURABLE = Path(
    "/root/share/mnt164/huangrulin/awma_post_classic_baseline_residual_discovery_v1/observatory_raw"
)


def overlay_10_80() -> list[str]:
    result = common.vm_overlay()
    index = result.index("-gpgpu_vm_l1_tlb_lookup_latency")
    result[index + 1] = "10"
    return result


def run(target: str, timeout_seconds: int, overwrite: bool) -> dict[str, object]:
    family, filename, trace_sha, reference_cycles = common.TARGETS[target]
    payload = common.INPUTS / filename
    if common.sha256(payload) != trace_sha:
        raise RuntimeError(f"{target}: trace SHA mismatch")
    out = DURABLE / f"{target}_REFERENCE_OBSERVATORY_L1_10_80"
    rc_path = out / "rc.txt"
    if not overwrite and rc_path.is_file() and rc_path.read_text().strip() == "0":
        return {"target": target, "rc": 0, "status": "SKIPPED_EXISTING_PASS"}
    out.mkdir(parents=True, exist_ok=True)
    traces = out / "traces"
    if traces.exists():
        shutil.rmtree(traces)
    traces.mkdir()
    (traces / filename).symlink_to(payload)
    (traces / "kernelslist.g").write_text(filename + "\n")

    environment = os.environ.copy()
    for key in tuple(environment):
        if key.startswith("GPGPUSIM_AWMA_") or key in (
            "GPGPUSIM_READY_APPLICATION_V2",
            "GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH",
        ):
            environment.pop(key, None)
    environment["LD_LIBRARY_PATH"] = (
        f"{common.CORE_LIB}:{environment.get('LD_LIBRARY_PATH', '')}"
    )
    environment.update(
        GPGPUSIM_AWMA_TRANSLATION_CANDIDATE="warp_vpn_dedup_reference",
        GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH="1",
        GPGPUSIM_AWMA_PASSIVE_MEMO_OBSERVER="0",
        GPGPUSIM_AWMA_MECHANISM_DIAGNOSTICS="1",
        GPGPUSIM_AWMA_OWNER_WAIT_DIAGNOSTICS="1",
        GPGPUSIM_AWMA_BOTTLENECK_OBSERVATORY="1",
        GPGPUSIM_VM_COVERAGE_KERNEL_UID="1",
        GPGPUSIM_READY_APPLICATION_DIAGNOSTICS="1",
        GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS="1",
    )
    command = [
        "nice", "-n", "10", str(common.BINARY),
        "-config", str(common.CONFIG),
        "-trace", "traces/kernelslist.g",
    ] + common.trace_args() + overlay_10_80()
    receipt = {
        "stage": common.STAGE,
        "target": target,
        "family": family,
        "arm": "REFERENCE_OBSERVATORY_L1_10_80",
        "scientific_role": "BEHAVIOR_NEUTRAL_OBSERVATIONAL_LOCALIZATION",
        "expected_reference_cycles": reference_cycles,
        "lane_b_authority": "9efe8236e0c6338addfef5480e1da91bffb504eb",
        "observatory_authority": "b85d388abe98e5da70b749b52075c33fad7cede4",
        "argv": command,
        "environment": {
            key: environment[key]
            for key in sorted(environment)
            if key.startswith("GPGPUSIM_")
        },
        "binary_sha256": common.sha256(common.BINARY),
        "config_sha256": common.sha256(common.CONFIG),
        "trace_config_sha256": common.sha256(common.TRACE_CONFIG),
        "trace_sha256": trace_sha,
    }
    (out / "command.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    (out / "start_utc.txt").write_text(common.utc() + "\n")
    started = time.monotonic()
    with (out / "run.log").open("w") as stdout, (out / "run.stderr").open(
        "w"
    ) as stderr:
        try:
            rc = subprocess.run(
                command,
                cwd=out,
                env=environment,
                stdout=stdout,
                stderr=stderr,
                timeout=timeout_seconds,
            ).returncode
        except subprocess.TimeoutExpired:
            rc = 124
    rc_path.write_text(f"{rc}\n")
    (out / "end_utc.txt").write_text(common.utc() + "\n")
    (out / "wall_seconds.txt").write_text(f"{time.monotonic() - started:.6f}\n")
    return {"target": target, "rc": rc, "status": "PASS" if rc == 0 else "FAIL"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=2, choices=(1, 2))
    parser.add_argument("--timeout-seconds", type=int, default=21600)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    DURABLE.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [
            pool.submit(run, target, args.timeout_seconds, args.overwrite)
            for target in common.TARGETS
        ]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, sort_keys=True), flush=True)
    results.sort(key=lambda row: str(row["target"]))
    (DURABLE / "launcher_results.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n"
    )
    return 0 if all(row["rc"] == 0 for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
