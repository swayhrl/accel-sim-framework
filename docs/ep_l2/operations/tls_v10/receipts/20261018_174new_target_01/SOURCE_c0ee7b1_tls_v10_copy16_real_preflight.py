#!/usr/bin/env python3
"""Fresh read-only old174 P9 B0001 preflight; never stages or releases data."""

from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

import tls_v10_copy_only16g_gate as policy
import tls_v10_copy_only20g_gate as old


HERE = Path(__file__).resolve().parent
TEST_RECEIPT = HERE / "TLS_V10_COPY_ONLY_16G_POLICY_TEST_RECEIPT.json"
PASS_RECEIPT = HERE / "TLS_V10_COPY_ONLY_16G_GATE_PASS_B0001.json"
LANE_COMMIT = "94fd48b69b37adb692e6152301b317f5f2e6a1e9"
LANE_RECEIPT_PATH = "docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/RECEIPT.json"
FIRST_REL = "matrix-d10fe92/cfd_097k.baseline.dynamic.driver.out"
FIRST_SHA = "bc85cb82388094a4cc5f7b9bb58893bd2982ad79e66a29e4fd20fa35d5ac58e6"
TARGET_ADOPTION = old.BRIDGE / "TLS_V10_COPY16_TARGET_AUTHORITY_ADOPTION_RECEIPT.json"
TARGET_REQUEST = old.BRIDGE / "TLS_V10_P9_PUBLIC_TARGET_SOLE_WINDOW_READY.json"
SCRIPT_SHA = {
    "/workspace/worktrees/accel-sim-tls-cache/experiments/tls_cache/finalize_p9_matrix.sh": "33f1372a280e720c07bbc94cd9985f6be2818cb0a17d3dd9819c4cfde87ad42c",
    "/workspace/worktrees/accel-sim-tls-cache/experiments/tls_cache/merge_p9_staging.sh": "cd543db26b12cf827a06cdaa61d3f7284e00898bb1a29886ac72a5d391d0e437",
    "/workspace/worktrees/accel-sim-tls-cache/experiments/tls_cache/verify_p9_matrix.sh": "d17b9cc3d927abc07db8b79bba1c0c8166ea17d469e5e367fbc5dc17bb2ab8bc",
    "/workspace/worktrees/accel-sim-tls-cache/experiments/tls_cache/analyze_p9_matrix.sh": "1c66f833307337cb2f7c943236bc8465861d7115058731b50cd36f0fe5349e3a",
    "/workspace/worktrees/accel-sim-tls-cache/experiments/tls_cache/capture_p9_provenance.sh": "fc0c5e0569ecf9f79ecb5617b1e14af649c028cc712b4ba7ddfb3bed9fb4f431",
    "/workspace/worktrees/accel-sim-decoupled-l2/experiments/v100_trace_campaign/scripts/offload_archives.sh": "6aedde9b48e68b8e9403ae275897ffb08da711831efcaea04a6724044af5dc48",
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def lane_closure():
    api = "repos/swayhrl/accel-sim-framework/contents/" + LANE_RECEIPT_PATH + "?ref=" + LANE_COMMIT
    raw = subprocess.check_output(["gh", "api", api, "--jq", ".content"])
    import base64
    payload = base64.b64decode(raw)
    obj = json.loads(payload)
    return (obj.get("status") == "BOUNDED_FINAL_INTAKE_COMPLETE_REMOTE_DATA_VERIFIED" and
            obj.get("active_runs") == []), sha(payload)


def first_source():
    manifest_raw = (HERE / "TLS_V10_P9_PUBLIC_TARGET_TRANSACTION_MANIFEST.json").read_bytes()
    if sha(manifest_raw) != old.MANIFEST_SHA256:
        return False, None
    entry = next((v for v in json.loads(manifest_raw)["files"] if v["relative_path"] == FIRST_REL), None)
    if entry is None or entry["sha256"] != FIRST_SHA:
        return False, None
    root = Path(old.SOURCE_ROOT)
    if root.resolve(strict=True) != root:
        return False, None
    parent = root / "matrix-d10fe92"
    if parent.resolve(strict=True) != parent:
        return False, None
    dirfd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fd = os.open(Path(FIRST_REL).name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=dirfd)
        try:
            before = os.fstat(fd)
            body = os.read(fd, entry["size"] + 1)
            after = os.fstat(fd)
            pathstat = os.stat(Path(FIRST_REL).name, dir_fd=dirfd, follow_symlinks=False)
            names = {"st_dev": "dev", "st_ino": "inode", "st_nlink": "nlink",
                     "st_uid": "uid", "st_gid": "gid", "st_mtime_ns": "mtime_ns",
                     "st_ctime_ns": "ctime_ns", "st_size": "size"}
            exact = (stat.S_ISREG(before.st_mode) and before == after and
                     all(getattr(before, k) == entry[v] for k, v in names.items()) and
                     before.st_mode & 0o777 == entry["mode"] and
                     before.st_blocks * 512 == entry["allocated"] and
                     pathstat.st_ino == before.st_ino and pathstat.st_dev == before.st_dev and
                     len(body) == entry["size"] and sha(body) == FIRST_SHA)
            return exact, {"path": str(root / FIRST_REL), "sha256": sha(body),
                           "dev": before.st_dev, "inode": before.st_ino,
                           "ctime_ns": before.st_ctime_ns, "mtime_ns": before.st_mtime_ns,
                           "nlink": before.st_nlink, "size": before.st_size}
        finally:
            os.close(fd)
    finally:
        os.close(dirfd)


def physical_refs():
    """Full bounded proc scan, including maps; vanished PIDs are harmless."""
    root = old.SOURCE_ROOT
    hits = []
    unknown = []
    lane_pids = []
    transfer_pids = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdecimal() or int(proc.name) == os.getpid():
            continue
        try:
            args = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
            cwd = os.readlink(proc / "cwd")
            fds = [os.readlink(fd) for fd in (proc / "fd").iterdir()]
            maps = (proc / "maps").read_text(errors="replace")
            stat_text = (proc / "stat").read_text()
            start_ticks = int(stat_text[stat_text.rfind(") ") + 2:].split()[19])
        except FileNotFoundError:
            continue
        except (PermissionError, OSError, ValueError) as exc:
            unknown.append({"pid": int(proc.name), "error": type(exc).__name__})
            continue
        targets = [v for v in [args, cwd, maps, *fds] if root in v]
        if targets:
            hits.append({"pid": int(proc.name), "start_ticks": start_ticks,
                         "args": args[:2048], "cwd": cwd, "matching_refs": targets[:8]})
        lower = args.lower()
        if ("lane5" in lower or "ep_l2_ft20261016_shared" in lower) and "copy16_real_preflight" not in lower:
            lane_pids.append({"pid": int(proc.name), "start_ticks": start_ticks, "args": args[:512]})
        if (("tls_v10" in lower or "tls-v10" in lower or "rsync" in lower) and
                "copy16_real_preflight" not in lower and "rg " not in lower):
            transfer_pids.append({"pid": int(proc.name), "start_ticks": start_ticks, "args": args[:512]})
    return hits, unknown, lane_pids, transfer_pids


def inspect():
    snap = old.real_snapshot()
    now = datetime.now(timezone.utc)
    b = old.GateInput(**snap["input"])
    reasons = []
    try:
        closure_ok, closure_sha = lane_closure()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        closure_ok, closure_sha = False, None
        reasons.append("LANE_CLOSURE_REMOTE_READBACK_FAILED:" + type(exc).__name__)
    hits, unknown, lane_pids, transfers = physical_refs()
    scripts = {name: sha(Path(name).read_bytes()) for name in SCRIPT_SHA}
    scripts_exact = scripts == SCRIPT_SHA
    if not scripts_exact:
        reasons.append("ACTIVE_SCRIPT_SHA_CHANGED")
    script_texts = {name: Path(name).read_text() for name in SCRIPT_SHA}
    # These active script chains have exact separate roots.  A changed script
    # or future P9_PUBLIC reference makes the proof fail closed.
    scheduled_clear = scripts_exact and all(
        old.SOURCE_ROOT not in value and "tls-cache-p9-public-v1" not in value
        for value in script_texts.values())
    target_raw = TARGET_REQUEST.read_bytes()
    target_req = json.loads(target_raw)
    adoption = json.loads(TARGET_ADOPTION.read_bytes())
    target_exact = (sha(target_raw) == old.TARGET_REQUEST_SHA256 and
                    target_req["window_id"] == old.WINDOW and
                    target_req["txid"] == old.TXID and
                    target_req["selector_sha256"] == old.SELECTOR and
                    target_req["canonical_manifest_sha256"] == old.MANIFEST_SHA256 and
                    target_req["target_root_native164"] == old.TARGET_ROOT and
                    target_req["range"]["relative_path"] == FIRST_REL and
                    target_req["range"]["length"] == 144 and
                    adoption.get("coordination_commit") == "f8baa3acfdbd2f420c108d4d4baff0432ef38822" and
                    adoption.get("source_signed_COPY_ONLY_16G_GATE_PASS_received") is False)
    source_ok, source_entry = first_source()
    staged = Path(target_req["range"]["bridge_payload_path"])
    payload_absent = not staged.exists() and not staged.parent.parent.exists()
    test = json.loads(TEST_RECEIPT.read_bytes())
    tests_exact = test["passed"] == 45 and test["failed"] == 0 and test["gate_code_sha256"] == sha((HERE / "tls_v10_copy_only16g_gate.py").read_bytes())
    boot_id = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    b = replace(b, policy_id=policy.POLICY_ID, amendment_sha256=policy.AUTHORITY_SHA256,
                planned_overlay_write_bytes=old.MIB,
                copy_lease_authorized=(closure_ok and not lane_pids and not transfers and
                                       snap["registry"]["active_leases"] == 0 and payload_absent),
                physical_scan_complete=not unknown,
                candidate_root_idle=not hits,
                scheduled_readers_clear=scheduled_clear,
                first_source_identity_ok=source_ok,
                first_source_sha_refreshed=source_ok,
                target_request_present_and_exact=target_exact,
                sole_source_sender=not transfers,
                sole_target_receiver=adoption.get("target_resources_snapshot", {}).get("receiver_idle") is True,
                planned_bridge_staged_bytes=144)
    item = policy.Copy16Input(b, policy.APPROVAL_SHA256, 144, target_exact,
                              snap["local_frozen_binding_exact"], closure_ok, not lane_pids)
    result = policy.evaluate(item)
    if not payload_absent:
        reasons.append("BRIDGE_PAYLOAD_PREEXISTS_OR_TX_DIRECTORY_PRESENT")
    if not tests_exact:
        reasons.append("POLICY_TEST_RECEIPT_DRIFT")
    if not scheduled_clear:
        reasons.append("ACTIVE_SCRIPT_FUTURE_SET_UNPROVEN")
    if reasons:
        result["reasons"].extend(reasons)
        result["decision"] = "RESOURCE_HOLD"
    return {"schema": "TLS_V10_COPY_ONLY16G_OLD174_REAL_PREFLIGHT_V1",
            "at_utc": now.isoformat(), "policy_id": policy.POLICY_ID,
            "authority_sha256": policy.AUTHORITY_SHA256,
            "user_approval_sha256": policy.APPROVAL_SHA256,
            "source_originals": "SOURCE_KEEP", "window_id": old.WINDOW,
            "txid": old.TXID, "selector_sha256": old.SELECTOR,
            "target_request_sha256": sha(target_raw), "target_root_native164": old.TARGET_ROOT,
            "boot_id": boot_id, "lane_closure_commit": LANE_COMMIT,
            "lane_closure_receipt_sha256": closure_sha,
            "lane_registry_age_seconds": snap["registry"]["age_seconds"],
            "lane_current_active_runs": snap["registry"]["active_runs"],
            "lane_current_active_leases": snap["registry"]["active_leases"],
            "lane_physical_pids": lane_pids,
            "candidate_root_process_refs": hits, "proc_unreadable": unknown,
            "other_transfer_pids": transfers,
            "active_script_sha256": scripts,
            "active_script_chain_separate_from_P9_PUBLIC": scheduled_clear,
            "first_source": source_entry, "test_receipt_sha256": sha(TEST_RECEIPT.read_bytes()),
            "input": asdict(b), "decision": result,
            "scientific_payload_staged_bytes": 0, "source_unlink_count": 0}


if __name__ == "__main__":
    result = inspect()
    if len(sys.argv) == 2 and sys.argv[1] == "--write-pass":
        if result["decision"]["decision"] != "POLICY_ELIGIBLE_NOT_READY":
            raise SystemExit("HOLD: " + json.dumps(result["decision"]["reasons"]))
        result["schema"] = "TLS_V10_COPY_ONLY_16G_GATE_PASS_B0001_V1"
        result["status"] = "COPY_ONLY_16G_GATE_PASS_NOT_READY"
        with PASS_RECEIPT.open("x") as out:
            json.dump(result, out, sort_keys=True, indent=2)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
    elif len(sys.argv) != 1:
        raise SystemExit("usage: tls_v10_copy16_real_preflight.py [--write-pass]")
    print(json.dumps({"at_utc": result["at_utc"], "decision": result["decision"],
                      "workspace_available_bytes": result["input"]["workspace_available_bytes"],
                      "share_available_bytes": result["input"]["share_available_bytes"],
                      "memory_available_bytes": result["input"]["memory_available_bytes"],
                      "candidate_root_refs": len(result["candidate_root_process_refs"]),
                      "lane_physical_pids": len(result["lane_physical_pids"]),
                      "other_transfer_pids": len(result["other_transfer_pids"])}, sort_keys=True))
