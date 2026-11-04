"""Three new-mode actual native prefixes to mock fork; no real model."""
import sys
sys.dont_write_bytecode=True
import pathlib,json,importlib.util,os,copy
P=pathlib.Path;D=P(__file__).parent
def guard(event,args):
 if event in ['subprocess.Popen','os.exec','os.system','os.kill','os.killpg']:raise RuntimeError('CPU_FIXTURE_FORBIDS_REAL_FORK_EXEC_SIGNAL')
 if event=='open':
  p,mode,flags=args
  if (isinstance(mode,str)and any(c in mode for c in 'wax+'))or flags&(os.O_WRONLY|os.O_RDWR):
   if isinstance(p,(str,bytes)):assert P(os.fsdecode(p)).resolve().is_relative_to(D.resolve()),'OUTSIDE_OWN_CPU_ROOT'
sys.addaudithook(guard)
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
F=load('stage2_actual_cpu_builder',D/'cpu_prefix_fixture.py');rows=[]
for c,mode in F.load('stage2_scope_only',D/'strace_entry.py').SCOPE_MODES.items():
 if c.endswith('731af5428c4b8155-DH-P0-OBSCTRL-V1'):continue
 f=F.build_fixture(cohort=c,mode=mode);r=F.run_prefix(f);resource=F.replay_new_resource(r);extra=F.load('stage2_new_observation_'+f.root.name,f.cfg['source_paths']['extra_strict'])
 contract=extra.normalize_contract(F.read(f.cfg['exclusion_contract_path']),f.root,f.cfg['exclusion_contract_sha256'],True,cfg=f.cfg)
 proof=extra.terminal(f.c,resource,root=f.root,contract=contract,authority=f.q)
 argv=f.calls[0]['argv'];snap=F.read(r.out/'STRACE_BPF_OBSERVATION_SNAPSHOT.json');before=snap['expected_argv_before']
 assert len(f.calls)==1 and argv==f.producer.mode_argv(before,mode)
 assert (argv.count('--seccomp-bpf')==1)if mode=='BPF_REQUIRED'else('--seccomp-bpf'not in argv)
 docs=[r.intent,F.read(r.out/'NATIVE_LAUNCH.json'),F.read(r.out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')]
 assert all(x[f.producer.FIELD]==docs[0][f.producer.FIELD]and x['additional_cpu_shared_timeslice_binding']==docs[0]['additional_cpu_shared_timeslice_binding']for x in docs)
 obs=proof['additional_strace_bpf_observation_strict'];assert proof['cycles']==f.reference_cycles and obs['activation']['model_Seccomp']==(2 if mode=='BPF_REQUIRED'else 0)and obs['activation']['model_filters']==(1 if mode=='BPF_REQUIRED'else 0)
 assert 'additional_cpu_spare_memory_admission_strict'not in proof and snap['scope_extension_approval_utf8']==P(f.cfg['scope_extension_approval_path']).read_text()
 assert f.producer.INITIAL in f.q['consumed']and f.q['consumed'][f.producer.INITIAL]['uuid']=='2d24a1be-db7b-4100-9752-42b16ea46035'
 rows.append(dict(cohort=c,mode=mode,root=str(f.root),out=str(r.out),uuid=r.intent['uuid'],reference_cycles=f.reference_cycles,counts=f.spec['expected'],resource_status=resource['additional_cpu_shared_timeslice_strict']['status'],observation_status=obs['status'],activation=obs['activation'],source_observation=f.cfg['qualified_sources'],source_resource=f.memcfg['qualified_sources'],scope_extension_approval_sha256=f.cfg['scope_extension_approval_sha256'],three_bindings_equal=True,one_flag_only_when_BPF=True,first_consumed_birth_unchanged=True))
out=dict(status='PASS_STAGE2_THREE_NEW_MODE_NATIVE_PREFIXES_TO_MOCK_ONLY',prefixes=rows,count=len(rows),standins=['private authority/root and source-qualified fixture CPU counters','mock Popen/proc/progress/resources/physics leaf','actual old native/observer/atomicIO and new resource/observation strict executed','no real archive transfer; not actual canary qualification'],actual_model_starts=0,new_grants=0,production_changes=0,production_release_eligible=False)
old=D/'CPU_STAGE2_PREFIX_QUALIFICATION.json'
if old.exists():
 pre=D/('DEVELOPMENT_PREIMAGE_'+F.sha(old)+'.json')
 if not pre.exists():pre.write_bytes(old.read_bytes())
F.put(D/'CPU_STAGE2_PREFIX_QUALIFICATION.json',out);print(json.dumps(dict(path=str(D/'CPU_STAGE2_PREFIX_QUALIFICATION.json'),sha256=F.sha(D/'CPU_STAGE2_PREFIX_QUALIFICATION.json'),status=out['status'])))
