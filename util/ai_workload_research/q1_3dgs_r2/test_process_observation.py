"""CPU mocks for own-process observation; zero GPU, locks, APIs or signals."""
from types import SimpleNamespace
import unittest

from process_observation import observe_processes, enforce_observation
from resource_monitor import MonitorStop


class NoSuchProcess(Exception):
    pass


class AccessDenied(Exception):
    pass


class FakeProcess:
    def __init__(self, owner, pid):
        self.owner, self.pid = owner, pid

    def create_time(self):
        item = self.owner.data[self.pid]
        if item.get("denied"):
            raise AccessDenied("identity denied")
        return item.get("birth", 1.0)

    def status(self):
        item = self.owner.data[self.pid]
        if item.get("status_denied"):
            raise AccessDenied("status denied")
        return item.get("status", "sleeping")

    def is_running(self):
        return self.owner.data[self.pid].get("running", True)


class FakePs:
    NoSuchProcess = NoSuchProcess
    AccessDenied = AccessDenied

    def __init__(self):
        self.data = {pid: {} for pid in [10, 20, 30]}

    def Process(self, pid):
        if pid not in self.data or self.data[pid].get("absent"):
            raise NoSuchProcess(str(pid))
        return FakeProcess(self, pid)

    def pid_exists(self, pid):
        return pid in self.data and not self.data[pid].get("absent")


class ProcessObservationTests(unittest.TestCase):
    def setUp(self):
        self.ps = FakePs()
        self.ids = {10: 1.0, 20: 1.0, 30: 1.0}
        self.row = {
            "live_own_pids": [10, 20, 30],
            "rss_observed_processes": [
                {"pid": p, "creation_time": 1.0, "rss_bytes": 1000}
                for p in self.ids],
            "monitor_gaps": [], "unknown_gpu_pids": [], "invalid_pid_rows": [],
        }
        self.stat_calls = {}
        self.affinity_map = {10: {22, 23}, 20: {0, 2}, 30: {0, 2}}

    def read(self, pid, member):
        item = self.ps.data.get(pid, {"absent": True})
        if item.get("proc_denied"):
            raise AccessDenied("proc denied")
        if item.get("absent") and not item.get("proc_present"):
            raise FileNotFoundError(str(pid))
        state = item.get("proc_state", "S")
        if member == "stat":
            count = self.stat_calls.get(pid, 0)
            self.stat_calls[pid] = count + 1
            ticks = item.get("ticks", pid*100)
            if item.get("tick_reuse") and count:
                ticks += 1
            tail = [state] + ["0"] * 18 + [str(ticks)]
            return str(pid) + " (test (nested) comm) " + " ".join(tail)
        if member == "status":
            if item.get("transition_on_status"):
                item.update(status="zombie", proc_state="Z", status_state="Z")
                state = "Z"
            text = "State: " + item.get("status_state", state) + " (test)\n"
            if not item.get("missing_swap"):
                text += "VmSwap: " + item.get("swap_text", str(pid) + " kB") + "\n"
            return text
        raise ValueError(member)

    def observe(self, **kwargs):
        return observe_processes(
            self.ps, self.row, self.ids, 10, 20, {0, 2, 4},
            supervisor_affinity={22, 23}, proc_read=self.read,
            task_ids=lambda pid: [pid],
            affinity_get=lambda tid: self.affinity_map[tid], **kwargs)

    def assert_stop(self, result):
        with self.assertRaises(MonitorStop):
            enforce_observation(result)

    def terminal(self, pid=30):
        self.ps.data[pid].update(
            missing_swap=True, status="zombie", proc_state="Z", status_state="Z")

    def test_nonzero_worker_zombie_and_disappeared_children_remain_fatal(self):
        self.ps.data[20].update(missing_swap=True,status="zombie",proc_state="Z",status_state="Z")
        self.ps.data[30]["absent"]=True
        result=self.observe(normal_worker_exit={"pid":20,"creation_time":1.0,"returncode":1})
        self.assert_stop(result)
        self.assertIn("WORKER_NOT_HEALTHY_OR_VERIFIED_NORMAL_EXIT",result["gaps"])
        self.assertIn("MISSING_VMSWAP_NOT_SAFELY_CENSORED:20",result["gaps"])
        self.assertIn("MISSING_VMSWAP_NOT_SAFELY_CENSORED:30",result["gaps"])
        self.assertEqual(result["censored"],[])
        self.assertIsNone(result["process_observations"][1]["VmSwap_bytes"])
        self.assertTrue(result["process_observations"][2]["disappearance_proof"]["proc_stat_absent_2"])

    def test_normal_live_swap_and_affinity(self):
        result = self.observe()
        enforce_observation(result)
        self.assertEqual(result["observed_live_VmSwap_subtotal_bytes"], 60*1024)
        self.assertTrue(result["swap_observation_complete"])
        self.assertEqual(len(result["process_observations"]), 3)
        self.assertEqual(result["censored"], [])

    def test_missing_swap_alive_is_gap_not_zero(self):
        self.ps.data[30]["missing_swap"] = True
        result = self.observe()
        self.assert_stop(result)
        self.assertIsNone(result["process_observations"][2]["VmSwap_bytes"])
        self.assertEqual(result["observed_live_VmSwap_subtotal_bytes"], 30*1024)
        self.assertEqual(result["censored"], [])

    def test_missing_swap_confirmed_zombie_is_censored(self):
        self.terminal()
        result = self.observe()
        enforce_observation(result)
        self.assertEqual(result["censored"][0]["VmSwap_bytes"], None)
        self.assertEqual(result["censored"][0]["reason"], "confirmed_terminal_no_mm")
        self.assertTrue(result["censored"][0]["not_an_RSS_race_classification"])
        self.assertTrue(result["censored"][0]["qualification_valid"])
        self.assertFalse(result["swap_observation_complete"])
        self.assertEqual(result["observed_live_VmSwap_subtotal_bytes"], 30*1024)

    def test_transition_to_zombie_is_independently_rechecked(self):
        self.ps.data[30].update(missing_swap=True, transition_on_status=True)
        result = self.observe()
        enforce_observation(result)
        observation = result["process_observations"][2]
        self.assertEqual(observation["before"]["proc_stat"]["state"], "S")
        self.assertEqual(observation["after"]["proc_stat"]["state"], "Z")
        self.assertEqual(observation["terminal_recheck"]["proc_stat"]["state"], "Z")
        self.assertTrue(result["censored"][0]["qualification_valid"])

    def test_double_disappearance_is_censored_and_proofs_retained(self):
        self.ps.data[30]["absent"] = True
        result = self.observe()
        enforce_observation(result)
        proof = result["process_observations"][2]["disappearance_proof"]
        self.assertFalse(proof["pid_exists_recheck"])
        self.assertTrue(proof["fresh_Process_NoSuchProcess"])
        self.assertTrue(proof["proc_stat_absent_1"])
        self.assertTrue(proof["proc_stat_absent_2"])
        self.assertEqual(result["censored"][0]["reason"], "double_confirmed_disappearance")

    def test_missing_field_inconsistent_zombie_state_stops(self):
        self.terminal()
        self.ps.data[30]["status"] = "sleeping"
        result = self.observe()
        self.assert_stop(result)
        self.assertEqual(result["censored"], [])

    def test_abnormal_worker_exit_blocks_censorship(self):
        self.ps.data[20]["absent"] = True
        self.terminal()
        result = self.observe(normal_worker_exit={"pid": 20, "creation_time": 1.0,
                                                 "returncode": 3})
        self.assert_stop(result)
        self.assertEqual(result["censored"], [])

    def test_verified_normal_worker_exit_can_support_censorship(self):
        self.ps.data[20]["absent"] = True
        self.terminal()
        result = self.observe(normal_worker_exit={"pid": 20, "creation_time": 1.0,
                                                 "returncode": 0})
        enforce_observation(result)
        self.assertEqual([item["pid"] for item in result["censored"]], [20, 30])
        self.assertTrue(result["worker_health_or_verified_normal_exit"]["normal_exit_verified"])

    def test_unproven_normal_exit_is_rejected(self):
        self.ps.data[20]["absent"] = True
        self.terminal()
        result = self.observe(normal_worker_exit={"pid": 20, "creation_time": 999.0,
                                                 "returncode": 0})
        self.assert_stop(result)

    def test_worker_pid_reuse_does_not_count_as_normal_exit(self):
        self.ps.data[20]["birth"] = 2.0
        self.terminal()
        result = self.observe(normal_worker_exit={"pid": 20, "creation_time": 1.0,
                                                 "returncode": 0})
        self.assert_stop(result)
        self.assertEqual(result["censored"], [])

    def test_child_pid_reuse_is_gap(self):
        self.ps.data[30]["birth"] = 2.0
        result = self.observe()
        self.assert_stop(result)
        self.assertIn("PID_REUSE", result["process_observations"][2]["gap"])

    def test_proc_start_ticks_change_is_gap(self):
        self.ps.data[30]["tick_reuse"] = True
        result = self.observe()
        self.assert_stop(result)
        self.assertIn("PID_REUSE", result["process_observations"][2]["gap"])

    def test_access_denied_is_not_censored(self):
        self.ps.data[30]["denied"] = True
        result = self.observe()
        self.assert_stop(result)
        self.assertIn("AccessDenied", result["process_observations"][2]["gap"])
        self.assertEqual(result["censored"], [])

    def test_proc_access_denied_is_not_censored(self):
        self.ps.data[30]["proc_denied"] = True
        result = self.observe()
        self.assert_stop(result)

    def test_unenumerated_pid_is_not_owned_by_whitelist(self):
        self.row["rss_observed_processes"] = self.row["rss_observed_processes"][:2]
        self.ps.data[30]["absent"] = True
        result = self.observe()
        self.assert_stop(result)
        self.assertEqual(result["process_observations"][2]["gap"],
                         "PID_NOT_VALID_CURRENT_OWN_ENUMERATION")

    def test_prior_independent_monitor_gap_blocks_censorship(self):
        self.terminal()
        self.row["monitor_gaps"] = ["RSS_PID_99:AccessDenied"]
        result = self.observe()
        self.assert_stop(result)
        self.assertEqual(result["censored"], [])

    def test_later_independent_failure_invalidates_candidate(self):
        self.terminal()
        self.ids[40] = 1.0
        self.ps.data[40] = {"denied": True}
        self.row["live_own_pids"].append(40)
        self.row["rss_observed_processes"].append(
            {"pid": 40, "creation_time": 1.0, "rss_bytes": 1000})
        result = self.observe()
        self.assert_stop(result)
        self.assertEqual(len(result["censored"]), 1)
        self.assertFalse(result["censored"][0]["qualification_valid"])

    def test_unknown_gpu_observation_blocks_censorship(self):
        self.terminal()
        self.row["unknown_gpu_pids"] = [7777]
        result = self.observe()
        self.assert_stop(result)
        self.assertEqual(result["censored"], [])

    def test_child_affinity_violation(self):
        self.affinity_map[30] = {0, 99}
        result = self.observe()
        self.assert_stop(result)
        self.assertEqual(result["affinity_violations"],
                         [{"pid": 30, "tid": 30, "CPUs": [0, 99]}])

    def test_supervisor_affinity_violation(self):
        self.affinity_map[10] = {0, 22, 23}
        result = self.observe()
        self.assert_stop(result)
        self.assertEqual(result["affinity_violations"][0]["pid"], 10)

    def test_thread_disappearance_during_affinity_is_gap(self):
        def disappeared(tid):
            if tid == 30:
                raise ProcessLookupError("thread ended")
            return self.affinity_map[tid]
        result = observe_processes(
            self.ps, self.row, self.ids, 10, 20, {0, 2, 4},
            supervisor_affinity={22, 23}, proc_read=self.read,
            task_ids=lambda pid: [pid], affinity_get=disappeared)
        self.assert_stop(result)

    def test_partial_observation_retained_after_malformed_swap(self):
        self.ps.data[30]["swap_text"] = "oops kB"
        result = self.observe()
        self.assert_stop(result)
        self.assertEqual(result["observed_live_VmSwap_subtotal_bytes"], 30*1024)
        self.assertEqual(len(result["process_observations"]), 3)
        self.assertIsNotNone(result["process_observations"][2]["before"])

    def test_false_absence_when_actual_proc_exists_stops(self):
        self.ps.data[30].update(absent=True, proc_present=True)
        result = self.observe()
        self.assert_stop(result)
        self.assertEqual(result["censored"], [])

    def test_root_disappearance_is_never_censored(self):
        self.ps.data[10]["absent"] = True
        result = self.observe()
        self.assert_stop(result)
        self.assertTrue(any("ROOT_NOT_HEALTHY" in gap for gap in result["gaps"]))
        self.assertFalse(any(item["pid"] == 10 for item in result["censored"]))

    def test_rss_values_are_not_modified_or_reclassified(self):
        before = repr(self.row)
        self.terminal()
        self.observe()
        self.assertEqual(repr(self.row), before)

    def test_non_kilobyte_swap_unit_is_gap(self):
        self.ps.data[30]["swap_text"] = "1 MB"
        self.assert_stop(self.observe())


if __name__ == "__main__":
    unittest.main(verbosity=2)
