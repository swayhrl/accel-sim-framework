"""Bounded trace-header reads only; no workload/simulator execution."""
import os,sys,json,hashlib,gzip,lzma,stat,time,concurrent.futures,collections,datetime
requests=json.load(sys.stdin)
def probe(r):
 out={'key':r['key'],'path':r['path']}
 try:
  fd=os.open(r['path'],os.O_RDONLY|getattr(os,'O_NOATIME',0))
  with os.fdopen(fd,'rb') as raw:
   before=os.fstat(raw.fileno())
   if r['path'].endswith('.xz'):f=lzma.LZMAFile(raw)
   elif r['path'].endswith('.gz'):f=gzip.GzipFile(fileobj=raw)
   else:f=raw
   b=f.read(2048);read_bytes=raw.tell();after=os.fstat(raw.fileno())
   fields={}
   for l in b.decode(errors='replace').splitlines():
    if l.startswith('-') and '=' in l:
     k,v=l[1:].split('=',1);fields[k.strip()]=v.strip()
   out.update(exists=True,stable=(before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),metadata_matches_prior=(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==tuple(r['identity']),physical_prefix_bytes_read=read_bytes,decoded_prefix_bytes=len(b),prefix_sha256=hashlib.sha256(b).hexdigest(),header=fields,binary_version=fields.get('binary version','UNKNOWN'))
 except Exception as e:out.update(exists=False,error=str(e),binary_version='UNKNOWN')
 return out
t=time.monotonic()
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(probe,requests))
print(json.dumps({'schema':'BOUNDED_ALL_DECLARED_MEMBER_HEADER_PROBE_V3','hostname':os.uname().nodename,'namespace':os.readlink('/proc/self/ns/mnt'),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-t,'files':rows,'architecture_counts':dict(collections.Counter(r['binary_version'] for r in rows)),'trace_full_content_sha_verified':False,'simulator_or_workload_invocations':0}))
