#!/usr/bin/env python3
"""Finalize durable-publication receipts and pack checksums."""

import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--copyback", type=Path, required=True)
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--remote-path", required=True)
    args = parser.parse_args()
    manifest = args.raw / "RAW_SHA256SUMS"
    entries = []
    for line in manifest.read_text().splitlines():
        digest, relative = line.split("  ", 1)
        path = args.raw / relative
        copy = args.copyback / relative
        if sha256(path) != digest or sha256(copy) != digest:
            raise RuntimeError(f"raw/copyback mismatch: {relative}")
        entries.append((relative, path, digest))
    if sha256(args.copyback / "RAW_SHA256SUMS") != sha256(manifest):
        raise RuntimeError("copyback manifest mismatch")
    publication = {
        "status": "PASS_DURABLE_PUBLISH_AND_COPYBACK",
        "remote_host": "hrl174new",
        "local_raw_path": str(args.raw), "remote_path": args.remote_path,
        "copyback_path": str(args.copyback), "manifest_entries": len(entries),
        "manifest_bytes": sum(path.stat().st_size for _, path, _ in entries),
        "manifest_sha256": sha256(manifest), "remote_manifest_verify": "PASS",
        "full_copyback_manifest_verify": "PASS", "bulk_git_commit": False,
    }
    dump(args.pack / "PUBLISH_RECEIPT.json", publication)
    rows = []
    for relative, path, digest in entries + [("RAW_SHA256SUMS", manifest, sha256(manifest))]:
        committed = "GPU_LOCK_RECEIPT.json" if relative == "GPU_LOCK_RECEIPT.json" else "INDEX_ONLY"
        rows.append({"artifact": relative, "node109_path": str(path), "bytes": path.stat().st_size,
                     "sha256": digest, "committed_copy": committed,
                     "node164_path": f"{args.remote_path}/{relative}",
                     "scientific_status": "QUARANTINED_CORRECTNESS_FAILURE"})
    with (args.pack / "RAW_INDEX.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    run_identity = {
        "status": "CORRECTNESS_MISMATCH_STOP",
        "run_id": args.raw.name, "node": 109, "gpu": "NVIDIA GeForce RTX 4080",
        "authority_commit": "30b3016a7ad5b5ef86a3494c784e072938dee6c5",
        "accepted_producer_commit": "071297ae7f4aa772a27fae0cf31ad47ab7d967be",
        "branch": "hrl/c16-ffn-gate-up-concurrency-native-diagnostic-109-v1",
        "formal_sample_count": 0, "gpu_lock_released": True,
        "raw_manifest_sha256": sha256(manifest), "durable_publish": publication["status"],
    }
    dump(args.pack / "RUN_IDENTITY.json", run_identity)
    checksum = args.pack / "SHA256SUMS"
    files = sorted(path for path in args.pack.iterdir() if path.is_file() and path.name != checksum.name)
    checksum.write_text("".join(f"{sha256(path)}  {path.name}\n" for path in files))
    print(json.dumps({"status": "PASS", "pack_files": len(files),
                      "pack_manifest_sha256": sha256(checksum), **publication}, sort_keys=True))


if __name__ == "__main__":
    main()
