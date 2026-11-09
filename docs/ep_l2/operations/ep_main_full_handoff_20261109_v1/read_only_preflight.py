#!/usr/bin/env python3
"""Print current EP-L2 handoff state. No writes, budgets, models or asset hashes.

Run on hrl-174-new: python3 -B read_only_preflight.py [--verify-remote]
This checks metadata/liveness, not scientific qualification or launch admission.
"""
import sys

sys.dont_write_bytecode = True

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-remote", action="store_true")
    args = parser.parse_args()
    native = Path("/root/data/ep_l2_dtc_l1_native_v2")
    project = Path("/root/data/ep_l2_full_workload_performance_20261027_v1")
    registry_path = native / "control/science_authority/NATIVE_SCIENCE_REGISTRY.json"
    epoch_path = native / "control/CURRENT_SCIENCE_EPOCH.json"
    for _ in range(5):
        registry_bytes = registry_path.read_bytes()
        registry = json.loads(registry_bytes)
        epoch = json.loads(epoch_path.read_bytes())
        before = hashlib.sha256(registry_bytes).hexdigest()
        if before == epoch["native_registry_sha256"] == digest(registry_path):
            break
    else:
        raise RuntimeError("Registry/epoch changed during read; rerun readonly audit")

    model_processes = []
    ep_supervisor_candidates = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            argv = [x.decode(errors="replace") for x in
                    (proc / "cmdline").read_bytes().split(b"\0") if x]
            if not argv:
                continue
            if any(x.endswith("/accel-sim.out") for x in argv):
                model_processes.append({"pid": int(proc.name), "argv": argv})
            if Path(argv[0]).name.startswith("python") and any(
                x.startswith(str(project)) and x.endswith(".py") and any(
                    token in x.lower() for token in
                    ("dispatcher", "supervisor", "finite_main")
                ) for x in argv[1:]
            ):
                ep_supervisor_candidates.append({"pid": int(proc.name), "argv": argv})
        except OSError:
            continue

    requests = []
    for request_id, row in registry["registered_future_requests"].items():
        if not request_id.startswith("EP_"):
            continue
        consumed = row.get("consumed", 0)
        requests.append({
            "request_id": request_id,
            "state": row.get("state"),
            "budget": row.get("budget"),
            "remaining": row.get("remaining"),
            "consumed_records": len(consumed) if isinstance(consumed, dict) else consumed,
            "reserved_write_bytes": row.get("reserved_write_bytes", 0),
            "remaining_does_not_grant_new_scope_permission": True,
        })
    result = {
        "status": "READ_ONLY_METADATA_OBSERVATION_NOT_ADMISSION",
        "observed_Asia_Shanghai": datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        "host": os.uname().nodename,
        "epoch": epoch["epoch"],
        "epoch_state": epoch["state"],
        "holder": epoch["holder"],
        "registry_epoch_SHA_match": True,
        "registry_sha256": before,
        "shared_native_sha256": digest(native / "bin/native"),
        "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
        "mount_namespace": os.readlink("/proc/self/ns/mnt"),
        "model_or_strace_wrapper_candidates": model_processes,
        "model_count_requires_PID_maps_start_ticks_and_claim_join": True,
        "EP_supervisor_candidates": ep_supervisor_candidates,
        "EP_requests": requests,
        "df_bytes": subprocess.check_output(
            ["df", "-B1", "/root/data", "/root/share/mnt164"], text=True),
        "true164_mount": json.loads(subprocess.check_output(
            ["findmnt", "-J", "-T", "/root/share/mnt164"], text=True)),
        "cgroup": {
            name: (Path("/sys/fs/cgroup") / name).read_text().strip()
            for name in ("memory.max", "memory.current", "memory.events",
                         "cpu.max", "cpuset.cpus.effective")
            if (Path("/sys/fs/cgroup") / name).exists()
        },
        "MemAvailable": next(x for x in Path("/proc/meminfo").read_text().splitlines()
                             if x.startswith("MemAvailable:")),
        "no_authority_or_asset_write": True,
        "no_model_start_or_budget_consume": True,
    }
    if args.verify_remote:
        repo = project / "handoff/ep_l2_main_full_handoff_20261109_v1/review"
        result["latest_research_remote_ref"] = subprocess.check_output(
            ["git", "ls-remote", "origin",
             "refs/heads/hrl/ep-l2-next-cost-aware-architecture-20261107-v1"],
            cwd=repo, text=True).strip()
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
