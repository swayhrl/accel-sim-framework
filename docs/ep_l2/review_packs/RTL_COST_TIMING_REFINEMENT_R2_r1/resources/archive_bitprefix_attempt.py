from pathlib import Path
import gzip,json,hashlib
r=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_TIMING_REFINEMENT_R2_lane2_v3');d=r/'cost';rows=[]
for p in d.rglob('*'):
 if not p.is_file() or p.suffix=='.gz' or p.stat().st_size<5*2**20:continue
 blob=p.read_bytes();packed=gzip.compress(blob,6,mtime=0);out=p.with_name(p.name+'.gz');assert not out.exists();out.write_bytes(packed);assert gzip.decompress(out.read_bytes())==blob;rows.append({'original':str(p.relative_to(r)),'original_sha256':hashlib.sha256(blob).hexdigest(),'original_bytes':len(blob),'archive':str(out.relative_to(r)),'archive_sha256':hashlib.sha256(packed).hexdigest(),'archive_bytes':len(packed),'decoded_bytes_exact':True,'status':'BITPREFIX_ENGINEERING_ATTEMPT_NOT_FINAL_QUALIFIED_SOURCE'});p.unlink()
(r/'BITPREFIX_ATTEMPT_ARCHIVES.json').write_text(json.dumps(rows,indent=2)+'\n');print('bitprefix attempt raw retained losslessly',len(rows))
