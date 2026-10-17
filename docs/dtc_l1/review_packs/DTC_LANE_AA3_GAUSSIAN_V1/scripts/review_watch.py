import os,sys,json,hashlib,time
from pathlib import Path
sys.path.insert(0,'/workspace/worktrees/accel-sim-iscas2027-dtc-lane-aa2-gaussian-factorial-174-v1/docs/dtc_l1/review_packs/DTC_LANE_AA2_GAUSSIAN_V1/scripts')
import common as c
R=Path('/workspace/dtc-lane-aa3-gaussian-174-v1')
pid=1425986; expect=584741606
s=c.snapshot(); ps={p['pid']:p for p in s['processes']}
for p in ps.values():
 try:
  q=Path('/proc')/str(p['pid']);p['ppid']=int((q/'stat').read_text().rsplit(')',1)[1].split()[1]);p['cwd']=os.readlink(q/'cwd')
 except OSError:p['ppid']=-1
children=[];front=[pid]
while front:
 n=front.pop()
 for p in ps.values():
  if p['ppid']==n:children.append(p);front.append(p['pid'])
locks=[]
for p in ps.values():
 for fd in (Path('/proc')/str(p['pid'])/'fdinfo').glob('*'):
  try:
   txt=fd.read_text()
   if '\nlock:' not in txt:continue
   target=os.readlink(fd.parent.parent/'fd'/fd.name)
   if any(t in target.lower() for t in ['dtc','fast64','lane']):locks.append(dict(pid=p['pid'],start_ticks=p['start_ticks'],fd=fd.name,target=target,fdinfo=txt))
  except OSError:pass
sim=[]
for p in ps.values():
 try:exe=os.readlink(Path('/proc')/str(p['pid'])/'exe')
 except OSError:continue
 if 'accel-sim.out' in exe or any(Path(a).name=='accel-sim.out' for a in p['argv']):sim.append(dict(**p,exe=exe))
repo=Path('/workspace/worktrees/accel-sim-decoupled-l1-fast64')
script=repo/'util/dtc_l1/auto_dispatch_fast64_4_2d_core41_v1.sh'
base=repo/'docs/dtc_l1/fast64/generated/fast64_3_repair_v1/fast64_3_2DConvolution_base_core41d740e8_a1_v1.json'
struct=base.with_name('FAST64_3_2DCONVOLUTION_BASE_STRUCTURAL_METRICS_V1.json')
argv=['bash',str(script),'--watch','--poll-seconds','120','--log','/workspace/fast64-primary-r4/fast64_4_2d_core41_autodispatch_v1.log']
helper=[repo/'util/dtc_l1'/n for n in ['dispatch_fast64_4_2d_core41_v1.sh','monitor_fast64_repaired_core_row_v2.sh','audit_fast64_future_precompute_resources_v3.sh']]
expected=['e26f090f076f7929d4933aad743964c757ddabfa0514858768e365add286b441','266a489c246512d5d321d77c2ef6e10794b0b0deb4e6aa7bb9bd2ee3f37b67ff','2a806549ebbe1870609f03fab396a4b78f01945091683f7cfa93e2f447470355']
checks=dict(exact_PID_start_ticks=pid in ps and ps[pid]['start_ticks']==expect,exact_argv=pid in ps and ps[pid]['argv']==argv,exact_parent=pid in ps and ps[pid]['ppid']==1,held_expected_flock=any(l['pid']==pid and l['fd']=='9' and l['target']=='/workspace/fast64-primary-r4/.fast64_4_2d_core41_autodispatch_v1.lock' and 'FLOCK' in l['fdinfo'] for l in locks),only_timer_descendants=all(p['argv']==['sleep','120'] for p in children),no_simulators=not sim,no_triplet_run_directories=not list(Path('/workspace/fast64-primary-r4').glob('fast64_4_primary_2dconvolution*')),base_gate_absent=not base.exists() or not struct.exists(),pinned_helpers_match=all(c.sha(p)==h for p,h in zip(helper,expected)))
out=dict(utc=c.now(),watcher=ps.get(pid),descendants=children,all_visible_simulators=sim,all_DTC_FD_locks=locks,script=str(script),script_sha256=c.sha(script),helpers=[dict(path=str(p),sha256=c.sha(p)) for p in helper],base_exists=base.exists(),structural_exists=struct.exists(),log_tail=Path(argv[-1]).read_text().splitlines()[-8:],checks=checks,scientific_authorization='AA3 user authorizes no new old 2D input; this watcher is only conditional precompute and has no active served task.',signal_allowed=all(checks.values()),signal_sent=False)
(R/'WATCHER_PRE_SIGNAL_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n')
(R/'pre_signal_snapshot.json').write_text(json.dumps(s,indent=2)+'\n')
print(json.dumps(out,indent=2))
