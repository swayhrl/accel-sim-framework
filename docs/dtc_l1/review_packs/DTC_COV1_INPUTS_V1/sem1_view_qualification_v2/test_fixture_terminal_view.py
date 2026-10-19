"""PREPARED_NOT_TESTED. Four pure view groups; no root/process/proc operations.

Future parent must separately hash/admit this CPU test entry. These mocks prove
only view control-flow boundaries; not actual pidfds, live process observations,
resource admission or fixture results. Not imported or run during preparation.
"""
from copy import deepcopy
import unittest
from fixture_terminal_view import (FixtureTerminalView, OwnRootIdentityUnresolved,
                                   _OwnRootTerminal, eligible_terminal)

OWN = {"boot_id": "test-boot", "pid": 100, "start_ticks": 200, "tgid": 100}
Z = dict(OWN, state="Z", ppid=99)
PROOF = {"retained_direct_Popen": True, "unreaped": True, "pidfd_matches": True,
         "instance": OWN, "current": Z, "role": "SEM1_ACTUAL_OBJECT_FIXTURE_RUNTIME_V1"}


def fake_view(callback):
    view = object.__new__(FixtureTerminalView)
    view._owner = {"boot_id": "test-boot", "pid": 99, "start_ticks": 150, "tgid": 99}
    view._identity = lambda pid: deepcopy(view._owner)
    view._retained = lambda: deepcopy(PROOF)
    view._terminal_proof = lambda pid: deepcopy(PROOF) if pid == OWN["pid"] else None
    snapshot = {"processes": [dict(OWN, rss_bytes=10), {"pid": 300, "start_ticks": 400,
                  "rss_bytes": 20}], "all_process_RSS_sum_bytes": 30,
                "FLOCKs": [{"pid": 300, "path": "/test/foreign.lock"}]}
    view._snapshot = lambda: deepcopy(snapshot)
    view._review = callback
    return view, snapshot


class PureTerminalViewBoundaries(unittest.TestCase):
    def test_group1_only_same_retained_unreaped_pidfd_Z_is_eligible(self):
        self.assertTrue(eligible_terminal(PROOF, Z))
        self.assertFalse(eligible_terminal(PROOF, None))
        self.assertFalse(eligible_terminal(PROOF, dict(Z, state="R")))
        for key in ("boot_id", "pid", "start_ticks", "tgid"):
            self.assertFalse(eligible_terminal(PROOF, dict(Z, **{key: "changed"})))
        for key in ("retained_direct_Popen", "unreaped", "pidfd_matches"):
            self.assertFalse(eligible_terminal(dict(PROOF, **{key: False}), Z))

    def test_group2_only_authority_projects_own_Z_preserving_all_resources(self):
        seen = []
        def callback(snapshot):
            seen.append(deepcopy(snapshot))
            if any(row["pid"] == OWN["pid"] for row in snapshot["processes"]):
                raise _OwnRootTerminal(deepcopy(PROOF))
            return {"status": "PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY"}
        view, full = fake_view(callback)
        returned, verdict = view.review(view._owner)
        self.assertEqual(returned, full)
        self.assertEqual(returned["all_process_RSS_sum_bytes"], 30)
        self.assertEqual(seen[1]["FLOCKs"], full["FLOCKs"])
        self.assertEqual(seen[1]["processes"], [full["processes"][1]])
        self.assertEqual(verdict["own_fixture_terminal_projection"][0]["live_observation"],
                         "UNAVAILABLE_NO_RETRY")
        self.assertEqual(verdict["original_process_count"], 2)
        self.assertEqual(len(seen), 2)

    def test_group3_generic_foreign_failure_is_never_terminal_success(self):
        def callback(snapshot):
            raise ValueError("FOREIGN_ROLE_OR_AUTHORITY_FAILURE")
        view, _ = fake_view(callback)
        with self.assertRaisesRegex(ValueError, "FOREIGN_ROLE"):
            view.review(view._owner)
        view, _ = fake_view(lambda snapshot: {
            "status": "PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY",
            "exact_external_CPU_controls": [{
                "role": "SEM1_ACTUAL_OBJECT_FIXTURE_RUNTIME_V1",
                "pid": 300, "start_ticks": 400}]})
        with self.assertRaisesRegex(OwnRootIdentityUnresolved, "FOREIGN_MATCHING"):
            view.review(view._owner)

    def test_group4_absent_own_and_second_foreign_failure_remain_STOP(self):
        view, _ = fake_view(lambda snapshot: {"status": "SHOULD_NOT_RUN"})
        def absent():
            raise OwnRootIdentityUnresolved("OWN_UNREAPED_ROOT_ABSENT")
        view._retained = absent
        with self.assertRaises(OwnRootIdentityUnresolved):
            view.review(view._owner)
        calls = []
        def callback(snapshot):
            calls.append(1)
            if len(calls) == 1:
                raise _OwnRootTerminal(deepcopy(PROOF))
            raise ValueError("FOREIGN_LOCK_NOT_CLOSED")
        view, _ = fake_view(callback)
        with self.assertRaisesRegex(ValueError, "FOREIGN_LOCK"):
            view.review(view._owner)
        self.assertEqual(len(calls), 2)


if __name__ == "__main__":
    unittest.main()
