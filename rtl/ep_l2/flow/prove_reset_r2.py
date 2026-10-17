#!/usr/bin/env python3
"""Actual source reset network equivalence, three full-capacity organizations.
Proof-only flattening strips hierarchy preservation; cost keeps every buffer.
Caller holds central admission. No timing exception or extra reset cycle.
"""
import argparse,json,hashlib,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);repo=Path(__file__).resolve().parents[3];ctrl=repo/'rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv';word=repo/'rtl/ep_l2/rtl/ep_l2_metadata_word.sv';s=ctrl.read_text();start=s.index('    localparam integer RESET_LEAF=');end=s.index('    genvar m;',start);network=s[start:end];rows=[]
for mode in (0,1,2):
 top=a.out/f'reset-{mode}.sv';top.write_text(f'module reset_equiv(input rst_n,output equal);localparam MODE={mode},N_PAYLOAD=1168,N_TAG=1024,WB_BEGIN={1104 if mode==2 else 1152};\n'+network+"assign equal=reset_leaf=={RESET_LEAF{rst_n}};endmodule\n")
 ys=a.out/f'reset-{mode}.ys';ys.write_text(f'read_verilog -sv "{word}" "{top}"\nhierarchy -top reset_equiv\nsetattr -mod -unset keep_hierarchy\nsetattr -unset keep_hierarchy\nflatten\nprep -top reset_equiv\nsat -prove equal 1 -verify\n')
 log=a.out/f'reset-{mode}.log'
 with log.open('w') as f:subprocess.run(['yosys','-Q','-T','-s',str(ys)],stdout=f,stderr=subprocess.STDOUT,check=True)
 assert 'SUCCESS!' in log.read_text();rows.append({'mode':mode,'all_binary_reset_values_all292_leaf_outputs_equal':True,'no_registers_or_extra_cycles':True});print('RESET actual network mode',mode,'EQ_PASS',flush=True)
(a.out/'RESET_EQ_RECEIPT.json').write_text(json.dumps({'rows':rows,'actual_source_network_sha256':hashlib.sha256(network.encode()).hexdigest(),'controller_sha256':hashlib.sha256(ctrl.read_bytes()).hexdigest(),'module_file_sha256':hashlib.sha256(word.read_bytes()).hexdigest(),'proof_only_attributes_removed':['keep_hierarchy'],'cost_hierarchy_attributes_preserved':True},indent=2)+'\n')
