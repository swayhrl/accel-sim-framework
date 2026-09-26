#!/usr/bin/env python3
import unittest

from path_model_fixture import (
    AccessCase,
    ExactlyOnceApplication,
    Operation,
    current_sequential,
    vipt_like_minimum_overlap,
    virtual_l1_filter_bound,
)


class PathModelTests(unittest.TestCase):
    def test_l1d_hit_l1tlb_hit(self):
        case = AccessCase(tlb_hit=True, l1d_hit=True)
        self.assertEqual(current_sequential(case).completion_cycle, 42)
        self.assertEqual(vipt_like_minimum_overlap(case).completion_cycle, 32)

    def test_l1d_miss_l1tlb_hit_lower_waits(self):
        case = AccessCase(tlb_hit=True, l1d_hit=False)
        self.assertEqual(current_sequential(case).lower_physical_issue_cycle, 42)
        self.assertEqual(
            vipt_like_minimum_overlap(case).lower_physical_issue_cycle, 32
        )
        self.assertGreaterEqual(
            vipt_like_minimum_overlap(case).lower_physical_issue_cycle,
            case.physical_translation_latency,
        )

    def test_l1d_hit_l1tlb_miss_legality_wait(self):
        case = AccessCase(tlb_hit=False, l1d_hit=True)
        self.assertEqual(case.physical_translation_latency, 90)
        self.assertEqual(current_sequential(case).completion_cycle, 122)
        self.assertEqual(vipt_like_minimum_overlap(case).completion_cycle, 112)
        self.assertGreaterEqual(
            vipt_like_minimum_overlap(case).completion_cycle,
            case.physical_translation_latency,
        )

    def test_l1d_miss_l1tlb_miss_no_lower_skip(self):
        case = AccessCase(tlb_hit=False, l1d_hit=False)
        outcome = vipt_like_minimum_overlap(case)
        self.assertTrue(outcome.translation_required)
        self.assertEqual(outcome.translation_services, 1)
        self.assertEqual(outcome.lower_physical_issue_cycle, 112)

    def test_replay_translation_application_exactly_once(self):
        state = ExactlyOnceApplication()
        self.assertTrue(state.apply())
        self.assertFalse(state.apply())
        self.assertEqual(state.applications, 1)

    def test_b1_never_changes_request_counts(self):
        for tlb_hit in (False, True):
            for l1d_hit in (False, True):
                case = AccessCase(tlb_hit=tlb_hit, l1d_hit=l1d_hit)
                before = current_sequential(case)
                after = vipt_like_minimum_overlap(case)
                self.assertEqual(after.translation_services, before.translation_services)
                self.assertEqual(after.data_requests, before.data_requests)

    def test_virtual_filter_load_hit_bound(self):
        case = AccessCase(tlb_hit=False, l1d_hit=True, operation=Operation.LOAD)
        outcome = virtual_l1_filter_bound(case, cached_permission_valid=True)
        self.assertFalse(outcome.translation_required)
        self.assertEqual(outcome.translation_services, 0)
        self.assertEqual(outcome.completion_cycle, 32)

    def test_virtual_filter_miss_requires_translation(self):
        case = AccessCase(tlb_hit=True, l1d_hit=False, operation=Operation.LOAD)
        outcome = virtual_l1_filter_bound(case, cached_permission_valid=True)
        self.assertTrue(outcome.translation_required)
        self.assertEqual(outcome.lower_physical_issue_cycle, 42)

    def test_virtual_filter_without_cached_permission_requires_translation(self):
        case = AccessCase(tlb_hit=True, l1d_hit=True, operation=Operation.LOAD)
        outcome = virtual_l1_filter_bound(case, cached_permission_valid=False)
        self.assertTrue(outcome.translation_required)

    def test_store_and_atomic_do_not_use_unimplemented_filter(self):
        for operation in (Operation.STORE, Operation.ATOMIC):
            case = AccessCase(tlb_hit=True, l1d_hit=True, operation=operation)
            b1 = vipt_like_minimum_overlap(case)
            self.assertTrue(b1.translation_required)
            self.assertEqual(b1.translation_services, 1)
            self.assertEqual(b1.data_requests, 1)
            outcome = virtual_l1_filter_bound(case, cached_permission_valid=True)
            self.assertTrue(outcome.translation_required)
            self.assertEqual(outcome.translation_services, 1)
            self.assertEqual(outcome.data_requests, 1)


if __name__ == "__main__":
    unittest.main()
