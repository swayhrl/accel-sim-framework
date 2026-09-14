import datetime,hashlib,json,os,re,secrets,shutil
from pathlib import Path
STATUSES={'FORMAL','MECHANISM_ONLY','DIAGNOSTIC','PRE_FIX','OBSOLETE','INVALID'}
TOP=['schema_version','run_id','created_at_utc','scientific_status','producer','git','model','input','scenario','runtime','capture','artifacts']
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def valid_sha(x):return isinstance(x,str) and bool(re.fullmatch('[0-9a-f]{64}',x))
def validate_manifest(m):
 if not isinstance(m,dict) or set(m)!=set(TOP):raise ValueError('top-level schema')
 if m['schema_version']!=1 or m['scientific_status'] not in STATUSES:raise ValueError('status/schema')
 required={'producer':['hostname','gpu_name','gpu_uuid','driver','cuda'],'git':['repository','commit','dirty'],'model':['model_id','revision','asset_receipt_sha256'],'input':['binding_id','authority_status','receipt_sha256','token_ids_sha256_or_semantic_hash'],'scenario':['batch','prefill_tokens','decode_tokens','input_class','phase'],'runtime':['python','torch','transformers','dtype','attention_backend'],'capture':['instrument','tool_version','tool_identity_sha256_if_applicable','target','exact_argv']}
 for k,ks in required.items():
  if not isinstance(m[k],dict) or any(x not in m[k] for x in ks):raise ValueError('identity '+k)
 if not isinstance(m['artifacts'],list):raise ValueError('artifacts')
def run_id(model,scenario,phase,instrument,target):
 slug=lambda x:re.sub('[^a-z0-9]+','-',x.lower()).strip('-')
 return 'C16R_'+ '_'.join(map(slug,[model,scenario,phase,instrument,target]))+'_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+secrets.token_hex(6)
def inventory(root):
 out=[]
 for q in sorted(Path(root).rglob('*')):
  if q.is_symlink():raise ValueError('symlink')
  if q.is_file() and q.name not in {'CAPTURING','RUN_MANIFEST.json','LOCAL_CLOSE_RECEIPT.json','READY'}:out.append({'relative_path':q.relative_to(root).as_posix(),'size_bytes':q.stat().st_size,'sha256':sha(q)})
 return out
def atomic_json(path,obj):
 path=Path(path);tmp=path.with_name(path.name+'.tmp');data=(json.dumps(obj,indent=2,sort_keys=True)+'\n').encode();fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 try:os.write(fd,data);os.fsync(fd)
 finally:os.close(fd)
 os.replace(tmp,path)
def finalize(staging,ready,manifest_path,run):
 s=Path(staging);r=Path(ready);m=json.loads(Path(manifest_path).read_text());validate_manifest(m)
 if m['run_id']!=run or s.name!=run or (s/'CAPTURING').exists():raise ValueError('run/state')
 obs=inventory(s);decl=m['artifacts']
 if decl and decl!=obs:raise ValueError('artifact mismatch')
 if not obs:raise ValueError('missing artifact')
 dest=r/run
 if dest.exists():raise FileExistsError('collision')
 m['artifacts']=obs;atomic_json(s/'RUN_MANIFEST.json',m);ms=sha(s/'RUN_MANIFEST.json');close={'schema_version':1,'run_id':run,'manifest_sha256':ms,'file_count':len(obs),'total_bytes':sum(x['size_bytes'] for x in obs),'closed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};atomic_json(s/'LOCAL_CLOSE_RECEIPT.json',close);(s/'READY').write_text('READY\n');shutil.move(s,dest);return dest,close
def publish_argv(alias,destroot,run,source):
 if alias!='hrl174new' or not re.fullmatch(r'C16R_[A-Za-z0-9_.-]+',run) or '..' in destroot:raise ValueError('unsafe')
 dest=destroot.rstrip('/')+'/inbox/'+run+'.partial/'
 if '/raw/' in dest:raise ValueError('direct raw')
 # Phase B admitted SSHFS payload semantics, not producer UID/GID/mode
 # preservation.  `-a` causes remote chown failures there, so transport is
 # recursive, resume-capable and copy-only without source metadata mutation.
 return ['rsync','-r','--partial','--append-verify','--protect-args','--no-owner','--no-group','--no-perms','--omit-dir-times',str(source).rstrip('/')+'/',alias+':'+dest]
def validate_ack(a,run,manifest_sha,dest,file_count,total_bytes):
 req={'schema_version','run_id','source_manifest_sha256','destination_manifest_or_verification_sha256','file_count','total_bytes','destination_raw_path','verified_at_utc','verification_status','catalog_entry_sha256'}
 if set(a)!=req or a['schema_version']!=1 or a['verification_status']!='PASS' or a['run_id']!=run or a['source_manifest_sha256']!=manifest_sha or a['destination_raw_path']!=dest or a['file_count']!=file_count or a['total_bytes']!=total_bytes or not valid_sha(a['destination_manifest_or_verification_sha256']) or not valid_sha(a['catalog_entry_sha256']):raise ValueError('ack binding')
def transition(ready,transferred,run):
 s=Path(ready)/run;d=Path(transferred)/run
 if not s.is_dir() or d.exists(): raise ValueError('transition')
 shutil.move(s,d)
 return d
def cleanup(root):return {'mode':'REPORT_ONLY','files':inventory(root),'deleted':False}
