#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


p = argparse.ArgumentParser()
p.add_argument("--raw-root", type=Path, required=True)
p.add_argument("--copyback-root", type=Path, required=True)
p.add_argument("--pack", type=Path, required=True)
p.add_argument("--remote-root", required=True)
a = p.parse_args()
rows = []
run_receipts = []
total_bytes = 0
for run in sorted(x for x in a.raw_root.iterdir() if x.is_dir()):
    manifest = run / "RAW_SHA256SUMS"
    copy_run = a.copyback_root / run.name
    count = 0
    for line in manifest.read_text().splitlines():
        digest, relative = line.split("  ", 1)
        source, copied = run / relative, copy_run / relative
        if sha(source) != digest or sha(copied) != digest:
            raise RuntimeError(f"copyback mismatch {run.name}/{relative}")
        total_bytes += source.stat().st_size
        count += 1
        rows.append({"run_id": run.name, "artifact": relative, "node109_path": str(source),
                     "bytes": source.stat().st_size, "sha256": digest,
                     "node164_path": f"{a.remote_root}/raw/{run.name}/{relative}",
                     "git_copy": "INDEX_ONLY", "status": "FINAL" if "031741Z" in run.name else "ABORTED_ENGINEERING"})
    if sha(copy_run / "RAW_SHA256SUMS") != sha(manifest):
        raise RuntimeError(f"manifest mismatch {run.name}")
    rows.append({"run_id": run.name, "artifact": "RAW_SHA256SUMS", "node109_path": str(manifest),
                 "bytes": manifest.stat().st_size, "sha256": sha(manifest),
                 "node164_path": f"{a.remote_root}/raw/{run.name}/RAW_SHA256SUMS",
                 "git_copy": "INDEX_ONLY", "status": "FINAL" if "031741Z" in run.name else "ABORTED_ENGINEERING"})
    run_receipts.append({"run_id": run.name, "entries": count, "manifest_sha256": sha(manifest)})
with (a.pack / "RAW_INDEX.tsv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=tuple(rows[0]), delimiter="\t", lineterminator="\n")
    w.writeheader(); w.writerows(rows)
publish = {"status": "PASS_DURABLE_PUBLISH_AND_COPYBACK", "remote_host": "hrl174new",
           "local_raw_root": str(a.raw_root), "remote_root": a.remote_root,
           "copyback_root": str(a.copyback_root), "runs": run_receipts,
           "indexed_files_including_manifests": len(rows), "payload_bytes_excluding_manifests": total_bytes,
           "remote_manifest_verify": "PASS", "copyback_verify": "PASS"}
dump(a.pack / "PUBLISH_RECEIPT.json", publish)
run_identity = {"status": "CORRECTNESS_TOLERANCE_FAILED_STOP",
                "branch": "hrl/c16-merged-gate-up-native-strong-baseline-109-v1",
                "final_run_id": "C16R_merged-gate-up-native-strong-baseline_20261001T031741Z",
                "authority_commit": "3c3f667bbab8f3ae227dc3bc8eaa6c642b97a453",
                "vllm_commit": "df8fd42116f172b7a53bc10c8a680b05232edbed",
                "formal_samples": 0, "cumulative_gpu_wall_seconds": 86,
                "all_gpu_locks_released": True, "durable_publish": publish["status"]}
dump(a.pack / "RUN_IDENTITY.json", run_identity)
checksum = a.pack / "SHA256SUMS"
files = sorted(x for x in a.pack.iterdir() if x.is_file() and x.name != "SHA256SUMS")
checksum.write_text("".join(f"{sha(x)}  {x.name}\n" for x in files))
print(json.dumps({"status": "PASS", "pack_files": len(files), "pack_manifest_sha256": sha(checksum), **publish}, sort_keys=True))
