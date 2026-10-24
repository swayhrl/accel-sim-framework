from pathlib import Path
import json,hashlib,subprocess,tarfile,types,sys,importlib.util,pathlib
D=Path('/root/data/nn_parent_cold_review_20261025_v1');R=D/'base_inner/ada_call_snapshot_nn_20261024_v1'
I=D/'increment_inner/nn_A3_V4_admission_increment_20261024_v1'
source_root='/data/c16/ada_call_snapshot_nn_20261024_v1'
fmap=json.loads((R/'control/EXTERNAL_EVIDENCE_MAP_V1.json').read_text())
exact={x['source']:R/x['package_path']for x in fmap}
spec=json.loads((R/'control/CAPTURE_PAIR_SPEC_A3_V1.json').read_text())
for row in spec['inputs']:exact[row['source']]=R/'attempts/pair_A3_v1/observer'/row['relative']
realpath=pathlib.Path
def mapped(*args,**kwargs):
 p=realpath(*args,**kwargs);s=str(p)
 if s in exact:return exact[s]
 if s==source_root or s.startswith(source_root+'/'):return R/p.relative_to(source_root)
 return p
proxy=types.ModuleType('pathlib')
for k,v in vars(pathlib).items():setattr(proxy,k,v)
proxy.Path=mapped
sys.modules['pathlib']=proxy
try:
 p=I/'verify_nn_pair_full_bytes_v4.py';sp=importlib.util.spec_from_file_location('native_nn_full',p);v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v)
 results=[v.verify(x)for x in ['observer','trace']]
 assert results[0]['input_capsule_sha256']==results[1]['input_capsule_sha256']
 assert results[0]['output_capsule_sha256']==results[1]['output_capsule_sha256']
finally:sys.modules['pathlib']=pathlib
expected=json.loads((I/'NN_PAIR_FULL_BYTE_MEMORY_JOIN_A3_V4.json').read_text())
for got,old in zip(results,expected['modes']):
 for k in old:
  if k not in ['CPU_libm_sha256','CPU_libm_path']:assert got[k]==old[k],k
out={'schema':'NN_A3_NATIVE_COLD_CPU_JOIN_V4','status':'UNMODIFIED_FROZEN_VERIFIER_FILE_LOOKUP_REMAP_PASS_NO_GPU_NO_SIM','tar_sha256':hashlib.sha256(Path('/root/data/nn_parent_cold_review_20261025_v1/base_outer/174new/ada_nn_observed_io_engineering_pack_20261024_v1/NN_A3_COMPLETE_CODE_RAW_CONTROL_V1.tar.gz').read_bytes()).hexdigest(),'frozen_verifier_sha256':hashlib.sha256((I/'verify_nn_pair_full_bytes_v4.py').read_bytes()).hexdigest(),'all_original_logical_fields_equal':True,'path_remap_scope':'Only filesystem Path construction for copied109 root/external map/oldnative exact5inputs; immutable source bytes and original journal field values unchanged','CPU_libm_native_sha256':results[0]['CPU_libm_sha256'],'CPU_libm109_sha256':expected['modes'][0]['CPU_libm_sha256'],'full42764_outputs_bitwise_equal_again':True,'input_and_output_pair_MATCH':True,'results':results,'new_SIM_attempts':0,'formal_bulk_admission':False}
with(D/'NATIVE_COLD_FULL_BYTE_JOIN_A3_V4.json').open('x')as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in out.items()if k!='results'}))
