#!/usr/bin/env python3
"""Exactly two compiler invocations; fixed finite CPU front-end suite only."""
import hashlib,json,os,resource,shutil,struct,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent.parent
CORE=Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-lane-ag3-aead-core-174-v1')
EXT=Path('/workspace/dtc-lane-ag3-aead-screen-174-v1/raw/cpu-qualification/ae-suite')
MASK=(1<<64)-1
BASE='e32afdcf44be3374ff36d22568ed01a075459b6f'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def index(a,s,on):
 l=a//128
 if not on:return l%s
 bits=s.bit_length()-1
 return 4*(((l//4)^(l//s))%(s//4))+l%4

def mapping_oracle(s,on):
 h=14695981039346656037;n=0
 def visit(a):
  nonlocal h,n
  for b in struct.pack('<QI',a,index(a,s,on)):h=((h^b)*1099511628211)&MASK
  n+=1
 for line in range(4096):
  for offset in [0,1,127]:visit(128*line+offset)
 x=0x123456789abcdef0
 for i in range(64):
  x^=(x<<13)&MASK;x^=x>>7;x^=(x<<17)&MASK;x&=MASK;visit((x&((1<<57)-1))<<7)
 return dict(summary='mapping',count=n,fnv64=h,stride_sets=[[index(4096*k+128*b,s,on)for k in range(32)]for b in range(4)])

def trace_oracle(rows,s,w,on,sequence):
 tags={};clock=misses=hits=evictions=0
 for uid,row in enumerate(rows[:-1],1):
  k=(uid-1)%(w+1 if sequence=='adversary'else 32)
  line=32*k if sequence=='stride4096'else k if sequence=='neutral'else 4*k+k*s
  address=128*line;set_id=index(address,s,on)
  assert row['uid']==uid and row['address']==address and row['set']==set_id
  match=next((i for i,t in tags.items()if t[0]==address),None)
  if match is None:
   misses+=1;candidates=list(range(set_id*w,(set_id+1)*w));slot=next((i for i in candidates if i not in tags),None)
   if slot is None:slot=min(candidates,key=lambda i:tags[i][1]);evictions+=1
   clock+=1;tags[slot]=(address,clock)
  else:
   hits+=1;clock+=2;tags[match]=(address,clock)
  actual={t[0]:(t[1],t[4])for t in row['tags']}
  assert actual==tags,('independent set/way/LRU oracle',uid,actual,tags)
  for k,v in dict(misses=misses,hits=hits,evictions=evictions,clock=clock,allocated=len(tags),refs=0,pib=0,tag_requests=uid,conflicts=0).items():assert row[k]==v,(uid,k,row[k],v)
  assert row['map_loss']==[0,evictions]
 summary=rows[-1]
 expected=dict(summary='trace',sequence=sequence,requests=len(rows)-1,misses=misses,hits=hits,evictions=evictions,allocated=len(tags),refs=0,tag_count=s*w,physical_capacity=640,pib_capacity=128)
 assert all(summary[k]==v for k,v in expected.items())
 return expected

def comparable(text):
 rows=[json.loads(line) for line in text.splitlines()]
 for row in rows:row.pop('physical_entry_bytes',None)
 return rows

def main():
 resource.setrlimit(resource.RLIMIT_CORE,(0,0));log=EXT/'cpu_final_v1';log.mkdir()
 lock=EXT/'PRECOMPILE_LOCK.json';binding=json.loads(lock.read_text());assert binding['compiler_invocations']==0
 assert binding['plan_sha256']==sha(P/'inputs/ae/inputs/FIXED_CASE_PLAN.json')
 binding['test_source_sha256']=sha(CORE/'tests/dtc_l1_tag_hash_bankrow_test.cc');dump(lock,binding)
 receipts=[];results=[];paired={};binaries={}
 def run(args,label,rc=0):
  r=subprocess.run(list(map(str,args)),text=True,capture_output=True,cwd=log,timeout=30)
  receipt=dict(label=label,argv=list(map(str,args)),expected_exit_code=rc,exit_code=r.returncode)
  for stream in ['stdout','stderr']:
   f=log/(label+'.'+stream);f.write_text(getattr(r,stream));receipt[stream]=dict(path=str(f),sha256=sha(f),bytes=f.stat().st_size)
  receipts.append(receipt);dump(P/'CPU_COMMAND_RECEIPTS.json',receipts)
  assert r.returncode==rc,(label,r.returncode,r.stderr[-1500:]);return r
 compiler=Path(shutil.which('g++')).resolve();version=run([compiler,'--version'],'compiler_version').stdout
 for lineage,root in [('baseline',Path('/workspace/dtc-lane-ag3-aead-screen-174-v1/build/x2-source')),('ae',CORE)]:
  binary=log/lineage
  command=[str(compiler),'-std=c++17','-O1','-g0','-UNDEBUG','-fno-access-control','-Wall','-Wextra','-I'+str(root/'src/gpgpu-sim'),'-I'+str(root/'src'),str(CORE/'tests/dtc_l1_tag_hash_bankrow_test.cc'),'-o',str(binary)]
  if lineage=='ae':command.insert(1,'-DDTC_AE_NEW=1')
  binding['compiler_invocations']+=1;assert binding['compiler_invocations']<=2;dump(lock,binding)
  run(command,'compile_'+lineage);binaries[lineage]=dict(path=str(binary),sha256=sha(binary))
  variants=[('off','0')]if lineage=='baseline'else[('omitted','omit'),('off','0'),('on','1')]
  for s,w in [(32,4),(32,8),(64,4),(64,8)]:
   for policy,value in variants:
    for case,tail in [('mapping',[]),('conflicts',[]),('lru',[]),('late',[]),('trace',['stride4096']),('trace',['neutral']),('trace',['adversary'])]:
     name=case+('_'+tail[0]if tail else'');label=f'{lineage}_{policy}_S{s}_W{w}_{name}'
     r=run([binary,case,s,w,value,*tail],label);rows=[json.loads(l)for l in r.stdout.splitlines()];observed=rows[-1]
     expected={};on=policy=='on'
     if case=='mapping':expected=mapping_oracle(s,on);assert observed==expected
     elif case=='trace':expected=trace_oracle(rows,s,w,on,tail[0])
     elif case=='conflicts':expected=dict(summary='conflicts',default_granted=4,default_denied=4,global1_granted=2,global1_denied=1);assert observed==expected
     elif case=='late':expected=dict(summary='late_k1',wakeups=8,pending_hits=6,misses=2,retired=8,refs=0,allocated=0,map_loss_sum=8,map_loss_count=2);assert observed==expected
     elif case=='lru':expected=dict(summary='lru',evictions=1,precheck_recency_preserved=True);assert all(observed[k]==v for k,v in expected.items())
     if not on:
      key=(s,w,name)
      if lineage=='baseline':paired[key]=r.stdout
      else:assert comparable(r.stdout)==comparable(paired[key]),('OFF modeled per-request differential',label)
     # Independent comparison must reject a deliberately wrong expected field.
     bad=dict(expected);bad['must_not_exist']=True
     rejected=not all(observed.get(k)==v for k,v in bad.items());assert rejected
     results.append(dict(id=label,input=[case,s,w,value,*tail],source=BASE if lineage=='baseline'else'AE_SOURCE_MANIFEST',expected=expected,observed=observed,exit_code=0,per_request_output_sha256=hashlib.sha256(r.stdout.encode()).hexdigest(),per_request_count=len(rows)-1,independent_oracle='PASS',bad_expected_rejected=True))
  # OFF must also preserve old, non-power-of-two geometries.
  for s in [1,2,6,12]:
   r=run([binary,'mapping',s,4,'0'],f'{lineage}_off_geometry{s}');observed=json.loads(r.stdout);assert observed==mapping_oracle(s,False)
   if lineage=='baseline':paired[(s,'old_geometry')]=r.stdout
   else:assert r.stdout==paired[(s,'old_geometry')]
   results.append(dict(id=f'{lineage}_off_geometry{s}',expected=mapping_oracle(s,False),observed=observed,exit_code=0))
 ae=binaries['ae']['path']
 for value in ['omit','0','1']:
  args=[]if value=='omit'else['-gpgpu_dtc_l1_tag_hash_bankrow',value]
  r=run([ae,'options',*args],'parser_'+value);observed=json.loads(r.stdout.splitlines()[-1]);assert observed['hash']==int(value=='1')
  assert '-gpgpu_dtc_l1_tag_hash_bankrow'in r.stdout
  results.append(dict(id='parser_'+value,expected=dict(hash=int(value=='1')),observed=observed,exit_code=0))
 r=run([ae,'options','-ae_unknown_flag','1'],'parser_unknown',1);assert 'Unknown Option'in r.stderr
 results.append(dict(id='parser_unknown',expected_exit_code=1,diagnostic='Unknown Option',exit_code=1))
 for why,s in [('geometry',0),('geometry',1),('geometry',2),('geometry',6),('geometry',12),('banks1',32),('banks2',32),('banks8',32),('finite0',32),('LEGACY',32),('BASE',32),('IO',32),('MODERN',32)]:
  label=f'reject_{why}_{s}';r=run([ae,'reject',s,4,'1',why],label,-6)
  diagnostic='TAG_HASH_BANKROW_'+('FINITE_V1_REQUIRED_STOP'if why=='finite0'else'PAPER_OO_ONLY_STOP'if why in ['LEGACY','BASE','IO','MODERN']else'UNSUPPORTED_GEOMETRY_STOP');assert diagnostic in r.stderr
  results.append(dict(id=label,input=['reject',s,4,1,why],expected_exit_code=-6,diagnostic=diagnostic,exit_code=r.returncode))
 summary=dict(schema=1,status='PASS_BOUNDED_CPU_FRONTEND',compiler_invocations=binding['compiler_invocations'],compiler=dict(path=str(compiler),sha256=sha(compiler),version=version),binaries=binaries,precompile_lock=binding,results=results,off_exact_per_request_pairs=56,off_old_geometry_pairs=4,full_core_build='NOT_RUN_TWO_COMPILATION_BUDGET',full_simulations=0,native_applications=0,GPU_runs=0,application_trace_reads=0,hash_candidates=1)
 dump(P/'CPU_CASES.json',summary)
 print(json.dumps(dict(status=summary['status'],results=len(results),compiler_invocations=2,raw_output_bytes=sum(r[k]['bytes']for r in receipts for k in ['stdout','stderr']))))
if __name__=='__main__':main()
