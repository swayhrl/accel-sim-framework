#!/usr/bin/env python3
"""CPU-only Round16 R102 authority gate. Never imports torch or touches CUDA."""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from pathlib import Path


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()


def form_b_gate(headers: list[dict], source_has_wrong_base_rejection: bool) -> tuple[bool,list[str]]:
    reasons=[]
    if len(headers)<4: reasons.append('FEWER_THAN_FOUR_VERSIONS')
    else:
        versions=[int(x['metadata']['model_version']) for x in headers[:4]]
        if versions != list(range(versions[0],versions[0]+4)): reasons.append('VERSIONS_NOT_CONSECUTIVE')
        if headers[0]['metadata'].get('sparse') != 'False': reasons.append('FIRST_VERSION_NOT_FULL_ANCHOR')
        if any(x['metadata'].get('sparse') != 'True' for x in headers[1:4]): reasons.append('PATCH_CHAIN_NOT_THREE_DELTAS')
        if any(not x.get('has_base_hash',False) for x in headers[1:4]): reasons.append('PATCH_BASE_HASH_MISSING')
        if any(not x.get('has_target_hash',False) for x in headers[1:4]): reasons.append('RECONSTRUCTED_TARGET_HASH_MISSING')
    if not source_has_wrong_base_rejection: reasons.append('PUBLIC_CONSUMER_WRONG_BASE_REJECTION_MISSING')
    return not reasons,reasons


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--version-tsv',type=Path,required=True);a=p.parse_args();r=a.root;q=r/'receipts';s=r/'source';logs=r/'logs'
    headers=json.load(open(q/'HF_BUCKET_HEADER_AUDIT.json'));bucket=json.load(open(q/'HF_BUCKET_INFO.json'));tree=json.load(open(q/'HF_BUCKET_TREE.json'))
    trl_pr=json.load(open(q/'TRL_pulls_5937.json'));trl_engine=(s/'trl-pr5937-files-8bbc35f4bc7f030053d39063979af6df89a6c925/trl/experimental/async_grpo/delta_engine.py').read_text();trl_diff=(s/'trl-pr5937-files-8bbc35f4bc7f030053d39063979af6df89a6c925/trl/experimental/async_grpo/weight_diff.py').read_text()
    public_wrong_base=bool(re.search(r'base_hash|expected_base|wrong_base',trl_engine,re.I))
    admitted,reasons=form_b_gate(headers,public_wrong_base)
    helix_commit=json.load(open(q/'HELIX_MAIN_COMMIT_API.json'))['sha'];helix_releases=json.load(open(q/'HELIX_RELEASES_API.json'));helix_tags=json.load(open(q/'HELIX_TAGS_API.json'))
    grail_repo=json.load(open(q/'GRAIL_REPO_API.json'));grail_commit=json.load(open(q/'GRAIL_MAIN_COMMIT_API.json'))['sha'];grail_releases=json.load(open(q/'GRAIL_RELEASES_API.json'));grail_tags=json.load(open(q/'GRAIL_TAGS_API.json'));grail_tree=json.load(open(q/'GRAIL_TREE_API.json'))['tree']
    anchors=[x for x in tree if x['path'].startswith('anchors/')];deltas=[x for x in tree if x['path'].startswith('deltas/')]
    trl_file_rows=json.load(open(q/'TRL_pulls_5937_files_per_page_100.json'));trl_blobs={x['filename']:x['sha'] for x in trl_file_rows};grail_blobs={x['path']:x['sha'] for x in grail_tree if x.get('type')=='blob'}
    source_specs=[
      ('HF_delta-weight-sync.md',s/'HF_delta-weight-sync.md',json.load(open(q/'HF_BLOG_CONTENT_API.json'))['sha']),
      ('GRAIL_README.md',s/'GRAIL_README.md',json.load(open(q/'GRAIL_README_API.json'))['sha']),
      ('trl/delta_codec.py',s/'trl-pr5937-files-8bbc35f4bc7f030053d39063979af6df89a6c925/trl/experimental/async_grpo/delta_codec.py',trl_blobs['trl/experimental/async_grpo/delta_codec.py']),
      ('trl/delta_engine.py',s/'trl-pr5937-files-8bbc35f4bc7f030053d39063979af6df89a6c925/trl/experimental/async_grpo/delta_engine.py',trl_blobs['trl/experimental/async_grpo/delta_engine.py']),
      ('trl/weight_diff.py',s/'trl-pr5937-files-8bbc35f4bc7f030053d39063979af6df89a6c925/trl/experimental/async_grpo/weight_diff.py',trl_blobs['trl/experimental/async_grpo/weight_diff.py']),
      ('grail/delta_checkpoint.py',s/'grail-main-54d6342928dc516b1169342d801596fe4b88ef6f/grail/infrastructure/delta_checkpoint.py',grail_blobs['grail/infrastructure/delta_checkpoint.py']),
      ('grail/checkpoint_paths.py',s/'grail-main-54d6342928dc516b1169342d801596fe4b88ef6f/grail/shared/checkpoint_paths.py',grail_blobs['grail/shared/checkpoint_paths.py']),
    ]
    source_bindings={name:{'path':str(path.relative_to(r)),'git_blob':blob,'size_bytes':path.stat().st_size,'sha256':sha256(path)} for name,path,blob in source_specs}
    relevant=[q/'HF_BUCKET_INFO.json',q/'HF_BUCKET_TREE.json',q/'HF_BUCKET_HEADER_AUDIT.json',q/'TRL_pulls_5937.json',q/'TRL_pulls_5937_files_per_page_100.json',q/'GRAIL_REPO_API.json',q/'GRAIL_MAIN_COMMIT_API.json',q/'GRAIL_RELEASES_API.json',q/'GRAIL_TAGS_API.json',q/'GRAIL_TREE_API.json',q/'HELIX_MAIN_COMMIT_API.json',q/'HELIX_RELEASES_API.json',q/'HELIX_TAGS_API.json',q/'HF_BLOG_CONTENT_API.json',logs/'NEW_LOCAL_ASSET_SEARCH.txt',logs/'NEW_NODE164_ASSET_SEARCH.txt']
    result={
      'stage':'AWMA_R102_REAL_UPDATE_BOUNDARY_109_V2','decision':'R102_REAL_UPDATE_INPUT_AUTHORITY_NOT_QUALIFIED_V2','input_admitted':False,'cuda_operations':0,'gpu_lock_acquisitions':0,
      'source_files':source_bindings,
      'historical_authority':'056daae4082aafb4bfaab10db19f004d4d76ec73','starting_head':'6586b2530c38ccd3e7aa620e14990f0c1274bbef',
      'bounded_search':{'old_cutoff':'2026-09-27T15:41:42+08:00','node109_new_assets':{'log':str(logs/'NEW_LOCAL_ASSET_SEARCH.txt'),'qualified_chain_found':False},'node164_new_assets':{'log':str(logs/'NEW_NODE164_ASSET_SEARCH.txt'),'qualified_chain_found':False,'scope':'new top-level AWMA provenance dirs and new model revisions only; no full rescan'}},
      'helix':{'main_commit':helix_commit,'unchanged_from_old_audit':helix_commit=='867f76a82822dd87413da4fec617b7f8e7cf6414','release_count':len(helix_releases),'tag_count':len(helix_tags),'qualified_chain_found':False},
      'pulse':{'paper':'https://arxiv.org/abs/2602.03839v2','public_code_pointer':'https://github.com/huggingface/trl and https://github.com/one-covenant/grail','standalone_public_checkpoint_chain_found':False},
      'trl':{'pr':5937,'head_commit':trl_pr['head']['sha'],'state':trl_pr['state'],'merged':trl_pr['merged'],'bucket_id':bucket['id'],'bucket_private':bucket['private'],'bucket_size_bytes':bucket['size'],'bucket_total_files':bucket['totalFiles'],'anchor_files':len(anchors),'delta_files':len(deltas),'candidate_versions':[x['path'] for x in tree if x['path'] in {'anchors/step_000001.safetensors','deltas/step_000002.safetensors','deltas/step_000003.safetensors','deltas/step_000004.safetensors'}],'candidate_file_xet_hashes':{x['path']:x['xetHash'] for x in tree if x['path'] in {'anchors/step_000001.safetensors','deltas/step_000002.safetensors','deltas/step_000003.safetensors','deltas/step_000004.safetensors'}},'headers':headers,'form_b_admitted':admitted,'rejection_reasons':reasons,'source_semantics':{'detector':'AdamW inversion is documented exact only up to floating-point error; BF16 comparison may miss boundary cases and anchors bound drift','metadata_fields':'PatchMetadata has model_version but no model/run/base hash/target hash','consumer':'applies decoded absolute patches without base-version/hash or target-hash verification'},'payload_downloaded':False,'bounded_bytes_read':'bucket metadata/tree plus four safetensors headers only'},
      'grail':{'main_commit':grail_commit,'release_count':len(grail_releases),'release_asset_count':sum(len(x.get('assets',[])) for x in grail_releases),'tag_count':len(grail_tags),'tracked_tensor_checkpoint_files':[x['path'] for x in grail_tree if x.get('type')=='blob' and re.search(r'\.(pt|pth|safetensors|bin|ckpt|npy|npz)$',x['path'],re.I)],'code_has_full_delta_hash_protocol':True,'actual_public_chain_found':False,'access_boundary':'README/source use R2/S3 credentials and Bittensor coordination; no credentials requested'},
      'missing_scientific_payload':'No source provides either four full adjacent published working-precision versions or a full anchor plus three ordered real patches with authoritative base/target hashes sufficient to prove each target and reject a wrong base.',
      'receipt_files':{str(x.relative_to(r)):{'size_bytes':x.stat().st_size,'sha256':sha256(x)} for x in relevant},
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    chain={x['path']:x for x in tree}
    with a.version_tsv.open('w',newline='') as f:
      w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['candidate','model_version','kind','path','size_bytes','xet_hash','header_sha256','base_hash','target_hash','admission'])
      for h in headers:
        x=chain[h['path']];w.writerow(['TRL_ASYNC_GRPO_PUBLIC_BUCKET',h['metadata']['model_version'],'ANCHOR' if h['metadata']['sparse']=='False' else 'DELTA',h['path'],x['size'],x['xetHash'],h['header_sha256'],'MISSING' if not h['has_base_hash'] else 'PRESENT','MISSING' if not h['has_target_hash'] else 'PRESENT','REJECTED_FORM_B'])
    print(json.dumps({'decision':result['decision'],'trl_reasons':reasons,'output':str(a.output)},sort_keys=True))

if __name__=='__main__':main()
