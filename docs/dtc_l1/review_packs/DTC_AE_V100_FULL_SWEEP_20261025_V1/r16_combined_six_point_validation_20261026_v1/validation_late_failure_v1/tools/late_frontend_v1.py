"""New two-case memory validation route; frozen old/current routes fall through."""
import pathlib,json,hashlib,importlib.util,sys
P=pathlib.Path;R=P('/root/data/dtc_failure_repair_20261025_v1/validation_late_failure_v1');R1=P('/root/data/dtc_failure_repair_20261025_v1/validation')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main(argv):
 if len(argv)>=3 and argv[2].startswith('E2-AEREPAIR-LATE4-'):
  if argv[0]=='experiment':
   assert '--project' in argv and argv[argv.index('--project')+1]=='DTC_L1'
   engine=load('lavamem_native_route',R/'tools/late_native_v1.py')
   if argv[1] in ['prepare','inspect']:return engine.prepare(argv[2])
   if argv[1]=='run-native':return engine.run_native(argv[2])
  if argv[0]=='result' and argv[1]=='archive':return load('lavamem_archive_route',R/'tools/late_outbox_v1.py').archive(argv[2])
  raise ValueError('unsupported new memory-validation operation')
 fallback=P('/root/data/dtc_failure_repair_20261025_v1/validation_lava_memory_v2/tools/lavamem_frontend_v2.py');assert hashlib.sha256(fallback.read_bytes()).hexdigest()=='52e63e993240b22d63b63889715e7ba5a11d23d730e338b28116e7e2ca731ddf'
 return load('frozen_old_and_original_routes',fallback).main(argv)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),indent=2))
 except (RuntimeError,OSError,ValueError,KeyError,AssertionError) as error:print(json.dumps({'status':'HOLD','reason':str(error),'error_type':type(error).__name__,'errno':getattr(error,'errno',None),'model_retry':False}),file=sys.stderr);sys.exit(2)
