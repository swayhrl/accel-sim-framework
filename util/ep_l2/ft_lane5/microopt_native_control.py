"""One necessary new-binary all-OFF canary using the existing72-start control."""
import json
from pathlib import Path
from registry import Registry,PARALLEL,write_json,run_key
from run import require,digest,asset_manifest,content_hash
from qualify_native_off import BASELINE,ENV
from independent_microopt import audit,IDENTITY,CORE,FW,PUB
import local_ideal_native_control as controller

OUT=controller.OUT
CHECK=OUT/'MICROOPT_F0AF_NATIVE_OFF_CHECKPOINT_r1.json'
INDEPENDENT=OUT/'independent_mq2_runtime_r3/RECEIPT.json'

def prepare():
 h,p,off=audit();ind=json.loads(INDEPENDENT.read_text());require(ind['status']=='INDEPENDENT55_NATIVE_6_CONFIG_5_GUARDS_PASS_ELEVEN_REVIEW_PENDING' and ind['source_identity']==IDENTITY,'Independent candidate replay incomplete')
 for row in ind['tests']+ind['constructors']+ind['guards']:require(digest(row['log'])==row['sha256'] and digest(row['command'][0])==row['executable_sha256'],'Independent evidence changed')
 base=json.loads((BASELINE/'run_status.json').read_text());assets=json.loads((BASELINE/'input_assets.json').read_text());paths=[CORE/'configs/tested-cfgs/SM7_QV100/gpgpusim.config',FW/'gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config',FW/'tests/ep_l2/b0_banked_d512_850.config',FW/'tests/ep_l2/m0a_off.config'];configs=[{'name':f'config-{n}.config','path':str(p)} for n,p in enumerate(paths)];cm=asset_manifest(configs,ordered=True);tm=asset_manifest(assets['trace_paths']);require(cm==assets['configs'] and tm==assets['trace'],'Native all-OFF full input/config changed');identity={**base['identity'],**IDENTITY};identity['termination_contract']={**identity['termination_contract'],'timeout_seconds':3600}
 require(identity['runtime_config_sha256']==content_hash({'ordered_configs':cm,'auxiliary_assets':[],'environment':ENV}) and identity['trace_content_sha256']==content_hash(tm),'Native input identity differs')
 checkpoint={'status':'PREDECLARED_NECESSARY_SERVICE_RUNTIME_NATIVE_OFF_CANARY','experiment_id':PARALLEL,'identity':identity,'run_key':run_key(identity),'official_release':PUB,'independent55_sha256':digest(INDEPENDENT),'reason':'Preserve eleven gates: new actual binary all-OFF73873cycles/56000000instructions and sevenCSV equality. One necessary qualification fullapp charged to original72; no performance endpoint, no old gate inheritance.','configs':configs,'config_manifest':cm,'traces':assets['trace_paths'],'trace_manifest':tm,'parser':str(FW/'util/ep_l2/parse_epl2_b0.py'),'parser_sha256':digest(FW/'util/ep_l2/parse_epl2_b0.py'),'timeout_seconds':3600}
 if CHECK.exists():require(json.loads(CHECK.read_text())==checkpoint,'Immutable canary selection changed')
 else:write_json(CHECK,checkpoint)
 r=Registry();cell=r.register_native_off_control(identity,{'path':str(CHECK),'sha256':digest(CHECK)},cell_id='E_NATIVE_OFF_SERVICE_F0AF_R1');return h,p,checkpoint,cell,r

if __name__=='__main__':
 controller.prepare=prepare;controller.RESULT_NAME='MICROOPT_F0AF_NATIVE_OFF_RESULT_r1.json';controller.main()
