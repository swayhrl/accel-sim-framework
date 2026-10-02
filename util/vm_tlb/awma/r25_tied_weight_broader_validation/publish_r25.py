#!/usr/bin/env python3
"""Prepare and close the immutable R25 node164 raw publication."""

import argparse
import csv
import hashlib
import json
import shutil
import tarfile
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sums(pack):
    rows = []
    for f in sorted(x for x in pack.rglob("*") if x.is_file() and x.name != "SHA256SUMS"):
        rows.append(f"{sha(f)}  {f.relative_to(pack).as_posix()}")
    (pack / "SHA256SUMS").write_text("\n".join(rows) + "\n")


def prepare(a):
    root = Path(a.root)
    runner_dir = root / "source/runner"
    runner_dir.mkdir(parents=True, exist_ok=True)
    for source in (a.runner, a.base, a.freezer, a.finalizer, a.publisher):
        shutil.copy2(source, runner_dir / Path(source).name)
    archive = root / "r25_raw_publication.tgz"
    with tarfile.open(archive, "w:gz") as tf:
        for name in ("raw", "receipts", "source"):
            tf.add(root / name, arcname=name, recursive=True)
    rows = []
    for sub in (root / "raw", root / "receipts", root / "source"):
        for f in sorted(x for x in sub.rglob("*") if x.is_file()):
            rows.append({"asset": f.relative_to(root).as_posix(), "bytes": f.stat().st_size, "sha256": sha(f)})
    rows.append({"asset": archive.name, "bytes": archive.stat().st_size, "sha256": sha(archive)})
    manifest = root / "R25_PUBLICATION_MANIFEST.tsv"
    with manifest.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=("asset", "bytes", "sha256"), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    receipt = {
        "status": "LOCAL_PUBLICATION_READY",
        "destination": a.remote,
        "archive": archive.name,
        "archive_bytes": archive.stat().st_size,
        "archive_sha256": sha(archive),
        "manifest": manifest.name,
        "manifest_sha256": sha(manifest),
        "file_count_including_archive": len(rows),
    }
    dump(root / "NODE164_PUBLICATION_LOCAL_READY.json", receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


def close(a):
    root, pack = Path(a.root), Path(a.pack)
    local = json.loads((root / "NODE164_PUBLICATION_LOCAL_READY.json").read_text())
    if a.remote_archive_sha != local["archive_sha256"] or a.remote_manifest_sha != local["manifest_sha256"]:
        raise SystemExit("remote publication hash mismatch")
    receipt = {
        **local,
        "status": "NODE164_RAW_PUBLICATION_SHA_VERIFIED",
        "remote_archive_sha256": a.remote_archive_sha,
        "remote_manifest_sha256": a.remote_manifest_sha,
        "remote_verification": "archive and manifest byte hashes independently read back on node164",
    }
    dump(pack / "NODE164_PUBLICATION.json", receipt)
    run_path = pack / "RUN_RECEIPTS.json"
    run = json.loads(run_path.read_text())
    run["node164_publication"] = a.remote
    run["node164_archive_sha256"] = a.remote_archive_sha
    run["node164_manifest_sha256"] = a.remote_manifest_sha
    run["node164_readback_verified"] = True
    dump(run_path, run)
    index_path = pack / "RAW_DATA_INDEX.tsv"
    rows = list(csv.DictReader(index_path.open(), delimiter="\t"))
    for row in rows:
        path = Path(row["path"])
        try:
            rel = path.relative_to(root)
            row["node164_location"] = f"{a.remote}/{rel.as_posix()}"
        except ValueError:
            row["node164_location"] = "NOT_PUBLISHED_EXTERNAL_AUTHORITY"
    with index_path.open("w", newline="") as f:
        fields = list(rows[0])
        if "node164_location" not in fields:
            fields.append("node164_location")
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    sums(pack)
    print(json.dumps(receipt, indent=2, sort_keys=True))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("prepare", "close"))
    p.add_argument("--root", required=True)
    p.add_argument("--remote", required=True)
    p.add_argument("--pack")
    p.add_argument("--runner")
    p.add_argument("--base")
    p.add_argument("--freezer")
    p.add_argument("--finalizer")
    p.add_argument("--publisher")
    p.add_argument("--remote-archive-sha")
    p.add_argument("--remote-manifest-sha")
    a = p.parse_args()
    prepare(a) if a.mode == "prepare" else close(a)


if __name__ == "__main__":
    main()
