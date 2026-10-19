import pathlib,sys,json,hashlib,subprocess,base64
import tls_target as t
sys.path.insert(0,'D:/repo/storage-ops-174new-164-exec-v1/.git')
from storage_ops_git_hashes import staged_checks
B=t.BASE.relative_to(t.REPO).as_posix()
assert t.git('branch','--show-current').decode().strip()==t.BRANCH
assert all((t.BASE/n).is_file() for n in sys.argv[2:])
t.git('diff','--check');t.git('add','--sparse','--',B)
for p in t.BASE.rglob('*.csv'):t.git('add','--sparse','-f','--',p.relative_to(t.REPO).as_posix())
assert all(n.startswith(B+'/') for n in t.git('diff','--cached','--name-only').decode().splitlines())
(t.BASE/'SHA256SUMS').write_bytes(''.join(staged_checks(B)).encode());t.git('add','--sparse','--',B+'/SHA256SUMS')
if t.git('diff','--cached','--name-only').strip():print(t.git('commit','-m',sys.argv[1]).decode(),flush=True)
head=t.git('rev-parse','HEAD').decode().strip();print(t.git('push','-u','origin','HEAD:refs/heads/'+t.BRANCH).decode(),flush=True)
t.git('fetch','--no-tags','origin',t.BRANCH);assert t.git('rev-parse','origin/'+t.BRANCH).decode().strip()==head
paths=t.git('ls-tree','-r','--name-only',head,'--',B).decode().splitlines()
specs=''.join(head+':'+p+'\n' for p in paths).encode()
blobs=subprocess.run(['git','cat-file','--batch'],input=specs,cwd=t.REPO,capture_output=True,check=True).stdout
pos=0
for p in paths:
 end=blobs.index(b'\n',pos);header=blobs[pos:end].split();assert len(header)==3 and header[1]==b'blob',p
 size=int(header[2]);start=end+1;assert blobs[start:start+size]==(t.REPO/p).read_bytes(),p
 assert blobs[start+size:start+size+1]==b'\n';pos=start+size+1
assert pos==len(blobs)

publication=dict(schema='TLS_V10_TARGET_GIT_PUBLICATION',commit=head,branch=t.BRANCH,receipt_directory=B,exact_remote_Git_readback=True)
(t.META/'last_publication.json').write_bytes((json.dumps(publication,indent=2)+'\n').encode());print(json.dumps(publication),flush=True)
if len(sys.argv)>2:
 binding=t.get('TLS_V10_TARGET_ROOT_BINDING.json');root=binding['archive_root_on_174new'];assert root.startswith(t.STORAGE+'/tls_v10/')
 records={n:dict(path=B+'/'+n,sha256=t.sha(t.BASE/n),raw64=base64.b64encode((t.BASE/n).read_bytes()).decode()) for n in sys.argv[2:]}
 code=r'''
import pathlib,json,hashlib,base64,os,datetime
root=pathlib.Path(__ROOT__);bridge=pathlib.Path(__B__);records=__RECORDS__;proof=__PROOF__
for n,item in records.items():
 raw=base64.b64decode(item.pop('raw64'));assert hashlib.sha256(raw).hexdigest()==item['sha256'];actual=n
 if any((p/n).exists() and (p/n).read_bytes()!=raw for p in [root,bridge]):actual=proof['commit'][:12]+'__'+n
 item['control_filename']=actual
 for parent in [root,bridge]:
  p=parent/actual;assert not p.is_symlink()
  if p.exists():assert p.read_bytes()==raw
  else:
   with p.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
  assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
pub=dict(proof);pub.update(schema='TLS_V10_TARGET_CONTROL_PUBLICATION',records=records);raw=(json.dumps(pub,indent=2)+'\n').encode();name='TLS_V10_TARGET_CONTROL_'+proof['commit'][:12]+'_PUBLICATION.json'
for parent in [root,bridge]:
 p=parent/name
 if p.exists():assert p.read_bytes()==raw
 else:
  with p.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 assert p.read_bytes()==raw and isinstance(json.loads(raw),dict)
print(json.dumps(pub))
'''.replace('__ROOT__',repr(root)).replace('__B__',repr(t.BRIDGE)).replace('__RECORDS__',repr(records)).replace('__PROOF__',repr(publication))
 t.remote(code,'TLS_V10_TARGET_CONTROL_'+head[:12]+'_PUBLICATION',90)
