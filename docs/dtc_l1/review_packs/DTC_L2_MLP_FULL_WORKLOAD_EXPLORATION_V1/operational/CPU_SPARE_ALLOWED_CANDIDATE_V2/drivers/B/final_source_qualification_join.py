import pathlib,json,hashlib
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');B=A/'agents/B/cpu_spare_policy_review_v2';D=A/'agents/A/cpu_spare_memory_v2/candidate'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
qa=read(D/'CPU_JOINT_QUALIFICATION.json');prior=read(B/'B_LIMITED_INTERFACE_REVIEW.json');template=read(D/'INSTALL.template.json')
qp=D/'CPU_JOINT_QUALIFICATION.json';assert sha(qp)=='cccf33ca7d321f951c2bd4ea6acdb9077046fa7e2d57911aff0d9a92bc19facd'
paths={r:P(template[r+'_path'])for r in qa['qualified_sources']};paths.update(library=A/'agents/A/cpu_spare_memory_v2/cpu_memory.py',owner=A/'agents/E/cpu_spare_execution_v2/cpu_owner.py',extra_strict=A/'agents/E/cpu_spare_execution_v2/cpu_extra_strict.py')
actual={r:sha(p)for r,p in paths.items()}
assert actual==qa['qualified_sources'],dict(actual=actual,expected=qa['qualified_sources'])
delta=read(B/'FINAL_494_533_DELTA_REVIEW.json');assert delta['status']=='PASS'and delta['extra_AST_identical_to_qualified932']
assert prior['source_sha256']['library']==qa['qualified_sources']['library']
assert all(delta['source_sha256'][r]==qa['qualified_sources'][r]for r in ['owner','extra_strict'])
assert qa['status']=='PASS'and qa['native_prefix_qualified']and qa['joint_strict_qualified']and not qa['remaining_requirements']
for name in['library','owner','strict','actual_canary']:
 e=qa['evidence'][name];assert sha(e['path'])==e['sha256']
assert len(prior['checks'])==6 and all(x['status']=='PASS'for x in prior['checks'])
prep=read(D/'PREPARATION_RECEIPT.json');assert prep['status']=='QUALIFIED_CANDIDATE_NOT_INSTALLED'and not prep['remaining_requirements']
out=dict(schema='B_CPU2_FINAL_LIMITED_INDEPENDENT_REVIEW_V1',status='PASS',qualified_sources=qa['qualified_sources'],source_paths_reviewed={r:str(p)for r,p in paths.items()},joint_qualification=dict(path=str(qp),sha256=sha(qp)),limited_checks=dict(path=str(B/'B_LIMITED_INTERFACE_REVIEW.json'),sha256=sha(B/'B_LIMITED_INTERFACE_REVIEW.json'),count=6),actual_natural_canary_approval=qa['evidence']['actual_canary'],qualification_evidence=qa['evidence'],review_scope='Limited six interface/static checks plus exact immutable source6 and final qualification join; CPU sampler/quota math not rerun.',limitations=['Does not constitute production installation or broad-release authorization.','Existing owner CPU qualification supplies isolated replacement/rollback integration; independent rollback check is source-level.','Future production generations must retain immutable launch snapshots and historical strict sources; ACTIVE_MEMORY is a mutable routing pointer.'],blocking_findings=[],new_models=0,new_grants=0,production_changes=0,signals=0,broad_release_approved=False)
out['qualification_evidence']=dict(out['qualification_evidence']);out['qualification_evidence'].pop('independent_review',None)
out['delta_review']=dict(path=str(B/'FINAL_494_533_DELTA_REVIEW.json'),sha256=sha(B/'FINAL_494_533_DELTA_REVIEW.json'),behavioral_delta_checks=2,extra_AST_identical=True)
out['review_scope']='Six original limited interface/static checks bound to d98/fdd/932, plus two independent behavioral delta checks and AST equality for final d98/494/533; exact final six-source/qualification join. CPU sampler/quota math not rerun.'
out['source_join_drift_preimage']=dict(path=str(B/'FINAL_SOURCE_JOIN_HOLD.json'),sha256=sha(B/'FINAL_SOURCE_JOIN_HOLD.json'),resolution='A reassembled final qualification against stopped final sources; original HOLD retained.')
f=B/'B_FINAL_INDEPENDENT_REVIEW.json';f.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(path=str(f),sha256=sha(f),status=out['status'],joint_qualification_sha256=sha(qp))))
