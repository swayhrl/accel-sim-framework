import sys
sys.dont_write_bytecode=True
import pathlib,os,importlib.util,json
P=pathlib.Path;D=P(__file__).parent
def guard(event,args):
 if event in ['subprocess.Popen','os.exec','os.system','os.kill','os.killpg']:raise RuntimeError('SHARED_CPU_FIXTURE_NO_REAL_PROCESS_OR_SIGNAL')
 if event=='open':
  p,mode,flags=args
  if (isinstance(mode,str)and any(c in mode for c in 'wax+'))or flags&(os.O_WRONLY|os.O_RDWR):
   if isinstance(p,(str,bytes)):assert P(os.fsdecode(p)).resolve().is_relative_to(D.resolve()),'WRITE_OUTSIDE_OWN_FIXTURE'
sys.addaudithook(guard)
s=importlib.util.spec_from_file_location('actual_SharedCPU_fixture',D/'cpu_prefix_fixture.py');fmod=importlib.util.module_from_spec(s);s.loader.exec_module(fmod)
f=fmod.build_fixture();r=fmod.run_prefix(f);resource=fmod.replay_new_resource(r);extra=fmod.load('actual_shared_observation_extra',f.cfg['source_paths']['extra_strict']);contract=extra.normalize_contract(fmod.read(f.cfg['exclusion_contract_path']),f.root,f.cfg['exclusion_contract_sha256'],True);proof=extra.terminal(f.c,resource,root=f.root,contract=contract,authority=f.q)
assert len(f.calls)==1 and '--seccomp-bpf'not in f.calls[0]['argv']and proof['cycles']==8551
docs=[r.intent,fmod.read(r.out/'NATIVE_LAUNCH.json'),fmod.read(r.out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')];assert all(x[f.producer.FIELD]==docs[0][f.producer.FIELD]and x['additional_cpu_shared_timeslice_binding']==docs[0]['additional_cpu_shared_timeslice_binding']for x in docs)
assert resource['additional_cpu_shared_timeslice_strict']['status']=='PASS_CPU_SHARED_TIMESLICE_IO_AND_ORIGINAL_PERFORMANCE'and 'additional_cpu_spare_memory_admission_strict'not in resource
report=dict(status='PASS_ACTUAL_SHARED_NATIVE_PREFIX_TO_MOCK_CPU_ONLY',root=str(f.root),out=str(r.out),cohort=f.c,uuid=r.intent['uuid'],cycles=8551,source_observation=f.cfg['qualified_sources'],source_resource=f.memcfg['qualified_sources'],resource_extra_status=resource['additional_cpu_shared_timeslice_strict']['status'],observation_extra=proof['additional_strace_bpf_observation_strict'],actual_old_native_observer_atomic_IO_executed=True,oldCPU2_PASS_not_claimed=True,three_resource_and_observer_bindings_equal=True,standins=['private authority and Root','mock Popen/PID/physics/progress/resource samples','CPU quota/busy counters from explicit source-bound fixture','original legal allocator genuinely replayed','no actual archive transfer'],actual_model_starts=0,production_changes=0,production_release_eligible=False)
fmod.put(D/'CPU_PREFIX_SMOKE.json',report);print(json.dumps(dict(path=str(D/'CPU_PREFIX_SMOKE.json'),sha256=fmod.sha(D/'CPU_PREFIX_SMOKE.json'),root=str(f.root),out=str(r.out),status=report['status'])))
