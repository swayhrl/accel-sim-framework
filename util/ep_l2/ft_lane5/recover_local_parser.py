"""Reparse an unchanged exit0 full app; preserve failed revision, never rerun it."""
import json,shutil,sys,subprocess,hashlib
from pathlib import Path
from registry import Registry,write_json,canonical
from run import digest,inspect,require,validate_summary
from package_r0 import freeze_checksums

REPO=Path(__file__).resolve().parents[3]
OUT=Path('/workspace/ep_l2_potential20261017_lane5_results')
KEY='b6dbf02f3fd4aa092573cf06753021c94162156f05905d8c5814e19537c8aadc'


def main():
 r=Registry();old=r.snapshot()['runs'][KEY];require(old['status']=='FAILED' and old['exit_code']==0 and old['detail']=='InvalidEvidence: production terminal parser failed','Not the exact native-success/parser-only failure')
 source=Path(old['result_directory']);require('ModuleNotFoundError: No module named' in (source/'parser.log').read_text(),'Wrong parser failure');result=json.loads((source/'run_status.json').read_text());require(digest(source/'raw.log')==old['raw_log_sha256']==result['raw_log_sha256'],'Raw runtime changed')
 pack=REPO/'docs/ep_l2/review_packs/FT20261017_LANE5_LOCAL_PARSER_DEPENDENCY_RECOVERY_r1';require(not pack.exists(),'Keep old parser recovery revision');pack.mkdir();deps=pack/'deps';deps.mkdir()
 # These exact published modules import only; there is still one registry data file/lock.
 bindings=[]
 for name,commit in [('registry.py','cba946bfa1c49562da201f991ddef6a11ac883b9'),('headroom_config.py','11796e9f7152ea4b22374d6169c4c6703b28847c')]:
  raw=subprocess.check_output(['git','show',commit+':util/ep_l2/ft_lane5/'+name],cwd=REPO);(deps/name).write_bytes(raw);bindings.append({'name':name,'source_commit':commit,'sha256':digest(deps/name)})
 original=json.loads((source/'input_spec.json').read_text());wrapper=pack/'parse_with_frozen_dependencies.py';wrapper.write_text('import sys,runpy,json,argparse\nfrom pathlib import Path\nsys.path.insert(0,'+repr(str(deps))+')\noriginal=runpy.run_path('+repr(original['parser']['path'])+')\nparse=original["parse"]\nif __name__=="__main__":\n p=argparse.ArgumentParser();p.add_argument("--raw",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args();s=json.loads(Path("input_spec.json").read_text());a.out.write_text(json.dumps(parse(a.raw,s),indent=2)+"\\n")\n')
 spec={**original,'parser':{'path':str(wrapper),'sha256':digest(wrapper)}};directory=OUT/(KEY+'_validation_r2');require(not directory.exists(),'Preserve old validation revision');directory.mkdir();lease=r.build_lease('lane5',cpu=1,memory=2*2**30)
 try:
  audit=inspect(spec);fresh={(v['gate'],v['sha256']) for v in audit['qualification_evidence']};previous=result['audit']['qualification_evidence'];require(fresh=={(v['gate'],v['sha256']) for v in previous},'Gates changed');audit['qualification_evidence']=previous;require(audit==result['audit'],'Native inputs/qualification/current target authorization changed')
  write_json(directory/'input_spec.json',spec);write_json(directory/'input_audit.json',audit)
  for name in ['raw.log','accel-sim.out']+[v['name'] for v in audit['configs']+audit['auxiliary_assets']]:shutil.copy2(source/name,directory/name)
  with (directory/'parser.log').open('xb') as f:done=subprocess.run([sys.executable,str(wrapper),'--raw',str(directory/'raw.log'),'--out',str(directory/'terminal_summary.json')],cwd=directory,stdout=f,stderr=subprocess.STDOUT,timeout=120)
  require(done.returncode==0,'Frozen dependency parser failed');summary=json.loads((directory/'terminal_summary.json').read_text());validation=validate_summary(summary,spec['identity']);require(summary['instructions']==56000000,'Complete original vector input changed')
  after=inspect(spec);after['qualification_evidence']=previous;require(after==audit and digest(directory/'raw.log')==old['raw_log_sha256'],'Postprocessing evidence changed')
  result.update(status='COMPLETE_VALID',detail='AUDITED_POSTPROCESSING_ONLY_REVALIDATION',summary=summary,validation=validation,audit=audit,postprocessing_only=True,original_runtime_result_directory=str(source),parser_recovery_pack=str(pack));result['allocation']={**result['allocation'],'result_directory':str(directory)};write_json(directory/'run_status.json',result)
  proof={'status':'COMPLETE_VALID','run_key':KEY,'identity':old['identity'],'old_terminal_sha256':hashlib.sha256(canonical(old)).hexdigest(),'old_terminal':old,'raw_log_sha256':old['raw_log_sha256'],'new_result_directory':str(directory),'new_simulator_starts':0,'compiler_started':False,'original_failed_result_directory':str(source),'corrected_parser':spec['parser'],'frozen_dependency_bindings':bindings,'validation':validation,'cycles':summary['cycles'],'instructions':summary['instructions']};write_json(pack/'RECEIPT.json',proof);shutil.copyfile(source/'parser.log',pack/'ORIGINAL_PARSER_FAILURE.log');write_json(pack/'CORRECTED_SPEC.json',spec);freeze_checksums(pack)
  r.revalidate_postprocessing(KEY,old['lease_id'],{'path':str(pack/'RECEIPT.json'),'sha256':digest(pack/'RECEIPT.json')})
 finally:r.release_build(lease,'lane5')
 print(json.dumps({'status':'PARSER_ONLY_RECOVERY_COMPLETE_NO_NEW_SIM','cycles':summary['cycles'],'instructions':summary['instructions'],'same_key':KEY}))
if __name__=='__main__':main()
