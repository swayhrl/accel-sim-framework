"""Finite success-path closure after the existing execution chain exits.

This observer never starts/stops/signals Driver, Supervisor, Publisher or
science. It finalizes only 115/115 COMMITTED. Any other terminal state leaves
a review receipt and exits without claiming completion.
"""
from local_common import *
import ctypes,datetime,urllib.request,urllib.parse,traceback

BRANCH='hrl/ops-original174-verified-offload-reclaim-exec-20261024-v1'
MUTEX='Local\\LaneT2Frozen115BackgroundFinalizer20261025'
LOG=P/'background_finalizer.log'

REMOTE=r'''
import pathlib,json,time
T=pathlib.Path('/root/data/research_asset_verified_offload_20261024_v1')
s=json.loads((T/'control/STATE.json').read_bytes());sup=json.loads((T/'control/CONTINUATION_SUPERVISOR.json').read_bytes());rows=[json.loads(z) for z in (T/'control/LEDGER.jsonl').read_text().splitlines()]
done={z['asset_id']:z for z in rows if z['status']=='ARCHIVED_CONTENT_VERIFIED'}
def live(pid,ticks,script):
 p=pathlib.Path('/proc',str(pid))
 try:return int((p/'stat').read_text().rsplit(')',1)[1].split()[19])==ticks and str(T/'tools'/script).encode() in (p/'cmdline').read_bytes().split(b'\0')
 except OSError:return False
print(json.dumps(dict(unix=time.time(),completed=len(done),state=s,driver_live=live(s['driver_pid'],s['driver_start_ticks'],'offload_driver.py'),supervisor=sup,supervisor_live=live(sup['pid'],sup['start_ticks'],'continuation_supervisor.py'))))
'''

def log(event,**kw):
    row=dict(event=event,unix=time.time(),local=datetime.datetime.now().astimezone().isoformat(),**kw)
    with LOG.open('ab') as f:f.write((json.dumps(row,separators=(',',':'))+'\n').encode());f.flush();os.fsync(f.fileno())

def publishers():
    command="Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python' -and $_.CommandLine -like '*original174-verified-offload-reclaim-exec-20261024-v1*publish_continuation.py*' } | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"
    r=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,timeout=30)
    if r.returncode:raise RuntimeError(r.stderr[-2000:])
    if not r.stdout.strip():return []
    x=json.loads(r.stdout);return [x] if isinstance(x,dict) else x

def run_tool(name,*args,timeout=600):
    command=[sys.executable,'-B',str(R/'tools'/name),*args]
    r=subprocess.run(command,cwd=W,capture_output=True,text=True,timeout=timeout)
    log('FINAL_TOOL',tool=name,args=args,returncode=r.returncode,stdout=r.stdout[-2000:],stderr=r.stderr[-2000:])
    if r.returncode:raise RuntimeError(name+' failed: '+r.stderr[-3000:]+r.stdout[-3000:])
    return r.stdout

def raw(commit,relative):
    url='https://raw.githubusercontent.com/swayhrl/accel-sim-framework/'+urllib.parse.quote(commit,safe='')+'/'+urllib.parse.quote(relative,safe='/')
    with urllib.request.urlopen(url,timeout=90) as response:return response.read()

def publish_once():
    out=run_tool('publish_continuation.py','--once',timeout=600)
    lines=[json.loads(z) for z in out.splitlines() if z.startswith('{')]
    result=lines[-1];assert result['status']=='COMPLETE' and result['committed']==115
    return result['commit']

def put_true164(value):
    b=(json.dumps(value,sort_keys=True,indent=2)+'\n').encode();encoded=base64.b64encode(b).decode()
    code="import pathlib,base64,json,os\np=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/finalization/FINAL_GITHUB_PUBLICATION_AND_READBACK.json');p.parent.mkdir(exist_ok=True);b=base64.b64decode("+repr(encoded)+")\nassert not p.exists() or p.read_bytes()==b\nif not p.exists():\n f=p.open('xb');f.write(b);f.flush();os.fsync(f.fileno());f.close()\nassert p.read_bytes()==b\nprint(json.dumps({'path':str(p),'bytes':len(b)}))"
    return remote('hrl-174-new',code,90)

def main():
    kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.CreateMutexW.argtypes=[ctypes.c_void_p,ctypes.c_bool,ctypes.c_wchar_p];kernel.CreateMutexW.restype=ctypes.c_void_p
    handle=kernel.CreateMutexW(None,True,MUTEX)
    if not handle:raise ctypes.WinError(ctypes.get_last_error())
    if ctypes.get_last_error()==183:raise RuntimeError('EXISTING_BACKGROUND_FINALIZER_NO_SECOND_INSTANCE')
    initial=remote('hrl-174-new',REMOTE,90);deadline=initial['supervisor']['deadline_unix']+900
    log('FINALIZER_STARTED',pid=os.getpid(),original_supervisor_deadline=initial['supervisor']['deadline_unix'],own_deadline=deadline,signals_authorized_or_sent=0)
    while time.time()<deadline:
        try:x=remote('hrl-174-new',REMOTE,90)
        except Exception as e:log('OBSERVATION_RETRY',error=repr(e));time.sleep(120);continue
        if x['completed']==115:
            if x['driver_live'] or x['supervisor_live'] or publishers():time.sleep(30);continue
            break
        if not x['driver_live'] and not x['supervisor_live']:
            log('REVIEW_REQUIRED_NOT_ALL_COMMITTED',completed=x['completed'],state=x['state'],supervisor=x['supervisor']);return
        time.sleep(120)
    else:log('FINALIZER_BOUND_REACHED_NO_COMPLETION',last=remote('hrl-174-new',REMOTE,90));return
    assert not publishers(),'Publisher reappeared before final audit'
    run_tool('t2_closure_audit.py',timeout=600)
    run_tool('audit_restore_dependencies.py',timeout=900)
    run_tool('t2_runtime_audit.py','--final',timeout=900)
    run_tool('t2_report.py','--final','--pre-publication',timeout=600)
    closure_commit=publish_once()
    files=[
      'docs/ep_l2/operations/original174_verified_offload_reclaim_20261024_v1/t2/CONTENT_AND_RESTORE_CLOSURE.json',
      'docs/ep_l2/operations/original174_verified_offload_reclaim_20261024_v1/t2/FINAL_REPORT.md',
      'docs/ep_l2/operations/original174_verified_offload_reclaim_20261024_v1/t2/REQUIREMENT_CLOSURE_AUDIT.json',
      'docs/ep_l2/operations/original174_verified_offload_reclaim_20261024_v1/t2/FROZEN115_FINAL_STATE_TABLE.csv',
      'docs/ep_l2/operations/original174_verified_offload_reclaim_20261024_v1/LIVE_CONTINUATION_STATUS.json']
    checks=[]
    for relative in files:
        local=W/relative;body=raw(closure_commit,relative);checks.append(dict(path=relative,sha256=hashlib.sha256(body).hexdigest(),bytes=len(body),exact_bytes_match=body==local.read_bytes()))
    receipt=dict(schema='LANE_T2_FINAL_GITHUB_REMOTE_READBACK_V1',status='PASS' if all(z['exact_bytes_match'] for z in checks) else 'FAIL',unix=time.time(),closure_commit=closure_commit,branch=BRANCH,files=checks,all_exact_bytes_match=all(z['exact_bytes_match'] for z in checks),read_method='Independent raw.githubusercontent.com HTTPS by immutable commit')
    save('t2/FINAL_GITHUB_REMOTE_READBACK.json',receipt);assert receipt['status']=='PASS'
    run_tool('t2_report.py','--final',timeout=600)
    receipt_commit=publish_once()
    observed=git('ls-remote','origin','refs/heads/'+BRANCH).decode().split()[0];assert observed==receipt_commit
    relative='docs/ep_l2/operations/original174_verified_offload_reclaim_20261024_v1/t2/FINAL_GITHUB_REMOTE_READBACK.json';remote_receipt=raw(receipt_commit,relative);assert remote_receipt==(W/relative).read_bytes()
    final=dict(schema='LANE_T2_FINAL_GITHUB_PUBLICATION_AND_READBACK_V1',status='PASS',unix=time.time(),closure_commit=closure_commit,receipt_commit=receipt_commit,remote_branch_head=observed,remote_receipt_sha256=hashlib.sha256(remote_receipt).hexdigest(),remote_receipt_exact_bytes_match=True,all115_committed=True,driver_supervisor_publisher_naturally_stopped=True,signals_sent=0,true164_receipt='control/finalization/FINAL_GITHUB_PUBLICATION_AND_READBACK.json')
    where=put_true164(final);log('FINALIZER_COMPLETE',result=final,true164=where)

if __name__=='__main__':
    try:main()
    except BaseException as e:log('FINALIZER_EXCEPTION_REVIEW_REQUIRED',error=repr(e),traceback=traceback.format_exc());raise
