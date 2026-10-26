#!/usr/bin/python3
"""Fixed ordinary CPU-adoption archive/receiver/CURRENT candidate. No GPU/validator/QUEUE branch."""
from pathlib import Path
import os,json,hashlib,time,importlib.util,stat,socket,math
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('fixed_selected',HERE/'selected_cpu_post_v2.py');M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
sp=importlib.util.spec_from_file_location('fixed_noreplace',HERE/'preimages/noreplace_v9.py');V=importlib.util.module_from_spec(sp);sp.loader.exec_module(V)
B=Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
AUTH=M.AUTH.with_name('ROOT_STREAMCLUSTER_CPU_ARCHIVE_APPROVAL_V2.json')
def publish(spec,grant_ref=None,qualification=False):
 root=Path(spec['source_root']).absolute();library=Path(spec['library_root']).absolute();ident=spec['asset_id']
 M.need(Path(ident).name==ident and len(ident)<=180,'EXACT_ASSET_ID');M.no_links(root);M.no_links(library)
 snapshot=M.readref(spec['snapshot_ref']);names=snapshot['declared_order'];M.need(len(names)==len(set(names))and set(names)==set(snapshot['known_raw_sha256']),'EXACT_ARCHIVE_SCOPE')
 for n in names:M.need(Path(n).name==n and n.startswith('kernel-')and n.endswith('.trace.xz'),'SAFE_ARCHIVE_RAW_NAME')
 M.need(spec['source_KEEP']is True and spec['consumer_science_numeric_upgrade']is False,'NO_UPGRADE_SOURCE_KEEP')
 M.need(type(spec['deadline_seconds'])is int and 0<spec['deadline_seconds']<=72*3600,'FINITE_ARCHIVE_TIME')
 M.need(type(spec['rate_bytes_sec'])is int and 1<=spec['rate_bytes_sec']<=15*2**20,'ONE_ARCHIVE_RATE')
 wall_deadline=float('inf')
 if qualification:
  M.no_links(HERE/'fixtures');M.need(root.resolve().is_relative_to((HERE/'fixtures').resolve())and library.resolve().is_relative_to((HERE/'fixtures').resolve()),'QUAL_ARCHIVE_PRIVATE')
  deadline=time.monotonic()+spec['deadline_seconds']
 else:
  M.need(grant_ref and Path(grant_ref['path'])==AUTH,'EXACT_ARCHIVE_ROOT_AUTHORITY')
  g=M.readref(grant_ref);M.need(AUTH.stat().st_uid==0 and AUTH.stat().st_mode&0o022==0,'ROOT_ARCHIVE_OWNER')
  M.need(g['schema']=='ROOT_STREAMCLUSTER_CPU_ARCHIVE_V2'and g['status']=='ROOT_APPROVED_EXACT_FULL_BODY_RECEIVER_CURRENT_V2','ARCHIVE_APPROVAL')
  M.need(g['spec_sha256']==hashlib.sha256(M.canon(spec)).hexdigest()and g['code_manifest_sha256']==M.sha(HERE/'CODE_MANIFEST.json'),'ARCHIVE_CODE_SPEC')
  mf=json.loads((HERE/'CODE_MANIFEST.json').read_text())
  for name,row in mf['files'].items():M.need(M.sha(HERE/name)==row['sha256']and(HERE/name).stat().st_size==row['bytes'],'ARCHIVE_FRESH_CODE')
  M.need(root==M.PROD_ROOT and library==B and ident==g['asset_id']and ident.startswith(M.JOB+'_CPU_ADOPT_'),'FIXED_ARCHIVE_DOMAIN')
  M.need(spec['snapshot_ref']['sha256']==M.sha(HERE/'preimages/FROZEN_ADOPTION_INPUT_V1.json'),'ORIGINAL_F9_SNAPSHOT')
  M.need(g['host']==socket.gethostname()and g['boot_id']==Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'ARCHIVE_HOST_BOOT')
  M.need(type(g['not_before_unix'])in[int,float]and type(g['absolute_deadline_unix'])in[int,float]and math.isfinite(g['not_before_unix'])and math.isfinite(g['absolute_deadline_unix'])and g['not_before_unix']<=time.time()<g['absolute_deadline_unix']and 0<g['absolute_deadline_unix']-g['not_before_unix']<=72*3600,'ARCHIVE_ABSOLUTE_WINDOW');wall_deadline=g['absolute_deadline_unix']
  term=M.readref(g['terminal_evidence_ref']);gp=HERE/'preimages/metadata_gate_v1.py';s=importlib.util.spec_from_file_location('archive_terminal',gp);gate=importlib.util.module_from_spec(s);s.loader.exec_module(gate);gate.boundary(term,snapshot)
  expected={'RTX_SOURCE_174':str(AUTH.parent/'RTX4080_SOURCE.lock'),'RTX_TARGET_174':str(AUTH.parent/'RTX4080_TARGET.lock')}
  M.need({x['role']:x['path']for x in spec['leases']}==expected,'ARCHIVE_EXACT_WRITER_LEASES')
  deadline=time.monotonic()+min(spec['deadline_seconds'],g['absolute_deadline_unix']-time.time())
 M.lease_check(spec['leases']);M.need(time.monotonic()<deadline,'ARCHIVE_DEADLINE_ADMISSION')
 M.need(type(spec['max_package_bytes'])is int and 0<spec['max_package_bytes']<=4*2**40,'FINITE_PACKAGE_LIMIT')
 rows=spec['post_rows'];M.need(len(rows)==len(names)and len({x['name']for x in rows})==len(names)and{x['name']for x in rows}==set(names),'ALL_KERNEL_POST_ROWS_REQUIRED')
 by={x['name']:x for x in rows};artifacts=spec['artifacts'];members=[x['member']for x in artifacts]
 M.need(len(members)==len(set(members)),'UNIQUE_STATIC_ARTIFACT_MEMBERS')
 for n in members:M.need(not Path(n).is_absolute()and'..'not in Path(n).parts and n not in['ASSET.json','MANIFEST.json','COMMIT.json','SENDER_MANIFEST.json']and not n.startswith('traces/kernel-')and n!='traces/kernelslist.g','SAFE_STATIC_ARTIFACT')
 if not qualification:
  required={'FULL_RECORD_VALIDATION.json':snapshot['metadata']['validation_sha256'],'EXECUTION.json':snapshot['metadata']['execution_sha256'],'map/manifest.json':snapshot['metadata']['map_sha256'],'bin/application':snapshot['identity']['binary_sha256'],'tools/producer.so':snapshot['identity']['producer_sha256'],'tools/validate_v7_stream_v3.py':snapshot['metadata']['validator_sha256'],'contract/validate_v7.py':snapshot['metadata']['parser_sha256'],'tools/postprocess_nas_sharded_v4.py':M.POST_SHA,'contract/CONTRACT.json':'97901eb373fc94b041c5ef6923e0e5ca1635edd1bac4213d53c28271abb6c184'}
  ar={x['member']:x['source_ref']for x in artifacts};M.need(all(n in ar and ar[n]['sha256']==h for n,h in required.items()),'REQUIRED_ORIGINAL_STATIC_ARTIFACTS')
  M.need(all(n in ar for n in['TASK.json','NATIVE_QUALIFICATION.json','STATIC_IMAGE_ENUMERATION_CENSUS.json','map/semantic-map.tsv']),'REQUIRED_ORIGINAL_PROVENANCE_MEMBERS')
  M.need(len([n for n in members if n.startswith('traces/stats_ctx_')])==1,'EXACT_ORIGINAL_STATS_MEMBER')
  for item in snapshot['identity']['source_files']:M.need(any(x.get('original_source_path')==item['path']and x['source_ref']['sha256']==item['sha256']for x in artifacts),'ORIGINAL_SOURCE_ARTIFACT')
 objects=library/'objects';catalog=library/'catalog';receipts=library/'receipts'
 for controlled in[objects,catalog,receipts,catalog/'ASSETS.json',catalog/'versions',catalog/'CURRENT_RTX4080_CATALOG.json']:M.no_links(controlled)
 objects.mkdir(parents=True,exist_ok=True);catalog.mkdir(parents=True,exist_ok=True);receipts.mkdir(parents=True,exist_ok=True)
 dest=objects/ident;M.need(not dest.exists(),'UNKNOWN_OR_EXISTING_OBJECT_REQUIRES_ROOT_RECONCILIATION')
 cat=catalog/'ASSETS.json';old=M.sha(cat)if cat.exists()else None;M.need(old==spec['catalog_preimage_sha256'],'CATALOG_CAS_PREIMAGE_BEFORE_BODY')
 dest.mkdir(mode=0o700);next_ns=[time.monotonic_ns()];owned_bytes=[0];body=[]
 def check():
  M.need(time.monotonic()<deadline and time.time()<wall_deadline,'ARCHIVE_DEADLINE');M.lease_check(spec['leases'])
  if not qualification:M.need(__import__('shutil').disk_usage(library).free>=20*2**30,'ARCHIVE_NAS_FLOOR')
 def charge(n):
  check();now=time.monotonic_ns();slot=max(now,next_ns[0]);next_ns[0]=slot+(n*10**9+spec['rate_bytes_sec']-1)//spec['rate_bytes_sec'];delay=slot/1e9-time.monotonic()
  if delay>0:time.sleep(min(delay,max(0,deadline-time.monotonic())))
  check()
 def hashed(p):
  h=hashlib.sha256();before=M.regular(p)
  with Path(p).open('rb')as f:
   while True:
    check();b=f.read(2**20)
    if not b:break
    charge(len(b));h.update(b)
  M.need(M.token(p)==before,'ARCHIVE_HASH_SOURCE_CHANGED');return h.hexdigest()
 def copy_payload(source,relative,expected):
  check();source=Path(source);M.no_links(source)
  if qualification:M.need(source.resolve().is_relative_to((HERE/'fixtures').resolve()),'QUAL_ARCHIVE_SOURCE_PRIVATE')
  else:M.need(source.resolve().is_relative_to(Path('/root/share/mnt164/huangrulin/traces')),'NAS_ONLY_ARCHIVE_SOURCE')
  before=M.regular(source);M.need(owned_bytes[0]+before[2]+16*2**20<=spec['max_package_bytes'],'PACKAGE_OWNED_BYTES')
  target=dest/relative;M.no_links(target);target.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256()
  with source.open('rb')as inp,target.open('xb')as out:
   while True:
    check();b=inp.read(2**20)
    if not b:break
    charge(len(b));h.update(b);M.need(out.write(b)==len(b),'ARCHIVE_SHORT_WRITE');charge(len(b))
   out.flush();os.fsync(out.fileno())
  M.need(M.token(source)==before and h.hexdigest()==expected,'ACTUAL_SOURCE_FULL_BODY_SHA')
  M.need(target.stat().st_size==before[2]and hashed(target)==expected,'TRUE164_CLOSED_REOPEN_BODY_SHA')
  owned_bytes[0]+=before[2];body.append(dict(path=str(relative),bytes=before[2],sha256=expected))
 try:
  for name in names:
   row=by[name];r=M.readref(row['receipt_ref']);q=snapshot['per_kernel'][name]
   M.need(row['postprocessor_sha256']==M.POST_SHA and r['status']=='GROUPED_ALL_SHARDS_CRC_PASS'and r['source_sha256']==snapshot['known_raw_sha256'][name]and r['closed_reopened_full_xz_crc']is True,'EXACT_CLOSED5D_BODY_CHAIN')
   M.need([r['records'],r['ctas'],r['warps']]==[q['records'],q['ctas'],q['warps']],'WHOLE_F9_COUNTS')
   copy_payload(root/'traces'/name,'traces/'+name,snapshot['known_raw_sha256'][name])
   grouped=Path(row['grouped_path']);M.no_links(grouped)
   M.need(grouped.resolve().is_relative_to(root.resolve())or grouped.resolve().is_relative_to(HERE.resolve()),'EXACT_APPROVED_GROUP_PATH')
   copy_payload(grouped,'traces/'+name.replace('.trace.xz','.traceg.xz'),r['grouped_sha256'])
  for x in artifacts:copy_payload(x['source_ref']['path'],x['member'],x['source_ref']['sha256'])
  if not qualification:
   task=json.loads((dest/'TASK.json').read_text());M.need(task['argv']==snapshot['identity']['argv']and task['binary_sha256']==snapshot['identity']['binary_sha256'],'COPIED_TASK_EXACT_ARGV_BINARY')
   f9=json.loads((dest/'FULL_RECORD_VALIDATION.json').read_text());execution=json.loads((dest/'EXECUTION.json').read_text());mapped=json.loads((dest/'map/manifest.json').read_text())
   M.need(f9['status']=='ADA7_ORDINARY_FULL_RECORD_PASS'and f9['kernels']==len(names)and f9['counts']['sass_records']==snapshot['records'],'COPIED_ORIGINAL_F9_COUNTS')
   M.need(execution['exit_code']==0 and execution['binary_sha256']==mapped['binary_sha256']==snapshot['identity']['binary_sha256'],'COPIED_CAPTURE_CLOSED_IDENTITY')
  asset=dict(schema='RTX4080_FULL_TRACE_ASSET_V1',kind='QUALIFICATION_SYNTHETIC_CPU_FIXTURE'if qualification else'FULL_APPLICATION_TRACE',asset_id=ident,original_job_id=M.JOB,CPU_only_adoption=True,GPU_replayed=False,binary_sha256=snapshot.get('identity',{}).get('binary_sha256'),producer_sha256=snapshot.get('identity',{}).get('producer_sha256'),original_identity=snapshot.get('identity'),full_application=dict(kernel_launches=len(names),records=sum(snapshot['per_kernel'][n]['records']for n in names),sampling='NONE',commandlist='traces/kernelslist.g'),producer_semantic_qualification='SYNTHETIC_NOT_REAL_F9'if qualification else'ADA7_ORDINARY_FULL_RECORD_PASS',numerical_status=snapshot.get('identity',{}).get('numerical_status','QUALIFICATION_ONLY'),consumer_qualification='NOT_GRANTED',hardware_timing_calibration='NOT_GRANTED',source_keep=True,release_bytes=0)
  if not qualification:
   identity=snapshot['identity'];asset.update(suite='Rodinia',source_version='3.1',program='streamcluster',variant='ORIGINAL_CAPTURE_CPU_ADOPT_ONLY',argv=identity['argv'],input_identity=identity['input_identity'],binary_member='bin/application',capture_gpu_uuid='GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59',actual_cubin_arch=89,validator_sha256=snapshot['metadata']['validator_sha256'],frozen_parser_sha256=snapshot['metadata']['parser_sha256'],map_manifest_sha256=snapshot['metadata']['map_sha256'],postprocessor_sha256=M.POST_SHA,contract_sha256='97901eb373fc94b041c5ef6923e0e5ca1635edd1bac4213d53c28271abb6c184',tracer_control_flags=identity['tracer_control_flags'],original_capture_worker_sha256='a546e0cfdf47e463bed63740289f44737f503b7cd6b822510c5845a6ec80b183',input_byte_identity_qualification='ORIGINAL_CAPTURE_DECLARED_SOURCE_RECIPE_ONLY_NO_NEW_ARRAY_SNAPSHOT_CLAIM')
   asset['full_application'].update(ctas=sum(snapshot['per_kernel'][n]['ctas']for n in names),warps=sum(snapshot['per_kernel'][n]['warps']for n in names),all_warps_terminate=True,context_count=1,stream_ids=[0])
  # Caller supplies exact original ctx commandlist and stats as SHA-bound artifacts;
  # this derived commandlist only changes each already-frozen relative kernel suffix.
  commands=[x for x in artifacts if x['member'].startswith('traces/kernelslist_ctx_')]
  if not qualification:M.need(len(commands)==1,'EXACT_RAW_COMMANDLIST_ARTIFACT')
  if commands:
   lines=(dest/commands[0]['member']).read_text().splitlines();declared=[x.strip()for x in lines if x.startswith('kernel-')];M.need(declared==names,'ORIGINAL_COMMANDLIST_DECLARED_ORDER')
   (dest/'traces/kernelslist.g').write_text('\n'.join(x.replace('.trace.xz','.traceg.xz')if x.startswith('kernel-')else x for x in lines)+'\n')
  M.save(dest/'ASSET.json',asset);sender=dict(asset=asset,files=[dict(path=str(p.relative_to(dest)),bytes=p.stat().st_size,sha256=hashed(p))for p in sorted(dest.rglob('*'))if p.is_file()]);M.save(dest/'SENDER_MANIFEST.json',sender)
  # Actual receiver pass across all files; no metadata-only substitution.
  for row in sender['files']:M.need(hashed(dest/row['path'])==row['sha256'],'SENDER_ALL_BODY_RECONCILIATION')
  files=[dict(path=str(p.relative_to(dest)),bytes=p.stat().st_size,sha256=hashed(p))for p in sorted(dest.rglob('*'))if p.is_file()]
  manifest=dict(asset_id=ident,files=files,logical_bytes=sum(x['bytes']for x in files));M.save(dest/'MANIFEST.json',manifest);mh=hashed(dest/'MANIFEST.json')
  commit=dict(schema='RTX4080_SHARED_IMMUTABLE_COMMIT_V1',status='QUALIFICATION_BODY_CLOSED_NOT_PUBLIC'if qualification else'COMMITTED_VERIFIED',asset_id=ident,kind=asset['kind'],manifest_sha256=mh,object_path=str(dest),files=len(files),logical_bytes=manifest['logical_bytes'],producer_semantic_status=asset['producer_semantic_qualification'],ssd_payload_staging_bytes=0,channel='CPU_ONLY_NAS_COPY_NATIVE174_RECEIVER_CLOSED',source_keep=True,release_bytes=0,consumer_per_profile_qualification='NOT_GRANTED',utc_unix=time.time())
  temporary=receipts/(ident+'.COMMIT_OWNED_WRITING.json');M.save(temporary,commit);V.rename_noreplace(temporary,dest/'COMMIT.json')
  M.need(hashed(dest/'MANIFEST.json')==mh,'RECEIVER_MANIFEST_REOPEN')
  for row in files:M.need((dest/row['path']).stat().st_size==row['bytes']and hashed(dest/row['path'])==row['sha256'],'RECEIVER_ALL_BODY_CLOSED_REOPEN')
  readback=receipts/(ident+'_RECEIVER_READBACK.json');M.save(readback,commit)
  check();M.need((M.sha(cat)if cat.exists()else None)==old,'CATALOG_CAS_CHANGED_DURING_BODY')
  doc=json.loads(cat.read_text())if cat.exists()else dict(schema='RTX4080_ASSET_CATALOG_V1',objects=[]);M.need(all(x['asset_id']!=ident for x in doc['objects']),'CATALOG_ASSET_COLLISION');doc['objects'].append(commit)
  raw=M.canon(doc);dh=hashlib.sha256(raw).hexdigest();versions=catalog/'versions';versions.mkdir(exist_ok=True);version=versions/(dh+'.json')
  if version.exists():M.need(M.sha(version)==dh,'VERSION_COLLISION')
  else:M.save(version,doc)
  tmp=catalog/('ASSETS.OWNED_'+ident+'.json');M.save(tmp,doc);check();M.need((M.sha(cat)if cat.exists()else None)==old,'CATALOG_CAS_BEFORE_REPLACE');os.replace(tmp,cat)
  pointer=dict(relative_path='versions/'+version.name,sha256=dh,objects=len(doc['objects']),previous_catalog_sha256=old,unix=time.time());ptr=catalog/'CURRENT_RTX4080_CATALOG.json';tmp=ptr.with_name('CURRENT.OWNED_'+ident+'.json');M.save(tmp,pointer);check();os.replace(tmp,ptr)
  M.need(M.sha(cat)==M.sha(version)==dh and json.loads(ptr.read_text())==pointer,'CURRENT_VERSION_CLOSED_REOPEN')
  receipt=dict(status='QUALIFICATION_ARCHIVE_RECEIVER_CURRENT_CLOSED'if qualification else'CPU_ADOPT_ARCHIVE_RECEIVER_CURRENT_CLOSED',asset_id=ident,manifest_sha256=mh,catalog_sha256=dh,RAW_bodies=len(names),grouped_bodies=len(names),actual_full_body_copy_and_receiver_reopen=True,source_KEEP=True,release_bytes=0,scientific_qualification=False,qualification_only=qualification)
  check();closed_tmp=receipts/(ident+'_CLOSED_OWNED_WRITING.json');final_closed=receipts/(ident+'_CPU_ADOPT_ARCHIVE_CLOSED.json');M.save(closed_tmp,receipt);check();V.rename_noreplace(closed_tmp,final_closed)
  try:check()
  except BaseException:
   V.rename_noreplace(final_closed,final_closed.with_name(final_closed.name+'.EXPIRED_NOT_COMMITTED'));raise
  return receipt
 except BaseException as e:
  failure=receipts/(ident+'_ARCHIVE_FAILED_RETAINED.json')
  if not failure.exists():M.save(failure,dict(error=repr(e),owned_partial=str(dest),source_KEEP=True,no_automatic_partial_reuse=True,archive_receiver_CURRENT_qualified=False))
  raise

def main():
 import argparse,resource
 p=argparse.ArgumentParser();p.add_argument('--spec',required=True);p.add_argument('--spec-sha',required=True);p.add_argument('--qualification',action='store_true');p.add_argument('--grant');p.add_argument('--grant-sha');a=p.parse_args()
 resource.setrlimit(resource.RLIMIT_AS,(2*2**30,2*2**30));os.nice(15)
 spec=M.readref(dict(path=a.spec,sha256=a.spec_sha,bytes=Path(a.spec).stat().st_size));grant=None if a.grant is None else dict(path=a.grant,sha256=a.grant_sha,bytes=Path(a.grant).stat().st_size)
 print(json.dumps(publish(spec,grant,a.qualification)))
if __name__=='__main__':main()
