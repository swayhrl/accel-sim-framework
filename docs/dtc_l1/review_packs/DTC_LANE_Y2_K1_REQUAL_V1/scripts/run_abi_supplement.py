#!/usr/bin/env python3
"""Bounded CPU production-object tests. No kernel or runtime thread launch.
The only transport seam captures genuine requests and supplies chosen replies;
clock and already-coalesced synthetic instructions are explicit test inputs.
"""
import copy,os,sys,json,hashlib,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent.parent
EXT=Path('/workspace/dtc-lane-y2-k1-requal-174-v1/supplement-r1')
SOURCES={'new':Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-lane-y2-source-c0a5e2c3'),'frozen':Path('/workspace/worktrees/gpgpu-sim-iscas2027-dtc-lane-y2-frozen-6fba0136')}
BUILDS={'new':EXT.parent/'build-c0a5e2c3','frozen':EXT/'build-frozen'}
SHAS={'new':'c0a5e2c31e407c57e3a4af3ce529c921e8059a05','frozen':'6fba0136f8465b59fe5858a950fa39efb265f654'}
OUT=P/'supplement_r1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def oracle(c,finite):
 ticks=c['ticks'];assert [t[0] for t in ticks]==list(range(1,41))
 # Independently sum occupancy rectangles, including clock-gated 31..34 and
 # event32 inside that interval; empty GPU source ticks add the terminal tail.
 pib=sum(t[1]for t in ticks[:-1])+3*ticks[-1][1]
 physical=sum(t[2]for t in ticks[:-1])+3*ticks[-1][2]
 loss={};prev={};loss_sum=loss_count=0
 for cycle,rows in enumerate(c['physical'],1):
  now={(r[0],r[1]):r for r in rows}
  for ident,old in prev.items():
   new=now.get(ident)
   if old[3] and (new is None or not new[3]):loss[ident]=cycle
   if new is None:
    assert ident in loss
    loss_count+=1;loss_sum+=cycle-loss.pop(ident)
  prev=now
 expected=[43,pib,physical] if finite else [0,0,0]
 assert c['result']['finite'][:3]==expected
 assert c['result']['finite'][9:]==([loss_sum,loss_count]if finite else[0,0])
 return dict(occupancy_rectangles=expected,map_loss=[loss_sum,loss_count],remaining_map_loss_owners=len(loss))
def main():
 log=EXT/sys.argv[1];log.mkdir();receipts=[];cases={};comparisons=[];bins={}
 def run(argv,label,env=None,expected=0):
  r=subprocess.run(list(map(str,argv)),text=True,capture_output=True,env=env,cwd=log)
  entry={'label':label,'argv':list(map(str,argv)),'exit_code':r.returncode,'expected_exit_code':expected}
  if env:entry['environment_overrides']={k:env[k]for k in ['LD_LIBRARY_PATH','Y2_MULTI','Y2_DUPLICATE']if k in env}
  for key in ('stdout','stderr'):
   f=log/(label+'.'+key);f.write_text(getattr(r,key));entry[key]={'path':str(f),'sha256':sha(f)}
  receipts.append(entry);dump(OUT/'ABI_RECEIPTS.json',receipts)
  if r.returncode!=expected:raise RuntimeError(label+' exit '+str(r.returncode)+' expected '+str(expected))
  return r
 for key,src in SOURCES.items():
  assert subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip()==SHAS[key]
  assert not subprocess.check_output(['git','-C',str(src),'status','--porcelain','--untracked-files=no'],text=True).strip()
  build=BUILDS[key];binary=log/('abi_'+key);bins[key]=binary
  args=['g++','-std=c++17','-fno-access-control','-UNDEBUG','-DCUDART_VERSION=11080','-I'+str(src/'src'),'-I'+str(src/'libcuda'),'-I/usr/local/cuda-11.8/include',P/'scripts/abi_ldst_probe.cc','-L'+str(build),'-Wl,-rpath,'+str(build),'-lcudart','-ldl','-o',binary]
  if key=='new':args.insert(1,'-DY2_HAS_K1=1')
  run(args,'compile_'+key)
  variants=[('omitted',[])]if key=='frozen'else[('omitted',[]),('off',['-gpgpu_dtc_l1_invalidate_on_source_event','0']),('on',['-gpgpu_dtc_l1_invalidate_on_source_event','1'])]
  for finite in [0,1]:
   for multi in [0,1]:
    for variant,flags in variants:
     label=f'{key}_{variant}_finite{finite}_multi{multi}';env=os.environ.copy();env['LD_LIBRARY_PATH']=str(build);env.pop('Y2_MULTI',None);env.pop('Y2_DUPLICATE',None)
     if multi:env['Y2_MULTI']='1'
     r=run([binary,P/'inputs/abi_base.config',*flags,'-gpgpu_dtc_l1_finite_service',str(finite)],label,env)
     lines=r.stdout.splitlines();bound=next(l.split(' ',1)[1]for l in lines if l.startswith('Y2_LIBRARY '));assert Path(bound).resolve()==(build/'libcudart.so').resolve()
     c={'input_config_sha256':sha(P/'inputs/abi_base.config'),'flags':flags+['-gpgpu_dtc_l1_finite_service',str(finite)],'multi':bool(multi),'binary':str(binary),'binary_sha256':sha(binary),'source':SHAS[key],'library':bound,'library_sha256':sha(bound),'ticks':[json.loads(l.split(' ',1)[1])for l in lines if l.startswith('Y2_TICK ')],'physical':[json.loads(l.split(' ',1)[1])for l in lines if l.startswith('Y2_PHYSICAL ')],'packets':[l for l in lines if l.startswith('Y2_PACKET ')],'counters':json.loads(next(l.split(' ',1)[1]for l in lines if l.startswith('Y2_COUNTERS '))),'result':json.loads(next(l.split(' ',1)[1]for l in lines if l.startswith('Y2_RESULT '))),'source_summaries':[l for l in lines if l.startswith('DTC_INVALIDATE_V1_SUMMARY ')],'exit_code':r.returncode}
     expected=dict(cycles=43,packets=2 if multi and variant=='on'else 1,bytes=256 if multi and variant=='on'else 128,ordinary_packets=1,ordinary_bytes=128,retired=3 if multi else 1,refs=0,allocated=0 if variant=='on'else 1)
     ep=log/(label+'.expected.json');op=log/(label+'.observed.json');dump(ep,expected);dump(op,c['result']);run([sys.executable,P/'scripts/check_observation.py',ep,op],label+'_compare')
     bad=copy.deepcopy(expected);bad['cycles']=44;bp=log/(label+'.bad_expected.json');dump(bp,bad);run([sys.executable,P/'scripts/check_observation.py',bp,op],label+'_negative_oracle',expected=1)
     c['expected']=expected;c['integral_oracle']=oracle(c,finite);c['negative_oracle_exit_code']=1;cases[label]=c;dump(OUT/'ABI_OBSERVATIONS.json',dict(status='RUNNING',cases=cases))
 for finite in [0,1]:
  for multi in [0,1]:
   labels=[f'{k}_finite{finite}_multi{multi}'for k in ['new_omitted','new_off','frozen_omitted']]
   for field in ['ticks','physical','packets','result','counters']:assert cases[labels[0]][field]==cases[labels[1]][field]==cases[labels[2]][field],(labels,field)
   comparisons.append(dict(id=f'K0_ABI_finite{finite}_multi{multi}',inputs=labels,fields=['ticks','physical','packets','result','counters'],status='PASS_EXACT'))
 env=os.environ.copy();env.update(LD_LIBRARY_PATH=str(BUILDS['new']),Y2_MULTI='1',Y2_DUPLICATE='1')
 r=run([bins['new'],P/'inputs/abi_base.config','-gpgpu_dtc_l1_invalidate_on_source_event','1'],'actual_duplicate_sector',env,expected=1)
 assert 'OO response identity/address mismatch'in r.stderr and 'Y2_RESULT 'not in r.stdout
 dump(OUT/'ABI_OBSERVATIONS.json',dict(schema=1,status='PASS',cases=cases,k0_comparisons=comparisons,actual_duplicate_sector=dict(exit_code=1,diagnostic='OO response identity/address mismatch',signal_handler='production crash handler exits 1 after SIGABRT',accepted_result=False),probe_sha256=sha(P/'scripts/abi_ldst_probe.cc'),config_origin='docs/dtc_l1/iscas2027/service_closure_174_v1/config/RTX4080_FROZEN_BASELINE.config',full_simulations_dispatched=0))
 print('PASS: 16 production-object runs, 4 exact K0 triplets, 16 rejecting comparator negatives, 1 production duplicate-sector rejection')
if __name__=='__main__':main()
