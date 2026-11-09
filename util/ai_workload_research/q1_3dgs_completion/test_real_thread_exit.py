"""Actual Linux thread exit regression; zero CUDA, NVML, API, or locks."""
import os
os.sched_setaffinity(0,{22,23})
import time,threading,json,unittest
import psutil
from process_observation import observe_processes,enforce_observation
class RealThreads(unittest.TestCase):
    def test_hundred_real_thread_exit_after_kernel_enumeration(self):
        pid=os.getpid();birth=psutil.Process(pid).create_time();censored=0
        row=dict(live_own_pids=[pid],rss_observed_processes=[dict(pid=pid,creation_time=birth)],monitor_gaps=[],unknown_gpu_pids=[],invalid_pid_rows=[])
        for attempt in range(100):
            release=threading.Event();ready=threading.Event();native=[]
            def target():
                native.append(threading.get_native_id());ready.set();release.wait()
            t=threading.Thread(target=target);t.start();ready.wait()
            exited=False
            def aff(tid):
                nonlocal exited
                if tid==native[0] and not exited:
                    self.assertTrue(os.path.exists("/proc/%d/task/%d"%(pid,tid)))
                    release.set();t.join();exited=True
                    deadline=time.monotonic()+1
                    while os.path.exists("/proc/%d/task/%d"%(pid,tid)) and time.monotonic()<deadline:time.sleep(.0001)
                    self.assertFalse(os.path.exists("/proc/%d/task/%d"%(pid,tid)))
                return os.sched_getaffinity(tid)
            result=observe_processes(psutil,row,{pid:birth},pid,pid,{22,23},
                     supervisor_affinity={22,23},affinity_get=aff,
                     allow_thread_exit_censor=True)
            release.set();t.join()
            enforce_observation(result)
            item=next(x for x in result["affinity_censored"] if x["tid"]==native[0])
            self.assertIsNone(item["affinity"])
            self.assertFalse(result["affinity_observation_complete"])
            self.assertTrue(item["task_absent_1"] and item["task_absent_2"])
            censored+=1
        print(json.dumps(dict(real_thread_exits=censored,root_identity_healthy=True,cuda_calls=0)))
if __name__=="__main__":unittest.main(verbosity=2)
