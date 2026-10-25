"""One read-only pidfd wait and bounded rate-transition handoff snapshot."""
from local_common import *
import argparse

CODE=r'''
import pathlib,sys,os,json,time,select,hashlib
P=pathlib.Path;T=P('/root/data/research_asset_verified_offload_20261024_v1');s=json.loads((T/'control/STATE.json').read_bytes());sup=json.loads((T/'control/CONTINUATION_SUPERVISOR.json').read_bytes())
def proc(pid,ticks,script):
 p=P('/proc',str(pid))
 try:
  raw=(p/'stat').read_text().rsplit(')',1)[1].split();valid=int(raw[19])==ticks and str(T/'tools'/script).encode() in (p/'cmdline').read_bytes().split(b'\0')
  return dict(pid=pid,start_ticks=ticks,alive=valid,process_state=raw[0],wait_channel=(p/'wchan').read_text())
 except OSError:return dict(pid=pid,start_ticks=ticks,alive=False)
intent_path=T/'control/RATE_POLICY_TRANSITION_INTENT.json';intent=json.loads(intent_path.read_bytes()) if intent_path.exists() else {}
pid=intent.get('coordinator_pid');ticks=intent.get('coordinator_start_ticks');coordinator=proc(pid,ticks,'apply_staged_transfer_rates.py') if pid else None
if SECONDS and coordinator and coordinator['alive']:
 fd=os.pidfd_open(pid)
 try:select.select([fd],[],[],SECONDS)
 finally:os.close(fd)
s=json.loads((T/'control/STATE.json').read_bytes());sup=json.loads((T/'control/CONTINUATION_SUPERVISOR.json').read_bytes())
rows=[json.loads(z) for z in (T/'control/LEDGER.jsonl').read_text().splitlines()];done={x['asset_id']:x for x in rows if x['status']=='ARCHIVED_CONTENT_VERIFIED'}
controls={}
for name in ['RATE_POLICY_TRANSITION_INTENT.json','RATE_POLICY_POST_COMMIT_LOCK_BOUNDARY.json','RATE_POLICY_TRANSITION_DONE.json','TRANSFER_RATE_POLICY.json','TIER_30_60_INTENT.json']:
 p=T/'control'/name
 if p.exists():controls[name]=json.loads(p.read_bytes())
for p in (T/'control').glob('RATE_POLICY_TRANSITION_FAILURE_*.json'):controls[p.name]=json.loads(p.read_bytes())
N=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets');b=N/s['asset_id'];writing=[dict(relative_path=p.relative_to(b).as_posix(),size=p.stat().st_size) for p in (b/'tree').rglob('*.writing')]
x=dict(schema='LANE_T2_RATE_TRANSITION_LIVE_OBSERVATION_V1',unix=time.time(),completed=len(done),pending=115-len(done),committed_original_bytes=sum(z['original_bytes'] for z in done.values()),driver=proc(s['driver_pid'],s['driver_start_ticks'],'offload_driver.py'),supervisor=proc(sup['pid'],sup['start_ticks'],'continuation_supervisor.py'),coordinator=proc(pid,ticks,'apply_staged_transfer_rates.py') if pid else None,state=s,supervisor_state=sup,active_tree_writing=writing,controls=controls,coordinator_log_tail=(T/'control/rate_policy_transition.log').read_text()[-1000:])
print(json.dumps(x))
'''

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=int,default=0);args=ap.parse_args();assert 0<=args.seconds<=55
    x=remote('hrl-174-new','SECONDS='+str(args.seconds)+'\n'+CODE,args.seconds+35)
    save('t2/rate_transition/CURRENT_RECOVERY_STATUS.json',x)
    for name,value in x['controls'].items():save('t2/rate_transition/'+name,value)
    print(json.dumps({k:x[k] for k in ['unix','completed','pending','driver','supervisor','coordinator','active_tree_writing','coordinator_log_tail']}))
    print(json.dumps(dict(asset=x['state']['asset_id'],phase=x['state']['phase'],rates=x['state'].get('archive_transfer_rate_policy'),control_receipts=list(x['controls']))))
