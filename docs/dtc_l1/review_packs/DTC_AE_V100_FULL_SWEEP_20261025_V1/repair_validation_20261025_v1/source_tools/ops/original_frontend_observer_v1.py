"""New original-scope frontends add only qualified proc-exit observation handling."""
import pathlib,importlib.util,json,sys
T=pathlib.Path('/root/data/dtc_main_v100_sweep_20261025_v1');O=pathlib.Path('/root/data/dtc_failure_repair_20261025_v1/ops')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main(argv):
 n=load('r13_original_native',T/'tools/sweep_native_cap1m.py')
 if len(argv)>=3 and argv[0]=='experiment' and argv[2] in n.COHORTS:
  host=load('r13_original_host',T/'tools/sweep_host_execution_v4.py');q,p=host.plan(n)
  if argv[2] not in p['preserved_prefix_cells']:
   n=host.install(n);n=load('r13_observer',O/'observer_exit_race_v1.py').install(n)
   if argv[1] in ['prepare','inspect']:return n.prepare(argv[2])
   if argv[1]=='run-native':return n.finish_cell(argv[2])
 return load('r13_preserved_routes',T/'tools/sweep_frontend_host_v4.py').main(argv)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),indent=2))
 except (RuntimeError,OSError,ValueError,KeyError,AssertionError) as e:print(json.dumps({'status':'HOLD','reason':str(e),'error_type':type(e).__name__,'errno':getattr(e,'errno',None),'model_retry':False}),file=sys.stderr);sys.exit(2)
