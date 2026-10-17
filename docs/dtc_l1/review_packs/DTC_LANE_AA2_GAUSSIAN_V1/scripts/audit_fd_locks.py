"""Supplement /proc/locks with actual per-process fdinfo lock witnesses."""
from common import *


def main():
    admission=json.loads((PACK/'CURRENT_EXECUTION_ADMISSION.json').read_text())
    identities={}
    for observation in admission['observations']:
        for role in ['foreign_DTC_authorities','other_DTC_helpers_requiring_review']:
            for p in observation[role]:identities[p['pid']]=p['start_ticks']
    witnesses=[]
    for pid,ticks in sorted(identities.items()):
        before=proc(pid)
        if not before or before['start_ticks']!=ticks:continue
        for info in sorted((Path('/proc')/str(pid)/'fdinfo').glob('*')):
            try:
                text=info.read_text()
                locks=[line for line in text.splitlines() if line.startswith('lock:')]
                if not locks:continue
                fd=Path('/proc')/str(pid)/'fd'/info.name
                target=os.readlink(fd);stat=fd.stat()
                witnesses.append(dict(pid=pid,start_ticks=ticks,fd=info.name,fd_target=target,
                      fdinfo=text,device=stat.st_dev,inode=stat.st_ino,
                      lock_lines=locks,fdinfo_sha256=hashlib.sha256(text.encode()).hexdigest()))
            except (FileNotFoundError,ProcessLookupError):continue
        after=proc(pid)
        assert after and after['start_ticks']==ticks,'Process incarnation changed during lock observation'
    write(PACK/'LOCK_FDINFO_SUPPLEMENT.json',dict(utc=now(),status='HOLD_OBSERVED_FOREIGN_DTC_FD_LOCKS' if witnesses else 'NO_FD_LOCK_WITNESS_FOR_CHECKED_IDENTITIES',
          checked_process_incarnations=[dict(pid=p,start_ticks=t) for p,t in sorted(identities.items())],
          actual_fdinfo_lock_witnesses=witnesses,
          no_foreign_DTC_fd_locks=len(witnesses)==0,
          proc_locks_only_is_not_sufficient_absence_proof=True,
          original_proc_locks_observation_preserved=True,locks_acquired_by_AA2=False,
          note='A live fdinfo FLOCK may show owner0 and be absent from global /proc/locks. Do not turn global absence into release PASS.'))
    print('fdinfo lock witnesses:',len(witnesses))


if __name__=='__main__':main()
