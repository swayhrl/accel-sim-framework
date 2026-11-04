from pathlib import Path as P
import json,hashlib
V=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1/activation_20261104_v1');F=V/'agent_a_formal';R=V/'runtimes/midtag';C=V/'agent_c_resources'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def put(p,d):P(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
refs=[ref(C/n)for n in ['resources_midtag.py','resources_v3.py','RESOURCE_POLICY_CAP10.json']]
assert refs[0]['sha256']=='a43cc5a3e2154dbcded819e73fcb6d4391672304e52497b3110c9e42176cc6a2'
assert refs[1]['sha256']=='ebaacc5efecf4e2162532b0722822763df55fb5cab05dbec0e0eaa161e6465bd'
assert refs[2]['sha256']=='6efb40ce41fb3b0d8e91ae318dd7a132f0846d6ea6c607015177692798dcb5bb'
for p in(F/'spec_candidates').glob('*.json'):
 d=json.loads(p.read_text());d['resource_module_ref']=refs[0];d['resource_policy_ref']=refs[2];d['resource_qualification_ref']=ref(C/'CPU_RESOURCE_QUALIFICATION.json')
 for r in refs:d['pinned_files'][r['path']]=r['sha256']
 put(p,d)
p=F/'review_drafts/MAIN_HOST_QUALIFICATION_DRAFT.json';d=json.loads(p.read_text())
seen={r['path']for r in d['modules']}
for r in refs:
 if r['path']not in seen:d['modules'].append(r)
d['resource_qualification_ref']=ref(C/'CPU_RESOURCE_QUALIFICATION.json');d['resource_policy_ref']=refs[2]
d['fresh_formal_Host_evidence_ref']=ref(F/'FORMAL_DRY_HOST_RECEIPT.json');put(p,d)
# Seal helper also requires the immutable shared resource implementation/policy in Main review and runtime pins.
p=F/'seal_formal_specs.py';t=p.read_text();needle=" needed +=[V/'activation_20261104_v1/agent_d_execution/native_route_guard_v3.py',V/'activation_20261104_v1/agent_d_execution/safe_native_core_v3.py',P(args.resource_module)]"
assert needle in t;t=t.replace(needle,needle+"\n needed +=[P(args.resource_module).with_name('resources_v3.py'),P(args.resource_policy)]");p.write_text(t)
state=json.loads((F/'PREPARATION_STATE.json').read_text());state.update(status='FORMAL_RUNTIME_READY_RESOURCE_CAP10_BOUND_PENDING_MAIN_REVIEW_AND_SEAL',resource_module_ref=refs[0],resource_policy_ref=refs[2],resource_qualification_ref=ref(C/'CPU_RESOURCE_QUALIFICATION.json'),formal_Host_proof_ref=ref(F/'FORMAL_DRY_HOST_RECEIPT.json'));put(F/'PREPARATION_STATE.json',state)
print(json.dumps(dict(status=state['status'],engine_ref=ref(R/'ep_perf_native_wv_modes_draft.py'),host_draft_ref=ref(F/'review_drafts/MAIN_HOST_QUALIFICATION_DRAFT.json'))))

