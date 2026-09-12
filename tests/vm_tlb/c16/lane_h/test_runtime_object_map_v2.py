from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from util.vm_tlb.c16.lane_h.runtime_object_map_v2 import (  # noqa: E402
    ObjectMapError,
    RuntimeObjectMapV2,
)


FIXTURE = Path(__file__).with_name("fixtures") / "object_map_v2.json"


class RuntimeObjectMapV2Test(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.object_map = RuntimeObjectMapV2.from_payload(self.payload)

    def test_tied_storage_generation_grow_replace_and_unknown_release(self) -> None:
        self.assertEqual(self.object_map.event_count, 11)
        self.assertEqual(self.object_map.classify(0x7F, 4).object_class, "WEIGHT")
        self.assertEqual(self.object_map.classify(0x210, 4).object_class, "QUANT_METADATA")
        self.assertEqual(self.object_map.classify(0x3FFF8, 16).object_class, "KV_CACHE")

        # A full-width access straddling WEIGHT and quant metadata must not be
        # assigned to either class.
        crossing = self.object_map.classify(0x1FF, 2)
        self.assertEqual(crossing.object_class, "UNKNOWN_RUNTIME")
        self.assertEqual(crossing.reason, "RANGE_BOUNDARY_CROSSING")

        # Re-use of a pointer is generation-qualified, not address-qualified.
        before_release = self.object_map.classify(0x90000, 4, event_ordinal=8)
        after_reuse = self.object_map.classify(0x90000, 4)
        self.assertEqual((before_release.object_class, before_release.generation), ("WEIGHT", 1))
        self.assertEqual((after_reuse.object_class, after_reuse.generation), ("KV_CACHE", 2))

        # A replaced KV allocation does not imply an unobserved GPU free.
        audit = {(row["storage_id"], row["generation"]): row for row in self.object_map.audit_rows()}
        self.assertEqual(audit[("kv-original", 0)]["state"], "UNKNOWN_ACTIVE")
        self.assertEqual(audit[("unknown-release-proof", 0)]["state"], "RELEASED")
        self.assertEqual(self.object_map.classify(0x70000, 4).object_class, "UNKNOWN_RUNTIME")

    def test_activation_and_python_gc_are_rejected(self) -> None:
        activation = copy.deepcopy(self.payload)
        activation["events"][0]["object_class"] = "ACTIVATION"
        with self.assertRaises(ObjectMapError):
            RuntimeObjectMapV2.from_payload(activation)

        guessed_release = copy.deepcopy(self.payload)
        guessed_release["events"][7]["release_evidence"] = "PYTHON_GC"
        with self.assertRaises(ObjectMapError):
            RuntimeObjectMapV2.from_payload(guessed_release)

    def test_view_must_stay_inside_storage(self) -> None:
        escaped_view = copy.deepcopy(self.payload)
        escaped_view["events"][1]["view_end_exclusive"] = "0x201"
        with self.assertRaises(ObjectMapError):
            RuntimeObjectMapV2.from_payload(escaped_view)


if __name__ == "__main__":
    unittest.main()
