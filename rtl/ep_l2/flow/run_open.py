#!/usr/bin/env python3
"""Source-controlled open mapping/STA entry. Caller must hold central lease.
No SRAM technology mapping: the controller top exposes its RAM timing cut.
"""
import argparse,os,subprocess,json,hashlib,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--mapping',choices=['standard','fast','fast-clean'],default='standard',help='Yosys ABC effort; use one identical effort for compared modes');p.add_argument('--mode',choices=['B16','UNIFIED','S64'],required=True);p.add_argument('--liberty',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--drive-cell',default='BUF_X1');p.add_argument('--load',type=float,default=5.0);a=p.parse_args();lib=a.liberty.resolve(strict=True);out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);root=a.root.resolve();repo=root.parents[1]
# No implicit library download or substitution.
assert 'cell (' in lib.read_text() or 'cell(' in lib.read_text()
mode={'B16':0,'UNIFIED':1,'S64':2}[a.mode];wb=64 if mode==2 else 16
quote=lambda x:'"'+str(x).replace('\\','\\\\').replace('"','\\"')+'"'
files=[repo/x for x in (root/'flow/filelist.f').read_text().splitlines() if x and not x.startswith('#')]
source_identity={'git_HEAD_at_start':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'git_status_at_start':subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True),'entry_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'RTL_files':[{ 'path':str(f.relative_to(repo)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files]}
(out/'SOURCE_IDENTITY_START.json').write_text(json.dumps(source_identity,indent=2)+'\n')
abc_options={'standard':'','fast':'-fast ','fast-clean':'-script "+strash;map,-D,883;cleanup,-i,-o;buffer;upsize,-D,883;dnsize,-D,883;stime,-p" '}[a.mapping]
abc=out/'abc.constr';abc.write_text(f'set_driving_cell {a.drive_cell}\nset_load {a.load}\n')
script=out/'synth.ys';script.write_text('\n'.join([
 'read_verilog -sv -defer -D SYNTHESIS '+' '.join(map(quote,files)),
 f'hierarchy -check -top ep_l2_slice_ctrl -chparam MODE {mode} -chparam STATIC_WB {wb} -chparam N_TAG 1024 -chparam N_PAYLOAD 1168 -chparam N_WAD 128 -chparam GEN_W 32', 'log -stdout SYNTHESIS_START', 'synth -top ep_l2_slice_ctrl -noabc', 'log -stdout GENERIC_SYNTHESIS_COMPLETE',
 'check -assert','select -assert-none t:$dlatch t:$_DLATCH_*',
 f'read_liberty -lib {quote(lib)}', 'dffunmap',f'dfflibmap -liberty {quote(lib)}',
 f'abc {abc_options}-liberty {quote(lib)} -constr {quote(abc)} -D 883',
 'log -stdout LIBRARY_MAPPING_COMPLETE', 'clean',f'tee -o {quote(out/"stat.json")} stat -json -liberty {quote(lib)}',
 f'write_verilog -noattr -noexpr {quote(out/"mapped.v")}',
 'check -assert','select -assert-none t:$dlatch t:$_DLATCH_*'
 ])+'\n')
start=time.time()
tool_tmp=out/'tool_tmp';tool_tmp.mkdir();tool_env=os.environ.copy();tool_env['TMPDIR']=str(tool_tmp)
with (out/'yosys.log').open('w') as f:subprocess.run(['yosys','-Q','-T','-s',str(script)],stdout=f,stderr=subprocess.STDOUT,env=tool_env,check=True)
assert (out/'mapped.v').stat().st_size>10000,'meaningful connected design absent'
env=os.environ.copy();env.update(LIBERTY=str(lib),NETLIST=str(out/'mapped.v'),RTL_ROOT=str(root),IO_DRIVE_CELL=a.drive_cell,OUTPUT_LOAD_LIB_UNITS=str(a.load))
for label,period in [('target_1132MHz',0.883392226),('exploration_2ns',2.0)]:
 d=out/label;d.mkdir();env.update(OUTPUT_DIR=str(d),CLOCK_PERIOD_NS=str(period))
 with (d/'sta.log').open('w') as f:subprocess.run(['sta','-threads','1','-exit','-no_init',str(root/'flow/opensta.tcl')],stdout=f,stderr=subprocess.STDOUT,env=env,check=True)
 log=(d/'sta.log').read_text();assert 'Error:' not in log and 'error:' not in log,log[-3000:]
assert source_identity['RTL_files']==[{ 'path':str(f.relative_to(repo)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files],'RTL changed during mapping'
receipt={'mode':a.mode,'mapping_effort':a.mapping,'source_identity_at_start':source_identity,'parameters':{'MODE':mode,'STATIC_WB':wb,'N_TAG':1024,'N_PAYLOAD':1168,'N_WAD':128,'GEN_W':32,'data_bits':1024,'banks':4,'rows_per_bank':292,'P':1},'scope':'mapped control+access datapath; SRAM and traditional Tag/MSHR excluded, NOT whole L2','library_path':str(lib),'library_sha256':hashlib.sha256(lib.read_bytes()).hexdigest(),'RTL_files':[{ 'path':str(f.relative_to(repo)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files],'netlist_sha256':hashlib.sha256((out/'mapped.v').read_bytes()).hexdigest(),'sdc_sha256':hashlib.sha256((root/'flow/common.sdc').read_bytes()).hexdigest(),'tools':{cmd:subprocess.check_output(args,stderr=subprocess.STDOUT,text=True).strip() for cmd,args in [('yosys',['yosys','-V']),('OpenSTA',['sta','-version'])]},'elapsed_seconds':time.time()-start,'SRAM_area':None,'SRAM_delay':None,'post_layout':False}
(out/'FLOW_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
