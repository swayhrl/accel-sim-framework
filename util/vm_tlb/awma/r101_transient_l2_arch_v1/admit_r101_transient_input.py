#!/usr/bin/env python3
"""Fail-closed admission and deterministic runtime-sidecar derivation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import lzma
import re
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
    for root in (
        DURABLE,
        DURABLE / "raw",
        DURABLE / "raw/formal_full5/raw",
        DURABLE / "trace",
        DURABLE / "traces",
    ):
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
    accepted_payload_sha256 = (
        "1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234")
    accepted_output_sha256 = (
        "36aaed3f8360aa099301ae1d705bc2e6ab5ba61586adaf7ead93ecab808dc1b0")
    binding = capture.get("accepted_input_binding", {})
    if binding.get("payload_sha256") != accepted_payload_sha256 or \
            binding.get("accepted_output_sha256") != accepted_output_sha256 or \
            capture.get("output_sha256") != accepted_output_sha256 or \
            capture.get("output_bitwise_accepted") is not True:
        raise RuntimeError("accepted scientific payload/output binding mismatch")
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
    if len(members) != 18:
        raise RuntimeError(f"expected complete 18-kernel payload, got {len(members)}")
    for expected_index, row in enumerate(members):
        if int(field(row, ("roi_launch_index",))) != expected_index:
            raise RuntimeError("trace manifest launch order is not contiguous")
        if field(row, ("grammar_status",)) != "PASS" or \
                field(row, ("traceg_xz_status",)) != "PASS":
            raise RuntimeError(f"trace member is not qualified: {row}")
        path = resolve_payload(field(row, ("traceg_member", "path", "trace_path",
                                           "payload_path", "trace_member")))
        expected = field(row, ("traceg_sha256", "sha256", "trace_sha256",
                               "payload_sha256"))
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
        base = int(field(row, ("base_device_address_hex", "base", "base_address",
                               "device_base", "device_address")), 0)
        size = int(field(row, ("bytes", "size_bytes", "byte_length")), 0)
        limit = int(field(row, ("end_exclusive_hex",)), 0)
        if limit != base + size:
            raise RuntimeError(f"region limit/size mismatch: {row}")
        if name not in expected_names or base % 128 or size % 128 or size <= 0:
            raise RuntimeError(f"invalid region record: {row}")
        normalized_regions.append((name, base, base + size))
    if {name for name, _, _ in normalized_regions} != expected_names:
        raise RuntimeError("region identity mismatch")
    normalized_regions.sort(key=lambda item: (item[1], item[2]))
    for left, right in zip(normalized_regions, normalized_regions[1:]):
        if left[2] > right[1]:
            raise RuntimeError("overlapping transient regions")

    address_pattern = re.compile(rb"0x[0-9a-fA-F]+")
    probe_indices = {"X0": 2, "A": 3, "B": 4, "X1": 5}
    region_intersections: dict[str, dict[str, object]] = {}
    for name, base, limit in normalized_regions:
        path = payloads[probe_indices[name]]
        first_address: int | None = None
        with lzma.open(path, "rb") as stream:
            for line in stream:
                if not line or line[:1] in {b"-", b"#"}:
                    continue
                for encoded in address_pattern.findall(line):
                    address = int(encoded, 16)
                    if base <= address < limit:
                        first_address = address
                        break
                if first_address is not None:
                    break
        if first_address is None:
            raise RuntimeError(
                f"formal trace has no address intersection for {name}")
        region_intersections[name] = {
            "member": path.name,
            "first_address_hex": hex(first_address),
            "region_base_hex": hex(base),
            "region_limit_hex": hex(limit),
        }
    x0_base, x0_limit = next(
        (base, limit) for name, base, limit in normalized_regions
        if name == "X0"
    )
    for path in payloads[:2]:
        with lzma.open(path, "rb") as stream:
            for line in stream:
                if any(x0_base <= int(encoded, 16) < x0_limit
                       for encoded in address_pattern.findall(line)):
                    raise RuntimeError(
                        f"unexpected early-normalization X0 intersection: {path}")

    lifetime = table(blob(commit, f"{PACK_PATH}/REGION_LIFETIME.tsv"))
    if len(lifetime) != 18:
        raise RuntimeError(f"expected 18 lifetime boundaries, got {len(lifetime)}")
    bindings = table(blob(commit, f"{PACK_PATH}/NATIVE_KERNEL_BINDING.tsv"))
    if len(bindings) != 18:
        raise RuntimeError(f"expected 18 kernel bindings, got {len(bindings)}")
    expected_families = (
        ["NORMALIZATION"] * 3
        + [family for _ in range(5) for family in ("XXT", "BA", "BMM_ADD")]
    )
    generations = {"A": 1, "B": 1, "X0": 1, "X1": 1}
    initial = {name: (1, False) for name in ("A", "B", "X0", "X1")}
    current = dict(initial)
    pre_transitions: list[tuple[int, str, int, bool]] = []
    post_transitions: list[tuple[int, str, int, bool]] = []
    for expected_index, (row, binding, expected_family) in enumerate(
            zip(lifetime, bindings, expected_families)):
        if int(field(row, ("roi_launch_index",))) != expected_index:
            raise RuntimeError("lifetime launch order is not contiguous")
        if field(row, ("context",)) != "0x43c6c760" or \
                field(row, ("stream_id",)) != "0":
            raise RuntimeError("unexpected context/stream identity")
        if field(row, ("kernel_family",)) != expected_family:
            raise RuntimeError(
                f"unexpected kernel family at {expected_index}: {row}")
        if field(row, ("kernel_boundary_only",)).lower() != "true" or \
                field(row, ("per_line_future_last_use",)).lower() != "false":
            raise RuntimeError("lifetime authority violates boundary-only gate")
        ordinal = expected_index + 1
        for lifetime_name, binding_name in (
                ("roi_launch_index", "roi_launch_index"),
                ("exact_function", "exact_function"),
                ("grid", "grid"), ("block", "block"),
                ("stream_id", "stream_id")):
            if field(row, (lifetime_name,)) != field(binding, (binding_name,)):
                raise RuntimeError(
                    f"lifetime/kernel binding mismatch at {expected_index}")
        if field(binding, ("context_from_filename",)) != "0x43c6c760" or \
                field(binding, ("binary_version",)) != "89":
            raise RuntimeError("unexpected native kernel binding identity")

        produced: str | None = None

        # A produced generation must be protected before its first dirty fill.
        # These PRE records are derived only from the published producer family
        # and ping-pong boundary states; no per-line/future access is consumed.
        if expected_index == 2:
            produced = "X0"
        elif expected_family == "XXT":
            iteration = int(field(row, ("iteration",)))
            generations["A"] = iteration + 1
            produced = "A"
        elif expected_family == "BA":
            iteration = int(field(row, ("iteration",)))
            generations["B"] = iteration + 1
            produced = "B"
        elif expected_family == "BMM_ADD":
            x0_after = field(row, ("X0_after",)).upper()
            x1_after = field(row, ("X1_after",)).upper()
            if (x0_after, x1_after) == ("LIVE", "DEAD"):
                produced = "X0"
            elif (x0_after, x1_after) == ("DEAD", "LIVE"):
                produced = "X1"
            else:
                raise RuntimeError(f"ambiguous BMM ping-pong output: {row}")
            if produced == "X0":
                generations["X0"] += 1
            else:
                iteration = int(field(row, ("iteration",)))
                generations["X1"] = iteration // 2 + 1
        if produced is not None:
            desired = (generations[produced], True)
            if current[produced] == desired:
                raise RuntimeError(f"redundant producer activation: {row}")
            if current[produced][1]:
                raise RuntimeError(f"producer overwrites live generation: {row}")
            pre_transitions.append((ordinal, produced, *desired))
            current[produced] = desired

        for name in ("A", "B", "X0", "X1"):
            state = field(row, (f"{name}_after",)).upper()
            if state not in {"LIVE", "DEAD", "UNDEFINED_NOT_READ",
                             "NOT_YET_LIVE"}:
                raise RuntimeError(f"invalid published liveness state: {state}")
            # NOT_YET_LIVE is an in-progress normalized X0 generation. It is
            # not consumer-ready, but remains cache-live so dirty partial
            # output cannot be dropped between normalization kernels.
            cache_live = state == "LIVE" or (
                state == "NOT_YET_LIVE" and current[name][1])
            desired = (generations[name], cache_live)
            if current[name] != desired:
                post_transitions.append((ordinal, name, *desired))
                current[name] = desired
    expected_kernels = len(lifetime)
    if len(pre_transitions) != 16 or len(post_transitions) != 15:
        raise RuntimeError(
            f"unexpected finite event budget: pre={len(pre_transitions)} "
            f"post={len(post_transitions)}")
    trace_headers: list[dict[str, str]] = []
    for path, binding in zip(payloads, bindings):
        header: dict[str, str] = {}
        with lzma.open(path, "rt") as stream:
            for raw in stream:
                line = raw.strip()
                if line == "#BEGIN_TB":
                    break
                for prefix, key in (
                        ("-kernel name = ", "exact_function"),
                        ("-kernel id = ", "kernel_id"),
                        ("-grid dim = ", "grid"),
                        ("-block dim = ", "block"),
                        ("-cuda stream id = ", "stream_id"),
                        ("-binary version = ", "binary_version")):
                    if line.startswith(prefix):
                        header[key] = line[len(prefix):].strip("()")
                        break
        for key in ("exact_function", "kernel_id", "grid", "block",
                    "stream_id", "binary_version"):
            if header.get(key) != field(binding, (key,)):
                raise RuntimeError(
                    f"trace header/binding mismatch {path.name} field={key}")
        expected_name = (
            f"kernel-{field(binding, ('kernel_id',))}-ctx_"
            f"{field(binding, ('context_from_filename',))}.traceg.xz"
        )
        if path.name != expected_name:
            raise RuntimeError(f"trace filename/binding mismatch: {path}")
        trace_headers.append({"member": path.name, **header})

    OUTPUT.mkdir(parents=True, exist_ok=True)
    trace_dir = OUTPUT / "traces"
    if trace_dir.exists():
        shutil.rmtree(trace_dir)
    trace_dir.mkdir()
    for path in payloads:
        (trace_dir / path.name).symlink_to(path)
    kernelslist_source = resolve_payload("raw/formal_full5/raw/kernelslist.g")
    kernelslist = kernelslist_source.read_text().splitlines()
    if kernelslist != [path.name for path in payloads]:
        raise RuntimeError("kernelslist/trace-manifest ordering mismatch")
    (trace_dir / "kernelslist.g").write_text("\n".join(kernelslist) + "\n")

    ids = {"A": 0, "B": 1, "X0": 2, "X1": 3}
    by_name = {name: (base, limit) for name, base, limit in normalized_regions}
    runtime = ["AWMA_TRANSIENT_L2_RUNTIME_V1", "LINE_SIZE 128",
               f"EXPECTED_KERNELS {expected_kernels}", "EXPECTED_STREAM 0"]
    for ordinal, binding in enumerate(bindings, 1):
        runtime.append(
            f"KERNEL {ordinal} {field(binding, ('kernel_id',))} "
            f"{field(binding, ('exact_function',))}")
    for name in ("A", "B", "X0", "X1"):
        base, limit = by_name[name]; generation, live = initial[name]
        runtime.append(f"REGION {ids[name]} {base:#x} {limit:#x} {generation} {int(live)}")
    for ordinal, name, generation, live in sorted(pre_transitions):
        runtime.append(f"PRE {ordinal} {ids[name]} {generation} {int(live)}")
    for ordinal, name, generation, live in sorted(post_transitions):
        runtime.append(f"POST {ordinal} {ids[name]} {generation} {int(live)}")
    runtime_path = OUTPUT / "transient_l2_runtime.tsv"
    runtime_path.write_text("\n".join(runtime) + "\n")
    receipt = {
        "status": "PASS", "producer_commit": commit,
        "input_identity": "SIM_INPUT_R101_L512_TRANSIENT_V1",
        "accepted_payload_sha256": accepted_payload_sha256,
        "accepted_output_sha256": accepted_output_sha256,
        "trace_members": [{"path": str(path), "sha256": sha(path)} for path in payloads],
        "kernelslist_sha256": sha(trace_dir / "kernelslist.g"),
        "runtime_sidecar_sha256": sha(runtime_path),
        "region_count": 4, "expected_kernels": expected_kernels,
        "pre_transition_count": len(pre_transitions),
        "post_transition_count": len(post_transitions),
        "lifetime_derivation": "KERNEL_BOUNDARY_PRE_PRODUCER_AND_POST_STATE_V1",
        "region_address_token_intersections": region_intersections,
        "region_intersection_method": "FIRST_EXACT_ADDRESS_IN_PRODUCER_FAMILY",
        "trace_header_binding_status": "PASS",
        "trace_headers": trace_headers,
        "raw_immutable": True,
    }
    (OUTPUT / "ADMISSION_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
