"""Read-only field diff after actual negative verifier HOLD; no repair."""
import hashlib,importlib.util,json,pathlib
P=pathlib.Path;HERE=P(__file__).resolve().parent
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
p=A/'agents/scan_m16_diagnosis_v1/terminal_impl_v1/scan_m16_engineering_negative_v1.py'
s=importlib.util.spec_from_file_location('readonly_hold_diff',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
b=A/'engineering_negative_evidence_v1'/m.C/'1e968456ccefd837eacee605d7ffacc712860114e8a7fea17b4633b25cecbf5f'
original=m.read(b/'SOURCE_MANIFEST.json');ctx=m.context();expected=m.build_manifest(ctx,original['original_entries'],b/'context',original['txid']);diff=[]
def compare(a,z,path=''):
 if type(a)is not type(z):diff.append(dict(path=path,original_type=type(a).__name__,current_type=type(z).__name__));return
 if isinstance(a,dict):
  for k in sorted(set(a)|set(z)):
   if k not in a or k not in z:diff.append(dict(path=path+'/'+k,missing_from='original'if k not in a else'current'))
   else:compare(a[k],z[k],path+'/'+k)
 elif isinstance(a,list):
  if len(a)!=len(z):diff.append(dict(path=path,original_length=len(a),current_length=len(z)))
  for i,(v,w)in enumerate(zip(a,z)):compare(v,w,path+'/'+str(i))
 elif a!=z:diff.append(dict(path=path,original=str(a)[:500],current=str(z)[:500]))
compare(original,expected)
out=dict(status='READONLY_EXISTING_CERT_MANIFEST_HOLD_DIFF',diffs=diff,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
 original_manifest_sha256=hashlib.sha256((b/'SOURCE_MANIFEST.json').read_bytes()).hexdigest(),new_registration=0,models=0,mutations=0)
(HERE/'EXISTING_CERT_HOLD_DIFF.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
