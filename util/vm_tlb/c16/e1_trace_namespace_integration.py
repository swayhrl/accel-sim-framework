#!/usr/bin/env python3
"""Deterministic C16 E1 trace-to-L2 namespace integration tooling."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import lzma
import re
from pathlib import Path


EXPECTED_RUN_ID = (
    "C16R_qwen2p5-7b-instruct-awq_s2-text-d1-d3_decode3_nvbit1771-"
    "sim-native-full-sass_bounded-context_20260925T120107Z_2b41b26fdb03"
)
EXPECTED_MANIFEST_SHA = "db3bdbb0295a47a6aa4644508ea1895779c987f2f77cd96f184c67b8a10ab389"
EXPECTED_ORACLE_SHA = "012d13f75d19e04811c2657296d1935ecf1d285368bfd4b02cece564a5845478"
EXPECTED_BYTES = 33_947_648
HEADER = "ORACLE_ELASTIC_QWEIGHT_RESIDENCY_V1\t1\tMODELED_L2_GET_ADDR\n"
ADDRESS = re.compile(r"0x([0-9a-fA-F]+)")
INSTRUCTION = re.compile(r"^[0-9a-fA-F]+\s+[0-9a-fA-F]+\s+")


class ContractError(ValueError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise ContractError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path):
    require(path.is_file() and path.stat().st_size > 0, f"missing/empty {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] < b[1] and b[0] < a[1]


def validated_authority(oracle_path: Path, manifest_path: Path):
    require(sha256(manifest_path) == EXPECTED_MANIFEST_SHA, "durable manifest SHA drift")
    manifest = read_json(manifest_path)
    require(manifest.get("run_id") == EXPECTED_RUN_ID, "run ID drift")
    artifacts = manifest.get("artifacts")
    require(isinstance(artifacts, list) and len(artifacts) == 9062, "artifact count drift")
    require(sum(int(row["size_bytes"]) for row in artifacts) == 114_926_148_782,
            "artifact byte total drift")
    require(sha256(oracle_path) == EXPECTED_ORACLE_SHA, "oracle source SHA drift")
    raw = read_json(oracle_path)
    require(raw.get("status") == "PASS" and raw.get("schema") == "C16_E1_ORACLE_QWEIGHT_REGIONS_V1",
            "oracle schema/status drift")
    targets = raw.get("targets")
    require(isinstance(targets, list) and len(targets) == 28, "requires exact 28 targets")
    by_layer = {}
    for item in targets:
        layer = int(item["layer_index"])
        require(layer in range(28) and layer not in by_layer, "target layer matrix drift")
        begin, end = int(item["exact_tensor_span_begin"]), int(item["exact_tensor_span_end_exclusive"])
        require(item.get("role") == "up_proj" and item.get("component") == "qweight",
                "target semantic identity drift")
        require(int(item["bytes"]) == EXPECTED_BYTES and end - begin == EXPECTED_BYTES,
                "target byte/span drift")
        require(begin % 128 == 0 and end % 128 == 0,
                "target interval is not 128-byte transaction aligned")
        require(item.get("contiguous") is True and item.get("pointer_stable") is True and
                item.get("storage_pointer_stable") is True and item.get("content_stable") is True,
                "target stability/contiguity drift")
        require(begin == int(item["data_ptr"]) == int(item["storage_data_ptr"]),
                "target pointer/span drift")
        by_layer[layer] = (begin, end, item)
    require(set(by_layer) == set(range(28)), "missing target layer")
    ordered = sorted(by_layer.values())
    require(all(left[1] <= right[0] for left, right in zip(ordered, ordered[1:])),
            "target intervals overlap")
    for item in raw.get("excluded_component_catalog", []):
        key = (int(item["layer_index"]), item["role"], item["component"])
        if key[1:] == ("up_proj", "qweight"):
            continue
        span = (int(item["exact_tensor_span_begin"]), int(item["exact_tensor_span_end_exclusive"]))
        require(not any(overlap(span, (begin, end)) for begin, end, _ in ordered),
                f"target overlaps excluded catalog entry {key}")
    return raw, by_layer


def generate(args) -> None:
    raw, by_layer = validated_authority(args.oracle_json, args.manifest)
    rows = []
    for begin, end, item in sorted(by_layer.values()):
        rows.append(
            f"0x{begin:x}\t0x{end:x}\t{item['tensor_name']}\t{int(item['layer_index']) + 1}\n"
        )
    args.sidecar.parent.mkdir(parents=True, exist_ok=True)
    args.sidecar.write_text(HEADER + "".join(rows), encoding="utf-8")
    sidecar_sha = sha256(args.sidecar)
    provenance = {
        "status": "PASS",
        "schema": "C16_E1_ORACLE_SIDECAR_PROVENANCE_V1",
        "run_id": EXPECTED_RUN_ID,
        "producer_branch_head": args.producer_head,
        "source_manifest_path": str(args.manifest),
        "source_manifest_sha256": EXPECTED_MANIFEST_SHA,
        "source_oracle_regions_path": str(args.oracle_json),
        "source_oracle_regions_sha256": EXPECTED_ORACLE_SHA,
        "generated_sidecar_path": str(args.sidecar),
        "generated_sidecar_sha256": sidecar_sha,
        "address_transform": "IDENTITY_NUMERIC_NO_ADDRESS_REWRITE",
        "address_namespace": "MODELED_L2_GET_ADDR",
        "target_count": 28,
        "single_region_bytes": EXPECTED_BYTES,
        "total_target_bytes": 28 * EXPECTED_BYTES,
        "regions": [
            {"layer_index": int(item["layer_index"]), "begin": begin, "end_exclusive": end,
             "bytes": end - begin, "target_class": int(item["layer_index"]) + 1,
             "tensor_name": item["tensor_name"]}
            for begin, end, item in sorted(by_layer.values())
        ],
        "excluded_catalog_overlap_count": 0,
        "deterministic_generation": True,
    }
    dump(args.provenance, provenance)
    print(json.dumps({"sidecar_sha256": sidecar_sha, "target_count": 28}, sort_keys=True))


def kernel_rows(path: Path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def trace_path(trace_root: Path, kernel_id: int) -> Path:
    matches = list((trace_root / "traces").glob(f"kernel-{kernel_id}-ctx_*.traceg.xz"))
    require(len(matches) == 1, f"kernel {kernel_id} trace artifact ambiguity")
    return matches[0]


def find_address(path: Path, span: tuple[int, int] | None = None,
                 outside: list[tuple[int, int]] | None = None):
    with lzma.open(path, "rt", encoding="utf-8", errors="strict") as stream:
        for line_number, line in enumerate(stream, 1):
            if not INSTRUCTION.match(line):
                continue
            values = [int(token, 16) for token in ADDRESS.findall(line)]
            for value in values:
                if span is not None and span[0] <= value < span[1]:
                    return value, line_number, line.rstrip()
                if outside is not None and value >= (1 << 40) and not any(
                        begin <= value < end for begin, end in outside):
                    return value, line_number, line.rstrip()
    raise ContractError(f"no qualifying address in {path}")


def find_exact(path: Path, expected: int):
    with lzma.open(path, "rt", encoding="utf-8", errors="strict") as stream:
        for line_number, line in enumerate(stream, 1):
            if not INSTRUCTION.match(line):
                continue
            values = [int(token, 16) for token in ADDRESS.findall(line)]
            if expected in values:
                return line_number, line.rstrip()
    raise ContractError(f"exact address {hex(expected)} absent from {path}")


def select_awq(rows, decode: int, layer: int, semantic: str,
               allow_multiple: bool = False) -> int:
    matches = [row for row in rows if int(row["decode_iteration"]) == decode and
               row["semantic_layer"] == str(layer) and row["semantic_identity"] == semantic and
               row["exact_function"] == "awq_gemm_kernel"]
    require(matches, f"AWQ kernel identity absent {decode}/{layer}/{semantic}")
    if not allow_multiple:
        require(len(matches) == 1, f"AWQ kernel identity ambiguity {decode}/{layer}/{semantic}")
    return min(int(row["global_dynamic_order"]) for row in matches)


def extract(args) -> None:
    raw, by_layer = validated_authority(args.oracle_json, args.manifest)
    audit = read_json(args.trace_audit)
    require(audit.get("status") == "PASS" and audit.get("canary_layers") == [0, 14, 27],
            "trace-side canary authority drift")
    targets = {(int(row["layer_index"])): row for row in audit["canaries"]}
    rows = kernel_rows(args.kernel_sequence)
    all_target_spans = [(begin, end) for begin, end, _ in by_layer.values()]
    target_output = []
    for layer in (0, 14, 27):
        row = targets[layer]
        path = trace_path(args.trace_root, int(row["kernel_id"]))
        address = int(row["first_trace_hit"])
        line_number, line = find_exact(path, address)
        target_output.append({"layer_index": layer, "kernel_id": int(row["kernel_id"]),
                              "trace_artifact": path.name, "trace_line_number": line_number,
                              "trace_numeric_address": address, "trace_numeric_address_hex": hex(address),
                              "trace_line": line})

    catalog = {(int(item["layer_index"]), item["role"], item["component"]): item
               for item in raw["excluded_component_catalog"]}
    exclusions = []
    for role in ("gate_proj", "down_proj"):
        item = catalog[(0, role, "qweight")]
        kernel = select_awq(rows, 2, 0, role)
        path = trace_path(args.trace_root, kernel)
        span = (int(item["exact_tensor_span_begin"]), int(item["exact_tensor_span_end_exclusive"]))
        address, line_number, line = find_address(path, span)
        exclusions.append({"kind": f"{role}.qweight", "kernel_id": kernel,
                           "trace_artifact": path.name, "trace_line_number": line_number,
                           "trace_numeric_address": address, "trace_numeric_address_hex": hex(address),
                           "oracle_expected": False, "trace_line": line})
    up_kernel = select_awq(rows, 2, 0, "up_proj")
    up_path = trace_path(args.trace_root, up_kernel)
    for component in ("qzeros", "scales"):
        item = catalog[(0, "up_proj", component)]
        span = (int(item["exact_tensor_span_begin"]), int(item["exact_tensor_span_end_exclusive"]))
        address, line_number, line = find_address(up_path, span)
        exclusions.append({"kind": f"up_proj.{component}", "kernel_id": up_kernel,
                           "trace_artifact": up_path.name, "trace_line_number": line_number,
                           "trace_numeric_address": address, "trace_numeric_address_hex": hex(address),
                           "oracle_expected": False, "trace_line": line})
    attention_kernel = select_awq(rows, 1, 0, "self_attn", allow_multiple=True)
    attention_path = trace_path(args.trace_root, attention_kernel)
    address, line_number, line = find_address(attention_path, outside=all_target_spans)
    exclusions.append({"kind": "self_attn_or_ordinary", "kernel_id": attention_kernel,
                       "trace_artifact": attention_path.name, "trace_line_number": line_number,
                       "trace_numeric_address": address, "trace_numeric_address_hex": hex(address),
                       "oracle_expected": False, "trace_line": line})
    region_coverage = []
    for layer in range(28):
        kernel = select_awq(rows, 2, layer, "up_proj")
        path = trace_path(args.trace_root, kernel)
        begin, end, _item = by_layer[layer]
        address, line_number, _line = find_address(path, (begin, end))
        region_coverage.append({"layer_index": layer, "kernel_id": kernel,
                                "trace_artifact": path.name,
                                "first_observed_address": address,
                                "first_observed_address_hex": hex(address),
                                "trace_line_number": line_number,
                                "observed_at_least_once": True})
    dump(args.output, {"status": "PASS", "run_id": EXPECTED_RUN_ID,
                       "targets": target_output, "non_targets": exclusions,
                       "region_coverage": region_coverage,
                       "all_28_regions_observed_at_least_once": True,
                       "selection_is_deterministic": True})
    print(json.dumps({"targets": len(target_output), "non_targets": len(exclusions)}, sort_keys=True))


def read_observer(path: Path):
    rows = []
    with path.open(newline="", encoding="utf-8") as stream:
        for line in stream:
            if line.startswith("ADDRESS_INTEGRATION_CANARY_ONLY_COMPLETE"):
                continue
            if line.startswith("stage\t"):
                header = line.rstrip("\n").split("\t")
                continue
            values = line.rstrip("\n").split("\t")
            require(len(values) == len(header), f"ragged observer row in {path}")
            rows.append(dict(zip(header, values)))
    require(rows, f"empty observer evidence {path}")
    return rows


def verify(args) -> None:
    inputs = read_json(args.input_canaries)
    expected = {int(row["layer_index"]): row for row in inputs["targets"]}
    observer_paths = {}
    for item in args.observer:
        layer_text, path_text = item.split("=", 1)
        observer_paths[int(layer_text)] = Path(path_text)
    require(set(observer_paths) == {0, 14, 27}, "requires exact L0/L14/L27 observer logs")
    required_stages = ("TRACE_PARSED_LANE", "INSTRUCTION_OPERAND", "MEM_ACCESS_CREATED",
                       "MEM_FETCH_CONSTRUCT", "L2_ENTRY", "ORACLE_LOOKUP")
    output = []
    for layer in (0, 14, 27):
        address = int(expected[layer]["trace_numeric_address"])
        rows = read_observer(observer_paths[layer])
        stage_rows = {}
        for stage in required_stages:
            selected = [row for row in rows if row["stage"] == stage and
                        int(row["address_dec"]) == address]
            require(selected, f"layer {layer} missing exact {stage} observation")
            require(all(int(row["address_dec"]) == address for row in selected),
                    f"layer {layer} {stage} numeric drift")
            stage_rows[stage] = {
                "observation_count": len(selected),
                "address": address,
                "address_hex": hex(address),
                "request_uids": sorted({int(row["request_uid"]) for row in selected}),
            }
        oracle = [row for row in rows if row["stage"] == "ORACLE_LOOKUP" and
                  int(row["address_dec"]) == address]
        require(all(row["target"] == "1" and row["interval_match"] == "1" and
                    row["eligibility"] == "1" and int(row["target_class"]) == layer + 1
                    for row in oracle), f"layer {layer} oracle activation mismatch")
        output.append({
            "layer_index": layer,
            "kernel_id": int(expected[layer]["kernel_id"]),
            "trace_artifact": expected[layer]["trace_artifact"],
            "selected_trace_line_number": int(expected[layer]["trace_line_number"]),
            "numeric_address": address,
            "numeric_address_hex": hex(address),
            "stages": stage_rows,
            "exact_numeric_equality_all_hops": True,
            "oracle_target": True,
            "target_class": layer + 1,
            "run_class": "ADDRESS_INTEGRATION_CANARY_ONLY",
        })
    dump(args.output, {
        "status": "PASS",
        "schema": "C16_E1_REAL_ARTIFACT_ADDRESS_CANARIES_V1",
        "address_relation": "EXACT_NUMERIC_EQUALITY_ALL_OBSERVED_HOPS",
        "alignment_only": False,
        "deterministic_transform_required": False,
        "canaries": output,
    })

    with args.activation_tsv.open(newline="", encoding="utf-8") as stream:
        activation_rows = list(csv.DictReader(stream, delimiter="\t"))
    require(activation_rows and all(row["target"] == row["expected"] for row in activation_rows),
            "oracle activation expectation mismatch")
    by_label = {row["label"]: row for row in activation_rows}
    require(all(by_label[label]["target"] == "1" for label in
                ("L0_up_qweight", "L14_up_qweight", "L27_up_qweight")),
            "target activation matrix mismatch")
    require(all(by_label[label]["target"] == "0" for label in
                ("L0_gate_qweight", "L0_down_qweight", "L0_up_qzeros", "L0_up_scales",
                 "self_attn", "PTE_on_target_address", "write_on_target_address",
                 "writeback_on_target_address", "instruction_on_target_address")),
            "non-target exclusion matrix mismatch")
    dump(args.activation_output, {
        "status": "PASS", "schema": "C16_E1_ORACLE_TAG_ACTIVATION_CANARY_V1",
        "authority": "CORE_ORACLE_CONFIG_PARSER_AND_LOOKUP",
        "rows": activation_rows,
        "not_all_global_reads_are_target": True,
        "pte_synthetic_write_writeback_instruction_excluded": True,
    })
    print(json.dumps({"address_canaries": 3, "activation_rows": len(activation_rows)},
                     sort_keys=True))


def opcode_audit(args) -> None:
    with args.trace_index.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    require(len(rows) == 4515, "opcode audit requires complete 4515-kernel index")
    counts = {}
    for row in rows:
        for opcode, count in json.loads(row["opcode_counts_json"]).items():
            counts[opcode] = counts.get(opcode, 0) + int(count)
    header = args.ampere_header.read_text(encoding="utf-8")
    mapped = set(re.findall(r'\{"([A-Z0-9_]+)",\s*OpcodeChar', header))
    bases = {opcode.split(".", 1)[0] for opcode in counts}
    missing = sorted(bases - mapped)
    dump(args.output, {
        "status": "PASS" if not missing else "FAIL",
        "schema": "C16_E1_SM89_TO_AMPERE_FULL_BUNDLE_OPCODE_AUDIT_V1",
        "trace_kernel_count": len(rows),
        "trace_opcode_spelling_count": len(counts),
        "trace_base_opcode_count": len(bases),
        "ampere_map_entry_count": len(mapped),
        "missing_base_opcodes": missing,
        "all_trace_base_opcodes_mapped": not missing,
        "binary_version_adapter": "SM89_89_TO_ACCEPTED_AMPERE_OPCODE_MAP",
        "claim_boundary": "PARSER_EXECUTION_COMPATIBILITY_ONLY_NO_ADA_MICROARCH_FIDELITY_CLAIM",
        "opcode_counts": counts,
    })
    require(not missing, f"SM89 trace contains unmapped base opcodes: {missing}")
    print(json.dumps({"base_opcodes": len(bases), "missing": 0}, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--oracle-json", type=Path, required=True)
    common.add_argument("--manifest", type=Path, required=True)
    generate_parser = sub.add_parser("generate", parents=[common])
    generate_parser.add_argument("--sidecar", type=Path, required=True)
    generate_parser.add_argument("--provenance", type=Path, required=True)
    generate_parser.add_argument("--producer-head", required=True)
    extract_parser = sub.add_parser("extract", parents=[common])
    extract_parser.add_argument("--trace-root", type=Path, required=True)
    extract_parser.add_argument("--trace-audit", type=Path, required=True)
    extract_parser.add_argument("--kernel-sequence", type=Path, required=True)
    extract_parser.add_argument("--output", type=Path, required=True)
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--input-canaries", type=Path, required=True)
    verify_parser.add_argument("--observer", action="append", required=True)
    verify_parser.add_argument("--activation-tsv", type=Path, required=True)
    verify_parser.add_argument("--output", type=Path, required=True)
    verify_parser.add_argument("--activation-output", type=Path, required=True)
    opcode_parser = sub.add_parser("opcode-audit")
    opcode_parser.add_argument("--trace-index", type=Path, required=True)
    opcode_parser.add_argument("--ampere-header", type=Path, required=True)
    opcode_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "generate":
        generate(args)
    elif args.command == "extract":
        extract(args)
    elif args.command == "verify":
        verify(args)
    else:
        opcode_audit(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
