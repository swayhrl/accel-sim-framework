from pathlib import Path
import json,hashlib,datetime,re
b=Path('/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection');out={'observed_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':[],'bounded_absence_checks':{}}
apps=['backprop','cfd','kmeans','nn','nw','pathfinder','streamcluster']
for v in ['2.0-ft','3.1']:
 for app in apps:
  p=b/'src/cuda/rodinia'/v/('cuda' if v=='3.1' else '')/app
  if not p.exists():continue
  for z in sorted(p.iterdir()):
   if z.is_file() and z.stat().st_size<150000 and z.suffix not in ['.o','.jpg','.png']:
    by=z.read_bytes();t=by.decode('utf-8','replace');out['sources'].append({'version':v,'program':app,'path':str(z),'bytes':len(by),'sha256':hashlib.sha256(by).hexdigest(),'text':t})
for z in [b/'src/cuda/rodinia/2.0-ft/README.md',b/'get_data.sh',b/'.gitmodules',b/'src/README.md',Path('/root/workspace/offline-sim-v1/accel-sim-framework/util/job_launching/apps/define-all-apps.yml')]:
 by=z.read_bytes();out['sources'].append({'program':'collection','path':str(z),'bytes':len(by),'sha256':hashlib.sha256(by).hexdigest(),'text':by.decode('utf-8','replace')})
for z in [b/'data_dirs',b/'data_dirs/cuda/rodinia',b/'data_dirs/cuda/rodinia/3.1',b/'data_dirs/cuda/rodinia/2.0-ft']:
 out['bounded_absence_checks'][str(z)]={'exists':z.exists(),'scope':'Only expected collection data_dirs paths checked; not a global dataset absence assertion'}
print(json.dumps(out))
