"""Run each precise new identity at most once; truthful closed-source archival."""
import pathlib,json,hashlib,importlib.util,subprocess,time,uuid,concurrent.futures,os,math
P=pathlib.Path;R=P('/root/data/dtc_hash_downstream18_20261027_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,f):
 s=importlib.util.spec_from_file_location(n,R/'tools'/f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,x,exclusive=False):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 if exclusive:
  with p.open('x')as h:json.dump(x,h,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
 else:tmp=p.with_name(p.name+'.DS18writing');tmp.write_text(json.dumps(x,indent=2)+'\n');tmp.replace(p)
def event(state,**kw):
 with(R/'logs/EVENTS.jsonl').open('a')as h:h.write(json.dumps(dict(state=state,monotonic=time.monotonic(),**kw))+'\n');h.flush()
def archive_closed(c):
 o=load('ds18_ops_archive','ds18_outbox.py');began=time.monotonic()
 while True:
  if(R/'control'/(c+'_ARCHIVE_RECEIPT.json')).exists():return o.verify(c)
  try:o.archive(c)
  except BlockingIOError:assert time.monotonic()-began<21600;time.sleep(10)
  except RuntimeError as x:
   if 'HOLD'not in str(x)or time.monotonic()-began>=21600:raise
   time.sleep(10)
def finish_evidence(c):
 e=load('ds18_finish_engine','ds18_native.py');q=e.registered()[2];i=read(R/'control/qualification_ledger'/(c+'.INTENT.json'));d=read(R/'control/qualification_ledger'/(c+'.DONE.json'));out=P(i['output']);assert d==q['consumed'][c]['execution_receipt']==read(out/'NATIVE_EXIT.json')and i['uuid']==d['uuid'];failed=bool(d['stop_reason']or d['launcher_wait_returncode'])
 if failed:proof=dict(status='DOWNSTREAM18_NATIVE_NEGATIVE_UNACCEPTED',stop_reason=d['stop_reason'],returncode=d['launcher_wait_returncode'],accepted_cycles=None,raw_sha256=d['raw_sha256']);assert sha(out/'raw.log.gz')==d['raw_sha256']
 else:
  proof=load('ds18_whole_input_strict','ds18_strict.py').terminal(c);p=out/'DOWNSTREAM_STRICT.json'
  if p.exists():assert read(p)==proof
  else:put(p,proof,True)
  qual=dict(status='DOWNSTREAM18_NATIVE_TRACE_PERFORMANCE_QUALIFIED',cohort=c,uuid=d['uuid'],strict_sha256=sha(p),performance_scope='NEW_DOWNSTREAM18_ONLY_NEVER_ORIGINAL',SOURCE_KEEP=True);p=R/'DTC/control'/('SCIENCE_QUALIFICATION_'+c+'.json')
  if p.exists():assert read(p)==qual
  else:put(p,qual,True)
 a=archive_closed(c);v=dict(state='FAIL_DOWNSTREAM18_ARCHIVED_NO_RETRY'if failed else'PASS_DOWNSTREAM18_STRICT_ARCHIVE_NATIVE_RESTORE',cohort=c,uuid=d['uuid'],cycles=None if failed else proof['cycles'],proof=proof,archive=a,new_contract_only=True,original_or_repair_results_replaced=False);p=R/'analysis'/(c+'.RESULT.json')
 if p.exists():assert read(p)==v
 else:put(p,v,True)
 return v
def run_cell(c):
 e=load('ds18_worker_lease','ds18_native.py');e.assert_parent_lease();ip=R/'control/qualification_ledger'/(c+'.INTENT.json');assert not ip.exists();token=uuid.uuid4().hex
 for stage in ['prepare','run-native']:
  cmd=subprocess.run([str(N/'bin/experiment'),stage,c,'--project','DTC_L1'],capture_output=True,text=True);put(R/'logs'/(c+'.'+stage+'.'+token+'.json'),dict(stdout=cmd.stdout,stderr=cmd.stderr,returncode=cmd.returncode),True)
  if cmd.returncode:
   try:v=json.loads(cmd.stderr)
   except ValueError:v={}
   if not ip.exists()and c not in e.registered()[2]['consumed']and v.get('status')=='HOLD'and v.get('reason')in['RESOURCE_HOLD_NO_START','RESOURCE_HOLD','RESOURCE_HOLD_AFTER_DTC_PAIR','DTC original memory/paired/native-device admission HOLD']:return dict(state='ADMISSION_DEFERRED_ZERO_START',cohort=c,model_starts=0)
   return dict(state='ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS',cohort=c,error=cmd.stderr,model_retries=0)
 return finish_evidence(c)
def safe(c):
 try:return run_cell(c)
 except BaseException as x:return dict(state='ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS',cohort=c,error=repr(x),model_retries=0)
def summary():
 scope=read(R/'control/SCOPE.json');table={};states={}
 for p in scope['points']:
  c=p['cohort'];rp=R/'analysis'/(c+'.RESULT.json');v=read(rp)if rp.exists()else{};states[c]=v.get('state','PENDING');table.setdefault(p['program'],{}).setdefault(p['profile'],{})[p['cell']]=dict(cohort=c,state=states[c],cycles=v.get('cycles'))
 comparisons={}
 for prog,profiles in table.items():
  ratios={k:row['CH']['cycles']/row['DH']['cycles']if all(row.get(m,{}).get('cycles')for m in ['CH','DH'])else None for k,row in profiles.items()};changes={}
  for k in ['PQ','PS']:
   changes[k]=dict(relative_DTC_improvement=ratios[k]/ratios['P0']if ratios.get(k)and ratios.get('P0')else None,CH_speedup=profiles['P0']['CH']['cycles']/profiles[k]['CH']['cycles']if profiles['P0']['CH'].get('cycles')and profiles[k]['CH'].get('cycles')else None,DH_speedup=profiles['P0']['DH']['cycles']/profiles[k]['DH']['cycles']if profiles['P0']['DH'].get('cycles')and profiles[k]['DH'].get('cycles')else None)
  comparisons[prog]=dict(CH_over_DH_by_profile=ratios,changes=changes)
 out=dict(schema='DTC_HASH18_AUTO_SUMMARY_V1',states=states,table=table,comparisons=comparisons,no_missing_imputation=True,original_performance_reused=False);put(R/'analysis/AUTO_SUMMARY.json',out);return out
def run_scheduler():
 e=load('ds18_scheduler_engine','ds18_native.py');q=e.registered()[2];assert not q['consumed'];claims={};running={};results={};cool={};pool=concurrent.futures.ThreadPoolExecutor(max_workers=18,thread_name_prefix='DS18');put(R/'control/SCHEDULER_STARTED.json',dict(parent_pid=os.getpid(),new_slots=18,PQ_first=True,model_retries=0),True)
 def save():put(R/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims=claims))
 try:
  while True:
   assert not(R/'control/ABORT').exists()
   for f,c in list(running.items()):
    if not f.done():continue
    v=f.result();running.pop(f);row=e.registered()[2]['consumed'].get(c)
    if row and'execution_receipt'not in row:
     # Never free a spent uncertain generation or resubmit it as a model.
     put(R/'analysis'/(c+'.ENGINEERING_GUARD.json'),v);results[c]=v;continue
    claims.pop(c,None);save()
    if v['state']=='ADMISSION_DEFERRED_ZERO_START':assert row is None;cool[c]=time.monotonic()+30;event(v['state'],cohort=c);continue
    results[c]=v;put(R/'analysis'/(c+'.RESULT.json'),v);event(v['state'],cohort=c)
   reg,ep,q,p=e.registered();pending=[c for c in p['dispatch_order']if c not in q['consumed']and c not in claims and c not in results and cool.get(c,0)<=time.monotonic()]
   for c in pending:
    if len(claims)>=18:break
    s=e.spec_for(c);sample=e.resources(s,True)
    if not(sample['physical_RAM_pass']and sample['physical_disk_pass']):continue
    claims[c]=dict(host_cpu=s['host_cpu'],result_cap_bytes=e.output_cap(s),RAM_cap_bytes=16*1024**3);save();running[pool.submit(safe,c)]=c;event('DISPATCH_NEW_IDENTITY',cohort=c,profile=s['downstream_profile'],cpu=s['host_cpu'])
   reg,ep,q,p=e.registered();put(R/'analysis/BATCH_STATE.json',dict(spent=len(q['consumed']),remaining=q['remaining'],running=list(running.values()),claims=claims,results={k:v['state']for k,v in results.items()},PQ_first=True));summary()
   if not running and len(results)==18 and all('execution_receipt'in v for v in q['consumed'].values())and not claims:
    status='ALL18_STRICT_ARCHIVED_PASS'if all(v['state']=='PASS_DOWNSTREAM18_STRICT_ARCHIVE_NATIVE_RESTORE'for v in results.values())else'FINITE18_CLOSED_WITH_UNACCEPTED_OR_ENGINEERING_POINTS';put(R/'analysis/FINAL_STATUS.json',dict(status=status,results=results,model_retries=0),True)
    def close(r):
     qq=r['registered_future_requests'][e.REQ];assert len(qq['consumed'])==18 and qq['remaining']==0;qq.update(state='CLOSED',final_status=status,reserved_write_bytes=1024**3)
    e.update_authority(close);return
   time.sleep(2)
 finally:pool.shutdown(wait=True)
