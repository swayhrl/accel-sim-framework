#!/usr/bin/env python3
"""Exact r5 configure/build helper, invoked only under the original E build lease.
No native, simulator invocation, lease, controller, source mutation or retry API.
"""
import argparse,datetime,hashlib,json,os,re,shlex,subprocess,sys,time
from pathlib import Path

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,obj):
 tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(obj,indent=2)+'\n');os.replace(tmp,p)
def git(p,*args): return subprocess.check_output(['git','-C',str(p),*args],text=True).strip()
def allocated(root):
 # Only this dedicated build directory; no project/result/trace scan.
 total=0;seen=set()
 for here,dirs,files in os.walk(root):
  for name in dirs+files:
   try:s=os.lstat(os.path.join(here,name))
   except FileNotFoundError:continue
   if (s.st_dev,s.st_ino) in seen:continue
   seen.add((s.st_dev,s.st_ino));total+=s.st_blocks*512
 return total

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--spec',required=True);ap.add_argument('--expected-spec-sha256',required=True);ap.add_argument('--out',required=True);args=ap.parse_args()
 specpath=Path(args.spec);out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
 receipts=[];status='FAILED_BEFORE_CONFIGURE';code=3
 start={'schema':'E2_R5_ACTUAL_BUILD_ENTRY_V1','started_utc':now(),'pid':os.getpid(),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'process_stat':Path('/proc/self/stat').read_text().strip(),'spec_path':str(specpath),'actual_spec_sha256':digest(specpath),'expected_spec_sha256':args.expected_spec_sha256,'native_or_app_invoked':False}
 save(out/'ENTRY_BEGIN.json',start)
 build=None
 try:
  if start['actual_spec_sha256']!=args.expected_spec_sha256:raise ValueError('exact spec hash mismatch')
  spec=json.loads(specpath.read_text());build=Path(spec['build_directory'])
  if str(build)!='/workspace/build/ep-l2-ms20261022-e2-tagpressure-observer-r5':raise ValueError('wrong exact buildroot')
  if spec['parallel_jobs']!=2 or spec['scratch_hard_cap_bytes']!=1073741824:raise ValueError('build contract mismatch')
  env=os.environ.copy();env.update(spec['environment_overrides']);core=Path(env['GPGPUSIM_ROOT']);fw=Path(spec['working_directory']).parent;vendor=fw/'gpu-simulator/extern/pybind11'
  actual={'core_source_commit':git(core,'rev-parse','HEAD'),'framework_source_commit':git(fw,'rev-parse','HEAD'),'vendor_pybind11_commit':git(vendor,'rev-parse','HEAD')}
  if actual!=spec['source_identity']:raise ValueError('source identity mismatch')
  for p in (core,fw,vendor):
   if git(p,'status','--porcelain'):raise ValueError('source worktree dirty: '+str(p))
  for ref in spec['files']:
   if digest(ref['path'])!=ref['sha256']:raise ValueError('build source pin mismatch '+ref['path'])
  if spec['targets']!=['accel-sim.out','ep_l2_detach_diagnostic','ep_l2_tagpressure_metadata']:raise ValueError('targets not exact')
  expected_build=[spec['cmake_executable'],'--build',str(build),'--target',*spec['targets'],'-j2']
  if spec['build_argv']!=expected_build:raise ValueError('build argv mismatch')
  if spec['configure_argv'][:5]!=[spec['cmake_executable'],'-S',str(fw/'gpu-simulator'),'-B',str(build)]:raise ValueError('configure home/build mismatch')
  if build.exists():raise ValueError('refuse to overwrite/preuse existing r5 build directory')
  save(out/'SOURCE_PRECHECK.json',{'status':'PASS','identity':actual,'all_source_trees_clean':True,'time':now()})
  def command(name,argv):
   log=out/(name+'.log');began=now();wall=time.monotonic();print('R5_BUILD_COMMAND_BEGIN '+name,flush=True)
   with log.open('xb') as f:
    child=subprocess.Popen(argv,cwd=spec['working_directory'],env=env,stdout=f,stderr=subprocess.STDOUT)
    # Child inherits original durable guardian process group and lease. No setsid,
    # nohup, background controller or independent authorization is created here.
    try:child_stat=Path("/proc/"+str(child.pid)+"/stat").read_text().strip()
    except FileNotFoundError:child_stat=None
    result=child.wait()
   r={'name':name,'argv':argv,'cwd':spec['working_directory'],'environment_overrides':spec['environment_overrides'],'child_pid':child.pid,'child_start_proc_stat':child_stat,'boot_id':start['boot_id'],'started_utc':began,'finished_utc':now(),'wall_seconds':time.monotonic()-wall,'native_exit_code':result,'log':str(log),'log_sha256':digest(log),'log_bytes':log.stat().st_size,'allocated_build_bytes_after':allocated(build) if build.exists() else 0}
   receipts.append(r);save(out/(name+'_RESULT.json'),r);print('R5_BUILD_COMMAND_END '+name+' exit='+str(result),flush=True)
   if result:return result
   if r['allocated_build_bytes_after']>spec['scratch_hard_cap_bytes']:raise ValueError('actual buildscratch >1GiB')
   return 0
  code=command('CONFIGURE',spec['configure_argv'])
  if code:
   status='CONFIGURE_FAILED';code=code if code>0 else 128-code;return code
  def flags_check(label):
   flags=list(build.rglob('flags.make'));refs=[];bad=[]
   if not flags:raise ValueError('no generated flags')
   for f in sorted(flags):
    text=f.read_text();tokens=[]
    for line in text.splitlines():
     if line.startswith(('CXX_FLAGS =','C_FLAGS =','CXX_DEFINES =','C_DEFINES =')):tokens+=shlex.split(line.split('=',1)[1])
    defines=[]
    for i,t in enumerate(tokens):
     if t.startswith('-D'):defines.append(t[2:] if t!='-D' else tokens[i+1] if i+1<len(tokens) else '')
    rejected=any(x.split('=',1)[0]=='NDEBUG' for x in defines)
    if rejected:bad.append(str(f))
    refs.append({'path':str(f),'sha256':digest(f),'bytes':f.stat().st_size,'contains_DNDEBUG':rejected})
   required=[build/'CMakeFiles/accel-sim.out.dir/flags.make',build/'gpgpu-sim/CMakeFiles/ep_l2_detach_diagnostic.dir/flags.make',build/'gpgpu-sim/CMakeFiles/ep_l2_tagpressure_metadata.dir/flags.make',build/'gpgpu-sim/src/gpgpu-sim/CMakeFiles/gpgpusim.dir/flags.make']
   if any(not f.is_file() for f in required):raise ValueError('required target flags missing')
   cc=build/'compile_commands.json';commands=json.loads(cc.read_text())
   # Excluded old-reference compile entries may be generated by CMake but are
   # never built. Actual requested main/native dependency link lines below are
   # independently checked to reject references to old archive buildroots.
   for f in required[:3]:
    if '-DNDEBUG' in f.read_text():bad.append(str(f))
   for link in [build/'CMakeFiles/accel-sim.out.dir/link.txt',build/'gpgpu-sim/CMakeFiles/ep_l2_detach_diagnostic.dir/link.txt']:
    for token in shlex.split(link.read_text()):
     if token.startswith('/workspace/build/') and token.endswith('.a') and not token.startswith(str(build)+'/'):bad.append('old archive in '+str(link)+': '+token)
   result={'status':'PASS' if not bad else 'FAIL','stage':label,'flags_files_count':len(refs),'flags':refs,'required_targets_present':True,'compile_commands_sha256':digest(cc),'compile_command_count':len(commands),'no_DNDEBUG_in_generated_flags':not bad,'bad':bad,'excluded_old_reference_not_built':True}
   save(out/(label+'_ASSERTIONS_AND_FLAGS.json'),result)
   if bad:raise ValueError('generated assertions/source flags audit failed')
  status='CONFIGURED_ASSERTION_AUDIT_NOT_COMPLETE';flags_check('POST_CONFIGURE');status='CONFIGURED_BUILD_NOT_COMPLETE'
  code=command('BUILD',spec['build_argv'])
  if code:
   status='BUILD_FAILED';code=code if code>0 else 128-code;return code
  status='BUILD_RETURNED_ZERO_POSTBUILD_AUDIT_NOT_COMPLETE';flags_check('POST_BUILD')
  artifacts={}
  for name,path in spec['expected_artifacts'].items():
   f=Path(path)
   if not f.is_file():raise ValueError('missing actual artifact '+path)
   st=f.stat();artifacts[name]={'path':path,'sha256':digest(f),'bytes':st.st_size,'allocated_bytes':st.st_blocks*512}
  for p in (core,fw,vendor):
   if git(p,'status','--porcelain'):raise ValueError('source changed during build: '+str(p))
  save(out/'BUILD_ARTIFACTS.json',{'status':'ACTUAL_BUILD_ARTIFACTS_NOT_NATIVE_OR_APPLICATION_QUALIFIED','source_identity':actual,'artifacts':artifacts,'allocated_build_bytes':allocated(build)})
  status='BUILD_COMPLETE_ASSERTIONS_AUDITED_NOT_NATIVE_OR_APPLICATION_QUALIFIED';code=0;return 0
 except Exception as e:
  save(out/'ENTRY_ERROR.json',{'type':type(e).__name__,'message':str(e),'time':now()});print('R5_BUILD_ENTRY_ERROR '+type(e).__name__+': '+str(e),flush=True);code=3;return code
 finally:
  save(out/'ENTRY_RESULT.json',{'schema':'E2_R5_ACTUAL_BUILD_ENTRY_RESULT_V1','status':status,'exit_code':code,'finished_utc':now(),'command_receipts':receipts,'native_or_application_executed':False,'actual_allocated_build_bytes':allocated(build) if build is not None and build.exists() else 0})
if __name__=='__main__':sys.exit(main())
