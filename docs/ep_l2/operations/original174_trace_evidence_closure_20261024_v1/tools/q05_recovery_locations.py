from closure_local import *
from closure_resources import UTIL
code=UTIL+r'''
import hashlib
out=dict(utc=time.time(),known_roots=[],documents=[])
roots=['/root/share/mnt164/huangrulin/awma_q05_full_kernel_translation_analysis_v1','/root/share/mnt164/huangrulin/awma','/root/share/mnt164/huangrulin/awma_tlb_ptw_characterization_174new_v1']
n=0
for root in roots:
 q=[(root,0)]
 while q and n<600:
  p,d=q.pop(0)
  try:
   for e in os.scandir(p):
    n+=1;s=meta(e.path);out['known_roots'].append(s)
    if e.is_dir(follow_symlinks=False) and d<1:q.append((e.path,d+1))
    if e.is_file(follow_symlinks=False) and s.get('size',10**10)<128*1024 and e.name.lower().endswith(('.json','.tsv','.md','.sha256')):
     b=Path(e.path).read_bytes();out['documents'].append(dict(path=e.path,sha256=hashlib.sha256(b).hexdigest(),text=b.decode(errors='replace')))
    if n>=600:break
  except OSError as ex:out['known_roots'].append(dict(path=p,error=str(ex)))
print(json.dumps(out))
'''
x=remote('hrl-174-new',code,60);save('evidence/Q05_KNOWN_DURABLE_ROOTS_AND_RECOVERY_METADATA.json',x)
print('metadata',len(x['known_roots']),'documents',len(x['documents']))
for r in x['known_roots']:
 if 'run.log' in r['path'] or '92a553' in r['path']:print(r['path'],r.get('size'))
for r in x['documents']:
 if '06822c9f' in r['text'] or 'c8b4175d' in r['text']:print('BINDING',r['path'],r['text'][:2000])
