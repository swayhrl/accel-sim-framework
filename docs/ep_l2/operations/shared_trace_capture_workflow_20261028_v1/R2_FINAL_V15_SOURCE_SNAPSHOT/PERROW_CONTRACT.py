"""Exact remaining3 closed ENTRY witness and stride40 package identity; no execution."""
from pathlib import Path
import json,hashlib,os,re
NATIVE='/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1';REMOTE='/data/c16/rtx4080_suite_fill_20261024_v1/nas_fast_sc_copy_st_20261029_v2'
ORDER=['SCAN_CUDA118_ORIGINAL_N6815744_R2_ALL17_SEED2009_SM89_V1', 'TRANSPOSE_CUDA118_REPEAT2_ORIGINAL1024_OBJECTLINK_V2', 'CUDA118_CONVOLUTION_SEPARABLE_ORIGINAL_3072_REPEAT2_V1']
ROOT_ENTRY_SHA='69a4296477884dbce29310f1bf146fbd76f02073653ca8df1e6e6c79350bd22b'
def need(v,m):
 if not v:raise ValueError(m)
def actual(p):
 p=str(p)
 if str(__file__).startswith('/data/c16/'):return Path(p.replace(NATIVE,REMOTE,1))
 return Path(p.replace(REMOTE,NATIVE,1))
def pinned(r):
 p=actual(r['path']);need(p.is_absolute()and '..'not in p.parts and 0<r['bytes']<=2**20,'bounded absolute metadata')
 for q in[p,*p.parents]:need(not q.is_symlink(),'metadata symlink')
 with p.open('rb')as f:
  a=os.fstat(f.fileno());raw=f.read(2**20+1);z=os.fstat(f.fileno())
 key=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
 need(key(a)==key(z)and len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['sha256'],'pinned metadata raw bytes')
 return json.loads(raw)
def validate_packet(packet,load_ref=None):
 read=pinned if load_ref is None else load_ref
 need(packet['schema']=='EXACT_REPEAT_ROWS_POST_SMOKE_ARCHIVE_INPUTS_V3','new exact3 data schema')
 rows=packet['rows'];ids=[r['job_id']for r in rows]
 need(1<=len(ids)<=3 and len(set(ids))==len(ids)and ids==[q for q in ORDER if q in ids],'exact ordered remaining3 subset')
 expected=[]
 for r in rows:
  q=r['job_id'];expected.extend([r['ordinary_asset_id'],r['derived_asset_id']])
  need(r['ordinary_asset_id']==q+'_ORDINARY_V1'and r['derived_asset_id']==q+'_DERIVED_CTA_STRIDE40_V1','exact pair identities')
  need(r['Root_SMOKE_acceptance']['sha256']==r['Root_SMOKE_acceptance_staged_ref']['sha256']==ROOT_ENTRY_SHA,'Root actual all3 entry acceptance pin')
  a=read(r['Root_SMOKE_acceptance_staged_ref'])
  need(a['schema']=='ROOT_EXACT3_ENTRY_CTA_ACTUAL_ACCEPTANCE_V3'and a['status']=='ALL3_ENTRY_COMPLETE_CTA_RUNTIME_STARTUP_RETIREMENT_ROOT_ACCEPTED_OWNED_CLOSED','Root actual entry owned acceptance')
  rr=[x for x in a['rows']if x['job_id']==q];need(len(rr)==1,'per-row actual Root acceptance')
  x=rr[0];need(x['result_ref']==r['entry_model_result_ref']and x['subview_ref']==r['entry_sample_receipt_ref'],'actual entry refs join')
  need(x['covered_first_witness_subset']==r['covered_feature_witness_subset']and x['remaining_first_witness_features']==r['remaining_unexercised_features']and x['all_features_exercised']is False,'retained subset and remaining features')
 need(len(expected)==len(set(expected)),'unique ordinary/derived IDs')
 return expected
