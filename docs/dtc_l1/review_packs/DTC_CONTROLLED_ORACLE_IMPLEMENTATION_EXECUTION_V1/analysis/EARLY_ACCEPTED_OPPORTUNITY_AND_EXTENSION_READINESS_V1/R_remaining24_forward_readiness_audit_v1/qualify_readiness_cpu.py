from pathlib import Path
import ast,json,types,hashlib,copy,traceback,os
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1');B=Path('/root/data/dtc_controlled_oracle_20261106_v1');R=B/'remaining24';OUT=A/'agents/R_remaining24_forward_readiness_audit_v1';OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p):return json.loads(Path(p).read_bytes())
def load(p):
 m=types.ModuleType('cpu_'+Path(p).stem);m.__file__=str(p);exec(compile(Path(p).read_bytes(),str(p),'exec'),m.__dict__);return m
autop=B/'control/EXTENSION_AUTOMATION.p5-forward-v2.fixed.json';auto=rd(autop);template=rd(auto['build_release_template']['path']);builder=load(auto['builder']['path']);matrix=auto['matrix']['path'];draft=rd(R/'control/CPU_DRAFT_BUILD.json');tests=[]
def check(name,condition,details=None):
 assert condition,name
 tests.append(dict(name=name,status='PASS',details=details))
check('AUTOMATION_FROZEN_SHA',sha(autop)=='f245545365d6e227a927c03f0bdb5fd687a28d2ab09eb1646c38ecca7d296eb1')
check('TEMPLATE_FROZEN_SHA',sha(auto['build_release_template']['path'])=='9914d8829b9d2a512a15a0b670ba49e2f65a12d9bd5c37527bd308bab1f30de2')
check('AUTOMATION_ALL_SOURCE_PINS',all(sha(auto[k]['path'])==auto[k]['sha256']for k in ['builder','matrix','final_artifact_qualifier','build_release_template']))
check('FORWARD_DRAFT_875F_ALL_228_PINS',sha(R/'control/CPU_DRAFT_BUILD.json')=='875f13222f959986bb88533041180f88cba30070a42805216ea9bb5c06ebb02a'and len(draft['files'])==228 and all(sha(R/x['path'])==x['sha256']for x in draft['files']))
check('R24_NO_REAL_SCIENTIFIC_AUTHORITY',not(R/'control/REGISTRY_REQUEST_CANDIDATE.json').exists()and not(R/'control/SCIENCE_AUTHORIZATION.json').exists()and not(R/'control/PARENT_ADDON_ACK.json').exists())
rows=builder.validate_input(template,matrix,'remaining24',phase='cpu-draft');check('REAL_TEMPLATE_PURE_VALIDATION_96',len(rows)==96)
oldspec={p.stem:rd(p)for p in (R/'control/specs').glob('*.json')};before={str(p):sha(p)for p in [R/'control/EXECUTION_PLAN.json',R/'control/CPU_DRAFT_BUILD.json',*sorted((R/'control/specs').glob('*.json'))]}
inputpins={s['input_digest']:s['input_binding_sha256']for s in oldspec.values()}
check('ALL_24_NATIVE_INPUT_BINDINGS_PINNED',len(inputpins)==24 and all(sha(R/'control/input_bindings'/(d+'.json'))==h for d,h in inputpins.items()))
check('RESULTS_NATIVE_PARENT_EXISTS', (R/'DTC/run/results').is_dir()and os.stat(R/'DTC/run/results').st_dev==2128)
check('EXTRA_ENGINEERING_DIRS_NOT_MARKER_EXCLUSIVE',all(not x['path'].startswith('control/input_bindings/')for x in draft['files']))
# Isolated, explicitly mocked metadata builder. Never target actual native R24.
scratch=OUT/'scratch_cpu';scratch.mkdir(exist_ok=False);mockroot=scratch/'remaining24';mockroot.mkdir()
for item in draft['files']+[{'path':'control/CPU_DRAFT_BUILD.json'}]:
 p=mockroot/item['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((R/item['path']).read_bytes())
# Reproduce engineering additions; builder must retain rather than remove them.
(mockroot/'control/input_bindings').mkdir();(mockroot/'control/input_bindings/CPU_ONLY_EXTRA').write_text('not science\n');(mockroot/'DTC/run/results').mkdir(parents=True)
mockrelease=copy.deepcopy(template);mockrelease['mock']=True;mockrelease['cpu_draft_archive_root']=str(scratch/'archived_cpu_draft');builder.BASE=scratch
mockgate={'schema':'DTC_ORACLE_GATE2_REGISTRATION_RELEASE_V1','status':'PASS','released_modes':['M_DATAREAD'],'mode_releases':{'M_DATAREAD':{'status':'PASS','MOCK_ONLY':True},'L2_DATAREAD':{'status':'WAIT'},'L1_DATAREADY':{'status':'WAIT'}},'fixed8_matched_OFF_and_mode_strict_archive_restore_independently_reviewed':True,'CPU_FIXTURE_ONLY_NOT_REAL_GATE2':True}
gatepath=scratch/'MOCK_ONLY_GATE2.json';gatepath.write_text(json.dumps(mockgate,sort_keys=True,indent=2)+'\n');mockrelease['Gate2_release']={'path':str(gatepath),'sha256':sha(gatepath)};mockrelease['Gate2_mode_releases']=mockgate['mode_releases']
built=builder.build(mockrelease,matrix,'remaining24',target_root=mockroot,phase='final',finalize_draft=True)
check('ISOLATED_CPU_MOCK_FINALIZE_96_SUCCESS',built['exact_budget']==96 and built['models_started']==built['UUIDs_generated']==built['registered']==0)
plan=rd(mockroot/'control/EXECUTION_PLAN.json');candidate=rd(mockroot/'control/REGISTRY_REQUEST_CANDIDATE.json');auth=rd(mockroot/'control/SCIENCE_AUTHORIZATION.json')
check('MOCK_SAFETY_FLAGS_PRESERVED',plan['mock']is True and candidate['mock']is True)
check('CANDIDATE_BUDGET_96_ONE_USE',candidate['budget']==candidate['remaining']==96 and candidate['consumed']=={}and len(candidate['admitted_specs'])==96 and len(auth['budgets'])==96 and set(auth['budgets'].values())=={1})
check('ALL_FINAL_GENERATED_SOURCEPINS_MATCH',all(sha(x['path'])==x['sha256']for x in plan['source_pins']))
check('STANDARD_ALIASES_COPY_IDENTICAL',sha(mockroot/'control/RESULT_ENGINE_PIN.json')==sha(mockroot/'control/RESULT_ENGINE_PIN.fixed.json')and sha(mockroot/'control/RESOURCE_POLICY.json')==sha(mockroot/'control/RESOURCE_POLICY.fixed.json'))
newspec={p.stem:rd(p)for p in(mockroot/'control/specs').glob('*.json')}
check('ALL_96_EXECUTION_IDENTITIES_UNCHANGED',set(newspec)==set(oldspec)and all(builder.execution_identity(s)==builder.execution_identity(newspec[c])for c,s in oldspec.items()))
check('EXTRA_INPUT_BINDINGS_AND_RESULTS_RETAINED',(mockroot/'control/input_bindings/CPU_ONLY_EXTRA').read_text()=='not science\n'and(mockroot/'DTC/run/results').is_dir())
check('P5_FINAL_ADAPTER_PROPAGATED',plan['peer_disk_adapter']['sha256']=='1d93127340982e744c35763234e5cdcdef384c4346991cbf57869dc4491a5e10')
check('ACTUAL_DRAFT_AND_ALL_SPECS_UNCHANGED',before=={p:sha(p)for p in before})
try:builder.qualify_final_stage_artifacts(mockroot)
except AssertionError:tests.append(dict(name='MOCK_FINALQUALIFIER_REJECTS_SCIENCE_PROMOTION',status='PASS'))
else:raise AssertionError('mock qualifier wrongly authorized')
# Read the actual per-mode gate source, rather than manufacturing gate receipts.
resources=load(B/'initial8/tools/oracle_resources.py');ip=rd(B/'initial8/control/EXECUTION_PLAN.json');gate_status={}
for mode in ip['qualified_modes']:
 try:gate_status[mode]={'status':'PASS_REAL','evidence':resources.verify_mode_extension_receipt(ip,mode)}
 except resources.WaitInitialRuntimeGate as x:gate_status[mode]={'status':'WAIT_EXPECTED','reason':str(x)}
 except Exception as x:gate_status[mode]={'status':'HOLD','error':repr(x)}
check('CURRENT_GATE2_NOT_SYNTHESIZED',all(x['status']in['WAIT_EXPECTED','PASS_REAL']for x in gate_status.values()),gate_status)
# Both overlays compose for a new R24 consumer without actual attach/register.
alias=load(A/'agents/R_outbox_metadata_alias_amendment_v1/oracle_postprocess_alias.py');sparse=load(A/'agents/R_source_proven_sparse_reporting_v3/oracle_sparse_reporting.py')
consumer=alias.wrap_consumer(load(R/'tools/oracle_results.py'),R);sparse.wrap_consumer(consumer,R)
check('FUTURE_R24_OUTBOX_ALIAS_PRIVATE_HOOK',getattr(consumer.load('r24_cpu_outbox','oracle_outbox.py'),alias.MARKER,False))
st=consumer.load('r24_cpu_strict','oracle_strict.py');pop=st.load('r24_cpu_pop',R/'tools/oracle_population.py');legacy=pop.load('r24_cpu_legacy',sparse.LEGACY)
check('FUTURE_R24_STRICT_SPARSE_PRIVATE_HOOK',all(getattr(m,sparse.MARKER,False)for m in [consumer,st,pop,legacy]))
report=dict(schema='DTC_ORACLE_REMAINING24_FORWARD_READINESS_CPU_AUDIT_V1',status='PASS_CPU_READINESS_PENDING_REAL_GATE2',checks=tests,actual_scientific_builds=0,actual_scientific_registrations=0,model_starts=0,owner_mutations=0,actual_R24_DRAFT_unchanged=True,CPU_mock_root=str(mockroot),actual_gate2=gate_status,sourcepins={'builder':auto['builder'],'template':auto['build_release_template'],'automation':{'path':str(autop),'sha256':sha(autop)},'draft_marker':{'path':str(R/'control/CPU_DRAFT_BUILD.json'),'sha256':sha(R/'control/CPU_DRAFT_BUILD.json')}},mock_finalization=built)
with(OUT/'READINESS_AUDIT.json').open('x')as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(report,indent=2))
