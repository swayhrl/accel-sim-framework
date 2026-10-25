"""Exact repair route through the same174-new epoch2 native entry."""
import pathlib,json,importlib.util,sys
P=pathlib.Path;R=P('/root/data/dtc_failure_repair_20261025_v1/validation');T=P('/root/data/dtc_main_v100_sweep_20261025_v1')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main(argv):
 if len(argv)>=3 and argv[0]=='experiment' and argv[2].startswith('E2-AEREPAIR-'):
  assert '--project' in argv and argv[argv.index('--project')+1]=='DTC_L1';engine=load('repair_native_route',R/'tools/repair_native_v1.py')
  if argv[1] in ['prepare','inspect']:return engine.prepare(argv[2])
  if argv[1]=='run-native':return engine.run_native(argv[2])
  raise ValueError('unsupported repair experiment operation')
 if len(argv)>=3 and argv[0]=='result' and argv[2].startswith('E2-AEREPAIR-'):
  assert argv[1]=='archive';return load('repair_outbox_route',R/'tools/repair_outbox_v1.py').archive(argv[2])
 plan=json.loads((R/'control/EXECUTION_PLAN_V1.json').read_bytes());fallback=P(plan['original_frontend_path']);assert fallback!=P(__file__)
 import hashlib
 assert hashlib.sha256(fallback.read_bytes()).hexdigest()==plan['original_frontend_sha256'];return load('original_scope_preserved_route',fallback).main(argv)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),indent=2))
 except (RuntimeError,OSError,ValueError,KeyError,AssertionError) as error:print(json.dumps({'status':'HOLD','reason':str(error),'error_type':type(error).__name__,'errno':getattr(error,'errno',None),'model_retry':False}),file=sys.stderr);sys.exit(2)
