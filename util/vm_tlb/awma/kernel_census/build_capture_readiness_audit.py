#!/usr/bin/env python3
"""Offline exact-selector readiness audit; it never invokes a GPU tool or producer."""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import defaultdict
from pathlib import Path

ROOT=Path('/data/c16/awma/awma_qwen25_cross_context_census_20260924')
REPO=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-cross-context-readiness-v1')
BASE=REPO/'docs/vm_tlb/review_packs/AWMA_QWEN25_STRUCTURAL_SIGNATURE_AND_SCENARIO_WEIGHT_V1/QWEN25_STRUCTURAL_AND_WEIGHTED_KERNEL_CATALOG_V1.tsv'
AUTH={
 'T256_D32_DERIVED_CONTROL':('T256','DERIVED_CONTROL_S2_PREFIX_256','60a5e2239924fde29e6a872a55f953adb4052e5e5e152fe47a112d18ea773e15'),
 'T8192_D32_ACCEPTED_S3_TEXT':('T8192','ACCEPTED_FROZEN_S3_TEXT_T8192','9e127ae9363358c3b2ed3b09608d9268fd3fc799070d58688aa540be019a3bb4'),
 'B4_T2048_D32_REPLICATED_CONTROL':('B4','CONTROLLED_REPLICATION_OF_ACCEPTED_S2_TEXT','0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9'),
 'T2048_D128_ACCEPTED_S2_TEXT':('D128','ACCEPTED_FROZEN_S2_TEXT_CONTINUED_DECODE','0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9'),
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(path,fields,rows):
 with Path(path).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 rows=[]
 # S2 is deliberately explicit: authority catalog exists, but no per-launch raw selector ledger was recovered by this read-only audit.
 for r in csv.DictReader(BASE.open(),delimiter='\t'):
  if r['phase'] not in ('PREFILL','DECODE') or r['exact_implementation'] in ('','UNKNOWN'):continue
  rows.append(dict(scenario='S2_BASELINE',phase=r['phase'],decode_step='UNKNOWN',global_launch_index='UNKNOWN',exact_function=r['exact_implementation'],grid=r['grid'],block=r['block'],occurrence='UNKNOWN',occurrences_at_selector='UNKNOWN',model_authority='Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775',input_authority='ACCEPTED_S2_TEXT_T2048_SHA256=0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9',driver_sha256='HISTORICAL_S2_DRIVER_IDENTITY_NOT_RECOVERED_IN_COMPACT_CATALOG',classification='SELECTOR_IDENTITY_BLOCKED',traceg_audit='NODE164_TRACEG_NOT_FOUND_BY_READ_ONLY_PATH_AUDIT',producer_compatibility='NVBIT1771_REQUIRES_EXACT_GLOBAL_INDEX_OR_PHASE_SHAPE_SELECTOR_BINDING'))
 for scenario,(d,inp,toksha) in AUTH.items():
  path=ROOT/'analysis'/scenario/'ALL_KERNEL_LAUNCHES.tsv'
  source=list(csv.DictReader(path.open(),delimiter='\t'))
  groups=defaultdict(list)
  for r in source:
   if r['phase'] not in ('PREFILL','DECODE'):continue
   key=(r['phase'],r['decode_step'],r['exact_implementation'],r['grid'],r['block']);groups[key].append(r)
  driver=ROOT/d/'driver.py'; driver_sha=sha(driver)
  for key,items in sorted(groups.items()):
   r=items[0]; phase,step,fun,grid,block=key
   rows.append(dict(scenario=scenario,phase=phase,decode_step=step or 'NOT_APPLICABLE',global_launch_index=r['global_launch_index'],exact_function=fun,grid=grid,block=block,occurrence='1',occurrences_at_selector=len(items),model_authority='Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775',input_authority=f'{inp};token_sha256={toksha}',driver_sha256=driver_sha,classification='CAPTURE_READY',traceg_audit='NODE164_TRACEG_NOT_FOUND_BY_READ_ONLY_PATH_AUDIT',producer_compatibility='NVBIT1771_READY_IF_GLOBAL_INDEX_PHASE_GRID_BLOCK_EXACTLY_BOUND'))
 fields=list(rows[0]);write(a.out/'CAPTURE_READY_CATALOG.tsv',fields,rows)
 summary=[]
 for s in sorted(set(r['scenario'] for r in rows)):
  x=[r for r in rows if r['scenario']==s];summary.append(dict(scenario=s,selector_rows=len(x),capture_ready=sum(r['classification']=='CAPTURE_READY' for r in x),reusable_existing=sum(r['classification']=='REUSABLE_EXISTING' for r in x),input_authority_blocked=sum(r['classification']=='INPUT_AUTHORITY_BLOCKED' for r in x),selector_identity_blocked=sum(r['classification']=='SELECTOR_IDENTITY_BLOCKED' for r in x)))
 write(a.out/'READINESS_SUMMARY.tsv',list(summary[0]),summary)
 receipt={'stage':'AWMA_CROSS_CONTEXT_CAPTURE_READINESS_AUDIT_109_V1','execution_boundary':'READ_ONLY_AUDIT_NO_GPU_LOCK_NO_GPU_WORKLOAD_NO_CAPTURE','node164_traceg_search':'no matching traceg file discovered under /data, /root/share, or /home via node164 alias hrl174new','content_control_authority_search':'no second legal T2048 TEXT frozen input found; S2_CODE/S2_STRUCTURED/S4_STRUCTURED are not TEXT and were not substituted','s2_status':'selector identity blocked because the accepted compact S2 structural catalog lacks per-launch global indices','nvbit1771':'existing mature producer can consume an exact global-launch-index / phase / shape binding once catalog identity is present; this audit did not invoke it'}
 (a.out/'RUN_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 (a.out/'SHA256SUMS').write_text(''.join(f'{sha(x)}  {x.name}\n' for x in sorted(a.out.iterdir()) if x.is_file()))
 print(json.dumps(summary,sort_keys=True))
if __name__=='__main__':main()
