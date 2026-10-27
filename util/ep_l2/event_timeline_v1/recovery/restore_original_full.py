#!/usr/bin/env python3
"""Standalone engineering original-tree recovery from a verified native parcel.
Original case failed96MiB. No runtime/actor/registry/model/NAS operations.
Only destination is written; failure preserves partials. Receipt goes to stdout.
"""
from __future__ import annotations
import argparse,decimal,gzip,hashlib,json,os,pathlib,re,stat,subprocess,sys,tarfile
sys.dont_write_bytecode=True
P=pathlib.Path;PP=pathlib.PurePosixPath;M=1<<20;SCIENCE_CAP=96*M;EXTRA=64*1024;CHUNK=M
class Rejected(ValueError):pass
def need(ok,msg):
 if not ok:raise Rejected(msg)
def sha(path):
 h=hashlib.sha256()
 with P(path).open('rb')as f:
  for data in iter(lambda:f.read(CHUNK),b''):h.update(data)
 return h.hexdigest()
def unique_object(pairs):
 d={}
 for k,v in pairs:need(k not in d,'duplicate JSON key');d[k]=v
 return d
def integer(v,name,minimum=0,maximum=(1<<63)-1):
 need(type(v)is int and minimum<=v<=maximum,'invalid integer '+name);return v
def direct(value):
 p=P(value);need('..'not in p.parts,'parent traversal in filesystem path');p=P(os.path.abspath(str(p)))
 for q in[*reversed(p.parents),p]:
  try:s=q.lstat()
  except FileNotFoundError:continue
  need(not stat.S_ISLNK(s.st_mode),'symlink filesystem path '+str(q))
 return p
def regular(path):
 p=direct(path);s=p.lstat();need(stat.S_ISREG(s.st_mode)and s.st_nlink==1,'regular non-hardlinked parcel file required');return p

def validate_inventory(doc,max_bytes):
 need(doc['original_case_resource_qualified']is False and doc['original_cap_bytes']==SCIENCE_CAP and integer(doc['actual_original_allocated_bytes'],'original allocation')>SCIENCE_CAP,'engineering-only original case FAILED96MiB evidence required')
 entries=doc['entries'];need(type(entries)is list and 1<=len(entries)<=65536,'bounded nonempty inventory');by={}
 for row in entries:
  name=row['path'];need(type(name)is str and name and chr(0)not in name and chr(92)not in name,'bad inventory path')
  pp=PP(name);need(not pp.is_absolute()and '..'not in pp.parts and pp.as_posix()==name and len(pp.parts)<=128,'unsafe noncanonical inventory path')
  need(name not in by and row['type']in('file','directory'),'duplicate/unsupported inventory entry')
  integer(row['size'],'size');integer(row['uid'],'uid',0,(1<<32)-1);integer(row['gid'],'gid',0,(1<<32)-1);integer(row['mode'],'mode',0,0o7777);integer(row['mtime_ns'],'mtime_ns',-(1<<63),(1<<63)-1)
  if row['type']=='file':need(type(row['sha256'])is str and re.fullmatch('[0-9a-f]{64}',row['sha256']),'file SHA identity')
  by[name]=row
 need('.'in by and by['.']['type']=='directory','root directory inventory required')
 for name,row in by.items():
  if name=='.':continue
  parent=PP(name).parent.as_posix();need(parent in by and by[parent]['type']=='directory','every parent directory must be declared')
 expected=sum(((r['size']+4095)//4096)*4096 if r['type']=='file'else 4096 for r in entries)+EXTRA
 need(integer(max_bytes,'engineering max bytes',1)==expected,'max-bytes must equal file ceil4K + directory4K +64KiB; no large replacement cap')
 return entries,by,expected

class LimitedReader:
 def __init__(self,source,limit):self.source=source;self.limit=limit;self.count=0
 def read(self,n):
  need(type(n)is int and n>=0,'bounded decompression read required');data=self.source.read(min(n,self.limit-self.count+1));self.count+=len(data);need(self.count<=self.limit,'decompressed tar exceeds bounded inventory+metadata');return data

FLAGS=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW
def parent_fd(rootfd,name):
 fd=os.dup(rootfd)
 try:
  for component in PP(name).parent.parts:
   if component=='.':continue
   newer=os.open(component,FLAGS,dir_fd=fd);os.close(fd);fd=newer
  return fd
 except BaseException:os.close(fd);raise

def directory_fd(rootfd,name):
 if name=='.':return os.dup(rootfd)
 pfd=parent_fd(rootfd,name)
 try:return os.open(PP(name).name,FLAGS,dir_fd=pfd)
 finally:os.close(pfd)

def scan(rootfd,hash_files=False):
 found={};allocated=logical=0
 def visit(fd,name):
  nonlocal allocated,logical
  st=os.fstat(fd);allocated+=st.st_blocks*512;found[name]={'type':'directory','stat':st}
  with os.scandir(fd)as it:
   names=sorted(x.name for x in it)
  for base in names:
   rel=base if name=='.'else name+'/'+base;st=os.stat(base,dir_fd=fd,follow_symlinks=False)
   if stat.S_ISDIR(st.st_mode):
    child=os.open(base,FLAGS,dir_fd=fd)
    try:visit(child,rel)
    finally:os.close(child)
   else:
    need(stat.S_ISREG(st.st_mode)and st.st_nlink==1,'unexpected link/special/hardlinked target entry')
    allocated+=st.st_blocks*512;logical+=st.st_size;row={'type':'file','stat':st}
    if hash_files:
     child=os.open(base,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=fd)
     try:
      h=hashlib.sha256()
      for data in iter(lambda:os.read(child,CHUNK),b''):h.update(data)
      row['sha256']=h.hexdigest()
     finally:os.close(child)
    found[rel]=row
 visit(rootfd,'.');return found,allocated,logical

def apply_metadata(fd,row):
 os.fchown(fd,row['uid'],row['gid']);os.fchmod(fd,row['mode']);os.utime(fd,ns=(row['mtime_ns'],row['mtime_ns']));os.fsync(fd)

def restore(parcel,destination,max_bytes,inventory_sha256,archive_sha256):
 for h in[inventory_sha256,archive_sha256]:need(type(h)is str and re.fullmatch('[0-9a-f]{64}',h),'both external expected SHA256 values are mandatory')
 parcel=direct(parcel);need(parcel.is_dir(),'parcel directory required');inventory=regular(parcel/'ORIGINAL_CONTENTS.json');archive=regular(parcel/'ORIGINAL_RESULT.tar.gz')
 need(inventory.stat().st_size<=8*M and archive.stat().st_size<=32*M,'bounded inventory and original engineering parcel')
 need(sha(inventory)==inventory_sha256 and sha(archive)==archive_sha256,'parcel inventory/archive expected SHA mismatch')
 doc=json.loads(inventory.read_bytes(),object_pairs_hook=unique_object,parse_constant=lambda _:(_ for _ in()).throw(Rejected('nonfinite JSON')));entries,by,limit=validate_inventory(doc,max_bytes)
 dst=direct(destination);need(not os.path.lexists(dst)and dst.parent.is_dir(),'fresh destination with existing parent required')
 original=direct(doc['original_root']);need(not dst.is_relative_to(original)and not original.is_relative_to(dst),'destination cannot alter original source tree')
 need(not dst.is_relative_to(parcel)and not parcel.is_relative_to(dst),'parcel/destination trees must be disjoint')
 need(subprocess.check_output(['findmnt','-n','-T',str(dst.parent),'-o','FSTYPE'],text=True).strip()=='ext4','engineering original-full target must be native ext4')
 need(os.statvfs(dst.parent).f_bavail*os.statvfs(dst.parent).f_frsize>limit,'destination actual free bytes below this target bound')
 dst.mkdir(mode=0o700);rootfd=os.open(dst,FLAGS);identity=os.fstat(rootfd);written=0;rows_proof=[]
 def within():
  st=dst.lstat();need(stat.S_ISDIR(st.st_mode)and(st.st_dev,st.st_ino)==(identity.st_dev,identity.st_ino),'destination root identity changed')
  _,allocated,logical=scan(rootfd);need(allocated<=limit and logical<=limit,'actual engineering allocated/logical cap exceeded');return allocated,logical
 try:
  for row in sorted((r for r in entries if r['type']=='directory'and r['path']!='.'),key=lambda r:len(PP(r['path']).parts)):
   fd=parent_fd(rootfd,row['path'])
   try:os.mkdir(PP(row['path']).name,mode=0o700,dir_fd=fd)
   finally:os.close(fd)
  metadata_limit=max(2*M,len(entries)*16384);decompressed_limit=sum(r['size']for r in entries if r['type']=='file')+metadata_limit;seen=0
  with gzip.open(archive,'rb')as gz:
   bounded=LimitedReader(gz,decompressed_limit)
   with tarfile.open(fileobj=bounded,mode='r|')as tar:
    for number,item in enumerate(tar):
     need(number<len(entries),'extra tar entry');row=entries[number];need(item.name==row['path'],'tar inventory order/path mismatch')
     need(not item.issym()and not item.islnk()and not item.linkname and item.sparse is None,'tar link/sparse/special entry rejected')
     need(item.mode==row['mode']and item.uid==row['uid']and item.gid==row['gid']and'mtime'in item.pax_headers,'tar mode/uid/gid/nanosecond identity')
     stamp=decimal.Decimal(item.pax_headers['mtime'])*decimal.Decimal(10**9);need(stamp==row['mtime_ns'],'tar nanosecond mtime mismatch')
     if row['type']=='directory':need(item.type==tarfile.DIRTYPE,'directory type mismatch')
     else:
      need(item.type in(tarfile.REGTYPE,tarfile.AREGTYPE)and item.size==row['size'],'regular file type/size mismatch')
      fd=parent_fd(rootfd,row['path'])
      try:target=os.open(PP(row['path']).name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
      finally:os.close(fd)
      try:
       h=hashlib.sha256();count=0
       with tar.extractfile(item)as source:
        for data in iter(lambda:source.read(CHUNK),b''):
         count+=len(data);need(count<=row['size'],'file stream exceeds inventory');h.update(data);view=memoryview(data)
         while view:
          n=os.write(target,view);need(n>0,'zero-byte target write');view=view[n:]
         written+=len(data);within()
       need(count==row['size']and h.hexdigest()==row['sha256'],'full original file SHA mismatch');apply_metadata(target,row)
      finally:os.close(target)
     seen+=1;within()
    need(seen==len(entries),'truncated/incomplete tar inventory')
    # Consume cached+remaining tar padding through gzip EOF/CRC. No hidden member.
    while True:
     tail=tar.fileobj.read(CHUNK)
     if not tail:break
     need(not tail.strip(bytes(1)),'nonzero data after tar end marker')
  for row in sorted((r for r in entries if r['type']=='directory'),key=lambda r:len(PP(r['path']).parts),reverse=True):
   fd=directory_fd(rootfd,row['path'])
   try:apply_metadata(fd,row)
   finally:os.close(fd)
  found,allocated,logical=scan(rootfd,True);need(set(found)==set(by),'final exact target inventory')
  for name,row in by.items():
   got=found[name];st=got['stat'];need(got['type']==row['type']and(st.st_mode&0o7777)==row['mode']and st.st_uid==row['uid']and st.st_gid==row['gid']and st.st_mtime_ns==row['mtime_ns'],'final native metadata '+name)
   if row['type']=='file':need(st.st_size==row['size']and got['sha256']==row['sha256'],'final reopened file SHA/size '+name)
   rows_proof.append({'path':name,'type':row['type'],'sha256':got.get('sha256'),'mode':st.st_mode&0o7777,'uid':st.st_uid,'gid':st.st_gid,'mtime_ns':st.st_mtime_ns})
  need(allocated<=limit and logical<=limit,'final engineering native cap');within();need(sha(inventory)==inventory_sha256 and sha(archive)==archive_sha256,'input parcel changed during recovery')
  return {'status':'ENGINEERING_ONLY_ORIGINAL_CASE_FAILED96M_ORIGINAL_FULL_NATIVE_RESTORE_PASS','case':doc['case'],'uuid':doc['uuid'],'parcel':str(parcel),'destination':str(dst),'inventory_sha256':inventory_sha256,'archive_sha256':archive_sha256,'original_case_resource_qualified':False,'original_scientific_cap_bytes':SCIENCE_CAP,'original_reported_allocation_bytes':doc['actual_original_allocated_bytes'],'engineering_only_max_bytes':limit,'bound_formula':'sum(file ceil4KiB)+directory_count*4096+65536','actual_allocated_bytes':allocated,'actual_logical_file_bytes':logical,'regular_files':sum(r['type']=='file'for r in entries),'directories':sum(r['type']=='directory'for r in entries),'full_source_file_SHA_and_mode_UID_GID_mtime_ns_checked':True,'proof_rows_sha256':hashlib.sha256(json.dumps(rows_proof,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'synthetic_fixture':doc.get('synthetic_fixture',False),'scientific_acceptance_granted':False,'model_or_actor_or_registry_or_NAS_write':False,'source_parcel_unchanged':True,'source_keep':True}
 finally:os.close(rootfd)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parcel',required=True);p.add_argument('--destination',required=True);p.add_argument('--max-bytes',required=True,type=int);p.add_argument('--inventory-sha256',required=True);p.add_argument('--archive-sha256',required=True);a=p.parse_args()
 try:r=restore(a.parcel,a.destination,a.max_bytes,a.inventory_sha256,a.archive_sha256);print(json.dumps(r,sort_keys=True));return 0
 except(Exception)as e:print(json.dumps({'status':'ENGINEERING_ORIGINAL_FULL_RESTORE_REJECTED_PARTIALS_PRESERVED','reason':type(e).__name__+': '+str(e),'destination':a.destination,'scientific_acceptance_granted':False,'source_keep':True,'partial_target_may_exist_and_was_not_deleted':os.path.lexists(a.destination)}),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
