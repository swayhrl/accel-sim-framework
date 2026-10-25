"""Cooperative post-COMMIT reload through the original Receiver lock.

No process signals. Never takes over a held lock. Same Supervisor/Publisher,
normal common-resource exit and admission; original counters remain cumulative.
"""
import pathlib,sys,os,time,json,hashlib,fcntl,signal,subprocess,traceback
P=pathlib.Path;T=P('/root/data/research_asset_verified_offload_20261024_v1');Q=T/'qualification/staged_transfer_rates_v1'
sys.path.insert(0,str(T/'tools'))
import retire_174new_build_duplicates as a
N=a.DEST.parent/'staged_transfer_rates_v1'

def blob(x):return (json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
def load(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(name,x):
 b=blob(x);a.put(T/'control'/name,b);a.put(N/name,b)
def live(pid,ticks,script):
 p=P('/proc',str(pid))
 try:return int((p/'stat').read_text().rsplit(')',1)[1].split()[19])==ticks and str(script).encode() in (p/'cmdline').read_bytes().split(b'\0')
 except OSError:return False
def durable_replace(p,b):
 tmp=p.with_name(p.name+'.rate-policy-writing')
 with tmp.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.replace(tmp,p);assert p.read_bytes()==b
def count():return len({x['asset_id'] for x in map(json.loads,(T/'control/LEDGER.jsonl').read_text().splitlines()) if x['status']=='ARCHIVED_CONTENT_VERIFIED'})

def main():
 a.q.mount_check()
 guard=(T/'control/RATE_POLICY_TRANSITION.lock').open('a+b');fcntl.flock(guard,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not (T/'control/RATE_POLICY_TRANSITION_INTENT.json').exists(),'retained transition: inspect existing owner and receipts; no replay'
 q=load(Q/'QUALIFICATION.json');assert all(x=='PASS' for x in q['checks'].values())
 auth=(Q/'TRANSFER_RATE_USER_AUTHORIZATION.json').read_bytes();assert hashlib.sha256(auth).hexdigest()==q['authorization_sha256']
 for n,h in q['staged_sha256'].items():assert sha(Q/n)==h;compile((Q/n).read_bytes(),str(T/'tools'/n),'exec')
 for n in ['copy_engine.py','offload_driver.py','server_resources.py','continuation_supervisor.py']:
  assert (T/'tools'/n).read_bytes()==(Q/('BEFORE_'+n)).read_bytes(),'native code changed before qualified handoff '+n
 state=load(T/'control/STATE.json');sup=load(T/'control/CONTINUATION_SUPERVISOR.json')
 oldpid=state['driver_pid'];oldticks=state['driver_start_ticks'];asset=state['asset_id']
 assert live(oldpid,oldticks,T/'tools/offload_driver.py') and live(sup['pid'],sup['start_ticks'],T/'tools/continuation_supervisor.py')
 assert sup['driver']['pid']==oldpid and sup['driver']['start_ticks']==oldticks
 assert state['asset_kind']=='TRACE' and state['asset_expected_bytes']>240*1024**2,'handoff requires current large scope with bounded restore skipped'
 assert time.time()<sup['deadline_unix'] and sup['driver_restarts']<sup['max_driver_restarts'] and sup['resource_rechecks']<sup['max_resource_rechecks']
 lockpath=a.BRIDGE/'.TARGET_RECEIVER.lock';ino=lockpath.stat().st_ino
 owners=[int(z.split()[4]) for z in P('/proc/locks').read_text().splitlines() if '->' not in z and z.split()[5].endswith(':'+str(ino))]
 assert owners==[oldpid],('current driver does not own exact Receiver lock',owners)
 assert sha(T/'control/FROZEN_SCOPES.json.gz')=='718f30ec3bc8e5ece20df02cd472ebee17eac320f7b5a9e5b5e69841cc63cc04'
 own_ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])
 intent=dict(schema='LANE_T2_COOPERATIVE_RATE_RELOAD_INTENT_V1',unix=time.time(),coordinator_pid=os.getpid(),coordinator_start_ticks=own_ticks,current_asset=asset,previous_driver_state=state,previous_supervisor_state=sup,authorization_sha256=q['authorization_sha256'],qualified_staged_sha256=q['staged_sha256'],requested_initial_tier=[30,60],protocol_changes=False,signals_sent=0,maximum_lock_wait_seconds=2700,original_deadline_unix=sup['deadline_unix'])
 put('RATE_POLICY_TRANSITION_INTENT.json',intent)
 f=lockpath.open('rb')
 try:
  # Wait for the existing owner's NORMAL unlock, bounded by the old deadline.
  seconds=min(2700,max(1,int(sup['deadline_unix']-time.time())))
  def expired(sig,frame):raise TimeoutError('normal post-COMMIT Receiver release not reached within bounded wait; existing transfer untouched')
  signal.signal(signal.SIGALRM,expired);signal.alarm(seconds)
  fcntl.flock(f,fcntl.LOCK_EX);signal.alarm(0)
  acquired=time.time();bundle=a.DEST.parent.parent/'assets'/asset
  # a.DEST is a control subdirectory; obtain the actual assets root explicitly.
  bundle=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets')/asset
  assert (bundle/'COMMIT.json').exists(),'no completed current transaction; release lock and inspect failure'
  committed_sha=sha(bundle/'COMMIT.json')
  put('RATE_POLICY_POST_COMMIT_LOCK_BOUNDARY.json',dict(unix=acquired,current_asset=asset,COMMIT_sha256=committed_sha,receiver_lock_inode=ino,coordinator_pid=os.getpid(),normal_owner_release=True,signals_sent=0))
  # Current large native restore is a recorded >240MiB skip, so the original
  # Driver commits its ledger then encounters this normal lock on next admission.
  end=time.monotonic()+25
  while live(oldpid,oldticks,T/'tools/offload_driver.py') and time.monotonic()<end:time.sleep(.1)
  assert not live(oldpid,oldticks,T/'tools/offload_driver.py'),'old Driver did not leave normal common-resource boundary; no code replacement'
  final=load(T/'control/STATE.json')
  assert (final['driver_pid'],final['driver_start_ticks'])==(oldpid,oldticks)
  assert final['phase']=='COMMON_RESOURCE_HOLD' and final.get('driver_exit_observed') and final.get('driver_exit_code')==0
  assert final['last_hold']['reason']=='OTHER_EXISTING_ARCHIVE_LOCK_HELD_NO_TAKEOVER'
  rows=[x for x in map(json.loads,(T/'control/LEDGER.jsonl').read_text().splitlines()) if x['asset_id']==asset and x['status']=='ARCHIVED_CONTENT_VERIFIED']
  assert len(rows)==1 and rows[0]['commit_sha256']==committed_sha,'missing or duplicate current COMMIT ledger closure'
  current_sup=load(T/'control/CONTINUATION_SUPERVISOR.json')
  assert live(sup['pid'],sup['start_ticks'],T/'tools/continuation_supervisor.py')
  assert current_sup['pid']==sup['pid'] and current_sup['start_ticks']==sup['start_ticks'] and current_sup['deadline_unix']==sup['deadline_unix']
  assert current_sup['resource_rechecks']>=sup['resource_rechecks'] and current_sup['driver_restarts']==sup['driver_restarts']
  for n in ['server_resources.py','continuation_supervisor.py']:assert (T/'tools'/n).read_bytes()==(Q/('BEFORE_'+n)).read_bytes()
  a.put(T/'control/TRANSFER_RATE_USER_AUTHORIZATION.json',auth);a.put(N/'TRANSFER_RATE_USER_AUTHORIZATION.json',auth)
  a.put(N/'QUALIFICATION.json',(Q/'QUALIFICATION.json').read_bytes())
  policy=dict(schema='LANE_T2_ACTIVE_TRANSFER_RATE_TIER_V1',source_MiB_per_second=30,total_MiB_per_second=60,authorization_sha256=q['authorization_sha256'],tier_receipt=str(N/'TIER_30_60_INTENT.json'))
  put('TIER_30_60_INTENT.json',dict(unix=time.time(),policy=policy,previous_completed=count(),previous_supervisor_state=current_sup))
  a.put(T/'control/TRANSFER_RATE_POLICY.json',blob(policy));a.put(N/'INITIAL_TRANSFER_RATE_POLICY.json',blob(policy))
  for n in ['copy_engine.py','offload_driver.py']:
   b=(Q/n).read_bytes();durable_replace(T/'tools'/n,b);a.put(N/n,b)
  done=dict(schema='LANE_T2_COOPERATIVE_RATE_RELOAD_DONE_V1',unix=time.time(),current_asset=asset,current_asset_COMMIT_sha256=committed_sha,completed=count(),old_driver_pid=oldpid,old_driver_start_ticks=oldticks,old_driver_normal_exit=True,original_driver_final_state=final,supervisor_pid_unchanged=sup['pid'],supervisor_start_ticks_unchanged=sup['start_ticks'],original_deadline_unix=sup['deadline_unix'],counters_before=dict(resource_rechecks=sup['resource_rechecks'],driver_restarts=sup['driver_restarts']),policy=policy,new_tools_sha256=q['staged_sha256'],signals_sent=0,duplicate_driver_or_supervisor_started=0,publisher_restarts=0,lock_inode_unchanged=lockpath.stat().st_ino==ino,lock_held_seconds_before_release=time.time()-acquired)
  put('RATE_POLICY_TRANSITION_DONE.json',done)
 finally:
  signal.alarm(0);f.close()
 print(json.dumps(done),flush=True)

if __name__=='__main__':
 try:main()
 except BaseException as e:
  put('RATE_POLICY_TRANSITION_FAILURE_%d.json'%time.time_ns(),dict(unix=time.time(),error=repr(e),traceback=traceback.format_exc(),no_blind_retry=True,signals_sent=0));raise
