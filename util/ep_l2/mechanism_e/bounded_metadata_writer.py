"""Root-invoked bounded metadata writer/publisher. No action on import.
Engineering metadata only. Never controller, app, lease, registry or Q mutation.
All original terminal/raw are external immutable references, never copied here.
"""
import json,hashlib,os,stat,tempfile,subprocess,struct,fcntl
from pathlib import Path
MIB=2**20
ROLE_CAP={'review':64*MIB,'compact':8*MIB,'control':2*MIB}
TARGETS=('V8_TAGPRESSURE_vectorAdd_4M_F','V8_TAGPRESSURE_convolutionSeparable_F')
OPTIONS=['-c','gc.auto=0','-c','maintenance.auto=false','-c','fetch.writeCommitGraph=false','-c','gc.writeCommitGraph=false','-c','submodule.recurse=false','-c','fetch.recurseSubmodules=false']
def need(ok,msg):
 if not ok:raise ValueError(msg)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def fsync_dir(p):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def regular_bytes(p,cap):
 p=Path(p);s=p.lstat();need(stat.S_ISREG(s.st_mode) and not p.is_symlink() and 0<s.st_size<=cap,'bounded regular metadata only')
 b=p.read_bytes();t=p.stat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns),'metadata changed during bounded read');return b
class Writer:
 def __init__(self,root,condition_id,repo,allowed_roots,*,create=False,publication_lock_path='/workspace/ep_l2_ms20261019_shared/E2_GIT_PUBLICATION.lock'):
  self.root=Path(root).resolve();self.cid=condition_id;self.repo=Path(repo).resolve();self.allowed=[Path(x).resolve() for x in allowed_roots];self.journal=self.root/'JOURNAL.jsonl';self.store=self.root/'bodies';self.publication_lock_path=Path(publication_lock_path)
  need(condition_id in TARGETS,'exact remaining2 only');need(self.root.is_relative_to(Path('/workspace/ep_l2_ms20261019_e_results')) or self.root.is_relative_to(Path('/tmp')),'owned accounting or synthetic/tmp root only')
  if create:
   need(not self.root.exists(),'fresh mode root required');self.store.mkdir(parents=True);self._append({'event':'BEGIN','condition_id':condition_id,'physical_cap_bytes':96*MIB,'generation_per_condition_bytes':160*MIB,'generation_batch_bytes':640*MIB})
  need(self.journal.is_file(),'Writer.begin must run before physical96 admission')
  self.state()
 def state(self):
  with self.journal.open('rb') as lock:
   fcntl.flock(lock,fcntl.LOCK_SH);return self._state_unlocked()
 def _state_unlocked(self):
  b=regular_bytes(self.journal,2*MIB);prev='0'*64;records=[];bodies={};aliases={};newdirs=set();tree_reserved=tree_count=publications=0;roles={k:0 for k in ROLE_CAP}
  for line in b.splitlines():
   x=json.loads(line);need(x.pop('previous')==prev,'writer journal chain differs');prev=digest(line);records.append(x)
   if x['event']=='BODY':
    need(x['sha256'] not in bodies,'duplicate body charge');bodies[x['sha256']]=x;roles[x['role']]+=x['bytes']
   elif x['event']=='ALIAS':aliases.setdefault(x['sha256'],set()).add(x['path']);newdirs.update(x['planned_new_directories'])
   elif x['event']=='PUBLICATION':tree_reserved+=x['tree_upper_bytes'];tree_count+=x['tree_count'];publications+=1
  need(records and records[0]['event']=='BEGIN' and records[0]['condition_id']==self.cid,'actual mode journal condition differs')
  need(tree_reserved<=4*MIB and tree_count<=128 and publications<=2,'cumulative Git tree/commit fence changed')
  need(all(len(v)<=5 for v in aliases.values()) and len(newdirs)<=64,'bounded aliases/directories changed')
  roles['control']+=len(b)
  need(all(roles[k]<=ROLE_CAP[k] for k in roles),'metadata retention role cap HOLD')
  return {'head':prev,'records':records,'bodies':bodies,'role_bytes':roles,'journal_bytes':len(b),'aliases':aliases,'newdirs':newdirs,'tree_reserved':tree_reserved,'tree_count':tree_count,'publications':publications}
 def _append(self,event):
  with self.journal.open('a+b') as f:
   fcntl.flock(f,fcntl.LOCK_EX);f.seek(0);old=f.read();previous=digest(old.splitlines()[-1]) if old else '0'*64
   line=canonical(dict(event,previous=previous))+b'\n'
   if old:
    state=self._state_unlocked();need(state['role_bytes']['control']+len(line)<=ROLE_CAP['control'],'new journal/control cap HOLD before write')
    extra=event.get('bytes',0) if event['event']=='BODY' else 0
    if state['publications'] or event['event']=='PUBLICATION':need(sum(x['bytes'] for x in state['bodies'].values())+state['journal_bytes']+len(line)+extra<=12*MIB,'all future body/control/journal12MiB cap HOLD before write')
    if event['event']=='PUBLICATION':need(state['publications']<2 and state['tree_reserved']+event['tree_upper_bytes']<=4*MIB and state['tree_count']+event['tree_count']<=128,'cumulative Git publication attempt/tree limit HOLD before mutation')
   else:need(event['event']=='BEGIN','journal must begin explicitly')
   f.seek(0,os.SEEK_END);f.write(line);f.flush();os.fsync(f.fileno())
  fsync_dir(self.root)
 def activation_candidate(self):
  state=self.state();begin=self.journal.read_bytes().splitlines()[0]
  return {'schema':'E2_R5_BOUNDED_METADATA_WRITER_ACTIVATED_BEFORE_FORECAST_V1','status':'ACTUAL_BEGIN_ROOT_REVIEW_REQUIRED','condition_id':self.cid,'ledger_root':str(self.root),'repo':str(self.repo),'allowed_roots':[str(x) for x in self.allowed],'writer_source_ref':{'path':str(Path(__file__).resolve()),'sha256':digest(Path(__file__).read_bytes())},'journal_begin_sha256':digest(begin),'root_actual_activation_reviewed':False,'generation_batch_unchanged':640*MIB,'current_journal_control_bytes':state['journal_bytes']}
 def allowed_path(self,p):
  p=Path(p).absolute();need(not p.is_symlink() and any(p.is_relative_to(r) for r in self.allowed),'outside exact owner allowed paths');need(p.parent.resolve()==p.parent,'no symlink parent path');return p
 def _declare(self,b,role):
  need(role in ROLE_CAP and type(b)is bytes and b and len(b)<=64*MIB,'complete metadata body cap HOLD before write; never truncate')
  s=self.state();sha=digest(b)
  if sha in s['bodies']:need(s['bodies'][sha]['bytes']==len(b),'body identity collision');return sha
  need(len(b)<=ROLE_CAP[role],'role-specific body cap HOLD before write')
  need(len(s['bodies'])<63,'metadata body versions cap HOLD; journal snapshot final slot reserved')
  need(s['role_bytes'][role]+len(b)+(1024 if role=='control' else 0)<=ROLE_CAP[role],'aggregate role+prospective journal cap HOLD before write')
  self._append({'event':'BODY','sha256':sha,'bytes':len(b),'role':role});return sha
 def before_alias(self,path,sha):
  dest=self.allowed_path(path);state=self.state();need(sha in state['bodies'],'alias must reference charged complete body')
  aliases=state['aliases'].get(sha,set())
  if str(dest) in aliases:return
  need(len(aliases)<5,'six physical/path slots including canonical body exceeded: HOLD')
  dirs=[];cur=dest.parent
  while not cur.exists():dirs.append(str(cur));cur=cur.parent
  need(len(state['newdirs']|set(dirs))<=64,'new directory cap HOLD before mkdir/copy')
  self._append({'event':'ALIAS','sha256':sha,'path':str(dest),'planned_new_directories':dirs})
 def _body(self,b,role):
  sha=self._declare(b,role);p=self.store/sha
  if p.exists():need(regular_bytes(p,64*MIB)==b,'immutable body changed');return p
  # Exactly one persistent immutable body inode. Atomic temp installation does
  # not create another full data copy: rename moves this same inode.
  fd,t=tempfile.mkstemp(prefix='.body-',dir=self.store)
  try:
   with os.fdopen(fd,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
   os.rename(t,p);fsync_dir(self.store)
  finally:
   if os.path.exists(t):os.unlink(t)
  return p
 def import_existing(self,path,role):
  p=self.allowed_path(path);b=regular_bytes(p,ROLE_CAP[role]);sha=self._declare(b,role);self.before_alias(p,sha);target=self.store/sha
  # Existing fresh one-off report becomes an immutable same-device alias.
  # Never import mutable run_status/summary/raw/trace or changing STATUS here.
  need(p.name not in ('run_status.json','terminal_summary.json','raw.log'),'original runtime evidence must remain referenced only')
  need(p.stat().st_dev==self.store.stat().st_dev,'no cross-device copying')
  if target.exists():need(regular_bytes(target,64*MIB)==b,'immutable body changed')
  else:os.chmod(p,0o444);os.link(p,target);fsync_dir(self.store)
  return {'path':str(target),'sha256':sha,'bytes':len(b)}
 def write_bytes(self,path,b,role='control'):
  dest=self.allowed_path(path);body=self._body(b,role);self.before_alias(dest,digest(b));dest.parent.mkdir(parents=True,exist_ok=True);need(dest.parent.stat().st_dev==body.stat().st_dev,'same-device only')
  # Atomic alias replacement never truncates an inode used by prior evidence.
  fd,tmp=tempfile.mkstemp(prefix='.alias-',dir=dest.parent);os.close(fd);os.unlink(tmp)
  try:os.link(body,tmp);os.replace(tmp,dest);fsync_dir(dest.parent)
  finally:
   if os.path.exists(tmp):os.unlink(tmp)
  return {'path':str(dest),'sha256':digest(b),'bytes':len(b)}
 def write_json(self,path,obj,role='control'):return self.write_bytes(path,(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode(),role)
 def copy(self,source,destination,role='control'):
  src=self.allowed_path(source);return self.write_bytes(destination,regular_bytes(src,ROLE_CAP[role]),role)
 def git(self,*args,input=None):return subprocess.check_output(['git',*OPTIONS,*args],cwd=self.repo,input=input)
 def _hooks(self):
  result=subprocess.run(['git','config','--path','--get','core.hooksPath'],cwd=self.repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  need(result.returncode in (0,1),'hooks config read failed')
  hp=Path(result.stdout.strip()) if result.returncode==0 else Path(self.git('rev-parse','--git-path','hooks').decode().strip());hp=hp if hp.is_absolute() else self.repo/hp
  if hp.exists():
   entries=list(hp.iterdir());need(len(entries)<=64,'hook inventory cap')
   need(not any(p.is_file() and not p.name.endswith('.sample') and os.access(p,os.X_OK) for p in entries),'actual required hooks present: HOLD; do not bypass')
  sign=subprocess.run(['git','config','--bool','--get','commit.gpgsign'],cwd=self.repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  need(sign.returncode in (0,1) and sign.stdout.strip() not in ('true','yes','1'),'required signing needs separate bounded review; do not bypass')
 def publication_check(self,paths):
  s=self.state();need(sum(x['bytes'] for x in s['bodies'].values())+s['journal_bytes']<=12*MIB,'complete publication body aggregate>12MiB: HOLD, preserve terminal/raw')
  need(0<len(paths)<=64,'exact <=64 publication files');rels=[];children={}
  for path in paths:
   p=self.allowed_path(path);need(p.is_relative_to(self.repo),'published path outside original E tree');b=regular_bytes(p,64*MIB);need(digest(b) in s['bodies'],'root writer must register every complete publication body first')
   rel=p.relative_to(self.repo);rels.append(str(rel))
   for i in range(len(rel.parts)):children.setdefault('/'.join(rel.parts[:i]),set()).add(rel.parts[i])
  need(len(children)<=64,'ancestor tree count HOLD')
  self._hooks()
  attrs=self.git('check-attr','filter','working-tree-encoding','--',*rels).decode().splitlines();need(all(x.rsplit(': ',1)[-1] in ('unspecified','unset') for x in attrs),'metadata filter/encoding changes require bounded review')
  idx=Path(self.git('rev-parse','--git-path','index').decode().strip());idx=idx if idx.is_absolute() else self.repo/idx;b=regular_bytes(idx,2*MIB);need(b[:4]==b'DIRC' and struct.unpack('!I',b[4:8])[0] in (2,3),'new index layout needs own exact bound')
  split=subprocess.run(['git','config','--bool','--get','core.splitIndex'],cwd=self.repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);need(split.returncode in (0,1) and split.stdout.strip() not in ('true','yes','1'),'split index not covered')
  objects=[('HEAD:'+d if d else 'HEAD^{tree}') for d in children]
  lines=self.git('cat-file','--batch-check',input=('\n'.join(objects)+'\n').encode()).decode().splitlines();need(len(lines)==len(objects),'tree-size response differs')
  total=0;newdirs=0
  for (d,names),line in zip(children.items(),lines):
   fields=line.rsplit(' ',2)
   if line.endswith(' missing'):base=0;newdirs+=1
   else:need(len(fields)==3 and fields[-2]=='tree','non-tree ancestor metadata');base=int(fields[-1])
   total+=base+sum(len(n.encode())+32 for n in names)
  need(total<=2*MIB and s['tree_reserved']+total<=4*MIB and s['tree_count']+len(children)<=128 and s['publications']<2 and newdirs<=64,'cumulative tree/commit sizing or publication attempt HOLD')
  futureindex=len(b)+sum(len(r.encode())+256 for r in rels)+len(children)*4096
  need(futureindex<=2*MIB,'index rewrite upper bound HOLD')
  return {'status':'BOUNDED_METADATA_PUBLICATION_CHECK_PASS','aggregate_body_bytes':sum(x['bytes'] for x in s['bodies'].values())+s['journal_bytes'],'distinct_body_versions':len(s['bodies'])+1,'paths':rels,'index_bytes':len(b),'index_rewrite_upper_bound_bytes':futureindex,'tree_uncompressed_upper_bound_bytes':total,'tree_count':len(children),'new_directory_count':newdirs,'maximum_publication_attempts':2,'physical_cap_bytes':96*MIB,'maximum_body_copies':6,'nonbody_cap_bytes':24*MIB,'generation_reserve_bytes':640*MIB,'hooks_bypassed':False}
 def publish(self,message,paths,*,branch='hrl/ep-l2-ms20261019-e-eval-v1',remote='origin'):
  with self.publication_lock_path.open('a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX);return self._publish_locked(message,paths,branch=branch,remote=remote)
 def _publish_locked(self,message,paths,*,branch,remote):
  need(branch=='hrl/ep-l2-ms20261019-e-eval-v1' and remote=='origin' and len(message.encode())<=4096,'exact original publication destination')
  proof=self.publication_check(paths);self._append({'event':'PUBLICATION','tree_upper_bytes':proof['tree_uncompressed_upper_bound_bytes'],'tree_count':proof['tree_count'],'failed_attempt_still_consumed':True});self.git('add','-f','--',*proof['paths']);staged=self.git('diff','--cached','--name-only').decode().splitlines();need(staged and set(staged)<=set(proof['paths']),'unrelated staged source: HOLD')
  self.git('commit','-m',message);head=self.git('rev-parse','HEAD').decode().strip();self.git('push',remote,'HEAD:refs/heads/'+branch)
  advertised=self.git('ls-remote','--heads',remote,'refs/heads/'+branch).decode().split();need(advertised and advertised[0]==head,'actual remote branch differs')
  # Own immutable object is already complete locally; no foreign HEAD/tags or
  # auto-maintenance graph/pack work is fetched into this constrained pipeline.
  self.git('fetch','--no-auto-maintenance','--no-tags','--no-recurse-submodules',remote,head);need(self.git('rev-parse','FETCH_HEAD').decode().strip()==head,'actual own-commit readback differs')
  for rel in proof['paths']:need(self.git('show',head+':'+rel)==regular_bytes(self.repo/rel,64*MIB),'actual published byte mismatch')
  return {'remote_commit':head,'verified':True,'verified_paths':proof['paths'],'actual_remote_branch_verified':True,'bounded_publication_proof':proof}
