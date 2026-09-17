#!/usr/bin/env python3
from __future__ import annotations
import hashlib, csv
from pathlib import Path

root=Path('/data/c16/awma/qwen25_s2_kernel_census_20260917T101100Z')
analysis=root/'analysis'
dest='/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/qwen25_s2_kernel_census_20260917T101100Z'
post=root/'gpu_post_archive.csv'
if not post.exists():
    import subprocess
    post.write_text(subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.used,driver_version','--format=csv,noheader'],text=True))
files=[root/'qwen25_s2_census.nsys-rep',root/'qwen25_s2_census.sqlite',root/'driver.py',root/'driver.stdout',root/'driver.stderr',root/'gpu_before.csv',post]
files += [p for p in sorted(analysis.iterdir()) if p.is_file()]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
with (root/'RAW_DATA_INDEX.tsv').open('w',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['relative_path','size_bytes','sha256','durable_destination'])
 for p in files:
  rel=p.relative_to(root).as_posix();w.writerow([rel,p.stat().st_size,sha(p),dest+'/'+rel])
print(dest)
