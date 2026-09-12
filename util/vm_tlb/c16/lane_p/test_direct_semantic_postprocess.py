#!/usr/bin/env python3
"""Focused checks for semantic-output publication boundaries."""
from __future__ import annotations

import unittest

from direct_semantic_postprocess import ContractError, publication_policy


class SemanticPublicationPolicyTest(unittest.TestCase):
    def test_default_remains_provisional(self) -> None:
        policy = publication_policy({})
        self.assertEqual(policy["status"], "REAL_NATIVE_SCHEMA_SANITY / PROVISIONAL")
        self.assertFalse(policy["scientific_eligible"])

    def test_holdout_is_c_forbidden(self) -> None:
        policy = publication_policy({"publication_policy": {
            "status": "PIPELINE_DIAGNOSTIC_ONLY / HOLDOUT_PENDING_FREEZE",
            "scientific_eligible": False,
            "cross_lane_visibility": "C_FORBIDDEN_HOLDOUT_PENDING_SELECTOR_FREEZE",
        }})
        self.assertEqual(policy["cross_lane_visibility"], "C_FORBIDDEN_HOLDOUT_PENDING_SELECTOR_FREEZE")

    def test_invalid_policy_fails_closed(self) -> None:
        with self.assertRaises(ContractError):
            publication_policy({"publication_policy": {"scientific_eligible": "false"}})


if __name__ == "__main__":
    unittest.main()
