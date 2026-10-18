#!/usr/bin/env python3
"""Resume actual STA from an already successful full-size mapped netlist.
Caller holds central lease. Never re-synthesize or accept incomplete mapping.
"""
import argparse,os,subprocess,json,hashlib,time,re,gzip
from pathlib import Path
from sta_netlist import portable_netlist

def main():
    p=argparse.ArgumentParser();p.add_argument('--mapped-run',type=Path,required=True);p.add_argument('--mode',choices=['B16','UNIFIED','S64'],required=True);p.add_argument('--liberty',type=Path,required=True);p.add_argument('--phase',default='sta-portable-v1');p.add_argument('--drive-cell',default='BUF_X1');p.add_argument('--load',type=float,default=5.0);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];repo=root.parents[1];run=a.mapped_run.resolve(strict=True);lib=a.liberty.resolve(strict=True);out=run/a.phase;out.mkdir(exist_ok=False)
    source=json.loads((run/'SOURCE_IDENTITY_START.json').read_text());script=(run/'synth.ys').read_text();mode={'B16':0,'UNIFIED':1,'S64':2}[a.mode];wb=64 if mode==2 else 16
    assert f'-chparam MODE {mode} -chparam STATIC_WB {wb} -chparam N_TAG 1024 -chparam N_PAYLOAD 1168 -chparam N_WAD 128 -chparam GEN_W 32' in script
    assert source['RTL_files']==[{'path':r['path'],'sha256':hashlib.sha256((repo/r['path']).read_bytes()).hexdigest()} for r in source['RTL_files']],'hardware changed'
    assert source['flow_files']['rtl/ep_l2/flow/common.sdc']==hashlib.sha256((root/'flow/common.sdc').read_bytes()).hexdigest(),'physical constraints changed'
    mapping_log=(run/'yosys.log').read_text() if (run/'yosys.log').exists() else gzip.decompress((run/'yosys.log.gz').read_bytes()).decode()
    assert 'Found and reported 0 problems.' in mapping_log[-2000:],'final mapping check absent'
    stats=json.loads((run/'stat.json').read_text());assert stats['design']['num_cells']>10000
    assert all(x.get('num_memories',0)==0 and x.get('num_processes',0)==0 for x in stats['modules'].values()),'memory/process must not leak into standard-cell cut'
    start=time.time();portable=out/'STA_netlist.v';mapped=run/'mapped.v' if (run/'mapped.v').exists() else run/'mapped.v.gz';conversion=portable_netlist(mapped,portable);(out/'NETLIST_FORMAT_RECEIPT.json').write_text(json.dumps(conversion,indent=2)+'\n')
    env=os.environ.copy();env.update(LIBERTY=str(lib),NETLIST=str(portable),RTL_ROOT=str(root),IO_DRIVE_CELL=a.drive_cell,OUTPUT_LOAD_LIB_UNITS=str(a.load),LIB_TIME_UNIT_NS='1.0')
    phase_identity={'git_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'files':{str(f.relative_to(repo)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [root/'flow/run_sta.py',root/'flow/sta_netlist.py',root/'flow/opensta.tcl',root/'flow/common.sdc']},'OpenSTA_threads':1,'time_unit_ns':1.0,'library_sha256':hashlib.sha256(lib.read_bytes()).hexdigest()}
    (out/'STA_PHASE_IDENTITY.json').write_text(json.dumps(phase_identity,indent=2)+'\n')
    for label,period in [('target_1132MHz',0.883392226),('exploration_2ns',2.0)]:
        d=out/label;d.mkdir();env.update(OUTPUT_DIR=str(d),CLOCK_PERIOD_NS=str(period));cmd=['sta','-threads','1','-exit','-no_init',str(root/'flow/opensta.tcl')]
        with (d/'sta.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=env,check=True)
        log=(d/'sta.log').read_text();assert 'Error:' not in log and 'error:' not in log,log[-3000:]
    receipt={'mode':a.mode,'mapping_effort':'fast-clean' if 'cleanup,-i,-o' in script else 'other-see-synth.ys','parameters':{'MODE':mode,'STATIC_WB':wb,'N_TAG':1024,'N_PAYLOAD':1168,'N_WAD':128,'GEN_W':32,'data_bits':1024,'banks':4,'rows_per_bank':292,'P':1},'scope':'mapped control+access datapath; SRAM and traditional Tag/MSHR excluded, NOT whole L2','library_path':str(lib),'library_sha256':phase_identity['library_sha256'],'RTL_files':source['RTL_files'],'source_identity_at_start':source,'STA_phase_identity':phase_identity,'netlist_sha256':conversion['STA_sha256'],'raw_mapped_netlist_sha256':conversion['raw_sha256'],'STA_root':str(out),'sdc_sha256':phase_identity['files']['rtl/ep_l2/flow/common.sdc'],'tools':{cmd:subprocess.check_output(args,stderr=subprocess.STDOUT,text=True).strip() for cmd,args in [('yosys',['yosys','-V']),('OpenSTA',['sta','-version']),('ABC',['yosys-abc','-c','version'])]},'STA_elapsed_seconds':time.time()-start,'SRAM_area':None,'SRAM_delay':None,'post_layout':False}
    (run/'FLOW_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
if __name__=='__main__':main()
