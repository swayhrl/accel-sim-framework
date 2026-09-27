#!/usr/bin/env python3
"""CPU-only source authority audit for AWMA R102. Never imports torch or touches CUDA."""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path

REQUIRED = [
    'sparse_update/common/compare.py',
    'sparse_update/common/convert.py',
    'sparse_update/megatron/updater.py',
    'sparse_update/megatron/gather_indices.py',
    'sparse_update/slime/sparse_bucket.py',
    'sparse_update/megatron/observer.py',
    'sparse_update/megatron/sparse_data.py',
    'sparse_update/megatron/statistics/manager.py',
    'sparse_update/megatron/statistics/statistics.py',
    'offline/common/io.py',
    'patch/sparse_slime.patch',
    'README.md',
    'LICENSE',
]


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''): h.update(block)
    return h.hexdigest()


def git(root: Path,*args: str) -> str:
    return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()


def positions(text: str, needles: list[str]) -> list[int]:
    out=[];start=0
    for needle in needles:
        i=text.find(needle,start)
        if i < 0: raise AssertionError(f'missing ordered source fragment: {needle}')
        out.append(i);start=i+len(needle)
    return out


def audit(root: Path, expected_commit: str, release_json: Path) -> dict:
    head=git(root,'rev-parse','HEAD')
    if head != expected_commit: raise AssertionError(f'HEAD {head} != {expected_commit}')
    compare=(root/'sparse_update/common/compare.py').read_text()
    updater=(root/'sparse_update/megatron/updater.py').read_text()
    observer=(root/'sparse_update/megatron/observer.py').read_text()
    convert=(root/'sparse_update/common/convert.py').read_text()
    bucket=(root/'sparse_update/slime/sparse_bucket.py').read_text()
    stats=(root/'sparse_update/megatron/statistics/manager.py').read_text()
    offline=(root/'offline/common/io.py').read_text()
    positions(compare,['curr_param.view(-1) != prev_param.view(-1)','mask.nonzero(as_tuple=False).view(-1)','to(torch.int32)'])
    positions(compare,['indices = get_sparse_diff_indices','curr_param.index_select(0, indices)'])
    positions(updater,['shard_model_weight.detach().clone()','get_sparse_diff_indices(','self.union_indices(model_weight_indices)'])
    positions(convert,['torch.where(~torch.isnan(flat))[0]','values = flat[idx64]','idx64.to(torch.int32), values'])
    positions(bucket,['dense_nan_to_sparse_tensor(dense_nan_tensor)','self.merged_indices[offset : offset + nnz].copy_','self.merged_values[offset : offset + nnz].copy_'])
    releases=json.loads(release_json.read_text())
    tracked=git(root,'ls-files').splitlines()
    tensor_suffixes=('.pt','.pth','.safetensors','.bin','.npy','.npz')
    files=[]
    for rel in REQUIRED:
        p=root/rel
        files.append({'path':rel,'git_blob':git(root,'hash-object',rel),'sha256':sha256(p),'size_bytes':p.stat().st_size})
    return {
      'stage':'AWMA_R102_PRECISION_GATED_UPDATE_ENCODING_V1',
      'status':'PASS_SOURCE_AUTHORITY_ONLY',
      'repository':'scitix/helix','commit':head,'tree':git(root,'rev-parse','HEAD^{tree}'),
      'files':files,
      'verified_code':{
        'previous_low_precision_weight_retained':'updater.before_copy detach().clone()',
        'comparison':'flattened curr != flattened prev',
        'indices':'nonzero -> flattened -> int32; PyTorch nonzero output is lexicographically ascending for this 1D mask',
        'values':'get_sparse_diff/observer use index_select; operational bucket path materializes NaN sentinel then where(~isnan) and gathers current values',
        'bucket':'per-dtype concatenated int32 indices and exact values with 256-element capacity alignment',
        'triton_todo_present':'# TODO: Use triton to implement this.',
      },
      'dump_contract':{
        'default':'rank*_indices_*.pt contains per-parameter SparseData history whose mandatory scientific payload is indices',
        'optional_values':'SPARSE_SAVE_VALUES=1 stores changed previous/current values only; default is 0',
        'full_before_after_pair_saved':False,
        'offline_reader':'normalizes model_weight_indices and optional analysis dictionaries; it does not reconstruct full before/after weights',
        'torch_save_present':'torch.save(names_to_sparse_history, tensor_path)' in stats,
        'offline_indices_only':('model_weight_indices' in offline and 'prev_model_weight_values' not in offline and 'curr_model_weight_values' not in offline),
      },
      'public_artifact':{
        'tracked_tensor_like_files':[x for x in tracked if x.lower().endswith(tensor_suffixes)],
        'release_count':len(releases),
        'release_assets':[a.get('name') for r in releases for a in r.get('assets',[])],
        'tags':[],
        'documented_dump_location':'SPARSE_STATS_SAVED_DIR is a user-selected output directory, not a published download',
      },
      'claim_boundary':'Source verifies the software protocol only. It supplies no real before/after tensor authority and is not a hardware limitation.',
    }


def main():
    p=argparse.ArgumentParser();p.add_argument('--helix-root',type=Path,required=True);p.add_argument('--expected-commit',required=True);p.add_argument('--release-json',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=audit(a.helix_root,a.expected_commit,a.release_json)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'output':str(a.output),'files':len(result['files'])},sort_keys=True))

if __name__=='__main__':main()
