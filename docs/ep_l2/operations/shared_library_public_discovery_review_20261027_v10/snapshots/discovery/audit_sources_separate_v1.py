import pathlib,json,hashlib,copy,resource,os,time
resource.setrlimit(resource.RLIMIT_AS,(512*2**20,512*2**20));os.nice(15)
ROOT=pathlib.Path('/root/share/mnt164/huangrulin/traces')
D=pathlib.Path('/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1/unified_discovery_public_prepare_20261027_v2')
PRIVATE=D.parent/'unified_discovery_prepare_20261027_v1'
def sha(b):return hashlib.sha256(b).hexdigest()
def source(ref):
 b=pathlib.Path(ref['path']).read_bytes();assert len(b)==ref['bytes']and sha(b)==ref['sha256'];return json.loads(b)
def audit(v):
 refs=v['source_refs'];plans=source(refs['frozen_SM70_plan']);old=source(refs['SM70_historical_access_snapshot'])
 sm={x['id']:x for x in v['SM70_exact_inputs']};assert len(sm)==len(v['SM70_exact_inputs'])==125
 for x in plans:
  actual=sm[x['bundle_id']]
  for k in ['suite','program','extent','version','members','ordered_kernel_members']:
   assert actual.get(k)==x.get(k),(x['bundle_id'],k)
 oldids={x['bundle_id']for x in old['assets']}
 for aid,x in sm.items():
  assert (x['access_snapshot_status']!='NOT_IN_HISTORICAL_118_ACCESS_SNAPSHOT')==(aid in oldids)
 assert v['counts']['SM70_historical_access_rows']==len(oldids)==118
 ordinary=source(refs['SM89_ordinary']['target'])['objects'];derived=source(refs['SM89_derived']['target'])['objects']
 expected={(kind,x['asset_id']):x for kind,rows in [('regular',ordinary),('derived',derived)]for x in rows}
 actual={(x['variant'],x['asset_id']):x for x in v['SM89_committed_trace_assets']};assert len(actual)==len(v['SM89_committed_trace_assets'])==len(expected)==82
 parents={x['asset_id']:x for x in ordinary}
 identity_keys=['suite','source_version','program','variant','input','input_identity','argv','binary_sha256','producer_sha256','contract_sha256','actual_cubin_arch','input_byte_identity_qualification','numerical_status']
 for key,catalog in expected.items():
  row=actual[key];assert row['manifest_sha256']==catalog['manifest_sha256']and row['status']==catalog['status']
  parent=catalog if key[0]=='regular'else parents[catalog['parent_asset_id']]
  base=ROOT/'rtx4080_sm89/bulk_20261024_v1/objects'/parent['asset_id']
  b=(base/'MANIFEST.json').read_bytes();assert sha(b)==parent['manifest_sha256']
  mf=json.loads(b);pin=next(x for x in mf['files']if x['path']=='ASSET.json')
  b=(base/'ASSET.json').read_bytes();assert sha(b)==pin['sha256']and len(b)==pin['bytes']
  identity=json.loads(b)
  for k in identity_keys:
   if k in identity:assert row[('input_variant'if k=='variant'else k)]==identity[k],(key,k)
  for name,file in [('manifest','MANIFEST.json'),('asset','ASSET.json'),('commit','COMMIT.json')]:
   b=(base/file).read_bytes();assert row['identity_refs'][name]['sha256']==sha(b)and row['identity_refs'][name]['bytes']==len(b)
  if key[0]=='derived':assert row['parent_manifest_sha256']==parent['manifest_sha256']
 q=source(refs['historical_queue']);allowed=['id','type','status','asset_id','job_path','scientific_content_id','source_capture_job_id','superseded_by']
 assert v['SM89_historical_capture_work_items']==[{k:r[k]for k in allowed if k in r}for r in q]
 assert all(x['qualification_inferred']is False for x in sm.values())and all(x['qualification_inferred']is False for x in actual.values())
 assert v['consumer_or_scientific_qualification_granted']is False and v['public_entry_changed']is False
 return True
v=json.loads((PRIVATE/'PRIVATE_UNIFIED_TRACE_INDEX_V1.json').read_text());assert audit(v)
rows=[]
for label,modify in [
 ('wrong SM70 frozen member SHA',lambda x:x['SM70_exact_inputs'][0]['members'][0].update(sha256='0'*64)),
 ('wrong ordinary binary identity',lambda x:x['SM89_committed_trace_assets'][0].update(binary_sha256='0'*64)),
 ('wrong ordinary source input',lambda x:x['SM89_committed_trace_assets'][0].update(program='INVENTED')),
 ('wrong asset metadata ref',lambda x:x['SM89_committed_trace_assets'][0]['identity_refs']['asset'].update(sha256='0'*64)),
 ('wrong queue row type',lambda x:x['SM89_historical_capture_work_items'][0].update(type='INVENTED'))
]:
 x=copy.deepcopy(v);modify(x)
 try:audit(x)
 except AssertionError:rows.append(dict(case=label,rejected=True))
 else:raise AssertionError('audit accepted '+label)
out=dict(schema='ROOT_SEPARATE_IMPLEMENTATION_SOURCE_JOIN_AUDIT_V1',completed_unix=time.time(),all125_SM70_and82_SM89_and242_queue_rows_reopened=True,builder_not_imported=True,independent_implementation_not_external_review=True,negative_tests=rows,trace_body_reads=0,qualification_granted=False,index_sha256=sha((PRIVATE/'PRIVATE_UNIFIED_TRACE_INDEX_V1.json').read_bytes()))
(D/'ROOT_SOURCE_JOIN_AUDIT_V1.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
