#!/usr/bin/env python3
"""Correct provenance metadata only after reconstructing the immutable source chain."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile

HEX64 = re.compile(r"^[0-9a-f]{64}$")


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_bytes(repo, spec):
    return subprocess.check_output(["git", "-C", str(repo), "show", spec])


def duplicate_detail(observed, expected):
    matches = []
    if len(observed) == len(expected) + 1:
        for i in range(len(observed)):
            if observed[:i] + observed[i + 1:] == expected:
                matches.append({"index": i, "duplicated_hex": observed[i]})
    return matches


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--pack", type=Path, required=True)
    p.add_argument("--gate-commit", required=True)
    p.add_argument("--gate-path", required=True)
    p.add_argument("--source-archive", type=Path, required=True)
    p.add_argument("--source-member", required=True)
    p.add_argument("--patch-artifact", type=Path, required=True)
    p.add_argument("--source-root", type=Path, required=True)
    p.add_argument("--build-log", type=Path, required=True)
    p.add_argument("--build-object", type=Path, required=True)
    p.add_argument("--binary", type=Path, required=True)
    p.add_argument("--historical-binary-sha", required=True)
    p.add_argument("--original-head", required=True)
    p.add_argument("--receipt", type=Path, required=True)
    args = p.parse_args()

    head = subprocess.check_output(["git", "-C", str(args.repo), "rev-parse", "HEAD"], text=True).strip()
    if head != args.original_head:
        raise RuntimeError(f"refuse correction: HEAD {head} != original {args.original_head}")
    gate_raw = git_bytes(args.repo, f"{args.gate_commit}:{args.gate_path}")
    gate = json.loads(gate_raw)
    bindings = gate["bindings"]
    expected = {
        "base_source": bindings["old_source_sha256"],
        "patch_artifact": bindings["patch_artifact_sha256"],
        "patch_plain": bindings["patch_sha256"],
        "patched_generator": bindings["patched_generator_sha256"],
    }
    if not all(HEX64.fullmatch(v) for v in expected.values()):
        raise RuntimeError("immutable gate contains non-64hex SHA")

    with tarfile.open(args.source_archive) as tf:
        base_bytes = tf.extractfile(args.source_member).read()
    patch_bytes = args.patch_artifact.read_bytes()
    patch_plain = gzip.decompress(patch_bytes)
    generator = args.source_root / args.source_member
    actual = {
        "base_source": sha_bytes(base_bytes),
        "patch_artifact": sha_bytes(patch_bytes),
        "patch_plain": sha_bytes(patch_plain),
        "patched_generator": sha_file(generator),
        "build_log": sha_file(args.build_log),
        "build_object": sha_file(args.build_object),
        "binary": sha_file(args.binary),
        "source_archive": sha_file(args.source_archive),
        "setup": sha_file(args.source_root / "setup_residual_parallelism.py"),
        "patched_header": sha_file(args.source_root / "awq_ext/quantization/gemm_cuda.h"),
    }
    for name in ("base_source", "patch_artifact", "patch_plain", "patched_generator"):
        if actual[name] != expected[name]:
            raise RuntimeError(f"provenance mismatch {name}: {actual[name]} != {expected[name]}")
    if actual["binary"] != args.historical_binary_sha:
        raise RuntimeError("historical binary identity mismatch")

    with tempfile.TemporaryDirectory(prefix="c16_residual_metadata_") as td:
        temp = Path(td)
        with tarfile.open(args.source_archive) as tf:
            tf.extractall(temp)
        patch_file = temp / "gate.patch"
        patch_file.write_bytes(patch_plain)
        subprocess.run(["git", "-C", str(temp), "apply", "--check", "--unsafe-paths", str(patch_file)], check=True)
        subprocess.run(["git", "-C", str(temp), "apply", "--unsafe-paths", str(patch_file)], check=True)
        regenerated_generator = sha_file(temp / args.source_member)
        regenerated_header = sha_file(temp / "awq_ext/quantization/gemm_cuda.h")
    if regenerated_generator != actual["patched_generator"] or regenerated_header != actual["patched_header"]:
        raise RuntimeError("base+patch reconstruction does not match source root")

    log_text = args.build_log.read_text(errors="replace")
    required_log_fragments = [str(generator), str(args.build_object), str(args.binary),
                              "-gencode arch=compute_89,code=sm_89",
                              "building 'awq_residual_parallelism_ext' extension"]
    missing = [x for x in required_log_fragments if x not in log_text]
    if missing:
        raise RuntimeError(f"build log source-chain fragments missing: {missing}")

    source_path = args.pack / "SOURCE_AND_GATE.json"
    build_path = args.pack / "BUILD_RECEIPT.json"
    source = json.loads(source_path.read_text())
    build = json.loads(build_path.read_text())
    original = {
        "SOURCE_AND_GATE.base_source.sha256": source["base_source"]["sha256"],
        "SOURCE_AND_GATE.gate.patch_artifact_sha256": source["gate"]["patch_artifact_sha256"],
        "SOURCE_AND_GATE.gate.patched_generator_sha256": source["gate"]["patched_generator_sha256"],
        "BUILD_RECEIPT.patched_generator_sha256": build["patched_generator_sha256"],
    }
    corrected = {
        "SOURCE_AND_GATE.base_source.sha256": expected["base_source"],
        "SOURCE_AND_GATE.gate.patch_artifact_sha256": expected["patch_artifact"],
        "SOURCE_AND_GATE.gate.patched_generator_sha256": expected["patched_generator"],
        "BUILD_RECEIPT.patched_generator_sha256": expected["patched_generator"],
    }
    source["base_source"]["sha256"] = expected["base_source"]
    source["gate"]["patch_artifact_sha256"] = expected["patch_artifact"]
    source["gate"]["patched_generator_sha256"] = expected["patched_generator"]
    build["patched_generator_sha256"] = expected["patched_generator"]
    source_path.write_text(json.dumps(source, indent=2) + "\n")
    build_path.write_text(json.dumps(build, indent=2) + "\n")

    gate_blob = subprocess.check_output(["git", "-C", str(args.repo), "rev-parse", f"{args.gate_commit}:{args.gate_path}"], text=True).strip()
    original_tree = subprocess.check_output(["git", "-C", str(args.repo), "rev-parse", f"{args.original_head}^{{tree}}"], text=True).strip()
    receipt = {
        "status": "PASS_METADATA_CORRECTION",
        "scope": "metadata only; no scientific payload, build, binary, or experiment execution",
        "original_science_commit": args.original_head,
        "original_science_tree": original_tree,
        "immutable_gate": {"commit": args.gate_commit, "path": args.gate_path,
                           "blob": gate_blob, "content_sha256": sha_bytes(gate_raw)},
        "original_invalid_values": original,
        "corrected_values": corrected,
        "duplication_analysis": {k: duplicate_detail(original[k], corrected[k]) for k in original},
        "error_cause": "The four active metadata values each contained one duplicated hexadecimal nibble introduced during manual transcription; immutable gate and reconstructed artifacts prove the exact values.",
        "actual_artifacts": actual,
        "expected_from_immutable_gate": expected,
        "comparisons": {k: actual[k] == expected[k] for k in expected},
        "reconstruction": {"base_plus_patch_generator_sha256": regenerated_generator,
                           "base_plus_patch_header_sha256": regenerated_header,
                           "matches_existing_source_root": True},
        "build_chain": {"required_log_fragments_present": True,
                        "build_log_path": str(args.build_log), "build_object_path": str(args.build_object),
                        "binary_path": str(args.binary), "binary_bytes": args.binary.stat().st_size,
                        "binary_mtime": str(args.binary.stat().st_mtime_ns)},
        "prohibited_actions_attestation": {"cuda_initialized": False, "extension_imported": False,
                                           "gpu_lock_requested": False, "experiment_rerun": False,
                                           "recompiled": False, "lane4_partial_accessed": False}
    }
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
