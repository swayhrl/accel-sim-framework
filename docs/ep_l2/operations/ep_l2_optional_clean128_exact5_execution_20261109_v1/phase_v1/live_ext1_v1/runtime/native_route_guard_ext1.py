import hashlib,json
from pathlib import Path
P=Path
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def validate_current(p):
 r=json.loads(P(p).read_bytes())
 assert r['request_ids']==['EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1'] and r['exact_cohorts']==['EP_PERF_CLEAN128_STENCIL_WV_EXT1_20261110_V1']
 assert r['guard_module_ref']=={'path':str(P(__file__).resolve()),'sha256':sha(__file__)}
 assert r['Main_user_authorization_ref']['sha256']==sha(r['Main_user_authorization_ref']['path'])
 a=json.loads(P(r['Main_user_authorization_ref']['path']).read_bytes())
 assert a['explicit_user_approval'] and a['approved_total_launches']==1 and a['request_id']==r['request_ids'][0]
 for k in ('old_route_ref','old_global_ref','owned_prefix_ref'):
  assert sha(r[k]['path'])==r[k]['sha256']
 old=json.loads(P(r['old_route_ref']['path']).read_bytes())
 assert old['request_ids']==['EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1','EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1']
 assert P(r['old_global_ref']['path']).read_bytes()==P(old['owned_prefix_ref']['path']).read_bytes()+P(old['global_preimage_ref']['path']).read_bytes()
 prefix=P(r['owned_prefix_ref']['path']).read_bytes()
 assert prefix.count(b'experiment:EP_PERF_CLEAN128_STENCIL_WV_EXT1_20261110_V1')==1
 assert P(r['global_shared_native_path']).read_bytes()==prefix+P(r['old_global_ref']['path']).read_bytes()
 entry=r['entry_refs'][r['request_ids'][0]]
 assert sha(entry['path'])==entry['sha256'] and b'EP_FULL_PERF_NATIVE_ENTRY=1' in P(entry['path']).read_bytes()
 return {'status':'EXT1_ADDITIVE_NATIVE_ROUTE_PASS','global_sha256':sha(r['global_shared_native_path'])}
