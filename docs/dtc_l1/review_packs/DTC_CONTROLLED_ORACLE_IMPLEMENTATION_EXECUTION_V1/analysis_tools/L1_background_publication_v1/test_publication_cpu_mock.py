#!/usr/bin/env python3
"""MOCK_NOT_SCIENTIFIC: zero real Git, SSH, model or registry invocations."""
import copy, hashlib, importlib.util, json, pathlib, subprocess, tempfile
from types import SimpleNamespace
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('pub',HERE/'watch_publish_oracle_results.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
BASE=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1')
matrix=p.load(BASE/'control/authority/FUTURE_DH_ORACLE_MATRIX.json')
checks=0

def check(x):
 global checks
 checks+=1
 assert x

def throws(f):
 global checks
 checks+=1
 try:f()
 except (ValueError,BlockingIOError):return
 raise AssertionError('expected fail-closed')

def report(n=0):
 rows=[]
 for i,r in enumerate(matrix['rows']):
  row={k:r[k] for k in ('plan_id','program','input_digest','mode','suite','stage')}
  row.update(status='MISSING',result_path=None,result_sha256=None,uuid=None,classification=None,cycles=None,S_oracle=None,H=None)
  if i<n:row.update(status='ACCEPTED' if i%2==0 else 'NEGATIVE',result_path='/MOCK_NOT_SCIENTIFIC/'+str(i)+'.RESULT.json',result_sha256=hashlib.sha256(str(i).encode()).hexdigest(),uuid='MOCK-'+str(i),classification='accepted' if i%2==0 else 'negative',cycles=200,S_oracle=0.5,H=-1.0)
  rows.append(row)
 return {'schema':'DTC_ORACLE_LIVE_READONLY_SNAPSHOT_V1','rows':rows,'closed_result_count':n,'closed_fingerprint_sha256':hashlib.sha256(('MOCKCLOSED'+str(n)).encode()).hexdigest()}

class FakeGit:
 def __init__(self,work):self.work=work;self.calls=[];self.head='a'*40;self.remote=self.head;self.paths=[]
 def __call__(self,cmd,input=None,env=None,capture_output=None,check=None,timeout=None):
  # An in-process fake. In particular a recorded push command is never run.
  self.calls.append((cmd,dict(env)))
  a=cmd[cmd.index('-C')+2:];out=b''
  if a[:2]==['symbolic-ref','--short']:out=(p.BRANCH+'\n').encode()
  elif a[0]=='rev-parse':out=(self.head+'\n').encode()
  elif a[0]=='ls-remote':out=(self.remote+'\trefs/heads/'+p.BRANCH+'\n').encode()
  elif a[:2]==['add','-f']:self.paths=a[3:]
  elif a[:3]==['diff','--cached','--name-only']:out=('\n'.join(self.paths)+'\n').encode()
  elif a[0]=='commit':self.head='b'*40
  elif a[0]=='push':self.remote=self.head
  elif a[0]=='show':out=(self.work/a[1].split(':',1)[1]).read_bytes()
  return SimpleNamespace(returncode=0,stdout=out,stderr=b'')

with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENTIFIC_ORACLE_PUB_') as td:
 root=pathlib.Path(td);r0=report(0);v0=p.publication_view(r0,matrix)
 check(v0['program_population']==32 and v0['PLAN_population']==128)
 check(p.due(v0,{},2000)==(False,'PLAN_NO_ACTUAL_RESULTS'))
 r2=report(2);v2=p.publication_view(r2,matrix);check(p.due(v2,{},2000)[0])
 check(p.due(v2,{'last_published_fingerprint':v2['closed_fingerprint_sha256']},99999)[1]=='NO_NEW_CLOSED_DATA')
 check(p.due(v2,{'last_publication_epoch':1900},2000)[1]=='WAIT_30MIN_INTERVAL')
 check(p.due(v2,{'last_publication_epoch':100},2000)[0])
 broken=copy.deepcopy(r2);broken['rows']=broken['rows'][:-1];throws(lambda:p.publication_view(broken,matrix))
 broken=copy.deepcopy(r2);broken['rows'][1]['plan_id']=broken['rows'][0]['plan_id'];throws(lambda:p.publication_view(broken,matrix))
 broken=copy.deepcopy(r2);broken['rows'][0]['result_sha256']=None;throws(lambda:p.publication_view(broken,matrix))
 broken=copy.deepcopy(r2);broken['mock']=True;throws(lambda:p.publication_view(broken,matrix))
 derived=root/'derived';derived.mkdir();p.atomic(derived/'ORACLE_LIVE_RESULTS.json',r2);(derived/'REPORT.md').write_text('MOCK_NOT_SCIENTIFIC\n');(derived/'raw.log').write_text('must not export')
 view,mf=p.build_payload(r2,matrix,derived,root/'payload','c'*64)
 copied=p.load(root/'payload/ORACLE_LIVE_RESULTS.json');check(copied['rows'][0]['H']==-1 and copied['rows'][0]['S_oracle']==0.5)
 check(not (root/'payload/raw.log').exists());check(len(mf['source_RESULT_pins'])==2)
 check(mf['source_RESULT_pins'][0]['result_path'].startswith('/MOCK_NOT_SCIENTIFIC/'))
 check((root/'payload/.gitattributes').read_text()=='* -filter -text\n')
 lock=root/'LOCK'
 with p.exclusive(lock):throws(lambda: (p.exclusive(lock).__enter__()))
 # Fake linked worktree contains a deliberately contaminated default index.
 base=root/'base';work=base/'review-worktree';work.mkdir(parents=True);gitdir=base/'control/mockgitdir';gitdir.mkdir(parents=True)
 (work/'.git').write_text('gitdir: '+str(gitdir)+'\n');(gitdir/'gitdir').write_text(str(work/'.git')+'\n');(gitdir/'index').write_bytes(b'CONTAMINATED_DEFAULT_INDEX_STAGED_D')
 cfg={'schema':'DTC_ORACLE_MAIN_PUBLICATION_ENABLE_V1','enabled':True,'coordinator':'DTC-MAIN','first_main_publication_complete':True,'first_main_commit':'a'*40,'branch':p.BRANCH,'relative_root':p.REL,'worktree':str(work)}
 fake=FakeGit(work);pub=p.GitPublication(base,cfg,runner=fake);receipt=pub.commit_snapshot(root/'payload',view,2000)
 check(receipt['remote_sha']=='b'*40 and receipt['default_index_touched'] is False)
 check((gitdir/'index').read_bytes()==b'CONTAMINATED_DEFAULT_INDEX_STAGED_D')
 check(all(env['GIT_INDEX_FILE'].endswith('/control/publication_v1/BACKGROUND_INDEX') for _,env in fake.calls))
 check(all(not any(x in cmd for x in ('reset','restore','--force','-A')) for cmd,_ in fake.calls))
 add=[cmd for cmd,_ in fake.calls if 'add' in cmd];check(len(add)==1 and '--' in add[0])
 check(all(x.startswith(p.REL+'/live_results/') for x in receipt['explicit_staged_paths']))
 check(any('fetch' in cmd for cmd,_ in fake.calls) and any('show' in cmd for cmd,_ in fake.calls))
 bad=dict(cfg,first_main_publication_complete=False);throws(lambda:p.GitPublication(base,bad,runner=fake))
 check(len([cmd for cmd,_ in fake.calls if 'push' in cmd])==1) # in-memory fake only
 # A real no-result cycle calls the supplied read-only mock consumer and no Git.
 fakeconsumer=SimpleNamespace(snapshot=lambda b,m,o:report(0))
 state=base/'agent_state';result=p.cycle(base,BASE/'control/authority/FUTURE_DH_ORACLE_MATRIX.json',fakeconsumer,'c'*64,state,now=2000)
 check(result['reason']=='PLAN_NO_ACTUAL_RESULTS' and result['action']=='COLLECT_ONLY')
 check(not (state/'payloads').exists());check(not (base/'control/publication_v1/BACKGROUND_INDEX').exists())
 print(json.dumps({'schema':'DTC_ORACLE_PUBLICATION_CPU_MOCK_TEST_V1','classification':'MOCK_NOT_SCIENTIFIC','pass':True,'checks':checks,'actual_Git_pushes':0,'actual_simulator_invocations':0,'actual_scientific_registrations':0}))
