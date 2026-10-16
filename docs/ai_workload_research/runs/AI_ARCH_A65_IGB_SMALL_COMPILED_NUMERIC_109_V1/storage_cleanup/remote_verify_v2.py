"""Two bounded read-only SHA workers, durable completed-file resume, no archive writes."""
from pathlib import Path
import os,json,time,hashlib,threading,concurrent.futures
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2])
R=Path('/tmp/aiarch_109_firstbatch_sha_20261016_lane_m_v1');BASE=Path('/root/share/mnt164/huangrulin/c16_ai_workload')
lock=threading.Lock();resume={};jobs=[];rows=[];readbytes=0;last=time.monotonic()
for name in ['verified.jsonl','verified_v2.jsonl']:
 p=R/name
 if p.exists():
  for line in p.read_text().splitlines():
   row=json.loads(line);resume[row['path']]=row
log=(R/'verified_v2.jsonl').open('a',buffering=1)
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
 return h.hexdigest()
revisions={'deepseek-v2-lite':'604d5664dddd88a0433dbae533b7fe9472482de0','qwen3-8b':'b968826d9c46dd6066d109eabc6255188de91218','qwen2.5-7b-instruct-raw':'a09a35458c702b33eeacc393d103063234e8bc28','qwen2.5-7b-instruct-awq':'b25037543e9394b818fdfca67ab2a00ecc7dd641','qwen2.5-0.5b-instruct':'7ae557604adf67be50417f59c2c2f167def9a775'}
for name,rev in revisions.items():
 base=BASE/'assets/models'/name/rev;receipt=json.loads((base/'MODEL_ARCHIVE_RECEIPT.json').read_text());a=base/'SOURCE_INVENTORY.tsv';b=base/'DESTINATION_INVENTORY.tsv';assert a.read_bytes()==b.read_bytes();assert digest(a)==receipt['source_inventory_file_sha256']
 for line in a.read_text().splitlines()[1:]:
  rel,num,sha=line.split('\t');p=base/rel;assert p.resolve().is_relative_to(base.resolve());jobs.append((p,int(num),sha))
run='C16R_qwen2p5-7b-instruct-awq_s2-text-d1-d3_decode3_nvbit1771-sim-native-full-sass_bounded-context_20260925T120107Z_2b41b26fdb03';base=BASE/'raw'/run;manifest=base/'RUN_MANIFEST.json';assert digest(manifest)=='db3bdbb0295a47a6aa4644508ea1895779c987f2f77cd96f184c67b8a10ab389'
for x in json.loads(manifest.read_text())['artifacts']:
 p=base/x['relative_path'];assert p.resolve().is_relative_to(base.resolve());jobs.append((p,x['size_bytes'],x['sha256']))
def verify(job):
 global readbytes,last
 p,size,expected=job;before=p.stat();assert before.st_size==size
 old=resume.get(str(p));cached=old is not None and old['sha256']==expected and old['bytes']==size and old['mtime_ns']==before.st_mtime_ns
 actual=expected if cached else digest(p);after=p.stat();assert before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns;assert actual==expected,str(p)
 row={'path':str(p),'bytes':size,'sha256':actual,'mtime_ns':after.st_mtime_ns,'resumed_completed_file':cached}
 with lock:
  rows.append(row);log.write(json.dumps(row)+'\n');readbytes+=0 if cached else size
  if time.monotonic()-last>20:
   print('VERIFIED_FILES',len(rows),'CURRENT_READ_BYTES',readbytes,flush=True);last=time.monotonic()
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for result in pool.map(verify,jobs):pass
log.close();assert len(rows)==len(jobs)==9172
(R/'final.json').write_text(json.dumps({'status':'PASS_FULL_CURRENT_164_PAYLOAD_SHA256','hashed_bytes':sum(x['bytes'] for x in rows),'files':rows,'archive_writes':0,'CPU_hash_workers':2})+'\n');print('PASS_FULL_CURRENT_164_PAYLOAD_SHA256',len(rows),flush=True)
