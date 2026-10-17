"""Existing all-OFF control, rebound to official local-ideal runtime and new72 budget."""
import argparse,csv,json,os,resource,shutil,subprocess,sys,time
from pathlib import Path
from registry import Registry,run_key,write_json,process_identity,PARALLEL
from acceptance import immutable_loader_binding
from run import digest,require,asset_manifest,content_hash,process_tree_rss,terminate_owned,tree_bytes
from qualify_native_off import BASELINE,CSVS,ENV,native_metrics,safe_resources

REPO=Path(__file__).resolve().parents[3]
OUT=Path('/workspace/ep_l2_potential20261017_lane5_results')
HAND=Path('/workspace/ep_l2_ft20261016_shared/lane1/PARALLEL_LOCAL_IDEALS_RELEASE_r1.json')
CHECK=OUT/'LOCAL_IDEAL_NATIVE_OFF_CHECKPOINT_r1.json'


def prepare():
 h=json.loads(HAND.read_text());prod=json.loads(Path(h['producer_receipt_path']).read_text());ind=json.loads((OUT/'independent_local_ideals_runtime_r1/RECEIPT.json').read_text());require(ind['status']=='AFFECTED_NEW_RUNTIME_ASSERTIONS_PASS_ELEVEN_AND_MODE_REVIEW_PENDING' and len(ind['tests'])==27 and ind['source_identity']['binary_sha256']==h['binary_sha256'],'Missing exact new27 independent checks')
 for row in ind['tests']:require(row['exit_code']==0 and row['status']=='ACTUAL_ASSERTIONS_PASS' and digest(row['log'])==row['sha256'],'Independent check changed')
 require(digest(h['binary'])==h['binary_sha256'],'Changed official runtime')
 base=json.loads((BASELINE/'run_status.json').read_text());assets=json.loads((BASELINE/'input_assets.json').read_text());fw=Path(h['lane1_frozen_framework']);core=Path(h['lane1_frozen_equivalent_core'])
 paths=[core/'configs/tested-cfgs/SM7_QV100/gpgpusim.config',fw/'gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config',fw/'tests/ep_l2/b0_banked_d512_850.config',fw/'tests/ep_l2/m0a_off.config'];cfg=[{'name':f'config-{i}.config','path':str(p)} for i,p in enumerate(paths)];cm=asset_manifest(cfg,ordered=True);tm=asset_manifest(assets['trace_paths']);require(cm==assets['configs'] and tm==assets['trace'],'Actual full native control input differs')
 identity={**base['identity'],**{k:h[k] for k in ('core_source_commit','framework_source_commit','binary_sha256')}};identity['termination_contract']={**identity['termination_contract'],'timeout_seconds':3600}
 require(identity['runtime_config_sha256']==content_hash({'ordered_configs':cm,'auxiliary_assets':[],'environment':ENV}) and identity['trace_content_sha256']==content_hash(tm),'Native input formula differs')
 checkpoint={'status':'PREDECLARED_NECESSARY_NEW_RUNTIME_ALL_OFF_CANARY','experiment_id':PARALLEL,'identity':identity,'run_key':run_key(identity),'official_release':h['publication'],'independent27_sha256':digest(OUT/'independent_local_ideals_runtime_r1/RECEIPT.json'),'reason':'New runtime changes L2/metadata/defaultOFF paths. Preserve original11 gates: real same-input native OFF73873cycles/56000000insn and sevenCSV equivalence needed; cannot inherit oldbinaryPASS. This one new full-app canary counts in72.','same_complete_trace':True,'configs':cfg,'config_manifest':cm,'traces':assets['trace_paths'],'trace_manifest':tm,'parser':str(fw/'util/ep_l2/parse_epl2_b0.py'),'parser_sha256':digest(fw/'util/ep_l2/parse_epl2_b0.py'),'timeout_seconds':3600}
 if CHECK.exists():require(json.loads(CHECK.read_text())==checkpoint,'Canary checkpoint immutable')
 else:write_json(CHECK,checkpoint)
 r=Registry();cell=r.register_native_off_control(identity,{'path':str(CHECK),'sha256':digest(CHECK)})
 return h,prod,checkpoint,cell,r


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare-only',action='store_true');p.add_argument('--retry-checkpoint',type=Path);a=p.parse_args();h,prod,s,cell,r=prepare()
 if a.prepare_only:print(json.dumps({'status':'CANARY_REGISTERED_NOT_STARTED','cell':cell,'new_application_starts':0}));return
 snap=r.snapshot();deadline=snap['campaigns'][PARALLEL]['deadline_unix'];require(time.time()<deadline,'No new canary after deadline');safe_resources();directory=OUT/(s['run_key']+('_attempt_r2' if a.retry_checkpoint else ''));recovery={'path':str(a.retry_checkpoint),'sha256':digest(a.retry_checkpoint)} if a.retry_checkpoint else None;fresh,allocation=r.claim(s['identity'],'lane5',directory,cpu=1,memory=4*2**30,client_binding=immutable_loader_binding(),retry_checkpoint=recovery,experiment={'experiment_id':PARALLEL,'regime':'H0','profile':'NATIVE_OFF_CONTROL','cell_id':cell['cell_id'],'deadline_unix':deadline})
 if not fresh:print('DUPLICATE_CONTROL_NOT_STARTED');return
 proc=None;status='INCOMPLETE';report={'qualification_control':True,'experiment_id':PARALLEL,'cell_id':cell['cell_id'],'identity':s['identity'],'run_key':s['run_key'],'allocation':allocation,'status':status};resource.setrlimit(resource.RLIMIT_CORE,(0,0));started=time.monotonic()
 try:
  directory.mkdir(exist_ok=False);write_json(directory/'input_assets.json',s);binary=directory/'accel-sim.out';shutil.copyfile(h['binary'],binary);binary.chmod(0o555);require(digest(binary)==h['binary_sha256'],'Snapshot binary changed');command=[str(binary)]
  for i,row in enumerate(s['configs']):
   target=directory/f'config-{i}.config';shutil.copyfile(row['path'],target);require(digest(target)==s['config_manifest'][i]['sha256'],'Snapshot config changed');command+=['-config',str(target)]
  command+=['-trace',next(v['path'] for v in s['traces'] if v['name']=='kernelslist.g')];report['command']=command
  with (directory/'raw.log').open('xb') as stream:
   proc=subprocess.Popen(command,cwd=directory,stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,**ENV),start_new_session=True);report['process']=process_identity(proc.pid);r.update(s['run_key'],allocation['lease_id'],'RUNNING',process=report['process']);peak=0
   while proc.poll() is None:
    safe_resources();peak=max(peak,process_tree_rss(proc.pid));require(peak<=allocation['memory_bytes'] and time.monotonic()-started<3600 and (directory/'raw.log').stat().st_size<2*2**30 and tree_bytes(OUT)<8*2**30,'Canary resource/timeout cap');time.sleep(1)
  require(proc.returncode==0 and 'GPGPU-Sim: *** exit detected ***' in (directory/'raw.log').read_text(),'Native control exit failed')
  require(digest(s['parser'])==s['parser_sha256'],'Parser changed');cmd=[sys.executable,s['parser'],str(directory/'raw.log'),'--out',str(directory),'--framework-commit',h['framework_source_commit'],'--core-commit',h['core_source_commit'],'--source-log',str(directory/'raw.log')];parsed=subprocess.run(cmd,cwd=directory,capture_output=True,timeout=120);(directory/'parser.stdout').write_bytes(parsed.stdout);(directory/'parser.stderr').write_bytes(parsed.stderr);require(parsed.returncode==0,'Native parser failed')
  summary=next(csv.DictReader((directory/'target_summary.csv').open()));require(all(summary[k]=='1' for k in ('invariants_terminal_clean','invariants_payload_consistent')) and summary['slice_count']=='64' and summary['terminal_invariant_records']=='64','Native all64 closure failed')
  require(native_metrics(directory/'raw.log')==native_metrics(BASELINE/'raw.log')=={'cycle':73873,'insn':56000000},'New nativeOFF metrics differ')
  hashes={}
  base=json.loads((BASELINE/'run_status.json').read_text())
  for n in CSVS:require(digest(directory/n)==digest(BASELINE/n)==base['artifact_sha256'][n],'New nativeOFF CSV differs '+n);hashes[n]=digest(directory/n)
  require(asset_manifest(s['configs'],ordered=True)==s['config_manifest'] and asset_manifest(s['traces'])==s['trace_manifest'] and digest(h['binary'])==h['binary_sha256'],'Control inputs changed')
  status='COMPLETE_VALID';report.update(off_equivalence='PASS',metrics=native_metrics(directory/'raw.log'),seven_csv_sha256=hashes,scope='Necessary one new-source qualification canary; not a seed performance endpoint or paper result')
 except BaseException as e:status='FAILED';report['error']=repr(e);raise
 finally:
  if proc:terminate_owned(proc)
  report.update(status=status,exit_code=proc.returncode if proc else None,wall_seconds=time.monotonic()-started,raw_log_sha256=digest(directory/'raw.log') if (directory/'raw.log').exists() else None);write_json(directory/'run_status.json',report);r.update(s['run_key'],allocation['lease_id'],status,exit_code=report['exit_code'],raw_log_sha256=report['raw_log_sha256'],detail=report.get('error','NativeOFF all64/metrics/sevenCSV equivalence'));write_json(OUT/'LOCAL_IDEAL_NATIVE_OFF_RESULT_r1.json',report)
 print(json.dumps({'status':status,'run_key':s['run_key']}))
if __name__=='__main__':main()
