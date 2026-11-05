"""Bounded new scope wiring tests; no actors, grants, dispatch or mutation outside this addendum."""
from pathlib import Path
import importlib.util,hashlib,json,copy
N=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('scoped_resource_final_delta',N/'resource_scope_v5.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
results=[]
def check(name,fn,reject=False):
 try:v=fn()
 except Exception as exc:
  if not reject:raise
  results.append(dict(name=name,status='PASS_REJECT',reason=str(exc)));return
 if reject:raise AssertionError('accepted negative '+name)
 if v is False:raise AssertionError('false positive '+name)
 results.append(dict(name=name,status='PASS'))
snapshots=[]
for label,request in [('A',m.REQUEST_A),('B',m.REQUEST_B),('D',m.REQUEST_D)]:
 a=m.for_scope(request);v=a.snapshot()
 assert v['current_request']==request and v['current_scope_registered']is False
 assert not v['foreign_metadata_errors'],v['foreign_metadata_errors']
 (N/('ACTUAL_'+label+'_RESOURCE_SNAPSHOT.json')).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 check(label+'_real_snapshot_full_owner_mapping',lambda:True)
 check(label+'_unregistered_admit',lambda a=a,v=v:a.admit(v,1<<30,128<<20,dict(max_global_EP_models=10)),True)
 actual={(x['pid'],x['start_ticks'])for x in v['actual_loader_aware_models']}
 known={(x.get('pid'),x.get('start_ticks'))for x in v['foreign_RAM_entries']}
 assert actual<=known,(actual-known)
 check(label+'_all_actual_model_generations_mapped',lambda:True)
 snapshots.append(dict(label=label,request=request,root=str(a.roots[request]),current_scope_registered=False,foreign_metadata_errors=v['foreign_metadata_errors'],actual_model_count=len(actual),all_actual_PID_generations_mapped=True,global_EP_active=v['global_EP_consumed_active_count'],snapshot_sha256=m.sha(N/('ACTUAL_'+label+'_RESOURCE_SNAPSHOT.json'))))
check('unknown_request',lambda:m.for_scope('UNKNOWN'),True)
a=m.for_scope(m.REQUEST_A);b=m.for_scope(m.REQUEST_B)
check('cross_scope_snapshot',lambda:b.admit(a.snapshot(),1,1),True)
f=N/'ROOT_BINDINGS_V1.json';v=json.loads(f.read_text());F=N/'bounded_negative_fixtures';F.mkdir(exist_ok=True)
for name,mutate in [('unexpected_scope',lambda q:q['request_roots'].update({'UNKNOWN':'/tmp'})),('B_cross_owner_root',lambda q:q['request_roots'].__setitem__(m.REQUEST_B,'/tmp')),('A_cross_owner_root',lambda q:q['request_roots'].__setitem__(m.REQUEST_A,str(N.parent/'three_mm/execution'))),('science_grant_in_resource_map',lambda q:q.__setitem__('scientific_permission',True))]:
 q=copy.deepcopy(v);mutate(q);p=F/(name+'.json');p.write_text(json.dumps(q,indent=2,sort_keys=True)+'\n');r=dict(path=str(p),sha256=m.sha(p));check(name,lambda r=r:m.checked_roots(r),True)
bad=dict(path=str(f),sha256='0'*64);check('roots_ref_drift',lambda:m.checked_roots(bad),True)
a=m.for_scope(m.REQUEST_A);a.roots[m.REQUEST_A]=Path('/tmp');check('mutable_scope_object_rejected',lambda:a.snapshot(),True)
d=N.parent;old=json.loads((d/'DELIVERY_MANIFEST.json').read_text());assert m.sha(d/'DELIVERY_MANIFEST.json')=='3ec68a007ca02c40b2fb01152af0fce9cfda46a892ffb237fcf8c89a9763ad64'
assert all(m.sha(x['path'])==x['sha256']for x in old['files'])
out=dict(schema='EP_V5_FINITE_THREE_SCOPE_RESOURCE_REBIND_DELTA_V1',status='PASS_CURRENT_READONLY_MAPPING_ONLY',count=len(results),results=results,snapshots=snapshots,original_D85_refs_unchanged=True,original_D85_manifest_sha256=m.sha(d/'DELIVERY_MANIFEST.json'),new_science_registered_consumed_or_models=0,shared_Native_or_foreign_mutations=False)
(N/'ACTUAL_SCOPE_SNAPSHOT_READBACK.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(dict(status=out['status'],count=len(results),scopes=snapshots,old85_unchanged=True)))
