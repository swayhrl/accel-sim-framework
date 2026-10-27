from pathlib import Path
import json,hashlib,os
out={}
paths=['/root/workspace/offline-sim-v1/cache/assets/official/rodinia_2.0-ft/rodinia_2.0-ft/9.1/backprop-rodinia-2.0-ft/4096___data_result_4096_txt', '/root/workspace/offline-sim-v1/cache/assets/official/rodinia_2.0-ft/rodinia_2.0-ft/9.1/kmeans-rodinia-2.0-ft/_i_data_400_txt__g_data_400_result_txt__o', '/root/workspace/offline-sim-v1/cache/assets/official/rodinia_2.0-ft/rodinia_2.0-ft/9.1/nn-rodinia-2.0-ft/__data_filelist_4_3_30_90___data_filelist_4_3_30_90_result_txt', '/root/workspace/offline-sim-v1/cache/assets/official/rodinia_2.0-ft/rodinia_2.0-ft/9.1/nw-rodinia-2.0-ft/128_10___data_result_128_10_txt', '/root/workspace/offline-sim-v1/cache/assets/official/rodinia_2.0-ft/rodinia_2.0-ft/9.1/pathfinder-rodinia-2.0-ft/1000_20_5___data_result_1000_20_5_txt']
paths+=['/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1','/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/data','/root/workspace/offline-sim-v1/cache/assets/official/rodinia_2.0-ft']
for name in paths:
 p=Path(name);rec={'exists':p.exists(),'children':[]}
 if p.exists():
  for z in p.iterdir():
   rec['children'].append({'path':str(z),'link':os.readlink(z) if z.is_symlink() else None,'exists':z.exists(),'dir':z.is_dir(),'bytes':z.stat().st_size if z.exists() and not z.is_dir() else None})
  d=p/'data';rec['data_target']=str(d.resolve(strict=False));rec['data_exists']=d.exists()
  if d.exists() and d.is_dir():rec['data_children']=[{'path':str(z),'bytes':z.stat().st_size if z.is_file() else None} for z in d.iterdir()][:50]
 out[name]=rec
print(json.dumps(out,indent=2))
