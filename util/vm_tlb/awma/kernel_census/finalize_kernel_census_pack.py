#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,shutil,subprocess
from pathlib import Path

repo=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-qwen25-census-v1')
root=Path('/data/c16/awma/qwen25_s2_kernel_census_20260917T101100Z')
analysis=root/'analysis'
pack=repo/'docs/vm_tlb/review_packs/AWMA_QWEN25_S2_KERNEL_CENSUS_109_V1'
report=repo/'docs/vm_tlb/codex_handoff/awma/QWEN25_S2_KERNEL_CENSUS_109_V1_REPORT.md'
durable='/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/qwen25_s2_kernel_census_20260917T101100Z'

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def copy(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def writej(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')

def main():
 if pack.exists():raise SystemExit('pack exists')
 idx=json.loads((analysis/'ALL_KERNEL_LAUNCHES_INDEX.json').read_text());idx['durable_destination']=durable+'/analysis/ALL_KERNEL_LAUNCHES.tsv';idx['node164_verify_receipt_sha256']=sha(root/'NODE164_VERIFY.stdout');(analysis/'ALL_KERNEL_LAUNCHES_INDEX.json').write_text(json.dumps(idx,indent=2,sort_keys=True)+'\n')
 # Refresh analysis checksum after durable pointer update.
 with (analysis/'SHA256SUMS').open('w') as f:
  for p in sorted(x for x in analysis.iterdir() if x.is_file() and x.name!='SHA256SUMS'):
   f.write(f'{sha(p)}  {p.name}\n')
 pack.mkdir(parents=True); report.parent.mkdir(parents=True,exist_ok=True)
 workload={'model':'Qwen/Qwen2.5-0.5B-Instruct','revision':'7ae557604adf67be50417f59c2c2f167def9a775','scenario':'S2_TEXT','batch':1,'input':'TEXT','prefill_tokens':2048,'decode_tokens':32,'dtype':'FP16','backend':'SDPA','token_ids_sha256':'0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9'}
 writej(pack/'WORKLOAD_IDENTITY.json',workload)
 (pack/'README.md').write_text('AWMA_QWEN25_S2_KERNEL_CENSUS_V1 complete with scope. One lightweight NSYS CUDA/NVTX census of the exact frozen workload; no NCU, NVBit, C16WARP1, or simulator-native trace capture.\n')
 (pack/'SOURCE_ANCHORS.md').write_text(f'''Coordination branch head: 282b54db2de80bfb694df51517629ef538ff952c.
Previous producer anchor: 5143b4e10aaf2fc47bb60492155d2464b0b726fd.
New NSYS driver SHA256: {sha(root/'driver.py')}.
NSYS report SHA256: {sha(root/'qwen25_s2_census.nsys-rep')}.
SQLite export SHA256: {sha(root/'qwen25_s2_census.sqlite')}.
Node164 durable root: {durable}.
''')
 (pack/'D0_REUSE_AUDIT.md').write_text('Existing qwen05 S2 NSYS evidence was not reused as final census authority: it exposed only a Prefill range and a single Decode STEP=1 NVTX range with no hash-closed frozen Decode32 driver receipt. The new capture has one Prefill and 32 explicit Decode step ranges, and exact frozen-driver output.\n')
 q=json.loads((analysis/'Q05_REPRESENTATIVENESS.json').read_text())
 (pack/'Q05_REPRESENTATIVENESS.md').write_text(f'''Q05 occurrence 0 is one of {q['prefill_flash_fwd_launch_count']} Prefill PYTORCH_FLASH_FWD launches. All share grid/block {q['q05_grid']} / {q['q05_block']}. Q05 duration {q['q05_duration_ns']} ns is the family maximum, versus mean {q['prefill_flash_duration_stats_ns']['mean']} and median {q['prefill_flash_duration_stats_ns']['median']} ns; it remains within a narrow 146,976–159,969 ns same-shape distribution.

Classification: REPRESENTATIVE_WITHIN_SAME_FLASH_FAMILY, with an upper-tail duration caveat. It is PARTIALLY_REPRESENTATIVE for broader Attention: identified FlashAttention accounts for {q['flash_family_gpu_time_share_prefill']:.2%} of Prefill GPU duration, while GEMM/GEMV role attribution is UNKNOWN. It is SPECIAL_CASE for the whole run: Q05 alone is {q['q05_single_launch_gpu_time_share_prefill']:.2%} of Prefill GPU time and does not represent all model kernels.

Decode uses the same normalized flash family but different shapes (1,9,14 and 2,1,1), so Prefill Q05 must not be assumed representative of Decode. LAYER_MAPPING_NOT_PROVEN.
''')
 for name in ['KERNEL_FAMILY_SUMMARY.tsv','SEMANTIC_KERNEL_SUMMARY.tsv','PHASE_SUMMARY.tsv','ATTENTION_KERNEL_SUMMARY.tsv','FLASH_ATTENTION_OCCURRENCES.tsv','ALL_KERNEL_LAUNCHES_INDEX.json','RUN_RECEIPT.json','SEMANTIC_RULES.md','SHA256SUMS']:
  copy(analysis/name,pack/name)
 for name in ['RAW_DATA_INDEX.tsv','NODE164_VERIFY.stdout','NODE164_VERIFY.stderr','NODE164_VERIFY_SHA256SUMS','ARCHIVE_TRANSFER_SHA256SUMS','driver.stdout','driver.stderr','driver_SHA256SUMS','gpu_before.csv','gpu_post_archive.csv']:
  copy(root/name,pack/'evidence'/name)
 writej(pack/'RUN_RECEIPT.json',json.loads((analysis/'RUN_RECEIPT.json').read_text()))
 (pack/'STOP_BOUNDARY.md').write_text('Completion marker: AWMA_QWEN25_S2_KERNEL_CENSUS_V1_COMPLETE_WITH_SCOPE. No additional kernel capture or mechanism work was started.\n')
 report.write_text(f'''# Qwen2.5 S2 kernel census — node109

Decision: `AWMA_QWEN25_S2_KERNEL_CENSUS_V1_COMPLETE_WITH_SCOPE`.

One lightweight NSYS CUDA/NVTX census ran the exact frozen B1/T2048/Decode32 FP16/SDPA workload. It recorded 34,677 total CUDA kernel activities, with 34,072 inside the explicit inference NVTX ranges: 408 Prefill and 33,664 Decode (1,052 each for 32 steps). Full launch inventory SHA256 is `{idx['sha256']}` and resides at `{idx['durable_destination']}`; node164 hash verification passed.

Q05 occurrence 0: 159,969 ns, grid 16,1,14 / block 128,1,1. Prefill has 10 same-shape flash_fwd launches, duration median 154,112.5 ns. FlashAttention family consumes 14.31% of Prefill GPU duration; the single Q05 launch is 1.50%. Decode has 1,536 flash_fwd launches using distinct shapes. Q05 is representative within its same Prefill FlashAttention family, partially representative for broader Attention, and a special case for the whole run. Layer/operator mapping beyond explicit implementation labels is not proven.

No NCU/NVBit/C16WARP1/simulator-native additional trace was run.\n''')
 with (pack/'SHA256SUMS').open('w') as f:
  for p in sorted(x for x in pack.rglob('*') if x.is_file() and x.name!='SHA256SUMS'):
   f.write(f'{sha(p)}  {p}\n')
 print(json.dumps({'pack':str(pack),'report':str(report),'all_index':idx},sort_keys=True))

if __name__=='__main__':main()
