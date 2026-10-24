from closure_local import *
from closure_resources import UTIL,checkpoint
dis=load(T/'EXACT_SOURCE_RUN_SPEC_AND_REGISTRATION_DISCOVERY.json');sup=load(T/'SUPPLEMENTAL_ACCEPTED_AND_PLANNED_INPUT_COVERAGE.json')
req=[];held=[]
for r in dis['DTC']:
 row=r['row'];p=row.get('raw_dir')
 if not p or not p.startswith('/workspace/') or '..' in Path(p).parts:held.append(dict(label=row.get('label'),scientific_status=row.get('status'),why='NO_EXECUTED_RAW_ROOT; empty rejected before path resolution'));continue
 req.append(dict(project='DTC_L1',stage='ORIGINAL44',label=row.get('label'),path=p,owner_status=row.get('status'),owner_stdout_sha256=row.get('stdout_sha256'),owner_terminal_sha256=row.get('terminal_sha256'),owner_spec_sha256=row.get('spec_sha256')))
for r in sup['SG3_rows']:
 p=str(Path(r['source_manifest']).parent).replace('\\','/')
 if p.startswith('/workspace/') and not any(q['path']==p for q in req):req.append(dict(project='DTC_L1',stage='SG3_INDEPENDENT_COHORT',label=Path(p).name,path=p,owner_status=r['state'],manifest_sha256=r['source_manifest_sha256']))
save('evidence/P2_OWNER_SCOPED_NONEMPTY_ROOT_REQUESTS.json',dict(roots=req,rejected_empty=held,owner_reference=TRACE+':EXACT_SOURCE_RUN_SPEC_AND_REGISTRATION_DISCOVERY.json;SUPPLEMENTAL_ACCEPTED_AND_PLANNED_INPUT_COVERAGE.json'))
code=UTIL+'\nreq='+repr(req)+r'''
import collections,hashlib
out=[];n=0;t=time.monotonic()
for row in req:
 root=row['path'];o=dict(**row,root=meta(root),files=0,logical_bytes=0,allocated_bytes=0,role_counts={},control_documents=[],symlinks=[],status='COMPLETE_SCOPED_METADATA')
 if not root or not root.startswith('/workspace/') or '..' in Path(root).parts:o['status']='IDENTITY_HOLD';out.append(o);continue
 q=[root];roles=collections.defaultdict(lambda:dict(files=0,logical_bytes=0,allocated_bytes=0));t0=time.monotonic()
 while q:
  p=q.pop()
  if n>140000 or time.monotonic()-t>18 or time.monotonic()-t0>3:o['status']='INCOMPLETE_BUDGET';break
  try:
   for e in os.scandir(p):
    n+=1;s=meta(e.path)
    if e.is_symlink():o['symlinks'].append(dict(path=e.path,target=os.readlink(e.path)));continue
    if e.is_dir(follow_symlinks=False):
     if e.name not in ['.git','.ssh','.env']:q.append(e.path)
     continue
    if s.get('type')!='file':continue
    name=e.name;lower=name.lower();role='UNRESOLVED_OTHER'
    if lower.endswith(('.log','.out','.stdout')) or name in ['stdout','stderr']:role='SIMULATOR_RAW_OR_DIAGNOSTIC_LOG'
    elif lower.endswith(('.config','.conf')) or name in ['SPEC.json','RUN_START.json','RUN_MANIFEST.tsv','ACTUAL_PRODUCER_BINDING.json']:role='CONFIG_COMMAND_OR_RUNTIME_IDENTITY'
    elif 'strict' in lower or 'terminal' in lower or 'exit' in lower:role='TERMINAL_OR_CORRECTNESS_CONTROL'
    elif lower.endswith(('.csv','.tsv','.json','.jsonl')):role='STATISTICS_CONTROL_OR_DERIVED;SEMANTIC_OWNER_REVIEW'
    elif lower.endswith(('.o','.a','.so','.bin')):role='BINARY_OR_BUILD_IDENTITY;KEEP'
    elif 'maps' in Path(e.path).parts:role='MAPPER_AUXILIARY;KEEP_WITH_RESULT'
    o['files']+=1;o['logical_bytes']+=s['size'];o['allocated_bytes']+=s['allocated'];roles[role]['files']+=1;roles[role]['logical_bytes']+=s['size'];roles[role]['allocated_bytes']+=s['allocated']
    if name in ['STRICT.json','RUN_TERMINAL.json','NATIVE_EXIT.json','RUN_START.json','RUN_MANIFEST.tsv','ACTUAL_PRODUCER_BINDING.json','SPEC.json'] and s['size']<=131072:
     b=Path(e.path).read_bytes();o['control_documents'].append(dict(path=e.path,size=len(b),sha256=hashlib.sha256(b).hexdigest(),type=name))
  except OSError as e:o['status']='UNREADABLE_HOLD';o['error']=str(e)
 o['role_counts']=dict(roles);out.append(o)
print(json.dumps(dict(utc=time.time(),records=out,entries=n,seconds=time.monotonic()-t,large_payload_hash_bytes=0)))
'''
checkpoint('P2_BEFORE_OWNER_SCOPES')
x=remote('hrl',code,70);save('evidence/P2_DTC_ORIGINAL44_AND_SG3_RAW_CURRENT_METADATA.json',x)
print('scopedrawroots',len(x['records']),'entries',x['entries'],'held_empty',len(held),'bytes',sum(r['logical_bytes'] for r in x['records']))
checkpoint('P2_AFTER_OWNER_SCOPES')
