from pathlib import Path
import hashlib,gzip,json,shutil,datetime
root=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_OPEN_FLOW_V1_lane2_r1');assert root.name=='EPL2_RTL_COST_OPEN_FLOW_V1_lane2_r1';rows=[]
size=lambda:sum(p.stat().st_size for p in root.rglob('*') if p.is_file() and not p.is_symlink())
before=size()
for p in sorted(root.rglob('*')):
 if not p.is_file() or p.is_symlink() or 'PUBLIC_REVIEW_PACK' in p.parts or p.suffix not in ['.v','.vvp','.blif','.log','.rpt'] or p.stat().st_size<512*1024:continue
 with p.open('rb') as f:oldsha=hashlib.file_digest(f,'sha256').hexdigest()
 oldbytes=p.stat().st_size;out=p.with_name(p.name+'.gz')
 if not out.exists():
  with p.open('rb') as f,out.open('wb') as stream,gzip.GzipFile(filename='',mode='wb',fileobj=stream,compresslevel=1,mtime=0) as z:shutil.copyfileobj(f,z,1024*1024)
 with gzip.open(out,'rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==oldsha
 row={'original_relative_path':str(p.relative_to(root)),'original_bytes':oldbytes,'original_sha256':oldsha,'archive_relative_path':str(out.relative_to(root)),'archive_bytes':out.stat().st_size,'archive_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'lossless_decoded_sha256_verified':True};p.unlink();rows.append(row)
after=size();receipt={'root':str(root),'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'only new Lane2 own RTL-cost artifacts; no simulator campaign raw or foreign project touched','retained_before_bytes':before,'retained_after_bytes_before_this_index':after,'files':rows,'restore':'gzip -dc exact_archive.gz > original_path; validate original_sha256; do restores under current central output/resource admission'};(root/'ARTIFACT_ARCHIVE_INDEX.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'files':len(rows),'before':before,'after':after,'all_original_bytes_recoverable':True}))
