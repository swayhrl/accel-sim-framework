#!/usr/bin/env python3
from __future__ import annotations
import json,unittest
from pathlib import Path
import numpy as np
import torch
import xgrammar as xgr

ROOT=Path('/data/c16/awma/r81_legal_vocab_20260927')

def unpack_mask(bitmask:torch.Tensor,vocab_size:int)->np.ndarray:
    words=bitmask.detach().cpu().numpy().view(np.uint8)
    bits=np.unpackbits(words,axis=-1,bitorder='little')
    return bits[...,:vocab_size].astype(bool,copy=False)

def selected(dense_scores,legal):
    if not legal:return None
    return min(legal,key=lambda i:(-dense_scores[i],i))

def grouped_masks(sets):
    groups={}
    for i,ids in enumerate(sets):groups.setdefault(tuple(ids),[]).append(i)
    return groups

class TestLegalityMath(unittest.TestCase):
    def test_union_mapping_and_ragged_on_integer_fixture(self):
        hidden=[[2,-1,3],[0,4,1],[1,1,1],[3,0,-2]]
        weights=[[i%5-2,(i*3)%7-3,(i*7)%11-5] for i in range(17)]
        legal=[[1,4,7,13],[4],[0,1,3,9,16],[]]
        union=sorted(set().union(*map(set,legal)))
        self.assertEqual(len(union),len(set(union)))
        self.assertEqual(sorted(union),union)
        local={idx:j for j,idx in enumerate(union)}
        for b,ids in enumerate(legal):
            scores=[sum(x*y for x,y in zip(hidden[b],w)) for w in weights]
            reference=selected(scores,ids)
            union_scores=[scores[i] for i in union]
            remapped=min(ids,key=lambda i:(-union_scores[local[i]],i)) if ids else None
            direct=min(ids,key=lambda i:(-sum(x*y for x,y in zip(hidden[b],weights[i])),i)) if ids else None
            self.assertEqual(reference,remapped)
            self.assertEqual(reference,direct)
            self.assertEqual(len(ids),len(set(ids)))
            self.assertTrue(all(i in local for i in ids))
        self.assertEqual(grouped_masks([[1,2],[1,2],[3],[4]]),{(1,2):[0,1],(3,):[2],(4,):[3]})

    def test_xgrammar_bitmask_matches_cpu_application(self):
        req=json.loads((ROOT/'raw/fixture/requests.json').read_text())
        info=xgr.TokenizerInfo.deserialize_json((ROOT/'raw/fixture/tokenizer_info.json').read_text())
        schema_id=req[0]['schema_sha256']
        compiled=xgr.CompiledGrammar.deserialize_json((ROOT/'raw/compiled_grammar'/f'{schema_id}.json').read_text(),info)
        matcher=xgr.GrammarMatcher(compiled)
        vocab=151936
        words=xgr.allocate_token_bitmask(1,vocab)
        matcher.fill_next_token_bitmask(words)
        legal=unpack_mask(words,vocab)[0]
        self.assertEqual(legal.shape,(vocab,))
        self.assertGreater(int(legal.sum()),0)
        logits=torch.arange(vocab,dtype=torch.float32).view(1,-1)
        xgr.apply_token_bitmask_inplace(logits,words,vocab_size=vocab,backend='cpu')
        actual=torch.isfinite(logits[0]).numpy()
        np.testing.assert_array_equal(legal,actual)

if __name__=='__main__':unittest.main()
