"""One-shot event wait for the verified current driver/COMMIT, no polling loop."""
import sys
sys.dont_write_bytecode=True
from local_common import *
import argparse

CODE=r'''
import pathlib,json,os,time,ctypes,select,hashlib,gzip
P=pathlib.Path;T=P('/root/data/research_asset_verified_offload_20261024_v1');s=json.loads((T/'control/STATE.json').read_bytes());pid=s['driver_pid'];ticks=s['driver_start_ticks'];proc=P('/proc',str(pid));role='driver';script=T/'tools/offload_driver.py'
def live(pid,ticks,script):
 p=P('/proc',str(pid))
 try:return int((p/'stat').read_text().rsplit(')',1)[1].split()[19])==ticks and str(script).encode() in (p/'cmdline').read_bytes().split(b'\0')
 except FileNotFoundError:return False
if not live(pid,ticks,script):
 sup=json.loads((T/'control/CONTINUATION_SUPERVISOR.json').read_bytes());pid=sup['pid'];ticks=sup['start_ticks'];script=T/'tools/continuation_supervisor.py';proc=P('/proc',str(pid));role='supervisor'
assert live(pid,ticks,script),'NO_VERIFIED_LIVE_EXECUTION_OR_SUPERVISOR_HANDLE; inspect terminal state instead of restarting'
aid=s['asset_id'];q=json.loads(gzip.decompress((T/'control/FROZEN_SCOPES.json.gz').read_bytes()))['scopes'];assert aid in {x['asset_id'] for x in q}
N=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets');b=N/aid;started=time.monotonic();lib=ctypes.CDLL(None,use_errno=True)
lib.inotify_init1.argtypes=[ctypes.c_int];lib.inotify_init1.restype=ctypes.c_int;lib.inotify_add_watch.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32];lib.inotify_add_watch.restype=ctypes.c_int
fd=lib.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC);assert fd>=0,ctypes.get_errno();pidfd=os.pidfd_open(pid);events=[]
try:
 watch=T/'control' if role=='supervisor' else b if b.exists() else N
 assert lib.inotify_add_watch(fd,os.fsencode(watch),0x00000100|0x00000080|0x00000008)>=0,ctypes.get_errno()
 if not (b/'COMMIT.json').exists():
  ready,_,_=select.select([fd,pidfd],[],[],SECONDS)
  if fd in ready:events.append('FILESYSTEM_EVENT')
  if pidfd in ready:events.append('VERIFIED_DRIVER_EXIT_EVENT')
 current=json.loads((T/'control/STATE.json').read_bytes());alive=live(pid,ticks,script)
 commit=b/'COMMIT.json';visible=commit.exists()
 status='COMMIT_VISIBLE_RECHECK_LEDGER_FOR_FINALIZATION' if visible else 'VERIFIED_RESOURCE_WAIT_SUPERVISOR_LIVE' if role=='supervisor' and alive else 'VERIFIED_WAIT_SAME_DRIVER_LIVE' if alive else 'VERIFIED_PROCESS_EXIT_RECHECK_FINAL_STATE'
 driver_live=live(current['driver_pid'],current['driver_start_ticks'],T/'tools/offload_driver.py')
 if role=='supervisor' and driver_live:status='ORIGINAL_SUPERVISOR_AUTOMATICALLY_RESUMED_SAME_QUEUE'
 print(json.dumps(dict(status=status,unix=time.time(),waited_seconds=time.monotonic()-started,events=events,observed_role=role,pid=pid,start_ticks=ticks,observed_process_alive=alive,current_driver_alive=driver_live,observed_asset=aid,current_asset=current.get('asset_id'),current_phase=current['phase'],completed=current['completed_assets'],held_this_pass=current['held_assets'],current_new_transferred_bytes=current['current_asset_new_transferred_bytes'],COMMIT_visible=visible,COMMIT_sha256=hashlib.sha256(commit.read_bytes()).hexdigest() if visible else None,new_execution_or_supervision_processes_started=0,observer_is_one_shot_read_only_metadata_process=True,locks_or_data_modified=False)))
finally:os.close(fd);os.close(pidfd)
'''

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=int,default=50);args=ap.parse_args();assert 1<=args.seconds<=55
    x=remote('hrl-174-new','SECONDS='+str(args.seconds)+'\n'+CODE,args.seconds+30)
    save('t2/LAST_VERIFIED_EVENT_WAIT.json',x);print(json.dumps(x))

if __name__=='__main__':main()
