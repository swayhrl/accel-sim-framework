#!/usr/bin/env python3
"""Exact authorized V3 additive global route handler; Main installation only.
No budget consumption here: the immutable scoped engine is the sole consumer."""
import hashlib,importlib.util,json,os,subprocess,sys
from pathlib import Path
GUARD='/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1/activation_20261104_v1/agent_d_execution/native_route_guard_v3.py'
GUARD_SHA='9df2bab0058b571466998f71bfa487a929b6718a0d7e56d347746e98d6208ca9'
ROOTS={'midtag': '/root/data/ep_l2_full_workload_performance_20261027_v1/execution_midtag_v3_20261104_v1/midtag', 'vector1700': '/root/data/ep_l2_full_workload_performance_20261027_v1/execution_vector1700_decomposition_v3_20261104_v1/vector1700'}
COHORT_GROUP={'EP_PERF_PFV3_MIDTAG_FWT_S_G32W16_V1': 'midtag', 'EP_PERF_PFV3_MIDTAG_FWT_S_G64W8_V1': 'midtag', 'EP_PERF_PFV3_MIDTAG_FWT_WV_ZERO_RO_G32W16_V1': 'midtag', 'EP_PERF_PFV3_MIDTAG_FWT_WV_ZERO_RO_G64W8_V1': 'midtag', 'EP_PERF_PFV3_MIDTAG_GEMM_S_G32W16_V1': 'midtag', 'EP_PERF_PFV3_MIDTAG_GEMM_S_G64W8_V1': 'midtag', 'EP_PERF_PFV3_MIDTAG_GEMM_WV_ZERO_RO_G32W16_V1': 'midtag', 'EP_PERF_PFV3_MIDTAG_GEMM_WV_ZERO_RO_G64W8_V1': 'midtag', 'EP_PERF_PFV3_VECTOR4M_WV_ZERO_RO_1700_V1': 'vector1700', 'EP_PERF_PFV3_VECTOR4M_W_ONLY_1700_V1': 'vector1700'}
def need(v,m):
 if not v:raise ValueError(m)
def sealed_command(fd,argv):
 head=os.pread(fd,64,0);path="/proc/self/fd/"+str(fd)
 if head.startswith(b"#!/bin/sh\n"):return ["/bin/sh",path,*argv]
 if head.startswith(b"#!/usr/bin/env python3\n")or head.startswith(b"#!/usr/bin/python3\n"):return ["/usr/bin/python3","-B",path,*argv]
 raise RuntimeError("unqualified sealed scoped-entry interpreter")
def main(argv=None):
 a=list(sys.argv[1:]if argv is None else argv)
 need(len(a)==5 and a[0]in["experiment","result"]and a[1]in["prepare","inspect","run-native","accept"]and a[3:]==["--project","EP_L2"],"exact5 V3 native command")
 need(a[2]in COHORT_GROUP,"outside exact approved V3 cohorts")
 need(hashlib.sha256(Path(GUARD).read_bytes()).hexdigest()==GUARD_SHA,"Native route guard drift")
 sp=importlib.util.spec_from_file_location("ep_v3_global_exact_routeguard",GUARD);guard=importlib.util.module_from_spec(sp);sp.loader.exec_module(guard)
 route=Path(ROOTS[COHORT_GROUP[a[2]]])/"control/NATIVE_ENTRY_ROUTE_V3.json"
 fd,receipt=guard.sealed_entry(route)
 try:
  need(a[2]in receipt["exact_cohorts"],"scoped route wrong family")
  # Scope CLI uses experiment for result aliases; the runtime retains operation checks.
  scoped=["experiment",*a[1:]]
  return subprocess.run(sealed_command(fd,scoped),pass_fds=(fd,),stdin=None,stdout=None,stderr=None).returncode
 finally:os.close(fd)
if __name__=="__main__":
 try:sys.exit(main())
 except Exception as e:
  print(json.dumps(dict(status="HOLD",reason=repr(e),scientific_starts=0)),file=sys.stderr);sys.exit(2)
