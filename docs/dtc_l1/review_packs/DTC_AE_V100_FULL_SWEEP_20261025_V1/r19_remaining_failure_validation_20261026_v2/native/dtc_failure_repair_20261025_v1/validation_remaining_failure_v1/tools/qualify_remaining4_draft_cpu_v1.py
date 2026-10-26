import pathlib,json,hashlib,importlib.util,copy,tempfile,types,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');R=F/'validation_remaining_failure_v1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load():
 s=importlib.util.spec_from_file_location('remaining4_draft_cpu',R/'tools/remaining_native_v1.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,d):P(p).parent.mkdir(parents=True,exist_ok=True);P(p).write_text(json.dumps(d))
checks=[]
def ok(n,c):assert c,n;checks.append(n)
def rejected(n,fn):
 try:fn()
 except AssertionError:ok(n,True)
 else:raise AssertionError(n+' accepted')
profile=read(R/'control/REMAINING_BUILD_PROFILE_DRAFT_V1.json');engine=load();source_sha=sha(R/'tools/remaining_native_v1.py');realreuse=engine.check_reclaimed_cpu_pool(profile);ok('real_closed_R1_23_done_archive_pidproofs_allow_disjoint192_207_without_clearing4claims',realreuse['status']=='CLOSED_R1_CPU_POOL_REUSE_VERIFIED_NO_HISTORY_OR_CLAIM_CHANGE')
authority=engine.authority();oldrow=copy.deepcopy(authority[0]['registered_future_requests'][engine.PRIOR_REPAIR]);orig_claims=(engine.R1/'control/POOL_DISPATCH_RESERVATIONS.json').read_bytes()
with tempfile.TemporaryDirectory(prefix='REMAIN4_DRAFT_CPU_',dir=R/'analysis') as td:
 d=P(td);engine.R=d/'new';put(engine.R/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}});specs={}
 for path in (R/'control/spec_candidates').glob('*.json'):
  s=read(path);specs[s['cohort']]=s;put(engine.R/'control/specs'/path.name,s)
 q={'admitted_specs':{c:sha(engine.R/'control/specs'/(c+'.json')) for c in specs},'consumed':{}}
 engine.registered=lambda:({}, {},q,profile)
 for c,s in specs.items():
  got=engine.spec_for(c);expected=(128,96) if s['program']=='lavamd' else (16,4);ok(c+'_mixed_hard_estimate_unchanged',got['limits']['max_process_tree_rss_bytes']==expected[0]*1024**3 and got['estimated_peak_model_RAM_bytes']==expected[1]*1024**3)
 histo=next(c for c,s in specs.items() if s['program']=='histo');sp=engine.R/'control/specs'/(histo+'.json');before=read(sp);bad=copy.deepcopy(before);bad['limits']['max_process_tree_rss_bytes']=128*1024**3;put(sp,bad);q['admitted_specs'][histo]=sha(sp);rejected('wrong_histo_hard128_rejected_by_per_cohort_memory',lambda:engine.spec_for(histo));put(sp,before);q['admitted_specs'][histo]=sha(sp)
 bad=copy.deepcopy(before);bad['estimated_peak_model_RAM_bytes']=96*1024**3;put(sp,bad);q['admitted_specs'][histo]=sha(sp);rejected('wrong_histo_estimate96_rejected_by_per_cohort_memory',lambda:engine.spec_for(histo));put(sp,before);q['admitted_specs'][histo]=sha(sp)
 # Shared resource delegation is exact and source-pinned; physics arithmetic is
 # independently owned by R19's common module qualification, not duplicated here.
 resource=d/'shared.py';resource.write_text("def resources(spec,fresh_source=False):return {'received_cohort':spec['cohort'],'fresh_source':fresh_source,'CPU_FIXTURE_NOT_REAL_RESOURCE_MEASUREMENT':True}\n");engine.plan=lambda:{'resource_accounting_overlay':{'path':str(resource),'sha256':sha(resource)}}
 got=engine.resources({'cohort':'CPU_CALL'},True);ok('shared_resource_overlay_receives_exact_fresh_and_spec',got['received_cohort']=='CPU_CALL' and got['fresh_source'] is True)
 original_plan=engine.plan;badpin={'resource_accounting_overlay':{'path':str(resource),'sha256':'0'*64}};engine.plan=lambda:badpin;rejected('changed_shared_resource_source_fails_closed',lambda:engine.resources({'cohort':'CPU_CALL'},True));engine.plan=original_plan
 closed=copy.deepcopy(authority[0]);closed['registered_future_requests'][engine.PRIOR_REPAIR]['state']='RUNNING';engine.authority=lambda:(closed,authority[1]);rejected('old_R1_not_closed_rejects_CPUreuse',lambda:engine.check_reclaimed_cpu_pool(profile));engine.authority=lambda:authority
 engine.R1=d/'oldR1';put(engine.R1/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{'UNCERTAIN':{'host_cpu':192}}});rejected('selected_CPU_claimed_rejects_reuse',lambda:engine.check_reclaimed_cpu_pool(profile));put(engine.R1/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
 current_pid=read(profile['closed_R1_cpu_reuse_evidence']['path'])['rows'][0]['model_pid'];present=d/'proc_present';present.mkdir();(present/str(current_pid)).mkdir();oldP=engine.P;engine.P=lambda path:P(present) if str(path)=='/proc' else P(path);rejected('present_or_reused_modelPID_rejects_CPUreuse',lambda:engine.check_reclaimed_cpu_pool(profile));engine.P=oldP
ok('old_R1_request_and_historical_claim_bytes_unchanged',load().authority()[0]['registered_future_requests'][load().PRIOR_REPAIR]==oldrow and (load().R1/'control/POOL_DISPATCH_RESERVATIONS.json').read_bytes()==orig_claims)
ok('draft_source_unchanged',sha(R/'tools/remaining_native_v1.py')==source_sha)
out=R/'control/DRAFT_MIXED_RESOURCES_AND_CPU_REUSE_CPU_QUALIFICATION_V1.json';receipt={'schema':'REMAIN4_DRAFT_MIXED_SPEC_RESOURCE_DELEGATION_AND_CPU_REUSE_QUALIFICATION_V1','status':'PASS_DRAFT_ONLY_NOT_NATIVE_PRE_POPEN_QUALIFICATION','check_count':len(checks),'checks':checks,'source_sha256':source_sha,'profile_draft_sha256':sha(R/'control/REMAINING_BUILD_PROFILE_DRAFT_V1.json'),'CPU_reuse_certificate_sha256':sha(R/'control/CLOSED_R1_CPU_REUSE_EVIDENCE_CANDIDATE_V1.json'),'model_or_native_calls':0,'old_request_or_claim_mutations':0,'actual_registration_entry_or_simulation_actions':0,'unqualified_until':['R19 parent and fallbackfrontend real source SHA','shared R19 resource module/policy final SHA and independent CPU','final source/spec/plan/approval/registry candidates','actual native4positive+missingalias prePopen privateRoot CPU'],'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with out.open('x') as f:json.dump(receipt,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'status':receipt['status'],'checks':len(checks),'path':str(out),'sha256':sha(out)},indent=2))
