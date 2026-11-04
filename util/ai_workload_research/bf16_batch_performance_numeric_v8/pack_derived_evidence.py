"""Lossless deterministic archival of large derived numeric tables;no sample filtering."""
from pathlib import Path
import json,gzip,hashlib
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/"docs/ai_workload_research/runs/QWEN_BF16_BATCH_PERFORMANCE_NUMERIC_STUDY_109_V8"
def main():
 for p in sorted(OUT.glob('NUMERIC_*.json')):
  raw=p.read_bytes();v=json.loads(raw)
  if '_full_evidence_archive' in v or len(raw)<=200000:continue
  (OUT/'.private'/('UNCOMPRESSED_'+p.name)).write_bytes(raw)
  archive=OUT/'raw'/(p.name+'.gz');archive.write_bytes(gzip.compress(raw,compresslevel=9,mtime=0));assert gzip.decompress(archive.read_bytes())==raw
  small={k:x for k,x in v.items() if k not in ['B1_B2_pairs','repetition']}
  small['_full_evidence_archive']=dict(path=str(archive.relative_to(OUT)),encoding='gzip',uncompressed_sha256=hashlib.sha256(raw).hexdigest(),uncompressed_bytes=len(raw),archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),byte_exact=True)
  p.write_text(json.dumps(small,indent=2)+'\n')
  print(p.name,len(raw),archive.stat().st_size)
if __name__=='__main__':main()
