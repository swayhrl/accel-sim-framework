"""Pure read-only MS-only application NI comparator. No science/ledger writes."""
import copy,gzip,hashlib,io,json,pathlib,zlib
P=pathlib.Path
X=P('/root/data/ep_l2_full_workload_performance_20261027_v1/execution_performance_first_20261103_v1')
ROOT=X/'retention';NATIVE=P('/root/data/ep_l2_dtc_l1_native_v2')
REG=NATIVE/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'
GOAL='EP_L2_PF_RETENTION_CLASS_FWT_GEMM_20261103_V1'
AUTH=X/'control/NI011_USER_AMENDMENT_AUTHORIZATION.json'
INDEX=X/'control/APPROVED_CELL_INDEX_V2_NI011.json'
SOURCE={'core_source_commit':'78f4b59e865b136eede74df74c44c210f5b4ca04','framework_source_commit':'9dd1ee57a83d83b56b7874bc7c716185ab52c8f7','vendor_pybind11_commit':'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b','binary_sha256':'78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a','archive_sha256':'e5a743a2bb796d82f58109251f43d5c1997d5c1f7fdeac61213416da3835b697'}
MS='-gpgpu_ep_l2_ms_observer';B0='-gpgpu_ep_l2_b0_stats';M0A='-gpgpu_ep_l2_m0a_stats'
FIELDS=('cycles','instructions','CTA','kernel_count','hardware_drained','ordered_kernel_identity','FT_TVD_resource_closure')
SELECT={('EPL2FTV1','SUMMARY'),('EPL2FTV1','TERMINAL'),('EPL2B0V1','INVARIANT'),('EPL2TVDV2','SUMMARY'),('EPL2TVDV3','METADATA_COST'),('EPL2STRUCTV1','CONFIG'),('EPL2STRUCTV1','BANK_PEAK'),('EPL2STRUCTV1','WB_QUOTA')}
class Hold(Exception):pass
class Invalid(Exception):pass
def need(value,message):
 if not value:raise Invalid(message)
def _pairs(items):
 d={}
 for k,v in items:need(k not in d,'duplicate JSON key');d[k]=v
 return d
def read(p):return json.loads(P(p).read_bytes(),object_pairs_hook=_pairs,parse_constant=lambda x: (_ for _ in ()).throw(Invalid('nonfinite JSON')))
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def exact(r):need(sha(r['path'])==r['sha256'],'immutable ref drift '+r['path']);return read(r['path'])
def _result(status,**kw):return dict(schema='EP_MAIN_PF_RETENTION_MS_APPLICATION_NI_V1',status=status,NI_scope='MS_ONLY_APPLICATION_NI',B0_M0a_application_NI='NOT_PROVEN',scientific_start_or_acceptance_granted=False,**kw)
class _HashReader:
 def __init__(self,f,cap):self.f=f;self.h=hashlib.sha256();self.n=0;self.cap=cap
 def read(self,n=-1):
  b=self.f.read(n);self.n+=len(b);need(self.n<=self.cap,'compressed raw bound exceeded');self.h.update(b);return b
 def seekable(self):return False
 def readable(self):return True
 def tell(self):return self.n

def _projection(lines,nslices):
 h=hashlib.sha256();common=hashlib.sha256();common_counts={};counts={};last={};maxline=1024*1024
 for line in lines:
  need(len(line)<=maxline,'raw line bound exceeded')
  if isinstance(line,bytes):line=line.decode('utf-8','strict')
  a=line.strip().split('|')
  # Preserve every EPL2 mechanism/resource family, excluding only the exact MS observer record families.
  if a[0].startswith('EPL2') and a[0] not in ['EPL2MSV1','EPL2MSV2']:
   common.update((line.strip()+'\n').encode());common_counts[a[0]]=common_counts.get(a[0],0)+1
  if len(a)<2 or (a[0],a[1]) not in SELECT:continue
  fields={}
  for token in a[2:]:
   if '=' in token:
    k,v=token.split('=',1);need(k not in fields,'duplicate record field');fields[k]=v
  need('slice' in fields,'selected record without slice')
  sl=int(fields['slice']);need(0<=sl<nslices,'selected record slice domain')
  if a[:2]==['EPL2B0V1','INVARIANT'] and fields.get('kernel_uid')!=str(2**64-1):continue
  kind=a[0]+'|'+a[1];key=kind+'|'+str(sl);counts[kind]=counts.get(kind,0)+1
  last[key]=fields;h.update((json.dumps([kind,sl,fields],sort_keys=True,separators=(',',':'))+'\n').encode())
 for prefix,tag in SELECT:
  kind=prefix+'|'+tag
  need(counts.get(kind,0)>=nslices and counts[kind]%nslices==0,'missing/incomplete '+kind)
  for sl in range(nslices):need(kind+'|'+str(sl) in last,'missing terminal slice '+kind)
 for sl in range(nslices):
  t=last['EPL2FTV1|TERMINAL|'+str(sl)];i=last['EPL2B0V1|INVARIANT|'+str(sl)]
  for k in ['hardware_drained','requester_exact_once']:need(t.get(k)=='1','FT terminal '+k)
  for k in ['requester_live','pending_lower_reads','pending_returns','pending_responses']:need(t.get(k)=='0','FT terminal '+k)
  need(t.get('unique_requesters')==t.get('responses'),'FT exactly once counts')
  for k in ['line_mshr_used','descriptor_used','wad_live','resident_pending','bypass_live','bank_pending','payload_double_owner']:need(i.get(k)=='0','B0 terminal '+k)
  for k in ['resident_tag_payload_consistent','terminal_clean']:need(i.get(k)=='1','B0 terminal '+k)
  need(int(i['descriptor_free'])==int(i['descriptor_capacity']),'descriptor pool not free')
 return {'common_non_MS_records_sha256':common.hexdigest(),'common_non_MS_record_counts':common_counts,'semantic_sha256':h.hexdigest(),'record_counts':counts,'last_records':last,'complete':True,'scope':'ALL_AVAILABLE_FT_SUMMARY_TERMINAL_B0_FINAL_INVARIANT_TVD2_TVD3_STRUCT_FIELDS; MS_RECORDS_ONLY_EXCLUDED'}

def _raw_projection(spec,point):
 r=point['raw_stream_receipt'];need(r.get('complete_compressed_stream') is True and r.get('truncated') is False,'incomplete raw receipt')
 p=P(r['path']);need(p.is_file(),'new NI raw missing')
 stored=r['stored_bytes'];logical=r['raw_bytes'];need(0<stored<=spec['limits']['result_bytes'] and 0<logical<=2**31,'bounded new NI raw required')
 hh=hashlib.sha256();crc=0;n=0
 with p.open('rb') as stream:
  tee=_HashReader(stream,stored)
  with gzip.GzipFile(fileobj=tee,mode='rb') as gz:
   def lines():
    nonlocal crc,n
    while True:
     b=gz.readline(1024*1024+1)
     if not b:break
     n+=len(b);need(n<=logical,'decompressed raw bound exceeded');hh.update(b);crc=zlib.crc32(b,crc);yield b
   out=_projection(lines(),spec['geometry']['slices'])
  need(tee.n==stored and tee.h.hexdigest()==r['stored_sha256'],'stored raw digest/size mismatch')
 need(n==logical and hh.hexdigest()==r['raw_sha256'] and crc==r['raw_crc32'],'logical raw SHA/CRC/size mismatch')
 out['raw_read_passes']=1;out['raw_stored_sha256']=r['stored_sha256'];return out

def _closed(cohort,request):
 if cohort not in request.get('consumed',{}):raise Hold('cohort not consumed')
 row=copy.deepcopy(request['consumed'][cohort])
 if row.get('state')!='CLOSED_ACCEPTED':raise Hold('official cohort not CLOSED_ACCEPTED')
 sp=ROOT/'cases'/cohort/'control/FROZEN_SPEC.json';spec=read(sp)
 need(sha(sp)==request['admitted_specs'][cohort],'official registered spec drift')
 point=exact(row['accepted_point_ref']);done=exact(row['done_ref']);bundle=exact(point['validation_ref']);archive=exact(row['archive_receipt_ref'])
 need(point['spec_ref']['path']==str(sp) and point['spec_ref']['sha256']==sha(sp),'point/spec mismatch')
 need(point['done_ref']==row['done_ref'],'point/DONE ref mismatch')
 need(point['validation_ref']==row['validation_ref'],'point/bundle ref mismatch')
 need(point['uuid']==row['uuid']==done['uuid']==archive['uuid'],'uuid population mismatch')
 need(point['cohort']==archive['cohort']==cohort,'cohort population mismatch')
 need(point['mode']==spec['mode'],'official point/spec mode mismatch')
 need(done==read(P(point['validation_ref']['path']).parent/'NATIVE_EXIT.json'),'official DONE/EXIT mismatch')
 if archive.get('status')!='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS':raise Hold('mandatory archive not closed')
 restores=archive.get('native_restores',[])
 if len(restores)!=2 or any(x.get('status')!='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS' for x in restores):raise Hold('two independent native restores absent')
 need(len({x['target'] for x in restores})==2,'restore targets not independent')
 need('/mnt164/' in archive['archive_ref']['path'] and archive.get('source_keep') is True,'archive true164/SourceKEEP')
 need(all(x['archive_sha256']==archive['archive_ref']['sha256'] for x in restores),'restore SHA population')
 exact(archive['manifest_ref']) # Small immutable manifest only, never rehash result tar/Trace.
 need(point['status']=='EP_FULL_PERF_APPLICATION_ACCEPTED','official accepted-point status')
 need(bundle['hardware_drained'] is True and point['hardware_drained'] is True,'accepted drain false')
 need(bundle['source_identity']==point['source_identity']==spec['source_identity']==SOURCE,'exact Source78 identity')
 return dict(cohort=cohort,row=row,spec=spec,point=point,bundle=bundle,archive=archive,point_ref=row['accepted_point_ref'],done_ref=row['done_ref'],spec_ref=ref(sp),projection=None)

def _compare_snapshots(off,on):
 a,b=off['spec'],on['spec'];pa,pb=off['point'],on['point'];ba,bb=off['bundle'],on['bundle']
 need(a['source_identity']==b['source_identity']==SOURCE,'source identity mismatch')
 need(a['mode']==b['mode'] and a['mode'] in ['WV_CLEAN_ONLY','WV_DIRTY_ONLY'],'same retention mode required')
 need(a['input_identity_sha256']==b['input_identity_sha256'],'input mismatch')
 need(a['geometry']==b['geometry'] and a['geometry']=={'line_bytes':128,'sets':32,'slices':64,'ways':8},'geometry mismatch')
 need(a['observer_env']==b['observer_env'],'observer environment mismatch')
 ao=a['expected_effective_options'];bo=b['expected_effective_options'];need(len(ao)==len(bo)==282 and set(ao)==set(bo),'282 exact options required')
 need(ao[MS]=='0' and bo[MS]=='1' and ao[B0]==bo[B0]==ao[M0A]==bo[M0A]=='1','MS-only011/111 required')
 need({k:v for k,v in ao.items() if k!=MS}=={k:v for k,v in bo.items() if k!=MS},'other281 options differ')
 for spec,bundle,point in [(a,ba,pa),(b,bb,pb)]:
  for k in ['cycles','instructions','CTA','kernel_count','hardware_drained']:need(point[k]==bundle[k],'point/bundle '+k+' mismatch')
  need(point['hardware_drained'] is True,'hardware not drained')
  need(bundle['application']['actual_options']==spec['expected_effective_options'],'actual option echo mismatch')
  need(point['input_identity_sha256']==spec['input_identity_sha256'],'point input mismatch')
  need(point['instructions']==spec['expected_instructions'] and point['CTA']==spec['expected_CTA'],'complete application population')
 equal={k:pa[k]==pb[k] for k in FIELDS[:5]}
 # Preserve full ordered scopes/catalog, not an unordered set of kernel names.
 ordered_fields=['all_unique_kernel_members','expected_kernel_launches','expected_kernel_scopes','command_count']
 equal['ordered_kernel_identity']=all(a[k]==b[k] for k in ordered_fields) and ba['application']['ordered_kernel_catalog']==bb['application']['ordered_kernel_catalog']
 need(all(equal.values()),'application/order equality mismatch')
 ap=off['projection'] if off.get('projection') is not None else _raw_projection(a,pa)
 bp=on['projection'] if on.get('projection') is not None else _raw_projection(b,pb)
 # Equal selected raw fields are stronger than dropping all mechanism_metrics.
 equal['FT_TVD_resource_closure']=ap['complete'] is True and bp['complete'] is True and ap['semantic_sha256']==bp['semantic_sha256'] and ap['record_counts']==bp['record_counts'] and ap['last_records']==bp['last_records'] and ap['common_non_MS_records_sha256']==bp['common_non_MS_records_sha256'] and ap['common_non_MS_record_counts']==bp['common_non_MS_record_counts']
 need(equal['FT_TVD_resource_closure'],'FT/TVD/resource common semantics differ')
 return _result('PASS_MS_ONLY_APPLICATION_NI',mode=a['mode'],source_identity=SOURCE,input_identity_sha256=a['input_identity_sha256'],geometry=a['geometry'],primary_point_ref=on['point_ref'],off_point_ref=off['point_ref'],equal_fields=equal,semantic_projection={'off':ap,'on':bp},OFF='011',ON='111')

def compare(off_cohort,on_cohort):
 """Return a receipt only. Caller alone may persist/review it; this writes nothing."""
 try:
  for case in [off_cohort,on_cohort]:need(isinstance(case,str) and case and '/' not in case and '..' not in case,'invalid cohort')
  auth=read(AUTH);need(auth['status']=='USER_APPROVED_EXACT_NI011_PRESTART_CONTRACT_AMENDMENT','NI011 user approval missing');exact(auth['approved_amendment_ref'])
  index=read(INDEX);need(exact(index['NI_amendment_authorization_ref'])==auth,'index NI authorization mismatch')
  cells={z['cohort']:z for z in index['cells'] if z['group']=='retention'};need(off_cohort in cells and on_cohort in cells,'outside approved exact cells')
  need(cells[off_cohort]['point']['observer_variant']=='OFF' and cells[on_cohort]['point']['observer_variant']=='ON','wrong ON/OFF arm')
  reg=read(REG);request=reg['registered_future_requests'].get(GOAL)
  if request is None:raise Hold('fresh request not registered')
  off=_closed(off_cohort,request);on=_closed(on_cohort,request);out=_compare_snapshots(off,on)
  # Other scopes may progress. Require only our two official rows/spec hashes stable.
  fresh=read(REG)['registered_future_requests'][GOAL]
  for v in [off,on]:need(fresh['consumed'][v['cohort']]==v['row'],'official terminal row changed during comparison');need(fresh['admitted_specs'][v['cohort']]==v['spec_ref']['sha256'],'registered spec changed during comparison')
  for v in [off,on]:exact(v['point_ref']);exact(v['done_ref']);exact(v['spec_ref'])
  out['NI_amendment_authorization_ref']=ref(AUTH);return out
 except (FileNotFoundError,KeyError,Hold) as e:return _result('HOLD',reason=str(e),equal_fields={k:False for k in FIELDS})
 except Exception as e:return _result('FAIL',reason=str(e),equal_fields={k:False for k in FIELDS})
