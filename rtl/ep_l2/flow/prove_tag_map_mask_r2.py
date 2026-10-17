#!/usr/bin/env python3
"""Inductive actual Tag-map word equivalence for the new group-data mask.
All1024 symbolic word tags, all11-bit landing values, arbitrary clock events.
Caller holds central admission. No broad controller formal-equivalence claim.
"""
import argparse,subprocess,json,hashlib,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(exist_ok=False,parents=True);repo=Path(__file__).resolve().parents[3];ctrl=repo/'rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv';mod=repo/'rtl/ep_l2/rtl/ep_l2_metadata_word.sv';source=ctrl.read_text();expression=re.search(r'assign group_tag_map_data\[g\*PID_W \+:PID_W\]=(.*?);',source)[1];assert 'p_tag/META_GROUP==g' in expression
expression=expression.replace('==g','==(word_tag/META_GROUP)');wrapper='''module equiv(input clk,rst_n,native_commit,input [1:0] p_op,input [9:0] p_tag,word_tag,input [10:0] p_landing,output equal);
localparam META_GROUP=16,PID_W=11;
wire write=native_commit && p_op==0 && p_tag==word_tag;
wire [10:0] masked='''+expression+''';wire [10:0] a,b;
ep_l2_tag_map_word old_word(clk,rst_n,write,p_landing,a);
ep_l2_tag_map_word new_word(clk,rst_n,write,masked,b);
assign equal=a==b;endmodule\n''';top=a.out/'wrapper.sv';top.write_text(wrapper);ys=a.out/'proof.ys';ys.write_text(f'read_verilog -sv "{mod}" "{top}"\nprep -top equiv -flatten\nsat -seq 2 -tempinduct -set-init-zero -prove equal 1 -verify\n')
with (a.out/'proof.log').open('w') as f:subprocess.run(['yosys','-Q','-T','-s',str(ys)],stdout=f,stderr=subprocess.STDOUT,check=True)
assert 'Induction step proven: SUCCESS!' in (a.out/'proof.log').read_text();(a.out/'TAG_MAP_MASK_EQ_RECEIPT.json').write_text(json.dumps({'status':'INDUCTIVE_ALL_TAGS_LANDING_EVENTS_EQ_PASS','controller_sha256':hashlib.sha256(ctrl.read_bytes()).hexdigest(),'actual_mask_expression':expression,'Tag_width':10,'PID_width':11,'scope':'actual map word+actual data-mask expression, all symbolic word_tag, not complete controller formal proof'},indent=2)+'\n');print('actual Tag-map mask all tags/landings/events induction PASS')
