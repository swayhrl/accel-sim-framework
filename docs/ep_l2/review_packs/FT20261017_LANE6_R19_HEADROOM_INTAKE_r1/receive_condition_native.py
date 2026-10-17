"""One explicit new-directory r19 native intake event; never polls or launches."""
import argparse,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--adapter',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args()
R=args.repo.resolve();HERE=Path(__file__).resolve().parent;P=args.output_dir.resolve();assert not P.exists();P.mkdir(parents=True)
s=importlib.util.spec_from_file_location('r19_native_engine',HERE/'native_engine_r19.py');e=importlib.util.module_from_spec(s);s.loader.exec_module(e);e.R=R;e.P=P
try:
 adapter=json.loads(args.adapter.read_text());assert adapter.get('experiment_id')=='EPL2_DOWNSTREAM_HEADROOM_R19' and adapter.get('regime') in ('Q4','D4')
 e.write('NATIVE_ADAPTER_SAD.json',adapter);e.write('native_pair_intake_r19.py',(HERE/'native_pair_intake_r19.py').read_bytes());e.receive()
 packet=json.loads((P/'SAD_NATIVE_INTAKE.json').read_text());assert len(packet['packet']['runs'])==2
 # Full body rehash and scoped atomic proof are inside the reused engine.
 # Bind the unchanged original-byte semantic proof to those exact body hashes.
 raw=e.git('show',packet['current_authority']['publication_commit']+':docs/ep_l2/review_packs/FT20261017_LANE5_R17_NATIVE_BYTE_SEMANTIC_PROOF_r1/NATIVE_LEGACY_BYTE_SEMANTIC_PROOF_R17_r1.json')
 assert e.sha(raw)=='9b62884190b8f6bd77d3b3bf873d0e3e60ce718db9e7c51a9797ec99bd46dce2'
 proof=json.loads(raw);assert proof['status']=='PASS_FULL_NATIVE_BYTE_AND_ZERO_MASK_SEMANTIC_PROOF'
 from regime_rules import verify_appended_contract
 H0=HERE.with_name('FT20261017_LANE6_R18_FIVE_PAIR_EN_V6_r1')
 for run in packet['packet']['runs']:
  workload=run['workload'];assert workload in ('convolutionSeparable','FWT_7_21')
  matches=[w for w in proof['workloads'] if w['workload']==workload];assert len(matches)==1
  assert all(run['identity'][k]==v for k,v in proof['source_identity'].items())
  audit=run['original_result']['audit'];entry=run['original_spec']['entry_trace_name']
  assert sorted([{k:f[k] for k in ('name','bytes','sha256')} for f in matches[0]['files']],key=lambda x:x['name'])==[x for x in audit['traces'] if x['name']!=entry]
  anchor_dir=H0/'intakes'/(workload+'_attempt2');anchors=json.loads((anchor_dir/'SAD_NATIVE_INTAKE.json').read_text())['packet']['runs'];base=next(r for r in anchors if r['mode']==run['mode'])
  verify_appended_contract(base,run,adapter['regime'],run['original_result']['allocation']['result_directory'])
 assert e.live_reader()(R)==packet['current_authority']['publication_commit']
 sidecars={n:e.sha((P/n).read_bytes()) for n in ['SAD_64_SLICE_EVIDENCE.json','SAD_IDENTITY_AND_CLOSURE.json','SAD_RAW_METRICS.json']}
 e.write('R19_NATIVE_RECEIPT.json',{'status':'PASS_COMPLETE_R19_NATIVE_CONDITION_INTAKE','authority':packet['current_authority'],'experiment_id':adapter['experiment_id'],'regime':adapter['regime'],'workload':packet['packet']['runs'][0]['workload'],'run_keys':[r['run_key'] for r in packet['packet']['runs']],'native_packet_sha256':e.sha((P/'SAD_NATIVE_INTAKE.json').read_bytes()),'native_sidecar_sha256':sidecars,'native_clock_config_body_64slice_checks':True,'original_byte_semantics_proof_sha256':e.sha(raw),'new_simulators':0})
except BaseException as error:
 e.write('FAILURE.json',{'status':'FAIL_CLOSED','type':type(error).__name__,'reason':str(error)});raise
