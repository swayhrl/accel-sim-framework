"""A67 owns only this worktree and output root; all scientific sources stay read-only."""
import os,json,hashlib,time
from pathlib import Path
W=Path(__file__).resolve().parents[2]
OLD=Path('/data/c16/aiarch_a61_igb_small_gnn_native_109_v1')
OLD65=Path('/data/c16/aiarch_a65_igb_small_compiled_numeric_109_v1')
R=Path('/data/c16/aiarch_a67_igb_small_eager_scope_wall_109_v1')
ROOT=R
DISPATCH_EPOCH=1792122884
os.sched_setaffinity(0,[0,2,4,6])
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
 return h.hexdigest()
def save(name,value):
 p=R/name;tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');os.replace(tmp,p)
def event(phase,**kw):
 x={'phase':phase,'epoch':time.time(),**kw};print(json.dumps(x),flush=True)
 with (R/'events.jsonl').open('a') as f:f.write(json.dumps(x)+'\n')
def usage(roots):
 seen=set();total=0
 for root in roots:
  if not root.exists():continue
  for p in root.rglob('*'):
   s=p.lstat();k=(s.st_dev,s.st_ino)
   if k not in seen:seen.add(k);total+=s.st_blocks*512
 return total
def allocated():return usage([R,W])
def new_raw_allocated():
 return usage([R,W/'docs/ai_workload_research/runs/AI_ARCH_A67_IGB_SMALL_EAGER_SCOPE_BOUNDED_WALL_109_V1'])
