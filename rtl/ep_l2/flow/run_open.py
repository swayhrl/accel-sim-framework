#!/usr/bin/env python3
"""Source-controlled open mapping/STA entry. Caller must hold central lease.
No SRAM technology mapping: the controller top exposes its RAM timing cut.
"""
import argparse,os,subprocess,json,hashlib,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--mode',choices=['B16','UNIFIED','S64'],required=True);p.add_argument('--liberty',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--drive-cell',default='BUF_X1');p.add_argument('--load',type=float,default=5.0);a=p.parse_args();lib=a.liberty.resolve(strict=True);out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);root=a.root.resolve();repo=root.parents[1]
# No implicit library download or substitution.
assert 'cell (' in lib.read_text() or 'cell(' in lib.read_text()
mode={'B16':0,'UNIFIED':1,'S64':2}[a.mode];wb=64 if mode==2 else 16
quote=lambda x:'"'+str(x).replace('\\','\\\\').replace('"','\\"')+'"'
files=[repo/x for x in (root/'flow/filelist.f').read_text().splitlines() if x and not x.startswith('#')]
abc=out/'abc.constr';abc.write_text(f'set_driving_cell {a.drive_cell}\nset_load {a.load}\n')
script=out/'synth.ys';script.write_text('\n'.join([
 'read_verilog -sv -D SYNTHESIS '+' '.join(map(quote,files)),
 f'chparam -set MODE {mode} -set STATIC_WB {wb} -set N_TAG 1024 -set N_PAYLOAD 1168 -set N_WAD 128 -set GEN_W 32 ep_l2_slice_ctrl',
 'hierarchy -check -top ep_l2_slice_ctrl', 'synth -top ep_l2_slice_ctrl -noabc',
 'check -assert','select -assert-none t:$dlatch t:$_DLATCH_*',
 'dffunmap',f'dfflibmap -liberty {quote(lib)}',
 f'abc -liberty {quote(lib)} -constr {quote(abc)} -D 883',
 'clean',f'tee -o {quote(out/"stat.json")} stat -json -liberty {quote(lib)}',
 f'write_verilog -noattr -noexpr {quote(out/"mapped.v")}',
 'check -assert','select -assert-none t:$dlatch t:$_DLATCH_*'
 ])+'\n')
start=time.time()
with (out/'yosys.log').open('w') as f:subprocess.run(['yosys','-Q','-T','-q','-s',str(script)],stdout=f,stderr=subprocess.STDOUT,check=True)
assert (out/'mapped.v').stat().st_size>10000,'meaningful connected design absent'
env=os.environ.copy();env.update(LIBERTY=str(lib),NETLIST=str(out/'mapped.v'),RTL_ROOT=str(root),IO_DRIVE_CELL=a.drive_cell,OUTPUT_LOAD_LIB_UNITS=str(a.load))
for label,period in [('target_1132MHz',0.883392226),('exploration_2ns',2.0)]:
 d=out/label;d.mkdir();env.update(OUTPUT_DIR=str(d),CLOCK_PERIOD_NS=str(period))
 with (d/'sta.log').open('w') as f:subprocess.run(['sta','-exit','-no_init',str(root/'flow/opensta.tcl')],stdout=f,stderr=subprocess.STDOUT,env=env,check=True)
 log=(d/'sta.log').read_text();assert 'Error:' not in log and 'error:' not in log,log[-3000:]
receipt={'mode':a.mode,'parameters':{'MODE':mode,'STATIC_WB':wb,'N_TAG':1024,'N_PAYLOAD':1168,'N_WAD':128,'GEN_W':32,'data_bits':1024,'banks':4,'rows_per_bank':292,'P':1},'scope':'mapped control+access datapath; SRAM and traditional Tag/MSHR excluded, NOT whole L2','library_path':str(lib),'library_sha256':hashlib.sha256(lib.read_bytes()).hexdigest(),'RTL_files':[{ 'path':str(f.relative_to(repo)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files],'netlist_sha256':hashlib.sha256((out/'mapped.v').read_bytes()).hexdigest(),'sdc_sha256':hashlib.sha256((root/'flow/common.sdc').read_bytes()).hexdigest(),'tools':{cmd:subprocess.check_output(args,stderr=subprocess.STDOUT,text=True).strip() for cmd,args in [('yosys',['yosys','-V']),('OpenSTA',['sta','-version'])]},'elapsed_seconds':time.time()-start,'SRAM_area':None,'SRAM_delay':None,'post_layout':False}
(out/'FLOW_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
