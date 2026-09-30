#!/usr/bin/env python3
"""Accepted R101 L512 natural invocation, with receipt redirected to R101R5."""
import hashlib
import json
import os
from pathlib import Path

import torch
from himuon.optimizers.himuon import HiMuon

ACCEPTED = Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
NEW = Path('/data/c16/awma/r101r5_native_post_l1_downstream_20260930')
INPUT_SHA = '1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234'
SOURCE_SHA = 'af89eda9a0176effed99e1fe19cc1f8a1a2c9588'

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def main():
    path = ACCEPTED / 'raw/discovery_tiles_T512.pt'
    assert sha(path) == INPUT_SHA
    receipt = json.loads((ACCEPTED / 'R101_TILE_INPUT_RECEIPT_DISCOVERY.json').read_text())
    assert receipt['tiles']['512']['payload_sha256'] == INPUT_SHA
    x = torch.load(path, map_location='cpu', weights_only=True).to('cuda:0')
    frozen = torch.load(ACCEPTED / 'raw/discovery_numerical_outputs.pt', map_location='cpu', weights_only=True)['L512'].to('cuda:0')
    assert len(x) == 44 and tuple(x.shape[1:]) == (512, 512)
    with torch.no_grad():
        for _ in range(3):
            HiMuon._newton_schulz_3kernel(x, steps=5)
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_push('R101_NCU_L512')
        out = HiMuon._newton_schulz_3kernel(x, steps=5)
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_pop()
    good = bool(torch.allclose(out, frozen, rtol=1e-2, atol=1e-2))
    family = os.environ['R101R5_TARGET_FAMILY']
    target = NEW / 'raw/phase_b' / f'{family}.numerical_receipt.json'
    target.write_text(json.dumps({
        'arm': 'L512', 'tile_edge': 512, 'tile_count': 44, 'steps': 5,
        'input_payload_sha256': INPUT_SHA, 'source_commit': SOURCE_SHA,
        'same_numerical_output_with_author_tolerance': good,
        'author_tolerance': {'rtol': 1e-2, 'atol': 1e-2},
        'ncu_nvtx_range': 'R101_NCU_L512',
    }, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'same_numerical_output': good, 'input_sha256': INPUT_SHA}))
    if not good:
        raise SystemExit(2)

if __name__ == '__main__':
    main()
