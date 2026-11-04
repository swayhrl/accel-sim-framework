from pathlib import Path
import sys,types,json,hashlib,copy
sys.dont_write_bytecode=True
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1');O=A/'agents/A_remaining28_runtime_source_draft_v1';F=O/'fixtures/C_receipt_CPU_ONLY';F.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,sort_keys=True)+'\n')
def load(p):m=types.ModuleType('CPU_ONLY_'+p.stem);m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
r=load(O/'perf28_terminal_gate_receipt.py');r.FIRST4=F/'first4';r.OUTPUT=F/'Cgate/C_FIRST4_TERMINAL_GATE.json';r.OUTPUT.parent.mkdir(exist_ok=True);tag=F/'Tag_CPU_ONLY.json';put(tag,dict(CPU_only=True));validator=types.SimpleNamespace(PLAN_SHA='CPU_plan',CANDIDATE_SHA='',TAG_SHA=sha(tag),TAG_MANIFEST=tag,live_generation=lambda packet:False);put(r.FIRST4/'control/REGISTRY_REQUEST_CANDIDATE.json',dict(CPU_only=True));validator.CANDIDATE_SHA=sha(r.FIRST4/'control/REGISTRY_REQUEST_CANDIDATE.json')
fields=json.loads((A/'agents/A_remaining28_owner_resource_v1/REMAINING28_RESOURCE_SPEC_FIELDS.json').read_text())['points'];digests={x['program']:x['input_digest']for x in fields};cohorts=['E2-DTCPF4-'+digests[p][:16]+'-DH-PHYS768-V1'for p in ['2DCONV','GEMM','MVT','BICG']]
def reset():
 q=dict(execution_plan_sha256='CPU_plan',consumed={});g=dict(schema=r.SCHEMA,status='PASS',gate_passed=True,validator_source_path=str(r.VALIDATOR_SOURCE),validator_source_sha256=r.VALIDATOR_SHA,request=r.FIRST4_REQ,budget=4,consumed=4,remaining=0,model_starts=0,registry_writes=0,owner_actions=0,not_a_REQ28_registration_or_extra_grant=True,execution_plan_sha256='CPU_plan',registry_candidate_sha256=validator.CANDIDATE_SHA,Tag16_review_manifest_sha256=sha(tag),Tag16_review_manifest_path=str(tag),points={})
 for prog,c in zip(['2DCONV','GEMM','MVT','BICG'],cohorts):
  uid='CPU_ONLY_'+prog;out=r.FIRST4/'DTC/run/results'/uid;spec=r.FIRST4/'control/specs'/(c+'.json');result=r.FIRST4/'analysis'/(c+'.RESULT.json');put(spec,dict(CPU_only=True,program=prog,input_digest=digests[prog]));put(result,dict(CPU_only=True,cycles=1));paths=[result,r.FIRST4/'control/qualification_ledger'/(c+'.INTENT.json'),r.FIRST4/'control/qualification_ledger'/(c+'.DONE.json'),r.FIRST4/'control'/(c+'_ARCHIVE_RECEIPT.json'),out/'NATIVE_EXIT.json',out/'L2_STRICT.json',spec]
  for p in paths[1:-1]:put(p,dict(CPU_only=True))
  put(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',dict(CPU_only=True,pid=0,start_ticks=0));refs={}
  for j in range(6):p=F/'metadata'/(c+str(j)+'.json');put(p,dict(CPU_only=True));refs[str(p)]=sha(p)
  ap=r.OUTPUT.parent/(c+'.FULL_ARCHIVE_NATIVE_REHASH.json');put(ap,dict(CPU_only=True,status='PASS_FULL_CHUNK_SOURCE_NATIVE_TYPED_REHASH',typed_entry_count=1,typed_entries=[dict(CPU_only=True)],metadata_references=refs));q['consumed'][c]=dict(uuid=uid);g['points'][c]=dict(uuid=uid,program=prog,input_digest=digests[prog],cycles=1,strict_reexecuted=True,natural_nonlive=True,archive_native_full_rehash=True,closure_file_sha256={str(p):sha(p)for p in paths},archive_native_proof=dict(path=str(ap),sha256=sha(ap)),typed_entry_count=1,metadata_references=refs)
 return g,q
checks=[]
def case(name,mutator=None,expected=False):
 g,q=reset()
 if mutator:mutator(g,q)
 try:r.validate_document(g,q,validator);passed=True
 except(AssertionError,FileNotFoundError,KeyError):passed=False
 assert passed==expected,name;checks.append(dict(name=name,PASS=True,synthetic_document_accepted=passed))
c=cohorts[0]
case('valid_synthetic_consumer_document',expected=True)
case('schema_mismatch',lambda g,q:g.update(schema='wrong'))
case('not_PASS',lambda g,q:g.update(status='HOLD'))
case('not_gate_passed',lambda g,q:g.update(gate_passed=False))
case('wrong_validator_source_pin',lambda g,q:g.update(validator_source_sha256='wrong'))
case('wrong_origin_request',lambda g,q:g.update(request='REQ28'))
case('wrong_budget',lambda g,q:g.update(budget=28))
case('wrong_plan',lambda g,q:g.update(execution_plan_sha256='wrong'))
case('wrong_candidate',lambda g,q:g.update(registry_candidate_sha256='wrong'))
case('wrong_Tag_pin',lambda g,q:g.update(Tag16_review_manifest_sha256='wrong'))
case('wrong_UUID',lambda g,q:g['points'][c].update(uuid='wrong'))
case('strict_not_reexecuted',lambda g,q:g['points'][c].update(strict_reexecuted=False))
case('fullarchive_flag_false',lambda g,q:g['points'][c].update(archive_native_full_rehash=False))
case('closure_path_missing',lambda g,q:g['points'][c]['closure_file_sha256'].pop(next(iter(g['points'][c]['closure_file_sha256']))))
case('closure_SHA_drift',lambda g,q:g['points'][c]['closure_file_sha256'].update({next(iter(g['points'][c]['closure_file_sha256'])):'wrong'}))
case('independent_archive_proof_SHA_drift',lambda g,q:g['points'][c]['archive_native_proof'].update(sha256='wrong'))
case('metadata_SHA_drift',lambda g,q:g['points'][c]['metadata_references'].update({next(iter(g['points'][c]['metadata_references'])):'wrong'}))
case('cycles_identity_drift',lambda g,q:g['points'][c].update(cycles=2))
validator.live_generation=lambda packet:True;case('live_generation_rejected');validator.live_generation=lambda packet:False
# Family state machine is input fixed and never uses cycles/speedup.
ops=load(O/'perf28_ops.py');points=fields;seeds=ops.family_seeds(points);state={p:dict(state='QUALIFIED'if p=='PHYS768_TAG64x8'else'PENDING')for p in ops.FAMILY_VARIANTS}
def check(name,b):assert b,name;checks.append(dict(name=name,PASS=True))
check('initial4phys_plus3own_seeds_eligible',sum(ops.eligible_for_family(x,state,seeds)for x in points)==7)
p='OO_PIB192';state[p]=ops.update_family_state(state[p],dict(state='QUALIFIED',reason='CPU_RUNTIME_FIXTURE'));check('own_family_releases_without_waiting_other2',sum(ops.eligible_for_family(x,state,seeds)for x in points)==14)
p='PHYS1024_TAG64x8';state[p]=ops.update_family_state(state[p],dict(state='FAILED',reason='CPU_FAILURE_FIXTURE'));check('failed_family_all_unused_not_eligible',not any(ops.eligible_for_family(x,state,seeds)for x in points if x['profile']==p));check('other_qualified_family_kept',all(ops.eligible_for_family(x,state,seeds)for x in points if x['profile']=='OO_PIB192'))
check('pending_postprocess_does_not_revoke_prior_healthy_qualification',ops.update_family_state(state['OO_PIB192'],dict(state='PENDING'))==state['OO_PIB192']);check('failure_state_sticky_no_automatic_seed_retry',ops.update_family_state(state['PHYS1024_TAG64x8'],dict(state='QUALIFIED'))['state']=='FAILED');check('each_seed_is_original_vectorAdd',all(next(x for x in points if x['cohort']==co)['program']=='vectorAdd'for co in seeds.values()))
text=(O/'perf28_ops.py').read_text();check('partial_terminal_keeps_budget_and_specs',"own['budget']==28"in text and "own['remaining']==28-len(own['consumed'])"in text and "own['state']='STOP_UNACCEPTED'"in text and 'no_budget_refund=True'in text and 'no_spec_removal=True'in text)
(O/'C_RECEIPT_AND_FAMILY_GATE_CPU_QUALIFICATION.json').write_text(json.dumps(dict(status='PASS_CPU_ONLY',n=len(checks),tests=checks,synthetic_receipts_only=True,actual_C_audit_or_output_created=False,actual_native_models=0,actual_registry_writes=0,actual_services=0,source_pins=[dict(path=str(O/n),sha256=sha(O/n))for n in ['perf28_terminal_gate_receipt.py','perf28_ops.py']]),indent=2)+'\n');print('RECEIPT_FAMILY_CPU',len(checks),'PASS')
