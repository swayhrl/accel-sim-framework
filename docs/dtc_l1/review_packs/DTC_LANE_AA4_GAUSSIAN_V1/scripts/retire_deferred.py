"""Audit exact historical deferred authority and, only on explicit --retire, one pidfd SIGTERM."""
from common import *
import signal,sys
PID=3291777;TICKS=550530984
OLD=Path('/workspace/worktrees/accel-sim-decoupled-l1-fast64')
SCRIPT=OLD/'util/dtc_l1/deferred_fast64_1_telemetry_rerun.sh'
EXPECTED='1872d0f98a53d9ffacf1f221ab6f1ef3406fd7041dba1238cdf7e93c3ff10cbf'

def process_snapshot():
    s=snapshot()
    for p in s['processes']:
        try:
            q=Path('/proc')/str(p['pid']);st=(q/'stat').read_text().rsplit(')',1)[1].split();p.update(ppid=int(st[1]),pgrp=int(st[2]),session=int(st[3]),cwd=os.readlink(q/'cwd'),exe=os.readlink(q/'exe'))
        except OSError:p['racy_read']=True
    return s

def flock_records(s):
    records=[]
    for p in s['processes']:
        for f in (Path('/proc')/str(p['pid'])/'fdinfo').glob('*'):
            try:
                info=f.read_text()
                if '\nlock:' not in info:continue
                target=os.readlink(f.parent.parent/'fd'/f.name)
                if any(x in target.lower() for x in ['dtc','fast64','lane']):records.append(dict(pid=p['pid'],start_ticks=p['start_ticks'],fd=f.name,path=target,fdinfo=info))
            except OSError:pass
    return records

def evidence(p):
    if not p.exists():return dict(path=str(p),exists=False)
    return dict(path=str(p),exists=True,bytes=p.stat().st_size,sha256=sha(p),tail=p.read_bytes()[-8192:].decode(errors='replace'))

def audit():
    s=process_snapshot();ps={p['pid']:p for p in s['processes']};target=ps.get(PID)
    descendants=[];todo=[PID]
    while todo:
        n=todo.pop()
        for p in ps.values():
            if p.get('ppid')==n:descendants.append(p);todo.append(p['pid'])
    script=SCRIPT.read_text();old=re.search(r'old_rows=\((.*?)\)',script,re.S).group(1).split();new=[r.split('|')[0] for r in re.findall(r"'([^']+)'",re.search(r'new_rows=\((.*?)\)',script,re.S).group(1))]
    rows=[]
    for oldrow,newrow in zip(old,new):
        root=Path('/workspace/fast64-runs');before=root/oldrow;future=root/newrow
        rows.append(dict(original=oldrow,future=newrow,old_manifest=evidence(before/'RUN_MANIFEST.tsv'),old_terminal=evidence(before/'RUN_TERMINAL.tsv'),future_exists=future.exists(),future_manifest=evidence(future/'RUN_MANIFEST.tsv'),future_terminal=evidence(future/'RUN_TERMINAL.tsv'),launch=evidence(root/(newrow+'.launcher.log')),supervisor=evidence(root/(newrow+'.supervisor.tsv'))))
    # Actual command arguments, not strings embedded in an unrelated shell -c.
    related=[];sim=[]
    for p in s['processes']:
        args=p['argv'];actual=[a for a in args if '\n' not in a and len(a)<4096]
        if p['pid']!=PID and any(any(str(Path('/workspace/fast64-runs')/n) in a for n in new) for a in actual):related.append(p)
        if 'accel-sim.out' in p.get('exe','') or any(Path(a).name=='accel-sim.out' for a in actual):sim.append(p)
    info=[]
    if target:
        for f in sorted((Path('/proc')/str(PID)/'fdinfo').glob('*')):
            try:info.append(dict(fd=f.name,fdinfo=f.read_text(),path=os.readlink(f.parent.parent/'fd'/f.name)))
            except OSError:pass
    fdscript=Path('/proc')/str(PID)/'fd/255'
    openedsha=sha(fdscript) if fdscript.exists() else 'UNAVAILABLE'
    locklist=flock_records(s);core41='/workspace/fast64-primary-r4/.fast64_4_2d_core41_autodispatch_v1.lock'
    checks=dict(exact_PID_start=bool(target and target['start_ticks']==TICKS),exact_argv=bool(target and target['argv']==['bash',str(SCRIPT)]),cwd=bool(target and target.get('cwd')=='/workspace'),parent=bool(target and target.get('ppid')==1),disk_and_open_script=sha(SCRIPT)==openedsha==EXPECTED,only_wait_timer_children=all(p['argv']==['sleep','60'] for p in descendants),no_related_live_targets=not related,no_nonexternal_simulators=all(p.get('exe','').startswith('/workspace/ep_l2_potential20261017_lane5_results/') for p in sim),old_core41_watcher_absent=proc(1425986) is None,old_core41_FLOCK_released=not any(r['path']==core41 for r in locklist))
    policy=blob(FW_REPO,'dab43027467d577291aabd6a5d2812d601219188','docs/dtc_l1/review_packs/DTC_LANE_AA3_GAUSSIAN_V1/inputs/old_controls/FAST64_1_R1_EXECUTION_PATH_CONTAMINATION.md')
    checks['scientific_R1_superseded']='SUPERSEDED_NONFORMAL' in policy.decode()
    checks['no_foreign_signal_or_data_change_needed']=all(p['argv']==['sleep','60'] for p in descendants) and not related
    record=dict(utc=now(),target=target,descendants=descendants,target_fdinfo=info,opened_script_sha256=openedsha,script_path=str(SCRIPT),script_sha256=sha(SCRIPT),rows=rows,related_live_target_processes=related,all_visible_simulators=sim,DTC_FLOCK_records=locklist,checks=checks,eligible=all(checks.values()),A='exact PID/start/argv/cwd/disk and fd255 source match',B='only sleep timer; no active future-row simulator/runner/monitor/archive/closeout or related target arguments',C='AA4 user explicitly prohibits restoring superseded R1; frozen AA3 policy records all R1 nonformal, preserved collectors do not depend on deferred parent',D='single pidfd parent only; timers natural; other projects, old data and locks untouched',old_policy_sha256=hashlib.sha256(policy).hexdigest(),signal_sent=False)
    write(PACK/'DEFERRED_PRE_RETIREMENT_AUDIT.json',record);write(ROOT/'DEFERRED_PRE_RETIREMENT_SNAPSHOT.json',s)
    return record

def main():
    r=audit();print(json.dumps(dict(checks=r['checks'],eligible=r['eligible']),indent=2),flush=True)
    if '--retire' not in sys.argv:return
    if not r['eligible']:raise SystemExit('SCIENCE_STOP_A_D_NOT_PROVEN; no signal')
    fd=os.pidfd_open(PID)
    p=proc(PID);assert p and p['start_ticks']==TICKS and p['argv']==['bash',str(SCRIPT)]
    assert sha(SCRIPT)==sha(Path('/proc')/str(PID)/'fd/255')==EXPECTED
    ids=(Path('/proc')/str(PID)/f'task/{PID}/children').read_text().split()
    timers=[proc(int(i)) for i in ids];assert all(p and p['argv']==['sleep','60'] for p in timers)
    write(ROOT/'DEFERRED_SIGTERM_RECEIPT.json',dict(utc=now(),pid=PID,start_ticks=TICKS,signal='SIGTERM',pidfd_bound=True,maximum_signals=1,parent_only=True,timers_not_signaled=timers,old_files_deleted=False))
    signal.pidfd_send_signal(fd,signal.SIGTERM);os.close(fd)
    deadline=time.monotonic()+180
    while time.monotonic()<deadline:
        p=proc(PID);remaining=[proc(t['pid']) for t in timers];remaining=[p for p in remaining if p and p['state']!='Z']
        if (p is None or p['state']=='Z') and not remaining:break
        time.sleep(1)
    s=process_snapshot();locks=flock_records(s)
    checks=dict(parent_incarnation_ended=proc(PID) is None or proc(PID)['state']=='Z',timer_children_naturally_ended=not remaining,no_retired_PID_lock=not any(l['pid']==PID for l in locks),old_Core41_FLOCK_released=not any(l['path']=='/workspace/fast64-primary-r4/.fast64_4_2d_core41_autodispatch_v1.lock' for l in locks))
    write(PACK/'WATCHER_RETIREMENT_RECEIPT.json',dict(utc=now(),status='PASS_RETIRED_PARENT_ONLY' if all(checks.values()) else 'STOP_RELEASE_UNPROVEN',checks=checks,pid=PID,start_ticks=TICKS,one_pidfd_SIGTERM=True,other_signals_sent=False,all_remaining_DTC_FLOCKs=locks,old_Core41_lock_file_preserved=Path('/workspace/fast64-primary-r4/.fast64_4_2d_core41_autodispatch_v1.lock').exists(),raw_signal_receipt_sha256=sha(ROOT/'DEFERRED_SIGTERM_RECEIPT.json')))
    write(ROOT/'POST_RETIREMENT_SNAPSHOT.json',s)
    assert all(checks.values())
    print('PASS: exact deferred parent retired; timers natural; old Core41 FLOCK remains released.')

if __name__=='__main__':main()
