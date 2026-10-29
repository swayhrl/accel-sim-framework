"""Root-frozen single future manifest bound; no generic ceiling change and no body I/O."""
from pathlib import Path
import json,hashlib,inspect
HERE=Path(__file__).parent
QID='SCAN_CUDA118_ORIGINAL_N6815744_R2_ALL17_SEED2009_SM89_V1'
INPUT_IDENTITY={'bytes': 1229, 'path': '/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates/r2_shared_post_pipeline_root_20261029_v4/input_identities/scan.json', 'sha256': 'ed00bdf31d08c0175cfee7c69e07db4a60c6d7bbe0340114af5c36184a5d8d8f'}
ASSET=QID+'_ORDINARY_V1'
H_SHA='1dd52a5789936d0ae19ce0388d39c09b29615e49218fed11a7a0b0cf3f74521f'
MEMBER_SHA='b04893e5e4eb8debcffd6f5e863a32e9c513a27118e864b6e58f2c95452587e6'
NB='/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1'
ST='/data/c16/rtx4080_suite_fill_20261024_v1/nas_fast_sc_copy_st_20261029_v2'
def need(v,m):
 if not v:raise RuntimeError(m)
def canonical(m):return json.dumps(m,indent=2,sort_keys=True).encode()+b'\n'
def remote(p):
 p=str(p);return p.replace(NB,ST,1)if p==NB or p.startswith(NB+'/')else p
def same_ref(a,b):return a['bytes']==b['bytes']and a['sha256']==b['sha256']and remote(a['path'])==remote(b['path'])
def root_bound_for(m,d):
 # Only the exact Root-frozen ordinary raw manifest receives its exact total.
 if (d['qid']==QID and d['asset_id']==ASSET and m.get('asset_id')==ASSET and
     m.get('kind')=='FULL_APPLICATION_TRACE'and m.get('logical_bytes')==d['logical_bytes']and
     type(m.get('files'))is list and len(m['files'])==d['file_count']and
     hashlib.sha256(canonical(m)).hexdigest()==d['manifest_ref']['sha256']):
  return d['logical_bytes']
 return 256*1024**2
def install(H,actual_ref):
 need(hashlib.sha256(Path(H.__file__).read_bytes()).hexdigest()==H_SHA,'ORIGINAL_H_BYTES')
 dp=HERE/'ROOT_ACCEPTED_SINGLE_MANIFEST_INSTANCE_V1.json'
 d=json.loads(H.raw(dp))
 need(d['schema']=='ROOT_ACCEPTED_SINGLE_MANIFEST_INSTANCE_V1'and d['status']=='ROOT_ACCEPTED_FROM_REAL_PACKAGE_NOT_TEMPLATE','REAL_ROOT_FROZEN_DESCRIPTOR_REQUIRED')
 need(d['qid']==QID and d['asset_id']==ASSET and d['input_identity_ref']==INPUT_IDENTITY,'FIXED_CASE_AND_INPUT')
 need(type(d['file_count'])is int and 1<=d['file_count']<=256 and type(d['logical_bytes'])is int and d['logical_bytes']>0,'EXACT_INSTANCE_COUNTS')
 need(same_ref(actual_ref,d['manifest_ref']),'EXACT_ROOT_MANIFEST_REF')
 def readref(r):
  b=H.raw(Path(remote(r['path'])));need(len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['sha256'],'EXACT_ROOT_METADATA_REF');return b
 raw=readref(actual_ref);m=json.loads(raw);need(canonical(m)==raw and root_bound_for(m,d)==d['logical_bytes'],'EXACT_RAW_CANONICAL_MANIFEST')
 packet=json.loads(readref(d['actual_package_packet_ref']));need(len(packet['rows'])==1,'ONE_REAL_PACKAGE')
 row=packet['rows'][0]
 need(row['job_id']==QID and row['ordinary_asset_id']==ASSET and row['derived_asset_id']==QID+'_DERIVED_CTA_STRIDE40_V1'and row['input_identity_ref']==INPUT_IDENTITY,'REAL_PACKAGE_CASE_IDENTITY')
 need(same_ref(row['ordinary_manifest_ref'],actual_ref)and row['ordinary_member_count']==d['file_count']and row['ordinary_logical_bytes']==d['logical_bytes'],'REAL_PACKAGE_MANIFEST_JOIN')
 proof=json.loads(readref(d['Root_package_acceptance_ref']))
 need(type(proof.get('status'))is str and 'ROOT_ACCEPTED'in proof['status']and proof['package_row']==row and same_ref(proof['actual_package_packet_ref'],d['actual_package_packet_ref']),'ROOT_ACTUAL_PACKAGE_ACCEPTANCE_JOIN')
 source=inspect.getsource(H.member_rows);need(hashlib.sha256(source.encode()).hexdigest()==MEMBER_SHA,'ORIGINAL_MEMBER_GATE')
 marker="sum(r['bytes']for r in rows)<=256*1024**2";need(source.count(marker)==1,'ONE_TOTAL_GATE')
 source=source.replace(marker,"sum(r['bytes']for r in rows)<=_one_root_bound(m)")
 scope=dict(H.__dict__);scope['_one_root_bound']=lambda candidate:root_bound_for(candidate,d)
 exec(compile(source,'<exact_root_case_total_bound_only>','exec'),scope);H.member_rows=scope['member_rows'];need(H.member_rows(m)==m['files'],'EXACT_MEMBER_GATE')
 return dict(status='EXACT_ROOT_FROZEN_SINGLE_MANIFEST_BOUND_INSTALLED',qid=QID,asset_id=ASSET,manifest_sha256=d['manifest_ref']['sha256'],file_count=d['file_count'],logical_bytes=d['logical_bytes'],all_other_manifests_total_cap=256*1024**2,member_cap=128*1024**2,count_cap=256,transfer_receiver_unchanged=True)
