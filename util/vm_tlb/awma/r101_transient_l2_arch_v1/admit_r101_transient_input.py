#!/usr/bin/env python3
"""Fail-closed admission and deterministic runtime-sidecar derivation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import lzma
import shutil
import subprocess
from pathlib import Path


REPO = Path("/root/workspace/accel-sim-framework-awma-r101-transient-l2-arch-174-v1")
PACK_PATH = "docs/vm_tlb/review_packs/AWMA_R101_TRANSIENT_L2_SIM_CAPTURE_109_V1"
DURABLE = Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r101_transient_l2_sim_capture_20260927")
OUTPUT = Path("/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/input")
REQUIRED = {
    "README.md", "ACCEPTED_INPUT_BINDING.json", "CAPTURE_SCOPE_PREREGISTRATION.json",
    "BUFFER_REGION_MAP.tsv", "REGION_LIFETIME.tsv", "NATIVE_KERNEL_BINDING.tsv",
    "SIM_CAPTURE_MANIFEST.json", "TRACE_MEMBER_MANIFEST.tsv",
    "TERMINAL_AND_COMPLETENESS.md", "RAW_DATA_INDEX.tsv", "SHA256SUMS",
}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def blob(commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=REPO)


def table(data: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(data.decode().splitlines(), delimiter="\t"))


def field(row: dict[str, str], aliases: tuple[str, ...]) -> str:
    for name in aliases:
        if name in row and row[name] != "":
            return row[name]
    raise RuntimeError(f"missing required field {aliases}; columns={sorted(row)}")


def resolve_payload(relative_or_absolute: str) -> Path:
    candidate = Path(relative_or_absolute)
    if candidate.is_absolute():
        return candidate
    for root in (DURABLE, DURABLE / "raw", DURABLE / "trace", DURABLE / "traces"):
        path = root / candidate
        if path.exists():
            return path
    raise RuntimeError(f"cannot resolve producer payload {relative_or_absolute}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--producer-commit", required=True)
    args = parser.parse_args()
    commit = args.producer_commit
    names = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", commit, PACK_PATH], cwd=REPO,
        text=True).splitlines()
    present = {Path(name).name for name in names}
    missing = REQUIRED - present
    if missing:
        raise RuntimeError(f"producer pack incomplete: {sorted(missing)}")
    readme = blob(commit, f"{PACK_PATH}/README.md").decode()
    if "R101_TRANSIENT_SIM_CAPTURE_PASS" not in readme:
        raise RuntimeError("producer is not READY/PASS")
    manifest_lines = blob(commit, f"{PACK_PATH}/SHA256SUMS").decode().splitlines()
    for line in manifest_lines:
        expected, name = line.split("  ", 1)
        actual = sha_bytes(blob(commit, f"{PACK_PATH}/{name}"))
        if actual != expected:
            raise RuntimeError(f"producer review hash mismatch: {name}")

    capture = json.loads(blob(commit, f"{PACK_PATH}/SIM_CAPTURE_MANIFEST.json"))
    encoded = json.dumps(capture, sort_keys=True)
    if "SIM_INPUT_R101_L512_TRANSIENT_V1" not in encoded:
        raise RuntimeError("stable simulator input identity missing")
    if "R101_DISCOVERY_L512_ACCEPTED_PAYLOAD" not in encoded:
        raise RuntimeError("accepted scientific payload relation missing")
    if any(token in encoded.lower() for token in ("synthetic_matrix", "last_read")):
        raise RuntimeError("forbidden synthetic/future metadata")

    terminal = blob(commit, f"{PACK_PATH}/TERMINAL_AND_COMPLETENESS.md").decode().lower()
    for required in ("complete", "drop=0", "overflow=0"):
        if required not in terminal:
            raise RuntimeError(f"terminal gate missing {required}")

    members = table(blob(commit, f"{PACK_PATH}/TRACE_MEMBER_MANIFEST.tsv"))
    if not members:
        raise RuntimeError("empty trace manifest")
    payloads = []
    for row in members:
        path = resolve_payload(field(row, ("path", "trace_path", "payload_path", "trace_member")))
        expected = field(row, ("sha256", "trace_sha256", "payload_sha256"))
        if not path.is_file() or sha(path) != expected:
            raise RuntimeError(f"trace payload hash mismatch: {path}")
        if path.suffix != ".xz":
            raise RuntimeError(f"unexpected trace encoding: {path}")
        with lzma.open(path, "rb") as stream:
            if not stream.read(32):
                raise RuntimeError(f"empty compressed trace: {path}")
        payloads.append(path)

    regions = table(blob(commit, f"{PACK_PATH}/BUFFER_REGION_MAP.tsv"))
    if len(regions) != 4:
        raise RuntimeError("exactly four A/B/X0/X1 regions required")
    normalized_regions = []
    expected_names = {"A", "B", "X0", "X1"}
    for row in regions:
        name = field(row, ("region", "region_id", "buffer", "name")).upper().replace("/C", "")
        base = int(field(row, ("base", "base_address", "device_base", "device_address")), 0)
        size = int(field(row, ("bytes", "size_bytes", "byte_length")), 0)
        if name not in expected_names or base % 128 or size % 128 or size <= 0:
            raise RuntimeError(f"invalid region record: {row}")
        normalized_regions.append((name, base, base + size))
    if {name for name, _, _ in normalized_regions} != expected_names:
        raise RuntimeError("region identity mismatch")
    normalized_regions.sort(key=lambda item: (item[1], item[2]))
    for left, right in zip(normalized_regions, normalized_regions[1:]):
        if left[2] > right[1]:
            raise RuntimeError("overlapping transient regions")

    lifetime = table(blob(commit, f"{PACK_PATH}/REGION_LIFETIME.tsv"))
    if not lifetime:
        raise RuntimeError("empty lifetime table")
    transitions = []
    for row in lifetime:
        ordinal = int(field(row, ("completed_kernel_ordinal", "kernel_ordinal", "boundary_ordinal")))
        name = field(row, ("region", "region_id", "buffer", "name")).upper().replace("/C", "")
        generation = int(field(row, ("generation", "generation_after", "epoch")))
        state = field(row, ("live_after", "state_after", "live")).upper()
        live = state in {"1", "TRUE", "LIVE"}
        if state not in {"0", "1", "FALSE", "TRUE", "DEAD", "LIVE"}:
            raise RuntimeError(f"invalid liveness state: {state}")
        transitions.append((ordinal, name, generation, live))
    expected_kernels = max(ordinal for ordinal, _, _, _ in transitions)

    # Producer may explicitly publish initial state columns. If absent, fail
    # closed rather than guessing which ping-pong generation is live.
    initial = {}
    for row in regions:
        name = field(row, ("region", "region_id", "buffer", "name")).upper().replace("/C", "")
        generation = int(field(row, ("initial_generation", "generation")))
        state = field(row, ("initial_live", "live_initial", "initial_state")).upper()
        if state not in {"0", "1", "FALSE", "TRUE", "DEAD", "LIVE"}:
            raise RuntimeError(f"invalid initial liveness: {state}")
        initial[name] = (generation, state in {"1", "TRUE", "LIVE"})

    OUTPUT.mkdir(parents=True, exist_ok=True)
    trace_dir = OUTPUT / "traces"
    if trace_dir.exists():
        shutil.rmtree(trace_dir)
    trace_dir.mkdir()
    for path in payloads:
        (trace_dir / path.name).symlink_to(path)
    kernelslist_source = resolve_payload("kernelslist.g")
    kernelslist = kernelslist_source.read_text().splitlines()
    if kernelslist != [path.name for path in payloads]:
        raise RuntimeError("kernelslist/trace-manifest ordering mismatch")
    (trace_dir / "kernelslist.g").write_text("\n".join(kernelslist) + "\n")

    ids = {"A": 0, "B": 1, "X0": 2, "X1": 3}
    by_name = {name: (base, limit) for name, base, limit in normalized_regions}
    runtime = ["AWMA_TRANSIENT_L2_RUNTIME_V1", "LINE_SIZE 128",
               f"EXPECTED_KERNELS {expected_kernels}"]
    for name in ("A", "B", "X0", "X1"):
        base, limit = by_name[name]; generation, live = initial[name]
        runtime.append(f"REGION {ids[name]} {base:#x} {limit:#x} {generation} {int(live)}")
    for ordinal, name, generation, live in sorted(transitions):
        runtime.append(f"BOUNDARY {ordinal} {ids[name]} {generation} {int(live)}")
    runtime_path = OUTPUT / "transient_l2_runtime.tsv"
    runtime_path.write_text("\n".join(runtime) + "\n")
    receipt = {
        "status": "PASS", "producer_commit": commit,
        "input_identity": "SIM_INPUT_R101_L512_TRANSIENT_V1",
        "trace_members": [{"path": str(path), "sha256": sha(path)} for path in payloads],
        "kernelslist_sha256": sha(trace_dir / "kernelslist.g"),
        "runtime_sidecar_sha256": sha(runtime_path),
        "region_count": 4, "expected_kernels": expected_kernels,
        "raw_immutable": True,
    }
    (OUTPUT / "ADMISSION_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
