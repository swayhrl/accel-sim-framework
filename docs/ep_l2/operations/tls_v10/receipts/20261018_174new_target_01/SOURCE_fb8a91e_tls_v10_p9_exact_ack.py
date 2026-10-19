#!/usr/bin/env python3
"""Bounded, fail-closed P9 B0004+ SOURCE_KEEP ACK sidecar.

No CLI or automatic invocation.  A caller supplies a literal, independently
reviewed window binding.  This module never deletes source or bridge data and
never writes to the target repository.  An ACK proves chunk ranges only.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess

import tls_v10_p9_streaming_ack_core as core


WINDOW = re.compile(r"^TLS_V10_P9_PUBLIC_B(\d{4})$")
SHA = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
TARGET_PREFIX = "docs/ep_l2/operations/tls_v10/receipts/20261018_174new_target_01/"
SOURCE_PREFIX = "docs/ep_l2/operations/tls_v10_174_to_164_source/"


class Hold(core.VerificationHold):
    """Preserve source, bridge and prior receipts; do not retry blindly."""


@dataclass(frozen=True)
class ExactWindow:
    window_id: str
    txid: str
    selector_sha256: str
    manifest_sha256: str
    source_ready_commit: str
    source_ready_sha256: str
    target_window_commit: str
    target_window_sha256: str
    target_receipt_commit: str
    dest_sha256: str
    restore_sha256: str
    receiving_sha256: str
    native164_base: str
    archived_chunks_root: str


@dataclass(frozen=True)
class Context:
    source_repo: Path
    target_repo: Path
    source_remote: str
    target_remote: str
    source_branch: str
    target_branch: str
    source_root: Path
    bridge_root: Path
    manifest_path: Path
    ack_directory: Path
    production: bool = True


def _need(condition, reason):
    if not condition:
        raise Hold(reason)


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _json(raw, label):
    try:
        item = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise Hold(label + ": malformed JSON") from exc
    _need(isinstance(item, dict), label + ": expected object")
    return item


def _git(repo, *args):
    try:
        return subprocess.check_output(("git", "-C", str(repo), *args),
                                       stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise Hold("Git readback unavailable") from exc


def _remote_commits(repo, remote, branch, commits):
    """Require a pinned commit reachable from the currently advertised ref.

    This is read-only.  If the advertised HEAD object is not already local,
    HOLD; a separate operator may fetch it, but this sidecar never does.
    """
    _need(all(isinstance(commit, str) and COMMIT.fullmatch(commit)
              for commit in commits), "invalid commit")
    ref = "refs/heads/" + branch
    lines = _git(repo, "ls-remote", remote, ref).decode().splitlines()
    _need(len(lines) == 1 and lines[0].endswith("\t" + ref),
          "remote branch missing or ambiguous")
    head = lines[0].split("\t", 1)[0]
    _need(bool(COMMIT.fullmatch(head)), "invalid remote HEAD")
    for commit in commits:
        try:
            subprocess.run(("git", "-C", str(repo), "merge-base", "--is-ancestor",
                            commit, head), stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, check=True)
        except (OSError, subprocess.CalledProcessError) as exc:
            raise Hold("pinned commit not proven on advertised remote branch") from exc


def _git_raw(repo, commit, relative):
    _need(bool(COMMIT.fullmatch(commit)) and not Path(relative).is_absolute() and
          ".." not in Path(relative).parts, "unsafe Git path/commit")
    return _git(repo, "show", commit + ":" + relative)


def _names(window):
    return {
        "request": window + "_TARGET_SOLE_WINDOW_REQUEST_COPY16.json",
        "ready": window + "_SOURCE_READY_COPY16.json",
        "dest": window + "_DEST_VERIFIED.json",
        "restore": window + "_RESTORE_VERIFIED.json",
        "receiving": window + "_TARGET_RECEIVING_RECEIPT_COPY16.json",
        "ack": window + "_SOURCE_KEEP_ACK.json",
        "publication": window + "_SOURCE_KEEP_ACK_PUBLICATION.json",
    }


def _binding(binding, ctx):
    match = WINDOW.fullmatch(binding.window_id)
    _need(match is not None and int(match.group(1)) >= 4,
          "only exact P9 B0004+ windows are supported")
    for value in (binding.txid, binding.selector_sha256,
                  binding.manifest_sha256, binding.source_ready_sha256,
                  binding.target_window_sha256, binding.dest_sha256,
                  binding.restore_sha256, binding.receiving_sha256):
        _need(isinstance(value, str) and SHA.fullmatch(value), "invalid SHA binding")
    for value in (binding.source_ready_commit, binding.target_window_commit,
                  binding.target_receipt_commit):
        _need(isinstance(value, str) and COMMIT.fullmatch(value),
              "invalid commit binding")
    _need(ctx.source_branch == "hrl/ops-174-tls-v10-source-exec-v1" and
          ctx.target_branch == "hrl/tls-v10-174new-target-exec-v1" and
          ctx.manifest_path.name == "TLS_V10_P9_PUBLIC_TARGET_TRANSACTION_MANIFEST.json" and
          ctx.source_root.is_absolute() and ctx.bridge_root.is_absolute() and
          ctx.ack_directory.is_absolute() and
          ctx.source_root.resolve(strict=True) == ctx.source_root and
          ctx.bridge_root.resolve(strict=True) == ctx.bridge_root,
          "unqualified context or root")
    _need(binding.native164_base.startswith("/home/shared/huangrulin/host174_storage_recovery/tls_v10/")
          and binding.archived_chunks_root.startswith("/root/share/mnt164/huangrulin/host174_storage_recovery/tls_v10/")
          and binding.archived_chunks_root.endswith("/" + binding.txid + ".partial/chunks"),
          "164 archive root does not match P9 transaction")
    if ctx.production:
        import tls_v10_copy_only20g_gate as old
        here = Path(__file__).resolve().parent
        _need(ctx.source_root == Path(old.SOURCE_ROOT) and
              ctx.bridge_root == old.BRIDGE and
              ctx.manifest_path == here / "TLS_V10_P9_PUBLIC_TARGET_TRANSACTION_MANIFEST.json" and
              ctx.ack_directory == here and
              binding.txid == old.TXID and
              binding.selector_sha256 == old.SELECTOR and
              binding.manifest_sha256 == old.MANIFEST_SHA256 and
              binding.native164_base == old.TARGET_ROOT,
              "production P9 authority drift")


def _readback(repo, commit, relative, bridge_path, expected_sha):
    git_raw = _git_raw(repo, commit, relative)
    _need(_sha(git_raw) == expected_sha, "Git raw SHA mismatch: " + relative)
    bridge_raw = bridge_path.read_bytes()
    _need(bridge_raw == git_raw, "Git/bridge raw mismatch: " + relative)
    return git_raw


def _frozen_metadata(manifest, source_root):
    files = manifest.get("files")
    directories = manifest.get("directories")
    _need(isinstance(files, list) and len(files) == 141 and
          isinstance(directories, list) and len(directories) == 4,
          "P9 frozen cardinality drift")
    seen = set()
    for row in files:
        rel = row.get("relative_path")
        parts = core._relative_parts(rel)
        _need(rel not in seen, "duplicate frozen file")
        seen.add(rel)
        info = os.lstat(source_root.joinpath(*parts))
        want = {key: row[key] for key in core.IDENTITY}
        _need(stat.S_ISREG(info.st_mode) and core._identity(info) == want,
              "frozen original identity drift: " + rel)
    for row in directories:
        rel = row.get("relative_path")
        path = source_root if rel == "." else source_root.joinpath(*core._relative_parts(rel))
        _need(stat.S_ISDIR(os.lstat(path).st_mode), "frozen directory drift")


def _receive(receiving, binding, summary):
    expected = {
        "window_id": binding.window_id, "txid": binding.txid,
        "selector_sha256": binding.selector_sha256,
        "canonical_manifest_sha256": binding.manifest_sha256,
        "source_ready_git_commit": binding.source_ready_commit,
        "source_ready_sha256": binding.source_ready_sha256,
        "target_window_git_commit": binding.target_window_commit,
        "target_window_sha256": binding.target_window_sha256,
        "dest_receipt_sha256": binding.dest_sha256,
        "restore_receipt_sha256": binding.restore_sha256,
        "range_count": summary["range_count"], "raw_bytes": summary["raw_bytes"],
        "source_originals": "SOURCE_KEEP", "source_files_deleted_by_target": 0,
        "bridge_payloads_retained": True,
        "full_group_certificate_created": False,
        "full_group_all141_native_tree_restored": False,
    }
    for key, value in expected.items():
        _need(receiving.get(key) == value, "receiving receipt mismatch: " + key)
    _need(receiving.get("status") ==
          binding.window_id.rsplit("_", 1)[-1] +
          "_DEST_AND_NATIVE_RANGE_RESTORE_VERIFIED_AWAIT_SOURCE_KEEP_ACK" and
          receiving.get("source_scientific_release_bytes") == 0,
          "receiving status or scope overclaim")


def _request(request, ready, binding):
    for key, expected in (("window_id", binding.window_id),
                          ("txid", binding.txid),
                          ("selector_sha256", binding.selector_sha256),
                          ("canonical_manifest_sha256", binding.manifest_sha256),
                          ("target_root_native164", binding.native164_base),
                          ("group", "P9_PUBLIC"),
                          ("source_originals", "SOURCE_KEEP")):
        _need(request.get(key) == expected, "target request mismatch: " + key)
    ranges = request.get("ranges")
    entries = ready.get("entries")
    _need(isinstance(ranges, list) and isinstance(entries, list) and
          len(ranges) == len(entries) == request.get("range_count") ==
          ready.get("range_count"), "request/READY vector cardinality mismatch")
    _need(request.get("raw_bytes") == ready.get("raw_bytes") and
          request.get("source_scientific_release_authorized_by_this_window") is False,
          "request bytes or source release scope mismatch")
    for requested, entry in zip(ranges, entries):
        for request_key, ready_key in (("relative_path", "relative_path"),
                                       ("offset", "offset"),
                                       ("length", "length"),
                                       ("original_sha256", "source_full_sha256"),
                                       ("bridge_path", "bridge_path"),
                                       ("source_identity", "source_identity")):
            _need(requested.get(request_key) == entry.get(ready_key),
                  "request/READY exact range mismatch: " + request_key)


def _no_clobber_json(path, value):
    raw = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as out:
        out.write(raw)
        out.flush()
        os.fsync(out.fileno())
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return _sha(raw)


def prepare(binding, ctx):
    """Verify exact target/source evidence, then create one local ACK (no bridge write)."""
    _binding(binding, ctx)
    names = _names(binding.window_id)
    ack_path = ctx.ack_directory / names["ack"]
    _need(not ack_path.exists() and not (ctx.bridge_root / names["ack"]).exists(),
          "ACK already exists; inspect, never overwrite")
    _remote_commits(ctx.source_repo, ctx.source_remote, ctx.source_branch,
                    (binding.source_ready_commit,))
    _remote_commits(ctx.target_repo, ctx.target_remote, ctx.target_branch,
                    (binding.target_window_commit, binding.target_receipt_commit))
    ready_raw = _readback(ctx.source_repo, binding.source_ready_commit,
                          SOURCE_PREFIX + names["ready"], ctx.bridge_root / names["ready"],
                          binding.source_ready_sha256)
    manifest_raw = ctx.manifest_path.read_bytes()
    _need(_sha(manifest_raw) == binding.manifest_sha256,
          "frozen manifest raw SHA drift")
    manifest = _json(manifest_raw, "manifest")
    _frozen_metadata(manifest, ctx.source_root)
    ready = _json(ready_raw, "READY")
    request_raw = _readback(ctx.target_repo, binding.target_window_commit,
                            TARGET_PREFIX + names["request"],
                            ctx.bridge_root / names["request"],
                            binding.target_window_sha256)
    _request(_json(request_raw, "request"), ready, binding)
    target_raw = {}
    for key, expected in (("dest", binding.dest_sha256),
                          ("restore", binding.restore_sha256),
                          ("receiving", binding.receiving_sha256)):
        name = names[key]
        target_raw[key] = _readback(ctx.target_repo, binding.target_receipt_commit,
                                    TARGET_PREFIX + name, ctx.bridge_root / name,
                                    expected)
    bridge_directory = ctx.bridge_root / (binding.window_id + "_" + binding.txid[:12])
    summary = core.verify_grouped_range_receipts(
        ready_raw=ready_raw, manifest_raw=manifest_raw,
        dest_raw=target_raw["dest"], restore_raw=target_raw["restore"],
        bindings=core.Bindings(
            window_id=binding.window_id, txid=binding.txid,
            selector_sha256=binding.selector_sha256,
            manifest_sha256=binding.manifest_sha256,
            source_ready_commit=binding.source_ready_commit,
            source_ready_sha256=binding.source_ready_sha256,
            target_window_commit=binding.target_window_commit,
            target_window_sha256=binding.target_window_sha256,
            target_receipt_commit=binding.target_receipt_commit,
            dest_receipt_sha256=binding.dest_sha256,
            restore_receipt_sha256=binding.restore_sha256,
            native164_base=binding.native164_base,
            archived_chunks_root=binding.archived_chunks_root),
        source_root=ctx.source_root, bridge_directory=bridge_directory)
    _receive(_json(target_raw["receiving"], "receiving"), binding, summary)
    _need(ready.get("source_files_unlinked") == 0 and
          ready.get("source_originals") == "SOURCE_KEEP" and
          ready.get("status") == "READY_SOURCE_KEEP", "source READY not KEEP")
    receipt = {
        "schema": "TLS_V10_P9_EXACT_RANGE_SOURCE_KEEP_ACK_V1",
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "SOURCE_KEEP_ACK_TARGET_MAY_CLEAN_EXACT_VERIFIED_BRIDGE_RANGES",
        "window_id": binding.window_id, "group": "P9_PUBLIC",
        "txid": binding.txid, "selector_sha256": binding.selector_sha256,
        "canonical_manifest_sha256": binding.manifest_sha256,
        "source_ready_git_commit": binding.source_ready_commit,
        "source_ready_sha256": binding.source_ready_sha256,
        "target_dest_restore_git_commit": binding.target_receipt_commit,
        "target_dest_receipt_sha256": binding.dest_sha256,
        "target_native_restore_receipt_sha256": binding.restore_sha256,
        "target_receiving_receipt_sha256": binding.receiving_sha256,
        "target_true164_native_root": binding.native164_base,
        "verified_scope": "LISTED_CHUNK_RANGES_ONLY_NOT_FULL_ORIGINAL_OR_GROUP",
        "source_frozen_files_metadata_rechecked": 141,
        "range_count": summary["range_count"], "raw_bytes": summary["raw_bytes"],
        "bridge_payload_exact_cleanup_permission": [
            {"path": entry["bridge_path"],
             "sha256": entry["sha256"],
             "identity": ready["entries"][index]["bridge_identity"],
             "owner": "174-new TARGET ONLY AFTER_GITHUB_SOURCE_ACK_READBACK"}
            for index, entry in enumerate(summary["entries"])],
        "source_originals": "SOURCE_KEEP", "source_science_files_unlinked": 0,
        "source_science_df_gain_bytes": 0,
        "next_window_requires_verified_bridge_cleanup": True,
    }
    return ack_path, _no_clobber_json(ack_path, receipt)


def publish_bridge(binding, ctx, ack_commit):
    """Publish ACK only after remote source Git readback and fresh payload check."""
    _binding(binding, ctx)
    _remote_commits(ctx.source_repo, ctx.source_remote, ctx.source_branch,
                    (ack_commit,))
    names = _names(binding.window_id)
    ack_path = ctx.ack_directory / names["ack"]
    raw = ack_path.read_bytes()
    _need(_git_raw(ctx.source_repo, ack_commit, SOURCE_PREFIX + names["ack"]) == raw,
          "ACK Git raw differs from local bytes")
    ack = _json(raw, "ACK")
    _need(ack.get("window_id") == binding.window_id and
          ack.get("txid") == binding.txid and
          ack.get("source_originals") == "SOURCE_KEEP" and
          ack.get("source_science_files_unlinked") == 0 and
          ack.get("target_dest_receipt_sha256") == binding.dest_sha256 and
          ack.get("target_native_restore_receipt_sha256") == binding.restore_sha256,
          "ACK binding/release drift")
    entries = ack.get("bridge_payload_exact_cleanup_permission")
    _need(isinstance(entries, list) and entries and len(entries) == ack.get("range_count"),
          "ACK cleanup vector missing")
    bridge_directory = ctx.bridge_root / (binding.window_id + "_" + binding.txid[:12])
    for index, entry in enumerate(entries):
        path = bridge_directory / "files" / ("range-%04d.bin" % index)
        _need(entry.get("path") == str(path) and
              entry.get("owner") == "174-new TARGET ONLY AFTER_GITHUB_SOURCE_ACK_READBACK" and
              entry.get("identity", {}).get("size", 0) > 0,
              "ACK exact bridge path/identity mismatch")
        _need(core._stream_range(bridge_directory,
                                 ("files", "range-%04d.bin" % index), 0,
                                 entry["identity"]["size"], entry["identity"]) ==
              entry.get("sha256"), "bridge payload identity/SHA drift")
    bridge_ack = ctx.bridge_root / names["ack"]
    _need(not bridge_ack.exists() and
          not (ctx.bridge_root / names["publication"]).exists(),
          "bridge ACK/publication already exists")
    _no_clobber_json(bridge_ack, ack)
    _need(bridge_ack.read_bytes() == raw, "bridge ACK raw differs from Git ACK")
    publication = {
        "schema": "TLS_V10_P9_EXACT_ACK_GITHUB_BRIDGE_READBACK_V1",
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "window_id": binding.window_id, "txid": binding.txid,
        "source_git_commit": ack_commit, "source_branch": ctx.source_branch,
        "source_keep_ack_name": names["ack"],
        "source_keep_ack_sha256": _sha(raw),
        "bridge_keep_ack_sha256": _sha(bridge_ack.read_bytes()),
        "range_count": len(entries), "source_originals": "SOURCE_KEEP",
        "source_files_unlinked": 0,
    }
    return bridge_ack, _no_clobber_json(ctx.bridge_root / names["publication"], publication)
