from pathlib import Path
import json,hashlib
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');path=R/'control/EXPANDED_OBJECTS.json';objects=json.loads(path.read_text());bundles=json.loads((R/'control/EXPANDED_BUNDLES.json').read_text())
cat=json.loads(Path('/root/data/ep_dtc_trace_migration_20261024_v1/controls/ASSET_CATALOG.json').read_text())
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
programs={'DTC_BICG':('PolyBench/GPU','BICG'),'DTC_BTREE':('Rodinia','b+tree'),'DTC_BTREE_DERIVED':('Rodinia','b+tree'),'DTC_2DCONVOLUTION':('PolyBench/GPU','2DCONV'),'DTC_HOTSPOT1':('Rodinia','hotspot'),'DTC_HOTSPOT_V2_SOURCE_PROFILE':('Rodinia','hotspot'),'DTC_ATAX':('PolyBench/GPU','ATAX'),'DTC_GESUMMV':('PolyBench/GPU','GESUMMV'),'DTC_AD_GEMM':('PolyBench/GPU','GEMM'),'DTC_DWT2D':('Rodinia','dwt2d'),'DTC_GAUSSIAN':('Rodinia','gaussian'),'DTC_LUD':('Rodinia','lud'),'DTC_LEGACY_NN':('Rodinia','nn'),'DTC_MRI_Q':('Parboil','mri-q'),'EP_SGEMM':('Parboil','sgemm'),'EP_FWT_7_21':('CUDA Samples','fastWalshTransform'),'EP_CONVOLUTION_SEPARABLE':('CUDA Samples','convolutionSeparable'),'EP_CFD_097K':('Rodinia','cfd'),'EP_SAD':('Parboil','sad'),'EP_VECTORADD_S':('CUDA Samples','vectorAdd')}
versions={'CUDA Samples':'cudasdk/9.1 path; exact capture provenance not newly certified','PolyBench/GPU':'GPU 1.0 source mapping; capture path 11.0 is toolchain label','Parboil':'Parboil; capture path 11.0 is not suite revision proof','Rodinia':'3.1'}
for a in cat['assets']:
 su,program=programs[a['asset_id']];members=[]
 for m in a['members']:
  p=Path(a['mount_tree'])/m['relative_path'];s=p.stat();assert [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns]==m['verified_tree_identity']
  members.append({'relative_path':m['relative_path'],'sha256':m['sha256'],'size':m['size']})
  o=objects.setdefault(m['sha256'],{'sha256':m['sha256'],'size':m['size'],'sources':[]})
  o['storage']={'path':str(p),'kind':'PRIOR_VERIFIED_TRUE164_OBJECT','proof_reference':a['proof_reference'],'expected_identity':m['verified_tree_identity']}
 identity={'suite':su,'program':program,'version':versions[su],'extent':'NO_FRACTION_LABEL_NOT_FULL_CAPTURE_CERTIFIED','members':sorted(members,key=lambda m:m['relative_path'])}
 bid=hashlib.sha256(canon(identity)).hexdigest();b=next((b for b in bundles if b['bundle_id']==bid),None)
 if not b:
  b={'bundle_id':bid,**identity,'source_aliases':[],'ordered_kernel_members':a['ordered_kernel_members'],'scientific_qualification_granted':False,'access_scope':'ALL_PROJECTS_IN_174NEW_NAMESPACE'};bundles.append(b)
 b.setdefault('prior_asset_aliases',[]).extend(a['aliases']);b['source_aliases'].append({'host':'PRIOR164','path':a['source_root']+'/kernelslist.g','proof_reference':a['proof_reference'],'scientific_contexts':a['scientific_contexts'],'source_keep':True})
path.write_text(json.dumps(objects,indent=2)+'\n');(R/'control/EXPANDED_BUNDLES.json').write_text(json.dumps(bundles,indent=2)+'\n')
print(json.dumps({'all20_prior_assets_adopted':True,'content_objects':len(objects),'bundles':len(bundles)}))
