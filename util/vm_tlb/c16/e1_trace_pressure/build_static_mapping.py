#!/usr/bin/env python3
"""Build exact 28-region static L2 mapping using accepted_l2_mapper_cli."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import struct
import subprocess
import tempfile
from collections import Counter
from pathlib import Path


U64 = struct.Struct("<Q")
LINE_BYTES = 128
SUBPARTITIONS = 16
SETS = 2048
ASSOCIATIVITY = 16
ACCEPTED_CORE_SHA = "a2322069b9701597db7019080b5b54d29518e3a2"
ACCEPTED_CONFIG_SHA256 = "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8"


def need(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def intervals(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as stream:
        header = stream.readline().rstrip("\n")
        need(header == "ORACLE_ELASTIC_QWEIGHT_RESIDENCY_V1\t1\tMODELED_L2_GET_ADDR",
             "sidecar header drift")
        result = []
        for raw in stream:
            if not raw.strip():
                continue
            begin, end, name, target_class = raw.rstrip("\n").split("\t")
            result.append({"begin": int(begin, 0), "end_exclusive": int(end, 0),
                           "tensor_name": name, "target_class": int(target_class),
                           "layer_index": int(target_class) - 1})
    need(len(result) == 28, "requires exact 28 sidecar regions")
    need({row["target_class"] for row in result} == set(range(1, 29)),
         "sidecar target classes must be unique exact 1..28")
    for row in result:
        need(row["begin"] < row["end_exclusive"] and
             row["begin"] % LINE_BYTES == row["end_exclusive"] % LINE_BYTES == 0,
             "region is not a nonempty 128B-aligned interval")
    by_address = sorted(result, key=lambda row: row["begin"])
    need(all(left["end_exclusive"] <= right["begin"]
             for left, right in zip(by_address, by_address[1:])),
         "sidecar regions overlap")
    return sorted(result, key=lambda row: row["target_class"])


def map_region(mapper: Path, row: dict, temporary: Path) -> Counter[tuple[int, int]]:
    input_path = temporary / f"layer-{row['layer_index']}.u64"
    output_path = temporary / f"layer-{row['layer_index']}.tsv"
    with input_path.open("wb") as stream:
        for address in range(row["begin"], row["end_exclusive"], LINE_BYTES):
            stream.write(U64.pack(address))
    subprocess.run([str(mapper), "map", "--input-lines-u64", str(input_path),
                    "--output-tsv", str(output_path)], check=True)
    counts: Counter[tuple[int, int]] = Counter()
    expected = range(row["begin"], row["end_exclusive"], LINE_BYTES)
    with output_path.open(newline="", encoding="utf-8") as stream:
        rows = csv.DictReader(stream, delimiter="\t")
        observed = 0
        for address, mapped in zip(expected, rows):
            need(int(mapped["line_address_hex"], 0) == address, "mapper address order drift")
            sp, set_index = int(mapped["subpartition"]), int(mapped["set_index"])
            need(0 <= sp < SUBPARTITIONS and 0 <= set_index < SETS,
                 "mapper coordinate out of accepted geometry")
            counts[sp, set_index] += 1
            observed += 1
        need(next(rows, None) is None, "mapper emitted extra rows")
    need(observed == (row["end_exclusive"] - row["begin"]) // LINE_BYTES,
         "mapper omitted region lines")
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapper", type=Path, required=True)
    parser.add_argument("--mapper-identity-json", type=Path)
    parser.add_argument("--sidecar", type=Path, required=True)
    parser.add_argument("--sidecar-sha256")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    need(args.mapper.is_file() and os.access(args.mapper, os.X_OK), "mapper not executable")
    need(not args.output.exists(), "output exists")
    sidecar_sha = digest(args.sidecar)
    if args.sidecar_sha256:
        need(sidecar_sha == args.sidecar_sha256, "sidecar SHA drift")
    provenance_run = subprocess.run([str(args.mapper), "--provenance"], text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    check=True)
    provenance = {}
    for raw in provenance_run.stdout.splitlines():
        key, separator, value = raw.partition("=")
        need(separator == "=" and key and value, f"malformed mapper provenance: {raw!r}")
        provenance[key] = value
    need(provenance.get("accepted_core_sha") == ACCEPTED_CORE_SHA,
         "mapper Core authority drift")
    need(provenance.get("accepted_config_sha256") == ACCEPTED_CONFIG_SHA256,
         "mapper config authority drift")
    source = intervals(args.sidecar)
    regions = []
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".qweight-static-map-",
                                     dir=args.output.parent) as directory:
        temporary = Path(directory)
        for row in source:
            counts = map_region(args.mapper, row, temporary)
            per_sp = [0] * SUBPARTITIONS
            for (sp, _), count in counts.items():
                per_sp[sp] += count
            line_count = (row["end_exclusive"] - row["begin"]) // LINE_BYTES
            need(sum(counts.values()) == line_count, "static set counts do not close")
            regions.append({
                **row,
                "bytes": row["end_exclusive"] - row["begin"],
                "line_count": line_count,
                "subpartition_line_counts": per_sp,
                "set_line_counts": [
                    {"subpartition": sp, "set_index": set_index, "line_count": count}
                    for (sp, set_index), count in sorted(counts.items())
                ],
            })
            print(f"STATIC_QWEIGHT_REGION_PASS layer={row['layer_index']} lines={line_count}",
                  flush=True)
    identity = {"mapper_cli": str(args.mapper), "mapper_cli_sha256": digest(args.mapper),
                "provenance": provenance}
    if args.mapper_identity_json:
        identity["authority"] = json.loads(args.mapper_identity_json.read_text(encoding="utf-8"))
        identity["authority_sha256"] = digest(args.mapper_identity_json)
    document = {
        "schema": "C16_E1_QWEIGHT_L2_SET_MAPPING_MAPPER_V1",
        "status": "PASS",
        "claim_boundary": "STATIC_ACCEPTED_CORE_MAPPER_OUTPUT",
        "address_namespace": "MODELED_L2_GET_ADDR",
        "sidecar_sha256": sidecar_sha,
        "mapper": identity,
        "geometry": {
            "l2_bytes": 64 << 20,
            "line_size_bytes": LINE_BYTES,
            "subpartition_count": SUBPARTITIONS,
            "sets_per_subpartition": SETS,
            "associativity": ASSOCIATIVITY,
        },
        "region_count": 28,
        "total_target_lines": sum(row["line_count"] for row in regions),
        "regions": regions,
    }
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({"status": "PASS", "regions": 28,
                      "total_target_lines": document["total_target_lines"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
