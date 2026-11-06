"""EP-MAIN UMT1 finite metadata closure and rolling Git publisher; never science actors."""
import pathlib,json,hashlib,datetime,os,fcntl,time,subprocess,uuid,copy
P=pathlib.Path;C=P(__file__).resolve().parent;V=C.parent.parent
N=P('/root/data/ep_l2_dtc_l1_native_v2');REG=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';EPOCH=N/'control/CURRENT_SCIENCE_EPOCH.json'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def exact(r):
 assert sha(r['path'])==r['sha256'],'evidence drift';return read(r['path'])
def put(p,x):
 p=P(p);t=p.with_name('.'+p.name+'.'+str(uuid.uuid4()));b=(json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
 with t.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.replace(t,p);return ref(p)
def close_ready(m):
 with (N/'control/science_authority/REGISTRY_UPDATE.lock').open('a+b')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);reg=read(REG);epoch=read(EPOCH);assert sha(REG)==epoch['native_registry_sha256'];before=copy.deepcopy(reg);changed=[]
  for g,z in m['groups'].items():
   q=reg['registered_future_requests'][z['request_id']]
   if q.get('state')in ['CLOSED_COMPLETED','CLOSED_WITH_TECHNICAL_FAILURES']:continue
   rows=q['consumed']
   if len(rows)!=z['budget']or q['remaining']!=0 or any(r.get('state')not in ['CLOSED_ACCEPTED','CLOSED_UNACCEPTED']for r in rows.values()):continue
   for c,r in rows.items():
    ar=exact(r['archive_receipt_ref']);rs=ar['native_restores']
    assert ar['status']=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS'and ar['uuid']==r['uuid']and len(rs)==2 and len({x['target']for x in rs})==2
    assert all(x['status']=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS'and x['archive_sha256']==ar['archive_ref']['sha256']for x in rs)
    if r['state']=='CLOSED_ACCEPTED':
     a=exact(r['accepted_point_ref']);assert a['hardware_drained']is True and a['cohort']==c and a['uuid']==r['uuid']and a['spec_ref']['sha256']==q['admitted_specs'][c]
   q['state']='CLOSED_COMPLETED'if all(r['state']=='CLOSED_ACCEPTED'for r in rows.values())else'CLOSED_WITH_TECHNICAL_FAILURES'
   q['Main_scope_closure']=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_exact_starts_consumed=True,no_retry_or_refund=True,all_raw_archive_and_two_native_restores=True,metadata_only=True)
   changed.append(z['request_id'])
  if not changed:return
  assert all(reg['registered_future_requests'][k]==q for k,q in before['registered_future_requests'].items()if k not in changed)
  assert {k:x for k,x in reg.items()if k!='registered_future_requests'}=={k:x for k,x in before.items()if k!='registered_future_requests'}
  for p in [REG,EPOCH]:
   out=N/'control/science_authority/request_history'/(p.stem+'.'+sha(p)+'.json')
   if not out.exists():out.write_bytes(p.read_bytes())
  put(REG,reg);epoch['native_registry_sha256']=sha(REG);epoch['request_revision']=dict(request_id=changed,operation='EP_MAIN_UMT1_CLOSE_INDEPENDENT_FINITE_SCOPES_AFTER_ARCHIVE_TWO_RESTORES',utc=datetime.datetime.now(datetime.timezone.utc).isoformat());put(EPOCH,epoch)
def main():
 with (C/'SINGLE_MAIN_UMT1_METADATA_WATCH.lock').open('a+b')as l:
  fcntl.flock(l,fcntl.LOCK_EX|fcntl.LOCK_NB)
  assert not(C/'METADATA_WATCH_STARTED.json').exists(),'no duplicate metadata watcher'
  ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])
  put(C/'METADATA_WATCH_STARTED.json',dict(pid=os.getpid(),start_ticks=ticks,code_ref=ref(__file__),metadata_only=True,automatic_model_retry=False))
  m=read(C/'EXACT_EXECUTION_MANIFEST.json');expiry=time.monotonic()+14*86400;published=None;nexttry=0
  if (C/'REMOTE_PROGRESS_PUBLICATION_RECEIPT.json').exists():
   previous=read(C/'REMOTE_PROGRESS_PUBLICATION_RECEIPT.json');reg=read(REG)
   rows=[r for z in m['groups'].values()for r in reg['registered_future_requests'][z['request_id']]['consumed'].values()]
   actual={'accepted':sum(r.get('state')=='CLOSED_ACCEPTED'for r in rows),'technical_failure':sum(r.get('state')=='CLOSED_UNACCEPTED'for r in rows),'pending':4-sum(r.get('state')in ['CLOSED_ACCEPTED','CLOSED_UNACCEPTED']for r in rows)}
   if previous.get('counts')==actual and read(C/'PUBLICATION_EXPECTED_HEAD.json')['head']==previous['head']:
    summary=[(z['request_id'],q['state'],[(co,r['state'],r.get('accepted_point_ref'),r.get('archive_receipt_ref'))for co,r in sorted(q['consumed'].items())if r['state']in ['CLOSED_ACCEPTED','CLOSED_UNACCEPTED']])for z in m['groups'].values()for q in [reg['registered_future_requests'][z['request_id']]]]
    published=hashlib.sha256(json.dumps(summary,sort_keys=True).encode()).hexdigest()
    put(C/'METADATA_WATCH_STATE.json',dict(status='EXISTING_MAIN_PROGRESS_PUBLICATION_REUSED',signature=published,published_signature=published,publication_ref=ref(C/'REMOTE_PROGRESS_PUBLICATION_RECEIPT.json'),metadata_only=True,models_started_here=0))
  while time.monotonic()<expiry:
   try:
    close_ready(m)
    reg=read(REG);summary=[(z['request_id'],q['state'],[(c,r['state'],r.get('accepted_point_ref'),r.get('archive_receipt_ref'))for c,r in sorted(q['consumed'].items())if r['state']in ['CLOSED_ACCEPTED','CLOSED_UNACCEPTED']])for z in m['groups'].values()for q in [reg['registered_future_requests'][z['request_id']]]]
    signature=hashlib.sha256(json.dumps(summary,sort_keys=True).encode()).hexdigest()
    allclosed=all(reg['registered_future_requests'][z['request_id']]['state']in ['CLOSED_COMPLETED','CLOSED_WITH_TECHNICAL_FAILURES']for z in m['groups'].values())
    if allclosed and not(C/'FINAL_SCOPE_CLOSURE.json').exists():
     put(C/'FINAL_SCOPE_CLOSURE.json',dict(status='EXACT4_BOTH_INDEPENDENT_SCIENTIFIC_SCOPES_CLOSED',groups=summary,all_scope_budget_consumed=4,new_unauthorized_models=0,no_retry_or_refund=True,Source_KEEP=True))
    if signature!=published and time.monotonic()>=nexttry:
     path=C/('ROLLING_PUBLICATION_'+str(time.time_ns())+'.log')
     with path.open('xb')as log:
      p=subprocess.run(['/usr/bin/python3','-B',str(C/'main_publish_umt1_progress.py')],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,timeout=900)
     if p.returncode==0:published=signature
     else:nexttry=time.monotonic()+60
     put(C/'METADATA_WATCH_STATE.json',dict(status='FINAL_PUBLISHED'if allclosed and published==signature else'WATCHING_AND_ROLLING_PUBLISH',signature=signature,published_signature=published,last_publication_returncode=p.returncode,last_publication_log_ref=ref(path),metadata_only=True,models_started_here=0))
    if allclosed and published==signature:
     put(C/'METADATA_WATCH_FINISHED.json',dict(status='FINITE_ALL4_CLOSURE_AND_FINAL_PUBLICATION_COMPLETE',closed_ref=ref(C/'FINAL_SCOPE_CLOSURE.json'),publication_ref=ref(C/'REMOTE_PROGRESS_PUBLICATION_RECEIPT.json'),models_started_here=0));return
    if (C/'EXECUTOR_FINISHED.json').exists()and not allclosed:
     put(C/'METADATA_WATCH_ATTENTION.json',dict(status='NEEDS_MAIN_SCOPE_LOCAL_DIAGNOSIS_RETAIN_EVERYTHING',executor_finished_ref=ref(C/'EXECUTOR_FINISHED.json'),no_model_restart=True,metadata_watch_continues=True))
   except Exception as e:
    put(C/'METADATA_WATCH_ATTENTION.json',dict(status='NEEDS_MAIN_METADATA_DIAGNOSIS',error=repr(e),models_started_here=0,never_kills_foreign=True));nexttry=time.monotonic()+60
   time.sleep(20)
  put(C/'METADATA_WATCH_FINISHED.json',dict(status='FINITE_METADATA_WATCH_EXPIRY_NO_SIGNAL_OR_MODEL_RESTART',models_started_here=0))
if __name__=='__main__':main()
