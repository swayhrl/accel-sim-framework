"""CPU-only full supervision mocks. Fake NVML never touches a driver or campaign lock."""
import unittest,ctypes,json,fcntl,ast,hashlib
from pathlib import Path
from types import SimpleNamespace as NS
from supervisor import Supervisor
from resource_monitor import collect_snapshot,enforce_snapshot,normalize_memory,MonitorStop
from persistence import save_json
TOOL=Path(__file__).resolve().parent
ROOT=TOOL.parents[2]
OUT=ROOT/"docs/ai_workload_research/runs/QWEN_DECODE_COST_MEMORY_MECHANISM_109_V9"
TESTROOT=OUT/".private/cpu_tests"
TESTROOT.mkdir(parents=True,exist_ok=True)

class FakePS:
    def __init__(self):self.alive={10,20,30};self.rss=100;self.gap=False;self.children=[]
    def Process(self,pid):
        if self.gap:raise RuntimeError("missing own tree")
        return NS(children=lambda recursive=True:[NS(pid=p) for p in self.children],memory_info=lambda:NS(rss=self.rss))
    def pid_exists(self,pid):return pid in self.alive
class FakeNV:
    def __init__(self,compute=None,graphics=None):
        self.compute=compute or [];self.graphics=graphics or [];self.inits=0;self.shutdowns=0;self.api_error=False;self.shutdown_error=False
    def nvmlInit(self):self.inits+=1
    def nvmlShutdown(self):
        self.shutdowns+=1
        if self.shutdown_error:raise RuntimeError("shutdown error")
    def nvmlDeviceGetHandleByUUID(self,uuid):return "fake_handle"
    def nvmlDeviceGetName(self,h):return "NVIDIA GeForce RTX 4080"
    def nvmlDeviceGetUUID(self,h):return "GPU-test"
    def nvmlDeviceGetMemoryInfo(self,h):return NS(total=16376*1024**2)
    def nvmlDeviceGetUtilizationRates(self,h):return NS(gpu=0,memory=0)
    def nvmlDeviceGetComputeRunningProcesses(self,h):
        if self.api_error:raise RuntimeError("NVML observation API error")
        return self.compute
    def nvmlDeviceGetGraphicsRunningProcesses(self,h):return self.graphics
class FakeLock:
    def __init__(self):self.closed=False
    def fileno(self):return 77
    def close(self):self.closed=True
class FakeChild:
    pid=20
    def __init__(self,exit_code):self.returncode=exit_code
    def poll(self):return self.returncode

def config(name):
    d=TESTROOT/name;d.mkdir(exist_ok=True)
    return dict(out=str(d),root=str(ROOT),goal_start_epoch=1000,lock="FAKE_LOCK_ONLY",UUID="GPU-test",held_seconds_max=720,goal_seconds_max=2700,own_vram_bytes_max=15400*1024**2,rss_bytes_max=16*1024**3,disk_bytes_max=3*1024**3,monitor_seconds=1,shutdown_reserve_seconds=10)
def services(nv=None,ps=None,lock_conflict=False,exit_code=0):
    nv=nv or FakeNV();ps=ps or FakePS();lock=FakeLock();calls=[];count={"spawn":0,"terminate":0}
    def flock(fd,flags):
        calls.append(flags)
        if flags & fcntl.LOCK_NB and lock_conflict:raise BlockingIOError("conflict")
    def spawn():count["spawn"]+=1;return FakeChild(exit_code)
    def terminate(child):count["terminate"]+=1;child.returncode=-15
    raw=dict(status="NATIVE_BATCH_SENSITIVITY_COMPLETE",model_initializations=1,samples=[dict(point="P"+str(p),role="FORMAL",status="PASS") for p in range(1,7) for i in range(5)])
    return NS(pid=10,nv=nv,ps=ps,wall=lambda:1001,mono=lambda:100, sleep=lambda n:None,disk=lambda:1000,open_lock=lambda p:lock,flock=flock,spawn=spawn,terminate=terminate,worker_result=lambda:raw,lock_object=lock,lock_calls=calls,counts=count,raw=raw)
def info(pid=10,mem=100):return NS(pid=pid,usedGpuMemory=mem)

class SnapshotTests(unittest.TestCase):
    def snapshot(self,nv,ps=None,owned=None,disk=1000):
        ps=ps or FakePS()
        return collect_snapshot(nv,"fake",ps,10,{10} if owned is None else owned,"CPU_SIMULATION",1001,1,1,disk)
    def test_none_sentinel_and_ctypes(self):
        for value in [None,(1<<64)-1,ctypes.c_ulonglong(-1),-1]:
            with self.subTest(value=value):
                row=self.snapshot(FakeNV([info(mem=value)]))
                self.assertEqual(row["state"],"UNKNOWN")
                with self.assertRaises(MonitorStop):enforce_snapshot(row,config("sentinel"))
        self.assertEqual(normalize_memory(ctypes.c_ulonglong(128)),128)
    def test_self_normal_and_duplicate_compute_graphics(self):
        row=self.snapshot(FakeNV([info(mem=ctypes.c_ulonglong(128))],[info(mem=128)]))
        self.assertEqual(row["state"],"OWN_LIVE_PID");self.assertEqual(row["own_NVML_bytes"],128);self.assertEqual(len(row["gpu_processes"]),1)
        enforce_snapshot(row,config("normal"))
    def test_child_self_process(self):
        ps=FakePS();ps.children=[20]
        row=self.snapshot(FakeNV([info(20,123)]),ps)
        self.assertEqual(row["state"],"OWN_LIVE_PID");self.assertEqual(row["own_NVML_bytes"],123)
    def test_external(self):
        row=self.snapshot(FakeNV([info(30,100)]))
        self.assertEqual(row["external_gpu_pids"],[30])
        with self.assertRaisesRegex(MonitorStop,"External"):enforce_snapshot(row,config("external"))
    def test_unknown_pid_and_memory(self):
        for val in [info(None,100),info(999,100),info(30,None),info("invalid",100)]:
            row=self.snapshot(FakeNV([val]))
            self.assertEqual(row["state"],"UNKNOWN")
            with self.assertRaises(MonitorStop):enforce_snapshot(row,config("unknown"))
    def test_conflicting_duplicate_observation(self):
        row=self.snapshot(FakeNV([info(mem=128)],[info(mem=256)]))
        self.assertEqual(row["state"],"UNKNOWN")
    def test_missing_tree_observation(self):
        ps=FakePS();ps.gap=True;row=self.snapshot(FakeNV(),ps)
        self.assertEqual(row["state"],"UNKNOWN")
        with self.assertRaises(MonitorStop):enforce_snapshot(row,config("gap"))
    def test_all_resource_boundaries(self):
        cfg=config("caps");base=self.snapshot(FakeNV())
        for key,limit in [("own_NVML_bytes","own_vram_bytes_max"),("own_tree_RSS_bytes","rss_bytes_max"),("own_new_disk_bytes","disk_bytes_max")]:
            row=dict(base);row[key]=cfg[limit]
            enforce_snapshot(row,cfg);row[key]+=1
            with self.assertRaisesRegex(MonitorStop,"Resource limit"):enforce_snapshot(row,cfg)
        for key,val in [("held_seconds",711),("goal_elapsed_seconds",2676)]:
            row=dict(base);row[key]=val
            with self.assertRaises(MonitorStop):enforce_snapshot(row,cfg)

class LifecycleTests(unittest.TestCase):
    def run_case(self,name,s):
        cfg=config(name);r=Supervisor(cfg,s).run()
        self.assertEqual(json.loads((Path(cfg["out"])/"RESOURCE_RECEIPT.json").read_text())["status"],r["status"])
        self.assertTrue(s.lock_object.closed);self.assertEqual(r["lock_attempt_count"],1)
        return r
    def test_lock_conflict_never_calls_nvml_or_spawns(self):
        s=services(lock_conflict=True);r=self.run_case("lock_conflict",s)
        self.assertEqual(r["status"],"GPU_RESOURCE_DEFERRED");self.assertEqual(s.nv.inits,0);self.assertEqual(s.counts["spawn"],0);self.assertFalse(r["lock_acquired"]);self.assertEqual(len(s.lock_calls),1)
    def test_external_snapshot_persisted_unlocks_and_never_spawns(self):
        s=services(FakeNV([info(30,100)]));r=self.run_case("external_lifecycle",s)
        self.assertEqual(r["status"],"GPU_RESOURCE_DEFERRED");self.assertTrue(r["lock_released"]);self.assertEqual(s.counts["spawn"],0);self.assertEqual(r["samples"][0]["external_gpu_pids"],[30]);self.assertEqual(s.nv.shutdowns,1);self.assertEqual(s.lock_calls[-1],fcntl.LOCK_UN)
    def test_unknown_memory_unlocks(self):
        s=services(FakeNV([info(30,None)]));r=self.run_case("unknown_lifecycle",s)
        self.assertEqual(r["status"],"GPU_RESOURCE_DEFERRED");self.assertTrue(r["lock_released"]);self.assertEqual(s.counts["spawn"],0)
    def test_api_exception_error_receipt_and_unlock(self):
        nv=FakeNV();nv.api_error=True;s=services(nv);r=self.run_case("api_error",s)
        self.assertEqual(r["status"],"NUMERIC_OR_RUNTIME_NO_GO");self.assertTrue(r["lock_released"]);self.assertIn("final_observation_error",r);self.assertEqual(s.counts["spawn"],0)
    def test_resource_excess_before_spawn(self):
        ps=FakePS();ps.rss=16*1024**3+1;s=services(ps=ps);r=self.run_case("rss_limit",s)
        self.assertEqual(r["status"],"INCONCLUSIVE");self.assertTrue(r["lock_released"]);self.assertEqual(s.counts["spawn"],0)
    def test_child_error_cleanup_unlock(self):
        s=services(exit_code=2);r=self.run_case("child_error",s)
        self.assertEqual(r["status"],"NUMERIC_OR_RUNTIME_NO_GO");self.assertTrue(r["lock_released"]);self.assertEqual(s.counts["terminate"],1)
    def test_simulated_complete_result(self):
        s=services();r=self.run_case("complete_mock_only",s)
        self.assertEqual(r["status"],"NATIVE_BATCH_SENSITIVITY_COMPLETE");self.assertTrue(r["lock_released"]);self.assertTrue(r["EXCLUSIVITY_EVIDENCE_COMPLETE"])
    def test_nvml_shutdown_error_still_unlocks_and_persists(self):
        nv=FakeNV();nv.shutdown_error=True;s=services(nv);r=self.run_case("shutdown_error",s)
        self.assertEqual(r["status"],"NUMERIC_OR_RUNTIME_NO_GO");self.assertTrue(r["lock_released"]);self.assertIn("NVML_shutdown_error",r)
    def test_incomplete_result_no_promotion(self):
        s=services();s.raw["samples"]=[]
        r=self.run_case("incomplete",s)
        self.assertEqual(r["status"],"NUMERIC_OR_RUNTIME_NO_GO");self.assertTrue(r["lock_released"])

    def test_resource_excess_during_live_worker_cleans_group(self):
        s=services();child=FakeChild(None)
        def spawn():
            s.counts["spawn"]+=1
            return child
        s.spawn=spawn
        calls=[0]
        def disk():
            calls[0]+=1
            return 1000 if s.counts["spawn"]==0 else 3*1024**3+1
        s.disk=disk
        r=self.run_case("live_disk_excess",s)
        self.assertEqual(r["status"],"INCONCLUSIVE");self.assertTrue(r["lock_released"]);self.assertEqual(s.counts["terminate"],1)
        self.assertTrue(any(x["phase"]=="WORKER" for x in r["samples"]))
    def test_unlock_exception_still_closes_and_writes_error(self):
        s=services();original=s.flock
        def unlock_error(fd,flags):
            if flags==fcntl.LOCK_UN:raise OSError("simulated unlock error")
            return original(fd,flags)
        s.flock=unlock_error
        r=self.run_case("unlock_error",s)
        self.assertEqual(r["status"],"NUMERIC_OR_RUNTIME_NO_GO");self.assertIn("unlock_error",r)
        self.assertTrue(r["lock_closed"])

class PersistenceAndStaticTests(unittest.TestCase):
    def test_failure_nonfinite_evidence_is_preserved(self):
        d=TESTROOT/"nonfinite.json";save_json(d,{"probs":[float("nan"),float("inf"),-float("inf")],"status":"FAIL"})
        result=json.loads(d.read_text());self.assertEqual(result["status"],"FAIL");self.assertTrue(all("nonfinite_float" in x for x in result["probs"]))
    def test_frozen_engine_sampling_and_timing_ast_equal(self):
        original=(TOOL.parent/"bf16_decode_weight_supply_probe_v5/worker.py").read_text()
        current=(TOOL/"worker.py").read_text()
        for name in ["LLM","SamplingParams","CompilationConfig"]:
            def calls(text):
                tree=ast.parse(text)
                for n in ast.walk(tree):
                    if isinstance(n,ast.Call) and isinstance(n.func,ast.Name):
                        for kw in n.keywords:
                            if n.func.id=="LLM" and kw.arg=="enable_prefix_caching" and isinstance(kw.value,ast.Name) and kw.value.id=="prefix_enabled":kw.value=ast.Constant(False)
                            if n.func.id=="SamplingParams" and kw.arg=="logprobs" and isinstance(kw.value,ast.Name) and kw.value.id=="lp":kw.value=ast.Constant(20)
                            if n.func.id=="LLM" and kw.arg=="enforce_eager" and isinstance(kw.value,ast.Name) and kw.value.id=="altered":kw.value=ast.Constant(False)
                            if n.func.id=="CompilationConfig" and isinstance(kw.value,ast.IfExp):kw.value=kw.value.orelse
                            if n.func.id=="SamplingParams" and kw.arg=="logprobs" and isinstance(kw.value,ast.Constant) and kw.value.value is None:kw.value=ast.Constant(20)
                return [ast.dump(n,include_attributes=False) for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==name]
            self.assertEqual(calls(original),calls(current),name)
        def timing(text):
            a=text.index("torch.cuda.synchronize();start=");b=text.index("elapsed=float(start.elapsed_time(stop))",a)
            return ast.dump(ast.parse(__import__("textwrap").dedent(text[a:b+len("elapsed=float(start.elapsed_time(stop))")]).replace("\\n   ","\\n").replace("\\n     ","\\n")),include_attributes=False)
        # Exact statements after stripping leading indentation; operation sequence unchanged.
        def lines(text):
            a=text.index("torch.cuda.synchronize();start=");b=text.index("elapsed=float(start.elapsed_time(stop))",a)
            return [s.strip() for s in text[a:b].splitlines() if "torch.cuda.nvtx.range_" not in s]
        self.assertEqual(lines(original),lines(current))
    def test_endpoint_order_and_one_lock_attempt_site(self):
        t=(TOOL/"worker.py").read_text()
        pieces=["torch.cuda.synchronize();start=","start.record();host_start=","responses=llm.generate","stop.record();torch.cuda.synchronize()","elapsed=float(start.elapsed_time(stop))"]
        positions=[t.index(x) for x in pieces];self.assertEqual(positions,sorted(positions))
        self.assertIn("assert active,",t)
        self.assertIn("if count>1:assert sum(graphs.values())==count-1",t)
        sup=(TOOL/"supervisor.py").read_text()
        self.assertEqual(sup.count("fcntl.LOCK_EX|fcntl.LOCK_NB"),1)
        self.assertLess(sup.index("fcntl.LOCK_EX|fcntl.LOCK_NB"),sup.index("self.s.nv.nvmlInit()"))
        self.assertNotIn("nv.NVML_VALUE_NOT_AVAILABLE",sup)
    def test_actual_binding_shape_without_init(self):
        import pynvml
        self.assertTrue(callable(pynvml.nvmlDeviceGetComputeRunningProcesses));self.assertTrue(callable(pynvml.nvmlDeviceGetGraphicsRunningProcesses))
        self.assertEqual(pynvml.NVML_VALUE_NOT_AVAILABLE_ulonglong.value,(1<<64)-1)
        self.assertIsNone(normalize_memory(pynvml.NVML_VALUE_NOT_AVAILABLE_ulonglong))
if __name__=="__main__":unittest.main(verbosity=2)
