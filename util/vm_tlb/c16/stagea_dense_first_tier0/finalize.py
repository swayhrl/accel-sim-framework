#!/usr/bin/env python3
"""Assemble manifests, durable-publish all raw, and copy-back verify."""

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def manifest(path, files):
    path.write_text("".join(f"{sha(item)}  {item.name}\n" for item in sorted(files, key=lambda value: value.name)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--contract-gate", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--refresh-existing", action="store_true")
    args = parser.parse_args()
    repo, raw, review, preflight = (value.resolve() for value in (args.repo, args.raw, args.review, args.preflight))

    # Bring immutable authorities and CPU qualification receipts into the pack.
    for name in ("CONTRACT_AUTHORITY.json", "CPU_PREFLIGHT.json", "SOURCE_VALIDATION.json", "SYNTHETIC_TESTS.json",
                 "RESULT_SCHEMA.json", "POINT_TOKEN_BINDINGS.tsv", "EXECUTION_AND_ESTIMATOR_NOTES.md",
                 "AUTHORITY_VERIFICATION.json"):
        shutil.copy2(preflight / name, review / name)
    shutil.copy2(args.contract_gate / "C16_STAGEA_DENSE_FIRST_TIER0_109_CONTRACT_V1.json", review / "C16_STAGEA_DENSE_FIRST_TIER0_109_CONTRACT_V1.json")
    shutil.copy2(args.contract_gate / "CONTRACT_DISCOVERY_RECEIPT.json", review / "CONTRACT_DISCOVERY_RECEIPT.json")

    source_root = repo / "util/vm_tlb/c16/stagea_dense_first_tier0"
    source_files = sorted(source_root.glob("*.py"))
    source_receipt = {
        "status": "PASS",
        "contract_commit": "fad9da8116c8ad794f99a93f153b0866162158a4",
        "contract_tree": "c657f1655ffabbeb0942732bdff08c8df8e79987",
        "contract_json_sha256": "a71349283b1661cb23d86cc61dfad6ab5ea2cd8752ca4252bbc1d2feee5acb08",
        "producer_base_commit": "137e3414c9c8e59cf1b167e5acc14149fb6273d6",
        "bf16_v1_observer_sha256": sha(repo / "util/vm_tlb/c16/stagea_runtime_qualification/runner.py"),
        "awq_v2_observer_sha256": sha(source_root / "observer_v2_authority.py"),
        "tool_sha256": {path.name: sha(path) for path in source_files},
        "runtime": "/data/c16/envs/c16-vllm-v0.30.0-sm89-v1",
        "vllm_source_commit": "ced6857afa0ea7b2e3f0846a62e1394e90f15607",
    }
    write_json(review / "SOURCE_AND_BUILD_RECEIPT.json", source_receipt)

    point_status = {row["point_id"]: row for row in csv.DictReader((review / "POINT_EXECUTION_STATUS.tsv").open(), delimiter="\t")}
    correctness_stop = {
        "status": "CORRECTNESS_STOPS_PRESERVED",
        "MP02": {"status": point_status["MP02"]["gpu_execution_status"], "observed_or_nsys_run": False},
        "MP03": {"status": point_status["MP03"]["gpu_execution_status"], "observed_or_nsys_run": False},
        "native_samples_rerun": False,
        "threshold_or_tolerance_changed": False,
        "observer_semantics_changed": False,
    }
    write_json(review / "CORRECTNESS_STOP_RECEIPT.json", correctness_stop)
    (review / "MANIFEST_POLICY.md").write_text(
        "# Manifest policy\n\n"
        "`RAW_PAYLOAD_SHA256SUMS` covers the immutable scientific/raw payload and `RAW_INDEX.tsv`, excluding only the final decision and manifest files to avoid self-reference. "
        "Its SHA256 is the `durable_raw_manifest_sha256` recorded in `FINAL_DECISION.json`.\n\n"
        "`REVIEW_PAYLOAD_SHA256SUMS` covers the review payload before the final decision and publish receipt; its SHA256 is `review_pack_sha256`. "
        "`RAW_SHA256SUMS` and `SHA256SUMS` are the final non-self-referential full-directory manifests.\n"
    )

    # Copy every current review artifact except the provisional final into raw.
    review_copy_exclusions = {"FINAL_DECISION.json", "PUBLISH_RECEIPT.json", "SHA256SUMS",
                              "REVIEW_PAYLOAD_SHA256SUMS", "RAW_PAYLOAD_SHA256SUMS", "RAW_SHA256SUMS", "RAW_INDEX.tsv"}
    for path in review.iterdir():
        if path.is_file() and path.name not in review_copy_exclusions:
            shutil.copy2(path, raw / path.name)

    excluded = {"RAW_INDEX.tsv", "RAW_PAYLOAD_SHA256SUMS", "RAW_SHA256SUMS", "REVIEW_PAYLOAD_SHA256SUMS", "FINAL_DECISION.json"}
    raw_payload_files = sorted(path for path in raw.rglob("*") if path.is_file() and path.name not in excluded)
    remote_root = "/root/share/mnt164/huangrulin/c16_ai_workload/measurement_campaign/stagea_dense_first_tier0_v1"
    remote_path = f"{remote_root}/{args.run_id}"
    with (raw / "RAW_INDEX.tsv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["artifact", "node109_path", "bytes", "sha256", "node164_path"], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for path in raw_payload_files:
            relative = path.relative_to(raw).as_posix()
            writer.writerow({"artifact": relative, "node109_path": str(path), "bytes": path.stat().st_size,
                             "sha256": sha(path), "node164_path": f"{remote_path}/{relative}"})
    raw_payload_files.append(raw / "RAW_INDEX.tsv")
    (raw / "RAW_PAYLOAD_SHA256SUMS").write_text("".join(
        f"{sha(path)}  {path.relative_to(raw).as_posix()}\n" for path in sorted(raw_payload_files)
    ))
    shutil.copy2(raw / "RAW_INDEX.tsv", review / "RAW_INDEX.tsv")
    shutil.copy2(raw / "RAW_PAYLOAD_SHA256SUMS", review / "RAW_PAYLOAD_SHA256SUMS")

    review_payload_files = sorted(path for path in review.iterdir() if path.is_file()
                                  and path.name not in {"FINAL_DECISION.json", "PUBLISH_RECEIPT.json", "REVIEW_PAYLOAD_SHA256SUMS", "RAW_SHA256SUMS", "SHA256SUMS"})
    manifest(review / "REVIEW_PAYLOAD_SHA256SUMS", review_payload_files)
    final = json.loads((review / "FINAL_DECISION.json").read_text())
    final["durable_raw_manifest_sha256"] = sha(raw / "RAW_PAYLOAD_SHA256SUMS")
    final["review_pack_sha256"] = sha(review / "REVIEW_PAYLOAD_SHA256SUMS")
    write_json(review / "FINAL_DECISION.json", final)
    shutil.copy2(review / "FINAL_DECISION.json", raw / "FINAL_DECISION.json")
    shutil.copy2(review / "REVIEW_PAYLOAD_SHA256SUMS", raw / "REVIEW_PAYLOAD_SHA256SUMS")

    raw_full_files = sorted(path for path in raw.rglob("*") if path.is_file() and path.name != "RAW_SHA256SUMS")
    # Full manifest paths are relative to raw root, including point subdirectories.
    (raw / "RAW_SHA256SUMS").write_text("".join(
        f"{sha(path)}  {path.relative_to(raw).as_posix()}\n" for path in raw_full_files
    ))
    shutil.copy2(raw / "RAW_SHA256SUMS", review / "RAW_SHA256SUMS")

    remote_host = "hrl174new"
    remote_exists = subprocess.run(["ssh", remote_host, "test", "-e", remote_path]).returncode == 0
    if remote_exists and not args.refresh_existing:
        raise SystemExit(f"durable target already exists: {remote_path}")
    subprocess.run(["ssh", remote_host, "mkdir", "-p", remote_root], check=True)
    subprocess.run(["rsync", "-rt", "--no-owner", "--no-group", "--no-perms",
                    f"{raw}/", f"{remote_host}:{remote_path}/"], check=True)
    remote_verify = subprocess.run(["ssh", remote_host, f"cd {remote_path} && sha256sum -c RAW_SHA256SUMS"],
                                   check=True, text=True, stdout=subprocess.PIPE).stdout

    copyback = Path("/data/c16/stagea_dense_first_tier0_v1/copyback_verify") / args.run_id
    if copyback.exists() and not args.refresh_existing:
        raise SystemExit(f"copyback target exists: {copyback}")
    copyback.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["rsync", "-rt", "--no-owner", "--no-group", "--no-perms",
                    f"{remote_host}:{remote_path}/", f"{copyback}/"], check=True)
    for path in raw_full_files + [raw / "RAW_SHA256SUMS"]:
        relative = path.relative_to(raw)
        other = copyback / relative
        if not other.is_file() or other.stat().st_size != path.stat().st_size or sha(other) != sha(path):
            raise SystemExit(f"copyback mismatch: {relative}")

    publish = {
        "status": "PASS_DURABLE_PUBLISH_AND_COPYBACK",
        "local_raw_path": str(raw), "remote_host": remote_host, "remote_path": remote_path,
        "remote_verify": "PASS", "remote_verify_lines": len(remote_verify.splitlines()),
        "copyback_path": str(copyback), "copyback_verify": "PASS",
        "raw_payload_manifest_sha256": final["durable_raw_manifest_sha256"],
        "raw_full_manifest_sha256": sha(raw / "RAW_SHA256SUMS"),
        "payload_bytes": sum(path.stat().st_size for path in raw_full_files),
    }
    write_json(review / "PUBLISH_RECEIPT.json", publish)
    review_full_files = sorted(path for path in review.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    manifest(review / "SHA256SUMS", review_full_files)
    print(json.dumps(publish, sort_keys=True))


if __name__ == "__main__":
    main()
