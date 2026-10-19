#!/usr/bin/env python3
"""Fail-closed, exact-window P9 COPY_ONLY source runner for B0004+.

This module has no CLI and no automatic production invocation.  A caller must
provide one target-authored binding JSON and a fresh evidence provider.  The
production context pins the sole old174 P9 asset and bridge; fixture contexts
are deliberately explicit.  No method unlinks a source file.
"""

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess

import tls_v10_copy_only16g_gate as policy
import tls_v10_copy_only20g_gate as old
import tls_v10_copy16_real_preflight as real
import tls_v10_p9_grouped_source_range as sender


MIB = 1024 * 1024
TARGET_RECEIPTS = "docs/ep_l2/operations/tls_v10/receipts/20261018_174new_target_01/"
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
WINDOW_RE = re.compile(r"^TLS_V10_P9_PUBLIC_B([0-9]{4})$")
FIELDS = ("dev", "inode", "nlink", "uid", "gid", "mode", "size",
          "mtime_ns", "ctime_ns", "allocated")


class Hold(sender.Hold):
    """No retry or cleanup is implied; preserve any uncertain stage."""


@dataclass(frozen=True)
class Context:
    source_root: Path
    bridge: Path
    source_repo: Path
    target_repo: Path
    manifest: Path
    plan: Path
    receipt_dir: Path
    file_count: int = 141
    production: bool = False


def production_context(source_repo, target_repo):
    """Only the historical frozen P9 root and single bridge are writable."""
    here = Path(__file__).resolve().parent
    return Context(Path(old.SOURCE_ROOT), old.BRIDGE, Path(source_repo),
                   Path(target_repo), here / "TLS_V10_P9_PUBLIC_TARGET_TRANSACTION_MANIFEST.json",
                   old.BRIDGE / "TLS_V10_P9_PUBLIC_INACTIVE_BATCHING_PROPOSAL_AFTER_B0001.json",
                   here, production=True)


def production_evidence(binding_path):
    """Fresh real old174 snapshot, not a caller-supplied boolean affidavit."""
    binding = _json(Path(binding_path).read_bytes())
    snapshot = old.real_snapshot()
    hits, unreadable, lane_pids, transfers = real.physical_refs()
    scripts = {name: sha(Path(name).read_bytes()) for name in real.SCRIPT_SHA}
    scheduled_clear = scripts == real.SCRIPT_SHA and all(
        old.SOURCE_ROOT not in Path(name).read_text() and
        "tls-cache-p9-public-v1" not in Path(name).read_text()
        for name in real.SCRIPT_SHA)
    lane_closed, _ = real.lane_closure()
    registry = snapshot["registry"]
    b = old.GateInput(**snapshot["input"])
    b = replace(b, policy_id=policy.POLICY_ID,
                amendment_sha256=policy.AUTHORITY_SHA256,
                window_id=binding["window_id"],
                target_request_sha256=binding["target_request_sha256"],
                planned_overlay_write_bytes=MIB,
                planned_memory_bytes=64 * MIB,
                copy_lease_authorized=lane_closed and not lane_pids and not transfers and
                                      registry["active_leases"] == 0,
                physical_scan_complete=not unreadable and b.physical_scan_complete,
                candidate_root_idle=not hits and b.candidate_root_idle,
                scheduled_readers_clear=scheduled_clear,
                sole_source_sender=not transfers,
                sole_target_receiver=True)
    return {"base": b, "lane_final_closure_verified": lane_closed,
            "lane_physical_clear": not lane_pids,
            "source_reader_clear": not hits and not unreadable,
            "scheduled_reader_clear": scheduled_clear,
            "sole_sender_clear": not transfers,
            "receiver_clear": True}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _require(ok, reason):
    if not ok:
        raise Hold(reason)


def _json(raw):
    try:
        return json.loads(raw)
    except (ValueError, UnicodeDecodeError) as error:
        raise Hold("invalid JSON: " + str(error)) from error


def _git_raw(repo, commit, relative_path):
    _require(bool(COMMIT_RE.fullmatch(commit)), "invalid Git commit")
    _require(relative_path.startswith(TARGET_RECEIPTS) and
             ".." not in Path(relative_path).parts and not Path(relative_path).is_absolute(),
             "target receipt path outside pinned directory")
    try:
        return subprocess.check_output(["git", "-C", str(repo), "show",
                                        commit + ":" + relative_path], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as error:
        raise Hold("target Git raw receipt unavailable") from error


def _source_git_raw(repo, commit, path):
    _require(bool(COMMIT_RE.fullmatch(commit)), "invalid source commit")
    try:
        relative = path.relative_to(repo)
    except ValueError as error:
        raise Hold("source receipt outside repo") from error
    try:
        return subprocess.check_output(["git", "-C", str(repo), "show",
                                        commit + ":" + str(relative)], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as error:
        raise Hold("source Git raw receipt unavailable") from error


def _no_clobber_json(path, item):
    raw = (json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(raw)
            out.flush()
            os.fsync(out.fileno())
    except BaseException:
        # Never discard ambiguous evidence, including a short write.
        raise
    parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(parent)
    finally:
        os.close(parent)
    return sha(raw)


def _check_context(ctx):
    _require(ctx.source_root.is_absolute() and ctx.bridge.is_absolute() and
             ctx.manifest.is_absolute() and ctx.plan.is_absolute() and
             ctx.receipt_dir.is_absolute(), "context must use absolute paths")
    _require(ctx.source_root.resolve(strict=True) == ctx.source_root and
             ctx.bridge.resolve(strict=True) == ctx.bridge,
             "source or bridge symlink")
    if ctx.production:
        _require(str(ctx.source_root) == old.SOURCE_ROOT and ctx.bridge == old.BRIDGE and
                 ctx.file_count == 141 and ctx.manifest ==
                 Path(__file__).resolve().parent / "TLS_V10_P9_PUBLIC_TARGET_TRANSACTION_MANIFEST.json" and
                 ctx.plan == old.BRIDGE / "TLS_V10_P9_PUBLIC_INACTIVE_BATCHING_PROPOSAL_AFTER_B0001.json" and
                 ctx.receipt_dir == Path(__file__).resolve().parent,
                 "production context not pinned to exact P9 asset")


def _range_sha(root, row, offset, length):
    parts = sender._parts(row["relative_path"])
    parent, fd = sender._source_fd(root, parts)
    try:
        expected = {k: row[k] for k in FIELDS}
        before = os.fstat(fd)
        named = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        _require(stat.S_ISREG(before.st_mode) and
                 sender._fingerprint(before) == expected and
                 sender._fingerprint(named) == expected, "range source identity drift")
        os.lseek(fd, offset, os.SEEK_SET)
        h = hashlib.sha256()
        remaining = length
        while remaining:
            block = os.read(fd, min(MIB, remaining))
            _require(bool(block), "short source range")
            h.update(block)
            remaining -= len(block)
        named_after = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        _require(sender._fingerprint(os.fstat(fd)) == expected and
                 sender._fingerprint(named_after) == expected, "range source changed during SHA")
        return h.hexdigest()
    finally:
        os.close(fd)
        os.close(parent)


def _all_metadata(ctx, manifest):
    files = manifest["files"]
    _require(len(files) == ctx.file_count and len({v["relative_path"] for v in files}) == len(files),
             "frozen file cardinality/duplicate mismatch")
    if ctx.production:
        _require(len(manifest["directories"]) == 4, "frozen directory count mismatch")
    for row in manifest["directories"]:
        rel = row["relative_path"]
        path = ctx.source_root if rel == "." else ctx.source_root.joinpath(*sender._parts(rel))
        _require(stat.S_ISDIR(os.lstat(path).st_mode) and path.resolve(strict=True) == path,
                 "frozen directory replaced by symlink/non-directory")
    for row in files:
        path = ctx.source_root.joinpath(*sender._parts(row["relative_path"]))
        info = os.lstat(path)
        _require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                 sender._fingerprint(info) == {k: row[k] for k in FIELDS},
                 "frozen source metadata drift: " + row["relative_path"])


def _full_plan_coverage(plan, manifest):
    files = {v["relative_path"]: v for v in manifest["files"]}
    ranges = {name: [] for name in files}
    total = 0
    for batch in plan["batches"]:
        amount = 0
        _require(batch.get("txid") == plan["txid"] and
                 batch.get("selector_sha256") == plan["selector_sha256"] and
                 batch.get("manifest_sha256") == plan["manifest_sha256"],
                 "plan batch identity mismatch")
        _require(len(batch["entries"]) <= 128, "batch range count cap")
        for entry in batch["entries"]:
            rel = entry["relative_path"]
            _require(rel in files, "plan foreign file")
            row = files[rel]
            off, length = entry["offset"], entry["length"]
            _require(type(off) is int and type(length) is int and
                     off >= 0 and 0 < length <= 128 * MIB and off + length <= row["size"] and
                     entry["original_size"] == row["size"] and
                     entry["original_sha256"] == row["sha256"], "plan range not frozen")
            ranges[rel].append((off, length))
            amount += length
        _require(amount == batch["raw_bytes"] and amount <= 128 * MIB, "plan batch raw cap")
        total += amount
    for name, row in files.items():
        end = 0
        for offset, length in sorted(ranges[name]):
            _require(offset == end, "plan gap/overlap: " + name)
            end += length
        _require(end == row["size"], "plan missing original bytes: " + name)
    _require(total == sum(v["size"] for v in files.values()), "plan total mismatch")


def _window_paths(ctx, window):
    return (ctx.receipt_dir / (window + "_SOURCE_GATE_PASS_COPY16.json"),
            ctx.receipt_dir / (window + "_SOURCE_READY_COPY16.json"),
            ctx.bridge / (window + "_SOURCE_READY_COPY16.json"))


def _bridge_allocated(bridge):
    """Count staged payload trees, not old top-level transaction receipts.

    The shared bridge retains ~196 MiB of small R1/R2 JSON evidence.  The
    256 MiB protocol cap is for in-flight payload staging, as in the qualified
    B0003 sender; counting historical receipts would make every 128 MiB
    window fail without improving payload isolation.
    """
    total = 0
    seen = 0
    for parent, dirs, files in os.walk(bridge, followlinks=False):
        for name in [*dirs, *files]:
            seen += 1
            _require(seen <= 10000, "bridge occupancy scan object cap")
            info = os.lstat(Path(parent) / name)
            _require(not stat.S_ISLNK(info.st_mode), "bridge symlink")
            if Path(parent) != Path(bridge) or stat.S_ISDIR(info.st_mode):
                total += info.st_blocks * 512
                _require(total <= 256 * MIB, "bridge staged payload cap")
    return total


class ExactWindowRunner:
    """Explicit per-window controller; evidence() must take a fresh snapshot."""

    def __init__(self, context, binding_path, evidence):
        self.ctx, self.binding_path, self.evidence = context, Path(binding_path), evidence

    def _inspect(self, *, stage_must_be_absent):
        ctx = self.ctx
        _check_context(ctx)
        binding_raw = self.binding_path.read_bytes()
        b = _json(binding_raw)
        _require(b.get("schema") == "TLS_V10_P9_EXACT_SOURCE_WINDOW_BINDING_V1", "binding schema")
        window = b["window_id"]
        match = WINDOW_RE.fullmatch(window)
        _require(match is not None and int(match[1]) >= 4, "only future B0004+ windows")
        index = b["plan_batch_index"]
        _require(type(index) is int and index == int(match[1]) - 1, "window/plan index")
        _require(b["txid"] == old.TXID and b["selector_sha256"] == old.SELECTOR and
                 (not ctx.production or b["canonical_manifest_sha256"] == old.MANIFEST_SHA256) and
                 b["source_root"] == str(ctx.source_root) and
                 b["target_root_native164"] == old.TARGET_ROOT and
                 b["policy_id"] == policy.POLICY_ID,
                 "exact P9 asset/policy binding")
        manifest_raw, plan_raw = ctx.manifest.read_bytes(), ctx.plan.read_bytes()
        _require(sha(manifest_raw) == b["canonical_manifest_sha256"] and
                 sha(plan_raw) == b["plan_sha256"], "manifest/plan byte identity")
        manifest, plan = _json(manifest_raw), _json(plan_raw)
        _require(plan["schema"] == "TLS_V10_INACTIVE_RAW_BATCH_PLAN_V1" and
                 plan["txid"] == b["txid"] and
                 plan["selector_sha256"] == b["selector_sha256"] and
                 plan["manifest_sha256"] == b["canonical_manifest_sha256"] and
                 plan["source_root"] == str(ctx.source_root) and
                 plan["native164_root"] == old.TARGET_ROOT and
                 len(plan["batches"]) > index and
                 manifest["source_root"] == str(ctx.source_root),
                 "frozen plan identity")
        _full_plan_coverage(plan, manifest)
        _all_metadata(ctx, manifest)
        request_name = b["target_request_name"]
        _require(request_name == window + "_TARGET_SOLE_WINDOW_REQUEST_COPY16.json",
                 "request name/window mismatch")
        request_path = ctx.bridge / request_name
        request_raw = request_path.read_bytes()
        _require(SHA_RE.fullmatch(b["target_request_sha256"]) is not None and
                 sha(request_raw) == b["target_request_sha256"] and
                 _git_raw(ctx.target_repo, b["target_request_git_commit"],
                          TARGET_RECEIPTS + request_name) == request_raw,
                 "target Git/bridge request bytes differ")
        req = _json(request_raw)
        prev = "TLS_V10_P9_PUBLIC_B%04d" % (int(match[1]) - 1)
        cleanup_name = b["prior_cleanup_name"]
        _require(cleanup_name in (prev + "_BRIDGE_CLEANUP_COPY16.json",
                                  prev + "_BRIDGE_CLEANUP_DONE_COPY16.json") and
                 req["prior_window"] == prev and
                 req["prior_window_cleanup_name"] == cleanup_name and
                 req["prior_window_cleanup_commit"] == b["prior_cleanup_git_commit"] and
                 req["prior_window_cleanup_sha256"] == b["prior_cleanup_sha256"],
                 "prior cleanup binding mismatch")
        cleanup_raw = _git_raw(ctx.target_repo, b["prior_cleanup_git_commit"],
                               TARGET_RECEIPTS + cleanup_name)
        _require(sha(cleanup_raw) == b["prior_cleanup_sha256"] and
                 (ctx.bridge / cleanup_name).read_bytes() == cleanup_raw,
                 "prior cleanup Git/bridge raw mismatch")
        cleanup = _json(cleanup_raw)
        _require(cleanup["window_id"] == prev and cleanup["txid"] == b["txid"] and
                 cleanup["source_originals"] == "SOURCE_KEEP" and
                 cleanup["source_files_deleted_by_target"] == 0 and
                 cleanup["removed_count"] > 0 and
                 cleanup["archive_and_native_every_range_reverified"] is True,
                 "prior cleanup incomplete")
        receiver_name = b["target_receiver_preflight_name"]
        _require(receiver_name == window + "_TARGET_METADATA_PREFLIGHT_COPY16.json",
                 "target receiver preflight name/window mismatch")
        receiver_raw = (ctx.bridge / receiver_name).read_bytes()
        _require(sha(receiver_raw) == b["target_receiver_preflight_sha256"] and
                 _git_raw(ctx.target_repo, b["target_receiver_preflight_git_commit"],
                          TARGET_RECEIPTS + receiver_name) == receiver_raw,
                 "target receiver Git/bridge evidence mismatch")
        receiver = _json(receiver_raw)
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(receiver["utc"])).total_seconds()
        # The source performs its own fresh live resource/reader scan at each
        # phase. A Git-pinned target preflight is a window binding, not the
        # source's live resource snapshot; allow bounded pipeline lag here.
        _require(0 <= age <= 900 and receiver["window_id"] == window and
                 receiver["receiver_idle"] is True and
                 receiver["bridge_payloads_absent"] is True and
                 receiver["next_stage_not_created_by_target"] is True and
                 receiver.get("prior_B%04d_closed" % (int(match[1]) - 1)) is True,
                 "target receiver evidence stale/not idle/prior not closed")
        expected_stage = ctx.bridge / (window + "_" + old.TXID[:12]) / "files"
        _require(req["schema"] == "TLS_V10_TARGET_GROUPED_RAW_WINDOW_V1" and
                 req["window_id"] == window and req["group"] == old.GROUP and
                 req["txid"] == b["txid"] and
                 req["selector_sha256"] == b["selector_sha256"] and
                 req["canonical_manifest_sha256"] == b["canonical_manifest_sha256"] and
                 req["source_root"] == str(ctx.source_root) and
                 req["target_root_native164"] == old.TARGET_ROOT and
                 req["source_frozen_commit"] == manifest["source_frozen_commit"] and
                 req["plan_sha256"] == b["plan_sha256"] and
                 req["plan_batch_index"] == index and
                 req["bridge_root"] == str(expected_stage) and
                 req["source_originals"] == "SOURCE_KEEP" and
                 req["source_scientific_release_authorized_by_this_window"] is False and
                 req["copy_ready"] is False and
                 req["payload_paths_created_by_target"] is False,
                 "request scope/state mismatch")
        if stage_must_be_absent:
            _require(not expected_stage.parent.exists(), "preexisting/uncertain stage; no retry")
        rows = req["ranges"]
        _require(0 < len(rows) <= 128 and len(rows) == req["range_count"] and
                 sum(v["length"] for v in rows) == req["raw_bytes"] and
                 0 < req["raw_bytes"] <= 128 * MIB,
                 "window count/raw cap")
        selected = plan["batches"][index]
        expected_entries = [{k: v[k] for k in
                             ("relative_path", "offset", "length", "original_size", "original_sha256")}
                            for v in rows]
        _require(selected["entries"] == expected_entries and
                 selected["raw_bytes"] == req["raw_bytes"], "request does not equal frozen plan batch")
        frozen = {v["relative_path"]: v for v in manifest["files"]}
        fresh = []
        for i, row in enumerate(rows):
            original = frozen[row["relative_path"]]
            identity = {k: original[k] for k in FIELDS}
            _require(row["source_identity"] == identity and
                     row["source_path"] == str(ctx.source_root / row["relative_path"]) and
                     row["bridge_path"] == str(expected_stage / ("range-%04d.bin" % i)) and
                     row["original_size"] == original["size"] and
                     row["original_sha256"] == original["sha256"],
                     "range path/source identity mismatch")
            fresh.append(_range_sha(ctx.source_root, dict(identity, relative_path=row["relative_path"]),
                                    row["offset"], row["length"]))
        return {"binding_sha256": sha(binding_raw), "request_sha256": sha(request_raw),
                "manifest_sha256": sha(manifest_raw), "plan_sha256": sha(plan_raw),
                "window_id": window, "request": req, "fresh_range_sha256": fresh,
                "stage_root": expected_stage,
                "target_receiver_preflight_sha256": sha(receiver_raw)}

    def _gate(self, inspected, *, staged_physical=0):
        """Re-snapshot must happen before and after staging; no cached booleans."""
        snap = self.evidence()
        _require(isinstance(snap["base"], old.GateInput), "fresh GateInput required")
        b = snap["base"]
        req = inspected["request"]
        _require(b.source_root == str(self.ctx.source_root) and
                 b.source_repo == old.SOURCE_REPO and b.source_branch == old.SOURCE_BRANCH and
                 b.source_namespace == old.SOURCE_NAMESPACE and b.source_dev == old.SOURCE_DEV and
                 b.bridge_dev == old.BRIDGE_DEV and b.group == old.GROUP and
                 b.txid == old.TXID and b.selector_sha256 == old.SELECTOR and
                 b.manifest_sha256 == inspected["manifest_sha256"] and
                 b.target_root_native164 == old.TARGET_ROOT and
                 b.policy_id == policy.POLICY_ID and
                 b.amendment_sha256 == policy.AUTHORITY_SHA256 and
                 b.window_id == inspected["window_id"] and
                 b.target_request_sha256 == inspected["request_sha256"],
                 "resource snapshot asset/window mismatch")
        # Worst-case physical reservation includes up to 1MiB directory/control slack.
        projected = 0 if staged_physical else req["raw_bytes"] + MIB
        _require(_bridge_allocated(self.ctx.bridge) + projected <= 256 * MIB,
                 "whole bridge physical cap")
        b = replace(b, planned_bridge_staged_bytes=projected,
                    planned_rate_bytes_per_second=old.MAX_RATE_BPS,
                    first_source_identity_ok=True,
                    first_source_sha_refreshed=True,
                    target_request_present_and_exact=True)
        # Original evaluator's identity is B0001-specific. Adapt only after
        # independent exact future-window checks above; all resource rules stay intact.
        adapter = replace(b, window_id=old.WINDOW, source_root=old.SOURCE_ROOT,
                          manifest_sha256=old.MANIFEST_SHA256,
                          target_request_sha256=old.TARGET_REQUEST_SHA256)
        decision = policy.evaluate(policy.Copy16Input(
            adapter, policy.APPROVAL_SHA256, req["raw_bytes"], True, True,
            snap["lane_final_closure_verified"], snap["lane_physical_clear"]))
        _require(decision["decision"] == "POLICY_ELIGIBLE_NOT_READY",
                 "COPY16 resource/activity/lease HOLD: " + ",".join(decision["reasons"]))
        _require(snap["source_reader_clear"] and snap["scheduled_reader_clear"] and
                 snap["sole_sender_clear"] and snap["receiver_clear"] and
                 SHA_RE.fullmatch(inspected["target_receiver_preflight_sha256"]) is not None,
                 "source/reader/sender/receiver not independently clear")
        return {"decision": decision, "workspace_available_bytes": b.workspace_available_bytes,
                "share_available_bytes": b.share_available_bytes,
                "snapshot_age_seconds": b.snapshot_age_seconds,
                "staged_physical_bytes": staged_physical}

    def prepare(self):
        """Read-only qualification; write an immutable local PASS only on success."""
        inspected = self._inspect(stage_must_be_absent=True)
        gate = self._gate(inspected)
        pass_path, ready_path, bridge_ready = _window_paths(self.ctx, inspected["window_id"])
        _require(not pass_path.exists() and not ready_path.exists() and
                 not bridge_ready.exists(), "existing PASS/READY; no retry")
        receipt = {"schema": "TLS_V10_P9_EXACT_WINDOW_SOURCE_PREPARE_PASS_V1",
                   "status": "PASS_NOT_READY_NO_STAGE", "window_id": inspected["window_id"],
                   "binding_sha256": inspected["binding_sha256"],
                   "request_sha256": inspected["request_sha256"],
                   "manifest_sha256": inspected["manifest_sha256"],
                   "plan_sha256": inspected["plan_sha256"],
                   "target_receiver_preflight_sha256": inspected["target_receiver_preflight_sha256"],
                   "fresh_range_sha256": inspected["fresh_range_sha256"],
                   "runner_code_sha256": sha(Path(__file__).read_bytes()),
                   "gate": gate, "source_originals": "SOURCE_KEEP", "source_files_unlinked": 0}
        return {"path": str(pass_path), "sha256": _no_clobber_json(pass_path, receipt),
                "receipt": receipt}

    def stage(self):
        """Serial bounded staging; uncertain partial output is intentionally retained."""
        ctx = self.ctx
        binding = _json(self.binding_path.read_bytes())
        pass_path, ready_path, bridge_ready = _window_paths(ctx, binding["window_id"])
        _require(pass_path.is_file() and not ready_path.exists() and not bridge_ready.exists(),
                 "PASS missing or READY already exists")
        lock_fd = os.open(ctx.bridge / ".TLS_V10_SOURCE_SENDER.lock",
                          os.O_RDWR | os.O_NOFOLLOW)
        try:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise Hold("existing sender owns lock") from error
            inspected = self._inspect(stage_must_be_absent=True)
            pinned = _json(pass_path.read_bytes())
            _require(pinned["binding_sha256"] == inspected["binding_sha256"] and
                     pinned["request_sha256"] == inspected["request_sha256"] and
                     pinned["target_receiver_preflight_sha256"] ==
                     inspected["target_receiver_preflight_sha256"] and
                     pinned["runner_code_sha256"] == sha(Path(__file__).read_bytes()) and
                     pinned["fresh_range_sha256"] == inspected["fresh_range_sha256"] and
                     pinned["status"] == "PASS_NOT_READY_NO_STAGE", "PASS/fresh source drift")
            before = self._gate(inspected)
            directory = inspected["stage_root"]
            os.mkdir(directory.parent, 0o700)
            os.mkdir(directory, 0o700)
            limiter = sender.RateLimiter(old.MAX_RATE_BPS)
            staged = []
            physical = 0
            for i, row in enumerate(inspected["request"]["ranges"]):
                item = sender.stage_range(ctx.source_root,
                                          dict(row["source_identity"], relative_path=row["relative_path"]),
                                          row["offset"], row["length"], directory,
                                          "range-%04d.bin" % i,
                                          existing_bridge_allocated_bytes=physical, limiter=limiter)
                _require(item["fresh_chunk_sha256"] == inspected["fresh_range_sha256"][i],
                         "stage/fresh source SHA changed; preserve stage")
                physical += item["bridge_identity"]["allocated"]
                staged.append(item)
            # Stage helper checks each inode and close/reopen SHA.  Recheck all
            # source ranges, current resources, and physical bridge occupancy.
            after_inspected = self._inspect(stage_must_be_absent=False)
            _require(after_inspected["binding_sha256"] == inspected["binding_sha256"] and
                     after_inspected["request_sha256"] == inspected["request_sha256"] and
                     after_inspected["fresh_range_sha256"] == inspected["fresh_range_sha256"],
                     "post-stage source/request drift; preserve stage")
            post = self._gate(after_inspected, staged_physical=physical)
            payload_names = {p.name for p in directory.iterdir()}
            _require(payload_names == {"range-%04d.bin" % i for i in range(len(staged))},
                     "unexpected bridge stage object")
            ready = {"schema": "TLS_V10_OLD174_GROUPED_RAW_READY_V1", "status": "READY_SOURCE_KEEP",
                     "window_id": inspected["window_id"], "group": old.GROUP,
                     "txid": old.TXID, "selector_sha256": old.SELECTOR,
                     "canonical_manifest_sha256": old.MANIFEST_SHA256,
                     "target_window_git_commit": binding["target_request_git_commit"],
                     "target_window_sha256": inspected["request_sha256"],
                     "prior_cleanup_sha256": binding["prior_cleanup_sha256"],
                     "target_root_native164": old.TARGET_ROOT,
                     "source_repo": old.SOURCE_REPO, "source_branch": old.SOURCE_BRANCH,
                     "source_root": str(ctx.source_root), "source_frozen_commit":
                     inspected["request"]["source_frozen_commit"],
                     "source_namespace": old.SOURCE_NAMESPACE, "source_dev": old.SOURCE_DEV,
                     "policy_id": policy.POLICY_ID, "source_gate_sha256": sha(pass_path.read_bytes()),
                     "source_sender_code_sha256": sha(Path(__file__).read_bytes()),
                     "source_range_primitive_sha256": sha(Path(sender.__file__).read_bytes()),
                     "gate_before_stage": before, "gate_after_stage": post,
                     "entries": [{"relative_path": r["relative_path"], "offset": r["offset"],
                                  "length": r["length"], "source_identity": r["source_identity"],
                                  "source_full_sha256": r["original_sha256"],
                                  "chunk_sha256": s["fresh_chunk_sha256"],
                                  "bridge_path": s["bridge_payload_path"],
                                  "bridge_identity": s["bridge_identity"]}
                                 for r, s in zip(inspected["request"]["ranges"], staged)],
                     "range_count": len(staged), "raw_bytes": inspected["request"]["raw_bytes"],
                     "bridge_payload_allocated_bytes": physical,
                     "source_originals": "SOURCE_KEEP", "source_files_unlinked": 0,
                     "complete_group_archived": False, "complete_group_native_restored": False}
            return {"path": str(ready_path), "sha256": _no_clobber_json(ready_path, ready),
                    "receipt": ready}
        finally:
            os.close(lock_fd)

    def publish(self, source_commit):
        """Only Git-readback exact local READY may be copied to the sole bridge."""
        binding = _json(self.binding_path.read_bytes())
        pass_path, ready_path, bridge_ready = _window_paths(self.ctx, binding["window_id"])
        _require(pass_path.is_file() and ready_path.is_file() and not bridge_ready.exists(),
                 "missing PASS/READY or duplicate bridge READY")
        raw = ready_path.read_bytes()
        _require(_source_git_raw(self.ctx.source_repo, source_commit, ready_path) == raw,
                 "READY not byte-exact in source Git commit")
        if self.ctx.production:
            remote = subprocess.check_output(
                ["git", "-C", str(self.ctx.source_repo), "ls-remote", "origin",
                 "refs/heads/" + old.SOURCE_BRANCH], text=True).split()
            _require(remote and remote[0] == source_commit,
                     "source Git remote branch does not read back READY commit")
        ready = _json(raw)
        pinned = _json(pass_path.read_bytes())
        _require(ready["source_originals"] == "SOURCE_KEEP" and
                 ready["source_files_unlinked"] == 0 and
                 pinned["binding_sha256"] == sha(self.binding_path.read_bytes()) and
                 ready["window_id"] == binding["window_id"] and
                 ready["target_window_sha256"] == binding["target_request_sha256"] and
                 ready["target_window_git_commit"] == binding["target_request_git_commit"] and
                 ready["prior_cleanup_sha256"] == binding["prior_cleanup_sha256"] and
                 ready["source_gate_sha256"] == sha(pass_path.read_bytes()) and
                 ready["source_sender_code_sha256"] == sha(Path(__file__).read_bytes()),
                 "READY/binding changed")
        # Do not rehash 141 full source files; only requested bounded ranges.
        checked = self._inspect(stage_must_be_absent=False)
        self._gate(checked, staged_physical=ready["bridge_payload_allocated_bytes"])
        _require(len(ready["entries"]) == len(checked["fresh_range_sha256"]) and
                 ready["range_count"] == checked["request"]["range_count"] and
                 ready["raw_bytes"] == checked["request"]["raw_bytes"], "READY entry count/bytes")
        for i, item in enumerate(ready["entries"]):
            p = Path(item["bridge_path"])
            source_row = checked["request"]["ranges"][i]
            _require(p == checked["stage_root"] / ("range-%04d.bin" % i) and
                     sender._fingerprint(os.lstat(p)) == item["bridge_identity"] and
                     item["chunk_sha256"] == checked["fresh_range_sha256"][i] and
                     item["relative_path"] == source_row["relative_path"] and
                     item["offset"] == source_row["offset"] and
                     item["length"] == source_row["length"] and
                     item["source_identity"] == source_row["source_identity"] and
                     item["source_full_sha256"] == source_row["original_sha256"],
                     "bridge/source READY identity drift")
            h = hashlib.sha256()
            fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                while True:
                    block = os.read(fd, MIB)
                    if not block:
                        break
                    h.update(block)
            finally:
                os.close(fd)
            _require(h.hexdigest() == item["chunk_sha256"], "bridge payload SHA drift")
        # Preserve byte-for-byte READY, not a reserialized JSON approximation.
        fd = os.open(bridge_ready, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "wb") as out:
            out.write(raw)
            out.flush()
            os.fsync(out.fileno())
        parent = os.open(self.ctx.bridge, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(parent)
        finally:
            os.close(parent)
        return {"bridge_ready": str(bridge_ready), "sha256": sha(raw),
                "source_commit": source_commit, "source_originals": "SOURCE_KEEP"}
