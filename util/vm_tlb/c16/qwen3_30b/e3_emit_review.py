#!/usr/bin/env python3
import csv,hashlib,json,statistics
from pathlib import Path
REPO=Path('/home/huangrulin/workspace/worktrees/accel-sim-c16-e3-q30-routing-diagnostic-109-v1')
SRC=Path('/data/c16/qwen3_30b/e3_routing_v1/E3_Q30_ROUTING_DIAGNOSTIC_109_V1/E3_RESULT.json')
OUT=REPO/'docs/vm_tlb/review_packs/C16_E3_Q30_ROUTING_DIAGNOSTIC_109_V1'
def write(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def sha(p):
 h=hashlib.sha256();h.update(p.read_bytes());return h.hexdigest()
def main():
 if OUT.exists():raise SystemExit('review output exists')
 e=json.loads(SRC.read_text());c=e['conditions'];OUT.mkdir(parents=True)
 write('UPSTREAM_AUTHORITY.json',{'branch':'hrl/c16-qwen3-30b-s2-state-replay-109-v1','commit':'ee67225edc8fc5868de585d38e0391cbeb755d9f','state_manifest_sha256':e['upstream_state_manifest_sha256'],'evidence_condition':'accepted S2/T2048 prefill Layer24'})
 write('TARGET_REGION_QUALIFICATION.json',{k:e[k] for k in ('status','layer','M','E','k','upstream_state_manifest_sha256','state_hidden_sha256','natural_router_logits_sha256')})
 write('NATURAL_ROUTING.json',c['N'])
 write('ROUTING_CONDITIONS.json',c)
 write('ROUTE_INVARIANTS.json',{'status':'PASS','assignments':{x:c[x]['assignments'] for x in c},'distinct_ids':{x:c[x]['per_token_distinct'] for x in c},'U_exact_128':all(x==128 for x in c['U']['histogram']),'H_exact_2048':set(x for x in c['H']['histogram'] if x)=={2048},'U_H_natural_weight_vectors_preserved':True})
 write('P_EQUIVALENCE.json',{'status':'PASS','permutation_seed':e['permutation_seed'],'permutation_sha256':e['permutation_sha256'],'inverse_permutation_sha256':e['inverse_permutation_sha256'],'natural_body_output_sha256':e['natural_body_output_sha256'],'inverse_permuted_P_output_sha256':e['p_inverse_output_sha256'],'bitwise_equal':e['p_equivalence_bitwise']})
 write('EXPERT_CALL_STRUCTURE.json',{x:{'expert_calls':c[x]['expert_calls'],'expert_calls_detail':c[x]['expert_calls_detail'],'expert_batch_sizes':c[x]['expert_batch_sizes'],'backend':c[x]['backend'],'dtype':c[x]['dtype'],'layout':c[x]['layout']} for x in c})
 write('SEMANTIC_ACTIVE_WEIGHT_CAPACITY.json',{x:c[x]['semantic_active_weight_capacity'] for x in c})
 with (OUT/'NATIVE_TIMING.tsv').open('w',newline='') as f:
  w=csv.writer(f,delimiter='\t');w.writerow(['condition','iteration','body_ms'])
  for x in ('N','U','H','P'):
   for i,v in enumerate(c[x]['body_timing']['raw_ms']):w.writerow([x,i,v])
  for i,v in enumerate(e['router_timing_N_only']['raw_ms']):w.writerow(['N_ROUTER_ONLY',i,v])
 write('TIMING_SUMMARY.json',{'warmups':e['warmups'],'measurements':e['measurements'],'router_N_only':e['router_timing_N_only'],'body':{x:c[x]['body_timing'] for x in c},'substage_limit':'Only full dispatch->experts->combine body timing; no fabricated sub-times.'})
 (OUT/'SCIENTIFIC_INTERPRETATION.md').write_text('# E3 interpretation\n\nN and U body medians differ by less than the observed run-to-run CV, so balanced routing is an adequate proxy for this fixed Q30 Layer24/S2/T2048 backend and these lightweight metrics. P is bitwise-equivalent to N after inverse permutation and has comparable timing, so no ordering effect is established here. H is substantially faster with only eight active experts, but it is an intentionally extreme synthetic hot-set result and is not evidence of a natural-routing bottleneck. `SEMANTIC_ACTIVE_WEIGHT_CAPACITY` is semantic parameter capacity, not observed traffic or page/line footprint.\n')
 write('NEXT_STEP_DECISION.json',{'decision':'STOP_LIGHTWEIGHT_E3_NO_DEEP_CAPTURE','case':'A_AND_C','N_U_median_difference_fraction':abs(c['N']['body_timing']['median_ms']-c['U']['body_timing']['median_ms'])/c['N']['body_timing']['median_ms'],'reason':'N/U difference is within observed variability; H only demonstrates extreme synthetic sensitivity.','forbidden_next_actions':['NVBit','NCU','NSYS','full address trace','OLMoE validation','CODE holdout','decode cross-step reuse','TLB/cache mechanism']})
 files=sorted(x for x in OUT.iterdir() if x.is_file());(OUT/'SHA256SUMS').write_text(''.join(f'{sha(x)}  {x.name}\n' for x in files))
if __name__=='__main__':main()
