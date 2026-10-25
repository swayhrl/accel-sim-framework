"""Bounded continuation of the same 115 scopes after common resource waits.

This is not a data sender, receiver, scientific scheduler or new task queue.
It observes the existing driver without intervention. Only after verified exit
at COMMON_RESOURCE_HOLD does it attempt fresh independent endpoint admission.
All other terminal failures stop for engineering review. No unlinks are used.
"""
import os,sys,time,json,pathlib,subprocess,fcntl,hashlib,traceback
import copy_engine as c
T=c.TASK;P=pathlib.Path
CONTROL=T/'control/CONTINUATION_SUPERVISOR.json'
JOURNAL=T/'control/CONTINUATION_SUPERVISOR.jsonl'

def process(pid,ticks):
    p=P('/proc')/str(pid)
    try:
        actual=int((p/'stat').read_text().rsplit(')',1)[1].split()[19])
        argv=(p/'cmdline').read_bytes().split(b'\0')
        return actual==ticks and str(T/'tools/offload_driver.py').encode() in argv
    except OSError:return False

def durable(path,x):
    path=P(path);tmp=path.with_name(path.name+'.supervisor-writing')
    with tmp.open('wb') as f:f.write(c.canon(x));f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)

def record(event,**kw):
    row=dict(event=event,unix=time.time(),supervisor_pid=os.getpid(),**kw)
    with JOURNAL.open('ab') as f:f.write(c.canon(row));f.flush();os.fsync(f.fileno())

def count():
    rows=[json.loads(z) for z in (T/'control/LEDGER.jsonl').read_text().splitlines()]
    return len({x['asset_id'] for x in rows if x['status']=='ARCHIVED_CONTENT_VERIFIED'})

def admission():
    target=c.rr.admission('TARGET',include_activity=False)
    code=P(c.rr.__file__).read_text()+'\nprint(json.dumps(admission("SOURCE",include_activity=False)))\n'
    ssh=['ssh','-i','/root/.ssh/id_ed25519_old174','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/data/result_offload_pilot_20261023_v1/controls/OLD174_VERIFIED_KNOWN_HOSTS','-p','2233','root@10.208.130.174','python3 -B -']
    r=subprocess.run(ssh,input=code.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=90)
    c.need(r.returncode==0,'SOURCE_READ_ONLY_RECHECK_HOLD '+r.stderr.decode(errors='replace')[-2000:])
    return dict(source=json.loads(r.stdout),target=target)

def main():
    c.need((os.uname().nodename,os.readlink('/proc/self/ns/mnt'))==('huangrulin-sshfs-174','mnt:[4026535153]'),'SUPERVISOR_ENDPOINT_CHANGED')
    lock=(T/'control/CONTINUATION_SUPERVISOR.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    c.need(hashlib.sha256((T/'control/FROZEN_SCOPES.json.gz').read_bytes()).hexdigest()=='718f30ec3bc8e5ece20df02cd472ebee17eac320f7b5a9e5b5e69841cc63cc04','FROZEN_QUEUE_CHANGED')
    identity=c.read(T/'control/RESUMED_DRIVER_PROCESS.json');current=dict(pid=identity['pid'],start_ticks=identity['start_ticks'],log=identity['log'])
    c.need(process(current['pid'],current['start_ticks']),'INITIAL_DRIVER_NOT_ALIVE_NO_BLIND_START')
    started=time.time();deadline=started+24*3600;own_ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]);restarts=0;rechecks=0;last_event=None;child=None
    def state(phase,running=True,**extra):
        x=dict(schema='LANE_T_FINITE_CONTINUATION_SUPERVISOR_V1',unix=time.time(),pid=os.getpid(),start_ticks=own_ticks,running=running,phase=phase,deadline_unix=deadline,max_resource_rechecks=288,max_driver_restarts=96,resource_rechecks=rechecks,driver_restarts=restarts,driver=current,frozen_scopes=115,Source_deletions=0,scientific_actions=0,**extra)
        durable(CONTROL,x)
    record('OBSERVE_EXISTING_DRIVER',driver=current,deadline_unix=deadline)
    while time.time()<deadline:
        completed=count()
        if completed==115:
            state('FROZEN_QUEUE_COMPLETE',False,completed=completed);record('FROZEN_QUEUE_COMPLETE',completed=completed);return
        if process(current['pid'],current['start_ticks']):
            state('OBSERVING_EXISTING_DRIVER',completed=completed)
            time.sleep(30);continue
        if child is not None:child.poll()
        final=c.read(T/'control/STATE.json')
        if (final.get('driver_pid'),final.get('driver_start_ticks'))!=(current['pid'],current['start_ticks']):
            state('OTHER_DRIVER_IDENTITY_REQUIRES_REVIEW',False,observed_state=final);return
        if final['phase']!='COMMON_RESOURCE_HOLD' or not final.get('driver_exit_observed'):
            state('TERMINAL_STATE_REQUIRES_ENGINEERING_REVIEW',False,observed_state=final)
            record('DRIVER_TERMINAL_NO_AUTOMATIC_RETRY',driver=current,final_state=final);return
        # An incompatible identity or genuine164 route is never retried.
        reason=final.get('last_hold',{}).get('reason','')
        if any(x in reason for x in ['POLICY_IDENTITY_HOLD','NOT_TRUE164','ENDPOINT_IDENTITY','UNKNOWN_SOURCE_ACTIVE_WRITE_RESERVATION']):
            state('CONTRACT_OR_IDENTITY_REQUIRES_REVIEW',False,reason=reason);return
        state('WAIT_COMMON_RESOURCE_ADMISSION',completed=completed,last_driver_hold=reason)
        rechecks+=1
        if rechecks>288 or restarts>=96:
            state('FINITE_CONTINUATION_BOUND_REACHED',False,completed=completed);return
        try:
            resources=admission()
        except Exception as e:
            if str(e)!=last_event:
                record('RESOURCE_OR_OTHER_OWNER_WAIT_NO_TAKEOVER',reason=str(e));last_event=str(e)
            state('WAIT_COMMON_RESOURCE_ADMISSION',completed=completed,reason=str(e));time.sleep(300);continue
        # Never infer that a dead PID makes locks stale. The fresh admissions
        # must report no foreign owner; the driver independently rechecks again.
        for proc in P('/proc').iterdir():
            if not proc.name.isdigit():continue
            try:argv=(proc/'cmdline').read_bytes().split(b'\0')
            except OSError:continue
            c.need(str(T/'tools/offload_driver.py').encode() not in argv,'ANOTHER_DRIVER_NO_SECOND_START')
        restarts+=1;log=T/'control'/('driver_continue_'+str(time.time_ns())+'.log')
        record('FRESH_TWO_ENDPOINT_PASS_BEFORE_SAME_QUEUE_RESUME',previous_driver=current,resources=resources)
        with log.open('xb') as out:
            child=subprocess.Popen(['nice','-n','19','ionice','-c','3','/usr/bin/python3','-B',str(T/'tools/offload_driver.py')],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,cwd=str(T),start_new_session=True)
        time.sleep(1)
        c.need(child.poll() is None,'RESUMED_DRIVER_LAUNCH_EXIT '+log.read_text()[-2000:])
        ticks=int(P('/proc',str(child.pid),'stat').read_text().rsplit(')',1)[1].split()[19]);current=dict(pid=child.pid,start_ticks=ticks,log=str(log));durable(T/'control/CURRENT_DRIVER_PROCESS.json',current)
        record('SAME_FROZEN_QUEUE_RESUMED',driver=current,driver_restarts=restarts)
    state('FINITE_24H_OBSERVATION_BOUND_REACHED',False)

if __name__=='__main__':
    try:main()
    except Exception as e:
        record('SUPERVISOR_STOPPED_NO_DATA_OR_SCIENTIFIC_INTERVENTION',error=str(e),traceback=traceback.format_exc())
        if CONTROL.exists():
            x=c.read(CONTROL);x.update(running=False,phase='SUPERVISOR_EXCEPTION_REQUIRES_REVIEW',error=str(e));durable(CONTROL,x)
        raise
