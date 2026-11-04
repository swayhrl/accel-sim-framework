from pathlib import Path as P
import json,hashlib
V=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1');F=V/'activation_20261104_v1/agent_a_formal';R=V/'activation_20261104_v1/runtimes/midtag';D=V/'activation_20261104_v1/agent_d_execution'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def put(p,d):P(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
guard=ref(D/'native_route_guard_v3.py');assert guard['sha256']=='9df2bab0058b571466998f71bfa487a929b6718a0d7e56d347746e98d6208ca9'
safe=ref(D/'safe_native_core_v3.py')
p=R/'ep_perf_native_wv_modes_draft.py';t=p.read_text();needle="LEDGER = NATIVE / 'control/qualification_ledger'\n";assert needle in t;t=t.replace(needle,needle+'NATIVE_ROUTE_GUARD_REF='+repr(guard)+'\n')
needle="    guard=module(route['guard_module_ref'],'midtag_formal_native_route_guard')\n";assert needle in t;t=t.replace(needle,"    need(route.get('guard_module_ref')==NATIVE_ROUTE_GUARD_REF,'pinned route guard mismatch')\n"+needle)
needle="    formal_mode_contract(s)\n";t=t.replace(needle,needle+"    need(s.get('native_route_guard_ref')==NATIVE_ROUTE_GUARD_REF,'spec route guard binding')\n")
needle="    decision = resources.admit(snapshot, additional, writes, policy=policy)\n";assert needle in t;t=t.replace(needle,"    decision = resources.admit(snapshot, additional, writes, policy=dict(policy,requested_host_cpu=binding['host_cpu']))\n");p.write_text(t)
for p in (F/'spec_candidates').glob('*.json'):
 d=json.loads(p.read_text());d['host_engine_ref']=ref(R/'ep_perf_native_wv_modes_draft.py');d['native_route_guard_ref']=guard
 for r in [d['host_engine_ref'],guard,safe]:d['pinned_files'][r['path']]=r['sha256']
 put(p,d)
p=F/'review_drafts/MAIN_HOST_QUALIFICATION_DRAFT.json';d=json.loads(p.read_text())
for r in d['modules']:r['sha256']=sha(r['path'])
d['modules'] += [guard,safe];put(p,d)
print('D immutable route guard and C requestedCPU interface pinned')

