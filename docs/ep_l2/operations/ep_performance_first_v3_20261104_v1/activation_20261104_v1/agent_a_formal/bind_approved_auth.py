from pathlib import Path as P
import json,hashlib
V=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1');F=V/'activation_20261104_v1/agent_a_formal';R=V/'activation_20261104_v1/runtimes/midtag';DATA=P('/root/data/ep_l2_full_workload_performance_20261027_v1/execution_midtag_v3_20261104_v1/midtag')
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def put(p,d):P(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
p=R/'ep_perf_native_wv_modes_draft.py';t=p.read_text().replace("authorization.get('source_identity')==s['source_identity']","authorization.get('Source5')==s['source_identity']")
needle="    need(authorization.get('Source5')==s['source_identity'],'authorization Source5 binding')\n"
t=t.replace(needle,needle+"    need(s.get('Main_scientific_launch_authorization')==q['authorization_ref'],'exact authorization/spec binding')\n")
p.write_text(t)
for p in (F/'spec_candidates').glob('*.json'):
 d=json.loads(p.read_text());d['host_engine_ref']=ref(R/'ep_perf_native_wv_modes_draft.py');d['pinned_files'][str(R/'ep_perf_native_wv_modes_draft.py')]=sha(R/'ep_perf_native_wv_modes_draft.py');d['Main_scientific_launch_authorization']=ref(DATA/'control/USER_AUTHORIZATION.json');d['scientific_scope_approved']=True;d['approved_contract_commit']='881a4f07a190af519c61a02614866d95b68b0de3';put(p,d)
p=F/'review_drafts/MAIN_HOST_QUALIFICATION_DRAFT.json';d=json.loads(p.read_text())
for r in d['modules']:r['sha256']=sha(r['path'])
put(p,d)
print('approved scoped Source5/user contract bound; no authority writes')

