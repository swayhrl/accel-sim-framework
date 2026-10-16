from common import *
import tarfile,stat
header=json.loads((R/'canonical_header.json').read_text());assert header['status']==200;url=header['url'];size=int(header['headers']['Content-Length']);etag=header['headers']['ETag'];assert size<=int(4.5*1024**3)
assert shutil.disk_usage(R).free-size>=64*1024**3
assert 'all the data shared publicly' in (R/'source/ODC-By-1.0').read_text()
save('rights_initial.json',{'status':'PASS_OFFICIAL_PUBLIC_NUMERIC_LOCAL_RESEARCH_PENDING_ARCHIVE_INSPECTION','IGB_source_commit':'fc36357f2c1d861870b4c13a58f73da2b93d1e73','ODC_data_blob':'dab29a14b77b9cd9b523e4aeaaf6fdb2aaa3624b','MIT_code_blob':'931d368d8f65923bb22d8d059da3d45ab3afac1c','scope':'official small graph, numeric1024FP32 embeddings,19classlabels; local nonredistributed research; raw text excluded','ODC_section2_4':'independent content rights not universally licensed; inspect actual archive for extra restrictions before finalG0','attribution':'Contains information from Illinois Graph Benchmark (IGB), available under ODC Attribution License1.0; Khatua et al., KDD2023'})
p=R/'downloads/igb_homogeneous_small.tar.gz.part';attempts=[]
for attempt in range(3):
 offset=p.stat().st_size if p.exists() else 0
 if offset==size:break
 prior_data=sum(x['bytes'] for x in rows() if x.get('kind')=='data');assert prior_data+size-offset<=int(4.5*1024**3)
 req=urllib.request.Request(url,headers={'If-Match':etag,**({'Range':f'bytes={offset}-'} if offset else {})});row={'url':url,'kind':'data','method':'GET','start_epoch':time.time(),'attempt':attempt,'offset':offset,'bytes':0};q=None
 try:
  q=urllib.request.urlopen(req,timeout=40);row.update(status=q.status,headers=dict(q.headers));assert q.headers['ETag']==etag
  if offset:assert q.status==206 and q.headers['Content-Range']==f'bytes {offset}-{size-1}/{size}'
  else:assert q.status==200 and int(q.headers['Content-Length'])==size
  with p.open('ab' if offset else 'wb') as f:
   while offset+row['bytes']<size:
    b=q.read(min(256*1024,size-offset-row['bytes']))
    if not b:break
    f.write(b);row['bytes']+=len(b)
    if row['bytes']%(16*1024**2)<256*1024:
     check();save('download_progress.json',{'attempt':attempt,'already_accounted_previous_data_bytes':prior_data,'current_attempt_bytes':row['bytes'],'archive_current_bytes':offset+row['bytes'],'archive_total_bytes':size,'epoch':time.time()})
  assert p.stat().st_size==size,'INCOMPLETE_ENTITY_RESUME_ALLOWED'
 except Exception as e:row['error']=repr(e)
 finally:
  if q:q.close()
  row['finish_epoch']=time.time();receipt(row);attempts.append(row);save('download_progress.json',{'attempt_complete':True,'archive_current_bytes':p.stat().st_size if p.exists() else 0,'archive_total_bytes':size,'epoch':time.time()})
 if p.exists() and p.stat().st_size==size:break
assert p.exists() and p.stat().st_size==size,'BOUNDED_DOWNLOAD_RECOVERY_EXHAUSTED'
md5=sha(p,'md5');digest=sha(p);save('archive_identity.json',{'bytes':size,'ETag':etag,'version_id':header['headers'].get('x-amz-version-id'),'MD5':md5,'SHA256':digest,'expected_MD5':'6781c699723529902ace0a95cafe6fe4','attempts':attempts,'status':'PASS' if md5=='6781c699723529902ace0a95cafe6fe4' else 'MD5_FAIL'});assert md5=='6781c699723529902ace0a95cafe6fe4','SCIENTIFIC_ARCHIVE_IDENTITY_FAIL'
archive=R/'downloads/igb_homogeneous_small.tar.gz';p.rename(archive);print('ARCHIVE_IDENTITY_PASS',size,digest,flush=True)
seen={};members=[];expanded=0
with tarfile.open(archive,'r|gz') as tf:
 for m in tf:
  parts=pathlib.PurePosixPath(m.name).parts;assert parts and not m.name.startswith('/') and '..' not in parts and '\\' not in m.name,'UNSAFE_PATH'
  assert m.name not in seen,'DUPLICATE_MEMBER';seen[m.name]=True
  assert m.isfile() or m.isdir(),'LINK_OR_SPECIAL_FILE'
  assert not any(k not in ['mtime','atime','ctime','path','size'] for k in m.pax_headers),'UNKNOWN_PAX'
  if m.isfile():expanded+=m.size
  assert expanded<14*1024**3,'EXPANSION_UNBOUNDED'
  members.append({'name':m.name,'bytes':m.size,'type':'file' if m.isfile() else 'directory'})
current=check();free=shutil.disk_usage(R).free;reserve=512*1024**2
save('tar_scan.json',{'status':'PASS_SAFE_MEMBERS','members':members,'expanded_bytes':expanded,'current_new_allocated_bytes':current,'free_bytes_before_extract':free,'future_conversion_reserve_bytes':reserve,'extraction_budget_pass':current+expanded+reserve<14*1024**3 and free-expanded-reserve>=64*1024**3});assert current+expanded+reserve<14*1024**3 and free-expanded-reserve>=64*1024**3,'EXTRACTION_STORAGE_SCIENTIFIC_STOP'
# Second stream pass, only after the complete member and storage audit.
with tarfile.open(archive,'r|gz') as tf:
 for m in tf:
  dest=R/'data'/m.name;assert dest.resolve().is_relative_to((R/'data').resolve())
  if m.isdir():dest.mkdir(parents=True,exist_ok=True);continue
  dest.parent.mkdir(parents=True,exist_ok=True);src=tf.extractfile(m)
  with dest.open('xb') as out:
   while True:
    b=src.read(4*1024**2)
    if not b:break
    out.write(b)
   os.chmod(dest,0o444)
  check()
save('data_extraction.json',{'status':'PASS','expanded_bytes':expanded,'member_count':len(members),'source_archive_preserved_readonly':True,'new_disk_bytes':check()});os.chmod(archive,0o444);print('DATA_SAFE_EXTRACTION_PASS',expanded,len(members),flush=True)
