"""CPU integration of real worker control/store and actual CPU Tensor values.
Not GS kernels, not native performance. CUDA boundary explicitly mocked."""
import os
os.sched_setaffinity(0,{22,23})
import sys,copy,json,tempfile,unittest,threading,random
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
import torch
import worker as w
from state_store import semantic_fingerprint
torch.set_num_threads(1)
w.torch=torch;w.np=np;w.threading=threading

class Opt:
    def __init__(self,p):
        self.param_groups=[dict(params=[p],lr=.1)]
        self.defaults=dict(lr=.1)
        self.state={p:dict(step=1,exp_avg=torch.ones_like(p),exp_avg_sq=torch.ones_like(p)*2)}
    def state_dict(self):
        return dict(state={0:self.state[self.param_groups[0]["params"][0]]},
          param_groups=[dict(params=[0],lr=self.param_groups[0]["lr"])])
    def load_state_dict(self,b):
        self.state={self.param_groups[0]["params"][0]:b["state"][0]}
        self.param_groups[0]["lr"]=b["param_groups"][0]["lr"]
class Schedule:
    def __init__(self):self.n=1
    def state_dict(self):return dict(n=self.n)
    def load_state_dict(self,b):self.n=b["n"]
class Inner:
    def __init__(self,state=None):
        self.state=copy.deepcopy(state) if state else dict(initial_base_seed_rng_state=torch.get_rng_state(),cursor=2)
    def snapshot(self):return self.state
    def __iter__(self):return self
    def __next__(self):raise StopIteration
    def close(self):pass
class Flow(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.out=Path(self.tmp.name)
        (self.out/"raw").mkdir()
        self.patches=[
          patch.object(w,"OUT",self.out),patch.object(w,"CFG",dict(goal_start_epoch=1)),
          patch.object(torch.cuda,"synchronize"),patch.object(torch.cuda,"empty_cache"),
          patch.object(torch.cuda,"get_rng_state_all",return_value=[]),
          patch.object(torch.cuda,"set_rng_state_all"),
          patch.object(torch.cuda,"_lazy_init",side_effect=AssertionError("REAL_CUDA_FORBIDDEN"))]
        for p in self.patches:p.start()
        self.assertFalse(torch.cuda.is_initialized())
    def tearDown(self):
        self.assertFalse(torch.cuda.is_initialized())
        for p in reversed(self.patches):p.stop()
        self.tmp.cleanup()
    def fixture(self,job):
        c=w.Controller(job);c.context=self.out/"JOBS"/job["id"];c.context.mkdir(parents=True)
        c.source_sha="CPU_FIXTURE_NOT_GS";c.current_ids=[7];c.stable_ids=torch.arange(3);c.next_id=3
        params=torch.nn.ParameterDict(dict(means=torch.nn.Parameter(torch.arange(6.).reshape(3,2)),
          opacities=torch.nn.Parameter(torch.ones(3,1))))
        for p in params.values():p.grad=torch.ones_like(p)*.25
        r=SimpleNamespace(splats=params,optimizers_gpu=dict(means=Opt(params["means"])),
           optimizers_cpu=dict(opacities=Opt(params["opacities"])),strategy_state=dict(counter=2),
           cfg=SimpleNamespace(batch_size=1))
        c.runner=r;c.loader=SimpleNamespace(inner=Inner())
        live={k:None for k in w.LIVE};live.update(is_densify=False,counter=torch.zeros(3,dtype=torch.int64),
          valid_ids=torch.arange(3),valid_ids_cpu=torch.arange(3),valid_ids_cpu_prev=torch.arange(3),
          camtoworlds=torch.eye(4),Ks=torch.eye(3),pixels=torch.ones(1,2,2,3),
          image_ids=torch.tensor([7]),height=2,width=2,
          opacities=params["opacities"],colors0=torch.ones(3,1,3),colorsN=torch.ones(3,2,3))
        live["schedulers"]=[Schedule()];live["update_ids"]=torch.arange(3)
        return c,r,live
    def resume(self,path,job):
        c,r,live=self.fixture(job)
        def loader_factory(*a,**kw):
            state=copy.deepcopy(c.sidecar["loader"])
            state["initial_base_seed_rng_state"]=torch.tensor(state["initial_base_seed_rng_state"],dtype=torch.uint8)
            c.loader=SimpleNamespace(inner=Inner(state),prestarted=False)
            return c.loader
        c.loader_factory=loader_factory;r.trainset=object()
        w.restore_runner(c,r,path)
        live.update(c.resume_live)
        c.restore_schedule(live["schedulers"],r)
        return c,r,live
    def test_full_capture_save_real_store_restore_continue_resave_and_endpoint(self):
        c,r,live=self.fixture(dict(id="seed",mode="CONTINUE",stop_next=5))
        c.save("C_E",r,4,live);path=w.state_dir("C_E")
        saved=json.loads((self.out/"raw/STATE_C_E_MANIFEST.json").read_text())
        self.assertTrue(saved["semantic_state_fingerprint"])
        c2,r2,live2=self.resume(path,dict(id="continue",mode="CONTINUE",restore="C_E",
            stop_next=8,window_start=5,window_end=8,final_checkpoint_name="C_R_E",
            expected_semantic_fingerprint="intentionally_not_equal"))
        c2.assert_restored(r2,live2["schedulers"],live2)
        for step in range(5,8):
            c2.before(r2,step,live2)
            with torch.no_grad():
                for p in r2.splats.values():p.add_(.125)
            if step==7:
                with self.assertRaises(w.BlockDone):c2.after(r2,step,live2)
            else:c2.after(r2,step,live2)
        result=json.loads((c2.context/"RESULT.json").read_text())
        self.assertEqual(result["status"],"COMPLETE")
        self.assertEqual(result["continuation_numeric_class"],"NOT_ESTABLISHED")
        self.assertTrue(result["final_semantic_fingerprint"])
        self.assertEqual(len(result["rows"]),3)
        c3,r3,l3=self.resume(w.state_dir("C_R_E"),dict(id="restore_only",mode="RESTORE_ONLY",stop_next=8))
        with self.assertRaises(w.BlockDone):c3.assert_restored(r3,l3["schedulers"],l3)
        self.assertEqual(c3.result["new_training_steps"],0)
    def test_orphan_after_save_write_failure_not_published_success(self):
        c,r,live=self.fixture(dict(id="fail",mode="CONTINUE",stop_next=5))
        original=w.dump
        def fail_side(path,v):
            if str(path).endswith(".sidecar.json"):raise OSError("injected sidecar failure")
            return original(path,v)
        with patch.object(w,"dump",side_effect=fail_side):
            with self.assertRaises(OSError):c.save("C_ORPHAN",r,4,live)
        self.assertTrue((w.state_dir("C_ORPHAN")/"MANIFEST.json").exists())
        self.assertFalse((self.out/"raw/STATE_C_ORPHAN_MANIFEST.json").exists())
        self.assertEqual(c.saved,[])
    def test_exact_semantic_endpoint_branch_computes_hash_without_save(self):
        c,r,live=self.fixture(dict(id="endpoint",mode="CONTINUE",stop_next=6,
            window_start=5,expected_semantic_fingerprint="bad"))
        c.before(r,5,live)
        with self.assertRaises(w.BlockDone):c.after(r,5,live)
        self.assertEqual(c.result["continuation_numeric_class"],"NOT_ESTABLISHED")
        self.assertTrue(c.result["final_semantic_fingerprint"])
    def test_final_checkpoint_keeps_canonical_discovery_state(self):
        c,r,live=self.fixture(dict(id="canonical",mode="CONTINUE",stop_next=5))
        c.save("C_D",r,4,live)
        c.job.update(stop_next=6,final_checkpoint=True)
        c.before(r,5,live)
        with self.assertRaises(w.BlockDone):c.after(r,5,live)
        self.assertTrue(w.state_dir("C_D").exists())
        self.assertTrue(w.state_dir("C_FINAL").exists())

    def test_exact_endpoint_branch_really_compares_full_semantic_hash(self):
        c,r,live=self.fixture(dict(id="exact",mode="CONTINUE",stop_next=6,window_start=5))
        c.before(r,5,live)
        expected=semantic_fingerprint(c.capture(r,5,live))
        c.job["expected_semantic_fingerprint"]=expected
        with self.assertRaises(w.BlockDone):c.after(r,5,live)
        self.assertEqual(c.result["continuation_numeric_class"],"EXACT")
        self.assertEqual(c.result["final_semantic_fingerprint"],expected)

if __name__=="__main__":unittest.main(verbosity=2)
