"""New two-case memory validation route; frozen old/current routes fall through."""
import pathlib,json,hashlib,importlib.util,sys
P=pathlib.Path;R=P('/root/data/dtc_failure_repair_20261025_v1/validation_lava_memory_v2');R1=P('/root/data/dtc_failure_repair_20261025_v1/validation')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main(argv):
 if len(argv)>=3 and argv[2].startswith('E2-AEREPAIR-LAVAMEM2-'):
  if argv[0]=='experiment':
   assert '--project' in argv and argv[argv.index('--project')+1]=='DTC_L1'
   engine=load('lavamem_native_route',R/'tools/lavamem_native_v2.py')
   if argv[1] in ['prepare','inspect']:return engine.prepare(argv[2])
   if argv[1]=='run-native':return engine.run_native(argv[2])
  if argv[0]=='result' and argv[1]=='archive':return load('lavamem_archive_route',R/'tools/lavamem_outbox_v2.py').archive(argv[2])
  raise ValueError('unsupported new memory-validation operation')
 fallback=R1/'tools/repair_frontend_v1.py';assert hashlib.sha256(fallback.read_bytes()).hexdigest()=='91a26f8b91116cb5e1d1570835a2ec5a8cd967de1b88551bdba6784e288dfd45'
 return load('frozen_old_and_original_routes',fallback).main(argv)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),indent=2))
 except (RuntimeError,OSError,ValueError,KeyError,AssertionError) as error:print(json.dumps({'status':'HOLD','reason':str(error),'error_type':type(error).__name__,'errno':getattr(error,'errno',None),'model_retry':False}),file=sys.stderr);sys.exit(2)
