#!/usr/bin/env python3
import csv,hashlib,sys
from pathlib import Path
root=Path(sys.argv[1])
for row in csv.DictReader((root/'RAW_DATA_INDEX.tsv').open(),delimiter='\t'):
 p=root/row['relative_path']
 if not p.is_file() or p.stat().st_size != int(row['size_bytes']): raise SystemExit('size/path mismatch '+row['relative_path'])
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 if h != row['sha256']: raise SystemExit('sha mismatch '+row['relative_path'])
print('NODE164_CENSUS_HASH_VERIFY_PASS files='+str(sum(1 for _ in csv.DictReader((root/'RAW_DATA_INDEX.tsv').open(),delimiter='\t'))))
