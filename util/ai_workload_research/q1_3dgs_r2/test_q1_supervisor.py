"""CPU mocks of Q1 supervisor; no real NVML, flock, service API or child launch."""
import copy
import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, patch

import q1_supervisor as q
from resource_monitor import MonitorStop

GIB = 1024**3
MIB = 1024**2


class SupervisorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="q1-supervisor-cpu-")
        self.path = Path(self.tmp.name)
        (self.path / "raw").mkdir()
        (self.path / ".private").mkdir()
        self.cg = self.path / "own_cgroup"
        self.cg.mkdir()
        self.lock = self.path / "MOCK_LOCK_ONLY"
        self.lock.write_text("")
        self.cfg = dict(out=str(self.path), root=str(self.path),
                        lock=str(self.lock), author_assets="/FAKE_ASSETS",
                        goal_start_epoch=950, training_affinity=[0, 2, 4, 6],
                        supervisor_affinity=[22, 23], own_vram_bytes_max=14336*MIB,
                        rss_bytes_max=40*GIB, charged_bytes_max=48*GIB,
                        disk_bytes_max=64*GIB, free_bytes_min=32*GIB,
                        held_seconds_max=10800, shutdown_reserve_seconds=60,
                        goal_seconds_max=28800, UUID="MOCK-4080",
                        monitor_seconds=0)
        self.obj = q.Q1Supervisor.__new__(q.Q1Supervisor)
        self.obj.cfg = self.cfg
        self.obj.out = self.path
        self.obj.owned = {os.getpid()}
        self.obj.child = None
        self.obj.lock = None
        self.obj.held = 50
        self.obj.handle = "MOCK_HANDLE"
        nv = Mock()
        nv.nvmlDeviceGetHandleByUUID.return_value = "MOCK_HANDLE"
        nv.nvmlDeviceGetName.return_value = b"NVIDIA GeForce RTX 4080"
        nv.nvmlDeviceGetUUID.return_value = b"MOCK-4080"
        self.obj.s = SimpleNamespace(nv=nv, ps=Mock(), pid=os.getpid())
        self.obj.lifecycle = Mock()
        self.obj.lifecycle.identities={424242:1.0}
        self.obj.s.ps.NoSuchProcess=ProcessLookupError
        self.obj.s.ps.pid_exists.return_value=False
        self.obj.s.ps.Process.side_effect=ProcessLookupError("mock absent")
        nv.nvmlDeviceGetComputeRunningProcesses.return_value=[]
        nv.nvmlDeviceGetGraphicsRunningProcesses.return_value=[]
        self.obj.shared = Mock()
        self.obj.shared.lease_events = []
        self.obj.shared.reserve.return_value = {"request_id": "MOCK"}
        self.obj.shared.release.return_value = {"released": True}
        self.obj.shared.check.side_effect = lambda row: dict(row, shared_gate={"verified": True})
        self.obj.session_memory = SimpleNamespace(
            path=self.cg, read=Mock(return_value={
                "current_bytes": 1*GIB, "kernel_charged_peak_bytes": 2*GIB}))
        self.obj.disk = Mock(return_value=123)
        self.obj.disk_last = 0
        self.obj.disk_value = 0
        self.obj.r = dict(status="PRELOCK", lock_attempt_count=0,
                          lock_acquired=False, lock_released=False,
                          reservation_created=False, NVML_initialized=False,
                          jobs=[], monitor_gaps=[], samples_count=0,
                          peak_own_NVML_bytes=0, peak_sampled_RSS_bytes=0,
                          peak_charged_bytes=0, worker_launches=0)
        self.row = dict(phase="WORKER", own_NVML_bytes=100*MIB,
                        own_tree_RSS_bytes=1*GIB, own_new_disk_bytes=123,
                        held_seconds=50, goal_elapsed_seconds=50,
                        unknown_gpu_pids=[], invalid_pid_rows=[], monitor_gaps=[],
                        external_gpu_pids=[], unqualified_external_gpu_pids=[],
                        gpu_processes=[], live_own_pids=[os.getpid()])
        self._read_text = Path.read_text
        def fake_read_text(path, *args, **kwargs):
            if str(path) == "/proc/meminfo":
                return "MemAvailable: 104857600 kB\n"
            if str(path).startswith("/proc/") and str(path).endswith("/status"):
                return "VmSwap: %d kB\n" % self.swap_kib
            return self._read_text(path, *args, **kwargs)
        self.swap_kib = 0
        def legal_process_observation(ps, row, identities, root, worker, training, **kwargs):
            violations = []
            for pid in row["live_own_pids"]:
                if pid != root:
                    allowed = q.os.sched_getaffinity(pid)
                    if not set(allowed).issubset(set(training)):
                        violations.append({"pid": pid, "tid": pid, "CPUs": sorted(allowed)})
            return dict(observed_live_VmSwap_subtotal_bytes=self.swap_kib*1024,
                        censored=[], affinity_violations=violations, gaps=[],
                        process_observations=[], swap_observation_complete=True)
        self.patches = [
            patch.object(q, "observe_processes", side_effect=legal_process_observation),
            patch.object(q, "collect_snapshot", side_effect=lambda *a, **k: copy.deepcopy(self.row)),
            patch.object(q, "apply_desktop_policy", side_effect=lambda row, cfg: row),
            patch.object(q, "runtime_activity"),
            patch.object(q, "finalize_races"),
            patch.object(q.shutil, "disk_usage", return_value=SimpleNamespace(free=100*GIB)),
            patch.object(q.time, "time", return_value=1000),
            patch.object(q.time, "monotonic", return_value=100),
            patch.object(q.time, "sleep"),
            patch.object(Path, "read_text", new=fake_read_text),
            patch.object(q.os, "sched_setaffinity"),
            patch.object(q.os, "sched_getaffinity", return_value={0, 2, 4, 6}),
        ]
        self.started = [p.start() for p in self.patches]

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.tmp.cleanup()

    def snapshot(self):
        return self.obj.snapshot("WORKER")

    def expect_stop(self, fragment=None):
        with self.assertRaises(MonitorStop) as raised:
            self.snapshot()
        if fragment:
            self.assertIn(fragment, str(raised.exception))
        return raised.exception

    def test_missing_live_swap_helper_gap_is_persisted_then_stops(self):
        failure = dict(observed_live_VmSwap_subtotal_bytes=12,
                       censored=[], affinity_violations=[],
                       gaps=["MISSING_VMSWAP_NOT_SAFELY_CENSORED:999999"],
                       process_observations=[{"pid": 999999, "VmSwap_bytes": None,
                                              "gap": "missing while live"}],
                       swap_observation_complete=False)
        q.observe_processes.side_effect = lambda *a, **k: failure
        self.expect_stop("VmSwap/identity observation gap")
        records = (self.path / "raw/RESOURCE_SAMPLES.jsonl").read_text().splitlines()
        saved = json.loads(records[-1])["own_process_observation"]
        self.assertEqual(saved["gaps"], failure["gaps"])
        self.assertIsNone(saved["process_observations"][0]["VmSwap_bytes"])
        self.assertFalse(self.obj.r["latest_snapshot"]["own_VmSwap_observation_complete"])

    def test_censored_swap_with_independent_gap_is_not_accepted(self):
        self.row["monitor_gaps"] = ["RSS_PID_999:AccessDenied"]
        failure = dict(
            observed_live_VmSwap_subtotal_bytes=17,
            censored=[{"pid": 999999, "VmSwap_bytes": None, "qualification_valid": False}],
            affinity_violations=[],
            gaps=["INDEPENDENT_MONITOR_GAP:RSS_PID_999:AccessDenied"],
            process_observations=[], swap_observation_complete=False)
        q.observe_processes.side_effect = lambda *a, **k: failure
        self.expect_stop("VmSwap/identity observation gap")
        saved = self.obj.r["latest_snapshot"]
        self.assertEqual(saved["own_VmSwap_bytes"], 17)
        self.assertIsNone(saved["own_VmSwap_censored"][0]["VmSwap_bytes"])
        self.assertFalse(saved["own_VmSwap_censored"][0]["qualification_valid"])
        records = (self.path / "raw/RESOURCE_SAMPLES.jsonl").read_text().splitlines()
        self.assertEqual(json.loads(records[-1])["monitor_gaps"],
                         ["RSS_PID_999:AccessDenied"])

    def test_disk_collection_failure_persists_partial(self):
        q.shutil.disk_usage.side_effect=OSError("disk observation missing")
        with self.assertRaises(OSError):self.snapshot()
        self.assertIn("disk observation",self.obj.r["latest_snapshot"]["field_collection_error"])
        self.assertTrue((self.path/"raw/RESOURCE_SAMPLES.jsonl").is_file())

    def test_helper_unexpected_failure_persists_partial(self):
        q.observe_processes.side_effect=ValueError("invalid status")
        with self.assertRaises(ValueError):self.snapshot()
        self.assertIn("invalid status",self.obj.r["latest_snapshot"]["field_collection_error"])

    def test_retirement_rejects_still_existing_pid(self):
        self.obj.child=self._mock_child()
        self.obj.s.ps.pid_exists.return_value=True
        with self.assertRaisesRegex(MonitorStop,"PID still exists"):self.obj.retire_finished_worker()
        self.assertFalse(getattr(self.obj,"inactive_child_verified",False))

    def test_retirement_preserves_nonzero_exit_and_clears_only_active_expectation(self):
        self.obj.child=self._mock_child(returncode=7)
        proof=self.obj.retire_finished_worker()
        self.assertEqual(proof["returncode"],7)
        self.assertIsNone(self.obj.lifecycle.worker)
        self.assertTrue(self.obj.inactive_child_verified)
        self.assertEqual(self.obj.child.returncode,7)

    def test_retirement_requires_recorded_creation_identity(self):
        self.obj.child=self._mock_child()
        self.obj.lifecycle.identities={}
        with self.assertRaisesRegex(MonitorStop,"identity/exit"):self.obj.retire_finished_worker()

    def test_nonzero_exit_during_active_sample_never_uses_normal_exit_bypass(self):
        child=self._mock_child(returncode=1,polls=[None,1])
        failed=dict(self.row,monitor_gaps=[],own_process_observation={
            "gaps":["WORKER_NOT_HEALTHY_OR_VERIFIED_NORMAL_EXIT",
                    "MISSING_VMSWAP_NOT_SAFELY_CENSORED:"+str(child.pid)]})
        calls=[]
        def samples(phase,**kwargs):
            calls.append(phase)
            self.obj.last_attempt=failed
            raise MonitorStop("RESOURCE_STOP","Own process VmSwap/identity observation gap")
        with self.assertRaises(MonitorStop):
            self._launch(self._job("nonzero_during_active"),child,samples)
        self.assertEqual(calls,["WORKER"])
        self.assertFalse(getattr(self.obj,"inactive_child_verified",False))
        self.assertNotIn("normal_exit_during_phase_sample",self.obj.r["jobs"][-1])

    def test_valid_snapshot_persists_complete_observation(self):
        result = self.snapshot()
        self.assertEqual(result["session_memory"]["kernel_charged_peak_bytes"], 2*GIB)
        self.assertEqual(self.obj.r["samples_count"], 1)
        records = (self.path / "raw/RESOURCE_SAMPLES.jsonl").read_text().splitlines()
        self.assertEqual(len(records), 1)
        self.assertEqual(json.loads(records[0])["own_tree_RSS_bytes"], GIB)

    def test_rss_40gib_boundary_and_violation(self):
        self.row["own_tree_RSS_bytes"] = 40*GIB
        self.snapshot()
        self.row["own_tree_RSS_bytes"] += 1
        self.expect_stop("own_tree_RSS_bytes")

    def test_charged_current_48gib_boundary_and_violation(self):
        self.obj.session_memory.read.return_value = {
            "current_bytes": 48*GIB, "kernel_charged_peak_bytes": 48*GIB}
        self.snapshot()
        self.obj.session_memory.read.return_value["current_bytes"] += 1
        self.expect_stop("charged-memory")

    def test_charged_kernel_peak_cannot_be_hidden_by_lower_current(self):
        self.obj.session_memory.read.return_value = {
            "current_bytes": GIB, "kernel_charged_peak_bytes": 48*GIB+1}
        self.expect_stop("charged-memory")

    def test_disk_32gib_reserve_boundary_and_violation(self):
        q.shutil.disk_usage.return_value = SimpleNamespace(free=32*GIB)
        self.snapshot()
        q.shutil.disk_usage.return_value = SimpleNamespace(free=32*GIB-1)
        self.expect_stop("reserve below32GiB")

    def test_swap_64mib_boundary_and_violation(self):
        self.swap_kib = 64*1024
        self.snapshot()
        self.swap_kib += 1
        self.expect_stop("VmSwap")

    def test_unknown_compute_is_not_swallowed(self):
        self.row["unknown_gpu_pids"] = [2345]
        self.expect_stop("Unknown GPU")

    def test_monitor_gap_is_not_swallowed(self):
        self.row["monitor_gaps"] = ["RSS_PID_7:AccessDenied"]
        self.expect_stop("incomplete resource")

    def test_gpu_vram_over_limit_stops(self):
        self.row["own_NVML_bytes"] = self.cfg["own_vram_bytes_max"]+1
        self.expect_stop("own_NVML_bytes")

    def test_new_disk_budget_still_enforced(self):
        self.row["own_new_disk_bytes"] = 64*GIB+1
        self.expect_stop("own_new_disk_bytes")

    def test_uncovered_child_cgroup_stops(self):
        (self.cg / "unexpected").mkdir()
        self.expect_stop("delegated child cgroup")

    def test_gate_failure_stops_even_if_other_resources_valid(self):
        self.obj.shared.check.side_effect = RuntimeError("changed incarnation")
        self.expect_stop("Shared gate")

    def test_failed_sample_is_retained_for_resource_stop(self):
        self.row["own_tree_RSS_bytes"] = 40*GIB+1
        self.expect_stop()
        records = (self.path / "raw/RESOURCE_SAMPLES.jsonl").read_text().splitlines()
        self.assertEqual(json.loads(records[-1])["own_tree_RSS_bytes"], 40*GIB+1)

    def test_affinity_violation_stops_owned_worker_thread(self):
        self.row["live_own_pids"].append(999999)
        original = Path.iterdir
        def fake_iterdir(path):
            if str(path) == "/proc/999999/task":
                return iter([Path("/proc/999999/task/999999")])
            return original(path)
        with patch.object(Path, "iterdir", new=fake_iterdir), \
                patch.object(q.os, "sched_getaffinity", return_value={0, 2, 55}):
            self.expect_stop("CPU")

    def _dispatcher_stop(self):
        (self.path / ".private/DISPATCH.jsonl").write_text('{"action":"STOP"}\n')
        self.obj.held = None
        self.obj.handle = None

    def test_one_nonblocking_lock_conflict_releases_reservation(self):
        self._dispatcher_stop()
        def conflict(fd, mode):
            raise BlockingIOError("mock conflict")
        with patch.object(q.fcntl, "flock", side_effect=conflict) as flock:
            result = self.obj.run()
        self.assertEqual(flock.call_count, 1)
        self.assertEqual(flock.call_args.args[1], q.fcntl.LOCK_EX|q.fcntl.LOCK_NB)
        self.assertEqual(result["lock_attempt_count"], 1)
        self.assertFalse(result["lock_acquired"])
        self.obj.shared.release.assert_called_once()
        self.obj.s.nv.nvmlInit.assert_not_called()

    def test_final_observation_error_still_unlocks_and_releases(self):
        self._dispatcher_stop()
        self.obj.snapshot = Mock(side_effect=[self.row, RuntimeError("mock final gap")])
        with patch.object(q.fcntl, "flock") as flock, \
                patch.object(q, "admit_low_activity"):
            result = self.obj.run()
        self.assertEqual([c.args[1] for c in flock.call_args_list],
                         [q.fcntl.LOCK_EX|q.fcntl.LOCK_NB, q.fcntl.LOCK_UN])
        self.assertTrue(result["lock_released"])
        self.assertIn("final gap", result["cleanup_observation_error"])
        self.obj.shared.release.assert_called_once()
        self.obj.s.nv.nvmlShutdown.assert_called_once()

    def test_unlock_error_still_closes_descriptor_and_releases_reservation(self):
        self._dispatcher_stop()
        self.obj.snapshot = Mock(return_value=self.row)
        def flock_failure(fd, mode):
            if mode == q.fcntl.LOCK_UN:
                raise OSError("mock unlock error")
        with patch.object(q.fcntl, "flock", side_effect=flock_failure), \
                patch.object(q, "admit_low_activity"):
            result = self.obj.run()
        self.assertTrue(self.obj.lock.closed)
        self.obj.shared.release.assert_called_once()
        self.assertEqual(result["reservation_cleanup"], {"released": True})
        self.assertTrue((self.path / "RESOURCE_RECEIPT.json").is_file())

    def test_supervisor_affinity_is_bound_before_reservation(self):
        self._dispatcher_stop()
        self.obj.snapshot = Mock(return_value=self.row)
        with patch.object(q.fcntl, "flock"), patch.object(q, "admit_low_activity"):
            self.obj.run()
        q.os.sched_setaffinity.assert_called_once_with(0, {22, 23})
        self.obj.shared.reserve.assert_called_once()

    def _job(self, identifier):
        return {"id": identifier, "OMP_cap": 8}

    def _mock_child(self, returncode=0, polls=None):
        child = Mock(pid=424242, returncode=returncode)
        pending=list(polls or [])
        child.poll.side_effect=lambda: pending.pop(0) if pending else returncode
        return child

    def _launch(self, job, child, snapshots):
        with patch.object(q.subprocess, "Popen", return_value=child) as popen, \
                patch.object(q, "identity", return_value={"pid": child.pid}), \
                patch.object(self.obj, "snapshot", side_effect=snapshots):
            record = self.obj.run_job(job)
        return record, popen

    def test_launch_uses_taskset_training_subset_and_frozen_omp_cap(self):
        child = self._mock_child()
        self.obj.r["latest_snapshot"] = self.row
        record, popen = self._launch(self._job("affinity"), child, [self.row])
        command = popen.call_args.args[0]
        self.assertEqual(command[:3], ["taskset", "-c", "0,2,4,6"])
        self.assertTrue(popen.call_args.kwargs["start_new_session"])
        self.assertEqual(popen.call_args.kwargs["env"]["OMP_THREAD_LIMIT"], "8")
        self.assertEqual(popen.call_args.kwargs["env"]["Q1_LOCK_OWNER_PID"], str(os.getpid()))
        self.obj.lifecycle.bind_worker.assert_called_once_with(child.pid)
        self.assertEqual(record["returncode"], 0)

    def test_abnormal_worker_exit_is_not_marked_success(self):
        child = self._mock_child(returncode=7)
        self.obj.r["latest_snapshot"] = self.row
        record, _ = self._launch(self._job("failed"), child, [self.row])
        self.assertEqual(record["returncode"], 7)
        self.assertEqual(self.obj.r["status"], "JOB_FAILED_ENGINEERING_DECISION_PENDING")

    def test_completed_worker_cuda_context_must_clear(self):
        child = self._mock_child()
        self.obj.r["latest_snapshot"] = dict(self.row, gpu_processes=[{"pid": child.pid}])
        self.obj.s.nv.nvmlDeviceGetComputeRunningProcesses.return_value=[SimpleNamespace(pid=child.pid)]
        with self.assertRaisesRegex(MonitorStop, "context not cleared"):
            self._launch(self._job("context"), child, [self.row])

    def _exit_race(self, gap, reason, extra_unknown=False):
        child = self._mock_child(polls=[None, 0])
        failure = MonitorStop("GPU_RESOURCE_DEFERRED", reason)
        def snapshots(phase, **kwargs):
            if phase == "WORKER":
                failed = dict(
                    self.row, monitor_gaps=gap,
                    unknown_gpu_pids=[2345] if extra_unknown else [],
                    session_memory={"current_bytes": GIB, "kernel_charged_peak_bytes": 2*GIB},
                    filesystem_available_bytes=100*GIB, MemAvailable_bytes=100*GIB,
                    own_VmSwap_bytes=0)
                self.obj.r["latest_snapshot"] = failed
                self.obj.last_attempt = failed
                raise failure
            self.obj.r["latest_snapshot"] = self.row
            return self.row
        return child, snapshots

    def test_known_normal_exit_health_label_allows_recollection(self):
        child, samples = self._exit_race(
            ["OWNER_HEALTH:NoSuchProcess"], "Unknown GPU PID/memory or incomplete resource observation")
        record, _ = self._launch(self._job("normalexit"), child, samples)
        self.assertTrue(record["normal_exit_during_phase_sample"])

    def test_normal_exit_does_not_hide_unknown_gpu_pid(self):
        child, samples = self._exit_race(
            ["OWNER_HEALTH:NoSuchProcess"], "Unknown GPU PID/memory or incomplete resource observation", True)
        with self.assertRaises(MonitorStop):
            self._launch(self._job("unknownexit"), child, samples)

    def test_normal_exit_does_not_hide_access_denied_gap(self):
        child, samples = self._exit_race(
            ["RSS_PID_7:AccessDenied"], "Unknown GPU PID/memory or incomplete resource observation")
        with self.assertRaises(MonitorStop):
            self._launch(self._job("accessdeniedexit"), child, samples)

    def test_normal_exit_does_not_hide_resource_limit(self):
        child, samples = self._exit_race([], "Resource limit: own_tree_RSS_bytes")
        with self.assertRaises(MonitorStop):
            self._launch(self._job("rss_exit"), child, samples)

    def test_normal_exit_health_gap_plus_real_rss_violation_still_stops(self):
        self.row["own_tree_RSS_bytes"] = 40*GIB+1
        child, samples = self._exit_race(
            ["OWNER_HEALTH:NoSuchProcess"], "Unknown GPU PID/memory or incomplete resource observation")
        with self.assertRaises(MonitorStop):
            self._launch(self._job("mixed_rss_exit"), child, samples)

    def test_cleanup_remaining_own_context_marks_resource_stop(self):
        self._dispatcher_stop()
        ownrow = dict(self.row, gpu_processes=[{"pid": os.getpid()}])
        self.obj.snapshot = Mock(side_effect=[self.row]+[ownrow]*11)
        with patch.object(q.fcntl, "flock"), patch.object(q, "admit_low_activity"):
            result = self.obj.run()
        self.assertFalse(result["own_GPU_contexts_cleared"])
        self.assertEqual(result["status"], "RESOURCE_STOP")
        self.assertTrue(result["lock_released"])
        self.obj.shared.release.assert_called_once()

    def test_stop_own_times_out_then_signals_only_owned_group(self):
        child = self._mock_child(polls=[None])
        child.wait.side_effect = [q.subprocess.TimeoutExpired("mock", 3), 0]
        self.obj.child = child
        with patch.object(q.os, "killpg") as signal_group:
            self.obj.stop_own()
        self.assertEqual([c.args for c in signal_group.call_args_list],
                         [(child.pid, q.signal.SIGTERM), (child.pid, q.signal.SIGKILL)])
        self.assertEqual(child.wait.call_count, 2)

    def test_unrelated_runtime_activity_failure_is_not_ignored(self):
        q.runtime_activity.side_effect = MonitorStop("GPU_RESOURCE_DEFERRED", "new external activity")
        self.expect_stop("new external activity")

    def test_inherited_desktop_attribution_gap_is_explicitly_recorded(self):
        q.runtime_activity.side_effect = MonitorStop(
            "GPU_RESOURCE_DEFERRED", "Desktop activity attribution unavailable during own work")
        self.snapshot()
        self.assertIn("Inherited gap", self.obj.r["desktop_per_process_activity_gap"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
