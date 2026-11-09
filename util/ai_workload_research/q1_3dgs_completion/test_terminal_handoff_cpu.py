"""Actual CPU child terminal handshake integration. GPU/service/flock boundary mocked."""
import os
os.sched_setaffinity(0,{22,23})
import json,sys,subprocess
from pathlib import Path
from unittest.mock import patch
import unittest,psutil
import q1_supervisor as q
from rss_lifecycle import OwnLifecycle
from test_q1_supervisor import SupervisorTests
REAL_POPEN=subprocess.Popen
class Handoff(SupervisorTests):
    def test_real_children_success_error_success_handoff_and_cleanup(self):
        self.obj.cfg["terminal_handoff"]=True
        self.obj.s.ps=psutil
        self.obj.lifecycle=OwnLifecycle(psutil,os.getpid())
        self.obj.lifecycle.identities[os.getpid()]=psutil.Process().create_time()
        self.obj.held=None
        jobs=[dict(id="CPU_OK"),dict(id="CPU_ERROR"),dict(id="CPU_AFTER"),dict(action="STOP",status="CPU_COMPLETE")]
        (self.path/".private/DISPATCH.jsonl").write_text("".join(json.dumps(x)+"\n" for x in jobs))
        previous=Path.read_text
        def real_status(path,*a,**k):
            if str(path).startswith("/proc/") and str(path).endswith("/status"):return self._read_text(path,*a,**k)
            return previous(path,*a,**k)
        def launch(command,**kw):
            p=Path(command[-1]).parent;job=json.loads(Path(command[-1]).read_text());bad=job["id"]=="CPU_ERROR"
            script="import os,pathlib,json,sys; import shared_gate; shared_gate.kernel_holders=lambda p:["+str(os.getpid())+"]; from terminal_protocol import worker_terminal; p=pathlib.Path("+repr(str(p))+");"
            script+="(p/"+repr("ERROR.json" if bad else "RESULT.json")+").write_text(json.dumps({'status':"+repr("ERROR" if bad else "COMPLETE")+"}));"
            script+="worker_terminal(p,"+str(os.getpid())+","+repr(str(self.lock))+","+str(not bad)+",True);sys.exit("+str(7 if bad else 0)+")"
            kw["env"]["PYTHONPATH"]=str(q.TOOL);kw["env"]["CUDA_VISIBLE_DEVICES"]=""
            return REAL_POPEN([sys.executable,"-B","-c",script],**kw)
        with patch.object(q.subprocess,"Popen",side_effect=launch),patch.object(q,"admit_low_activity"),patch.object(Path,"read_text",new=real_status),patch.object(q.fcntl,"flock") as lock:
            result=self.obj.run()
        self.assertEqual(result["status"],"CPU_COMPLETE",str(result))
        self.assertEqual([j["returncode"] for j in result["jobs"]],[0,7,0])
        self.assertTrue(all("terminal_handoff" in j for j in result["jobs"]))
        self.assertTrue(result["lock_released"] and result["own_GPU_contexts_cleared"])
        self.assertEqual(lock.call_count,2)
        self.assertFalse(any(psutil.pid_exists(j["pid"]) for j in result["jobs"]))
if __name__=="__main__":unittest.main(verbosity=2)
