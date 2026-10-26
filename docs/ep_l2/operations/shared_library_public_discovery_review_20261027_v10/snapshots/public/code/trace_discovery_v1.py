#!/usr/bin/python3
"""Private cross-project metadata index. Never restores, captures, grants or publishes."""
import pathlib,json,hashlib,os,stat,argparse,time,collections,resource
PLAN_SHA='7ebb0949d9f81cd47d1d0cc4abab0596318babd6eafb2fb3295e8b0325182cc6'
def need(x,m):
 if not x:raise ValueError(m)
def sha(b):return hashlib.sha256(b).hexdigest()
def pairs(items):
 out={}
 for k,v in items:
  need(k not in out,'duplicate JSON key');out[k]=v
 return out
def parse(b):return json.loads(b,object_pairs_hook=pairs)
def read(p,cap=32*2**20):
 p=pathlib.Path(p);need(not p.is_symlink(),'metadata symlink')
 with p.open('rb')as f:
  st=os.fstat(f.fileno());need(stat.S_ISREG(st.st_mode)and 0<st.st_size<=cap,'metadata shape/cap')
  b=f.read(cap+1);end=os.fstat(f.fileno())
 need(len(b)==st.st_size and (st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns)==(end.st_dev,end.st_ino,end.st_size,end.st_mtime_ns),'metadata changed')
 return parse(b),dict(path=str(p),bytes=len(b),sha256=sha(b)),b
def pointer(catalog,name):
 doc,ref,raw=read(catalog/name,1024*1024)
 rel=pathlib.PurePosixPath(doc['relative_path'])
 need(str(rel)==doc['relative_path']and not rel.is_absolute()and len(rel.parts)>=2 and rel.parts[0]in ['versions','qualification_overlays']and all(x not in ['.','..','']for x in rel.parts),'pointer traversal')
 current=catalog
 for part in rel.parts:
  current=current/part;need(not current.is_symlink(),'pointer symlink')
 value,target,_=read(current)
 need(target['sha256']==doc['sha256'],'pointer SHA mismatch')
 return value,dict(pointer=ref,target=target),raw
def unique(rows,key):
 values=[x[key]for x in rows];need(len(set(values))==len(values),'duplicate '+key)
def assemble(plan,available,ordinary,derived,queue,refs):
 unique(plan,'bundle_id');unique(available['assets'],'bundle_id')
 unique(ordinary['objects'],'asset_id');unique(derived['objects'],'asset_id');unique(queue,'id')
 need(len(plan)==125,'frozen125 scope')
 status={r['bundle_id']:r for r in available['assets']}
 need(set(status)<=set(r['bundle_id']for r in plan),'historical access outside plan')
 sm70=[]
 for p in plan:
  ids=[m['relative_path']for m in p['members']];need(len(set(ids))==len(ids),'duplicate member')
  need(p['extent']in ['FRACTION_OR_TRIM_PATH','NO_FRACTION_LABEL_NOT_FULL_CAPTURE_CERTIFIED'],'unknown extent')
  h=status.get(p['bundle_id'])
  sm70.append(dict(id=p['bundle_id'],architecture='SM70',suite=p['suite'],program=p['program'],extent=p['extent'],version=p.get('version'),members=p['members'],ordered_kernel_members=p['ordered_kernel_members'],access_snapshot_status=h['data_status']if h else 'NOT_IN_HISTORICAL_118_ACCESS_SNAPSHOT',access_snapshot_unix=available['observed_unix'],access_snapshot_is_not_current_body_readback=True,trace_entry=h.get('trace_entry')if h else None,qualification_inferred=False))
 sm89=[];parents={r['asset_id']:r for r in ordinary['objects']}
 for kind,rows in [('regular',ordinary['objects']),('derived',derived['objects'])]:
  for p in rows:
   need(p['status']=='COMMITTED_VERIFIED','uncommitted asset catalog row')
   if kind=='derived':
    parent=parents.get(p['parent_asset_id']);need(parent is not None,'orphan derived parent')
    need(parent['manifest_sha256']==p['parent_manifest_sha256'],'derived parent manifest mismatch')
   row={k:p[k]for k in ['asset_id','manifest_sha256','kind','status','logical_bytes','parent_asset_id','parent_manifest_sha256','policy','ctas_retained','records_retained','object_path','producer_semantic_status','consumer_per_profile_qualification','consumer_qualification']if k in p}
   identity=p.get('_indexed_identity')if kind=='regular'else parent.get('_indexed_identity')
   need(type(identity)is dict and identity.get('program'),'missing immutable asset identity')
   row.update(identity)
   row['identity_refs']=p['_identity_refs']if kind=='regular'else parent['_identity_refs']
   row['identity_basis']='OWN_ASSET_MANIFEST'if kind=='regular'else 'EXACT_PARENT_MANIFEST_NO_CONSUMER_QUALIFICATION_INHERITANCE'
   row.update(architecture='SM89',variant=kind,qualification_inferred=False,current_asset_body_reread_by_this_builder=False)
   sm89.append(row)
 work=[{k:p[k]for k in ['id','type','status','asset_id','job_path','scientific_content_id','source_capture_job_id','superseded_by']if k in p}for p in queue]
 return dict(schema='PRIVATE_UNIFIED_TRACE_DISCOVERY_INDEX_V1',status='PRIVATE_METADATA_ONLY_NOT_PUBLIC_ACTIVATION_OR_FULL_ACCEPTANCE',source_refs=refs,SM70_exact_inputs=sm70,SM89_committed_trace_assets=sm89,SM89_historical_capture_work_items=work,counts=dict(SM70_exact_inputs=len(sm70),SM70_regular=sum(p['extent']=='NO_FRACTION_LABEL_NOT_FULL_CAPTURE_CERTIFIED'for p in plan),SM70_fraction=sum(p['extent']=='FRACTION_OR_TRIM_PATH'for p in plan),SM70_historical_access_rows=len(status),SM89_regular=len(ordinary['objects']),SM89_derived=len(derived['objects']),SM89_work_items=len(work),SM89_historical_queue_status=dict(collections.Counter(p['status']for p in queue))),counts_are_different_units_not_aggregate_workload_coverage=True,source_release_bytes=0,public_entry_changed=False,consumer_or_scientific_qualification_granted=False)
def enrich_ordinary(base,ordinary):
 base=pathlib.Path(base)
 out=[]
 identity_keys=['suite','source_version','program','variant','input','input_identity','argv','binary_sha256','producer_sha256','contract_sha256','actual_cubin_arch','input_byte_identity_qualification','numerical_status']
 for original in ordinary['objects']:
  aid=original['asset_id'];need(type(aid)is str and '/'not in aid and aid not in ['.','..'],'asset ID path')
  directory=base/'objects'/aid
  if 'object_path'in original:need(pathlib.Path(original['object_path'])==directory,'ordinary object path mismatch')
  manifest,mr,_=read(directory/'MANIFEST.json')
  need(mr['sha256']==original['manifest_sha256']and manifest['asset_id']==aid,'ordinary manifest binding')
  members=manifest['files'];need(sum(x['path']=='ASSET.json'for x in members)==1,'one ASSET membership required')
  pin=next(x for x in members if x['path']=='ASSET.json')
  identity,ir,_=read(directory/'ASSET.json')
  need(ir['sha256']==pin['sha256']and ir['bytes']==pin['bytes']and identity['asset_id']==aid,'ASSET raw membership binding')
  commit,cr,_=read(directory/'COMMIT.json')
  need(all(commit[k]==original[k]for k in ['asset_id','manifest_sha256','kind','status']),'catalog COMMIT binding')
  row=dict(original);row['_indexed_identity']={('input_variant'if k=='variant'else k):identity[k]for k in identity_keys if k in identity}
  row['_identity_refs']=dict(manifest=mr,asset=ir,commit=cr);out.append(row)
 return dict(ordinary,objects=out)
def collect(root,queue_path):
 root=pathlib.Path(root);frozen=root/'receipts/sm70_binding_parent_20261025_v1/content/sha256'/PLAN_SHA
 plan,pr,_=read(frozen);need(pr['sha256']==PLAN_SHA,'frozen plan SHA mismatch')
 av,ar,_=read(root/'catalog/AVAILABLE_V100_SM70_20261025_V1.json')
 need(av['source_plan_sha256']==PLAN_SHA and av['all_plan_inputs']==125,'access snapshot plan binding')
 cat=root/'rtx4080_sm89/bulk_20261024_v1/catalog'
 ordinary,ore,o_raw=pointer(cat,'CURRENT_RTX4080_CATALOG.json')
 derived,dre,d_raw=pointer(cat,'CURRENT_RTX4080_DERIVED_CATALOG.json')
 _,qre,q_raw=pointer(cat,'CURRENT_RTX4080_QUALIFICATION_OVERLAY.json')
 queue,qr,raw_queue=read(queue_path)
 refs=dict(frozen_SM70_plan=pr,SM70_historical_access_snapshot=ar,SM89_ordinary=ore,SM89_derived=dre,SM89_qualification_overlay=qre,historical_queue=qr)
 ordinary=enrich_ordinary(cat.parent,ordinary)
 result=assemble(plan,av,ordinary,derived,queue,refs)
 for name,raw in [('CURRENT_RTX4080_CATALOG.json',o_raw),('CURRENT_RTX4080_DERIVED_CATALOG.json',d_raw),('CURRENT_RTX4080_QUALIFICATION_OVERLAY.json',q_raw)]:
  need(read(cat/name,1024*1024)[2]==raw,'CURRENT changed during collection')
 need(read(queue_path)[2]==raw_queue,'queue changed during collection')
 return result
def validate_index(v):
 need(v['schema']=='PRIVATE_UNIFIED_TRACE_DISCOVERY_INDEX_V1'and v['consumer_or_scientific_qualification_granted']is False and v['public_entry_changed']is False,'qualification/publish assertion')
 need(all(x['qualification_inferred']is False for x in v['SM70_exact_inputs']+v['SM89_committed_trace_assets']),'implicit qualification')
 unique(v['SM70_exact_inputs'],'id')
 unique(v['SM89_historical_capture_work_items'],'id')
 assets=v['SM89_committed_trace_assets'];need(len(set((x['variant'],x['asset_id'])for x in assets))==len(assets),'duplicate asset')
 for x in v['SM70_exact_inputs']:need(x['access_snapshot_is_not_current_body_readback']is True,'historical qualification inflated')
 c=v['counts'];sm70=v['SM70_exact_inputs'];ordinary=[x for x in assets if x['variant']=='regular'];derived=[x for x in assets if x['variant']=='derived']
 need(c['SM70_exact_inputs']==len(sm70)==125 and c['SM70_regular']==sum(x['extent']=='NO_FRACTION_LABEL_NOT_FULL_CAPTURE_CERTIFIED'for x in sm70)==100 and c['SM70_fraction']==sum(x['extent']=='FRACTION_OR_TRIM_PATH'for x in sm70)==25,'count/extent drift')
 need(c['SM70_historical_access_rows']==sum(x['access_snapshot_status']!='NOT_IN_HISTORICAL_118_ACCESS_SNAPSHOT'for x in sm70),'historical snapshot count drift')
 need(c['SM89_regular']==len(ordinary)and c['SM89_derived']==len(derived)and c['SM89_work_items']==len(v['SM89_historical_capture_work_items']),'asset/work count drift')
 parents={x['asset_id']:x for x in ordinary}
 for x in assets:
  need(x['status']=='COMMITTED_VERIFIED'and type(x.get('program'))is str and x['program'],'asset identity/status')
  if x['variant']=='derived':need(x['parent_asset_id']in parents and parents[x['parent_asset_id']]['manifest_sha256']==x['parent_manifest_sha256'],'derived parent mismatch')
 need(c['SM89_historical_queue_status']==dict(collections.Counter(x['status']for x in v['SM89_historical_capture_work_items'])),'queue count drift')
 return True
def main():
 resource.setrlimit(resource.RLIMIT_AS,(512*2**20,512*2**20));resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.nice(15)
 a=argparse.ArgumentParser();a.add_argument('--index');a.add_argument('--architecture',choices=['SM70','SM89']);a.add_argument('--program');args=a.parse_args()
 need(args.index is not None,'explicit private index required')
 v,_,_=read(args.index);validate_index(v)
 if not args.architecture:print(json.dumps(v['counts'],ensure_ascii=False));return
 rows=v['SM70_exact_inputs']if args.architecture=='SM70'else v['SM89_committed_trace_assets']
 if args.program:rows=[x for x in rows if x.get('program')==args.program]
 print(json.dumps(rows,ensure_ascii=False))
if __name__=='__main__':main()
