#!/usr/bin/env python3
"""Bounded no-rsync TLS source range stage primitive, not a READY publisher.

The existing P9 selector/target request and fresh source policy must be
validated by a future transaction wrapper.  This helper has no production
CLI, never unlinks originals, and leaves an uncertain staged file in place
for exact investigation rather than deleting or retrying it blindly.
"""

import hashlib
import os
from pathlib import Path
import stat
import time


MIB = 1024 * 1024
MAX_RAW = 128 * MIB
MAX_PHYSICAL = 256 * MIB
MAX_RATE = 30 * MIB
BLOCK = MIB


class Hold(RuntimeError):
    pass


class RateLimiter:
    """One cumulative elapsed-time budget shared by all ranges in a window."""

    def __init__(self, bytes_per_second=MAX_RATE):
        if not 0 < bytes_per_second <= MAX_RATE:
            raise Hold("aggregate rate outside COPY_ONLY limit")
        self.bytes_per_second = bytes_per_second
        self.started = time.monotonic()
        self.total_bytes = 0

    def account(self, count):
        self.total_bytes += count
        remaining = (self.total_bytes / self.bytes_per_second) - (time.monotonic() - self.started)
        if remaining > 0:
            time.sleep(remaining)


def _parts(relative_path):
    parts = relative_path.split("/")
    if (not parts or relative_path.startswith("/") or "\x00" in relative_path or
            any(v in ("", ".", "..") for v in parts)):
        raise Hold("noncanonical range path")
    return parts


def _fingerprint(info):
    return {"dev": info.st_dev, "inode": info.st_ino, "nlink": info.st_nlink,
            "uid": info.st_uid, "gid": info.st_gid, "mode": info.st_mode & 0o777,
            "size": info.st_size, "mtime_ns": info.st_mtime_ns,
            "ctime_ns": info.st_ctime_ns, "allocated": info.st_blocks * 512}


def _source_fd(root, parts):
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        source = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fd)
        return fd, source
    except BaseException:
        os.close(fd)
        raise


def stage_range(root, frozen, offset, length, bridge_directory, payload_name,
                *, existing_bridge_allocated_bytes, limiter=None):
    """Write one exact range to an already-created bounded bridge directory.

    Returns pinned source/staged inode, size, allocated bytes and fresh SHA.
    A caller must own the single sender lock and validate signed target
    request, 16GiB/Share/RAM/lease/activity gates and whole-bridge occupancy.
    """
    parts = _parts(frozen["relative_path"])
    if payload_name in ("", ".", "..") or "/" in payload_name or "\x00" in payload_name:
        raise Hold("noncanonical payload basename")
    root, bridge_directory = Path(root), Path(bridge_directory)
    if root.resolve(strict=True) != root or bridge_directory.resolve(strict=True) != bridge_directory:
        raise Hold("source/bridge directory symlink")
    if (offset < 0 or length <= 0 or length > MAX_RAW or
            offset + length > frozen["size"] or
            existing_bridge_allocated_bytes < 0 or
            existing_bridge_allocated_bytes + ((length + 4095) // 4096) * 4096 > MAX_PHYSICAL):
        raise Hold("raw range/physical bridge limit")
    if limiter is None:
        limiter = RateLimiter()
    if not isinstance(limiter, RateLimiter):
        raise Hold("unqualified aggregate limiter")
    parent, source = _source_fd(root, parts)
    try:
        before = os.fstat(source)
        expected = {name: frozen[name] for name in
                    ("dev", "inode", "nlink", "uid", "gid", "mode", "size",
                     "mtime_ns", "ctime_ns", "allocated")}
        named_before = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or
                _fingerprint(named_before) != _fingerprint(before) or
                _fingerprint(before) != expected):
            raise Hold("source frozen identity mismatch")
        bridgefd = os.open(bridge_directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            staged = os.open(payload_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o600, dir_fd=bridgefd)
            try:
                os.lseek(source, offset, os.SEEK_SET)
                digest = hashlib.sha256()
                copied = 0
                while copied < length:
                    block = os.read(source, min(BLOCK, length - copied))
                    if not block:
                        raise Hold("source short read")
                    digest.update(block)
                    if os.write(staged, block) != len(block):
                        raise Hold("bridge short write")
                    copied += len(block)
                    limiter.account(len(block))
                os.fsync(staged)
                after = os.fstat(source)
                staged_info = os.fstat(staged)
            finally:
                os.close(staged)
            os.fsync(bridgefd)
            named_after = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
            if (_fingerprint(after) != expected or
                    _fingerprint(named_after) != expected or
                    staged_info.st_nlink != 1 or staged_info.st_size != length or
                    existing_bridge_allocated_bytes + staged_info.st_blocks * 512 > MAX_PHYSICAL):
                raise Hold("post-copy source or physical bridge identity mismatch")
            verify = os.open(payload_name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=bridgefd)
            try:
                actual = hashlib.sha256()
                while True:
                    block = os.read(verify, BLOCK)
                    if not block:
                        break
                    actual.update(block)
                verify_info = os.fstat(verify)
            finally:
                os.close(verify)
            if (_fingerprint(verify_info) != _fingerprint(staged_info) or
                    actual.hexdigest() != digest.hexdigest()):
                raise Hold("staged close/reopen SHA/identity mismatch")
            return {"source_relative_path": frozen["relative_path"],
                    "offset": offset, "length": length,
                    "fresh_chunk_sha256": digest.hexdigest(),
                    "source_identity": expected,
                    "bridge_payload_path": str(bridge_directory / payload_name),
                    "bridge_identity": _fingerprint(staged_info),
                    "source_originals": "SOURCE_KEEP"}
        finally:
            os.close(bridgefd)
    finally:
        os.close(source)
        os.close(parent)
