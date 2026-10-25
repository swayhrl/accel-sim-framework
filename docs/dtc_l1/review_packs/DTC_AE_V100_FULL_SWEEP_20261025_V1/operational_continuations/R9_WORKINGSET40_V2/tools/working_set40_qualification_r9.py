import pathlib,json,hashlib,importlib.util,os,copy,types,tempfile,datetime,ast
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,r):
 with P(p).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
a=load('R9_resource_zero_model_tests','sweep_host_execution_v2.py');m=load('R9_queue_zero_model_tests','revision9/sweep_controller.py');checks=[]
assert a.envelope(16*G,0,0)==4*G and a.envelope(16*G,3*G,0)==7*G and a.envelope(16*G,0,2*G)==16*G and a.envelope(16*G,0,0,True)==16*G;checks.append('working_set_floor_growth_body_scale_and_legacy_hard_reservation')
assert a.envelope(16*G,20*G,0)==16*G;checks.append('planning_estimate_never_changes_or_exceeds16GiB_hard_cap')
yes,hard,eff=a.ram_decision(300*G,str(256*G),64*G,64*G,160*G,640*G,True,False);assert yes and not hard;checks.append('40_small_working_sets_can_fit_without_claiming640GiB_physical_commit')
assert not a.ram_decision(300*G,str(256*G),64*G,64*G,160*G,640*G,True,True)[0];checks.append('live_V1_full_hard_guard_never_bypassed_for40')
assert a.ram_decision(100*G,str(256*G),180*G,0,200*G,300*G,False,False)[0] and not a.ram_decision(100*G,str(256*G),180*G,0,200*G,300*G,True,False)[0];checks.append('runtime_actual_safety_separated_from_future_admission_estimates')
assert not a.ram_decision(50*G,str(256*G),20*G,0,0,0,False,False)[0] and not a.ram_decision(300*G,str(256*G),220*G,0,0,0,False,False)[0];checks.append('host64GiB_and_cgroup48GiB_actual_safety_floors_retained')
assert not a.ram_decision(300*G,str(256*G),48*G,0,0,160*G,True,True)[0];checks.append('legacy_admission_extra8GiB_buffer_retained')
for reason,err in [('[Errno 11] Resource temporarily unavailable',None),("BlockingIOError(11, 'Resource temporarily unavailable')",None),('opaque',11)]:assert m.copy_wait(json.dumps({'status':'HOLD','reason':reason,'errno':err}))
for text in [json.dumps({'status':'HOLD','reason':'[Errno 13] Permission denied','errno':13}),json.dumps({'status':'HOLD','reason':'identity drift'}),'[]','badJSON']:assert not m.copy_wait(text)
checks.append('typed_and_both_legacy_EAGAIN_forms_retry_only_COPY_not_models')
qfixture={'admitted_specs':{'A':'x','B':'x'},'consumed':{},'sealed':[]};assert m.pending_cells(qfixture,{'future':{'cell':'A'}},{'A':{}},{},0)==['B'];checks.append('R8_preINTENT_inflight_and_claim_dedup_preserved')
with tempfile.TemporaryDirectory(prefix='DTC_R9_write_budget_metadata_') as tmp:
 root=P(tmp);(root/'logs').mkdir();old=m.T;m.T=root;reg={'registered_future_requests':{m.REQ:{'reserved_write_bytes':16*G}}};fake=types.SimpleNamespace(read_current_authority=lambda:(copy.deepcopy(reg),{}),resources=lambda s,f:{'native_free_bytes':42*G,'other_outstanding_write_reservations_bytes':0},update_authority=lambda fn:fn(reg))
 m.grow_write_budget(fake);assert reg['registered_future_requests'][m.REQ]['reserved_write_bytes']==36*G;m.T=old;checks.append('write_ceiling_stays_within5GiB_capacity_and_event_timestamp_does_not_crash')
cell='E2-AEV100-1df9d5479504d9c7-CM';n=load('R9_actual_scope','sweep_native_cap1m.py');q=n.read_current_authority()[0]['registered_future_requests'][n.REQUEST];assert len(q['consumed'])==141 and q['budget']==356
ip=T/'control/qualification_ledger'/(cell+'.INTENT.json');i=read(ip);out=P(i['output']);done=read(out/'NATIVE_EXIT.json');assert done==q['consumed'][cell]['execution_receipt'] and done['launcher_wait_returncode']==0 and done['stop_reason'] is None
strict=load('R9_copy_wait_actual_strict','sweep_strict_cap1m.py');stored=read(out/'AEFAIR_STRICT.json');assert strict.terminal(cell)==stored;sc=read(T/'DTC/control'/('SCIENCE_QUALIFICATION_'+cell+'.json'));assert sc['strict_sha256']==sha(out/'AEFAIR_STRICT.json') and sc['uuid']==done['uuid'];checks.append('actual_BFS_CM_full_natural_strict_complete_only_copy_waits')
stable={'cohort':cell,'uuid':done['uuid'],'strict_sha256':sha(out/'AEFAIR_STRICT.json'),'qualification_sha256':sha(T/'DTC/control'/('SCIENCE_QUALIFICATION_'+cell+'.json')),'native_done_sha256':sha(out/'NATIVE_EXIT.json'),'known_error':'Archive EAGAIN only;no scientific retry permitted','source_files_stable':True,'scientific_performance_acceptance_still_requires_archive':True};put(T/'control/R9_CLOSED_COPY_WAIT_STABILITY_REVIEW.json',stable)
for row in read(T/'control/HOST_EXECUTION_PLAN_V1.json')['source_pins']+q['shared_tool_pins']:assert sha(row['path'])==row['sha256']
checks.append('all_active_V1_and_original_scientific_source_pins_unchanged')
cpus=[];cores=set();allowed=os.sched_getaffinity(0)
for cpu in range(64,256):
 if cpu not in allowed:continue
 p=P('/sys/devices/system/cpu')/('cpu'+str(cpu))/'topology';key=((p/'physical_package_id').read_text(),(p/'core_id').read_text())
 if key not in cores:cores.add(key);cpus.append(cpu)
 if len(cpus)==80:break
assert len(cpus)>=40 and set(range(32,64))<=allowed;checks.append('at_least40_distinct_model_cores_and_separate32_core_frontend_pool')
pins=read(T/'control/HOST_EXECUTION_PLAN_V1.json')['source_pins'][:]
for file in ['sweep_host_execution_v2.py','sweep_frontend_host_v2.py','revision9/sweep_controller.py']:
 p=T/'tools'/file;ast.parse(p.read_text());pins.append({'path':str(p),'sha256':sha(p)})
pins=list({r['path']:r for r in pins}.values())
plan={'schema':'DTC_HOST_WORKINGSET40_PLAN_V2','profile_id':a.ID,'adapter_sha256':sha(T/'tools/sweep_host_execution_v2.py'),'preserved_prefix_cells':sorted(q['consumed']),'preserved_prefix_count':141,'maximum_jobs':40,'model_CPUs':cpus,'control_CPUs':list(range(32,64)),'allowed_CPUs':sorted(set(cpus)|set(range(4,9))),'source_pins':pins,'prior_entry_sha256':sha(P('/root/data/ep_l2_dtc_l1_native_v2/bin/native')),'per_job_hard_cap_unchanged_bytes':16*G,'minimum_working_set_reservation_bytes':4*G,'reservation_is_estimate_not_hard_peak_guarantee':True,'reserve_formula':'min(hard,max(4GiB,ceilGiB(8*largest_trace_member+1GiB),ceilGiB(2*actual_model_RSS+1GiB)))','legacy_compatibility':'Until every141-prefix model naturally closes, also enforce its exact V1 full16GiB-future-cap predicate;new admissions retain8GiB extra compatibility headroom. No active guard code changes.','runtime_safety':'Actual host64GiB and cgroup48GiB effective headroom;future estimates gate admission,not completed/native scientific acceptance. Native hard16GiB RSS/AS,all other BA controls unchanged.','ramp':'At most4 fresh admissions in any60seconds,maximum40. Actual count remains resource-gated.','disk':'Original per-job result caps unchanged;pool ceiling may grow only within fresh5GiB+registered-peer capacity,up to56GiB.','user_authorized_maximum40':True,'model_retries':0,'Core_cache_config_input_changes':False}
put(T/'control/HOST_EXECUTION_PLAN_V2.json',plan);proof={'status':'PASS','controller_sha256':sha(T/'tools/revision9/sweep_controller.py'),'plan_sha256':sha(T/'control/HOST_EXECUTION_PLAN_V2.json'),'checks':checks,'check_count':len(checks),'preserved_spent_count':141,'closed_copy_wait_review_sha256':sha(T/'control/R9_CLOSED_COPY_WAIT_STABILITY_REVIEW.json'),'source_pins':pins,'model_starts':0,'model_signals':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};put(T/'control/CONTINUATION_R9_ZERO_MODEL_QUALIFICATION.json',proof)
print(json.dumps({'status':'PASS','checks':len(checks),'maximum_jobs':40,'actual_hard_cap_GiB':16,'working_set_floor_GiB':4,'preserved_prefix':141,'model_starts':0}))
