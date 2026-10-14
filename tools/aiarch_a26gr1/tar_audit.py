"""Bounded full gzip/tar scan followed by validated regular-file extraction."""
import argparse,gzip,hashlib,json,os,pathlib,resource,tarfile,time
from control import ROOT,check
ARCHIVE=ROOT/'downloads/rubble-pixsfm.tgz'
LIMIT=30*1024**3
class SafeInfo(tarfile.TarInfo):
 def _proc_sparse(self,*args,**kwargs):raise RuntimeError('SPARSE_TAR_REJECTED_BEFORE_PARSE')
 def _proc_gnusparse_00(self,*args,**kwargs):raise RuntimeError('SPARSE_PAX_REJECTED')
 def _proc_gnusparse_01(self,*args,**kwargs):raise RuntimeError('SPARSE_PAX_REJECTED')
 def _proc_gnusparse_10(self,*args,**kwargs):raise RuntimeError('SPARSE_PAX_REJECTED')
 def _proc_pax(self,tarfile_obj):
  if self.size>16384:raise RuntimeError('PAX_HEADER_TOO_LARGE')
  return super()._proc_pax(tarfile_obj)
 def _proc_gnulong(self,tarfile_obj):
  if self.size>16384:raise RuntimeError('GNU_LONG_HEADER_TOO_LARGE')
  return super()._proc_gnulong(tarfile_obj)
def validate(m,seen):
 p=pathlib.PurePosixPath(m.name)
 if not m.name or p.is_absolute() or '..' in p.parts or '\\' in m.name or len(m.name)>4096:raise RuntimeError('UNSAFE_TAR_PATH')
 key=str(p)
 if key in seen:raise RuntimeError('DUPLICATE_TAR_PATH '+key)
 if any(seen.get(str(a))=='regular' for a in p.parents):raise RuntimeError('TAR_REGULAR_PARENT_CONFLICT')
 if m.isreg() and any(k.startswith(key+'/') for k in seen):raise RuntimeError('TAR_CHILD_PARENT_TYPE_CONFLICT')
 if m.isdir() and m.size:raise RuntimeError('NONZERO_DIRECTORY_PAYLOAD')
 if p.parts[0]!='rubble-pixsfm':raise RuntimeError('UNEXPECTED_SCENE_ROOT')
 if not (m.isdir() or m.isreg()) or m.sparse:raise RuntimeError('UNSAFE_LINK_SPECIAL_OR_SPARSE')
 if m.size<0 or m.size>1024**3:raise RuntimeError('SINGLE_MEMBER_SIZE_BOUND')
 for k in m.pax_headers:
  if k not in {'path','mtime','atime','ctime','uid','gid','uname','gname','size'}:raise RuntimeError('UNQUALIFIED_PAX_KEY '+k)
 seen[key]='directory' if m.isdir() else 'regular';return key
def scan():
 start=time.monotonic();seen={};members=[];logical=0;allocated=0
 with gzip.open(ARCHIVE,'rb') as gz:
  with tarfile.open(fileobj=gz,mode='r|',tarinfo=SafeInfo,errorlevel=2) as tf:
   for m in tf:
    name=validate(m,seen);logical+=m.size;allocated+=((m.size+4095)//4096)*4096+4096
    if logical>LIMIT or len(seen)>100000:raise RuntimeError('ASSET_EXPANDED_BOUND_EXCEEDS_CAP')
    members.append({'name':name,'size':m.size,'kind':'directory' if m.isdir() else 'regular'})
    if len(members)%128==0:check();print('TAR_SCAN_PROGRESS',len(members),logical,flush=True)
   padding=0
   while b:=tf.fileobj.read(1024**2):
    padding+=len(b)
    if any(b) or padding>1024**2:raise RuntimeError('UNQUALIFIED_NONZERO_TRAILING_TAR_DATA')
   if padding<512:raise RuntimeError('TAR_SECOND_ZERO_TERMINATOR_MISSING')
 check(extra=allocated+16*1024**3)
 receipt={'status':'PASS','completed_entire_gzip_stream':True,'gzip_crc_validated_to_eof':True,'tar_header_checksums_valid':True,'rejected_links_special_sparse_duplicate_traversal':True,'member_count':len(members),'regular_file_count':sum(x['kind']=='regular' for x in members),'logical_bytes':logical,'filesystem_allocation_estimate_bytes':allocated,'max_member_bytes':max(x['size'] for x in members),'members':members,'members_manifest_sha256':hashlib.sha256(json.dumps(members,sort_keys=True).encode()).hexdigest(),'wall_seconds':time.monotonic()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'post_scan_budget':check()}
 (ROOT/'tar_scan_safety.json').write_text(json.dumps(receipt,indent=2)+'\n');print('FULL_TAR_SCAN_PASS',len(members),logical,'allocated_estimate',allocated,flush=True)
def extract():
 receipt=json.loads((ROOT/'tar_scan_safety.json').read_text());assert receipt['status']=='PASS'
 check(extra=receipt['filesystem_allocation_estimate_bytes']+16*1024**3)
 dst=ROOT/'raw';dst.mkdir(exist_ok=False);seen={};hashes=[];start=time.monotonic()
 with gzip.open(ARCHIVE,'rb') as gz:
  with tarfile.open(fileobj=gz,mode='r|',tarinfo=SafeInfo,errorlevel=2) as tf:
   for index,m in enumerate(tf):
    name=validate(m,seen);assert {'name':name,'size':m.size,'kind':'directory' if m.isdir() else 'regular'}==receipt['members'][index]
    target=dst/name;assert target.resolve().is_relative_to(dst.resolve())
    if m.isdir():target.mkdir(parents=True,exist_ok=True);continue
    target.parent.mkdir(parents=True,exist_ok=True)
    sha=hashlib.sha256();left=m.size
    with tf.extractfile(m) as source,target.open('xb') as sink:
     while left:
      b=source.read(min(left,1024**2))
      if not b:raise RuntimeError('TRUNCATED_TAR_PAYLOAD')
      sink.write(b);sha.update(b);left-=len(b)
    target.chmod(0o600);hashes.append({'name':name,'bytes':m.size,'sha256':sha.hexdigest()})
    if index%128==0:check();print('SAFE_EXTRACT_PROGRESS',index,flush=True)
 assert len(seen)==receipt['member_count']
 (ROOT/'extracted_asset_files.json').write_text(json.dumps({'status':'PASS','files':hashes,'file_count':len(hashes),'wall_seconds':time.monotonic()-start,'budget':check()},indent=2)+'\n')
 print('SAFE_EXTRACT_PASS',len(hashes),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['scan','extract']);a=p.parse_args();scan() if a.mode=='scan' else extract()
