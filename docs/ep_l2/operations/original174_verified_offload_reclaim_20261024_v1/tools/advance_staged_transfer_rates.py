"""One bounded observation/promotion, never starts or signals an executor."""
from local_common import *

CODE=r'''
import pathlib,sys,json,os,time,hashlib,fcntl
P=pathlib.Path;T=P('/root/data/research_asset_verified_offload_20261024_v1');sys.path.insert(0,str(T/'tools'))
import copy_engine as c
import retire_174new_build_duplicates as a
N=a.DEST.parent/'staged_transfer_rates_v1'
def load(p):return json.loads(P(p).read_bytes())
def live(pid,ticks,script):
 p=P('/proc',str(pid))
 try:return int((p/'stat').read_text().rsplit(')',1)[1].split()[19])==ticks and str(T/'tools'/script).encode() in (p/'cmdline').read_bytes().split(b'\0')
 except OSError:return False
guard=(T/'control/RATE_POLICY_TRANSITION.lock').open('a+b');fcntl.flock(guard,fcntl.LOCK_EX|fcntl.LOCK_NB)
result=dict(schema='LANE_T2_STAGED_RATE_OBSERVATION_V1',unix=time.time(),signals_sent=0,new_executors_started=0)
try:
 assert (T/'control/RATE_POLICY_TRANSITION_DONE.json').exists(),'cooperative reload not finished'
 before=c.rate_limits(force=True);result['current_rates']=before
 if before['source_MiB_per_second']==60:result['status']='ALREADY_AT_AUTHORIZED_MAXIMUM'
 else:
  assert (before['source_MiB_per_second'],before['total_MiB_per_second'])==(30,60)
  s=load(T/'control/STATE.json');sup=load(T/'control/CONTINUATION_SUPERVISOR.json');done=load(T/'control/RATE_POLICY_TRANSITION_DONE.json')
  assert live(s['driver_pid'],s['driver_start_ticks'],'offload_driver.py') and live(sup['pid'],sup['start_ticks'],'continuation_supervisor.py')
  assert sup['pid']==done['supervisor_pid_unchanged'] and sup['start_ticks']==done['supervisor_start_ticks_unchanged'] and sup['deadline_unix']==done['original_deadline_unix'] and time.time()<sup['deadline_unix']
  assert s.get('archive_transfer_rate_policy',{}).get('source_MiB_per_second')==30,'new Driver has not confirmed initial tier'
  sent=s.get('current_asset_new_transferred_bytes',0);expected=s['asset_expected_bytes']
  result.update(asset_id=s['asset_id'],phase=s['phase'],verified_bytes=sent,expected_bytes=expected)
  if s['phase']!='TRANSFER_RANGE_VERIFIED' or not 0<sent<expected:result['status']='WAIT_FOR_LIVE_30_60_PAYLOAD_SAMPLE'
  else:
   children=[]
   for p in P('/proc').iterdir():
    if not p.name.isdigit():continue
    try:
     raw=(p/'stat').read_text().rsplit(')',1)[1].split();argv=(p/'cmdline').read_bytes().split(b'\0')
     if int(raw[1])==s['driver_pid'] and (argv[0].endswith(b'/ssh') or argv[0]==b'ssh' or str(T/'tools/copy_engine.py').encode() in argv):children.append(int(p.name))
    except OSError:pass
   assert len(children)==1,'single live Sender child not identified'
   resource=c.rr.admission('TARGET',include_activity=False,allowed_lock_pids=(s['driver_pid'],*children));result['resources']=resource
   sample=dict(unix=time.time(),asset_id=s['asset_id'],driver_pid=s['driver_pid'],driver_start_ticks=s['driver_start_ticks'],verified_bytes=sent,resources=resource)
   bp=T/'control/rate_observations'/s['asset_id']/'BASELINE_30_60.json'
   if not bp.exists():
    a.put(bp,c.canon(sample));a.put(N/(s['asset_id']+'_BASELINE_30_60.json'),c.canon(sample));result['status']='BASELINE_30_60_RECORDED'
   else:
    baseline=load(bp);elapsed=sample['unix']-baseline['unix'];delta=sent-baseline['verified_bytes'];result.update(observed_seconds=elapsed,verified_delta_bytes=delta,effective_range_MiB_per_second=delta/elapsed/c.MIB)
    assert (baseline['driver_pid'],baseline['driver_start_ticks'])==(s['driver_pid'],s['driver_start_ticks']),'Driver changed; inspect sample boundary'
    io=resource['IO'];margin=io['some']['avg60']<18 and io['full']['avg60']<15
    if elapsed<120 or delta<512*c.MIB:result['status']='WAIT_FOR_120_SECOND_AND_512MIB_VERIFIED_SAMPLE'
    elif not margin:result['status']='RETAIN_30_60_PROMOTION_MARGIN_NOT_MET'
    else:
     # All original gates already passed above. This extra promotion margin
     # leaves space below severe pressure some25/full20; it lowers no gate.
     result['status']='PROMOTE_TO_AUTHORIZED_60_120';result['baseline']=baseline;result['sample']=sample
     stamp=str(time.time_ns());receipt=N/('TIER_60_120_INTENT_'+stamp+'.json')
     policy=dict(schema='LANE_T2_ACTIVE_TRANSFER_RATE_TIER_V1',source_MiB_per_second=60,total_MiB_per_second=120,authorization_sha256=c.RATE_AUTH_SHA256,tier_receipt=str(receipt))
     result['new_policy']=policy;a.put(receipt,c.canon(result));a.put(T/'control'/receipt.name,c.canon(result))
     p=T/'control/TRANSFER_RATE_POLICY.json';tmp=p.with_name(p.name+'.tier-writing')
     assert load(p)['source_MiB_per_second']==30
     with tmp.open('xb') as f:f.write(c.canon(policy));f.flush();os.fsync(f.fileno())
     os.replace(tmp,p);fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY)
     try:os.fsync(fd)
     finally:os.close(fd)
     assert c.rate_limits(force=True)['source_MiB_per_second']==60
     a.put(N/('TIER_60_120_DONE_'+stamp+'.json'),c.canon(dict(unix=time.time(),policy=policy,policy_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),intent=str(receipt),executors_restarted=0)))
finally:guard.close()
print(json.dumps(result))
'''

if __name__=='__main__':
    x=remote('hrl-174-new',CODE,90);save('t2/rate_transition/LATEST_TIER_OBSERVATION.json',x)
    print(json.dumps({k:v for k,v in x.items() if k not in ['resources','baseline','sample']}))
