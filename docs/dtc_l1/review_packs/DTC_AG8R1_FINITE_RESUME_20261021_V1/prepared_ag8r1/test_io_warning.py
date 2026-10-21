"""Focused user-amendment CPU checks. Synthetic samples; no simulator or signals."""
import copy,hashlib,importlib.util,json,sys,time
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parent;R=P.parents[3]
sys.path.insert(0,str(D))
import runtime_io_warning as amended
import runtime_policy_b as prior
oldpath=R/'docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/prepared_ag6/resources_v2.py'
spec=importlib.util.spec_from_file_location('immutable_original_resources',oldpath);resources=importlib.util.module_from_spec(spec);spec.loader.exec_module(resources)
E=Path('/workspace/dtc-ag8r1-finite-resume-174-v1/evidence')
baseline=json.loads((E/'c2_c3_once/admissions/AD_GEMM_window1/FIRST.json').read_text())['snapshot']
G=1024**3;started=10**9
baseline=copy.deepcopy(baseline);baseline.update(monotonic_ns=started,host_MemAvailable_bytes=64*G,disk_free_bytes=32*G)
baseline['cgroup'].update({'memory.max':'max','memory.swap.current':0});baseline['pswpin']=baseline['pswpout']=0
for pressure in (baseline['pressure'],baseline['cgroup_pressure_parsed']):
 for kind in ('memory','io'):pressure[kind]['full']['avg10']='0'
safety={k:True for k in amended.SAFETY_KEYS};impact=dict(known_scope=True,harm_detected=False,conservative_host_episode_profile_accepted=True)
def new(cls=amended.RuntimePolicyB):return cls(copy.deepcopy(baseline),E,resource_module=resources,started_ns=started,opt_in=True)
def obs(policy,seconds,*,high=True,change=None,checks=None,completed=None):
 s=copy.deepcopy(baseline);s['monotonic_ns']=started+seconds*10**9
 if high:
  s['pressure']['io']['full']['avg10']=s['cgroup_pressure_parsed']['io']['full']['avg10']='99.0'
 if change:change(s)
 return policy.observe(s,0,0,progress=dict(mono_ns=s['monotonic_ns'],completed=seconds if completed is None else completed,end='NONE'),safety_checks=safety if checks is None else checks,io_impact=impact)
def check(value,name):
 assert value,name
 cases.append(name)
cases=[];t=time.monotonic()
p=new();old=new(prior.RuntimePolicyB)
for sec in range(10,21600,10):
 result=obs(p,sec);assert result['decision']!='STOP',result
 if sec<=70:previous=obs(old,sec)
check(any('IO_FULL' in x for x in previous['stop_reasons']),'old_high_host_IO_stops_at_qualified_persistence')
check(p.high_since_ns is not None and result['warnings'],'sustained_host_and_cgroup_IO_warn_through_21590s')
check('WALL_DEADLINE_21600S' in obs(p,21600)['stop_reasons'],'21600s_deadline_still_hard')
check(obs(new(),10,change=lambda s:s.update(disk_free_bytes=5*G))['decision']=='STOP','disk_5GiB_still_hard')
check(obs(new(),10,change=lambda s:s.update(host_oom_kill=s['host_oom_kill']+1))['decision']=='STOP','host_OOM_still_hard')
check(obs(new(),10,change=lambda s:s['cgroup']['events'].update(oom=s['cgroup']['events']['oom']+1))['decision']=='STOP','cgroup_OOM_still_hard')
check(obs(new(),10,change=lambda s:s.update(host_MemAvailable_bytes=7*G))['decision']=='STOP','memory_headroom_still_hard')
p=new()
for sec in (10,20,30):z=obs(p,sec,change=lambda s:s['cgroup'].update({'memory.swap.current':16*1024**2}))
check(z['decision']=='STOP','persistent_swap_still_hard')
p=new()
for sec in (10,40,70):z=obs(p,sec,change=lambda s:s['pressure']['memory']['full'].update(avg10='11'))
check(z['decision']=='STOP','persistent_memory_PSI_still_hard')
p=new()
for sec in range(10,601,10):z=obs(p,sec,completed=0)
check('NO_SEMANTIC_RETIREMENT_600S' in z['stop_reasons'],'no_retirement_600s_still_hard')
check(obs(new(),31)['decision']=='STOP','missing_sample_cadence_still_hard')
check(obs(new(),10,checks=dict(safety,identity=False))['decision']=='STOP','identity_still_hard')
# Exercise exact amended entry gate rather than a test-only analogue.
spec=importlib.util.spec_from_file_location('entry',P/'ag8r1_io_warning_entry.py');entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(entry)
source=(P/'ag8r1_io_warning_entry.py').read_text()
check("values.pop(k)" in source and "k.endswith(('host_io_full_avg10','cgroup_io_full_avg10'))" in source,'both_single_and_paired_admission_remove_only_IO_keys')
check(amended.PROFILE==prior.PROFILE and amended.TerminalClosure.observe.__code__.co_code==prior.TerminalClosure.observe.__code__.co_code,'wall_progress_and_terminal_closure_unchanged')
# Original C1 qualified source remains byte-identical, avoiding historical receipt recertification.
c1=json.loads((E/'c1_cpu_once/RESULT.json').read_text())
check(all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==v for p,v in c1['actual_wall_result']['source_sha256'].items()),'original_C1_four_qualified_subjects_unchanged')
result=dict(status='PASS_USER_IO_WARNING_TARGETED_TESTS',declared_synthetic=True,case_count=len(cases),cases=cases,synthetic_long_run_samples=2159,elapsed_s=time.monotonic()-t,simulator_starts=0,process_signals=0,historical_suites_reexecuted=False,source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).resolve(),D/'runtime_io_warning.py',D/'controller_pipeline.py',D/'ag7_runner.py',D/'authority_dispatch.py',D/'ag7_strict.py',P/'ag8r1_io_warning_entry.py',P/'USER_IO_WARNING_AMENDMENT.json']})
with (E/'io_warning_route_repair/QUALIFICATION.json').open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps(result))
