#!/usr/bin/env python3
"""Validate exact 64hex SHA fields and immutable-gate cross-file identity."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile

HEX64 = re.compile(r"^[0-9a-f]{64}$")


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_sha_fields(value, prefix=""):
    out = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            if key == "original_invalid_values":
                continue
            if key.endswith("sha256") and isinstance(child, str):
                out.append((path, child))
            out.extend(collect_sha_fields(child, path))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            out.extend(collect_sha_fields(child, f"{prefix}[{i}]"))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--pack", type=Path, required=True)
    p.add_argument("--gate-commit", required=True)
    p.add_argument("--gate-path", required=True)
    p.add_argument("--source-archive", type=Path, required=True)
    p.add_argument("--source-member", required=True)
    p.add_argument("--patch-artifact", type=Path, required=True)
    p.add_argument("--patched-generator", type=Path, required=True)
    p.add_argument("--binary", type=Path, required=True)
    p.add_argument("--historical-binary-sha", required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    source = json.loads((args.pack / "SOURCE_AND_GATE.json").read_text())
    build = json.loads((args.pack / "BUILD_RECEIPT.json").read_text())
    receipt = json.loads((args.pack / "METADATA_CORRECTION_RECEIPT.json").read_text())
    gate_raw = subprocess.check_output(["git", "-C", str(args.repo), "show", f"{args.gate_commit}:{args.gate_path}"])
    gate = json.loads(gate_raw)
    all_fields = []
    for label, obj in (("SOURCE_AND_GATE", source), ("BUILD_RECEIPT", build),
                       ("METADATA_CORRECTION_RECEIPT", receipt), ("IMMUTABLE_GATE", gate)):
        for path, value in collect_sha_fields(obj):
            all_fields.append((f"{label}.{path}", value, bool(HEX64.fullmatch(value))))
    invalid = [row for row in all_fields if not row[2]]
    if invalid:
        raise RuntimeError(f"non-64hex active SHA fields: {invalid}")
    with tarfile.open(args.source_archive) as tf:
        base_sha = sha_bytes(tf.extractfile(args.source_member).read())
    patch_bytes = args.patch_artifact.read_bytes()
    actual = {"base": base_sha, "patch_artifact": sha_bytes(patch_bytes),
              "patch_plain": sha_bytes(gzip.decompress(patch_bytes)),
              "patched_generator": sha_file(args.patched_generator), "binary": sha_file(args.binary)}
    b = gate["bindings"]
    checks = {
        "source_base_equals_gate": source["base_source"]["sha256"] == b["old_source_sha256"] == actual["base"],
        "source_patch_equals_gate": source["gate"]["patch_artifact_sha256"] == b["patch_artifact_sha256"] == actual["patch_artifact"],
        "patch_plain_equals_gate": source["gate"]["patch_sha256"] == b["patch_sha256"] == actual["patch_plain"],
        "source_generator_equals_gate_actual": source["gate"]["patched_generator_sha256"] == b["patched_generator_sha256"] == actual["patched_generator"],
        "build_generator_equals_source_gate_actual": build["patched_generator_sha256"] == source["gate"]["patched_generator_sha256"] == actual["patched_generator"],
        "binary_identity": build["binary_sha256"] == args.historical_binary_sha == actual["binary"],
        "receipt_comparisons_all_true": all(receipt["comparisons"].values()),
    }
    if not all(checks.values()):
        raise RuntimeError(f"cross-file validation failure: {checks}")
    result = {"status": "PASS", "active_sha256_fields_checked": len(all_fields),
              "all_active_sha256_exact_64hex": True, "checks": checks, "actual": actual}
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
