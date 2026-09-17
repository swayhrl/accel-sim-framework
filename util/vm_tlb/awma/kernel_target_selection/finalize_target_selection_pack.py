#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,shutil,subprocess
from pathlib import Path

wt=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-target-selection-v1')
src=Path('/data/c16/awma/qwen25_s2_kernel_target_selection_v1')
pack=wt/'docs/vm_tlb/review_packs/AWMA_KERNEL_TARGET_SELECTION_109_V1'
report=wt/'docs/vm_tlb/codex_handoff/awma/KERNEL_TARGET_SELECTION_109_V1_REPORT.md'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def copy(s,d):d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(s,d)

def main():
 if pack.exists():raise SystemExit('pack exists')
 pack.mkdir(parents=True);report.parent.mkdir(parents=True,exist_ok=True)
 candidates=list(json.loads(p.read_text()) for p in sorted((src/'candidate_targets').glob('*.json')))
 (pack/'README.md').write_text('AWMA_KERNEL_TARGET_SELECTION_V1_COMPLETE_WITH_SCOPE. Offline-only selection from accepted node164 census; all descriptors are CANDIDATE_ONLY_NOT_CAPTURED.\n')
 (pack/'SOURCE_ANCHORS.md').write_text('Coordination handoff = a3dee1888d1bc71189c6f3bd4c0dadc3ce69af67\nAccepted census = 678d7b491d4788369ca0c22717453b20846ab195\nFull inventory SHA256 = 7825697aa23647daee6a38ac4436029c5746fe29a468d303520d3884f2b4abef\nNode164 inventory path = /root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/qwen25_s2_kernel_census_20260917T101100Z/analysis/ALL_KERNEL_LAUNCHES.tsv\n')
 (pack/'CENSUS_REUSE_RECEIPT.md').write_text(Path('/tmp/d0_selection_receipt.txt').read_text())
 for name in ['PREFILL_GEMM_SUBFAMILIES.tsv','DECODE_GEMV_SUBFAMILIES.tsv','DECODE_FLASH_SUBFAMILIES.tsv','PREFILL_FLASH_10_OCCURRENCES.tsv','TARGET_CANDIDATES.tsv','NATIVE_TARGET_ALIGNMENT.md','TARGET_SELECTION_RATIONALE.md','NODE164_VERIFY.stdout','NODE164_VERIFY.stderr','NODE164_VERIFY_SHA256SUMS','LOCAL_SHA256SUMS']:
  copy(src/name,pack/name)
 for p in sorted((src/'candidate_targets').glob('*.json')):copy(p,pack/'candidate_targets'/p.name)
 rawindex={'full_launch_inventory_path':'/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/qwen25_s2_kernel_census_20260917T101100Z/analysis/ALL_KERNEL_LAUNCHES.tsv','sha256':'7825697aa23647daee6a38ac4436029c5746fe29a468d303520d3884f2b4abef','node164_selection_path':'/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/qwen25_s2_kernel_target_selection_v1','node164_verify_sha256':sha(src/'NODE164_VERIFY.stdout')}
 (pack/'RAW_DATA_INDEX.tsv').write_text('artifact\tpath\tsha256\nALL_KERNEL_LAUNCHES.tsv\t'+rawindex['full_launch_inventory_path']+'\t'+rawindex['sha256']+'\n')
 (pack/'TARGET_SELECTION_RATIONALE.md').write_text('Prefill GEMM primary is the highest-time recurring exact+shape subfamily (57.31% GEMM-family; 38.10% Prefill GPU time), using a near-median occurrence. Decode GEMV primary recurs in all 32 steps (40.64% GEMV-family; 20.22% Decode GPU time). Decode Flash has two materially distinct shapes with 82.10% and 17.90% Flash-family time, so both are candidates. No layer/operator role is inferred.\n')
 report.write_text('''# AWMA kernel target selection — node109

Decision: `AWMA_KERNEL_TARGET_SELECTION_V1_COMPLETE_WITH_SCOPE`.

Offline-only selection from the accepted exact census. No NSYS/NCU/NVBit/C16WARP1/simulator-native capture ran in this stage.

Selected candidates (all `CANDIDATE_ONLY_NOT_CAPTURED`):

- Prefill GEMM: CUTLASS Kernel2 `grid=128,3,1`, `block=256,1,1`, reference global launch 285, occurrence 12; 20 recurrences and 57.31% of Prefill GEMM family time (38.10% Prefill GPU time).
- Decode GEMV: `internal::gemvx` int6 `grid=1216,1,1`, `block=16,4,1`, reference launch 1244, occurrence 10; 1,536 occurrences across all 32 steps, 40.64% GEMV-family time (20.22% Decode GPU time).
- Decode Flash splitkv: `grid=1,9,14`, `block=128,1,1`, reference launch 1748, occurrence 17; 768 occurrences across all steps, 82.10% Decode Flash time.
- Decode Flash splitkv-combine: `grid=2,1,1`, `block=128,1,1`, reference launch 1018, occurrence 0; 768 occurrences across all steps, 17.90% Decode Flash time.

Q05 clarification: the 10 Prefill FlashAttention occurrences all use Q05's grid/block. Q05 is representative within that same family, but Decode uses distinct Flash shapes. `LAYER_MAPPING_NOT_PROVEN`; existing Native Prefill Heavy GEMM exact alignment is `NATIVE_TARGET_MATCH_NOT_PROVEN`.

Full inventory remains on node164 and its hash was reverified. No candidate was captured.\n''')
 (pack/'CANDIDATE_STATUS.json').write_text(json.dumps({'status':'AWMA_KERNEL_TARGET_SELECTION_V1_COMPLETE_WITH_SCOPE','candidates':candidates,'native_target_alignment':'NATIVE_TARGET_MATCH_NOT_PROVEN','layer_mapping':'LAYER_MAPPING_NOT_PROVEN'},indent=2,sort_keys=True)+'\n')
 (pack/'GIT_STATE.txt').write_text('branch='+subprocess.check_output(['git','-C',str(wt),'branch','--show-current'],text=True)+'head='+subprocess.check_output(['git','-C',str(wt),'rev-parse','HEAD'],text=True)+'status:\n'+subprocess.check_output(['git','-C',str(wt),'status','--short'],text=True))
 with (pack/'SHA256SUMS').open('w') as f:
  for p in sorted(x for x in pack.rglob('*') if x.is_file() and x.name!='SHA256SUMS'):f.write(f'{sha(p)}  {p}\n')
 print(json.dumps({'pack':str(pack),'report':str(report),'candidates':len(candidates)},sort_keys=True))
if __name__=='__main__':main()
