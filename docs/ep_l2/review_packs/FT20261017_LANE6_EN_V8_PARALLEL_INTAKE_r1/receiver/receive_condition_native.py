"""One explicit new-directory r19 native intake event; never polls or launches."""
import argparse,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--adapter',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args()
R=args.repo.resolve();HERE=Path(__file__).resolve().parent;P=args.output_dir.resolve();assert not P.exists();P.mkdir(parents=True)
s=importlib.util.spec_from_file_location('r19_native_engine',HERE/'native_engine_r19.py');e=importlib.util.module_from_spec(s);s.loader.exec_module(e);e.R=R;e.P=P
try:
 adapter=json.loads(args.adapter.read_text());assert adapter.get('experiment_id')=='EPL2_DOWNSTREAM_HEADROOM_R19' and adapter.get('regime') in ('Q4','D4','D2','L25')
 e.write('NATIVE_ADAPTER_SAD.json',adapter);e.write('native_pair_intake_r19.py',(HERE/'native_pair_intake_r19.py').read_bytes());e.receive()
 packet=json.loads((P/'SAD_NATIVE_INTAKE.json').read_text());assert len(packet['packet']['runs'])==2
 # Full body/atomic proof and producing parser/64-slice replay remain in the frozen engine.
 from scope_binding import bind_scope, find_anchor
 from regime_rules import verify_appended_contract
 scope_evidence=[]
 qraw=e.git('show',adapter['qualification_publication']+':'+adapter['qualification_path']);q=json.loads(qraw);adapter['_current_pub']=packet['current_authority']['publication_commit']
 for run in packet['packet']['runs']:
  base,anchor_path=find_anchor(R,run['workload'],run['mode'],e.git)
  scope_evidence.append(bind_scope(R,adapter,q,run,base,anchor_path,e.git))
  verify_appended_contract(base,run,adapter['regime'],run['original_result']['allocation']['result_directory'])
 e.write('INPUT_SCOPE_BINDING.json',scope_evidence)
 assert e.live_reader()(R)==packet['current_authority']['publication_commit']
 sidecars={n:e.sha((P/n).read_bytes()) for n in ['SAD_64_SLICE_EVIDENCE.json','SAD_IDENTITY_AND_CLOSURE.json','SAD_RAW_METRICS.json']}
 e.write('R19_NATIVE_RECEIPT.json',{'status':'PASS_COMPLETE_R19_NATIVE_CONDITION_INTAKE','authority':packet['current_authority'],'experiment_id':adapter['experiment_id'],'regime':adapter['regime'],'workload':packet['packet']['runs'][0]['workload'],'run_keys':[r['run_key'] for r in packet['packet']['runs']],'native_packet_sha256':e.sha((P/'SAD_NATIVE_INTAKE.json').read_bytes()),'native_sidecar_sha256':sidecars,'native_clock_config_body_64slice_checks':True,'input_scope_binding_sha256':e.sha((P/'INPUT_SCOPE_BINDING.json').read_bytes()),'new_simulators':0})
except BaseException as error:
 e.write('FAILURE.json',{'status':'FAIL_CLOSED','type':type(error).__name__,'reason':str(error)});raise
