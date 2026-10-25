"""One controlled policy reload at the existing common-resource boundary.

Terminates only the verified old sleeping supervisor, never a driver/science
process. Retains original counters/deadline/locks/queue and the live Publisher.
Requires a Publisher timing window so its normal liveness check sees no gap.
"""
import os,sys,pathlib,json,time,hashlib,signal,select,fcntl,subprocess,importlib.util,argparse,traceback
P=pathlib.Path;T=P('/root/data/research_asset_verified_offload_20261024_v1');STAGE=T/'qualification/active_science_io_policy_v1'
sys.path.insert(0,str(T/'tools'))
import retire_174new_build_duplicates as audit
N=audit.DEST.parent/'active_science_io_monitor_only_20261025_v1'

def put(name,x):
    b=(json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
    audit.put(N/name,b);audit.put(T/'control'/name,b)

def live(pid,ticks,script):
    p=P('/proc',str(pid))
    try:
        raw=(p/'stat').read_text().rsplit(')',1)[1].split()
        return int(raw[19])==ticks and str(script).encode() in (p/'cmdline').read_bytes().split(b'\0')
    except OSError:return False

def no_driver():
    for p in P('/proc').iterdir():
        if not p.name.isdigit():continue
        try:args=(p/'cmdline').read_bytes().split(b'\0')
        except OSError:continue
        assert str(T/'tools/offload_driver.py').encode() not in args,'existing driver appeared; do not reload supervision'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--publisher-safe-until',required=True,type=float);a=ap.parse_args()
    assert time.time()+20<a.publisher_safe_until,'no safe Publisher sleep window'
    audit.q.mount_check()
    own=(T/'control/IO_POLICY_TRANSITION.lock').open('a+b');fcntl.flock(own,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert not (T/'control/IO_POLICY_TRANSITION_INTENT.json').exists(),'retained transition: inspect instead of blind replay'
    no_driver()
    spec=importlib.util.spec_from_file_location('policy_for_transition',STAGE/'server_resources.py');rr=importlib.util.module_from_spec(spec);spec.loader.exec_module(rr)
    auth=rr.active_science_io_authorization();assert auth
    qualification=json.loads((STAGE/'QUALIFICATION.json').read_bytes());assert all(v=='PASS' for v in qualification['checks'].values())
    before_tools={n:hashlib.sha256((T/'tools'/n).read_bytes()).hexdigest() for n in ['server_resources.py','continuation_supervisor.py']}
    for n in before_tools:assert (T/'tools'/n).read_bytes()==(STAGE/('BEFORE_'+n)).read_bytes(),'live code changed since qualification'
    locks=[]
    for n in ['.TARGET_RECEIVER.lock','.TLS_V10_SOURCE_SENDER.lock']:
        f=(audit.BRIDGE/n).open('rb');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
    rr.admission('TARGET',include_activity=False,allowed_lock_pids=(os.getpid(),))
    previous=json.loads((T/'control/CONTINUATION_SUPERVISOR.json').read_bytes())
    assert previous['phase']=='WAIT_COMMON_RESOURCE_ADMISSION' and previous['running']
    assert previous['reason'] in ['RESOURCE_HOLD_ACTUAL_ACTIVE_AEFAIR_IO','OTHER_EXISTING_ARCHIVE_LOCK_HELD_NO_TAKEOVER']
    assert live(previous['pid'],previous['start_ticks'],T/'tools/continuation_supervisor.py')
    final=(T/'control/STATE.json').read_bytes();state=json.loads(final)
    assert state['phase']=='COMMON_RESOURCE_HOLD' and state['driver_exit_observed']
    assert (state['driver_pid'],state['driver_start_ticks'])==(previous['driver']['pid'],previous['driver']['start_ticks'])
    assert not live(state['driver_pid'],state['driver_start_ticks'],T/'tools/offload_driver.py')
    assert hashlib.sha256((T/'control/FROZEN_SCOPES.json.gz').read_bytes()).hexdigest()=='718f30ec3bc8e5ece20df02cd472ebee17eac320f7b5a9e5b5e69841cc63cc04'
    assert hasattr(signal,'pidfd_send_signal'),'exact process-handle signalling unavailable'
    fd=os.pidfd_open(previous['pid'])
    assert live(previous['pid'],previous['start_ticks'],T/'tools/continuation_supervisor.py')
    intent={'schema':'LANE_T2_IO_POLICY_RELOAD_INTENT_V1','unix':time.time(),'previous_supervisor_state':previous,'previous_tools_sha256':before_tools,'driver_STATE_sha256':hashlib.sha256(final).hexdigest(),'io_authorization':auth,'qualified_checks':qualification['checks'],'publisher_safe_until':a.publisher_safe_until,'targeted_signal':'SIGTERM only to verified old supervisor via pidfd','science_or_driver_signals':0,'publisher_restarts':0,'no_new_deadline_or_counter_budget':True}
    put('IO_POLICY_TRANSITION_INTENT.json',intent)
    assert time.time()+15<a.publisher_safe_until,'Publisher timing window closed before handoff'
    signal.pidfd_send_signal(fd,signal.SIGTERM)
    try:assert select.select([fd],[],[],10)[0],'old supervisor did not exit; no replacement launched'
    finally:os.close(fd)
    assert not live(previous['pid'],previous['start_ticks'],T/'tools/continuation_supervisor.py')
    no_driver();assert (T/'control/STATE.json').read_bytes()==final,'driver boundary changed during handoff'
    old=json.loads((T/'control/CONTINUATION_SUPERVISOR.json').read_bytes())
    assert (old['pid'],old['start_ticks'])==(previous['pid'],previous['start_ticks'])
    assert old['deadline_unix']==previous['deadline_unix'] and old['resource_rechecks']>=previous['resource_rechecks'] and old['driver_restarts']==previous['driver_restarts']
    handoff={'schema':'LANE_T2_IO_POLICY_SUPERVISOR_HANDOFF_V1','unix':time.time(),'io_authorization_sha256':rr.IO_AUTHORIZATION_SHA256,'previous_supervisor_state':old,'old_supervisor_exit_verified_by_pidfd':True,'old_driver_STATE_sha256':hashlib.sha256(final).hexdigest(),'original_deadline_and_cumulative_counters_preserved':True,'publisher_pid_unchanged':32272}
    name='SUPERVISOR_IO_POLICY_HANDOFF_20261025_V1.json';put(name,handoff)
    after_tools={}
    for n in ['server_resources.py','continuation_supervisor.py']:
        b=(STAGE/n).read_bytes();compile(b,str(T/'tools'/n),'exec')
        tmp=T/'tools'/(n+'.io-policy-writing')
        with tmp.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
        os.replace(tmp,T/'tools'/n);assert (T/'tools'/n).read_bytes()==b
        audit.put(N/n,b);after_tools[n]=hashlib.sha256(b).hexdigest()
    # Probe/release the existing supervisor lock file, never replace/delete it.
    lease=(T/'control/CONTINUATION_SUPERVISOR.lock').open('a+b');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB);lease.close()
    for f in locks:f.close()
    log=T/'control'/('supervisor_io_policy_continue_'+str(time.time_ns())+'.log')
    with log.open('xb') as out:
        child=subprocess.Popen(['nice','-n','19','ionice','-c','3','/usr/bin/python3','-B',str(T/'tools/continuation_supervisor.py'),'--resume-preserved-supervision',str(T/'control'/name)],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,cwd=T,start_new_session=True)
    started=time.monotonic();new=None
    while time.monotonic()-started<10:
        assert child.poll() is None,'replacement exited '+log.read_text()[-3000:]
        value=json.loads((T/'control/CONTINUATION_SUPERVISOR.json').read_bytes())
        if value['pid']==child.pid and live(child.pid,value['start_ticks'],T/'tools/continuation_supervisor.py'):new=value;break
        time.sleep(0.1)
    assert new,'new supervisor did not publish its verified identity within timing window'
    assert new['deadline_unix']==old['deadline_unix'] and new['resource_rechecks']>=old['resource_rechecks'] and new['driver_restarts']>=old['driver_restarts']
    result={'schema':'LANE_T2_IO_POLICY_RELOAD_DONE_V1','unix':time.time(),'old_supervisor_pid':old['pid'],'old_supervisor_start_ticks':old['start_ticks'],'old_supervisor_exited_before_replacement':True,'new_supervisor_state':new,'preserved_original_deadline_unix':old['deadline_unix'],'counters_before':{'resource_rechecks':old['resource_rechecks'],'driver_restarts':old['driver_restarts']},'new_tools_sha256':after_tools,'authorization_sha256':rr.IO_AUTHORIZATION_SHA256,'log':str(log),'single_existing_queue_and_lock_files':True,'science_or_driver_signals':0,'publisher_restarts':0,'no_24h_or_counter_reset':True}
    put('IO_POLICY_TRANSITION_DONE.json',result);print(json.dumps(result),flush=True)

if __name__=='__main__':
    try:main()
    except BaseException as e:
        put('IO_POLICY_TRANSITION_FAILURE_%d.json'%time.time_ns(),{'unix':time.time(),'error':repr(e),'traceback':traceback.format_exc(),'no_blind_replay':True});raise
