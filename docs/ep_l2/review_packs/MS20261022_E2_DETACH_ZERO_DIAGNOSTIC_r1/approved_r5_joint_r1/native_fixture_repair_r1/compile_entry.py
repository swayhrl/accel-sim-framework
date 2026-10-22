#!/usr/bin/env python3
"""Compile/link one test-only object/ELF under original E test lease. No native/app."""
import argparse,datetime,hashlib,json,os,subprocess,sys,time
from pathlib import Path

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for x in iter(lambda:f.read(1048576),b''):h.update(x)
 return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,x):
 t=p.with_name(p.name+'.tmp')
 with t.open('x') as f:json.dump(x,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(t,p);fd=os.open(str(p.parent),os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def size(root):
 seen=set();n=0
 for p in root.rglob('*'):
  s=p.lstat()
  if (s.st_dev,s.st_ino) not in seen:seen.add((s.st_dev,s.st_ino));n+=s.st_blocks*512
 return n

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--spec',required=True);ap.add_argument('--expected-spec-sha256',required=True);ap.add_argument('--out',required=True);args=ap.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=False);rows=[];code=3;status='PRECHECK_NOT_COMPLETE'
 try:
  assert sha(args.spec)==args.expected_spec_sha256;s=json.loads(Path(args.spec).read_text());artifact=Path(s['artifact_directory']);artifact.mkdir(parents=True,exist_ok=False)
  assert s['production_source_identity']['core_source_commit']=='1093d2629e3d6a9130ba25b9dd119b6f3e16c092'
  for ref in s['source_files']+s['archive_refs']+[s['source_compile_flags_ref'],s['source_link_ref']]:assert sha(ref['path'])==ref['sha256'],ref['path']
  assert s['max_parallel_compile_jobs']==1 and s['candidate_result_hard_cap_bytes']==33554432
  assert s['object'] in s['compile_argv'] and s['native_elf'] in s['link_argv']
  assert '-g0' in s['compile_argv'] and '-UNDEBUG' in s['compile_argv'] and '-Wl,--strip-debug' in s['link_argv']
  assert not any(x.startswith('-DNDEBUG') for x in s['compile_argv'])
  for name,argv in [('COMPILE',s['compile_argv']),('LINK',s['link_argv'])]:
   started=now();clock=time.monotonic();print('R5_FIXTURE_BUILD_BEGIN '+name,flush=True);log=out/(name+'.log')
   with log.open('xb') as f:
    child=subprocess.Popen(argv,cwd=s['cwd'],stdout=f,stderr=subprocess.STDOUT)
    try:proc=Path('/proc/'+str(child.pid)+'/stat').read_text().strip()
    except FileNotFoundError:proc=None
    wait=child.wait()
   row={'name':name,'argv':argv,'cwd':s['cwd'],'actual_exit_code':wait,'pid':child.pid,'proc_stat_at_start':proc,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'started_utc':started,'finished_utc':now(),'wall_seconds':time.monotonic()-clock,'log_path':str(log),'log_sha256':sha(log),'artifact_allocated_bytes_after':size(artifact)};rows.append(row);save(out/(name+'_RESULT.json'),row)
   if wait:status=name+'_FAILED';code=wait if wait>0 else 128-wait;return code
   if size(artifact)+size(out)>s['candidate_result_hard_cap_bytes']:raise ValueError('actual32MiB engineering artifact cap exceeded')
  for ref in s['archive_refs']:assert sha(ref['path'])==ref['sha256'],'production archive changed'
  artifacts={}
  for name,path in [('object',s['object']),('native_elf',s['native_elf'])]:
   f=Path(path);st=f.stat();artifacts[name]={'path':path,'sha256':sha(f),'bytes':st.st_size,'allocated_bytes':st.st_blocks*512}
  save(out/'ARTIFACTS.json',{'status':'TEST_ONLY_ELF_COMPILED_NOT_NATIVE_QUALIFICATION','production_source_identity':s['production_source_identity'],'source_spec_sha256':args.expected_spec_sha256,'artifacts':artifacts,'linked_archives_rehashed_equal':True});status='COMPILE_LINK_COMPLETE_NO_NATIVE_EXECUTION';code=0;return 0
 except Exception as e:save(out/'FAILURE.json',{'type':type(e).__name__,'message':str(e),'time':now()});print('R5_FIXTURE_BUILD_FAILURE '+str(e),flush=True);return code
 finally:save(out/'RECEIPT.json',{'status':status,'exit_code':code,'commands':rows,'finished_utc':now(),'native_app_build_main_invoked':False})
if __name__=='__main__':sys.exit(main())
