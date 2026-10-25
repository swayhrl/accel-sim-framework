import pathlib,json,hashlib,ast,importlib.util,datetime,subprocess,os,time,signal
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,r):
 with P(p).open('x') as f:json.dump(r,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def fn(s,name):return ast.dump(next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
def stat(pid):
 try:
  s=(P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split();return {'pid':pid,'state':s[0],'ppid':int(s[1]),'sid':int(s[3]),'start_ticks':int(s[19])}
 except FileNotFoundError:return None
oldcfg=read(T/'control/FINAL_CONSUMER_WAITER_CONFIG_V4.json');w=load('R10_waiter5_qualification','final_consumer_waiter_v5.py');w.verify_pins(oldcfg['source_pins']);checks=['all62_previous_pinned_sources_unchanged'];old=(T/'tools/final_consumer_waiter_v4.py').read_text();new=(T/'tools/final_consumer_waiter_v5.py').read_text()
assert all(fn(old,k)==fn(new,k) for k in ['eligibility','final_disk_floor','generation_present','verify_pins']);checks.append('full_R6_72_288_17_68_body_controller_and_fresh_disk_eligibility_AST_unchanged')
old=(T/'tools/sweep_final_consumer_v7.py').read_text();new=(T/'tools/sweep_final_consumer_v8.py').read_text();expected=old.replace('CONSUMER_V7','CONSUMER_V8').replace('sweep_failure_review_host_v1.py','sweep_failure_review_telemetry_v1.py').replace('sweep_close_delivery_v7.py','sweep_close_delivery_v8.py');assert ast.dump(ast.parse(expected),include_attributes=False)==ast.dump(ast.parse(new),include_attributes=False);checks.append('consumer_changes_only_versioned_negative_route_domain_gate_and_schema')
for part in ['delivery','authority']:
 old=(T/'tools'/('sweep_close_'+part+'_v7.py')).read_text();new=(T/'tools'/('sweep_close_'+part+'_v8.py')).read_text();assert ast.dump(ast.parse(old.replace('CONSUMER_V7','CONSUMER_V8')),include_attributes=False)==ast.dump(ast.parse(new),include_attributes=False)
checks.append('delivery_and_authority_only_consumer_schema_changes')
n=load('R10_final_qualification_native','sweep_native_cap1m.py');q=n.read_current_authority()[0]['registered_future_requests'][n.REQUEST];v=load('R10_final_scheduler_replay','host_scheduler_r10_provenance_v1.py');proof=v.verify(q);checks.append('actual_current_nested_R8_R9_and_R10_parent_source_publication_joins')
r10=read(T/'control/CONTROLLER_LAUNCH_R10.json');r6=read(T/'control/CONTROLLER_LAUNCH_R6.json');cell=next(c for c in q['consumed'] if c not in read(T/'control/REQUEST_BEFORE_CONTINUATION_R10.json')['consumed']);i=read(T/'control/qualification_ledger'/(cell+'.INTENT.json'));bad=dict(i,batch_lease_pid=r10['pid']+10000)
try:v.check_parent(cell,bad,r10,r6)
except AssertionError:pass
else:raise AssertionError('wrong parent accepted')
checks.append('wrong_actual_parent_rejected')
f=load('R10_final_negative_replay','sweep_failure_review_telemetry_v1.py');negative=f.classify('E2-AEV100-2b93f70cd0666c51-DH');assert negative==read(T/'analysis/E2-AEV100-2b93f70cd0666c51-DH.RESULT.json')['failure_classification'] and negative['accepted_cycles'] is None;checks.append('new_negative_full_replay_matches_archived_controller_result_without_cycles')
assert w.eligibility(q,None,None,read(T/'analysis/BODY_QUALIFICATION_PROGRESS.json'),{},[r10],False)=='WAIT_NATIVE_MATRIX';checks.append('actual_incomplete_matrix_cannot_trigger_final_consumer')
pins=list(oldcfg['source_pins']);seen={r['path'] for r in pins};files=['revision10/sweep_controller.py','sweep_failure_review_telemetry_v1.py','host_scheduler_r10_provenance_v1.py','sweep_final_consumer_v8.py','sweep_prepare_final_pack_v9.py','sweep_close_delivery_v8.py','sweep_close_authority_v8.py']
for file in files:
 p=T/'tools'/file;assert str(p) not in seen;pins.append({'path':str(p),'sha256':sha(p)})
w.verify_pins(pins);p=T/'tools/final_consumer_waiter_v5.py';qp=T/'control/FINAL_CONSUMER_WAITER_QUALIFICATION_V5.json';qual={'status':'PASS','waiter_sha256':sha(p),'source_pins':pins,'check_count':len(checks),'checks':checks,'previous_qualification_sha256':sha(T/'control/FINAL_CONSUMER_WAITER_QUALIFICATION_V4.json'),'scheduler_proof_at_qualification_not_reused_as_final':proof,'models_started':0,'consumer_starts':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};put(qp,qual);cfg=dict(oldcfg,waiter_sha256=sha(p),source_pins=pins,qualification_sha256=sha(qp),consumer_path=str(T/'tools/sweep_final_consumer_v8.py'));cp=T/'control/FINAL_CONSUMER_WAITER_CONFIG_V5.json';put(cp,cfg)
assert not any((T/relative).exists() for relative in ['control/FINAL_CONSUMER_START_V1.json','control/FINAL_CONSUMER_LAUNCH_V1.json','analysis/COMPLETE_RESULT.json']);prior=read(T/'control/FINAL_CONSUMER_WAITER_LAUNCH_V4.json');st=stat(prior['pid']);assert st and st['start_ticks']==prior['start_ticks'] and st['state'] not in ['Z','X'] and sha(prior['source'])==prior['source_sha256'];os.kill(prior['pid'],signal.SIGTERM);deadline=time.monotonic()+3
while time.monotonic()<deadline:
 st=stat(prior['pid'])
 if st is None or st['start_ticks']!=prior['start_ticks'] or st['state'] in ['Z','X']:break
 time.sleep(.05)
assert st is None or st['start_ticks']!=prior['start_ticks'] or st['state'] in ['Z','X'];put(T/'control/FINAL_CONSUMER_WAITER_V4_RETIRED_FOR_R10_NEGATIVE_CLASSIFIER.json',{'prior':prior,'metadata_only_SIGTERM':True,'models_or_consumer_signaled':0,'reason':'Versioned consumer for independently classified telemetry guard STOP;all strict and full closure gates unchanged'})
log=T/'logs/FINAL_CONSUMER_WAITER_V5.log'
with log.open('xb') as f:
 child=subprocess.Popen(['/usr/bin/taskset','-c','9','/usr/bin/nice','-n','10','/usr/bin/python3','-B','-u',str(p)],stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,cwd=T,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'));time.sleep(.4);assert child.poll() is None,log.read_text();launch=dict(stat(child.pid),source=str(p),source_sha256=sha(p),qualification_sha256=sha(qp),config_sha256=sha(cp),consumer_path=cfg['consumer_path'],source_pin_count=len(pins),log=str(log),models_started=0,observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());put(T/'control/FINAL_CONSUMER_WAITER_LAUNCH_V5.json',launch)
print(json.dumps({'qualification':'PASS','checks':len(checks),'waiter':launch,'actual_consumed_at_qualification':len(q['consumed']),'consumer_started':False}))
