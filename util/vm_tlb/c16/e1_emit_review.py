#!/usr/bin/env python3
import csv,hashlib,json,shutil
from pathlib import Path
REPO=Path('/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-clean-baseline-109-v1');OUT=REPO/'docs/vm_tlb/review_packs/C16_E1_CLEAN_BASELINE_109_V1';ROOT=Path('/data/c16/e1_clean_baseline_v1')
def load(p):return json.loads(Path(p).read_text())
def write(n,x):(OUT/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if OUT.exists():raise SystemExit('pack exists')
 a=load(ROOT/'capture_a/CANONICAL_RAW_CAPTURE_RECEIPT.json');regen=load(ROOT/'AUTHORITY_REGENERATION_CHECK.json');m=load(ROOT/'matrix/CORE_18_POINT_RESULT.json');analysis=load(ROOT/'CORE_ANALYSIS.json');transition=load(ROOT/'transition/TRANSITION_RESULT.json');code=load(ROOT/'code_holdout/CODE_HOLDOUT.json');OUT.mkdir(parents=True)
 write('UPSTREAM_IDENTITY.json',{'raw_model_revision':a['model_revision'],'token_sha256':a['token_sha256'],'historical_eight_point_status':'HISTORICAL_DEPLOYMENT_MEASUREMENT_PROVENANCE_LIMITED'})
 write('CANONICAL_ACTIVATION_AUTHORITY.json',a);write('AUTHORITY_REGENERATION_CHECK.json',regen);write('RAW_FP16_WEIGHT_BRIDGE.json',{'activation':m['fp16_activation_bridge'],'weights_bias':m['fp16_weight_bias_cast_audit']});write('CORE_ANALYSIS.json',analysis);write('CODE_HOLDOUT.json',code)
 with (OUT/'CANONICAL_ACTIVATION_INDEX.tsv').open('w',newline='') as f:
  w=csv.writer(f,delimiter='\t');w.writerow(['point','shape','stride','dtype','sha256']);
  for k,v in a['points'].items():w.writerow([k,v['input']['shape'],v['input']['stride'],v['input']['dtype'],v['input']['byte_sha256']])
 with (OUT/'CORE_18_POINT_TIMING.tsv').open('w',newline='') as f:
  w=csv.writer(f,delimiter='\t');w.writerow(['role','M','implementation','median_ms','min_ms','max_ms','cv','samples_ms']);
  for r in m['rows']:w.writerow([r['role'],r['M'],r['implementation'],r['median_ms'],r['min_ms'],r['max_ms'],r['cv'],json.dumps(r['samples_ms'])])
 with (OUT/'CORE_18_POINT_PATHS.tsv').open('w',newline='') as f:
  w=csv.writer(f,delimiter='\t');w.writerow(['role','M','implementation','module_class','path','input_sha','output_sha']);
  for r in m['rows']:w.writerow([r['role'],r['M'],r['implementation'],r['module_class'],r['path_fingerprint'],r['input']['sha256'],r['output_sha256']])
 with (OUT/'TRANSITION_DIAGNOSTIC.tsv').open('w',newline='') as f:
  w=csv.writer(f,delimiter='\t');w.writerow(['M','implementation','path','median_ms','cv','kernel_names']);
  for r in transition['rows']:w.writerow([r['M'],r['implementation'],r['path'],r['median_ms'],r['cv'],json.dumps(r['kernel_names'])])
 write('NCU_ENTRY_GATE.json',{'status':'PASS','selected_role':analysis['selected_role'],'roles':analysis['roles'],'selector_status':'NCU_SELECTOR_UNRESOLVED'})
 (OUT/'NCU_SELECTED_POINTS.tsv').write_text('role\tM\timplementation\tstatus\n'+''.join(f"{analysis['selected_role']}\t{M}\t{impl}\tNCU_SELECTOR_UNRESOLVED\n" for M in (1,256) for impl in ('RAW_FP16','AWQ_FP16_INPUT')))
 (OUT/'NCU_METRICS.tsv').write_text('status\tmetric\tunit\tvalue\nNCU_SELECTOR_UNRESOLVED\tNA\tNA\tNA\n')
 (OUT/'SCIENTIFIC_INTERPRETATION.md').write_text('# E1 clean-baseline interpretation\n\nThe clean same-FP16-input matrix shows strong operator-by-shape interaction in the deployed AWQ effect. The largest registered interaction is up_proj. Finite BF16-to-FP16 rounding is reported as part of the dtype effect. Historical eight-point values remain provenance-limited and are not mixed into clean ratios. CODE holdout and the bounded M1023/M1024 transition closed. Conditional NCU was entered but no unique semantic-kernel selector could be proven, so traffic metrics are not fabricated.\n')
 write('NEXT_STEP_DECISION.json',{'decision':'STOP_AFTER_CLEAN_E1_REVIEW','deep_trace_authorized':False,'reason':'Clean interaction is material, but bounded NCU selector is unresolved; define a reviewed semantic selector before any deeper memory study.','forbidden':['NVBit','full address trace','TLB/cache mechanism']})
 files=[p for p in OUT.iterdir() if p.is_file()];(OUT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in sorted(files)))
if __name__=='__main__':main()
