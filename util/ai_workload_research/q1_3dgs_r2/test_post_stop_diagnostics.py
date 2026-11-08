"""PostSTOP CPU-only diagnostics/cleanup tests, no new thread-exit permission."""
import os
os.sched_setaffinity(0,{22,23})
import unittest
from unittest.mock import patch
from test_q1_supervisor import SupervisorTests
from test_process_observation import ProcessObservationTests
from process_observation import observe_processes
class ThreadGap(ProcessObservationTests):
    def test_healthy_worker_departed_TID_is_recorded_but_still_stops(self):
        def aff(tid):
            if tid==777:raise ProcessLookupError("injected departed thread")
            return self.affinity_map[tid]
        x=observe_processes(self.ps,self.row,self.ids,10,20,{0,2,4},
            supervisor_affinity={22,23},proc_read=self.read,
            task_ids=lambda pid:[pid,777] if pid==20 else [pid],affinity_get=aff)
        failed=next(p for p in x["process_observations"] if p["pid"]==20)
        self.assertEqual(failed["affinity_error_detail"]["tid"],777)
        self.assertIn("UNQUALIFIED",failed["affinity_error_detail"]["classification"])
        self.assert_stop(x)
class Drain(SupervisorTests):
    def test_context_drain_waits_under_existing_owner_until_driver_clears(self):
        present={"gpu_processes":[{"pid":os.getpid()}]}
        empty={"gpu_processes":[]}
        with patch.object(self.obj,"snapshot",return_value=empty) as observe:
            row=self.obj.drain_own_contexts(present)
        self.assertEqual(row,empty)
        self.assertTrue(self.obj.r["own_GPU_contexts_cleared"])
        self.assertEqual(observe.call_count,1)
        self.assertEqual(self.obj.r["context_drain_attempts"][0]["own_context_PIDs"],[os.getpid()])
    def test_context_drain_is_bounded_and_retains_cleanup_gap(self):
        row={"gpu_processes":[{"pid":os.getpid()}]}
        with patch.object(self.obj,"snapshot",return_value=row) as observe:
            self.obj.drain_own_contexts(row)
        self.assertFalse(self.obj.r["own_GPU_contexts_cleared"])
        self.assertEqual(observe.call_count,10)
        self.assertEqual(len(self.obj.r["context_drain_attempts"]),11)
        self.assertIn("did not clear",self.obj.r["cleanup_gap"])

    def test_cleanup_observation_error_cannot_leave_complete_status(self):
        import q1_supervisor as q
        from unittest.mock import Mock
        self._dispatcher_stop()
        ownrow=dict(self.row,gpu_processes=[{"pid":os.getpid()}])
        self.obj.snapshot=Mock(side_effect=[self.row,ownrow,OSError("injected GPU cleanup observation gap")])
        with patch.object(q.fcntl,"flock"),patch.object(q,"admit_low_activity"):
            result=self.obj.run()
        self.assertEqual(result["status"],"RESOURCE_STOP")
        self.assertFalse(result["own_GPU_contexts_cleared"])
        self.assertIn("cleanup observation gap",result["cleanup_observation_error"])
        self.assertTrue(result["lock_released"])

if __name__=="__main__":unittest.main(verbosity=2)
