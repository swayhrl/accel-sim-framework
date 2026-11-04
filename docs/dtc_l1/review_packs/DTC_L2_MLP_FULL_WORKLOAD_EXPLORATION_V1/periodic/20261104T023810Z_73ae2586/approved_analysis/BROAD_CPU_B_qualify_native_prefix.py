"""Finite primary/IR actual native-prefix qualification, real gate, mock fork."""
import sys
sys.dont_write_bytecode=True
import pathlib,json,os,importlib.util
P=pathlib.Path;D=P(__file__).parent
def guard(event,args):
 if event in ['subprocess.Popen','os.exec','os.system','os.kill','os.killpg']:raise RuntimeError('NO_REAL_MODEL_FORK_EXEC_OR_SIGNAL')
 if event=='open':
  p,mode,flags=args
  if (isinstance(mode,str)and any(c in mode for c in 'wax+'))or flags&(os.O_WRONLY|os.O_RDWR):
   if isinstance(p,(str,bytes)):assert P(os.fsdecode(p)).resolve().is_relative_to(D.resolve()),'OUTSIDE_OWN_FIXTURE_ROOT'
sys.addaudithook(guard)
s=importlib.util.spec_from_file_location('actual_broad_prefix_builder',D/'cpu_prefix_fixture.py');F=importlib.util.module_from_spec(s);s.loader.exec_module(F);rows=[]
for kind in ['PRIMARY','IR']:
 f=F.build_fixture(kind=kind);r=F.run_prefix(f);resource=F.replay_new_resource(r);extra=F.load('broad_actual_obs_'+f.root.name,f.cfg['source_paths']['extra_strict']);contract=extra.normalize_contract(f.cfg,f.root,qualification_only=True);proof=extra.terminal(f.c,resource,root=f.root,contract=contract,authority=f.q)
 docs=[r.intent,F.read(r.out/'NATIVE_LAUNCH.json'),F.read(r.out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')];assert all(x[f.producer.FIELD]==docs[0][f.producer.FIELD]and x['additional_cpu_shared_timeslice_binding']==docs[0]['additional_cpu_shared_timeslice_binding']for x in docs)
 assert len(f.calls)==1 and f.calls[0]['argv'].count('--seccomp-bpf')==1
 assert '--seccomp-bpf'not in F.read(r.out/'STRACE_BPF_OBSERVATION_SNAPSHOT.json')['expected_argv_before']
 assert 'additional_cpu_spare_memory_admission_strict'not in proof
 obs=proof['additional_strace_bpf_observation_strict'];shared=proof['additional_cpu_shared_timeslice_strict'];assert obs['activation']['model_Seccomp']==2 and obs['activation']['model_filters']==1
 rows.append(dict(kind=kind,cohort=f.c,uuid=r.intent['uuid'],root=str(f.root),out=str(r.out),cycles=proof['cycles'],full_expected_counts=f.spec['expected'],strict_resource_status=shared['status'],strict_observation_status=obs['status'],sources_observation=f.cfg['qualified_sources'],sources_resource=f.memcfg['qualified_sources'],three_bindings_equal=True,raw_BPF_activation_standin_verified=True,real_Main_approval_sha256=f.cfg['broad_approval_sha256'],real_Main_gate_sha256=f.cfg['canary4_prerequisite_sha256'],primary_statistics_excluded=obs['primary_statistics_excluded']))
result=dict(status='PASS_PRIMARY_AND_IR_ACTUAL_NATIVE_PREFIX_TO_MOCK_ONLY',count=len(rows),rows=rows,actual_models_started=0,new_grants=0,production_changes=0,production_release_eligible=False,standins=['private authority/root; exact real scope science preserved','mock Popen/proc/CPU/memory/progress/physics leaf','actual immutable real Main engineering4 gate/approval/artifact chain consumed','actual frozen native/observer/IO/new resource/new observation executed','no actual archive transfer'])
p=D/'CPU_NATIVE_PREFIX_QUALIFICATION.json'
if p.exists():
 old=D/('DEVELOPMENT_PREIMAGE_'+F.sha(p)+'.json')
 if not old.exists():old.write_bytes(p.read_bytes())
F.put(p,result);print(json.dumps(dict(path=str(p),sha256=F.sha(p),status=result['status'])))
