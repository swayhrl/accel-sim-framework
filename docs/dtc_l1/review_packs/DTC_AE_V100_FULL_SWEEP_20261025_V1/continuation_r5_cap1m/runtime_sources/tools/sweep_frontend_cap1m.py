import pathlib,json,sys,importlib.util
T=pathlib.Path('/root/data/dtc_main_v100_sweep_20261025_v1');PRIOR=pathlib.Path('/root/data/dtc_main_short3_20261024_v1/tools/short3_frontend_floor5_v3.py')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main(argv):
 if len(argv)>=3 and argv[2] in load('sweep_native_matrix',T/'tools/sweep_native_cap1m.py').COHORTS:
  if '--project' in argv and argv[argv.index('--project')+1]!='DTC_L1':raise RuntimeError('project/request mismatch')
  if argv[0]=='experiment':
   m=load('sweep_exact_native',T/'tools/sweep_native_cap1m.py')
   if argv[1] in ['prepare','inspect']:return m.prepare(argv[2])
   if argv[1]=='run-native':return m.finish_cell(argv[2])
  if argv[:2]==['result','archive']:return load('sweep_closed_outbox',T/'tools/sweep_outbox.py').archive(argv[2])
  raise RuntimeError('unsupported exact sweep operation')
 return load('prior_science_routes_preserved',PRIOR).main(argv)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),indent=2))
 except (RuntimeError,OSError,ValueError,KeyError,AssertionError) as e:print(json.dumps({'status':'HOLD','reason':str(e),'model_retry':False}),file=sys.stderr);sys.exit(2)
