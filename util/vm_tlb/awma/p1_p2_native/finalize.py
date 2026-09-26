#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,shutil
from pathlib import Path
ROOT=Path('/data/c16/awma/p1_p2_native_qualification_20260926');WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-p1-p2-native-qualification-v1');PACK=WT/'docs/vm_tlb/review_packs/AWMA_P1_P2_NATIVE_PROBLEM_QUALIFICATION_V1';REPORT=WT/'docs/vm_tlb/reports/AWMA_P1_P2_NATIVE_PROBLEM_QUALIFICATION_109_V1_REPORT.md';DUR='/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/p1_p2_native_qualification_20260926'
PACK.mkdir(parents=True,exist_ok=True);REPORT.parent.mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def write(p,rows):
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

shutil.copy2(ROOT/'input/P2_INPUT_RECEIPT.json',ROOT/'P2_INPUT_RECEIPT.json')
p1=json.loads((ROOT/'P1_GATE.json').read_text());p2=json.loads((ROOT/'P2_GATE.json').read_text());live=json.loads((ROOT/'P2_STRONG_LIVENESS_RECEIPT.json').read_text());matrix=read(ROOT/'RUN_MATRIX.tsv')
(ROOT/'SOURCE_AND_ASSET_AUDIT.md').write_text('''# Source and asset audit

Status: `PASS`.

- Accepted execution base: `9098443082d8edd4f0efa2fa8922969c0559254a`.
- Goal handoff: `aea9cc79186c23fa163b3c215d1b43eac7c6b174`; literature boundary: `082dd8b36b199e135585c0ba61cab587d6814e60`.
- Model: `Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775`; config SHA `18e18afcaccafade98daf13a54092927904649e1dd4eba8299ab717d5d94ff45`; safetensors SHA `fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe`.
- P1 target input is accepted S2 TEXT T2048 (`0ab5bfe...`); companions are accepted S2 CODE (`7acdc48f...`), accepted S2 STRUCTURED (`890eea66...`), and the explicitly labeled deterministic CODE-roll control. Target and companions were executed through decode step 16 and layer-12 Q/K/V were frozen.
- P2 input is accepted S3 TEXT T8192 (`9e127ae9...`); layer-12 decode-step1 Q and 8,192-token historical K/V were frozen. Exact tensor hashes are in `P2_INPUT_RECEIPT.json`.
- Historical P1 SplitKV/Combine anchors are Lane D V3 (`ba1b4bdb...`) and the Lane A inventory; this round's functional Q/K/V/output receipts supersede filename-only inference.
- Runtime: PyTorch 2.5.1+cu124, Transformers 4.46.3, Triton 3.1.0, driver 580.178.04, RTX4080/SM89. FlashInfer, flash-attn package, xFormers, and local Quest checkout were absent.
- `PREREGISTRATION_AMENDMENT_3.json` closes a clerical bootstrap-filename mismatch: the executed Qwen extractor is hash-bound by `INPUT_SOURCE_CLOSURE.json`; the unused Llama draft is preserved only in raw `superseded_sources/`.
- GPU work was serialized with `/data/c16/locks/c16_gpu_campaign.lock`. No model was downloaded; no Accel-Sim or NVBit full trace ran.
''')
(ROOT/'P2_SELECTOR_CONTRACT.md').write_text('''# P2 selector contract

Implementation label: `QUEST_STYLE_SELECTOR_DIAGNOSTIC_V1`; this is not a full Quest reproduction and does not claim that the dense Qwen model naturally deploys sparse attention.

For layer-12 Qwen2.5-0.5B decode-step1 Q and the first 8,192 historical K/V tokens:

- page size: 16 tokens; 512 pages;
- per physical KV head and channel, precompute page `K_min` and `K_max` outside the query-time chain;
- score in FP32: `sum_i max(q_i*K_min_i, q_i*K_max_i)`;
- rank score descending with `torch.argsort(..., stable=True)`; exact ties retain ascending page ID;
- discovery configurations frozen before timing: Top-256 (50%) and Top-128 (25%);
- gather in exact ranked-page order and token offset 0..15, map each of 14 Q heads to its model-defined GQA KV head, then use the same Flash SDPA consumer;
- ONLINE, paired READY-INDEX and strong CUDA-Graph ONLINE arms must have identical ordered indices and output bytes.

The paired READY-INDEX arm is `DIAGNOSTIC_NOT_IMPLEMENTABLE_BASELINE`, not a strict upper bound. Primary source semantics: Tang et al., QUEST, ICML 2024, https://proceedings.mlr.press/v235/tang24l.html.
''')
(ROOT/'P1_DECISION.md').write_text(f'''# P1 decision

`P1_SOFTWARE_BASELINE_CLOSES_GAP`

Stock Flash SDPA changes the target output across B1/B4: 11 FP16 elements differ, maximum absolute difference is {p1['stock_batch_max_abs']:.12g}, and maximum ordered-code distance is 6. This establishes the numerical phenomenon.

Two contract-preserving software baselines close it:

- fixed physical B4 padding is bitwise invariant but costs {p1['padding_b1_overhead_relative']*100:.3f}% over stock B1;
- the parallel Triton fixed-split-256 producer plus fixed-order per-head combine is bitwise invariant and costs only {p1['fixed_b1_overhead_relative']*100:.3f}% over stock B1. Its B1/B4 timing delta is {p1['fixed_batch_delta_relative']*100:.3f}%, but the larger CV is {p1['fixed_larger_cv']*100:.3f}%, so it fails the pre-registered `>3x CV` materiality gate.

The Triton baseline remains parallel (126/504 producer programs and 14/56 combine programs for B1/B4), has no global lock or single-thread reduction, and is closer to the FP32 reference than stock in the recorded maximum-error check. No material residual remains to localize to completion/commit rather than arithmetic organization. Conditional NCU was therefore not authorized.
''')
g256,g128=p2['configurations']
(ROOT/'P2_DECISION.md').write_text(f'''# P2 decision

`P2_COST_DOMINATED_BY_SELECTOR_COMPUTE`

Both frozen configurations preserve exact ordered indices and bitwise-identical consumer outputs across ONLINE, paired READY-INDEX, and strong CUDA-Graph ONLINE arms. The graph liveness test mutates Q in place, observes changed indices equal to fresh eager selection, and restores the original indices; status is `{live['status']}`.

- Top-256: strong ONLINE {g256['strong_online_median_ms']:.6f} ms versus READY {g256['ready_median_ms']:.6f} ms; residual {g256['residual_ms']:.6f} ms ({g256['residual_relative_to_ready']*100:.3f}%). Selector-only median is {g256['selector_only_median_ms']:.6f} ms.
- Top-128: strong ONLINE {g128['strong_online_median_ms']:.6f} ms versus READY {g128['ready_median_ms']:.6f} ms; residual {g128['residual_ms']:.6f} ms ({g128['residual_relative_to_ready']*100:.3f}%). Selector-only median is {g128['selector_only_median_ms']:.6f} ms.

The residual passes the timing materiality gate in both configurations, but is only {g256['residual_over_selector']*100:.3f}% and {g128['residual_over_selector']*100:.3f}% of independently measured selector arithmetic time. CUDA Graph improves the eager full chain by {g256['eager_to_strong_speedup']:.3f}x and {g128['eager_to_strong_speedup']:.3f}x. There is no localized cost beyond the live selector work itself, so this does not support an index-readiness hardware residual. Conditional NCU was not authorized.
''')
(ROOT/'FINAL_DECISION.md').write_text('''# Final decision

`P1_P2_NATIVE_QUALIFICATION_NO_RESIDUAL_V1`

- P1 exhibits a real batch-dependent FP16 output change in stock Flash SDPA, but a parallel fixed-split software baseline is bitwise batch-invariant with no material residual under the preregistered timing/CV gate.
- P2 has a material ONLINE-minus-READY difference after CUDA-Graph launch optimization, but exact-index and liveness checks show it is fully bounded by the selector's own arithmetic cost; no independent index-publication/readiness cost is localized.
- Neither candidate survives discovery, so no holdout or NCU run is triggered. This stage authorizes no mechanism and no 174/Accel-Sim work.
''')
(ROOT/'NCU_STATUS.md').write_text('# Conditional NCU status\n\n`NOT_RUN_NO_UNEXPLAINED_NATIVE_RESIDUAL`. P1 is closed by software; P2 residual is bounded by selector compute.\n')
(ROOT/'PUBLICATION_HISTORY.md').write_text('''# Publication history

Two pre-close publications are preserved rather than overwritten: raw-index `a8ab4736...` at `.p1_p2_native_qualification_20260926.superseded_preclose_a8ab4736` predates the extraction-source pointer audit; raw-index `53df1b57...` at `.p1_p2_native_qualification_20260926.superseded_preclose_53df1b57` includes Amendment-3 but predates explicit `N/A` normalization of trailing empty timing fields. The canonical stage root is republished atomically after both closures; its final raw-index SHA is recorded in `FINAL_RECEIPT.json`.
''')
# Preserve all engineering failures rather than hiding retries.
fails=[]
for r in matrix:
 if r['status']!='COMPLETE':
  ep=ROOT/'runs'/r['point_id']/'runner_error.txt';fails.append({'point_id':r['point_id'],'candidate':r['candidate'],'arm':r['arm'],'status':r['status'],'formal_receipt_present':(ROOT/'runs'/r['point_id']/'formal.stdout').exists(),'reason':ep.read_text(errors='replace').splitlines()[0] if ep.exists() else 'UNKNOWN','disposition':'SUPERSEDED_BY_R1' if r['point_id'] in ('P1_PADDED_B4_FLASH_SDPA_B1','P1_FIXED_SPLIT_TRITON_256_B1') else 'BOUNDED_ATTEMPT_FAILED_FALLBACK_SUCCEEDED'})
write(ROOT/'ENGINEERING_FAILURES.tsv',fails)
thermal=[]
for r in matrix:
 if r['status']=='COMPLETE':
  def parse(s):
   z=[x.strip() for x in s.split(',')];return (z[1] if len(z)>1 else '',z[-1] if z else '')
  tb,rb=parse(r.get('smi_before',''));ta,ra=parse(r.get('smi_after',''));thermal.append({'point_id':r['point_id'],'temp_before_c':tb,'temp_after_c':ta,'throttle_before':rb,'throttle_after':ra,'admission':'PASS' if ta and int(float(ta))<80 and ra in ('0x0000000000000000','RECORDED_IN_FAILED_PARENT_PROCESS_NOT_SERIALIZED') else ('RECOVERED_TELEMETRY_GAP' if 'RECORDED' in r.get('smi_after','') else 'REVIEW')})
write(ROOT/'THERMAL_VALIDATION.tsv',thermal)
(ROOT/'README.md').write_text(f'''# AWMA P1/P2 native problem qualification V1

Final state: `P1_P2_NATIVE_QUALIFICATION_NO_RESIDUAL_V1`.

P1: `P1_SOFTWARE_BASELINE_CLOSES_GAP`. P2: `P2_COST_DOMINATED_BY_SELECTOR_COMPUTE`.

Start with `FINAL_DECISION.md`, then the two candidate decisions, `P1_P2_DECISION_MATRIX.tsv`, exact numeric/index tables, timing tables, and `NSYS_LAUNCH_STRATA.tsv`. Engineering retries are explicit in `ENGINEERING_FAILURES.tsv`; inference and reproduction boundaries are in `SOURCE_AND_ASSET_AUDIT.md` and `P2_SELECTOR_CONTRACT.md`.

Durable raw authority: `{DUR}`.
''')
(ROOT/'REPORT.md').write_text((ROOT/'README.md').read_text()+'\nNo candidate crossed the scientific STOP boundary into architecture review.\n')
# Raw index and receipt.
idx=[]
for p in sorted(x for x in ROOT.rglob('*') if x.is_file() and x.name not in ('RAW_DATA_INDEX.tsv','SHA256SUMS','FINAL_RECEIPT.json')):idx.append({'relative_path':str(p.relative_to(ROOT)),'size_bytes':p.stat().st_size,'sha256':sha(p)})
write(ROOT/'RAW_DATA_INDEX.tsv',idx)
critical=['PREREGISTRATION.json','P2_INPUT_RECEIPT.json','P1_TARGETS.tsv','P1_NUMERIC_CONTRACT_RESULTS.tsv','P1_TIMING_RESULTS.tsv','P2_TIMING_RESULTS.tsv','P2_INDEX_EQUALITY.tsv','P2_CAUSAL_ACCOUNTING.tsv','P1_P2_DECISION_MATRIX.tsv','FINAL_DECISION.md','RAW_DATA_INDEX.tsv']
(ROOT/'SHA256SUMS').write_text(''.join(f'{sha(ROOT/n)}  {n}\n' for n in critical))
final={'stage':'AWMA_P1_P2_NATIVE_PROBLEM_QUALIFICATION_V1','final_state':'P1_P2_NATIVE_QUALIFICATION_NO_RESIDUAL_V1','p1_decision':'P1_SOFTWARE_BASELINE_CLOSES_GAP','p2_decision':'P2_COST_DOMINATED_BY_SELECTOR_COMPUTE','preregistration_sha256':sha(ROOT/'PREREGISTRATION.json'),'input_receipt_sha256':sha(ROOT/'P2_INPUT_RECEIPT.json'),'raw_index_sha256':sha(ROOT/'RAW_DATA_INDEX.tsv'),'node164_authority':DUR,'valid_formal_points':sum(r['status']=='COMPLETE' for r in matrix),'engineering_failure_records':len(fails),'ncu':'NOT_RUN','holdout':'NOT_TRIGGERED'};(ROOT/'FINAL_RECEIPT.json').write_text(json.dumps(final,indent=2,sort_keys=True)+'\n')
compact=['README.md','REPORT.md','SOURCE_AND_ASSET_AUDIT.md','PUBLICATION_HISTORY.md','PREREGISTRATION.json','PREREGISTRATION_SHA256','PREREGISTRATION_AMENDMENT_1.json','PREREGISTRATION_AMENDMENT_2.json','PREREGISTRATION_AMENDMENT_3.json','INPUT_SOURCE_CLOSURE.json','P1_TARGETS.tsv','P1_NUMERIC_CONTRACT_RESULTS.tsv','P1_TIMING_RESULTS.tsv','P1_DECISION.md','P2_SELECTOR_CONTRACT.md','P2_INPUT_RECEIPT.json','P2_TARGET.tsv','P2_TIMING_RESULTS.tsv','P2_INDEX_EQUALITY.tsv','P2_CAUSAL_ACCOUNTING.tsv','P2_STRONG_LIVENESS_RECEIPT.json','P2_DECISION.md','NSYS_LAUNCH_STRATA.tsv','ENGINEERING_FAILURES.tsv','THERMAL_VALIDATION.tsv','NCU_STATUS.md','P1_P2_DECISION_MATRIX.tsv','FINAL_DECISION.md','RAW_DATA_INDEX.tsv','FINAL_RECEIPT.json']
for n in compact:shutil.copy2(ROOT/n,PACK/n)
for p in PACK.glob('*.tsv'):p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
pack_files=sorted(p for p in PACK.iterdir() if p.is_file() and p.name!='SHA256SUMS')
(PACK/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in pack_files))
shutil.copy2(PACK/'SHA256SUMS',ROOT/'SHA256SUMS')
REPORT.write_text('# AWMA P1/P2 native problem qualification 109 V1 report\n\nFinal state: `P1_P2_NATIVE_QUALIFICATION_NO_RESIDUAL_V1`. Review pack: `docs/vm_tlb/review_packs/AWMA_P1_P2_NATIVE_PROBLEM_QUALIFICATION_V1/`. Durable authority: `'+DUR+'`.\n')
print(json.dumps(final,sort_keys=True))
if __name__=='__main__':pass
