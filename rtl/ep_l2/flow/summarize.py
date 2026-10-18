#!/usr/bin/env python3
"""Summarize REAL Yosys cell counts/Liberty areas and actual OpenSTA reports.
Never insert an SRAM estimate or substitute a requested clock for timing.
"""
import argparse,json,re,csv,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--liberty',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('runs',nargs='+',type=Path);a=p.parse_args();lib=a.liberty.read_text();cells={}
for match in re.finditer(r'\bcell\s*\(\s*"?([\w]+)"?\s*\)\s*\{',lib):
 start=match.end();pos=start;depth=1
 while depth:
  if lib[pos]=='{':depth+=1
  if lib[pos]=='}':depth-=1
  pos+=1
 body=lib[start:pos];area=re.search(r'\barea\s*:\s*([\d.eE+-]+)\s*;',body)
 cells[match[1]]={'area':float(area[1]) if area else None,'sequential':bool(re.search(r'\b(ff|latch)\s*\(',body)),'latch':bool(re.search(r'\blatch\s*\(',body))}
def metric(pat,text):
 m=re.search(pat,text);return float(m[1]) if m else None
summaries=[]
for directory in a.runs:
 receipt=json.loads((directory/'FLOW_RECEIPT.json').read_text());stats=json.loads((directory/'stat.json').read_text());modules=stats['modules'];local={}
 for name,m in modules.items():
  types=m.get('num_cells_by_type',{});area=0;seqarea=0;seq=0;latches=0;std=0;children={};unknown={}
  for typ,n in types.items():
   if typ in cells:
    assert cells[typ]['area'] is not None,typ;value=n*cells[typ]['area'];area+=value;std+=n
    if cells[typ]['sequential']:seq+=n;seqarea+=value
    if cells[typ]['latch']:latches+=n
   elif typ in modules or '\\'+typ in modules:children[typ if typ in modules else '\\'+typ]=n
   else:unknown[typ]=n
  local[name]={'own_standard_cells':std,'own_area':area,'own_sequential_area':seqarea,'own_sequential_cells':seq,'latch_cells':latches,'own_combinational_area':area-seqarea,'children':children,'unmapped':unknown}
 def accumulate(name,factor=1,visited=None):
  row=local[name];total={'area':row['own_area']*factor,'sequential_area':row['own_sequential_area']*factor,'cells':row['own_standard_cells']*factor,'sequential_cells':row['own_sequential_cells']*factor,'latch_cells':row['latch_cells']*factor,'unmapped':{k:v*factor for k,v in row['unmapped'].items()}}
  for child,n in row['children'].items():
   r=accumulate(child,factor*n)
   for key in ['area','sequential_area','cells','sequential_cells','latch_cells']:total[key]+=r[key]
   for typ,n in r['unmapped'].items():total['unmapped'][typ]=total['unmapped'].get(typ,0)+n
  return total
 top='\\ep_l2_slice_ctrl' if '\\ep_l2_slice_ctrl' in modules else 'ep_l2_slice_ctrl';total=accumulate(top);total['combinational_area']=total['area']-total['sequential_area'];timing={}
 assert abs(total['area']-stats['design']['area'])<0.001,'independent Liberty sum differs from Yosys area'
 assert abs(total['sequential_area']-stats['design']['sequential_area'])<0.001
 assert total['cells']==stats['design']['num_cells'],'hierarchy cell count mismatch'
 for label in ['target_1132MHz','exploration_2ns']:
  d=Path(receipt.get('STA_root',str(directory)))/label;path=(d/'critical_paths.rpt').read_text();coverage=(d/'constraint_coverage.rpt').read_text()
  timing[label]={'wns_ns':metric(r'wns max\s+([-+\d.eE]+)',(d/'wns.rpt').read_text()),'tns_ns':metric(r'tns max\s+([-+\d.eE]+)',(d/'tns.rpt').read_text()),'worst_reported_data_arrival_ns_includes_IO_budget':metric(r'([-+\d.eE]+)\s+data arrival time',path),'reported_slack_ns':metric(r'([-+\d.eE]+)\s+slack\s+\(',path),'constraint_coverage_report':coverage,'scope':'controller/interface netlist only; external SRAM0.10ns budget is assumption, not macro delay; no SPEF','design_rules_report':str(d/'design_rules.rpt')}
  timing[label]['path_classes']={}
  for cls,file in [('hit_data_interface','hit_data_interface.rpt'),('allocation_request_interface','allocation_interface.rpt'),('WB_interface','wb_interface.rpt')]:
   content=(d/file).read_text();paths=[]
   for block in content.split('Startpoint: ')[1:]:
    begin=block.splitlines()[0];end=re.search(r'Endpoint: (.*)',block);paths.append({'startpoint':begin,'endpoint':end[1] if end else None,'data_arrival_ns_includes_IO_budget':metric(r'([-+\d.eE]+)\s+data arrival time',block),'slack_ns':metric(r'([-+\d.eE]+)\s+slack\s+\(',block)})
   timing[label]['path_classes'][cls]={'actual_paths':paths,'no_paths':not bool(paths),'raw_report':str(d/file)}
  assert timing[label]['wns_ns'] is not None and timing[label]['tns_ns'] is not None
 summary={'mode':receipt['mode'],'mapping_effort':receipt.get('mapping_effort','standard'),'mapped_area_qualification':'COMPLETE_WITHIN_CONTROLLER_CUT' if not total['unmapped'] else 'PARTIAL_UNMAPPED_CELLS_EXCLUDED_DO_NOT_CLAIM_TOTAL','netlist_sha256':receipt['netlist_sha256'],'SDC_sha256':receipt['sdc_sha256'],'flow_directory':str(directory),'area_units':'Liberty cell-area reference units; no target-chip mm2 claim','library_sha256':receipt['library_sha256'],'library_corner':'NangateOpenCellLibrary typical / nom_process1.0 /1.1V /25C','scope':receipt['scope'],'full_parameters':receipt['parameters'],'standard_cell_totals':total,'per_module':local,'timing':timing,'SRAM':{'instances':4,'rows_per_bank':292,'bits_per_row':1024,'physical_bits':1196032,'capacity_KiB':146,'ports':'1RW per bank,128 byte enables','macro_area':None,'macro_delay':None,'reason':'no matching macro binding/Liberty; functional wrapper is explicit blackbox for synthesis'},'excluded_traditional_logic_area':None,'dc_status':'UNRUN','post_layout':False,'power_status':'UNRUN','flow_complete':True,'design_status':'R3_STRUCTURALLY_OPTIMIZED_TIMING_UNCLOSED' if timing['target_1132MHz']['wns_ns']<0 else 'TARGET_WNS_NONNEGATIVE_REVIEW_DRC_AND_SCOPE','target_clock_met_within_STA_cut':timing['target_1132MHz']['wns_ns']>=0,'paper_performance_pairing_eligible':False,'pairing_blockers':['SIM/RTL frontend/copy/WB/arbitration/approval timing differs','SRAM macro timing/area and nativeTag/MSHR costs unknown','No DRC/post-layout closure; static hardwire proof is limited to resident mapping/owner']};summaries.append(summary)
a.out.mkdir(exist_ok=True,parents=True);(a.out/'COST_SUMMARY.json').write_text(json.dumps(summaries,indent=2)+'\n')
with (a.out/'COST_SUMMARY.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['mode','stdcell_area_library_units','combinational_area','sequential_area','stdcells','sequential_cells','latches','unmapped_types','WNS_target_ns','TNS_target_ns','WNS_2ns_ns','SRAM_area','SRAM_delay','scope'])
 for x in summaries:
  t=x['standard_cell_totals'];w.writerow([x['mode'],t['area'],t['combinational_area'],t['sequential_area'],t['cells'],t['sequential_cells'],t['latch_cells'],json.dumps(t['unmapped']),x['timing']['target_1132MHz']['wns_ns'],x['timing']['target_1132MHz']['tns_ns'],x['timing']['exploration_2ns']['wns_ns'],'UNKNOWN','UNKNOWN',x['scope']])
print(json.dumps([{'mode':x['mode'],**x['standard_cell_totals'],'target':x['timing']['target_1132MHz']['wns_ns']} for x in summaries],indent=2))
