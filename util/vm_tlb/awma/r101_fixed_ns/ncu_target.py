#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import torch
from himuon.optimizers.himuon import HiMuon

ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')

def sha_file(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for x in iter(lambda:f.read(1024*1024),b''):h.update(x)
    return h.hexdigest()

def main(arm):
    edge=128 if arm=='K128' else 512
    path=ROOT/'raw'/f'discovery_tiles_T{edge}.pt'
    authority=json.loads((ROOT/'R101_TILE_INPUT_RECEIPT_DISCOVERY.json').read_text())
    assert sha_file(path)==authority['tiles'][str(edge)]['payload_sha256']
    x=torch.load(path,map_location='cpu',weights_only=True).to('cuda:0')
    frozen=torch.load(ROOT/'raw/discovery_numerical_outputs.pt',map_location='cpu',weights_only=True)[arm].to('cuda:0')
    with torch.no_grad():
        for _ in range(3):HiMuon._newton_schulz_3kernel(x,steps=5)
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_push(f'R101_NCU_{arm}')
        out=HiMuon._newton_schulz_3kernel(x,steps=5)
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_pop()
    good=bool(torch.allclose(out,frozen,rtol=1e-2,atol=1e-2))
    receipt={'arm':arm,'tile_edge':edge,'tile_count':len(x),
      'input_payload_sha256':authority['tiles'][str(edge)]['payload_sha256'],
      'source_commit':'af89eda9a0176effed99e1fe19cc1f8a1a2c9588',
      'steps':5,'same_numerical_output_with_author_tolerance':good,
      'profile_durations_not_primary':True,'ncu_nvtx_range':f'R101_NCU_{arm}'}
    outdir=ROOT/'raw/ncu'/arm
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/'PROFILE_TARGET_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'arm':arm,'same_numerical_output':good}))
    if not good:raise SystemExit(2)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--arm',choices=['K128','L512'],required=True)
    main(p.parse_args().arm)
