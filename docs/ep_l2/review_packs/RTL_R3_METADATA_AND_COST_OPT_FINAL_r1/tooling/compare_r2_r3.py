#!/usr/bin/env python3
from pathlib import Path
import argparse,json,csv,hashlib,collections
p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',nargs=2,action='append',required=True,metavar=('LABEL','SUMMARY_JSON'));p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);base={x['mode']:x for x in json.loads(a.baseline.read_text())};rows=[];modules=[];cross=[];sourceids={}
def buckets(x):
 mods=x['per_module'];counts=collections.Counter()
 def walk(n,k):
  counts[n]+=k
  for child,v in mods[n]['children'].items():walk(child,k*v)
 walk(next(k for k in mods if k.endswith('\\ep_l2_slice_ctrl')),1);out={}
 kinds=('ep_l2_metadata_word','ep_l2_tag_map_word','ep_l2_generation_step','ep_l2_index_mux','ep_l2_first_one','ep_l2_bank_arbiter','ep_l2_control_inverter','ep_l2_control_buffer')
 for n,v in mods.items():
  k=counts[n]
  if not k:continue
  kind=next((s for s in kinds if (n.endswith('\\'+s) or ('\\'+s+'\\') in n)),'top_or_other');d=out.setdefault(kind,{'instances':0,'area':0.,'seq_area':0.,'comb_area':0.,'FF':0,'cells':0});d['instances']+=k
  for dest,src in [('area','own_area'),('seq_area','own_sequential_area'),('comb_area','own_combinational_area'),('FF','own_sequential_cells'),('cells','own_standard_cells')]:d[dest]+=k*v[src]
 assert abs(sum(v['area'] for v in out.values())-x['standard_cell_totals']['area'])<.01
 return out
allsets=[('R2',base)]+[(name,{x['mode']:x for x in json.loads(Path(path).read_text())}) for name,path in a.candidate]
for label,data in allsets:
 assert set(data)=={'B16','S64','UNIFIED'}
 for mode,x in data.items():
  old=base[mode]
  for key in ('library_sha256','SDC_sha256','mapping_effort','full_parameters'):assert x[key]==old[key],(label,mode,key)
  t=x['standard_cell_totals'];param=x['full_parameters'];assert param['N_TAG']==1024 and param['N_PAYLOAD']==1168 and param['N_WAD']==128 and param['GEN_W']==32 and param['P']==1
  row={'candidate':label,'mode':mode,'area':t['area'],'area_change_vs_R2_percent':100*(t['area']/old['standard_cell_totals']['area']-1),'combinational_area':t['combinational_area'],'sequential_area':t['sequential_area'],'cells':t['cells'],'FF':t['sequential_cells'],'FF_delta_vs_R2':t['sequential_cells']-old['standard_cell_totals']['sequential_cells'],'latches':t['latch_cells'],'WNS0_883392226_ns':x['timing']['target_1132MHz']['wns_ns'],'TNS0_883392226_ns':x['timing']['target_1132MHz']['tns_ns'],'WNS2_ns':x['timing']['exploration_2ns']['wns_ns'],'TNS2_ns':x['timing']['exploration_2ns']['tns_ns'],'SRAM_area':'UNKNOWN','SRAM_delay':'UNKNOWN','scope':'partial mapped standard-cell controller/access cut; no whole-L2/app pairing'};rows.append(row)
  for kind,v in buckets(x).items():modules.append({'candidate':label,'mode':mode,'module_group':kind,**v,'comb_cells':v['cells']-v['FF']})
 if label!='R2':
  recs=[json.loads((Path(x['flow_directory'])/'FLOW_RECEIPT.json').read_text()) for x in data.values()];assert all(r['RTL_files']==recs[0]['RTL_files'] for r in recs);sourceids[label]=recs[0]['RTL_files']
 areas={mode:x['standard_cell_totals']['area'] for mode,x in data.items()};cross.append({'candidate':label,'U_minus_B16_area':areas['UNIFIED']-areas['B16'],'U_div_B16':areas['UNIFIED']/areas['B16'],'U_div_S64':areas['UNIFIED']/areas['S64'],'scope':'same partial standard-cell cut, unknown macros/native costs'})
for name,data in [('PARETO_COMPARISON',rows),('MODULE_ATTRIBUTION',modules),('DYNAMIC_PREMIUM',cross)]:
 (a.out/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
 with (a.out/(name+'.csv')).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]),lineterminator='\n');w.writeheader();w.writerows(data)
(a.out/'COMPARISON_RECEIPT.json').write_text(json.dumps({'baseline_sha256':hashlib.sha256(a.baseline.read_bytes()).hexdigest(),'candidates':sourceids,'same_library_SDC_effort_full_parameters':True,'source_or_cycle_modification_by_comparison':False,'metadata_GEN_bits_remain32':True,'all_no_false_multicycle_reset_exception':True,'unknown_SRAM_native_cost':True,'numeric_or_timing_closure_not_inferred':True},indent=2)+'\n');print(json.dumps(rows,indent=2))
