import pathlib,json,hashlib,ast,importlib.util,datetime,subprocess,shutil,os
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');F=T/'docs-worktree';G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,r):
 with P(p).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def git(*a):return subprocess.check_output(['git','-C',str(F),*a],text=True).strip()
a=load('R11_fixed4_adapter_zero_model','sweep_host_execution_v3.py');c=load('R11_parent_zero_model','revision11/sweep_controller.py');checks=[];p=read(T/'control/HOST_EXECUTION_PLAN_V3.json');policy=read(T/'control/ALL_REMAINING_DISPATCH_POLICY_R11.json')
assert a.envelope(16*G,0,100*G)==4*G and a.envelope(16*G,3*G,100*G)==4*G and a.envelope(16*G,6*G,0)==6*G and a.envelope(16*G,20*G,0)==16*G;checks.append('4GiB_initial_reservation_ignores_body_size_and_grows_only_with_actual_RSS')
assert a.envelope(16*G,0,0,True)==16*G and p['per_job_hard_cap_unchanged_bytes']==16*G;checks.append('hard16GiB_retained_and_legacy_guard_compatibility_explicit')
assert a.ram_decision(300*G,str(256*G),64*G,32*G,160*G,640*G,True,False)[0];assert not a.ram_decision(300*G,str(256*G),64*G,32*G,160*G,640*G,True,True)[0];checks.append('40times4GiB_admitted_after_legacy_drain_not_while_old_guards_would_fail')
assert a.ram_decision(300*G,str(256*G),46*G,0,100*G,160*G,True,True)[0];checks.append('unnecessary_previous8GiB_fresh_margin_removed_with_exact_V1_predicate_preserved')
assert a.ram_decision(100*G,str(256*G),180*G,0,200*G,300*G,False,False)[0] and not a.ram_decision(100*G,str(256*G),180*G,0,200*G,300*G,True,False)[0];checks.append('runtime_actual_headroom_and_future_admission_separate')
assert not a.ram_decision(50*G,str(256*G),20*G,0,0,0,False,False)[0] and not a.ram_decision(300*G,str(256*G),220*G,0,0,0,False,False)[0];checks.append('actual_host64GiB_cgroup48GiB_safety_floors_retained')
fixture={'admitted_specs':{'A':1,'B':1},'consumed':{},'sealed':[]};assert c.pending_cells(fixture,{'f':{'cell':'A'}},{'A':{}},{},0)==['B'];fixture['consumed']['B']={};assert not c.pending_cells(fixture,{'f':{'cell':'A'}},{'A':{}},{},0);checks.append('no_pre_INTENT_duplicate_or_consumed_model_retry')
assert policy['maximum_jobs']==p['maximum_jobs']==40 and policy['initial_per_cell_RAM_reservation_bytes']==4*G and policy['host_plan_sha256']==sha(T/'control/HOST_EXECUTION_PLAN_V3.json');checks.append('exact_user40slot4GiB_policy_bound')
pins=read(T/'control/FINAL_CONSUMER_WAITER_CONFIG_V5.json')['source_pins']+p['source_pins']
for r in pins:assert sha(r['path'])==r['sha256']
checks.append('all69_previous_active_source_pins_and_new_plan_sources_unchanged')
before=read(T/'control/REQUEST_AT_R10_RETIREMENT_FOR_R11.json');n=load('R11_actual_authority_zero_model','sweep_native_cap1m.py');q=n.read_current_authority()[0]['registered_future_requests'][n.REQUEST];assert set(q['consumed'])==set(before['consumed'])==set(p['preserved_prefix_cells']) and q['budget']==356
for cell,row in before['consumed'].items():assert all(q['consumed'][cell][k]==v for k,v in row.items())
transport=read(T/'control/R10_PARENT_RETIREMENT_LIVE_MODELS_PRESERVED_R11.json');assert transport['signals_to_scientific_models']==transport['signals_to_original_frontends']==0 and all(r['preserved_or_naturally_closed'] for r in transport['active_generations_after']);checks.append('all172spent_identities_preserved_and_11live_models_not_signaled')
cores=set()
for cpu in p['model_CPUs']:
 top=P('/sys/devices/system/cpu')/('cpu'+str(cpu))/'topology';key=((top/'physical_package_id').read_text(),(top/'core_id').read_text());assert key not in cores;cores.add(key)
assert len(cores)>=40;checks.append('at_least40_available_distinct_model_cores')
assert p['prior_entry_sha256']==sha(P('/root/data/ep_l2_dtc_l1_native_v2/bin/native')) and p['RSS_evidence_sha256']==sha(T/'analysis/RSS_EVIDENCE_REVIEW_BEFORE_FIXED4_V3.json');checks.append('current_V2_entry_and_full_historical_RSS_review_bound_before_activation')
# Actual arithmetic fixture installs only in this short-lived query process.
a.plan=lambda native:(q,dict(p,plan_sha256=sha(T/'control/HOST_EXECUTION_PLAN_V3.json')));n=a.install(n);candidate=next(c for c in q['admitted_specs'] if c not in q['consumed'] and c not in q.get('sealed',[]));res=n.resources(n.spec_for(candidate),True);assert res['host_execution_accounting']==a.ID and res['RAM_decision_scope']=='ADMISSION_PROJECTED_WORKINGSET';assert all(e['working_set_envelope_bytes']==min(e['hard_cap_bytes'],max(4*G,e['observed_model_RSS_bytes'])) for e in res['RAM_reservation_entries'] if not e['legacy_V1']);checks.append('real_current_RSS_and_resource_sample_fixed4_arithmetic_without_model_fork')
qp=T/'control/CONTINUATION_R11_ZERO_MODEL_QUALIFICATION.json';put(qp,{'status':'PASS','controller_sha256':sha(T/'tools/revision11/sweep_controller.py'),'plan_sha256':sha(T/'control/HOST_EXECUTION_PLAN_V3.json'),'policy_sha256':sha(T/'control/ALL_REMAINING_DISPATCH_POLICY_R11.json'),'checks':checks,'check_count':len(checks),'preserved_spent_count':len(before['consumed']),'source_pins':p['source_pins'],'actual_current_admission_diagnostic':res,'models_started':0,'models_signaled':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
assert not git('status','--porcelain');parent=git('rev-parse','HEAD');assert parent=='871584501c7cb8628199ef1f8903210048c8e6a8';rel='docs/dtc_l1/review_packs/DTC_AE_V100_FULL_SWEEP_20261025_V1/operational_continuations/R11_FIXED4G40_V3';D=F/rel;D.mkdir(parents=True)
files=['tools/revision11/sweep_controller.py','tools/sweep_host_execution_v3.py','tools/sweep_frontend_host_v3.py','tools/qualification_r11_v1.py','control/HOST_EXECUTION_PLAN_V3.json','control/ALL_REMAINING_DISPATCH_POLICY_R11.json','control/CONTINUATION_R11_ZERO_MODEL_QUALIFICATION.json','control/R10_PARENT_RETIREMENT_LIVE_MODELS_PRESERVED_R11.json','analysis/RSS_EVIDENCE_REVIEW_BEFORE_FIXED4_V3.json']
for file in files:
 dest=D/file;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(T/file,dest)
(D/'README.md').write_text('''# Initial4GiB admission with40slot target

The user's explicit amendment replaces input-size/doubled-RSS estimates with
an initial4GiB per-cell planning envelope that grows only with observed RSS.
Admission reserves max(0,min(hard,max(4GiB,RSS))-RSS), plus actual cgroup/host
headroom; runtime checks actual headroom. The16GiB hard AS/RSS limit remains:
historical161closed points include an accepted sgemm peak15.246GiB, and a live
3MM point already exceeds4GiB. A4GiB hard-kill policy would discard valid work.
The original simulator/Core/cache/config/telemetry/strict/source ledger remain.

The target is40, with8fresh admissions per5seconds and distinct assigned cores.
Three still-live V1 frontend closures compiled the original full16GiB future
reservation formula. They expose no safe hot-reload/monitor-adoption hook.
Until they naturally close, the exact old predicate remains to prevent their
MEMORY_HEADROOM termination. The additional8GiB fresh compatibility margin is
removed. Once all original V1 cells close, the compatibility predicate lifts
automatically; remaining loaded V2 guards then check actual headroom, and new
V3 points use4GiB admission. This does not claim40models already ran. Only the
R10 metadata parent retired; all11models/frontends survived,172spent identities
remain unchanged, and no model is retried or refunded. Original four reviewed
Cutcp cells retain R6 handoff. New adapter/entry/controller identities are
explicitly versioned, qualified and published before new scientific starts.
''');entries=[{'path':p.relative_to(D).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(D.rglob('*')) if p.is_file()];(D/'PACKAGE_MANIFEST.json').write_text(json.dumps({'files':entries,'model_starts_by_qualification':0},indent=2)+'\n');subprocess.run(['git','-C',str(F),'add','--',rel],check=True);subprocess.run(['git','-C',str(F),'diff','--cached','--check'],check=True);subprocess.run(['git','-C',str(F),'commit','-m','Use historical RSS to admit forty-slot sweep with initial four GiB reservations'],check=True);commit=git('rev-parse','HEAD');branch=git('branch','--show-current');bundle=T/'control/continuation_r11_source.bundle';subprocess.run(['git','-C',str(F),'bundle','create',str(bundle),branch,'^'+parent],check=True);rec={'commit':commit,'parent':parent,'branch':branch,'package_path':rel,'package_tree':git('rev-parse',commit+':'+rel),'bundle':str(bundle),'controller_sha256':sha(T/'tools/revision11/sweep_controller.py'),'qualification_sha256':sha(qp)};put(T/'control/CONTINUATION_R11_SOURCE_COMMIT.json',rec);print(json.dumps({'checks':len(checks),'source_commit':rec,'models_started':0}))
