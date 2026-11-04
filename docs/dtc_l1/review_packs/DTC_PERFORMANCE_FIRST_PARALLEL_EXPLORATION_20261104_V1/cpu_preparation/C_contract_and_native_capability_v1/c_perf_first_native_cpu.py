from pathlib import Path
import json,ast,copy,datetime,os,fcntl,hashlib,types
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1');O=A/'C_contract_and_native_capability_v1';F=O/'private_registry_CPU_fixture';F.mkdir(exist_ok=False);N=Path('/root/data/ep_l2_dtc_l1_native_v2');T=Path('/root/data/dtc_main_v100_sweep_20261025_v1');R=Path('/root/data/dtc_stage_iia_remaining48_20261104_v1');PREP=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1/agents/C_final48_review_preparation_v1');REQOLD='DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1';REQFIX='C_CPU_FIXTURE_ONLY_NOT_A_REGISTERED_REQUEST';read=lambda p:json.loads(Path(p).read_bytes());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();checks=[]
def ck(n,v):assert v,n;checks.append({'check':n,'pass':True})
with(N/'control/science_authority/REGISTRY_UPDATE.lock').open('rb')as lk:
 fcntl.flock(lk,fcntl.LOCK_SH);rp=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';ep=N/'control/CURRENT_SCIENCE_EPOCH.json';reg=read(rp);epoch=read(ep);ck('actual epoch2 registry pair SHA-consistent under shared lock',sha(rp)==epoch['native_registry_sha256']and epoch['epoch']==2 and epoch['state']=='NATIVE_SCIENCE_ACTIVE')
actual_registry_sha=sha(rp);actual_epoch_sha=sha(ep);old=read(PREP/'OLD_DTC_IDENTITIES_BEFORE_NEW48.fixed.json');q=reg['registered_future_requests'][REQOLD];basebefore=copy.deepcopy(reg)
validator=PREP/'final48_readonly_audit.py';tree=ast.parse(validator.read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main');segments=[]
for node in ast.walk(main):
 if isinstance(node,(ast.Assert,ast.Assign))and getattr(node,'lineno',0)in [346,347,348,349,350]:segments.append(node)
segments.sort(key=lambda n:n.lineno);ck('extract exact five old-final predicates for baseline and UUID namespace',len(segments)==5)
code=compile(ast.Module(body=segments,type_ignores=[]),'<C-original-final-registry-predicates>','exec')
def eval_old_predicate(r):
 ns={'old':old,'registry':r,'request':r['registered_future_requests'][REQOLD],'REQ':REQOLD};exec(code,ns)
eval_old_predicate(reg);ck('current actual old-final baseline and UUID predicates pass',True)
fake=copy.deepcopy(reg);fake['registered_future_requests'][REQFIX]={'budget':32,'remaining':32,'consumed':{},'admitted_specs':{}};eval_old_predicate(fake);ck('extra request key allowed by exact old-final predicates',True)
fake['registered_future_requests'][REQFIX]['consumed']={'CPU_COHORT_NOT_REAL':{'uuid':'CPU_FIXTURE_NOT_A_REAL_EXECUTION_UUID'}};eval_old_predicate(fake);ck('fresh UUID of another active request allowed by old final',True)
wrong=copy.deepcopy(fake);wrong['registered_future_requests'][REQFIX]['consumed']['CPU_COHORT_NOT_REAL']['uuid']=next(iter(q['consumed'].values()))['uuid']
try:eval_old_predicate(wrong)
except AssertionError:ck('UUID reused from old48 rejected',True)
else:raise AssertionError('duplicate UUID accepted')
wrong=copy.deepcopy(fake);oldkey=next(iter(old));wrong['registered_future_requests'][oldkey]['budget']+=1
try:eval_old_predicate(wrong)
except AssertionError:ck('old recorded budget mutation rejected',True)
else:raise AssertionError('old mutation accepted')
# Execute production global-lock update logic only against an isolated C fixture directory.
FN=F/'native_fixture';(FN/'control/science_authority/request_history').mkdir(parents=True);frp=FN/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';fep=FN/'control/CURRENT_SCIENCE_EPOCH.json';frp.write_text(json.dumps(reg,sort_keys=True,indent=2)+'\n');e=copy.deepcopy(epoch);e['native_registry_sha256']=sha(frp);fep.write_text(json.dumps(e,sort_keys=True,indent=2)+'\n')
src=R/'tools/stage2_native.py';st=ast.parse(src.read_text());fun=next(n for n in st.body if isinstance(n,ast.FunctionDef)and n.name=='update_authority');ns={'N':FN,'P':Path,'read':read,'sha':sha,'copy':copy,'fcntl':fcntl,'json':json,'os':os,'datetime':datetime,'REQ':REQFIX};exec(compile(ast.Module(body=[fun],type_ignores=[]),'<C-production-update-against-private-fixture>','exec'),ns)
def add(r):
 assert REQFIX not in r['registered_future_requests'];r['registered_future_requests'][REQFIX]={'request':REQFIX,'budget':32,'remaining':32,'consumed':{},'admitted_specs':{}}
ns['update_authority'](add);now=read(frp);ck('isolated production update can append one distinct request and preserve all peers',all(now['registered_future_requests'][k]==v for k,v in reg['registered_future_requests'].items())and now['old_source_history']==reg['old_source_history']and now['qualification_history']==reg['qualification_history'])
ck('isolated aggregate credit sum is bookkeeping not old-credit reassignment',now['new_scientific_budget_remaining']==reg['new_scientific_budget_remaining']+32 and read(fep)['native_registry_sha256']==sha(frp))
before=(frp.read_bytes(),fep.read_bytes())
def mutate_peer(r):r['registered_future_requests'][REQOLD]['budget']+=1
try:ns['update_authority'](mutate_peer)
except AssertionError:ck('production peer mutation rejected before commit',before==(frp.read_bytes(),fep.read_bytes()))
else:raise AssertionError('peer mutation accepted')
try:ns['update_authority'](add)
except AssertionError:ck('registration closure refuses duplicate request reset/re-add',before==(frp.read_bytes(),fep.read_bytes()))
else:raise AssertionError('duplicate request accepted')
lease=read(T/'control/BATCH_LEASE.json');proc=Path('/proc',str(lease['pid']));st=proc.joinpath('stat').read_text().rsplit(')',1)[1].split();fds={str(fd):{'target':os.readlink(proc/'fd'/str(fd)),'fdinfo':(proc/'fdinfo'/str(fd)).read_text()}for fd in [3,4]};ck('actual sole owner generation and FD3/FD4 lock identities',lease['pid']==1498278 and lease['start_ticks']==int(st[19])==977758783 and lease['request']=='DTC_AE_V100_FULL_SWEEP_20261025_V1'and fds['3']['target']==str(T/'control/FINITE_CONTROLLER.lock')and fds['4']['target']==str(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock')and all('FLOCK' in v['fdinfo']and'1498278'in v['fdinfo']for v in fds.values()))
plan=read(R/'control/EXECUTION_PLAN.json');ck('old122 pin namespace does not pin global mutable registry lease route',len(plan['source_pins'])==122 and all(not any(k in x['path']for k in ['NATIVE_SCIENCE_REGISTRY.json','CURRENT_SCIENCE_EPOCH.json','BATCH_LEASE.json','/bin/native'])for x in plan['source_pins']))
(O/'NATIVE_CAPABILITY_CPU.json').write_text(json.dumps({'schema':'C_PERF_FIRST_NATIVE_DUAL_REQUEST_CPU_CAPABILITY_REVIEW_V1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'SUPPORTED_CONDITIONAL_NEW_PRIVATE_CONTRACT_ONLY_NOT_EXECUTION_QUALIFICATION','checks':checks,'check_count':len(checks),'actual_registry_snapshot_sha256':actual_registry_sha,'actual_epoch_snapshot_sha256':actual_epoch_sha,'actual_owner':{'pid':lease['pid'],'start_ticks':lease['start_ticks'],'primary_request':lease['request'],'controller_sha256':lease['controller_sha256'],'lease_fd':lease['fd'],'FD3_FD4':fds},'old48_accounting':{'budget':q['budget'],'remaining':q['remaining'],'consumed':len(q['consumed'])},'C_final_validator_sha256':sha(validator),'production_update_source_sha256':sha(src),'isolated_registration_fixture_never_wrote_real_authority':True,'new_scientific_requests_registered':0,'actual_owner_callbacks':0,'actual_model_starts':0,'old_source_or_budget_changes':0},indent=2)+'\n');print(json.dumps({'status':'PASS_CONDITIONAL_CAPABILITY','checks':len(checks),'sha256':sha(O/'NATIVE_CAPABILITY_CPU.json')}))
