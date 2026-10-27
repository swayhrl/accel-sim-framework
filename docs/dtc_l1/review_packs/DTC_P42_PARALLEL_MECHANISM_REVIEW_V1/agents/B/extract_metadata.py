import pathlib,json,gzip,hashlib,re,resource,os
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');R=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_p42_parallel_mechanism_review_v1/agents/B');R.mkdir(parents=True,exist_ok=True)
payload=json.loads(__PAYLOAD__)
out=[]
for item in payload:
 p=T/'control/input_bindings'/(item['input_digest']+'.json'); b=json.loads(p.read_text()); ch=item['modes']['CH'];s=P(ch['strict_path']); d=json.loads(s.read_text());raw=P(ch['output'])/'raw.log.gz'
 # Existing closed accepted raw only; incremental line read, retain numeric records only.
 nums={}; keylines=[]; un=hashlib.sha256()
 with gzip.open(raw,'rb') as f:
  for line in f:
   un.update(line); txt=line.decode(errors='replace').strip();m=re.match(r'^([A-Za-z_][A-Za-z_0-9.: -]*)\s*=\s*([-+0-9.eE]+)(?:\s|$)',txt)
   if m:
    try: val=float(m.group(2)); nums.setdefault(m.group(1).strip(),[]).append(val)
    except ValueError: pass
 assert un.hexdigest()==ch['raw_uncompressed_sha256']
 out.append({'program':item['program'],'input_digest':item['input_digest'],'binding_path':str(p),'binding_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'qualification':b['qualification'],'body_parser_sha256':b['body_parser_sha256'],'qualification_source_sha256':b['qualification_source_sha256'],'CH':ch,'strict':d,'raw_numeric':nums,'raw_uncompressed_sha_verified':True})
result={'schema':'DTC_B_READONLY_METADATA_V1','rows':out,'new_simulations':0}
(R/'METADATA.json').write_text(json.dumps(result,indent=2)+'\n')
for name in ['original_body_audit.py','body_audit_ratebound.py']:(R/name).write_bytes((T/'tools'/name).read_bytes())
print(json.dumps({'rows':len(out),'path':str(R/'METADATA.json'),'bytes':(R/'METADATA.json').stat().st_size}))
