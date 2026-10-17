#!/usr/bin/env python3
"""Bounded actual R1/R2 metadata-word equivalence, unconstrained event overlaps.
Caller holds central lease. Not a proof of the whole allocator/controller.
"""
import argparse,subprocess,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--induct-only',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);repo=Path(__file__).resolve().parents[3]
r1=subprocess.check_output(['git','show','09de19579c0708f6542dfd65e1f3aae8a9a8b841:rtl/ep_l2/rtl/ep_l2_metadata_word.sv'],cwd=repo,text=True).split('endmodule',1)[0]+'endmodule\n';r1=r1.replace('module ep_l2_metadata_word','module ep_l2_metadata_word_r1');(a.out/'r1_word.sv').write_text(r1)
ports='''input clk,rst_n,reserve_resident,reserve_wb,pin_update,pin_increment,read_pin_add,read_pin_release,fill_update,become_wb,install,already_reserved,install_old_live,hit_write,invalidate,rollback_release,lower_release,
input [9:0] new_owner,input [3:0] fill_sectors,install_ready,install_pending,install_dirty,write_ready,write_dirty,output equal'''
controls='clk,rst_n,reserve_resident,reserve_wb,new_owner,pin_update,pin_increment,read_pin_add,read_pin_release,fill_update,fill_sectors,become_wb,install,already_reserved,install_ready,install_pending,install_dirty,hit_write,write_ready,write_dirty,invalidate,rollback_release,lower_release'.split(',')
connections=','.join('.'+x+'('+x+')' for x in controls)
for support in (0,1):
 wrapper='module word_equiv('+ports+');\n'
 for q in ('a','b'):
  wrapper+=f'wire [2:0] role_{q};wire [31:0] generation_{q};wire [9:0] owner_tag_{q};wire [5:0] pins_{q};wire [3:0] sectors_ready_{q},sectors_pending_{q},dirty_{q};\n'
 extra='';outs=['role','generation','owner_tag','pins','sectors_ready','sectors_pending','dirty']
 for mod,q,genport in [('ep_l2_metadata_word_r1','a',".install_generation(generation_a+(install_old_live ? 32'd2 : 32'd1))"),('ep_l2_metadata_word','b','.install_old_live(install_old_live)')]:
  wrapper+=f'{mod} #(.SUPPORT_RES({support})) {q}({connections},{genport},'+','.join('.'+v+'('+v+'_'+q+')' for v in outs)+');\n'
 wrapper+='assign equal={' + ','.join(v+'_a' for v in outs)+'}=={'+','.join(v+'_b' for v in outs)+'};\nendmodule\n'
 path=a.out/f'wrapper-{support}.sv';path.write_text(wrapper);ys=a.out/f'prove-{support}.ys';proof='sat -seq 2 -tempinduct -set-init-zero -prove equal 1 -verify' if a.induct_only else 'sat -seq 6 -set-at 1 rst_n 0 -set rst_n 1 -prove-skip 1 -prove equal 1 -verify';ys.write_text(f'read_verilog -sv "{a.out}/r1_word.sv" "{repo}/rtl/ep_l2/rtl/ep_l2_metadata_word.sv" "{path}"\nprep -top word_equiv -flatten\n{proof}\n')
 log=a.out/f'proof-{support}.log'
 with log.open('w') as f:subprocess.run(['yosys','-Q','-T','-s',str(ys)],stdout=f,stderr=subprocess.STDOUT,check=True)
 assert 'SUCCESS!' in log.read_text();print('METADATA_EQ SUPPORT_RES',support,('induction unconstrained coincident controls PASS' if a.induct_only else '6steps unconstrained coincident controls PASS'),flush=True)
(a.out/'METADATA_EQ_RECEIPT.json').write_text(json.dumps({'status':('INDUCTIVE_ACTUAL_R1_R2_WORD_EQ_PASS' if a.induct_only else 'BOUNDED_6_STEP_ACTUAL_R1_R2_WORD_EQ_PASS'),'GEN_W':32,'SUPPORT_RES':[0,1],'initialization':('all word state zero; reset then arbitrary' if a.induct_only else 'step1reset'),'event_controls':'unconstrained including overlaps','DYNAMIC_OWNER':1,'scope':'single word state, no global controller/free-search formal claim','r1_source':'09de19579c0708f6542dfd65e1f3aae8a9a8b841','R2_word_file_sha256':hashlib.sha256((repo/'rtl/ep_l2/rtl/ep_l2_metadata_word.sv').read_bytes()).hexdigest()},indent=2)+'\n')
