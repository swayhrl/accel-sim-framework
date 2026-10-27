"""Metadata-only correction; never opens a trace file."""
import pathlib,json,hashlib
P=pathlib.Path;R=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_p42_parallel_mechanism_review_v1');O=R/'shared_address_index'; corrections=[]
for name in ['ATAX_K1','MVT_K1','BICG_K2']:
 p=O/(name+'.json');d=json.loads(p.read_text());assert d['coverage']=='FULL_DECLARED_KERNEL' and d['full_SHA_reverified'] and d['stop_reason']=='EOF' and d['warp_count_seen']==d['qualified_total_warps']==128
 original=p.read_bytes();(O/(name+'.ORIGINAL_SCAN_RECEIPT.json')).write_bytes(original)
 old=d['warps_complete'];assert old==127
 d['raw_reported_warps_complete']=old;d['warps_complete']=128;d['receipt_only_correction']={'reason':'Completed-warp set incorrectly used next CTA coordinate when finalizing prior warp. Complete EOF body parser verified every previous warp declared-count plus terminal EXIT and final warp EXIT; whole SHA matches prior qualified all128-warps body. No address metrics changed.','original_receipt_sha256':hashlib.sha256(original).hexdigest(),'corrector_sha256':hashlib.sha256(P(__file__).read_bytes()).hexdigest(),'trace_reads_in_correction':0,'prior_qualifier_unchanged':True}
 p.write_text(json.dumps(d,indent=2)+'\n');corrections.append({'file':p.name,'old':old,'corrected':128,'original_sha256':hashlib.sha256(original).hexdigest(),'corrected_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(O/'RECEIPT_CORRECTION.json').write_text(json.dumps({'schema':'METADATA_ONLY_WARP_COUNT_CORRECTION_V1','trace_bytes_read':0,'original_scan_receipts_preserved':True,'changes':corrections},indent=2)+'\n')
print(json.dumps(corrections))
