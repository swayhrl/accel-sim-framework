#!/usr/bin/env python3
"""New two-gate handoff; exact still-PENDING subset of original33, old deadline."""
import pathlib,json,os,time,fcntl,signal,traceback
from native_reduction_entry_candidate_v1 import D,C,B,DEADLINE,approved,sha,save,load,identity,need,pinned_archive,queue33
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--plan',required=True);a=p.parse_args()
 pp=pathlib.Path(a.plan);need(pp.resolve()==(D/'entry_run/RESUME_PLAN.json').resolve(),'fixed resume plan')
 plan=load(pp);approved(plan['Root_approval_path'],plan['Root_approval_sha256'])
 need(plan['resume_source_sha256']==sha(__file__) and plan['deadline_unix']==DEADLINE,'resume source/deadline')
 token=os.environ.pop('RTX_REDUCTION_RESUME_TOKEN','');need(token and token==plan['token'],'resume token')
 frozen=load(D/'preimages/FROZEN_PENDING_33.json')['jobs'];by={x['id']:x for x in frozen}
 selected=plan['selected_ids'];need(len(set(selected))==len(selected) and selected==[x['id'] for x in frozen if x['id'] in set(selected)],'exact ordered subset')
 need(all(x in by for x in selected),'outside original33')
 os.nice(15);os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2])
 from resume_gate_v1 import acquire_and_wait
 me,lease=acquire_and_wait(D/'entry_run',C,token,DEADLINE)
 run=D/'entry_run/remaining33_run';run.mkdir(exist_ok=False)
 arc=pinned_archive()
 def state(status,**kw):arc['save'](run/'STATE.json',dict(me,status=status,deadline_unix=DEADLINE,selected_ids=selected,unix=time.time(),**kw))
 def timeout(sig,frame):raise TimeoutError('original batch absolute deadline reserve')
 signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,max(.1,DEADLINE-time.time()-60))
 ack=dict(me,token=token,selected_ids=selected,deadline_unix=DEADLINE,run_directory=str(run))
 save(D/'entry_run/REMAINING33_NEW_ACK.json',ack)
 while True:
  if (C/'STOP_AFTER_CURRENT').exists():state('STOP_AFTER_CURRENT');return
  if time.time()>=DEADLINE-120:state('BATCH_DEADLINE');return
  jobs=arc['scope_jobs'](load(C/'QUEUE.json'),by,selected)
  if not jobs:state('FROZEN_REMAINING_SCOPE_EXHAUSTED');return
  job=jobs[0];hs=[];claimed=False
  try:
   for name in ['RTX4080_SOURCE.lock','RTX4080_TARGET.lock']:
    f=(C/name).open('r+')
    try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BaseException:f.close();raise
    hs.append(f)
   if (C/'STOP_AFTER_CURRENT').exists():state('STOP_AFTER_CURRENT');return
   fresh=arc['scope_jobs'](load(C/'QUEUE.json'),by,[job['id']])
   if not fresh:continue
   job=fresh[0];need(job['type']=='CAPTURE_ORDINARY','ordinary only')
   job.update(status='RUNNING',started=time.time());arc['update_job'](job);claimed=True;state('RUNNING',job_id=job['id'])
   with (run/(job['id']+'.stderr.log')).open('x') as err:
    rc,out=arc['run_remote'](job,by[job['id']],DEADLINE,err)
   (run/(job['id']+'.stdout.log')).write_text(out);need(rc==0,'ordinary guard/worker failure')
   sender=json.loads(out)
   if sender.get('status')=='SENDER_COMPLETE':job.update(status='COMMITTED_VERIFIED',commit=arc['publish'](sender))
   else:job.update(status=sender.get('status','HOLD'),result=sender)
  except BlockingIOError:state('WAIT_CHANNEL_LEASE');time.sleep(2);continue
  except BaseException as e:
   if claimed:
    job.update(status='FAILED_RETAINED',error=repr(e),end_unix=time.time());arc['update_job'](job)
   state('FAILED_RETAINED_STOP_NO_RETRY',error=repr(e));raise
  finally:
   for f in reversed(hs):fcntl.flock(f,fcntl.LOCK_UN);f.close()
  job['end_unix']=time.time();arc['update_job'](job);state(job['status'],job_id=job['id'])
  if job['status']!='COMMITTED_VERIFIED':state('NONCOMMIT_STOP');return
if __name__=='__main__':main()
