"""Main-started read-only snapshot publisher. Never a simulator/controller."""
import argparse,contextlib,datetime,fcntl,gzip,hashlib,importlib.util,json,os,pathlib,shutil,subprocess,sys,time,urllib.request,uuid
sys.dont_write_bytecode=True
P=pathlib.Path
GEN_SHA='9ad9cdf8db29eb062f8053b51b3396a1bac6ff9132f6ad0d89ac64aac58786d7'
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
START='<!-- DTC_PERIODIC_CURRENT_START -->';END='<!-- DTC_PERIODIC_CURRENT_END -->'
def encode(v):return(json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(p):return digest(P(p).read_bytes())
def read(p):return json.loads(P(p).read_bytes())
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def atomic(p,v):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name('.'+p.name+'.'+uuid.uuid4().hex);raw=v if isinstance(v,bytes)else encode(v)
 with tmp.open('xb')as h:h.write(raw);h.flush();os.fsync(h.fileno())
 os.replace(tmp,p);fd=os.open(p.parent,os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def coherent(p):
 p=P(p)
 for _ in range(3):
  with p.open('rb')as h:a=os.fstat(h.fileno());b=h.read();z=os.fstat(h.fileno())
  if(a.st_size,a.st_mtime_ns,a.st_ino)==(z.st_size,z.st_mtime_ns,z.st_ino)and len(b)==z.st_size:return b,json.loads(b)
 raise RuntimeError('NONATOMIC_SOURCE_WRITE '+str(p))
@contextlib.contextmanager
def lock(path):
 p=P(path);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('a+b')as h:
  fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:yield h
  finally:fcntl.flock(h,fcntl.LOCK_UN)
def load_generator(path):
 assert sha(path)==GEN_SHA,'GENERATOR_SOURCE_DRIFT'
 s=importlib.util.spec_from_file_location('qualified_readonly_report',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def result_delta(accepted,already):return sorted(set(accepted)-set(already))
def export_document(cohort,identity,value):
 raw,current=coherent(identity['path'])
 assert digest(raw)==identity['sha256']and current==value,'EXPORT_SOURCE_CHANGED '+cohort
 return dict(cohort=cohort,source=identity,result=value,original_utf8=raw.decode('utf-8'),original_bytes_reconstructible=True)
def safe_rel(name):
 p=P(name);assert not p.is_absolute()and name and '..'not in p.parts and '\\'not in name and not name.startswith('-');return p
def config(v):
 assert v['schema']=='DTC_PERIODIC_PUBLICATION_CONFIG_V1'
 assert set(v)<=set('schema root archive_root worktree branch remote repo review_relative output_root git_lock interval_seconds expected_initial_head generator_path generator_sha256 generator_tool_commit analysis_ready_path registry_path'.split()),'CONFIG_MUST_CONTAIN_PUBLIC_PATHS_AND_PINS_ONLY'
 assert v['interval_seconds']==1800 and v['generator_sha256']==GEN_SHA
 assert v['branch']=='hrl/dtc-l2-mlp-full-workload-exploration-v1'and v['remote']=='origin'and v['repo']=='swayhrl/accel-sim-framework'
 assert v['review_relative']=='docs/dtc_l1/review_packs/DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_V1'
 a=P(v['archive_root']).resolve();r=P(v['root']).resolve();w=P(v['worktree']).resolve();o=P(v['output_root']).resolve()
 assert w.is_relative_to(a)and o.is_relative_to(a)and not o.is_relative_to(r)and o!=w and not o.is_relative_to(w)
 assert P(v['git_lock']).resolve()==a/'coordinator/git.lock';assert v['generator_tool_commit']=='fce10d92eb09bc8f562b84a5a84b202bbf1ea385'
 return v

def stable_results(paths,known):
 rows={};values={}
 for cohort,path in paths.items():
  if not P(path).exists():continue
  raw,v=coherent(path);identity=dict(path=str(path),sha256=digest(raw),uuid=v.get('uuid'),cycles=v.get('cycles'),state=v.get('state'))
  if cohort in known:assert identity==known[cohort],'RESULT_REPLACEMENT_FORBIDDEN '+cohort
  rows[cohort]=identity;values[cohort]=v
 for cohort in known:assert cohort in rows,'PREVIOUS_RESULT_DISAPPEARED '+cohort
 return rows,values

def root_readme(previous,snapshot_relative,accepted_n,planned,stamp):
 current=(START+'\n# DTC L2 MLP full-workload exploration V1\n\n'
  f'Latest read-only snapshot: [{stamp}]({snapshot_relative}/README.md) · '
  f'[{accepted_n}/{planned} primary accepted cells]({snapshot_relative}/dashboard.html). '
  f'[Machine-readable report]({snapshot_relative}/report.json) · '
  f'[Snapshot member hashes]({snapshot_relative}/MEMBER_MANIFEST.json).\n\n'
  'Coverage is partial until all valid planned cells are accepted. Original negatives remain visible; '
  'independent R2 is supplemental and never replaces a primary negative. '
  'CH non-P0 controls may be absent; available-subset GMs are not final suite winners. '
  'Sources are coherent per file, not one global transaction. The old BATCH_STATE .88 label is historical, '
  'not evidence of the active admission policy. English v0.23 is unchanged.\n\n'
  'The root MEMBER_MANIFEST.json and historical checkpoint manifests describe their original snapshots; '
  'they are not manifests for later appended files. Use each snapshot MEMBER_MANIFEST.json.\n'+END)
 if START in previous:
  assert previous.count(START)==previous.count(END)==1
  return current+previous.split(END,1)[1]
 return current+'\n\n<details><summary>Historical root README, preserved in full</summary>\n\n'+previous+'\n</details>\n'

class Publisher:
 def __init__(self,cfg):
  self.cfg=config(cfg);self.root=P(cfg['root']);self.out=P(cfg['output_root']);self.w=P(cfg['worktree']);self.control=self.out/'control';self.control.mkdir(parents=True,exist_ok=True);self.statepath=self.control/'STATE.json';self.state=read(self.statepath)if self.statepath.exists()else dict(schema='DTC_PERIODIC_PUBLISHER_STATE_V1',known_results={},exported_primary=[],exported_supplemental=[],last_success=None,pending=None)
 def save(self,**kw):self.state.update(kw,updated_UTC=utc());atomic(self.statepath,self.state)
 def run(self,args,timeout=120,env=None):
  r=subprocess.run(args,capture_output=True,text=True,timeout=timeout,env=dict(os.environ if env is None else env,GIT_TERMINAL_PROMPT='0'))
  if r.returncode:raise RuntimeError('COMMAND_FAILED '+repr(args[:5])+' '+r.stderr[-3000:])
  return r.stdout.strip()
 def git(self,*args,timeout=120):return self.run(['git','-c','safe.directory='+str(self.w),'-C',str(self.w),*args],timeout)
 def clean(self):
  assert not self.git('diff','--name-only')and not self.git('diff','--cached','--name-only'),'GIT_TRACKED_OR_STAGED_DIRTY'
  assert self.git('branch','--show-current')==self.cfg['branch'],'WRONG_BRANCH'
  if self.state['last_success']is None and self.state['pending']is None:assert self.git('rev-parse','HEAD')==self.cfg['expected_initial_head'],'INITIAL_HEAD_DRIFT'
 def identities(self,matrix):
  paths={p['cohort']:self.root/'analysis'/(p['cohort']+'.RESULT.json')for p in matrix['points']}
  reg=read(self.cfg['registry_path'])['registered_future_requests'][REQ];supp={x['new_cohort']:self.root/'analysis'/(x['new_cohort']+'.RESULT.json')for x in reg.get('authorized_supplemental_trials',[])}
  assert not(set(paths)&set(supp)),'SUPPLEMENTAL_PRIMARY_UNION_FORBIDDEN'
  return paths,supp
 def generate(self):
  gen=load_generator(self.cfg['generator_path']);matrix=read(self.root/'control/MATRIX_CURRENT.json');primary,supp=self.identities(matrix);allpaths=dict(primary,**supp)
  before,values=stable_results(allpaths,self.state['known_results'])
  token=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:8];d=self.out/'snapshots'/token;d.mkdir(parents=True)
  (d/'.gitignore').write_text('!*.jsonl.gz\n')
  atomic(d/'PUBLISHER_CONFIG.json',self.cfg)
  env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',MPLCONFIGDIR=str(self.out/'matplotlib-cache'))
  self.run([sys.executable,self.cfg['generator_path'],'--root',str(self.root),'--output',str(d),'--tool-commit',self.cfg['generator_tool_commit']],timeout=240,env=env)
  report=read(d/'report.json');assert report['planned_cells']==len(matrix['points']);table={c['cohort']:c for profiles in report['table'].values()for cells in profiles.values()for c in cells.values()}
  assert set(table)==set(primary),'REPORT_PRIMARY_POPULATION_CHANGED'
  after,values=stable_results(allpaths,before)
  for c,row in table.items():
   if row['result_path']:
    assert c in after and row['result_sha256']==after[c]['sha256'],'RESULT_CHANGED_DURING_GENERATOR '+c
    assert row['accepted']==gen.accepted(values[c])
    assert row['uuid']==values[c].get('uuid')and row['raw_reported_cycles']==values[c].get('cycles')
   if row['accepted']:assert row['cycles']==values[c]['cycles']
  accepted=[c for c,row in table.items()if row['accepted']];new=result_delta(accepted,self.state['exported_primary'])
  filename='accepted_primary_results.jsonl.gz'if not self.state['exported_primary']else'new_accepted_primary_results.jsonl.gz'
  with(d/filename).open('wb')as raw:
   with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0)as z:
    for c in sorted(new):z.write(encode(export_document(c,after[c],values[c])).replace(b'\n',b'')+b'\n')
  supplemental=[];suppnew=[]
  for c,path in supp.items():
   v=values.get(c);item=dict(cohort=c,role='SUPPLEMENTAL_ONLY_NEVER_PRIMARY_UNION',state=v.get('state')if v else'PENDING',accepted=gen.accepted(v)if v else False,cycles=v.get('cycles')if v and gen.accepted(v)else None,source=after.get(c));supplemental.append(item)
   if v and item['accepted']and c not in self.state['exported_supplemental']:suppnew.append(c)
  atomic(d/'supplemental_results.json',dict(schema='SUPPLEMENTAL_SEPARATE_NO_PRIMARY_UNION_V1',rows=supplemental,primary_population_unchanged=True))
  with(d/'new_accepted_supplemental_results.jsonl.gz').open('wb')as raw:
   with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0)as z:
    for c in sorted(suppnew):z.write(encode(export_document(c,after[c],values[c])).replace(b'\n',b'')+b'\n')
  approved=[];ready=P(self.cfg['analysis_ready_path'])
  if ready.exists():
   raw,a=coherent(ready);assert a['schema']=='MAIN_APPROVED_ANALYSIS_PUBLICATION_V1'and a['status']=='MAIN_APPROVED_FOR_PUBLICATION'
   for item in a['files']:
    name=item['name'];assert P(name).name==name and name not in ['.','..']and not name.startswith('.')
    source=P(item['path']).resolve();assert source.is_relative_to(P(self.cfg['archive_root']).resolve())
    raw=source.read_bytes();assert digest(raw)==item['sha256'],'APPROVED_ANALYSIS_SHA_DRIFT'
    target=d/'approved_analysis'/name;assert not target.exists();target.parent.mkdir(exist_ok=True);target.write_bytes(raw);approved.append(dict(path='approved_analysis/'+name,source=str(source),sha256=digest(raw)))
   atomic(d/'APPROVED_ANALYSIS_READY.json',a)
  note=(f'# DTC periodic read-only snapshot {token}\n\nPrimary coverage: {len(accepted)}/{len(primary)} accepted; full primary states/cycles are in [report.json](report.json) and [dashboard](dashboard.html). This is a partial, time-labelled population. Raw negatives/HOLD/pending remain visible; missing CH variants are not imputed.\n\n'+f'This archive exports {len(new)} newly accepted primary structured RESULT documents; previous exports remain immutable. Supplementary R2 is separately listed in [supplemental_results.json](supplemental_results.json), never replacing or unioning with primary rows.\n\n'+'Source SHA/UUID/cycles were checked before and after generation. Per-file snapshots are coherent; there is no global transaction across independently changing files. The source BATCH_STATE .88 label is historical and does not identify active admission policy. English v0.23 remains unchanged.\n\n'+('Main-approved analysis files: '+', '.join('['+x['path']+']('+x['path']+')'for x in approved)if approved else'No Main-approved analysis READY file was available; this publication contains basic data and coverage only.')+'\n')
  (d/'README.md').write_text(note);atomic(d/'RESULT_IDENTITY_MANIFEST.json',dict(before=before,after=after,previous_results_unchanged=True,new_primary_exports=new,new_supplemental_exports=suppnew,primary_population=list(primary),source_transaction='PER_FILE_ONLY'))
  manifest=dict(schema='DTC_PERIODIC_SNAPSHOT_MEMBER_MANIFEST_V1',generator=dict(path=self.cfg['generator_path'],sha256=GEN_SHA,tool_commit=self.cfg['generator_tool_commit']),publisher_source_sha256=sha(__file__),files={str(p.relative_to(d)):dict(sha256=sha(p),bytes=p.stat().st_size)for p in sorted(d.rglob('*'))if p.is_file()},partial=report['partial'],primary_planned=len(primary),primary_accepted=len(accepted),supplemental_primary_union=False,old_root_manifests_are_historical=True,structured_export_original_bytes='original_utf8.encode(utf-8) reproduces source.sha256 exactly')
  atomic(d/'MEMBER_MANIFEST.json',manifest)
  assert sum(p.stat().st_size for p in d.rglob('*')if p.is_file())<=50*1024**2,'PUBLICATION_EXCEEDS50MiB_NO_TRUNCATION'
  return dict(token=token,directory=str(d),known_results=after,exported_primary=sorted(set(self.state['exported_primary'])|set(accepted)),exported_supplemental=sorted(set(self.state['exported_supplemental'])|set(suppnew)),accepted=len(accepted),planned=len(primary),report_utc=report['utc'])
 def stage_snapshot(self,snapshot):
  self.clean();rel=self.cfg['review_relative'];target=self.w/rel/'periodic'/snapshot['token'];assert not target.exists();shutil.copytree(snapshot['directory'],target)
  README=self.w/rel/'README.md';previous=README.read_text();new=root_readme(previous,'periodic/'+snapshot['token'],snapshot['accepted'],snapshot['planned'],snapshot['report_utc']);atomic(README,new.encode())
  pointer=self.w/rel/'PERIODIC_CURRENT.json';atomic(pointer,dict(snapshot='periodic/'+snapshot['token'],report='periodic/'+snapshot['token']+'/report.json',manifest='periodic/'+snapshot['token']+'/MEMBER_MANIFEST.json',partial=True))
  files=[str(p.relative_to(self.w))for p in sorted(target.rglob('*'))if p.is_file()]+[str(README.relative_to(self.w)),str(pointer.relative_to(self.w))]
  expected={p:sha(self.w/p)for p in files};base=self.git('rev-parse','HEAD');pending=dict(phase='COMMITTING',base_head=base,message='docs(dtc): periodic read-only snapshot '+snapshot['token'],files=files,file_sha256=expected,snapshot=snapshot)
  self.save(pending=pending,status='COMMITTING');self.finish_commit()
 def finish_commit(self):
  p=self.state['pending'];head=self.git('rev-parse','HEAD')
  if head==p['base_head']:
   staged=set(self.git('diff','--cached','--name-only').splitlines());assert staged<=set(p['files']),'UNRELATED_STAGED_CHANGES'
   dirty=set(self.git('diff','--name-only').splitlines());assert dirty<=set(p['files']),'UNRELATED_TRACKED_CHANGES'
   assert all(sha(self.w/f)==h for f,h in p['file_sha256'].items()),'OWN_SNAPSHOT_DRIFT'
   self.git('add','--',*p['files']);assert set(self.git('diff','--cached','--name-only').splitlines())==set(p['files'])
   self.git('commit','-m',p['message'],'--',*p['files']);head=self.git('rev-parse','HEAD')
  assert self.git('log','-1','--format=%P',head)==p['base_head']and self.git('log','-1','--format=%s',head)==p['message'],'UNEXPECTED_HEAD_NO_RESET'
  assert set(self.git('diff-tree','--no-commit-id','--name-only','-r',head).splitlines())==set(p['files'])
  for f,h in p['file_sha256'].items():assert digest(subprocess.run(['git','-c','safe.directory='+str(self.w),'-C',str(self.w),'show',head+':'+f],check=True,capture_output=True,timeout=30).stdout)==h
  p.update(phase='PENDING_PUSH',commit=head);self.save(pending=p,status='PENDING_PUSH')
 def push_verify(self):
  p=self.state['pending'];assert p['phase']=='PENDING_PUSH';commit=p['commit'];assert self.git('rev-parse','HEAD')==commit,'PENDING_COMMIT_HEAD_CHANGED_NO_RESET';self.clean_pending()
  ref='refs/heads/'+self.cfg['branch'];remote=self.git('ls-remote',self.cfg['remote'],ref,timeout=45).split()
  if not remote or remote[0]!=commit:self.git('push',self.cfg['remote'],commit+':'+ref,timeout=90)
  assert self.git('ls-remote',self.cfg['remote'],ref,timeout=45).split()[0]==commit,'REMOTE_HEAD_NOT_CONFIRMED'
  rootrel=self.cfg['review_relative'];snaprel=rootrel+'/periodic/'+p['snapshot']['token'];checks={}
  for rel in[rootrel+'/README.md',snaprel+'/report.json',snaprel+'/MEMBER_MANIFEST.json']:
   url='https://raw.githubusercontent.com/'+self.cfg['repo']+'/'+commit+'/'+rel
   with urllib.request.urlopen(url,timeout=20)as h:raw=h.read(16*1024**2+1)
   assert len(raw)<=16*1024**2 and digest(raw)==p['file_sha256'][rel],'HTTPS_READBACK_MISMATCH '+rel
   checks[rel]=dict(url=url,sha256=digest(raw))
  proof=dict(status='PUSH_LSREMOTE_AND_HTTPS_VERIFIED',commit=commit,UTC=utc(),files=checks);atomic(P(p['snapshot']['directory'])/'PUBLICATION_READBACK.json',proof)
  s=p['snapshot'];self.save(pending=None,status='SUCCESS',last_error=None,error_UTC=None,known_results=s['known_results'],exported_primary=s['exported_primary'],exported_supplemental=s['exported_supplemental'],last_success=proof,last_snapshot=s['directory'],next_snapshot_epoch=time.time()+self.cfg['interval_seconds'])
 def clean_pending(self):
  assert self.git('branch','--show-current')==self.cfg['branch'],'WRONG_PENDING_BRANCH'
  assert not self.git('diff','--name-only')and not self.git('diff','--cached','--name-only'),'DIRTY_DURING_PENDING_PUSH'
 def tick(self):
  with lock(self.cfg['git_lock']):
   if self.state['pending']:
    if self.state['pending']['phase']=='COMMITTING':self.finish_commit()
    self.push_verify();return
   self.clean();snapshot=self.generate();self.stage_snapshot(snapshot);self.push_verify()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--config',required=True);ap.add_argument('--once',action='store_true');a=ap.parse_args();cfg=config(read(a.config));out=P(cfg['output_root']);control=out/'control';control.mkdir(parents=True,exist_ok=True)
 with lock(control/'publisher.process.lock'):
  publisher=Publisher(cfg);f=P('/proc/self/stat').read_text().rsplit(')',1)[1].split();atomic(control/'PID.json',dict(pid=os.getpid(),start_ticks=int(f[19]),source_sha256=sha(__file__),config_sha256=sha(a.config),UTC=utc(),not_a_model_controller=True))
  while True:
   if(control/'STOP').exists():publisher.save(status='STOPPED_NATURALLY',stopped_UTC=utc());return
   due=publisher.state.get('next_snapshot_epoch',0)
   if publisher.state['pending']or time.time()>=due:
    try:publisher.tick()
    except Exception as e:publisher.save(status='PUBLICATION_RETRY_OR_HOLD',last_error=repr(e),error_UTC=utc());print(json.dumps(dict(status='PUBLICATION_RETRY_OR_HOLD',error=repr(e))),flush=True)
   if a.once:return
   time.sleep(30)
if __name__=='__main__':main()
