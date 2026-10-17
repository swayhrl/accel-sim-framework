"""Reuse existing native OFF runner, positive-bind official unifiedfb and separate extra cell."""
import json,subprocess
from pathlib import Path
from registry import Registry,PARALLEL,run_key,write_json
from run import digest,require,asset_manifest,content_hash
from qualify_native_off import BASELINE,ENV
import local_ideal_native_control as controller

OUT=controller.OUT
CHECK=OUT/'UNIFIED_FB_NATIVE_OFF_CHECKPOINT_r1.json'


def prepare_unified():
 hand=json.loads(Path('/workspace/ep_l2_ft20261016_shared/lane1/PARALLEL_ALL_DATA_RELEASE_r1.json').read_text());prod=json.loads(Path(hand['producer_receipt_path']).read_text());ind=json.loads((OUT/'independent_unified_fb_runtime_r1/RECEIPT.json').read_text());guards=json.loads((OUT/'unified_constructors_and_guards_r1/RECEIPT.json').read_text())
 require(ind['status']=='AFFECTED_NEW_RUNTIME_ASSERTIONS_PASS_ELEVEN_AND_MODE_REVIEW_PENDING' and len(ind['tests'])==49 and ind['source_identity']['binary_sha256']==hand['binary_sha256'],'Exact new49 assertions missing')
 require(guards['status']=='11_ACTUAL_CONSTRUCTORS_5_EXPECTED_NATIVE_REJECTIONS_PASS_NOT_FULL_QUALIFICATION','Exact new constructors/guards incomplete')
 for row in ind['tests']:require(row['exit_code']==0 and row['status']=='ACTUAL_ASSERTIONS_PASS' and digest(row['log'])==row['sha256'],'Independent evidence changed')
 for row in guards['positive']+guards['expected_rejections']:require(digest(row['log'])==row['sha256'],'Actual constructors/guards changed')
 require(digest(hand['binary'])==hand['binary_sha256']=='fb67448d08818bc8cbe72961580e8340f0e6f337a4df95e7c8ee9468472953f7','Changed official unified runtime')
 require(Path(hand['producer_receipt_path']).read_bytes()==subprocess.check_output(['git','show',hand['publication']+':'+hand['producer_receipt_repository_path']]),'Unpublished producer receipt')
 baseline=json.loads((BASELINE/'run_status.json').read_text());assets=json.loads((BASELINE/'input_assets.json').read_text());core=Path(hand['actual_build_core']);fw=Path(hand['actual_build_framework']);paths=[core/'configs/tested-cfgs/SM7_QV100/gpgpusim.config',fw/'gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config',fw/'tests/ep_l2/b0_banked_d512_850.config',fw/'tests/ep_l2/m0a_off.config'];configs=[{'name':f'config-{n}.config','path':str(p)} for n,p in enumerate(paths)];cm=asset_manifest(configs,ordered=True);tm=asset_manifest(assets['trace_paths']);require(cm==assets['configs'] and tm==assets['trace'],'Native full input/config differs')
 identity={**baseline['identity'],**{k:hand[k] for k in ['core_source_commit','framework_source_commit','binary_sha256']}};identity['termination_contract']={**identity['termination_contract'],'timeout_seconds':3600}
 require(identity['runtime_config_sha256']==content_hash({'ordered_configs':cm,'auxiliary_assets':[],'environment':ENV}) and identity['trace_content_sha256']==content_hash(tm),'Native identity formula differs')
 checkpoint={'status':'PREDECLARED_NECESSARY_NEW_UNIFIED_RUNTIME_NATIVE_OFF_CANARY','experiment_id':PARALLEL,'identity':identity,'run_key':run_key(identity),'official_release':hand['publication'],'independent49_sha256':digest(OUT/'independent_unified_fb_runtime_r1/RECEIPT.json'),'actual_constructors_guards_sha256':digest(OUT/'unified_constructors_and_guards_r1/RECEIPT.json'),'reason':'Necessary new-binary allOFF73873cycles/56000000instructions plus sevenCSV exact regression; not a performance endpoint or inherited qualification','configs':configs,'config_manifest':cm,'traces':assets['trace_paths'],'trace_manifest':tm,'parser':str(fw/'util/ep_l2/parse_epl2_b0.py'),'parser_sha256':digest(fw/'util/ep_l2/parse_epl2_b0.py'),'timeout_seconds':3600}
 if CHECK.exists():require(json.loads(CHECK.read_text())==checkpoint,'Native canary checkpoint immutable')
 else:write_json(CHECK,checkpoint)
 registry=Registry();cell=registry.register_native_off_control(identity,{'path':str(CHECK),'sha256':digest(CHECK)},cell_id='E_NATIVE_OFF_UNIFIED_FB_R1')
 return hand,prod,checkpoint,cell,registry

if __name__=='__main__':
 controller.prepare=prepare_unified
 controller.RESULT_NAME='UNIFIED_FB_NATIVE_OFF_RESULT_r1.json'
 controller.main()
