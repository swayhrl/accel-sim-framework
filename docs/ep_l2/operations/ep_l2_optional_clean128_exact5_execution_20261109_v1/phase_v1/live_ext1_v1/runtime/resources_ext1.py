"""Own EXT1 resource mapping. Retain all foreign published writes."""
import hashlib,importlib.util,json
from pathlib import Path
P=Path
BASE=P("/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1/runtime/host_stencil_ext1_bound_v1/resources_b1.py")
PIN="f396e590861fa423a5b52ac9dcb1794d8ed153842e759ba32d3500c88d7e350d"
REG=P('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
EPOCH=P('/root/data/ep_l2_dtc_l1_native_v2/control/CURRENT_SCIENCE_EPOCH.json')
OLD=('EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1','EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1')
def impl():
 assert hashlib.sha256(BASE.read_bytes()).hexdigest()==PIN
 s=importlib.util.spec_from_file_location('ext1_base_resources',BASE);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def snapshot():
 m=impl();s=m.snapshot();raw=REG.read_bytes();e=json.loads(EPOCH.read_bytes())
 if hashlib.sha256(raw).hexdigest()!=s.get('registry_sha256') or e['native_registry_sha256']!=s.get('registry_sha256'):
  s['foreign_metadata_errors'].append('EXT1 registry/epoch race');return s
 reg=json.loads(raw)['registered_future_requests'];claims=json.loads((P("/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1/control/DISPATCH_CLAIMS.json")).read_bytes())['claims']
 if any(c.get('request') not in ("EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1",)+OLD or c.get('cohort')!=name for name,c in claims.items()):
  s['foreign_metadata_errors'].append('unknown shared claim owner');return s
 live=s.get('actual_loader_aware_models',[])
 if live:return s
 for req in OLD:
  q=reg[req];rows=q['consumed']
  if not(q['remaining']==0 and q['reserved_write_bytes']==0 and len(rows)==q['budget'] and all(r['state']=='CLOSED_ACCEPTED' for r in rows.values())):return s
  if any(c.get('request')==req for c in claims.values()):return s
  reason='unmapped active foreign RAM owner '+req
  if reason in s['foreign_metadata_errors']:s['foreign_metadata_errors'].remove(reason)
 s['ext1_terminal_reconciliation']={'closed_old_requests':list(OLD),'registry_sha256':s['registry_sha256'],'foreign_write_entries_unchanged':True,'no_live_models':True}
 return s
def admit(s,additional,writes,policy):return impl().admit(s,additional,writes,policy)
