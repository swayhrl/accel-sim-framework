"""Authorized namespace-only READY CAS emitter. No Git or model operations."""
import contextlib,fcntl,hashlib,json,os,pathlib,uuid
P=pathlib.Path
PREFIX='AUTO_DERIVED35_V1_'
STATUS='auto_derived35_v1_status'
def encode(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(p):return digest(P(p).read_bytes())
def read(p):return json.loads(P(p).read_bytes())
def atomic(p,v):
 p=P(p);tmp=p.with_name('.'+p.name+'.'+uuid.uuid4().hex);raw=v if isinstance(v,bytes) else encode(v)
 with tmp.open('xb') as h:h.write(raw);h.flush();os.fsync(h.fileno())
 os.replace(tmp,p)
 fd=os.open(p.parent,os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def projection(v):
 v=dict(v);v['files']=[x for x in v['files'] if not x['name'].startswith(PREFIX)];v.pop(STATUS,None);return v
def owned(v):return {'files':[x for x in v['files'] if x['name'].startswith(PREFIX)],STATUS:v.get(STATUS)}
def emit(ready,authorization,emitter_state,items,status,daemon,config,receipt):
 a=read(authorization);assert a['schema']=='DTC_AUTO_ANALYSIS_READY_AUTHORIZATION_V1' and a['authorized'] is True
 assert a['namespace']==PREFIX and str(ready)==a['ready_path'];assert sha(daemon)==a['daemon_sha256'] and sha(config)==a['config_sha256'],'AUTHORIZED_SOURCE_DRIFT'
 if a['publication_receipt_path']:
  assert str(receipt)==a['publication_receipt_path'] and sha(receipt)==a['publication_receipt_sha256'],'AUTHORIZED_PUBLIC_RECEIPT_DRIFT'
 assert all(x['name'].startswith(PREFIX) and P(x['name']).name==x['name'] for x in items)
 assert len({x['name'] for x in items})==len(items)
 output=P(a['output_root']).resolve();payload=0
 for x in items:
  p=P(x['path']).resolve();assert p.is_relative_to(output) and '/runs/' in str(p) and sha(p)==x['sha256'],'NONIMMUTABLE_OR_CHANGED_PAYLOAD';payload+=p.stat().st_size
 assert payload<=1048576,'AUTO_NAMESPACE_EXCEEDS_1MiB'
 sp=P(emitter_state);lock=P(a['ready_lock_path']);lock.parent.mkdir(parents=True,exist_ok=True)
 with lock.open('a+b') as h:
  fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB)
  raw=P(ready).read_bytes();v=json.loads(raw);st=read(sp) if sp.exists() else {'owned':a.get('initial_owned',{'files':[],STATUS:None}),'pending':None}
  assert digest(encode(projection(v)))==a['base_projection_sha256'],'UNKNOWN_READY_BASE_MODIFICATION_HOLD'
  pending=st.get('pending')
  if pending:
   if digest(raw)==pending['new_sha256']:st={'owned':owned(pending['new']),'pending':None};atomic(sp,st)
   elif digest(raw)==pending['old_sha256']:
    atomic(ready,encode(pending['new']));v=pending['new'];raw=encode(v);st={'owned':owned(v),'pending':None};atomic(sp,st)
   else:raise AssertionError('READY_CHANGED_DURING_INTERRUPTED_CAS_HOLD')
  assert owned(v)==st['owned'],'UNKNOWN_READY_NAMESPACE_MODIFICATION_HOLD'
  if not sp.exists():assert digest(raw)==a['base_ready_sha256'],'FIRST_READY_BYTES_CHANGED_HOLD'
  new=projection(v);new['files']+=items;new[STATUS]=status
  assert projection(new)==projection(v),'NAMESPACE_ONLY_INVARIANT'
  if new==v:return {'changed':False,'sha256':digest(raw),'payload_bytes':payload}
  nb=encode(new);intent={'owned':st['owned'],'pending':{'old_sha256':digest(raw),'new_sha256':digest(nb),'new':new}};atomic(sp,intent)
  assert P(ready).read_bytes()==raw,'READY_CAS_CONFLICT_HOLD'
  atomic(ready,nb);atomic(sp,{'owned':owned(new),'pending':None})
  return {'changed':True,'sha256':digest(nb),'payload_bytes':payload}
