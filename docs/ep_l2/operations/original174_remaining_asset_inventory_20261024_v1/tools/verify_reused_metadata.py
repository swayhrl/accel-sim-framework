from audit_local import *
from collect_audit import SNAP
old=Path('D:/repo/ep-dtc-trace-migration-20261024-v1/docs/ep_l2/operations/174new_ep_dtc_trace_migration_20261024_v1')
idx=json.loads((old/'TRUE164_TRACE_RECOVERY_INDEX.json').read_text(encoding='utf8'))
req=[]
for r in idx['records']:
 m=json.loads((old/r['all_original_numeric_metadata_and_SHA']).read_text(encoding='utf8'))
 req.append(dict(asset_id=r['asset_id'],source_root=r['source_root'],members=[{k:v for k,v in f.items() if k in ['relative_path','dev','inode','size','mtime_ns','ctime_ns','sha256']} for f in m['members']],tree=r['true164_tree'],bundle=r.get('true164_bundle'),expected_commit_sha256=r.get('actual_target_commit_sha256'),existing_commit=r.get('actual_existing_commit_path')))
code=SNAP[:SNAP.index('x=dict(')]+ '\nreq='+repr(req)+r'''
out=[]
for r in req:
 rows=[]
 for f in r['members']:
  p=r['source_root']+'/'+f['relative_path'];s=meta(p)
  s['historical_sha256']=f.get('sha256');s['identity_fields_match']=all(s.get(k)==f.get(k) for k in ['dev','inode','size','mtime_ns','ctime_ns'])
  rows.append(s)
 out.append(dict(asset_id=r['asset_id'],files=rows,all_current_source_identities_match=all(s['identity_fields_match'] for s in rows)))
print(json.dumps(out))
'''
save('evidence/TRACE_CURRENT_SOURCE_MEMBERS_VS_COMPLETED_SHA_IDENTITIES.json',remote('hrl',code,60))
code=SNAP[:SNAP.index('x=dict(')]+ '\nreq='+repr(req)+r'''
import hashlib
out=[]
for r in req:
 tree=r['tree'].replace('/home/shared/','/root/share/mnt164/',1)
 rows=[meta(tree+'/'+f['relative_path']) for f in r['members']]
 cr=dict(asset_id=r['asset_id'],files=len(rows),all_members_present_sizes_match=all(s.get('size')==f['size'] and s.get('type')=='file' for s,f in zip(rows,r['members'])),allocated_sum=sum(s.get('allocated',0) for s in rows))
 p=r['existing_commit'] or ((r['bundle']+'/COMMIT.json') if r['bundle'] else None)
 if p:
  p=p.replace('/home/shared/','/root/share/mnt164/',1)
  if os.path.isfile(p) and os.path.getsize(p)<131072:
   b=Path(p).read_bytes();cr.update(commit_path=p,commit_sha256=hashlib.sha256(b).hexdigest(),expected_sha256=r['expected_commit_sha256'],commit_hash_matches=hashlib.sha256(b).hexdigest()==r['expected_commit_sha256'])
 out.append(cr)
print(json.dumps(out))
'''
save('evidence/TRACE_TRUE164_SMALL_COMMIT_AND_MEMBER_STAT_READBACK.json',remote('hrl-174-new',code,90))
print('trace member current metadata checks complete')
