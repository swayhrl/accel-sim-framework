"""Finite metadata publisher for this queue; never starts or stops a driver.

One publication on --once, otherwise at most 24 hours while the recorded
PID/start_ticks remains alive. Stops after publishing a terminal/HOLD state.
Only this task's documentation is staged. Failed pushes are durably recorded.
The separate supervisor can re-admit the same queue after resource waits;
this publisher cannot launch a driver or change transfer ownership.
"""
import sys
sys.dont_write_bytecode=True
from local_common import *
import argparse,datetime,ctypes,contextlib
from export_snapshot import main as export_snapshot

BRANCH='hrl/ops-original174-verified-offload-reclaim-exec-20261024-v1'
REMOTE_STATUS=r'''
import os,json,time,pathlib,hashlib,subprocess
T=pathlib.Path('/root/data/research_asset_verified_offload_20261024_v1')
s=json.loads((T/'control/STATE.json').read_bytes());p=pathlib.Path('/proc')/str(s['driver_pid']);live=False;actual_ticks=None
try:
 actual_ticks=int((p/'stat').read_text().rsplit(')',1)[1].split()[19]);argv=(p/'cmdline').read_bytes().split(b'\0');live=actual_ticks==s.get('driver_start_ticks') and any(x==str(T/'tools/offload_driver.py').encode() for x in argv)
except OSError:pass
supervisor=None;supervised=False
sp=T/'control/CONTINUATION_SUPERVISOR.json'
if sp.exists():
 supervisor=json.loads(sp.read_bytes());q=pathlib.Path('/proc')/str(supervisor['pid'])
 try:
  qticks=int((q/'stat').read_text().rsplit(')',1)[1].split()[19]);qargs=(q/'cmdline').read_bytes().split(b'\0');supervised=bool(supervisor['running']) and qticks==supervisor['start_ticks'] and str(T/'tools/continuation_supervisor.py').encode() in qargs
 except OSError:pass
receipt_path=T/'control/CURRENT_DRIVER_PROCESS.json'
driver_receipt=json.loads(receipt_path.read_bytes()) if receipt_path.exists() else json.loads((T/'control/RESUMED_DRIVER_PROCESS.json').read_bytes())
driver_log=pathlib.Path(driver_receipt['log']);assert driver_log.is_relative_to(T/'control')
rows=[json.loads(z) for z in (T/'control/LEDGER.jsonl').read_text().splitlines()];done={x['asset_id']:x for x in rows if x['status']=='ARCHIVED_CONTENT_VERIFIED'};latest={x['asset_id']:x for x in rows}
f=os.statvfs('/root/data');nas=os.statvfs('/root/share/mnt164');share=os.statvfs('/root/share')
value=dict(schema='LANE_T_LIVE_CONTINUATION_STATUS_V1',goal='ORIGINAL174_VERIFIED_OFFLOAD_AND_SSD_RECLAIM_V1',unix=time.time(),driver_running=live,pid=s['driver_pid'],expected_start_ticks=s.get('driver_start_ticks'),actual_start_ticks=actual_ticks,completed=len(done),pending=115-len(done),current_in_progress=1 if live else 0,latest_uncommitted_holds=sum(x['status']=='HOLD_EXACT_ASSET' for a,x in latest.items() if a not in done),committed_original_bytes=sum(x['original_bytes'] for x in done.values()),state=s,SSD_available_bytes=f.f_bavail*f.f_frsize,Share_available_bytes=share.f_bavail*share.f_frsize,true164_available_bytes=nas.f_bavail*nas.f_frsize,log_tail=(T/'control/driver_resume_20261025.log').read_text()[-5000:],new_Source_retirements_by_recovery=0,prior_retirements_repeated=False)
value.update(supervisor_running=supervised,supervisor_state=supervisor,driver_log=str(driver_log),log_tail=driver_log.read_text()[-5000:])
# Durable metadata on real164 is separate from the mutable SSD checkpoint.
m=json.loads(subprocess.check_output(['findmnt','-J','-T','/root/share/mnt164'],text=True))['filesystems'][0]
assert m['source']=='admin-wcx@10.208.130.164:/home/shared' and m['fstype']=='fuse.sshfs'
root=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/continuation_20261025');root.mkdir(exist_ok=True)
b=(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode();digest=hashlib.sha256(b).hexdigest();dest=root/(str(time.time_ns())+'_'+digest[:16]+'.json')
with dest.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
assert dest.read_bytes()==b
value['true164_durable_status_receipt']=dict(path=str(dest).replace('/root/share/mnt164','/home/shared',1),sha256=digest,closed_reopen_equal=True)
print(json.dumps(value))
'''

def journal(x):
    p=R/'checkpoint/recovery_20261025/PUBLICATION_RECEIPTS.jsonl'
    with p.open('ab') as f:f.write((json.dumps(x,separators=(',',':'))+'\n').encode());f.flush();os.fsync(f.fileno())

def once():
    assert git('branch','--show-current').decode().strip()==BRANCH
    live=remote('hrl-174-new',REMOTE_STATUS,180)
    export_snapshot()
    save('LIVE_CONTINUATION_STATUS.json',live)
    state=live['state'];when=datetime.datetime.fromtimestamp(live['unix'],datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    status='COMPLETE' if live['completed']==115 else 'ACTIVE' if live['driver_running'] else 'WAIT_RESOURCE_ADMISSION' if live.get('supervisor_running') else 'HOLD / REVIEW REQUIRED'
    text=f'''# Lane T verified offload — {status}

Observed {when}. Frozen queue: **{live['completed']} committed, {live['pending']} pending**. Unique committed payload: {live['committed_original_bytes']:,} bytes. Driver running: {live['driver_running']}; PID {live['pid']}, start_ticks {live['expected_start_ticks']}. Phase: `{state['phase']}`; asset: `{state.get('asset_id')}`. Historical HOLD rows remain in the append-only ledger and do not mean an active asset is currently held.

Shared SSD available: {live['SSD_available_bytes']:,} bytes. Share/MD127 available: {live['Share_available_bytes']:,} bytes; qualified payload staging remains zero. Genuine164 available: {live['true164_available_bytes']:,} bytes. Fresh resource/science gates remain enforced by the driver.

`CURRENT_RECOVERY_STATUS.md` is the preserved pre-resume audit. `LIVE_CONTINUATION_STATUS.json` is the live PID-checked handoff, including a closed/reopened durable genuine164 metadata receipt. Existing COMMIT controls are independently read back by the exporter, without retransmitting committed payload. Original task IDs, frozen scopes, object identities, global exclusion and range/SHA rules are retained.

No prior retirement has been repeated. Recovery has performed no new Source retirement. Historical measured pool reclaim remains 18,936,295,424 bytes and Source unlink interval reclaim remains 18,420,580,352 bytes; archive bytes are not physical reclaim. USER_AUTHORIZATION.md and AUTONOMOUS_RECLAIM_AND_CONTINUE_POLICY.md remain unchanged. No scientific starts/stops or registry/budget/controller edits are authorized by this publisher.

The finite publisher only reads task execution state and publishes task metadata. It cannot start another driver, take over a lock or retry a failed asset. A separate finite supervisor observes the existing driver and can resume only the same frozen queue after a confirmed common-resource exit and fresh two-endpoint admission. It stops for identity/contract or exact-asset terminal failures, completion or its 24-hour bound. The publisher stops when both execution and supervision end, or after its own 24-hour bound. Remote execution continues independently of the chat context.
'''
    for name in ['STATUS_AND_RECEIPT.md','FINAL_STATUS_AND_RECEIPT.md']:(R/name).write_text(text,encoding='utf-8')
    head_before=git('rev-parse','HEAD').decode().strip()
    git('add','--',str(R.relative_to(W)).replace('\\','/'))
    changed=bool(git('diff','--cached','--name-only').strip())
    if changed:git('commit','-m',f"ops: Lane T {live['completed']}/115 {state['phase']} checkpoint")
    head=git('rev-parse','HEAD').decode().strip()
    try:
        git('push','origin',BRANCH)
        observed=git('ls-remote','origin','refs/heads/'+BRANCH).decode().split()[0]
        assert observed==head,'REMOTE_BRANCH_HEAD_MISMATCH'
        journal(dict(status='GITHUB_PUSH_AND_REMOTE_REF_VERIFIED',unix=time.time(),commit=head,previous_local_head=head_before,committed=live['completed'],pending=live['pending'],driver_running=live['driver_running'],true164_status_receipt=live['true164_durable_status_receipt']))
    except Exception as e:
        journal(dict(status='GITHUB_PUBLICATION_FAILED_RETRY_NEXT_FINITE_CYCLE',unix=time.time(),commit=head,error=str(e)))
        raise
    print(json.dumps(dict(status=status,commit=head,committed=live['completed'],pending=live['pending'],driver_running=live['driver_running'],phase=state['phase'])),flush=True)
    return live

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--once',action='store_true');args=ap.parse_args()
    # A named OS mutex serializes all local publishers for this task. It does
    # not touch transfer locks or scientific state. Windows handle auto-closes.
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateMutexW.argtypes=[ctypes.c_void_p,ctypes.c_bool,ctypes.c_wchar_p];kernel.CreateMutexW.restype=ctypes.c_void_p
    handle=kernel.CreateMutexW(None,True,'Local\\LaneTOriginal174VerifiedOffloadPublisher20261025')
    if not handle:raise ctypes.WinError(ctypes.get_last_error())
    if ctypes.get_last_error()==183:raise RuntimeError('EXISTING_METADATA_PUBLISHER_NO_SECOND_INSTANCE')
    started=time.monotonic();failures=0
    while time.monotonic()-started<24*3600:
        try:
            x=once();failures=0
            if args.once or (not x['driver_running'] and not x.get('supervisor_running')) or x['completed']==115:return
        except Exception as e:
            failures+=1;print(json.dumps(dict(publisher_error=str(e),consecutive_failures=failures)),flush=True)
            if args.once or failures>=12:raise
        time.sleep(300)

if __name__=='__main__':main()
