#!/usr/bin/env python3
import pathlib,json,collections,time,os,hashlib
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
deadline=time.time()+24*3600
seed=C/'UNIFIED_SCOPE_SEED_V1.json'
if not seed.exists():seed.write_bytes((C/'UNIFIED_SCOPE_STATUS.json').read_bytes())
def save(p,o):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(o,indent=2)+'\n');os.replace(t,p)
save(C/'SCOPE_OVERLAY_IDENTITY.json',{'pid':os.getpid(),'start_ticks':pathlib.Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19],'deadline_unix':deadline,'stop_file':str(C/'STOP_SCOPE_OVERLAY'),'terminal_rule':'No PENDING/RUNNING dispatcher jobs and no PREPARED_NOT_DISPATCHED contents'})
while time.time()<deadline and not (C/'STOP_SCOPE_OVERLAY').exists():
 try:
  o=json.loads(seed.read_text());queue=json.loads((C/'QUEUE.json').read_text());states={q['id']:q for q in queue}
  jobs=json.loads((C/'ALL_PREPARED_CAPTURE_JOBS_V1.json').read_text());group=collections.defaultdict(list)
  for j in jobs:
   q=states.get(j['id']);group[j['content_id']].append(dict(j,dispatcher_status=q['status'] if q else 'PREPARED_NOT_DISPATCHED',dispatcher_evidence=q))
  rank={'COMMITTED_VERIFIED':0,'RUNNING':1,'PENDING':2,'PREPARED_NOT_DISPATCHED':3,'PENDING_SPECIALIST_EXTENSION':4,'FAILED_RETAINED':5}
  for row in o['contents']:
   found=group[row['content_id']]
   if not found:continue
   best=min(found,key=lambda j:rank.get(j['dispatcher_status'],9));s=best['dispatcher_status']
   row.update(status={'COMMITTED_VERIFIED':'SEALED','RUNNING':'ACTIVE','PENDING':'QUEUED','PENDING_SPECIALIST_EXTENSION':'SPECIAL'}.get(s,s),capture_job_id=best['id'],capture_attempts=[{'job_id':j['id'],'status':j['dispatcher_status'],'evidence':j['dispatcher_evidence']} for j in found])
  o['updated_unix']=time.time();o['status_counts']=dict(collections.Counter(r['status'] for r in o['contents']));o['dispatcher_state']=json.loads((C/'DISPATCHER_STATE.json').read_text());o['capture_state_overlay_required']=False
  o['native_attempt_status_counts']=dict(collections.Counter(r['scope_status'] for r in o['native_attempts']))
  save(C/'UNIFIED_SCOPE_STATUS.json',o)
  if not any(q['status'] in ['PENDING','RUNNING'] for q in queue) and not any(r['status']=='PREPARED_NOT_DISPATCHED' for r in o['contents']):break
 except Exception as e:save(C/'UNIFIED_SCOPE_OVERLAY_ERROR.json',{'error':repr(e),'unix':time.time()})
 time.sleep(10)
save(C/'SCOPE_OVERLAY_TERMINATION.json',{'ended':time.time(),'pid':os.getpid(),'reason':'deadline/explicit stop/all dispatcher jobs terminal'})
