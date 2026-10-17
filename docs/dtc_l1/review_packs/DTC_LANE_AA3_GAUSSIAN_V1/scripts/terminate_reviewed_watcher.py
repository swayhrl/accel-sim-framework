import os,sys,json,signal,time
from pathlib import Path
sys.path.insert(0,'/workspace/worktrees/accel-sim-iscas2027-dtc-lane-aa2-gaussian-factorial-174-v1/docs/dtc_l1/review_packs/DTC_LANE_AA2_GAUSSIAN_V1/scripts')
import common as c
R=Path('/workspace/dtc-lane-aa3-gaussian-174-v1');review=json.loads((R/'WATCHER_PRE_SIGNAL_REVIEW_V2.json').read_text());assert review['signal_allowed']
pid=1425986
fd=os.pidfd_open(pid)
p=c.proc(pid);assert p['start_ticks']==584741606 and p['argv']==review['watcher']['argv']
assert c.sha(review['script'])==review['script_sha256']
assert 'FLOCK' in Path('/proc/1425986/fdinfo/9').read_text()
children=Path('/proc/1425986/task/1425986/children').read_text().split()
assert all(c.proc(int(p))['argv']==['sleep','120'] for p in children)
record=dict(utc=c.now(),pid=pid,start_ticks=p['start_ticks'],pidfd_bound=True,signal='SIGTERM',target_scope='SINGLE_REVIEWED_WATCHER_ONLY',children_not_signaled=[c.proc(int(p)) for p in children],lock_file_not_deleted=True)
with (R/'WATCHER_SIGTERM.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
signal.pidfd_send_signal(fd,signal.SIGTERM)
os.close(fd)
for _ in range(100):
 p=c.proc(pid)
 if p is None or p['state']=='Z':break
 time.sleep(.1)
record=dict(utc=c.now(),watcher_after=c.proc(pid),exit_or_zombie=c.proc(pid) is None or c.proc(pid)['state']=='Z',no_other_signal_sent=True)
with (R/'WATCHER_PARENT_EXIT.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps(record))
