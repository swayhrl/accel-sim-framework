#!/usr/bin/env python3
"""Offline, fail-closed forensic accounting for a filtered NVBit trace.

The Accel-Sim/NVBit textual format deliberately serializes the conjunction of
the warp active and instruction predicate masks.  Consequently an emitted row
proves at least one active lane (the device-side producer pushes only from an
active lane), while the textual mask is the authoritative predicate-true lane
set.  This utility never treats addresses from predicate-false lanes as data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def parse_row(line: str) -> tuple[str, int, int, list[int]]:
    """Return opcode, conjunctive mask, width, and listed addresses.

    The row prefix is ``cta_x cta_y cta_z warp PC mask dest_num ...``.  We
    parse register lists from their explicit counts instead of assuming a
    fixed number of operands.
    """
    fields = line.split()
    if len(fields) < 10:
        raise ValueError("short trace row")
    cursor = 6  # after CTA/warp/PC/mask
    destination_count = int(fields[cursor])
    cursor += 1 + destination_count
    opcode = fields[cursor]
    cursor += 1
    source_count = int(fields[cursor])
    cursor += 1 + source_count
    width = int(fields[cursor])
    cursor += 1
    address_format = int(fields[cursor])
    cursor += 1
    # Compression is contractually disabled in the capture wrapper.  A
    # list-all row has one address per predicate-true lane; an empty list is
    # valid exactly when the conjunctive predicate mask is zero.
    mask = int(fields[5], 16)
    addresses: list[int] = []
    if address_format == 0:
        for token in fields[cursor:]:
            if token.startswith("0x"):
                addresses.append(int(token, 16))
    return opcode, mask, width, addresses


def inspect(trace_root: Path, *, target_opcode: str, target_static_index: int,
            target_offset: int, target_function: str) -> dict[str, Any]:
    files = sorted(trace_root.rglob("*.trace"))
    if not files:
        raise ValueError("no uncompressed .trace payload exists")
    row_count = active_nonzero = predicate_nonzero = predicate_zero = 0
    nonzero_lanes = zero_lanes = 0
    opcodes: set[str] = set()
    widths: set[int] = set()
    functions: set[str] = set()
    matching_pc_rows = 0
    for trace in files:
        declared_function = None
        for raw in trace.read_text(encoding="utf-8", errors="strict").splitlines():
            if raw.startswith("-kernel name = "):
                declared_function = raw.removeprefix("-kernel name = ")
                functions.add(declared_function)
                continue
            if not raw or raw.startswith("-") or raw.startswith("#"):
                continue
            opcode, mask, width, addresses = parse_row(raw)
            row_count += 1
            # Device producer requires first_laneid from active_mask, so an
            # emitted row establishes active_mask != 0 without inventing a
            # non-serialized mask value.
            active_nonzero += 1
            if mask:
                predicate_nonzero += 1
                lane_count = mask.bit_count()
                if len(addresses) != lane_count:
                    raise ValueError("predicate-true row address count differs from lane count")
                nonzero_lanes += sum(address != 0 for address in addresses)
                zero_lanes += sum(address == 0 for address in addresses)
            else:
                predicate_zero += 1
                if addresses:
                    raise ValueError("predicate-false row unexpectedly carries addresses")
            opcodes.add(opcode)
            widths.add(width)
            # PC is the fifth field and is emitted as hexadecimal vpc.
            if int(raw.split()[4], 16) == target_offset:
                matching_pc_rows += 1
        if declared_function != target_function:
            raise ValueError("trace function identity differs from frozen target")
    if opcodes != {target_opcode}:
        raise ValueError("trace opcode differs from frozen target")
    if matching_pc_rows != row_count:
        raise ValueError("trace PC differs from frozen target offset")
    return {
        "schema_version": "C16_G_RECOVERY_V3_ADDRESS_ZERO_FORENSICS_V1",
        "trace_root": str(trace_root),
        "trace_file_count": len(files),
        "trace_row_count": row_count,
        "target_opcode_observed": sorted(opcodes),
        "target_instr_idx_observed": [target_static_index],
        "target_instr_idx_observation_method": "frozen_NVBit_native_map_static_index_plus_matching_trace_vpc_offset",
        "target_instruction_offset_observed": target_offset,
        "target_function_observed": sorted(functions),
        "active_mask_nonzero_rows": active_nonzero,
        "active_mask_observation_method": "inferred_from_device_producer_first_active_lane_push",
        "predicate_mask_nonzero_rows": predicate_nonzero,
        "predicate_mask_zero_rows": predicate_zero,
        "nonzero_address_lane_count": nonzero_lanes,
        "zero_address_lane_count": zero_lanes,
        "address_lane_accounting_scope": "predicate_true_lanes_only",
        "width_values": sorted(widths),
        "trace_payload_sha256": {str(path.relative_to(trace_root)): sha256(path) for path in files},
        "classification": ("PREDICATED_OFF_TARGET" if predicate_nonzero == 0 else
                           "ADDRESS_PRESENT" if nonzero_lanes else "PREDICATE_TRUE_ZERO_ADDRESS"),
        "scientific_eligible": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-root", type=Path, required=True)
    parser.add_argument("--target-opcode", required=True)
    parser.add_argument("--target-static-index", type=int, required=True)
    parser.add_argument("--target-offset", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--target-function", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("FAIL address-zero forensics: refuses to overwrite receipt")
    try:
        value = inspect(args.trace_root, target_opcode=args.target_opcode,
                        target_static_index=args.target_static_index,
                        target_offset=args.target_offset,
                        target_function=args.target_function)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"FAIL address-zero forensics: {exc}")
    atomic_json(args.output, value)
    print("PASS address-zero forensics", value["classification"])


if __name__ == "__main__":
    main()
