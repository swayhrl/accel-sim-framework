from pathlib import Path
import json,hashlib,importlib.util,types,copy,os
R=Path('/root/data/dtc_stage_iia_first16_20261104_v1');P=R/'tools/stage2_native.py';O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1/agents/C');matrix=json.loads((R/'control/MATRIX.json').read_text());c=matrix['points'][0]['cohort'];canonical=json.loads((R/'control/specs'/(c+'.json')).read_text());cpu=min(os.sched_getaffinity(0));rows=[]
class PrivateOS:
 def __init__(self):self.environ=dict(os.environ,DTC_STAGEII_FIRST16_NATIVE_ENTRY='1')
 def __getattr__(self,k):return getattr(os,k)
def fixture():
 sp=importlib.util.spec_from_file_location('C_private_stage2_engine_fixture',P);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=copy.deepcopy(canonical);resolved=dict(s,host_cpu=cpu);binding={'cohort':c,'canonical_spec_sha256':m.sha(R/'control/specs'/(c+'.json')),'host_cpu':cpu,'resolved_spec_sha256':m.jsonsha(resolved)};q={'state':'ARMED','remaining':16,'consumed':{},'admitted_specs':{x['cohort']:x['spec_sha256'] for x in matrix['points']}};ep={'epoch':2,'state':'NATIVE_SCIENCE_ACTIVE','holder':os.uname().nodename};plan={};realread=m.read;claims={c:{'host_cpu':cpu}};state={'q':q,'ep':ep,'binding':binding,'claims':claims,'resources':{'physical_RAM_pass':True,'physical_disk_pass':True}}
 def read(path):
  if Path(path)==R/'control/dispatch_bindings'/(c+'.json'):return copy.deepcopy(state['binding'])
  if Path(path)==R/'control/POOL_DISPATCH_RESERVATIONS.json':return {'claims':copy.deepcopy(state['claims'])}
  return realread(path)
 m.read=read;m.registered=lambda:({},state['ep'],state['q'],plan);m.os=PrivateOS();m.assert_parent_lease=lambda:None;m.check_input=lambda s:{'FIXTURE_ONLY':True};m.resources=lambda *a,**k:dict(state['resources']);m.binding=lambda:{'FIXTURE_ONLY':True};m.base=lambda:types.SimpleNamespace(identity=lambda:{'FIXTURE_ONLY':True});m.subprocess=types.SimpleNamespace(check_output=lambda argv,**k: (s['core_commit'] if argv[2]==s['source_worktrees']['core'] else s['framework_commit'])+'\n' if argv[-2:]==['rev-parse','HEAD'] else '')
 return m,state
def case(name,mut=None,expect_success=False):
 m,state=fixture()
 if mut:mut(m,state)
 try:v=m.prepare(c);ok=expect_success and v['scientific_starts']==0;err=None
 except (AssertionError,RuntimeError,KeyError,ValueError,FileNotFoundError) as e:ok=not expect_success;err=repr(e)
 rows.append({'case':name,'PASS':ok,'expected':'PREPARE_PASS_NO_START' if expect_success else 'REJECT_NO_START','error':err})
case('CanonicalValidPrepareOnly',expect_success=True)
case('SpentCohortReject',lambda m,s:s['q']['consumed'].update({c:{'uuid':'fixture-spent'}}))
case('ZeroRemainingReject',lambda m,s:s['q'].update(remaining=0))
case('ClosedStateReject',lambda m,s:s['q'].update(state='COMPLETE'))
case('WrongEpochReject',lambda m,s:s['ep'].update(epoch=1))
case('WrongHostReject',lambda m,s:s['ep'].update(holder='not174'))
case('MissingNativeEntryReject',lambda m,s:m.os.environ.pop('DTC_STAGEII_FIRST16_NATIVE_ENTRY'))
case('MissingClaimReject',lambda m,s:s['claims'].clear())
case('DuplicateCPUClaimReject',lambda m,s:s['claims'].update({'FIXTURE_OTHER':{'host_cpu':cpu}}))
case('DispatchBindingSHADriftReject',lambda m,s:s['binding'].update(canonical_spec_sha256='0'*64))
case('ResolvedBindingSHADriftReject',lambda m,s:s['binding'].update(resolved_spec_sha256='0'*64))
case('RAMHoldRejectBeforeAnyFork',lambda m,s:s['resources'].update(physical_RAM_pass=False))
case('DiskHoldRejectBeforeAnyFork',lambda m,s:s['resources'].update(physical_disk_pass=False))
out={'schema':'DTC_STAGE_IIA_C_PRIVATE_ACTUAL_PREPARE_CPU_FIXTURES_V1','engine_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'all_PASS':all(x['PASS'] for x in rows),'cases':rows,'model_starts':0,'real_authority_reads_or_writes':0,'scope_limit':'Actual new prepare/canonical/spec_for control flow with in-memory registry/lease/resource/input/git stubs; only existing small immutable files hashed. No engine(), run_native(), subprocess, owner attachment or real prepare authority was called. Does not qualify actual sole-owner ancestry or model lifecycle.'};(O/'CPU_ENGINE_PREPARE_FIXTURES_FINAL_CANDIDATE.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'cases':len(rows),'allPASS':out['all_PASS'],'engine_sha256':out['engine_sha256'],'failed':[x for x in rows if not x['PASS']]},indent=2))

