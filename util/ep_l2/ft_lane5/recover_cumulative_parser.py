"""Audit reparse of exact exit0 cumulative-snapshot parser failures; never re-simulate."""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path
from registry import Registry,canonical,write_json,live_result_output,ACTIVE
from run import digest,inspect,require,validate_summary,tree_bytes
from package_r0 import freeze_checksums

REPO=Path(__file__).resolve().parents[3]
OUT=Path('/workspace/ep_l2_potential20261017_lane5_results')
FIX=REPO/'docs/ep_l2/review_packs/FT20261017_LANE5_CUMULATIVE_TERMINAL_READER_FIX_r1'
KEYS={'I_WB':'f9bc3c47f553f763a5c8f9a466636194d8d49584d65bcb1367a3458fcb46f184','I_META':'8385d47bbab46eea3e173d71e02cd97475d7535028d8994bf14c60c0a97d3a4a'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--profile',choices=KEYS,required=True);a=ap.parse_args();key=KEYS[a.profile];r=Registry();old=r.snapshot()['runs'][key]
 require(old['status']=='FAILED' and old['exit_code']==0 and old['detail']=='InvalidEvidence: production terminal parser failed','Not exact native-success/parser failure')
 source=Path(old['result_directory']);require('duplicate ideal application slice' in (source/'parser.log').read_text(),'Wrong parser failure class');native=json.loads((source/'run_status.json').read_text());spec=json.loads((source/'input_spec.json').read_text());require(spec['profile']==a.profile and spec['identity']['binary_sha256']=='37dc77943e7667327069faa203139b089bcb88c7d38e6347602928e3ba6cd0b5','Wrong current audited source/mode');require(digest(source/'raw.log')==old['raw_log_sha256']==native['raw_log_sha256'],'Raw input changed')
 corrected=json.loads((REPO/'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/parallel_local_ideal_specs_execution_r3'/('I012_vectorAdd_4M_I_WB.json' if a.profile=='I_WB' else 'I013_vectorAdd_4M_I_META.json')).read_text());require({k:v for k,v in corrected.items() if k!='parser'}=={k:v for k,v in spec.items() if k!='parser'},'Correction changed more than independent parser metadata');directory=OUT/(key+'_validation_r2');require(not directory.exists(),'Preserve validation revision');pack=REPO/'docs/ep_l2/review_packs'/('FT20261017_LANE5_LOCAL_'+a.profile+'_CUMULATIVE_REVALIDATION_r1');require(not pack.exists(),'Preserve repair proof revision')
 with r.locked() as data:
  live=live_result_output(directory);growth=tree_bytes(source)+16*2**20;pending=sum(max(0,v.get('output_budget',{}).get('predicted_growth_bytes',2*2**30)-tree_bytes(Path(v['result_directory']))) for v in data['runs'].values() if v['status'] in ACTIVE);policy=data['hosts'][old['host']];require(live['actual_bytes']+pending+growth<policy['max_result_bytes'] and live['resources']['disk_free_bytes']-growth>policy['min_disk_free_bytes'],'Revalidation copy exceeds remaining authorized output/floor')
 lease=r.build_lease('lane5',cpu=1,memory=2*2**30)
 try:
  audit=inspect(corrected);audit['qualification_evidence']=sorted(audit['qualification_evidence'],key=lambda x:x['gate']);previous={**native['audit'],'qualification_evidence':sorted(native['audit']['qualification_evidence'],key=lambda x:x['gate'])};require(audit==previous,'Original input/qualification/current exact target changed');audit['qualification_evidence']=native['audit']['qualification_evidence'];directory.mkdir();write_json(directory/'input_spec.json',corrected);write_json(directory/'input_audit.json',audit)
  for name in ['raw.log','accel-sim.out']+[v['name'] for v in audit['configs']+audit['auxiliary_assets']]:shutil.copy2(source/name,directory/name)
  with (directory/'parser.log').open('xb') as stream:done=subprocess.run([sys.executable,corrected['parser']['path'],'--raw',str(directory/'raw.log'),'--out',str(directory/'terminal_summary.json')],cwd=directory,stdout=stream,stderr=subprocess.STDOUT,timeout=120)
  require(done.returncode==0,'Corrected cumulative parser failed');summary=json.loads((directory/'terminal_summary.json').read_text());validation=validate_summary(summary,corrected['identity']);require(summary['instructions']==56000000,'Full native vector input count changed');after=inspect(corrected);after['qualification_evidence']=native['audit']['qualification_evidence'];require(after==audit and digest(directory/'raw.log')==old['raw_log_sha256'],'Evidence changed during reparse')
  native.update(status='COMPLETE_VALID',detail='AUDITED_POSTPROCESSING_ONLY_REVALIDATION',summary=summary,validation=validation,audit=audit,postprocessing_only=True,original_runtime_result_directory=str(source),parser_recovery_pack=str(FIX));native['allocation']={**native['allocation'],'result_directory':str(directory)};write_json(directory/'run_status.json',native);pack.mkdir();proof={'status':'COMPLETE_VALID','run_key':key,'identity':old['identity'],'old_terminal_sha256':hashlib.sha256(canonical(old)).hexdigest(),'old_terminal':old,'raw_log_sha256':old['raw_log_sha256'],'new_result_directory':str(directory),'new_simulator_starts':0,'compiler_started':False,'corrected_parser':corrected['parser'],'original_failed_result_directory':str(source),'native_cycles':summary['cycles'],'native_instructions':summary['instructions'],'charged_extra_payload_slots':summary['diagnostic_payload_extra_slots'],'validation':validation};write_json(pack/'RECEIPT.json',proof);shutil.copyfile(source/'parser.log',pack/'ORIGINAL_PARSER_FAILURE.log');write_json(pack/'CORRECTED_SPEC.json',corrected);freeze_checksums(pack);r.revalidate_postprocessing(key,old['lease_id'],{'path':str(pack/'RECEIPT.json'),'sha256':digest(pack/'RECEIPT.json')})
 finally:r.release_build(lease,'lane5')
 print(json.dumps({'status':'CUMULATIVE_PARSER_ONLY_REVALIDATION_NO_NEW_SIM','profile':a.profile,'cycles':summary['cycles'],'instructions':summary['instructions'],'extra_payload_slots':summary['diagnostic_payload_extra_slots']}))
if __name__=='__main__':main()
