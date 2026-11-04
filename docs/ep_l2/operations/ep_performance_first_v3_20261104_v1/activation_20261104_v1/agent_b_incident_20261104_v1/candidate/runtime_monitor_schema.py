"""Pure pre-consume Native Host schema candidate. No actor, registry or file writes."""
from pathlib import Path
import json,hashlib,re,os
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_bytes())
def need(x,m):
 if not x:raise ValueError(m)
def validate_spec_contract(s,require_bound_cpu=False,check_current_domain=False):
 contract=read(ROOT/'RUNTIME_STATIC_KEY_CONTRACT.json')
 missing=sorted(set(contract['required_keys'])-set(s))
 need(not missing,'missing required runtime fields: '+','.join(missing))
 need(isinstance(s['native_boot_id'],str) and re.fullmatch(r'[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}',s['native_boot_id']) is not None,'invalid native_boot_id')
 need(isinstance(s['native_mount_namespace'],str) and re.fullmatch(r'mnt:\[[0-9]+\]',s['native_mount_namespace']) is not None,'invalid native_mount_namespace')
 if check_current_domain:
  need(s['native_boot_id']==Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'native boot changed before consume')
  need(s['native_mount_namespace']==os.readlink('/proc/self/ns/mnt'),'native mount namespace changed before consume')
 if require_bound_cpu:need(type(s['host_cpu'])is int and s['host_cpu']>=0,'dispatch CPU binding missing')
 else:need(s['host_cpu'] is None or type(s['host_cpu'])is int,'invalid dispatch CPU type')
 for k in ['AS_bytes','RSS_bytes','wall_seconds','result_bytes']:
  need(type(s['limits'].get(k))is int and s['limits'][k]>0,'missing/invalid runtime hard limit '+k)
 need(s['limits']['AS_bytes']>=s['limits']['RSS_bytes'],'AS below RSS')
 for k in ['binary_sha256','archive_sha256','core_source_commit','framework_source_commit','vendor_pybind11_commit']:
  v=s['source_identity'].get(k);need(isinstance(v,str)and len(v)==(64 if k.endswith('sha256') else 40),'missing/invalid Source5 '+k)
 closure=read(ROOT/'SOURCE862_NATIVE_RUNTIME_CLOSURE.json')
 need(s['source_identity']==closure['Source5'],'runtime closure belongs to different Source5')
 missing_pins={p:h for p,h in closure['pinned_files'].items()if s['pinned_files'].get(p)!=h}
 need(not missing_pins,'missing/mismatched native runtime dependency pins: '+','.join(sorted(missing_pins)))
 return dict(status='PRECONSUME_RUNTIME_SCHEMA_AND_NATIVE_CLOSURE_PASS',required_key_count=len(contract['required_keys']),native_dependency_pins=len(closure['pinned_files']),launch_permission=False)
