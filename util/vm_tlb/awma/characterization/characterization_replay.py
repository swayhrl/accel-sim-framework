#!/usr/bin/env python3
"""Run an already-admitted AWMA characterization profile in a fresh process."""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'simulation'))
import fixed_window_replay as replay
import simulation_foundation as foundation
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(); p.add_argument('--admission',type=Path,required=True); p.add_argument('--profile',required=True); p.add_argument('--config',type=Path,required=True); p.add_argument('--binary',type=Path,required=True); p.add_argument('--kernelslist',type=Path,required=True); p.add_argument('--output-dir',type=Path,required=True); p.add_argument('--telemetry-exporter',type=Path,required=True); p.add_argument('--max-cycles',type=int,required=True); p.add_argument('--framework',required=True); p.add_argument('--core',required=True); p.add_argument('--env',action='append',default=[])
 a=p.parse_args(); ad=json.loads(a.admission.read_text())
 if not ad.get('admitted') or ad.get('status')!='ADMITTED': raise SystemExit('admission receipt is not ADMITTED')
 out=a.output_dir.resolve()
 if out.exists(): raise SystemExit('refusing existing output dir')
 out.mkdir(parents=True); effective=out/'effective.config'; effective.write_text(a.config.read_text() + ('\n' if not a.config.read_text().endswith('\n') else '') + '-gpgpu_max_cycle %d\n' % a.max_cycles); env=os.environ.copy(); ov={}
 for x in a.env: k,v=x.split('=',1); env[k]=v; ov[k]=v
 cmd=[str(a.binary.resolve()),'-config',str(effective.resolve()),'-trace',str(a.kernelslist.resolve())]
 try: c=subprocess.run(cmd,cwd=out,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=900,check=False); log,rc,ext=c.stdout,c.returncode,False
 except (OSError,subprocess.TimeoutExpired) as e: log,rc,ext='EXTERNAL_RUNTIME_FAILURE: %s\n'%e,127,True
 (out/'run.log').write_text(log); cycles=re.findall(r'^gpu_sim_cycle = ([0-9]+)$',log,re.M); boundary='GPGPU-Sim: ** break due to reaching the maximum cycles (or instructions) **' in log; status='EXPECTED_FIXED_WINDOW_BOUNDARY' if (not ext and rc==0 and boundary and cycles and int(cycles[-1])==a.max_cycles) else replay.classify_execution(log,rc,admitted=True,external_failure=ext)
 vals={'roi':'Q05_PREFILL_ATTN_FLASH','framework_head':a.framework,'core_head':a.core,'profile':a.profile,'sim_input_id':ad['sim_input_id'],'max_cycles':str(a.max_cycles),'execution_status':status,'returncode':str(rc),'config_sha256':sha(effective)}
 (out/'RUN_MANIFEST.tsv').write_text('key\tvalue\n'+'\n'.join('%s\t%s'%x for x in sorted(vals.items()))+'\n')
 tele={'status':'NOT_RUN','output_sha256':None}
 if status=='EXPECTED_FIXED_WINDOW_BOUNDARY':
  td=out/'telemetry'; e=subprocess.run([sys.executable,str(a.telemetry_exporter.resolve()),'--run-dir',str(out),'--output-dir',str(td),'--trace-policy','FULL_RANK0'],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False); files={str(x.relative_to(td)):sha(x) for x in sorted(td.glob('*')) if x.is_file()} if td.exists() else {}; tele={'status':'PASS' if e.returncode==0 and files else 'FAIL','diagnostic':e.stdout.strip(),'files':files,'output_sha256':foundation.hash_root(files) if files else None}
 r={'profile':a.profile,'sim_input_id':ad['sim_input_id'],'execution_status':status,'returncode':rc,'max_cycles':a.max_cycles,'config_sha256':sha(effective),'raw_log_sha256':sha(out/'run.log'),'command_sha256':foundation.stable_id('COMMAND',{'argv':cmd}).split('_',1)[1],'environment_sha256':foundation.stable_id('ENVIRONMENT',ov).split('_',1)[1],'telemetry':tele}
 (out/'RESEARCH_RUN_RECEIPT.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n'); print(json.dumps(r,sort_keys=True,indent=2)); return 0 if status=='EXPECTED_FIXED_WINDOW_BOUNDARY' and tele['status']=='PASS' else 2
if __name__=='__main__': raise SystemExit(main())