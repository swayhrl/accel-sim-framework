#!/usr/bin/env python3
"""Diagnose real sequential paths without changing primary reset qualification.
Caller holds central EDA lease. Same immutable netlists/Liberty/SDC as finalcost.
"""
import argparse,json,subprocess,os,hashlib,re,gzip
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--runs-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--liberty',type=Path,required=True);a=p.parse_args();a.out.mkdir(exist_ok=False,parents=True);root=Path(__file__).resolve().parents[1];result=[]
for mode in ('B16','S64','UNIFIED'):
 run=a.runs_root/(mode+'-map-v2');r=json.loads((run/'FLOW_RECEIPT.json').read_text());net=Path(r['STA_root'])/'STA_netlist.v';compressed=not net.exists();source_net=net.with_suffix('.v.gz') if compressed else net;blob=gzip.decompress(source_net.read_bytes()) if compressed else source_net.read_bytes();assert hashlib.sha256(blob).hexdigest()==r['netlist_sha256'];assert hashlib.sha256(a.liberty.read_bytes()).hexdigest()==r['library_sha256'];assert hashlib.sha256((root/'flow/common.sdc').read_bytes()).hexdigest()==r['sdc_sha256'];d=a.out/mode;d.mkdir()
 if compressed:net=d/'EXACT_STA_INPUT.v';net.write_bytes(blob)
 env=os.environ.copy();env.update(LIBERTY=str(a.liberty.resolve()),NETLIST=str(net),OUTPUT_DIR=str(d),RTL_ROOT=str(root),IO_DRIVE_CELL='BUF_X1',OUTPUT_LOAD_LIB_UNITS='5.0',LIB_TIME_UNIT_NS='1.0',CLOCK_PERIOD_NS='0.883392226')
 cmd=['sta','-threads','1','-exit','-no_init',str(root/'flow/opensta_data_paths_r2.tcl')]
 with (d/'sta.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=env,check=True)
 assert 'Error:' not in (d/'sta.log').read_text();actual=(d/'primary_wns.rpt').read_bytes();expected=(Path(r['STA_root'])/'target_1132MHz/wns.rpt').read_bytes();assert actual==expected,'primary WNS changed'
 assert (d/'primary_tns.rpt').read_bytes()==(Path(r['STA_root'])/'target_1132MHz/tns.rpt').read_bytes(),'primary TNS changed'
 if compressed:
  packed=gzip.compress(blob,6,mtime=0);archive=net.with_suffix('.v.gz');archive.write_bytes(packed);assert gzip.decompress(archive.read_bytes())==blob;net.unlink()
 result.append({'mode':mode,'same_primary_WNS_TNS':True,'netlist_sha256':r['netlist_sha256'],'SDC_sha256':r['sdc_sha256'],'Liberty_sha256':r['library_sha256'],'reset_timed':True,'purpose':'Additional path filters only; primary timing qualification unchanged','command':cmd})
 print(mode,'additional actual FF/control paths; exact primary WNS/TNS unchanged',flush=True)
(a.out/'DATA_PATHS_RECEIPT.json').write_text(json.dumps({'rows':result,'Tcl_sha256':hashlib.sha256((root/'flow/opensta_data_paths_r2.tcl').read_bytes()).hexdigest(),'entry_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
