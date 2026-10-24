import pathlib,json,time,os,signal,shutil,traceback
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');W=C.parent/'parallel_post_3mm_AB_A001';i=json.loads((W/'IDENTITY.json').read_text());root=i['pid'];deadline=i['deadline_unix'];peaks={'aggregate_RSS_bytes':0,'all_descendant_processes':0,'local_spill_bytes':0,'aggregate_CPU_ticks':0};samples=0
def proc():
 out={}
 for d in pathlib.Path('/proc').iterdir():
  if not d.name.isdigit():continue
  try:
   t=(d/'stat').read_text().split(') ',1)[1].split();cmd=(d/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
   out[int(d.name)]={'pid':int(d.name),'ppid':int(t[1]),'pgrp':int(t[2]),'start_ticks':t[19],'RSS':int(t[21])*os.sysconf('SC_PAGE_SIZE'),'CPU_ticks':int(t[11])+int(t[12]),'cmd':cmd}
  except (FileNotFoundError,ProcessLookupError,PermissionError):pass
 return out
def save(p,o):p.write_text(json.dumps(o,indent=2)+'\n')
save(W/'RESOURCE_REVIEW_ADDENDUM.json',{'V1_identity_corrections':['RLIMIT_AS applies separately to Python and inherited sort descendants; original aggregate3GiB label excludes sort grandchildren and is not full process-group bound','V1 ThreadPoolExecutor outer except can wait before kill; internal asserts alone do not prove immediate interruption','disk4GiB is polled budget, not filesystem quota;10GiB physical free margin retained'],'independent_guard_pid':os.getpid(),'independent_guard_deadline':deadline,'max_concurrent_postprocess_Python':2,'resource_sample_scope':'root and recursive all descendants by PID/startticks, RSS+CPU; local compressed/sort scratch only, no NAS output','stop_rule':'On budget/free/deadline violation terminate exact own controller first to prevent queued future spawn, then exact own postprocess groups incl late orphan scan','source_KEEP':True})
last=[];failure=None
try:
 with (W/'RESOURCE_SAMPLES.jsonl').open('x')as log:
  while True:
   allp=proc();p=allp.get(root)
   if not p or p['start_ticks']!=i['start_ticks']:break
   ids={root}
   for _ in range(12):
    grown={pid for pid,x in allp.items()if x['ppid']in ids}
    if grown<=ids:break
    ids|=grown
   current=[allp[x]for x in ids if x in allp];last=current
   used=sum(p.stat().st_size for p in W.rglob('*')if p.is_file());free=shutil.disk_usage(W).free
   rss=sum(x['RSS']for x in current);cpu=sum(x['CPU_ticks']for x in current)
   peaks['aggregate_RSS_bytes']=max(peaks['aggregate_RSS_bytes'],rss);peaks['all_descendant_processes']=max(peaks['all_descendant_processes'],len(current));peaks['local_spill_bytes']=max(peaks['local_spill_bytes'],used);peaks['aggregate_CPU_ticks']=max(peaks['aggregate_CPU_ticks'],cpu)
   row={'unix':time.time(),'aggregate_RSS_bytes':rss,'local_spill_bytes':used,'physical_free_bytes':free,'aggregate_CPU_ticks':cpu,'processes':current};log.write(json.dumps(row)+'\n');log.flush();samples+=1
   if used>=4*2**30 or free<=10*2**30 or rss>=4*2**30 or time.time()>deadline:
    failure={'unix':time.time(),'reason':'polled disk/free/RSS/deadline budget','sample':row}
    os.killpg(root,signal.SIGTERM)
    for x in current:
     if x['pgrp']!=root:
      try:os.killpg(x['pgrp'],signal.SIGTERM)
      except ProcessLookupError:pass
    time.sleep(.2)
    for x in proc().values():
     if str(W) in x['cmd'] and ('postprocess_nas_sharded_v4.py' in x['cmd'] or x['cmd'].startswith('sort ')):
      try:os.killpg(x['pgrp'],signal.SIGTERM)
      except ProcessLookupError:pass
    break
   time.sleep(2)
 save(W/'RESOURCE_PEAKS_AND_TERMINATION.json',{'status':'RESOURCE_GUARD_STOPPED_OWN_AB'if failure else 'AB_CONTROLLER_ENDED_RESOURCE_MONITOR_COMPLETE','samples':samples,'peaks':peaks,'failure':failure,'source_KEEP':True,'no_NAS_writes':True,'zero_GPU_execution':True})
except BaseException as e:save(W/'RESOURCE_GUARD_FAILURE.json',{'error':repr(e),'traceback':traceback.format_exc()});raise
