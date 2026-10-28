"""Library-only CPU qualification; synthetic authority/native receipt sinks.
One REAL >=.5s host CPU double sample is recorded truthfully (PASS or HOLD).
No owner attach, real native process/INTENT, registration or simulation.
"""
from pathlib import Path as P
import copy,json,types,os,time,sys
import cpu_fixture as F
f=F.fixture();lib=f.lib;D=F.D;checks=[]
def ck(n,v):assert v,n;checks.append(n)
def reject(n,fn):
 try:fn()
 except(RuntimeError,AssertionError,KeyError,ValueError):checks.append(n);return
 raise AssertionError(n+' accepted')
def ev(cpu=None):return F.evidence(lib,cpu)
lib.validate(f.cfg,f.q);ck('separate_schema_and_unchanged_old39_record_valid',lib.ID!=lib._OLD.ID and f.q['additional_operational_overlays'][lib._OLD.ID]['allowed_cohorts']==f.oldcfg['allowed_cohorts'])
a=lib.verify_cpu_evidence(ev(2),2);ck('synthetic_two_sample_visible_quota_spare8_distinct_cores',a['spare_physical_core_count']==8 and a['hidden_ancestor_limits_excluded']is False)
for name,mutate in [
 ('sample_short',lambda e:e['second'].update(monotonic=e['first']['monotonic']+.49)),
 ('sample_same',lambda e:e['second'].update(monotonic=e['first']['monotonic'])),
 ('different_boot',lambda e:e['second'].update(boot_id='OTHER_BOOT')),
 ('different_PID_birth',lambda e:e['second'].update(sampler_start_ticks=2)),
 ('different_UID_parent',lambda e:e['second'].update(sampler_ppid=0)),
 ('unknown_tasks',lambda e:e['second']['unreadable_tasks'].append('UNKNOWN')),
 ('hidden_falsely_excluded',lambda e:e['second']['cgroups'].update(hidden_ancestor_limits_excluded=True)),
 ('quota_used_plus1_over75pct',lambda e:e['second']['cgroups']['visible'][0]['stat'].update(usage_usec=8000000)),
 ('any_nr_throttle',lambda e:e['second']['cgroups']['visible'][0]['stat'].update(nr_throttled=1)),
 ('any_throttle_usec',lambda e:e['second']['cgroups']['visible'][0]['stat'].update(throttled_usec=1)),
 ('missing_usage_counter',lambda e:e['second']['cgroups']['visible'][0]['stat'].pop('usage_usec')),
 ('missing_throttle_counter',lambda e:e['second']['cgroups']['visible'][0]['stat'].pop('nr_throttled')),
 ('quota_changed',lambda e:e['second']['cgroups']['visible'][0].update(quota=['800000','100000'])),
 ('selected_not_legal',lambda e:e.update(selected_cpu=99)),
 ('all_cores_pinned_by_other_jobs',lambda e:e['second']['other_task_claims'].append(dict(affinity=list(range(16)),processor=0))),
 ('selected_busy_sibling',lambda e:e['second']['other_task_claims'].append(dict(affinity=[10],processor=10))),
 ('stale_collection',lambda e:e.update(created_monotonic=e['second']['completed_monotonic']+3))]:
 e=ev(2);mutate(e);reject(name,lambda e=e:lib.verify_cpu_evidence(e,2))
e=ev(2)
for c in [0,1,3,4,5]:e['second']['other_task_claims'].append(dict(affinity=[c],processor=c))
reject('fewer_than4_physical_cores_not_SMT_count',lambda:lib.verify_cpu_evidence(e,2))
raw=copy.deepcopy(f.base);old=lib.project(raw);ck('project_default_and_Tiny_path_keep_old_cpu_full_HOLD',old['physical_RAM_pass']is False and old['admission_decision']['pressure_reasons']==['cpu_pressure_full'])
value=lib.project_for_candidate(raw,f.cfg,f.C,selected_cpu=2,evidence=ev(2),context=dict(kind='OWNER_CHOOSE'));p=value['additional_cpu_spare_memory_admission_proof'];ck('only_new_explicit_generation_waives_cpu_full_raw_unchanged',value['physical_RAM_pass']and f.base==raw and p['raw_pressure_reasons']==['cpu_pressure_full']and p['old_V2_PRESSURE_PASS_claimed']is False and p['old95_resource_snapshot']['physical_RAM_pass']is False)
ck('pure_offline_owner_proof_verifies_without_Main_state',lib.verify_memory_proof(p)['mode']=='CPU_SPARE_SINGLETON')
reject('OWNER_CHOOSE_never_native_strict',lambda:lib.verify_memory_proof(p,require_native=True))
frame=lib.project_for_candidate(lib._OLD.project(raw),f.cfg,f.C,evidence=ev(),context=dict(kind='OWNER_FRAME'));ck('already_old95_frame_unwrap_no_doublecount_and_selected_None',frame['total_projected_additional_RAM_bytes']==raw['total_projected_additional_RAM_bytes']and frame['additional_cpu_spare_memory_admission_proof']['context']['kind']=='OWNER_FRAME')
reject('other_cohort_cannot_use_singleton',lambda:lib.project_for_candidate(raw,f.cfg,'NOT_ALLOWED',evidence=ev()))
bad=copy.deepcopy(raw);bad['admission_decision']['pressure_reasons']+=['memory_pressure_full'];v=lib.project_for_candidate(bad,f.cfg,f.C,evidence=ev());ck('other_pressure_not_waived',v['physical_RAM_pass']is False and v['admission_decision']['pressure_reasons']==['memory_pressure_full'])
badp=copy.deepcopy(p);badp['base_resource_snapshot']['own_ram_forecasts'][0]['additional_reserved_bytes']-=1;badp['old95_resource_snapshot']=lib._OLD.project(badp['base_resource_snapshot']);reject('full_peer_own_growth_math_not_sufficient_without_sum',lambda:lib.verify_memory_proof(badp))
badp=copy.deepcopy(p);badp['cpu_evidence']['sampler_source_sha256']='0'*64;reject('sampler_source_wrongSHA',lambda:lib.verify_memory_proof(badp))
saved_sampler=lib.sample_cpu_evidence;lib.sample_cpu_evidence=lambda selected_cpu=None,**kwargs:ev(selected_cpu)
actual_spec=F.read(F.R/'control/specs'/(f.C+'.json'));actual_cost=actual_spec['estimated_peak_model_RAM_bytes'];outroot=f.root/'native_fixtures';outroot.mkdir();runtime=dict(EXACT_RUNTIME_OLD=True)
def native(cohort,base=None):
 base=copy.deepcopy(f.base if base is None else base);base['own_ram_forecasts']=[dict(cohort=cohort,kind='CLAIM_OR_CANDIDATE',RSS_bytes=0,additional_reserved_bytes=actual_cost)];base['total_projected_additional_RAM_bytes']=3*F.G+actual_cost;base['admission_decision']['additional_reserved_RAM_bytes']=base['total_projected_additional_RAM_bytes']
 spec=copy.deepcopy(actual_spec);spec.update(cohort=cohort,host_cpu=2);n=types.SimpleNamespace(__file__=str(F.R/'tools/l2_native.py'),registered=lambda:(None,None,f.q,None),assert_parent_lease=lambda:dict(pid=99999990,start_ticks=1,fd=17,controller_sha256='CPU_ONLY'),spec_for=lambda c:copy.deepcopy(spec),resources=lambda s,fresh_source=False:copy.deepcopy(base)if fresh_source else runtime)
 def engine():return types.SimpleNamespace(exclusive=lambda path,obj:F.put(path,obj))
 n.engine=engine;return n,base
n,nbase=native(f.C);lib.install_future_native(n,f.cfg,False,invocation_cohort=f.C);nv=n.resources(n.spec_for(f.C),True);ck('native_with_own_claim_preserves_all_RAM_and_selected_core',nv['physical_RAM_pass']and nv['total_projected_additional_RAM_bytes']==nbase['total_projected_additional_RAM_bytes']and n.resources({},False)is runtime)
e=n.engine();out=outroot/'CPU_SINGLETON';out.mkdir();ip=out/'CPU.INTENT.json';e.exclusive(ip,dict(cohort=f.C,uuid='CPU_ONLY_NOT_A_SCIENCE_GENERATION',output=str(out)));e.exclusive(out/'NATIVE_LAUNCH.json',dict(CPU_fixture_no_real_model=True));e.exclusive(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',dict(CPU_fixture_no_real_PID=True));docs=[F.read(x)for x in [ip,out/'NATIVE_LAUNCH.json',out/'NATIVE_SIMULATOR_PID_AND_MAPS.json']];b=docs[0]['additional_cpu_spare_memory_admission_binding'];snap=F.read(out/'CPU_SPARE_MEMORY_ADMISSION_SNAPSHOT.json')
ck('three_new_bindings_sidecar_no_oldCPU_PASS_and_NOFLAG',all(d['additional_cpu_spare_memory_admission_binding']==b for d in docs)and b['padding_optin']is False and b['mode']=='CPU_SPARE_SINGLETON'and F.sha(out/'CPU_SPARE_MEMORY_ADMISSION_SNAPSHOT.json')==b['snapshot_sha256']and snap['invocation']['selected_cpu']==b['selected_cpu']==2)
ck('final_fresh_selectedCPU_forecast_and_claim_verified',all(lib.verify_memory_proof(p,require_native=True)['selected_cpu']==2 for p in snap['fresh_preflights'])and b['final_cpu_evidence_sha256']==lib.objsha(snap['fresh_preflights'][-1]['cpu_evidence']))
tamper=copy.deepcopy(snap['fresh_preflights'][-1]);tamper['base_resource_snapshot']['own_ram_forecasts']=[];tamper['base_resource_snapshot']['total_projected_additional_RAM_bytes']=3*F.G;tamper['base_resource_snapshot']['admission_decision']['additional_reserved_RAM_bytes']=3*F.G;tamper['old95_resource_snapshot']=lib._OLD.project(tamper['base_resource_snapshot']);tamper['growth_unchanged_bytes']=3*F.G;tamper['effective_decision'].update(additional_reserved_RAM_bytes=3*F.G);reject('native_candidate_omission_even_after_recomputed_math',lambda:lib.verify_memory_proof(tamper,require_native=True))
bad=copy.deepcopy(snap['fresh_preflights'][-1]);bad['context']['kind']='OWNER_FRAME';reject('native_rejects_relabelled_owner_frame',lambda:lib.verify_memory_proof(bad,require_native=True))
f.q['consumed'][f.C]=dict(uuid='CPU_FIXTURE_SPENT');lib.validate(f.cfg,f.q);ck('singleton_consumed_does_not_invalidate_other39',True);n2,_=native(f.C);reject('spent_native_singleton_no_retry',lambda:lib.install_future_native(n2,f.cfg,False,invocation_cohort=f.C));f.q['consumed'].pop(f.C)
n2,_=native(f.C);reject('CPU_exception_padding_flag_forbidden',lambda:lib.install_future_native(n2,f.cfg,True,invocation_cohort=f.C))
other=next(c for c in f.oldcfg['allowed_cohorts']if c!=f.C);n2,_=native(other);lib.install_future_native(n2,f.cfg,False,invocation_cohort=other);ck('nonCPU_old39_exact_old95_delegate_not_old88_or_newCPU',hasattr(n2,'_FUTURE_MEMORY_BINDING')and not hasattr(n2,'_CPU_SPARE_MEMORY_BINDING')and n2._FUTURE_MEMORY_BINDING['cfg_sha256']==lib.objsha(f.oldcfg)and n2.resources({},True)['admission_decision']['memory_utilization_fraction']==.95 and not n2.resources({},True)['physical_RAM_pass'])
future='CPU_FIXTURE_FUTURE_PRIMARY';f.cfg['allowed_cohorts'].append(future);f.q['admitted_specs'][future]='CPU_FIXTURE_NOT_A_SCIENCE_CANONICAL';f.q['additional_operational_overlays'][lib.ID]=dict(lib.record(f.cfg),status='ACTIVE')
n3,_=native(future);lib.install_future_native(n3,f.cfg,False,invocation_cohort=future);ck('future_memoryonly_keeps_old_cpu_full_HOLD',not n3.resources({},True)['physical_RAM_pass'])
n4,mbase=native(future);mbase['admission_decision']['pressure_reasons']=[];lib.install_future_native(n4,f.cfg,False,invocation_cohort=future);o=outroot/'CPU_MEMORYONLY';o.mkdir();x=n4.engine();x.exclusive(o/'ONLY.INTENT.json',dict(cohort=future,output=str(o)));msnap=F.read(o/'CPU_SPARE_MEMORY_ADMISSION_SNAPSHOT.json');ck('future_memoryonly_new_lineage_passes_without_CPU_waiver',msnap['mode']=='MEMORY_ONLY_OLD_CPU_RULES'and all(lib.verify_memory_proof(p,require_native=True)['mode']=='MEMORY_ONLY_OLD_CPU_RULES'and 'cpu_evidence'not in p for p in msnap['fresh_preflights']))
lib.sample_cpu_evidence=saved_sampler
real=lib.sample_cpu_evidence(sample_seconds=.5);F.put(f.root/'ACTUAL_READONLY_CPU_DOUBLE_SAMPLE.json',real);ck('REAL_host_double_sample_recorded_honestly_no_model',real['second']['monotonic']-real['first']['monotonic']>=.5 and real['second']['cgroups']['hidden_ancestor_limits_excluded']is False)
if real['eligible']:ck('actual_sample_PASS_replays_offline',lib.verify_cpu_evidence(real)['status'].startswith('PASS'))
else:ck('actual_sample_HOLD_is_not_faked_as_resource_PASS',real['assessment']['status']=='HOLD')
report=dict(status='PASS',schema='CPU_SPARE_LIBRARY_ONLY_QUALIFICATION_V1',cpu_spare_library_qualified=True,native_binding_qualified=True,source_sha256=F.sha(D/'cpu_memory.py'),driver_sha256=F.sha(__file__),builder_sha256=F.sha(D/'cpu_fixture.py'),checks=checks,passed=len(checks),fixture=str(f.root),actual_readonly_sample_path=str(f.root/'ACTUAL_READONLY_CPU_DOUBLE_SAMPLE.json'),actual_readonly_sample_sha256=F.sha(f.root/'ACTUAL_READONLY_CPU_DOUBLE_SAMPLE.json'),actual_sample_eligible=real['eligible'],actual_assessment=real['assessment'],CPU_pid=os.getpid(),native_receipt_sinks_and_authority_are_CPU_FIXTURES_NOT_SCIENCE=True,role_paths_for_owner_strict_are_fixture_placeholders_pending_E_join=True,qualified_library_source_only=True,production_mutations=0,models_started=0,grants_added=0,signals=0)
F.put(D/'CPU_LIBRARY_QUALIFICATION.json',report);print(json.dumps(dict(status='PASS',checks=len(checks),source_sha256=report['source_sha256'],CPU_pid=os.getpid(),actual_sample_eligible=real['eligible'],report=str(D/'CPU_LIBRARY_QUALIFICATION.json'))))
