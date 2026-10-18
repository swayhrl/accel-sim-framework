#!/usr/bin/env python3
"""Actual-source R2/R3 word induction and exhaustive GEN write-port miter.
Caller holds central EDA lease. Not a whole-controller/unbounded proof.
"""
from pathlib import Path
import argparse,subprocess,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);repo=Path(__file__).resolve().parents[3];meta=repo/'rtl/ep_l2/rtl/ep_l2_metadata_word.sv';ref='1b011c6a51900462db9ae169d33bca742999abdb';old=subprocess.check_output(['git','show',ref+':rtl/ep_l2/rtl/ep_l2_metadata_word.sv'],cwd=repo,text=True).split('endmodule',1)[0]+'endmodule\n';old=old.replace('module ep_l2_metadata_word','module ep_l2_metadata_word_r2');(a.out/'r2_word.sv').write_text(old)
ports='''input clk,rst_n,reserve_resident,reserve_wb,pin_update,pin_increment,read_pin_add,read_pin_release,fill_update,become_wb,install,already_reserved,install_old_live,hit_write,invalidate,rollback_release,lower_release,
input [9:0] new_owner,input [3:0] fill_sectors,install_ready,install_pending,install_dirty,write_ready,write_dirty,output equal'''
controls='clk,rst_n,reserve_resident,reserve_wb,new_owner,pin_update,pin_increment,read_pin_add,read_pin_release,fill_update,fill_sectors,become_wb,install,already_reserved,install_old_live,install_ready,install_pending,install_dirty,hit_write,write_ready,write_dirty,invalidate,rollback_release,lower_release'.split(',');outs=['role','generation','owner_tag','pins','sectors_ready','sectors_pending','dirty'];results=[]
def prove(label,sources,wrapper,cmd):
 path=a.out/(label+'.sv');path.write_text(wrapper);ys=a.out/(label+'.ys');ys.write_text('read_verilog -sv '+ ' '.join('"'+str(x)+'"' for x in sources+[path])+'\nprep -top word_equiv -flatten\n'+cmd+'\n');log=a.out/(label+'.log')
 with log.open('w') as f:subprocess.run(['yosys','-Q','-T','-s',str(ys)],stdout=f,stderr=subprocess.STDOUT,check=True)
 assert 'SUCCESS!' in log.read_text();print(label,'PASS',flush=True);results.append({'label':label,'status':'ACTUAL_SOURCE_SAT_PASS','script_sha256':hashlib.sha256(ys.read_bytes()).hexdigest()})
for support,static in ((0,0),(1,0),(1,1)):
 connections=','.join('.'+x+'('+('1\'b0' if static and x in ('reserve_resident','reserve_wb','become_wb','rollback_release','lower_release') else x)+')' for x in controls)
 wrapper='module word_equiv('+ports+');\n'
 for q in ('a','b'):wrapper+=f'wire [2:0] role_{q};wire [31:0] generation_{q};wire [9:0] owner_tag_{q};wire [5:0] pins_{q};wire [3:0] sectors_ready_{q},sectors_pending_{q},dirty_{q};\n'
 sr='0' if static else 'reserve_resident';sw='0' if static else 'reserve_wb';rb='0' if static else 'rollback_release';lr='0' if static else 'lower_release'
 wrapper+=f'wire step2={support} && install && !already_reserved && install_old_live && !invalidate && !({rb}) && !({lr});\nwire gwe=({support} && ({sr})) || ({sw}) || ({support} && install && !already_reserved) || ({support} && invalidate) || ({rb}) || ({lr});\nwire [31:0] nv;ep_l2_generation_step e(generation_b,step2,nv);\n'
 for mod,q,extra in [('ep_l2_metadata_word_r2','a',''),('ep_l2_metadata_word','b',',.generation_write(gwe),.generation_value(nv)')]:wrapper+=f'{mod} #(.SUPPORT_RES({support}),.STATIC_RESIDENT({static})) {q}({connections}'+extra+','+','.join('.'+v+'('+v+'_'+q+')' for v in outs)+');\n'
 wrapper+='assign equal={'+','.join(v+'_a' for v in outs)+'}=={'+','.join(v+'_b' for v in outs)+'};endmodule\n';prove(f'word-{support}-{static}',[a.out/'r2_word.sv',meta],wrapper,'sat -seq 2 -tempinduct -set-init-zero -prove equal 1 -verify')
for w in (3,32):
 wrapper=f'''module word_equiv(input [4*{w}-1:0] old,input [1:0] fp,lp,input reserve,commit,abort,lower,old_live,input [1:0] state,output equal);
 wire r=state==0 && reserve,c=state==1 && commit && !abort,b=state!=0 && abort;
 wire fw=r|c|b;wire st=c&&old_live;wire [{w}-1:0] fn,ln;
 ep_l2_generation_step #(.GEN_W({w})) fe(old[fp*{w} +:{w}],st,fn);
 ep_l2_generation_step #(.GEN_W({w})) lo(old[lp*{w} +:{w}],1'b0,ln);
 wire [4*{w}-1:0] a,z;
 genvar i;generate for(i=0;i<4;i=i+1)begin
 wire [{w}-1:0] x=old[i*{w} +:{w}];
 assign a[i*{w} +:{w}]=lower&&lp==i ? x+{w}'d1 : (r||c||b)&&fp==i ? x+(st?{w}'d2:{w}'d1) : x;
 assign z[i*{w} +:{w}]=lower&&lp==i ? ln : fw&&fp==i ? fn : x;
 end endgenerate
 assign equal=a==z;endmodule
''';prove('two-port-'+str(w),[meta],wrapper,'sat -prove equal 1 -verify')
(a.out/'R3_PORT_WORD_EQ_RECEIPT.json').write_text(json.dumps({'status':'ACTUAL_R2_R3_WORD_INDUCTION_AND_EXHAUSTIVE_TWO_GEN_PORTS_PASS','R2':ref,'R3_metadata_sha256':hashlib.sha256(meta.read_bytes()).hexdigest(),'rows':results,'scope':'word induction arbitrary coincident non-GEN events; unreachable static role controls0 in both; two-port all indices/GEN bits/same or different slot/front state event overlap/lower priority, GEN3 andGEN32','environment':'frontend reservation/commit/abort mutually exclusive by actual state predicates; lower independent; no assumption that P1 serializes metadata','whole_controller_equivalence':False},indent=2)+'\n')
