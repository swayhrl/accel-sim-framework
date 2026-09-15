import csv,hashlib,json,shutil
from pathlib import Path
V12=Path('/root/workspace/accel-sim-framework-c16-qwen3-authorization-174new-v12'); S=Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/prospective_inputs/C16_PROSPECTIVE_COMMON_INPUT_V2'); O=Path('docs/vm_tlb/review_packs/C16_QWEN3_V2_INPUT_EXPORT_174NEW_V13'); AUTH='79d3899a1279210c008e0caff2950958e7f06dba'
def h(p):
 x=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):x.update(b)
 return x.hexdigest()
def main():
 O.mkdir();(O/'payloads').mkdir(); val=V12/'docs/vm_tlb/review_packs/C16_QWEN3_AUTHORIZATION_174NEW_V12/V2_CANONICAL_REVALIDATION.tsv'; vr={r['payload']:r for r in csv.DictReader(open(val),delimiter='\t')}; names=sorted(p.name for p in S.glob('qwen3-8b__*.json'))
 if len(names)!=7 or any(n not in vr or vr[n]['result']!='PASS' for n in names):raise RuntimeError('V12 canonical PASS prerequisite failed')
 rows=[]
 for n in names:
  a,b=S/n,O/'payloads'/n;shutil.copyfile(a,b); rows.append({'filename':n,'model':'Qwen/Qwen3-8B','revision':'b968826d9c46dd6066d109eabc6255188de91218','scenario':n.split('__',1)[1].removesuffix('.json'),'original_v2_source_path':str(a),'source_sha256':h(a),'source_bytes':a.stat().st_size,'exported_path':str(b),'exported_sha256':h(b),'exported_bytes':b.stat().st_size,'v12_authorization_sha':AUTH,'v2_validation_sha':h(val),'result':'PASS' if h(a)==h(b) and a.stat().st_size==b.stat().st_size else 'FAIL'})
 with open(O/'PAYLOAD_EXPORT_RECEIPT.tsv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
 ok=all(r['result']=='PASS' for r in rows); (O/'APPROVED_TRANSFER.json').write_text(json.dumps({'authority_commit':AUTH,'v2_validation_sha256':h(val),'payload_count':len(rows),'byte_for_byte':ok,'scenarios':[r['scenario'] for r in rows]},indent=2)+'\n');(O/'FINAL_DECISION.json').write_text(json.dumps({'decision':'C16_QWEN3_V2_INPUT_EXPORT_174NEW_V13_PASS' if ok else 'FAIL_CLOSED','gpu_execution':False,'v1_fallback':False,'retokenization':False,'v2_mutation':False,'formal_raw_catalog_mutation':False},indent=2)+'\n');(O/'OPEN_ISSUES.md').write_text('Transport-only snapshot; it does not expand V12 scenario authorization.\n')
 with open(O/'SHA256SUMS','w') as f:
  for p in sorted(O.rglob('*')):
   if p.is_file() and p.name!='SHA256SUMS':f.write(h(p)+'  '+str(p.relative_to(O))+'\n')
main()
