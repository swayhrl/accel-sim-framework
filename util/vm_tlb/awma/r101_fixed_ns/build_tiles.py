#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
import torch
from himuon.optimizers.himuon import HiMuon

ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
ORDER=['self_attn.q_proj.weight','mlp.up_proj.weight','mlp.down_proj.weight']

def sha_tensor(t):return hashlib.sha256(t.contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()
def sha_file(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for x in iter(lambda:f.read(1024*1024),b''):h.update(x)
    return h.hexdigest()

def build(which):
    layer=0 if which=='discovery' else 12
    raw=ROOT/'raw'/f'{which}_gradient_microstate.pt'
    grad_receipt=json.loads((ROOT/f'R101_GRADIENT_MICROSTATE_RECEIPT_{which.upper()}.json').read_text())
    if sha_file(raw)!=grad_receipt['payload_sha256']:raise ValueError('microstate payload hash mismatch')
    micro=torch.load(raw,map_location='cpu',weights_only=True)
    rows=[];bindings={}
    edges=[128,256,512] if which=='discovery' else [128,512]
    for edge in edges:
        tensors=[];offset=0
        for role in ORDER:
            name=f'model.layers.{layer}.{role}'
            G=micro[name]['nesterov_input']
            if G.dtype!=torch.bfloat16 or not torch.isfinite(G).all():raise ValueError(name)
            tiled,info=HiMuon._tile(G,(edge,edge))
            flat=tiled.view(-1,edge,edge).contiguous()
            count=len(flat)
            rows.append({'fixture':which,'population':f'{which.upper()}_LAYER{layer}',
              'parameter_name':name,'tile_edge':edge,'tile_count':count,
              'tile_start_index':offset,'tile_end_index_exclusive':offset+count,
              'original_shape':json.dumps(list(G.shape),separators=(',',':')),
              'author_tile_info':json.dumps(list(info),separators=(',',':')),
              'tile_sha256':sha_tensor(flat),'input_bytes':flat.numel()*flat.element_size(),
              'zero_padding_h':info[2],'zero_padding_w':info[3]})
            tensors.append(flat);offset+=count
        batch=torch.cat(tensors,dim=0).contiguous()
        path=ROOT/'raw'/f'{which}_tiles_T{edge}.pt'
        torch.save(batch,path)
        bindings[str(edge)]={'tile_count':len(batch),'shape':list(batch.shape),
          'dtype':str(batch.dtype),'tensor_sha256':sha_tensor(batch),
          'payload_sha256':sha_file(path),'payload_bytes':path.stat().st_size,
          'dispatch':'FUSED_ELIGIBLE_F128_OR_K128' if edge==128 else 'COMPILED_3KERNEL_ONLY'}
    out=ROOT/f'R101_TILE_INPUT_RECEIPT_{which.upper()}.json'
    out.write_text(json.dumps({'fixture':which,'layer':layer,
      'author_source_commit':'af89eda9a0176effed99e1fe19cc1f8a1a2c9588',
      'gradient_receipt_sha256':sha_file(ROOT/f'R101_GRADIENT_MICROSTATE_RECEIPT_{which.upper()}.json'),
      'tile_order':'q_proj, up_proj, down_proj; each row-major R,C from HiMuon._tile',
      'tiles':bindings},indent=2,sort_keys=True)+'\n')
    with (ROOT/f'TILE_POPULATIONS_{which.upper()}_EXACT.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)
    print(json.dumps({'fixture':which,'tile_counts':{k:v['tile_count'] for k,v in bindings.items()},
      'tile_input_receipt_sha256':sha_file(out)},sort_keys=True))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--which',choices=['discovery','holdout'],required=True)
    build(p.parse_args().which)
