from closure_local import *
from closure_resources import UTIL
ref=git('rev-parse','6415d3f1').decode().strip()
code=UTIL+'\nref='+repr(ref)+r'''
import urllib.request,hashlib
root='docs/vm_tlb/review_packs/AWMA_FIRST_CURRENT_MODEL_BASELINE_SIM_174NEW_V1'
out=[]
for name in ['raw/replay_1/run.log','raw/replay_1/RUN_MANIFEST.tsv','raw/replay_2/run.log','raw/replay_1/SIM_RUN_RECEIPT.json','raw/replay_2/SIM_RUN_RECEIPT.json']:
 url='https://raw.githubusercontent.com/swayhrl/accel-sim-framework/'+ref+'/'+root+'/'+name
 try:
  with urllib.request.urlopen(url,timeout=20) as f:b=f.read(512*1024+1)
  o=dict(path=root+'/'+name,url=url,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),whole_file_within_budget=len(b)<=512*1024)
  if name.endswith('run.log'):o['equals_SIM_EVIDENCE_c8_raw_log_sha256']=o['sha256']=='06822c9fb9d2de0208eb51fb61c82f21150f509b8320662fd935efbac283843f'
  else:o['metadata_text']=b.decode(errors='replace')
 except Exception as e:o=dict(path=name,error=str(e))
 out.append(o)
print(json.dumps(dict(utc=time.time(),documents=out,actual_execution_host=cmd(['hostname']).strip(),any_164_payload_written=False,any_scientific_run_launched=False,scope='Existing Git immutable recovery objects in memory only, not a claim that these bytes are on164')))
'''
x=remote('hrl-174-new',code,115);save('evidence/Q05_FIXED10000_ACCEPTED_GIT_RECOVERY_CONTENT_BINDING.json',x)
print([(r['path'],r.get('bytes'),r.get('equals_SIM_EVIDENCE_c8_raw_log_sha256'),r.get('error')) for r in x['documents']])
