import ast,csv,datetime,hashlib,json,os,pathlib,subprocess,sys,tarfile,tempfile,threading,time,types
BASE=pathlib.Path('/workspace/worktrees/framework-c16-storage-audit-20261020-v1/docs/ep_l2/operations/c16_storage_audit_20261020');OUT=BASE/'conditional_retirement';code=(BASE/'RESTORE.sh').read_text().split("<<'PY'\n",1)[1].rsplit('\nPY',1)[0];prod=list(csv.DictReader((BASE/'RESTORE_MAPPING.tsv').open(),delimiter='\t'));results={}
with tempfile.TemporaryDirectory(prefix='c16-restore-synthetic-') as d:
 root=pathlib.Path(d);nas=root/'nas';bridge=root/'bridge';bridge.mkdir();(root/'conditional_retirement').mkdir();(root/'RESTORE.sh').write_text('fixture');rows=[]
 for r in prod:
  x=dict(r);x['original174_path']=str(root/'outbound'/r['package']/pathlib.Path(r['original174_path']).name);pathlib.Path(x['original174_path']).parent.mkdir(parents=True,exist_ok=True);payload=('synthetic-'+r['pair_id']).encode()*101;x['size_bytes']=str(len(payload));x['sha256_expected']=hashlib.sha256(payload).hexdigest();s=nas/pathlib.Path(r['native164_path']).relative_to('/home/shared');s.parent.mkdir(parents=True,exist_ok=True);s.write_bytes(payload);rows.append(x)
 with (root/'RESTORE_MAPPING.tsv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
 (root/'registry.json').write_text(json.dumps({'runs':{},'resource_leases':{},'mechanism_study_20261019_v1':{'controller':{'state':'STOPPED'}}}));(root/'pressure').write_text('some avg10=0 avg60=0 avg300=0 total=0\nfull avg10=0 avg60=0 avg300=0 total=0\n');(root/'conditional_retirement/USER_IO_OVERRIDE.json').write_text('{}')
 probe={'nonce':'synthetic-test-route'};(bridge/'SOURCE_ROUTE_PROBE.json').write_text(json.dumps(probe));(bridge/'TARGET_ROUTE_ACK.json').write_text(json.dumps({'nonce':probe['nonce'],'namespace':'mnt:[4026535153]','mount':'admin-wcx@10.208.130.164:/home/shared'}));(root/'conditional_retirement/RESTORE_ROUTE_SOURCE_PROBE.json').write_text(json.dumps({'sha256':hashlib.sha256((bridge/'SOURCE_ROUTE_PROBE.json').read_bytes()).hexdigest()}))
 # Test-only filesystem path substitutions. Production namespace, member allowlist,
 # size/SHA, attrs, no-overwrite and copy/publication logic are unchanged.
 repl={'/workspace/c16_exchange/autodl_wave1/outbound/C16_GPU_PACKAGE_':str(root/'outbound')+'/', '/root/share/c16_storage_audit_restore_20261020_v1':str(bridge),'/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json':str(root/'registry.json'),'/proc/pressure/io':str(root/'pressure')}
 class Substitute(ast.NodeTransformer):
  def visit_Constant(self,n):
   if isinstance(n.value,str) and n.value in repl:return ast.copy_location(ast.Constant(repl[n.value]),n)
   return n
 tree=Substitute().visit(ast.parse(code));ast.fix_missing_locations(tree);tested=ast.unparse(tree)
 prefix="import os,subprocess,json,types; os.statvfs=lambda p:types.SimpleNamespace(f_bavail=2**30,f_frsize=4096); subprocess.check_output=lambda *a,**k:json.dumps({'filesystems':[{'target':"+repr(str(nas))+",'source':'admin-wcx@10.208.130.164:/home/shared','fstype':'fuse.sshfs'}]}); "
 def run(args,background=False):
  snippet=prefix+'import sys;sys.argv='+repr(['-',str(root/'RESTORE.sh')]+args)+';exec('+repr(tested)+')'
  return subprocess.Popen([sys.executable,'-c',snippet],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) if background else subprocess.run([sys.executable,'-c',snippet],capture_output=True,text=True,timeout=15)
 def verify():
  for r in rows:
   if r['package']!='P3':continue
   p=pathlib.Path(r['original174_path']);s=p.stat();assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256_expected'];assert(s.st_uid,s.st_gid,s.st_mode&0o777,s.st_mtime_ns)==(int(r['uid']),int(r['gid']),int(r['mode_octal'],8),int(r['mtime_ns']))
 p=run(['--package','P3','--mount',str(nas),'--execute']);assert p.returncode==0,p.stderr;verify();results['tiny_direct_restore_bytes_permissions_mtime']=True
 p=run(['--package','P3','--mount',str(nas),'--execute']);assert p.returncode!=0 and 'Destination exists' in p.stderr;verify();results['default_refuses_existing_files_without_modifying_them']=True
 for r in rows:
  if r['package']=='P3':pathlib.Path(r['original174_path']).unlink()
 pipe=bridge/'restore-P3.fifo';consumer=run(['--package','P3','--shared-pipe',str(pipe),'--execute'],True)
 for _ in range(100):
  if pipe.exists():break
  if consumer.poll() is not None:raise AssertionError(consumer.communicate())
  time.sleep(.02)
 assert pipe.exists()
 with pipe.open('wb') as f:
  with tarfile.open(fileobj=f,mode='w|',format=tarfile.USTAR_FORMAT) as tf:
   for r in rows:
    if r['package']=='P3':
     rel=pathlib.Path(r['native164_path']).relative_to('/home/shared');tf.add(nas/rel,arcname=str(rel))
 stdout,stderr=consumer.communicate(timeout=15);assert consumer.returncode==0,stderr;verify();results['tiny_foreground_FIFO_tar_restore_exact_members_bytes_permissions_mtime']=True
 results['production_model_bytes_read_or_written']=0;results['only_tiny_owned_temp_files_used']=True
result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='PASS',scope='Synthetic tiny data, mocked capacity/mount and isolated control paths; not a claimed real164 full restore',checks=results)
(OUT/'RESTORE_SYNTHETIC_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
