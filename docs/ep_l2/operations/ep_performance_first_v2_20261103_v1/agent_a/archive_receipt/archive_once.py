from pathlib import Path,PurePosixPath
import os,subprocess,json,hashlib,tarfile,time,uuid,stat,shutil,datetime,io
A=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v2_20261103_v1/agent_a').resolve();R=A/'archive_receipt';C=A/'core_candidate';F=Path('/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/framework');V=F/'gpu-simulator/extern/pybind11'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p),bytes=Path(p).stat().st_size)
def write(p,j):
 with Path(p).open('x') as f:json.dump(j,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def safe_name(n):
 p=PurePosixPath(n);assert not p.is_absolute() and '..' not in p.parts and n==str(p) and n not in ['','.'];return n
def safe_remove(p,base,prefix):
 p=Path(p);base=Path(base).resolve();q=p.resolve();assert q.parent==base and q.name.startswith(prefix) and q!=base and not p.is_symlink(),(q,base);shutil.rmtree(q);assert not q.exists();return str(q)
start=time.time();original_manifest_sha=sha(A/'DELIVERY_MANIFEST.json');assert original_manifest_sha=='7a873e66cebad48b64e4143da0d66ae3f6f00e60565da735eded62046ad074f0'
identity=json.loads((A/'NEW_SOURCE_BUILD_IDENTITY.json').read_text());assert identity['source_identity']['core_source_commit']=='bf4e48447136b990bd2db15e2972a4394e37d21f';assert sha(Path(identity['ELF_ref']['path']))=='bab27c440a58426b05d4d10312feeaa55cd28319d52e9396009738e036667553'
mount=json.loads(subprocess.check_output(['findmnt','-J','-T','/root/share/mnt164'],text=True))['filesystems'][0];assert mount['source']=='admin-wcx@10.208.130.164:/home/shared' and mount['fstype']=='fuse.sshfs'
remote=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v2_20261103_v1/agent_a/source_bf4e484_elf_bab27c44_v1');remote.mkdir(parents=True,exist_ok=True);archive=remote/'SOURCE_AND_ENGINEERING_ARTIFACTS.tar.gz';partial=remote/('.ARCHIVE_PARTIAL_'+uuid.uuid4().hex+'.tar.gz');assert not archive.exists() and not (remote/'ARTIFACT_MANIFEST.json').exists(),'existing archive needs read-only review; no overwrite'
stage=R/('.STAGING_'+uuid.uuid4().hex);stage.mkdir();snapshots=[]
for name,root,expected,url in [('Core',C,identity['source_identity']['core_source_commit'],'https://github.com/swayhrl/gpgpu-sim.git')]:
 dest=stage/name;p=subprocess.run(['git','clone','--no-checkout','--depth','1','file://'+str(root),str(dest)],text=True,capture_output=True,timeout=120);assert p.returncode==0,p.stderr
 assert subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip()==expected
 subprocess.run(['git','-C',str(dest),'reset','--mixed','HEAD'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE);subprocess.run(['git','-C',str(dest),'remote','set-url','origin',url],check=True)
 assert not (dest/'.git/objects/info/alternates').exists();prefix='sources/Core' if name=='Core' else 'sources/Framework' if name=='Framework' else 'sources/Framework/gpu-simulator/extern/pybind11';snapshots.append((name,root,dest,prefix,expected))
print('SOURCE_GIT_METADATA_READY',flush=True)
rows=[];seen={};reuse=[]
class Reader:
 def __init__(self,f):self.f=f;self.h=hashlib.sha256();self.n=0
 def read(self,n=-1):b=self.f.read(n);self.h.update(b);self.n+=len(b);return b
def add_stream(tf,name,f,size,mode,role,origin):
 safe_name(name)
 if name in seen:
  r=Reader(f)
  while r.read(1024*1024):pass
  assert seen[name]['sha256']==r.h.hexdigest() and seen[name]['bytes']==size,'conflicting source member '+name;reuse.append({'member':name,'same_source_bytes_reused':True});return
 ti=tarfile.TarInfo(name);ti.size=size;ti.mode=mode&0o777;ti.mtime=0;r=Reader(f);tf.addfile(ti,r);assert r.n==size
 row=dict(member=name,bytes=size,mode=ti.mode,sha256=r.h.hexdigest(),role=role,origin=origin);seen[name]=row;rows.append(row)
def add_file(tf,path,name,role):
 path=Path(path);before=path.stat();assert path.is_file() and not path.is_symlink()
 with path.open('rb') as f:add_stream(tf,name,f,before.st_size,stat.S_IMODE(before.st_mode),role,str(path))
 after=path.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'live file changed'
with tarfile.open(partial,'w:gz',compresslevel=1,format=tarfile.PAX_FORMAT) as tf:
 for name,root,dest,prefix,expected in snapshots:
  p=subprocess.Popen(['git','-C',str(root),'archive','--format=tar',expected],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  with tarfile.open(fileobj=p.stdout,mode='r|') as source:
   for member in source:
    if member.isdir():continue
    assert member.isfile(),'nonregular tracked source member';f=source.extractfile(member);add_stream(tf,prefix+'/'+safe_name(member.name),f,member.size,member.mode,'COMMITTED_SOURCE_SNAPSHOT',str(root)+'@'+expected+':'+member.name)
  err=p.stderr.read();assert p.wait()==0,err
  for path in sorted((dest/'.git').rglob('*')):
   if not path.is_file():continue
   rel=path.relative_to(dest/'.git')
   if rel.parts[0] in ['hooks','logs'] or rel.name in ['FETCH_HEAD','ORIG_HEAD']:continue
   add_file(tf,path,prefix+'/.git/'+rel.as_posix(),'SELF_CONTAINED_SHALLOW_GIT_IDENTITY')
  print('PACKED_SOURCE',name,flush=True)
 add_file(tf,Path(identity['ELF_ref']['path']),'artifacts/accel-sim.out','EXACT_NEW_ELF')
 for lib in identity['libraries']:
  p=Path(lib['path']);assert sha(p)==lib['sha256'];add_file(tf,p,'artifacts/static/'+p.relative_to(A/'build').as_posix(),'EXACT_MATCHING_STATIC_LIBRARY')
 original=json.loads((A/'DELIVERY_MANIFEST.json').read_text())
 for item in original['files']:
  p=Path(item['path']);assert sha(p)==item['sha256'];add_file(tf,p,'evidence/'+p.relative_to(A).as_posix(),'FROZEN_ENGINEERING_OR_CPU_EVIDENCE')
 add_file(tf,A/'DELIVERY_MANIFEST.json','evidence/DELIVERY_MANIFEST.json','ORIGINAL_FROZEN_MANIFEST_UNCHANGED')
 for p in [A/'build/CMakeCache.txt',A/'build/compile_commands.json',A/'build/accelsim_version.h']:
  if p.exists():add_file(tf,p,'build_metadata/'+p.name,'REBUILD_METADATA')
 for p in [R/'REBUILD_AND_RESTORE.md',R/'TOOLCHAIN_REFERENCE.json',R/'FRAMEWORK_GRAPH_BOUNDARY.json',R/'FRAMEWORK_BUILD_SOURCE_DEPENDENCY.json',R/'archive_once.py']:add_file(tf,p,'archive_metadata/'+p.name,'ARCHIVE_OR_REBUILD_METADATA')
with partial.open('rb') as f:os.fsync(f.fileno())
os.rename(partial,archive);ar=ref(archive);logical=sum(r['bytes'] for r in rows);manifest=dict(schema='EP_CLEAN_CAP_ENGINEERING_ARTIFACT_ARCHIVE_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='ARCHIVE_CLOSED_SHA_PENDING_NATIVE_RESTORES',source_identity=identity['source_identity'],archive_ref=ar,members=rows,member_count=len(rows),logical_bytes=logical,duplicate_identical_source_reused=reuse,Source_KEEP=True,no_Trace_or_scientific_raw_copied=True,no_scientific_launch=True,external_dependencies='recorded compiler/CUDA/toolchain/runtime and sharedFW/vendor source in verified B archive; no full Framework Git graph or OS image',frozen_research_manifest_sha256=original_manifest_sha)
mp=remote/'ARTIFACT_MANIFEST.json';write(mp,manifest);print('ARCHIVE_CLOSED',len(rows),logical,ar['bytes'],flush=True)
free=os.statvfs(A).f_bavail*os.statvfs(A).f_frsize;assert free>=logical+1024**3,'native restore window insufficient actualfree';restores=[];parent=R/'native_restore';parent.mkdir(exist_ok=True)
for label in ['FIRST','INDEPENDENT']:
 target=parent/(label+'_'+uuid.uuid4().hex);assert not target.exists();target.mkdir();observed=set();t=time.time();assert sha(archive)==ar['sha256'];expected={r['member']:r for r in rows}
 with tarfile.open(archive,'r|gz') as tf:
  for member in tf:
   n=safe_name(member.name);assert member.isfile() and n in expected and n not in observed and member.size==expected[n]['bytes'];out=target/Path(n);out.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256();count=0
   with tf.extractfile(member) as f,out.open('xb') as w:
    for b in iter(lambda:f.read(1024*1024),b''):count+=len(b);assert count<=member.size;h.update(b);w.write(b)
   os.chmod(out,expected[n]['mode']);assert count==member.size and h.hexdigest()==expected[n]['sha256'];observed.add(n)
 assert observed==set(expected)
 # Independently reopen every restored file and confirm SHA again, including the executable and all8libraries.
 for n,row in expected.items():assert sha(target/Path(n))==row['sha256'],n
 heads={}
 for name,root,dest,prefix,expected_head in snapshots:
  repo=target/prefix;heads[name]=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip();assert heads[name]==expected_head
  # Do not refresh/archive-modify the Git index during identity verification.
  st=subprocess.check_output(['git','-C',str(repo),'status','--porcelain','--untracked-files=no'],env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'),text=True);assert not st.strip(),(name,st[:300])
 receipt=dict(status='INDEPENDENT_NATIVE_COMPLETE_EVERY_FILE_SHA_RESTORE_PASS',label=label,target=str(target),archive_sha256=ar['sha256'],member_count=len(observed),logical_bytes=logical,source_heads=heads,seconds=time.time()-t,restored_file_reopen_sha_pass=True)
 receipt['removed_temporary_native_directory']=safe_remove(target,parent,label+'_');restores.append(receipt);print('RESTORE_PASS',label,len(observed),flush=True)
removed_stage=safe_remove(stage,R,'.STAGING_');assert sha(A/'DELIVERY_MANIFEST.json')==original_manifest_sha
receipt=dict(schema='EP_AGENT_A_V2_TRUE164_ARTIFACT_ARCHIVE_RECEIPT_V1',status='TRUE164_SOURCE_ELF_8LIBS_SHA_AND_TWO_INDEPENDENT_NATIVE_RESTORES_PASS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),archive_ref=ar,artifact_manifest_ref=ref(mp),source_identity=identity['source_identity'],Framework_build_source_dependency_ref=ref(R/'FRAMEWORK_BUILD_SOURCE_DEPENDENCY.json'),Framework_Git_graph='NOT_CLAIMED',native_restores=restores,archive_mount=mount,Source_KEEP=True,original_manifest_ref=ref(A/'DELIVERY_MANIFEST.json'),original_manifest_unchanged=True,metadata_staging_removed=removed_stage,new_models_started=0,rebuilds_or_CPU_tests_rerun=0,elapsed_seconds=time.time()-start)
write(R/'ARCHIVE_RECEIPT.json',receipt);write(remote/'ARCHIVE_CLOSURE_RECEIPT.json',receipt);print('DONE',json.dumps({'archive':ar,'manifest':ref(mp),'local_receipt':ref(R/'ARCHIVE_RECEIPT.json'),'seconds':time.time()-start}),flush=True)
