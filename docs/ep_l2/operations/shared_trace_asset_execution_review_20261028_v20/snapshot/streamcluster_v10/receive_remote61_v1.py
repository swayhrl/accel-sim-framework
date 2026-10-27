"""Read-only61 receipt closure + prior1550 logical join. No archive/publication."""
import pathlib,hashlib,sys
_C=pathlib.Path(__file__).with_name('sc_remote_common_v1.py');_B=_C.read_bytes()
if hashlib.sha256(_B).hexdigest()!='4472b0ff40f6448dd67f78d861c0e7394d23bce5f48607985df11c01d8063cd5':raise RuntimeError('COMMON_RAW_PIN')
exec(compile(_B,str(_C),'exec'),globals())
import argparse
D=pathlib.Path(__file__).resolve().parent
def native_path(remote):
 p=pathlib.Path(remote);need(p.is_relative_to(RB),'REMOTE_OUTPUT_PREFIX');return NB/p.relative_to(RB)
def main():
 p=argparse.ArgumentParser();p.add_argument('--scope',required=True);p.add_argument('--scope-sha',required=True);p.add_argument('--code-sha',required=True);x=p.parse_args();code_check(D,x.code_sha)
 ap=pathlib.Path(x.scope);a=validate_scope(readref(dict(path=str(ap),bytes=ap.stat().st_size,sha256=x.scope_sha)));root=NB/'runs'/a['run_id']
 release=json.loads((root/'NATIVE_RELEASED.json').read_bytes());need(release['scope_sha256']==x.scope_sha and release['remote_returncode']==0,'ACTUAL_CLOSED_RELEASE')
 z=json.loads((root/'REMOTE_CLOSED_PROPOSAL.json').read_bytes());need(z['scope_sha256']==x.scope_sha and z['status']=='ALL_REMAINING_SELECTED_CLOSED'and set(z['closed_refs'])==set(a['selected']),'ALL61_ACTUAL_CLOSED')
 old=readref(a['adoption_index_ref']);need(old['unique_closed_names']==1550 and old['duplicate_names']==0 and old['remaining_names']==a['original61_selected'],'EXACT1550_PRIOR_LOGICAL_INDEX')
 new=[]
 for n in a['selected']:
  rr=dict(z['closed_refs'][n]);rr['path']=str(native_path(rr['path']));v=readref(rr);q=a['expected'][n];r=v['result']
  need(v['name']==n and v['logical_source']==str(NS/'traces'/n)and v['postprocessor_sha256']==POST_SHA,'NORMALIZED_IDENTITY')
  need(r['source_sha256']==q['source_sha256']and[r[k]for k in ['records','ctas','warps']]==[q[k]for k in ['records','ctas','warps']],'EXACT61_COUNTS')
  gr=native_path(r['grouped']);no_links(gr);need(digest(gr)==r['grouped_sha256']and gr.stat().st_size==r['grouped_bytes'],'NEW61_CURRENT_GROUPED_FULL_SHA')
  original=dict(v['raw_receipt_ref']);original['path']=str(native_path(original['path']));receipt=readref(original);need(receipt==r,'ORIGINAL5D_RECEIPT_BINDING')
  checkpoint=dict(v['checkpoint_ref']);checkpoint['path']=str(native_path(checkpoint['path']));cp=readref(checkpoint);need(cp['source_sha256']==q['source_sha256']and cp['partition_complete']is True and cp['records']==q['records']and len(cp['groups'])==len(cp['partition_members'])==r['shards'],'NAS_CHECKPOINT_CLOSURE')
  sm=dict(v['local_scratch_manifest_ref']);sm['path']=str(native_path(sm['path']));manifest=readref(sm);need(manifest['schema']=='SC_LOCAL_SCRATCH_FINAL_MEMBER_ATTESTATION_V1'and manifest['all_final_payload_on_NAS']is True,'NAS_LOCAL_SCRATCH_MANIFEST')
  new.append(dict(name=n,source_sha256=q['source_sha256'],records=r['records'],grouped_ref=ref(gr),normalized_ref=rr,original_receipt_ref=original))
 need(sum(v['records']for v in new)==a['remaining_records'],'ALL_REMAINING_RECORDS')
 adopted=validate_v8_adopted_rows(a,accepted_v8(a))
 extra=extra2_acceptance();need(sum(r['records']for r in extra['rows'])==6829392,'EXACT2_RECORDS')
 need(old['closed_records']+6829392+adopted['closed_records']+sum(v['records']for v in new)==5518423824,'ALL1611_RECORDS')
 save(root/'SC_ALL1611_LOGICAL_POST_CLOSURE.json',dict(schema='SC_ALL1611_REMOTE_REMAINING_WITH_EXTRA2_AND_V8_ADOPTION_CLOSURE_V3',scope_sha256=x.scope_sha,old1550_adoption_ref=a['adoption_index_ref'],old193_batch_refs=a['old193_batch_refs'],old6_partial_ref=a['old6_partial_ref'],extra2_root_acceptance_ref=ref(D/'ROOT_EXTRA2_ACCEPTANCE_V1.json'),extra2=extra['rows'],V8_adoption_ref=a['Root_V8_closed_adoption_ref'],V8_adopted=adopted['rows'],new_remaining=new,kernels=1611,records=5518423824,postprocessor_sha256=POST_SHA,old1550_and_extra2_NOT_rePOSTed=True,old1550_current_body_SHA_NOT_rechecked_in_this_receiver=True,new59_current_grouped_SHA_reopened=True,accepted_extra2_body_SHA_NOT_rechecked_in_this_receiver=True,archive_current_raw_full_SHA_still_required=True,public_catalog_changed=False,scientific_qualification=False,source_KEEP=True))
if __name__=='__main__':main()
