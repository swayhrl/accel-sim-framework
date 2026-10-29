import datetime,hashlib,json,os,pathlib,time,uuid,zlib
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');sha=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:json.loads(P(p).read_bytes());now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
W={'E2-DTCL2MLP-af7320f9d9dc6629-DH-Q128-V1':('0fbafa03-550a-43bf-ad96-ee79c62428e5',2169571,993679587),'E2-DTCL2MLP-af7320f9d9dc6629-DH-Q64-V1':('19b832e6-fcfa-4499-8c72-61aaad69fa5e',2170151,993702325)}
def live(pid,start):
 try:
  x=P('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split();return dict(matches=int(x[19])==start and x[0]not in ['Z','X','x'],state=x[0],CPU_ticks=int(x[11])+int(x[12]))
 except(FileNotFoundError,ProcessLookupError):return dict(matches=False)
def tail(path):
 with P(path).open('rb')as f:f.seek(max(0,os.fstat(f.fileno()).st_size-131072));b=f.read(131072)
 i=len(b)
 while True:
  i=b.rfind(b'\x1f\x8b\x08',0,i)
  if i<0:return None
  try:
   z=zlib.decompressobj(16+zlib.MAX_WBITS);raw=z.decompress(b[i:],1048576)
   if z.eof:
    v=json.loads(raw);assert isinstance(v,dict)and'protected_bytes'in v
    return dict(source_record_sha256=sha(raw),record=v)
  except(zlib.error,ValueError,AssertionError):pass
q=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']['DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1']
for c,(u,pid,start)in W.items():assert q['consumed'][c]['uuid']==u and live(pid,start)['matches'] and not(R/'analysis'/(c+'.RESULT.json')).exists()
O=A/'coordinator/cutcp_Q_pair_acceptance_window_observation_v1'/('watch_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:6]);O.mkdir(parents=True);initial=set(read(R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']);seen=set(initial);events={c:dict(DONE_first_seen=None,RESULT_first_seen=None,active_barrier_seen=False,strict_credit_seen=False)for c in W};key0=None;last_emit=0;end=time.monotonic()+900;records=0;last_result_mono=None
with(O/'OBSERVATIONS.jsonl').open('x',encoding='utf-8')as log:
 while True:
  stamp=now();j=tail(A/'coordinator/large_job_aging_v1/decisions.jsonl.gz');jr=j['record']if j else{};rows=[];errors=[]
  for c,(u,pid,start)in W.items():
   row=dict(cohort=c,uuid=u,pid=pid,start_ticks=start,process=live(pid,start),DONE=None,RESULT=None)
   for path,label in [(R/'control/qualification_ledger'/(c+'.DONE.json'),'DONE'),(R/'analysis'/(c+'.RESULT.json'),'RESULT')]:
    if not path.exists():continue
    try:
     raw=path.read_bytes();v=json.loads(raw);assert v['cohort']==c and v['uuid']==u
     row[label]=dict(path=str(path),sha256=sha(raw),natural=v.get('stop_reason')is None and v.get('launcher_wait_returncode')==0,returncode=v.get('launcher_wait_returncode'),stop_reason=v.get('stop_reason'))if label=='DONE'else dict(path=str(path),sha256=sha(raw),state=v['state'],cycles=v.get('cycles'),performance_accepted=v.get('proof',{}).get('performance_accepted'))
     if events[c][label+'_first_seen']is None:
      events[c][label+'_first_seen']=stamp
      if label=='RESULT':last_result_mono=time.monotonic()
    except(OSError,ValueError,AssertionError)as ex:errors.append(dict(cohort=c,kind=label,error=repr(ex)))
   bar=jr.get('pending_natural_acceptance_barrier',{})
   if bar.get('active')and any(x.get('cohort')==c and x.get('uuid')==u for x in bar.get('pending',[])):events[c]['active_barrier_seen']=True
   if any(x.get('kind')=='STRICT_NATURAL_COMPLETION_CREDIT'and x.get('cohort')==c and x.get('uuid')==u for x in jr.get('new_credit_events',[])):events[c]['strict_credit_seen']=True
   rows.append(row)
  claims=set(read(R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']);new=sorted(claims-seen);seen|=claims;key=(tuple((x['cohort'],x['process']['matches'],(x['DONE']or{}).get('sha256'),(x['RESULT']or{}).get('sha256'))for x in rows),(j or{}).get('source_record_sha256'))
  if key!=key0 or new or errors:
   log.write(json.dumps(dict(observed_UTC=stamp,rows=rows,new_claims_first_seen=new,existing_journal_tail=j,read_errors=errors,source_timing='Observer times; journal cadence can omit a short active window; no isolated physical causal attribution'),sort_keys=True)+'\n');log.flush();records+=1;key0=key
  if time.monotonic()-last_emit>=45:
   print(json.dumps(dict(UTC=stamp,observer_directory=str(O),events=events,live_count=sum(x['process']['matches']for x in rows),models_started=0,signals=0)),flush=True);last_emit=time.monotonic()
  if all(x['RESULT_first_seen']is not None for x in events.values())and(all(x['strict_credit_seen']for x in events.values())or time.monotonic()-last_result_mono>=90):break
  if time.monotonic()>=end:break
  time.sleep(3)
s=dict(UTC=now(),observer_directory=str(O),events=events,identities=W,initial_claims=sorted(initial),all_claims_first_seen_during_observation=sorted(seen-initial),observations_sha256=sha((O/'OBSERVATIONS.jsonl').read_bytes()),records=records,window_expiry_is_not_model_terminal=True,missing_journal_window_is_not_zero_or_disproof=True,model_starts=0,signals=0,registry_changes=0)
with(O/'SUMMARY.json').open('x')as f:json.dump(s,f,indent=2);f.write('\n')
print(json.dumps(s),flush=True)
