#!/usr/bin/env python3
from pathlib import Path
import argparse,subprocess,re,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--depth',type=int,default=4);p.add_argument('--modes',default='0,1,2');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);repo=Path(__file__).resolve().parents[3];ref='1b011c6a51900462db9ae169d33bca742999abdb';base=repo/'rtl/ep_l2/rtl';names=['ep_l2_slice_ctrl','ep_l2_metadata_word','ep_l2_tag_map_word','ep_l2_first_one','ep_l2_index_mux','ep_l2_control_buffer','ep_l2_control_inverter'];rows=[];captured_RTL_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (base/'ep_l2_slice_ctrl.sv',base/'ep_l2_metadata_word.sv')}
oldmeta=subprocess.check_output(['git','show',ref+':rtl/ep_l2/rtl/ep_l2_metadata_word.sv'],cwd=repo,text=True)
oldctrl=subprocess.check_output(['git','show',ref+':rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv'],cwd=repo,text=True)
# Proof-only observable state ports; exact production procedural bodies retained.
debugs={'proof_gen':'N_PAYLOAD*GEN_W','proof_role':'N_PAYLOAD*3','proof_pins':'N_PAYLOAD*6','proof_ready':'N_PAYLOAD*4','proof_pending':'N_PAYLOAD*4','proof_dirty':'N_PAYLOAD*4','proof_live':'N_TAG','proof_map':'N_TAG*PID_W'};signals=['generation_bits','role_bits','pins_bits','sectors_ready_bits','sectors_pending_bits','dirty_bits','tag_live','tag_map_bits']
def instrument(s):
 s=s.replace('    input wire [4095:0] ram_rdata',''.join('    output wire ['+w+'-1:0] '+n+',\n' for n,w in debugs.items())+'    input wire [4095:0] ram_rdata');idx=s.rfind('endmodule');s=s[:idx]+''.join('    assign '+n+'='+v+';\n' for n,v in zip(debugs,signals))+s[idx:];return s
# Proof-only flattening removes physical keep attributes, never production gates/SDC.
strip_keep=lambda x:re.sub(r'\(\*[^*]*\bkeep(?:_hierarchy)?\s*=[^*]*\*\)','',x)
ctrl=strip_keep(instrument((base/'ep_l2_slice_ctrl.sv').read_text()));oldctrl=strip_keep(instrument(oldctrl));oldmeta=strip_keep(oldmeta)
(a.out/'r3_meta.sv').write_text(strip_keep((base/'ep_l2_metadata_word.sv').read_text()))
for n in names:
 oldmeta=re.sub(r'\b'+n+r'\b',n+'_r2',oldmeta);oldctrl=re.sub(r'\b'+n+r'\b',n+'_r2',oldctrl)
(a.out/'r2_meta.sv').write_text(oldmeta);(a.out/'r2_ctrl.sv').write_text(oldctrl);(a.out/'r3_ctrl.sv').write_text(ctrl)
header=ctrl.split(')(\n',1)[1].split(');',1)[0];header=re.sub(r'//[^\n]*','',header);ports=[];kind=width=None
for token in header.split(','):
 token=token.strip();match=re.match(r'^(input|output)\s+(?:wire|reg)\s*(\[[^]]+\])?\s*(\w+)$',token)
 if match:kind,width,name=match.groups();width=width or ''
 else:
  assert re.fullmatch(r'\w+',token),token
  name=token
 ports.append((kind,width,name))
inputs=[(w,n) for k,w,n in ports if k=='input'];outputs=[(w,n) for k,w,n in ports if k=='output'];params='MODE=0,N_TAG=4,N_PAYLOAD=32,STATIC_WB=2,N_WAD=2,GEN_W=3,ADDR_W=8,TAG_W=2,PID_W=5,WAD_W=1,ROW_W=3';connections=','.join('.'+x+'('+('4096\'b0' if x=='ram_rdata' else '1024\'b0' if x in ('req_data','fill_data') else x)+')' for _,x in inputs)
for mode in map(int,a.modes.split(',')):
 wrapper='module word_equiv #('+params.replace('MODE=0','MODE='+str(mode))+')('+','.join('input wire '+w+' '+n for w,n in inputs)+',output wire equal,output wire ['+str(len(outputs)-6)+':0] mismatch);\n'
 for q in ('a','b'):
  wrapper+=''.join('wire '+w+' '+n+'_'+q+';\n' for w,n in outputs)
  wrapper+=('ep_l2_slice_ctrl_r2' if q=='a' else 'ep_l2_slice_ctrl')+' #('+','.join('.'+k+'('+k+')' for k in ('MODE','N_TAG','N_PAYLOAD','STATIC_WB','N_WAD','GEN_W','ADDR_W'))+') '+q+'('+connections+','+','.join('.'+n+'('+n+'_'+q+')' for _,n in outputs)+');\n'
 checks=[]
 for w,n in outputs:
  if n in ('ram_be','ram_wdata','wb_be','wb_data','rsp_data'):continue
  eq=n+'_a=='+n+'_b'
  qualifier='native_commit_a' if n in ('native_tag','native_pid','native_gen') else 'rsp_valid_a' if n.startswith('rsp_') and n!='rsp_valid' else 'wb_valid_a' if n in ('wb_data','wb_be','wb_addr','wb_ticket','wb_ticket_gen') else None
  checks.append('(!'+qualifier+' || ('+eq+'))' if qualifier else '('+eq+')')
 wrapper+='assign equal='+' && '.join(checks)+';\n'+''.join('assign mismatch['+str(i)+']=!('+check+');\n' for i,check in enumerate(checks))+'endmodule\n';path=a.out/f'wrapper-{mode}.sv';path.write_text(wrapper);ys=a.out/f'proof-{mode}.ys';files=[base/'ep_l2_bank_arbiter.sv',a.out/'r3_meta.sv',a.out/'r3_ctrl.sv',a.out/'r2_meta.sv',a.out/'r2_ctrl.sv',path];ys.write_text('read_verilog -sv -D SYNTHESIS '+' '.join('"'+str(f)+'"' for f in files)+'\nprep -top word_equiv -flatten\nmemory_map\nopt -full\nwreduce\nopt_clean\n'+f'sat -seq {a.depth} -set-init-zero -set rst_n 1 -set-at 1 rst_n 0 -prove-skip 1 -prove equal 1 -verify -timeout 120 -dump_vcd \"{a.out}/counterexample-{mode}.vcd\" -show-inputs -show mismatch -show a.state -show b.state -show proof_gen_a -show proof_gen_b -show b.fe_gen_write -show b.frontend_generation_pid -show b.frontend_generation_old -show b.frontend_generation_next\n');log=a.out/f'proof-{mode}.log'
 with log.open('w') as f:subprocess.run(['yosys','-Q','-T','-s',str(ys)],stdout=f,stderr=subprocess.STDOUT,check=True)
 assert 'SUCCESS!' in log.read_text();rows.append({'mode':mode,'status':'BOUNDED_ACTUAL_CONTROLLER_EQ_PASS','depth':a.depth});print('actual R2/R3 controller',mode,'PASS',flush=True)
(a.out/'CONTROLLER_EQ_RECEIPT.json').write_text(json.dumps({'rows':rows,'scope':'actual controller control/metadata state and valid-qualified identity IO; byte data/mask datapath outputs excluded (separate full production byte suites); proof-only state output ports/keep removal for flattening (production cells retained); small4Tags/32payload/2WAD/GEN3 (PID_W5 represents BLOCK16 divisor); data values tied0 (numeric bytes separately tested), address width8; all masks/handshakes/identities unconstrained; no whole-controller unbounded proof or full-size cost claim','R2':ref,'captured_RTL_sha256':captured_RTL_sha256},indent=2)+'\n')
