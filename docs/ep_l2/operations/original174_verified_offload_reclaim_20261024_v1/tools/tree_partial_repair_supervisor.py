"""Finite same-queue continuation after qualified tree-partial repair.

Runs only after the original Supervisor and Driver stopped at the verified
114/115 engineering boundary. Preserves the original deadline and cumulative
resource/restart counters. Never signals or starts scientific processes.
"""
import pathlib,sys,os,json,time,hashlib,fcntl,subprocess,traceback
P=pathlib.Path;T=P('/root/data/research_asset_verified_offload_20261024_v1');sys.path.insert(0,str(T/'tools'))
import server_resources as rr
import retire_174new_build_duplicates as audit
CONTROL=T/'control/CONTINUATION_SUPERVISOR.json';JOURNAL=T/'control/CONTINUATION_SUPERVISOR.jsonl';AID='TRACE_c80bfba3c26ce8b2'
N=audit.DEST.parent/'tree_partial_resume_v1';ENGINE_SHA='0eaa01dca208979695e583e12f7ac83cb1af074b066f25b8b7c066123c98f69a'

def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def read(p):return json.loads(P(p).read_bytes())
def need(v,m):
 if not v:raise RuntimeError(m)
def live(pid,ticks,script):
 p=P('/proc',str(pid))
 try:return int((p/'stat').read_text().rsplit(')',1)[1].split()[19])==ticks and str(T/'tools'/script).encode() in (p/'cmdline').read_bytes().split(b'\0')
 except OSError:return False
def durable(p,x):
 p=P(p);tmp=p.with_name(p.name+'.tree-repair-supervisor-writing')
 with tmp.open('xb') as f:f.write(canon(x));f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def record(event,**kw):
 row=dict(event=event,unix=time.time(),supervisor_pid=os.getpid(),**kw)
 with JOURNAL.open('ab') as f:f.write(canon(row));f.flush();os.fsync(f.fileno())
def completed():
 rows=[json.loads(z) for z in (T/'control/LEDGER.jsonl').read_text().splitlines()]
 return {z['asset_id']:z for z in rows if z['status']=='ARCHIVED_CONTENT_VERIFIED'}
def source_admission():
 code=P(rr.__file__).read_text()+'\nprint(json.dumps(admission("SOURCE",include_activity=False)))\n'
 ssh=['ssh','-i','/root/.ssh/id_ed25519_old174','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/data/result_offload_pilot_20261023_v1/controls/OLD174_VERIFIED_KNOWN_HOSTS','-p','2233','root@10.208.130.174','python3 -B -']
 r=subprocess.run(ssh,input=code.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=90)
 need(r.returncode==0,'SOURCE_READ_ONLY_RECHECK_HOLD '+r.stderr.decode(errors='replace')[-2000:]);return json.loads(r.stdout)
def admissions():return dict(target=rr.admission('TARGET',include_activity=False),source=source_admission())

def main():
 need((os.uname().nodename,os.readlink('/proc/self/ns/mnt'))==('huangrulin-sshfs-174','mnt:[4026535153]'),'SUPERVISOR_ENDPOINT_CHANGED')
 lease=(T/'control/CONTINUATION_SUPERVISOR.lock').open('a+b');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
 need(hashlib.sha256((T/'control/FROZEN_SCOPES.json.gz').read_bytes()).hexdigest()=='718f30ec3bc8e5ece20df02cd472ebee17eac320f7b5a9e5b5e69841cc63cc04','FROZEN_QUEUE_CHANGED')
 need(hashlib.sha256((T/'tools/copy_engine.py').read_bytes()).hexdigest()==ENGINE_SHA,'QUALIFIED_REPAIR_ENGINE_CHANGED')
 need((T/'control/TREE_PARTIAL_REPAIR_CODE_INSTALL_DONE.json').exists(),'REAL_REPAIR_QUALIFICATION_MISSING')
 old=read(CONTROL);need(old['phase']=='TERMINAL_STATE_REQUIRES_ENGINEERING_REVIEW' and old['running'] is False,'OLD_SUPERVISOR_NOT_ENGINEERING_TERMINAL')
 need(not live(old['pid'],old['start_ticks'],'continuation_supervisor.py'),'OLD_SUPERVISOR_STILL_LIVE')
 final=read(T/'control/STATE.json');need(final['phase']=='FINITE_QUEUE_PASS_ENDED' and final['driver_exit_observed'] and final['completed_assets']==114,'OLD_DRIVER_NOT_114_FINITE_BOUNDARY')
 need(not live(final['driver_pid'],final['driver_start_ticks'],'offload_driver.py'),'OLD_DRIVER_STILL_LIVE')
 done=completed();need(len(done)==114 and AID not in done,'UNEXPECTED_COMMITTED_SET_AT_REPAIR_BOUNDARY')
 import gzip
 queue=json.loads(gzip.decompress((T/'control/FROZEN_SCOPES.json.gz').read_bytes()))['scopes'];need([z['asset_id'] for z in queue if z['asset_id'] not in done]==[AID],'REPAIR_SCOPE_NOT_EXACTLY_C80')
 deadline=old['deadline_unix'];rechecks=old['resource_rechecks'];restarts=old['driver_restarts'];need(time.time()<deadline,'ORIGINAL_SUPERVISION_DEADLINE_EXPIRED');need(rechecks<288 and restarts<96,'ORIGINAL_SUPERVISION_COUNTER_EXHAUSTED')
 own_ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]);current=dict(old['driver']);child=None;initial=True
 intent=dict(schema='LANE_T2_TREE_PARTIAL_REPAIR_SUPERVISION_INTENT_V1',unix=time.time(),asset_id=AID,old_supervisor=old,old_driver_state=final,qualified_engine_sha256=ENGINE_SHA,preserved_deadline_unix=deadline,preserved_counters=dict(resource_rechecks=rechecks,driver_restarts=restarts),remaining_scope=[AID],signals_sent=0,new_queue_created=False)
 audit.put(N/'REPAIR_SUPERVISION_INTENT.json',audit.blob(intent));audit.put(T/'control/TREE_PARTIAL_REPAIR_SUPERVISION_INTENT.json',audit.blob(intent))
 def state(phase,running=True,**extra):
  durable(CONTROL,dict(schema='LANE_T_FINITE_CONTINUATION_SUPERVISOR_V1',unix=time.time(),pid=os.getpid(),start_ticks=own_ticks,running=running,phase=phase,deadline_unix=deadline,max_resource_rechecks=288,max_driver_restarts=96,resource_rechecks=rechecks,driver_restarts=restarts,driver=current,frozen_scopes=115,Source_deletions=0,scientific_actions=0,engineering_repair='C80_EXACT_TREE_PREFIX_RESUME_V1',**extra))
 record('QUALIFIED_ENGINEERING_REPAIR_SUPERVISOR_STARTED',intent=intent)
 last_reason=None
 while time.time()<deadline:
  done=completed()
  if len(done)==115:
   state('FROZEN_QUEUE_COMPLETE',False,completed=115);result=dict(schema='LANE_T2_TREE_PARTIAL_REPAIR_SUPERVISION_DONE_V1',unix=time.time(),asset_id=AID,completed=115,preserved_deadline_unix=deadline,final_resource_rechecks=rechecks,final_driver_restarts=restarts,signals_sent=0,new_queue_created=False)
   audit.put(N/'REPAIR_SUPERVISION_DONE.json',audit.blob(result));audit.put(T/'control/TREE_PARTIAL_REPAIR_SUPERVISION_DONE.json',audit.blob(result));record('FROZEN_QUEUE_COMPLETE_AFTER_QUALIFIED_REPAIR',result=result);return
  if not initial and live(current['pid'],current['start_ticks'],'offload_driver.py'):
   state('OBSERVING_EXISTING_DRIVER',completed=len(done));time.sleep(10);continue
  if not initial:
   driver_final=read(T/'control/STATE.json')
   need((driver_final['driver_pid'],driver_final['driver_start_ticks'])==(current['pid'],current['start_ticks']),'REPAIR_DRIVER_IDENTITY_CHANGED')
   if driver_final['phase']!='COMMON_RESOURCE_HOLD' or not driver_final.get('driver_exit_observed'):
    state('TERMINAL_STATE_REQUIRES_ENGINEERING_REVIEW',False,observed_state=driver_final);record('REPAIR_DRIVER_TERMINAL_REVIEW',state=driver_final);return
   reason=driver_final.get('last_hold',{}).get('reason','')
  else:reason='INITIAL_QUALIFIED_C80_REPAIR_START'
  state('WAIT_COMMON_RESOURCE_ADMISSION',completed=len(done),reason=reason)
  rechecks+=1
  if rechecks>288 or restarts>=96:state('FINITE_CONTINUATION_BOUND_REACHED',False,completed=len(done));return
  try:resources=admissions()
  except Exception as e:
   if str(e)!=last_reason:record('RESOURCE_OR_OTHER_OWNER_WAIT_NO_TAKEOVER',reason=str(e));last_reason=str(e)
   state('WAIT_COMMON_RESOURCE_ADMISSION',completed=len(done),reason=str(e));time.sleep(300);continue
  for proc in P('/proc').iterdir():
   if not proc.name.isdigit():continue
   try:argv=(proc/'cmdline').read_bytes().split(b'\0')
   except OSError:continue
   need(str(T/'tools/offload_driver.py').encode() not in argv,'ANOTHER_DRIVER_NO_SECOND_START')
  restarts+=1;log=T/'control'/('driver_tree_partial_repair_'+str(time.time_ns())+'.log');record('FRESH_TWO_ENDPOINT_PASS_BEFORE_SAME_QUEUE_REPAIR',resources=resources,previous_driver=current)
  with log.open('xb') as out:child=subprocess.Popen(['nice','-n','19','ionice','-c','3','/usr/bin/python3','-B',str(T/'tools/offload_driver.py')],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,cwd=T,start_new_session=True)
  time.sleep(1);need(child.poll() is None,'REPAIR_DRIVER_LAUNCH_EXIT '+log.read_text()[-2000:]);ticks=int(P('/proc',str(child.pid),'stat').read_text().rsplit(')',1)[1].split()[19]);current=dict(pid=child.pid,start_ticks=ticks,log=str(log));durable(T/'control/CURRENT_DRIVER_PROCESS.json',current);record('SAME_FROZEN_QUEUE_REPAIR_DRIVER_STARTED',driver=current,driver_restarts=restarts);initial=False
 state('FINITE_24H_OBSERVATION_BOUND_REACHED',False)

if __name__=='__main__':
 try:main()
 except BaseException as e:
  record('REPAIR_SUPERVISOR_EXCEPTION_REQUIRES_REVIEW',error=repr(e),traceback=traceback.format_exc())
  try:
   x=read(CONTROL);x.update(running=False,phase='SUPERVISOR_EXCEPTION_REQUIRES_REVIEW',error=repr(e));durable(CONTROL,x)
  except Exception:pass
  raise
