#!/usr/bin/env python3
"""Focused contract checks for terminal event scoping in the P monitor."""
from __future__ import annotations

import unittest

from unattended_event_monitor import receipt_terminal_declarations


class TerminalDeclarationTest(unittest.TestCase):
    def test_scoped_terminal_receipt_is_recorded(self) -> None:
        payload = {
            "deployment_id": "c16_qwen25_7b_awq",
            "status": "SKIPPED_RESOURCE",
        }
        self.assertEqual(
            receipt_terminal_declarations("event.json", payload),
            [{
                "path": "event.json",
                "deployment_id": "c16_qwen25_7b_awq",
                "json_pointer": "status",
                "terminal_marker": "SKIPPED_RESOURCE",
                "value": "SKIPPED_RESOURCE",
            }],
        )

    def test_unscoped_or_nonterminal_receipts_do_not_skip(self) -> None:
        self.assertEqual(receipt_terminal_declarations("event.json", {"status": "SKIPPED_RESOURCE"}), [])
        self.assertEqual(
            receipt_terminal_declarations(
                "event.json",
                {"deployment_id": "c16_qwen25_7b_awq", "status": "CONSUMED_TRANSFER_HASH_CLOSED"},
            ),
            [],
        )

    def test_nested_deployment_scope_is_preserved(self) -> None:
        payload = {
            "events": [{
                "identity": {"deployment_id": "c16_qwen25_7b_awq"},
                "outcome": "BLOCKED",
            }],
        }
        found = receipt_terminal_declarations("event.json", payload)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["deployment_id"], "c16_qwen25_7b_awq")
        self.assertEqual(found[0]["terminal_marker"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
