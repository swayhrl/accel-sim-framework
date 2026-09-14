#!/usr/bin/env python3
"""CPU-only Q0 tests for the Route-B LANE_EVENT host preflight/parser."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LANE = ROOT / "util" / "vm_tlb" / "c16" / "lane_g"
sys.path.insert(0, str(LANE))

from route_b_memory_event_contract import RouteBContractError
from route_b_memory_event_host import load_whitelist, parse_raw_jsonl, write_parse_manifest, write_verified_producer_manifest
from route_b_producer_q0 import ProducerBinding, whitelist_sha256


def lane_event(sequence: int, lane: int, address: int) -> dict:
    return {
        "record_kind": "LANE_EVENT", "raw_schema": "C16_ROUTE_B_LANE_EVENT_V1",
        "sequence_label": "OBSERVED_CALLBACK_ORDER", "observed_event_sequence": sequence,
        "warp_instruction_instance_id": 41, "kernel_launch_id": 5, "function_mangled_name": "_Zexact",
        "cta": [0, 0, 0], "warp_id": 0, "static_index": 7, "instruction_offset": 32,
        "opcode": "LDG.E.64", "mref_ordinal": 0, "access_kind": "READ", "width_bytes": 8,
        "memory_space": "GLOBAL", "active_mask": 3, "predicate_mask": 3, "predicate_semantics": "GUARD_PREDICATE_MASK",
        "lane_id": lane, "gpu_va": address,
    }


class RouteBMemoryEventHostTests(unittest.TestCase):
    def _binding_and_manifest(self, root: Path):
        code, static_map, whitelist = root / "code.so", root / "map.tsv", root / "whitelist.json"
        code.write_bytes(b"code-object")
        static_map.write_bytes(b"static-map")
        rows = [{"static_index": 7, "opcode": "LDG.E.64", "memory_space": "GLOBAL", "has_mref": True,
                 "access_kind": "READ", "width_bytes": 8, "mref_ordinal": 0, "mref_count": 1}]
        whitelist.write_text(json.dumps({"whitelist": rows}), encoding="utf-8")
        loaded = load_whitelist(whitelist)
        binding = ProducerBinding("_Zexact", code, hashlib.sha256(b"code-object").hexdigest(), static_map,
                                  hashlib.sha256(b"static-map").hexdigest(), whitelist_sha256(loaded), 4096)
        return write_verified_producer_manifest(root / "producer_manifest.json", binding, whitelist)

    def test_manifest_and_explicit_instance_parser_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); manifest = self._binding_and_manifest(root); raw = root / "raw.jsonl"
            raw.write_text("\n".join(json.dumps(x) for x in [lane_event(1, 0, 0x1000), lane_event(2, 1, 0x1008),
                           {"record_kind": "TERMINAL", "terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0, "event_count": 2}]) + "\n")
            parsed = parse_raw_jsonl(raw, manifest)
            self.assertEqual("PASS_LANE_EVENT_STREAM", parsed["result"])
            self.assertEqual(2, parsed["event_count"])
            written = write_parse_manifest(root / "parse_manifest.json", raw, manifest)
            self.assertEqual(parsed["raw_sha256"], written["raw_sha256"])

    def test_parser_fails_closed_for_missing_terminal_and_dropped_event(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); manifest = self._binding_and_manifest(root); raw = root / "raw.jsonl"
            raw.write_text(json.dumps(lane_event(1, 0, 0x1000)) + "\n")
            with self.assertRaises(RouteBContractError):
                parse_raw_jsonl(raw, manifest)
            raw.write_text("\n".join(json.dumps(x) for x in [lane_event(1, 0, 0x1000), lane_event(2, 1, 0x1008),
                           {"record_kind": "TERMINAL", "terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 1, "event_count": 2}]) + "\n")
            with self.assertRaises(RouteBContractError):
                parse_raw_jsonl(raw, manifest)

    def test_parser_gates_actual_raw_bytes_and_terminal_event_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); manifest = self._binding_and_manifest(root); raw = root / "raw.jsonl"
            raw.write_text("\n".join(json.dumps(x) for x in [lane_event(1, 0, 0x1000), lane_event(2, 1, 0x1008),
                           {"record_kind": "TERMINAL", "terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0, "event_count": 1}]) + "\n")
            with self.assertRaises(RouteBContractError):
                parse_raw_jsonl(raw, manifest)
            manifest["host_output_cap_bytes"] = raw.stat().st_size - 1
            with self.assertRaises(RouteBContractError):
                parse_raw_jsonl(raw, manifest)

    def test_host_tool_has_required_lifecycle_and_lane_schema(self):
        source = (LANE / "route_b_memory_event_tool.cu").read_text(encoding="utf-8")
        for token in ("load_whitelist", "nvbit_add_call_arg_mref_addr64", "cudaMalloc", "cudaMemset", "cudaMemcpy",
                      "append_readback", "emit_terminal", "host_output_cap_bytes", "actual_output_bytes", "stat(output_jsonl.c_str()", "events_already_serialized", "terminal_json", "warp_instruction_instance_id", "ROUTE_B_LANE_EVENT"):
            self.assertIn(token, source)
        self.assertNotIn("gpu_va_by_address_lane", source)


if __name__ == "__main__":
    unittest.main()
