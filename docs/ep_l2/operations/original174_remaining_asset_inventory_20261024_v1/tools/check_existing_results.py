from audit_local import *
from collect_audit import SNAP
req=[]
for a in ['EP_L2_E057','DTC_L1_AD_GEMM']:
 p='docs/ep_l2/operations/full_result_offload_20261023_v1/results/'+a+'/SOURCE_MANIFEST.json'
 x=json.loads(obj('c02fbf9f554b6287151ae50666889ff3aac4eebc',p))
 req.append(dict(asset=a,source=x['source_root'],entries=[{k:v for k,v in e.items() if k in ['path','type','dev','inode','size','mtime_ns','ctime_ns','uid','gid','mode']} for e in x['entries']]))
code=SNAP[:SNAP.index('x=dict(')]+ '\nreq='+repr(req)+r'''
out=[]
for r in req:
 o=dict(asset=r['asset'],source=r['source'],files=0,directories=0,symlinks=0,allocated=0,logical=0,identity_mismatches=[],all_identity_match=True)
 for f in r['entries']:
  if '..' in Path(f['path']).parts:o['all_identity_match']=False;continue
  p=r['source']+'/'+f['path'];s=meta(p)
  if f['type']=='file':o['files']+=1;o['allocated']+=s.get('allocated',0);o['logical']+=s.get('size',0)
  elif f['type']=='directory':o['directories']+=1
  else:o['symlinks']+=1
  keys=['dev','inode','size','mtime_ns','ctime_ns','uid','gid']
  if not all(s.get(k)==f.get(k) for k in keys):o['all_identity_match']=False;o['identity_mismatches'].append(dict(path=p,fields=[k for k in keys if s.get(k)!=f.get(k)]))
 out.append(o)
print(json.dumps(out))
'''
save('evidence/EXISTING_FULL_RESULTS_CURRENT_SOURCE_IDENTITY_AUDIT.json',remote('hrl',code,60))
req=[dict(asset_id='V3_'+r['transaction'],source=r['source_root'],target=r['target_mount_alias_root']+'/'+r['archive']) for r in json.loads((R/'references/V3_BOTH_BATCHES_RECOVERY_INDEX_20261020.json').read_text(encoding='utf8'))['assets']]
for a in ['EP_L2_E057','DTC_L1_AD_GEMM']:
 r=json.loads((R/'references'/(a+'_RECOVERY_POINTER.json')).read_text(encoding='utf8'));req.append(dict(asset_id=a,source=r['source_root'],target=r['mount_path_on_174new']))
for alias,which in [('hrl','source'),('hrl-174-new','target')]:
 code=SNAP[:SNAP.index('x=dict(')]+'\nreq='+repr(req)+'\nprint(json.dumps([dict(asset_id=r["asset_id"],stat=meta(r['+repr(which)+'])) for r in req]))'
 save('evidence/V3_AND_FULL_RESULT_'+which.upper()+'_CURRENT_LOCATORS.json',remote(alias,code,60))
print('results and releasedV3 locators checked')
