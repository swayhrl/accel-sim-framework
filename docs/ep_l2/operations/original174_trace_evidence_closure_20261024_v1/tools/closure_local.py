from pathlib import Path
import subprocess,json,csv,hashlib,time,os
W=Path(subprocess.check_output(['git','-C',str(Path(__file__).parent),'rev-parse','--show-toplevel']).decode().strip())
R=W/'docs/ep_l2/operations/original174_trace_evidence_closure_20261024_v1';R.mkdir(parents=True,exist_ok=True)
P=Path('D:/repo/tmp/original174_trace_evidence_closure_20261024_v1');P.mkdir(parents=True,exist_ok=True)
B=Path('D:/repo/original174-remaining-assets-inventory-20261024-v1/docs/ep_l2/operations/original174_remaining_asset_inventory_20261024_v1')
T=Path('D:/repo/ep-dtc-trace-migration-20261024-v1/docs/ep_l2/operations/174new_ep_dtc_trace_migration_20261024_v1')
BASE='6a1a86ce3626bcd89274af071c4f4c5064ad607d'
TRACE='b93fc0dbac79d6f9c5ca027baa2d2e1cf371455b'
def load(p):
 p=Path(p);x=json.loads(p.read_text(encoding='utf8'))
 if isinstance(x,dict) and x.get('schema')=='LOSSLESS_AUDIT_METADATA_POINTER_V1':
  import gzip
  raw=gzip.decompress((p.parent/x['compressed_file']).read_bytes());assert hashlib.sha256(raw).hexdigest()==x['uncompressed_sha256'];return json.loads(raw)
 return x
def rows(p):return list(csv.DictReader(Path(p).open(encoding='utf-8-sig')))
def save(n,x):
 p=R/n;p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def git(*a):return subprocess.check_output(['git','-C',str(W),*a])
def remote(alias,code,timeout=70):
 p=subprocess.run(['ssh','-o','BatchMode=yes',alias,'nice -n 19 ionice -c 3 python3 -B -'],input=code.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-1500:])
 return json.loads(p.stdout)
def csvout(n,rs):
 if not rs:return
 with (R/n).open('w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,list(dict.fromkeys(k for r in rs for k in r)));w.writeheader();w.writerows(rs)
if __name__=='__main__':
 mandatory=['STORAGE_SUMMARY.md','LARGE_ASSETS_TOP30.csv','LARGE_ASSET_EVIDENCE_GAP_QUEUE.csv','POLYBENCH_TRACE_INVENTORY.csv','ARCHIVE_COVERAGE.csv','RAW_EXPERIMENT_RECORDS.csv','AWMA_C16_ASSET_AUDIT.md','UNKNOWN_AND_HOLDS.md']
 cat=[]
 for n in mandatory:
  b=(B/n).read_bytes();expected=git('show',BASE+':docs/ep_l2/operations/original174_remaining_asset_inventory_20261024_v1/'+n);assert b==expected
  cat.append(dict(path=n,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),rows=len(rows(B/n)) if n.endswith('.csv') else None))
 save('BASELINE_FULL_READ_AND_SHA.json',dict(commit=BASE,inputs=cat,true164_references=load(B/'references/IMMUTABLE_GIT_EVIDENCE_CATALOG.json'),trace_recovery_index=load(T/'TRUE164_TRACE_RECOVERY_INDEX.json')))
 text=Path('C:/Users/huang/.codex/attachments/275cf85e-4390-44c5-beb1-2670e88d84f8/已粘贴的文本.txt').read_text(encoding='utf8');(R/'GOAL_USER_INSTRUCTION.md').write_text(text,encoding='utf8')
 for n in ['LARGE_ASSETS_TOP30.csv','POLYBENCH_TRACE_INVENTORY.csv']:
  x=rows(B/n);print(n,len(x));print('\n'.join(r['source_path'] for r in x))
