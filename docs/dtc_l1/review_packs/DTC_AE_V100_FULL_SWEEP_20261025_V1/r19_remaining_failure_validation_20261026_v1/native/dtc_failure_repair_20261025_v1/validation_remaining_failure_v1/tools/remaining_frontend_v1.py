"""New REMAIN4 route, with explicitly pinned real continuation fallback."""
import pathlib,json,hashlib,importlib.util,sys
P=pathlib.Path;R=P('/root/data/dtc_failure_repair_20261025_v1/validation_remaining_failure_v1')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main(argv):
 if len(argv)>=3 and argv[2].startswith('E2-AEREPAIR-REMAIN4-'):
  if argv[0]=='experiment':
   assert '--project' in argv and argv[argv.index('--project')+1]=='DTC_L1';engine=load('remaining_finite_engine',R/'tools/remaining_native_v1.py')
   if argv[1] in ['prepare','inspect']:return engine.prepare(argv[2])
   if argv[1]=='run-native':return engine.run_native(argv[2])
  if argv[0]=='result' and argv[1]=='archive':return load('remaining_finite_archive',R/'tools/remaining_outbox_v1.py').archive(argv[2])
  raise ValueError('unsupported exact remaining4 operation')
 p=json.loads((R/'control/REMAINING_BUILD_PROFILE_V1.json').read_bytes());fallback=P(p['continuation_fallback_frontend_path']);assert fallback.resolve()!=P(__file__).resolve() and hashlib.sha256(fallback.read_bytes()).hexdigest()==p['continuation_fallback_frontend_sha256']
 return load('remaining_actual_continuation_fallback',fallback).main(argv)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),indent=2))
 except (RuntimeError,OSError,ValueError,KeyError,AssertionError) as error:print(json.dumps({'status':'HOLD','reason':str(error),'error_type':type(error).__name__,'model_retry':False}),file=sys.stderr);sys.exit(2)
