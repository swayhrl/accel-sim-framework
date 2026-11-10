#!/usr/bin/env python3
"""Bounded one-shot terminal watcher and closure; never launches/retries a model."""
import datetime,json,os,subprocess,time
from pathlib import Path
P=Path
R=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
N=P('/root/data/ep_l2_dtc_l1_native_v2')
REQ='EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1'
CASE='EP_PERF_CLEAN128_STENCIL_WV_EXT1_20261110_V1'
SUPERVISOR=1602833
CONTROL=R/'control'
STATUS=CONTROL/'EXT1_BACKGROUND_MONITOR_STATUS.json'
LOG=CONTROL/'EXT1_ACCEPT_ARCHIVE_20261110.log'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(x):
 x.update(utc=now(),request=REQ,cohort=CASE,automatic_retry=False)
 tmp=STATUS.with_name('.'+STATUS.name+'.tmp')
 with tmp.open('w') as f:json.dump(x,f,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,STATUS)
def live(pid):
 try:
  s=(P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[0]
  return s not in ('Z','X')
 except OSError:return False
def row():
 q=json.loads((N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_bytes())['registered_future_requests'][REQ]
 assert q['budget']==1 and q['remaining']==0 and set(q['consumed'])=={CASE}
 return q['consumed'][CASE]
def main():
 started=time.monotonic();dead_count=0
 while time.monotonic()-started<48*3600:
  q=row();state=q['state']
  if state=='NATURAL_COMPLETE_PENDING_VALIDATION':
   write({'status':'NATURAL_COMPLETE_ACCEPT_ARCHIVE_START','uuid':q['uuid']})
   assert not LOG.exists(),'existing acceptance log; no second attempt'
   with LOG.open('xb') as f:
    result=subprocess.run([str(N/'bin/native'),'experiment','accept',CASE,'--project','EP_L2'],
      stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,cwd='/root/workspace',timeout=4*3600)
   final=row();write({'status':'ACCEPT_ARCHIVE_COMMAND_FINISHED','returncode':result.returncode,
        'registry_state':final['state'],'uuid':final['uuid'],'log':str(LOG)})
   return
  if state in ('CLOSED_ACCEPTED','CLOSED_UNACCEPTED','PARSE_HOLD','UNACCEPTED_ENGINEERING_FAILURE','ACCEPTED_PENDING_ARCHIVE'):
   write({'status':'TERMINAL_WITHOUT_AUTO_RETRY','registry_state':state,'uuid':q['uuid']});return
  if live(SUPERVISOR):dead_count=0
  else:dead_count+=1
  if dead_count>=3:
   write({'status':'SUPERVISOR_GONE_WITHOUT_NATURAL_DONE_STOP','registry_state':state,'uuid':q['uuid']});return
  write({'status':'WAITING_FOR_NATURAL_DONE','registry_state':state,'uuid':q['uuid'],
         'supervisor_pid':SUPERVISOR,'supervisor_live':live(SUPERVISOR),
         'deadline_hours':48})
  time.sleep(90)
 write({'status':'BOUND_48H_MONITOR_STOP','registry_state':row()['state']})
if __name__=='__main__':
 try:main()
 except Exception as e:write({'status':'MONITOR_EXCEPTION_STOP','reason':repr(e)});raise
