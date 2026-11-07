"""Create small engineering review archive on actual164; never materialize Trace or model results."""
from pathlib import Path
import json,hashlib,subprocess,tarfile,io,datetime,os,gzip
P=Path(__file__).resolve().parent.parent;M=P/'main'
DEST=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/ep_l2_next_cost_aware_architecture_20261107_v1')
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
def main():
 mount=json.loads(subprocess.check_output(['findmnt','-T',str(DEST.parent),'-J','-o','TARGET,SOURCE,FSTYPE']))
 z=mount['filesystems'][0]
 assert '10.208.130.164' in z['source']and z['fstype'].startswith('fuse'),'not actual164'
 native=os.statvfs('/root/data');assert native.f_bavail*native.f_frsize>=5*(1<<30)
 sel=read(M/'REVIEW_EXPORT_SELECTION.json');files=[]
 for q in sel['files']:
  p=Path(q['source']);assert sha(p)==q['sha256'];assert '..'not in Path(q['export']).parts
  files.append(q)
 assert sum(Path(q['source']).stat().st_size for q in files)<30*(1<<20)
 DEST.mkdir(parents=True,exist_ok=True)
 out=DEST/'EP_L2_NEXT_ARCHITECTURE_SMALL_REVIEW_EVIDENCE_V1.tar.gz'
 manifest={'schema':'SMALL_ENGINEERING_ARCHIVE_MEMBER_MANIFEST_V1','files':files,'raw_original_evidence_bytes_preserved':True,'model_or_Trace_data':False}
 mb=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
 if not out.exists():
  partial=out.with_suffix(out.suffix+'.partial')
  assert not partial.exists(),'retained partial requires Main diagnosis'
  with partial.open('xb')as raw:
   with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0)as gz:
    with tarfile.open(fileobj=gz,mode='w')as t:
     for q in files:
      b=Path(q['source']).read_bytes();assert hashlib.sha256(b).hexdigest()==q['sha256']
      ti=tarfile.TarInfo(q['export']);ti.size=len(b);ti.mode=0o444;ti.mtime=0;t.addfile(ti,io.BytesIO(b))
     ti=tarfile.TarInfo('ARCHIVE_MEMBER_MANIFEST.json');ti.size=len(mb);ti.mode=0o444;ti.mtime=0;t.addfile(ti,io.BytesIO(mb))
   raw.flush();os.fsync(raw.fileno())
  before=sha(partial);partial.rename(out);assert sha(out)==before
 whole=sha(out)
 with tarfile.open(out,'r:gz')as t:
  members=t.getmembers();assert len(members)==len(files)+1
  assert t.extractfile('ARCHIVE_MEMBER_MANIFEST.json').read()==mb
  for q in files:assert hashlib.sha256(t.extractfile(q['export']).read()).hexdigest()==q['sha256']
 assert sha(out)==whole
 r={'schema':'NEXT_ARCHITECTURE_TRUE164_SMALL_EVIDENCE_RECEIPT_V1','status':'ACTUAL164_WHOLE_SHA_AND_ALL_SMALL_MEMBERS_CLOSED_REOPEN_PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive':str(out),'archive_sha256':whole,'archive_bytes':out.stat().st_size,'members':len(files)+1,'mount':z,'Native_source_floor_5GiB_checked':True,'Source_KEEP':True,'released_bytes':0,'full_library_body_restore_performed':False,'science_starts':0,'receipt_not_self_included':True}
 write(M/'TRUE164_SMALL_EVIDENCE_RECEIPT.json',r);write(DEST/'TRUE164_SMALL_EVIDENCE_RECEIPT.json',r);print(json.dumps(r))
if __name__=='__main__':main()
