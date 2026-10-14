import base64,email,hashlib,io,json,pathlib,sys,urllib.parse,zipfile
from control import ROOT,http,check
lock=json.loads((ROOT/'distribution_closure.json').read_text())
prior=json.loads(pathlib.Path('docs/ai_workload_research/runs/AI_ARCH_A26G_GSSCALE_RUBBLE_109_V1/DEPENDENCY_PREFLIGHT.json').read_text())
class RemoteZIP(io.RawIOBase):
 def __init__(self,url,size):self.url=url;self.size=size;self.pos=0
 def seekable(self):return True
 def tell(self):return self.pos
 def seek(self,n,whence=0):self.pos=n if whence==0 else self.pos+n if whence==1 else self.size+n;return self.pos
 def read(self,n=-1):
  if n<0:n=self.size-self.pos
  if n>4*1024**2:raise RuntimeError('METADATA_RANGE_READ_BOUND')
  if self.pos>=self.size:return b''
  n=min(n,self.size-self.pos)
  if not n:return b''
  start=self.pos;end=start+n-1;r,b=http(self.url,limit=n,headers={'Range':'bytes='+str(start)+'-'+str(end)})
  assert r.get('status')==206 and r['headers'].get('Content-Range',r['headers'].get('content-range'))=='bytes '+str(start)+'-'+str(end)+'/'+str(self.size)
  assert len(b)==n;self.pos+=len(b);return b
for name in ['torch','torchvision']:
 url=next(x['matching_official_release_urls'][0] for x in prior['release_candidates'] if x['package'].startswith(name+'-'))
 rawurl,_,sha=url.partition('#sha256=');r,b=http(rawurl,'HEAD');assert r.get('status')==200;size=int(next(v for k,v in r['headers'].items() if k.lower()=='content-length'))
 with zipfile.ZipFile(RemoteZIP(rawurl,size)) as z:
  mname=next(x for x in z.namelist() if x.endswith('.dist-info/METADATA'));mb=z.read(mname)
 message=email.message_from_bytes(mb);version=message['Version'];assert version==('2.2.0+cu121' if name=='torch' else '0.17.0+cu121')
 target=next(x for x in lock['official_registry_wheels'] if x['name']==name)
 target.update(version=version,url=rawurl,sha256=sha,bytes=size,metadata_sha256=hashlib.sha256(mb).hexdigest(),requires_dist=message.get_all('Requires-Dist') or [])
 (ROOT/(name+'_official_metadata')).write_bytes(mb);print('EXACT_CORE_WHEEL_METADATA',name,version,size,flush=True)
sources=[]
for repo,commit in [('rmbrualla/pycolmap','cc7ea4b7301720ac29287dbe450952511b32125e'),('rahul-goel/fused-ssim','1272e21a282342e89537159e4bad508b19b34157')]:
 entry='pyproject.toml' if repo=='rmbrualla/pycolmap' else 'setup.py'
 r,b=http('https://api.github.com/repos/'+repo+'/contents/'+entry+'?ref='+commit);assert r.get('status')==200,r
 j=json.loads(b);data=base64.b64decode(j['content']);sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert sha==j['sha']
 (ROOT/(repo.split('/')[-1]+'_'+entry)).write_bytes(data);sources.append({'repo':repo,'commit':commit,'setup_blob':sha,'setup_sha256':hashlib.sha256(data).hexdigest()});print('VCS_SETUP',repo,data.decode(),flush=True)
tree=json.loads((ROOT/'gsscale_tree.json').read_text());assert not tree.get('truncated')
print('AUTHOR_SUBMODULES',[x for x in tree['tree'] if x['type']=='commit'])
lock['vcs_source_setup_identity']=sources
head_checks=[]
for i,x in enumerate(lock['official_registry_wheels']):
 r,b=http(x['url'],'HEAD');assert r.get('status')==200,(x['name'],r)
 length=next((int(v) for k,v in r['headers'].items() if k.lower()=='content-length'),None);assert length==x['bytes'],(x['name'],length,x['bytes'])
 head_checks.append({'name':x['name'],'status':r['status'],'size_bytes':length,'expected_sha256':x['sha256']})
 if i%20==0:print('RELEASE_HEAD_CHECKS',i+1,flush=True)
lock['status']='PASS_METADATA_DISTRIBUTION_CLOSURE_WITH_VCS_SOURCES';lock['official_release_head_checks']=head_checks
lock['not_yet_qualified']=['installed ABI','CPUAdam actual threads','native function/quality','actual archive expansion/extraction']
(ROOT/'distribution_closure.json').write_text(json.dumps(lock,indent=2)+'\n')
resource=check(extra=9773995561+2*1024**3)
(ROOT/'r0_preflight.json').write_text(json.dumps({'status':'PASS','archive_known_bytes':9773995561,'compressed_plus_safety_bytes':9773995561+2*1024**3,'source':'fixed A26G source cache independently hashed; exact author tree and VCS refs verified','controller_camera_roundtrip':'PASS','distribution_count':len(lock['official_registry_wheels']),'distribution_expected_bytes':sum(x['bytes'] for x in lock['official_registry_wheels']),'r0_resource':resource,'future_expand_unknown_not_a_stop':True,'thread_plan':'OMP_THREAD_LIMIT=16 + Torch intra/inter-op and BLAS=1; actual CPUAdam canary required before native','gpu_lock':'nonblocking preflight available; no CUDA initialization'},indent=2)+'\n')
print('R0_PASS',json.dumps(resource))
