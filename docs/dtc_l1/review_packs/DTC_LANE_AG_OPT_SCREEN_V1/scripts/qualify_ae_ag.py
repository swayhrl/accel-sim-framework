#!/usr/bin/env python3
"""AG-owned reproduction of fixed AE CPU cases, using independent Python oracle."""
from common import *
import importlib.util
import resource
import tarfile
import io

def main():
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 root=BUILD/'x2-source'
 if not root.exists():
  root.mkdir()
  data=subprocess.check_output(['git','-C',str(CORE_REPO),'archive',X2,'src','libcuda'])
  with tarfile.open(fileobj=io.BytesIO(data)) as archive:archive.extractall(root)
 raw=RAW/'cpu-qualification'/'ae-independent-ag';raw.mkdir(parents=True,exist_ok=False)
 oracle_path=PACK/'inputs/AE/scripts/run_cpu.py'
 module=importlib.util.spec_from_file_location('ae_oracle',oracle_path)
 oracle=importlib.util.module_from_spec(module);module.loader.exec_module(oracle)
 source=CORE/'tests/dtc_l1_tag_hash_bankrow_test.cc'
 assert sha(source)=='8a8519ca35d5159bc0267dbdfbc93b823a1eb1b7f7fbbe5aa2890ebb85a45652'
 receipts=[];cases=[];baseline={}
 def run(argv,label,expected=0):
  r=subprocess.run(list(map(str,argv)),cwd=raw,capture_output=True,timeout=60)
  for stream in ['stdout','stderr']:(raw/(label+'.'+stream)).write_bytes(getattr(r,stream))
  receipts.append(dict(label=label,argv=list(map(str,argv)),exit_code=r.returncode,
      stdout_sha256=sha(raw/(label+'.stdout')),stderr_sha256=sha(raw/(label+'.stderr'))))
  write(PACK/'AE_AG_CPU_COMMANDS.json',receipts)
  assert r.returncode==expected,(label,r.returncode,r.stderr[-1500:]);return r.stdout.decode(),r.stderr.decode()
 for lineage,include in [('x2',root),('ag',CORE)]:
  exe=BUILD/('ae-header-'+lineage)
  argv=['/usr/bin/g++','-std=c++17','-O1','-g0','-UNDEBUG','-fno-access-control',
      '-I'+str(include/'src/gpgpu-sim'),'-I'+str(include/'src'),str(source),'-o',str(exe)]
  if lineage=='ag':argv.insert(1,'-DDTC_AE_NEW=1')
  run(argv,'compile_'+lineage)
  variants=[('off','0')] if lineage=='x2' else [('omitted','omit'),('off','0'),('on','1')]
  for sets,ways in [(32,4),(32,8),(64,4),(64,8)]:
   for policy,value in variants:
    for case,tail in [('mapping',[]),('conflicts',[]),('lru',[]),('late',[]),('trace',['stride4096']),('trace',['neutral']),('trace',['adversary'])]:
     name=case+('_'+tail[0] if tail else '')
     label=f'{lineage}_{policy}_{sets}_{ways}_{name}'
     out,_=run([exe,case,sets,ways,value,*tail],label)
     rows=[json.loads(l) for l in out.splitlines()];observed=rows[-1];on=policy=='on'
     if case=='mapping':assert observed==oracle.mapping_oracle(sets,on)
     elif case=='trace':oracle.trace_oracle(rows,sets,ways,on,tail[0])
     elif case=='conflicts':assert observed==dict(summary='conflicts',default_granted=4,default_denied=4,global1_granted=2,global1_denied=1)
     elif case=='late':assert observed==dict(summary='late_k1',wakeups=8,pending_hits=6,misses=2,retired=8,refs=0,allocated=0,map_loss_sum=8,map_loss_count=2)
     else:assert observed['evictions']==1 and observed['precheck_recency_preserved']
     if not on:
      key=(sets,ways,name)
      if lineage=='x2':baseline[key]=out
      else:assert out==baseline[key],('OFF per-request differential',label)
     cases.append(dict(label=label,status='PASS_INDEPENDENT_ORACLE',observed=observed,stdout_sha256=hashlib.sha256(out.encode()).hexdigest()))
  for sets in [1,2,6,12]:
   out,_=run([exe,'mapping',sets,4,'0'],f'{lineage}_legacy_geometry_{sets}')
   assert json.loads(out)==oracle.mapping_oracle(sets,False)
   if lineage=='x2':baseline[sets]=out
   else:assert out==baseline[sets]
   cases.append(dict(label=f'{lineage}_old_geometry_{sets}',status='PASS'))
 exe=BUILD/'ae-header-ag'
 for value in ['omit','0','1']:
  args=[] if value=='omit' else ['-gpgpu_dtc_l1_tag_hash_bankrow',value]
  out,_=run([exe,'options',*args],'parser_'+value)
  assert json.loads(out.splitlines()[-1])['hash']==int(value=='1')
  cases.append(dict(label='parser_'+value,status='PASS_REAL_PARSER'))
 _,err=run([exe,'options','-unknown_ag_option','1'],'unknown_option',1);assert 'Unknown Option' in err
 cases.append(dict(label='parser_unknown',status='PASS_REJECT'))
 for why,sets in [('geometry',0),('geometry',1),('geometry',2),('geometry',6),('geometry',12),('banks1',32),('banks2',32),('banks8',32),('finite0',32),('LEGACY',32),('BASE',32),('IO',32),('MODERN',32)]:
  _,err=run([exe,'reject',sets,4,1,why],f'reject_{why}_{sets}',-6)
  assert 'TAG_HASH_BANKROW_' in err
  cases.append(dict(label=f'reject_{why}_{sets}',status='PASS_EXPECTED_ABORT'))
 assert len(cases)==137
 write(PACK/'AE_AG_INDEPENDENT_CPU.json',dict(status='PASS_137_AG_OWNED_CPU_CASES',cases=cases,
     test_source_sha256=sha(source),oracle_sha256=sha(oracle_path),
     default_OFF_per_request_pairs=56,old_geometry_pairs=4,
     raw=str(raw),new_simulations_started=0,full_LDST_qualification='SEPARATE_REQUIRED_GATE'))
 print('PASS: 137 AE cases; independent oracle + 56 OFF pairs + 4 legacy geometries; 0 simulations')

if __name__=='__main__':main()
