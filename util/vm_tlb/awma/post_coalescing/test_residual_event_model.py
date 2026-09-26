#!/usr/bin/env python3
import unittest

from residual_event_model import (
    AccessTimeline,
    PortRequest,
    TranslationGroup,
    choose_demand_before_prelaunch,
    classify_residual,
    is_last_unresolved_head_group,
)


class LastUnresolvedTests(unittest.TestCase):
    def test_last_unresolved_multi_page_head_is_critical(self):
        groups = [
            TranslationGroup("i0", "p0", 0, False, True),
            TranslationGroup("i0", "p1", 1, True, False),
        ]
        self.assertTrue(is_last_unresolved_head_group(groups[1], groups))

    def test_nonhead_is_not_critical(self):
        groups = [
            TranslationGroup("i0", "p0", 0, False, False),
            TranslationGroup("i0", "p1", 1, False, True),
        ]
        self.assertFalse(is_last_unresolved_head_group(groups[0], groups))

    def test_two_unresolved_groups_are_not_last(self):
        groups = [
            TranslationGroup("i0", "p0", 0, True, False),
            TranslationGroup("i0", "p1", 1, False, False),
        ]
        self.assertFalse(is_last_unresolved_head_group(groups[0], groups))

    def test_single_page_is_ordinary_demand_not_h1(self):
        group = TranslationGroup("i0", "p0", 0, True, False)
        self.assertFalse(is_last_unresolved_head_group(group, [group]))

    def test_other_instruction_state_is_not_future_or_cross_group(self):
        groups = [
            TranslationGroup("i0", "p0", 0, True, False),
            TranslationGroup("i1", "p0", 1, False, True),
        ]
        self.assertFalse(is_last_unresolved_head_group(groups[0], groups))


class DemandBeforePrelaunchTests(unittest.TestCase):
    def test_head_demand_wins_one_real_port(self):
        requests = [
            PortRequest("prelaunch", 0, True, False, True),
            PortRequest("head", 1, True, True, False),
        ]
        self.assertEqual(choose_demand_before_prelaunch(requests), ["head"])

    def test_prelaunch_uses_idle_port(self):
        request = PortRequest("prelaunch", 0, True, False, True)
        self.assertEqual(choose_demand_before_prelaunch([request]), ["prelaunch"])

    def test_ineligible_request_is_never_granted(self):
        requests = [
            PortRequest("head", 0, False, True, False),
            PortRequest("prelaunch", 1, True, False, True),
        ]
        self.assertEqual(choose_demand_before_prelaunch(requests), ["prelaunch"])

    def test_finite_two_slots(self):
        requests = [
            PortRequest("h1", 1, True, True, False),
            PortRequest("h0", 0, True, True, False),
            PortRequest("p0", 2, True, False, True),
        ]
        self.assertEqual(
            choose_demand_before_prelaunch(requests, slots=2), ["h0", "h1"]
        )

    def test_zero_slots_is_zero_grants(self):
        request = PortRequest("head", 0, True, True, False)
        self.assertEqual(choose_demand_before_prelaunch([request], slots=0), [])


class TimelineTests(unittest.TestCase):
    def test_translation_wait_is_separate(self):
        timeline = AccessTimeline(10, 20, 20, 20)
        self.assertEqual(classify_residual(timeline), "TRANSLATION_WAIT_PRESENT")

    def test_ready_consumption_delay_is_separate(self):
        timeline = AccessTimeline(10, 10, 15, 15)
        self.assertEqual(
            classify_residual(timeline), "READY_RESULT_CONSUMPTION_DELAY"
        )

    def test_post_translation_admission_delay_is_separate(self):
        timeline = AccessTimeline(10, 10, 10, 18)
        self.assertEqual(
            classify_residual(timeline), "POST_TRANSLATION_ADMISSION_DELAY"
        )

    def test_non_monotonic_events_fail(self):
        with self.assertRaises(ValueError):
            AccessTimeline(10, 9, 11, 12).validate()


if __name__ == "__main__":
    unittest.main()
