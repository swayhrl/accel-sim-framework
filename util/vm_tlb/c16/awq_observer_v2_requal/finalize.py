#!/usr/bin/env python3
"""Assemble, manifest, durably publish, and copy-back verify the canary raw payload."""

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


REQUIRED = [
    "OBSERVER_V2_RUNTIME_RECEIPT.json",
    "NATIVE_SAMPLES.tsv",
    "NEUTRALITY_RESULT.json",
    "SEMANTIC_ORDER_RECEIPT.json",
    "KERNEL_INVENTORY_RECEIPT.json",
    "NSYS_STRUCTURAL_RECEIPT.json",
    "GPU_ACTIVE_BUDGET.json",
    "GPU_LOCK_RECEIPT.json",
    "FINAL_DECISION.json",
    "TESTS.json",
]


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    raw, review = args.raw.resolve(), args.review.resolve()
    for name in REQUIRED:
        shutil.copy2(review / name, raw / name)

    remote_host = "hrl174new"
    remote_path = f"/root/share/mnt164/huangrulin/c16_ai_workload/provenance/c16_awq_observer_v2_requal_canary_109_v1/{args.run_id}"
    copyback = Path("/data/c16/awq_observer_v2_requal_canary_v1/copyback_verify") / args.run_id
    if copyback.exists():
        raise SystemExit(f"copyback target already exists: {copyback}")
    remote_exists = subprocess.run(["ssh", remote_host, "test", "-e", remote_path]).returncode == 0

    files = sorted(path for path in raw.iterdir() if path.is_file() and path.name not in {"RAW_INDEX.tsv", "RAW_SHA256SUMS"})
    with (raw / "RAW_INDEX.tsv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["artifact", "node109_path", "bytes", "sha256", "node164_path"],
                                delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for path in files:
            writer.writerow({"artifact": path.name, "node109_path": str(path), "bytes": path.stat().st_size,
                             "sha256": sha(path), "node164_path": f"{remote_path}/{path.name}"})
    manifest_files = sorted(path for path in raw.iterdir() if path.is_file() and path.name != "RAW_SHA256SUMS")
    (raw / "RAW_SHA256SUMS").write_text("".join(f"{sha(path)}  {path.name}\n" for path in manifest_files))

    subprocess.run(["ssh", remote_host, "mkdir", "-p", str(Path(remote_path).parent)], check=True)
    subprocess.run(["rsync", "-rt", "--no-owner", "--no-group", "--no-perms",
                    f"{raw}/", f"{remote_host}:{remote_path}/"], check=True)
    verify = subprocess.run(["ssh", remote_host, f"cd {remote_path} && sha256sum -c RAW_SHA256SUMS"],
                            check=True, text=True, stdout=subprocess.PIPE).stdout
    copyback.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["rsync", "-a", f"{remote_host}:{remote_path}/", f"{copyback}/"], check=True)

    manifest_rows = []
    for line in (raw / "RAW_SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        local = raw / name
        back = copyback / name
        ok = back.is_file() and sha(local) == sha(back) == digest and local.stat().st_size == back.stat().st_size
        manifest_rows.append(ok)
    if not all(manifest_rows):
        raise SystemExit("copyback byte/SHA verification failed")

    shutil.copy2(raw / "RAW_INDEX.tsv", review / "RAW_INDEX.tsv")
    shutil.copy2(raw / "RAW_SHA256SUMS", review / "RAW_SHA256SUMS")
    payload_bytes = sum(path.stat().st_size for path in raw.iterdir() if path.is_file())
    receipt = {
        "status": "PASS_DURABLE_PUBLISH_AND_COPYBACK",
        "local_raw_path": str(raw),
        "remote_host": remote_host,
        "remote_path": remote_path,
        "remote_path_preexisted_from_attribute_only_failed_publish_attempt": remote_exists,
        "publish_transport": "rsync content/times without owner/group/perms",
        "remote_verify": "PASS",
        "remote_verify_lines": len(verify.splitlines()),
        "copyback_path": str(copyback),
        "copyback_verify": "PASS",
        "manifest_entries": len(manifest_files),
        "manifest_sha256": sha(raw / "RAW_SHA256SUMS"),
        "payload_bytes": payload_bytes,
    }
    (review / "PUBLISH_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
