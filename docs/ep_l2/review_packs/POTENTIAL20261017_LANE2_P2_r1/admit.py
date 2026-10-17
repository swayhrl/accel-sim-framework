import importlib.util,json,hashlib,os,sys,subprocess
from pathlib import Path
root=Path('/workspace/ep_l2_ft20261016_shared');local=Path('/workspace/ep_l2_potential20261017/lane2');p=local/'registry_pinned.py'
release=len(sys.argv)>1 and sys.argv[1]=='release'
if release:
 c=json.loads((local/'lease-client.json').read_text())
else:
 c=json.loads((root/'CLIENT_CONTRACT.json').read_text());live=Path(c['registry_client']);content=live.read_bytes()
 if hashlib.sha256(content).hexdigest()!=c['registry_client_sha256']:
  repo=live.parents[3];relative=str(live.relative_to(repo));content=subprocess.check_output(['git','show',c['registry_source_commit']+':'+relative],cwd=repo)
 assert hashlib.sha256(content).hexdigest()==c['registry_client_sha256'];p.write_bytes(content);(local/'lease-client.json').write_text(json.dumps(c,indent=2)+'\n')
assert hashlib.sha256(p.read_bytes()).hexdigest()==c['registry_client_sha256']
spec=importlib.util.spec_from_file_location('registry',p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);r=mod.Registry(root)
if release:
 r.release_build((local/'lease.txt').read_text().strip(),'lane2');sys.exit()
resources=mod.local_resources();st=os.statvfs('/root/share');share=st.f_bavail*st.f_frsize
assert resources['disk_free_bytes']>=54*1024**3 and share>=40*1024**3
snap=r.snapshot();active=[v for v in list(snap['runs'].values())+list(snap.get('resource_leases',{}).values()) if v['status'] in mod.ACTIVE];print(json.dumps({'resources':resources,'share_free':share,'active':active,'registry_client_sha256':c['registry_client_sha256']}))
cpu=int(os.environ.get('LANE2_CPU','2'));memory=int(os.environ.get('LANE2_MEM_GIB','8'))*1024**3
key=r.build_lease('lane2',cpu=cpu,memory=memory);(local/'lease.txt').write_text(key+'\n');print('lease',key)
