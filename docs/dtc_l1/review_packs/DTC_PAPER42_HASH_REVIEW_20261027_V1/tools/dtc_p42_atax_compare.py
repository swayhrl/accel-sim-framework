import pathlib,json,hashlib,re
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_paper42_hash_review_20261027_v1');e=json.loads((A/'evidence/prior_EVIDENCE_SNAPSHOT.json').read_bytes());rs=[r for r in e['rows']if r['intake']['program']=='ATAX'];full=next(r for r in rs if r['intake']['input_digest'].startswith('eeded'));part=next(r for r in rs if r['intake']['input_digest'].startswith('dd895'));records=[]
for name in ['kernel-1.traceg','kernel-2.traceg']:
 fp=P(full['intake']['asset']['trace_directory'])/name;pp=P(part['intake']['asset']['trace_directory'])/name
 pb=pp.read_bytes();at=pb.index(b'#BEGIN_TB');header=pb[:at];body=pb[at:]
 with fp.open('rb')as h:
  fh=b''
  while True:
   l=h.readline()
   if l.startswith(b'#BEGIN_TB'):break
   fh+=l
  prefix=l+h.read(len(body)-len(l));following=h.read(200)
 normal=lambda b:re.sub(rb'-grid dim = \([^\n]*\)',b'-grid dim = (NORMALIZED)',b)
 records.append(dict(kernel=name,full_path=str(fp),partial_path=str(pp),partial_file_sha256=hashlib.sha256(pb).hexdigest(),partial_body_sha256=hashlib.sha256(body).hexdigest(),full_body_prefix_sha256=hashlib.sha256(prefix).hexdigest(),partial_body_bytes=len(body),body_exact_prefix=body==prefix,headers_equal_except_grid=normal(header)==normal(fh),partial_TB_coordinates=[x.decode()for x in re.findall(rb'thread block = ([^\n]+)',body)],next_full_bytes=following.decode(errors='replace'),full_member_registered_sha=next(x['sha256']for x in full['intake']['asset']['members']if x['relative_path']==name)))
assert all(r['body_exact_prefix']and r['headers_equal_except_grid']for r in records)
out=dict(status='PROVEN_GRID_REWRITTEN_PREFIX_SUBSET_NOT_COMPLETE_APPLICATION',full_input_digest=full['intake']['input_digest'],partial_input_digest=part['intake']['input_digest'],same_command_list=full['intake']['expected_commands']==part['intake']['expected_commands'],kernels=records,interpretation='Both partial kernel execution bodies are byte-identical prefixes of the ordinary full-grid trace; only grid metadata is rewritten 16->2. Copies still describe the 4096x4096 matrix. This is not a separately captured smaller application. Preserves original historical strict PASS of each declared grid; excludes partial identity from the paper ordinary-input suite.',new_model_starts=0,original_files_modified=False)
(A/'evidence/ATAX_PREFIX_PROOF.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
