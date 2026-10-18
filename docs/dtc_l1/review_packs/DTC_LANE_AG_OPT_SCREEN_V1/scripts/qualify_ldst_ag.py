#!/usr/bin/env python3
"""Actual production parser/LDST/normal-export OFF differential and bounded ON safety."""
from common import *
import re
import argparse
import resource

def frames(text):
 result=[]
 for m in re.finditer(r'^AA5_EXPORT_SNAPSHOT_BEGIN label=(\S+) expected_cycle=(\d+)\n(.*?)^AA5_EXPORT_SNAPSHOT_END label=\1\s*$',text,re.M|re.S):
  body='\n'.join(l for l in m[3].splitlines() if not re.match(r'^(AA5_NORMAL_ENTRY_LIBRARY |gpu_total_sim_rate|gpgpu_simulation_time|gpgpu_simulation_rate|gpgpu_silicon_slowdown)',l))
  result.append((m[1],m[2],body))
 assert len(result)==4
 return result

def witnesses(text):
 lines=[l for l in text.splitlines() if l.startswith(('Y2_PACKET ','Y2_PHYSICAL ','Y2_TICK ','Y2_CONTROL ','Y2_RESULT ','PUBLIC_STAT '))]
 assert len([l for l in lines if l.startswith('Y2_TICK ')])==40
 return lines

def main(build_name,label):
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 raw=RAW/'cpu-qualification'/label;raw.mkdir(parents=True,exist_ok=False)
 receipts=[];results=[];gold={}
 def run(args,name,library):
  env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','CUDA_VISIBLE_DEVICES':'','LD_LIBRARY_PATH':str(library)}
  r=subprocess.run(list(map(str,args)),cwd=raw,env=env,capture_output=True,timeout=180)
  for stream in ['stdout','stderr']:(raw/(name+'.'+stream)).write_bytes(getattr(r,stream))
  receipts.append(dict(label=name,argv=list(map(str,args)),returncode=r.returncode,
      stdout_sha256=sha(raw/(name+'.stdout')),stderr_sha256=sha(raw/(name+'.stderr'))))
  write(PACK/(label.upper()+'_COMMANDS.json'),receipts)
  assert r.returncode==0,(name,r.returncode,r.stderr[-2000:]);return r.stdout.decode()
 for lineage,source,build in [('x2',BUILD/'x2-source',BUILD/'x2-reference'),('ag',CORE,BUILD/build_name)]:
  exe=BUILD/(label+'-'+lineage)
  args=['/usr/bin/g++','-std=c++17','-O1','-fno-access-control','-UNDEBUG','-DY2_HAS_K1=1','-DCUDART_VERSION=11080',
      '-I'+str(source/'src'),'-I'+str(source/'libcuda'),'-I/usr/local/cuda-11.8/include',str(PACK/'scripts/ldst_cpu_fixture.cc'),
      '-L'+str(build),'-Wl,-rpath,'+str(build),'-lcudart','-ldl','-o',str(exe)]
  run(args,'compile_'+lineage,build)
  for k in ['0','1']:
   variants=['x2'] if lineage=='x2' else ['omitted','0','1']
   for ae in variants:
    name=lineage+'_K'+k+'_AE'+ae
    args=[exe,PACK/'inputs/AA5/inputs/CPU_EXPORT_FIXTURE_BASE.config','-gpgpu_dtc_l1_invalidate_on_source_event',k]
    if ae not in ['x2','omitted']:args.extend(['-gpgpu_dtc_l1_tag_hash_bankrow',ae])
    text=run(args,name,build)
    actual=re.findall(r'^Y2_LIBRARY (.*)$',text,re.M)
    assert len(actual)==1 and Path(actual[0]).resolve()==(build/'libcudart.so').resolve()
    f=frames(text);w=witnesses(text)
    if lineage=='x2':gold[k]=(f,w)
    elif ae!='1':assert (f,w)==gold[k],('DEFAULT_OFF_REAL_LDST_OR_NORMAL_EXPORT_DIFFERENCE',name)
    else:
     # Hash changes row only; for this controlled one-line transport the same
     # real LDST service/credit/WB/sector observations must remain identical.
     assert (f,w)==gold[k],('HASH_ON_ONE_LINE_LIFECYCLE_CHANGED',name)
    result=json.loads(next(l[len('Y2_RESULT '):] for l in text.splitlines() if l.startswith('Y2_RESULT ')))
    assert result['cycles']==43 and result['retired']==3 and result['refs']==0 and result['wb_blocked']>0
    assert result['packets']==(2 if k=='1' else 1) and result['ordinary_packets']==1
    results.append(dict(label=name,status='PASS_BOUNDED_REAL_LDST_AND_NORMAL_EXPORT',result=result,
        public_boundaries=len(f),witness_sha256=hashlib.sha256(json.dumps(w).encode()).hexdigest(),
        loaded_library_sha256=sha(build/'libcudart.so')))
 write(PACK/(label.upper()+'_RESULT.json'),dict(status='PASS_ACTUAL_LDST_OFF_EQUIVALENCE_AND_AE_K1_SAFETY',
     build=build_name,source_sha256=sha(PACK/'scripts/ldst_cpu_fixture.cc'),cases=results,
     sectors='REAL_OUT_OF_ORDER_3_1_0_2_RESPONSES',WB='REAL_OPERAND_COLLECTOR_BANK_CONFLICT',
     ordinary_pending='REAL_DELAYED_FILL_TO_CYCLE23',K1='SOURCE_EVENT_WITH_OUTSTANDING_OLD_GENERATION',
     bounded_empty_gpu_clock_ticks_per_case=3,kernels=0,full_simulations_started=0,
     multi_optimization='NOT_APPLICABLE_ONLY_AE_QUALIFIED_NO_AD_MERGE',
     architectural_value_correctness='UNPROVEN'))
 print('PASS: 8 actual LDST CPU fixtures, default OFF/public normal export identical; bounded AE/K1 safety')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--build',required=True);p.add_argument('--label',required=True);a=p.parse_args();main(a.build,a.label)
