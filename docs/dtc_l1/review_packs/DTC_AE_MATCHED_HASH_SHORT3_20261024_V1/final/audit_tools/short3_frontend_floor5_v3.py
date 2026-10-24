import sys,pathlib,json,importlib.util
T=pathlib.Path('/root/data/dtc_main_short3_20261024_v1')
PRIOR=pathlib.Path('/root/data/dtc_main_20261023_v1/ae_fair_v1/tools/native_epoch2_frontend.py')
CELLS={f'E2-AEF3-{w}-{c}' for w in ['NN','DWT2D','MRIQ'] for c in ['DM','DH','CM','CH']}
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
ORIGINAL_ARCHIVED=['E2-AEF3-DWT2D-CH', 'E2-AEF3-DWT2D-CM', 'E2-AEF3-DWT2D-DH', 'E2-AEF3-DWT2D-DM', 'E2-AEF3-MRIQ-DM', 'E2-AEF3-NN-CH', 'E2-AEF3-NN-CM', 'E2-AEF3-NN-DH', 'E2-AEF3-NN-DM']
def main(argv):
 if len(argv)>=3 and argv[2] in CELLS and argv[0] in ['experiment','result']:
  if '--project' in argv and argv[argv.index('--project')+1]!='DTC_L1':raise RuntimeError('project mismatch')
  if argv[0]=='result':
   if argv[2] in ORIGINAL_ARCHIVED:return load('preserved_short3_original_frontend',T/'tools/short3_frontend.py').main(argv)
   if argv[1]!='archive':raise RuntimeError('exact bundled native restore only')
   return load('exact_short3_outbox',T/'tools/short3_result_floor5_v3.py').archive(argv[2])
  m=load('exact_short3_science',T/'tools/short3_native_floor5_v3.py')
  if argv[1] in ['inspect','prepare']:return m.prepare(argv[2])
  if argv[1]=='run-native':return m.finish_cell(argv[2])
  raise RuntimeError('unknown exact short3 operation')
 return load('preserved_prior_epoch2_science',PRIOR).main(argv)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),indent=2))
 except (RuntimeError,OSError,KeyError,ValueError) as e:print(json.dumps({'status':'HOLD','reason':str(e),'retry':False}),file=sys.stderr);sys.exit(2)
