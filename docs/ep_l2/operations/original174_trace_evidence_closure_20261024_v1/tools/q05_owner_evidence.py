from closure_local import *
import urllib.request
ref=git('rev-parse','6415d3f1').decode().strip()
paths=['docs/vm_tlb/review_packs/AWMA_FIRST_CURRENT_MODEL_BASELINE_SIM_174NEW_V1/SIM_EVIDENCE_RECORD.json','docs/vm_tlb/review_packs/AWMA_FIRST_CURRENT_MODEL_BASELINE_SIM_174NEW_V1/SIM_RUN_RECORD.json','docs/vm_tlb/review_packs/AWMA_Q05_FULL_KERNEL_TRANSLATION_BEHAVIOR_174NEW_V1/RAW_DATA_INDEX.tsv','docs/vm_tlb/review_packs/AWMA_Q05_FULL_KERNEL_TRANSLATION_BEHAVIOR_174NEW_V1/RUN_RECEIPTS.json','docs/vm_tlb/review_packs/AWMA_Q05_FULL_KERNEL_TRANSLATION_BEHAVIOR_174NEW_V1/README.md']
out=[]
for path in paths:
 url='https://raw.githubusercontent.com/swayhrl/accel-sim-framework/'+ref+'/'+path
 try:
  with urllib.request.urlopen(url,timeout=25) as r:b=r.read(2*1024**2)
  out.append(dict(commit=ref,path=path,sha256=hashlib.sha256(b).hexdigest(),text=b.decode()))
 except Exception as e:out.append(dict(commit=ref,path=path,error=str(e)))
save('evidence/Q05_EXACT_ACCEPTED_OWNER_GITHUB_DOCUMENTS.json',out)
for r in out:print(r['path'],r.get('error',r.get('text','')[:3000]))
