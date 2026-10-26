#!/usr/bin/env python3
"""Exact CPU-proven specialist admission. Import is side-effect free."""
import pathlib,json,hashlib,time
UNSUPPORTED=('CALL','RET','JMX','BRX','LDGSTS','CPASYNC','TEX','TLD','SULD','SUST','SUATOM','UTMA','WGMMA','WARPSYNC','BAR.WARP')
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(pathlib.Path(p).read_text())
def verify_admission(package,job_path,job,now=None,approval_path=None):
 package=pathlib.Path(package);now=time.time()if now is None else now
 ap=pathlib.Path(approval_path)if approval_path else package/'ROOT_GPU_WINDOW_APPROVAL.json'
 assert ap.is_file(),'ROOT_GRANT_REQUIRED'
 grant=load(ap)
 assert grant.get('schema')=='ROOT_EXACT_SPECIALIST_GPU_WINDOW_V1'and grant.get('status')=='APPROVED','ROOT_GRANT_NOT_APPROVED'
 assert grant.get('not_before_unix',now+1)<=now<grant.get('expires_unix',0),'ROOT_GRANT_EXPIRED_OR_EARLY'
 assert grant.get('package_manifest_sha256')==sha(package/'PACKAGE_MANIFEST.json'),'ROOT_PACKAGE_PIN_MISMATCH'
 pins=load(package/'PACKAGE_MANIFEST.json')
 for x in pins['files']:
  p=package/x['path'];assert p.resolve().is_relative_to(package.resolve()),'PACKAGE_PATH_ESCAPE'
  assert p.is_file()and sha(p)==x['sha256'],'PACKAGE_MEMBER_DRIFT'
 for x in pins['external_tools']:
  assert sha(x['path'])==x['sha256'],'EXTERNAL_TOOL_DRIFT'
 row=grant.get('jobs',{}).get(job['id']);assert row,'UNKNOWN_JOB_NO_ROOT_GRANT'
 assert row.get('job_sha256')==sha(job_path),'JOB_ROOT_PIN_MISMATCH'
 assert row.get('worker_sha256')==sha(package/'capture_specialist_exact_candidate.py'),'WORKER_ROOT_PIN_MISMATCH'
 scope=load(package/'EXACT_SCOPE.json')
 item=next((x for x in scope['rows']if x['id']==job['id']),None);assert item,'JOB_OUTSIDE_SCOPE'
 assert item['job_sha256']==sha(job_path)and item['asset_id']==job['asset_id'],'SCOPE_JOB_OR_ASSET_DRIFT'
 assert job['input_byte_identity_qualification']=='DETERMINISTIC_SOURCE_INPUT_POLICY_ONLY;ACTUAL_INPUT_BYTE_SNAPSHOT_NOT_GRANTED','INPUT_POLICY_MISLABEL'
 assert job['task']['binary_sha256']==item['binary_sha256']and sha(job['task']['argv'][0])==item['binary_sha256'],'UNKNOWN_OR_DRIFTED_BINARY'
 for x in job['specialist_source_pins']:assert sha(x['path'])==x['sha256'],'SOURCE_ORACLE_DRIFT'
 proof=load(package/item['proof'])
 assert sha(package/item['proof'])==row.get('static_proof_sha256')==item['proof_sha256'],'ROOT_STATIC_PROOF_MISMATCH'
 assert proof['binary_sha256']==item['binary_sha256'],'PROOF_BINARY_MISMATCH'
 assert proof['input_policy']=='DETERMINISTIC_SOURCE_ONLY_NOT_ACTUAL_BYTE_SNAPSHOT','PROOF_INPUT_POLICY'
 return item,proof,grant
def verify_fresh_map(item,proof,map_root,listing):
 map_root=pathlib.Path(map_root)
 assert hashlib.sha256(listing.encode()).hexdigest()==proof['listing_sha256'],'LISTING_PROOF_MISMATCH'
 for name,field in [('manifest.json','manifest_sha256'),('ORDINAL_EXTRACTION.json','extraction_sha256'),('semantic-map.tsv','semantic_map_sha256')]:
  assert sha(map_root/name)==proof[field],'FRESH_MAP_PROOF_MISMATCH_'+name
 m=load(map_root/'manifest.json');ex=load(map_root/'ORDINAL_EXTRACTION.json')
 assert m['binary_sha256']==ex['source_sha256']==item['binary_sha256'],'FRESH_BINARY_MISMATCH'
 assert len(ex['rows'])==proof['images']and ex['rows']==proof['ordinal_rows'],'MISSING_OR_CHANGED_ORDINAL_IMAGE'
 assert len(m['cubins'])==proof['images'],'MISSING_MAPPED_IMAGE'
 for x in ex['rows']:assert sha(map_root/x['preserved_filename'])==x['sha256'],'PRESERVED_IMAGE_DRIFT'
 for x in m['instructions']:
  ts=x['sass'].split();op=ts[1]if ts[0].startswith('@')else ts[0]
  assert not op.startswith(UNSUPPORTED),'UNSUPPORTED_STATIC_DOMAIN'
 return {'status':'EXACT_APPROVED_ORDINAL_ALL_IMAGE_STATIC_CLOSURE','images':proof['images'],'binary_sha256':item['binary_sha256'],'actual_loaded_JIT_qualification':'GPU_REQUIRED_NOT_GRANTED_BY_STATIC_PROOF','input_byte_snapshot':'NOT_GRANTED'}
