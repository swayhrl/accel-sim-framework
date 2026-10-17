from pathlib import Path
import gzip,hashlib,json,shutil
root=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_OPEN_FLOW_V1_lane2_r1/retained_aborted_abc');rows=[]
def sha_stream(f):
 h=hashlib.sha256()
 while True:
  b=f.read(1024*1024)
  if not b:break
  h.update(b)
 return h.hexdigest()
for p in root.glob('yosys-abc-*/input.blif'):
 s=p.parent/'abc.script';assert s.exists() and 'EPL2_RTL_COST_OPEN_FLOW_V1_lane2_r1' in s.read_text()
 out=p.with_suffix('.blif.gz');assert not out.exists()
 with p.open('rb') as f:oldsha=sha_stream(f)
 with p.open('rb') as f,out.open('wb') as stream,gzip.GzipFile(filename='',mode='wb',fileobj=stream,compresslevel=1,mtime=0) as g:shutil.copyfileobj(f,g,1024*1024)
 with gzip.open(out,'rb') as f:assert sha_stream(f)==oldsha
 row={'original_file':str(p),'original_bytes':p.stat().st_size,'original_sha256':oldsha,'archive':str(out),'archive_bytes':out.stat().st_size,'archive_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'lossless_verified':True};p.unlink();rows.append(row)
(root/'LOSSLESS_COMPRESSION_RECEIPT.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({'own_aborted_EDA_files':len(rows),'source_bytes_preserved_losslessly':sum(r['original_bytes'] for r in rows),'retained_archive_bytes':sum(r['archive_bytes'] for r in rows),'old_simulator_raw_results_touched':False}))
