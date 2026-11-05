"""CPU2/nice15 byte reproduction only; never execute/rewrite an ELF or old input."""
from pathlib import Path
import concurrent.futures,hashlib,json,os,resource,shlex,subprocess,time
HERE=Path(__file__).parent
N=Path('/root/share/mnt164/huangrulin/ep_l2_performance_first_v5_20261105_v1/track_a_wv')
B=N/'build';R=N/'original_byte_reproduction_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=sha(p))
def dump(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def limited():
 os.nice(15);resource.setrlimit(resource.RLIMIT_AS,(4<<30,4<<30));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def main():
 start=time.time();R.mkdir(exist_ok=False);(R/'overlay').mkdir()
 # Exactly the initial observed literal, NOT a change to original generated header.
 (R/'overlay/detailed_version').write_text('const char *g_gpgpusim_build_string="gpgpu-sim_git-commit-78f4b59_modified_6.0.";\\n'.replace('\\n','\n'))
 source=json.loads((HERE/'ORIGINAL_TRACKED_SOURCE_HASH_CLOSURE.json').read_bytes())
 for x in source['rows']:
  p=Path(x['path']);b=os.readlink(p).encode()if x['git_mode']=='120000'else p.read_bytes()
  assert hashlib.sha256(b).hexdigest()==x['sha256']
 original_inputs=json.loads((HERE/'ORIGINAL_BUILD_PROVENANCE.json').read_bytes())['original_artifacts']
 before={x['path']:x['sha256']for x in original_inputs}
 recipes=subprocess.run(['ninja','-t','commands','accel-sim.out'],cwd=B,stdout=subprocess.PIPE,text=True,check=True).stdout.splitlines()
 dump(R/'ORIGINAL_RECIPE_LINES.json',recipes)
 comp=[];ar=[];link=None
 for line in recipes:
  a=shlex.split(line)
  if '-c'in a and '-o'in a and '/usr/bin/c++'in a:
   out=a[a.index('-o')+1];target=R/'objects'/out
   assert not Path(out).is_absolute();target.parent.mkdir(parents=True,exist_ok=True)
   actual=list(a);actual[actual.index('-o')+1]=str(target)
   for flag in ['-MF','-MT']:
    if flag in actual:actual[actual.index(flag)+1]=str(target)+('.d'if flag=='-MF'else'')
   actual.insert(actual.index('/usr/bin/c++')+1,'-I'+str(R/'overlay'))
   comp.append(dict(original_argv=a,actual_argv=actual,original_output=str(B/out),new_output=str(target)))
  elif '/usr/bin/ar'in a:
   begin=a.index('/usr/bin/ar');end=a.index('&&',begin)if '&&'in a[begin:]else len(a);av=a[begin:end]
   rn=a.index('/usr/bin/ranlib');re=a.index('&&',rn)if '&&'in a[rn:]else len(a);rv=a[rn:re]
   ar.append((av,rv))
  elif '-o'in a and '/usr/bin/c++'in a:
   assert link is None;begin=a.index('/usr/bin/c++');end=a.index('&&',begin)if '&&'in a[begin:]else len(a);link=a[begin:end]
 assert len(comp)>100 and len(ar)==8 and link is not None,(len(comp),len(ar))
 dump(R/'COMPILE_PLAN.json',dict(compile_jobs=2,translation_units=len(comp),rows=comp,old_recipe_cwd=str(B),source_inputs='original absolute Source paths at exact current clean Source7b4',only_code_input_overlay=ref(R/'overlay/detailed_version'),no_ELF_execution=True))
 def compile_one(z):
  t=time.time();log=R/('compile_'+str(comp.index(z)).zfill(3)+'.log')
  with log.open('wb')as f:p=subprocess.run(z['actual_argv'],cwd=B,stdout=f,stderr=subprocess.STDOUT,timeout=300,env=dict(os.environ,CUDA_VISIBLE_DEVICES=''))
  row=dict(**z,returncode=p.returncode,seconds=time.time()-t,log=str(log))
  if p.returncode==0:
   row.update(original_object_ref=ref(z['original_output']),new_object_ref=ref(z['new_output']),byte_MATCH=sha(z['original_output'])==sha(z['new_output']))
  dump(R/('result_'+str(comp.index(z)).zfill(3)+'.json'),row)
  if p.returncode:raise RuntimeError('CPU compile failed '+str(log))
  return row
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:rows=list(pool.map(compile_one,comp))
 # Recreate all static libraries with original member ordering, only fresh objects.
 archives=[]
 for av,rv in ar:
  old=av[2];target=R/'libraries'/old;target.parent.mkdir(parents=True,exist_ok=True)
  members=[R/'objects'/x for x in av[3:]]
  assert all(x.exists()for x in members)
  command=[av[0],av[1],str(target)]+[str(x)for x in members]
  subprocess.run(command,cwd=B,check=True,timeout=60,preexec_fn=limited)
  subprocess.run([rv[0],str(target)],cwd=B,check=True,timeout=60,preexec_fn=limited)
  original_names=subprocess.run(['/usr/bin/ar','t',str(B/old)],stdout=subprocess.PIPE,check=True).stdout
  new_names=subprocess.run(['/usr/bin/ar','t',str(target)],stdout=subprocess.PIPE,check=True).stdout
  assert original_names==new_names
  archives.append(dict(original_ref=ref(B/old),new_ref=ref(target),member_order_MATCH=True,byte_MATCH=sha(B/old)==sha(target)))
 # Exact original link flags/order; input object/library paths are the new copies.
 actual=[];skip=False
 for i,x in enumerate(link):
  if skip:skip=False;continue
  if x=='-o':actual+=['-o',str(R/'reproduced_blob.elf')];skip=True
  elif x.endswith('.o')and (R/'objects'/x).exists():actual.append(str(R/'objects'/x))
  elif x.endswith('.a')and (R/'libraries'/x).exists():actual.append(str(R/'libraries'/x))
  else:actual.append(x)
 assert all(Path(x).name!='accel-sim.out'for x in actual)
 with (R/'LINK.log').open('wb')as f:subprocess.run(actual,cwd=B,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=300,preexec_fn=limited,env=dict(os.environ,CUDA_VISIBLE_DEVICES=''))
 for path,h in before.items():assert sha(path)==h,'original input mutated '+path
 for x in source['rows']:
  p=Path(x['path']);b=os.readlink(p).encode()if x['git_mode']=='120000'else p.read_bytes();assert hashlib.sha256(b).hexdigest()==x['sha256']
 original_elf=ref(B/'accel-sim.out');new_elf=ref(R/'reproduced_blob.elf')
 original_lib=ref(B/'gpgpu-sim/src/gpgpu-sim/libgpgpusim.a');new_lib=ref(R/'libraries/gpgpu-sim/src/gpgpu-sim/libgpgpusim.a')
 result=dict(schema='EP_PFV5_A_CPU_ORIGINAL_BYTE_REPRODUCTION_V1',translation_units=len(rows),object_byte_MATCH=sum(x['byte_MATCH']for x in rows),object_mismatches=[x for x in rows if not x['byte_MATCH']],all_archive_results=archives,original_ELF_ref=original_elf,reproduced_blob_ref=new_elf,ELF_complete_SHA_MATCH=original_elf['sha256']==new_elf['sha256'],original_gpgpusim_library_ref=original_lib,reproduced_gpgpusim_library_ref=new_lib,gpgpusim_library_complete_SHA_MATCH=original_lib['sha256']==new_lib['sha256'],original_source_and_outputs_unchanged=True,core_tracked_source_closure_ref=ref(HERE/'ORIGINAL_TRACKED_SOURCE_HASH_CLOSURE.json'),compile_plan_ref=ref(R/'COMPILE_PLAN.json'),link_argv=actual,original_link_argv=link,seconds=time.time()-start,ELF_executions=0,model_starts=0,science_permission=False)
 dump(R/'RESULT.json',result);dump(HERE/'CPU_BYTE_REPRODUCTION_RESULT.json',result)
 print(json.dumps({k:result[k]for k in ['translation_units','object_byte_MATCH','ELF_complete_SHA_MATCH','gpgpusim_library_complete_SHA_MATCH','seconds','ELF_executions']}))
if __name__=='__main__':
 try:main()
 except BaseException as exc:
  if R.exists():dump(R/'FAILED_RETAINED.json',dict(reason=repr(exc),model_starts=0,original_inputs_keep=True))
  raise
