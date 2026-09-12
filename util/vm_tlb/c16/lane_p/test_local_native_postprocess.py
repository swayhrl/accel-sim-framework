#!/usr/bin/env python3
"""Focused contract checks for local-catalog publication boundaries."""
from __future__ import annotations

import unittest

from local_native_postprocess import ContractError, publication_policy


class PublicationPolicyTest(unittest.TestCase):
    def test_default_is_provisional_and_not_cross_lane_consumable(self) -> None:
        policy = publication_policy({})
        self.assertFalse(policy["scientific_eligible"])
        self.assertEqual(policy["status"], "REAL_NATIVE_SCHEMA_SANITY / PROVISIONAL")

    def test_holdout_policy_is_preserved(self) -> None:
        policy = publication_policy({
            "publication_policy": {
                "status": "PIPELINE_DIAGNOSTIC_ONLY / HOLDOUT_PENDING_FREEZE",
                "scientific_eligible": False,
                "provisional_reason": "await selector freeze",
                "cross_lane_visibility": "C_FORBIDDEN_UNTIL_SELECTOR_FREEZE",
            },
        })
        self.assertEqual(policy["status"], "PIPELINE_DIAGNOSTIC_ONLY / HOLDOUT_PENDING_FREEZE")
        self.assertEqual(policy["cross_lane_visibility"], "C_FORBIDDEN_UNTIL_SELECTOR_FREEZE")

    def test_invalid_holdout_policy_fails_closed(self) -> None:
        with self.assertRaises(ContractError):
            publication_policy({"publication_policy": {"scientific_eligible": "false"}})


if __name__ == "__main__":
    unittest.main()
