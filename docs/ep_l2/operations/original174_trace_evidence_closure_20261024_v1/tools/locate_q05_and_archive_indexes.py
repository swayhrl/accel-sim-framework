from closure_local import *
from closure_resources import UTIL
code=UTIL+r'''
import hashlib
out=dict(utc=time.time(),own164_top_level=[],q05_catalog_documents=[],known_index_candidates=[])
base='/root/share/mnt164/huangrulin'
try:
 for i,e in enumerate(os.scandir(base)):
  if i>=150:break
  if any(z in e.name.lower() for z in ['trace','archive','accel','awma','c16','storage','dtc','polybench','rodinia','parboil']):out['own164_top_level'].append(meta(e.path))
except OSError as e:out['error']=str(e)
# Exact catalog categories and known review pack only; never raw/NAS recursion.
roots=[base+'/c16_ai_workload/catalog/awma/entries/SIM_EVIDENCE',base+'/c16_ai_workload/catalog/awma/entries/SIM_RUN',base+'/c16_ai_workload/catalog/awma/entries/SIM_RUNS',base+'/c16_ai_workload/catalog/awma/entries/SIM_EVIDENCE',base+'/c16_ai_workload/derived/awma/simulation/runs']
for root in dict.fromkeys(roots):
 try:
  for i,e in enumerate(os.scandir(root)):
   if i>=160:break
   s=meta(e.path)
   if e.is_file(follow_symlinks=False) and e.name.endswith(('.json','.tsv','.md')) and s.get('size',10**10)<512*1024:
    b=Path(e.path).read_bytes();out['q05_catalog_documents'].append(dict(**s,sha256=hashlib.sha256(b).hexdigest(),text=b.decode(errors='replace')))
   elif e.is_dir(follow_symlinks=False):out['known_index_candidates'].append(s)
 except OSError as ex:out['known_index_candidates'].append(dict(path=root,error=str(ex)))
print(json.dumps(out))
'''
x=remote('hrl-174-new',code,70);save('evidence/EXACT_Q05_CATALOG_AND_OWN_RESEARCH_INDEX_LOCATORS.json',x)
print('own root research names',[r['path'] for r in x['own164_top_level']]);print('q05docs',len(x['q05_catalog_documents']))
for d in x['q05_catalog_documents']:
 if 'c8b4175d' in d['text'] or '92a553b0' in d['text']:print(d['path'],d['text'][:2600])
