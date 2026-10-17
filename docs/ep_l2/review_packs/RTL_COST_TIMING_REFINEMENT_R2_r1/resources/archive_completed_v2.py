from pathlib import Path
import gzip,hashlib,json
r=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_TIMING_REFINEMENT_R2_lane2');out=r/'COMPLETED_V2_ARCHIVES.json';rows=json.loads(out.read_text()) if out.exists() else []
for mode in ('B16','S64'):
 d=r/(mode+'-map-v2')
 if not (d/'FLOW_RECEIPT.json').exists():continue
 for p in d.rglob('*'):
  if not p.is_file() or p.stat().st_size<5*2**20 or p.suffix=='.gz':continue
  blob=p.read_bytes();packed=gzip.compress(blob,6,mtime=0);q=p.with_name(p.name+'.gz');assert not q.exists();q.write_bytes(packed);assert gzip.decompress(q.read_bytes())==blob
  rows.append({'original':str(p.relative_to(r)),'original_bytes':len(blob),'original_sha256':hashlib.sha256(blob).hexdigest(),'archive':str(q.relative_to(r)),'archive_bytes':len(packed),'archive_sha256':hashlib.sha256(packed).hexdigest(),'decoded_bytes_exact':True});p.unlink()
out.write_text(json.dumps(rows,indent=2)+'\n');print('lossless completed v2 artifact archives',len(rows))
