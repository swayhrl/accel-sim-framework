import pathlib,json,hashlib,ast,importlib.util,datetime,subprocess,os,time,signal,copy
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,r):
 with P(p).open('x') as f:json.dump(r,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def fn(s,name):return ast.dump(next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
def stat(pid):
 try:
  s=(P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split();return {'pid':pid,'state':s[0],'ppid':int(s[1]),'sid':int(s[3]),'start_ticks':int(s[19])}
 except FileNotFoundError:return None
checks=[];oldcfg=read(T/'control/FINAL_CONSUMER_WAITER_CONFIG_V5.json');assert len(oldcfg['source_pins'])==69
w=load('R11_waiter6_qualification','final_consumer_waiter_v6.py');w.verify_pins(oldcfg['source_pins']);checks.append('all69_previous_pinned_sources_unchanged')
old=(T/'tools/final_consumer_waiter_v5.py').read_text();new=(T/'tools/final_consumer_waiter_v6.py').read_text()
assert all(fn(old,k)==fn(new,k) for k in ['eligibility','final_disk_floor','generation_present','verify_pins']);checks.append('full_R6_72_288_17_68_body_controller_and_fresh_disk_eligibility_AST_unchanged')
assert "FINAL_CONSUMER_WAITER_V1.lock" in new and 'FINAL_CONSUMER_START_V1.json' in new and 'FINAL_CONSUMER_LAUNCH_V1.json' in new;checks.append('same_global_one_shot_markers_and_private_lock')
old=(T/'tools/sweep_final_consumer_v8.py').read_text();new=(T/'tools/sweep_final_consumer_v9.py').read_text();expected=old.replace('CONSUMER_V8','CONSUMER_V9').replace('sweep_host_provenance_v2.py','sweep_host_provenance_v3.py').replace('sweep_close_delivery_v8.py','sweep_close_delivery_v9.py');assert ast.dump(ast.parse(expected),include_attributes=False)==ast.dump(ast.parse(new),include_attributes=False);checks.append('consumer_only_schema_and_versioned_host_and_domain_routes_changed')
for part in ['delivery','authority']:
 old=(T/'tools'/('sweep_close_'+part+'_v8.py')).read_text();new=(T/'tools'/('sweep_close_'+part+'_v9.py')).read_text();assert ast.dump(ast.parse(old.replace('CONSUMER_V8','CONSUMER_V9')),include_attributes=False)==ast.dump(ast.parse(new),include_attributes=False)
checks.append('delivery_authority_only_versioned_consumer_schema_change')
h=load('R11_independent_host_V3_replay','sweep_host_provenance_v3.py')
def sample(fresh=True,legacy=False,rss=1*G,headroom=200*G,hard_remaining=40*G):
 hard=16*G;e=hard if legacy else min(hard,max(4*G,rss));projected=max(0,e-rss);credit=32*G;maximum=256*G;free=headroom-credit;current=maximum-free;mem=400*G;old=mem>=64*G+hard_remaining and headroom>=48*G+hard_remaining;raw=mem>=64*G+hard_remaining and free>=48*G+hard_remaining;need=projected if fresh else 0;passed=mem>=64*G+need and headroom>=48*G+need
 if legacy:passed=passed and old
 return {'host_execution_accounting':h.ID,'working_set_reservation_is_not_a_hard_cap':True,'cgroup_memory_stat_for_credit':{'file':40*G,'inactive_file':40*G,'shmem':0,'file_mapped':0,'file_dirty':0,'file_writeback':0},'cgroup_reclaimable_clean_inactive_file_credit_bytes':credit,'RAM_reservation_entries':[{'cohort':'fixture','legacy_V1':legacy,'hard_cap_bytes':hard,'observed_model_RSS_bytes':rss,'working_set_envelope_bytes':e,'additional_reserved_bytes':projected}],'reserved_additional_live_and_candidate_RAM_bytes':projected,'legacy_host_V1_live_cells':['fixture'] if legacy else [],'cgroup_memory_max':str(maximum),'cgroup_memory_current':current,'cgroup_effective_headroom_bytes':headroom,'original_full_hard_cap_RAM_reservation_bytes':hard_remaining,'host_MemAvailable_bytes':mem,'legacy_full_hard_cap_predicate_pass':old,'original_raw_cgroup_RAM_pass':raw,'RAM_decision_scope':'ADMISSION_PROJECTED_WORKINGSET' if fresh else 'RUNTIME_ACTUAL_HEADROOM','physical_RAM_pass':passed}
for name,r in [('initial_4GiB_not_16GiB',sample()),('actual_RSS_5GiB_grows_without_4GiB_hard_kill',sample(rss=5*G)),('legacy_keeps_16GiB_full_hard_reservation',sample(legacy=True)),('legacy_exact_boundary_pass_without_extra8GiB',sample(legacy=True,headroom=88*G)),('runtime_actual_headroom_separate_from_future_reservation',sample(fresh=False,headroom=48*G)),('admission_future_projection_rejected_at_runtime_floor',sample(fresh=True,headroom=48*G))]:h.verify_sample(r);checks.append(name)
for name,key,value in [('wrong_cache_credit_rejected','cgroup_reclaimable_clean_inactive_file_credit_bytes',0),('wrong_verdict_rejected','physical_RAM_pass',False),('wrong_profile_rejected','host_execution_accounting','HOST_WORKINGSET40_V2')]:
 r=sample();r[key]=value
 try:h.verify_sample(r)
 except AssertionError:pass
 else:raise AssertionError(name)
 checks.append(name)
r=sample();r['RAM_reservation_entries'][0]['hard_cap_bytes']=4*G
try:h.verify_sample(r)
except AssertionError:pass
else:raise AssertionError('4GiB hard cap was accepted')
checks.append('shrunk_hard_cap_rejected')
n=load('R11_final_native_readonly','sweep_native_cap1m.py');q=n.read_current_authority()[0]['registered_future_requests'][n.REQUEST]
binding=h.bind(q);checks.append('actual_R11_profile_source_publication_transport_and_nested_V2_V1_prefix_bound')
v=load('R11_final_scheduler_replay','host_scheduler_r11_provenance_v1.py');proof=v.verify(q);checks.append('actual_current_nested_R8_R9_R10_R11_scheduler_parent_source_publication_joins')
r11=read(T/'control/CONTROLLER_LAUNCH_R11.json');r6=read(T/'control/CONTROLLER_LAUNCH_R6.json');dummy='E2-AEV100-fixture-CM'
try:v.check_parent(dummy,{'batch_lease_pid':r11['pid']+10000,'batch_lease_start_ticks':r11['start_ticks']},r11,r6)
except AssertionError:pass
else:raise AssertionError('wrong parent accepted')
checks.append('wrong_actual_parent_rejected')
assert w.eligibility(q,None,None,read(T/'analysis/BODY_QUALIFICATION_PROGRESS.json'),{},[r11],False)=='WAIT_NATIVE_MATRIX';checks.append('actual_incomplete_matrix_cannot_trigger_consumer')
assert not any((T/relative).exists() for relative in ['control/FINAL_CONSUMER_START_V1.json','control/FINAL_CONSUMER_LAUNCH_V1.json','analysis/COMPLETE_RESULT.json'])
for proc in P('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:cmd=(proc/'cmdline').read_bytes().split(b'\0')
 except (FileNotFoundError,PermissionError,ProcessLookupError):continue
 assert not any(x.startswith(os.fsencode(T/'tools/sweep_final_consumer')) and x.endswith(b'.py') for x in cmd),('active consumer found',proc.name)
checks.append('no_one_shot_start_launch_complete_or_active_consumer')
pins=list(oldcfg['source_pins']);seen={r['path'] for r in pins};files=['revision11/sweep_controller.py','sweep_host_execution_v3.py','sweep_frontend_host_v3.py','sweep_host_provenance_v3.py','host_scheduler_r11_provenance_v1.py','sweep_final_consumer_v9.py','sweep_prepare_final_pack_v10.py','sweep_close_delivery_v9.py','sweep_close_authority_v9.py']
for file in files:
 p=T/'tools'/file;assert str(p) not in seen;pins.append({'path':str(p),'sha256':sha(p)})
w.verify_pins(pins);p=T/'tools/final_consumer_waiter_v6.py';qp=T/'control/FINAL_CONSUMER_WAITER_QUALIFICATION_V6.json';qual={'status':'PASS','waiter_sha256':sha(p),'source_pins':pins,'check_count':len(checks),'checks':checks,'previous_qualification_sha256':sha(T/'control/FINAL_CONSUMER_WAITER_QUALIFICATION_V5.json'),'scheduler_proof_at_qualification_not_reused_as_final':proof,'models_started':0,'consumer_starts':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};put(qp,qual);cfg=dict(oldcfg,waiter_sha256=sha(p),source_pins=pins,qualification_sha256=sha(qp),consumer_path=str(T/'tools/sweep_final_consumer_v9.py'));cp=T/'control/FINAL_CONSUMER_WAITER_CONFIG_V6.json';put(cp,cfg)
prior=read(T/'control/FINAL_CONSUMER_WAITER_LAUNCH_V5.json');st=stat(prior['pid']);assert st and st['start_ticks']==prior['start_ticks'] and st['state'] not in ['Z','X'] and sha(prior['source'])==prior['source_sha256'];os.kill(prior['pid'],signal.SIGTERM);deadline=time.monotonic()+3
while time.monotonic()<deadline:
 st=stat(prior['pid'])
 if st is None or st['start_ticks']!=prior['start_ticks'] or st['state'] in ['Z','X']:break
 time.sleep(.05)
assert st is None or st['start_ticks']!=prior['start_ticks'] or st['state'] in ['Z','X'];put(T/'control/FINAL_CONSUMER_WAITER_V5_RETIRED_FOR_R11_HOST_PROFILE.json',{'prior':prior,'metadata_only_SIGTERM':True,'models_or_consumer_signaled':0,'reason':'Versioned consumer independently replays new4GiB admission host profile;all strict and full closure gates unchanged'})
log=T/'logs/FINAL_CONSUMER_WAITER_V6.log'
with log.open('xb') as f:
 child=subprocess.Popen(['/usr/bin/taskset','-c','9','/usr/bin/nice','-n','10','/usr/bin/python3','-B','-u',str(p)],stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,cwd=T,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'));time.sleep(.4);assert child.poll() is None,log.read_text();launch=dict(stat(child.pid),source=str(p),source_sha256=sha(p),qualification_sha256=sha(qp),config_sha256=sha(cp),consumer_path=cfg['consumer_path'],source_pin_count=len(pins),log=str(log),models_started=0,observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());put(T/'control/FINAL_CONSUMER_WAITER_LAUNCH_V6.json',launch)
manifest={'files':[{'path':str(T/'tools'/file),'sha256':sha(T/'tools'/file)} for file in files+['final_consumer_waiter_v6.py']],'qualification_path':str(qp),'qualification_sha256':sha(qp),'config_path':str(cp),'config_sha256':sha(cp),'launch':launch,'source_pin_count':len(pins),'models_started':0,'consumer_starts':0};put(T/'control/R11_FINAL_TOOLS_SOURCE_MANIFEST.json',manifest)
print(json.dumps({'qualification':'PASS','checks':len(checks),'waiter':launch,'actual_consumed_at_qualification':len(q['consumed']),'consumer_started':False,'manifest':manifest},indent=2))
