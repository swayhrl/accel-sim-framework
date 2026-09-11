#!/usr/bin/env python3
"""Derive C13's complete tied Embedding/Output exclusion from immutable sidecars."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PAGE=65536
INPUTS={
 'prefill':(Path('/workspace/m4a-rented-host-pilot/formal-prefill/extracted/m4a-llama-prefill-20260902T182016Z/allocation-sidecar.json'),'8b605b8b19034613106a61ab993dcab60b6eb34509293074b123b44ceeaa839a'),
 'decode1':(Path('/workspace/m4a-rented-host-pilot/formal-decode1/extracted/m4a-llama-decode1-20260903T004138Z/allocation-sidecar.json'),'7a07d6715fe79abd24cfc0b12d2619555e0bf472f5285781e098940acefccaa7'),
}
REG={
 'prefill':Path('/workspace/worktrees/accel-sim-vm-m4b-speculative/configs/vm_tlb/c5_registrations/C11_C5_PREFILL_V2_REGISTRATION.tsv'),
 'decode1':Path('/workspace/worktrees/accel-sim-vm-m4b-speculative/configs/vm_tlb/c5_registrations/C11_C5_DECODE1_V2_REGISTRATION.tsv'),
}
OUT=ROOT/'configs/vm_tlb/c13_diagnostics/selective'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
for roi,(sidecar,expected) in INPUTS.items():
    assert sha(sidecar)==expected
    data=json.loads(sidecar.read_text())
    alloc=[x for x in data['allocations'] if x.get('object_kind')=='WEIGHT']
    assert len(alloc)==1
    tensor=[x for x in data['weight_layout']['tensors'] if x['name']=='model.embed_tokens.weight']
    assert len(tensor)==1 and int(tensor[0]['offset_bytes'])==0
    # lm_head is absent from this flat layout.  The accepted operator map shows
    # final output traffic intersects this same tensor; exclude the entire
    # shared physical range rather than pretending it can be split by kernel.
    assert not any(x['name']=='lm_head.weight' for x in data['weight_layout']['tensors'])
    base=int(alloc[0]['simva_start'],0); size=int(tensor[0]['size_bytes'])
    assert base%PAGE==0 and size%PAGE==0
    begin=base//PAGE; end=begin+size//PAGE-1
    descriptors=[line.split('\t') for line in REG[roi].read_text().splitlines() if line.startswith('descriptor\t')]
    assert len(descriptors)==1
    # This assertion proves the policy overlay is contained by, but does not
    # alter, the immutable V2 conventional-PTW registration.
    _,asid,epoch,reg_begin,reg_end,reg_ppn,ro,mapping=descriptors[0]
    assert int(reg_begin)<=begin<=end<=int(reg_end) and (asid,epoch,ro,mapping)==('0','1','1','0')
    body=('C13_WEIGHT_SEGMENT_EXCLUSION_V1\n'
          '# immutable_sidecar_sha256 %s\n'
          '# selector_parameter model.embed_tokens.weight\n'
          '# tied_output_fact lm_head.weight absent from flat weight_layout; complete shared range excluded\n'
          '# simva_start 0x%x\n# bytes %d\n# pages %d\n'
          'exclude\t%d\t%d\n' % (expected,base,size,size//PAGE,begin,end))
    OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/('C13_%s_EXCLUDE_EMBEDDING_OUTPUT_WEIGHT.tsv'%roi.upper())
    path.write_text(body)
    print('%s\t%s\tpages=%d\tsha256=%s'%(roi,path,size//PAGE,sha(path)))
