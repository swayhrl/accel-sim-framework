"""Isolated real native prefix to mocked Popen. Every real fork/signal forbidden."""
import sys
sys.dont_write_bytecode=True
import pathlib,json,hashlib,importlib.util,copy,os,types
P=pathlib.Path;D=P(__file__).parent
def guard(event,args):
 if event in ['subprocess.Popen','os.exec','os.system','os.kill','os.killpg']:raise RuntimeError('CPU_PREFIX_FORBIDS_REAL_PROCESS_OR_SIGNAL '+event)
 if event=='open':
  path,mode,flags=args
  write=isinstance(mode,str)and any(x in mode for x in 'wax+')or flags&os.O_WRONLY or flags&os.O_RDWR
  if write and isinstance(path,(str,bytes)):
   assert P(os.fsdecode(path)).resolve().is_relative_to(D.resolve()),'CPU_PREFIX_WRITE_OUTSIDE_ISOLATED_ROOT'
sys.addaudithook(guard)
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def reject(fn):
 try:fn()
 except Exception:return
 raise AssertionError('Expected HOLD')
fmod=load('B_actual_prefix_fixture',D/'cpu_prefix_fixture.py');checks=[];fixtures=[]
def ck(n,b):assert b,n;checks.append(n)
before=read(D.parent/'strace_bpf_future_integration_v1/ACTUAL_ENTRY_AND_ANCESTRY_READONLY.json')['source_pins'];sharedPopen=__import__('subprocess').Popen
contract=read(D.parents[2]/'coordinator/bpf_canary_orchestration_v1/ENGINEERING_EXCLUSION_CONTRACT.json')
for mode in ['BPF_REQUIRED','DEFAULT_CONTROL']:
 actual_c=next(c for c,row in contract['scope_cohorts'].items()if row['program']=='heartwall'and row['mode']==mode)
 f=fmod.build_fixture(mode=mode,cohort=actual_c);v=fmod.run_prefix(f);fixtures.append(dict(root=str(v.root),cohort=v.c,uuid=v.intent['uuid'],out=str(v.out),mode=mode))
 docs=[v.intent,read(v.out/'NATIVE_LAUNCH.json'),read(v.out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')];b=docs[0][f.producer.FIELD];snap=read(v.out/'STRACE_BPF_OBSERVATION_SNAPSHOT.json');act=read(v.out/'STRACE_BPF_ACTIVATION.json');fork=read(v.out/'STRACE_BPF_FORK_PLAN.json')
 ck(mode+' real unchanged native+observer prefix charges exactly one private UUID and publishes3equal bindings',len(f.calls)==1 and all(x[f.producer.FIELD]==b for x in docs)and f.q['consumed'][f.c]['charged']==1 and f.q['consumed'][f.c]['uuid']==v.intent['uuid'])
 ck(mode+' explicit flag/default command is actual same recorded argv and exact model arguments',docs[1]['argv']==f.calls[0]['argv']==snap['expected_argv_after']and docs[1]['argv'][-len(f.spec['native_simulator_argv']):]==f.spec['native_simulator_argv']and('--seccomp-bpf'in docs[1]['argv'])==(mode=='BPF_REQUIRED')and fork['argv_list_mutated_in_place'])
 ck(mode+' double-stat status/PID/tracer/baseline activation sidecar is joined to3bindings and launch',act['verdict']['status']==('PASS_BPF_REQUIRED_ACTIVE'if mode=='BPF_REQUIRED'else'PASS_DEFAULT_CONTROL_NO_BPF')and sha(v.out/'STRACE_BPF_ACTIVATION.json')==docs[2]['strace_observation_activation_sha256']and sha(v.out/'STRACE_BPF_FORK_PLAN.json')==docs[1]['strace_fork_plan_sha256']==act['fork_plan_sha256'])
 ck(mode+' original atomicIO + CPU2 bindings and fresh fullcost preflights remain present',all(x['additional_shared_json_io_binding']==docs[0]['additional_shared_json_io_binding']and x['additional_cpu_spare_memory_admission_binding']==docs[0]['additional_cpu_spare_memory_admission_binding']and x['shared_json_publication_binding']['publication']=='FSYNC_SAME_DIRECTORY_LINK_NOREPLACE'for x in docs)and len(read(v.out/'CPU_SPARE_MEMORY_ADMISSION_SNAPSHOT.json')['fresh_preflights'])==4)
 ck(mode+' source UTF8/current canonicalNone/resolvedCPU/formal Main contract preserved',all(hashlib.sha256(x['utf8'].encode()).hexdigest()==x['sha256']==f.cfg['qualified_sources'][r]for r,x in snap['source_snapshots'].items())and b['canonical_spec_sha256']==sha(f.root/'control/specs'/(f.c+'.json'))and b['dispatch_binding_sha256']==sha(f.root/'control/dispatch_bindings'/(f.c+'.json'))and json.loads(snap['canonical_spec_utf8'])['host_cpu']is None and snap['resolved_spec']['host_cpu']==0 and f.cfg['exclusion_contract_sha256']=='4d7e1d1990771d8dc8bc1a9afe6ea85b9dae0f8752e951332742664a28dd0aa7')
 original=(f.root/'control/qualification_ledger'/(f.c+'.INTENT.json')).read_bytes();reject(lambda:f.producer.atomic_exclusive(f.root/'control/qualification_ledger'/(f.c+'.INTENT.json'),{'replace':True}));ck(mode+' exclusive one-start bytes cannot be overwritten',original==(f.root/'control/qualification_ledger'/(f.c+'.INTENT.json')).read_bytes())
 priorcalls=len(f.calls);reject(lambda:f.front.main(['experiment','run-native',f.c,'--project','DTC_L1'],cfg=f.cfg,native_module=f.native,hooks=f.hooks,memory_cfg_override=f.memcfg));ck(mode+' consumed identity never retries or silently falls back',len(f.calls)==priorcalls)
 f.producer.restore_private(f.native);ck(mode+' private native functions reverse close without shared subprocess change',not hasattr(f.native,'_STRACE_ENTRY_V2')and __import__('subprocess').Popen is sharedPopen)
 # Real existing CPU2+IO extra uses this actual prefix; base physics is an explicit stand-in.
 old=fmod.load('CPU_old_strict_AND',f.memcfg['extra_strict_path']);old.R=f.root;combined=old.terminal(f.c,v.base_proof);ck(mode+' existing CPU2 and IO additional strict actually replay produced prefix',combined['additional_cpu_spare_memory_admission_strict']['status']=='PASS_CPU_SPARE_MEMORY_IO_AND_ORIGINAL_PERFORMANCE'and combined['additional_shared_json_io_strict']['status']=='PASS_SHARED_JSON_IO_AND_ORIGINAL_STRICT');fmod.put(f.root/'CPU_ONLY_BASE_PROOF.json',combined)
# Missing/invalid source or unsupported baseline holds before INTENT (no fork/charge).
f=fmod.build_fixture(mode='BPF_REQUIRED');bad=copy.deepcopy(f.cfg);bad['expected_pins'][bad['native_source_path']]='0'*64;reject(lambda:f.front.main(['experiment','run-native',f.c,'--project','DTC_L1'],cfg=bad,native_module=f.native,hooks=f.hooks,memory_cfg_override=f.memcfg));ck('source drift blocks prior to INTENT and model fork',f.c not in f.q['consumed']and not f.calls)
f=fmod.build_fixture(mode='BPF_REQUIRED');old_reader=f.hooks['proc_reader']
def nested(pid):
 v=old_reader(pid);v['status_utf8']=v['status_utf8'].replace('TracerPid:\t0','TracerPid:\t99');return v
f.hooks['proc_reader']=nested;reject(lambda:fmod.run_prefix(f));ck('nested/unsupported baseline is explicit preINTENT HOLD with0private starts',f.c not in f.q['consumed']and not f.calls)
# Post-birth fallback is captured as unaccepted, never mislabeled DEFAULT_CONTROL.
f=fmod.build_fixture(mode='BPF_REQUIRED');old_reader=f.hooks['proc_reader']
def fallback(pid):
 v=old_reader(pid)
 if 'Seccomp:\t2'in v['status_utf8']:v['status_utf8']=v['status_utf8'].replace('Seccomp:\t2','Seccomp:\t0').replace('Seccomp_filters:\t1','Seccomp_filters:\t0')
 return v
f.hooks['proc_reader']=fallback;v=fmod.run_prefix(f);act=read(v.out/'STRACE_BPF_ACTIVATION.json');ck('postbirth ordinary-mode fallback stays BPF_REQUIRED but explicit unaccepted activation; no second identity/fork',act['mode']=='BPF_REQUIRED'and act['verdict']['status']=='HOLD_ACTIVATION_UNPROVEN'and len(f.calls)==1 and f.c in f.q['consumed'])
f=fmod.build_fixture(mode='DEFAULT_CONTROL');delegate=[];ret=f.front.main(['experiment','inspect','E2-DTCL2MLP-NONSELECTED','--project','DTC_L1'],cfg=f.cfg,native_module=f.native,delegate=lambda path,argv:delegate.append((path,argv))or'CPU_DELEGATE');ck('nonselected route exact delegates old native46 without private entry configuration',ret=='CPU_DELEGATE'and len(delegate)==1 and delegate[0][0]==f.cfg['default_native_entry']and not f.calls)
ck('old native46/fa3/CPU2/IO/observer/source pins remain exact after both modes and HOLD cases',all(sha(p)==h for p,h in before.items())and __import__('subprocess').Popen is sharedPopen)
out=dict(schema='B_STRACE_BPF_V2_ACTUAL_NATIVE_PREFIX_CPU_QUALIFICATION_V1',status='PASS_NATIVE_PREFIX_CPU_ONLY_NO_MODEL',count=len(checks),checks=checks,qualified_B_sources={str(p):sha(p)for p in[D/'strace_entry.py',D/'bpf_frontend.py',D/'native-entry/bin/experiment']},E_sources_used={str(p):sha(p)for p in[D.parent.parent/'E/strace_bpf_strict_consumer_v2/bpf_extra_strict.py',D.parent.parent/'E/strace_bpf_strict_consumer_v2/consumer_bridge.py']},fixtures=fixtures,unchanged_original_native_and_observer_code_executed=True,old_sharedIO_atomic_leaf_and_actual_CPU2_AND_replayed=True,controlled_standins=['authority/root/old prepare admission','resource samples/CPU evidence','Popen and PID/proc observations','BA progress/physics raw stdout'],original_GPU_physics_strict_NOT_executed=True,all_real_spawns_exec_signals_forbidden=True,all_writes_inside_isolated_B_fixture=True,new_ledger_consumption_is_private_fixture_only=True,actual_model_starts=0,production_changes=0,registry_changes=0,production_release_eligible=False,actual_native_canary_qualified=False)
p=D/'CPU_NATIVE_PREFIX_QUALIFICATION.json';fmod.put(p,out);print(json.dumps(dict(path=str(p),sha256=sha(p),count=len(checks),status=out['status'],fixtures=fixtures)))
