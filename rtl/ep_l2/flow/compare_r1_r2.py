#!/usr/bin/env python3
"""Compare actual same-library/constraints/effect mappings; never estimate SRAM.
Use summarize.py on completed runs before invoking this report generator.
"""
import argparse,json,csv,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--r2-summary',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();repo=Path(__file__).resolve().parents[3]
r1path=repo/'docs/ep_l2/review_packs/RTL_COST_OPEN_FLOW_V1_r1/COST_SUMMARY.json';old={x['mode']:x for x in json.loads(r1path.read_text())};new=json.loads(a.r2_summary.read_text());a.out.mkdir(parents=True,exist_ok=False)
def buckets(row):
 result={}
 def walk(name,count):
  d=row['per_module'][name];kind=next((k for k in ('ep_l2_tag_map_word','ep_l2_metadata_word','ep_l2_bank_arbiter','ep_l2_first_one','ep_l2_index_mux') if k in name),'ep_l2_slice_ctrl_other')
  b=result.setdefault(kind,{'instances':0,'area':0.,'sequential_area':0.,'cells':0,'sequential_cells':0});b['instances']+=count
  for target,source in [('area','own_area'),('sequential_area','own_sequential_area'),('cells','own_standard_cells'),('sequential_cells','own_sequential_cells')]:b[target]+=count*d[source]
  for child,n in d['children'].items():walk(child,count*n)
 top=next(k for k in row['per_module'] if k.endswith('\\ep_l2_slice_ctrl') or k=='ep_l2_slice_ctrl');walk(top,1);assert abs(sum(x['area'] for x in result.values())-row['standard_cell_totals']['area'])<.001;return result
rows=[]
for n in new:
 o=old[n['mode']]
 for identity in ('library_sha256','SDC_sha256','mapping_effort','full_parameters'):assert n[identity]==o[identity],identity
 b=n['standard_cell_totals'];before=o['standard_cell_totals'];mode=n['mode'];ff_saved=before['sequential_cells']-b['sequential_cells'];expected=23553 if mode!='UNIFIED' else 0
 # Static invariants remove exactly1024*(11 map +10 owner) FF; other state stays.
 ff_audit={'actual_removed_FF':ff_saved,'static_map_owner_role_and_captured_handle_upper_bound_removed_FF':expected,'matches_static_bound':ff_saved==expected,'scope':'Static role pruning may remove only1 or2 role bits per resident after mapping; actual charged FF and residual role implementation must be explained. All used generation/pins/ready/pending/dirty/WAD/data holding state remains charged.'}
 rows.append({'mode':mode,'R1_area':before['area'],'R2_area':b['area'],'area_change_percent':100*(b['area']/before['area']-1),'R1_target_WNS_ns':o['timing']['target_1132MHz']['wns_ns'],'R2_target_WNS_ns':n['timing']['target_1132MHz']['wns_ns'],'R1_2ns_WNS_ns':o['timing']['exploration_2ns']['wns_ns'],'R2_2ns_WNS_ns':n['timing']['exploration_2ns']['wns_ns'],'R1_target_TNS_ns':o['timing']['target_1132MHz']['tns_ns'],'R2_target_TNS_ns':n['timing']['target_1132MHz']['tns_ns'],'R1_buckets':buckets(o),'R2_buckets':buckets(n),'metadata_FF_audit':ff_audit,'same_library_SDC_parameters_effort':True,'SRAM_macro_area':None,'SRAM_macro_delay':None,'whole_slice_PPA':False,'paper_performance_pairing_eligible':False})
receipts=[json.loads((Path(n['flow_directory'])/'FLOW_RECEIPT.json').read_text()) for n in new]
assert all(r['RTL_files']==receipts[0]['RTL_files'] for r in receipts)
result={'schema':'EPL2_RTL_COST_R2_ACTUAL_BEFORE_AFTER_V1','R1_publication':'09de19579c0708f6542dfd65e1f3aae8a9a8b841','R1_summary_sha256':hashlib.sha256(r1path.read_bytes()).hexdigest(),'R2_summary_sha256':hashlib.sha256(a.r2_summary.read_bytes()).hexdigest(),'modes':rows,'same_R2_RTL_all_modes':True,'scope':'controller/access changed path only, unknown SRAM/nativeTag/MSHR; no target-GPU area/Fmax or app net-benefit claim'}
(a.out/'R1_R2_COMPARISON.json').write_text(json.dumps(result,indent=2)+'\n')
with (a.out/'R1_R2_COMPARISON.csv').open('w') as f:
 keys=[k for k,v in rows[0].items() if not isinstance(v,dict)];w=csv.DictWriter(f,keys,extrasaction='ignore');w.writeheader();w.writerows(rows)
print(json.dumps([{k:v for k,v in r.items() if not isinstance(v,dict)} for r in rows],indent=2))
