#!/usr/bin/env python3
"""Bounded CPU-only accepted-parent identity recheck for R27R1 Gate A."""

import argparse,hashlib,json,subprocess
from pathlib import Path
import torch


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def tsha(t):return hashlib.sha256(memoryview(t.detach().contiguous().cpu().view(torch.uint8).numpy())).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True);ap.add_argument('--pack',required=True);ap.add_argument('--common',required=True);ap.add_argument('--model',required=True);ap.add_argument('--model-receipt',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    repo,pack,common,model=Path(a.repo),Path(a.pack),Path(a.common),Path(a.model);errors=[]
    commit='4dca1cd713df8315b9e04f702d7f3b990c8f4b88';tree='03debf7395f51062c133ad4d534791f2b5fc1770'
    git_tree=subprocess.check_output(['git','-C',str(repo),'rev-parse',f'{commit}^{{tree}}'],text=True).strip()
    if git_tree!=tree:errors.append('closed R27 commit/tree mismatch')
    pack_errors=[]
    for line in (pack/'SHA256SUMS').read_text().splitlines():
        h,n=line.split('  ',1);g=sha(pack/n)
        if h!=g:pack_errors.append((n,h,g))
    if pack_errors:errors.append('closed R27 review-pack mismatch')
    decision=json.loads((pack/'FINAL_DECISION.json').read_text());raw=json.loads((pack/'R26_RAW_READBACK.json').read_text())
    if decision['decision']!='R27_INPUT_OR_SOURCE_NOT_QUALIFIED' or raw['status']!='R27_PARENT_RAW_QUALIFIED':errors.append('accepted R27 decision/raw status mismatch')
    state=torch.load(common,map_location='cpu',weights_only=False)
    common_info={'path':str(common),'bytes':common.stat().st_size,'sha256':sha(common),'logical_step':state.get('step'),'schema':state.get('schema'),'weight_sha256':tsha(state['weight']),'m_sha256':tsha(state['m']),'v_sha256':tsha(state['v']),'cpu_rng_sha256':tsha(state['cpu_rng']),'cuda_rng_sha256':tsha(state['cuda_rng']),'all_tensors_cpu':all(v.device.type=='cpu' for v in state.values() if isinstance(v,torch.Tensor)),'identity':state.get('identity')}
    expected=raw['common_checkpoint']
    if common_info['bytes']!=2626691315 or common_info['sha256']!='09e293774ac9dcb535e1a3d47d72878ff68f3831476175060b1016bce8a28b55' or common_info['logical_step']!=1 or not common_info['all_tensors_cpu']:errors.append('consumed common checkpoint file/state mismatch')
    for n in ('weight','m','v'):
        if common_info[f'{n}_sha256']!=expected[n]['sha256']:errors.append(f'common {n} mismatch')
    source=[]
    for x in raw['frozen_source']:
        p=Path(x['path']);p=repo/'util/vm_tlb/awma/r26_tied_weight_production_capacity'/p.name;g=sha(p);source.append({'path':str(p),'sha256':g,'expected':x['expected'],'qualified':g==x['expected']})
    if not all(x['qualified'] for x in source):errors.append('R26 frozen source mismatch')
    receipt=json.loads(Path(a.model_receipt).read_text());payload=[];total=0
    for x in receipt['payloads']:
        p=model/x['filename'];s=p.stat().st_size;g=sha(p);total+=s;payload.append({'filename':x['filename'],'bytes':s,'sha256':g,'qualified':s==x['size_bytes'] and g==x['sha256']})
    if sha(a.model_receipt)!='7694c95442cc7ff1d3fc8ed1104d5c0d6a50c3a17f779f402ef90669edeb7b47' or total!=2480783094 or not all(x['qualified'] for x in payload):errors.append('model payload authority mismatch')
    cce=[]
    for rel,expected_sha in [('cut_cross_entropy/cce_backward.py','e5402a590ef019692d8341805d3adf18ed95d3062c59236b364322c296b42d36'),('cut_cross_entropy/tl_utils.py','e117b70a0fdc2ec4313fd7d9ba5a7e1d78b30fb478760c3c661f9d717cc65ea4'),('cut_cross_entropy/tl_autotune.py','445745f6c20efcd5bcfb2fbc784361c3b4a3a0e8f2089242fde6d4362a977a20')]:
        p=Path('/data/c16/awma/r26_tied_weight_production_capacity_109_v1_20261002/source/cce')/rel;g=sha(p);cce.append({'path':str(p),'sha256':g,'expected':expected_sha,'qualified':g==expected_sha})
    if not all(x['qualified'] for x in cce):errors.append('CCE source mismatch')
    review=repo/'docs/vm_tlb/chatgpt_handoff/awma/r27r1_varied_batch_capacity_continuation_v1/ACCEPTED_R27_REVIEW.md'
    result={'schema':'R27R1_GATE_A_PARENT_IDENTITY_RECHECK_V1','status':'R27R1_PARENT_AUTHORITY_QUALIFIED' if not errors else 'R27R1_PARENT_AUTHORITY_NOT_QUALIFIED','qualified':not errors,'closed_R27':{'commit':commit,'tree':git_tree,'review_pack_entries':len((pack/'SHA256SUMS').read_text().splitlines()),'review_pack_errors':pack_errors,'decision':decision['decision'],'raw_status':raw['status'],'accepted_review_path':str(review),'accepted_review_sha256':sha(review)},'consumed_common_checkpoint':common_info,'R26_frozen_source':source,'model':{'path':str(model),'receipt':a.model_receipt,'receipt_sha256':sha(a.model_receipt),'payload_total_bytes':total,'payloads':payload},'CCE':cce,'full_207_item_audit_rerun':False,'reused_accepted_R27_Gate_A':not errors,'errors':errors}
    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':result['status'],'errors':errors},sort_keys=True));raise SystemExit(0 if not errors else 2)
if __name__=='__main__':main()
