import sys,json,subprocess,resource,os
from pathlib import Path
sys.path.insert(0,'util/ep_l2/ft_lane5')
from registry import Registry,write_json
from run import require,digest
from independent_headroom_r19 import safe
hand=json.load(open('/workspace/ep_l2_ft20261016_shared/lane1/PARALLEL_ALL_DATA_RELEASE_r1.json'));prod=json.load(open(hand['producer_receipt_path']));m=json.load(open(hand['producer_manifest_path']));exe=Path('/workspace/ep_l2_parallel_lane1/all_data_release_r1/effective_entry/effective_config');require(digest(exe)==prod['effective_entry_sha256'],'Changed native option/constructor entry')
out=Path('/workspace/ep_l2_potential20261017_lane5_results/unified_mode_guards_r1');require(not out.exists(),'Keep previous mode revision');r=Registry();safe();lease=r.build_lease('lane5',cpu=1,memory=4*2**30);out.mkdir();rows=[];resource.setrlimit(resource.RLIMIT_CORE,(0,0))
cases=[('FT_'+str(mode)+'_'+str(cap),{'-gpgpu_ep_l2_ft_mode':str(mode),'-gpgpu_ep_l2_wbuf_entries':str(cap)}) for mode,cap in [(1,7),(1,0),(2,7),(3,16)]]
cases += [('IDEAL_WB_U',{'-gpgpu_ep_l2_ft_mode':'2','-gpgpu_ep_l2_ideal_wb':'1'}),('READ_META',{'-gpgpu_ep_l2_ideal_read_hit':'1','-gpgpu_ep_l2_ideal_meta':'1'}),('READ_WB',{'-gpgpu_ep_l2_ideal_read_hit':'1','-gpgpu_ep_l2_ideal_wb':'1'}),('META_NO_DESCRIPTOR',{'-gpgpu_ep_l2_ideal_meta':'1','-gpgpu_ep_l2_descriptor_pool_size':'0'})]
try:
 for name,opts in cases:
  safe();overlay=out/(name+'.config');overlay.write_text(''.join(k+' '+v+'\n' for k,v in opts.items()));cmd=[str(exe),*[x['path'] for x in m['profiles']['B16_OFF']['configs']],str(overlay)];log=out/(name+'.log')
  with log.open('xb') as f:done=subprocess.run(cmd,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=30,env=dict(os.environ,OMP_NUM_THREADS='1'),start_new_session=True)
  text=log.read_text();row={'name':name,'command':cmd,'exit_code':done.returncode,'log':str(log),'sha256':digest(log)};rows.append(row);require(done.returncode==-6 and 'PARALLEL_EFFECTIVE_PASS' not in text and ('EP-L2' in text or 'Assertion' in text),'Invalid native combination accepted or wrong failure');row['status']='EXPECTED_NATIVE_REJECTION_PASS';print(name,'REFUSED',flush=True)
finally:r.release_build(lease,'lane5');write_json(out/'RECEIPT.json',{'status':'ALL8_EXPECTED_NATIVE_REJECTIONS_PASS' if len(rows)==8 and all(v.get('status') for v in rows) else 'FAILED_RETAIN_ALL','rows':rows,'lease':lease,'lease_released':True,'actual_compiles':0,'full_application_starts':0})
