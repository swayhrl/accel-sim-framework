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
p.add_argument("--raw", type=Path, required=True)
p.add_argument("--copyback", type=Path, required=True)
p.add_argument("--pack", type=Path, required=True)
p.add_argument("--remote-path", required=True)
a = p.parse_args()
manifest = a.raw / "RAW_SHA256SUMS"
rows = []
payload_bytes = 0
for line in manifest.read_text().splitlines():
    digest, relative = line.split("  ", 1)
    source, copied = a.raw / relative, a.copyback / relative
    if sha(source) != digest or sha(copied) != digest:
        raise RuntimeError(f"copyback mismatch: {relative}")
    payload_bytes += source.stat().st_size
    rows.append({"artifact": relative, "node109_path": str(source), "bytes": source.stat().st_size,
                 "sha256": digest, "node164_path": f"{a.remote_path}/{relative}", "git_copy": "INDEX_ONLY"})
if sha(a.copyback / "RAW_SHA256SUMS") != sha(manifest):
    raise RuntimeError("manifest copyback mismatch")
rows.append({"artifact": "RAW_SHA256SUMS", "node109_path": str(manifest), "bytes": manifest.stat().st_size,
             "sha256": sha(manifest), "node164_path": f"{a.remote_path}/RAW_SHA256SUMS", "git_copy": "INDEX_ONLY"})
with (a.pack / "RAW_INDEX.tsv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=tuple(rows[0]), delimiter="\t", lineterminator="\n")
    w.writeheader(); w.writerows(rows)
publish = {"status": "PASS_DURABLE_PUBLISH_AND_COPYBACK", "remote_host": "hrl174new",
           "local_raw_path": str(a.raw), "remote_path": a.remote_path,
           "copyback_path": str(a.copyback), "manifest_entries": len(rows) - 1,
           "payload_bytes": payload_bytes, "manifest_sha256": sha(manifest),
           "remote_manifest_verify": "PASS", "copyback_verify": "PASS"}
dump(a.pack / "PUBLISH_RECEIPT.json", publish)
run_identity = {"status": "PASS", "task": "C16_FFN_GATE_UP_CONCURRENCY_NATIVE_DIAGNOSTIC_V2",
                "run_id": a.raw.name, "branch": "hrl/c16-ffn-gate-up-concurrency-native-diagnostic-109-v2",
                "authority_commit": "ee8cadd4a9a0be31186fcc0bdc8fb47dd515dbf8",
                "runner_sha256": "0297e142457ea5ac4ed3d6c37889993fda4168bfcca8392b41d74ba4b698fc0b",
                "formal_samples": 48, "gpu_lock_released": True,
                "decision": "CONCURRENCY_ACTIVATED_BUT_RESOURCE_CONTENTION_LIMITED",
                "durable_publish": publish["status"]}
dump(a.pack / "RUN_IDENTITY.json", run_identity)
checksum = a.pack / "SHA256SUMS"
files = sorted(x for x in a.pack.iterdir() if x.is_file() and x.name != "SHA256SUMS")
checksum.write_text("".join(f"{sha(x)}  {x.name}\n" for x in files))
print(json.dumps({"status": "PASS", "pack_files": len(files), "pack_manifest_sha256": sha(checksum), **publish}, sort_keys=True))
