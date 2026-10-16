#!/usr/bin/env python3
"""Reuse the fixed index; inspect only 30 raw risk witnesses plus bounded context.
No 2D candidate, GPU build/execution, archive search, or full trace scan.
"""
from collections import Counter,defaultdict
import hashlib,json,re
from pathlib import Path
import btree_format_stability_cpu_v1 as m

def main():
    original=Path('/workspace/worktrees/accel-sim-decoupled-l2/hw_run/c2p-polybench-full-20260821/polybench/11.0/polybench-2DConvolution/NO_ARGS/traces/kernel-1.traceg')
    source=Path('/workspace/dtc-hotspot-format-174-v1/source-binding-v1/assets/e63e3bb185ba-2DConvolution.cu')
    m.need(m.sha(source)=='5e12047cbe8cc8a21658d15df602434ee70ebf0b873d45119974fb49da63a192','fixed source')
    rr=[r for r in m.rows() if r['workload']=='2DConvolution'];pcs=defaultdict(list)
    for r in rr:
        m.need(r['mask']=='fffffffe' and r['mode']=='1' and r['anchor_count']=='2','fixed indexed ambiguity')
        pcs[r['pc']].append(r)
    m.need(len(rr)==40940 and len(pcs)==10 and all(len(v)==4094 for v in pcs.values()),'40940/10PC')
    evidence=[];bytes_read=0
    with original.open('rb') as f:
        header=f.read(1024);bytes_read+=len(header)
        for pc,values in sorted(pcs.items()):
            for index in [0,len(values)//2,len(values)-1]:
                r=values[index];offset=int(r['byte_offset']);f.seek(offset);line=f.readline();bytes_read+=len(line)
                m.need(hashlib.sha256(line).hexdigest()==r['original_line_sha256'],'raw witness SHA')
                t,p,mask,j,wi,k=m.shape(line,3)
                m.need(p==int(pc,16) and mask==0xfffffffe and t[j].decode()==r['opcode'] and int(t[wi])==4 and t[k]==b'1' and int(t[k+2])==4,'raw witness shape')
                start=max(0,offset-32768);f.seek(start);context=f.read(offset-start);bytes_read+=len(context)
                # Closest preceding complete CTA and warp headers, not inferred from addresses.
                ctas=list(re.finditer(rb'thread block = (\d+),(\d+),(\d+)',context));warps=list(re.finditer(rb'warp = (\d+)',context))
                m.need(ctas and warps and warps[-1].start()>ctas[-1].start(),'bounded context contains CTA+warp')
                coord=tuple(map(int,ctas[-1].groups()));warp=int(warps[-1][1]);i=8*coord[1]+warp
                m.need(coord[0]==0 and coord[2]==0 and i==index+1,'sample geometry risk-index order')
                base=int(t[k+1],16);op=r['opcode']
                if op.startswith('LDG'):
                    # A fixed PC->stencil hypothesis inferred from first-PC offset only;
                    # the remaining two witnesses are held out. Not a SASS binding.
                    firstbase=int(values[0]['frozen_addresses'].split(',')[0],16)
                    offset4=(firstbase-0x7fdc00000000)//4
                    dy=offset4//4096-1;dx=offset4%4096-1
                    m.need(dy in (-1,0,1) and dx in (-1,0,1),'source stencil hypothesis domain')
                    expected=0x7fdc00000000+4*((i+dy)*4096+1+dx)
                    model=dict(dy=dy,dx=dx,input_base='0x7fdc00000000',base_evidence='original memcpy list')
                else:
                    firstbase=int(values[0]['frozen_addresses'].split(',')[0],16)
                    outputbase=firstbase-4*(4096+1);expected=outputbase+4*(i*4096+1)
                    model=dict(output_base=hex(outputbase),base_evidence='fitted from first raw store; NOT independent allocation binding')
                m.need(base==expected,'held-out risk-witness source-offset hypothesis')
                evidence.append(dict(pc=pc,index=index,line=int(r['line']),byte_offset=offset,original_line_sha256=r['original_line_sha256'],raw=line.decode().strip(),cta=coord,warp=warp,source_i=i,P='fffffffe',recorded_base=hex(base),lane1_if_firstE0=hex(base+4),lane1_if_firstP1_or_firstE1=hex(base),source_offset_hypothesis=model,hypothesis_base_match=True))
    policy=m.B/'docs/dtc_l1/review_packs/LEGACY_FORMAT_SOURCE_BINDING_V1/PRODUCER_POLICY_COMPARISON.json'
    proof=m.B/'docs/dtc_l1/review_packs/LEGACY_FORMAT_SOURCE_BINDING_V1/ARCHIVED_GIT_SOURCE_PROOF.json'
    receipt=dict(status='UNRESOLVED_FORMAT_APPLICABILITY',feasibility='NOT_READY_FOR_WHOLE_KERNEL_DERIVED_INTERPRETATION',
      source=m.facts(source),risk_index=m.facts(m.INDEX),reused_rows=len(rr),pc_counts={p:len(v) for p,v in sorted(pcs.items())},opcode_counts=dict(Counter(r['opcode'] for r in rr)),
      original_identity=dict(path=str(original),bytes=original.stat().st_size,sha256='c330dcb2f491a9376011c8e4b3741ead2481dd0b5e1cb775879d21895939e871',sha_evidence='reuse frozen B full-member audit; not a new whole-member hash scan'),list_identity=m.facts(original.with_name('kernelslist.g')),
      bounded_new_raw=dict(risk_witnesses=30,bytes_read_including_overlapping_context=bytes_read,context_window_limit=32768,header_sha256=hashlib.sha256(header).hexdigest(),witnesses=evidence),
      policies=m.facts(policy),archived_source_git_proof=m.facts(proof),
      facts=['version3 permits both checked E and P address encodings; no capture source/build binding',
             'all40940 indexed P masks lack E; two possible first execution anchors remain',
             'one consistent firstP1 source-offset hypothesis matches30 sampled records across all10 PCs; PC mapping and output base were fitted, not independently bound',
             'sampled EXIT/c0 P=1 followed by P=fffffffe is compatible with an early-exit/E=P model but printed P alone is not execution-mask evidence'],
      missing=['independent all-PC source/SASS/GPR/offset binding, not just fitting10 memory PCs',
               'single dynamic E/predicate/control model covering all65536CTAs/524288warps, including boundary/early EXIT; full-kernel base/stride comparison and heldout beyond fitted samples',
               'independent output allocation/base binding and full-kernel consumer/reference proof if a separately authorized derived profile is proposed'],
      exact_new_input_definition=None,formal_input_created=False,admission='NOT_RUN_NOT_AUTHORIZED',paired_experiments='NOT_RUN_NOT_AUTHORIZED',archive_searches=0,gpu_compiles=0,gpu_runs=0,simulator_runs=0,LUD='NOT_TOUCHED',tool=m.facts(Path(__file__)))
    m.save(m.PACK/'2D_FEASIBILITY_RECEIPT.json',receipt);print(json.dumps({k:receipt[k] for k in ['status','feasibility','reused_rows']}))
if __name__=='__main__':main()
