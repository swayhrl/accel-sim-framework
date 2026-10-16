
from pathlib import Path
import hashlib,json,os,time,sys
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2])
r=Path('/root/share/mnt164/huangrulin/c16_ai_workload');rows=[];done=0;last=time.monotonic()
work=Path('/tmp/aiarch_109_firstbatch_sha_20261016_lane_m_v1')
verified=(work/'verified.jsonl').open('a',buffering=1)
def record(p,actual,num):
 rows.append({'path':str(p),'bytes':num,'sha256':actual,'mtime_ns':p.stat().st_mtime_ns})
 verified.write(json.dumps(rows[-1])+'\n')
def sha(p):
 global done,last
 h=hashlib.sha256();before=p.stat()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024**2),b''):
   h.update(b);done+=len(b)
   if time.monotonic()-last>30:print('REMOTE_SHA_PROGRESS_BYTES',done,flush=True,file=sys.stderr);last=time.monotonic()
 after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
 return h.hexdigest()
for name in ['deepseek-v2-lite','qwen3-8b','qwen2.5-7b-instruct-raw','qwen2.5-7b-instruct-awq','qwen2.5-0.5b-instruct']:
 revisions={'deepseek-v2-lite':'604d5664dddd88a0433dbae533b7fe9472482de0','qwen3-8b':'b968826d9c46dd6066d109eabc6255188de91218','qwen2.5-7b-instruct-raw':'a09a35458c702b33eeacc393d103063234e8bc28','qwen2.5-7b-instruct-awq':'b25037543e9394b818fdfca67ab2a00ecc7dd641','qwen2.5-0.5b-instruct':'7ae557604adf67be50417f59c2c2f167def9a775'}
 q=r/'assets/models'/name/revisions[name];rec=json.loads((q/'MODEL_ARCHIVE_RECEIPT.json').read_text());a=q/'SOURCE_INVENTORY.tsv';b=q/'DESTINATION_INVENTORY.tsv';assert a.read_bytes()==b.read_bytes();assert sha(a)==rec['source_inventory_file_sha256']
 for line in a.read_text().splitlines()[1:]:
  rel,num,h=line.split('\t');p=q/rel;assert p.stat().st_size==int(num);actual=sha(p);assert actual==h,'REMOTE_MODEL_SHA_FAILED '+str(p);record(p,actual,int(num))
run='C16R_qwen2p5-7b-instruct-awq_s2-text-d1-d3_decode3_nvbit1771-sim-native-full-sass_bounded-context_20260925T120107Z_2b41b26fdb03';q=r/'raw'/run;p=q/'RUN_MANIFEST.json';assert sha(p)=='db3bdbb0295a47a6aa4644508ea1895779c987f2f77cd96f184c67b8a10ab389';d=json.loads(p.read_text())
for x in d['artifacts']:
 p=q/x['relative_path'];assert p.stat().st_size==x['size_bytes'];actual=sha(p);assert actual==x['sha256'],'REMOTE_E1_SHA_FAILED '+str(p);record(p,actual,p.stat().st_size)
verified.close()
(work/'final.json').write_text(json.dumps({'status':'PASS_FULL_CURRENT_164_PAYLOAD_SHA256','hashed_bytes':done,'files':rows,'archive_writes':0})+'\n')
print('PASS_FULL_CURRENT_164_PAYLOAD_SHA256',done,flush=True)
