"""Immutable owned V3 scoped route guard. No consumption, registry or model writes."""
import hashlib,importlib.util,json,os,sys
from pathlib import Path
HERE=Path(__file__).parent
CORE_SHA="6f6e149210e3e6d2308bf4c28e2e77c414639965d3804f750cb03205cca3de5d"
def _core():
 p=HERE/"safe_native_core_v3.py"
 if hashlib.sha256(p.read_bytes()).hexdigest()!=CORE_SHA:raise ValueError("V3 safe Native core drift")
 s=importlib.util.spec_from_file_location("ep_v3_frozen_route_core",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def validate_current(routepath):
 c=_core();r=json.loads(c.stable_read(routepath)[0])
 c.need(r["status"]=="MAIN_INSTALLED_ADDITIVE_NATIVE_EP_PERF_ROUTE"and
        r["approved_by"]=="EP-MAIN"and r["scientific_scope_activated"] is True,"unactivated Main route")
 c.need(isinstance(r["exact_cohorts"],list)and len(r["exact_cohorts"])==len(set(r["exact_cohorts"])),"exact finite EP route list")
 c.need(r["goal"]=='EP_L2_PFV5_A_FWT_G32W8_COLD_PROOF_MATCHED3_V1' and sorted(r["exact_cohorts"])==['EP_PERF_PFV5_A_FWT_G32W8_S_V1', 'EP_PERF_PFV5_A_FWT_G32W8_WV_OFF_V1', 'EP_PERF_PFV5_A_FWT_G32W8_WV_ON_V1'],"outside exact A3 independent scope")
 contract=json.loads(c.pin(r["shared_route_contract_ref"])[0])
 c.need(contract["schema"]=="EP_MAIN_V3_SHARED_ROUTE_CONTRACT_V1","shared route contract schema")
 base=c.pin(contract["installed_baseline_ref"])[0]
 current,globaltoken=c.stable_read(r["global_shared_native_ref"]["path"])
 # Baseline hash is immutable; current bytes may differ only by a separately Main-pinned reviewed grant.
 route="EXACT_INSTALLED_BASE"
 if current!=base:
  accepted=False
  for x in contract.get("reviewed_foreign_insertions",[]):
   grant=json.loads(c.pin(x["grant_ref"])[0]);c.validate_grant(grant)
   try:c.validate_global(current,base,grant);accepted=True;route="EXACT_REVIEWED_FINITE_FOREIGN_INSERT";break
   except c.Hold:pass
  c.need(accepted,"unreviewed Native mutation/shadow/delete/replace/foreign route")
 c.need(r["global_shared_native_ref"]["sha256"]==c.digest(base),"route receipt wrong installed baseline identity")
 entry,entrytoken=c.pin(r["entry_ref"])
 pins=r["owned_runtime_pins"];c.need(isinstance(pins,list)and pins,"missing immutable owned dependency graph")
 seen=set();receipts=[]
 for p in pins:
  c.need(p["path"]not in seen,"duplicate owned dependency pin");seen.add(p["path"])
  b,t=c.pin(p);receipts.append(dict(path=p["path"],sha256=c.digest(b),token=t))
 c.need(r["frontend_ref"]["path"]in seen and r["guard_module_ref"]["path"]in seen,"frontend/guard absent from owned graph")
 c.need(c.digest(c.pin(r["guard_module_ref"])[0])==hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"wrong guard module")
 return dict(schema="EP_MAIN_V3_SCOPED_NATIVE_ROUTE_VALIDATION_V1",status="PASS",goal=r["goal"],
   entry_ref=r["entry_ref"],entry_sha256=c.digest(entry),entry_token=entrytoken,
   shared_native_current_sha256=c.digest(current),shared_native_baseline_sha256=c.digest(base),
   shared_route_status=route,shared_global_token=globaltoken,owned_runtime_verified=receipts,
   exact_cohorts=r["exact_cohorts"],Source5_ELF_lib_actual_verification="DELEGATED_TO_EXISTING_ENGINE_PREPARE",
   consumes_science_budget=False)
def sealed_entry(routepath):
 """Validate current route, then return a sealed reviewed entry FD; never execute shared Native."""
 import fcntl
 c=_core();receipt=validate_current(routepath);entry,_=c.pin(receipt["entry_ref"])
 fd=os.memfd_create("EP-V3-scoped-entry",os.MFD_CLOEXEC|os.MFD_ALLOW_SEALING)
 try:
  view=memoryview(entry)
  while view:
   n=os.write(fd,view);c.need(n>0,"memfd write");view=view[n:]
  os.lseek(fd,0,os.SEEK_SET)
  seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL
  fcntl.fcntl(fd,fcntl.F_ADD_SEALS,seals)
  c.need(fcntl.fcntl(fd,fcntl.F_GET_SEALS)==seals,"unsealed entry")
  c.need(c.digest(os.pread(fd,len(entry),0))==receipt["entry_sha256"],"sealed entry identity")
  return fd,receipt
 except BaseException:os.close(fd);raise
