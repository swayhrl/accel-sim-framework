import importlib.util,json,hashlib,os,sys
from pathlib import Path
root=Path('/workspace/ep_l2_ft20261016_shared')
c=json.loads((root/'CLIENT_CONTRACT.json').read_text());p=Path('/workspace/ep_l2_potential20261017/lane2/registry_pinned.py');assert hashlib.sha256(p.read_bytes()).hexdigest()==c['registry_client_sha256']
spec=importlib.util.spec_from_file_location('registry',p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);r=mod.Registry(root)
if len(sys.argv)>1 and sys.argv[1]=='release':
 r.release_build(Path('/workspace/ep_l2_potential20261017/lane2/lease.txt').read_text().strip(),'lane2');sys.exit()
resources=mod.local_resources();st=os.statvfs('/root/share');share=st.f_bavail*st.f_frsize
assert resources['disk_free_bytes']>=54*1024**3 and share>=40*1024**3
snap=r.snapshot();active=[v for v in list(snap['runs'].values())+list(snap.get('resource_leases',{}).values()) if v['status'] in mod.ACTIVE];print(json.dumps({'resources':resources,'share_free':share,'active':active}))
key=r.build_lease('lane2',cpu=2,memory=8*1024**3);Path('/workspace/ep_l2_potential20261017/lane2/lease.txt').write_text(key+'\n');print('lease',key)
