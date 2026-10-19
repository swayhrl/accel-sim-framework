import os,re,json,hashlib,time,glob,subprocess
O=os.path.dirname(os.path.abspath(__file__)); out=[]; t=time.time()
for name in os.listdir('/proc'):
 if not name.isdigit(): continue
 p='/proc/'+name
 try:
  raw=open(p+'/cmdline','rb').read(); args=raw.replace(b'\0',b' ').decode(errors='replace'); st=open(p+'/stat').read().rsplit(')',1)[1].split(); cwd=os.readlink(p+'/cwd'); exe=os.readlink(p+'/exe')
  paths=set(re.findall(r'/(?:workspace|tmp|root/(?:data|share|\.cache))/[A-Za-z0-9_./+@:=,~-]+',args)); fds=[]
  for fd in os.listdir(p+'/fd')[:1024]:
   try:
    target=os.readlink(p+'/fd/'+fd)
    if target.startswith(('/workspace/','/tmp/','/root/data/','/root/.cache/')): fds.append(target)
   except OSError: pass
  out.append(dict(pid=int(name),start_ticks=st[19],state=st[0],uid=os.stat(p).st_uid,cwd=cwd,exe=exe,argv_sha256=hashlib.sha256(raw).hexdigest(),argv_paths=sorted(paths),fd_paths=sorted(set(fds)),fd_probe_limit=1024))
 except (OSError,IndexError): pass
 if time.time()-t>20: break
json.dump(dict(at_epoch=time.time(),duration_seconds=time.time()-t,processes=out),open(O+'/SOURCE_ACTIVITY_SNAPSHOT.json','w'),indent=2)
print('processes',len(out),'seconds',time.time()-t)
for r in out:
 if r['pid']==1920891 or r['cwd'].startswith('/workspace') or any('c2p' in p.lower() for p in r['argv_paths']+r['fd_paths']):
  print(json.dumps({k:r[k] for k in ['pid','start_ticks','state','cwd','exe','argv_paths']}))
