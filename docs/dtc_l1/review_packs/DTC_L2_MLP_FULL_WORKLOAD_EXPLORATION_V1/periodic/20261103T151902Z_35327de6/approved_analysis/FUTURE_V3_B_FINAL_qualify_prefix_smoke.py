"""Two new V3 prefix integration cases; no rerun of old V2 qualification."""
import sys
sys.dont_write_bytecode=True
import pathlib,os,json,hashlib,importlib.util
P=pathlib.Path;D=P(__file__).parent
def guard(event,args):
 if event in ['subprocess.Popen','os.exec','os.system','os.kill','os.killpg']:raise RuntimeError('V3_NO_REAL_PROCESS_OR_SIGNAL')
 if event=='open':
  p,mode,flags=args
  if (isinstance(mode,str)and any(c in mode for c in 'wax+'))or flags&(os.O_WRONLY|os.O_RDWR):
   if isinstance(p,(str,bytes)):assert P(os.fsdecode(p)).resolve().is_relative_to(D.resolve())
sys.addaudithook(guard)
s=importlib.util.spec_from_file_location('V3actualfixture',D/'cpu_prefix_fixture.py');fmod=importlib.util.module_from_spec(s);s.loader.exec_module(fmod);cases=[]
for kind in ['PRIMARY','IR']:
 f=fmod.build_fixture(kind=kind);r=fmod.run_prefix(f);old=fmod.replay_old_additional(r);snap=fmod.read(r.out/'STRACE_BPF_OBSERVATION_SNAPSHOT.json');docs=[r.intent,fmod.read(r.out/'NATIVE_LAUNCH.json'),fmod.read(r.out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')]
 assert len(f.calls)==1 and all(d[f.producer.FIELD]==docs[0][f.producer.FIELD]for d in docs)
 assert docs[0][f.producer.FIELD]['schema']=='DTC_STRACE_FUTURE_ENTRY_V3'and snap['scope_policy']['primary_statistics_excluded']==(kind=='IR')
 assert old['additional_cpu_spare_memory_admission_strict']['status']=='PASS_CPU_SPARE_MEMORY_IO_AND_ORIGINAL_PERFORMANCE'
 extra=fmod.load('V3_actual_new_extra',f.cfg['source_paths']['extra_strict']);contract=extra.normalize_contract(f.cfg,f.root,qualification_only=True);proof=extra.terminal(f.c,old,root=f.root,contract=contract,authority=f.q)
 assert proof['additional_strace_bpf_observation_strict']['mode']=='BPF_REQUIRED'
 cases.append(dict(kind=kind,root=str(f.root),cohort=f.c,uuid=r.intent['uuid'],out=str(r.out),old_CPU2_IO_replayed=True,new_V3_extra_replayed=True,cycles=r.base_proof['cycles'],CPU_fixture=True))
out=dict(status='PASS_V3_TWO_NATIVE_PREFIX_SMOKE_CPU_ONLY',cases=cases,qualified_sources=f.cfg['qualified_sources'],source_paths=f.cfg['source_paths'],policy_source_sha256=f.cfg['policy_source_sha256'],actual_original_native_observer_and_CPU2_IO_executed=True,Popen_and_original_physics_and_4canary_gate_are_explicit_CPU_standins=True,all_real_processes_and_signals_forbidden=True,actual_model_starts=0,production_changes=0,production_release_eligible=False)
fmod.put(D/'CPU_PREFIX_SMOKE.json',out);print(json.dumps(dict(path=str(D/'CPU_PREFIX_SMOKE.json'),sha256=fmod.sha(D/'CPU_PREFIX_SMOKE.json'),cases=cases)))
