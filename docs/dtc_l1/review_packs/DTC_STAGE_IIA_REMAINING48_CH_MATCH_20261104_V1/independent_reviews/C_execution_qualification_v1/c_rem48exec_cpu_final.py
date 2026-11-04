from pathlib import Path
import json,hashlib,datetime,sys,importlib.util,types,copy,os,ast,gzip,re,subprocess,traceback
sys.dont_write_bytecode=True
R=Path('/root/data/dtc_stage_iia_remaining48_20261104_v1');A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');O=A/'agents/C_execution_qualification_v1';F=O/('CPU_FINAL_FIXTURES_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));F.mkdir(exist_ok=False);rd=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();checks=[]
def ck(n,b,detail=None):checks.append({'check':n,'PASS':bool(b),'detail':detail});assert b,n

def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def fails(name,fn):
 try:fn()
 except (AssertionError,RuntimeError,KeyError,FileNotFoundError,ValueError,TypeError)as err:ck(name,True,{'expected_rejection':type(err).__name__+':'+str(err)[:180]});return
 raise AssertionError('EXPECTED_REJECTION '+name)
plan=rd(R/'control/EXECUTION_PLAN.json');q=rd(R/'control/REGISTRY_REQUEST_CANDIDATE.json');REQ=q['request'];N=Path('/root/data/ep_l2_dtc_l1_native_v2');actualReg=rd(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');actualEpoch=rd(N/'control/CURRENT_SCIENCE_EPOCH.json');oldfileHashes={str(p):sha(p)for p in [N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json',N/'control/CURRENT_SCIENCE_EPOCH.json',Path('/root/data/dtc_main_v100_sweep_20261025_v1/control/BATCH_LEASE.json'),N/'bin/native']};beforebind=list((R/'control/dispatch_bindings').glob('*'));beforeintent=list((R/'control/qualification_ledger').glob('*'))
ck('ExactRoot finalplan/candidateSHA and122livepins',sha(R/'control/EXECUTION_PLAN.json')=='9f257eeea3ebe81610a88cef8ad37512b54bdb50728f965e8d73ccf5dd89a4b3'and sha(R/'control/REGISTRY_REQUEST_CANDIDATE.json')=='6f7aa38a351e58e0711cba1a2aabe5df916cc05fe3968e9fc70d595df6490703'and len(plan['source_pins'])==122 and all(sha(p['path'])==p['sha256']for p in plan['source_pins']))
ck('Exact48authorization nooldbudget/newextras',q['budget']==q['remaining']==48 and not q['consumed']and q['all_other_candidate_grants']==0 and q['old_request_budget_reused']is False and q['new_registration_only']and q['model_automatic_retries']==0 and REQ not in actualReg['registered_future_requests'])
M=rd(R/'control/MATRIX.json');auth=rd(R/'control/SCIENCE_AUTHORIZATION.json');ck('Exact48 onecredit whitelist andauthority5f67',len(M['points'])==48 and set(auth['budgets'])==set(q['admitted_specs'])=={p['cohort']for p in M['points']}and set(auth['budgets'].values())=={1}and auth['explicit_user_approval']and auth['approved_contract_commit']==plan['approved_contract_commit']=='5f67b4d6b94568a9f1acc80c3e56736bd81e4753'and auth['approval_request_sha256']==sha(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'))
for path in (R/'tools').glob('*.py'):ast.parse(path.read_text())
ck('Allnew Python sources ASTparse only no pyc/nativewrite',True)
e=load('C48_native_private_CPU',R/'tools/stage2_native.py');reg=copy.deepcopy(actualReg);reg['registered_future_requests'][REQ]=copy.deepcopy(q);epoch=copy.deepcopy(actualEpoch);e.authority=lambda:(reg,epoch);realRegistered=e.registered;e.registered();ck('Productionregistered validates proposedinmemory registration',True)
for key,val in [('budget',49),('remaining',47),('engine_sha256','0'*64),('execution_plan_sha256','0'*64),('model_automatic_retries',1)]:
 old=reg['registered_future_requests'][REQ][key];reg['registered_future_requests'][REQ][key]=val;fails('registered rejects '+key,realRegistered);reg['registered_future_requests'][REQ][key]=old
extra='E2-DTC2A48-UNAUTHORIZED-CH-F128-V1';reg['registered_future_requests'][REQ]['admitted_specs'][extra]='0'*64;fails('registered rejects extra grant',realRegistered);reg['registered_future_requests'][REQ]['admitted_specs'].pop(extra)
ctx=lambda:(reg,epoch,reg['registered_future_requests'][REQ],plan);e.registered=ctx
for p in M['points']:
 s=e.canonical(p['cohort']);ck(p['cohort']+' productioncanonical exactspec/ROI/build',s['host_cpu']is None and s['input_digest']==p['input_digest']and s['profile']==s['downstream_profile']==p['profile']and s['scientific_role']=='STAGEII_REMAINING48_AUTHORIZED_CH')
fails('canonical rejects first16',lambda:e.canonical('E2-DTC2A16-e7bb67e63e3c3847-CH-F128-V1'));fails('canonical rejects supplement',lambda:e.canonical('E2-DTC2A48-09f94fcc7494a03b-CH-F256-V1'));fails('canonical rejects deferred',lambda:e.canonical('E2-DTC2A48-09f94fcc7494a03b-CH-F128-V1'))
c=next(p['cohort']for p in M['points']if p['program']=='BlackScholes'and p['profile']=='F128');canonical=e.canonical(c);cpu=plan['new_dispatcher_cpu_allowance'][0];resolved=dict(canonical,host_cpu=cpu);binding={'cohort':c,'canonical_spec_sha256':sha(R/'control/specs'/(c+'.json')),'host_cpu':cpu,'resolved_spec_sha256':e.jsonsha(resolved)};claims={c:{'host_cpu':cpu,'result_cap_bytes':canonical['limits']['max_result_directory_bytes']}};lease=rd('/root/data/dtc_main_v100_sweep_20261025_v1/control/BATCH_LEASE.json');fixtureLease=dict(lease,additional_requests=lease['additional_requests']+[REQ]);realRead=e.read

def mappedRead(path):
 path=Path(path)
 if path==R/'control/dispatch_bindings'/(c+'.json'):return copy.deepcopy(binding)
 if path==R/'control/POOL_DISPATCH_RESERVATIONS.json':return {'claims':copy.deepcopy(claims)}
 return realRead(path)
e.read=mappedRead;n=e.base();n.ROOT=R;n.assert_batch_lease=lambda:copy.deepcopy(fixtureLease);e.base=lambda:n
# Resource production function receives only an in-memory proposedregistration;
# no real registry/lease/spec/claim is written.
res=load('C48_resource_private_CPU',R/'tools/stage2_resources.py');peer=res._peer();peer.authority=lambda:(reg,epoch);realResources=e.resources;e.resources=res.resources
realOS=e.os;e.os=types.SimpleNamespace(**dict({k:getattr(os,k)for k in dir(os)},environ=dict(os.environ,DTC_STAGEII_REMAINING48_NATIVE_ENTRY='1'),sched_getaffinity=lambda pid:set(plan['new_dispatcher_cpu_allowance'])))
p=e.prepare(c);ck('Productionprepare no-start with actualbuild/input and freshproductionresources',p['status']=='STAGEII_REMAINING48_PREPARE_PASS_NO_START'and p['scientific_starts']==0 and p['resources']['physical_RAM_pass']and p['resources']['physical_disk_pass']and p['resources']['admission_disk_pass'],{'resource_sample':{k:p['resources'][k]for k in ['native_free_bytes','required_free_bytes','host_MemAvailable_bytes','cgroup_effective_headroom_bytes','own_remaining_write_and_restore_bytes']},'real_build_input_checks':True,'registration_lease_binding_context':'ISOLATED_IN_MEMORY_ONLY'})
resource_good=dict(p['resources']);e.resources=lambda s,fresh_source=False:copy.deepcopy(resource_good)
for flag in ['physical_RAM_pass','physical_disk_pass','admission_disk_pass']:
 e.resources=lambda s,fresh_source=False,flag=flag:dict(resource_good,**{flag:False});fails('prepare blocks '+flag+' with noINTENT',lambda:e.prepare(c))
e.resources=lambda s,fresh_source=False:dict(resource_good)
saved=dict(binding);binding['resolved_spec_sha256']='0'*64;fails('prepare rejects stalebinding resolvedSHA',lambda:e.prepare(c));binding.clear();binding.update(saved)
savedclaims=copy.deepcopy(claims);claims.clear();fails('prepare rejects absentclaim',lambda:e.prepare(c));claims.update(savedclaims);claims['CPU_ONLY_DUPLICATE']={'host_cpu':cpu};fails('prepare rejects overlappingCPU claims',lambda:e.prepare(c));claims.pop('CPU_ONLY_DUPLICATE')
e.os.sched_getaffinity=lambda pid:set();fails('prepare rejects CPU outside actualaffinity',lambda:e.prepare(c));e.os.sched_getaffinity=lambda pid:set(plan['new_dispatcher_cpu_allowance'])
old=fixtureLease['start_ticks'];fixtureLease['start_ticks']=0;fails('prepare rejects staleowner generation',lambda:e.prepare(c));fixtureLease['start_ticks']=old;fixtureLease['additional_requests'].remove(REQ);fails('prepare rejects owner missingnewscope',lambda:e.prepare(c));fixtureLease['additional_requests'].append(REQ)
e.os.environ.pop('DTC_STAGEII_REMAINING48_NATIVE_ENTRY');fails('prepare rejects absent exactnativeentry',lambda:e.prepare(c));e.os.environ['DTC_STAGEII_REMAINING48_NATIVE_ENTRY']='1'
old=epoch['epoch'];epoch['epoch']=1;fails('prepare rejects wrong epoch',lambda:e.prepare(c));epoch['epoch']=old
qq=reg['registered_future_requests'][REQ];qq['consumed'][c]={'CPU_ONLY':True};qq['remaining']=47;fails('prepare refuses spentidentity',lambda:e.prepare(c));qq['consumed'].pop(c);qq['remaining']=48
front=load('C48_front_private_CPU',R/'tools/stage2_frontend.py');front.os=e.os;front.importlib=types.SimpleNamespace(util=types.SimpleNamespace(spec_from_file_location=lambda name,path:types.SimpleNamespace(loader=types.SimpleNamespace(exec_module=lambda module:None)),module_from_spec=lambda spec:e))
for operation in ['prepare','inspect']:ck('Productionfrontend '+operation+' callsactualprepare zero-start',front.main(['experiment',operation,c,'--project','DTC_L1'])['scientific_starts']==0)
for value in ['E2-DTC2A16-e7bb67e63e3c3847-CH-F128-V1','E2-DTC2A48-09f94fcc7494a03b-CH-F256-V1','E2-DTC2A48-09f94fcc7494a03b-CH-F128-V1','UNAUTHORIZED']:
 fails('frontend excludes '+value,lambda value=value:front.main(['experiment','inspect',value,'--project','DTC_L1']))
fails('frontend rejects wrongproject',lambda:front.main(['experiment','inspect',c,'--project','EP_L2']));fails('frontend rejects extra option',lambda:front.main(['experiment','inspect',c,'--project','DTC_L1','--force']))
# Exercise the exact productionregistry updater ONLY under C's sandbox root.
sandbox=F/'NON_SCIENTIFIC_AUTHORITY';(sandbox/'control/science_authority/request_history').mkdir(parents=True,exist_ok=True)
def putj(path,v):Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
freg={'registered_future_requests':{'CPU_ONLY_OLD_SPENT':{'budget':16,'remaining':0,'consumed':{'DO_NOT_IMPORT':{'uuid':'CPU_ONLY'}}},REQ:copy.deepcopy(q)},'old_source_history':['CPU_ONLY_PRESERVE'],'qualification_history':['CPU_ONLY_PRESERVE']};rp=sandbox/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';ep=sandbox/'control/CURRENT_SCIENCE_EPOCH.json';putj(rp,freg);putj(ep,{'epoch':2,'native_registry_sha256':sha(rp),'state':'NATIVE_SCIENCE_ACTIVE','holder':os.uname().nodename});realN=e.N;e.N=sandbox
baseSource=Path('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py');tree=ast.parse(baseSource.read_text());charge=next(z for z in reversed(tree.body)if isinstance(z,ast.FunctionDef)and z.name=='exclusive');ns={'P':Path,'REQUEST':REQ,'COHORTS':set(q['admitted_specs']),'assert_batch_lease':lambda:fixtureLease,'read':lambda path:{'claims':{k:{}for k in q['admitted_specs']}},'ROOT':sandbox,'require':lambda b,msg:(_ for _ in()).throw(RuntimeError(msg))if not b else None,'sha':sha,'update_authority':e.update_authority}
def exclusivefixture(path,obj):
 with Path(path).open('x')as h:json.dump(obj,h)
ns['_original_exclusive']=exclusivefixture;exec(compile(ast.Module(body=[charge],type_ignores=[]),str(baseSource), 'exec'),ns);ledger=sandbox/'CPU_ONLY_INTENTS';ledger.mkdir(exist_ok=True)
for i,cohort in enumerate(q['admitted_specs']):ns['exclusive'](ledger/(cohort+'.INTENT.json'),{'cohort':cohort,'uuid':'CPU_ONLY_NOT_MODEL_'+str(i)})
spent=rd(rp);ck('PinnedproductionINTENT charge48 once preservespeer/history epochSHA',spent['registered_future_requests'][REQ]['remaining']==0 and len(spent['registered_future_requests'][REQ]['consumed'])==48 and spent['registered_future_requests']['CPU_ONLY_OLD_SPENT']==freg['registered_future_requests']['CPU_ONLY_OLD_SPENT']and spent['old_source_history']==freg['old_source_history']and spent['qualification_history']==freg['qualification_history']and rd(ep)['native_registry_sha256']==sha(rp))
fails('Charge duplicate48identity no refund/replacement',lambda:ns['exclusive'](ledger/(c+'.INTENT.json'),{'cohort':c,'uuid':'CPU_ONLY_BAD_RETRY'}));before=sha(rp)
def corruptpeer(v):v['registered_future_requests']['CPU_ONLY_OLD_SPENT']['remaining']=1
fails('Atomicregistry updater rejects peerhistorymutation',lambda:e.update_authority(corruptpeer));ck('Rejected mutation leftsandboxregistrybytes unchanged',sha(rp)==before)
def corrupthistory(v):v['old_source_history'].append('BAD')
fails('Atomicregistry updater rejects oldsourcehistory change',lambda:e.update_authority(corrupthistory));ck('Rejected history leftsandbox registry unchanged',sha(rp)==before)
e.N=realN
# Native strict dispatch-binding helper uses only explicit C fixture output plus
# in-memory binding reads; no scientific result is fabricated.
st=load('C48_strict_private_CPU',R/'tools/stage2_strict.py');out=F/'CPU_ONLY_STRICT_BINDING';out.mkdir(exist_ok=True);(out/'DOWNSTREAM_FROZEN_SPEC.json').write_bytes((R/'control/specs'/(c+'.json')).read_bytes());putj(out/'DISPATCH_BINDING.json',binding);dbsha=sha(out/'DISPATCH_BINDING.json');sr,sh=st.read,st.sha;st.read=lambda path:copy.deepcopy(binding)if Path(path)==R/'control/dispatch_bindings'/(c+'.json')else sr(path);st.sha=lambda path:dbsha if Path(path)==R/'control/dispatch_bindings'/(c+'.json')else sh(path)
ck('Productionstrict dispatchbinding exactcanonical/resolved join',st.dispatch_binding(c,resolved,out,{'dispatch_binding_sha256':dbsha})['cohort']==c)
bad=dict(resolved,host_cpu=cpu+1);fails('Strictbinding rejects altered executionCPU',lambda:st.dispatch_binding(c,bad,out,{'dispatch_binding_sha256':dbsha}))
policy=load('C48_guardpolicy_CPU',R/'tools/stage2_guard_policy.py');ck('Unchanged pressureonly guardpolicy exactsource4086',sha(R/'tools/stage2_guard_policy.py')=='4086afd07dc9255cc8b0de97a5883127905579a9d68b3586554ea2f3f0152797');t=policy.TerminalClosure();ck('NATURAL packet alone isnotacceptance',t.observe(producer_end='NATURAL')['scientific_acceptance']is False);ans=t.observe(run_ended=True,natural_exit_zero=True,closure={k:True for k in policy.CLOSURE_KEYS});ck('Completeguard closure remains externalacceptancecandidate',ans['state']=='COMPLETE_CANDIDATE'and not ans['performance_pass']);ck('LateSTOP invalidates candidate',t.observe(actual_stop=True)['state']=='STOP_UNACCEPTED')
results=load('C48_results_CPU',R/'tools/stage2_results.py');ck('Typednegative never accepted',not results.accepted({'state':'FAIL_STAGEII48_CH_ARCHIVED_NO_RETRY','cycles':1,'proof':{'performance_accepted':False},'archive':True}));ck('Rawpending never accepted',not results.accepted({'state':'PENDING','cycles':100}));ck('Accepted helper demandsstrictpositivecycles/archive',not results.accepted({'state':results.PASS,'cycles':0,'proof':{'performance_accepted':True,'cycles':0},'archive':True}))
# Separate JSON report records non-execution scope and exact forwardbindings.
ck('No real newrequest/claims/INTENT/lease/nativeentry mutations',REQ not in rd(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']and list((R/'control/dispatch_bindings').glob('*'))==beforebind and list((R/'control/qualification_ledger').glob('*'))==beforeintent and sha(Path('/root/data/dtc_main_v100_sweep_20261025_v1/control/BATCH_LEASE.json'))==oldfileHashes['/root/data/dtc_main_v100_sweep_20261025_v1/control/BATCH_LEASE.json']and sha(N/'bin/native')==oldfileHashes[str(N/'bin/native')])
report={'schema':'C_REMAINING48_PRODUCTION_API_CPU_FIXTURES_V1','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','checks':checks,'execution_plan_sha256':sha(R/'control/EXECUTION_PLAN.json'),'registry_candidate_sha256':sha(R/'control/REGISTRY_REQUEST_CANDIDATE.json'),'scientific_models_started':0,'real_registrations_owner_callbacks_or_authority_writes':0,'fixture_scope':'Only in-memoryproposed registration/lease/claims/affinity and C-ownedNON_SCIENTIFIC_AUTHORITY filefixtures; actualprepare/inspect/build/input/resourcefunctions exercised read-only. No nativeengine/run_native/parentapply/archive called.','scientific_result_fabrication':False};(O/'PRODUCTION_API_CPU_QUALIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'sha256':sha(O/'PRODUCTION_API_CPU_QUALIFICATION.json')}))
