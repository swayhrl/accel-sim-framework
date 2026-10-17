"""Native producer fixtures only; central lease, hashes and immutable outputs."""
import argparse,hashlib,importlib.util,json,subprocess,time,resource
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 p.add_argument('--all-data',action='store_true')
 a=p.parse_args();b=json.loads(a.receipt.read_text());assert b['status']=='BUILT_NOT_INDEPENDENTLY_QUALIFIED'
 core=Path(b['core']);build=Path(b['build']);assert sha(build/'accel-sim.out')==b['binary_sha256']
 assert subprocess.check_output(['git','-C',str(core),'rev-parse','HEAD'],text=True).strip()==b['core_source_commit']
 client=json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text());path=Path(client['registry_client'])
 assert sha(path)==client['registry_client_sha256'],'registry hash mismatch'
 s=importlib.util.spec_from_file_location('lane4_directed_registry',path);api=importlib.util.module_from_spec(s);s.loader.exec_module(api)
 reg=api.Registry(client['canonical_root']);a.out.mkdir(exist_ok=False,parents=True)
 lease=reg.build_lease('lane4',cpu=1,memory=2*1024**3)
 base=str(core/'configs/tested-cfgs/SM7_QV100/gpgpusim.config');overlay=str(core/'tests/ep_l2/ft_wbuf.config');t=core/'tests/ep_l2'
 items=[('ideal_wb',[base,overlay]),('ideal_meta',[base,overlay]),('ideal_meta_integrated',[base,str(t/'ideal_meta_integrated.config')]),
  ('ideal_host_prefill_reference',[]),('ideal_host_prefill_partition',[base,str(t/'ideal_host_prefill_b16.config')]),
  ('ideal_read_hit',[base,str(t/'ideal_read_hit.config')]),('ft_directed',[base,overlay])]
 for mode in [1,2]:
  for cap in [8,16]:items.extend([('ft_a1',[base,overlay,str(mode),str(cap)]),('ft_memcpy_clock',[base,overlay,str(mode),str(cap),'4096']),('ft_partition',[base,overlay,str(mode),str(cap)])])
 for case in ['b1-read-first','b1-atomic-first','b1-multi','b1-b16','b1-dirty','b1-version-only']:items.append(('common_delta_r16',[base,overlay,case]))
 expected={}
 if a.all_data:
  items.extend([('ideal_read_hit',[base,str(t/'ideal_read_hit_rop160.config')]),
   ('all_data_reference',[]),('all_data_reference',['--duplicate']),
   ('all_data_ldst',[base,str(t/'all_data_reference.config')]),
   ('all_data_ldst',[base,str(t/'all_data_reference.config'),'--unsupported'])])
  expected[len(items)-3]=(-6,'EPL2MEMREF_DUPLICATE_ORIGINAL_INSTRUCTION')
  expected[len(items)-1]=(-6,'EPL2MEMREF_UNSUPPORTED')
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 rows=[]
 try:
  for n,(name,args) in enumerate(items):
   cmd=[str(build/'gpgpu-sim'/('ep_l2_'+name)),*args];log=a.out/(str(n)+'_'+name+'.log');start=time.monotonic()
   with log.open('x') as f:
    try:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=180,cwd=a.out);code=r.returncode
    except subprocess.TimeoutExpired:code='TIMEOUT'
   want,marker=expected.get(n,(0,None));passed=code==want and (marker is None or marker in log.read_text(errors='replace'))
   rows.append(dict(name=name,command=cmd,returncode=code,expected_returncode=want,required_log_marker=marker,passed=passed,log=str(log),log_sha256=sha(log),seconds=time.monotonic()-start));print(n,name,code,'PASS' if passed else 'FAIL',flush=True)
   (a.out/'TEST_RECEIPT.json').write_text(json.dumps(dict(lease=lease,producer=b,tool_sha256=sha(__file__),planned=len(items),tests=rows,full_application_starts=0,scope='Producer native-directed only, not independent qualification'),indent=2)+'\n')
 finally:reg.release_build(lease,'lane4')
 if any(not r['passed'] for r in rows):raise SystemExit(1)
if __name__=='__main__':main()
