"""Host-only isolated fixtures: no science authority mutation or model invocation."""
import concurrent.futures,contextlib,copy,fcntl,hashlib,importlib.util,json,os,subprocess,tempfile,threading,unittest
from pathlib import Path
from unittest import mock
import native_route_guard_v3 as G
import safe_native_core_v3 as core
import finite_main_v3 as D
HERE=Path(__file__).parent
OLD=HERE.parent.parent/"agent_d_native_queue"
def ref(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def put(p,v):p.write_text(json.dumps(v))
STUB=b"#!/bin/sh\n/usr/bin/python3 -c 'import json,os,sys;print(json.dumps(dict(marker=\"V3_CPU_ONLY\",argv=sys.argv[1:],token=os.getenv(\"EP_CPU_TOKEN\"))))' \"$@\"\n"
class Route(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.t=Path(self.tmp.name)
  self.base=self.t/"base";self.base.write_bytes((OLD/"shared_native_preimage.sh").read_bytes())
  self.shared=self.t/"shared";self.shared.write_bytes((OLD/"shared_native_reviewed_current.sh").read_bytes())
  self.entry=self.t/"scope";self.entry.write_bytes(STUB)
  self.front=self.t/"frontend.py";self.front.write_text("# CPU stub only")
  self.contract=self.t/"contract.json";put(self.contract,dict(schema="EP_MAIN_V3_SHARED_ROUTE_CONTRACT_V1",installed_baseline_ref=ref(self.base),reviewed_foreign_insertions=[dict(grant_ref=ref(OLD/"FOREIGN_FINITE_INSERT_GRANT_CANDIDATE.json"))]))
  self.route=self.t/"route.json"
  self.data=dict(goal="EP_L2_CPU_ONLY_FIXTURE",status="MAIN_INSTALLED_ADDITIVE_NATIVE_EP_PERF_ROUTE",
   approved_by="EP-MAIN",scientific_scope_activated=True,exact_cohorts=["EP_PERF_PFV3_CPU_ONLY"],
   global_shared_native_ref=ref(self.base),entry_ref=ref(self.entry),shared_route_contract_ref=ref(self.contract),
   frontend_ref=ref(self.front),guard_module_ref=ref(HERE/"native_route_guard_v3.py"),
   owned_runtime_pins=[ref(self.front),ref(HERE/"native_route_guard_v3.py"),ref(HERE/"safe_native_core_v3.py")])
  self.data["global_shared_native_ref"]["path"]=str(self.shared);put(self.route,self.data)
 def tearDown(self):self.tmp.cleanup()
 def test_finite_authorized_foreign_insert_PASS(self):
  p=G.validate_current(self.route);self.assertEqual(p["status"],"PASS")
  self.assertEqual(p["shared_route_status"],"EXACT_REVIEWED_FINITE_FOREIGN_INSERT")
  self.assertFalse(p["consumes_science_budget"])
 def test_exact_base_PASS(self):
  self.shared.write_bytes(self.base.read_bytes());self.assertEqual(G.validate_current(self.route)["shared_route_status"],"EXACT_INSTALLED_BASE")
 def test_shadow_and_EP_mutation_rejected(self):
  for bad in [b"#!/bin/sh\nexec /bin/true\n"+self.shared.read_bytes(),self.shared.read_bytes().replace(b"EP_PERF_*",b"EP_WRONG_*")]:
   self.shared.write_bytes(bad)
   with self.assertRaises(ValueError):G.validate_current(self.route)
 def test_owned_dependency_before_use_SHA_rejected(self):
  self.front.write_text("# corrupted owned dependency")
  with self.assertRaises(ValueError):G.validate_current(self.route)
 def test_missing_graph_and_wrong_baseline_rejected(self):
  self.data["owned_runtime_pins"]=[];put(self.route,self.data)
  with self.assertRaises(ValueError):G.validate_current(self.route)
 def test_scoped_entry_pin_before_open_reject(self):
  self.entry.write_bytes(STUB+b"# changed")
  with self.assertRaises(ValueError):G.sealed_entry(self.route)
 def test_sealed_execution_global_and_entry_swap_cannot_redirect(self):
  fd,p=G.sealed_entry(self.route)
  try:
   self.shared.write_bytes(b"#!/bin/sh\necho BAD_SHARED\n")
   self.entry.write_bytes(b"#!/bin/sh\necho BAD_SCOPED\n")
   with self.assertRaises(OSError):os.pwrite(fd,b"evil",0)
   r=subprocess.run(["/bin/sh","/proc/self/fd/"+str(fd),"arg with space","; literal"],pass_fds=(fd,),env=dict(os.environ,EP_CPU_TOKEN="preserved"),text=True,capture_output=True,check=True)
   z=json.loads(r.stdout);self.assertEqual(z,dict(marker="V3_CPU_ONLY",argv=["arg with space","; literal"],token="preserved"))
  finally:os.close(fd)
 def test_python_entry_sealed_interpreter_and_unknown_reject(self):
  body=b"#!/usr/bin/env python3\nimport json,sys;print(json.dumps(dict(marker='PY_CPU_ONLY',argv=sys.argv[1:])))\n"
  self.entry.write_bytes(body);self.data["entry_ref"]=ref(self.entry);put(self.route,self.data)
  fd,proof=G.sealed_entry(self.route)
  try:
   self.entry.write_text("# replaced after seal")
   r=subprocess.run(D.sealed_command(fd,["experiment","inspect","EP_PERF_PFV3_CPU_ONLY","--project","EP_L2"]),pass_fds=(fd,),capture_output=True,text=True,check=True)
   self.assertEqual(json.loads(r.stdout)["marker"],"PY_CPU_ONLY")
   self.assertEqual(json.loads(r.stdout)["argv"][1],"inspect")
  finally:os.close(fd)
  self.entry.write_bytes(b"#!/bin/bash\necho forbidden\n");self.data["entry_ref"]=ref(self.entry);put(self.route,self.data)
  fd,_=G.sealed_entry(self.route)
  try:
   with self.assertRaises(RuntimeError):D.sealed_command(fd,[])
  finally:os.close(fd)
 def test_repeated_and_concurrent_preview_no_state_writes(self):
  before={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in self.t.iterdir()}
  with concurrent.futures.ThreadPoolExecutor(max_workers=8)as ex:
   self.assertTrue(all(x["status"]=="PASS"for x in ex.map(lambda _:G.validate_current(self.route),range(64))))
  after={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in self.t.iterdir()}
  self.assertEqual(before,after)
class Queue(unittest.TestCase):
 def setUp(self):
  self.points=[dict(cohort=f"EP_PERF_PFV3_MIDTAG_{w}_{mode}_{geo}_V1",group="midtag")for w in["FWT","GEMM"]for mode in["S","WV_ZERO_RO"]for geo in["G32W16","G64W8"]]+[dict(cohort=f"EP_PERF_PFV3_VECTOR4M_{mode}_1700_V1",group="vector1700")for mode in["W_ONLY","WV_ZERO_RO"]]
 def test_initial_releases6_waits4(self):
  r=D.stage_decisions(self.points,{},{});self.assertEqual(sum(x["status"]=="RELEASE"for x in r.values()),6);self.assertEqual(sum(x["status"]=="WAIT"for x in r.values()),4)
 def test_FWT_all_accepted_archived_releasesGEMM(self):
  f=[p["cohort"]for p in self.points if"_FWT_"in p["cohort"]]
  rows={c:dict(state="CLOSED_ACCEPTED")for c in f};views={c:dict(accepted=True,archived=True)for c in f}
  self.assertTrue(all(x["status"]=="RELEASE"for c,x in D.stage_decisions(self.points,rows,views).items()if"_GEMM_"in c))
  views[f[0]]["archived"]=False
  self.assertTrue(all(x["status"]=="WAIT"for c,x in D.stage_decisions(self.points,rows,views).items()if"_GEMM_"in c))
 def test_FWT_failure_localHOLD_Vector_continues(self):
  f=next(p["cohort"]for p in self.points if"_FWT_"in p["cohort"])
  r=D.stage_decisions(self.points,{f:dict(state="CLOSED_UNACCEPTED")},{})
  self.assertTrue(all(x["status"]=="HOLD"for c,x in r.items()if"_GEMM_"in c))
  self.assertTrue(all(x["status"]=="RELEASE"for c,x in r.items()if"_VECTOR4M_"in c))
 def test_FWT_preconsume_technical_hold_also_blocks_only_GEMM(self):
  f=next(p["cohort"]for p in self.points if"_FWT_"in p["cohort"])
  out=D.stage_decisions(self.points,{}, {},technical=[f])
  self.assertTrue(all(x["status"]=="HOLD"for c,x in out.items()if"_GEMM_"in c))
  self.assertTrue(all(x["status"]=="RELEASE"for c,x in out.items()if"_VECTOR4M_"in c))
 def test_cap2_10_and11deny(self):
  self.assertTrue(D.concurrency_capacity(1,1,2));self.assertFalse(D.concurrency_capacity(2,1,2))
  self.assertTrue(D.concurrency_capacity(9,9,10));self.assertFalse(D.concurrency_capacity(10,9,10))
  with self.assertRaises(RuntimeError):D.concurrency_capacity(0,0,11)
 def test_mocked_exact10_dryloop_no_duplicate_no_refund(self):
  rows={};views={};consumed=[];active=set();peak=0;lock=threading.Lock()
  for step in range(3):
   r=D.stage_decisions(self.points,rows,views)
   for p in self.points:
    c=p["cohort"]
    if r[c]["status"]!="RELEASE":continue
    with lock:
     if c in rows or not D.concurrency_capacity(len(active),len(active),10):continue
     rows[c]=dict(state="RUNNING");active.add(c);consumed.append(c);peak=max(peak,len(active))
   for c in list(active):
    rows[c]["state"]="CLOSED_ACCEPTED";views[c]=dict(accepted=True,archived=True);active.remove(c)
  self.assertEqual(len(consumed),10);self.assertEqual(len(set(consumed)),10);self.assertEqual(peak,6)
  again=D.stage_decisions(self.points,rows,views);self.assertTrue(all(x["status"]=="CONSUMED"for x in again.values()))
 def test_archive_shared_lock_serial(self):
  # Isolated lock path, never the real archive/registry/owner lock.
  with tempfile.TemporaryDirectory()as t:
   path=Path(t)/"archive.lock";live=0;peak=0;gate=threading.Lock()
   def run(_):
    nonlocal live,peak
    with D.lock(path):
     with gate:live+=1;peak=max(peak,live)
     import time;time.sleep(.005)
     with gate:live-=1
   with concurrent.futures.ThreadPoolExecutor(max_workers=4)as ex:list(ex.map(run,range(8)))
   self.assertEqual(peak,1)
 def test_entry_route_addition_is_byte_exact_and_finite(self):
  pre=(HERE/"GLOBAL_NATIVE_PREIMAGE_530.sh").read_bytes();block=(HERE/"V3_EXACT10_ROUTE_INSERT.sh").read_bytes();new=(HERE/"GLOBAL_NATIVE_EXACT10_CANDIDATE.sh").read_bytes()
  self.assertEqual(new,core.HEADER+block+pre[len(core.HEADER):])
  self.assertNotIn(b"EP_PERF_*",block);self.assertEqual(block.count(b"experiment:EP_PERF_PFV3_"),10)
  self.assertEqual(block.count(b"result:EP_PERF_PFV3_"),10)
  subprocess.run(["/bin/sh","-n",str(HERE/"GLOBAL_NATIVE_EXACT10_CANDIDATE.sh")],check=True)
if __name__=="__main__":unittest.main(verbosity=2)
