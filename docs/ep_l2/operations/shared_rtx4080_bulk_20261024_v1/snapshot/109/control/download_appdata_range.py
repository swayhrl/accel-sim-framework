#!/usr/bin/env python3
import pathlib,os,signal,time,json,hashlib,urllib.request,concurrent.futures,tarfile
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1')
URL='https://engineering.purdue.edu/tgrogers/gpgpu-sim/benchmark_data/all.gpgpu-sim-app-data.tgz'
ETAG='"981b0a3f-56fa25b338596"';TOTAL=2551908927
part=R/'assets/all.gpgpu-sim-app-data.tgz.part'
# Stop only the exact task-owned superseded single-stream curl; preserve its bytes/log.
stopped=[]
for proc in pathlib.Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:cmd=(proc/'cmdline').read_bytes().split(b'\0')
 except (FileNotFoundError,PermissionError):continue
 if cmd and cmd[0]==b'curl' and str(part).encode() in cmd and URL.encode() in cmd:
  os.kill(int(proc.name),signal.SIGTERM);stopped.append(int(proc.name))
time.sleep(1)
with urllib.request.urlopen(urllib.request.Request(URL,headers={'Range':'bytes=0-1023','If-Range':ETAG}),timeout=30) as f:
 b=f.read();headers=dict(f.headers);assert f.status==206 and len(b)==1024 and f.headers['ETag']==ETAG
assert part.stat().st_size>0 and part.stat().st_size<TOTAL
N=part.stat().st_size
D=R/'assets/appdata_range_segments';D.mkdir(exist_ok=False)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
rec={'url':URL,'etag':ETAG,'total_bytes':TOTAL,'range_probe':headers,'superseded_curl_pids':stopped,'prefix':{'path':str(part),'start':0,'end':N-1,'bytes':N,'sha256':sha(part)},'segments':[]}
(R/'control/APPDATA_RANGE_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n')
width=(TOTAL-N+6)//7
bounds=[(i,N+i*width,min(TOTAL-1,N+(i+1)*width-1)) for i in range(7) if N+i*width<TOTAL]
def fetch(job):
 idx,start,end=job;errors=[]
 for attempt in [1,2]:
  p=D/('segment%02d.attempt%02d'%(idx,attempt))
  try:
   with urllib.request.urlopen(urllib.request.Request(URL,headers={'Range':'bytes=%d-%d'%(start,end),'If-Range':ETAG}),timeout=60) as src,p.open('xb') as out:
    assert src.status==206 and src.headers['ETag']==ETAG and src.headers['Content-Range']=='bytes %d-%d/%d'%(start,end,TOTAL)
    while True:
     b=src.read(1048576)
     if not b:break
     out.write(b)
   assert p.stat().st_size==end-start+1
   return {'index':idx,'start':start,'end':end,'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'status':'PASS','errors':errors}
  except Exception as e:errors.append(repr(e))
 return {'index':idx,'start':start,'end':end,'status':'GAP_RETAINED','errors':errors}
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:
 for future in concurrent.futures.as_completed([pool.submit(fetch,j) for j in bounds]):
  s=future.result();rec['segments'].append(s);(R/'control/APPDATA_RANGE_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n');print('SEGMENT',s['index'],s['status'],flush=True)
assert all(s['status']=='PASS' for s in rec['segments'])
final=R/'assets/all.gpgpu-sim-app-data.tgz'
with final.open('xb') as out:
 for p in [part]+[pathlib.Path(s['path']) for s in sorted(rec['segments'],key=lambda s:s['index'])]:
  with p.open('rb') as src:
   for b in iter(lambda:src.read(1048576),b''):out.write(b)
assert final.stat().st_size==TOTAL;rec['full_sha256']=sha(final)
dest=R/'assets/official_appdata_rodinia';dest.mkdir(exist_ok=False)
members=[];allnames=[];extracted=0
with tarfile.open(final,'r|gz') as t:
 for m in t:
  allnames.append({'name':m.name,'bytes':m.size,'type':m.type.decode(errors='replace')})
  if 'rodinia' not in m.name.lower() or not m.isfile():continue
  rel=pathlib.PurePosixPath(m.name)
  assert not rel.is_absolute() and '..' not in rel.parts
  extracted+=m.size;assert extracted<=30*1024**3,'30GiB extracted budget'
  p=dest/pathlib.Path(*rel.parts);p.parent.mkdir(parents=True,exist_ok=True)
  h=hashlib.sha256()
  with t.extractfile(m) as src,p.open('xb') as out:
   for b in iter(lambda:src.read(1048576),b''):out.write(b);h.update(b)
  assert p.stat().st_size==m.size
  members.append({'path':str(p.relative_to(dest)),'bytes':m.size,'sha256':h.hexdigest()})
rec.update(full_tar_eof_verified=True,archive_member_count=len(allnames),rodinia_files=len(members),rodinia_bytes=extracted,status='COMPLETE_RANGE_ASSEMBLY_AND_TAR_EOF_PASS')
(R/'control/APPDATA_RANGE_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n')
(R/'control/APPDATA_FULL_ARCHIVE_INDEX.json').write_text(json.dumps(allnames,indent=2)+'\n')
(R/'control/RODINIA_OFFICIAL_INPUT_MEMBERS.json').write_text(json.dumps(members,indent=2)+'\n')
print('COMPLETE',len(members),extracted,rec['full_sha256'],flush=True)

