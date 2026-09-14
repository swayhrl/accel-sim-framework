from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LANE = ROOT / "util" / "vm_tlb" / "c16" / "lane_g"
sys.path.insert(0, str(LANE))
from llama_route_formal_support import (  # noqa: E402
    MAX_RAW_BYTES, PRIMARY_IDENTITY, RouteBContractError, analyze_route_c,
    digest, freeze_partitions, freeze_whitelists, validate_capture,
)


class LlamaRouteFormalSupportTests(unittest.TestCase):
    def _frozen_whitelists(self, root: Path) -> Path:
        static_map = root / "map.tsv"
        fields = ["nvbit_static_index", "instruction_offset", "opcode", "memory_space", "is_load", "is_store", "has_mref", "mref_count", "width_bytes", "function_mangled_name"]
        with static_map.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t"); writer.writeheader()
            writer.writerow({"nvbit_static_index": "7", "instruction_offset": "12", "opcode": "LDG.E.64", "memory_space": "GLOBAL", "is_load": "1", "is_store": "0", "has_mref": "1", "mref_count": "2", "width_bytes": "8", "function_mangled_name": "_Zexact"})
        selection = root / "selection.json"
        selection.write_text(json.dumps({"schema_version": "C16_ROUTE_B_FINAL_SELECTION_V2", "status": "FROZEN_PRE_OUTCOME_SELECTION", "final_request_ids": ["R"]}))
        index = root / "index.json"
        index.write_text(json.dumps({"schema_version": "C16_ROUTE_B_SELECTED_MAP_INDEX_V1", "identity": PRIMARY_IDENTITY, "maps": [{"request_id": "R", "exact_function_mangled_name": "_Zexact", "static_map": str(static_map), "static_map_sha256": digest(static_map), "code_object_sha256": "a" * 64}]}))
        output = root / "whitelists.json"; freeze_whitelists(selection, index, output)
        return output

    def test_freeze_partitions_and_capture_validate_predicate_lanes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); whitelists = self._frozen_whitelists(root)
            assignments = root / "assignments.json"
            assignments.write_text(json.dumps({"schema_version": "C16_ROUTE_B_PARTITION_ASSIGNMENTS_V1", "assignments": [{"unit_id": "R:7:0", "partition_id": "P0"}, {"unit_id": "R:7:1", "partition_id": "P1"}]}))
            partitions = root / "partitions.json"; freeze_partitions(whitelists, assignments, partitions)
            raw = root / "raw.jsonl"
            base = {"sequence_label": "OBSERVED_CALLBACK_ORDER", "kernel_launch_id": 9, "function_mangled_name": "_Zexact", "cta": [0, 0, 0], "warp_id": 0, "static_index": 7, "instruction_offset": 12, "opcode": "LDG.E.64", "mref_ordinal": 0, "access_kind": "READ", "width_bytes": 8, "memory_space": "GLOBAL", "active_mask": 7, "predicate_mask": 5, "predicate_semantics": "GUARD_PREDICATE_MASK", "record_kind": "LANE_EVENT", "raw_schema": "C16_ROUTE_B_LANE_EVENT_V1", "warp_instruction_instance_id": 0}
            events = [dict(base, observed_event_sequence=0, lane_id=0, gpu_va=0x1000), dict(base, observed_event_sequence=1, lane_id=2, gpu_va=0x1010)]
            raw.write_text("".join(json.dumps(event) + "\n" for event in events))
            terminal = root / "terminal.json"; terminal.write_text(json.dumps({"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0, "event_count": 2}))
            metadata = root / "metadata.json"; metadata.write_text(json.dumps({"identity": PRIMARY_IDENTITY, "raw_schema": "C16_ROUTE_B_LANE_EVENT_V1", "capture_duration_seconds": 1, "serialized_raw_bytes": raw.stat().st_size, "raw_byte_cap": MAX_RAW_BYTES}))
            output = root / "canary.json"; validate_capture(whitelists, raw, terminal, metadata, output, "ROUTEB_CANARY")
            self.assertEqual("PASS_ROUTEB_CANARY", json.loads(output.read_text())["status"])

    def test_partition_and_route_c_fail_closed_on_missing_coverage_authority(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); whitelists = self._frozen_whitelists(root)
            bad = root / "bad.json"; bad.write_text(json.dumps({"schema_version": "C16_ROUTE_B_PARTITION_ASSIGNMENTS_V1", "assignments": [{"unit_id": "R:7:0", "partition_id": "P0"}]}))
            with self.assertRaises(RouteBContractError): freeze_partitions(whitelists, bad, root / "no.json")
            census = root / "census.json"; census.write_text(json.dumps({"schema_version": "C16_LLAMA_S0_FULL_CENSUS_V1", "identity": PRIMARY_IDENTITY, "rows": [{"request_id": "P", "phase": "PREFILL", "duration_ns": 5}, {"request_id": "D", "phase": "DECODE", "duration_ns": 7}]}))
            reference = root / "routec.json"; reference.write_text(json.dumps({"schema_version": "C16_ROUTE_C_PHASE_COVERAGE_V1", "identity": PRIMARY_IDENTITY, "covered_request_ids": ["P", "D"]}))
            out = root / "analysis.json"; analyze_route_c(census, reference, out)
            result = json.loads(out.read_text()); self.assertEqual(1.0, result["phases"]["PREFILL"]["coverage"])


if __name__ == "__main__":
    unittest.main()
