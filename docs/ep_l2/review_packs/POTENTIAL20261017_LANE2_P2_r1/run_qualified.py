from pathlib import Path
import subprocess,json,hashlib,resource
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
core=Path('/workspace/worktrees/gpgpu-sim-ep-l2-potential20261017-lane2-v1');b=Path('/workspace/build/ep-l2-potential20261017-lane2-v1');out=Path(__file__).parent
base='configs/tested-cfgs/SM7_QV100/gpgpusim.config';cfg='tests/ep_l2/ft_wbuf.config'
cases=[]
for mode in [1,2]:
 for ports in [1,2]:cases.append((f'p{ports}-mode{mode}','p2',[base,cfg,str(mode),str(ports)]))
cases += [('s64-full','s64',[base,cfg,'1','16','1','0','1']),('b16-full-control','s64',[base,cfg,'1','16','0','0','1']),('ucap16-full','ucap',[base,cfg,'2','16','0','16','1']),('u-off-staging17','ucap',[base,cfg,'2','16','0','0','1'])]
for name,args in [('a1-s64',['1','16','1','0','1']),('a1-b16',['1','16','0','0','1']),('a1-u16',['2','16','0','0','1']),('ucap-mixed',['2','16','0','16','1','mixed']),('ucap-rollback',['2','16','0','16','1','rollback'])]:cases.append((name,'a1',[base,cfg,*args]))
cases.append(('ucap-bank-retry','ucap_retry',[base,cfg]))
results=[]
sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=core,text=True).strip();assert not subprocess.check_output(['git','status','--porcelain'],cwd=core)
for name,target,args in cases:
 binary=b/('ep_l2_potential_'+target);cmd=[str(binary),*args]
 with (out/(name+'.log')).open('wb') as f:
  f.write(('SOURCE '+sha+'\nCMD '+json.dumps(cmd)+'\n').encode());f.flush()
  try:r=subprocess.run(cmd,cwd=core,stdout=f,stderr=subprocess.STDOUT,timeout=30);rc=r.returncode
  except subprocess.TimeoutExpired:rc='TIMEOUT'
 row={'case':name,'source_commit':sha,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'command':cmd,'returncode':rc,'status':'PASS' if rc==0 else 'FAIL'};results.append(row);print(json.dumps(row),flush=True)
(out/'directed-results.json').write_text(json.dumps(results,indent=2)+'\n')
# CLI/config guards through real memory-config/cache constructors, distinct
# from raw-store unit checks. Expected process failures are bounded/explicit.
negative=[]
for name,args,marker in [('reject-ucap-p2',['2','16','0','16','2'],'P2 requires'),('reject-s64-p2',['1','16','1','0','2'],'P2 requires'),('reject-p3',['1','16','0','0','3'],'P2 requires')]:
 cmd=[str(b/'ep_l2_potential_a1'),base,cfg,*args];r=subprocess.run(cmd,cwd=core,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30);(out/(name+'.log')).write_bytes(r.stdout);ok=r.returncode<0 and marker.encode() in r.stdout;negative.append({'case':name,'returncode':r.returncode,'expected_reason':marker,'status':'PASS_EXPECTED_REJECTION' if ok else 'FAIL','command':cmd})
(out/'negative-results.json').write_text(json.dumps(negative,indent=2)+'\n');print(json.dumps(negative),flush=True)
raise SystemExit(0 if all(r['returncode']==0 for r in results) and all(r['status']=='PASS_EXPECTED_REJECTION' for r in negative) else 1)
