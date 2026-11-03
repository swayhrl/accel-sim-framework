"""New SharedCPU complete-prefix/consumer CPU qualification, no real model."""
import copy,hashlib,importlib.util,json,pathlib,tempfile,shutil,types,sys,threading
P=pathlib.Path;D=P(__file__).parent
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def audit(event,args):
 if event=='subprocess.Popen'or event.startswith('os.exec')or event in('os.system','os.kill','os.killpg'):raise AssertionError('CPU-only: no real process/signal')
sys.addaudithook(audit)
B=A/'agents/B/cpu_shared_timeslice_entry_v1';builder=load('E_actual_shared_prefix_builder',B/'cpu_prefix_fixture.py')
extra=load('E_actual_shared_observation_extra',D/'bpf_extra_strict.py');bridge=load('E_actual_shared_consumer',D/'consumer_bridge.py');resource=load('E_actual_shared_resource_extra',D/'resource_extra_strict.py')
root=P(tempfile.mkdtemp(prefix='CPU_SHARED_JOINT_',dir=D));f=builder.build_fixture(root=root,extra_path=D/'bpf_extra_strict.py',consumer_path=D/'consumer_bridge.py');run=builder.run_prefix(f)
shared=builder.replay_new_resource(run);contract=extra.normalize_contract(read(f.cfg['exclusion_contract_path']),root,f.cfg['exclusion_contract_sha256'],True)
observed=extra.terminal(run.c,shared,root,contract,run.q)
checks=[]
def ok(n,fn):fn();checks.append({'name':n,'status':'PASS'})
def reject(fn):
 try:fn()
 except Exception:return
 raise AssertionError('Expected strict HOLD')
ok('actual_native_observer_atomicIO_Aresource_to_mockPopen_then_joint_strict',lambda:extra.require(observed[extra.KEY]['status']=='PASS_CPU_SHARED_OBSERVATION_AND_ORIGINAL_IO'and shared['additional_cpu_shared_timeslice_strict']['status']=='PASS_CPU_SHARED_TIMESLICE_IO_AND_ORIGINAL_PERFORMANCE','newchain'))
ok('reference_cycles_8551_complete_counts_original_physics_required',lambda:extra.require(observed['cycles']==8551 and observed['CTA']==f.spec['expected']['CTA']and observed['instructions']==f.spec['expected']['instructions']and observed['kernel_count']==f.spec['expected']['kernels'],'reference'))
ok('old_CPU2_PASS_never_invented',lambda:extra.require('additional_cpu_spare_memory_admission_strict'not in observed and observed[extra.KEY]['old_CPU2_PASS_claimed']is False,'honesty'))
p=copy.deepcopy(shared);p['cycles']+=1
ok('changed_reference_cycles_rejected',lambda:reject(lambda:extra.terminal(run.c,p,root,contract,run.q)))
p=copy.deepcopy(run.base_proof);p['instructions']-=1
ok('incomplete_trace_count_rejected_by_new_resource_joint',lambda:reject(lambda:resource.terminal(run.c,p,root,run.q)))
p=copy.deepcopy(shared);p['additional_cpu_spare_memory_admission_strict']={'status':'PASS_CPU_SPARE_MEMORY_IO_AND_ORIGINAL_PERFORMANCE'}
ok('old_CPU2_status_cannot_substitute_shared_proof',lambda:reject(lambda:extra.terminal(run.c,p,root,contract,run.q)))
lp=run.out/'NATIVE_LAUNCH.json';saved=lp.read_bytes();v=read(lp);v.pop('additional_cpu_shared_timeslice_binding');put(lp,v)
ok('missing_one_resource_binding_rejected',lambda:reject(lambda:resource.terminal(run.c,run.base_proof,root,run.q)));lp.write_bytes(saved)
pp=run.out/'NATIVE_SIMULATOR_PID_AND_MAPS.json';saved=pp.read_bytes();v=read(pp);v['host_cpu_affinity_actual']=[v['host_cpu_affinity_actual'][0]+1];put(pp,v)
ok('selected_CPU_dispatch_actual_affinity_join_rejected',lambda:reject(lambda:resource.terminal(run.c,run.base_proof,root,run.q)));pp.write_bytes(saved)
ap=run.out/extra.ACT;sa,sp=ap.read_bytes(),pp.read_bytes();v=read(ap);v['verdict']['status']='PASS_DEFAULT_CONTROL_NO_BPF';put(ap,v);pd=read(pp);pd['strace_observation_activation_sha256']=sha(ap);put(pp,pd)
ok('old_observation_status_not_falsely_claimed_as_shared',lambda:reject(lambda:extra.terminal(run.c,shared,root,contract,run.q)));ap.write_bytes(sa);pp.write_bytes(sp)
def archive_fixture():
 bundle=root/'ARCHIVE_TRANSPORT_STANDIN';restore=root/'DTC/run/recovery/CPU_STANDIN';bundle.mkdir(exist_ok=True);restore.mkdir(parents=True,exist_ok=True);entries=[]
 for p in sorted(run.out.iterdir()):
  if p.is_file():entries.append(dict(path=p.name,type='file',sha256=sha(p),size=p.stat().st_size));shutil.copyfile(p,restore/p.name)
 manifest=dict(cohort=run.c,source_root=str(run.out),entries=entries);put(bundle/'SOURCE_MANIFEST.json',manifest);raw=(json.dumps(manifest,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 return dict(receipt=dict(cohort=run.c,status='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET',source_disposition='SOURCE_KEEP',target_mount_path=str(bundle),native_restore=str(restore),manifest_sha256=hashlib.sha256(raw).hexdigest(),archive_sha256='CPU_STANDIN_NOT_REAL_TRANSPORT'),independently_verified_entries=len(entries))
consumer=load('E_actual_original_consumer',R/'tools/l2_results.py');delegated=[];sentinel=object();cache={}
def oldsafe(c):delegated.append(c);return sentinel
def physics_loader(n,file):
 if file=='l2_native.py':return types.SimpleNamespace(registered=lambda:(None,None,run.q,None))
 if file=='l2_strict.py':return types.SimpleNamespace(terminal=lambda c:run.base_proof)
 if file=='l2_outbox.py':return types.SimpleNamespace(verify=lambda c:cache['archive'])
 raise AssertionError('Unexpected original fixture load '+file)
def oldarchive(c):cache['archive']=archive_fixture();return cache['archive']
consumer.safe_finish=oldsafe;consumer.load=physics_loader;consumer.archive_closed=oldarchive
contract['qualification_loader_sha256']=sha(__file__)
api=bridge.make_private_consumer(consumer,contract,extra,lambda:run.q);value=api['safe_finish'](run.c)
extra.require(value['state']==consumer.PASS,str(value))
ok('actual_original_finish_clone_shared_branch_complete_before_accepted_write',lambda:extra.require(value['proof'][extra.KEY]['schema']==extra.ID and value['proof']['additional_cpu_shared_timeslice_strict']['schema']==resource.ID,'source'))
ok('canonical_newC_and_engineering_mirror_equal_excluded_unionFalse',lambda:extra.require(read(api['result_path'](run.c))==read(api['engineering_path'](run.c))and value['primary_statistics_excluded']is True and value['validated_union_authorized']is False,'mirror'))
ok('complete_shared_readonly_replay',lambda:extra.require(api['readonly_replay'](run.c)==value,'readonly'))
# Exercise the real frame-private install/restore APIs in this private process.
cfgpath=root/'E_PRIVATE_INSTALL_CONFIG.json';put(cfgpath,f.cfg)
aging=types.SimpleNamespace(lock=threading.RLock());engine=types.SimpleNamespace(registered=lambda:(None,None,run.q,None))
frame=types.SimpleNamespace(f_locals={'consumer':consumer,'engine':engine,'res':types.SimpleNamespace(DTC_LARGE_JOB_AGING_INSTALLED=aging)})
before=(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed,consumer.safe_finish)
bridge.install_on_frame(frame,cfgpath,f.cfg['exclusion_contract_path'],f.cfg['exclusion_contract_sha256'],lambda:None,qualification_loader_sha256=sha(__file__))
ok('actual_private_frame_safe_route_readiness',lambda:extra.require(bridge.consumer_check(frame,f.cfg)is True and before[:4]==(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed),'ready'))
resultpath=api['result_path'](run.c);original_result=resultpath.read_bytes()
bad=copy.deepcopy(value);bad['state']='FAIL_L2MLP_ARCHIVED_NO_RETRY';put(resultpath,bad)
ok('restore_refuses_existing_negative_RESULT',lambda:reject(lambda:bridge.restore_in_owner(lambda:None)))
bad=copy.deepcopy(value);bad['uuid']='WRONG_CPU_FIXTURE_UUID';put(resultpath,bad)
ok('restore_requires_q_same_UUID',lambda:reject(lambda:bridge.restore_in_owner(lambda:None)))
bad=copy.deepcopy(value);bad['proof']['additional_cpu_shared_timeslice_strict']['schema']='OLD_CPU2';put(resultpath,bad)
ok('restore_requires_honest_shared_resource_generation',lambda:reject(lambda:bridge.restore_in_owner(lambda:None)))
bad=copy.deepcopy(value);bad['proof'][extra.KEY]['schema']='DTC_STRACE_FUTURE_ENTRY_V2';put(resultpath,bad)
ok('restore_requires_shared_observation_generation',lambda:reject(lambda:bridge.restore_in_owner(lambda:None)))
bad=copy.deepcopy(value);bad['archive'].pop('additional_strace_bpf_archive_verification');put(resultpath,bad)
ok('restore_requires_new_archive_native_verification',lambda:reject(lambda:bridge.restore_in_owner(lambda:None)))
resultpath.write_bytes(original_result);main=sys.modules['__main__'];setattr(main,bridge.B_OWNER_MARKER,types.SimpleNamespace(qualification_only=True))
ok('restore_consumer_requires_B_dispatcher_first',lambda:reject(lambda:bridge.restore_in_owner(lambda:None)))
delattr(main,bridge.B_OWNER_MARKER);bridge.restore_in_owner(lambda:None)
ok('same_UUID_fullaccepted_restore_preserves_previous_V2_safe_exactly',lambda:extra.require(before==(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed,consumer.safe_finish),'restore'))
restore=P(cache['archive']['receipt']['native_restore'])/'CPU_SHARED_TIMESLICE_SNAPSHOT.json';saved=restore.read_bytes();restore.write_bytes(saved+b' ')
ok('new_resource_snapshot_native_restore_SHA_required',lambda:reject(lambda:extra.verify_archive(run.c,cache['archive'],root,contract)));restore.write_bytes(saved)
rp=api['result_path'](run.c);ep=api['engineering_path'](run.c);rp.rename(rp.with_suffix('.CPU_PREIMAGE'));ep.rename(ep.with_suffix('.CPU_PREIMAGE'))
original_verify=extra.verify_archive
def deny(*a,**k):raise extra.ObservationHold('CPU newarchive key failure')
extra.verify_archive=deny;failure=api['safe_finish'](run.c);extra.verify_archive=original_verify
ok('archive_failure_prevents_accepted_canonical_and_mirror',lambda:extra.require(failure['state']=='CPU_SHARED_OBSERVATION_HOLD_PRESERVE'and not rp.exists()and not ep.exists(),'order'))
rp.with_suffix('.CPU_PREIMAGE').rename(rp);ep.with_suffix('.CPU_PREIMAGE').rename(ep)
ok('every_nonselected_uses_exact_previous_V2_safe',lambda:extra.require(api['safe_finish']('OTHER_ENGINEERING_V2')is sentinel and delegated[-1]=='OTHER_ENGINEERING_V2','delegate'))
summary=load('E_actual_primary_summary',R/'tools/l2_results.py');matrix=read(R/'control/MATRIX_CURRENT.json');a=summary.summarize(matrix,{run.c:dict(value,cycles=1)});b=summary.summarize(matrix,{});a.pop('utc');b.pop('utc')
ok('malicious_engineering_one_cycle_not_in_actual350_GM_or_coverage',lambda:extra.require(a==b,'isolation'))
report={'schema':'CPU_SHARED_NEW_PREFIX_CONSUMER_QUALIFICATION','status':'PASS','checks':checks,'count':len(checks),'root':str(root),'cohort':run.c,'uuid':run.intent['uuid'],'cycles':value['cycles'],
 'sources':{'resource_library':sha(f.memcfg['source_paths']['library']),'resource_extra':sha(D/'resource_extra_strict.py'),'observation_extra':sha(D/'bpf_extra_strict.py'),'consumer':sha(D/'consumer_bridge.py'),'producer':sha(B/'strace_entry.py'),'frontend':sha(B/'bpf_frontend.py'),'entry':sha(B/'native-entry/bin/experiment'),'builder':sha(B/'cpu_prefix_fixture.py')},'driver_sha256':sha(__file__),
 'scope':'Actual original native/observer/atomicIO prefix to mocked Popen; actual A Shared proof and oldIO/new resource/new observation strict; actual original finish code private clone. Original physics/progress/guard/resource sampling and archive transport/device leaves are explicit CPU stand-ins.',
 'production_release_eligible':False,'actual_model_qualified':False,'actual_archive_transport_qualified':False,'models_started':0,'new_grants':0,'production_changes':0}
put(D/'CPU_PREFIX_CONSUMER_QUALIFICATION.json',report);print(json.dumps({'status':'PASS','checks':len(checks),'root':str(root),'sources':report['sources']}))
