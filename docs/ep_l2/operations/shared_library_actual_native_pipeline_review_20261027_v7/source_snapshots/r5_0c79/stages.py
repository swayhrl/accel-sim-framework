"""Complete data-only V3 stages. Root approval and archive closure precede any stage."""
from pathlib import Path
import os,sys,json,hashlib,importlib.util,time,fcntl,subprocess,re
PACKAGE=Path(__file__).resolve().parent
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def need(ok,msg):
 if not ok:raise RuntimeError('RESOURCE_HOLD_BINDING_V3_'+msg)
def module(name):
 spec=importlib.util.spec_from_file_location('public_stage_'+name,PACKAGE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def bounded(p):return module('runtime').bounded_metadata_raw(p)
def read(p):return json.loads(bounded(p))
def ref_read(ref,resources=None):
 raw=module('runtime').bounded_metadata_raw(ref['path'],consume=(lambda n:resources.account(n,'read'))if resources else None)
 need(sha(raw)==ref['sha256'],'IMMUTABLE_INPUT_REF_SHA')
 return json.loads(raw),bytes(raw)
def spec_load(path,expected):
 raw=module('runtime').bounded_metadata_raw(path);need(sha(raw)==expected,'SPEC_SHA')
 spec=json.loads(raw);r=module('runtime');r.verify_package();profile=r.profile()
 need(isinstance(spec.get('integration_id'),str)and re.fullmatch('[A-Za-z0-9_-]{1,96}',spec['integration_id']),'INTEGRATION_NAMESPACE')
 marker_names=dict(publish='LIBRARY_PUBLICATION.json',cross='CROSS_PROJECT_VALIDATION.json',restore='BOUNDED_NATIVE_RESTORE_COMPLETE.json',finish='FINAL_VALIDATION.json')
 need(spec['markers']=={k:str(Path(spec['legacy_goal_root'])/'control'/v)for k,v in marker_names.items()},'EXACT_FIVE_STAGE_MARKER_SCOPE')
 need(spec['schema']=='SM70_BINDING_INTEGRATION_SPEC_V3'and spec['code_version_id']==r.code_manifest()['code_version_id'],'SPEC_CODE_VERSION')
 need(spec['execution_scope']==profile['execution_scope'],'EXECUTION_SCOPE')
 if profile['execution_scope']=='PRODUCTION':
  need(Path(path).resolve().is_relative_to(Path(profile['nas_mount_root']).resolve())and PACKAGE.resolve().is_relative_to(Path(profile['nas_mount_root']).resolve()),'SPEC_AND_CODE_MUST_BE_PUBLIC_IMMUTABLE_NAS')
  need(spec['legacy_goal_root']=='/root/data/shared_sm70_trace_library_20261024_v1','PRODUCTION_OWNED_GOAL_ROOT')
  # Physical bootstrap inputs are public metadata. Legacy original path strings
  # inside proof/index/route documents remain resolver keys, never private reads.
  for key,value in spec.items():
   if key.endswith('_ref'):
    need(Path(value['path']).is_relative_to(Path(profile['nas_mount_root'])),'PUBLIC_BOOTSTRAP_REF_'+key)
  for ref in spec.get('archive_audit_refs',[]):
   need(Path(ref['path']).is_relative_to(Path(profile['nas_mount_root'])),'PUBLIC_ARCHIVE_AUDIT_REF')
  for row in spec.get('archives',[]):
   need(Path(row['source_manifest_ref']['path']).is_relative_to(Path(profile['nas_mount_root']))and Path(row['bundle']).is_relative_to(Path(profile['nas_mount_root'])),'PUBLIC_ARCHIVE_BOOTSTRAP')

  need(spec['expected_objects']==22769 and spec['expected_assets']==125 and not spec.get('test_dimensions'),'PRODUCTION_EXACT_DIMENSIONS')
 approval_path=Path(profile['native_work_root'])/'authority/ACTIVATION_APPROVAL.json'
 need(approval_path.is_file(),'ROOT_ACTIVATION_APPROVAL_REQUIRED')
 approval=read(approval_path)
 need(approval['status']=='ROOT_APPROVED_COMPLETE_EXACT_V3_SUITE'and approval['spec_sha256']==expected and approval['code_version_id']==spec['code_version_id'],'ROOT_APPROVAL_REQUIRED')
 need(spec['suite_complete']is True and spec['scientific_starts_authorized']is False,'COMPLETE_DATA_ONLY_SUITE_REQUIRED')
 return r,spec,profile
def closed_archives(r,spec,resources):
 reports=[]
 for row in spec['archives']:
  frozen,_=ref_read(row['source_manifest_ref'],resources);root=Path(row['bundle'])
  need((root/'COMMIT.json').is_file(),'ALL_ARCHIVE_COMMITTED')
  commit=read(root/'COMMIT.json');source_raw=bounded(root/'SOURCE_MANIFEST.json')
  expected=sha((json.dumps(frozen,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode())
  need(commit['manifest_sha256']==expected==sha(source_raw)and commit['object_id']==frozen['object_id'],'ARCHIVE_MANIFEST_BOUND')
  for name,key in [('TREE_VERIFICATION.json','tree_verification_sha256'),('RANGE_INDEX.json','range_index_sha256')]:
   need(sha(bounded(root/name))==commit[key],'ARCHIVE_CLOSED_'+name)
  receipt=read(root/'RECEIPT.json')
  need(receipt['manifest_sha256']==expected and receipt['object_id']==commit['object_id']and receipt['Source_full_SHA_matches']is True and receipt['true164_closed_reopen_whole_SHA_matches']is True,'ARCHIVE_CLOSED_FULL_SHA_RECEIPT')
  reports.append(dict(bundle=str(root),COMMIT_sha256=sha(bounded(root/'COMMIT.json')),source_manifest_sha256=expected))
 need(len(reports)==spec['archive_batch_count'],'ARCHIVE_DENOMINATOR')
 return reports
def stage_paths(profile,spec,stage):
 work=Path(profile['native_work_root'])/'integrations'/spec['integration_id'];work.mkdir(parents=True,exist_ok=True)
 return work,work/(stage+'.PHASE_RECEIPT.json')
def marker_done(r,spec,profile,stage,specsha):
 path=Path(spec['markers'][stage])
 if not path.exists():return None
 m=read(path)
 need(m.get('schema')=='SM70_BINDING_STAGE_MARKER_V3'and m['stage']==stage and m['integration_spec_sha256']==specsha and m['code_version_id']==spec['code_version_id'],'OLD_OR_WRONG_MARKER')
 receipt,_=ref_read(m['phase_receipt_ref']);need(receipt['stage']==stage and receipt['integration_spec_sha256']==specsha and receipt['code_version_id']==spec['code_version_id'],'MARKER_RECEIPT_BINDING')
 return receipt
def save_phase(r,spec,profile,stage,specsha,result,resources):
 work,path=stage_paths(profile,spec,stage)
 receipt=dict(schema='SM70_BINDING_PHASE_RECEIPT_V3',stage=stage,integration_spec_sha256=specsha,code_version_id=spec['code_version_id'],source_KEEP=True,scientific_qualification_granted=False,result=result,observed_unix=time.time())
 raw=canon(receipt)
 if path.exists():
  prior=read(path)
  identity=['schema','stage','integration_spec_sha256','code_version_id','source_KEEP','scientific_qualification_granted']
  need(all(prior.get(k)==receipt[k]for k in identity)and prior['result']==result,'PHASE_RECEIPT_COLLISION')
  receipt=prior;raw=bounded(path)
 else:
  with path.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
 phase_public=module('storage').Writer(r.library_root(),resources,module('primitive')).cas(raw,'receipts/v3_phases/'+spec['integration_id'])
 marker=dict(schema='SM70_BINDING_STAGE_MARKER_V3',stage=stage,integration_spec_sha256=specsha,code_version_id=spec['code_version_id'],pins=result.get('pins'),phase_receipt_ref=dict(path=phase_public['path'],sha256=phase_public['sha256']))
 target=Path(spec['markers'][stage]);target.parent.mkdir(parents=True,exist_ok=True)
 need(not os.path.lexists(target),'STALE_MARKER_NOT_RECONCILED')
 temp=target.with_name(target.name+'.v3-owned-'+str(os.getpid()))
 with temp.open('xb')as f:f.write(canon(marker));f.flush();os.fsync(f.fileno())
 primitive=module('primitive');primitive.rename_noreplace(temp,target)
 resources.check(True);return receipt
def prepare_inputs(r,spec,writer,resources):
 # Copy original metadata bytes to public CAS; no old JSON string is rewritten.
 source_map,_=ref_read(spec['source_relocation_ref'],resources)
 mapping={};dedup={}
 for original,row in source_map['mapping'].items():
  physical=Path(source_map['root'])/row['relative_path']
  if row['sha256']not in dedup:
   raw=bounded(physical);need(sha(raw)==row['sha256'],'SOURCE_METADATA_CAS_SHA');resources.account(len(raw),'read')
   result=writer.cas(raw);dedup[row['sha256']]=result
  result=dedup[row['sha256']]
  mapping[original]=dict(relative_path=str(Path(result['path']).relative_to(writer.root)),sha256=row['sha256'],bytes=result['bytes'])
 # New closed archive chains did not exist in the old snapshot. Snapshot metadata only.
 objects,_=ref_read(spec['base_all_objects_ref'],resources)
 roots={next(p.parent for p in Path(o['storage']['path']).parents if p.name=='tree')for o in objects.values()}
 legacy_roots={Path(x['root'])for x in spec['legacy_routes']}
 for root in sorted(roots-legacy_roots):
  for name in ['COMMIT.json','SOURCE_MANIFEST.json','RECEIPT.json','TREE_VERIFICATION.json','RANGE_INDEX.json']:
   original=str(root/name)
   if original in mapping:continue
   raw=bounded(root/name);resources.account(len(raw),'read');result=writer.cas(raw)
   mapping[original]=dict(relative_path=str(Path(result['path']).relative_to(writer.root)),sha256=result['sha256'],bytes=result['bytes'])
 for key in ['base_all_objects_ref','base_all_bundles_ref']:
  ref=spec[key]
  if ref['original_path']not in mapping:
   doc,raw=ref_read(ref,resources);result=writer.cas(raw);mapping[ref['original_path']]=dict(relative_path=str(Path(result['path']).relative_to(writer.root)),sha256=result['sha256'],bytes=result['bytes'])
 return objects,mapping

def exact_frozen_scope(spec,objects,bundles,resources):
 if spec['execution_scope']!='PRODUCTION':return
 contract,_=ref_read(spec['scope_contract_ref'],resources)
 need(spec['scope_contract_ref']['sha256']=='c7838d3704ffbe0204fba9c43a903f0f8fa007e55361ff79333851f0bfbf72a6','PARENT_SCOPE_CONTRACT_SHA')
 need(spec['base_all_objects_ref']['sha256']==contract['all_objects_raw_sha256']=='85b0d7a4866d58852d8541f6d46bf95ed77c4c47983904ca687334527be7cb17','FROZEN_ALL_OBJECTS_SHA')
 need(spec['base_all_bundles_ref']['sha256']==contract['all_bundles_raw_sha256']=='7ebb0949d9f81cd47d1d0cc4abab0596318babd6eafb2fb3295e8b0325182cc6','FROZEN_ALL_BUNDLES_SHA')
 edges=[];used=set();bids=set()
 for b in bundles:
  need(b['bundle_id']not in bids,'DUPLICATE_BUNDLE');bids.add(b['bundle_id']);names=set()
  for m in b['members']:
   need(m['relative_path']not in names,'DUPLICATE_MEMBER_PATH');names.add(m['relative_path'])
   need(m['sha256']in objects and objects[m['sha256']]['size']==m['size'],'REFERENCE_OBJECT_SIZE')
   used.add(m['sha256']);edges.append([b['bundle_id'],m['relative_path'],m['sha256'],m['size']])
 need(used==set(objects)and sorted(bids)==contract['expected_bundle_ids'],'FROZEN_SCOPE_REFERENCE_CLOSURE')
 need(sha(('\n'.join(sorted(objects))+'\n').encode())==contract['expected_object_id_set_sha256']=='a007b5b9fd7e15bc06ca8a21421dcaa6d73e8aeaaa152611d9f291ed6a3ba11f','FROZEN_OBJECT_SET')
 need(sha(canon(sorted(edges)))==contract['expected_member_reference_graph_sha256']=='dfce715212f36408b272d21a9b6f5c6d22d97caa686ef12c8f00ce692f2c5e6f','FROZEN_MEMBER_GRAPH')
 need(len(bundles)==125 and len(objects)==22769 and len(edges)==25149 and sum(o['size']for o in objects.values())==972603859656,'FROZEN_SCOPE_DENOMINATORS')

def activate_aliases(spec,profile,primitive):
 for alias in spec.get('public_aliases',[]):
  path=Path(alias['path']);target=Path(alias['target'])
  need(str(path)in['/root/workspace/assets/traces','/root/workspace/assets/bin/trace-assets']or profile['execution_scope']=='QUALIFICATION','PUBLIC_ALIAS_SCOPE')
  path.parent.mkdir(parents=True,exist_ok=True)
  if os.path.lexists(path):
   need(path.is_symlink()and path.resolve()==target.resolve(),'PUBLIC_ALIAS_COLLISION')
  else:path.symlink_to(os.path.relpath(target,path.parent));primitive.fsync_dir(path.parent)

def publish(r,spec,profile,resources,activate=True):
 storage=module('storage');primitive=module('primitive');lib=r.library_root();writer=storage.Writer(lib,resources,primitive)
 # A crash after atomic activation but before the phase marker must not rebuild a
 # binding from a later FUSE inode assignment or reopen old source metadata.
 current=lib/'catalog/CURRENT'
 if activate and current.exists():
  need(current.stat().st_size<=128*2**20,'CURRENT_METADATA128MIB')
  raw_current=bounded(current);resources.account(len(raw_current),'read');prior=json.loads(raw_current)
  if prior.get('schema')=='SHARED_SM70_TRACE_LIBRARY_V3'and prior.get('code_version_id')==spec['code_version_id']and prior.get('integration_id')==spec['integration_id']and prior.get('semantic_spec_sha256')==sha(canon(spec)):
   with r.Operation(resources=resources)as op:
    catalog,envelope=r.load_public_catalog(op)
    need(len(catalog['assets'])==spec['expected_assets']and len(catalog['overlay']['bindings'])==spec['expected_objects'],'RESUMED_PUBLICATION_EXACT_COUNTS')
    target=current.resolve(strict=True);data=bounded(target);resources.account(len(data),'read')
    result=dict(status='PASS_V3_BOUND_CATALOG_PUBLICATION',pins=r.gate_pins(catalog),catalog_id=catalog['catalog_id'],assets=spec['expected_assets'],objects=spec['expected_objects'],publication=dict(path=str(target),sha256=sha(data),bytes=len(data)),pointer=dict(status='ALREADY_EXACT_POINTER',path=str(current),target=str(target)),source_KEEP=True,scientific_qualification_granted=False)
   writer.pointer('tools/trace-assets',PACKAGE/'trace-assets-r5',spec['expected_previous_command_sha256'])
   activate_aliases(spec,profile,primitive)
   return result
 objects,mapping=prepare_inputs(r,spec,writer,resources)
 bundles_doc,_=ref_read(spec['base_all_bundles_ref'],resources)
 exact_frozen_scope(spec,objects,bundles_doc,resources)
 resolver=r.Relocation(lib,mapping,strict=True)
 with r.Operation(resolver,resources)as op:
  base=spec['base_all_objects_ref'];bundles=spec['base_all_bundles_ref']
  proof_index,_=ref_read(spec['current_proof_index_ref'],resources)
  r.attach_legacy(op,spec['legacy_routes'],spec['target_config'])
  reused=1183 if profile['execution_scope']=='PRODUCTION'else spec['test_dimensions']['reused']
  overlay=op.c.build_overlay(base['original_path'],proof_index,spec['target_config'],reused)
  need(overlay['all_objects']==spec['expected_objects'],'ALL_OBJECTS_EXACT')
  assets=r.enrich_assets(op.read(bundles['original_path']),spec['architecture_by_sha'])
  need(len(assets)==spec['expected_assets'],'ALL_ASSETS_EXACT')
  need(sum(len(a['members'])for a in assets)==spec['expected_declared_members'],'ALL_DECLARED_MEMBER_REFERENCES')
  need(sum(o['size']for o in objects.values())==spec['expected_unique_bytes'],'ALL_DISTINCT_CONTENT_BYTES')
  if profile['execution_scope']=='PRODUCTION':
   from collections import Counter
   need(dict(Counter(a['suite']for a in assets))==spec['expected_suite_counts'],'ALL_SUITE_DENOMINATORS')
  retired,_=ref_read(spec['retired_source_reuse_ref'],resources);retired_by={x['key']:x for x in retired['objects']}
  source_provenance={}
  for key,o in objects.items():
   records=[]
   for row in o['sources']:
    record=dict(row)
    if record.get('key')in retired_by:
     record.update(original_path_disposition='HISTORICAL_SOURCE_ALIAS_RETIRED_BY_OTHER_AUTHORIZED_STORAGE_TASK',new_original_source_body_read_claimed=False,verified_content_reuse_proof=spec['retired_source_reuse_ref'])
    records.append(record)
   source_provenance[key]=records
  for a in assets:
   a['availability']='READY_TARGET_BOUND_ALL_DECLARED_MEMBERS'
   for m in a['members']:writer.link(Path('bundles')/a['bundle_id']/'tree'/m['relative_path'],objects[m['sha256']]['storage']['path'])
   writer.link(a['relative_view_path'],lib/a['relative_tree_path'])
   writer.json(Path('bundles')/a['bundle_id']/'MANIFEST_V3.json',a)
  c=dict(schema='SHARED_SM70_TRACE_LIBRARY_V3',base_all_objects_sha256=op.sha(base['original_path']),base_all_bundles_sha256=op.sha(bundles['original_path']),overlay_id=overlay['overlay_id'],overlay=overlay,assets=assets,source_provenance=source_provenance,science_acceptance_granted=False,profile=r.PROFILE,issues_path='quarantine/INPUT_ISSUES_V3.json',coverage_path='catalog/SUITE_COVERAGE_V3.json')
  c['catalog_id']=op.c.catalog_id(c)
  envelope=dict(schema='SHARED_SM70_TRACE_LIBRARY_V3',integration_id=spec['integration_id'],semantic_spec_sha256=sha(canon(spec)),catalog_id=c['catalog_id'],catalog=c,base_all_objects_ref=dict(path=base['original_path'],sha256=base['sha256']),base_all_bundles_ref=dict(path=bundles['original_path'],sha256=bundles['sha256']),relocation=dict(relative_root='.',mapping=mapping),legacy_routes=spec['legacy_routes'],profile=r.PROFILE,pins=r.gate_pins(c),code_version_id=spec['code_version_id'],science_acceptance_granted=False)
  envelope['publication_id']=r.digest(r.canon(envelope))
  target=writer.json(Path('catalog/versions')/(envelope['publication_id']+'.json'),envelope)
 if not activate:return dict(status='PASS_R5_PREPARED_CATALOG_NO_ACTIVATION',pins=r.gate_pins(c),publication=target,source_KEEP=True,scientific_qualification_granted=False)
 # All source/proof cache end checks completed before mutable activation.
 issues,_=ref_read(spec['issues_ref'],resources);coverage,_=ref_read(spec['coverage_ref'],resources)
 writer.json('quarantine/INPUT_ISSUES_V3.json',issues);writer.json('catalog/SUITE_COVERAGE_V3.json',coverage)
 pointer=writer.pointer('catalog/CURRENT',target['path'],spec['expected_previous_current_sha256'])
 writer.pointer('tools/trace-assets',PACKAGE/'trace-assets-r5',spec['expected_previous_command_sha256'])
 activate_aliases(spec,profile,primitive)
 return dict(status='PASS_V3_BOUND_CATALOG_PUBLICATION',pins=r.gate_pins(c),catalog_id=c['catalog_id'],assets=spec['expected_assets'],objects=spec['expected_objects'],publication=target,pointer=pointer,source_KEEP=True,scientific_qualification_granted=False)

def validate_saved(r,spec,profile,stage,receipt,resources):
 need(receipt['result']['status']==dict(publish='PASS_V3_BOUND_CATALOG_PUBLICATION',cross='PASS_EXACT_V3_ALL_ASSET_METADATA_ACCESS_NOT_FRESH_SHA',restore='PASS_EXACT_V3_ALL_OBJECT_NATIVE_RESTORE',finish='PASS_EXACT_V3_FINISH_VALIDATION')[stage],'SAVED_PHASE_STATUS')
 with r.Operation(resources=resources)as op:
  c,envelope=r.load_public_catalog(op)
  need(receipt['result']['pins']==r.gate_pins(c),'SAVED_PHASE_CURRENT_CATALOG_PINS')
  if stage=='restore':
   work=Path(profile['native_work_root'])/'integrations'/spec['integration_id']
   now=r.finish_receipt(op,c,work/'NATIVE_ALL_OBJECTS_V3.jsonl')
   need(now['objects']==spec['expected_objects']and now['logical_bytes']==spec['expected_unique_bytes'],'SAVED_NATIVE_EXACT_COVERAGE')
 for row in receipt['result'].values():
  if isinstance(row,dict)and'path'in row and'sha256'in row:ref_read(row,resources)
 return receipt
def main(argv=None):
 import argparse
 a=argparse.ArgumentParser(description='Root-approved data-only public V3 migration stages')
 a.add_argument('--stage',choices=['publish','cross','restore','finish','resume'],required=True)
 a.add_argument('--integration-spec',required=True);a.add_argument('--spec-sha256',required=True)
 args=a.parse_args(argv);r,spec,profile=spec_load(args.integration_spec,args.spec_sha256)
 resources=r.Resources(extra_budget_roots=spec.get('migration_budget_roots',[]));resources.check(True)
 work=Path(profile['native_work_root']);work.mkdir(parents=True,exist_ok=True)
 lock=(work/'DATA_GOAL_SUPERVISOR.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 old_owner_lock=None
 try:
  if args.stage=='resume':
   old_owner_lock=(Path(spec['legacy_goal_root'])/'control/SUPERVISOR.lock').open('a+b');fcntl.flock(old_owner_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  stages=['publish','cross','restore','finish']if args.stage=='resume'else[args.stage]
  outputs=[]
  for stage in stages:
   resources.inner.deadline=time.monotonic()+spec['stage_deadlines_seconds'][stage]
   resources.check(True);closed=closed_archives(r,spec,resources)
   old=marker_done(r,spec,profile,stage,args.spec_sha256)
   if old:outputs.append(validate_saved(r,spec,profile,stage,old,resources));continue
   _,orphan_path=stage_paths(profile,spec,stage)
   if orphan_path.exists():
    orphan=read(orphan_path)
    need(orphan.get('schema')=='SM70_BINDING_PHASE_RECEIPT_V3'and orphan['stage']==stage and orphan['integration_spec_sha256']==args.spec_sha256 and orphan['code_version_id']==spec['code_version_id'],'ORPHAN_PHASE_CONTEXT')
    validate_saved(r,spec,profile,stage,orphan,resources)
    outputs.append(save_phase(r,spec,profile,stage,args.spec_sha256,orphan['result'],resources));continue
   if stage=='publish':
    writer_lock=(work/'PUBLIC_METADATA_WRITER.lock').open('a+b');fcntl.flock(writer_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    try:result=publish(r,spec,profile,resources)
    finally:fcntl.flock(writer_lock,fcntl.LOCK_UN);writer_lock.close()
   else:
    need(spec['body_reads_authorized']is True,'FULL_DATA_VALIDATION_AUTHORIZATION_REQUIRED')
    verification=r.load_verified('verification_stages')
    result=getattr(verification,stage)(r,spec,profile,resources)
   need(result.get('scientific_qualification_granted',False)is False,'SCIENCE_UPGRADE_FORBIDDEN')
   outputs.append(save_phase(r,spec,profile,stage,args.spec_sha256,result,resources))
  print(json.dumps(dict(status='PASS_EXACT_REQUESTED_V3_DATA_STAGES',stages=[x['stage']for x in outputs],source_KEEP=True,scientific_starts=0,production_goal_complete_claimed=False)))
 finally:
  if old_owner_lock is not None:fcntl.flock(old_owner_lock,fcntl.LOCK_UN);old_owner_lock.close()
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
