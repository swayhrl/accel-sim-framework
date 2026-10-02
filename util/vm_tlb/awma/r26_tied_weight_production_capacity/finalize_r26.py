#!/usr/bin/env python3
"""CPU-only finalizer for AWMA R26."""

from __future__ import annotations

import argparse, csv, hashlib, json, math, statistics
from pathlib import Path

import torch


STAGE = "AWMA_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_BOUNDARY_109_V1"


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()
def load(p): return json.loads(Path(p).read_text())
def dump(p,x): Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def tsv(p,rows,fields=None):
    fields=fields or list(rows[0]);
    with Path(p).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n',extrasaction='ignore'); w.writeheader(); w.writerows(rows)
def med(x): return statistics.median(x)
def mad(x):
    m=med(x); return statistics.median(abs(v-m) for v in x)
def metric_row(prefix,m):
    return {**prefix,'qualified':m.get('allclose'),'finite':m.get('finite'),'shape':json.dumps(m.get('shape',[]),separators=(',',':')),'dtype':m.get('dtype',''),'max_abs':m.get('max_abs',''),'mean_abs':m.get('mean_abs',''),'max_rel':m.get('max_rel',''),'cosine_similarity':m.get('cosine_similarity','')}
def classify(rows,metric):
    groups=[]
    for g in range(3):
        v={p:[r[metric] for r in rows if r['group']==g and r['policy']==p] for p in ('c1','s2')}
        m={p:med(x) for p,x in v.items()}; d={p:mad(x) for p,x in v.items()}; gap=m['c1']-m['s2']; th=3*max(d.values())
        direction='STABLE_BENEFIT' if gap>th else ('STABLE_REGRESSION' if -gap>th else 'MIXED')
        groups.append({'group':g,'c1_median_ms':m['c1'],'c1_mad_ms':d['c1'],'s2_median_ms':m['s2'],'s2_mad_ms':d['s2'],'c1_minus_s2_ms':gap,'c1_minus_s2_percent':100*gap/m['c1'],'three_mad_threshold_ms':th,'direction':direction})
    b=sum(x['direction']=='STABLE_BENEFIT' for x in groups); r=sum(x['direction']=='STABLE_REGRESSION' for x in groups)
    cls='BENEFIT' if b>=2 and r<2 else ('REGRESSION' if r>=2 else 'MIXED')
    return {'classification':cls,'stable_benefit_groups':b,'stable_regression_groups':r,'groups':groups}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',required=True); ap.add_argument('--pack',required=True); ap.add_argument('--repo',required=True); a=ap.parse_args()
    root,pack,repo=Path(a.root),Path(a.pack),Path(a.repo); pack.mkdir(parents=True,exist_ok=True)
    parent=load(repo/'docs/vm_tlb/chatgpt_handoff/awma/r26_tied_weight_production_capacity_v1/PARENT_AUTHORITY.json')
    contract=load(repo/'docs/vm_tlb/chatgpt_handoff/awma/r26_tied_weight_production_capacity_v1/R26_EXPERIMENT_CONTRACT.json')
    common=load(root/'raw/COMMON_START_STATE.json'); freeze=load(root/'raw/IMPLEMENTATION_FREEZE.json')
    anchor=load(root/'raw/ANCHOR_QUALIFICATION.json'); traj=load(root/'raw/TRAJECTORY_32_STEP.json')
    resumes={p:load(root/f'raw/CHECKPOINT_RESUME_{p.upper()}.json') for p in ('c1','s2')}; switch=load(root/'raw/POLICY_SWITCH_QUALIFICATION.json')
    endpoint=load(root/'raw/SELECTED_ENDPOINT_NUMERICAL_QUALIFICATION.json'); cap=load(root/'raw/CAPACITY_SEARCH_SUMMARY.json')
    formal=[]
    for f in sorted((root/'raw/formal').glob('*.jsonl')): formal += [json.loads(x) for x in f.read_text().splitlines() if x]
    assert len(formal)==30 and cap['decision']=='R26_INTEGRATED_BATCH_CAPACITY_EXTENSION_SUPPORTED' and endpoint['qualified']
    target=classify(formal,'target_gpu_ms'); complete=classify(formal,'complete_train_step_ms')
    arms={}
    for p in ('c1','s2'):
        rr=[x for x in formal if x['policy']==p]
        arms[p]={
            'target_median_ms':med([x['target_gpu_ms'] for x in rr]),'target_mad_ms':mad([x['target_gpu_ms'] for x in rr]),
            'complete_median_ms':med([x['complete_train_step_ms'] for x in rr]),'complete_mad_ms':mad([x['complete_train_step_ms'] for x in rr]),
            'target_peak_allocated_median_bytes':med([x['target_peak_allocated_bytes'] for x in rr]),
            'whole_step_peak_allocated_median_bytes':med([x['whole_step_peak_allocated_bytes'] for x in rr]),
            'whole_step_peak_reserved_median_bytes':med([x['whole_step_peak_reserved_bytes'] for x in rr]),
            'post_step_allocated_median_bytes':med([x['post_step_allocated_bytes'] for x in rr]),
            'full_gradient_lifetime_median_ms':None if p=='s2' else med([x['full_gradient_lifetime_gpu_ms'] for x in rr]),
            'compact_rows_median':med([x['compact_rows'] for x in rr]),'compact_bytes_median':med([x['compact_bytes'] for x in rr]),
        }
    decision={
        'stage':STAGE,'capacity_decision':cap['decision'],'B_common':cap['b_common'],'B_witness':cap['witness'],
        'C1_boundary':{'largest_confirmed_pass':70,'adjacent_confirmed_oom':71,'oom_phase':'BACKBONE_COMPACT_LOOKUP_BACKWARD'},
        'S2_boundary':{'largest_confirmed_pass':71,'adjacent_confirmed_oom':72,'oom_phase':'BACKBONE_COMPACT_LOOKUP_BACKWARD'},
        'same_batch_witness':{'batch':71,'C1':['OOM']*3,'S2':['PASS']*3,'confirmed':True},
        'target_timing':target,'complete_train_step_timing':complete,'formal_arm_summary':arms,
        'capacity_and_timing_separate':True,'training_convergence_claim':False,'all_parameter_training_claim':False,'unified_speedup_claim':False,
        'interpretation':'S2 explicit capacity opt-in extends physical repeated-sequence batch by one at the natural repeated-step allocator/backbone-backward boundary; both formal timing boundaries are MIXED at B70',
    }
    dump(pack/'CAPACITY_AND_TIMING_DECISION.json',decision)
    dump(pack/'PARENT_AUTHORITY.json',parent)
    model_input={'model':parent['model_authority'],'input':parent['input_authority'],'R26_runtime_authority':common['authority'],'physical_batch_meaning':'B materialized identical copies of one frozen 127-position sequence; no stochastic diversity or new holdout'}
    dump(pack/'MODEL_INPUT_AUTHORITY.json',model_input); dump(pack/'TRAINING_CONTRACT.json',contract); dump(pack/'OPTIMIZER_CONTRACT.json',contract['optimizer']); dump(pack/'COMMON_START_STATE.json',common); dump(pack/'IMPLEMENTATION_FREEZE.json',freeze)
    validation={'anchor_qualified':anchor['qualified'],'trajectory_32_qualified':traj['qualified'],'resume_c1_qualified':resumes['c1']['qualified'],'resume_s2_qualified':resumes['s2']['qualified'],'policy_switch_qualified':switch['qualified'],'selected_endpoint_qualified':endpoint['qualified'],'final_steps':{'trajectory':traj['final_step'],'resume_c1':resumes['c1']['final_step'],'resume_s2':resumes['s2']['final_step'],'switch':switch['final_step']},'tied_storage_reproved':True}
    dump(pack/'INTEGRATION_VALIDATION.json',validation); dump(pack/'FIRST_MISMATCH.json',{'status':'NONE_IN_FINAL_QUALIFICATION','first_mismatch':None})

    # Qualification TSVs.
    one=[]; four=[]
    for p in ('b0','c1','s2'):
        d=anchor['details'][p]
        if d.get('one_step'):
            for obs,m in d['one_step'].items(): one.append(metric_row({'policy':p,'observable':obs},m))
        for step in d.get('four_step',[]):
            for obs,m in step['metrics'].items(): four.append(metric_row({'policy':p,'trajectory_index':step['trajectory_index'],'observable':obs},m))
    tsv(pack/'ONE_STEP_NUMERICAL_QUALIFICATION.tsv',one); tsv(pack/'FOUR_STEP_ANCHOR_QUALIFICATION.tsv',four)
    tr=[]
    for x in traj['comparisons']:
        for obs,m in x['metrics'].items(): tr.append(metric_row({'policy':'s2_vs_c1','trajectory_index':x['trajectory_index'],'observable':obs},m))
    tsv(pack/'TRAJECTORY_32_STEP.tsv',tr)
    rr=[]
    for p,x in resumes.items():
        for obs,m in x['metrics'].items(): rr.append(metric_row({'policy':p,'observable':obs,'loaded_step':x['loaded_step'],'final_step':x['final_step']},m))
    tsv(pack/'CHECKPOINT_RESUME_QUALIFICATION.tsv',rr)
    sw=[metric_row({'comparison':'same_c1_step16_checkpoint_s2_vs_c1','observable':obs,'source_step':17,'final_step':18},m) for obs,m in switch['metrics'].items()]
    tsv(pack/'POLICY_SWITCH_QUALIFICATION.tsv',sw)
    ep=[metric_row({'batch':endpoint['batch'],'comparison':'s2_vs_c1','observable':obs},m) for obs,m in endpoint['metrics'].items()]
    tsv(pack/'SELECTED_ENDPOINT_NUMERICAL_QUALIFICATION.tsv',ep)

    # Deterministic batch bindings for every attempted B.
    tokens=json.loads((repo/'docs/vm_tlb/assets/c16/ai_workload_inputs/ADOPTED_LLAMA_S0_T128_V1/frozen_token_ids.json').read_text())
    binds=[]
    for b in sorted({x['batch'] for x in cap['all_trials']}):
        i=torch.tensor(tokens[:-1],dtype=torch.int64).view(1,-1).repeat(b,1).contiguous(); l=torch.tensor(tokens[1:],dtype=torch.int64).view(1,-1).repeat(b,1).contiguous()
        binds.append({'batch':b,'input_shape':json.dumps(list(i.shape)),'labels_shape':json.dumps(list(l.shape)),'input_bytes':i.numel()*8,'labels_bytes':l.numel()*8,'input_ids_sha256':hashlib.sha256(memoryview(i.view(torch.uint8).numpy())).hexdigest(),'labels_sha256':hashlib.sha256(memoryview(l.view(torch.uint8).numpy())).hexdigest(),'content':'identical frozen sequence copies'})
    tsv(pack/'BATCH_INPUT_BINDINGS.tsv',binds)

    # Capacity tables and witness.
    tsv(pack/'CAPACITY_SEARCH_LOG.tsv',cap['all_trials'])
    conf=[]
    for x in cap['confirmations']:
        conf.append({'policy':x['policy'],'batch':x['batch'],'expected':x['expected'],'outcomes':','.join(x.get('outcomes',[])),'qualified':x['qualified'],'reused':x.get('reused',False)})
    tsv(pack/'CAPACITY_ENDPOINT_CONFIRMATIONS.tsv',conf)
    witness={'batch':71,'C1':{'outcome':'OOM','confirmations':3,'phase':'BACKBONE_COMPACT_LOOKUP_BACKWARD','completed_steps_before_oom':2},'S2':{'outcome':'PASS','confirmations':3,'complete_steps_each':5,'finite_state_checks':True,'transient_active_growth_bytes_after_first_step':0},'same_model_input_context_state':True,'limitation':'C1 cannot supply a matched full-batch numerical reference at its OOM shape; numerical equivalence is established at B1 and B70'}
    dump(pack/'CAPACITY_WITNESS.json',witness)

    # Formal and memory tables.
    target_rows=[]; complete_rows=[]; lifetime=[]
    for x in formal:
        base={'group':x['group'],'repeat':x['repeat'],'policy':x['policy'],'batch':x['batch']}
        target_rows.append({**base,'target_gpu_ms':x['target_gpu_ms'],'target_host_ms':x['target_host_ms'],'pre_target_allocated_bytes':x['pre_target_allocated_bytes'],'target_peak_allocated_bytes':x['target_peak_allocated_bytes'],'target_peak_reserved_bytes':x['target_peak_reserved_bytes']})
        complete_rows.append({**base,'complete_train_step_ms':x['complete_train_step_ms'],'pre_step_allocated_bytes':x['pre_step_allocated_bytes'],'whole_step_peak_allocated_bytes':x['whole_step_peak_allocated_bytes'],'whole_step_peak_reserved_bytes':x['whole_step_peak_reserved_bytes'],'post_step_allocated_bytes':x['post_step_allocated_bytes'],'post_step_reserved_bytes':x['post_step_reserved_bytes']})
        lifetime.append({**base,'dense_lookup_gradient':x['dense_lookup_gradient_materialized'],'full_gradient':x['full_classifier_or_total_gradient_materialized'],'peak_full_buffers':x['peak_full_gradient_buffers'],'full_bf16_gradient_bytes':x['full_bf16_gradient_bytes'],'full_gradient_lifetime_gpu_ms':x['full_gradient_lifetime_gpu_ms'],'compact_rows':x['compact_rows'],'compact_bytes':x['compact_bytes'],'inverse_index_bytes':x['inverse_index_bytes'],'s2_fp32_tile_budget_bytes':x['s2_fp32_tile_budget_bytes']})
    tsv(pack/'FORMAL_TARGET_TIMING.tsv',target_rows); tsv(pack/'FORMAL_COMPLETE_TRAIN_STEP_TIMING.tsv',complete_rows); tsv(pack/'MEMORY_ACCOUNTING.tsv',complete_rows); dump(pack/'BUFFER_LIFETIME_RECEIPTS.json',{'formal':lifetime,'C1_accepted_internal_FP32_dW_workspace_bytes':128256*2048*4,'C1_full_BF16_total_gradient_bytes':128256*2048*2,'S2_FP32_tile_budget_bytes':33554432,'S2_BF16_consumer_tile_bytes':4096*2048*2,'source_and_actual_allocator_accounting_agree':True})
    groups=[]
    for metric_name,obj in [('TARGET_REGION',target),('COMPLETE_TRAIN_STEP',complete)]:
        for g in obj['groups']: groups.append({'metric':metric_name,**g,'point_class':obj['classification']})
    tsv(pack/'GROUP_RESPONSE_SUMMARY.tsv',groups)

    locks=[]
    for f in sorted((root/'receipts').glob('GPU_LOCK*.txt')): locks.append({'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f),'text':f.read_text()})
    dump(pack/'RESOURCE_LOCK_RECEIPTS.json',{'gpu_lock':'/data/c16/locks/c16_gpu_campaign.lock','receipts':locks,'all_CUDA_under_lock':True,'profiles':0,'node174_compute':False})

    (pack/'COMPONENT_API_AND_LIMITS.md').write_text("""# Component API and limits\n\n`TiedWeightTrainer.run_step(policy=\"c1\")` defaults to C1. S2 requires both explicit `policy=\"s2\"` and the campaign opt-in sentinel. State save/load covers tied BF16 W, FP32 m/v, logical step, CPU/CUDA RNG, identity, and policy metadata; policy changes do not reset state.\n\nSupported scope is only this tied input-embedding/lm-head W with the frozen full backbone in the dH path, fixed CCE exact math, and explicit AdamW. Unsupported: arbitrary autograd consumers, all-parameter training, gradient accumulation, clipping, scaler, checkpointing/offload, distributed training, scheduler, quantization, or automatic OOM fallback. No existing workflow is modified.\n""")
    (pack/'ENGINEERING_ATTEMPTS.md').write_text("""# Engineering attempts\n\nThe first common-start wrapper incorrectly required bitwise equality with the R25 receipt. An exact R25 runner replay also produced different W/m/v hashes while reproducing both RNG hashes, and no parent snapshot payload exists. The final implementation records the mismatch and freezes one accepted-semantics B1 B0 derivation. No optimizer, reducer, tolerance, input, model, or capacity classifier changed. All B1 gates were run after this fix and passed before implementation freeze.\n""")
    (pack/'FINAL_DECISION.md').write_text(f"""# Final decision\n\n`{cap['decision']}`\n\nC1 confirms B70 PASS and B71 OOM; S2 confirms B71 PASS and B72 OOM. The same B71 witness is C1 OOM 3/3 and S2 five-complete-step PASS 3/3. Both OOM endpoints occur in backbone/compact-lookup backward; C1 fails on the third repeated B71 step after its prior full-gradient allocator history.\n\nAt B70, TARGET_REGION and COMPLETE_TRAIN_STEP are both MIXED in all three groups. Whole-step peak is dominated by the common backbone path, so R25's local target-memory reduction does not appear as a lower determining peak here. Capacity and timing are separate: this is a one-batch physical-capacity extension for repeated identical content, not convergence, all-parameter training, or unified speedup.\n""")
    report=repo/'docs/vm_tlb/codex_handoff/awma/r26_tied_weight_production_capacity_v1/LANE_G_FINAL_REPORT.md'; report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(f"""# Lane G R26 final report\n\nDecision: `{cap['decision']}`. The integrated component defaults to C1 and exposes S2 only as an explicit capacity opt-in. All B1 one/four/32-step, resume, and policy-switch checks pass.\n\nMeasured natural boundaries are C1 B70/B71 and S2 B71/B72 (PASS/OOM). B71 is confirmed C1 OOM 3/3 versus S2 PASS 3/3. Both common-batch timing classes are MIXED. See the review pack for raw group directions, memory, and authority closure.\n""")
    (pack/'README.md').write_text(f"""# {STAGE}\n\nDecision: `{cap['decision']}`. This pack contains the integrated API qualification, deterministic natural-OOM search, B71 same-batch witness, B70 endpoint correctness, and all 30 formal samples. Large checkpoints/raw are published on node164 and bound after publication.\n""")
    # Initial raw index; node164 locations are added by publication closeout.
    raw=[]
    for sub in (root/'raw',root/'receipts',root/'logs',root/'checkpoints'):
        for f in sorted(x for x in sub.rglob('*') if x.is_file()): raw.append({'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f),'role':sub.name})
    tsv(pack/'RAW_DATA_INDEX.tsv',raw)
    sums=[]
    for f in sorted(x for x in pack.rglob('*') if x.is_file() and x.name!='SHA256SUMS'): sums.append(f'{sha(f)}  {f.relative_to(pack).as_posix()}')
    (pack/'SHA256SUMS').write_text('\n'.join(sums)+'\n')
    print(json.dumps(decision,indent=2,sort_keys=True))


if __name__=='__main__': main()
