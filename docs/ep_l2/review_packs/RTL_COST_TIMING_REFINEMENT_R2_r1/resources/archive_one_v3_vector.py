from pathlib import Path
import sys,json,hashlib,gzip
root=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_TIMING_REFINEMENT_R2_lane2_v3');d=root/'cost-vector'/sys.argv[1];assert (d/'FLOW_RECEIPT.json').exists();index=root/'COST_VECTOR_ARCHIVE_INDEX.json';rows=json.loads(index.read_text()) if index.exists() else []
for p in d.rglob('*'):
 if not p.is_file() or p.suffix=='.gz' or p.stat().st_size<5*2**20:continue
 blob=p.read_bytes();out=p.with_name(p.name+'.gz');assert not out.exists();packed=gzip.compress(blob,6,mtime=0);out.write_bytes(packed);assert gzip.decompress(out.read_bytes())==blob;rows.append({'original':str(p.relative_to(root)),'original_bytes':len(blob),'original_sha256':hashlib.sha256(blob).hexdigest(),'archive':str(out.relative_to(root)),'archive_bytes':len(packed),'archive_sha256':hashlib.sha256(packed).hexdigest(),'decoded_bytes_exact':True});p.unlink()
index.write_text(json.dumps(rows,indent=2)+'\n');print(sys.argv[1],'completed raw bytes archived losslessly',flush=True)
