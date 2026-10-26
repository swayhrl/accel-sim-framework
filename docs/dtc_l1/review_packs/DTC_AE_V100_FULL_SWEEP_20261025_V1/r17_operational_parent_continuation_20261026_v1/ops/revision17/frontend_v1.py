"""Transparent future R17 operational route; pinned old routes fall through."""
import pathlib,json,hashlib,importlib.util,sys
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');D=F/'ops/revision17'
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main(argv):
 if len(argv)>=3 and argv[0]=='experiment' and argv[1] in ['prepare','inspect','run-native'] and (argv[2].startswith('E2-AEREPAIR-LAVAMEM2-') or argv[2].startswith('E2-AEREPAIR-LATE4-')):
  assert '--project' in argv and argv[argv.index('--project')+1]=='DTC_L1';bridge=load('r17_explicit_operational_bridge',D/'operational_parent_bridge_v1.py');request=bridge.LAVA if argv[2].startswith('E2-AEREPAIR-LAVAMEM2-') else bridge.LATE
  return bridge.run_native(request,argv[2]) if argv[1]=='run-native' else bridge.prepare(request,argv[2])
 old=F/'validation_late_failure_v1/tools/late_frontend_v1.py';assert hashlib.sha256(old.read_bytes()).hexdigest()=='c35c873014f6c69351c0fb9fd377be100e6abd409a84279ee68db7d6758a0c74'
 return load('r17_frozen_routes',old).main(argv)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),indent=2))
 except (RuntimeError,OSError,ValueError,KeyError,AssertionError) as error:print(json.dumps({'status':'HOLD','reason':str(error),'error_type':type(error).__name__,'model_retry':False}),file=sys.stderr);sys.exit(2)
