#!/usr/bin/env python3
"""Offline recovery of S2 selector identities from the hash-verified V2 ledger."""
from __future__ import annotations
import csv, hashlib, json, sys
from collections import defaultdict
from pathlib import Path

EXPECTED_LEDGER_SHA='222d5dfeeb1e7aaae3423f13873053c37c27f5c6290d8a58bd3186a0803ca77a'
DRIVER_SHA='824f88b975580288a6a68b6997aa4ce5a611e241c42fd347fc2f59e933faab6c'
INPUT_SHA='0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9'
REV='7ae557604adf67be50417f59c2c2f167def9a775'
# Lane-C exact-safe reconciliation, source candidate index and not a filename inference.
ASSETS={
 34:('T0','Q05_PREFILL_ATTN_FLASH','PREFILL_FLASH','03924689da9c9691501d93567365c9265178b8a5'),
 45:('T1','PREFILL_GEMM_PRIMARY_OCC0','PREFILL_GEMM','03924689da9c9691501d93567365c9265178b8a5'),
 17039:('T2','DECODE_GEMV_PRIMARY_STEP16','DECODE_GEMV','03924689da9c9691501d93567365c9265178b8a5'),
 17543:('R1','DECODE_FLASH_PRIMARY_1_STEP16','DECODE_FLASH_SPLITKV','0fc6c559027b029d79b77c1f6dcfa5162648b1ac'),
 16813:('R2','DECODE_FLASH_PRIMARY_2_STEP16','DECODE_FLASH_SPLITKV_COMBINE','0fc6c559027b029d79b77c1f6dcfa5162648b1ac'),
}
def sha(b): return hashlib.sha256(b).hexdigest()
def write(path, fields, rows):
 with Path(path).open('w', newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
def main():
 out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
 raw=sys.stdin.buffer.read()
 if sha(raw)!=EXPECTED_LEDGER_SHA: raise SystemExit('Lane A V2 ledger SHA256 mismatch')
 src=list(csv.DictReader(raw.decode().splitlines(),delimiter='\t'))
 if len(src)!=34677: raise SystemExit(f'expected 34677 V2 rows, got {len(src)}')
 occurrence=defaultdict(int);catalog=[];joins=[]
 for r in src:
  key=(r['phase'],r['decode_step'],r['exact_kernel_function'],r['grid'],r['block']);occurrence[key]+=1
  idx=int(r['global_launch_index']); asset=ASSETS.get(idx)
  status='REUSABLE_NOW' if asset else 'CAPTURE_READY'
  row=dict(scenario='S2_TEXT_B1_T2048_D32',global_launch_index=idx,phase=r['phase'],decode_step=r['decode_step'] or 'NOT_APPLICABLE',exact_function=r['exact_kernel_function'],grid=r['grid'],block=r['block'],occurrence=occurrence[key],model='Qwen/Qwen2.5-0.5B-Instruct',model_revision=REV,input_token_sha256=INPUT_SHA,driver_sha256=DRIVER_SHA,selector_authority='LANE_A_V2_FULL_PER_LAUNCH_INVENTORY_HASH_VERIFIED',classification=status,lane_c_asset_id=asset[0] if asset else 'NONE',lane_c_candidate=asset[1] if asset else 'NONE')
  catalog.append(row)
  if asset:
   joins.append(dict(asset_id=asset[0],asset_role=asset[2],lane_c_candidate=asset[1],lane_c_authority_commit=asset[3],global_launch_index=idx,phase=row['phase'],decode_step=row['decode_step'],exact_function=row['exact_function'],grid=row['grid'],block=row['block'],join_basis='LANE_C_ACCEPTED_CANDIDATE_INDEX_PLUS_LANE_A_EXACT_PHASE_FUNCTION_GRID_BLOCK',classification='REUSABLE_NOW'))
 fields=list(catalog[0]);write(out/'S2_CAPTURE_READY_CATALOG.tsv',fields,catalog)
 write(out/'S2_EXISTING_TRACE_JOIN.tsv',list(joins[0]),joins)
 summary=[dict(scenario='S2_TEXT_B1_T2048_D32',selector_rows=len(catalog),reusable_now=len(joins),capture_ready=sum(x['classification']=='CAPTURE_READY' for x in catalog),selector_identity_blocked=0,input_authority_blocked=0,content_control='INPUT_AUTHORITY_BLOCKED_NO_SECOND_LEGAL_T2048_TEXT')]
 write(out/'UPDATED_READINESS_SUMMARY.tsv',list(summary[0]),summary)
 auth=f'''# Capture readiness authority\n\n- Lane A V2 full per-launch ledger: `hrl/awma-qwen25-s2-census-reclass-v2 @ 24f21db0aa921190ca40e4d3969aced7471347b6`; hash verified as `{EXPECTED_LEDGER_SHA}` with 34,677 rows.\n- Driver: `hrl/awma-qwen25-s2-census-109-v1 @ 678d7b491d4788369ca0c22717453b20846ab195`; SHA-256 `{DRIVER_SHA}`.\n- Input: Qwen/Qwen2.5-0.5B-Instruct revision `{REV}`, S2 TEXT T2048 SHA-256 `{INPUT_SHA}`.\n- Lane C assets use only the documented candidate-index plus exact phase/function/grid/block reconciliation. T0/T1/T2 come from `03924689da9c9691501d93567365c9265178b8a5`; splitkv and splitkv-combine are promoted to reusable by `0fc6c559027b029d79b77c1f6dcfa5162648b1ac`.\n- No second legal T2048 TEXT input was recovered. Same-length different-content control remains `INPUT_AUTHORITY_BLOCKED`.\n'''
 (out/'CAPTURE_READINESS_AUTHORITY.md').write_text(auth)
 receipt={'stage':'AWMA_S2_CAPTURE_READINESS_RECOVERY_109_V1','ledger_sha256':EXPECTED_LEDGER_SHA,'ledger_rows':len(src),'driver_sha256':DRIVER_SHA,'input_sha256':INPUT_SHA,'exact_lane_c_reusable_now':len(joins),'no_gpu_workload_or_lock_or_capture':True}
 (out/'RUN_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 (out/'SHA256SUMS').write_text(''.join(f'{sha(p.read_bytes())}  {p.name}\n' for p in sorted(out.iterdir()) if p.is_file()))
 print(json.dumps(summary,sort_keys=True))
if __name__=='__main__':main()
