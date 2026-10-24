from closure_local import *
from closure_resources import UTIL
code=UTIL+r'''
import hashlib
base='/root/workspace/accel-sim-framework-awma-storage-consumer-audit-174new-v1'
names=cmd(['git','-C',base,'ls-tree','-r','--name-only','HEAD','docs/vm_tlb']).splitlines()
selected=[p for p in names if any(z in p.upper() for z in ['STORAGE_CONSUMER','STORAGE_GOVERNANCE','STORAGE_CATALOG'])]
out=dict(utc=time.time(),consumer_git_head=cmd(['git','-C',base,'rev-parse','HEAD']).strip(),consumer_documents=[],q05_local_current=[])
for rel in selected[:80]:
 p=base+'/'+rel
 if os.path.isfile(p) and os.path.getsize(p)<200000 and rel.endswith(('.json','.tsv','.md')):
  b=Path(p).read_bytes();out['consumer_documents'].append(dict(path=p,sha256=hashlib.sha256(b).hexdigest(),text=b.decode(errors='replace')))
qbase='/root/workspace/accel-sim-framework-awma-first-current-model-replay-174new-v1/docs/vm_tlb/review_packs/AWMA_FIRST_CURRENT_MODEL_BASELINE_SIM_174NEW_V1'
for rel in ['raw/replay_1/run.log','raw/replay_2/run.log','raw/replay_1/RUN_MANIFEST.tsv','raw/replay_1/SIM_RUN_RECEIPT.json']:
 p=qbase+'/'+rel;s=meta(p)
 if os.path.isfile(p) and s['size']<512*1024:
  b=Path(p).read_bytes();s['sha256']=hashlib.sha256(b).hexdigest();s['matches_accepted_raw_log_sha256']=s['sha256']=='06822c9fb9d2de0208eb51fb61c82f21150f509b8320662fd935efbac283843f'
  if not rel.endswith('run.log'):s['metadata_text']=b.decode(errors='replace')
 out['q05_local_current'].append(s)
print(json.dumps(out))
'''
x=remote('hrl-174-new',code,75);save('evidence/AWMA_EXISTING_CONSUMER_AUDIT_AND_Q05_LOCAL_ORIGINAL.json',x)
print('consumer head',x['consumer_git_head'],'docs',len(x['consumer_documents']));print([(r['path'],r.get('size'),r.get('matches_accepted_raw_log_sha256')) for r in x['q05_local_current']])
for r in x['consumer_documents']:
 if any(t in r['text'] for t in ['c8b417','92a553','SIM_EVIDENCE','LOCAL_ONLY']):print(r['path'],r['text'][:1900])
