import pathlib,json,hashlib,os,datetime
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');D=R/'control/operational_amendments/future_memory_admission_v1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
cfg=read(D/'ACTIVE_MEMORY.json');c=read(D/'CANARY_SELECTION.json')['cohort'];q=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][cfg['request']];row=q['consumed'].get(c);ip=R/'control/qualification_ledger'/(c+'.INTENT.json');intent=read(ip)if ip.exists()else None;state=dict(CST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),cohort=c,scope_mode=cfg['scope_mode'],allowed_cohort_count=len(cfg['allowed_cohorts']),native_entry_sha256=sha(N/'bin/native'),owner_ACK=read(D/'ACK.json'),actually_spent=row is not None,INTENT_present=intent is not None,model_starts_by_observer=0,global_095_rollout=cfg['scope_mode']=='ALL_UNSPENT_FUTURE')
if row:
 state['uuid']=row['uuid'];out=R/'DTC/run/results'/row['uuid'];pidpath=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json';launchpath=out/'NATIVE_LAUNCH.json';pid=read(pidpath)if pidpath.exists()else None;launch=read(launchpath)if launchpath.exists()else None
 state['actual_new_memory_binding_present']=bool(intent and'additional_future_memory_admission_binding'in intent)
 if pid:
  try:
   f=(P('/proc')/str(pid['pid'])/'stat').read_text().rsplit(')',1)[1].split();assert int(f[19])==pid['start_ticks']and f[0]!='Z';state['live_model']=dict(pid=pid['pid'],start_ticks=pid['start_ticks'],state=f[0],CPU_ticks=int(f[11])+int(f[12]),RSS_GiB=int(f[21])*os.sysconf('SC_PAGE_SIZE')/1024**3)
  except(OSError,AssertionError):state['live_model']=None
 if state['actual_new_memory_binding_present']and pid and launch:
  b=intent['additional_future_memory_admission_binding'];assert launch['additional_future_memory_admission_binding']==pid['additional_future_memory_admission_binding']==b;sp=out/'FUTURE_MEMORY_ADMISSION_SNAPSHOT.json';assert sha(sp)==b['snapshot_sha256'];state['triple_binding_and_snapshot_SHA_verified']=True;state['snapshot_path']=str(sp)
 dp=R/'control/qualification_ledger'/(c+'.DONE.json');rp=R/'analysis'/(c+'.RESULT.json');state['DONE_present']=dp.exists();state['RESULT_present']=rp.exists()
 if dp.exists():state['DONE']=read(dp)
 if rp.exists():
  result=read(rp);state['RESULT_summary']={k:result.get(k)for k in ['state','uuid','cycles','archive']};state['RESULT_SHA256']=sha(rp);state['memory_extra_strict_present']='additional_future_memory_admission_strict'in result.get('proof',{})
  if state['memory_extra_strict_present']:
   link=result['proof']['additional_future_memory_admission_strict'];state['memory_extra_strict']=link;assert sha(link['sidecar_path'])==link['sidecar_sha256'];state['memory_sidecar_SHA_verified']=True
print(json.dumps(state,indent=2),flush=True)
