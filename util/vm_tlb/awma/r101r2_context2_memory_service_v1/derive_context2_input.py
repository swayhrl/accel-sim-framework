#!/usr/bin/env python3
"""Derive and qualify the zero-copy R101 L512 CONTEXT2 input.

The default mode is a read-only dry run.  ``--write`` publishes the qualified
view to the node164 durable input directory and the three declared review-pack
artifacts.  Producer trace bytes are never copied or modified.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from collections import Counter
from typing import Any, Iterable


STAGE = "AWMA_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_V1"
DERIVED_INPUT_ID = "R101_L512_NS_CONTEXT2_EXECORG_V1"
SOURCE_INPUT_ID = "SIM_INPUT_R101_L512_TRANSIENT_V1"
PRODUCER_COMMIT = "bb902283b7ce9e1902b460383fbd3e0bedbd884d"
HANDOFF_COMMIT = "8542a4d37372d586591ff9911929e523645e88f5"

DEFAULT_SOURCE_ROOT = Path(
    "/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/input"
)
DEFAULT_DURABLE_ROOT = Path(
    "/root/share/mnt164/huangrulin/awma_r101r2_context2_memory_service_174_v1"
)
PACK_RELATIVE = Path(
    "docs/vm_tlb/review_packs/"
    "AWMA_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_174_V1"
)

SOURCE_RECEIPT_SHA256 = (
    "a6c66cb41c1ffb77f6af805534d47ccb8a8641dbe4aa3b206850be8e478f1e7a"
)
SOURCE_KERNELSLIST_SHA256 = (
    "9fce012939496008814786a0c12d32c1f97a10c07c62cdd08f1fddcee5d86588"
)
SOURCE_SIDECAR_SHA256 = (
    "740820a195ae2bb9966a91b1e6d3423f4ded520bd91d1819aac8e78ce104b77d"
)

REGION_NAMES = {0: "A", 1: "B", 2: "X0", 3: "X1"}
EXPECTED_REGIONS = {
    0: (0x77CAC1600000, 0x77CAC2C00000),
    1: (0x77CAC2C00000, 0x77CAC4200000),
    2: (0x77CA9AA00000, 0x77CA9C000000),
    3: (0x77CAA2000000, 0x77CAA3600000),
}

# Source launch indices are deliberately zero-based.  The source sidecar uses
# one-based ordinals, hence source_sidecar_ordinal == source_launch_index + 1.
EXPECTED_SELECTION = (
    {
        "source_launch_index": 3,
        "source_sidecar_ordinal": 4,
        "derived_ordinal": 1,
        "iteration": 0,
        "role": "CONTEXT",
        "kernel_id": 3580,
        "function": "XXT_kernel",
        "member": "kernel-3580-ctx_0x43c6c760.traceg.xz",
        "grid": "2816,1,1",
        "block": "128,1,1",
        "sha256": "3ce2aaa2279de0ebdc1b022b39cdef453563620e123c45763c87d748f405ca74",
    },
    {
        "source_launch_index": 4,
        "source_sidecar_ordinal": 5,
        "derived_ordinal": 2,
        "iteration": 0,
        "role": "CONTEXT",
        "kernel_id": 3581,
        "function": "ba_plus_cAA_kernel",
        "member": "kernel-3581-ctx_0x43c6c760.traceg.xz",
        "grid": "2816,1,1",
        "block": "128,1,1",
        "sha256": "d78ab55806f04a6788c32af0c577bfe8f4f1282aa5211df6b9506bb67aaa31b7",
    },
    {
        "source_launch_index": 5,
        "source_sidecar_ordinal": 6,
        "derived_ordinal": 3,
        "iteration": 0,
        "role": "CONTEXT",
        "kernel_id": 3582,
        "function": "bmm_add_kernel",
        "member": "kernel-3582-ctx_0x43c6c760.traceg.xz",
        "grid": "32,44,1",
        "block": "128,1,1",
        "sha256": "bab2f4d9e5ace8c1de25617b815b8426510429a19d6ac0e1c2d6b0c141ecc64d",
    },
    {
        "source_launch_index": 6,
        "source_sidecar_ordinal": 7,
        "derived_ordinal": 4,
        "iteration": 1,
        "role": "MEASURED_ROI",
        "kernel_id": 3583,
        "function": "XXT_kernel",
        "member": "kernel-3583-ctx_0x43c6c760.traceg.xz",
        "grid": "2816,1,1",
        "block": "128,1,1",
        "sha256": "22cfb5590fef79895139ffc4ac9db5102981a35baf991349c1ce605cde8ddbbd",
    },
    {
        "source_launch_index": 7,
        "source_sidecar_ordinal": 8,
        "derived_ordinal": 5,
        "iteration": 1,
        "role": "MEASURED_ROI",
        "kernel_id": 3584,
        "function": "ba_plus_cAA_kernel",
        "member": "kernel-3584-ctx_0x43c6c760.traceg.xz",
        "grid": "2816,1,1",
        "block": "128,1,1",
        "sha256": "d01f8c681eeb25fce7534f11db45dbb9dc79bc4c5229ee80b5719a19e8fee086",
    },
    {
        "source_launch_index": 8,
        "source_sidecar_ordinal": 9,
        "derived_ordinal": 6,
        "iteration": 1,
        "role": "MEASURED_ROI",
        "kernel_id": 3585,
        "function": "bmm_add_kernel",
        "member": "kernel-3585-ctx_0x43c6c760.traceg.xz",
        "grid": "32,44,1",
        "block": "128,1,1",
        "sha256": "6cc3b8f455631135acfa727a9c4bb0329f65bb896ca3238fc9e4332bfce67a1e",
    },
)

EXPECTED_TRANSITIONS = {
    "PRE": (
        (1, 0, 1, 1),
        (2, 1, 1, 1),
        (3, 3, 1, 1),
        (4, 0, 2, 1),
        (5, 1, 2, 1),
        (6, 2, 2, 1),
    ),
    "POST": (
        (2, 0, 1, 0),
        (3, 1, 1, 0),
        (3, 2, 1, 0),
        (5, 0, 2, 0),
        (6, 1, 2, 0),
        (6, 3, 1, 0),
    ),
}

# State after the derived PRE transition and before the corresponding kernel.
# Address identity plus the active descriptor generation is the complete
# boundary-only eligibility contract; no future/per-line information is used.
EXPECTED_LIVE_REGIONS_BY_DERIVED_ORDINAL = {
    1: (0, 2),
    2: (0, 1, 2),
    3: (1, 2, 3),
    4: (0, 3),
    5: (0, 1, 3),
    6: (1, 2, 3),
}

KERNEL_TSV_FIELDS = (
    "derived_ordinal",
    "source_launch_index_0based",
    "source_sidecar_ordinal_1based",
    "iteration",
    "role",
    "kernel_id",
    "exact_function",
    "member",
    "stream_id",
    "grid",
    "block",
    "l512_tile_count",
    "tile_identity_proof",
    "compressed_bytes",
    "sha256",
    "source_path",
    "derived_reference",
    "reference_kind",
)


class DerivationError(RuntimeError):
    """A fail-closed derivation or semantic-qualification error."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DerivationError(message)


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def compact_json_sha(value: Any) -> str:
    blob = json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return sha256_bytes(blob)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def parse_runtime_sidecar(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8").splitlines()
    require(lines and lines[0] == "AWMA_TRANSIENT_L2_RUNTIME_V1", "bad source sidecar header")
    result: dict[str, Any] = {
        "line_size": None,
        "expected_kernels": None,
        "expected_stream": None,
        "kernels": [],
        "regions": {},
        "PRE": [],
        "POST": [],
    }
    for line_number, line in enumerate(lines[1:], 2):
        if not line or line.startswith("#"):
            continue
        fields = line.split()
        kind = fields[0]
        try:
            if kind == "LINE_SIZE" and len(fields) == 2:
                require(result["line_size"] is None, "duplicate LINE_SIZE")
                result["line_size"] = int(fields[1], 0)
            elif kind == "EXPECTED_KERNELS" and len(fields) == 2:
                require(result["expected_kernels"] is None, "duplicate EXPECTED_KERNELS")
                result["expected_kernels"] = int(fields[1], 0)
            elif kind == "EXPECTED_STREAM" and len(fields) == 2:
                require(result["expected_stream"] is None, "duplicate EXPECTED_STREAM")
                result["expected_stream"] = int(fields[1], 0)
            elif kind == "KERNEL" and len(fields) == 4:
                result["kernels"].append(
                    {"ordinal": int(fields[1]), "kernel_id": int(fields[2]), "name": fields[3]}
                )
            elif kind == "REGION" and len(fields) == 6:
                region_id = int(fields[1])
                require(region_id not in result["regions"], f"duplicate REGION {region_id}")
                result["regions"][region_id] = {
                    "base": int(fields[2], 0),
                    "limit": int(fields[3], 0),
                    "generation": int(fields[4], 0),
                    "live": bool(int(fields[5], 0)),
                }
            elif kind in {"PRE", "POST"} and len(fields) == 5:
                result[kind].append(
                    (int(fields[1]), int(fields[2]), int(fields[3]), int(fields[4]))
                )
            else:
                raise DerivationError(f"unknown/malformed source sidecar record at line {line_number}: {line}")
        except ValueError as exc:
            raise DerivationError(f"invalid numeric source sidecar field at line {line_number}") from exc
    require(result["line_size"] == 128, "source sidecar LINE_SIZE is not 128")
    require(result["expected_kernels"] == 18, "source sidecar is not FULL5 18-member authority")
    require(result["expected_stream"] == 0, "source sidecar stream is not zero")
    require(
        [row["ordinal"] for row in result["kernels"]] == list(range(1, 19)),
        "source sidecar kernel ordinals are not exact 1..18",
    )
    require(len(result["PRE"]) == 16 and len(result["POST"]) == 15, "source transition budget changed")
    require(set(result["regions"]) == set(EXPECTED_REGIONS), "source region ID set changed")
    for region_id, (base, limit) in EXPECTED_REGIONS.items():
        observed = result["regions"][region_id]
        require((observed["base"], observed["limit"]) == (base, limit), f"REGION {region_id} range changed")
        require(observed["generation"] == 1 and not observed["live"], f"REGION {region_id} initial state changed")
        require(base % 128 == 0 and limit % 128 == 0 and base < limit, f"REGION {region_id} alignment/range invalid")
    return result


def state_rows(state: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "region_id": region_id,
            "region": REGION_NAMES[region_id],
            "generation": state[region_id]["generation"],
            "live": state[region_id]["live"],
        }
        for region_id in sorted(state)
    ]


def apply_transitions(
    state: dict[int, dict[str, Any]],
    transitions: Iterable[tuple[int, int, int, int]],
    ordinal: int,
    phase: str,
) -> None:
    for transition_ordinal, region_id, generation, live in transitions:
        if transition_ordinal != ordinal:
            continue
        require(region_id in state, f"{phase} references unknown region {region_id}")
        old = state[region_id]
        require(generation >= old["generation"], f"{phase} generation reversal")
        if phase == "PRE":
            require(not old["live"], f"PRE overwrites live REGION {region_id}")
            require(bool(live), f"PRE does not activate REGION {region_id}")
        state[region_id] = {**old, "generation": generation, "live": bool(live)}


def derive_runtime(source: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    state = {region_id: dict(row) for region_id, row in source["regions"].items()}
    source_initial = state_rows(state)
    for source_ordinal in range(1, 4):
        apply_transitions(state, source["PRE"], source_ordinal, "PRE")
        apply_transitions(state, source["POST"], source_ordinal, "POST")
    derived_initial_state = state_rows(state)
    require(
        [(r["region_id"], r["generation"], r["live"]) for r in derived_initial_state]
        == [(0, 1, False), (1, 1, False), (2, 1, True), (3, 1, False)],
        "state after zero-based source launch 2 is not the accepted normalization state",
    )

    derived_transitions: dict[str, list[tuple[int, int, int, int]]] = {"PRE": [], "POST": []}
    for phase in ("PRE", "POST"):
        for source_ordinal, region_id, generation, live in source[phase]:
            if 4 <= source_ordinal <= 9:
                derived_transitions[phase].append(
                    (source_ordinal - 3, region_id, generation, live)
                )
        require(
            tuple(derived_transitions[phase]) == EXPECTED_TRANSITIONS[phase],
            f"derived {phase} transition mapping changed",
        )

    context_state = {region_id: dict(row) for region_id, row in state.items()}
    for derived_ordinal in range(1, 4):
        apply_transitions(context_state, derived_transitions["PRE"], derived_ordinal, "PRE")
        apply_transitions(context_state, derived_transitions["POST"], derived_ordinal, "POST")
    context_end_state = state_rows(context_state)
    roi_entry_state = {region_id: dict(row) for region_id, row in context_state.items()}
    apply_transitions(roi_entry_state, derived_transitions["PRE"], 4, "PRE")
    roi_entry_rows = state_rows(roi_entry_state)
    final_state = {region_id: dict(row) for region_id, row in context_state.items()}
    for derived_ordinal in range(4, 7):
        apply_transitions(final_state, derived_transitions["PRE"], derived_ordinal, "PRE")
        apply_transitions(final_state, derived_transitions["POST"], derived_ordinal, "POST")
    final_rows = state_rows(final_state)

    lines = [
        "AWMA_TRANSIENT_L2_RUNTIME_V1",
        "LINE_SIZE 128",
        "EXPECTED_KERNELS 6",
        "EXPECTED_STREAM 0",
        "CONTEXT_END 3",
        "MEASURED_ROI_START 4",
        "MEASURED_ROI_END 6",
    ]
    for selected in EXPECTED_SELECTION:
        source_kernel = source["kernels"][selected["source_sidecar_ordinal"] - 1]
        require(source_kernel["kernel_id"] == selected["kernel_id"], "source sidecar kernel ID changed")
        require(source_kernel["name"] == selected["function"], "source sidecar function changed")
        lines.append(
            f"KERNEL {selected['derived_ordinal']} {selected['kernel_id']} {selected['function']}"
        )
    initial_by_id = {row["region_id"]: row for row in derived_initial_state}
    for region_id in sorted(EXPECTED_REGIONS):
        base, limit = EXPECTED_REGIONS[region_id]
        row = initial_by_id[region_id]
        lines.append(
            f"REGION {region_id} {base:#x} {limit:#x} "
            f"{row['generation']} {int(row['live'])}"
        )
    for phase in ("PRE", "POST"):
        for ordinal, region_id, generation, live in derived_transitions[phase]:
            lines.append(f"{phase} {ordinal} {region_id} {generation} {live}")
    blob = ("\n".join(lines) + "\n").encode("utf-8")
    state_receipt = {
        "source_initial_state": source_initial,
        "derived_initial_boundary": {
            "description": "after zero-based source launch 2 / one-based source ordinal 3 normalization completes",
            "source_launch_index_0based": 2,
            "source_sidecar_ordinal_1based": 3,
            "state": derived_initial_state,
            "state_sha256": compact_json_sha(derived_initial_state),
            "scope": "TRANSIENT_REGION_GENERATION_AND_LIVENESS_ONLY",
        },
        "context_end_boundary": {
            "description": "after derived ordinal 3 POST, before derived ordinal 4 PRE",
            "derived_completed_ordinal": 3,
            "state": context_end_state,
            "state_sha256": compact_json_sha(context_end_state),
            "scope": "TRANSIENT_REGION_GENERATION_AND_LIVENESS_ONLY",
        },
        "measured_roi_entry_boundary": {
            "description": "after derived ordinal 4 PRE, before its first instruction/transaction",
            "derived_start_ordinal": 4,
            "state": roi_entry_rows,
            "state_sha256": compact_json_sha(roi_entry_rows),
            "scope": "TRANSIENT_REGION_GENERATION_AND_LIVENESS_ONLY",
        },
        "derived_final_boundary": {
            "description": "after derived ordinal 6 POST",
            "derived_completed_ordinal": 6,
            "state": final_rows,
            "state_sha256": compact_json_sha(final_rows),
            "scope": "TRANSIENT_REGION_GENERATION_AND_LIVENESS_ONLY",
        },
        "transitions": {
            phase.lower(): [
                {
                    "derived_ordinal": ordinal,
                    "source_sidecar_ordinal": ordinal + 3,
                    "region_id": region_id,
                    "region": REGION_NAMES[region_id],
                    "generation": generation,
                    "live": bool(live),
                }
                for ordinal, region_id, generation, live in derived_transitions[phase]
            ]
            for phase in ("PRE", "POST")
        },
    }
    return blob, state_receipt


def parse_trace_header(path: Path) -> dict[str, str]:
    import lzma

    header: dict[str, str] = {}
    prefixes = {
        "-kernel name = ": "exact_function",
        "-kernel id = ": "kernel_id",
        "-grid dim = ": "grid",
        "-block dim = ": "block",
        "-cuda stream id = ": "stream_id",
        "-binary version = ": "binary_version",
        "-accelsim tracer version = ": "trace_version",
        "-enable lineinfo = ": "lineinfo",
    }
    with lzma.open(path, "rt", encoding="ascii") as stream:
        for raw in stream:
            line = raw.strip()
            if line == "#BEGIN_TB":
                break
            for prefix, key in prefixes.items():
                if line.startswith(prefix):
                    header[key] = line[len(prefix) :].strip("()")
                    break
    require(set(prefixes.values()) <= set(header), f"incomplete trace header: {path}")
    return header


def opcode_width(opcode: str) -> int:
    for component in opcode.split("."):
        digits = component[1:] if component.startswith("U") and len(component) > 1 else component
        if digits.isdigit():
            bits = int(digits)
            require(bits > 0 and bits % 8 == 0, f"invalid opcode width: {opcode}")
            return bits // 8
    return 4


def access_kind_and_space(opcode: str) -> tuple[str, str]:
    base = opcode.split(".", 1)[0]
    if "ATOM" in base or base.startswith("RED"):
        access = "ATOMIC"
    elif base.startswith(("LD", "TEX", "SULD")):
        access = "READ"
    elif base.startswith(("ST", "SUST")):
        access = "WRITE"
    else:
        access = "UNSUPPORTED"
    if base.startswith(("LDG", "STG", "ATOMG", "REDG", "LDGSTS")):
        space = "GLOBAL"
    elif base.startswith(("LDS", "STS", "ATOMS", "REDS")):
        space = "SHARED"
    elif base.startswith(("LDL", "STL")):
        space = "LOCAL"
    elif base.startswith(("LDC", "ULDC")):
        space = "CONSTANT"
    elif base.startswith("TEX"):
        space = "TEXTURE"
    elif base.startswith(("SULD", "SUST")):
        space = "SURFACE"
    else:
        space = "UNSUPPORTED"
    return access, space


def decode_addresses(
    parts: list[bytes], index: int, mask: int, mode: int
) -> tuple[list[int], int]:
    lanes = [lane for lane in range(32) if mask & (1 << lane)]
    if mode == 0:  # address_format::list_all
        require(index + len(lanes) <= len(parts), "truncated list_all addresses")
        addresses = [int(parts[index + offset], 16) for offset in range(len(lanes))]
        return addresses, index + len(lanes)
    if mode == 1:  # address_format::base_stride
        require(index + 2 <= len(parts), "truncated base_stride addresses")
        base = int(parts[index], 16)
        stride = int(parts[index + 1], 10)
        # Accel-Sim's authoritative decompressor assumes a contiguous run of
        # active lanes for base_stride.  Reject rather than silently inventing
        # addresses if a producer violates that precondition.
        if not lanes:
            return [], index + 2
        require(lanes == list(range(lanes[0], lanes[-1] + 1)), "non-contiguous base_stride active mask")
        return [base + offset * stride for offset in range(len(lanes))], index + 2
    if mode == 2:  # address_format::base_delta
        require(index + 1 + len(lanes) <= len(parts), "truncated base_delta addresses")
        base = int(parts[index], 16)
        deltas = [int(parts[index + 1 + offset], 10) for offset in range(len(lanes))]
        if not lanes:
            return [], index + 1
        addresses = [base]
        current = base
        # The serialized grammar carries one delta per active lane; the
        # authoritative parser consumes the final delta but needs only N-1.
        for delta in deltas[: max(0, len(lanes) - 1)]:
            current += delta
            require(current >= 0, "base_delta address underflow")
            addresses.append(current)
        return addresses, index + 1 + len(lanes)
    raise DerivationError(f"unsupported trace address mode {mode}")


def parse_instruction(parts: list[bytes]) -> dict[str, Any]:
    index = 0
    require(len(parts) >= 7, "truncated instruction record")
    int(parts[index], 16)
    pc = int(parts[index], 16)
    index += 1
    mask = int(parts[index], 16)
    index += 1
    destinations = int(parts[index], 10)
    index += 1
    require(0 <= destinations <= 1, "destination count exceeds trace grammar")
    index += destinations
    require(index < len(parts), "missing opcode")
    opcode = parts[index].decode("ascii")
    index += 1
    sources = int(parts[index], 10)
    index += 1
    require(0 <= sources <= 4, "source count exceeds trace grammar")
    index += sources
    require(index < len(parts), "missing memory width")
    serialized_width = int(parts[index], 10)
    index += 1
    addresses: list[int] = []
    mode: int | None = None
    effective_width = 0
    if serialized_width:
        require(index < len(parts), "missing address mode")
        mode = int(parts[index], 10)
        index += 1
        addresses, index = decode_addresses(parts, index, mask, mode)
        effective_width = opcode_width(opcode)
        require(
            effective_width == serialized_width,
            f"trace/opcode width mismatch for {opcode}: {serialized_width} != {effective_width}",
        )
    require(index < len(parts), "missing immediate")
    int(parts[index], 10)
    index += 1
    require(index == len(parts), "trailing tokens in instruction record")
    return {
        "pc": pc,
        "mask": mask,
        "opcode": opcode,
        "serialized_width": serialized_width,
        "effective_width": effective_width,
        "address_mode": mode,
        "addresses": addresses,
    }


def intersected_regions(addresses: list[int], width: int) -> set[int]:
    result: set[int] = set()
    for address in addresses:
        require(address <= (1 << 64) - 1 - width, "address interval overflow")
        access_limit = address + width
        for region_id, (base, limit) in EXPECTED_REGIONS.items():
            if address < limit and base < access_limit:
                result.add(region_id)
    return result


def scan_trace(payload: tuple[str, int, str, str, tuple[int, ...]]) -> dict[str, Any]:
    path_text, derived_ordinal, role, expected_grid, eligible_region_ids = payload
    path = Path(path_text)
    process = subprocess.Popen(
        ["xz", "-dc", "--", str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1024 * 1024,
    )
    assert process.stdout is not None and process.stderr is not None
    opcode_counts: Counter[str] = Counter()
    memory_opcode_counts: Counter[str] = Counter()
    access_counts: Counter[str] = Counter()
    space_counts: Counter[str] = Counter()
    address_mode_counts: Counter[str] = Counter()
    target_opcode_counts: Counter[str] = Counter()
    target_region_record_counts: Counter[str] = Counter()
    target_region_lane_counts: Counter[str] = Counter()
    target_bytes_by_region: Counter[str] = Counter()
    instruction_records = 0
    memory_records = 0
    thread_blocks = 0
    atomic_or_red_records = 0
    unsupported_memory_records = 0
    unsupported_target_records = 0
    ineligible_region_target_records = 0
    measured_target_ordinary_records = 0
    measured_target_read_records = 0
    measured_target_write_records = 0
    measured_target_ldgsts_records = 0
    failures: list[dict[str, Any]] = []
    in_tb = False
    thread_block_seen = False
    warp_open = False
    declared_instructions: int | None = None
    seen_instructions = 0

    def close_warp() -> None:
        if warp_open:
            require(declared_instructions is not None, f"warp missing insts record in {path.name}")
            require(
                seen_instructions == declared_instructions,
                f"warp instruction count mismatch in {path.name}: {seen_instructions} != {declared_instructions}",
            )

    try:
        for line_number, raw in enumerate(process.stdout, 1):
            line = raw.strip()
            if not line:
                continue
            if line == b"#BEGIN_TB":
                require(not in_tb, f"nested #BEGIN_TB in {path.name}")
                in_tb = True
                thread_block_seen = False
                warp_open = False
                declared_instructions = None
                seen_instructions = 0
                continue
            if line == b"#END_TB":
                require(in_tb and thread_block_seen, f"orphan/incomplete #END_TB in {path.name}")
                close_warp()
                in_tb = False
                warp_open = False
                thread_blocks += 1
                continue
            if not in_tb:
                continue
            if line.startswith(b"thread block = "):
                require(not thread_block_seen, f"duplicate thread block record in {path.name}")
                thread_block_seen = True
                continue
            if line.startswith(b"warp = "):
                require(thread_block_seen, f"warp before thread block record in {path.name}")
                close_warp()
                warp_open = True
                declared_instructions = None
                seen_instructions = 0
                continue
            if line.startswith(b"insts = "):
                require(warp_open and declared_instructions is None, f"malformed insts record in {path.name}")
                declared_instructions = int(line.split(b"=", 1)[1], 10)
                continue
            require(warp_open and declared_instructions is not None, f"instruction outside declared warp in {path.name}")
            try:
                instruction = parse_instruction(line.split())
            except (ValueError, UnicodeDecodeError, DerivationError) as exc:
                raise DerivationError(f"{path.name}:{line_number}: {exc}") from exc
            seen_instructions += 1
            require(seen_instructions <= declared_instructions, f"too many instructions in warp in {path.name}")
            instruction_records += 1
            opcode = instruction["opcode"]
            opcode_counts[opcode] += 1
            width = instruction["effective_width"]
            if not width:
                continue
            memory_records += 1
            memory_opcode_counts[opcode] += 1
            access, space = access_kind_and_space(opcode)
            access_counts[access] += 1
            space_counts[space] += 1
            address_mode_counts[str(instruction["address_mode"])] += 1
            base_opcode = opcode.split(".", 1)[0]
            if access == "ATOMIC":
                atomic_or_red_records += 1
            if access == "UNSUPPORTED" or space == "UNSUPPORTED":
                unsupported_memory_records += 1
            regions = intersected_regions(instruction["addresses"], width)
            if not regions:
                continue
            target_opcode_counts[opcode] += 1
            for region_id in sorted(regions):
                name = REGION_NAMES[region_id]
                target_region_record_counts[name] += 1
                target_lanes = sum(
                    1
                    for address in instruction["addresses"]
                    if address < EXPECTED_REGIONS[region_id][1]
                    and EXPECTED_REGIONS[region_id][0] < address + width
                )
                target_region_lane_counts[name] += target_lanes
                target_bytes_by_region[name] += target_lanes * width
            ineligible_regions = regions - set(eligible_region_ids)
            if ineligible_regions:
                ineligible_region_target_records += 1
                if len(failures) < 20:
                    failures.append(
                        {
                            "line_number": line_number,
                            "pc_hex": hex(instruction["pc"]),
                            "opcode": opcode,
                            "failure": "REGION_NOT_LIVE_FOR_DERIVED_KERNEL",
                            "regions": [REGION_NAMES[item] for item in sorted(ineligible_regions)],
                        }
                    )
            if role == "MEASURED_ROI":
                ordinary = (
                    base_opcode in {"LDG", "LDGSTS", "STG"}
                    and space == "GLOBAL"
                    and access in {"READ", "WRITE"}
                )
                if not ordinary:
                    unsupported_target_records += 1
                    if len(failures) < 20:
                        failures.append(
                            {
                                "line_number": line_number,
                                "pc_hex": hex(instruction["pc"]),
                                "opcode": opcode,
                                "access": access,
                                "space": space,
                                "regions": [REGION_NAMES[item] for item in sorted(regions)],
                            }
                        )
                else:
                    measured_target_ordinary_records += 1
                    if access == "READ":
                        measured_target_read_records += 1
                    else:
                        measured_target_write_records += 1
                    if base_opcode == "LDGSTS":
                        measured_target_ldgsts_records += 1
        require(not in_tb, f"non-terminal thread block in {path.name}")
        close_warp()
        stderr = process.stderr.read().decode("utf-8", errors="replace")
        return_code = process.wait()
        require(return_code == 0, f"xz rejected {path.name}: {stderr.strip()}")
    except BaseException:
        process.kill()
        process.wait()
        raise

    grid = tuple(int(component) for component in expected_grid.split(","))
    expected_thread_blocks = grid[0] * grid[1] * grid[2]
    require(thread_blocks == expected_thread_blocks, f"thread-block count mismatch in {path.name}")
    require(instruction_records > 0 and memory_records > 0, f"empty trace census in {path.name}")
    require(
        ineligible_region_target_records == 0,
        f"trace targets region not live for derived ordinal {derived_ordinal} in {path.name}: {failures}",
    )
    require(target_region_record_counts, f"trace has no admitted transient-region access in {path.name}")
    return {
        "derived_ordinal": derived_ordinal,
        "role": role,
        "member": path.name,
        "thread_blocks": thread_blocks,
        "instruction_records": instruction_records,
        "memory_records": memory_records,
        "opcode_counts": dict(sorted(opcode_counts.items())),
        "memory_opcode_counts": dict(sorted(memory_opcode_counts.items())),
        "access_counts": dict(sorted(access_counts.items())),
        "space_counts": dict(sorted(space_counts.items())),
        "address_mode_counts": dict(sorted(address_mode_counts.items())),
        "atomic_or_red_records": atomic_or_red_records,
        "unsupported_memory_records": unsupported_memory_records,
        "eligible_regions": [REGION_NAMES[item] for item in eligible_region_ids],
        "transient_target_opcode_counts": dict(sorted(target_opcode_counts.items())),
        "transient_target_region_record_counts": dict(sorted(target_region_record_counts.items())),
        "transient_target_region_lane_counts": dict(sorted(target_region_lane_counts.items())),
        "transient_target_lane_bytes": dict(sorted(target_bytes_by_region.items())),
        "measured_target_ordinary_records": measured_target_ordinary_records,
        "measured_target_read_records": measured_target_read_records,
        "measured_target_write_records": measured_target_write_records,
        "measured_target_ldgsts_records": measured_target_ldgsts_records,
        "unsupported_target_records": unsupported_target_records,
        "ineligible_region_target_records": ineligible_region_target_records,
        "unsupported_target_examples": failures,
        "qualification": "PASS_LDG_LDGSTS_STG_ONLY" if unsupported_target_records == 0 else "FAIL",
    }


def build_kernels_tsv(rows: list[dict[str, Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=KERNEL_TSV_FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return stream.getvalue().encode("utf-8")


def atomic_write(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(blob)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def ensure_symlink(link: Path, target: Path) -> None:
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.is_symlink():
        require(link.resolve(strict=True) == target.resolve(strict=True), f"existing symlink target mismatch: {link}")
        return
    require(not link.exists(), f"refusing to replace non-symlink path: {link}")
    link.symlink_to(target)


def qualify_and_render(args: argparse.Namespace) -> tuple[dict[str, bytes], dict[str, Any]]:
    source_root = args.source_root.resolve(strict=True)
    source_receipt_path = source_root / "ADMISSION_RECEIPT.json"
    source_kernelslist_path = source_root / "traces/kernelslist.g"
    source_sidecar_path = source_root / "transient_l2_runtime.tsv"
    require(sha256_path(source_receipt_path) == SOURCE_RECEIPT_SHA256, "accepted admission receipt SHA changed")
    require(sha256_path(source_kernelslist_path) == SOURCE_KERNELSLIST_SHA256, "accepted kernelslist SHA changed")
    require(sha256_path(source_sidecar_path) == SOURCE_SIDECAR_SHA256, "accepted sidecar SHA changed")
    admission = json.loads(source_receipt_path.read_text(encoding="utf-8"))
    require(admission.get("status") == "PASS", "accepted admission status is not PASS")
    require(admission.get("input_identity") == SOURCE_INPUT_ID, "accepted input identity changed")
    require(admission.get("producer_commit") == PRODUCER_COMMIT, "producer commit changed")
    require(admission.get("raw_immutable") is True, "producer raw is not declared immutable")
    require(admission.get("expected_kernels") == 18, "accepted input is not 18 members")
    require(admission.get("kernelslist_sha256") == SOURCE_KERNELSLIST_SHA256, "receipt kernelslist binding changed")
    require(admission.get("runtime_sidecar_sha256") == SOURCE_SIDECAR_SHA256, "receipt sidecar binding changed")
    source_members = admission.get("trace_members")
    source_headers = admission.get("trace_headers")
    require(isinstance(source_members, list) and len(source_members) == 18, "receipt trace member set changed")
    require(isinstance(source_headers, list) and len(source_headers) == 18, "receipt trace header set changed")
    source_kernelslist = source_kernelslist_path.read_text(encoding="utf-8").splitlines()
    require(len(source_kernelslist) == 18, "accepted kernelslist length changed")
    require(
        source_kernelslist == [Path(row["path"]).name for row in source_members],
        "accepted kernelslist/member order mismatch",
    )
    source_sidecar = parse_runtime_sidecar(source_sidecar_path)
    sidecar_blob, state_receipt = derive_runtime(source_sidecar)

    input_root = args.durable_root / "input"
    input_trace_dir = input_root / "traces"
    selected_rows: list[dict[str, Any]] = []
    scan_payloads: list[tuple[str, int, str, str, tuple[int, ...]]] = []
    selected_receipt_members: list[dict[str, Any]] = []
    for expected in EXPECTED_SELECTION:
        source_index = expected["source_launch_index"]
        member_receipt = source_members[source_index]
        header_receipt = source_headers[source_index]
        require(Path(member_receipt["path"]).name == expected["member"], "selected receipt member changed")
        require(member_receipt["sha256"] == expected["sha256"], "selected receipt member SHA changed")
        require(header_receipt["member"] == expected["member"], "selected receipt header order changed")
        source_path = Path(member_receipt["path"])
        require(source_path.is_file(), f"missing immutable source member: {source_path}")
        admitted_link = source_root / "traces" / expected["member"]
        require(admitted_link.is_symlink(), f"accepted trace reference is not a symlink: {admitted_link}")
        require(os.path.samefile(source_path, admitted_link), f"accepted trace symlink identity mismatch: {admitted_link}")
        observed_sha = sha256_path(source_path)
        require(observed_sha == expected["sha256"], f"selected trace SHA mismatch: {source_path}")
        header = parse_trace_header(source_path)
        expected_header = {
            "exact_function": expected["function"],
            "kernel_id": str(expected["kernel_id"]),
            "grid": expected["grid"],
            "block": expected["block"],
            "stream_id": "0",
            "binary_version": "89",
        }
        for key, value in expected_header.items():
            require(header[key] == value, f"selected trace header mismatch: {expected['member']} {key}")
            require(header_receipt[key] == value, f"receipt/header mismatch: {expected['member']} {key}")
        require(header["trace_version"] == "5" and header["lineinfo"] == "0", "trace grammar version changed")
        if expected["function"] in {"XXT_kernel", "ba_plus_cAA_kernel"}:
            require(expected["grid"] == "2816,1,1" and 2816 == 44 * 64, "44-tile grid proof failed")
            tile_proof = "grid_x=2816=44*64"
        else:
            require(expected["grid"] == "32,44,1", "44-tile BMM grid proof failed")
            tile_proof = "grid_y=44"
        derived_reference = input_trace_dir / expected["member"]
        selected_rows.append(
            {
                "derived_ordinal": expected["derived_ordinal"],
                "source_launch_index_0based": source_index,
                "source_sidecar_ordinal_1based": expected["source_sidecar_ordinal"],
                "iteration": expected["iteration"],
                "role": expected["role"],
                "kernel_id": expected["kernel_id"],
                "exact_function": expected["function"],
                "member": expected["member"],
                "stream_id": 0,
                "grid": expected["grid"],
                "block": expected["block"],
                "l512_tile_count": 44,
                "tile_identity_proof": tile_proof,
                "compressed_bytes": source_path.stat().st_size,
                "sha256": observed_sha,
                "source_path": str(source_path),
                "derived_reference": str(derived_reference),
                "reference_kind": "SYMLINK_SAMEFILE_ZERO_COPY",
            }
        )
        selected_receipt_members.append(
            {
                **expected,
                "source_path": str(source_path),
                "source_realpath": str(source_path.resolve(strict=True)),
                "accepted_reference": str(admitted_link),
                "derived_reference": str(derived_reference),
                "compressed_bytes": source_path.stat().st_size,
                "header": header,
                "samefile_with_accepted_reference": True,
                "l512_tile_count": 44,
                "tile_identity_proof": tile_proof,
            }
        )
        scan_payloads.append(
            (
                str(source_path),
                expected["derived_ordinal"],
                expected["role"],
                expected["grid"],
                EXPECTED_LIVE_REGIONS_BY_DERIVED_ORDINAL[expected["derived_ordinal"]],
            )
        )

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.scan_workers) as executor:
        scans = list(executor.map(scan_trace, scan_payloads))
    scans.sort(key=lambda row: row["derived_ordinal"])
    require(
        all(row["qualification"] == "PASS_LDG_LDGSTS_STG_ONLY" for row in scans),
        "trace semantic qualification failed",
    )
    require(
        sum(row["unsupported_target_records"] for row in scans if row["role"] == "MEASURED_ROI") == 0,
        "measured ROI contains unsupported transient target semantics",
    )
    require(
        set().union(*(set(row["transient_target_region_record_counts"]) for row in scans))
        == set(REGION_NAMES.values()),
        "six-member trace census does not cover all admitted A/B/X0/X1 regions",
    )

    kernelslist_blob = (
        "\n".join(expected["member"] for expected in EXPECTED_SELECTION) + "\n"
    ).encode("utf-8")
    kernels_tsv_blob = build_kernels_tsv(selected_rows)
    receipt: dict[str, Any] = {
        "schema_version": "AWMA_R101R2_CONTEXT2_DERIVATION_RECEIPT_V1",
        "status": "R101_L512_NS_CONTEXT2_EXECORG_V1_DERIVATION_PASS",
        "stage": STAGE,
        "derived_input_identity": DERIVED_INPUT_ID,
        "authorities": {
            "coordination_handoff_commit": HANDOFF_COMMIT,
            "producer_commit": PRODUCER_COMMIT,
            "source_input_identity": SOURCE_INPUT_ID,
            "source_admission_receipt": str(source_receipt_path),
            "source_admission_receipt_sha256": SOURCE_RECEIPT_SHA256,
            "source_kernelslist": str(source_kernelslist_path),
            "source_kernelslist_sha256": SOURCE_KERNELSLIST_SHA256,
            "source_runtime_sidecar": str(source_sidecar_path),
            "source_runtime_sidecar_sha256": SOURCE_SIDECAR_SHA256,
            "accepted_payload_sha256": admission["accepted_payload_sha256"],
            "accepted_output_sha256": admission["accepted_output_sha256"],
        },
        "indexing_contract": {
            "requested_source_indices": [3, 4, 5, 6, 7, 8],
            "requested_source_index_basis": "ZERO_BASED_LAUNCH_INDEX",
            "source_sidecar_index_basis": "ONE_BASED_ORDINAL",
            "derived_index_basis": "ONE_BASED_ORDINAL",
            "normalization_source_launch_indices_excluded": [0, 1, 2],
            "normalization_last_launch_index": 2,
            "mapping_rule": "source_sidecar_ordinal=source_launch_index+1; derived_ordinal=source_launch_index-2",
        },
        "selection": selected_receipt_members,
        "tile_contract": {
            "l512_tile_count": 44,
            "all_six_members_preserve_tiles": True,
            "xxt_ba_proof": "grid_x=2816=44*64",
            "bmm_proof": "grid=(32,44,1)",
        },
        "regions": [
            {
                "region_id": region_id,
                "region": REGION_NAMES[region_id],
                "base_hex": hex(base),
                "limit_hex": hex(limit),
                "bytes": limit - base,
                "line_size": 128,
            }
            for region_id, (base, limit) in sorted(EXPECTED_REGIONS.items())
        ],
        "state_derivation": state_receipt,
        "sidecar_contract": {
            "schema": "AWMA_TRANSIENT_L2_RUNTIME_V1",
            "expected_kernels": 6,
            "expected_stream": 0,
            "context_end_derived_ordinal": 3,
            "measured_roi_start_derived_ordinal": 4,
            "measured_roi_end_derived_ordinal": 6,
            "markers": ["CONTEXT_END 3", "MEASURED_ROI_START 4", "MEASURED_ROI_END 6"],
            "pre_transition_count": 6,
            "post_transition_count": 6,
            "no_per_line_future_last_use": True,
            "sha256": sha256_bytes(sidecar_blob),
        },
        "roi_contract": {
            "context_members": [1, 2, 3],
            "measured_members": [4, 5, 6],
            "roi_start_cycle_boundary": "cycle_after_derived_ordinal_3_BMM_completion_and_POST_before_ordinal_4_PRE",
            "oracle_activation_boundary": "after_derived_ordinal_4_PRE_before_first_ordinal_4_instruction_or_transaction",
            "roi_end_cycle_boundary": "cycle_after_derived_ordinal_6_BMM_completion_and_POST_before_terminal_drain",
            "formula": "ROI_CYCLES=cycle_after_derived_ordinal_6_BMM-cycle_after_derived_ordinal_3_BMM",
            "terminal_drain": "REQUIRED_BUT_EXCLUDED_FROM_ROI_CYCLES",
        },
        "trace_semantics_qualification": {
            "status": "PASS_SUPPORTED_GLOBAL_LDG_LDGSTS_STG_ONLY_FOR_MEASURED_TRANSIENT_TARGETS",
            "method": (
                "strict trace-v5 record parse plus authoritative list_all/base_stride/base_delta "
                "address decode; opcode access/space classification; byte-interval intersection "
                "against admitted A/B/X0/X1 regions"
            ),
            "measured_transient_allowlist": ["LDG", "LDGSTS", "STG"],
            "ldgsts_classification": {
                "access": "READ",
                "space": "GLOBAL",
                "special_dependency_path": True,
                "source_basis": (
                    "trace-driven OP_LDGSTS shares the OP_LDG memory_load/global_space case, "
                    "sets m_is_ldgsts, and uses pending-LDGSTS/DEPBAR completion bookkeeping"
                ),
                "oracle_requirement": (
                    "one-cycle service must preserve the existing LDGSTS client/writeback "
                    "dependency completion exactly once"
                ),
            },
            "atomic_or_red_policy": "FAIL_CLOSED_IF_TARGETS_TRANSIENT_REGION_IN_MEASURED_ROI",
            "other_memory_semantic_policy": "FAIL_CLOSED_IF_TARGETS_TRANSIENT_REGION_IN_MEASURED_ROI",
            "region_liveness_policy": (
                "FAIL_CLOSED_IF_ANY_MEMBER_TARGETS_A_REGION_NOT_LIVE_AFTER_ITS_PRE_AND_BEFORE_ITS_POST"
            ),
            "members": scans,
            "atomic_or_red_records_all_six": sum(row["atomic_or_red_records"] for row in scans),
            "ldgsts_records_all_six": sum(
                sum(count for opcode, count in row["memory_opcode_counts"].items() if opcode.split(".", 1)[0] == "LDGSTS")
                for row in scans
            ),
            "ldgsts_transient_target_records_measured_roi": sum(
                row["measured_target_ldgsts_records"]
                for row in scans
                if row["role"] == "MEASURED_ROI"
            ),
            "unsupported_target_records_measured_roi": sum(
                row["unsupported_target_records"] for row in scans if row["role"] == "MEASURED_ROI"
            ),
        },
        "zero_copy_contract": {
            "raw_immutable": True,
            "trace_bytes_copied": False,
            "reference_kind": "SYMLINK_TO_ACCEPTED_IMMUTABLE_NODE164_MEMBER",
            "selected_members": 6,
            "selected_order_preserved": True,
        },
        "derived_artifacts": {
            "kernelslist_path": str(input_trace_dir / "kernelslist.g"),
            "kernelslist_sha256": sha256_bytes(kernelslist_blob),
            "runtime_sidecar_path": str(input_root / "transient_l2_runtime.tsv"),
            "runtime_sidecar_sha256": sha256_bytes(sidecar_blob),
            "kernels_table_path": str(input_root / "CONTEXT2_KERNELS.tsv"),
            "kernels_table_sha256": sha256_bytes(kernels_tsv_blob),
        },
    }
    receipt_blob = canonical_json(receipt)
    artifacts = {
        "kernelslist": kernelslist_blob,
        "sidecar": sidecar_blob,
        "kernels_tsv": kernels_tsv_blob,
        "receipt": receipt_blob,
    }
    summary = {
        "status": receipt["status"],
        "mode": "WRITE" if args.write else "DRY_RUN_READ_ONLY",
        "selected_members": 6,
        "kernelslist_sha256": sha256_bytes(kernelslist_blob),
        "runtime_sidecar_sha256": sha256_bytes(sidecar_blob),
        "kernels_table_sha256": sha256_bytes(kernels_tsv_blob),
        "derivation_receipt_sha256": sha256_bytes(receipt_blob),
        "atomic_or_red_records_all_six": receipt["trace_semantics_qualification"]["atomic_or_red_records_all_six"],
        "ldgsts_records_all_six": receipt["trace_semantics_qualification"]["ldgsts_records_all_six"],
        "ldgsts_transient_target_records_measured_roi": receipt["trace_semantics_qualification"][
            "ldgsts_transient_target_records_measured_roi"
        ],
        "unsupported_target_records_measured_roi": 0,
    }
    return artifacts, summary


def publish(args: argparse.Namespace, artifacts: dict[str, bytes]) -> None:
    input_root = args.durable_root / "input"
    trace_dir = input_root / "traces"
    for expected in EXPECTED_SELECTION:
        source_path = Path(
            json.loads((args.source_root / "ADMISSION_RECEIPT.json").read_text(encoding="utf-8"))["trace_members"]
            [expected["source_launch_index"]]["path"]
        )
        ensure_symlink(trace_dir / expected["member"], source_path)
    atomic_write(trace_dir / "kernelslist.g", artifacts["kernelslist"])
    atomic_write(input_root / "transient_l2_runtime.tsv", artifacts["sidecar"])
    atomic_write(input_root / "CONTEXT2_KERNELS.tsv", artifacts["kernels_tsv"])
    atomic_write(input_root / "CONTEXT2_DERIVATION_RECEIPT.json", artifacts["receipt"])

    args.pack_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(args.pack_dir / "CONTEXT2_DERIVATION_RECEIPT.json", artifacts["receipt"])
    atomic_write(args.pack_dir / "CONTEXT2_KERNELS.tsv", artifacts["kernels_tsv"])
    atomic_write(args.pack_dir / "CONTEXT2_RUNTIME_SIDECAR.tsv", artifacts["sidecar"])

    # Immediate read-back verification covers both durable and review copies.
    expected = {
        trace_dir / "kernelslist.g": artifacts["kernelslist"],
        input_root / "transient_l2_runtime.tsv": artifacts["sidecar"],
        input_root / "CONTEXT2_KERNELS.tsv": artifacts["kernels_tsv"],
        input_root / "CONTEXT2_DERIVATION_RECEIPT.json": artifacts["receipt"],
        args.pack_dir / "CONTEXT2_DERIVATION_RECEIPT.json": artifacts["receipt"],
        args.pack_dir / "CONTEXT2_KERNELS.tsv": artifacts["kernels_tsv"],
        args.pack_dir / "CONTEXT2_RUNTIME_SIDECAR.tsv": artifacts["sidecar"],
    }
    for path, blob in expected.items():
        require(path.read_bytes() == blob, f"published artifact read-back mismatch: {path}")
    for selected in EXPECTED_SELECTION:
        source_member = Path(
            json.loads((args.source_root / "ADMISSION_RECEIPT.json").read_text(encoding="utf-8"))["trace_members"]
            [selected["source_launch_index"]]["path"]
        )
        derived_member = trace_dir / selected["member"]
        require(derived_member.is_symlink(), f"derived member is not a symlink: {derived_member}")
        require(os.path.samefile(source_member, derived_member), f"derived member is not samefile: {derived_member}")


def arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="publish qualified artifacts; default is read-only")
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--durable-root", type=Path, default=DEFAULT_DURABLE_ROOT)
    parser.add_argument("--pack-dir", type=Path, default=repository_root() / PACK_RELATIVE)
    parser.add_argument("--scan-workers", type=int, choices=(1, 2), default=2)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = arguments(sys.argv[1:] if argv is None else argv)
    try:
        artifacts, summary = qualify_and_render(args)
        if args.write:
            publish(args, artifacts)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (DerivationError, OSError, json.JSONDecodeError) as exc:
        print(f"CONTEXT2_DERIVATION_REJECT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
