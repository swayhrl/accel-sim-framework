"""Small isolated git/IO qualification. Never invokes live reporting or remote GitHub."""
import pathlib,tempfile,json,hashlib,importlib.util,subprocess,copy,types,urllib.parse,sys,io,os
sys.dont_write_bytecode=True
P=pathlib.Path;D=P(__file__).parent
s=importlib.util.spec_from_file_location('B_publisher_candidate',D/'periodic_publisher.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def sh(args):
 if args[0]=='git':args=[args[0],'-c','safe.directory=*',*args[1:]]
 return subprocess.run(args,check=True,capture_output=True).stdout.decode().strip()
def put(p,v):P(p).parent.mkdir(parents=True,exist_ok=True);P(p).write_bytes(m.encode(v))
def reject(fn):
 try:fn()
 except Exception:return
 raise AssertionError('Expected refusal')
checks=[]
def ck(name,b):assert b,name;checks.append(name)
root=P(tempfile.mkdtemp(prefix='CPU_FIXTURE_',dir=D));a=root/'archive';a.mkdir();w=a/'worktree';w.mkdir();bare=root/'bare.git';sh(['git','init','--bare',str(bare)]);sh(['git','init','-b','hrl/dtc-l2-mlp-full-workload-exploration-v1',str(w)]);sh(['git','-C',str(w),'config','user.name','CPU fixture']);sh(['git','-C',str(w),'config','user.email','fixture@example.invalid'])
rel='docs/dtc_l1/review_packs/DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_V1';pack=w/rel;pack.mkdir(parents=True);historical='# Original historical README\n145accepted/88% historical policy\n';(pack/'README.md').write_text(historical);(w/'unrelated.txt').write_text('base\n');sh(['git','-C',str(w),'add','--',rel+'/README.md','unrelated.txt']);sh(['git','-C',str(w),'commit','-m','fixture initial']);head=sh(['git','-C',str(w),'rev-parse','HEAD']);sh(['git','-C',str(w),'remote','add','origin',str(bare)])
cfg=dict(schema='DTC_PERIODIC_PUBLICATION_CONFIG_V1',root=str(root/'live_fixture'),archive_root=str(a),worktree=str(w),branch='hrl/dtc-l2-mlp-full-workload-exploration-v1',remote='origin',repo='swayhrl/accel-sim-framework',review_relative=rel,output_root=str(a/'publisher'),git_lock=str(a/'coordinator/git.lock'),interval_seconds=1800,expected_initial_head=head,generator_path='UNUSED_CPU_FIXTURE',generator_sha256=m.GEN_SHA,generator_tool_commit='fce10d92eb09bc8f562b84a5a84b202bbf1ea385',registry_path=str(root/'registry.json'),analysis_ready_path=str(a/'READY.json'))
p=m.Publisher(cfg)
fixture_gitconfig=root/'fixture.gitconfig';fixture_gitconfig.write_text('[safe]\n\tdirectory = *\n')
original_run=p.run
def fixture_run(args,timeout=120,env=None):
 if args[0]=='git':args=['git','-c','safe.directory='+str(bare),*args[1:]]
 env=dict(os.environ if env is None else env,GIT_CONFIG_GLOBAL=str(fixture_gitconfig),GIT_CONFIG_NOSYSTEM='1')
 return original_run(args,timeout,env)
p.run=fixture_run
f=root/'result.json';v=dict(uuid='u',cycles=123,state='PASS',proof={'performance_accepted':True});put(f,v);known,values=m.stable_results({'PRIMARY':f},{})
doc=m.export_document('PRIMARY',known['PRIMARY'],v);ck('original UTF8 reconstructs exact RESULT bytes and SHA',doc['original_utf8'].encode()==f.read_bytes()and m.digest(doc['original_utf8'].encode())==known['PRIMARY']['sha256'])
ck('first structured accepted export and later delta cannot repeat original identity',m.result_delta(['A','B'],[])==['A','B']and m.result_delta(['A','B','C'],['A','B'])==['C'])
put(f,dict(v,cycles=124));reject(lambda:m.stable_results({'PRIMARY':f},known));ck('same cohort changed raw SHA/cycles cannot replace prior RESULT',True);put(f,v)
put(cfg['registry_path'],{'registered_future_requests':{m.REQ:{'authorized_supplemental_trials':[{'new_cohort':'R2'}]}}});primary,supp=p.identities({'points':[{'cohort':'PRIMARY'}]});ck('R2 independently exported and never unioned into primary population',set(primary)=={'PRIMARY'}and set(supp)=={'R2'});reject(lambda:p.identities({'points':[{'cohort':'R2'}]}));ck('primary supplemental identity collision refuses publication',True)
with m.lock(a/'double.lock'):reject(lambda:m.lock(a/'double.lock').__enter__())
ck('separate process-lock open refuses duplicate publisher lock',True)
(w/'unrelated.txt').write_text('dirty\n');reject(p.clean);(w/'unrelated.txt').write_text('base\n');(w/'alien.txt').write_text('staged\n');sh(['git','-C',str(w),'add','--','alien.txt']);reject(p.clean);sh(['git','-C',str(w),'restore','--staged','--','alien.txt'])
ck('tracked-dirty and unrelated staged changes fail closed without touching them',True)
(w/'__pycache__').mkdir();(w/'__pycache__/untouched.pyc').write_bytes(b'CPU unrelated');(w/'.git/info/exclude').write_text('*.gz\n')
snap=p.out/'snapshots'/'CPU_1';snap.mkdir(parents=True);put(snap/'report.json',{'planned_cells':1,'partial':True});put(snap/'MEMBER_MANIFEST.json',{'CPU_FIXTURE':True});(snap/'README.md').write_text('CPU snapshot\n')
snapshot=dict(token='CPU_1',directory=str(snap),known_results=known,exported_primary=['PRIMARY'],exported_supplemental=['R2'],accepted=1,planned=1,report_utc='CPU_ONLY')
(snap/'.gitignore').write_text('!*.jsonl.gz\n');(snap/'new_accepted_primary_results.jsonl.gz').write_bytes(b'CPU fixture gz bytes')
def dummy_generate():return snapshot
p.generate=dummy_generate
original_git=p.git;push_count=[0]
def flaky(*args,**kw):
 if args[0]=='push':
  push_count[0]+=1
  try:
   with m.lock(cfg['git_lock']):raise AssertionError('git lock not held across push')
  except BlockingIOError:pass
  if push_count[0]==1:raise RuntimeError('CPU_ONLY_SIMULATED_NETWORK_FAILURE')
 return original_git(*args,**kw)
p.git=flaky
reject(p.tick);pending=copy.deepcopy(p.state['pending']);commit=pending['commit'];count=original_git('rev-list','--count','HEAD');assert pending['phase']=='PENDING_PUSH'
ck('failed push preserves same durable pending commit and snapshot for retry',commit!=head and count=='2')
original_urlopen=m.urllib.request.urlopen
class Response(io.BytesIO):
 def __enter__(self):return self
 def __exit__(self,*args):self.close()
def fake_https(url,timeout):
 tail=url.split('/'+commit+'/',1)[1];raw=subprocess.run(['git','-c','safe.directory='+str(w),'-C',str(w),'show',commit+':'+tail],check=True,capture_output=True).stdout;return Response(raw)
m.urllib.request.urlopen=fake_https
try:p.tick()
finally:m.urllib.request.urlopen=original_urlopen
ck('retry pushes original pending commit without creating a second commit; lsremote+three SHA readbacks pass',original_git('rev-parse','HEAD')==commit and original_git('rev-list','--count','HEAD')=='2'and p.state['pending']is None and p.state['last_success']['commit']==commit)
ck('explicit paths preserve unrelated untracked pycache and alien file without staging',original_git('ls-files','--','__pycache__/untouched.pyc','alien.txt')==''and(w/'__pycache__/untouched.pyc').read_bytes()==b'CPU unrelated')
text=(pack/'README.md').read_text();ck('old root README remains byte-text-complete in historical section; new pointer and historical-manifest warning present',historical in text and 'old BATCH_STATE .88 label is historical'in text and 'MEMBER_MANIFEST.json'in text)
later=m.root_readme(text,'periodic/CPU_2',2,3,'later');ck('later current-entry updates do not duplicate or replace historical README',later.count(historical)==1 and 'periodic/CPU_2/report.json'in later)
out=dict(schema='B_PERIODIC_PUBLISHER_SMALL_FIXTURE_QUALIFICATION_V1',status='PASS',count=len(checks),checks=checks,source_sha256=m.sha(D/'periodic_publisher.py'),fixture_root=str(root),only_git_repo_and_dummy_json_inside_fixture=True,HTTPS_readback_was_fixture_not_GitHub=True,models_started=0,live_generator_invoked=False,live_registry_changes=0,production_commit_push_background=0,production_eligible=False)
put(D/'CPU_QUALIFICATION.json',out);print(json.dumps(dict(status='PASS',checks=len(checks),sha256=m.sha(D/'CPU_QUALIFICATION.json'),source_sha256=out['source_sha256'])))
