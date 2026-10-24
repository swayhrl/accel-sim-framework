from pathlib import Path,PurePosixPath
import json,gzip,hashlib,collections,re,decimal
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');NAS=Path('/root/share/mnt164/huangrulin/traces')
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def put(n,x):(R/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
objects=json.loads((R/'control/EXPANDED_OBJECTS.json').read_text());bundles=json.loads((R/'control/EXPANDED_BUNDLES.json').read_text());batches=[];issues=[]
poly={'2dconvolution':'2DCONV','3dconvolution':'3DCONV','2mm':'2MM','3mm':'3MM','atax':'ATAX','bicg':'BICG','correlation':'CORR','covariance':'COVAR','fdtd2d':'FDTD-2D','gemm':'GEMM','gesummv':'GESUMMV','gramschmidt':'GRAMSCHM','mvt':'MVT','syr2k':'SYR2K','syrk':'SYRK'}
def classify(path):
 l=path.lower()
 if '/polybench-' in '/'+l:
  p=re.search(r'polybench-([^/]+)',l)[1];return 'PolyBench/GPU',poly.get(p,p),'GPU 1.0 source mapping; capture path 11.0 is toolchain label'
 if '/parboil-' in '/'+l:return 'Parboil',re.search(r'parboil-([^/]+)',l)[1],'Parboil; capture path 11.0 is not suite revision proof'
 if 'cudasdk/' in l:
  part=l.split('cudasdk/',1)[1].split('/');p=part[1] if part[0]=='9.1' else part[0]
  names={'vectoradd':'vectorAdd','convolutionseparable':'convolutionSeparable','fastwalshtransform':'fastWalshTransform','blackscholes':'BlackScholes','mergesort':'mergeSort','scalarprod':'scalarProd','sortingnetworks':'sortingNetworks'}
  return 'CUDA Samples',names.get(p,p),'cudasdk/9.1 path; exact capture provenance not newly certified'
 m=re.search(r'([a-z0-9_+]+)-rodinia-(3\.1|2\.0-ft)',l)
 if m:return 'Rodinia',m[1],m[2]
 return None,None,None
for ap in sorted((R/'control').glob('ARCHIVE_[0-9]*.json.gz')):
 d=json.loads(gzip.decompress(ap.read_bytes()));members={};conflicts=set()
 for row in d['members']:
  name=PurePosixPath(row['archive_member']).as_posix()
  if name in members and members[name].get('sha256')!=row.get('sha256'):conflicts.add(name)
  else:members.setdefault(name,row)
 pending={}
 for name,entry in members.items():
  if PurePosixPath(name).name!='kernelslist.g' or not entry.get('small_bytes_hex'):continue
  su,program,version=classify(name)
  if not su:issues.append({'archive':d['path'],'entry':name,'reason':'UNASSIGNED_SUITE'});continue
  text=bytes.fromhex(entry['small_bytes_hex']).decode(errors='strict');order=[l for raw in text.splitlines() for l in [raw.strip()] if l and not l.startswith('#') and not l.lower().startswith(('memcpy','cudamemcpy'))]
  required=['kernelslist.g']+list(dict.fromkeys(order));selected=[];bad=[]
  for rel in required:
   if PurePosixPath(rel).is_absolute() or '..' in PurePosixPath(rel).parts or '\\' in rel:bad.append(rel);continue
   full=(PurePosixPath(name).parent/rel).as_posix();r=members.get(full)
   if not r or full in conflicts or not r.get('sha256') or not r.get('safe') or r['size']==0:bad.append(rel)
   else:selected.append((rel,r))
  if bad or not order:issues.append({'archive':d['path'],'entry':name,'reason':'INCOMPLETE_OR_CONFLICTING_INPUT','members':bad});continue
  extent='FRACTION_OR_TRIM_PATH' if any(t in name.lower() for t in ['1of','fraction','trim','interrupted']) else 'NO_FRACTION_LABEL_NOT_FULL_CAPTURE_CERTIFIED'
  logical=[{'relative_path':rel,'sha256':r['sha256'],'size':r['size']} for rel,r in selected]
  identity={'suite':su,'program':program,'version':version,'extent':extent,'members':sorted(logical,key=lambda m:m['relative_path'])};bid=hashlib.sha256(canon(identity)).hexdigest()
  provenance={'host':'174_ARCHIVE','path':d['path']+'!/'+name,'archive_sha256':d['archive_sha256'],'archive_member':entry['archive_member'],'kernel_launches':len(order),'source_keep':True}
  previous=next((b for b in bundles if b['bundle_id']==bid),None)
  if previous:previous['source_aliases'].append(provenance)
  else:bundles.append({'bundle_id':bid,**identity,'source_aliases':[provenance],'ordered_kernel_members':order,'scientific_qualification_granted':False,'access_scope':'ALL_PROJECTS_IN_174NEW_NAMESPACE'})
  for rel,row in selected:
   sha=row['sha256']
   if sha in objects:
    assert objects[sha]['size']==row['size'];continue
   objects[sha]={'sha256':sha,'size':row['size'],'sources':[{'host':'174_ARCHIVE','archive':d['path'],'archive_member':row['archive_member'],'archive_sha256':d['archive_sha256']}]} ;pending[sha]=row
 if not pending:continue
 rows=[]
 for sha,row in sorted(pending.items(),key=lambda x:x[1]['order']):
  # A content object gets one immutable path even when several archive aliases
  # contain the same byte sequence.
  rows.append({'relative_path':'archive_objects/'+sha,'archive_member':row['archive_member'],'size':row['size'],'sha256':sha,'header_prefix_hex':row['header_prefix_hex'],'uid':row['uid'],'gid':row['gid'],'mode':row['mode'],'mtime_ns':int(decimal.Decimal(row['mtime'])*1000000000),'ctime_ns':0,'dev':0,'inode':0,'type':'file','nlink':1})
 oid=hashlib.sha256(canon({'archive_sha256':d['archive_sha256'],'members':rows})).hexdigest();mid=oid[:20]
 m={'schema':'SHARED_SM70_ARCHIVE_CAS_PAYLOAD_V1','payload_kind':'CAS_FILES_V1','source_backend':'archive','freeze_status':'FROZEN_ARCHIVE_FULL_SHA','primary_asset_id':'ARCHIVE_'+mid,'object_id':oid,'source_root':'/','source_root_identity':{'uid':0,'gid':0,'mode':493,'mtime_ns':0,'metadata_policy':'VIRTUAL_PAYLOAD_NAMESPACE'},'archive_path':d['path'],'archive_identity':d['archive_identity'],'archive_sha256':d['archive_sha256'],'members':rows,'source_data_bytes':sum(r['size'] for r in rows),'ordered_kernel_members':[],'entry_name':'NOT_AN_APPLICATION_INPUT','commandlist_bytes_hex':'','new_true164_bundle':'/home/shared/huangrulin/traces/bundles/_payload/'+mid,'reuse':False,'source_host':'174'}
 path=R/'manifests'/(mid+'.json');path.write_text(json.dumps(m,indent=2)+'\n');batches.append({'manifest':str(path),'host':'174_ARCHIVE','id':mid,'bytes':m['source_data_bytes'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 for row in rows:objects[row['sha256']]['storage']={'path':str(NAS/'bundles/_payload'/mid/'tree'/row['relative_path']),'kind':'NEW_TRUE164_ARCHIVE_CAS_PAYLOAD','batch_id':mid}
put('control/ALL_OBJECTS.json',objects);put('control/ALL_BUNDLES.json',bundles);put('control/ARCHIVE_BATCHES.json',batches);put('control/ARCHIVE_INPUT_ISSUES.json',issues)
summary={'assets_including_archive_findings':len(bundles),'unique_content_objects':len(objects),'new_archive_bytes':sum(b['bytes'] for b in batches),'archive_batches':len(batches),'archive_input_issues':len(issues)}
put('control/ARCHIVE_FROZEN_BUDGET.json',summary);print(json.dumps(summary),flush=True)
