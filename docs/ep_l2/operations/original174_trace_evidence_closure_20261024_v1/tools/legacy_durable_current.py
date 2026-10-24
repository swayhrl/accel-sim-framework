from closure_local import *
from closure_resources import UTIL
code=UTIL+r'''
import hashlib
root='/root/share/mnt164/huangrulin/c16_ai_workload/provenance/historical_snapshots/old174_c12_c15_simulation'
q=[(root,0)];out=dict(utc=time.time(),root=meta(root),entries=[],documents=[]);n=0
while q and n<120:
 p,d=q.pop(0)
 try:
  for e in os.scandir(p):
   n+=1;s=meta(e.path);out['entries'].append(s)
   if e.is_dir(follow_symlinks=False) and d<1 and e.name in ['receipts','manifests','private_export']:q.append((e.path,d+1))
   if e.is_file(follow_symlinks=False) and s.get('size',10**10)<1024*1024 and e.name.endswith(('.tsv','.json','.md')):
    b=Path(e.path).read_bytes();out['documents'].append(dict(path=e.path,sha256=hashlib.sha256(b).hexdigest(),size=len(b),text=b.decode(errors='replace')))
   if n>=120:break
 except OSError as e:out['entries'].append(dict(path=p,error=str(e)))
print(json.dumps(out))
'''
x=remote('hrl-174-new',code,65);save('evidence/LEGACY_VM_TRUE164_CURRENT_CANONICAL_RECEIPTS.json',x)
print('entries',len(x['entries']),'documents',[(Path(d['path']).name,d['size']) for d in x['documents']])
