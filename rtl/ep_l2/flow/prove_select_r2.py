#!/usr/bin/env python3
"""Actual final RTL selector vs ascending R1 scan and full variable read.
All binary masks/word values and index codes; no capacity reduction for cost.
Caller holds central resource admission. No full-controller formal claim.
"""
import argparse,subprocess,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--mux-only',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);repo=Path(__file__).resolve().parents[3];rtl=repo/'rtl/ep_l2/rtl/ep_l2_metadata_word.sv';rows=[]
for n in (() if a.mux_only else (292,128,16,64)):
 w=(n-1).bit_length();name=f'first-{n}';s=f'''module equiv(input [{n-1}:0] eligible,output equal);
 wire found;wire [{w-1}:0] index;reg expected_found;reg [{w-1}:0] expected_index;
 ep_l2_first_one #(.N({n}),.W({w})) dut(eligible,found,index);
 always @* begin expected_found=0;expected_index=0;
 for(integer j=0;j<{n};j=j+1)if(!expected_found&&eligible[j])begin expected_found=1;expected_index=j;end end
 assign equal=(found==expected_found)&&(index==expected_index);endmodule\n'''
 (a.out/(name+'.sv')).write_text(s);rows.append((name,s))
name='mux-1168x32';s='''module equiv(input [1168*32-1:0] words,input [10:0] index,output equal);
 wire [31:0] data;ep_l2_index_mux #(.N(1168),.W(32),.IW(11)) dut(words,index,data);
 wire [31:0] reference=index<1168 ? words[index*32 +:32] : 32'b0;
 assign equal=data==reference;endmodule\n''';(a.out/(name+'.sv')).write_text(s);rows.append((name,s))
for name,_ in rows:
 ys=a.out/(name+'.ys');ys.write_text(f'read_verilog -sv "{rtl}" "{a.out}/{name}.sv"\nprep -top equiv -flatten\nsat -prove equal 1 -verify\n')
 with (a.out/(name+'.log')).open('w') as f:subprocess.run(['yosys','-Q','-T','-s',str(ys)],stdout=f,stderr=subprocess.STDOUT,check=True)
 assert 'SUCCESS!' in (a.out/(name+'.log')).read_text();print(name,'ALL_BINARY_INPUTS_EQ_PASS',flush=True)
(a.out/'SELECT_EQ_RECEIPT.json').write_text(json.dumps({'status':'ACTUAL_FINAL_RTL_ALL_BINARY_INPUTS_COMBINATIONAL_EQ_PASS','proofs':[x[0] for x in rows],'RTL_file_sha256':hashlib.sha256(rtl.read_bytes()).hexdigest(),'scope':'helper algorithms only; no global protocol/reachability proof','GEN_W_in_cost':32,'cost_capacities':[1024,1168,128]},indent=2)+'\n')
