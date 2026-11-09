"""Real CPU subprocesses through actual dispatcher lifecycle; all GPU/service/lock boundaries mocked."""
import os
os.sched_setaffinity(0,{22,23})
import json,sys,subprocess
from pathlib import Path
from unittest.mock import patch
import unittest
import psutil
import q1_supervisor as q
from rss_lifecycle import OwnLifecycle
from test_q1_supervisor import SupervisorTests
REAL_POPEN=subprocess.Popen
class DispatcherCPU(SupervisorTests):
    def test_serial_success_failure_next_job_and_final_cleanup_with_real_CPU_children(self):
        self.obj.s.ps=psutil
        self.obj.lifecycle=OwnLifecycle(psutil,os.getpid())
        self.obj.lifecycle.identities[os.getpid()]=psutil.Process().create_time()
        self.obj.cfg["monitor_seconds"]=.01
        self.obj.held=None
        self.obj.r["jobs"]=[]
        jobs=[dict(id="CPU_OK"),dict(id="CPU_ERROR"),dict(id="CPU_AFTER_ERROR"),
              dict(action="STOP",status="CPU_INTEGRATION_COMPLETE")]
        (self.path/".private/DISPATCH.jsonl").write_text("".join(json.dumps(x)+"\n" for x in jobs))
        previous_read=Path.read_text
        def real_child_status(path,*args,**kw):
            if str(path).startswith("/proc/") and str(path).endswith("/status"):
                return self._read_text(path,*args,**kw)
            return previous_read(path,*args,**kw)
        calls=[]
        def cpu_launch(command,**kw):
            request=Path(command[-1]);job=json.loads(request.read_text());context=request.parent
            code=("import pathlib,json,time,sys; p=pathlib.Path("+repr(str(context))+");"
                  "time.sleep(.03);")
            if job["id"]=="CPU_ERROR":
                code+="(p/'ERROR.json').write_text(json.dumps({'type':'InjectedCPUError'}));sys.exit(7)"
            else:code+="(p/'RESULT.json').write_text(json.dumps({'status':'COMPLETE','CPU_fixture':True}))"
            calls.append(job["id"])
            kw["env"]["CUDA_VISIBLE_DEVICES"]=""
            return REAL_POPEN([sys.executable,"-B","-c",code],**kw)
        with patch.object(q.subprocess,"Popen",side_effect=cpu_launch),patch.object(q,"admit_low_activity"),patch.object(Path,"read_text",new=real_child_status),patch.object(q.fcntl,"flock") as flock:
            result=self.obj.run()
        self.assertEqual(result["status"],"CPU_INTEGRATION_COMPLETE",str(result))
        self.assertEqual(calls,["CPU_OK","CPU_ERROR","CPU_AFTER_ERROR"])
        self.assertEqual([j["returncode"] for j in result["jobs"]],[0,7,0])
        self.assertEqual(result["jobs"][1]["error"]["type"],"InjectedCPUError")
        self.assertTrue(result["lock_released"])
        self.assertTrue(result["own_GPU_contexts_cleared"])
        self.assertEqual(result["lock_attempt_count"],1)
        self.assertTrue(result["reservation_cleanup"]["released"])
        self.assertFalse(any(psutil.pid_exists(j["pid"]) for j in result["jobs"]))
        self.assertEqual(flock.call_count,2)
    def test_monitor_failure_still_persists_observed_nonzero_exit_and_error(self):
        child=self._mock_child(returncode=7)
        self.obj.held=50
        def fail_snapshot(phase,enforce=True):
            raise q.MonitorStop("RESOURCE_STOP","injected genuine independent gap")
        context=self.path/".private/JOBS/CPU_FAIL"
        with patch.object(q.subprocess,"Popen",return_value=child),patch.object(q,"identity",return_value={"pid":424242}),patch.object(self.obj,"snapshot",side_effect=fail_snapshot):
            # run_job creates this folder and launch returns an already-ended child.
            def retire():
                (context/"ERROR.json").write_text(json.dumps(dict(type="InjectedError")))
                self.obj.inactive_child_verified=True
            with patch.object(self.obj,"retire_finished_worker",side_effect=retire):
                with self.assertRaises(q.MonitorStop):self.obj.run_job(dict(id="CPU_FAIL"))
        record=self.obj.r["jobs"][-1]
        self.assertEqual(record["returncode"],7)
        self.assertEqual(record["error"]["type"],"InjectedError")
        self.assertFalse(record.get("result",{}))

    def test_launch_failure_keeps_receipt_and_no_invented_exit_code(self):
        with patch.object(q.subprocess,"Popen",side_effect=FileNotFoundError("injected missing executable")):
            with self.assertRaises(FileNotFoundError):self.obj.run_job(dict(id="CPU_LAUNCH_FAIL"))
        record=self.obj.r["jobs"][-1]
        self.assertEqual(record["launch_status"],"STARTING")
        self.assertIsNone(record["last_observed_returncode"])
        self.assertIn("FileNotFoundError",record["supervisor_job_error"])
    def test_fast_exit_identity_failure_keeps_pid_and_actual_exit(self):
        child=self._mock_child(returncode=7)
        with patch.object(q.subprocess,"Popen",return_value=child),patch.object(q,"identity",side_effect=ProcessLookupError("injected identity race")):
            with self.assertRaises(ProcessLookupError):self.obj.run_job(dict(id="CPU_IDENTITY_FAIL"))
        record=self.obj.r["jobs"][-1]
        self.assertEqual(record["pid"],child.pid)
        self.assertEqual(record["returncode"],7)
        self.assertIn("ProcessLookupError",record["supervisor_job_error"])

if __name__=="__main__":unittest.main(verbosity=2)
