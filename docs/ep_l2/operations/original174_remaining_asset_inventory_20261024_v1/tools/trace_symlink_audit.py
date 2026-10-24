from audit_local import *
from collect_audit import SNAP
code=SNAP[:SNAP.index('x=dict(')]+r'''
root='/workspace/worktrees/accel-sim-decoupled-l2/hw_run'
q=[(root,0)];out=[];n=0;t=time.monotonic();pruned=[]
while q and n<35000 and time.monotonic()-t<14:
 p,d=q.pop()
 try:
  with os.scandir(p) as it:
   for e in it:
    n+=1
    if e.is_symlink():
     s=meta(e.path);z=os.path.realpath(e.path);s['resolved_path']=z
     if z.startswith(('/workspace/','/root/share/workspace_migrated_20260905/','/root/share/mnt164/huangrulin/')):s['resolved_stat']=meta(z)
     out.append(s)
    elif d<5 and e.is_dir(follow_symlinks=False) and e.name not in ['.git','.ssh','.env']:q.append((e.path,d+1))
    if n>=35000:break
 except OSError:pruned.append(p)
print(json.dumps(dict(utc=time.time(),root=root,symlinks=out,entries=n,seconds=time.monotonic()-t,pending_dirs=len(q),unreadable=pruned,scope='bounded depth5 metadata only; no symlink traversal')))
'''
save('evidence/SOURCE_TRACE_ALIAS_AND_STORAGE_ENDPOINTS.json',remote('hrl',code,35))
