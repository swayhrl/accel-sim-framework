"""Bounded correction of terminal legacy RAM metadata for EXT1 admission."""
import hashlib,importlib.util,json
from pathlib import Path
P=Path
BASE=P("/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1/runtime/host_stencil_ext1_bound_v1/resources_ext1.py")
PIN="06c6c3d091c418ce12ffb965af770c433bd9d0b278a11bd37478cb9b1e6e6001"
REG=P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
EP_CLOSED=('EP_L2_PFV4_A1_STENCIL_SOURCE78_850_L100_V1','EP_L2_PFV4_A2_3MM_SOURCE78_850_L100_V1','EP_L2_PFV4_A3_TRANSPOSE_SOURCE78_850_L100_V1','EP_L2_PFV5_A_FWT_G32W8_COLD_PROOF_MATCHED3_V1','EP_L2_PFV5_B1_VECTOR4M1700_PRESSURE_EPOCH_MATCHED_F_V1','EP_L2_UMT1_CONV3072_SOURCE812_PRESSURE_MATCHED_F_850_L100_V1','EP_L2_UMT1_SCAN_CF8D1C4D_SOURCE812_PRESSURE_MATCHED_F_850_L100_V1','EP_L2_VECTOR1700_WV_DECOMPOSITION_FRESH_V4_20261104')
DTC_TERMINAL=('DTC_ORACLE_INITIAL8_20261106_V1','DTC_ORACLE_REMAINING24_20261106_V1','DTC_PERF_FIRST_NON_TAG_REMAINING28_20261104_V1','DTC_PERF_FIRST_PHYS768_FIRST4_20261104_V1','DTC_PERF_FIRST_V2_CODESIGN16_LAYOUT_R1_20261105_V1','DTC_PERF_FIRST_V2_PHYSICAL_PIB16_20261105_V1')
def impl():
 assert hashlib.sha256(BASE.read_bytes()).hexdigest()==PIN
 x=importlib.util.spec_from_file_location('ext1_v1_resources',BASE);m=importlib.util.module_from_spec(x);x.loader.exec_module(m);return m
def snapshot():
 s=impl().snapshot()
 if s['actual_loader_aware_models']:return s
 raw=REG.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=s['registry_sha256']:s['foreign_metadata_errors'].append('registry changed during EXT1 terminal audit');return s
 rows=json.loads(raw)['registered_future_requests'];clear=[]
 for req in EP_CLOSED+DTC_TERMINAL:
  q=rows[req];cs=q.get('consumed')
  if not(isinstance(cs,dict) and q.get('remaining')==0 and len(cs)==q.get('budget')):return s
  if req in EP_CLOSED:
   if not(q.get('state')=='CLOSED_COMPLETED' and q.get('reserved_write_bytes')==0 and all(r.get('state') in ('CLOSED_ACCEPTED','CLOSED_UNACCEPTED') for r in cs.values())):return s
  else:
   if not(q.get('state')=='RUNNING' and all(isinstance(r.get('execution_receipt'),dict) and r.get('charged')==1 for r in cs.values())):return s
  clear.append('unmapped active foreign RAM owner '+req)
 if not set(clear).issubset(set(s['foreign_metadata_errors'])):return s
 s['foreign_metadata_errors']=[e for e in s['foreign_metadata_errors'] if e not in clear]
 s['ext1_legacy_terminal_reconciliation']={'cleared_errors':clear,'registry_sha256':s['registry_sha256'],'no_live_models':True,'foreign_write_commitments_retained':True}
 return s
def admit(s,additional,writes,policy):return impl().admit(s,additional,writes,policy)
