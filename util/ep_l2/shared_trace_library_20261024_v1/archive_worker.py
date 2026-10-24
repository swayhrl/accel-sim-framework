"""Finite immutable tar inventory plus full SHA for grouped trace members."""
import sys,json,os,hashlib,tarfile,time,stat,fcntl,lzma,gzip,subprocess,threading,zlib
req=json.load(sys.stdin)
parallel_read_only=isinstance(req,dict) and req.get('authorization')=='USER_AUTHORIZED_PARALLEL_READ_ONLY_INVENTORY_20261024'
if parallel_read_only:req=req['archives']
else:
 lock=open('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TLS_V10_SOURCE_SENDER.lock','rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
os.nice(19)
if os.path.isfile('/usr/bin/ionice'):subprocess.run(['/usr/bin/ionice','-c','3','-p',str(os.getpid())],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
rate_checked=0;current_rate=30*1024**2
def pace(count):
 global rate_checked,current_rate
 now=time.monotonic()
 if now-rate_checked>=5:
  try:
   line=next(x for x in open('/proc/pressure/io') if x.startswith('full '));full=float(next(x.split('=')[1] for x in line.split() if x.startswith('avg10=')))
  except (OSError,StopIteration,ValueError):full=100
  current_rate=(30 if full<5 else 10 if full<10 else 4 if full<20 else 1)*1024**2;rate_checked=now
 time.sleep(count/current_rate)
def ident(s):return {'dev':s.st_dev,'inode':s.st_ino,'size':s.st_size,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns,'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'nlink':s.st_nlink,'type':'file'}
class StrictTarInfo(tarfile.TarInfo):
 @classmethod
 def fromtarfile(cls,archive):
  try:return super().fromtarfile(archive)
  except (tarfile.EmptyHeaderError,tarfile.EOFHeaderError):raise
  except tarfile.HeaderError as exc:raise tarfile.ReadError('strict nonzero/truncated tar header: '+str(exc)) from exc

for request in req:
 path=request.get('actual_path',request['path'])
 if request.get('source_host')=='174-new':
  assert os.uname().nodename=='huangrulin-sshfs-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026535153]'
  assert os.path.realpath(path).startswith('/root/share/mnt164/huangrulin/') or (request.get('synthetic_qualification_only') and os.path.realpath(path).startswith('/root/data/shared_sm70_trace_library_20261024_v1/synthetic/'))
 else:assert os.uname().nodename=='huangrulin-174' and os.readlink('/proc/self/ns/mnt')=='mnt:[4026534768]'
 before=ident(os.stat(path));fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOATIME',0));raw=os.fdopen(fd,'rb');start=time.monotonic();hashed=0;last=start;records=[];raw_hash=hashlib.sha256();counter=[0];errors=[];reused=0
 prior=request.get('prior_index');cache={}
 if prior:
  for row in prior['members']:
   cache[(row['order'],row['archive_member'])]=row
 class Reader:
  def read(self,n=-1):
   b=raw.read(n);raw_hash.update(b);counter[0]+=len(b)
   pace(len(b))
   return b
  def tell(self):return raw.tell()
  def readable(self):return True
 reader=Reader();decoder=None;feeder=None;gz=None
 if path.endswith('.zst'):
  decoder=subprocess.Popen(['/usr/bin/zstd','-dc'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  def feed():
   try:
    while True:
     b=reader.read(1024**2)
     if not b:break
     decoder.stdin.write(b)
    decoder.stdin.close()
   except Exception as e:errors.append(str(e))
  feeder=threading.Thread(target=feed);feeder.start();decoded_stream=decoder.stdout
 else:gz=gzip.GzipFile(fileobj=reader,mode='rb');decoded_stream=gz
 tf=tarfile.open(fileobj=decoded_stream,mode='r|',ignore_zeros=True,tarinfo=StrictTarInfo,errorlevel=2)
 for number,ti in enumerate(tf):
  if number>2000000:raise RuntimeError('ARCHIVE_ENTRY_BOUND')
  n=ti.name;parts=n.split('/');safe=not n.startswith('/') and '..' not in parts and '\\' not in n
  row={'archive_member':n,'order':number,'size':ti.size,'mode':ti.mode,'uid':ti.uid,'gid':ti.gid,'mtime':str(ti.pax_headers.get('mtime',ti.mtime)),'regular':ti.isfile(),'safe':safe}
  grouped=('.traceg' in n or n.rsplit('/',1)[-1]=='kernelslist.g') and ti.isfile() and safe
  if request.get('hash_member_suffixes') and n.rsplit('/',1)[-1]!='kernelslist.g':grouped=grouped and any(n.endswith(suffix) for suffix in request['hash_member_suffixes'])
  companion=ti.isfile() and safe and ti.size<=65536 and n.rsplit('/',1)[-1] in ['run.sh','commandlist','stats.csv','README','README.md']
  if grouped or companion:
   old=cache.get((number,n))
   if old and all(old[k]==row[k] for k in row) and old.get('sha256'):
    row.update({k:old[k] for k in ['sha256','header_prefix_hex','binary_version','header','small_bytes_hex'] if k in old});row['member_hash_reused_from_same_archive_SHA']=True
    reused+=ti.size;records.append(row);continue
   f=tf.extractfile(ti);h=hashlib.sha256();prefix=b'';count=0;small=bytearray() if ti.size<=1048576 else None
   while True:
    b=f.read(1024**2)
    if not b:break
    h.update(b);count+=len(b);hashed+=len(b)
    if len(prefix)<65536:prefix+=b[:65536-len(prefix)]
    if small is not None:small.extend(b)
    # Decompressed bytes are memory/CPU work. Physical archive reads alone
    # consume the IO limiter, avoiding a second delay on inflated tar members.
    if time.monotonic()-last>=10:
     print(json.dumps({'event':'ARCHIVE_PROGRESS','archive':path,'member':n,'hashed_member_bytes':hashed,'entries':number,'elapsed':time.monotonic()-start}),flush=True);last=time.monotonic()
   assert count==ti.size
   decoded=prefix
   try:
    if n.endswith('.xz'):decoded=lzma.LZMADecompressor().decompress(prefix,max_length=2048)
    elif n.endswith('.gz'):decoded=zlib.decompressobj(31).decompress(prefix,2048)
   except Exception:decoded=b''
   fields={}
   for line in decoded[:2048].decode(errors='replace').splitlines():
    if line.startswith('-') and '=' in line:
     k,v=line[1:].split('=',1);fields[k.strip()]=v.strip()
   row.update(sha256=h.hexdigest(),header_prefix_hex=prefix[:128].hex(),binary_version=fields.get('binary version','UNKNOWN'),header=fields)
   if n.rsplit('/',1)[-1] in ['kernelslist.g','run.sh','commandlist','stats.csv'] and small is not None:row['small_bytes_hex']=small.hex()
  records.append(row)
 tf.close()
 if decoder:
  while decoder.stdout.read(1024**2):pass
  feeder.join();assert not errors,errors
  assert decoder.wait()==0,decoder.stderr.read().decode(errors='replace')
 else:
  while gz.read(1024**2):pass
  gz.close()
  while reader.read(1024**2):pass
 raw.close();assert ident(os.stat(path))==before
 assert counter[0]==before['size']
 if prior:assert raw_hash.hexdigest()==prior['archive_sha256'],'prior cache archive whole SHA differs'
 if request.get('expected_archive_sha256'):assert raw_hash.hexdigest()==request['expected_archive_sha256']
 result={'event':'ARCHIVE_DONE','path':request['path'],'archive_path':path,'source_host':request.get('source_host','174'),'inventory_format':'V2_FULL_DECODED_EOF_IGNORE_ZEROS','decoded_compression_EOF_integrity_checked':True,'strict_nonzero_invalid_headers_rejected':True,'archive_identity':before,'archive_sha256':raw_hash.hexdigest(),'compressed_bytes_read':counter[0],'hashed_member_bytes':hashed,'reused_same_archive_SHA_member_bytes':reused,'members':records,'source_before_after_unchanged':True,'source_writes':0,'parallel_read_only_inventory_authorized':parallel_read_only,'payload_transfer_sender_started':False,'elapsed':time.monotonic()-start}
 print(json.dumps(result),flush=True)
