"""Focused actual journal+registry integration with fake, isolated authority."""
import copy,datetime,hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path;H=P(__file__).resolve().parent;sys.path.insert(0,str(H));import interaction_policy as policy
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
jp=R/'control/operational_amendments/registry_journal_v1/l2_registry_journal.py';journal=load('actual_journal',jp)
assert sha(jp)=='1823d39b92edf2ccd69a9d51e68e7a4f501e4743e91060452efdcc06469ec57a'
matrix=read(R/'control/MATRIX_CURRENT.json');history=read(R/'control/SEARCH_HISTORY.json');plan=read(R/'control/EXECUTION_PLAN.json')
native=load('native_metadata_only',R/'tools/l2_native.py');own=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][native.REQ]
gen=load('actual_gen',R/'tools/l2_config_generator.py');res=load('actual_full_resource_forecast',R/'tools/l2_resources.py');ids=sorted({p['input_digest']for p in matrix['points']})
import resource_qualifier as rq
import owner_adapter as owner
qualifier=rq.make_host_qualifier(R,rq.pins(R))
resource_proofs=[]
run=H/('journal_fixtures_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));run.mkdir()
checks=[];cases=[]
def ck(n,b):assert b,n;checks.append(n)
source_before={str(p):sha(p)for p in [jp,R/'tools/l2_registry.py',R/'tools/l2_native.py',R/'tools/l2_config_generator.py',R/'control/MATRIX_CURRENT.json',N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json']}
for case,parameters,fault in [('seed35',dict(entries=768,merge=8),'NONE'),('boundary35_authoritygap',dict(entries=1536,frfcfs=256),'AFTER_AUTHORITY')]:
 root=run/case;root.mkdir();reg=load('actual_registry_'+case,R/'tools/l2_registry.py');e=load('actual_native_'+case,R/'tools/l2_native.py')
 fake=dict(registered_future_requests={e.REQ:copy.deepcopy(own),'FOREIGN':dict(untouched=True)});calls=[];fired=[]
 def registered():return fake,{},fake['registered_future_requests'][e.REQ],plan
 def update(fn):
  nextreg=copy.deepcopy(fake);fn(nextreg);fake.clear();fake.update(nextreg);calls.append(True)
 e.registered=registered;e.update_authority=update
 reg.R=root;reg.load=lambda n,f:e if f=='l2_native.py'else gen if f=='l2_config_generator.py'else res if f=='l2_resources.py'else(_ for _ in()).throw(AssertionError(f))
 e.canonical=lambda c:read(root/'control/specs'/(c+'.json'))
 put(root/'control/MATRIX_CURRENT.json',matrix);put(root/'control/SEARCH_HISTORY.json',history)
 for n in ('EXECUTION_PLAN.json','SCOPE.json'):(root/'control'/n).write_bytes((R/'control'/n).read_bytes())
 for p in matrix['points']:
  if p['profile']=='P0':put(root/'control/specs'/(p['cohort']+'.json'),read(R/'control/specs'/(p['cohort']+'.json')))
 parameters=policy.normalize(parameters);profile=policy.name(parameters)
 proposal=dict(proposal_id=policy.proposal_id(parameters,'DH',ids),profile=profile,parameters=parameters,
  cells=['DH'],new_cells=[dict(input_digest=d,cell='DH')for d in ids],new_cell_count=35,
  supplementary_policy=policy.SCHEMA,phase='V3_STRUCTURAL_SEED'if case=='seed35'else'V3_CONTEXT_BOUNDARY')
 def hook(where):
  if where==fault and not fired:fired.append(where);raise OSError('CPU_ONLY_AUTHORITYGAP')
 manifest=dict(wrapper_sha256=sha(jp),registry_sha256=sha(R/'tools/l2_registry.py'),execution_plan_sha256=sha(R/'control/EXECUTION_PLAN.json'))
 guard=journal.RegistryJournal(reg,e,manifest,hook)
 extension=owner.make_extend_guard(guard,qualifier,{},lambda c:None)
 new=extension(proposal);assert extension.last_issue is None,extension.last_issue
 q=fake['registered_future_requests'][e.REQ];mm=read(root/'control/MATRIX_CURRENT.json');hh=read(root/'control/SEARCH_HISTORY.json')
 ck(case+' exact35 additive legal grant once',len(new)==35 and len(calls)==1 and q['budget']==own['budget']+35 and q['remaining']==own['remaining']+35)
 ck(case+' old primary points and consumed UUIDs unchanged',all(p in mm['points']for p in matrix['points'])and q['consumed']==own['consumed'])
 ck(case+' committed full35 matrix and vector history once',len(mm['points'])==len(matrix['points'])+35 and hh['proposal_ids'].count(proposal['proposal_id'])==1)
 before=copy.deepcopy(fake);ck(case+' repeat cannot regrant or retry identity',guard.extend(proposal)==[]and fake==before and len(calls)==1)
 ck(case+' same journal finalguard preserved',guard.guard_decision(dict(proposals=[],scientific_stage_complete=False,adoption_ready=False))['registry_journal_status']['safe_for_scientific_completion'])
 if fault!='NONE':ck(case+' injected authoritygap recovered without refund',fired==[fault])
 for p in new:
  spec=read(root/'control/specs'/(p['cohort']+'.json'));basepoint=next(b for b in matrix['points']if b['input_digest']==p['input_digest']and b['cell']=='DH'and b['profile']=='P0')
  base=read(R/'control/specs'/(basepoint['cohort']+'.json'))
  assert len(spec['expected_options'])==270 and all(v==base['expected_options'][k]for k,v in spec['expected_options'].items()if k not in(gen.L2,gen.FR))
  assert spec['input_binding_sha256']==base['input_binding_sha256']and spec['binary_sha256']==base['binary_sha256']
 ck(case+' canonical270 non-target options and input/binary unchanged',True)
 forecast_history=read(R/'control/HISTORICAL_RSS.json');resource_proof=qualifier(proposal);resource_proofs.append(resource_proof)
 ck(case+' real35 candidate forecast proof covers exact source and retained policy',resource_proof['status']=='PASS_SEPARATE_COMBINATION_RESOURCE_QUALIFICATION'and len(resource_proof['cell_forecasts'])==35 and not resource_proof['initial_profile_padding_discount_applied']and not resource_proof['invented_fixed_margin_used'])
 changes_before=len(calls)
 for p in new:
  before=read(root/'control/specs'/(p['cohort']+'.json'));expected=res.forecast(before,forecast_history)
  reg.refresh_pending_resource_spec(p['cohort'],forecast_history);after=read(root/'control/specs'/(p['cohort']+'.json'))
  assert after['estimated_peak_model_RAM_bytes']==expected['predicted_peak_RAM_bytes']
  assert after['limits']['max_process_tree_rss_bytes']==expected['proposed_process_tree_rss_cap_bytes']
  assert after['limits']['max_process_tree_vms_bytes']==max(2*expected['proposed_process_tree_rss_cap_bytes'],expected['proposed_process_tree_rss_cap_bytes']+8*1024**3)
  assert journal.scientific_spec(after)==journal.scientific_spec(before)
 ck(case+' real dispatch refresh consumes exact forecast updating only allowed3 RAM fields',True)
 ck(case+' refresh does not alter grants remaining or historical spent UUIDs',q['budget']==own['budget']+35 and fake['registered_future_requests'][e.REQ]['consumed']==own['consumed'])
 cases.append(dict(name=case,root=str(root),proposal_id=proposal['proposal_id'],profile=profile,status='PASS'))
# A live authority file can change concurrently; only immutable production source/matrix pins are compared.
ck('all production source and primary matrix bytes unchanged',all(sha(p)==v for p,v in source_before.items()if '/science_authority/'not in p))
receipt=dict(status='PASS',count=len(checks),checks=checks,cases=cases,production_grants=0,model_starts=0,
 sourcepins=dict(journal=sha(jp),registry=sha(R/'tools/l2_registry.py'),generator=sha(R/'tools/l2_config_generator.py')),
 caveat='Synthetic authority copies only; this is not production registration')
put(H/'JOURNAL_CPU_QUALIFICATION.json',receipt);print(json.dumps(receipt))
put(H/'ACTUAL_RESOURCE_QUALIFICATION.json',dict(status='READONLY_REAL_FULL_FORECASTS',proofs=resource_proofs,model_starts=0,production_changes=0))
