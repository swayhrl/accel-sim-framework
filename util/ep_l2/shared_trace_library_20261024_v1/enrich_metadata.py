from pathlib import Path
import gzip,json,hashlib
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
p=Path('/root/data/ep_l2_main_20261023_v1/worktree/docs/ep_l2/operations/ep_main_account_workload_audit_20261024_v2/EXACT_INPUT_INDEX.json.gz')
rows=json.loads(gzip.decompress(p.read_bytes()));data={}
for r in rows:
 scripts=[]
 for s in r.get('capture_scripts',[]):scripts.append({**s,'text_reencodes_to_original_sha':hashlib.sha256(s['text'].encode()).hexdigest()==s['sha256'],'scope':'Historical inventory snapshot; never executed by this Goal'})
 data[r['host']+'::'+r['path']]={'capture_scripts':scripts,'inventory_source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'inventory_commit':'0bc1aa9f3bfb3cceccdea32af4af668037769027'}
(R/'control/INPUT_SOURCE_METADATA.json').write_text(json.dumps(data,indent=2)+'\n');print('HISTORICAL_CAPTURE_METADATA_ATTACHED')
