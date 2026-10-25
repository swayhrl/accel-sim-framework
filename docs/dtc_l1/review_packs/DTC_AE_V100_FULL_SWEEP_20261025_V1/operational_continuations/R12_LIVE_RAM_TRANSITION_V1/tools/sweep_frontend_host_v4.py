"""New-only working-set host route; legacy error text stays compatible."""
import pathlib,sys,json,importlib.util
T=pathlib.Path('/root/data/dtc_main_v100_sweep_20261025_v1')
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main(argv):
 n=load('working_set_route_native','sweep_native_cap1m.py')
 if len(argv)>=3 and argv[2] in n.COHORTS and argv[0]=='experiment':
  assert '--project' in argv and argv[argv.index('--project')+1]=='DTC_L1';p=load('fixed4_route_plan','sweep_host_execution_v4.py');q,plan=p.plan(n)
  if argv[2] not in plan['preserved_prefix_cells']:
   n=p.install(n)
   if argv[1] in ['prepare','inspect']:return n.prepare(argv[2])
   if argv[1]=='run-native':return n.finish_cell(argv[2])
 return load('all_earlier_routes_preserved','sweep_frontend_host_v3.py').main(argv)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),indent=2))
 except (RuntimeError,OSError,ValueError,KeyError,AssertionError) as e:print(json.dumps({'status':'HOLD','reason':str(e),'error_type':type(e).__name__,'errno':getattr(e,'errno',None),'model_retry':False}),file=sys.stderr);sys.exit(2)
