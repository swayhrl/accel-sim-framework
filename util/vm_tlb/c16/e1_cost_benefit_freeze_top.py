#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path('/data/c16/e1_residency_cost_benefit_closure_v1')
def childid(r):return [(x['layer'],x['role'],x['decode_index'],x['input_sha256'],x['output_sha256']) for x in r['child_occurrences']]
def topid(r):return [(x['layer'],x['category'],x['decode_index'],x['input_sha256'],x['output_sha256']) for x in r['top_occurrences']]
def main():
 ps=sorted((ROOT/'authority/native').glob('run[0-6].json'));runs=[json.loads(p.read_text()) for p in ps]
 if len(runs)!=7:raise RuntimeError('seven authority runs required')
 b=runs[0]
 for r in runs:
  if r['generated_token_ids_D0_D3']!=[23578,11,323,3950] or r['child_call_order']!=b['child_call_order'] or r['top_call_order']!=b['top_call_order'] or childid(r)!=childid(b) or topid(r)!=topid(b):raise RuntimeError('authority drift')
 if len(b['child_call_order'])!=420 or len(b['top_call_order'])!=570 or len(b['child_occurrences'])!=336 or len(b['top_occurrences'])!=456:raise RuntimeError('authority counts')
 phases=('PREFILL','D0','D1','D2','D3')
 for ph in phases:
  tc=[x for x in b['top_call_order'] if x['phase']==ph]
  if len(tc)!=114 or [x['ordinal'] for x in tc]!=list(range(114)):raise RuntimeError(f'top order {ph}')
 result={'status':'PASS','fresh_process_runs':7,'generated_token_ids_D0_D3':[23578,11,323,3950],'child_call_order':b['child_call_order'],'top_call_order':b['top_call_order'],'child_bindings':b['child_occurrences'],'top_bindings':b['top_occurrences'],'child_module_census':b['child_module_census'],'top_module_census':b['top_module_census'],'top_level_nonoverlap_asserted_all_runs':True}
 (ROOT/'contracts/TOPLEVEL_AUTHORITY.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','child_calls':420,'top_calls':570,'child_occurrences':336,'top_occurrences':456}))
if __name__=='__main__':main()
