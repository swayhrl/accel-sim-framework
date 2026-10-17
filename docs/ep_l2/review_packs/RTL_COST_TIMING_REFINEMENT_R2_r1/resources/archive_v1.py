from pathlib import Path
import gzip,json,hashlib,subprocess
r=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_TIMING_REFINEMENT_R2_lane2')
subprocess.run(['python3','rtl/ep_l2/flow/summarize.py','--liberty','/workspace/ep_l2_rtl_cost_open_flow_v1/r1/Nangate45_typ.lib','--out',str(r/'B16-v1-summary'),str(r/'B16-map-v1')],check=True)
rows=[]
for dirname in ('B16-map-v1','functional-v4','functional-v5'):
 for p in (r/dirname).rglob('*'):
  if not p.is_file() or p.stat().st_size<5*2**20 or p.suffix=='.gz':continue
  blob=p.read_bytes();out=p.with_name(p.name+'.gz');assert not out.exists();packed=gzip.compress(blob,6,mtime=0);out.write_bytes(packed);assert gzip.decompress(out.read_bytes())==blob
  rows.append({'original':str(p.relative_to(r)),'original_bytes':len(blob),'original_sha256':hashlib.sha256(blob).hexdigest(),'archive':str(out.relative_to(r)),'archive_bytes':len(packed),'archive_sha256':hashlib.sha256(packed).hexdigest(),'decoded_bytes_exact':True});p.unlink()
(r/'V1_ARCHIVE_INDEX.json').write_text(json.dumps(rows,indent=2)+'\n');print('V1 own artifacts archived',len(rows))
