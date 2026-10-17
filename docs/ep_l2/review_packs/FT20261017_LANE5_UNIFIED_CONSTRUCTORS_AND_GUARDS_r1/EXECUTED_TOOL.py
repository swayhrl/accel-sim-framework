"""Execute only new unified producer constructors and expected failures, no app/build."""
import json,os,resource,subprocess,time
from pathlib import Path
from registry import Registry,write_json,process_identity
from run import digest,require,process_tree_rss,terminate_owned,asset_manifest
from independent_headroom_r19 import safe

OUT=Path('/workspace/ep_l2_potential20261017_lane5_results/unified_constructors_and_guards_r1')

def execute(command,log):
 safe()
 with log.open('xb') as stream:
  process=subprocess.Popen(command,cwd=OUT,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1'))
  pid=process_identity(process.pid);started=time.monotonic();peak=0
  try:
   while process.poll() is None:
    safe();peak=max(peak,process_tree_rss(process.pid));require(peak<2*2**30 and time.monotonic()-started<30 and log.stat().st_size<16*2**20,'constructor resource bound');time.sleep(.1)
  finally:
   if process.poll() is None:terminate_owned(process)
 return {'command':command,'process':pid,'exit_code':process.returncode,'log':str(log),'sha256':digest(log),'peak_rss_bytes':peak}

def main():
 require(not OUT.exists(),'Preserve old constructor revision')
 hand=json.loads(Path('/workspace/ep_l2_ft20261016_shared/lane1/PARALLEL_ALL_DATA_RELEASE_r1.json').read_text());manifest=json.loads(Path(hand['producer_manifest_path']).read_text());prod=json.loads(Path(hand['producer_receipt_path']).read_text());supp=json.loads(Path(hand['supplement_receipt_path']).read_text())
 require(digest(hand['binary'])==hand['binary_sha256']=='fb67448d08818bc8cbe72961580e8340f0e6f337a4df95e7c8ee9468472953f7','wrong runtime')
 require(Path(hand['producer_manifest_path']).read_bytes()==subprocess.check_output(['git','show',hand['publication']+':'+hand['producer_manifest_repository_path']]),'unpublished config manifest')
 resource.setrlimit(resource.RLIMIT_CORE,(0,0));r=Registry();safe();lease=r.build_lease('lane5',cpu=1,memory=2*2**30);OUT.mkdir();receipt={'status':'RUNNING_CONSTRUCTORS_ONLY','source_identity':{k:hand[k] for k in ['core_source_commit','framework_source_commit','binary_sha256']},'lease_id':lease,'application_starts':0,'compiler_started':False,'positive':[],'expected_rejections':[]}
 try:
  executable=Path(hand['producer_receipt_path']).parent/'effective_entry/effective_config';require(digest(executable)==prod['effective_entry_sha256'],'constructor executable changed')
  for name,row in manifest['profiles'].items():
   require(asset_manifest(row['configs'],ordered=True)==row['ordered_config_manifest'],'config changed')
   old=row['effective_log'];require(digest(old['log'])==old['log_sha256'],'producer constructor raw changed')
   result=execute([str(executable)]+[v['path'] for v in row['configs']],OUT/(name+'.log'));text=Path(result['log']).read_text();require(result['exit_code']==0 and 'PARALLEL_EFFECTIVE_PASS|' in text,'native constructor failed '+name)
   tokens=('EPL2STRUCTV1|CONFIG|','EPL2B0_FEATURE_VECTOR|','EPL2IDEAL_FEATURE_VECTOR|')
   actual=[v for v in text.splitlines() if v.startswith(tokens)];expected=[v for v in Path(old['log']).read_text().splitlines() if v.startswith(tokens)];require(actual==expected,'native structural/feature getter dump changed '+name)
   if name=='S64':require(any('bypass_capacity=80|wb_begin=1104|static_wb_capacity=64|legacy_wbuf=16' in v for v in actual),'S64 fixed total getter boundary missing')
   receipt['positive'].append({**result,'profile':name,'actual_structural_feature_lines':actual});write_json(OUT/'RECEIPT.json',receipt)
  markers=['EPL2MEMREF_DUPLICATE_ORIGINAL_INSTRUCTION|','EPL2MEMREF_UNSUPPORTED|atomic=0|ldgsts=1','ALL_DATA requires separate B16 OFF reference scope','EPL2MEMREF_DUPLICATE_NATIVE_ACCESS|','EPL2MEMREF_UNSUPPORTED|atomic=1|ldgsts=0']
  for index,(old,marker) in enumerate(zip(prod['expected_rejections']+supp['expected_rejections'],markers)):
   require(digest(old['log'])==old['log_sha256'] and marker in Path(old['log']).read_text(),'producer rejection changed')
   result=execute(old['command'][2:],OUT/('expected_rejection_'+str(index)+'.log'));require(result['exit_code']==-6 and marker in Path(result['log']).read_text(),'wrong native rejection');receipt['expected_rejections'].append({**result,'expected_marker':marker});write_json(OUT/'RECEIPT.json',receipt)
  receipt['status']='11_ACTUAL_CONSTRUCTORS_5_EXPECTED_NATIVE_REJECTIONS_PASS_NOT_FULL_QUALIFICATION'
 finally:
  r.release_build(lease,'lane5');receipt['lease_released']=True;write_json(OUT/'RECEIPT.json',receipt)
 print(json.dumps({'status':receipt['status'],'constructors':len(receipt['positive']),'expected_rejections':len(receipt['expected_rejections']),'new_applications':0}))
if __name__=='__main__':main()
