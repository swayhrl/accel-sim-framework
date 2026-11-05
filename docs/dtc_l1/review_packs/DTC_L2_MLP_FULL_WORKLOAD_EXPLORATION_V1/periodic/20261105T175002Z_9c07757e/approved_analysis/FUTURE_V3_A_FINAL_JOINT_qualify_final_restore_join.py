"""Final exact-source join: existing six + only two changed restore functions.
No final-prefix rerun, no process/authority/model operation.
"""
import pathlib,json,hashlib,ast,copy,types,threading,importlib.util,tempfile,difflib,sys,os
sys.dont_write_bytecode=True
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');BASE=A/'agents/A/future_bpf_v3_joint_qualification_v1';D=BASE/'final6';B=A/'agents/B/strace_bpf_future_entry_v3';E=A/'agents/E/strace_bpf_future_strict_consumer_v3';D.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def audit(event,args):
 if event=='subprocess.Popen'or event.startswith('os.exec')or event in['os.system','os.kill','os.killpg']:raise RuntimeError('FINAL_DELTA_NO_REAL_PROCESS_OR_SIGNAL')
 if event=='open':
  p,mode,flags=args
  if(isinstance(mode,str)and any(c in mode for c in 'wax+'))or flags&(os.O_WRONLY|os.O_RDWR):
   if isinstance(p,(str,bytes)):assert P(os.fsdecode(p)).resolve().is_relative_to(D.resolve())
sys.addaudithook(audit)
basepath=BASE/'JOINT6_CPU_QUALIFICATION.json';assert sha(basepath)=='05415c6164709f4488fcbd5d1c04b68ba81c357cb37f875fc18d2d4c2dece618';base=read(basepath);assert len(base['cases'])==6 and all(x['status']=='PASS'for x in base['cases'])
assert sha(BASE/'qualify_joint6.py')==base['driver_sha256']
case=next(x for x in base['cases']if x['case'].startswith('PRIMARY_'));out=P(case['evidence']['root'])/'DTC/run/results'/case['evidence']['UUID'];snap=read(out/'STRACE_BPF_OBSERVATION_SNAPSHOT.json')
expected={'producer':'06e52cd8e359791a912ba081b9e3cb16d7e23baae1d7a8511eefa8d74528c675','frontend':'c1557a219ada13fb0478830209f137036324048d8387cdffaa850f3744a5e8d2','entry':'2a21ba7d62ea9094dd1dc6de7c4d0c699c9baf491e07467228f1b307d60c8792','extra_strict':'702a0a3e27645ece6cf15a68c598bce4067b69132a74c1fb1e3cfde03a621c3b','consumer':'de70cede8876fca5bf909f5b8d685b74da43a6ca08880e18e09d59e924c0225b'}
finalpins={};diffs=[]
for role,row in snap['source_snapshots'].items():
 path=P(row['path']);old=row['utf8'];oldh=hashlib.sha256(old.encode()).hexdigest();assert oldh==row['sha256']==base['source_pins'][str(path)];assert sha(path)==expected[role];finalpins[str(path)]=sha(path)
 if role in ['producer','consumer']:
  name='restore_owner_dispatch'if role=='producer'else'restore_in_owner';oldt=ast.parse(old);newtext=path.read_text();newt=ast.parse(newtext)
  oldfn=next(x for x in oldt.body if isinstance(x,ast.FunctionDef)and x.name==name);newfn=next(x for x in newt.body if isinstance(x,ast.FunctionDef)and x.name==name)
  oldt.body=[x for x in oldt.body if x is not oldfn];newt.body=[x for x in newt.body if x is not newfn];assert ast.dump(oldt,include_attributes=False)==ast.dump(newt,include_attributes=False),'NON_RESTORE_SOURCE_CHANGE '+role
  pre=D/'preimages'/(role+'.DEVELOPMENT_SOURCE.py');pre.parent.mkdir(exist_ok=True);pre.write_text(old)
  dp=D/(role+'.restore-only.diff');dp.write_text(''.join(difflib.unified_diff(old.splitlines(True),newtext.splitlines(True),fromfile=role+'/'+oldh,tofile=role+'/'+sha(path))))
  diffs.append(dict(role=role,changed_function=name,old_source_sha256=oldh,final_source_sha256=sha(path),preimage_path=str(pre),diff_path=str(dp),all_other_AST_identical=True))
 else:assert oldh==sha(path),'UNCHANGED_ROLE_DRIFT '+role
for path,h in base['source_pins'].items():
 if path not in finalpins:assert sha(path)==h;finalpins[path]=h
producer=load('A_final_B06e52',B/'strace_entry.py');consumer=load('A_final_Ede70',E/'consumer_bridge.py');root=P(tempfile.mkdtemp(prefix='RESTORE_PENDING_CLAIM_',dir=D));cohort='E2-DTCL2MLP-CPU-RESTORE-PENDING-V3';claimpath=root/'control/strace_bpf_v3_route_claims'/(cohort+'.json');put(claimpath,dict(schema='STRACE_BPF_V3_FUTURE_ROUTE_CLAIM_V1',overlay_id=producer.ID,cohort=cohort))
q=dict(admitted_specs={cohort:'PRIVATE_CANONICAL_SHA'},consumed={});engine=types.SimpleNamespace(R=root,assert_parent_lease=lambda:None,registered=lambda:(None,None,q,None));aging=types.SimpleNamespace(lock=threading.RLock());prior=lambda c:'PRIOR_V2';wrapper=lambda c:'PRIVATE_V3';frame=types.SimpleNamespace(f_locals=dict(engine=engine),f_globals=dict(worker=wrapper));main=types.SimpleNamespace();setattr(main,producer.OWNER_MARKER,dict(frame=frame,aging=aging,wrapper=wrapper,previous=prior))
def rejected(fn):
 try:fn()
 except Exception as e:return dict(type=type(e).__name__,reason=str(e))
 raise AssertionError('Pending route must block restore')
bhold=rejected(lambda:producer.restore_owner_dispatch(main));assert frame.f_globals['worker']is wrapper and hasattr(main,producer.OWNER_MARKER)
main2=types.SimpleNamespace();cs=types.SimpleNamespace(safe_finish=wrapper,accepted=lambda v:True);api=dict(result_path=lambda c:root/'analysis'/(c+'.RESULT.json'),selected=lambda c:True,original_safe=prior);setattr(main2,consumer.MARKER,dict(aging=aging,consumer=cs,wrapper=wrapper,engine=engine,cfg={'root':str(root)},bridge=api))
ehold=rejected(lambda:consumer.restore_in_owner(lambda:None,main2));assert cs.safe_finish is wrapper and hasattr(main2,consumer.MARKER)
delta=dict(schema='FINAL_V3_PENDING_CLAIM_RESTORE_DELTA_CPU_V1',status='PASS',one_group_two_actual_restore_functions=True,fixture_path=str(root),registered_unspent_claim=True,B_restore_rejection=bhold,E_restore_rejection=ehold,worker_and_consumer_wrapper_and_markers_retained=True,actual_lease_authority_and_owner_are_explicit_private_fixtures=True,source_diffs=diffs,source_pins=finalpins,driver_sha256=sha(__file__),production_mutations=0,actual_model_starts=0,new_grants=0)
put(D/'RESTORE_DELTA_CPU_QUALIFICATION.json',delta)
joint=dict(schema='FUTURE_BPF_V3_FINAL_JOINT_SOURCE_QUALIFICATION_V1',status='PASS_CPU_MECHANICS_NOT_ACTUAL4_RELEASE',qualified_sources=expected,source_pins=finalpins,base_six=dict(path=str(basepath),sha256=sha(basepath),cases=base['cases'],source_roles_note='Baca9/Ecf114 development sources; all unchanged AST remains identical except two restore functions.'),restore_delta=dict(path=str(D/'RESTORE_DELTA_CPU_QUALIFICATION.json'),sha256=sha(D/'RESTORE_DELTA_CPU_QUALIFICATION.json'),one_group_two_function_rejections=True),source_coverage=dict(exact_diff_only_restore=True,final_native_prefix_rerun=False,unchanged_prefix_CPU2_IO_policy_and_strict_covered_by_existing_six=True,changed_restore_functions_covered_by_new_private_delta=True),actual4_qualified=False,production_release_eligible=False,physics_Popen_archive_device_canaryquorum='EXPLICIT_PRIVATE_CPU_STANDINS',actual_model_starts=0,new_grants=0,production_mutations=0,old_suites_rerun=False)
put(D/'FINAL_JOINT_CPU_QUALIFICATION.json',joint)
(D/'REPORT.txt').write_text('''Final V3 CPU qualification: existing six joint groups + exact restore-only delta. No production installation/model/grant.\n\nOriginal 05415 receipt is preserved byte-for-byte. It ran actual native/observer/atomicIO/CPU2 prefix to mockPopen for PRIMARY andIR, real oldCPU2+IO replay then newextra/privateconsumer readonly/mirror; four realcanaries absent block production; exactV2 delegate, binding/options/oldstrict tamper and unknowngeneration HOLD passed. Physics/archive/device/quorum were explicitly CPUstandins, not realperformance.\n\nFinal producer06e52 and consumerde70 differ from developmentaca9/cf114 ONLY in restore_owner_dispatch/restore_in_owner; full remaining AST and frontend/entry/extra/policy are identical. Exactpreimages/diffs saved. One fresh private admitted-unspent persistentclaim group ran both final restore functions: both HOLD and keep mandatory worker/consumer/markers intact. This is an honest source-coverage join, not a claim finalnativeprefix was rerun.\n\nFinal five roles are bound in FINAL_JOINT_CPU_QUALIFICATION.json. Real exact4 full natural readonly-replay qualification remains absent, so production release is FALSE. Main remains sole installer/dispatcher.\n''')
files=[]
for p in sorted(D.rglob('*')):
 if p.is_file()and p.name!='MANIFEST.json':files.append(dict(path=str(p),pack_path=str(p.relative_to(D)),bytes=p.stat().st_size,sha256=sha(p)))
put(D/'MANIFEST.json',dict(schema='FUTURE_BPF_V3_FINAL_JOINT_CANDIDATE_MANIFEST',status='FROZEN_CPU_ONLY',files=files,base_six_sha256=sha(basepath),final_joint_sha256=sha(D/'FINAL_JOINT_CPU_QUALIFICATION.json'),qualified_sources=expected,production_release_eligible=False))
print(json.dumps(dict(path=str(D),final_qualification_sha256=sha(D/'FINAL_JOINT_CPU_QUALIFICATION.json'),delta_sha256=sha(D/'RESTORE_DELTA_CPU_QUALIFICATION.json'),manifest_sha256=sha(D/'MANIFEST.json'),qualified_sources=expected)))
