"""Private SM89 flat-COMMIT restore candidate. Existing manifests/parent refs stay byte-identical."""
from pathlib import Path
import argparse,hashlib,json,os,re,stat,time,resource,shutil,signal,math
LIB=Path('/root/share/mnt164/huangrulin/traces')
B=LIB/'rtx4080_sm89/bulk_20261024_v1'
OBJECTS=B/'objects'
AUTH=Path('/root/data/shared_trace_assets_platform_v3/authority/restore_one_sm89')
NATIVE=Path('/root/data/trace_assets_restore_one_sm89')
EVIDENCE=LIB/'receipts/sm89_restore_one_runs'
G=2**30;M=2**20
def need(x,m):
 if not x:raise RuntimeError('RESTORE_ONE_HOLD_'+m)
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def no_links(p):
 p=Path(p);need(p.is_absolute()and'..'not in p.parts,'ABSOLUTE_NO_PARENT_PATH')
 for q in[p,*p.parents]:need(not q.is_symlink(),'NO_SYMLINK')
 return p
def ident(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)

def mount_for(path):
 path=Path(path);matches=[]
 for line in Path('/proc/self/mountinfo').read_text().splitlines():
  left,right=line.split(' - ',1);fields=left.split();mp=Path(fields[4].replace('\\040',' '));after=right.split()
  if path.is_relative_to(mp):matches.append((len(mp.parts),dict(target=str(mp),fstype=after[0],source=after[1])))
 need(matches,'ACTUAL_MOUNT_METADATA')
 depth=max(x[0]for x in matches);rows=[v for n,v in matches if n==depth];need(len(rows)==1,'UNAMBIGUOUS_ACTUAL_MOUNT')
 return rows[0]

def digest64(s):return type(s)is str and re.fullmatch('[0-9a-f]{64}',s)is not None
def relative(s):
 p=Path(s);need(type(s)is str and s and not p.is_absolute()and'..'not in p.parts and'.'not in p.parts,'SAFE_RELATIVE_MEMBER');return p
def raw_json(p,maximum=8*M,account=None):
 p=no_links(p);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  a=os.fstat(fd);need(stat.S_ISREG(a.st_mode)and 0<a.st_size<=maximum,'SMALL_REGULAR_METADATA');raw=b''
  while len(raw)<=maximum:
   b=os.read(fd,min(65536,maximum+1-len(raw)))
   if not b:break
   raw+=b
  z=os.fstat(fd);need(ident(a)==ident(z)and len(raw)==a.st_size,'METADATA_SAME_FD')
 finally:os.close(fd)
 if account:account(len(raw),'metadata')
 def pairs(items):
  d={}
  for k,v in items:need(k not in d,'DUPLICATE_JSON_KEY');d[k]=v
  return d
 return json.loads(raw,object_pairs_hook=pairs),raw
def pinned(r,account=None):
 p=Path(r['path']);need(p.is_relative_to(LIB)and type(r['bytes'])is int and 0<r['bytes']<=8*M and digest64(r['sha256']),'PINNED_LIBRARY_METADATA')
 x,b=raw_json(p,account=account);need(len(b)==r['bytes']and sha(b)==r['sha256'],'RAW_METADATA_PIN');return x


def asset_id(a):
 need(type(a)is str and re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.-]{0,240}',a)is not None,'EXACT_SM89_ASSET_ID')
 return a

def exact_pointer_equal(expected,current):
 if type(expected)is not dict or type(current)is not dict or set(expected)!=set(current):return False
 timestamps={'unix','utc_unix','published_unix','tool_updated_unix'}
 for k in expected:
  if k in timestamps:
   if not all(type(v)in[int,float]and math.isfinite(v)for v in[expected[k],current[k]]):return False
  elif expected[k]!=current[k]:return False
 return True
def pointer(r,account):
 need(type(r['expected_pointer'])is dict,'FROZEN_FULL_EXPECTED_POINTER_DOCUMENT')
 current,raw=raw_json(r['pointer_ref']['path'],account=account)
 need(exact_pointer_equal(r['expected_pointer'],current),'EXACT_CURRENT_POINTER_SEMANTIC_FIELDS_TIMESTAMP_ONLY_TOLERANCE')
 return current

def catalog_pair(r,name,schema,account):
 need(Path(r['pointer_ref']['path'])==B/'catalog'/name,'EXACT_CURRENT_CATALOG_POINTER')
 ptr=pointer(r,account);sp=Path(r['snapshot_ref']['path'])
 need(sp==B/'catalog'/ptr['relative_path']and sp.is_relative_to(B/'catalog/versions')and r['snapshot_ref']['sha256']==ptr['sha256'],'CURRENT_CATALOG_SNAPSHOT_PIN')
 cat=pinned(r['snapshot_ref'],account);need(cat['schema']==schema and ptr['objects']==len(cat['objects']),'CURRENT_CATALOG_SCHEMA_COUNT')
 return cat
OBSERVED_ENGINEERING_SCAN_IDS={'SCAN_SMALL_SHORT_N262144_SEED2009_ITER1_PILOT_V1_ORDINARY_V1', 'SCAN_SMALL_HIERARCHICAL_N262144_SEED2009_ITER1_PILOT_V1_ORDINARY_V1', 'SCAN_SMALL_HIERARCHICAL_N262144_SEED2009_ITER1_PILOT_V1_DERIVED_CTA_STRIDE40_V1', 'SCAN_SMALL_SHORT_N262144_SEED2009_ITER1_PILOT_V1_DERIVED_CTA_STRIDE40_V1'}
OBSERVED_SCHEMALESS_PARENT_IDS={'C8_SDK42_REDUCTION_DEFAULT65536_SPECIALIST_A001_SAMEEXEC_INPUT_CAPTURE_V1_DERIVED_CTA_STRIDE40_V2', 'SCAN_SMALL_HIERARCHICAL_N262144_SEED2009_ITER1_PILOT_V1_DERIVED_CTA_STRIDE40_V1', 'SCAN_SMALL_SHORT_N262144_SEED2009_ITER1_PILOT_V1_DERIVED_CTA_STRIDE40_V1'}
def committed(req,aid,account):
 root=OBJECTS/asset_id(aid);r=req
 need(Path(r['commit_ref']['path'])==root/'COMMIT.json'and Path(r['manifest_ref']['path'])==root/'MANIFEST.json','EXACT_FLAT_OBJECT_METADATA_PATHS')
 c=pinned(r['commit_ref'],account);m=pinned(r['manifest_ref'],account)
 need(c['schema']in['RTX4080_SHARED_IMMUTABLE_COMMIT_V1','RTX4080_DERIVED_CTA_COMMIT_V1','RTX4080_DERIVED_COPY_ONLY_COMMIT_V1','RTX4080_ENGINEERING_PILOT_COMMIT_V1']and c['status']=='COMMITTED_VERIFIED'and c['asset_id']==m['asset_id']==aid,'COMMITTED_FLAT_REGISTERED_SCHEMA')
 if c['schema']=='RTX4080_ENGINEERING_PILOT_COMMIT_V1':
  need(aid in OBSERVED_ENGINEERING_SCAN_IDS and c['profile_use']=='ENGINEERING_SMALL_SCAN_PILOT_NOT_DEFAULT_SCAN17'and m.get('profile_use')==c['profile_use'],'EXACT_OBSERVED_ENGINEERING_SCAN_COMMIT_PROFILE')
 if 'all_members_closed_reopened_wholeSHA'in c:need(c['all_members_closed_reopened_wholeSHA']is True,'RECORDED_PRIOR_WHOLESHA_BOOL_MUST_BE_TRUE')
 supported_mf={None,'CURRENT3_ORIGINAL55_PRIVATE_MANIFEST_V1','RTX4080_DERIVED_COPY_ONLY_MANIFEST_V1','RTX4080_DERIVED_IDENTITY_PRIVATE_MANIFEST_V1','RTX4080_GAUSSIAN16_EXACT_PRIVATE_ARCHIVE_MANIFEST_V1','RTX4080_MVT4096_PRIVATE_MANIFEST_V1','RTX4080_SDK42_VECTOR50K_DERIVED_PRIVATE_MANIFEST_V1','RTX4080_SDK42_VECTOR50K_EXACT_PRIVATE_ARCHIVE_MANIFEST_V1','RTX4080_SHARED_IMMUTABLE_MANIFEST_V1','RTX4080_STREAMCLUSTER_DERIVED_MANIFEST_V1','RTX4080_STREAMCLUSTER_PRIVATE_MANIFEST_V1'}
 need(m.get('schema')in supported_mf and c['manifest_sha256']==r['manifest_ref']['sha256'],'EXACT_OBSERVED_RAW_MANIFEST_SCHEMA_AND_SHA_NOT_REENCODED')
 files=m['files'];names=[x['path']for x in files]
 need(len(names)==len(set(names)),'UNIQUE_MANIFEST_MEMBERS')
 for x in[c,m]:
  for key in['files','file_count']:
   if key in x and type(x[key])is not list:need(type(x[key])is int and x[key]==len(files),'RECORDED_FILE_COUNT')
 if 'kind'in m:need(c['kind']==m['kind'],'RECORDED_MANIFEST_KIND')
 for x in files:
  relative(x['path']);need(type(x['bytes'])is int and x['bytes']>=0 and digest64(x['sha256']),'EXACT_MEMBER_BYTES_SHA')
  need(not any(n!=x['path']and Path(n).is_relative_to(Path(x['path']))for n in names),'NO_MANIFEST_FILE_PARENT_COLLISION')
 total=sum(x['bytes']for x in files)
 need(total==c['logical_bytes']==m['logical_bytes'],'EXACT_ALL_FILES_LOGICAL_SUM')
 return root,c,m
def observed_schemaless_parent_refs(inp,aid,pid,request,proot,pc,pm,account):
 need(aid in OBSERVED_SCHEMALESS_PARENT_IDS and 'schema'not in inp,'EXACT_OBSERVED_SCHEMALESS_PARENT_ONLY')
 need(inp['input_payload_duplicate_bytes']==0 and inp['parent_object_id']==pc['object_id']==sha((pid+':'+request['parent']['manifest_ref']['sha256']).encode()),'SCHEMALESS_EXACT_PARENT_OBJECT_AND_NO_DUPLICATE')
 if aid.startswith('SCAN_SMALL_'):
  need(inp.get('input_members')==[],'OBSERVED_SCAN_EMPTY_DECLARED_PARENT_INPUT_LIST')
  return []
 need(inp['Root_actual_parent_bound']is True and inp['Root_must_bind_parent_manifest_and_actual_COMMIT_before_formal_child_commit']is False and inp['inputs_not_copied_to_child']is True,'OBSERVED_C8_ACTUAL_PARENT_BOUND')
 need(inp['parent_commit_ref']==request['parent']['commit_ref']and inp['parent_manifest_ref']==request['parent']['manifest_ref'],'OBSERVED_C8_CANONICAL_PARENT_REFS')
 pby={r['path']:r for r in pm['files']};cr=pby['QUALIFIED_INPUT_CAPSULE.json'];claim=inp['parent_input_capsule_ref']
 need(claim['bytes']==cr['bytes']and claim['sha256']==cr['sha256'],'OBSERVED_C8_CAPSULE_CANONICAL_PARENT_MEMBER_SHA')
 capsule=pinned(dict(path=str(proot/'QUALIFIED_INPUT_CAPSULE.json'),bytes=cr['bytes'],sha256=cr['sha256']),account)
 need(capsule['schema']=='ADA7_INPUT_OBSERVED_SOURCE_BYTES_AND_LIFECYCLE_V4R2'and capsule['status']=='OBSERVED_SUPPORTED_HTOD_SOURCE_BYTES_CLOSED_SHA_QUALIFIED','OBSERVED_C8_SUPPORTED_SOURCE_BYTES_SCOPE')
 need(capsule['ordered_input_identity_sha256']==inp['parent_input_identity']and capsule['total_bytes']==inp['actual_parent_payload_input_bytes']==262400 and set(capsule['copies'])=={'1','2'},'OBSERVED_C8_EXACT_ORDERED_INPUT_IDENTITY')
 refs=[cr]
 for key,size in [('1',262144),('2',256)]:
  cp=capsule['copies'][key];name=relative(cp['restorable_relative_path']);r=pby[str(name)]
  need(cp['bytes']==r['bytes']==size and cp['sha256']==r['sha256']and cp['api']=='cuMemcpyHtoD_v2','OBSERVED_C8_TWO_SYNC_HTOD_DECLARED_PARENT_MEMBER')
  refs.append(r)
 return refs

OBSERVED_SMALLPOLY3_DERIVED_IDS={'BICG_DEFINED_HOST_INIT_ORIGINAL_SPATIAL_NATIVEQA_V1_DERIVED_CTA_STRIDE40_V1', 'ATAX_DEFINED_HOST_INIT_ORIGINAL_SPATIAL_NATIVEQA_V1_DERIVED_CTA_STRIDE40_V1', 'GESUMMV_DEFINED_HOST_INIT_ORIGINAL_SPATIAL_NATIVEQA_V1_DERIVED_CTA_STRIDE40_V1'}
def observed_smallpoly3_parent_refs(inp,aid,pid,request,pc,pm,c,asset):
 need(aid in OBSERVED_SMALLPOLY3_DERIVED_IDS and inp['schema']=='EXACT_SMALLPOLY3_PARENT_SOURCE_RECIPE_REFERENCE_V1','EXACT_REGISTERED_SMALLPOLY3_PARENT_SCHEMA')
 purpose='DEFINED_HOST_INITIALIZATION_REPAIR_ORIGINAL_SPATIAL'
 need(inp['purpose']==c['profile_use']==pc['profile_use']==asset['purpose']==asset['profile_use']==purpose,'EXACT_SMALLPOLY_DEFINED_HOST_INIT_PURPOSE')
 need(inp['actual_GPU_input_byte_SHA_observed']is False and asset['actual_input_byte_SHA_observed']is False and asset['input_identity']['actual_input_byte_SHA_observed']is False,'SOURCE_RECIPE_NOT_OLD_INPUT_BYTE_SHA')
 need(asset['old_undefined_input_equivalence']is False and c['old_original_undefined_input_row_completed']is False and c['original_frozen153_row_completed']is False,'POLY_REPAIR_NOT_OLD_UNDEFINED_INPUT_COMPLETED')
 need(inp['Root_actual_parent_bound']is True and inp['Root_must_bind_parent_manifest_and_actual_COMMIT_before_formal_child_commit']is False,'ACTUAL_POLY_PARENT_BOUND')
 need(inp['parent_asset_id']==pid and inp['parent_commit_ref']==request['parent']['commit_ref']and inp['parent_manifest_ref']==request['parent']['manifest_ref'],'EXACT_POLY_PARENT_ID_AND_CANONICAL_REFS')
 need(inp['parent_object_id']==pc['object_id']==sha((pid+':'+request['parent']['manifest_ref']['sha256']).encode()),'EXACT_POLY_PARENT_OBJECT_ID')
 need(inp['input_members']==[]and inp['input_payload_duplicate_bytes']==0,'POLY_NO_DUPLICATE_INPUT_PAYLOAD')
 pby={r['path']:r for r in pm['files']};refs=[]
 for key,name in [('parent_binary_member','bin/application'),('parent_recorded_input_table','traces/kernelslist.g')]:
  r=inp[key];need(r['path']==name and r==pby[name],'EXACT_POLY_DECLARED_PARENT_BINARY_OR_TABLE')
  refs.append(r)
 return refs

OBSERVED_LUD_CFI5_DERIVED_ID='ISA_LUD256_CFI5_PIPELINE_PILOT_V1_DERIVED_CTA_STRIDE40_CFI5_V1'
def observed_lud_cfi5_parent_refs(inp,aid,pid,request,pc,pm,c,asset):
 need(aid==OBSERVED_LUD_CFI5_DERIVED_ID and inp['schema']=='LUD_CFI5_PARENT_INPUT_REFERENCE_V1','EXACT_REGISTERED_LUD_CFI5_PARENT_SCHEMA')
 need(pid=='ISA_LUD256_CFI5_PIPELINE_PILOT_V1_ORDINARY_CFI5_V1'and inp['parent_asset_id']==pid,'EXACT_LUD_PARENT_ID')
 purpose='LUD256_ORIGINAL_SHAPE_PRIVATE_CFI5_TERMINAL_CONTROL'
 need(c['profile_use']==pc['profile_use']==asset['profile_use']==purpose,'EXACT_LUD_PROFILE_PURPOSE')
 need(inp['parent_commit_ref']==request['parent']['commit_ref']and inp['parent_manifest_ref']==request['parent']['manifest_ref'],'EXACT_LUD_CANONICAL_PARENT_REFS')
 need(inp['parent_object_id']==pc['object_id']==sha((pid+':'+request['parent']['manifest_ref']['sha256']).encode()),'EXACT_LUD_PARENT_OBJECT')
 need(inp['Root_actual_parent_bound']is True and inp['Root_must_bind_parent_manifest_and_actual_COMMIT_before_formal_child_commit']is False,'LUD_ACTUAL_PARENT_BOUND')
 need(inp['input_members']==[]and inp['input_payload_duplicate_bytes']==0 and inp['actual_input_byte_SHA_observed']is False and inp['original_recipe_not_array_snapshot']is True,'LUD_RECIPE_NOT_GPU_ARRAY_SNAPSHOT')
 need(inp['full46_shape_terminal_contract_NOT_a_derived_permission']is True and asset['full_shape_terminal_contract_permission_inherited']is False and asset['ordinary_full_shape_terminal_not_inherited']is True and asset['derived_terminal_contract_ref']is None,'LUD_NO_DERIVED_TERMINAL_PERMISSION')
 need(inp['consumer_status']==asset['consumer_qualification']=='STRUCTURAL_ONLY_PARENT_ENTRY_NOT_DERIVED_MODEL'and asset['header_state']=='ORIGINAL_DEFERRED_NOT_CONSUMER_GRANTED'and asset['actual_GPU_input_byte_SHA_observed']is False,'LUD_DERIVED_STRUCTURAL_ONLY_NO_MODEL')
 return []

def build_plan(request,account=None,stat_files=True):
 need(request['schema']=='ROOT_EXACT_SINGLE_SM89_FLAT_ASSET_RESTORE_REQUEST_V1','SM89_REQUEST_SCHEMA')
 parent_account=account;metadata_used=[0]
 def debit(n,kind):
  metadata_used[0]+=n;need(metadata_used[0]<=16*M,'PLAN_METADATA16MIB_BOUND')
  if parent_account:parent_account(n,kind)
 aid=asset_id(request['asset_id']);reg=request['registration']
 ordinary=catalog_pair(reg['ordinary'],'CURRENT_RTX4080_CATALOG.json','RTX4080_ASSET_CATALOG_V1',debit)
 derived=catalog_pair(reg['derived'],'CURRENT_RTX4080_DERIVED_CATALOG.json','RTX4080_DERIVED_TRACE_CATALOG_V1',debit)
 ur=reg['unified'];need(Path(ur['pointer_ref']['path'])==LIB/'catalog/CURRENT_UNIFIED_DISCOVERY.json','CURRENT_UNIFIED_POINTER')
 up=pointer(ur,debit);need(Path(ur['snapshot_ref']['path'])==LIB/'catalog'/up['relative_path']and ur['snapshot_ref']['sha256']==up['sha256']and ur['snapshot_ref']['bytes']==up['bytes'],'CURRENT_UNIFIED_IMMUTABLE_PIN')
 unified=pinned(ur['snapshot_ref'],debit);need(unified['schema']=='PRIVATE_UNIFIED_TRACE_DISCOVERY_INDEX_V1','SUPPORTED_UNIFIED_SCHEMA')
 root,c,m=committed(request['object'],aid,debit);kind=c['kind'];need(kind in['FULL_APPLICATION_TRACE','DERIVED_COMPLETE_CTA_TRACE'],'ORDINARY_OR_DERIVED_ONLY_NOT_RAW')
 cat=ordinary if kind=='FULL_APPLICATION_TRACE'else derived
 rows=[x for x in cat['objects']if x['asset_id']==aid];urows=[x for x in unified['SM89_committed_trace_assets']if x['asset_id']==aid]
 need(len(rows)==len(urows)==1,'EXACT_CURRENT_CATALOG_AND_UNIFIED_ASSET_ID')
 rr=rows[0];uu=urows[0]
 for x in[rr,uu]:need(x['manifest_sha256']==request['object']['manifest_ref']['sha256']and x['logical_bytes']==m['logical_bytes']and x['kind']==kind and('object_path'not in x or Path(x['object_path'])==root),'REGISTERED_OWN_RAW_MANIFEST_AND_TOTAL')
 if 'files'in rr:need(rr['files']==len(m['files']),'RECORDED_CATALOG_FILE_COUNT')
 need(uu['architecture']=='SM89'and uu['status']=='COMMITTED_VERIFIED'and('object_path'not in uu or Path(uu['object_path'])==root),'REGISTERED_UNIFIED_COMMITTED_SM89_FIXED_CANONICAL_ROOT')
 by={x['path']:x for x in m['files']};need('ASSET.json'in by,'DECLARED_ASSET_METADATA')
 ar=dict(path=str(root/'ASSET.json'),bytes=by['ASSET.json']['bytes'],sha256=by['ASSET.json']['sha256']);asset=pinned(ar,debit)
 need(asset['asset_id']==aid and asset['kind']==kind and asset['actual_cubin_arch']==89,'OWN_ASSET_METADATA_IDENTITY')
 dependencies=[];parent=None
 if kind=='DERIVED_COMPLETE_CTA_TRACE':
  pid=asset_id(c['parent_asset_id']);need(pid==asset['parent_asset_id']==uu['parent_asset_id'],'REAL_PARENT_ID')
  if 'parent_asset_id'in m:need(m['parent_asset_id']==pid,'RECORDED_MANIFEST_PARENT_ID')
  proot,pc,pm=committed(request['parent'],pid,debit)
  need(pc['kind']=='FULL_APPLICATION_TRACE','DERIVED_PARENT_MUST_BE_ORDINARY_NO_UNADMITTED_CHAIN')
  need(c['parent_manifest_sha256']==request['parent']['manifest_ref']['sha256']and uu['parent_manifest_sha256']==request['parent']['manifest_ref']['sha256'],'COMMIT_AND_REGISTERED_REAL_PARENT_RAW_MANIFEST')
  for x in[c,m,asset]:
   if 'parent_manifest_sha256'in x:need(x['parent_manifest_sha256']==request['parent']['manifest_ref']['sha256'],'RECORDED_DERIVED_PARENT_RAW_MANIFEST')
   if 'parent_commit_sha256'in x:need(x['parent_commit_sha256']==request['parent']['commit_ref']['sha256'],'RECORDED_DERIVED_PARENT_COMMIT_SHA')
  pr=[x for x in ordinary['objects']if x['asset_id']==pid];need(len(pr)==1 and pr[0]['manifest_sha256']==request['parent']['manifest_ref']['sha256']and('object_path'not in pr[0]or Path(pr[0]['object_path'])==proot),'PARENT_CURRENT_ORDINARY_REGISTRATION')
  unknowns=[]
  if 'PARENT_INPUT_REFERENCE.json'in by:
   er=by['PARENT_INPUT_REFERENCE.json'];inp=pinned(dict(path=str(root/er['path']),bytes=er['bytes'],sha256=er['sha256']),debit)
   need((inp.get('schema')=='RTX4080_DERIVED_PARENT_INPUT_REFERENCE_V1'or inp.get('schema')is None and aid in OBSERVED_SCHEMALESS_PARENT_IDS or inp.get('schema')=='EXACT_SMALLPOLY3_PARENT_SOURCE_RECIPE_REFERENCE_V1'and aid in OBSERVED_SMALLPOLY3_DERIVED_IDS or inp.get('schema')=='LUD_CFI5_PARENT_INPUT_REFERENCE_V1'and aid==OBSERVED_LUD_CFI5_DERIVED_ID)and inp['parent_asset_id']==pid and inp['parent_commit_sha256']==request['parent']['commit_ref']['sha256']and inp['parent_manifest_sha256']==request['parent']['manifest_ref']['sha256'],'EXACT_RECORDED_PARENT_INPUT_REFERENCE')
   pby={x['path']:x for x in pm['files']};refs=list(inp.get('input_members',[]))
   if inp.get('schema')is None:refs.extend(observed_schemaless_parent_refs(inp,aid,pid,request,proot,pc,pm,debit))
   if inp.get('schema')=='EXACT_SMALLPOLY3_PARENT_SOURCE_RECIPE_REFERENCE_V1':refs.extend(observed_smallpoly3_parent_refs(inp,aid,pid,request,pc,pm,c,asset))
   if inp.get('schema')=='LUD_CFI5_PARENT_INPUT_REFERENCE_V1':
    refs.extend(observed_lud_cfi5_parent_refs(inp,aid,pid,request,pc,pm,c,asset));unknowns.append('LUD_RECIPE_ONLY_NO_DECLARED_INPUT_MEMBERS; NO_GPU_ARRAY_OR_DERIVED_TERMINAL_PERMISSION')
   for key in['binary_member','recorded_input_commandlist_member','source_generation_recipe_member']:
    if inp.get(key)is not None:refs.append(inp[key])
   for r in refs:
    need(r['path']in pby and r==pby[r['path']],'PARENT_DECLARED_MEMBER_BYTES_REFERENCE')
    p=no_links(proot/relative(r['path']))
    if stat_files:
     st=p.stat();need(stat.S_ISREG(st.st_mode)and st.st_size==r['bytes'],'PARENT_NAS_MEMBER_METADATA_AVAILABLE')
    dependencies.append(dict(r,path=str(p),payload_copied=False,fresh_parent_body_SHA=False))
  else:unknowns.append('PARENT_INPUT_REFERENCE_MEMBER_NOT_HISTORICALLY_DECLARED; EXACT_PARENT_MEMBER_DEPENDENCY_SUBSET_NOT_INFERRED')
  parent=dict(asset_id=pid,object_path=str(proot),commit_ref=request['parent']['commit_ref'],manifest_ref=request['parent']['manifest_ref'],payload_copied=False,dependency_resolution='CURRENT_CANONICAL_NAS_PARENT_KEPT_NOT_DUPLICATED',members=dependencies,unknowns=unknowns,historical_parent_commit_sha_recorded_in={key:'parent_commit_sha256'in value for key,value in[('COMMIT',c),('MANIFEST',m),('ASSET',asset)]},historical_parent_manifest_sha_recorded_in={key:'parent_manifest_sha256'in value for key,value in[('COMMIT',c),('MANIFEST',m),('ASSET',asset)]})
 else:need('parent'not in request or request['parent']is None,'ORDINARY_HAS_NO_PARENT_COPY')
 out=[]
 for r in m['files']:
  p=no_links(root/relative(r['path']))
  if stat_files:
   st=p.stat();need(stat.S_ISREG(st.st_mode)and st.st_size==r['bytes'],'FLAT_DECLARED_REGULAR_MEMBER_METADATA')
  # Internal single-file stream descriptor, not a new on-disk chunk/source format.
  out.append(dict(output_relative_path=r['path'],source_member=dict(size=r['bytes'],sha256=r['sha256']),source_files=[dict(path=str(p),size=r['bytes'],sha256=r['sha256'])]))
 return dict(schema='EXACT_SINGLE_SM89_FLAT_MANIFEST_RESTORE_PLAN_V1',asset_id=aid,kind=kind,commit_ref=request['object']['commit_ref'],manifest_ref=request['object']['manifest_ref'],registration=dict(canonical_object_root=str(root),catalog_object_path_recorded='object_path'in rr,unified_object_path_recorded='object_path'in uu,ordinary_catalog_sha256=reg['ordinary']['snapshot_ref']['sha256'],derived_catalog_sha256=reg['derived']['snapshot_ref']['sha256'],unified_sha256=ur['snapshot_ref']['sha256']),metadata_read_bytes=metadata_used[0],members=out,file_count=len(out),max_member_bytes=max((r['bytes']for r in m['files']),default=0),logical_bytes=m['logical_bytes'],selection_mode='ALL_DECLARED_THIS_ASSET_MANIFEST_MEMBERS',all_declared_members_selected=True,source_file_read_bytes=m['logical_bytes'],native_closed_readback_bytes=m['logical_bytes'],native_write_bytes=m['logical_bytes'],parent_dependency=parent,parent_payload_read_or_copied_bytes=0,scientific_or_consumer_qualification=False)

class Budget:
 def __init__(self,grant):
  self.a=grant;self.used={k:0 for k in['metadata','source','write','readback']};self.start=time.monotonic()
 def account(self,n,kind):
  self.used[kind]+=n;need(self.used[kind]<=self.a['max_'+kind+'_bytes'],'EXACT_'+kind.upper()+'_BUDGET');self.check()
 def check(self):
  need(self.a['not_before_unix']<=time.time()<self.a['deadline_unix']and time.monotonic()-self.start<=self.a['wall_seconds'],'FINITE_ROOT_CLOCK')
  need(shutil.disk_usage(NATIVE).free>=5*G,'NATIVE_ACTUAL5G_FLOOR')
  mem=int(next(x.split()[1]for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))*1024
  need(mem>=self.a['min_host_MemAvailable_bytes'],'CURRENT_ROOT_EXACT_MEMORY_FLOOR')
 def pace(self,n):
  target=n/self.a['source_rate_bytes_s']
  while target>time.monotonic()-self.start:
   time.sleep(min(target-(time.monotonic()-self.start),.25));self.check()
def dirfd(p):
 p=no_links(p);fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
 try:
  for part in p.parts[1:]:
   child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd);os.close(fd);fd=child
  return fd
 except BaseException:os.close(fd);raise
def output_parent(rootfd,rel):
 parts=relative(rel).parts;fd=os.dup(rootfd)
 try:
  for part in parts[:-1]:
   try:os.mkdir(part,mode=0o700,dir_fd=fd)
   except FileExistsError:pass
   child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd);os.close(fd);fd=child
  return fd,parts[-1]
 except BaseException:os.close(fd);raise
def write_json_new(path,obj):
 raw=json.dumps(obj,indent=2,sort_keys=True).encode()+b'\n';need(len(raw)<=M,'BOUNDED_CONTROL_RECEIPT')
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 with os.fdopen(fd,'wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
def validate_grant(a,request_raw,code_sha,now=None):
 now=time.time()if now is None else now
 need(a['schema']=='ROOT_EXACT_SINGLE_SM89_FLAT_ASSET_RESTORE_ONE_GRANT_V1'and a['status']=='ROOT_APPROVED_EXACT_SINGLE_ASSET_RESTORE_ONCE','NEW_ROOT_RESTORE_ONE_AUTHORITY_REQUIRED')
 need(a['request_sha256']==sha(request_raw)and a['source_code_sha256']==code_sha,'EXACT_REQUEST_AND_NEW_CODE')
 req=json.loads(request_raw);need(a['asset_id']==req['asset_id']and a['manifest_sha256']==req['object']['manifest_ref']['sha256'],'EXACT_REGISTERED_SM89_INSTANCE')
 need(a['new_native_attributes_policy']=='ROOT0_GID0_READONLY0444_NEW_TIMESTAMP'and type(a['new_native_mtime_ns'])is int and a['new_native_mtime_ns']>=0,'NO_UNRECORDED_CAPTURE_ATTRIBUTE_CLAIM')
 need(re.fullmatch('[A-Za-z0-9_-]{1,80}',a['scope_id'])is not None and re.fullmatch('[A-Za-z0-9_-]{1,80}',a['destination_name'])is not None,'EXACT_SCOPE_AND_TARGET_LEAF')
 need(a['not_before_unix']<=now<a['deadline_unix']<=a['not_before_unix']+a['wall_seconds']and 0<a['wall_seconds']<=3600,'FRESH_BOUNDED_ROOT_WINDOW')
 need(a['Native_floor_bytes']==5*G and a['AS_bytes']==512*M and type(a['CPU_ids'])is list and len(a['CPU_ids'])==1 and type(a['CPU_ids'][0])is int,'ROOT_DISK_MEMORY_CPU_PROFILE')
 need(0<a['max_metadata_bytes']<=16*M,'EXACT_METADATA16MIB_IMPLEMENTATION_LIMIT')
 need(0<a['source_rate_bytes_s']<=64*M and a['min_host_MemAvailable_bytes']>=16*G+512*M,'EXACT_RATE_AND_MEMORY_BUDGET')
 need(a['NAS_mount']==dict(target='/root/share/mnt164',fstype='fuse.sshfs',source='admin-wcx@10.208.130.164:/home/shared'),'EXACT_ROOT_GENUINE164_NAS_PROFILE')
 need(a['Source_KEEP']is True and a['consumer_or_science_qualification_granted']is False,'NO_SOURCE_OR_SCIENCE_CHANGES')
 return a
def execute(a,request,request_raw,plan,budget):
 parent=Path(a['destination_parent_ref']['path']);need(parent.is_relative_to(NATIVE)and parent!=NATIVE.parent,'NEW_DEDICATED_NATIVE_NAMESPACE_ONLY')
 need(mount_for(LIB)==a['NAS_mount'],'CURRENT_GENUINE164_NAS_MOUNT')
 pfd=dirfd(parent);ps=os.fstat(pfd);r=a['destination_parent_ref']
 need((ps.st_dev,ps.st_ino,ps.st_uid)==(r['dev'],r['inode'],0)and stat.S_IMODE(ps.st_mode)==0o700,'ROOT_PINNED_PRIVATE_NATIVE_PARENT')
 need(ps.st_dev==a['native_device']and ps.st_dev==NATIVE.stat().st_dev==Path('/root/data').stat().st_dev,'EXACT_NATIVE_DEVICE')
 need(mount_for(parent)['fstype']=='ext4','ACTUAL_NATIVE_EXT4')
 need(shutil.disk_usage(parent).free>=5*G+plan['logical_bytes'],'PREALLOCATION_PLUS5G_FLOOR')
 need(a['max_source_bytes']==a['max_write_bytes']==a['max_readback_bytes']==plan['logical_bytes']and a['expected_file_count']==plan['file_count']and a['max_member_bytes']==plan['max_member_bytes'],'EXACT_MANIFEST_COUNT_MAX_MEMBER_TOTAL_ROOT_INSTANCE_BUDGET')
 ev=EVIDENCE/a['scope_id'];no_links(EVIDENCE);ev.mkdir(mode=0o700);target=parent/a['destination_name'];dfd=None;proofs=[]
 try:
  os.mkdir(a['destination_name'],mode=0o700,dir_fd=pfd);dfd=os.open(a['destination_name'],os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=pfd);destination_identity=os.fstat(dfd)
  write_json_new(ev/'START.json',dict(kind=plan['kind'],commit_ref=plan['commit_ref'],manifest_ref=plan['manifest_ref'],registration=plan['registration'],scope_id=a['scope_id'],request_sha256=sha(request_raw),asset_id=plan['asset_id'],destination=str(target),source_KEEP=True,new_grant_not_R5_or_C8_authority=True))
  for row in plan['members']:
   budget.check();m=row['source_member'];ofd,name=output_parent(dfd,row['output_relative_path']);fd=None
   try:
    fd=os.open(name,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=ofd)
    if m['size']:os.posix_fallocate(fd,0,m['size'])
    need(os.fstat(fd).st_size==m['size']and(m['size']==0 or os.fstat(fd).st_blocks*512>=m['size']),'REAL_OWNED_PREALLOCATION')
    whole=hashlib.sha256();count=0;chunk_proofs=[]
    for chunk in row['source_files']:
     sfd=dirfd(Path(chunk['path']).parent);sf=os.open(Path(chunk['path']).name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=sfd);os.close(sfd);h=hashlib.sha256();n=0
     try:
      before=os.fstat(sf);need(stat.S_ISREG(before.st_mode)and before.st_size==chunk['size']and before.st_dev==LIB.stat().st_dev,'SOURCE_FILE_EXACT_NAS_DEVICE_AND_SIZE')
      while n<chunk['size']:
       b=os.read(sf,min(M,chunk['size']-n));need(b,'SOURCE_CHUNK_EOF');budget.account(len(b),'source');h.update(b);whole.update(b);left=memoryview(b)
       while left:
        z=os.write(fd,left);need(z>0,'SHORT_NATIVE_WRITE');budget.account(z,'write');left=left[z:]
       n+=len(b);count+=len(b);budget.pace(budget.used['source'])
      need(n==before.st_size and ident(os.fstat(sf))==ident(before)and h.hexdigest()==chunk['sha256'],'FRESH_SOURCE_FILE_WHOLESHA_AND_STABLE_FD')
     finally:os.close(sf)
     chunk_proofs.append(dict(path=chunk['path'],bytes=n,sha256=h.hexdigest(),full_SHA_fresh=True))
    need(count==m['size']and whole.hexdigest()==m['sha256'],'FRESH_MEMBER_WHOLESHA')
    os.fsync(fd);os.fchown(fd,0,0);os.fchmod(fd,0o444);os.utime(fd,ns=(a['new_native_mtime_ns'],a['new_native_mtime_ns']));closed=os.fstat(fd);os.close(fd);fd=None
    rf=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=ofd);h=hashlib.sha256();n=0
    try:
     rb=os.fstat(rf);need(ident(rb)==ident(closed)and rb.st_nlink==1,'CLOSED_REOPEN_SAME_NATIVE_OBJECT')
     while n<m['size']:
      b=os.read(rf,min(M,m['size']-n));need(b,'CLOSED_NATIVE_EOF');h.update(b);n+=len(b);budget.account(len(b),'readback')
     need(ident(os.fstat(rf))==ident(rb)and n==m['size']and h.hexdigest()==m['sha256'],'CLOSED_REOPEN_NATIVE_WHOLESHA')
    finally:os.close(rf)
    need((closed.st_uid,closed.st_gid,stat.S_IMODE(closed.st_mode),closed.st_mtime_ns)==(0,0,0o444,a['new_native_mtime_ns']),'EXPLICIT_NEW_NATIVE_SAFE_ATTRIBUTES_NOT_CAPTURE_ATTRS')
    proofs.append(dict(relative_path=row['output_relative_path'],bytes=n,member_sha256=m['sha256'],native_closed_reopen_sha256=h.hexdigest(),source_file_proofs=chunk_proofs,attributes_policy='NEW_NATIVE_ROOT0_GID0_READONLY0444_ROOT_TIMESTAMP',original_capture_attrs_preserved_or_known=False))
   finally:
    if fd is not None:os.close(fd)
    os.close(ofd)
  now=os.stat(a['destination_name'],dir_fd=pfd,follow_symlinks=False);need((now.st_dev,now.st_ino)==(destination_identity.st_dev,destination_identity.st_ino),'FINAL_DESTINATION_NAMESPACE')
  result=dict(schema='ROOT_EXACT_SINGLE_SM89_FLAT_ASSET_FRESH_NATIVE_RESTORE_RECEIPT_V1',status='EXACT_SELECTED_MEMBERS_NATIVE_WHOLESHA_CLOSED',asset_id=plan['asset_id'],kind=plan['kind'],commit_ref=plan['commit_ref'],manifest_ref=plan['manifest_ref'],registration=plan['registration'],scope_id=a['scope_id'],request_sha256=sha(request_raw),source_code_sha256=a['source_code_sha256'],destination=str(target),selection_mode=plan['selection_mode'],all_declared_members_materialized=plan['all_declared_members_selected'],members=proofs,budget_used=budget.used,parent_dependency=plan['parent_dependency'],parent_payload_read_or_copied_bytes=0,whole_library_restored=False,consumer_or_scientific_qualification=False,Source_KEEP=True,release_bytes=0,destination_root_metadata='NEW_ROOT_OWNED_DIRECTORY_NOT_HISTORICAL_ROOT')
  write_json_new(ev/'RESULT.json',result);return result
 except BaseException as error:
  write_json_new(ev/'FAILURE_RETAINED.json',dict(status='FAILED_PARTIAL_RETAINED_NOT_RESTORE_PASS',error=repr(error),destination=str(target),completed_members=proofs,budget_used=budget.used,Source_KEEP=True,partial_destination_KEEP=True));raise
 finally:
  if dfd is not None:os.close(dfd)
  os.close(pfd)
def main():
 p=argparse.ArgumentParser();p.add_argument('--asset',required=True);p.add_argument('--request',required=True);p.add_argument('--request-sha',required=True);p.add_argument('--inspect-metadata',action='store_true');p.add_argument('--grant');p.add_argument('--grant-sha');p.add_argument('--execute',action='store_true');a=p.parse_args()
 rp=Path(a.request);need(rp.is_relative_to(LIB/'receipts'),'PRIVATE_REQUEST_METADATA_NAMESPACE');request,raw=raw_json(rp,M);need(sha(raw)==a.request_sha and request['asset_id']==a.asset,'EXACT_ASSET_REQUEST_RAW_SHA')
 if a.inspect_metadata:
  need(not a.execute and not a.grant and not a.grant_sha,'INSPECT_HAS_NO_BODY_PERMISSION');print(json.dumps(build_plan(request),indent=2));return
 need(a.execute and a.grant and a.grant_sha,'EXPLICIT_FRESH_ROOT_GRANT_AND_EXECUTE')
 gp=no_links(a.grant);need(gp.parent==AUTH,'NEW_SEPARATE_RESTORE_ONE_AUTHORITY');st=gp.stat();need(st.st_uid==0 and stat.S_IMODE(st.st_mode)==0o600,'ROOT0600_GRANT')
 grant,graw=raw_json(gp,M);need(sha(graw)==a.grant_sha,'GRANT_RAW_SHA');code_raw=Path(__file__).read_bytes();validate_grant(grant,raw,sha(code_raw))
 signal.signal(signal.SIGALRM,lambda *_:(_ for _ in()).throw(TimeoutError('ROOT_RESTORE_ONE_ABSOLUTE_DEADLINE')));signal.alarm(max(1,math.ceil(grant['deadline_unix']-time.time())))
 need(os.geteuid()==0,'NATIVE_NUMERIC_RESTORE_ROOT');resource.setrlimit(resource.RLIMIT_AS,(512*M,512*M));resource.setrlimit(resource.RLIMIT_CORE,(0,0));need(set(grant['CPU_ids'])<=os.sched_getaffinity(0),'ROOT_CPU_CURRENTLY_ALLOWED');os.sched_setaffinity(0,set(grant['CPU_ids']))
 if os.getpriority(os.PRIO_PROCESS,0)<15:os.nice(15-os.getpriority(os.PRIO_PROCESS,0))
 budget=Budget(grant);budget.account(len(raw)+len(graw)+len(code_raw),'metadata');plan=build_plan(request,budget.account)
 result=execute(grant,request,raw,plan,budget);signal.alarm(0);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
