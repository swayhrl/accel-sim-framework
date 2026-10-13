"""Exact pinned-version official wheel metadata gate. No dependency resolver or CUDA."""
import pathlib,os,json,re,subprocess,hashlib,urllib.parse,html,sys,concurrent.futures
from packaging.utils import parse_wheel_filename,canonicalize_name
from packaging.tags import sys_tags
root=pathlib.Path(os.environ['TASK_DATA']);raw=root/'raw';lock=root/'ORIGINAL_RESOLVED_REQUIREMENTS.lock';cache=root/'cache/official_metadata';cache.mkdir(exist_ok=True)
blocks=re.split(r'(?m)(?=^[A-Za-z0-9_.-]+==)',lock.read_text());packages={}
for block in blocks:
 m=re.match(r'([A-Za-z0-9_.-]+)==([^\s]+)',block)
 if m:packages[m[1]]={'version':m[2],'hashes':re.findall(r'--hash=sha256:([0-9a-f]{64})',block)}
assert len(packages)==82 and packages['antlr4-python3-runtime']['version']=='4.9.3';ordered=list(sys_tags());ranks={t:i for i,t in enumerate(ordered)}
def evaluate(name,pin):
 version=pin['version'];allowed=set(pin['hashes']);result={'distribution':name,'version':version,'original_allowed_hashes_count':len(allowed),'status':'NOT_RUN'};candidates=[]
 if name=='antlr4-python3-runtime':
  r=json.loads((raw/'PACKAGING_EXCEPTION_RECEIPT.json').read_text());assert r['status']=='PACKAGING_SOURCE_WHEEL_PASS_ANTLR_ONLY';result.update(status='APPROVED_LOCAL_SOURCE_WHEEL',filename=r['wheel_filename'],sha256=r['wheel_sha256'],bytes=r['wheel_bytes'],url=None);return result
 if name=='torch':
  url='https://download.pytorch.org/whl/cu126/torch/';out=cache/'torch_official_index.html'
 else:
  url='https://pypi.org/pypi/'+name+'/'+urllib.parse.quote(version,safe='')+'/json';out=cache/(name+'.json')
 cmd=['curl','--silent','--show-error','--fail','--location','--connect-timeout','10','--max-time','45','--max-filesize','2097152','--output',str(out),url]
 r=subprocess.run(cmd,capture_output=True,text=True)
 if r.returncode:result.update(status='OFFICIAL_METADATA_BLOCKED',error=r.stderr,returncode=r.returncode,metadata_url=url);return result
 result.update(metadata_url=url,metadata_sha256=hashlib.sha256(out.read_bytes()).hexdigest())
 if name=='torch':
  for href in re.findall(r'href=["\']([^"\']+)',out.read_text()):
   link=urllib.parse.urljoin(url,html.unescape(href));parsed=urllib.parse.urlparse(link);filename=urllib.parse.unquote(parsed.path.rsplit('/',1)[-1])
   if not filename.endswith('.whl'):continue
   try:n,v,b,tags=parse_wheel_filename(filename)
   except Exception:continue
   if canonicalize_name(n)!=canonicalize_name(name) or str(v)!=version:continue
   digest=urllib.parse.parse_qs(parsed.fragment).get('sha256',[None])[0]
   if digest not in allowed:continue
   matching=set(tags)&set(ranks)
   if matching:candidates.append({'rank':min(ranks[t] for t in matching),'filename':filename,'sha256':digest,'bytes':None,'url':urllib.parse.urldefrag(link)[0],'compatible_tags':sorted(map(str,matching))})
 else:
  j=json.loads(out.read_text());assert j['info']['version']==version
  result['sdist_files']=[x['filename'] for x in j['urls'] if x['packagetype']=='sdist']
  for f in j['urls']:
   if f['packagetype']!='bdist_wheel' or f['digests']['sha256'] not in allowed:continue
   try:n,v,b,tags=parse_wheel_filename(f['filename'])
   except Exception:continue
   matching=set(tags)&set(ranks)
   if str(v)==version and matching:
    assert f['url'].startswith('https://files.pythonhosted.org/');candidates.append({'rank':min(ranks[t] for t in matching),'filename':f['filename'],'sha256':f['digests']['sha256'],'bytes':f['size'],'url':f['url'],'compatible_tags':sorted(map(str,matching))})
 result['compatible_official_locked_wheel_count']=len(candidates)
 if not candidates:result['status']='ADDITIONAL_WHEEL_BLOCKED';return result
 chosen=min(candidates,key=lambda x:(x['rank'],x['filename']));result.update(chosen);result['status']='OFFICIAL_LOCKED_WHEEL_AVAILABLE';return result
# Eight bounded CPU/IO workers, only exact frozen-version metadata.
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
 futures={executor.submit(evaluate,n,p):n for n,p in packages.items()}
 for f in concurrent.futures.as_completed(futures):
  n=futures[f]
  try:r=f.result()
  except Exception as e:r={'distribution':n,'version':packages[n]['version'],'status':'METADATA_IDENTITY_FAIL','error':str(e)}
  results.append(r)
  if r['status'] not in ['OFFICIAL_LOCKED_WHEEL_AVAILABLE','APPROVED_LOCAL_SOURCE_WHEEL']:print(json.dumps(r),flush=True)
  (raw/'FROZEN_WHEEL_AVAILABILITY.json').write_text(json.dumps({'status':'SCANNING','completed':len(results),'packages':sorted(results,key=lambda r:r['distribution'])},indent=2)+'\n')
failures=[r for r in results if r['status'] not in ['OFFICIAL_LOCKED_WHEEL_AVAILABLE','APPROVED_LOCAL_SOURCE_WHEEL']]
state={'status':'PASS_ALL82_WHEEL_ARTIFACTS_AVAILABLE' if not failures else ('ADDITIONAL_WHEEL_BLOCKED' if any(r['status']=='ADDITIONAL_WHEEL_BLOCKED' for r in failures) else 'ENVIRONMENT_METADATA_BLOCKED'),'versions_changed':False,'resolver_invoked':False,'checked':len(results),'failures':failures,'packages':sorted(results,key=lambda r:r['distribution']),'selected_wheel_known_total_bytes':sum(r.get('bytes') or 0 for r in results if r['status'] in ['OFFICIAL_LOCKED_WHEEL_AVAILABLE','APPROVED_LOCAL_SOURCE_WHEEL'])};(raw/'FROZEN_WHEEL_AVAILABILITY.json').write_text(json.dumps(state,indent=2)+'\n');print(json.dumps({k:v for k,v in state.items() if k!='packages'},indent=2),flush=True);sys.exit(0 if not failures else 1)
