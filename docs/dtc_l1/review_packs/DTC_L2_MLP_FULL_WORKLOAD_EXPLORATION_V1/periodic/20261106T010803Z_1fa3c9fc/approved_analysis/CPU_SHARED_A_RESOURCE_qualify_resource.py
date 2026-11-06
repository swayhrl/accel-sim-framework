"""Necessary new shared resource contracts only; no old-suite replay."""
import pathlib,json,copy,hashlib,importlib.util,types,os,time,sys
sys.dont_write_bytecode=True
P=pathlib.Path;D=P(__file__).parent
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
fx=load('shared_resource_private_fixture',D/'cpu_fixture.py');f=fx.fixture();lib=f.lib;checks=[]
def check(name,condition):assert condition,name;checks.append(dict(name=name,status='PASS'))
def rejects(fn):
 try:fn()
 except Exception as e:return str(e)
 raise AssertionError('Required rejection did not occur')
i=f.inputs();value=lib.project_for_candidate(**i);proof=value[lib.PROOF]
check('busy90pct_timeslice_passes_quota_but_not_old_idle_spare',lib.verify_proof(proof)['CPU2_spare_PASS_claimed']is False and proof['cpu_assessment']['host_mean_busy']>.85 and bool(rejects(lambda:lib._CPU2.verify_cpu_evidence(i['evidence']['raw_cpu2_evidence'],0))))
actual=lib.sample_cpu_evidence(None,.5);actual_verdict=lib.verify_cpu_evidence(actual);check('actual_double_sample_shared_quota_assessment_not_idle_claim',actual_verdict['min_idle_core_rule_applied']is False and actual_verdict['hidden_ancestor_limits_excluded']is False)
for name,mutate in[
 ('quota_fraction_exceeded',lambda e:e['raw_cpu2_evidence']['second']['cgroups']['visible'][0]['stat'].update(usage_usec=999999999)),
 ('throttle_increment',lambda e:e['raw_cpu2_evidence']['second']['cgroups']['visible'][0]['stat'].update(nr_throttled=1)),
 ('missing_quota_counter',lambda e:e['raw_cpu2_evidence']['second']['cgroups']['visible'][0]['stat'].pop('usage_usec')),
 ('selected_CPU_not_allowed',lambda e:e['raw_cpu2_evidence'].update(selected_cpu=999)),
]:
 e=f.cpu(0);mutate(e);check(name,bool(rejects(lambda:lib.verify_cpu_evidence(e,0))))
for name,mutate in[
 ('full_RAM_gate',lambda i:i['base'].update(host_MemAvailable_bytes=10*1024**3)),
 ('disk_gate',lambda i:i['base'].update(physical_disk_pass=False)),
 ('other_pressure_not_ignored',lambda i:i['base']['admission_decision'].update(pressure_reasons=['cpu_pressure_full','memory_pressure_full'])),
 ('stale_snapshot',lambda i:i['base'].update(monotonic=time.monotonic()-20)),
 ('omitted_candidate_fullcost',lambda i:i['base'].update(own_ram_forecasts=[],total_projected_additional_RAM_bytes=3*1024**3)),
]:
 i=f.inputs();mutate(i);check(name,bool(rejects(lambda:lib.project_for_candidate(**i))))
oldscan='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V1';f.q['consumed'][oldscan]={'uuid':'PRIVATE_OLD_SCAN_NO_DONE'};fx.put(f.root/'control/qualification_ledger'/(oldscan+'.INTENT.json'),dict(cohort=oldscan,uuid='PRIVATE_OLD_SCAN_NO_DONE'))
slot=lib.capture_slot_evidence(f.cfg,f.q,f.c,0,root=f.root);check('ordinary_old_scan_negative_noDONE_never_shared_slot',slot['prospective_shared_count']==1 and not slot['unknown_shared_cohorts'])
other='PRIVATE_OTHER_CPU2';claims=copy.deepcopy(f.claims);claims[other]={'host_cpu':0};fx.put(f.root/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims=claims));slot=lib.capture_slot_evidence(f.cfg,f.q,f.c,0,root=f.root);check('other_ownclaim_selectedCPU_collision_rejected',bool(rejects(lambda:lib.verify_slot_evidence(slot,f.cfg,f.c,0))));fx.put(f.root/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims=f.claims))
unknown='PRIVATE_UNKNOWN_SHARED';f.q['consumed'][unknown]={'uuid':'PRIVATE_SHARED_GONE'};fx.put(f.root/'control/qualification_ledger'/(unknown+'.INTENT.json'),dict(cohort=unknown,uuid='PRIVATE_SHARED_GONE',output=str(f.root/'GONE'),**{lib.FIELD:{'schema':lib.ID}}));slot=lib.capture_slot_evidence(f.cfg,f.q,f.c,0,root=f.root);check('unknown_shared_consumption_withoutDONE_never_releases',unknown in slot['unknown_shared_cohorts']and bool(rejects(lambda:lib.verify_slot_evidence(slot,f.cfg,f.c,0))));del f.q['consumed'][unknown]
cfg=copy.deepcopy(f.cfg);cfg['allowed_cohorts'].append('UNAPPROVED_BROAD');q=copy.deepcopy(f.q);q['admitted_specs']['UNAPPROVED_BROAD']='PRIVATE';check('initial_exact1_cannot_silently_broaden',bool(rejects(lambda:lib._scope(cfg,q))))
fp=f.inputs(kind='OWNER_FRAME');frameproof=lib.project_for_candidate(**fp)[lib.PROOF];check('owner_frame_cannot_stand_in_for_native',bool(rejects(lambda:lib.verify_proof(frameproof,True))))
raw=f.base();check('project_does_not_mask_global_CPUpressure',lib.project(raw)['admission_decision']['pressure_reasons']==raw['admission_decision']['pressure_reasons'])
# Real library installer and exclusive binder; this is a unit API exercise,
# not an actual native loop/Popen. B jointprefix will supply that separately.
native=types.SimpleNamespace(R=f.root,__file__=str(lib.R/'tools/l2_native.py'),registered=lambda:(None,None,f.q,None),assert_parent_lease=lambda:{'pid':os.getpid(),'fixture':True},spec_for=lambda c:dict(f.spec,host_cpu=0),resources=lambda spec,fresh_source=False:f.base())
def write(path,obj):fx.put(path,obj);return obj
native.engine=lambda:types.SimpleNamespace(exclusive=write)
lib.sample_cpu_evidence=f.cpu;lib.capture_legal_cpu_evidence=f.legal;oldresources=native.resources;lib.install_future_native(native,f.cfg,False,invocation_cohort=f.c)
sentinel=native.resources(f.spec,False);check('freshFalse_exact_original_no_CPU_projection',lib.PROOF not in sentinel and sentinel['admission_decision']['pressure_reasons']==['cpu_pressure_full'])
out=f.root/'DTC/run/results/UNIT_BINDER';out.mkdir(parents=True);n=native.engine();ip=f.root/'control/qualification_ledger'/(f.c+'.INTENT.json');n.exclusive(ip,dict(cohort=f.c,uuid='CPU_UNIT_BINDER_ONLY',output=str(out)));n.exclusive(out/'NATIVE_LAUNCH.json',dict(cohort=f.c));n.exclusive(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',dict(cohort=f.c));docs=[read(p)for p in[ip,out/'NATIVE_LAUNCH.json',out/'NATIVE_SIMULATOR_PID_AND_MAPS.json']];snap=read(out/lib.SNAP)
check('new_snapshot_three_binding_and_fullforecast_native_verify',all(x[lib.FIELD]==docs[0][lib.FIELD]for x in docs)and all(lib.verify_proof(p,True)['status']=='PASS_CPU_SHARED_TIMESLICE_RESOURCE_NOT_CPU2_SPARE'for p in snap['fresh_preflights'])and snap['fresh_preflights'][-1]['native_full_forecast']['canonical_estimated_peak_model_RAM_bytes']==f.spec['estimated_peak_model_RAM_bytes'])
p=copy.deepcopy(snap['fresh_preflights'][-1]);p['native_full_forecast']['canonical_estimated_peak_model_RAM_bytes']-=1;check('forecast_estimated_field_must_match_canonical',bool(rejects(lambda:lib.verify_proof(p,True))))
output=dict(schema='CPU_SHARED_TIMESLICE_RESOURCE_CPU_QUALIFICATION_V1',status='PASS',qualification_only=True,checks=checks,count=len(checks),source_sha256=sha(lib.__file__),driver_sha256=sha(__file__),fixture_sha256=sha(D/'cpu_fixture.py'),actual_readonly_CPU_double_sample=actual_verdict,fixture_root=str(f.root),source_roles='Private explicit role standins; not final B/E joint source qualification',native_binding_exercised=True,actual_native_loop_or_Popen_exercised=False,actual_model_starts=0,new_grants=0,production_mutations=0,global_CPU2_ACTIVE_unchanged=True)
fx.put(D/'CPU_RESOURCE_QUALIFICATION.json',output);print(json.dumps(dict(path=str(D/'CPU_RESOURCE_QUALIFICATION.json'),sha256=sha(D/'CPU_RESOURCE_QUALIFICATION.json'),source_sha256=sha(lib.__file__),checks=len(checks))))
