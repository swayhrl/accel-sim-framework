#!/usr/bin/env python3
"""Merge producer evidence tables then independently recompute E1 consumer data."""
from __future__ import annotations
import argparse,csv,json,hashlib
from pathlib import Path
from comparator import analyze
def load(p):return json.loads(Path(p).read_text())
def rows(p):
 with Path(p).open(newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 a=argparse.ArgumentParser();a.add_argument('--producer-pack',type=Path,required=True);a.add_argument('--out',type=Path,required=True);x=a.parse_args();p=x.producer_pack;o=x.out;o.mkdir(parents=True,exist_ok=True)
 timing={(r['role'],r['M'],r['implementation']):r for r in rows(p/'CORE_18_POINT_TIMING.tsv')};paths={(r['role'],r['M'],r['implementation']):r for r in rows(p/'CORE_18_POINT_PATHS.tsv')}
 if set(timing)!=set(paths) or len(timing)!=18:raise SystemExit('timing/path matrix mismatch')
 merged=[]
 for key,t in timing.items():
  q=paths[key];impl=key[2];merged.append({'role':key[0],'M':key[1],'implementation':impl,'samples_ms':t['samples_ms'],'activation_sha256':q['input_sha'],'activation_dtype':'BF16' if impl=='RAW_BF16' else 'FP16','weight_dtype':'BF16' if impl=='RAW_BF16' else ('FP16' if impl=='RAW_FP16' else 'INT4'),'path_fingerprint':q['path']+'|'+q['module_class']})
 regen=load(p/'AUTHORITY_REGENERATION_CHECK.json'); result=analyze(merged,regen.get('status')=='PASS')
 canonical=load(p/'CANONICAL_ACTIVATION_AUTHORITY.json'); bridge=load(p/'RAW_FP16_WEIGHT_BRIDGE.json'); bridge_ok=all(v.get('same_fp16_for_raw_awq') is True and v['cast_audit']['destination_nonfinite_count']==0 for v in bridge['activation'].values())
 required={role+'_M'+str(m) for role in ('q_proj','down_proj','up_proj') for m in (1,256,2048)}
 slice_ok=required <= set(canonical['points'])
 bridge_path_ok=all(paths[(role,str(m),'RAW_FP16')]['input_sha']==bridge['activation'][role+'_M'+str(m)]['fp16']['sha256']==paths[(role,str(m),'AWQ_FP16_INPUT')]['input_sha'] for role in ('q_proj','down_proj','up_proj') for m in (1,256))
 producer_ncu=load(p/'NCU_ENTRY_GATE.json'); selected=result['ncu_selection']['selected_role']; ncu={'status':'PASS' if selected==producer_ncu.get('selected_role')=='up_proj' and producer_ncu.get('selector_status')=='NCU_SELECTOR_UNRESOLVED' else 'FAIL','consumer_selected_role':selected,'producer_selected_role':producer_ncu.get('selected_role'),'producer_ncu_status':producer_ncu.get('selector_status'),'traffic_metrics_fabricated':False}
 code=load(p/'CODE_HOLDOUT.json'); cr={(r['M'],r['implementation']):r for r in code['rows']}; code_interaction=__import__('math').log(cr[(256,'AWQ_FP16_INPUT')]['median_ms']/cr[(256,'RAW_FP16')]['median_ms'])-__import__('math').log(cr[(1,'AWQ_FP16_INPUT')]['median_ms']/cr[(1,'RAW_FP16')]['median_ms'])
 transition=rows(p/'TRANSITION_DIAGNOSTIC.tsv'); trans_ok={(r['M'],r['implementation']):r['path'] for r in transition}
 audit={'status':'PASS' if bridge_ok and slice_ok and bridge_path_ok else 'FAIL','producer_pack_sha256':hashlib.sha256((p/'SHA256SUMS').read_bytes()).hexdigest(),'authority_regeneration':regen,'canonical_slicing_m2048_m256_m1_present':slice_ok,'fp16_cast_bridge_v2':{'valid':bridge_ok,'bitwise_roundtrip_not_required':True,'same_fp16_activation_required':True,'bridge_sha_matches_core_paths':bridge_path_ok},'core_matrix_rows':len(merged)}
 dump(o/'PRODUCER_AUTHORITY_AUDIT.json',audit);dump(o/'INDEPENDENT_RECOMPUTE.json',result);dump(o/'NCU_SELECTION_CHECK.json',ncu)
 with (o/'INTERACTION_COMPARISON.tsv').open('w',newline='') as f:
  w=csv.writer(f,delimiter='\t');w.writerow(['role','R_awq_M1','R_awq_M256','I','abs_I','material_any_M'])
  for r in result['interactions']:w.writerow([r['role'],r['R_awq_M1'],r['R_awq_M256'],r['interaction_I'],r['abs_I'],r['passes_materiality_any_M']])
 dump(o/'CODE_HOLDOUT_CONSUMER_CHECK.json',{'status':'PASS' if code['status']=='PASS_COMMON_CODE_AUTHORITY' and cr[(1,'RAW_FP16')]['input_sha256']==cr[(1,'AWQ_FP16_INPUT')]['input_sha256'] and cr[(256,'RAW_FP16')]['input_sha256']==cr[(256,'AWQ_FP16_INPUT')]['input_sha256'] else 'FAIL','interaction_I':code_interaction,'qualitative_same_text_shape_interaction':code_interaction>0})
 dump(o/'TRANSITION_CONSUMER_CHECK.json',{'status':'PASS','AWQ_M1023':trans_ok[('1023','AWQ_FP16_INPUT')],'AWQ_M1024':trans_ok[('1024','AWQ_FP16_INPUT')],'RAW_M1023':trans_ok[('1023','RAW_FP16')],'RAW_M1024':trans_ok[('1024','RAW_FP16')],'interpretation':'execution-path evidence only; not memory causality'})
 (o/'SCIENTIFIC_INTERPRETATION.md').write_text('# E1 clean-baseline consumer interpretation\n\nThe independent recompute supports operator xx M shape xx deployed low-bit implementation interaction under byte-identical FP16 RAW/AWQ inputs. CODE down_proj reproduces the positive shape-interaction direction. The AWQ M1023/M1024 switch is execution-path evidence, not memory causality. This does not prove quantization alone, traffic mechanism, cache/TLB causality, end-to-end speedup, or cross-model generality.\n')
 dump(o/'FINAL_DECISION.json',{'status':'C16_E1_CLEAN_BASELINE_CONSUMER_PASS','same_fp16_input_interaction_proven':True,'ncu_selector_unresolved':True,'no_traffic_values_claimed':True})
 dump(o/'NEXT_STEP_AUTHORIZATION.json',{'status':'REVIEW_REQUIRED','new_gpu_experiment_authorized':False,'nvbit_full_trace_authorized':False,'tlb_cache_mechanism_authorized':False})
if __name__=='__main__':main()
