#!/usr/bin/env python3
import pathlib,json,hashlib,collections
from scientific_identity_v2 import key,identity,physical
C=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/control');S=pathlib.Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1')
o=json.loads((C/'UNIFIED_SCOPE_STATUS.json').read_text());index={r['content_id']:r for r in o['contents']};aliases=collections.defaultdict(set);audit=[]
jobs=[dict(json.loads(p.read_text()),job_path=str(p)) for p in (C/'capture_jobs').glob('*.json')]
for j in jobs:aliases[physical(j['task'])].add(key(j['task']))
for state in o['native_attempts']:
 p=pathlib.Path(state['native_receipt']);n=json.loads(p.read_text());t=n.get('task')
 if not t:state['identity_status']='FULL_TASK_NOT_IN_RECEIPT_REQUIRES_MANIFEST_JOIN';continue
 k=key(t);state.update(content_id=k,identity_status='FULL_RECEIPT_TASK_SCIENTIFIC_IDENTITY_V2')
 if k not in index:
  r={'content_id':k,'legacy_physical_content_id':physical(t),'scientific_identity':identity(t),'suite':t['suite'],'source_version':t.get('version'),'source_head':t.get('source_head'),'program':t['program'],'variant':t.get('variant'),'argv':t['argv'],'binary_sha256':t.get('binary_sha256'),'input_identity':t.get('input_files',t.get('input_identity')),'observations':[{'native_state_receipt':str(p)}],'native_evidence':[state],'status':state['scope_status'],'consumer_qualification':'NOT_GRANTED'}
  index[k]=r;o['contents'].append(r)
for t in json.loads((S/'manifests/ALL_CAPTURE_CANDIDATES_PROFILE_PENDING_V1.json').read_text()):
 matches=[j for j in jobs if physical(j['task'])==physical(t)]
 audit.append({'candidate_task_id':t.get('task_id'),'physical_id':physical(t),'scientific_id':key(t),'scientific_matching_jobs':[j['id'] for j in matches if key(j['task'])==key(t)],'same_physical_different_scientific_jobs':[j['id'] for j in matches if key(j['task'])!=key(t)]})
(C/'SCIENTIFIC_IDENTITY_ALIAS_AUDIT_V2.json').write_text(json.dumps({'schema':'V2_LOGICAL_VS_PHYSICAL_ALIAS_AUDIT','candidate_rows':len(audit),'physical_groups_with_multiple_logical_identities':sum(len(v)>1 for v in aliases.values()),'rows':audit},indent=2)+'\n')
o['scope_identity_module_sha256']=hashlib.sha256((C/'scientific_identity_v2.py').read_bytes()).hexdigest();o['status_counts']=dict(collections.Counter(r['status'] for r in o['contents']))
(C/'UNIFIED_SCOPE_STATUS.json').write_text(json.dumps(o,indent=2)+'\n')
mapping=[{'id':j['id'],'content_id':key(j['task']),'asset_id':j['asset_id'],'job_path':j['job_path'],'task':j['task']} for j in jobs]
(C/'ALL_PREPARED_CAPTURE_JOBS_V2.json').write_text(json.dumps(mapping,indent=2)+'\n')
print(json.dumps({'scope_rows':len(o['contents']),'logical_split_groups':sum(len(v)>1 for v in aliases.values()),'native_receipt_mapping':dict(collections.Counter(x.get('identity_status') for x in o['native_attempts']))}))
