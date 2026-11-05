from pathlib import Path
import ast,copy,hashlib,importlib.util,json,os,sys,types
HERE=Path(__file__).parent
def load(p,name):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
p=load(HERE/'prepare_a_activation.py','A_patch_test');original={r['path']:Path(r['path']).read_bytes()for r in p.PLAN['changed_files']}
ar=p.read(HERE.parent/'control/A_MAIN_HOST_DELTA_APPROVAL_REF.json');approval=p.exact(ar);payload=p.build_payload(original,approval,ar)
def vbytes(path):return payload.get(str(path),Path(path).read_bytes())
def vsha(path):return hashlib.sha256(vbytes(path)).hexdigest()
def vread(path):return json.loads(vbytes(path))
def vref(path):return dict(path=str(path),sha256=vsha(path))
def vexact(r):
 assert vsha(r['path'])==r['sha256'];return vread(r['path'])
def vm(r,name):
 assert vsha(r['path'])==r['sha256'];m=types.ModuleType(name);m.__file__=r['path']
 exec(compile(vbytes(r['path']),r['path'],'exec'),m.__dict__)
 for k,v in [('sha',vsha),('read',vread),('ref',vref),('exact',vexact),('module',vm)]:
  if hasattr(m,k):setattr(m,k,v)
 return m
sys.path.insert(0,str(p.R));e=vm(vref(p.R/'ep_perf_native_wv_modes_draft.py'),'A_virtual_engine')
scases={vread(path)['cohort']:vread(path)for path in payload if path.endswith('/control/FROZEN_SPEC.json')}
mock=dict(budget=3,remaining=3,consumed={},admitted_specs={c:vsha(e.spec_path(c))for c in scases},authorization_ref=next(iter(scases.values()))['Main_scientific_launch_authorization'],runtime_versions={vsha(p.R/'ep_perf_native_wv_modes_draft.py'):dict(engine_ref=vref(p.R/'ep_perf_native_wv_modes_draft.py'),common_ref=vref(p.R/'ep_perf_common_v2.py'))})
e.authority=lambda:(dict(registered_future_requests={p.PLAN['request_id']:mock}),{})
rows=[]
for c in reversed(sorted(scases)): # optimization can release first, no accepted predecessor
 s=e.spec_for(c);assert s['limits']['wall_seconds']==28800 and len(s['expected_effective_options'])==283
 rows.append(dict(cohort=c,pass_independent_spec_release_without_any_consumed_predecessor=True))
# Newly changed metadata does not alter protected execution/monitor mechanics.
def funcs(b):return {n.name:ast.dump(n,include_attributes=False)for n in ast.parse(b).body if isinstance(n,ast.FunctionDef)}
before=funcs(original[str(p.R/'ep_perf_native_wv_modes_draft.py')]);after=funcs(payload[str(p.R/'ep_perf_native_wv_modes_draft.py')])
kept=['run_native','verify_actual','resource_gate','fresh_input','dispatch_binding'];assert all(before[k]==after[k]for k in kept)
negatives=[]
for name,change in [
 ('hardwall3600',lambda a:a.update(hard_wall_seconds=3600)),
 ('wrongSource',lambda a:a['Source5'].update(binary_sha256='0'*64)),
 ('pointBudget2',lambda a:a['per_cohort_budget'].update({p.PLAN['exact_cohorts'][0]:2})),
 ('extraCohort',lambda a:a['allowed_cohorts'].append('EP_PERF_FOREIGN')),
 ('dependentRelease',lambda a:a.update(independent_release=False)),
 ('wrongRequest',lambda a:a.update(request_id='FOREIGN')),
]:
 bad=copy.deepcopy(approval);change(bad)
 try:p.reviewed(bad,ar)
 except Exception as exc:negatives.append(dict(case=name,pass_reject=True,reason=str(exc)))
 else:raise AssertionError(name)
# Full guard+sealed-entry finite route wiring fixture. No shared Native is read/written.
F=HERE/'guard_cpu_fixture';F.mkdir(exist_ok=True)
(F/'native_route_guard.py').write_bytes(payload[str(p.R/'native_route_guard_v3.py')])
(F/'safe_native_core_v3.py').write_bytes((p.R/'safe_native_core_v3.py').read_bytes())
(F/'shared_native').write_bytes(b'#!/bin/sh\nset -eu\n')
(F/'frontend.py').write_bytes(b'# CPU fixture, no actors\n')
(F/'entry').write_bytes(b'#!/usr/bin/python3\nraise SystemExit(0)\n')
def fr(path):return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
contract=dict(schema='EP_MAIN_V3_SHARED_ROUTE_CONTRACT_V1',installed_baseline_ref=fr(F/'shared_native'),reviewed_foreign_insertions=[],CPU_FIXTURE_NOT_AUTHORITY=True)
(F/'contract.json').write_text(json.dumps(contract))
base=dict(status='MAIN_INSTALLED_ADDITIVE_NATIVE_EP_PERF_ROUTE',approved_by='EP-MAIN',scientific_scope_activated=True,goal=p.PLAN['request_id'],exact_cohorts=p.PLAN['exact_cohorts'],shared_route_contract_ref=fr(F/'contract.json'),global_shared_native_ref=fr(F/'shared_native'),entry_ref=fr(F/'entry'),frontend_ref=fr(F/'frontend.py'),guard_module_ref=fr(F/'native_route_guard.py'),owned_runtime_pins=[fr(F/'frontend.py'),fr(F/'native_route_guard.py')],CPU_FIXTURE_NOT_AUTHORITY=True)
g=load(F/'native_route_guard.py','A_guard_delta')
def guard(row):
 (F/'route.json').write_text(json.dumps(row));return g.validate_current(str(F/'route.json'))
assert guard(base)['status']=='PASS'
fd,receipt=g.sealed_entry(str(F/'route.json'));assert os.read(fd,4096)==(F/'entry').read_bytes();os.close(fd)
guardNeg=[]
for name,change in [
 ('D3MM',lambda r:r.update(exact_cohorts=['EP_PERF_PFV4_A2_3MM_S_G64W8_V1','EP_PERF_PFV4_A2_3MM_WV_ZERO_RO_G64W8_V1','EP_PERF_PFV4_A2_3MM_WV_ZERO_RO_REF32W8_V1'])),
 ('foreignRequest',lambda r:r.update(goal='FOREIGN')),
 ('missingPoint',lambda r:r.update(exact_cohorts=r['exact_cohorts'][:2])),
 ('duplicatePoint',lambda r:r.update(exact_cohorts=[r['exact_cohorts'][0]]*3)),
 ('extraPoint',lambda r:r['exact_cohorts'].append('EP_PERF_FOREIGN')),
 ('missingGuardPin',lambda r:r.update(owned_runtime_pins=r['owned_runtime_pins'][:1])),
 ('wrongOwnedSHA',lambda r:r['owned_runtime_pins'][0].update(sha256='0'*64)),
 ('unactivated',lambda r:r.update(scientific_scope_activated=False)),
]:
 row=copy.deepcopy(base);change(row)
 try:guard(row)
 except Exception as exc:guardNeg.append(dict(case=name,pass_reject=True,reason=str(exc)))
 else:raise AssertionError(name)
# Shared/owned files of real graph are untouched by the entire test.
assert all(Path(path).read_bytes()==b for path,b in original.items())
result=dict(schema='EP_PFV5_A_ACTIVATION_DELTA_CPU_V1',independent_scope_cases=rows,approval_negative_cases=negatives,guard_positive_and_sealed_entry=True,guard_negative_cases=guardNeg,AST_preserved=kept,latest_resource_ref_preserved=p.PLAN['expected_resource_module_ref'],real_graph_unchanged=True,Native_or_registry_writes=0,scientific_starts=0,fixture_is_not_Main_activation=True)
(HERE/'ACTIVATION_DELTA_TEST_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(independent_scope_pass=len(rows),approval_negative_pass=len(negatives),guard_negative_pass=len(guardNeg),sealed_entry=True,models=0)))
