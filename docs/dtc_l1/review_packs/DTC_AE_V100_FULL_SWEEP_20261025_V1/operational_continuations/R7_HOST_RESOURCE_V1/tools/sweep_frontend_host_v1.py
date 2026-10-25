"""Explicit epoch2 host-only adapter route; all other routes remain preserved."""
import pathlib,sys,json,importlib.util
T=pathlib.Path('/root/data/dtc_main_v100_sweep_20261025_v1')
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main(argv):
 native=load('unchanged_native_with_host_adapter','sweep_native_cap1m.py')
 if len(argv)>=3 and argv[2] in native.COHORTS and argv[0]=='experiment':
  assert '--project' in argv and argv[argv.index('--project')+1]=='DTC_L1'
  native=load('explicit_host_adapter','sweep_host_execution_v1.py').install(native)
  if argv[1] in ['prepare','inspect']:return native.prepare(argv[2])
  if argv[1]=='run-native':return native.finish_cell(argv[2])
 return load('unchanged_other_epoch2_routes','sweep_frontend_cap1m.py').main(argv)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),indent=2))
 except (RuntimeError,OSError,ValueError,KeyError,AssertionError) as e:print(json.dumps({'status':'HOLD','reason':repr(e),'model_retry':False}),file=sys.stderr);sys.exit(2)
