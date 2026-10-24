import pathlib,sys,json,importlib.util
N=pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2')
T=pathlib.Path('/root/data/dtc_main_20261023_v1/ae_fair_v1')
sys.path.insert(0,str(N/'tools'))
import native_v2
def main(argv):
 if len(argv)>=3 and argv[0]=='experiment' and argv[2] in ['E2-AEFAIR-CM','E2-AEFAIR-CH','E2-AEFAIR-DM','E2-AEFAIR-DH']:
  if '--project' in argv and argv[argv.index('--project')+1]!='DTC_L1':raise RuntimeError('project/request mismatch')
  s=importlib.util.spec_from_file_location('exact_aefair_native',T/'tools/aefair_native.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
  if argv[1] in ['inspect','prepare']:return m.prepare(argv[2])
  if argv[1]=='run-native':return m.finish_cell(argv[2])
  raise RuntimeError('unknown exact AE fairness operation')
 if len(argv)>=3 and argv[0]=='result' and argv[2] in ['E2-AEFAIR-CM','E2-AEFAIR-CH','E2-AEFAIR-DM','E2-AEFAIR-DH']:
  if argv[1]!='archive':raise RuntimeError('use exact bundled restore command for this new result')
  s=importlib.util.spec_from_file_location('exact_aefair_result',T/'tools/aefair_result_gate_v2.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
  return m.archive(argv[2])
 # Preserve the existing EP-MAIN exact router byte-for-byte as fallback.
 sys.path.insert(0,'/root/data/ep_l2_main_vector_r5_20261023_v1')
 import native_dispatch_post_v1 as prior_epoch2_dispatch
 result=prior_epoch2_dispatch.main(argv)
 if argv[:2]==['project','status']:
  result['registered_science_requests']=native_v2.read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']
 return result
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),indent=2))
 except (RuntimeError,KeyError,OSError,ValueError) as e:print(json.dumps({'status':'HOLD','reason':str(e),'retry':False}),file=sys.stderr);sys.exit(2)
