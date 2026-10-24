from pathlib import Path
import json,re,collections,hashlib,csv,datetime,os,gzip
P=Path('/root/data/ep_l2_main_20261023_v1/asset_audit_20261024_v2')
W=Path('/root/data/ep_l2_main_20261023_v1/worktree')
O=W/'docs/ep_l2/operations/ep_main_account_workload_audit_20261024_v2'
O.mkdir(exist_ok=True)
def put(n,x):
 b=(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode()
 if len(b)>1000000:
  (O/(n+'.gz')).write_bytes(gzip.compress(b,compresslevel=6,mtime=0))
  if (O/n).exists():(O/n).unlink()
 else:(O/n).write_bytes(b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
cuda=['BlackScholes','convolutionSeparable','fastWalshTransform','histogram','mergeSort','scalarProd','scan','sortingNetworks','transpose','vectorAdd']
poly={'2dconvolution':'2DCONV','2dconv':'2DCONV','3dconvolution':'3DCONV','3d':'3DCONV','3dconv':'3DCONV','2mm':'2MM','3mm':'3MM','atax':'ATAX','bicg':'BICG','correlation':'CORR','covariance':'COVAR','fdtd2d':'FDTD-2D','gemm':'GEMM','gesummv':'GESUMMV','gramschmidt':'GRAMSCHM','mvt':'MVT','syrk':'SYRK','syr2k':'SYR2K'}
old={'CUDA Samples':{'convolutionSeparable','fastWalshTransform','scan','vectorAdd'},'Parboil':{'sad','sgemm','spmv'},'PolyBench/GPU':{'GEMM','3MM'},'Rodinia':{'b+tree','bfs','cfd','dwt2d','hotspot'}}
def classify(x):
 p=x['path'];l=p.lower();su=x.get('suite');program=None;version='capture_path_reference'
 if 'cudasdk' in l:su='CUDA Samples'
 if su=='CUDA Samples':program=next((c for c in cuda if c.lower() in l),None);version='cudasdk/9.1 path; exact capture provenance not newly certified'
 elif su=='Rodinia':
  m=re.search(r'([a-z0-9_+]+)-rodinia-(3\.1|2\.0-ft)',l)
  if m:program=m[1].split('__')[-1];version=m[2]
  else:
   m=re.search(r'rodinia_(hotspot1|lud|dwt2d|bfs)',l);program=m[1] if m else None;version='unconfirmed'
  if program=='hotspot1':program='hotspot'
 elif su=='Parboil':
  m=re.search(r'parboil[-_](mri-gridding|mri-q|bfs|cutcp|histo|lbm|sad|sgemm|spmv|stencil|tpacf)',l);program=m[1] if m else None;version='Parboil; capture path 11.0 is not suite revision proof'
 elif su=='PolyBench/GPU':
  for s in re.findall(r'polybench[-_]([a-z0-9]+)',l):
   if s in poly:program=poly[s]
  version='GPU 1.0 source mapping; capture path 11.0 is toolchain label'
 return su,program,version
def extent(p):return 'FRACTION_OR_TRIM_PATH' if any(t in p.lower() for t in ['1of','fraction','trim','interrupted']) else 'NO_FRACTION_LABEL_NOT_FULL_CAPTURE_CERTIFIED'
raw={h:json.loads((P/(h+'.json')).read_text()) for h in ['174','174-new']}
tmp={h:json.loads((P/(h+'_temporary.json')).read_text()) for h in raw}
exact={h:json.loads((P/(h+'_exact.json')).read_text()) for h in raw}
records=[];objects={};groups=collections.defaultdict(list);catalog=json.loads((P/'native_migration_current_metadata.json').read_text())
for h in raw:
 rows={x['path']:x for x in exact[h]['inputs']}
 for x in tmp[h]['commandlists']:
  if x['path'].endswith('kernelslist.g') and (x.get('suite') or 'cudasdk' in x['path'].lower()):rows.setdefault(x['path'],x)
 for x in rows.values():
  su,pr,v=classify(x)
  if not su:continue
  member_keys=[]
  for m in x.get('members',[]):
   if m.get('exists'):
    st=m['stat'];key=f"{h}:{st['dev']}:{st['inode']}"
    entry={k:m[k] for k in ['path','realpath','readable','regular','stat'] if k in m}
    if key not in objects:objects[key]=dict(host=h,stat=st,example_path=m['path'],realpath=m.get('realpath'),aliases=[])
    objects[key]['aliases'].append(m['path']);member_keys.append(key)
   else:member_keys.append({'missing_path':m['path'],'error':m.get('error')})
  r=dict(host=h,suite=su,program=pr,version=v,path=x['path'],realpath=x.get('realpath'),exists=x.get('exists',True),complete_by_metadata=x.get('complete_by_metadata',False),commandlist_sha256=x.get('sha256'),commandlist_stable=x.get('stable'),kernel_launches=x.get('kernel_launches'),unique_members=len(x.get('members',[])),missing_members=sum(not m.get('exists') for m in x.get('members',[])),logical_member_bytes=sum(m.get('stat',{}).get('bytes',0) for m in x.get('members',[])),extent=extent(x['path']),error=x.get('error'),member_object_keys=member_keys,capture_scripts=x.get('capture_scripts',[]),old_EP_named_program=pr in old.get(su,set()))
  records.append(r)
  if pr:groups[(su,pr,v if su=='Rodinia' else '')].append(r)
coverage=[]
for (su,pr,ver),rs in sorted(groups.items()):
 r=dict(suite=su,program=pr,version=ver,old_EP_named_program=pr in old.get(su,set()))
 for h in raw:
  valid=[x for x in rs if x['host']==h and x['complete_by_metadata']]
  nonfraction=[x for x in valid if x['extent'].startswith('NO_FRACTION')]
  frac=[x for x in valid if x['extent']=='FRACTION_OR_TRIM_PATH']
  # Prefer canonical original input paths over result aliases.
  best=sorted(nonfraction or frac,key=lambda x:(not any(t in x['path'] for t in ['decoupled-l2-pretraces/','c2p-polybench-full-20260821/','parboil.current.small8.stage/']),len(x['path'])))
  r[h]=dict(complete_path_count=len(valid),nonfraction_label_paths=len(nonfraction),fraction_label_paths=len(frac),example_entry=best[0]['path'] if best else None,example_kernel_launches=best[0]['kernel_launches'] if best else None)
 coverage.append(r)
put('PROGRAM_COVERAGE.json',coverage)
put('EXACT_INPUT_INDEX.json',records)
for obj in objects.values():obj['aliases']=sorted(set(obj['aliases']))
put('TRACE_MEMBER_OBJECT_METADATA.json',objects)
put('NATIVE_MIGRATION_CURRENT_METADATA.json',catalog)
# Preserve only suite-relevant directory, link, source and archive metadata in Git.
suite_dir=collections.defaultdict(list);sources=collections.defaultdict(list);archives=[]
def relevant(p):return any(t in p.lower() for t in ['cudasdk','polybench','parboil','rodinia','cuda-samples','cuda_samples','/sdk/'])
for h in raw:
 for d in [raw[h],tmp[h]]:
  suite_dir[h].extend(x for x in d['directories'] if relevant(x['path']))
  sources[h].extend(d['source_files'])
  archives.extend(dict(host=h,**x,archive_opened=False) for x in d['archives'] if x.get('suite'))
put('SUITE_DIRECTORY_METADATA.json',suite_dir)
put('SOURCE_FILE_METADATA.json',sources)
put('ARCHIVE_PRESENCE_ONLY.json',archives)
put('SOURCE_AND_RAW_INPUT_ROOTS.json',{h:{k:v for k,v in json.loads((P/(h+'_source_inputs.json')).read_text()).items() if k!='supplemental_discovery'} for h in raw})
put('EXISTING_ARCHIVE_INDEXES_NOT_FRESH_CONTENT_PROOF.json',json.loads((P/'source_existing_archive_indexes.json').read_text()))
scan_summary={}
for h in raw:
 scan_summary[h]={}
 for stage,d in [('account',raw[h]),('temporary',tmp[h])]:
  scan_summary[h][stage]={k:d[k] for k in ['hostname','namespace','uid','utc','roots','exclusions','counts','elapsed_seconds','truncated','errors','pending_directories']}
  scan_summary[h][stage]['raw_capture_sha256']=sha(P/(h+('_temporary' if stage=='temporary' else '')+'.json'))
 scan_summary[h]['exact_requests']=len(exact[h]['inputs'])
 scan_summary[h]['exact_existing']=sum(x.get('exists',False) for x in exact[h]['inputs'])
 scan_summary[h]['exact_complete_by_metadata']=sum(x.get('complete_by_metadata',False) for x in exact[h]['inputs'])
put('SCOPE_AND_SCAN_RECEIPT.json',scan_summary)
with (O/'PROGRAM_COVERAGE.csv').open('w',newline='') as f:
 cols=['suite','program','version','old_EP_named_program','174_nonfraction_paths','174_fraction_paths','174_entry','174-new_nonfraction_paths','174-new_fraction_paths','174-new_entry']
 w=csv.DictWriter(f,fieldnames=cols,lineterminator="\n");w.writeheader()
 for r in coverage:w.writerow(dict(suite=r['suite'],program=r['program'],version=r['version'],old_EP_named_program=r['old_EP_named_program'],**{k:v for h in raw for k,v in [(h+'_nonfraction_paths',r[h]['nonfraction_label_paths']),(h+'_fraction_paths',r[h]['fraction_label_paths']),(h+'_entry',r[h]['example_entry'])]}))
for name in ['scan_assets.py','check_exact.py','build_report.py']:
 (O/name).write_bytes((P/name).read_bytes())
summary={}
for su in ['CUDA Samples','Rodinia','Parboil','PolyBench/GPU']:
 rows=[r for r in coverage if r['suite']==su and (su!='Rodinia' or r['version']=='3.1')]
 summary[su]={}
 for h in raw:
  summary[su][h]=dict(program_labels_with_trace=sum(r[h]['complete_path_count']>0 for r in rows),nonfraction_label_programs=[r['program'] for r in rows if r[h]['nonfraction_label_paths']],fraction_only_programs=[r['program'] for r in rows if not r[h]['nonfraction_label_paths'] and r[h]['fraction_label_paths']],new_to_old_EP_programs=[r['program'] for r in rows if not r['old_EP_named_program'] and r[h]['complete_path_count']])
put('SUMMARY.json',summary)
print(json.dumps(dict(summary=summary,record_count=len(records),member_objects=len(objects),catalog20_current_metadata_ok=all(x['current_metadata_ok'] for x in catalog)),ensure_ascii=False,indent=2))
