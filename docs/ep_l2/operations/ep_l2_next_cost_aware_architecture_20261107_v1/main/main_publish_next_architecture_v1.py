"""Main-only review publisher. No science/Native/model operations."""
from pathlib import Path
import json,hashlib,subprocess,fcntl,datetime,base64
P=Path(__file__).resolve().parent.parent; M=P/'main'
J=P.parent.parent
REPO='repos/swayhrl/accel-sim-framework'
BASE='eae40596cb9a550785a50a3d64617686a6daa160'
BRANCH='hrl/ep-l2-next-cost-aware-architecture-20261107-v1'
PREFIX='docs/ep_l2/operations/ep_l2_next_cost_aware_architecture_20261107_v1'
def read(p):return json.loads(Path(p).read_bytes())
def write(p,d):Path(p).write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
def sha(b):return hashlib.sha256(b).hexdigest()
def sanitize(d):
 if isinstance(d,dict):return {k:sanitize(v)for k,v in d.items()if not any(x in k.lower()for x in ['token','nonce','secret'])}
 if isinstance(d,list):return [sanitize(x)for x in d]
 return d
def api(method,path,body=None,missing=False):
 args=['/usr/local/bin/gh','api','-X',method,path]
 if body is not None:
  write(M/'GITHUB_API_REQUEST_PRIVATE.json',body);args+=['--input',str(M/'GITHUB_API_REQUEST_PRIVATE.json')]
 z=subprocess.run(args,capture_output=True,timeout=180)
 if z.returncode:
  if missing and b'404'in z.stderr:return None
  raise RuntimeError('GitHub API failed: '+z.stderr.decode(errors='replace')[-400:])
 return json.loads(z.stdout)
def main():
 selection=read(M/'REVIEW_EXPORT_SELECTION.json')
 audit=read(M/'MAIN_FINAL_ENGINEERING_ACCEPTANCE.json')
 assert audit['status']=='ENGINEERING_SCOPE_COMPLETE_SCIENCE_ZERO'
 assert audit['new_scientific_starts']==audit['budget_consumed']==audit['official_dispatchers_created']==0
 entries=[]; exports=[]
 for item in selection['files']:
  path=Path(item['source']);raw=path.read_bytes()
  assert sha(raw)==item['sha256'],'source changed '+str(path)
  assert item['export'].split('/')[0] in ['main','agent_a','agent_b','agent_c','agent_d']
  assert '..'not in Path(item['export']).parts
  b=(json.dumps(sanitize(json.loads(raw)),sort_keys=True,separators=(',',':'))+'\n').encode()if path.suffix=='.json'else raw
  assert len(b)<5*(1<<20)
  entries.append({'path':PREFIX+'/'+item['export'],'mode':'100644','type':'blob','content':b.decode('utf-8')})
  exports.append({'export':item['export'],'source':str(path),'source_sha256':sha(raw),'export_sha256':sha(b),'export_bytes':len(b),'raw_preserved':raw==b})
 note=read(M/'README_CONTENT.json')['text']
 entries.append({'path':PREFIX+'/README.md','mode':'100644','type':'blob','content':note})
 entries.append({'path':PREFIX+'/REVIEW_EXPORT_MANIFEST.json','mode':'100644','type':'blob','content':json.dumps({'schema':'MAIN_REVIEW_EXPORT_V1','files':exports,'recursive_token_nonce_secret_key_redaction_in_JSON_review_copies_only':True,'original_Source_and_evidence_unchanged':True},sort_keys=True,indent=2)+'\n'})
 assert len({x['path']for x in entries})==len(entries)
 assert sum(len(x['content'].encode())for x in entries)<18*(1<<20)
 with (J/'execution_performance_first_20261103_v1/control/MAIN_GIT_PUBLICATION.lock').open('a+b')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  prior=M/'REMOTE_PUBLICATION_RECEIPT.json'
  if prior.exists():
   r=read(prior);assert api('GET',REPO+'/git/ref/heads/'+BRANCH)['object']['sha']==r['head'];print(json.dumps(r));return
  ref=api('GET',REPO+'/git/ref/heads/'+BRANCH,missing=True)
  if ref is None:ref=api('POST',REPO+'/git/refs',{'ref':'refs/heads/'+BRANCH,'sha':BASE})
  intent=M/'PUBLICATION_COMMIT_INTENT.json'
  allowed={BASE}
  if intent.exists():allowed.add(read(intent)['commit'])
  assert ref['object']['sha']in allowed,'remote moved; no force'
  if intent.exists():
   ci=read(intent);head=ci['commit'];tree=ci['tree']
   assert ci['entries_digest']==sha(json.dumps(entries,sort_keys=True).encode())
  else:
   tree=api('GET',REPO+'/git/commits/'+BASE)['tree']['sha']
   for i in range(0,len(entries),25):tree=api('POST',REPO+'/git/trees',{'base_tree':tree,'tree':entries[i:i+25]})['sha']
   c=api('POST',REPO+'/git/commits',{'message':'EP-L2 next cost-aware architecture: paid optional Victim retention, RO convergence, CLEAN lifecycle and exact requests; science0','tree':tree,'parents':[BASE]})
   head=c['sha'];write(intent,{'commit':head,'tree':tree,'entries_digest':sha(json.dumps(entries,sort_keys=True).encode())})
  current=api('GET',REPO+'/git/ref/heads/'+BRANCH)['object']['sha']
  if current==BASE:api('PATCH',REPO+'/git/refs/heads/'+BRANCH,{'sha':head,'force':False})
  else:assert current==head,'remote changed; no force'
  assert api('GET',REPO+'/git/ref/heads/'+BRANCH)['object']['sha']==head
  sub=tree
  for part in PREFIX.split('/'):
   t=api('GET',REPO+'/git/trees/'+sub);sub=next(x['sha']for x in t['tree']if x['path']==part and x['type']=='tree')
  t=api('GET',REPO+'/git/trees/'+sub+'?recursive=1');assert not t.get('truncated')
  by={x['path']:x['sha']for x in t['tree']if x['type']=='blob'}
  for e in entries:
   b=e['content'].encode();h=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
   assert by[e['path'][len(PREFIX)+1:]]==h
  primary=PREFIX+'/main/EP_L2_NEXT_COST_AWARE_ARCHITECTURE_AND_EXACT_EXPERIMENT_REQUEST.md'
  z=api('GET',REPO+'/contents/'+primary+'?ref='+head)
  want=next(x['content'].encode()for x in entries if x['path']==primary)
  assert base64.b64decode(z['content'])==want
  r={'status':'REMOTE_EXACT_HEAD_ALL_GIT_BLOBS_AND_PRIMARY_BODY_VERIFIED','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head':head,'tree':tree,'parent':BASE,'branch':BRANCH,'prefix':PREFIX,'files':len(entries),'science_starts':0}
  write(M/'REMOTE_PUBLICATION_RECEIPT.json',r);print(json.dumps(r))
if __name__=='__main__':main()
