from pathlib import Path
import json,hashlib,copy,importlib.util,datetime,ast
B=Path(r'D:/repo/artifacts/dtc-l2-mlp-full-workload-exploration-v1/agents/B/A-independent-review-by-B-v1');A=B/'A_SNAPSHOT';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_bytes());checks=[]
def ck(n,x):
 assert x,n
 checks.append(n)
def reject(n,fn):
 try:fn()
 except (RuntimeError,AssertionError,KeyError):checks.append(n);return
 raise AssertionError(n+' accepted')
s=importlib.util.spec_from_file_location('independent_A_future_memory',A/'future_memory.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);G=1024**3
manifest=read(A/'MANIFEST.json');qa=read(A/'CPU_QUALIFICATION.json')
ck('exact_requested_manifest',sha(A/'MANIFEST.json')=='f2f3373a43d802fc885eebb20c3d8e86d7ea672978acaacd492bcb6793631fe7')
ck('exact_requested_97QA',sha(A/'CPU_QUALIFICATION.json')=='9229440dfaea36b2f929bb7c17dc40ffb3e5c4a986979e75920f107dedc98679'and qa['total_checks']==97)
ck('every_manifest_member_bytes_and_SHA',all((A/x['pack_path']).stat().st_size==x['bytes']and sha(A/x['pack_path'])==x['sha256']for x in manifest['entries']))
ck('six_code_files_join_QA_and_manifest',qa['qualified_sources']==manifest['qualified_sources']and all(sha(A/n)==qa['qualified_sources'][r]for r,n in dict(library='future_memory.py',frontend='memory_frontend.py',owner='memory_owner.py',extra_strict='memory_extra_strict.py',joint_padding='joint_padding_strict.py',joint_io='joint_io_strict.py').items()))
snaps=[read(p)for p in A.rglob('FUTURE_MEMORY_ADMISSION_SNAPSHOT.json')]
proofs=[p for sn in snaps if not sn['padding_optin']for p in sn['fresh_preflights']]
p=proofs[-1];base=p['base_resource_snapshot'];out=m.project(base);proof=out['additional_future_memory_admission_proof'];m.verify_memory_proof(proof)
ck('noflag_complete_peer_own_growth_once',sum(r['additional_reserved_bytes']for r in base['RAM_reservation_entries'])+sum(r['additional_reserved_bytes']for r in base['own_ram_forecasts'])==proof['growth_unchanged_bytes']==base['total_projected_additional_RAM_bytes'])
ck('project_keeps_growth_and_original_snapshot',out['total_projected_additional_RAM_bytes']==base['total_projected_additional_RAM_bytes']and proof['base_resource_snapshot']==base)
ck('formula_host_bound_95_floor10',m.budget(dict(host_MemAvailable_bytes=100*G,cgroup_effective_headroom_bytes=None))==int(90*G*.95))
ck('formula_cgroup_bound_95_floor10',m.budget(dict(host_MemAvailable_bytes=100*G,cgroup_effective_headroom_bytes=50*G))==int(40*G*.95))
ck('formula_below_floor_no_budget',m.budget(dict(host_MemAvailable_bytes=9*G,cgroup_effective_headroom_bytes=50*G))==0)
for name,mutate in [('missing_peer_growth',lambda x:x['base_resource_snapshot']['RAM_reservation_entries'].append(dict(additional_reserved_bytes=123))),('double_growth',lambda x:x.update(growth_unchanged_bytes=x['growth_unchanged_bytes']*2)),('alter_budget',lambda x:x['effective_decision'].update(admission_RAM_budget_bytes=x['effective_decision']['admission_RAM_budget_bytes']+1)),('disk_gate_false',lambda x:x.update(disk_and_own_bound_pass=False)),('pressure_preserved',lambda x:x['pressure_reasons'].append('cpu_pressure_full'))]:
 x=copy.deepcopy(proof);mutate(x);reject(name,lambda:m.verify_memory_proof(x))
x=copy.deepcopy(base);x['admission_decision']['pressure_reasons']=['cpu_pressure_full'];ck('actual_project_cannot_override_CPU_pressure',not m.project(x)['physical_RAM_pass'])
runtime=object();seen=[]
f=m.wrap_resources(lambda spec,fresh:(seen.append(fresh)or runtime));ck('runtimeFalse_returns_identical_original_object',f({},False)is runtime and seen==[False])
# Do not execute terminal(): its sidecar publication is intentionally outside this read-only review.
ck('joint_padding_replay_retains_full_row_math',all(x in (A/'joint_padding_strict.py').read_text()for x in ["expected_claims={x['cohort']for x in rows if x['kind']=='CLAIM_OR_CANDIDATE'}","old=sum(x['additional_reserved_bytes']for x in rows)+sum(x['additional_reserved_bytes']for x in proof['base_peer_RAM_rows'])","new=old-computed+total_topup","assert proof['effective_decision']['pass_admission'] is(new<=oldbudget)"]))
r=dict(schema='A_FUTURE_MEMORY_INDEPENDENT_REVIEW_BY_B_V1',status='PASS_REVIEW_NO_BLOCKING_DEFECT_FOUND',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks,passed=len(checks),reviewed_manifest_sha256=sha(A/'MANIFEST.json'),reviewed_qualification_sha256=sha(A/'CPU_QUALIFICATION.json'),source_sha256=qa['qualified_sources'],production_mutations=0,real_models_started=0,large_97_fixture_reexecuted=False,terminal_sidecars_not_written=True,scope='Independent static review plus isolated pure arithmetic/runtimeFalse tests. Does not certify actual canary completion or production installation.')
(B/'INDEPENDENT_CHECKS.json').write_text(json.dumps(r,indent=2)+'\n',encoding='ascii');print(json.dumps(r))
