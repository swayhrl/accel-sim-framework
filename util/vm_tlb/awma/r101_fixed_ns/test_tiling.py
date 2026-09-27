#!/usr/bin/env python3
import json,unittest
from pathlib import Path
import torch
from himuon.optimizers.himuon import HiMuon

ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')

class TestRealGradientTiles(unittest.TestCase):
    def test_exact_roundtrip_and_padding(self):
        micro=torch.load(ROOT/'raw/discovery_gradient_microstate.pt',map_location='cpu',weights_only=True)
        receipt=json.loads((ROOT/'R101_TILE_INPUT_RECEIPT_DISCOVERY.json').read_text())
        for edge in (128,256,512):
            expected=[]
            for name in ['model.layers.0.self_attn.q_proj.weight',
                         'model.layers.0.mlp.up_proj.weight',
                         'model.layers.0.mlp.down_proj.weight']:
                G=micro[name]['nesterov_input']
                tiled,info=HiMuon._tile(G,(edge,edge))
                restored=HiMuon._untile(tiled,info)
                self.assertTrue(torch.equal(restored,G))
                expected.append(tiled.reshape(-1,edge,edge))
            actual=torch.load(ROOT/'raw'/f'discovery_tiles_T{edge}.pt',map_location='cpu',weights_only=True)
            self.assertTrue(torch.equal(actual,torch.cat(expected,dim=0)))
            self.assertEqual(len(actual),receipt['tiles'][str(edge)]['tile_count'])
            self.assertTrue(torch.isfinite(actual).all())

    def test_first_step_author_momentum_formula(self):
        p=torch.nn.Parameter(torch.zeros(2,2,dtype=torch.bfloat16))
        grad=torch.tensor([[1.0,-2.0],[0.5,0.0]],dtype=torch.bfloat16)
        opt=HiMuon([p],momentum=0.95,nesterov=True,cuda_graph=False)
        result=opt._compute_momentum(p,grad,0.95,True)
        self.assertTrue(torch.equal(opt.state[p]['momentum_buffer'],grad))
        self.assertTrue(torch.equal(result,grad.add(grad,alpha=0.95)))

if __name__=='__main__':unittest.main()
