from pathlib import Path
import json,hashlib,os,stat,collections
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');NAS=Path('/root/share/mnt164/huangrulin/traces')
for n in ['catalog','bundles','views','inbox','quarantine','receipts']:(NAS/n).mkdir(exist_ok=True)
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def put(n,x):(R/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
hashes={h:json.loads((R/'control'/f'{h}_HASH_COMPLETE.json').read_text())['files'] for h in ['174','174-new']}
freeze={h:json.loads((R/'control'/f'{h}_FROZEN_METADATA.json').read_text())['files'] for h in hashes}
frozen_by_key={r['key']:r for rows in freeze.values() for r in rows}
frozen_by_path={h:{r['path']:r for r in rows} for h,rows in freeze.items()}
bykey={k:{**v,'host':h} for h,rows in hashes.items() for k,v in rows.items()}
by_path={h:{v['path']:v for v in rows.values()} for h,rows in hashes.items()}
aliases=json.loads((R/'control/INPUT_ALIASES_FROM_AUDIT.json').read_text())
objects={};candidates=[]
for r in aliases:
 entry=by_path[r['host']][r['path']];members=[{'relative_path':'kernelslist.g','sha256':entry['sha256'],'size':entry['identity']['size'],'key':entry['key']}]
 text=frozen_by_path[r['host']][r['path']]['commandlist_hex']
 order=[l for raw in bytes.fromhex(text).decode().splitlines() for l in [raw.strip()] if l and not l.startswith('#') and not l.lower().startswith(('memcpy','cudamemcpy'))]
 names=list(dict.fromkeys(order));assert len(names)==len(r['member_object_keys'])
 for key in r['member_object_keys']:
  x=bykey[key];name=Path(x['path']).name
  # Keep the original member basename from this alias's directory, even if its
  # first inode alias has a different filename.
  # The old index object keys preserve order; match declared names directly.
  i=len(members)-1;name=names[i]
  members.append({'relative_path':name,'sha256':x['sha256'],'size':x['identity']['size'],'key':key})
 for m in members:
  x={**entry,'host':r['host']} if m['relative_path']=='kernelslist.g' else bykey[m['key']]
  ob=objects.setdefault(m['sha256'],{'sha256':m['sha256'],'size':m['size'],'sources':[]})
  assert ob['size']==m['size'];source={k:x[k] for k in ['host','key','path','identity']}
  source['realpath']=(frozen_by_path[r['host']][r['path']] if m['relative_path']=='kernelslist.g' else frozen_by_key[x['key']])['realpath']
  if source not in ob['sources']:ob['sources'].append(source)
 identity={'suite':r['suite'],'program':r['program'],'version':r['version'],'extent':r['extent'],'members':sorted([{k:m[k] for k in ['relative_path','sha256','size']} for m in members],key=lambda m:m['relative_path'])}
 bid=hashlib.sha256(canon(identity)).hexdigest()
 existing=next((x for x in candidates if x['bundle_id']==bid),None)
 provenance={k:r.get(k) for k in ['host','path','realpath','kernel_launches','capture_scripts']}
 metadata_path=R/'control/INPUT_SOURCE_METADATA.json'
 if metadata_path.exists():
  if 'source_metadata' not in globals():source_metadata=json.loads(metadata_path.read_text())
  provenance['capture_scripts']=source_metadata.get(r['host']+'::'+r['path'],{}).get('capture_scripts',[])
 if existing:existing['source_aliases'].append(provenance)
 else:candidates.append({'bundle_id':bid,**identity,'source_aliases':[provenance],'ordered_kernel_members':order,'scientific_qualification_granted':False,'access_scope':'ALL_PROJECTS_IN_174NEW_NAMESPACE'})
# Current immutable prior164 objects are adopted by hash after exact sealed
# identity checks, never copied to a duplicate physical object.
cat=json.loads(Path('/root/data/ep_dtc_trace_migration_20261024_v1/controls/ASSET_CATALOG.json').read_text())
reuse=0
for a in cat['assets']:
 for m in a['members']:
  sha=m['sha256']
  if sha not in objects:continue
  p=Path(a['mount_tree'])/m['relative_path'];s=p.stat()
  assert [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns]==m['verified_tree_identity']
  objects[sha]['storage']={'path':str(p),'kind':'PRIOR_VERIFIED_TRUE164_OBJECT','proof_reference':a['proof_reference'],'expected_identity':[s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns]};reuse+=1
pending={h:[] for h in hashes}
from verified_storage import discover
shared,shared_receipts=discover()
for sha,o in objects.items():
 if not o.get('storage') and sha in shared:
  assert Path(shared[sha]['path']).stat().st_size==o['size']
  o['storage']=shared[sha]
put('control/COMMITTED_STORAGE_REUSE.json',{'status':'PASS_PINNED_METADATA_AND_CURRENT_IDENTITY','bundles':shared_receipts,'matching_content_objects':sum(o.get('storage',{}).get('kind','').startswith('ADOPTED_') for o in objects.values()),'independent_full_SHA_done_by_final_restore_stage':False})
for sha,o in objects.items():
 if o.get('storage'):continue
 # Prefer native shared files when possible; the native backend can reuse the
# qualified local test transport without invoking a science controller.
 src=sorted(o['sources'],key=lambda r:r['host']!='174')[0]
 pending[src['host']].append(o)
batches=[]
for host,items in pending.items():
 batch=[];size=0
 def close(batch,size):
  if not batch:return
  rows=[]
  for o in batch:
   src=next(s for s in o['sources'] if s['host']==host)
   row=dict(src['identity']);row.update(relative_path=src['realpath'].lstrip('/'),sha256=o['sha256']);rows.append(row)
  body={'payload_kind':'CAS_FILES_V1','members':rows,'host':host}
  oid=hashlib.sha256(canon(body)).hexdigest();mid=oid[:20]
  m={'schema':'SHARED_SM70_CAS_PAYLOAD_V1','payload_kind':'CAS_FILES_V1','freeze_status':'FROZEN_FULL_SOURCE_SHA','primary_asset_id':'EXPANDED_'+mid,'object_id':oid,'source_root':'/','source_root_identity':{'uid':0,'gid':0,'mode':493,'mtime_ns':0,'metadata_policy':'VIRTUAL_PAYLOAD_NAMESPACE'},'members':rows,'source_data_bytes':size,'ordered_kernel_members':[],'entry_name':'NOT_AN_APPLICATION_INPUT','commandlist_bytes_hex':'','new_true164_bundle':'/home/shared/huangrulin/traces/bundles/_payload/'+mid,'reuse':False,'source_host':host}
  if host=='174-new':m['source_backend']='native'
  path=R/'manifests'/(mid+'.json');path.write_text(json.dumps(m,indent=2)+'\n');batches.append({'manifest':str(path),'host':host,'id':mid,'bytes':size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
  for o,row in zip(batch,rows):o['storage']={'path':str(NAS/'bundles/_payload'/mid/'tree'/row['relative_path']),'kind':'NEW_TRUE164_CAS_PAYLOAD','batch_id':mid}
 for o in sorted(items,key=lambda x:x['size']):
  if batch and size+o['size']>4*1024**3:close(batch,size);batch=[];size=0
  batch.append(o);size+=o['size']
 close(batch,size)
put('control/EXPANDED_OBJECTS.json',objects);put('control/EXPANDED_BUNDLES.json',candidates);put('control/EXPANDED_BATCHES.json',batches)
summary={'logical_aliases':len(aliases),'content_and_extent_bundles':len(candidates),'unique_file_content_objects':len(objects),'unique_content_bytes':sum(o['size'] for o in objects.values()),'new_transfer_bytes':sum(b['bytes'] for b in batches),'existing164_content_objects_reused':sum('expected_identity' in o['storage'] for o in objects.values()),'new_batches':len(batches),'input_extent_counts':dict(collections.Counter(b['extent'] for b in candidates))}
put('control/EXPANDED_FROZEN_BUDGET.json',summary);print(json.dumps(summary),flush=True)
