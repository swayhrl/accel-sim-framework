"""Root-run final explicit authorization, not invoked by the candidate daemon."""
import argparse,json,pathlib,sys
sys.dont_write_bytecode=True
import ready_emitter as e
import background_analysis as b
p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--publication-receipt',required=True);p.add_argument('--adopt-existing-namespace',action='store_true');p.add_argument('--authorize-ready-namespace',action='store_true',required=True);a=p.parse_args();cp=pathlib.Path(a.config);cfg=e.read(cp)
assert cfg['publication_receipt_path']==str(pathlib.Path(a.publication_receipt).resolve()),'SET_FINAL_CONFIG_RECEIPT_PATH_FIRST'
mod=b.load(cfg['consumer_path'],cfg['consumer_sha256']);mod.publication_gate(a.publication_receipt,cfg['qualification_path'])
D=pathlib.Path(__file__).parent;qa=e.read(D/'CPU_QUALIFICATION.json');assert qa['status']=='PASS'
for n,h in qa['source_sha256'].items():assert e.sha(D/n)==h,'CPU_QA_SOURCE_CHANGED '+n
for p,h in cfg['source_pins'].items():assert e.sha(p)==h
ready=pathlib.Path(cfg['analysis_ready_path']);raw=ready.read_bytes();v=json.loads(raw)
assert (not e.owned(v)['files'] and e.STATUS not in v) or a.adopt_existing_namespace,'STOP_PREVIOUS_DAEMON_AND_EXPLICITLY_ADOPT_FROZEN_NAMESPACE'
import analysis_extensions as ext
ext.policy(cfg)
if cfg.get('historical_provider'):ext.historical(cfg)
assert v['schema']=='MAIN_APPROVED_ANALYSIS_PUBLICATION_V1' and v['status']=='MAIN_APPROVED_FOR_PUBLICATION'
auth={'schema':'DTC_AUTO_ANALYSIS_READY_AUTHORIZATION_V1','authorized':True,'namespace':e.PREFIX,'ready_path':str(ready),'ready_lock_path':str(ready.with_suffix('.auto_analysis.lock')),'daemon_sha256':e.sha(D/'background_analysis.py'),'config_sha256':e.sha(cp),'emitter_sha256':e.sha(D/'ready_emitter.py'),'publication_receipt_path':str(pathlib.Path(a.publication_receipt).resolve()),'publication_receipt_sha256':e.sha(a.publication_receipt),'output_root':cfg['output_root'],'initial_owned':e.owned(v),'base_ready_sha256':e.digest(raw),'base_projection_sha256':e.digest(e.encode(e.projection(v))),'root_only_preparation':True,'authorization_scope':'ONLY_NAMESPACE_AUTO_DERIVED35_V1;NATURAL_STRICT_REFRESH_AND_CLOSED_STATUS;NO_ROLE_BUDGET_TRIAL_OR_CONTROLLER_CHANGES','publisher_source_unchanged':True,'payload_max_bytes':1048576}
assert ready.read_bytes()==raw,'READY_CHANGED_DURING_ROOT_PREPARE'
p=pathlib.Path(cfg['ready_authorization_path']);assert not p.exists(),'AUTH_ALREADY_EXISTS_DO_NOT_REWRITE';e.atomic(p,auth);print(json.dumps({'authorization':str(p),'sha256':e.sha(p),'base_READY_sha256':auth['base_ready_sha256'],'daemon_sha256':auth['daemon_sha256'],'config_sha256':auth['config_sha256']}))
