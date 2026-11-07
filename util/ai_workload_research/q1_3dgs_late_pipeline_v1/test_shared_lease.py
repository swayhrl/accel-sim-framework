import os
os.sched_setaffinity(0, {22, 23})
import copy
import time
import unittest
from unittest.mock import patch
import shared_lease


class FakeClient(shared_lease.RenewingSharedClient):
    def __init__(self):
        super().__init__({"lock": "/mock/lock",
                         "shared_resident": {"reservation_ttl_seconds": 1800}})
        self.request_id = "initial"
        self._reservation_attempted = True
        self.calls = []
        self.post_failure = None
        self.bad_response = None
        self.get_failure = None
        self.state = {
            "state": "GPU_RESERVED_FOR_AI_ARCH",
            "reservation": self.reservation("initial", 300),
            "kernel_holders": [{"identity": self.claimant}],
            "completed_scopes": 7,
            "last_quiescence": {"finished_unix": 42},
        }
        self.baseline = (7, 42)

    def reservation(self, request_id, ttl):
        return dict(owner=copy.deepcopy(self.claimant), request_id=request_id,
                    pause_new_work=True, expires_unix=time.time() + ttl)

    def get(self):
        self.calls.append(("GET", None))
        if self.get_failure:
            raise self.get_failure
        return copy.deepcopy(self.state)

    def api(self, method, path, body=None, admin=False):
        self.calls.append((method, body))
        if method == "POST":
            self.assert_post = body
            self.state["reservation"] = self.reservation("renewed", 1800)
            if self.post_failure:
                raise self.post_failure
            result = dict(reservation=copy.deepcopy(self.state["reservation"]),
                          ownership_granted=False)
            if self.bad_response:
                self.bad_response(result)
            return result, {}
        if method == "DELETE":
            self.state["reservation"] = None
            return dict(reservation=None, ownership_granted=False), {}
        raise AssertionError("No actual HTTP call is allowed")


class SharedLeaseTests(unittest.TestCase):
    def setUp(self):
        self.holders = [os.getpid()]
        self.patch = patch("shared_lease.kernel_holders",
                           side_effect=lambda _: self.holders)
        self.patch.start()
        self.client = FakeClient()

    def tearDown(self):
        self.patch.stop()

    def posts(self):
        return [x for x in self.client.calls if x[0] == "POST"]

    def deletes(self):
        return [x for x in self.client.calls if x[0] == "DELETE"]

    def test_due_renews_same_owner_and_lock(self):
        result = self.client.renew_if_due(os.getpid())
        self.assertTrue(result["renewed"])
        self.assertEqual(self.client.request_id, "renewed")
        self.assertEqual(self.posts()[0][1],
                         dict(owner_pid=os.getpid(), ttl_seconds=1800,
                              pause_new_work=True))
        self.assertFalse(result["ownership_granted"])

    def test_not_due_does_not_post(self):
        self.client.state["reservation"] = self.client.reservation("initial", 1200)
        self.assertFalse(self.client.renew_if_due()["renewed"])
        self.assertEqual([], self.posts())

    def test_foreign_owner_does_not_post(self):
        self.client.state["reservation"]["owner"]["start_ticks"] = "foreign"
        with self.assertRaisesRegex(RuntimeError, "CLAIMANT"):
            self.client.renew_if_due()
        self.assertEqual([], self.posts())

    def test_foreign_request_does_not_post(self):
        self.client.state["reservation"]["request_id"] = "foreign"
        with self.assertRaisesRegex(RuntimeError, "REQUEST"):
            self.client.renew_if_due()
        self.assertEqual([], self.posts())

    def test_foreign_lock_does_not_post(self):
        self.holders = [987654321]
        with self.assertRaisesRegex(RuntimeError, "FLOCK"):
            self.client.renew_if_due()
        self.assertEqual([], self.posts())

    def test_pause_false_does_not_post(self):
        self.client.state["reservation"]["pause_new_work"] = False
        with self.assertRaisesRegex(RuntimeError, "CLAIMANT"):
            self.client.renew_if_due()
        self.assertEqual([], self.posts())

    def test_loaded_gate_get_failure_does_not_post(self):
        self.client.get_failure = RuntimeError("Loaded code differs")
        with self.assertRaises(RuntimeError):
            self.client.renew_if_due()
        self.assertEqual([], self.posts())

    def test_invalid_ttl_constructor(self):
        for ttl in (0, True, 3600, 1800.0, 7200):
            with self.assertRaisesRegex(ValueError, "TTL"):
                shared_lease.RenewingSharedClient(
                    {"lock": "/mock", "shared_resident":
                     {"reservation_ttl_seconds": ttl}})

    def test_invalid_grant_response_stops_and_receipts(self):
        self.client.bad_response = lambda r: r.update(ownership_granted=True)
        with self.assertRaisesRegex(RuntimeError, "RESPONSE"):
            self.client.renew_if_due()
        self.assertTrue(self.client.lease_events[-1]["outcome_uncertain"])
        self.assertTrue(self.client.release()["released"])

    def test_failed_post_after_commit_cleanup_adopts_own_new_id(self):
        self.client.post_failure = TimeoutError("mock lost response")
        with self.assertRaises(TimeoutError):
            self.client.renew_if_due()
        self.assertEqual("initial", self.client.request_id)
        self.assertEqual("renewed",
                         self.client.state["reservation"]["request_id"])
        self.assertTrue(self.client.release()["released"])
        self.assertEqual(1, len(self.deletes()))

    def test_uncertain_post_followed_by_foreign_owner_not_deleted(self):
        self.client.post_failure = TimeoutError("mock lost response")
        with self.assertRaises(TimeoutError):
            self.client.renew_if_due()
        self.client.state["reservation"]["owner"]["pid"] += 1
        self.assertFalse(self.client.release()["released"])
        self.assertEqual([], self.deletes())

    def test_normal_release(self):
        self.assertTrue(self.client.release()["released"])
        self.assertIsNone(self.client.request_id)

    def test_release_foreign_id_without_own_uncertainty_refused(self):
        self.client.state["reservation"]["request_id"] = "foreign"
        self.assertFalse(self.client.release()["released"])
        self.assertEqual([], self.deletes())

    def test_get_uncertain_release_receipts_no_delete(self):
        self.client.get_failure = TimeoutError("mock no status")
        result = self.client.release()
        self.assertFalse(result["released"])
        self.assertTrue(result["outcome_uncertain"])
        self.assertEqual([], self.deletes())

    def test_execution_changed_stops_before_post(self):
        self.client.state["completed_scopes"] += 1
        with self.assertRaisesRegex(RuntimeError, "EXECUTION"):
            self.client.renew_if_due()
        self.assertEqual([], self.posts())

    def test_invalid_expiry_stops_before_post(self):
        for expiry in (None, float("nan"), float("inf"), True, time.time()-2):
            self.client.state["reservation"]["expires_unix"] = expiry
            with self.assertRaisesRegex(RuntimeError, "EXPIRY"):
                self.client.renew_if_due()
        self.assertEqual([], self.posts())

    def test_bad_renew_expiry_stops_and_cleanup(self):
        self.client.bad_response = lambda r: r["reservation"].update(
            expires_unix=time.time() + 7200)
        with self.assertRaisesRegex(RuntimeError, "TTL"):
            self.client.renew_if_due()
        self.assertTrue(self.client.release()["released"])

    def test_owner_argument_mismatch_does_not_post(self):
        with self.assertRaisesRegex(RuntimeError, "CALLER"):
            self.client.renew_if_due(os.getpid() + 1)
        self.assertEqual([], self.posts())

    def test_uncertain_renew_not_retried(self):
        self.client.post_failure = TimeoutError("lost")
        with self.assertRaises(TimeoutError):
            self.client.renew_if_due()
        with self.assertRaisesRegex(RuntimeError, "UNCERTAIN"):
            self.client.renew_if_due()
        self.assertEqual(1, len(self.posts()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
