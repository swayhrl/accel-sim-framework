from pathlib import Path
import gzip,hashlib,json,time
r=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_TIMING_REFINEMENT_R2_lane2');rows=[]
# Exact own completed engineering attempts only. No R1/active directory traversal.
for d in ('functional-v2','functional-v3','select-debug-v1','select-debug-v2','integration-debug-v3'):
 for p in (r/d).glob('*.vvp'):
  blob=p.read_bytes();out=p.with_suffix('.vvp.gz');assert not out.exists();packed=gzip.compress(blob,6,mtime=0);out.write_bytes(packed);assert gzip.decompress(out.read_bytes())==blob
  rows.append({'original':str(p.relative_to(r)),'original_bytes':len(blob),'original_sha256':hashlib.sha256(blob).hexdigest(),'archive':str(out.relative_to(r)),'archive_bytes':len(packed),'archive_sha256':hashlib.sha256(packed).hexdigest(),'decoded_bytes_exact':True});p.unlink()
(r/'ENGINEERING_ATTEMPT_ARCHIVES.json').write_text(json.dumps(rows,indent=2)+'\n');print('own completed attempts losslessly archived',len(rows))
