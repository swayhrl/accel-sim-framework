import pathlib,tempfile,csv,hashlib,subprocess,json,ast,os,sys,datetime
BASE=pathlib.Path('/workspace/worktrees/framework-c16-storage-audit-20261020-v1/docs/ep_l2/operations/c16_storage_audit_20261020');OUT=BASE/'conditional_retirement';source=(OUT/'release_exact_package.py').read_text();rows0=list(csv.DictReader((BASE/'RESTORE_MAPPING.tsv').open(),delimiter='\t'));checks={}
with tempfile.TemporaryDirectory(prefix='c16-release-synthetic-') as d:
 root=pathlib.Path(d);work=root/'conditional_retirement';work.mkdir();bridge=root/'bridge';bridge.mkdir();(root/'RESTORE.sh').write_text('synthetic program');rows=[];packages={p:dict(ready=True,files=[]) for p in ['P3','P2']}
 for r in rows0:
  row=dict(r);p=root/'outbound'/('C16_GPU_PACKAGE_'+r['package'])/pathlib.Path(r['original174_path']).name;p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes(('owned synthetic '+r['pair_id']).encode()*50);s=p.stat();digest=hashlib.sha256(p.read_bytes()).hexdigest();row['original174_path']=str(p);row['sha256_expected']=digest;rows.append(row);ident=dict(dev=s.st_dev,inode=s.st_ino,size=s.st_size,nlink=s.st_nlink,uid=s.st_uid,gid=s.st_gid,mode=s.st_mode&0o777,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,allocated_bytes=s.st_blocks*512);packages[r['package']]['files'].append(dict(path=str(p),identity=ident,source_sha256=digest,target_sha256=digest,frozen_sha256=digest))
 with (root/'RESTORE_MAPPING.tsv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
 controls=[]
 for i in range(126):
  p=root/'controls'/str(i);p.parent.mkdir(exist_ok=True);p.write_bytes(b'KEEP');controls.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 kept=root/'MODEL_SOURCE_ACTIVE_KEEP';kept.write_bytes(b'original remains')
 proof=dict(user_conditional_authority=True,historical_A_G_signature_claimed=False,restore_route_verified=True,future_duties_taken_over=True,target_current_full_SHA_count=6,source_current_full_SHA_count=6,target_commit='a'*40,packages=packages,controls_126=controls,restore_script_sha256=hashlib.sha256((root/'RESTORE.sh').read_bytes()).hexdigest());(work/'PRE_RELEASE_ELIGIBILITY.json').write_text(json.dumps(proof))
 # Only machine-specific filesystem paths and frozen fixture-map digest are substituted.
 repl={'/root/share/c16_storage_audit_restore_20261020_v1':str(bridge),'/workspace/c16_exchange/autodl_wave1/outbound/C16_GPU_PACKAGE_':str(root/'outbound/C16_GPU_PACKAGE_'),'0a5dd6177837b18e0928327110c3eaaac60fa994690c3c3d40e382c6ba251234':hashlib.sha256((root/'RESTORE_MAPPING.tsv').read_bytes()).hexdigest()}
 class Sub(ast.NodeTransformer):
  def visit_Constant(self,n):
   if isinstance(n.value,str) and n.value in repl:return ast.copy_location(ast.Constant(repl[n.value]),n)
   return n
 tree=Sub().visit(ast.parse(source));ast.fix_missing_locations(tree);prefix='import subprocess,pathlib\n_original_check_output=subprocess.check_output\ndef _fixture_output(args,**kwargs):\n if args[0]=="gh":return pathlib.Path(__file__).with_name("PRE_RELEASE_ELIGIBILITY.json").read_bytes()\n return _original_check_output(args,**kwargs)\nsubprocess.check_output=_fixture_output\n';driver=work/'test_driver.py';driver.write_text(prefix+ast.unparse(tree));proof['release_script_sha256']=hashlib.sha256(driver.read_bytes()).hexdigest();(work/'PRE_RELEASE_ELIGIBILITY.json').write_text(json.dumps(proof))
 def run(pack,execute=False):
  args=[sys.executable,str(driver),'--package',pack,'--proof-commit','a'*40]+(['--execute'] if execute else []);return subprocess.run(args,capture_output=True,text=True,timeout=15)
 def sources_exist():return all(pathlib.Path(r['original174_path']).exists() for r in rows)
 p=run('P3');assert p.returncode==0,p.stderr;assert sources_exist();checks['default_metadata_preflight_never_deletes']=True
 p=run('P2',True);assert p.returncode!=0 and 'P3 must sign off' in p.stderr;assert sources_exist();checks['P2_cannot_precede_P3']=True
 with pathlib.Path(packages['P3']['files'][0]['path']).open('rb') as held:
  p=run('P3',True);assert p.returncode!=0 and 'Live exact-path reader' in p.stderr;assert sources_exist()
 checks['open_reader_blocks_package_before_unlink']=True
 p=run('P3',True);assert p.returncode==0,p.stderr;events=[json.loads(x) for x in (bridge/'SOURCE_RELEASE_JOURNAL.jsonl').read_text().splitlines()];assert [e['event'] for e in events]==['PACKAGE_INTENT','INTENT','DONE','INTENT','DONE','PACKAGE_DONE'];checks['P3_durable_INTENT_DONE_two_file_signoff']=True
 p=run('P2',True);assert p.returncode==0,p.stderr;assert not any(pathlib.Path(r['original174_path']).exists() for r in rows);checks['only_frozen_six_files_removed_in_order']=True
 assert all(hashlib.sha256(pathlib.Path(c['path']).read_bytes()).hexdigest()==c['sha256'] for c in controls) and kept.read_bytes()==b'original remains';checks['126_controls_and_model_source_fixture_preserved']=True
result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='PASS',checks=checks,scope='Only tiny owned temporary fixtures; mocked GitHub proof readback and filesystem constants; real model deletion0')
(OUT/'RELEASE_SYNTHETIC_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
