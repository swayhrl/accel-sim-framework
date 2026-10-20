"""Publish lightweight cold indices on the original Target branch and read back."""
import base64,hashlib,json,pathlib,subprocess,sys,os
D=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));import tls_target as t
R=t.REPO/'docs/ep_l2/operations/cold_fast_20261020_target';rel=R.relative_to(t.REPO).as_posix()
assert t.git('branch','--show-current').decode().strip()==t.BRANCH
for n in ['cold_stream_source.py','cold_receive.py','run_cold_batch.py','finalize_cold_batch.py','verify_existing_cold_partial.py','publish_cold.py','cold_archive.py','check_second_gates.py','wait_second_gate_window.py']:
    (R/'tools'/n).write_bytes((D/n).read_bytes())
files=sorted(p for p in R.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
(R/'SHA256SUMS').write_bytes(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(R).as_posix()+'\n' for p in files).encode())
t.git('diff','--check');t.git('add','--sparse','--',rel)
assert all(x.startswith(rel+'/') for x in t.git('diff','--cached','--name-only').decode().splitlines())
if t.git('diff','--cached','--name-only').strip():print(t.git('commit','-m',sys.argv[1]).decode(),flush=True)
head=t.git('rev-parse','HEAD').decode().strip();t.git('push','origin','HEAD:refs/heads/'+t.BRANCH);t.git('fetch','--no-tags','origin',t.BRANCH)
assert t.git('rev-parse','origin/'+t.BRANCH).decode().strip()==head
for p in sorted(R.rglob('*')):
    if p.is_file():assert t.git('show',head+':'+p.relative_to(t.REPO).as_posix())==p.read_bytes()
pub=dict(schema='LANE_T_COLD_LIGHTWEIGHT_GIT_RAW_READBACK_V1',commit=head,branch=t.BRANCH,all_cold_index_script_SHA_blobs_readback_exact=True,heavy_archive_assets_pushed=False)
(D/'LAST_GITHUB_PUBLICATION.json').write_bytes((json.dumps(pub,indent=2)+'\n').encode());print(json.dumps(pub),flush=True)
names=sys.argv[2:]
if names:
    publish_tag=os.environ.get('LANE_T_COLD_PUBLISH_TAG','463600cb')
    assert publish_tag in ['463600cb','46bf3a69']
    config=json.loads((D/(publish_tag+'_CONFIG.json')).read_bytes())
    payload={n:base64.b64encode((R/n).read_bytes()).decode() for n in names}
    code=r'''
import pathlib,os,json,hashlib,base64,subprocess
B=pathlib.Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02');root=pathlib.Path(__ROOT__)
assert os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]'
m=json.loads(subprocess.check_output(['findmnt','-J','-T',str(root),'-o','TARGET,SOURCE,FSTYPE']))['filesystems'][0]
assert (m['target'],m['source'],m['fstype'])==('/root/share/mnt164','admin-wcx@10.208.130.164:/home/shared','fuse.sshfs')
records={}
for name,b64 in __PAYLOAD__.items():
 raw=base64.b64decode(b64);records[name]=dict(sha256=hashlib.sha256(raw).hexdigest(),path=__REL__+'/'+name)
 for parent in [B,root]:
  p=parent/name;assert not p.is_symlink()
  if p.exists():assert p.read_bytes()==raw
  else:
   with p.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
  assert p.read_bytes()==raw
proof=dict(__PUB__,records=records);raw=(json.dumps(proof,indent=2)+'\n').encode();name='LANE_T_COLD_PUBLICATION_'+__HEAD__[:12]+'.json'
for parent in [B,root]:
 p=parent/name
 if p.exists():assert p.read_bytes()==raw
 else:
  with p.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 assert p.read_bytes()==raw
print(json.dumps(proof))
'''
    for k,v in [('__ROOT__',config['target_root']),('__PAYLOAD__',payload),('__PUB__',pub),('__HEAD__',head),('__REL__',rel)]:code=code.replace(k,repr(v))
    r=t.remote(code,'LANE_T_COLD_PUBLICATION_'+head[:12],timeout=60,save_receipt=False)
    (D/'LAST_SHARED_PUBLICATION.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
