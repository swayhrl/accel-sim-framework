#!/usr/bin/env python3
"""Main-enabled read-only result watch and narrow review-package publication.

This does not launch/consume/register science or modify runtime/Core ledgers.
Without an explicit Main enable file it cannot execute any Git command.
"""
import argparse, collections, contextlib, hashlib, importlib.util, json, os
import pathlib, re, shutil, subprocess, time, fcntl, sys
sys.dont_write_bytecode=True
AUTHORITY='18b1ee9d339902e555fc2e04ef51c84f77dfe1b1'
MATRIX_SHA='11d5bfc7642a6262fde719119603c940ca64eb98de69d2554124f24b2302a3ee'
BRANCH='DTC_CONTROLLED_ORACLE_IMPLEMENTATION_EXECUTION_V1'
REL='docs/dtc_l1/review_packs/DTC_CONTROLLED_ORACLE_IMPLEMENTATION_EXECUTION_V1'
SCHEMA='DTC_ORACLE_BACKGROUND_PUBLICATION_V1'
MODES=('OFF_MATCHED','M_DATAREAD','L2_DATAREAD','L1_DATAREADY')

def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def digest(p):return sha_bytes(pathlib.Path(p).read_bytes())
def load(p):return json.loads(pathlib.Path(p).read_text())
def fail(ok,why):
 if not ok:raise ValueError(why)
def atomic(p,x):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 tmp=p.with_name(p.name+'.tmp.'+str(os.getpid()));tmp.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n');os.replace(tmp,p)
def within(path,root):
 p=pathlib.Path(path).resolve();r=pathlib.Path(root).resolve();fail(p==r or r in p.parents,'path escapes intended root');return p
@contextlib.contextmanager
def exclusive(lock):
 p=pathlib.Path(lock);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('a+') as f:
  fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:yield
  finally:fcntl.flock(f.fileno(),fcntl.LOCK_UN)

def pinned_consumer(path,expected):
 fail(re.fullmatch('[0-9a-f]{64}',expected or '') is not None,'consumer SHA required')
 fail(digest(path)==expected,'consumer implementation changed; explicit reviewed pin required')
 spec=importlib.util.spec_from_file_location('dtc_main_readonly_consumer',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 fail(callable(getattr(m,'snapshot',None)),'consumer snapshot interface missing');return m

def normalize_report(report,matrix):
 """Validate population; keep consumer scientific classifications untouched."""
 fail(isinstance(report,dict) and not report.get('mock'),'MOCK reports cannot be published')
 fail(report.get('schema')=='DTC_ORACLE_LIVE_READONLY_SNAPSHOT_V1','unexpected S live schema')
 rows=report['rows'];plans={p['plan_id']:p for p in matrix['rows']}
 fail(len(rows)==128 and len(plans)==128,'complete128 PLAN view required')
 fail(len({r['plan_id'] for r in rows})==128,'duplicate PLAN rows')
 fail(len({r['input_digest'] for r in rows})==32,'complete32 input scope required')
 for r in rows:
  p=plans.get(r['plan_id']);fail(p is not None,'unplanned result row')
  for k in ('program','input_digest','mode'):fail(r[k]==p[k],'row identity changed: '+k)
  fail(r['mode'] in MODES,'unexpected Oracle mode')
 return rows

def closed_identity(row):
 # S live consumer names are finalized in its explicit schema adapter below.
 path=row.get('result_path');sha=row.get('result_sha256')
 if path is None and sha is None:return None
 fail(isinstance(path,str) and path.startswith('/'),'RESULT source path absent')
 fail(re.fullmatch('[0-9a-f]{64}',sha or '') is not None,'RESULT source SHA absent')
 return {'plan_id':row['plan_id'],'uuid':row.get('uuid'),'result_path':path,'result_sha256':sha}

def publication_view(report,matrix):
 rows=normalize_report(report,matrix)
 closed=[x for x in (closed_identity(r) for r in rows) if x]
 closed.sort(key=lambda x:x['plan_id'])
 own_fp=sha_bytes(json.dumps(closed,sort_keys=True,separators=(',',':')).encode())
 fp=report.get('closed_fingerprint_sha256')
 fail(re.fullmatch('[0-9a-f]{64}',fp or '') is not None,'missing S closed fingerprint')
 fail(report.get('closed_result_count')==len(closed),'S closed count does not match pinned result rows')
 counts=dict(collections.Counter(str(r['status']) for r in rows))
 return {'schema':SCHEMA,'authority':AUTHORITY,'matrix_sha256':MATRIX_SHA,
   'program_population':32,'PLAN_population':128,'modes':list(MODES),
   'closed_RESULT_count':len(closed),'closed_fingerprint_sha256':fp,
   'publisher_source_pins_fingerprint_sha256':own_fp,
   'status_counts_exact_consumer_labels':counts,'closed_RESULT_source_pins':closed,
   'new_science_starts':0,'raw_scientific_ledgers_modified':False,
   'method':'Same immutable binary/input/270-option OFF pairs only; S/H remain un-clipped. Historical DH0 is context; no per-program best Oracle GM.'}

def build_payload(report,matrix,derived_dir,destination,consumer_pin):
 view=publication_view(report,matrix);dst=pathlib.Path(destination);dst.mkdir(parents=True,exist_ok=False)
 # Copy only explicit derived report types and bound sizes, never raw/model files.
 members=[];total_bytes=0
 for p in sorted(pathlib.Path(derived_dir).iterdir()):
  if not p.is_file() or p.suffix.lower() not in ('.json','.csv','.md','.gz'):continue
  fail(p.stat().st_size<=32*1024*1024,'derived report exceeds bounded review size')
  total_bytes+=p.stat().st_size
  fail(total_bytes<=128*1024*1024,'derived payload exceeds128MiB; Main must review a thin publication layout')
  fail(p.read_bytes()[:4]!=b'\x7fELF','ELF cannot enter review package')
  target=dst/p.name;shutil.copyfile(p,target)
  members.append({'path':p.name,'sha256':digest(target),'bytes':target.stat().st_size})
 fail(bool(members),'no derived report files')
 atomic(dst/'PUBLICATION_SCOPE.json',{**view,'consumer_implementation_sha256':consumer_pin,'watcher_implementation_sha256':digest(__file__)})
 members.append({'path':'PUBLICATION_SCOPE.json','sha256':digest(dst/'PUBLICATION_SCOPE.json'),'bytes':(dst/'PUBLICATION_SCOPE.json').stat().st_size})
 # Disable inherited Git text/LFS filters only in the immutable derived payload.
 (dst/'.gitattributes').write_text('* -filter -text\n')
 members.append({'path':'.gitattributes','sha256':digest(dst/'.gitattributes'),'bytes':(dst/'.gitattributes').stat().st_size})
 manifest={'schema':'DTC_ORACLE_PUBLISHED_DERIVED_SNAPSHOT_V1','authority':AUTHORITY,
   'matrix_sha256':MATRIX_SHA,'closed_fingerprint_sha256':view['closed_fingerprint_sha256'],
   'source_RESULT_pins':view['closed_RESULT_source_pins'],'members':members}
 atomic(dst/'MANIFEST.json',manifest)
 return view,manifest

class GitPublication:
 def __init__(self,base,config,runner=None):
  self.base=pathlib.Path(base).resolve();self.cfg=config;self.runner=runner or subprocess.run
  fail(config.get('schema')=='DTC_ORACLE_MAIN_PUBLICATION_ENABLE_V1','wrong Main enable schema')
  fail(config.get('enabled') is True and config.get('coordinator')=='DTC-MAIN','publication not Main enabled')
  fail(config.get('first_main_publication_complete') is True,'Main first publication not complete')
  fail(re.fullmatch('[0-9a-f]{40}',config.get('first_main_commit','')) is not None,'first Main commit missing')
  fail(config.get('branch')==BRANCH and config.get('relative_root')==REL,'wrong branch/review scope')
  fail(config.get('remote','origin')=='origin','unexpected remote')
  self.work=within(config['worktree'],self.base)
  dotgit=self.work/'.git';fail(dotgit.is_file(),'dedicated linked worktree required')
  line=dotgit.read_text().strip();fail(line.startswith('gitdir: '),'malformed worktree .git')
  self.gitdir=pathlib.Path(line[len('gitdir: '):]).resolve()
  fail((self.gitdir/'gitdir').is_file() and pathlib.Path((self.gitdir/'gitdir').read_text().strip()).resolve()==dotgit.resolve(),'nonreciprocal linked worktree')
  self.index=within(self.base/'control/publication_v1/BACKGROUND_INDEX',self.base/'control/publication_v1')
  self.index.parent.mkdir(parents=True,exist_ok=True)
  self.env=dict(os.environ,GIT_INDEX_FILE=str(self.index))
  self.env.update({'http_proxy':'http://127.0.0.1:27890','https_proxy':'http://127.0.0.1:27890'})
  self.prefix=['git','-c','safe.directory='+str(self.work),'-c','core.bare=false','-c','core.fileMode=false','-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','-c','http.version=HTTP/1.1','-c','user.name=swayhrl','-c','user.email=56393103+swayhrl@users.noreply.github.com','--git-dir='+str(self.gitdir),'--work-tree='+str(self.work),'-C',str(self.work)]
 def run(self,args,input_bytes=None):
  r=self.runner(self.prefix+list(args),input=input_bytes,env=self.env,capture_output=True,check=False,timeout=60)
  fail(r.returncode==0,'Git command failed: '+str(args[:2])+' '+r.stderr.decode(errors='replace')[:500])
  return r.stdout
 def remote_sha(self):
  s=self.run(['ls-remote','origin','refs/heads/'+BRANCH]).decode().strip().split()
  fail(len(s)==2 and re.fullmatch('[0-9a-f]{40}',s[0]),'remote branch not published');return s[0]
 def validate_head(self):
  fail(self.run(['symbolic-ref','--short','HEAD']).decode().strip()==BRANCH,'wrong local branch')
  head=self.run(['rev-parse','HEAD']).decode().strip();fail(self.remote_sha()==head,'local/remote publication heads diverged; Main reconciliation required')
  self.run(['merge-base','--is-ancestor',self.cfg['first_main_commit'],head])
  return head
 def commit_snapshot(self,source_payload,view,now):
  head=self.validate_head()
  stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime(now));name=stamp+'_'+view['closed_fingerprint_sha256'][:16]
  relative=REL+'/live_results/'+name;target=within(self.work/relative,self.work/REL/'live_results')
  fail(not target.exists(),'snapshot path already exists; no overwrite')
  target.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(source_payload,target)
  latest=within(self.work/REL/'live_results/LATEST.json',self.work/REL/'live_results')
  atomic(latest,{'schema':'DTC_ORACLE_LATEST_DERIVED_SNAPSHOT_V1','snapshot':name,'manifest_sha256':digest(target/'MANIFEST.json'),'closed_fingerprint_sha256':view['closed_fingerprint_sha256'],'closed_RESULT_count':view['closed_RESULT_count']})
  paths=[str(p.relative_to(self.work)) for p in sorted(target.iterdir()) if p.is_file()]+[str(latest.relative_to(self.work))]
  # Dedicated index is reinitialized from current HEAD after Main's first commit.
  # The worktree's existing default index (including staged deletions) is ignored.
  self.run(['read-tree',head]);self.run(['add','-f','--']+paths)
  self.run(['diff','--cached','--check'])
  staged=self.run(['diff','--cached','--name-only']).decode().splitlines()
  fail(staged and set(staged)==set(paths),'unexpected staged paths; never commit foreign changes')
  self.run(['update-index','--chmod=-x','--']+paths)
  # HEAD equality checked immediately before commit; common external flock covers
  # Main and watcher. A competing writer causes fail-closed reconciliation.
  fail(self.run(['rev-parse','HEAD']).decode().strip()==head,'HEAD changed during snapshot preparation')
  self.run(['commit','-m','DTC controlled Oracle: '+str(view['closed_RESULT_count'])+' closed-result snapshot'])
  commit=self.run(['rev-parse','HEAD']).decode().strip()
  self.run(['push','origin','HEAD:refs/heads/'+BRANCH])
  fail(self.remote_sha()==commit,'remote SHA readback mismatch')
  self.run(['fetch','--no-tags','origin','refs/heads/'+BRANCH])
  fail(self.run(['rev-parse','FETCH_HEAD']).decode().strip()==commit,'fetched remote commit mismatch')
  manifest_bytes=self.run(['show','FETCH_HEAD:'+relative+'/MANIFEST.json'])
  fail(manifest_bytes==(target/'MANIFEST.json').read_bytes(),'remote manifest bytes changed')
  return {'commit':commit,'parent':head,'remote_sha':commit,'remote_manifest_sha256':sha_bytes(manifest_bytes),'snapshot_relative':relative,'explicit_staged_paths':paths,'GIT_INDEX_FILE':str(self.index),'default_index_touched':False,'readback':'push -> ls-remote exact SHA -> fetch exact branch -> show FETCH_HEAD:MANIFEST bytes verified'}

def due(view,state,now):
 if view['closed_RESULT_count']==0:return False,'PLAN_NO_ACTUAL_RESULTS'
 if view['closed_fingerprint_sha256']==state.get('last_published_fingerprint'):return False,'NO_NEW_CLOSED_DATA'
 if now-state.get('last_publication_epoch',0)<1800:return False,'WAIT_30MIN_INTERVAL'
 return True,'NEW_CLOSED_DATA_DUE'

def cycle(base,matrix_path,consumer,consumer_pin,state_dir,config_path=None,now=None,native_base=None):
 now=time.time() if now is None else now;state_dir=pathlib.Path(state_dir);state_dir.mkdir(parents=True,exist_ok=True)
 fail(digest(matrix_path)==MATRIX_SHA,'frozen matrix changed');matrix=load(matrix_path)
 derived=state_dir/'derived';derived.mkdir(exist_ok=True)
 # S snapshot is read-only for source/result ledgers; only its own derived folder mutates.
 report=consumer.snapshot(str(native_base if native_base is not None else base),str(matrix_path),str(derived))
 view=publication_view(report,matrix);atomic(state_dir/'CURRENT_SCOPE.json',view)
 state=load(state_dir/'WATCH_STATE.json') if (state_dir/'WATCH_STATE.json').exists() else {}
 yes,reason=due(view,state,now);action='COLLECT_ONLY'
 if yes and config_path:
  cfg=load(config_path);publisher=GitPublication(base,cfg)
  payload=state_dir/'payloads'/view['closed_fingerprint_sha256'];payload.parent.mkdir(exist_ok=True)
  if payload.exists():
   # Reuse only unchanged immutable payload after a prior preparation failure.
   old=load(payload/'PUBLICATION_SCOPE.json');fail(old['closed_fingerprint_sha256']==view['closed_fingerprint_sha256'],'stale payload')
  else:build_payload(report,matrix,derived,payload,consumer_pin)
  receipt=publisher.commit_snapshot(payload,view,now)
  receipt.update({'schema':'DTC_ORACLE_PUBLICATION_READBACK_RECEIPT_V1','epoch':now,'closed_fingerprint_sha256':view['closed_fingerprint_sha256'],'publication_enable_sha256':digest(config_path)})
  atomic(state_dir/'readbacks'/(receipt['commit']+'.json'),receipt)
  state.update({'last_publication_epoch':now,'last_published_fingerprint':view['closed_fingerprint_sha256'],'last_commit':receipt['commit']});action='PUBLISHED'
 state.update({'last_poll_epoch':now,'last_observed_fingerprint':view['closed_fingerprint_sha256'],'last_closed_RESULT_count':view['closed_RESULT_count'],'last_reason':reason,'last_action':action})
 atomic(state_dir/'WATCH_STATE.json',state)
 return {'action':action,'reason':reason,'closed_RESULT_count':view['closed_RESULT_count'],'scope':'32 complete input identities / 128 PLAN slots','new_science_starts':0}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base',required=True);ap.add_argument('--native-base',required=True);ap.add_argument('--matrix',required=True);ap.add_argument('--consumer',required=True);ap.add_argument('--consumer-sha256',required=True);ap.add_argument('--state-dir',required=True);ap.add_argument('--publication-enable');ap.add_argument('--watch',action='store_true');ap.add_argument('--poll',type=float,default=60);ap.add_argument('--stop-file')
 a=ap.parse_args();fail(a.poll>=5,'minimum read-only polling interval5sec')
 base=pathlib.Path(a.base).resolve();state=within(a.state_dir,base);consumer=pinned_consumer(a.consumer,a.consumer_sha256)
 while True:
  if a.stop_file and pathlib.Path(a.stop_file).exists():return
  try:
   with exclusive(base/'control/publication_v1/LOCK'):
    result=cycle(base,a.matrix,consumer,a.consumer_sha256,state,a.publication_enable,native_base=a.native_base)
   print(json.dumps(result),flush=True)
  except BlockingIOError:print(json.dumps({'action':'WAIT_UNIQUE_PUBLICATION_LOCK','new_science_starts':0}),flush=True)
  except Exception as e:
   atomic(state/'LAST_WATCH_ERROR.json',{'error':type(e).__name__+': '+str(e),'epoch':time.time(),'new_science_starts':0})
   if not a.watch:raise
   print(json.dumps({'action':'HOLD_PUBLICATION_ERROR','error':str(e),'new_science_starts':0}),flush=True)
  if not a.watch:return
  time.sleep(a.poll)
if __name__=='__main__':main()
