from audit_local import *
from collect_audit import SNAP
old=Path('D:/repo/ep-dtc-trace-migration-20261024-v1')/'docs/ep_l2/operations/174new_ep_dtc_trace_migration_20261024_v1'
index=json.loads((old/'TRUE164_TRACE_RECOVERY_INDEX.json').read_text(encoding='utf8'))
requests=[]
for r in index['records']:
 m=json.loads((old/r['all_original_numeric_metadata_and_SHA']).read_text(encoding='utf8'))
 requests.append(dict(record=r,manifest=m))
(P/'TRACE_MANIFEST_SCHEMAS.json').write_text(json.dumps(requests[0],indent=2),encoding='utf8')
print('manifest schema',list(requests[0]['manifest']))
code=SNAP[:SNAP.index('x=dict(')]+ '\nrequests='+repr(requests)+r'''
out=[]
for a in requests:
 r=a['record'];out.append(dict(asset_id=r['asset_id'],source_root=meta(r['source_root']),true164_tree=r['true164_tree']))
print(json.dumps(out))
'''
save('evidence/TRACE_SOURCE_CURRENT_ROOT_METADATA.json',remote('hrl',code,60))
code=SNAP[:SNAP.index('x=dict(')]+ '\nrequests='+repr(requests)+r'''
out=[]
for a in requests:
 r=a['record'];p=r['true164_tree'].replace('/home/shared/','/root/share/mnt164/',1);bundle=r.get('true164_bundle')
 out.append(dict(asset_id=r['asset_id'],tree=meta(p),manifest_reference=r['all_original_numeric_metadata_and_SHA']))
print(json.dumps(out))
'''
save('evidence/TRACE_TRUE164_CURRENT_ROOT_METADATA.json',remote('hrl-174-new',code,60))
code=SNAP[:SNAP.index('x=dict(')]+r'''
o=dict(utc=time.time(),git_heads={},science_controls={},selected_metadata={},awma_local_roots=[])
for p in ['/root/data/ep_l2_main_20261023_v1/worktree','/root/data/dtc_main_20261023_v1/accel-sim-framework']:
 o['git_heads'][p]=cmd(['git','-C',p,'rev-parse','HEAD'])
for p in ['/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json']:
 if os.path.isfile(p) and os.path.getsize(p)<1024*1024:o['science_controls'][p]=json.loads(Path(p).read_text())
for base in ['/root/workspace','/root/workspace/worktrees','/root/data/dtc_main_20261023_v1/ae_fair_v1/control']:
 try:
  for e in os.scandir(base):
   if ('awma' in e.name.lower() or 'c16' in e.name.lower() or 'vm-' in e.name.lower()):o['awma_local_roots'].append(meta(e.path))
 except OSError:pass
print(json.dumps(o))
'''
save('evidence/CURRENT_OWNER_HEADS_AND_NATIVE_SCIENCE.json',remote('hrl-174-new',code,60))

